// The Signal — daily: D1 data layer.
//
// D1 holds the time-series engine data that powers the triage engine and the
// feeder loop (§1): per-source baselines, the per-story movement log (the
// weekly's evidence for whether a story has *moved*), the clustered item set,
// and a per-run log. Live config and the rendered home blob live in KV instead.
//
// All access goes through the DAILY_DB binding. `initSchema` is idempotent and
// is called at the top of every run so a fresh database self-heals.

export async function initSchema(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS items (
      id TEXT PRIMARY KEY,
      canonical_url TEXT,
      title TEXT,
      summary TEXT,
      domain TEXT,
      source TEXT,
      source_type TEXT,
      links TEXT,
      first_seen INTEGER,
      last_seen INTEGER,
      published INTEGER,
      raw_score REAL DEFAULT 0,
      source_count INTEGER DEFAULT 1,
      baseline_score REAL DEFAULT 0,
      profile_score REAL DEFAULT 0,
      velocity REAL DEFAULT 0,
      confidence REAL DEFAULT 0,
      above_fold INTEGER DEFAULT 0,
      entity_floor INTEGER DEFAULT 0,
      muted INTEGER DEFAULT 0,
      register TEXT,
      hook TEXT,
      enriched INTEGER DEFAULT 0,
      enrich_hash TEXT
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_items_last_seen ON items(last_seen)`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_items_conf ON items(confidence)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS source_samples (
      source TEXT,
      score REAL,
      ts INTEGER
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_samples_src ON source_samples(source, ts)`),
    // The per-story movement log — the weekly reads this to tell "moved" from
    // "still exists" (§9: news re-leads require new development).
    db.prepare(`CREATE TABLE IF NOT EXISTS story_log (
      cluster_id TEXT,
      ts INTEGER,
      score REAL,
      headline TEXT,
      domain TEXT,
      signal TEXT
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_story_cluster ON story_log(cluster_id, ts)`),
    // The latest story point per cluster, maintained on write. story_log holds
    // ~8M rows over its 60-day window; deriving "last point per cluster" from it
    // every 10-min tick was a full index scan (8M rows read × 144/day — the single
    // biggest line on the D1 bill). This table is ~30k rows and answers the same
    // question exactly. Backfilled once from story_log (see backfillStoryLatest).
    db.prepare(`CREATE TABLE IF NOT EXISTS story_latest (
      cluster_id TEXT PRIMARY KEY,
      ts INTEGER,
      score REAL,
      headline TEXT,
      signal TEXT,
      source_count INTEGER DEFAULT 1
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_story_latest_ts ON story_latest(ts)`),
    // Small key/value table for engine bookkeeping (e.g. whether story_latest has
    // been fully backfilled — until it has, reads fall back to the old query).
    db.prepare(`CREATE TABLE IF NOT EXISTS engine_meta (key TEXT PRIMARY KEY, value TEXT)`),
    // Cached per-source baseline cut (85th percentile over the trailing 30 days).
    // The cut moves negligibly tick to tick, but recomputing it read ~80k samples
    // per source per tick (48 sources → ~4M rows every 10 min). Cached with a TTL.
    db.prepare(`CREATE TABLE IF NOT EXISTS source_baselines (
      source TEXT PRIMARY KEY,
      cut REAL,
      n INTEGER,
      computed_at INTEGER
    )`),
    db.prepare(`CREATE TABLE IF NOT EXISTS runs (
      ts INTEGER,
      scanned INTEGER,
      kept INTEGER,
      sources INTEGER,
      enriched INTEGER,
      enrich_on INTEGER,
      spend_cents REAL,
      notes TEXT
    )`),
  ]);
  // Idempotent migration for databases created before the summary column.
  // ALTER must run outside the batch (a failed ALTER would roll the batch back).
  try {
    await db.prepare(`ALTER TABLE items ADD COLUMN summary TEXT`).run();
  } catch (_) {
    /* column already exists */
  }
  // Breadth signal: how many distinct feeds carried this story (a "bigness" cue
  // for Headlines). Idempotent migration for databases created before the column.
  try {
    await db.prepare(`ALTER TABLE items ADD COLUMN source_count INTEGER DEFAULT 1`).run();
  } catch (_) {
    /* column already exists */
  }
  // Developing-delta (D-2): the last-surfaced signal tier per cluster, so the
  // next poll can compute "was rumoured → now confirmed". Idempotent migration
  // for databases created before the column; getLastStoryPoints also degrades
  // gracefully if this ALTER hasn't run yet (old DB), so a miss never throws.
  try {
    await db.prepare(`ALTER TABLE story_log ADD COLUMN signal TEXT`).run();
  } catch (_) {
    /* column already exists */
  }
  // RSS velocity burst (D-4): the number of distinct feeds carrying a cluster at
  // each surfaced point, so the NEXT poll can read cross-feed pickup as a velocity
  // proxy for RSS (whose rawScore is constant → Δscore velocity is always 0).
  // Idempotent; getLastStoryPoints degrades gracefully if this ALTER hasn't run.
  try {
    await db.prepare(`ALTER TABLE story_log ADD COLUMN source_count INTEGER DEFAULT 1`).run();
  } catch (_) {
    /* column already exists */
  }
}

// Pull the current in-window item set for scoring/render. Retention ~14 days
// for the daily state window (§10).
export async function getWindowItems(db, sinceMs) {
  const { results } = await db
    .prepare(`SELECT * FROM items WHERE last_seen >= ? ORDER BY confidence DESC`)
    .bind(sinceMs)
    .all();
  return results || [];
}

export async function getItem(db, id) {
  return db.prepare(`SELECT * FROM items WHERE id = ?`).bind(id).first();
}

export async function upsertItem(db, it) {
  await db
    .prepare(
      `INSERT INTO items (id, canonical_url, title, domain, source, source_type, links,
         first_seen, last_seen, published, raw_score)
       VALUES (?,?,?,?,?,?,?,?,?,?,?)
       ON CONFLICT(id) DO UPDATE SET
         last_seen=excluded.last_seen,
         raw_score=MAX(items.raw_score, excluded.raw_score),
         links=excluded.links,
         title=excluded.title`
    )
    .bind(
      it.id, it.canonical_url, it.title, it.domain, it.source, it.source_type,
      JSON.stringify(it.links || []), it.first_seen, it.last_seen,
      it.published || it.first_seen, it.raw_score || 0
    )
    .run();
}

export async function updateScores(db, it) {
  await db
    .prepare(
      `UPDATE items SET baseline_score=?, profile_score=?, velocity=?, confidence=?,
         above_fold=?, entity_floor=?, muted=?, domain=? WHERE id=?`
    )
    .bind(
      it.baseline_score, it.profile_score, it.velocity, it.confidence,
      it.above_fold ? 1 : 0, it.entity_floor ? 1 : 0, it.muted ? 1 : 0,
      it.domain, it.id
    )
    .run();
}

export async function saveEnrichment(db, id, e) {
  await db
    .prepare(
      `UPDATE items SET register=?, hook=?, profile_score=?, enriched=1, enrich_hash=? WHERE id=?`
    )
    .bind(e.register || null, e.hook || null, e.relevance ?? null, e.enrich_hash || null, id)
    .run();
}

export async function addSourceSample(db, source, score, ts) {
  await db
    .prepare(`INSERT INTO source_samples (source, score, ts) VALUES (?,?,?)`)
    .bind(source, score, ts)
    .run();
}

// Run an array of prepared statements in chunked batches (one transaction per
// chunk). Keeps a poll to a handful of round-trips instead of thousands of
// sequential awaits — the difference between a sub-second run and a timeout.
export async function runChunked(db, stmts, size = 50) {
  for (let i = 0; i < stmts.length; i += size) {
    await db.batch(stmts.slice(i, i + size));
  }
}

export async function bulkUpsertItems(db, items) {
  const sql = `INSERT INTO items (id, canonical_url, title, summary, domain, source, source_type, links,
         first_seen, last_seen, published, raw_score, source_count)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
       ON CONFLICT(id) DO UPDATE SET
         last_seen=excluded.last_seen,
         raw_score=MAX(items.raw_score, excluded.raw_score),
         source_count=MAX(items.source_count, excluded.source_count),
         links=excluded.links,
         title=excluded.title,
         summary=COALESCE(NULLIF(excluded.summary, ''), items.summary)`;
  const stmts = items.map((it) =>
    db.prepare(sql).bind(
      it.id, it.canonical_url, it.title, it.summary || "", it.domain, it.source, it.source_type,
      JSON.stringify(it.links || []), it.first_seen, it.last_seen,
      // NULL when the feed gave no date — never fudge it to first_seen. Scoring
      // dates undated items by first_seen (with an age penalty) instead.
      it.published ?? null, it.raw_score || 0, it.source_count || 1
    )
  );
  await runChunked(db, stmts);
}

// Per-source article counts over a recent window (feed-health view §E). Counts
// items first caught within the window, with the most recent catch per source.
export async function getSourceCounts(db, sinceMs) {
  const { results } = await db
    .prepare(
      `SELECT source, COUNT(*) AS c, MAX(last_seen) AS last_seen
         FROM items WHERE first_seen >= ? GROUP BY source`
    )
    .bind(sinceMs)
    .all();
  const map = new Map();
  for (const r of results || []) map.set(r.source, { count: r.c, last_seen: r.last_seen });
  return map;
}

export async function bulkInsertSamples(db, rows) {
  if (!rows.length) return;
  const stmts = rows.map((r) =>
    db.prepare(`INSERT INTO source_samples (source, score, ts) VALUES (?,?,?)`).bind(r.source, r.score, r.ts)
  );
  await runChunked(db, stmts);
}

// Upsert into story_latest — the newest point wins (ts is monotonic per run, so a
// replayed older row can never clobber a newer one).
const STORY_LATEST_UPSERT = `INSERT INTO story_latest (cluster_id, ts, score, headline, signal, source_count)
       VALUES (?,?,?,?,?,?)
       ON CONFLICT(cluster_id) DO UPDATE SET
         ts=excluded.ts, score=excluded.score, headline=excluded.headline,
         signal=excluded.signal, source_count=excluded.source_count
       WHERE excluded.ts >= story_latest.ts`;

export async function bulkLogStories(db, rows) {
  if (!rows.length) return;
  const stmts = [];
  for (const r of rows) {
    stmts.push(
      db.prepare(`INSERT INTO story_log (cluster_id, ts, score, headline, domain, signal, source_count) VALUES (?,?,?,?,?,?,?)`)
        .bind(r.cluster_id, r.ts, r.score, r.headline, r.domain, r.signal || null, r.source_count || 1)
    );
    stmts.push(
      db.prepare(STORY_LATEST_UPSERT)
        .bind(r.cluster_id, r.ts, r.score, r.headline, r.signal || null, r.source_count || 1)
    );
  }
  await runChunked(db, stmts);
}

// Trailing baseline cut: the score at the ~85th percentile over the window,
// i.e. "significant for this source" (§3.3, default top ~15% over 14–30 days).
//
// Cached: the cut is a percentile over a 30-day window (~80k samples per source),
// so the ~18 samples a source adds per tick can't move it measurably — yet
// computing it reads every one of those rows. Recompute at most every
// BASELINE_TTL_MS (sooner while a source is still too thin to have a cut, so a
// new feed gets its baseline within the hour).
export const BASELINE_TTL_MS = 3 * 60 * 60 * 1000;
const BASELINE_THIN_TTL_MS = 60 * 60 * 1000;

export async function sourceBaselineCut(db, source, sinceMs, now = Date.now()) {
  let cached = null;
  try {
    cached = await db
      .prepare(`SELECT cut, n, computed_at FROM source_baselines WHERE source=?`)
      .bind(source)
      .first();
  } catch (_) { /* table missing on a not-yet-migrated DB → compute */ }
  if (cached && cached.computed_at) {
    const ttl = cached.n >= 8 ? BASELINE_TTL_MS : BASELINE_THIN_TTL_MS;
    if (now - cached.computed_at < ttl) return cached.n >= 8 ? cached.cut : null;
  }
  const { results } = await db
    .prepare(`SELECT score FROM source_samples WHERE source=? AND ts>=? ORDER BY score ASC`)
    .bind(source, sinceMs)
    .all();
  const scores = (results || []).map((r) => r.score).filter((s) => s > 0);
  const n = scores.length;
  const cut = n < 8 ? null : scores[Math.min(Math.floor(n * 0.85), n - 1)];
  try {
    await db
      .prepare(`INSERT INTO source_baselines (source, cut, n, computed_at) VALUES (?,?,?,?)
                ON CONFLICT(source) DO UPDATE SET cut=excluded.cut, n=excluded.n, computed_at=excluded.computed_at`)
      .bind(source, cut, n, now)
      .run();
  } catch (_) { /* cache write is best-effort */ }
  return cut; // null = not enough history yet
}

export async function logStory(db, clusterId, score, headline, domain, ts, signal = null) {
  await db.batch([
    db.prepare(`INSERT INTO story_log (cluster_id, ts, score, headline, domain, signal) VALUES (?,?,?,?,?,?)`)
      .bind(clusterId, ts, score, headline, domain, signal),
    db.prepare(STORY_LATEST_UPSERT).bind(clusterId, ts, score, headline, signal, 1),
  ]);
}

// Previous logged score for a cluster (for velocity = Δscore/Δhr).
export async function lastStoryPoint(db, clusterId, beforeTs) {
  return db
    .prepare(`SELECT ts, score FROM story_log WHERE cluster_id=? AND ts<? ORDER BY ts DESC LIMIT 1`)
    .bind(clusterId, beforeTs)
    .first();
}

const STORY_LATEST_READY_KEY = "story_latest_ready";

async function storyLatestReady(db) {
  try {
    const r = await db.prepare(`SELECT value FROM engine_meta WHERE key=?`).bind(STORY_LATEST_READY_KEY).first();
    return !!(r && r.value === "1");
  } catch (_) {
    return false;
  }
}

// One-time backfill of story_latest from story_log, for a database that predates
// the table: one full pass over story_log (the same query that used to run every
// tick — it fits D1's limits because it already ran 144×/day), then the ready flag
// is set and it never runs again. Until the flag is set, getLastStoryPoints keeps
// using the old query, so a backfill that fails or is cut off changes nothing —
// it is simply retried next tick. On an OLD story_log without the `signal`
// column, fall back to the always-present columns.
export async function backfillStoryLatest(db) {
  if (await storyLatestReady(db)) return false;
  const any = await db.prepare(`SELECT 1 AS x FROM story_log LIMIT 1`).first();
  if (any) {
    const join = `FROM story_log s
           JOIN (SELECT cluster_id, MAX(ts) AS mt FROM story_log GROUP BY cluster_id) m
             ON s.cluster_id = m.cluster_id AND s.ts = m.mt`;
    try {
      await db
        .prepare(`INSERT OR REPLACE INTO story_latest (cluster_id, ts, score, headline, signal, source_count)
                  SELECT s.cluster_id, s.ts, s.score, s.headline, s.signal, COALESCE(s.source_count, 1) ${join}`)
        .run();
    } catch (_) {
      await db
        .prepare(`INSERT OR REPLACE INTO story_latest (cluster_id, ts, score, headline, signal, source_count)
                  SELECT s.cluster_id, s.ts, s.score, s.headline, NULL, 1 ${join}`)
        .run();
    }
  }
  await db
    .prepare(`INSERT OR REPLACE INTO engine_meta (key, value) VALUES (?, '1')`)
    .bind(STORY_LATEST_READY_KEY)
    .run();
  return true;
}

// The most recent story point per cluster, in ONE query → Map(cluster_id ->
// {ts, score, headline, signal, source_count}).
//
// Once story_latest is backfilled this reads it (~30k rows, maintained on every
// write) instead of deriving the answer from the 8M-row story_log — same result,
// ~250× fewer rows read per tick. Until the backfill has succeeded it runs the
// original derivation, so the switch can never degrade a poll. One theoretical
// difference on the fast path: only the LATEST point per cluster is kept, so
// `beforeTs` can exclude a cluster outright rather than fall back to an older
// point; the pipeline always asks with beforeTs = this tick's `now`, before it
// logs this tick's rows, so nothing is ever excluded in practice.
export async function getLastStoryPoints(db, beforeTs) {
  let ready = false;
  try { await backfillStoryLatest(db); ready = await storyLatestReady(db); } catch (_) { ready = false; }
  let results;
  if (ready) {
    ({ results } = await db
      .prepare(`SELECT cluster_id, ts, score, headline, signal, source_count
                  FROM story_latest WHERE ts < ?`)
      .bind(beforeTs)
      .all());
  } else {
    // Original derivation (kept verbatim as the fallback). On an OLD database
    // whose story_log predates the `signal` column, fall back to the columns that
    // always exist so a missing column degrades gracefully.
    const join = `FROM story_log s
           JOIN (SELECT cluster_id, MAX(ts) AS mt FROM story_log WHERE ts < ? GROUP BY cluster_id) m
             ON s.cluster_id = m.cluster_id AND s.ts = m.mt`;
    try {
      ({ results } = await db
        .prepare(`SELECT s.cluster_id AS cluster_id, s.ts AS ts, s.score AS score,
                         s.headline AS headline, s.signal AS signal,
                         s.source_count AS source_count ${join}`)
        .bind(beforeTs)
        .all());
    } catch (_) {
      ({ results } = await db
        .prepare(`SELECT s.cluster_id AS cluster_id, s.ts AS ts, s.score AS score ${join}`)
        .bind(beforeTs)
        .all());
    }
  }
  const map = new Map();
  for (const r of results || [])
    map.set(r.cluster_id, {
      ts: r.ts, score: r.score, headline: r.headline || null,
      signal: r.signal || null, source_count: r.source_count || 1,
    });
  return map;
}

// Story-log rows within a window, oldest-first (the daily→weekly digest reads
// this to tell what surfaced from what MOVED). Degrades gracefully: on an OLD
// database whose story_log predates the `signal` column the signal-aware SELECT
// throws, so fall back to the always-present columns; a missing table returns [].
export async function getStoryLogSince(db, sinceMs) {
  const base = `FROM story_log WHERE ts >= ? ORDER BY ts ASC`;
  try {
    const { results } = await db
      .prepare(`SELECT cluster_id, ts, score, headline, domain, signal ${base}`)
      .bind(sinceMs).all();
    return results || [];
  } catch (_) {
    try {
      const { results } = await db
        .prepare(`SELECT cluster_id, ts, score, headline, domain ${base}`)
        .bind(sinceMs).all();
      return (results || []).map((r) => ({ ...r, signal: null }));
    } catch (_2) {
      return [];
    }
  }
}

// canonical_url + domain for a set of item ids → Map(id → row), so the digest can
// attach a tappable link. Best-effort: items are pruned at ~14d while story_log
// keeps ~60d, so a moved-weeks-ago cluster may have no live item (link stays null).
export async function getItemsByIds(db, ids) {
  const map = new Map();
  const list = [...new Set(ids || [])].filter((x) => x != null);
  if (!list.length) return map;
  const CHUNK = 100;
  for (let i = 0; i < list.length; i += CHUNK) {
    const slice = list.slice(i, i + CHUNK);
    const holes = slice.map(() => "?").join(",");
    try {
      const { results } = await db
        .prepare(`SELECT id, canonical_url, domain FROM items WHERE id IN (${holes})`)
        .bind(...slice).all();
      for (const r of results || []) map.set(r.id, r);
    } catch (_) { /* missing table / column → skip, link stays null */ }
  }
  return map;
}

export async function logRun(db, r) {
  await db
    .prepare(
      `INSERT INTO runs (ts, scanned, kept, sources, enriched, enrich_on, spend_cents, notes)
       VALUES (?,?,?,?,?,?,?,?)`
    )
    .bind(r.ts, r.scanned, r.kept, r.sources, r.enriched, r.enrich_on ? 1 : 0, r.spend_cents || 0, r.notes || "")
    .run();
}

// Wipe all pulled + derived engine data for a clean-slate rebuild (keeps the
// schema). Used by the token-gated /api/daily/reset so the reader can start a
// fresh history and watch the rolling rotation fill it in. Does NOT touch KV
// (config, the rendered state, source health, the spend ledger) — that's the
// caller's job via resetState().
export async function resetEngine(db) {
  await db.batch([
    db.prepare(`DELETE FROM items`),
    db.prepare(`DELETE FROM source_samples`),
    db.prepare(`DELETE FROM story_log`),
    db.prepare(`DELETE FROM story_latest`),
    db.prepare(`DELETE FROM source_baselines`),
    db.prepare(`DELETE FROM engine_meta`),
    db.prepare(`DELETE FROM runs`),
  ]);
}

// Timestamp indexes for the retention deletes. Without them `DELETE … WHERE ts < ?`
// is a full table scan of story_log (~8M rows) and source_samples (~4M) — and it
// ran every tick. Built here (not in initSchema) because on an existing database
// the first build walks the whole table: run it from the once-a-day prune path,
// best-effort, so a slow build can never fail a poll. A no-op once they exist.
export async function ensureRetentionIndexes(db) {
  for (const sql of [
    `CREATE INDEX IF NOT EXISTS idx_samples_ts ON source_samples(ts)`,
    `CREATE INDEX IF NOT EXISTS idx_story_ts ON story_log(ts)`,
  ]) {
    try { await db.prepare(sql).run(); } catch (_) { /* retried next prune */ }
  }
}

// Retention prune (§10): drop items out of the ~14-day state window; keep the
// story_log longer (~60d) so the weekly still has movement evidence. Intended to
// run about once a day (pipeline gates it) — retention is measured in days, and
// each pass is one range delete per table once the ts indexes exist.
export async function prune(db, now) {
  const itemCut = now - 1000 * 60 * 60 * 24 * 14;
  const sampleCut = now - 1000 * 60 * 60 * 24 * 30;
  const logCut = now - 1000 * 60 * 60 * 24 * 60;
  await ensureRetentionIndexes(db);
  await db.batch([
    db.prepare(`DELETE FROM items WHERE last_seen < ?`).bind(itemCut),
    db.prepare(`DELETE FROM source_samples WHERE ts < ?`).bind(sampleCut),
    db.prepare(`DELETE FROM story_log WHERE ts < ?`).bind(logCut),
    db.prepare(`DELETE FROM story_latest WHERE ts < ?`).bind(logCut),
    db.prepare(`DELETE FROM runs WHERE ts < ?`).bind(logCut),
  ]);
}
