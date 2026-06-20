// The Signal — daily: the triage engine (§3 Tier 1 steps 3–7).
//
// "The engine, not the sources, is the value." This is the source-agnostic core:
// per-source baseline normalisation, velocity, profile-weighted ranking, the
// named-entity floor, mutes/special-handling, and the fold.

import {
  sourceBaselineCut, getLastStoryPoints, bulkInsertSamples, bulkLogStories,
} from "./db.js";

const DISCUSSION = new Set(["hn", "bluesky", "reddit"]);

const lc = (s) => (s || "").toLowerCase();

function matchesAny(hay, patterns) {
  const h = lc(hay);
  return (patterns || []).some((p) => h.includes(lc(p)));
}

// Profile-weighted relevance for one item, purely mechanical (Tier 1).
// Returns { score 0..1, entityFloor, muted, demote }.
export function scoreProfile(item, profile, extraMutes) {
  const title = item.title || "";
  const h = lc(title);

  // Global mutes (§3.5).
  if (matchesAny(title, profile.mutes) || matchesAny(title, extraMutes)) {
    return { score: 0, entityFloor: false, muted: true, demote: false };
  }

  // Named-entity floor (§4): bypasses ranking, never below the fold.
  let entityFloor = false;
  for (const e of profile.named_entity_floor || []) {
    if (matchesAny(title, e.patterns)) {
      entityFloor = true;
      break;
    }
  }

  // Topic-weighted keyword match. Score = weighted keyword hits, saturating.
  // The feed already tags a domain; scan all domains so a genuinely cross-domain
  // item (e.g. HN tagged ai_engineering but about gaming) re-homes — but PREFER
  // the feed's own domain unless another beats it by a clear margin, so a thin
  // football headline doesn't get mis-filed under books on a stray keyword.
  const tw = profile.topic_weights || {};
  // The feed's configured domain is authoritative (a persisted row may carry a
  // stale re-domained value from an earlier poll).
  const ownDomain = item.feed_domain || item.domain;
  let best = 0;
  let bestDomain = ownDomain;
  let ownScore = 0;
  for (const [domain, spec] of Object.entries(tw)) {
    let hits = 0;
    for (const kw of spec.keywords) if (h.includes(lc(kw))) hits++;
    if (hits === 0) continue;
    const s = spec.weight * (1 - Math.pow(0.6, hits)); // diminishing returns
    if (domain === ownDomain) ownScore = s;
    if (s > best) {
      best = s;
      bestDomain = domain;
    }
  }
  if (ownScore > 0 && best <= ownScore * 1.25) {
    bestDomain = ownDomain;
    best = ownScore;
  }
  item.domain = bestDomain;

  // Special handling: suppression + demotion (§7.6).
  let demote = false;
  const sh = (profile.special_handling || {})[bestDomain];
  if (sh) {
    if (matchesAny(title, sh.suppress_patterns)) {
      return { score: 0, entityFloor, muted: true, demote: false };
    }
    if (matchesAny(title, sh.demote_patterns)) demote = true;
  }

  return { score: best, entityFloor, muted: false, demote };
}

// Score the whole batch: baselines, velocity, profile, confidence, fold.
// `items` are the in-window items. Mutates them with score fields in memory and
// writes only a handful of batched rows (samples for discussion sources, story
// points for the surfaced catches) — no per-item awaits. The recomputable score
// fields are NOT persisted: every poll recomputes them from raw_score + config.
export async function scoreBatch(db, items, config, now) {
  const profile = config.profile;
  const extraMutes = config.mutes || [];
  const baselineWindow = now - 1000 * 60 * 60 * 24 * 30;
  const fold = config.fold_threshold;

  // Baselines only matter for sources whose raw score actually varies
  // (discussion sources: HN/Bluesky/Reddit). RSS has no popularity signal, so it
  // uses the recency fallback. Compute each such source's trailing cut once.
  const cuts = new Map();
  const discSources = [...new Set(items.filter((i) => DISCUSSION.has(i.source_type)).map((i) => i.source))];
  for (const s of discSources) cuts.set(s, await sourceBaselineCut(db, s, baselineWindow));

  // One query for every cluster's previous story point (velocity).
  const lastPoints = await getLastStoryPoints(db, now);

  const sampleRows = [];
  const storyRows = [];

  for (const it of items) {
    // 1) per-source baseline normalisation (§3.3).
    if (DISCUSSION.has(it.source_type)) {
      const cut = cuts.get(it.source);
      it.baseline_score = cut && cut > 0
        ? Math.max(0, Math.min(1, it.rawScore / (cut * 1.5)))
        : 0.5;
      sampleRows.push({ source: it.source, score: it.rawScore, ts: now });
    } else {
      const ageH = (now - (it.published || now)) / 3.6e6;
      it.baseline_score = ageH < 6 ? 0.7 : ageH < 24 ? 0.5 : 0.3;
    }

    // 2) velocity (§3.4): Δscore/Δhr vs the cluster's last logged point.
    const prev = lastPoints.get(it.id);
    if (prev && prev.ts) {
      const dh = Math.max(0.25, (now - prev.ts) / 3.6e6);
      it.velocity = Math.max(0, (it.rawScore - prev.score) / dh);
    } else {
      it.velocity = 0;
    }
    const velNorm = Math.min(1, it.velocity / 20);

    // 3) profile-weighted ranking (§3.6) + entity floor + mutes. For an
    // already-enriched item the saved profile_score carries Tier-2's semantic
    // relevance (judged once); keep it if it beats the mechanical pass.
    const loadedProfile = it.profile_score || 0;
    const pr = scoreProfile(it, profile, extraMutes);
    it.profile_score = it.enriched ? Math.max(pr.score, loadedProfile) : pr.score;
    it.entity_floor = pr.entityFloor;
    it.muted = pr.muted;

    // 4) confidence: blend interest, source-significance and velocity, scaled by
    // source weight. Demote (UK politics etc.) cuts it hard.
    let conf = 0.55 * it.profile_score + 0.30 * it.baseline_score + 0.15 * velNorm;
    conf *= 0.6 + 0.4 * (it.weight || 0.5);
    if (pr.demote) conf *= 0.4;
    if (it.muted) conf = 0;
    it.confidence = Math.max(0, Math.min(1, conf));

    // 5) the fold (§3.7): above-fold = over the threshold (not a fixed count).
    // The named-entity floor *bypasses ranking* — it guarantees above-fold but
    // does NOT flatten the score, so the most significant core story still leads
    // and one entity doesn't flood Top Catches.
    if (it.entity_floor && !it.muted) {
      it.above_fold = true;
      it.confidence = Math.max(it.confidence, fold + 0.02);
    } else {
      it.above_fold = !it.muted && it.confidence >= fold;
    }

    // Log a story point only for surfaced catches + discussion items (movement
    // evidence for the weekly + future velocity) — not the whole firehose.
    if (!it.muted && (it.above_fold || DISCUSSION.has(it.source_type))) {
      storyRows.push({ cluster_id: it.id, ts: now, score: it.rawScore, headline: it.title, domain: it.domain });
    }
  }

  await bulkInsertSamples(db, sampleRows);
  await bulkLogStories(db, storyRows);
  return items;
}
