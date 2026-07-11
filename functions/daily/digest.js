// The Signal — daily→weekly digest (D-3 bridge).
//
// The FOUNDATIONAL bridge the weekly (Stream 1, Phase W-4) consumes: "what
// surfaced and what MOVED this week", assembled from the D-2 signal-tier history
// in `story_log`. Pure functions here (no Cloudflare bindings) so the assembly is
// unit-testable; the D1 read lives in db.js and the HTTP handler in api/daily.js.

import { signalPhrase } from "./score.js";

// Parse a flexible `since` into a millisecond window start. Accepts "7d", "72h",
// "90m", or a bare number (days). Falls back to 7 days on anything unparseable,
// and clamps to [1h, 60d] (story_log retention is ~60d, so a wider ask is moot).
export function parseSince(raw, now = Date.now()) {
  const H = 3.6e6, D = 8.64e7;
  const MIN = H, MAX = 60 * D;
  let ms = 7 * D;
  const s = String(raw == null ? "" : raw).trim().toLowerCase();
  const m = s.match(/^(\d+(?:\.\d+)?)\s*([dhm]?)$/);
  if (m) {
    const n = parseFloat(m[1]);
    if (Number.isFinite(n) && n > 0) {
      const unit = m[2] || "d";
      ms = unit === "h" ? n * H : unit === "m" ? n * 60000 : n * D;
    }
  }
  ms = Math.max(MIN, Math.min(MAX, ms));
  return now - ms;
}

// The earliest and latest non-null signal tier across a cluster's points, so a
// "moved" verdict compares where the story STARTED the window to where it is now.
function firstLastSignal(points) {
  let first = null, last = null;
  for (const p of points) {
    if (p.signal == null) continue;
    if (first == null) first = p.signal;
    last = p.signal;
  }
  return { first, last };
}

// Assemble the digest from raw story_log rows (each {cluster_id, ts, score,
// headline, domain, signal}). Rows may arrive in any order. `itemsById` (optional)
// maps cluster_id → { canonical_url, domain } for a tappable link. Never throws on
// missing/partial data — empty in → empty arrays out.
export function assembleDigest(rows, { since, sinceMs, now = Date.now(), itemsById = null } = {}) {
  const byCluster = new Map();
  for (const r of rows || []) {
    if (!r || r.cluster_id == null) continue;
    let g = byCluster.get(r.cluster_id);
    if (!g) { g = []; byCluster.set(r.cluster_id, g); }
    g.push(r);
  }

  const surfaced = [];
  const moved = [];
  const saga_lines = [];
  for (const [id, pts] of byCluster) {
    pts.sort((a, b) => (a.ts || 0) - (b.ts || 0));
    const firstPt = pts[0], lastPt = pts[pts.length - 1];
    const link = itemsById && itemsById.get(id) ? itemsById.get(id).canonical_url || null : null;
    const domain = lastPt.domain || firstPt.domain || null;
    const title = lastPt.headline || firstPt.headline || null;
    const peak = pts.reduce((mx, p) => Math.max(mx, p.score || 0), 0);
    surfaced.push({
      id, title, domain, link,
      first_seen: firstPt.ts || null,
      last_seen: lastPt.ts || null,
      points: pts.length,
      signal: lastPt.signal || null,
      peak_score: Math.round(peak * 100) / 100,
    });

    const { first, last } = firstLastSignal(pts);
    if (first && last && first !== last) {
      const was_label = signalPhrase(first), now_label = signalPhrase(last);
      moved.push({
        id, title, domain, link,
        was: first, now: last, was_label, now_label,
        first_seen: firstPt.ts || null, last_seen: lastPt.ts || null,
      });
      if (title) saga_lines.push(`${title}: was ${was_label} → now ${now_label}`);
    }
  }

  // Most-recent first for surfaced; biggest jumps (most recent) first for moved.
  surfaced.sort((a, b) => (b.last_seen || 0) - (a.last_seen || 0));
  moved.sort((a, b) => (b.last_seen || 0) - (a.last_seen || 0));

  return {
    since: since || null,
    since_ms: sinceMs || null,
    generated_at: now,
    counts: { surfaced: surfaced.length, moved: moved.length },
    surfaced,
    moved,
    saga_lines,
  };
}
