// The Signal — daily: config surface (§6).
//
// Flat rule: anything tunable lives in KV (DAILY_CONFIG), is read live by the
// Worker each run, and is editable in-app — never a deploy. This module owns the
// default config and the load/save helpers. On first read the defaults are
// seeded into KV so the in-app editor has something concrete to tune.

import { STARTER_FEEDS, STARTER_BLUESKY } from "./feeds.js";
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
    enrichment: {
      enabled: true,
      model: "claude-haiku-4-5",
      shortlist_size: 36, // ~top 30–40
      monthly_spend_cap_cents: 500, // $5/mo; on hit, auto-fall back to Tier 1
      batch: false, // synchronous per-run; flip on to use the Batch API
    },
    push: {
      // Daily = silent precache + app badge (no push). Weekly = the push.
      daily_badge: true,
    },
    sources: STARTER_FEEDS,
    bluesky: STARTER_BLUESKY,
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
  return mergeConfig(def, saved);
}

export async function saveConfig(env, config) {
  if (!env.DAILY_CONFIG) throw new Error("DAILY_CONFIG KV binding missing");
  config.version = 2;
  await env.DAILY_CONFIG.put(CONFIG_KEY, JSON.stringify(config));
  return config;
}

// Shallow-merge top-level keys; saved values win. Nested objects (enrichment,
// push, profile) are taken wholesale from saved when present so in-app edits are
// authoritative, but missing nested keys fall back to defaults.
function mergeConfig(def, saved) {
  const out = { ...def, ...saved };
  out.enrichment = { ...def.enrichment, ...(saved.enrichment || {}) };
  out.push = { ...def.push, ...(saved.push || {}) };
  if (saved.profile) {
    out.profile = {
      named_entity_floor: saved.profile.named_entity_floor || def.profile.named_entity_floor,
      topic_weights: saved.profile.topic_weights || def.profile.topic_weights,
      special_handling: saved.profile.special_handling || def.profile.special_handling,
      mutes: saved.profile.mutes || def.profile.mutes,
    };
  }
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
