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
import { mergeLinks } from "./dedup.js";

const BRIEFS_KEY = "editorial:briefs";
const PICKS_KEY = "editorial:picks";
const DIGESTS_KEY = "editorial:digests";
const MERGE_KEY = "editorial:merge";
const EDITIONS_KEY = "editorial:editions";

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

// Shared "what the reader has configured" context, so every editorial pass anchors
// its judgement to the SAME weightings as the mechanical engine — the core entities,
// topic weights, signal tiers and rules — instead of competing with them. The
// per-pass `guidance` then layers on TOP as an additional steer, not a rival signal.
// Exported so enrichment anchors to the same weightings too.
export function profileContext(config) {
  const p = (config && config.profile) || {};
  const floor = (p.named_entity_floor || []).map((e) => e.label).join(", ");
  const topics = Object.entries(p.topic_weights || {})
    .sort((a, b) => (b[1].weight || 0) - (a[1].weight || 0))
    .map(([d, s]) => `${s.label || d} (${s.weight})`)
    .join(", ");
  const tiers = p.signal_tiers || {};
  const hi = (tiers.high || []).slice(0, 14).join(", ");
  const lo = (tiers.low || []).slice(0, 14).join(", ");
  const handling = Object.entries(p.special_handling || {})
    .map(([d, s]) => (s && s.note ? `${d}: ${s.note}` : null))
    .filter(Boolean).join("; ");
  return [
    floor && `Always-relevant core entities: ${floor}.`,
    topics && `Topic priorities, higher number = more important: ${topics}.`,
    hi && `High-signal words to favour: ${hi}.`,
    lo && `Low-signal words to discount: ${lo}.`,
    handling && `Editorial rules — ${handling}.`,
  ].filter(Boolean).join("\n") || "(no explicit priorities configured)";
}

// ---- Edition briefs ------------------------------------------------------------
const BRIEF_SCHEMA = {
  type: "object",
  properties: { brief: { type: "string" } },
  required: ["brief"],
  additionalProperties: false,
};

function briefsSystem(label, guidance, maxSentences, ctx) {
  const steer = (guidance || "").trim();
  return `You write the short "what you need to know" intro for the "${label}" section of one reader's personal daily brief.

The reader's configured priorities (use these to decide what matters most — they come from the reader's own settings):
${ctx}

Given today's item titles in that section, write at most ${maxSentences || 3} sentences capturing what matters most in this area today, consistent with those priorities. Name the actual things — specific, plain, calm. No preamble ("here's what's happening"), no clickbait, no spoilers. If nothing is genuinely notable, a single low-key sentence is fine.${steer ? `\n\nAdditional reader guidance (layer on top of the priorities above, do not override them): ${steer}` : ""}`;
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
        system: briefsSystem(e.label, feat.guidance, feat.max_sentences, profileContext(config)),
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

// Editor's Picks emits ONE combined headline line per pick (it replaces the raw
// title + separate "why it matters" — the reader wanted a single AI-written line).
const PICKS_LINE_SCHEMA = {
  type: "object",
  properties: {
    picks: {
      type: "array",
      items: {
        type: "object",
        properties: { id: { type: "string" }, line: { type: "string" } },
        required: ["id", "line"],
        additionalProperties: false,
      },
    },
  },
  required: ["picks"],
  additionalProperties: false,
};

function picksSystem(count, guidance, ctx) {
  const steer = (guidance || "").trim();
  return `You are the front-page editor of one reader's personal daily brief.

The reader's configured priorities — honour these FIRST (they come from the reader's own settings, and define what "important" means for this reader):
${ctx}

From the candidate stories below (each with an id), choose the ones that genuinely belong on the front page and order them by importance to THIS reader, consistent with the priorities above — most important first, at most ${count || 8}. For each chosen story write ONE punchy front-page line (max ~20 words) that states what happened AND why it matters to this reader in a single sentence — specific (name the actual stake/number/consequence), no hype, no spoilers, no separate label or prefix. This single line REPLACES the raw headline, so it must read as a complete headline on its own. Drop anything that isn't real front-page material rather than padding to the limit. Return only the chosen stories, by their given id, in your chosen order.${steer ? `\n\nAdditional reader guidance (layer on top of the priorities above, do not override them): ${steer}` : ""}`;
}

// Reorders state.headlines within the mechanical candidate set and attaches a single
// combined `headline_line` to each (it replaces the title at render) — never promotes
// an item the mechanical bar rejected. Cached by the sorted candidate ids. On any
// failure the mechanical headlines stand unchanged.
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
    const picked = order.map((p) => { const it = byId.get(p.id); return it ? { ...it, headline_line: p.line } : null; })
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
      system: picksSystem(feat.count, feat.guidance, profileContext(config)),
      user: `Candidate stories:\n${lines}`,
      schema: PICKS_LINE_SCHEMA, model: feat.model, max_tokens: 700,
    });
    if (cents) await addSpendCents(env, cents);
    const order = (parsed && Array.isArray(parsed.picks)) ? parsed.picks.filter((p) => p && p.line && byId.has(p.id)) : [];
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

// ---- Curate Top 20 -------------------------------------------------------------
const TOP20_KEY = "editorial:top20";

function top20System(count, guidance, ctx) {
  const steer = (guidance || "").trim();
  return `You are the editor of one reader's "Top ${count || 20} across everything" — the single trustworthy cross-domain feed spanning News, Sport, Gaming, Tech, Culture and every other area of the brief.

The reader's configured priorities — honour these FIRST (they define what "important" means for this reader):
${ctx}

From the candidate stories below (each with an id, across all areas), choose the ones that genuinely matter most to THIS reader and order them by importance — most important first, at most ${count || 20}, spanning areas (don't let one topic dominate). For each chosen story write a ONE-line "why it matters": max ~18 words, specific, no hype, no spoilers. Drop weak entries rather than padding to the limit. Return only the chosen stories, by their given id, in your chosen order.${steer ? `\n\nAdditional reader guidance (layer on top of the priorities above, do not override them): ${steer}` : ""}`;
}

// Curates state.top20 (orders + attaches `why`) from the wider top20_candidates pool,
// across the WHOLE brief — never promotes outside the candidate set. Same template as
// editPicks; cached by candidate ids. On any failure the mechanical Top 20 stands.
export async function curateTop20(env, state, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.top20 || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  const cands = (state.top20_candidates && state.top20_candidates.length)
    ? state.top20_candidates : (state.top20 || []);
  if (!cands.length) return { degraded: false, reason: "no candidates" };
  const byId = new Map(cands.map((c) => [c.id, c]));

  const hash = await sha1(cands.map((c) => c.id).sort().join(","));
  const cache = (await loadCache(env, TOP20_KEY)) || { ts: 0, hash: "", order: [] };
  const apply = (order) => {
    const picked = order.map((p) => { const it = byId.get(p.id); return it ? { ...it, why: p.why } : null; })
      .filter(Boolean).slice(0, feat.count || 20);
    if (picked.length) state.top20 = picked;
  };
  if (cache.hash === hash && cache.order.length) { apply(cache.order); return { degraded: false, reason: "cached" }; }
  if (now - (cache.ts || 0) < (feat.min_interval_min ?? 30) * 60000 && cache.order.length) {
    apply(cache.order); return { degraded: false, reason: "throttled" };
  }

  const lines = cands.map((c) => `${c.id} | (${c.domain_label || c.domain}) ${c.title}${c.hook ? " — " + c.hook : ""}`).join("\n");
  try {
    const { parsed, cents } = await callModel(env, {
      system: top20System(feat.count, feat.guidance, profileContext(config)),
      user: `Candidate stories (across all areas):\n${lines}`,
      schema: PICKS_SCHEMA, model: feat.model, max_tokens: 1200,
    });
    if (cents) await addSpendCents(env, cents);
    const order = (parsed && Array.isArray(parsed.picks)) ? parsed.picks.filter((p) => p && byId.has(p.id)) : [];
    if (order.length) {
      apply(order);
      await saveCache(env, TOP20_KEY, { ts: now, hash, order });
      return { degraded: false, reason: "ok", spentCents: cents };
    }
    return { degraded: false, reason: "no usable picks", spentCents: cents };
  } catch (e) {
    return { degraded: false, reason: "error: " + String(e.message || e).slice(0, 60) };
  }
}

// ---- Firehose digests ----------------------------------------------------------
const DIGEST_SCHEMA = {
  type: "object",
  properties: { digest: { type: "string" } },
  required: ["digest"],
  additionalProperties: false,
};

function digestsSystem(label, guidance, ctx) {
  const steer = (guidance || "").trim();
  return `You summarise the pile of lower-ranked "${label}" posts in one reader's daily brief into 1–2 sentences — the gist, so they can skip the pile or dive in.

The reader's configured priorities (use them to judge what in the pile is worth surfacing):
${ctx}

Lead with anything confirmed or genuinely major (per those priorities), then the themes / who-and-what. Specific and factual; no hype, no clickbait, no "various stories about". If the pile is trivial, say so briefly.${steer ? `\n\nAdditional reader guidance: ${steer}` : ""}`;
}

// Writes state.rollup_digests = { [domain]: "1–2 sentence synthesis" } for the
// below-fold "+N more in {topic}" tails. Per-domain cache keyed by the tail's ids.
export async function digestRollups(env, state, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.digests || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  const byDom = {};
  for (const it of state.below_fold || []) (byDom[it.domain] ||= []).push(it);
  const domains = Object.keys(byDom)
    .filter((d) => byDom[d].length >= 3) // only a real pile is worth a digest
    .sort((a, b) => byDom[b].length - byDom[a].length)
    .slice(0, feat.max_rollups || 12);
  if (!domains.length) return { degraded: false, reason: "nothing to digest" };

  const cache = (await loadCache(env, DIGESTS_KEY)) || { ts: 0, dom: {} };
  const throttled = now - (cache.ts || 0) < (feat.min_interval_min ?? 30) * 60000;
  const out = {};
  let spentCents = 0, calls = 0;

  for (const d of domains) {
    const list = byDom[d];
    const hash = await sha1(list.map((i) => i.id).sort().join(","));
    const prev = cache.dom[d];
    if (prev && prev.hash === hash) { out[d] = prev.text; continue; }
    if ((throttled || g.spent + spentCents >= g.cap) && prev) { out[d] = prev.text; continue; }
    if (throttled || g.spent + spentCents >= g.cap) continue;
    const label = list[0].domain_label || d;
    const titles = list.slice(0, 20).map((i, n) => `${n + 1}. ${i.title}`).join("\n");
    try {
      const { parsed, cents } = await callModel(env, {
        system: digestsSystem(label, feat.guidance, profileContext(config)),
        user: `Topic: ${label}\nThe ${list.length} lower-ranked posts:\n${titles}`,
        schema: DIGEST_SCHEMA, model: feat.model, max_tokens: 180,
      });
      spentCents += cents; calls++;
      if (parsed && parsed.digest) { out[d] = parsed.digest.trim(); cache.dom[d] = { hash, text: out[d] }; }
      else if (prev) out[d] = prev.text;
    } catch (_) { if (prev) out[d] = prev.text; }
  }

  if (calls > 0) { cache.ts = now; await saveCache(env, DIGESTS_KEY, cache); }
  if (spentCents > 0) await addSpendCents(env, spentCents);
  state.rollup_digests = out;
  return { degraded: false, reason: calls ? "ok" : "cached", spentCents, calls };
}

// ---- Smart merge ---------------------------------------------------------------
// The ONLY pass that removes content → off by default, and conservative: same-domain
// groups only, candidate-capped, no-op on any failure. Runs BEFORE enrich/buildState
// and MUTATES `items` in place (collapses each same-story group into its highest-
// confidence member, folding in source_count + links; drops the rest).
const MERGE_SCHEMA = {
  type: "object",
  properties: {
    groups: {
      type: "array",
      items: {
        type: "object",
        properties: { ids: { type: "array", items: { type: "string" } } },
        required: ["ids"],
        additionalProperties: false,
      },
    },
  },
  required: ["groups"],
  additionalProperties: false,
};

function mergeSystem(guidance) {
  const steer = (guidance || "").trim();
  return `You are de-duplicating a news brief. Below are stories, each with an id. Group together ONLY stories that report the SAME concrete event — the same signing, the same announcement, the same release, the same incident. Different events, different people, or merely the same topic are NOT the same story. Most stories are unique; return only genuine duplicate groups of 2+ ids. When in any doubt, do NOT group. Return groups as lists of ids.${steer ? `\n\nReader's guidance: ${steer}` : ""}`;
}

export async function smartMerge(env, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.merge || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  const cands = items
    .filter((i) => !i.muted && i.above_fold)
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, feat.max_candidates || 40);
  if (cands.length < 2) return { degraded: false, reason: "too few candidates" };

  const cache = (await loadCache(env, MERGE_KEY)) || { ts: 0, hash: "", groups: [] };
  const hash = await sha1(cands.map((c) => c.id).sort().join(","));
  const throttled = now - (cache.ts || 0) < (feat.min_interval_min ?? 60) * 60000;

  let groups;
  if (cache.hash === hash) groups = cache.groups || [];
  else if (throttled) groups = cache.groups || [];
  else {
    const lines = cands.map((c) => `${c.id} | (${c.domain}) ${c.title}`).join("\n");
    try {
      const { parsed, cents } = await callModel(env, {
        system: mergeSystem(feat.guidance),
        user: `Stories (id | (domain) title):\n${lines}`,
        schema: MERGE_SCHEMA, model: feat.model, max_tokens: 500,
      });
      if (cents) await addSpendCents(env, cents);
      groups = (parsed && Array.isArray(parsed.groups)) ? parsed.groups : [];
      await saveCache(env, MERGE_KEY, { ts: now, hash, groups });
    } catch (e) {
      return { degraded: false, reason: "error: " + String(e.message || e).slice(0, 50) };
    }
  }

  // Apply only to the candidate set (never touch an id outside it).
  const candIds = new Set(cands.map((c) => c.id));
  const byId = new Map(items.map((i) => [i.id, i]));
  const dropIds = new Set();
  for (const grp of groups) {
    const members = (grp.ids || [])
      .filter((id) => candIds.has(id))
      .map((id) => byId.get(id))
      .filter((m) => m && !dropIds.has(m.id));
    if (members.length < 2) continue;
    const dom = members[0].domain;
    if (members.some((m) => m.domain !== dom)) continue; // same-domain only
    members.sort((a, b) => b.confidence - a.confidence);
    const keep = members[0];
    for (let k = 1; k < members.length; k++) {
      const m = members[k];
      keep.source_count = (keep.source_count || 1) + (m.source_count || 1);
      keep.links = mergeLinks([...(keep.links || [])], m.links || []);
      dropIds.add(m.id);
    }
  }
  if (dropIds.size) {
    for (let i = items.length - 1; i >= 0; i--) if (dropIds.has(items[i].id)) items.splice(i, 1);
  }
  return { degraded: false, reason: dropIds.size ? "merged " + dropIds.size : "nothing to merge", dropped: dropIds.size };
}

// ---- Order every edition -------------------------------------------------------
// Reorders the items WITHIN each domain section by AI importance (option a — keeps
// the section structure, labels and fairness caps exactly as buildState made them).
// One call per edition; skips News & Money (its date order is intentional). Off by
// default. On any failure / omitted ids, items keep their mechanical confidence order.
const ORDER_SCHEMA = {
  type: "object",
  properties: { order: { type: "array", items: { type: "string" } } },
  required: ["order"],
  additionalProperties: false,
};

function orderEditionsSystem(label, guidance, ctx) {
  const steer = (guidance || "").trim();
  return `You order the items in the "${label}" area of one reader's daily brief by importance to THIS reader.

The reader's configured priorities — honour these FIRST:
${ctx}

Below are the items, each with an id. Return EVERY given id exactly once, ordered most-important-first per those priorities. Return only ids, no commentary.${steer ? `\n\nAdditional reader guidance: ${steer}` : ""}`;
}

const ORDER_SKIP = new Set(["news_money"]); // date-ordered by contract

export async function orderEditions(env, state, items, config, now) {
  const ai = config.ai || {};
  const feat = ai.editions || {};
  const g = await gate(env, ai, feat);
  if (!g.ok) return { degraded: true, reason: g.reason };

  const byEd = {};
  for (const s of state.sections || []) {
    if (ORDER_SKIP.has(s.edition)) continue;
    (byEd[s.edition] ||= []).push(s);
  }
  const editions = (state.editions || []).filter((e) => !ORDER_SKIP.has(e.id) && (byEd[e.id] || []).length);
  if (!editions.length) return { degraded: false, reason: "nothing to order" };

  const cache = (await loadCache(env, EDITIONS_KEY)) || { ts: 0, ed: {} };
  const throttled = now - (cache.ts || 0) < (feat.min_interval_min ?? 30) * 60000;
  let spentCents = 0, calls = 0;

  for (const e of editions) {
    const secs = byEd[e.id];
    const all = [];
    for (const s of secs) for (const it of s.items) all.push(it);
    if (all.length < 2) continue;
    const hash = await sha1(all.map((i) => i.id).sort().join(","));
    const prev = cache.ed[e.id];
    let order = null;
    if (prev && prev.hash === hash) order = prev.order;
    else if ((throttled || g.spent + spentCents >= g.cap) && prev) order = prev.order;
    else if (throttled || g.spent + spentCents >= g.cap) continue;
    else {
      const lines = all.map((i) => `${i.id} | (${i.domain_label || i.domain}) ${i.title}`).join("\n");
      try {
        const { parsed, cents } = await callModel(env, {
          system: orderEditionsSystem(e.label, feat.guidance, profileContext(config)),
          user: `Items in ${e.label}:\n${lines}`,
          schema: ORDER_SCHEMA, model: feat.model, max_tokens: Math.min(1500, 200 + all.length * 8),
        });
        spentCents += cents; calls++;
        order = (parsed && Array.isArray(parsed.order)) ? parsed.order : null;
        if (order) cache.ed[e.id] = { hash, order };
      } catch (_) { order = prev ? prev.order : null; }
    }
    if (order && order.length) {
      const rank = new Map(order.map((id, i) => [id, i]));
      for (const s of secs) s.items.sort((a, b) => (rank.get(a.id) ?? 1e9) - (rank.get(b.id) ?? 1e9));
    }
  }

  if (calls > 0) { cache.ts = now; await saveCache(env, EDITIONS_KEY, cache); }
  if (spentCents > 0) await addSpendCents(env, spentCents);
  return { degraded: false, reason: calls ? "ok" : "cached", spentCents, calls };
}

// ---- Orchestrator --------------------------------------------------------------
// Runs the enabled editorial passes, mutating `state` in place, and returns a
// per-feature status blob for AI_STATUS_KEY / the health card. Near-instant no-op
// when the layer (or every feature) is off.
export async function augmentEditorial(env, state, items, config, now) {
  const ai = config.ai || {};
  const status = { ts: now };
  if (!ai.enabled) { delete state.headline_candidates; delete state.top20_candidates; return status; }
  const p = await editPicks(env, state, items, config, now);
  status.picks = { on: !p.degraded, reason: p.reason, model: (ai.picks || {}).model };
  const t = await curateTop20(env, state, items, config, now);
  status.top20 = { on: !t.degraded, reason: t.reason, model: (ai.top20 || {}).model };
  const b = await editionBriefs(env, state, items, config, now);
  status.briefs = { on: !b.degraded, reason: b.reason, model: (ai.briefs || {}).model };
  const d = await digestRollups(env, state, items, config, now);
  status.digests = { on: !d.degraded, reason: d.reason, model: (ai.digests || {}).model };
  const o = await orderEditions(env, state, items, config, now);
  status.editions = { on: !o.degraded, reason: o.reason, model: (ai.editions || {}).model };
  // Candidate pools were only needed by the curation passes — drop from shipped state.
  delete state.headline_candidates;
  delete state.top20_candidates;
  return status;
}
