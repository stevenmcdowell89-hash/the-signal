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

const ENDPOINT = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

// $1 / $5 per M tokens for claude-haiku-4-5.
const IN_PER_TOK = 1.0 / 1e6;
const OUT_PER_TOK = 5.0 / 1e6;
const CACHE_READ_PER_TOK = 0.1 / 1e6;
const CACHE_WRITE_PER_TOK = 1.25 / 1e6;

function systemPrompt(profile) {
  const floor = (profile.named_entity_floor || []).map((e) => e.label).join(", ");
  const topics = Object.entries(profile.topic_weights || {})
    .map(([d, s]) => `${d} (${s.weight})`)
    .join(", ");
  const handling = Object.entries(profile.special_handling || {})
    .map(([d, s]) => `${d}: ${s.note}`)
    .join("; ");
  return `You are the triage engine for "The Signal" daily brief — a dense, scannable, link-out digest for one reader. You classify and write one hook line per news item.

The reader's core entities (always relevant): ${floor}.
Weighted interest topics: ${topics}.
Special handling — ${handling}.

For each item return:
- register: one of "consequential" (it matters / something happened), "take" (an argument or opinion worth hearing), "colour" (a quirk / curiosity), "discovery" (something to find / try).
- hook: ONE line, register-matched. SPECIFICITY IS THE BAR — name the actual argument, number, or quirk. "Interesting discussion about X" is a failed line. Personal second-person voice is allowed ("your device", "your Sunday"). Max ~22 words. No clickbait, no spoilers (books/film), no diet/calorie framing (fitness).
- relevance: 0.0–1.0, how relevant to THIS reader's profile (not general importance). A precise reason to care is the gate; if there is no specific reason this reader should care, score low.

Be terse. Do not editorialise beyond the hook.`;
}

const OUTPUT_SCHEMA = {
  type: "object",
  properties: {
    register: { type: "string", enum: ["consequential", "take", "colour", "discovery"] },
    hook: { type: "string" },
    relevance: { type: "number" },
  },
  required: ["register", "hook", "relevance"],
  additionalProperties: false,
};

async function callHaiku(env, system, item, model) {
  const body = {
    model: model || "claude-haiku-4-5",
    max_tokens: 200,
    system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
    output_config: { format: { type: "json_schema", schema: OUTPUT_SCHEMA } },
    messages: [
      {
        role: "user",
        content: `Item (${item.domain}): "${item.title}"\nSource type: ${item.source_type}. Links: ${
          (item.links || []).map((l) => l.type).join(", ")
        }.`,
      },
    ],
  };
  const resp = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`anthropic ${resp.status}: ${t.slice(0, 200)}`);
  }
  const data = await resp.json();
  const usage = data.usage || {};
  const cents =
    100 *
    ((usage.input_tokens || 0) * IN_PER_TOK +
      (usage.output_tokens || 0) * OUT_PER_TOK +
      (usage.cache_read_input_tokens || 0) * CACHE_READ_PER_TOK +
      (usage.cache_creation_input_tokens || 0) * CACHE_WRITE_PER_TOK);
  let parsed = null;
  const block = (data.content || []).find((b) => b.type === "text");
  if (block) {
    try {
      parsed = JSON.parse(block.text);
    } catch {
      parsed = null;
    }
  }
  return { parsed, cents };
}

// Enrich the shortlist. Returns { enriched, spentCents, degraded, reason }.
export async function enrichShortlist(env, db, items, config, now) {
  const ec = config.enrichment || {};
  if (!ec.enabled) return { enriched: 0, spentCents: 0, degraded: true, reason: "enrichment off" };
  if (!env.ANTHROPIC_API_KEY)
    return { enriched: 0, spentCents: 0, degraded: true, reason: "no ANTHROPIC_API_KEY" };

  const spent = await getMonthlySpendCents(env);
  if (spent >= (ec.monthly_spend_cap_cents || 500))
    return { enriched: 0, spentCents: 0, degraded: true, reason: "monthly spend cap hit" };

  // Shortlist: top-N by confidence that need enriching (not already judged).
  const shortlist = items
    .filter((i) => !i.muted)
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, ec.shortlist_size || 36)
    .filter((i) => !i.enriched);

  if (!shortlist.length) return { enriched: 0, spentCents: 0, degraded: false, reason: "nothing new" };

  const system = systemPrompt(config.profile);
  let enriched = 0;
  let spentCents = 0;
  let capHit = false;

  // Sequential with a per-loop cap check so we never blow the budget. (Awaiting
  // fetch costs wall time, not CPU; ~36 items is well within a cron run.)
  for (const it of shortlist) {
    if (spent + spentCents >= (ec.monthly_spend_cap_cents || 500)) {
      capHit = true;
      break;
    }
    try {
      const { parsed, cents } = await callHaiku(env, system, it, ec.model);
      spentCents += cents;
      if (parsed) {
        // Semantic relevance feeds above-fold (§3 Tier 2). Blend with Tier-1.
        const rel = Math.max(0, Math.min(1, parsed.relevance));
        it.register = parsed.register;
        it.hook = parsed.hook;
        it.profile_score = Math.max(it.profile_score, rel);
        // Re-derive confidence influence from the AI relevance, keeping the
        // entity-floor pin.
        if (!it.entity_floor) {
          it.confidence = Math.max(it.confidence, 0.5 * rel + 0.5 * it.confidence);
          it.above_fold = it.confidence >= config.fold_threshold;
        }
        it.enriched = true;
        it.enrich_hash = it.canonical_url;
        await saveEnrichment(db, it.id, {
          register: it.register,
          hook: it.hook,
          relevance: it.profile_score,
          enrich_hash: it.enrich_hash,
        });
        enriched++;
      }
    } catch (e) {
      // Single-item failure: skip; Tier-1 line still ships for it.
    }
  }

  if (spentCents > 0) await addSpendCents(env, spentCents);
  return {
    enriched,
    spentCents,
    degraded: false,
    reason: capHit ? "spend cap reached mid-run" : "ok",
  };
}
