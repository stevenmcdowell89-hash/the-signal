// The Signal — daily: pipeline orchestration (§3).
//
// One poll run: ingest → dedup/cluster → persist (union across polls) →
// baseline/velocity/profile/fold scoring → optional Tier-2 enrichment →
// render state to KV → prune → log. The Cron Trigger and the manual
// /api/daily/run endpoint both call run().

import { loadConfig } from "./config.js";
import {
  initSchema, bulkUpsertItems, getWindowItems, logRun, prune,
} from "./db.js";
import { ingestAll } from "./ingest.js";
import { clusterEntries } from "./dedup.js";
import { scoreBatch } from "./score.js";
import { enrichShortlist } from "./enrich.js";
import { buildState } from "./render.js";

const STATE_KEY = "state";
// Items live in D1 for 14 days (dedup memory); the brief itself scores+renders a
// tighter recent window — the daily is fast-decay ("what happened"). The window
// is config-driven (recency.score_window_days) so it's tunable in-app.
const DEFAULT_SCORE_WINDOW_DAYS = 2;
// Health blobs the settings page reads via /api/health.
export const SOURCE_STATUS_KEY = "source_status";
export const ENRICH_STATUS_KEY = "enrich_status";

// Map a D1 row to the in-memory item shape the engine expects.
function rowToItem(row, weightBySource) {
  let links = [];
  try { links = JSON.parse(row.links || "[]"); } catch {}
  return {
    id: row.id,
    canonical_url: row.canonical_url,
    title: row.title,
    summary: row.summary || "",
    domain: row.domain,
    source: row.source,
    source_type: row.source_type,
    links,
    first_seen: row.first_seen,
    last_seen: row.last_seen,
    published: row.published,
    rawScore: row.raw_score || 0,
    weight: weightBySource.get(row.source) ?? 0.5,
    baseline_score: row.baseline_score || 0,
    profile_score: row.profile_score || 0,
    velocity: row.velocity || 0,
    confidence: row.confidence || 0,
    above_fold: !!row.above_fold,
    entity_floor: !!row.entity_floor,
    muted: !!row.muted,
    register: row.register || null,
    hook: row.hook || null,
    enriched: !!row.enriched,
    enrich_hash: row.enrich_hash || null,
  };
}

export async function run(env, { trigger } = {}) {
  const now = Date.now();
  const config = await loadConfig(env);

  if (!env.DAILY_DB) throw new Error("DAILY_DB (D1) binding missing");
  if (!env.DAILY_STATE) throw new Error("DAILY_STATE KV binding missing");
  const db = env.DAILY_DB;
  await initSchema(db);

  // 1) Ingest every tagged source.
  const { entries, live, dead } = await ingestAll(config);
  const scanned = entries.length;

  // Record per-source liveness for the feed-health view (§E): which sources
  // returned items this poll vs errored/empty. Counts come from D1 at read time.
  const liveSet = new Set(live);
  const sourceStatus = {};
  for (const id of [...live, ...dead]) {
    sourceStatus[id] = { ok: liveSet.has(id), ts: now };
  }
  for (const id of live) {
    sourceStatus[id].count_this_poll = entries.filter((e) => e.sourceId === id).length;
  }
  if (env.DAILY_STATE) {
    await env.DAILY_STATE.put(SOURCE_STATUS_KEY, JSON.stringify({ ts: now, sources: sourceStatus }));
  }

  // 2) Dedup / cluster this poll's entries (retain all links).
  const clustered = await clusterEntries(entries);

  // 3) Persist — union across polls (one batched upsert, not N awaits). New
  //    clusters insert; repeats refresh last_seen and keep the max raw_score so
  //    an early spike survives a later lull.
  await bulkUpsertItems(
    db,
    clustered.map((it) => ({
      id: it.id,
      canonical_url: it.canonical_url,
      title: it.title,
      summary: it.summary || "",
      domain: it.domain,
      source: it.source,
      source_type: it.source_type,
      links: it.links,
      first_seen: now,
      last_seen: now,
      published: it.published,
      raw_score: it.rawScore,
    }))
  );

  // 4) Load the recent in-window set (persisted + just-upserted) and score it
  //    in memory. The recomputable score fields are NOT written back — every
  //    poll recomputes them; only enrichment (hooks) is persisted, separately.
  const weightBySource = new Map();
  const domainBySource = new Map();
  for (const s of config.sources || []) { weightBySource.set(s.id, s.weight); domainBySource.set(s.id, s.domain); }
  for (const b of config.bluesky || []) { weightBySource.set(b.id, b.weight); domainBySource.set(b.id, b.domain); }

  const windowDays = (config.recency && config.recency.score_window_days) || DEFAULT_SCORE_WINDOW_DAYS;
  const sinceMs = now - 1000 * 60 * 60 * 24 * windowDays;
  const rows = await getWindowItems(db, sinceMs);
  const items = rows.map((r) => {
    const it = rowToItem(r, weightBySource);
    it.feed_domain = domainBySource.get(r.source) || it.domain; // authoritative
    return it;
  });

  await scoreBatch(db, items, config, now);

  // 5) Tier-2 enrichment (optional) on the shortlist.
  const enr = await enrichShortlist(env, db, items, config, now);

  // Record enrichment status for the AI-health card (§E).
  await env.DAILY_STATE.put(ENRICH_STATUS_KEY, JSON.stringify({
    ts: now,
    on: !enr.degraded,
    reason: enr.reason,
    model: (config.enrichment || {}).model || "claude-haiku-4-5",
    enriched: enr.enriched,
    spent_cents: enr.spentCents,
  }));

  // 6) Render the living surface and write it to KV.
  const meta = {
    scanned,
    sources: live.length,
    enrichment: { on: !enr.degraded, reason: enr.reason },
  };
  const state = buildState(items, meta, now, config);
  await env.DAILY_STATE.put(STATE_KEY, JSON.stringify(state));

  // 7) Prune the window + log the run.
  await prune(db, now);
  await logRun(db, {
    ts: now,
    scanned,
    kept: state.footer.kept,
    sources: live.length,
    enriched: enr.enriched,
    enrich_on: !enr.degraded,
    spend_cents: enr.spentCents,
    notes: `dead:${dead.length} ${trigger || "manual"}`,
  });

  return {
    ok: true,
    scanned,
    kept: state.footer.kept,
    sources_live: live.length,
    sources_dead: dead,
    enriched: enr.enriched,
    spend_cents: Math.round(enr.spentCents * 100) / 100,
    enrichment: meta.enrichment,
  };
}

export async function getState(env) {
  if (!env.DAILY_STATE) return null;
  const raw = await env.DAILY_STATE.get(STATE_KEY);
  return raw ? JSON.parse(raw) : null;
}
