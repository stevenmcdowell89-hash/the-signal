// The Signal — daily: the AI editorial layer.
//
// A quality layer ON TOP of the mechanical brief — never a dependency. Each pass
// is independently toggleable (config.ai.<feat>.enabled), reads its own plain-English
// `guidance` steer, draws on ONE shared monthly cap, and caches by a content-set hash
// (+ a min-interval throttle) so the 10-min cron doesn't re-bill when nothing changed.
// On any gate/parse/cap failure a pass is a no-op and the mechanical brief stands.
//
// `augmentEditorial` runs AFTER buildState (so buildState stays pure) and MUTATES the
// state blob, adding fields the front-end reads. `smartMerge` is the exception — it
// runs before scoring's consumers and mutates `items` (added in a later PR).

import { addSpendCents, getMonthlySpendCents } from "./config.js";
import { callModel } from "./llm.js";

const BRIEFS_KEY = "editorial:briefs";
const PICKS_KEY = "editorial:picks";

// Shared gate: master switch + per-feature toggle + API key + shared cap.
async function gate(env, ai, feat) {
  if (!ai || !ai.enabled) return { ok: false, reason: "ai off" };
  if (!feat || !feat.enabled) return { ok: false, reason: "feature off" };
  if (!env.ANTHROPIC_API_KEY) return { ok: false, reason: "no ANTHROPIC_API_KEY" };
  const cap = ai.monthly_cap_cents || 800;
  const spent = await getMonthlySpendCents(env);
  if (spent >= cap) return { ok: false, reason: "shared cap hit" };
  return { ok: true, spent, cap };
}

async function sha1(str) {
  const buf = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(str));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
async function loadCache(env, key) {
  if (!env.DAILY_STATE) return null;
  try { return JSON.parse((await env.DAILY_STATE.get(key)) || "null"); } catch { return null; }
}
async function saveCache(env, key, obj) {
  if (!env.DAILY_STATE) return;
  try { await env.DAILY_STATE.put(key, JSON.stringify(obj)); } catch { /* best-effort */ }
}

// ---- Edition briefs ------------------------------------------------------------
const BRIEF_SCHEMA = {
  type: "object",
  properties: { brief: { type: "string" } },
  required: ["brief"],
  additionalProperties: false,
};

function briefsSystem(label, guidance, maxSentences) {
  const steer = (guidance || "").trim();
  return `You write the short "what you need to know" intro for the "${label}" section of one reader's personal daily brief. Given today's item titles in that section, write at most ${maxSentences || 3} sentences capturing what matters most in this area today. Name the actual things — specific, plain, calm. No preamble ("here's what's happening"), no clickbait, no spoilers. If nothing is genuinely notable, a single low-key sentence is fine.${steer ? `\n\nReader's guidance: ${steer}` : ""}`;
}

// Writes state.edition_briefs = { [editionId]: "2–3 sentence intro" }. Per-edition
// cache keyed by the sorted item-ids in that edition, so only a changed edition re-bills.
export async function editionBriefs(env, state, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.briefs || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  // The edition's visible body = its sections + "also" one-liners (both carry `edition`).
  const byEd = {};
  for (const s of state.sections || []) (byEd[s.edition] ||= []).push(...(s.items || []));
  for (const a of state.also || []) if (a.item) (byEd[a.edition] ||= []).push(a.item);

  const editions = (state.editions || []).filter((e) => (byEd[e.id] || []).length);
  if (!editions.length) return { degraded: false, reason: "nothing to brief" };

  const cache = (await loadCache(env, BRIEFS_KEY)) || { ts: 0, ed: {} };
  const throttled = now - (cache.ts || 0) < (feat.min_interval_min ?? 30) * 60000;
  const out = {};
  let spentCents = 0, calls = 0;

  for (const e of editions) {
    const list = byEd[e.id];
    const hash = await sha1(list.map((i) => i.id).sort().join(","));
    const prev = cache.ed[e.id];
    if (prev && prev.hash === hash) { out[e.id] = prev.text; continue; }          // unchanged → free
    if ((throttled || g.spent + spentCents >= g.cap) && prev) { out[e.id] = prev.text; continue; } // reuse last good
    if (throttled || g.spent + spentCents >= g.cap) continue;                     // no prior → skip this run
    const titles = list.slice(0, 12).map((i, n) => `${n + 1}. ${i.title}`).join("\n");
    try {
      const { parsed, cents } = await callModel(env, {
        system: briefsSystem(e.label, feat.guidance, feat.max_sentences),
        user: `Edition: ${e.label}\nToday's items:\n${titles}`,
        schema: BRIEF_SCHEMA, model: feat.model, max_tokens: 220,
      });
      spentCents += cents; calls++;
      if (parsed && parsed.brief) { out[e.id] = parsed.brief.trim(); cache.ed[e.id] = { hash, text: out[e.id] }; }
      else if (prev) out[e.id] = prev.text;
    } catch (_) { if (prev) out[e.id] = prev.text; }
  }

  if (calls > 0) { cache.ts = now; await saveCache(env, BRIEFS_KEY, cache); }
  if (spentCents > 0) await addSpendCents(env, spentCents);
  state.edition_briefs = out;
  return { degraded: false, reason: calls ? "ok" : "cached", spentCents, calls };
}

// ---- Editor's Picks ------------------------------------------------------------
const PICKS_SCHEMA = {
  type: "object",
  properties: {
    picks: {
      type: "array",
      items: {
        type: "object",
        properties: { id: { type: "string" }, why: { type: "string" } },
        required: ["id", "why"],
        additionalProperties: false,
      },
    },
  },
  required: ["picks"],
  additionalProperties: false,
};

function picksSystem(count, guidance) {
  const steer = (guidance || "").trim();
  return `You are the front-page editor of one reader's personal daily brief. From the candidate stories below (each with an id), choose the ones that genuinely belong on the front page and order them by importance to THIS reader — most important first, at most ${count || 8}. For each chosen story write a ONE-line "why it matters": max ~18 words, specific (name the actual stake/number/consequence), no hype, no spoilers. Drop anything that isn't real front-page material rather than padding to the limit. Return only the chosen stories, by their given id, in your chosen order.${steer ? `\n\nReader's guidance: ${steer}` : ""}`;
}

// Reorders state.headlines within the mechanical candidate set and attaches a `why`
// to each — never promotes an item the mechanical bar rejected. Cached by the sorted
// candidate ids. On any failure the mechanical headlines stand unchanged.
export async function editPicks(env, state, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.picks || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  const cands = (state.headline_candidates && state.headline_candidates.length)
    ? state.headline_candidates : (state.headlines || []);
  if (!cands.length) return { degraded: false, reason: "no candidates" };
  const byId = new Map(cands.map((c) => [c.id, c]));

  const hash = await sha1(cands.map((c) => c.id).sort().join(","));
  const cache = (await loadCache(env, PICKS_KEY)) || { ts: 0, hash: "", order: [] };
  const apply = (order) => {
    const picked = order.map((p) => { const it = byId.get(p.id); return it ? { ...it, why: p.why } : null; })
      .filter(Boolean).slice(0, feat.count || 8);
    if (picked.length) state.headlines = picked;
  };
  if (cache.hash === hash && cache.order.length) { apply(cache.order); return { degraded: false, reason: "cached" }; }
  if (now - (cache.ts || 0) < (feat.min_interval_min ?? 30) * 60000 && cache.order.length) {
    apply(cache.order); return { degraded: false, reason: "throttled" };
  }

  const lines = cands.map((c) => `${c.id} | (${c.domain_label || c.domain}) ${c.title}${c.hook ? " — " + c.hook : ""}`).join("\n");
  try {
    const { parsed, cents } = await callModel(env, {
      system: picksSystem(feat.count, feat.guidance),
      user: `Candidate stories:\n${lines}`,
      schema: PICKS_SCHEMA, model: feat.model, max_tokens: 700,
    });
    if (cents) await addSpendCents(env, cents);
    const order = (parsed && Array.isArray(parsed.picks)) ? parsed.picks.filter((p) => p && byId.has(p.id)) : [];
    if (order.length) {
      apply(order);
      await saveCache(env, PICKS_KEY, { ts: now, hash, order });
      return { degraded: false, reason: "ok", spentCents: cents };
    }
    return { degraded: false, reason: "no usable picks", spentCents: cents };
  } catch (e) {
    return { degraded: false, reason: "error: " + String(e.message || e).slice(0, 60) };
  }
}

// ---- Orchestrator --------------------------------------------------------------
// Runs the enabled editorial passes, mutating `state` in place, and returns a
// per-feature status blob for AI_STATUS_KEY / the health card. Near-instant no-op
// when the layer (or every feature) is off.
export async function augmentEditorial(env, state, items, config, now) {
  const ai = config.ai || {};
  const status = { ts: now };
  if (!ai.enabled) { delete state.headline_candidates; return status; }
  const p = await editPicks(env, state, items, config, now);
  status.picks = { on: !p.degraded, reason: p.reason, model: (ai.picks || {}).model };
  const b = await editionBriefs(env, state, items, config, now);
  status.briefs = { on: !b.degraded, reason: b.reason, model: (ai.briefs || {}).model };
  // headline_candidates was only needed by editPicks — drop it from the shipped state.
  delete state.headline_candidates;
  return status;
}
