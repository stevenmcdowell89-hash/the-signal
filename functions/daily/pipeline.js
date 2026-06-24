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
import { augmentEditorial, smartMerge } from "./editorial.js";
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
const REDDIT_BATCH_KEY = "reddit_batch"; // {ids, pending, attempts} for the in-flight batch
const REDDIT_FETCH_TS_KEY = "reddit_fetch_ts"; // last time we rolled the reddit rotation
const REDDIT_SLICE = 6; // subreddits per batch
const REDDIT_MAX_ATTEMPTS = 3; // re-attempts of a batch's failures before advancing (~30 min at a 10-min cron)
const REDDIT_DEBOUNCE_MS = 5 * 60 * 1000; // manual "Run now" won't re-roll reddit inside this window

// Pick this tick's reddit subs as a RETRY-AWARE rotating batch. A batch is a slice
// of ~6 subs; each tick re-attempts only the ones in the batch that are STILL
// failing, for up to REDDIT_MAX_ATTEMPTS ticks (~30 min at a 10-min cron), then
// advances the cursor to the next slice. So a throttled sub gets several fresh
// shots at Reddit's shared-IP limit within half an hour instead of waiting a whole
// ~3h rotation; subs that succeed drop out of the batch immediately and keep their
// green state. Returns { slice:Set<id>, save(liveSet) } — call save() after ingest
// so the batch's pending set + attempt count carry to the next tick.
async function redditBatch(env, config) {
  const subs = (config.sources || [])
    .filter((s) => s.type === "reddit" && s.enabled !== false)
    .map((s) => s.id)
    .sort();
  if (!subs.length) return { slice: new Set(), save: async () => {} };

  let cursor = 0, prev = null;
  try { cursor = parseInt((await env.DAILY_STATE.get(REDDIT_CURSOR_KEY)) || "0", 10) || 0; } catch (_) {}
  try { prev = JSON.parse((await env.DAILY_STATE.get(REDDIT_BATCH_KEY)) || "null"); } catch (_) {}

  const prevIds = prev && Array.isArray(prev.ids) ? prev.ids.filter((id) => subs.includes(id)) : [];
  const prevPending = prev && Array.isArray(prev.pending) ? prev.pending.filter((id) => subs.includes(id)) : [];
  const prevAttempts = (prev && prev.attempts) || 0;

  let ids, pending, attempts;
  if (!prevIds.length || !prevPending.length || prevAttempts >= REDDIT_MAX_ATTEMPTS) {
    // Start the next batch: the current one is done (all succeeded) or out of
    // attempts. Advance the cursor by a slice (but not on the very first batch).
    cursor = prev
      ? (((cursor + REDDIT_SLICE) % subs.length) + subs.length) % subs.length
      : ((cursor % subs.length) + subs.length) % subs.length;
    ids = [];
    for (let i = 0; i < Math.min(REDDIT_SLICE, subs.length); i++) ids.push(subs[(cursor + i) % subs.length]);
    pending = ids.slice();
    attempts = 0;
    try { await env.DAILY_STATE.put(REDDIT_CURSOR_KEY, String(cursor)); } catch (_) {}
  } else {
    // Continue the in-flight batch: re-attempt only the subs still failing.
    ids = prevIds; pending = prevPending; attempts = prevAttempts;
  }

  const slice = new Set(pending);
  const save = async (liveSet) => {
    const stillPending = pending.filter((id) => !liveSet.has(id));
    try {
      await env.DAILY_STATE.put(REDDIT_BATCH_KEY, JSON.stringify({ ids, pending: stillPending, attempts: attempts + 1 }));
    } catch (_) {}
  };
  return { slice, save };
}
// Items live in D1 for 14 days (dedup memory); the brief itself scores+renders a
// tighter recent window — the daily is fast-decay ("what happened"). The window
// is config-driven (recency.score_window_days) so it's tunable in-app.
const DEFAULT_SCORE_WINDOW_DAYS = 2;
// Health blobs the settings page reads via /api/health.
export const SOURCE_STATUS_KEY = "source_status";
export const ENRICH_STATUS_KEY = "enrich_status";
// AI editorial layer per-feature status (written by the editorial passes; read by
// /api/health). Absent until the passes land — health falls back to config state.
export const AI_STATUS_KEY = "ai_status";

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

  // 1) Ingest every fast source (RSS/HN) + a RETRY-AWARE Reddit batch. The cron
  //    fires every 10 min; each tick refreshes all RSS/HN and re-attempts the
  //    Reddit batch's still-failing subs (≤6), advancing to the next batch after
  //    ~30 min — so a throttled sub gets a few fresh shots at the shared-IP limit
  //    before we move on, and a full rotation is still ~3h. `env` carries optional
  //    Reddit OAuth secrets. A MANUAL "Run now" debounces Reddit (skips it if we
  //    rolled within the last few minutes) so repeated presses can't add IP
  //    pressure — RSS/HN still refresh and the brief re-renders.
  const isCron = trigger === "cron";
  let lastRedditTs = 0;
  try { lastRedditTs = parseInt((await env.DAILY_STATE.get(REDDIT_FETCH_TS_KEY)) || "0", 10) || 0; } catch (_) {}
  const rollReddit = isCron || (now - lastRedditTs) >= REDDIT_DEBOUNCE_MS;
  let redditSlice = new Set(); // empty Set = fetch no reddit this run
  let saveRedditBatch = async () => {};
  if (rollReddit) {
    const b = await redditBatch(env, config);
    redditSlice = b.slice;
    saveRedditBatch = b.save;
    try { await env.DAILY_STATE.put(REDDIT_FETCH_TS_KEY, String(now)); } catch (_) {}
  }

  setProgress(env, rollReddit ? "polling sources" : "polling sources (reddit retried recently — skipping)", 0, 1);
  const { entries, live, dead, reasons } = await ingestAll(config, env, (d, t) => setProgress(env, "polling sources", d, t), redditSlice);
  const scanned = entries.length;

  // Record per-source liveness for the feed-health view (§E): which sources
  // returned items this poll vs errored/empty. MERGE over the previous blob — a
  // Reddit sub not in this tick's rotation keeps its last-known state instead of
  // vanishing (which would churn the health view as the rotation moves).
  const liveSet = new Set(live);
  // Carry the Reddit batch forward: drop the subs that succeeded, keep retrying the
  // rest next tick (until this batch is out of attempts and the cursor advances).
  await saveRedditBatch(liveSet);
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
  const capBySource = new Map(); // per-feed firehose-cap overrides (blank source.cap → global)
  for (const s of config.sources || []) { weightBySource.set(s.id, s.weight); domainBySource.set(s.id, s.domain); if (Number.isFinite(s.cap)) capBySource.set(s.id, s.cap); }
  for (const b of config.bluesky || []) { weightBySource.set(b.id, b.weight); domainBySource.set(b.id, b.domain); if (Number.isFinite(b.cap)) capBySource.set(b.id, b.cap); }

  const windowDays = (config.recency && config.recency.score_window_days) || DEFAULT_SCORE_WINDOW_DAYS;
  const sinceMs = now - 1000 * 60 * 60 * 24 * windowDays;
  const rows = await getWindowItems(db, sinceMs);
  const items = rows.map((r) => {
    const it = rowToItem(r, weightBySource);
    it.feed_domain = domainBySource.get(r.source) || it.domain; // authoritative
    return it;
  });

  setProgress(env, "scoring", 1, 1);
  await scoreBatch(db, items, config, now, capBySource);

  // 4b) Smart merge (optional, off by default) — collapse same-story dupes the
  //     mechanical dedup missed, BEFORE enrich/render see the items. No-op when off.
  const mrg = await smartMerge(env, items, config, now);

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
  // AI editorial layer (optional) — augments the mechanical state in place. No-op
  // when off / no key / cap hit, so `state` is unchanged in those cases.
  const aiStatus = await augmentEditorial(env, state, items, config, now);
  aiStatus.merge = { on: !mrg.degraded, reason: mrg.reason, model: ((config.ai || {}).merge || {}).model };
  await env.DAILY_STATE.put(AI_STATUS_KEY, JSON.stringify(aiStatus));
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

// Clear every KV blob the pipeline owns so health/rotation/state start fresh:
// the rendered brief, per-source health (last_ok/fail_since), enrichment status,
// run progress, and the reddit rotation cursor + debounce stamp. Deliberately
// enumerated (not a prefix wipe) so the user's config and the monthly spend
// ledger are left untouched.
export async function resetState(env) {
  if (!env.DAILY_STATE) return [];
  const keys = [
    STATE_KEY, SOURCE_STATUS_KEY, ENRICH_STATUS_KEY, AI_STATUS_KEY, RUN_PROGRESS_KEY,
    REDDIT_CURSOR_KEY, REDDIT_BATCH_KEY,
    "editorial:briefs", "editorial:picks", "editorial:digests", "editorial:merge",
  ];
  await Promise.all(keys.map((k) => env.DAILY_STATE.delete(k)));
  // Mark Reddit as "just rolled" rather than clearing the stamp: this debounces a
  // MANUAL "Run now" fired right after a clear, so it can't roll Reddit at the same
  // time as the next cron tick. That simultaneous double-fetch of the first batch is
  // what produced the confusing "red + has items" (one copy landed items, the other
  // got 429'd, and the two runs raced on the shared status record). The cron — which
  // ignores the debounce — does the first clean single Reddit pull within ~10 min.
  await env.DAILY_STATE.put(REDDIT_FETCH_TS_KEY, String(Date.now()));
  return [...keys, REDDIT_FETCH_TS_KEY];
}
