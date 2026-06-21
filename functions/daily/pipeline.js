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
export const RUN_PROGRESS_KEY = "run_progress";

// Best-effort run progress for the Settings "Run now" indicator (read via
// /api/daily/run-status). Never blocks or throws the run.
function setProgress(env, phase, done, total) {
  try {
    env.DAILY_STATE.put(RUN_PROGRESS_KEY, JSON.stringify({ phase, done, total, ts: Date.now() })).catch(() => {});
  } catch (_) {}
}

const REDDIT_CURSOR_KEY = "reddit_cursor";
const REDDIT_FETCH_TS_KEY = "reddit_fetch_ts"; // last time we rolled the reddit rotation
const REDDIT_SLICE = 6; // subreddits fetched per tick (≈ full cycle over ~3h)
const REDDIT_DEBOUNCE_MS = 5 * 60 * 1000; // manual "Run now" won't re-roll reddit inside this window

// The next rotating slice of enabled reddit subs (a Set of source ids). Advances
// and persists a cursor so successive ticks cover them all — a rolling refresh
// that never bursts Reddit's rate limit.
async function nextRedditSlice(env, config) {
  const subs = (config.sources || [])
    .filter((s) => s.type === "reddit" && s.enabled !== false)
    .map((s) => s.id)
    .sort();
  if (!subs.length) return new Set();
  let cursor = 0;
  try { cursor = parseInt((await env.DAILY_STATE.get(REDDIT_CURSOR_KEY)) || "0", 10) || 0; } catch (_) {}
  cursor = ((cursor % subs.length) + subs.length) % subs.length;
  const slice = [];
  for (let i = 0; i < Math.min(REDDIT_SLICE, subs.length); i++) slice.push(subs[(cursor + i) % subs.length]);
  try { await env.DAILY_STATE.put(REDDIT_CURSOR_KEY, String((cursor + REDDIT_SLICE) % subs.length)); } catch (_) {}
  return new Set(slice);
}
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
    source_count: row.source_count || 1,
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

  // 1) Ingest every fast source (RSS/HN) + a ROTATING slice of Reddit subs. The
  //    cron fires every 30 min and each tick fetches the next ~6 subreddits, so
  //    Reddit is a rolling update that never bursts its rate limit (a full cycle
  //    is ~3h). `env` carries optional Reddit OAuth secrets.
  //    The cron always rolls Reddit; a MANUAL "Run now" debounces it (skips Reddit
  //    if we rolled within the last few minutes) so repeated presses can't re-burst
  //    Reddit's shared-IP rate limit — RSS/HN still refresh and the brief re-renders.
  const isCron = trigger === "cron";
  let lastRedditTs = 0;
  try { lastRedditTs = parseInt((await env.DAILY_STATE.get(REDDIT_FETCH_TS_KEY)) || "0", 10) || 0; } catch (_) {}
  const rollReddit = isCron || (now - lastRedditTs) >= REDDIT_DEBOUNCE_MS;
  const redditSlice = rollReddit ? await nextRedditSlice(env, config) : new Set(); // empty Set = fetch no reddit this run
  if (rollReddit) { try { await env.DAILY_STATE.put(REDDIT_FETCH_TS_KEY, String(now)); } catch (_) {} }

  setProgress(env, rollReddit ? "polling sources" : "polling sources (reddit rolled recently — skipping)", 0, 1);
  const { entries, live, dead, reasons } = await ingestAll(config, env, (d, t) => setProgress(env, "polling sources", d, t), redditSlice);
  const scanned = entries.length;

  // Record per-source liveness for the feed-health view (§E): which sources
  // returned items this poll vs errored/empty. MERGE over the previous blob — a
  // Reddit sub not in this tick's rotation keeps its last-known state instead of
  // vanishing (which would churn the health view as the rotation moves).
  const liveSet = new Set(live);
  let sourceStatus = {};
  try {
    const prev = JSON.parse((await env.DAILY_STATE.get(SOURCE_STATUS_KEY)) || "null");
    if (prev && prev.sources) sourceStatus = prev.sources;
  } catch (_) {}
  // Per sub we keep a small HISTORY so a red sub is legible over time, not just
  // "tried Nm ago" (which a failed re-attempt resets): `last_ok` = last time it
  // actually returned items, `fail_since` = start of the current failing streak
  // (cleared on any success), `fails` = consecutive failures. This is what answers
  // "has it ever worked / is it being retried / has it been down 4h or 4d?".
  for (const id of [...live, ...dead]) {
    const ok = liveSet.has(id);
    const prevEntry = sourceStatus[id] || {};
    sourceStatus[id] = {
      ok,
      ts: now,
      reason: (reasons && reasons[id]) || (ok ? "ok" : "empty"),
      last_ok: ok ? now : (prevEntry.last_ok || null),
      fail_since: ok ? null : (prevEntry.fail_since || now),
      fails: ok ? 0 : ((prevEntry.fails || 0) + 1),
    };
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
      source_count: it.memberSources ? it.memberSources.length : 1,
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

  setProgress(env, "scoring", 1, 1);
  await scoreBatch(db, items, config, now);

  // 5) Tier-2 enrichment (optional) on the shortlist.
  setProgress(env, "enriching", 1, 1);
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

  // 6) Render the living surface and write it to KV. The footer's "scanned" is
  //    the brief's WINDOW population (items considered over the score window), not
  //    this single poll's raw ingest — otherwise "kept" (a windowed count) can
  //    exceed a one-poll "scanned". kept ≤ scanned now holds. The run log + return
  //    keep the per-poll `scanned` for operational accounting.
  const meta = {
    scanned: items.length,
    sources: live.length,
    enrichment: { on: !enr.degraded, reason: enr.reason },
  };
  setProgress(env, "rendering", 1, 1);
  const state = buildState(items, meta, now, config);
  await env.DAILY_STATE.put(STATE_KEY, JSON.stringify(state));
  setProgress(env, "done", 1, 1);

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
