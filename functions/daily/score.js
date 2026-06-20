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
  // Topic-keyword scoring runs over title + summary for a richer signal; the
  // floor / mutes / special-handling stay title-only to avoid over-matching on
  // a stray word in a long summary.
  const ht = lc(title + " " + (item.summary || ""));

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
  // Matching is WORD-BOUNDARY, not substring: a single-token keyword must appear
  // as a whole word (so "tor" doesn't match "direcTOR", "inter" doesn't match
  // "INTERnet"); multi-word / hyphenated keywords fall back to substring.
  const words = new Set(ht.split(/[^a-z0-9]+/).filter(Boolean));
  const kwHit = (kw) => {
    kw = lc(kw).trim();
    return /[^a-z0-9]/.test(kw) ? ht.includes(kw) : words.has(kw);
  };

  const tw = profile.topic_weights || {};
  // The feed already tags a domain; scan all domains so a genuinely cross-domain
  // item re-homes — but PREFER the feed's own (authoritative) domain unless
  // another beats it by a clear margin, so a thin headline isn't mis-filed.
  const ownDomain = item.feed_domain || item.domain;
  let best = 0;
  let bestDomain = ownDomain;
  let ownScore = 0;
  for (const [domain, spec] of Object.entries(tw)) {
    let hits = 0;
    for (const kw of spec.keywords) if (kwHit(kw)) hits++;
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
  const rc = config.recency || {};
  const halfLifeMs = (rc.half_life_hours || 20) * 3.6e6;
  const undatedPenaltyMs = (rc.undated_penalty_hours || 36) * 3.6e6;
  const floorFreshHours = rc.floor_fresh_hours || 36;
  const velKeep = rc.velocity_fresh_keep ?? 0.25;

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
    // 1) per-source baseline normalisation (§3.3). Discussion sources carry a
    //    real popularity signal (points/likes) → normalise it. RSS does not, so
    //    it gets a flat baseline; recency is applied separately and uniformly
    //    below (the old RSS age buckets were the only age signal and they were
    //    far too coarse — a 4-day-old item scored the same as a 25-hour-old one).
    if (DISCUSSION.has(it.source_type)) {
      const cut = cuts.get(it.source);
      it.baseline_score = cut && cut > 0
        ? Math.max(0, Math.min(1, it.rawScore / (cut * 1.5)))
        : 0.5;
      sampleRows.push({ source: it.source, score: it.rawScore, ts: now });
    } else {
      it.baseline_score = 0.5;
    }

    // Recency (the daily is fast-decay). Date the item by its real publish time;
    // if the feed gave none (published == null) fall back to when we first caught
    // it AND add an age penalty so undated items can't masquerade as fresh.
    const dateUnknown = it.published == null;
    const effTs = it.published ?? it.first_seen ?? now;
    const ageMs = Math.max(0, now - effTs) + (dateUnknown ? undatedPenaltyMs : 0);
    it.age_hours = ageMs / 3.6e6;
    const recency = Math.pow(0.5, ageMs / halfLifeMs); // 1 now → 0.5 at half-life

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

    // 4) confidence: blend interest + source-significance, scale by source
    //    weight, then apply recency. A genuinely moving story (high velocity)
    //    resists decay so breaking news isn't aged out the moment it's caught.
    let base = 0.65 * it.profile_score + 0.35 * it.baseline_score;
    base *= 0.6 + 0.4 * (it.weight || 0.5);
    if (pr.demote) base *= 0.4;
    const recencyLifted = Math.min(1, recency + 0.6 * velNorm * (1 - recency));
    it.recency_score = recencyLifted;
    let conf = it.muted ? 0 : base * recencyLifted;
    it.confidence = Math.max(0, Math.min(1, conf));

    // 5) the fold (§3.7): above-fold = over the threshold (not a fixed count).
    // The named-entity floor guarantees a core story above the fold — but only
    // while it's actually fresh (or still moving fast). A stale core item (the
    // 4-day-old Juventus rumour) no longer pins itself to the top; it competes
    // on its decayed confidence and sinks like anything else.
    const isFresh = it.age_hours <= floorFreshHours;
    const movingFast = velNorm >= velKeep;
    if (it.entity_floor && !it.muted && (isFresh || movingFast)) {
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
