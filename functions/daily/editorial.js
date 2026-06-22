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

// ---- Orchestrator --------------------------------------------------------------
// Runs the enabled editorial passes, mutating `state` in place, and returns a
// per-feature status blob for AI_STATUS_KEY / the health card. Near-instant no-op
// when the layer (or every feature) is off.
export async function augmentEditorial(env, state, items, config, now) {
  const ai = config.ai || {};
  const status = { ts: now };
  if (!ai.enabled) return status;
  const b = await editionBriefs(env, state, items, config, now);
  status.briefs = { on: !b.degraded, reason: b.reason, model: (ai.briefs || {}).model };
  return status;
}
