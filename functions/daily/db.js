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
      domain TEXT
    )`),
    db.prepare(`CREATE INDEX IF NOT EXISTS idx_story_cluster ON story_log(cluster_id, ts)`),
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

export async function bulkLogStories(db, rows) {
  if (!rows.length) return;
  const stmts = rows.map((r) =>
    db.prepare(`INSERT INTO story_log (cluster_id, ts, score, headline, domain) VALUES (?,?,?,?,?)`)
      .bind(r.cluster_id, r.ts, r.score, r.headline, r.domain)
  );
  await runChunked(db, stmts);
}

// Trailing baseline cut: the score at the ~85th percentile over the window,
// i.e. "significant for this source" (§3.3, default top ~15% over 14–30 days).
export async function sourceBaselineCut(db, source, sinceMs) {
  const { results } = await db
    .prepare(`SELECT score FROM source_samples WHERE source=? AND ts>=? ORDER BY score ASC`)
    .bind(source, sinceMs)
    .all();
  const scores = (results || []).map((r) => r.score).filter((s) => s > 0);
  if (scores.length < 8) return null; // not enough history yet
  const idx = Math.floor(scores.length * 0.85);
  return scores[Math.min(idx, scores.length - 1)];
}

export async function logStory(db, clusterId, score, headline, domain, ts) {
  await db
    .prepare(`INSERT INTO story_log (cluster_id, ts, score, headline, domain) VALUES (?,?,?,?,?)`)
    .bind(clusterId, ts, score, headline, domain)
    .run();
}

// Previous logged score for a cluster (for velocity = Δscore/Δhr).
export async function lastStoryPoint(db, clusterId, beforeTs) {
  return db
    .prepare(`SELECT ts, score FROM story_log WHERE cluster_id=? AND ts<? ORDER BY ts DESC LIMIT 1`)
    .bind(clusterId, beforeTs)
    .first();
}

// The most recent story point per cluster, in ONE query → Map(cluster_id ->
// {ts, score}). Replaces 1-query-per-item velocity lookups.
export async function getLastStoryPoints(db, beforeTs) {
  const { results } = await db
    .prepare(
      `SELECT s.cluster_id AS cluster_id, s.ts AS ts, s.score AS score
         FROM story_log s
         JOIN (SELECT cluster_id, MAX(ts) AS mt FROM story_log WHERE ts < ? GROUP BY cluster_id) m
           ON s.cluster_id = m.cluster_id AND s.ts = m.mt`
    )
    .bind(beforeTs)
    .all();
  const map = new Map();
  for (const r of results || []) map.set(r.cluster_id, { ts: r.ts, score: r.score });
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
    db.prepare(`DELETE FROM runs`),
  ]);
}

// Retention prune (§10): drop items out of the ~14-day state window; keep the
// story_log longer (~60d) so the weekly still has movement evidence.
export async function prune(db, now) {
  const itemCut = now - 1000 * 60 * 60 * 24 * 14;
  const sampleCut = now - 1000 * 60 * 60 * 24 * 30;
  const logCut = now - 1000 * 60 * 60 * 24 * 60;
  await db.batch([
    db.prepare(`DELETE FROM items WHERE last_seen < ?`).bind(itemCut),
    db.prepare(`DELETE FROM source_samples WHERE ts < ?`).bind(sampleCut),
    db.prepare(`DELETE FROM story_log WHERE ts < ?`).bind(logCut),
    db.prepare(`DELETE FROM runs WHERE ts < ?`).bind(logCut),
  ]);
}
