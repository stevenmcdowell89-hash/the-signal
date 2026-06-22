// The Signal — daily: config surface (§6).
//
// Flat rule: anything tunable lives in KV (DAILY_CONFIG), is read live by the
// Worker each run, and is editable in-app — never a deploy. This module owns the
// default config and the load/save helpers. On first read the defaults are
// seeded into KV so the in-app editor has something concrete to tune.

import { STARTER_FEEDS, STARTER_BLUESKY, STARTER_REDDIT } from "./feeds.js";
import { PROFILE } from "./profile.js";

export const CONFIG_KEY = "config";

export function defaultConfig() {
  return {
    version: 2,
    // Cron cadence is also declared in wrangler.jsonc (the trigger), but the
    // run reads this to decide whether to skip (e.g. if turned down in-app).
    cadence_hours: 3,
    // The fold (§3.7): above-fold = items over this confidence threshold.
    fold_threshold: 0.6,
    headline_max: 8, // Headlines shows up to this many "most important right now"
    // Content-led ranking knobs (§3.6). Interest relevance leads; source weight is
    // a light tiebreaker (was a dominant ±40% multiplier). Keyword signal tiers
    // (profile.signal_tiers) multiply the interest score. All in-app editable.
    scoring: {
      profile_weight: 0.70,   // interest relevance share of base (was 0.65)
      baseline_weight: 0.30,  // source-significance share of base (was 0.35)
      weight_floor: 0.85,     // source-weight multiplier base…
      weight_span: 0.15,      // …+ this × weight (so weight is ±7.5%, not ±40%)
      signal_high: 1.6,       // title carries a high-signal word → ×this
      signal_low: 0.5,        // title carries a low-signal word → ×this
      headline_signal_bonus: 0.15, // additive Headlines bump for high-signal items
      source_cap: 3,          // keep this many from one feed per topic at full strength…
      source_cap_penalty: 0.6, // …then ×this^rank on the tail (anti-firehose, in scoring)
    },
    // Recency (the daily is fast-decay — "what happened today"). One coherent
    // decay signal drives confidence, the named-entity floor, Top Catches
    // eligibility, and the below-fold window. All hours.
    recency: {
      half_life_hours: 20,        // confidence halves every N hours of age
      floor_fresh_hours: 36,      // entity-floor items only forced above-fold if this fresh…
      velocity_fresh_keep: 0.25,  // …or moving at least this fast (normalised 0–1)
      top_catch_max_hours: 30,    // Top Catches strip only admits items this fresh
      top_catch_recency_blend: 0.35, // Top Catches order = conf blended with recency
      undated_penalty_hours: 36,  // feeds with no date are treated as this much older
      score_window_days: 2,       // the brief scores/renders this recent a window
    },
    enrichment: {
      enabled: true,
      model: "claude-haiku-4-5",
      shortlist_size: 100, // top-N items judged per run (mini-batched, so far cheaper than 1/call)
      batch_size: 10, // items per Anthropic call (one cached system block amortised across the batch)
      monthly_spend_cap_cents: 500, // $5/mo; on hit, auto-fall back to Tier 1
      batch: false, // (reserved) async Batch API — orthogonal to the synchronous mini-batch above
      guidance: "", // reader-authored steer appended to the hook prompt (Settings)
    },
    // ---- AI editorial layer (§ AI) ----
    // A quality layer ON TOP of the mechanical brief — never a dependency. With
    // `enabled:false` (or no API key, or the shared cap hit) the brief is exactly
    // the mechanical one. Each pass is independently toggleable and fully
    // configurable in-app, including a plain-English `guidance` steer for HOW it
    // prioritises / groups / summarises. All passes draw on ONE shared monthly cap.
    ai: {
      enabled: true,
      monthly_cap_cents: 800, // shared across enrichment + all editorial passes
      // Editor's Picks — curate + order the front-page Headlines, write "why it matters".
      picks: {
        enabled: true,
        model: "claude-haiku-4-5",
        count: 8,
        min_interval_min: 30,
        guidance: "Lead with what genuinely changes the reader's day or world — confirmed, consequential developments over speculation. Order by importance to this reader; a precise reason to care is the bar.",
      },
      // Firehose digests — synthesise each "+N more in {topic}" tail.
      digests: {
        enabled: true,
        model: "claude-haiku-4-5",
        max_rollups: 12,
        min_interval_min: 30,
        guidance: "Synthesise the related posts factually in 1–2 sentences: lead with anything confirmed, then the gist of the rest. No hype, no clickbait.",
      },
      // Edition briefs — a short "what you need to know" intro per edition.
      briefs: {
        enabled: true,
        model: "claude-haiku-4-5",
        max_sentences: 3,
        min_interval_min: 30,
        guidance: "Open with the single most important thing in this area today, then one or two others worth knowing. Plain, calm, specific.",
      },
      // Smart merge — collapse same-story dupes the mechanical dedup missed. RISKIEST
      // (removes content) → off by default.
      merge: {
        enabled: false,
        model: "claude-haiku-4-5",
        max_candidates: 40,
        min_interval_min: 60,
        guidance: "Treat two items as the same story only when they report the same concrete event (same signing, same announcement, same release). Different people or events are different stories.",
      },
    },
    push: {
      // Daily = silent precache + app badge (no push). Weekly = the push.
      daily_badge: true,
      // Significance-gated push: a single nudge only when something genuinely
      // big lands (a fresh entity-floor catch or a high-confidence top catch),
      // throttled so quiet days stay silent. Not a fixed daily alarm.
      significant: {
        enabled: true,
        min_confidence: 0.85,   // a top catch this confident counts as "big"…
        fresh_hours: 12,        // …if first seen within this window
        min_interval_hours: 8,  // never push more often than this
      },
    },
    sources: [...STARTER_FEEDS, ...STARTER_REDDIT],
    bluesky: STARTER_BLUESKY,
    // Editions — the few big reading areas the brief groups into. Ordered; each
    // topic carries an `edition` id (profile.topic_weights[d].edition) pointing
    // here. Any domain with no/unknown edition falls into the `more` catch-all.
    // In-app editable; Headlines, Top 20 and Communities are fixed views, not
    // listed here.
    editions: [
      { id: "news_money", label: "News & Money" },
      { id: "sport", label: "Sport" },
      { id: "gaming_tech", label: "Gaming & Tech" },
      { id: "culture", label: "Culture & Books" },
      { id: "more", label: "More" },
    ],
    profile: PROFILE,
    // Extra mutes layered on top of profile.mutes, editable separately in-app.
    mutes: [],
  };
}

// Load live config from KV, seeding defaults on first read. Always merge over
// defaults so new fields added in a deploy appear without wiping user edits.
export async function loadConfig(env) {
  const def = defaultConfig();
  if (!env.DAILY_CONFIG) return def;
  const raw = await env.DAILY_CONFIG.get(CONFIG_KEY);
  if (!raw) {
    await env.DAILY_CONFIG.put(CONFIG_KEY, JSON.stringify(def));
    return def;
  }
  let saved;
  try {
    saved = JSON.parse(raw);
  } catch {
    return def;
  }
  const merged = mergeConfig(def, saved);
  let dirty = false;
  // If the saved profile predated the current profile_version we just re-seeded
  // it from code (in mergeConfig). Persist that so the editor + next run read the
  // fresh profile and we don't re-seed on every request.
  const savedVer = (saved.profile && saved.profile.profile_version) || 0;
  if (savedVer < (def.profile.profile_version || 0)) dirty = true;
  // One-time: the Reddit set was unioned in DISABLED. The `.rss` path needs no
  // approval and the reader asked for it on, so enable the reddit sources once.
  // A marker stops it re-running, so a later manual disable in Settings sticks.
  merged.migrations = merged.migrations || {};
  if (!merged.migrations.reddit_rss_v1) {
    for (const s of merged.sources || []) if (s.type === "reddit") s.enabled = true;
    merged.migrations.reddit_rss_v1 = true;
    dirty = true;
  }
  // v2: the per-subreddit Reddit sources tripped Reddit's rate limit (36 requests
  // a poll). Replace them with the per-domain multireddit defaults: drop any
  // reddit source not in the current default set (the union already added the new
  // ones), and make sure the survivors are enabled.
  if (!merged.migrations.reddit_multi_v2) {
    const defRedditIds = new Set((def.sources || []).filter((s) => s.type === "reddit").map((s) => s.id));
    merged.sources = (merged.sources || []).filter((s) => s.type !== "reddit" || defRedditIds.has(s.id));
    for (const s of merged.sources) if (s.type === "reddit") s.enabled = true;
    merged.migrations.reddit_multi_v2 = true;
    dirty = true;
  }
  // v3: replace the per-domain multireddits with per-subreddit sources that carry
  // a size `tier`. Drop reddit sources not in the new default set (the union added
  // the new per-sub ones); default any missing tier to "small".
  if (!merged.migrations.reddit_tier_v3) {
    const defReddit = new Map((def.sources || []).filter((s) => s.type === "reddit").map((s) => [s.id, s]));
    merged.sources = (merged.sources || []).filter((s) => s.type !== "reddit" || defReddit.has(s.id));
    for (const s of merged.sources) {
      if (s.type === "reddit") { s.enabled = true; if (!s.tier) s.tier = (defReddit.get(s.id) || {}).tier || "small"; }
    }
    merged.migrations.reddit_tier_v3 = true;
    dirty = true;
  }
  // Drop the home_selfhosting domain (no longer an interest): the topic itself
  // leaves via the profile_version re-seed, but its two seed feeds were unioned
  // into saved configs, so remove any source tagged to that domain here.
  if (!merged.migrations.drop_selfhosting_v1) {
    merged.sources = (merged.sources || []).filter((s) => s.domain !== "home_selfhosting");
    merged.migrations.drop_selfhosting_v1 = true;
    dirty = true;
  }
  if (dirty) {
    try { await env.DAILY_CONFIG.put(CONFIG_KEY, JSON.stringify(merged)); } catch { /* best-effort */ }
  }
  return merged;
}

export async function saveConfig(env, config) {
  if (!env.DAILY_CONFIG) throw new Error("DAILY_CONFIG KV binding missing");
  config.version = 2;
  // Stamp the saved profile as current so an in-app edit isn't treated as stale
  // and re-seeded away on the next load.
  if (config.profile) config.profile.profile_version = defaultConfig().profile.profile_version;
  await env.DAILY_CONFIG.put(CONFIG_KEY, JSON.stringify(config));
  return config;
}

// Shallow-merge top-level keys; saved values win, missing nested keys fall back
// to defaults. The whole profile (floor, topics, rules, mutes) is user-editable
// in-app and the saved values win — UNLESS the saved profile predates the
// current profile_version, in which case the code defaults re-seed (so engine
// improvements reach an existing config without a manual re-edit). Bump
// PROFILE.profile_version in code whenever a default change must override a
// saved profile.
function unionById(saved, def) {
  // Keep the saved entries (user edits win) and append any default entry whose id
  // isn't present — so a deploy that adds sources (e.g. the Reddit set) reaches an
  // existing saved config without clobbering the reader's own list.
  const byId = new Map((saved || []).map((s) => [s.id, s]));
  for (const d of def || []) if (!byId.has(d.id)) byId.set(d.id, d);
  return [...byId.values()];
}

function mergeConfig(def, saved) {
  const out = { ...def, ...saved };
  out.sources = unionById(saved.sources || def.sources, def.sources);
  out.enrichment = { ...def.enrichment, ...(saved.enrichment || {}) };
  out.recency = { ...def.recency, ...(saved.recency || {}) };
  out.scoring = { ...def.scoring, ...(saved.scoring || {}) };
  out.ai = { ...def.ai, ...(saved.ai || {}) };
  for (const k of ["picks", "digests", "briefs", "merge"]) {
    out.ai[k] = { ...def.ai[k], ...((saved.ai || {})[k] || {}) };
  }
  out.push = { ...def.push, ...(saved.push || {}) };
  out.push.significant = { ...def.push.significant, ...((saved.push || {}).significant || {}) };
  const sp = saved.profile;
  const fresh = sp && (sp.profile_version || 0) >= (def.profile.profile_version || 0);
  const pick = (key) => (fresh && sp[key] != null ? sp[key] : def.profile[key]);
  out.profile = {
    profile_version: def.profile.profile_version,
    named_entity_floor: pick("named_entity_floor"),
    topic_weights: pick("topic_weights"),
    special_handling: pick("special_handling"),
    signal_tiers: pick("signal_tiers"),
    mutes: pick("mutes"),
  };
  return out;
}

// ---- Monthly spend ledger (§3 toggle + spend cap) ----
function spendKey(d = new Date()) {
  return `spend:${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

export async function getMonthlySpendCents(env) {
  if (!env.DAILY_STATE) return 0;
  const raw = await env.DAILY_STATE.get(spendKey());
  return raw ? Number(raw) || 0 : 0;
}

export async function addSpendCents(env, cents) {
  if (!env.DAILY_STATE) return;
  const cur = await getMonthlySpendCents(env);
  await env.DAILY_STATE.put(spendKey(), String(cur + cents), {
    // Keep two months so month rollover never reads stale; expire after ~70d.
    expirationTtl: 60 * 60 * 24 * 70,
  });
}
