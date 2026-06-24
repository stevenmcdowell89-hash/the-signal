// The Signal — daily: Tier 2 enrichment (§3 Tier 2).
//
// Optional. Runs only on the shortlist (~top 30–40), never the firehose. Model:
// claude-haiku-4-5 ($1/$5 per M tokens). The profile/instructions live in a
// cached system block (cache_control: ephemeral) so re-polls only pay for the
// per-item user turn. Structured outputs guarantee parseable JSON. Each item is
// judged once and cached (enrich_hash); re-polls enrich only new arrivals.
//
// Degrade: if the API key is missing, the toggle is off, or the monthly spend
// cap is hit, the caller ships Tier-1 ranked items with headlines + links and no
// hooks — the daily can never run an unbounded AI bill.

import { saveEnrichment } from "./db.js";
import { addSpendCents, getMonthlySpendCents } from "./config.js";
import { callModel } from "./llm.js";
import { profileContext } from "./editorial.js";

function systemPrompt(ctx, guidance) {
  // Optional reader-authored steer (editable in Settings → Enrichment). Appended
  // so it extends the built-in instruction without replacing it.
  const steer = (guidance || "").trim();
  return `You are the triage engine for "The Signal" daily brief — a dense, scannable, link-out digest for one reader. You classify and write one hook line per news item.

The reader's configured priorities (honour these — they come from the reader's own settings):
${ctx}

You will be given a numbered list of items, each with an id. Return one object per item, keyed by its given id. Judge each item independently on its own merits — NOT relative to the others in the batch. For each item return:
- register: one of "consequential" (it matters / something happened), "take" (an argument or opinion worth hearing), "colour" (a quirk / curiosity), "discovery" (something to find / try).
- hook: ONE line, register-matched. SPECIFICITY IS THE BAR — name the actual argument, number, or quirk. "Interesting discussion about X" is a failed line. Personal second-person voice is allowed ("your device", "your Sunday"). Max ~22 words. No clickbait, no spoilers (books/film), no diet/calorie framing (fitness).
- relevance: 0.0–1.0, how relevant to THIS reader's profile (not general importance), consistent with the priorities above. A precise reason to care is the gate; if there is no specific reason this reader should care, score low.

Be terse. Do not editorialise beyond the hook.${steer ? `\n\nReader's editorial guidance: ${steer}` : ""}`;
}

// Array output: one judged object per item, keyed back to the item by id.
const BATCH_SCHEMA = {
  type: "object",
  properties: {
    items: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          register: { type: "string", enum: ["consequential", "take", "colour", "discovery"] },
          hook: { type: "string" },
          relevance: { type: "number" },
        },
        required: ["id", "register", "hook", "relevance"],
        additionalProperties: false,
      },
    },
  },
  required: ["items"],
  additionalProperties: false,
};

function callBatch(env, system, chunk, model) {
  const user = chunk
    .map((it) => `${it.id} | (${it.domain}) "${it.title}" [${it.source_type || "?"}]`)
    .join("\n");
  // ~item-count scales output; give headroom of ~60 tokens/item.
  return callModel(env, { system, user, schema: BATCH_SCHEMA, model, max_tokens: Math.min(2000, 120 + chunk.length * 70) });
}

// Effective spend ceiling: when the AI layer is on, the shared cap governs all
// passes (enrichment + editorial); otherwise enrichment's own legacy cap applies.
function effectiveCap(config) {
  const ec = config.enrichment || {};
  const ai = config.ai || {};
  const legacy = ec.monthly_spend_cap_cents || 500;
  return ai.enabled ? Math.min(legacy, ai.monthly_cap_cents || legacy) : legacy;
}

// Enrich the shortlist. Returns { enriched, spentCents, degraded, reason }.
export async function enrichShortlist(env, db, items, config, now) {
  const ec = config.enrichment || {};
  if (!ec.enabled) return { enriched: 0, spentCents: 0, degraded: true, reason: "enrichment off" };
  if (!env.ANTHROPIC_API_KEY)
    return { enriched: 0, spentCents: 0, degraded: true, reason: "no ANTHROPIC_API_KEY" };

  const cap = effectiveCap(config);
  const spent = await getMonthlySpendCents(env);
  if (spent >= cap)
    return { enriched: 0, spentCents: 0, degraded: true, reason: "monthly spend cap hit" };

  // Shortlist: top-N by confidence that need enriching (not already judged).
  const shortlist = items
    .filter((i) => !i.muted)
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, ec.shortlist_size || 100)
    .filter((i) => !i.enriched);

  if (!shortlist.length) return { enriched: 0, spentCents: 0, degraded: false, reason: "nothing new" };

  const system = systemPrompt(profileContext(config), ec.guidance);
  let enriched = 0;
  let spentCents = 0;
  let capHit = false;

  // Apply one judged result to its item (identical mutations to the per-item path
  // before; only the source is now a batch element).
  const applyOne = async (it, parsed) => {
    const rel = Math.max(0, Math.min(1, parsed.relevance));
    it.register = parsed.register;
    it.hook = parsed.hook;
    it.profile_score = Math.max(it.profile_score, rel);
    if (!it.entity_floor) {
      it.confidence = Math.max(it.confidence, 0.5 * rel + 0.5 * it.confidence);
      it.above_fold = it.confidence >= config.fold_threshold;
    }
    it.enriched = true;
    it.enrich_hash = it.canonical_url;
    await saveEnrichment(db, it.id, {
      register: it.register, hook: it.hook, relevance: it.profile_score, enrich_hash: it.enrich_hash,
    });
    enriched++;
  };

  // Mini-batch: chunk the shortlist into one call per `batch_size` items. The
  // cached system block means chunks 2..N pay almost nothing for the instructions,
  // so coverage can be far wider than the old one-call-per-item path at fewer calls.
  const batchSize = Math.max(1, ec.batch_size || 10);
  for (let off = 0; off < shortlist.length; off += batchSize) {
    if (spent + spentCents >= cap) { capHit = true; break; }
    const chunk = shortlist.slice(off, off + batchSize);
    try {
      const { parsed, cents } = await callBatch(env, system, chunk, ec.model);
      spentCents += cents;
      const byId = new Map(chunk.map((it) => [it.id, it]));
      for (const r of (parsed && Array.isArray(parsed.items) ? parsed.items : [])) {
        const it = byId.get(r.id);
        if (it && !it.enriched) await applyOne(it, r);
      }
    } catch (e) {
      // Whole-chunk failure: those items ship Tier-1 (same as a per-item failure before).
    }
  }

  if (spentCents > 0) await addSpendCents(env, spentCents, "enrichment");
  return {
    enriched,
    spentCents,
    degraded: false,
    reason: capHit ? "spend cap reached mid-run" : "ok",
  };
}
