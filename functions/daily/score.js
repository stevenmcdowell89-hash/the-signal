// The Signal — daily: the triage engine (§3 Tier 1 steps 3–7).
//
// "The engine, not the sources, is the value." This is the source-agnostic core:
// per-source baseline normalisation, velocity, profile-weighted ranking, the
// named-entity floor, mutes/special-handling, and the fold.

import {
  sourceBaselineCut, getLastStoryPoints, bulkInsertSamples, bulkLogStories,
} from "./db.js";

const DISCUSSION = new Set(["hn", "bluesky", "reddit"]);

// Register weights the ranking (A3): a consequential story outranks a take, which
// outranks colour/gossip — so the enrichment tag the cards already show actually
// moves the needle instead of being decoration. Un-enriched items (most of the
// firehose) get a neutral default; only the shortlist carries a register.
const REGISTER_WEIGHT = { consequential: 1.0, discovery: 0.95, take: 0.8, colour: 0.55 };
const REGISTER_NEUTRAL = 0.85;

const lc = (s) => (s || "").toLowerCase();

function matchesAny(hay, patterns) {
  const h = lc(hay);
  return (patterns || []).some((p) => h.includes(lc(p)));
}

// Effective high/low signal word lists for a domain: the global signal_tiers plus
// any per-topic overrides (topic_weights[d].signal_high/.signal_low), merged.
function signalTiersFor(profile, domain) {
  const g = profile.signal_tiers || {};
  const t = (profile.topic_weights || {})[domain] || {};
  return {
    high: (t.signal_high || []).concat(g.high || []),
    low: (t.signal_low || []).concat(g.low || []),
  };
}

// Profile-weighted relevance for one item, purely mechanical (Tier 1).
// Returns { score 0..1, entityFloor, entityId, muted, demote, signalHigh }.
export function scoreProfile(item, profile, extraMutes, scoring) {
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

  // Named-entity floor (§4): a bounded boost + a guaranteed-but-capped slot
  // (applied in scoreBatch / render), NOT a ranking bypass. A matched entity also
  // carries a `domain` that DOMINATES classification below, so a colliding topic
  // keyword (e.g. "director" in film_tv) can't re-home a core item.
  let entityFloor = false;
  let floorDomain = null;
  let entityId = null;
  for (const e of profile.named_entity_floor || []) {
    if (matchesAny(title, e.patterns)) {
      entityFloor = true;
      floorDomain = e.domain || null;
      entityId = e.id || null;
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
  // item re-homes — but PREFER the feed's own (authoritative) domain, and only let
  // a FOREIGN domain claim the item on a real signal (≥2 keyword hits). A single
  // stray token ("anniversary", "episode", "score") must NOT re-home a story into
  // a feedless niche (History/Listening) when its own feed-domain didn't match.
  const ownDomain = item.feed_domain || item.domain;
  let best = 0;
  let bestDomain = ownDomain;
  let ownScore = 0;
  for (const [domain, spec] of Object.entries(tw)) {
    let hits = 0;
    for (const kw of spec.keywords) if (kwHit(kw)) hits++;
    if (hits === 0) continue;
    const s = spec.weight * (1 - Math.pow(0.6, hits)); // diminishing returns
    if (domain === ownDomain) { ownScore = s; continue; } // own handled below
    if (hits >= 2 && s > best) { best = s; bestDomain = domain; } // foreign needs ≥2
  }
  // Keep the feed's own domain unless a qualifying foreign domain beat it by a
  // clear margin. If nothing qualified (best 0), this keeps ownDomain — so an item
  // whose feed-domain scored 0 stays put rather than being dumped into a niche.
  if (ownScore >= best || best <= ownScore * 1.25) {
    bestDomain = ownDomain;
    best = ownScore;
  }
  // A floor-entity match dominates the domain (B2): the entity's declared domain
  // wins over keyword scoring, so "ex-Sassuolo director hints at Juventus role"
  // can't land in film_tv on the back of "director".
  if (floorDomain) bestDomain = floorDomain;
  item.domain = bestDomain;

  // Content-led signal tiers (§3.6): a CONFIRMED/OFFICIAL title is lifted, a
  // RUMOUR/LINKED title is buried — title-only (whole-word for single tokens, so
  // "may" the month/name doesn't fire on substrings). This rides the interest
  // score (the dominant term), so a confirmed story from a small feed beats a
  // rumour from a firehose. Clamped so stacked low-signal words can't zero it.
  const titleWords = new Set(h.split(/[^a-z0-9]+/).filter(Boolean));
  const titleHit = (kw) => {
    kw = lc(kw).trim();
    return /[^a-z0-9]/.test(kw) ? h.includes(kw) : titleWords.has(kw);
  };
  const tiers = signalTiersFor(profile, bestDomain);
  const sc = scoring || {};
  const hiHit = tiers.high.some(titleHit);
  let signal = 1;
  if (hiHit) signal *= (sc.signal_high ?? 1.6);
  if (tiers.low.some(titleHit)) signal *= (sc.signal_low ?? 0.5);
  best = Math.max(0, best) * Math.max(0.3, Math.min(2, signal));

  // Special handling: suppression + demotion (§7.6).
  let demote = false;
  const sh = (profile.special_handling || {})[bestDomain];
  if (sh) {
    if (matchesAny(title, sh.suppress_patterns)) {
      return { score: 0, entityFloor, muted: true, demote: false };
    }
    if (matchesAny(title, sh.demote_patterns)) demote = true;
  }

  return { score: best, entityFloor, entityId, muted: false, demote, signalHigh: hiHit };
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
  const floorBoost = rc.floor_boost ?? 0.12; // bounded core lift (not a bypass)

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
    const pr = scoreProfile(it, profile, extraMutes, config.scoring);
    it.profile_score = it.enriched ? Math.max(pr.score, loadedProfile) : pr.score;
    it.entity_floor = pr.entityFloor;
    it.entity_id = pr.entityId || null;
    it.signal_high = !!pr.signalHigh;
    it.muted = pr.muted;

    // 4) confidence: blend interest + source-significance, scale by source
    //    weight, then apply recency. A genuinely moving story (high velocity)
    //    resists decay so breaking news isn't aged out the moment it's caught.
    // Relevance gate: HN is a broad firehose (its whole front page), so an HN
    // item with NO interest-keyword match must not ride HN-popularity into the
    // brief ("Google hits 50% IPv6"). Damp its baseline hard. Reddit/Bluesky are
    // user-curated (the sub/handle choice IS the relevance), so they're exempt.
    let effBaseline = it.baseline_score;
    if (it.source_type === "hn" && it.profile_score < 0.05) effBaseline *= 0.2;
    // Content-led: interest relevance leads; source weight is a light tiebreaker
    // (±7.5%, was ±40%) so a feed's volume can't muscle low-relevance items up.
    const sc = config.scoring || {};
    let base = (sc.profile_weight ?? 0.70) * it.profile_score + (sc.baseline_weight ?? 0.30) * effBaseline;
    base *= (sc.weight_floor ?? 0.85) + (sc.weight_span ?? 0.15) * (it.weight || 0.5);
    if (pr.demote) base *= 0.4;
    const recencyLifted = Math.min(1, recency + 0.6 * velNorm * (1 - recency));
    it.recency_score = recencyLifted;
    const regW = it.register ? (REGISTER_WEIGHT[it.register] ?? REGISTER_NEUTRAL) : REGISTER_NEUTRAL;
    let conf = it.muted ? 0 : base * recencyLifted * regW;
    it.confidence = Math.max(0, Math.min(1, conf));

    // 5) the named-entity floor — a BOUNDED BOOST, not a bypass. A fresh (or still
    //    moving) core item gets a capped lift so it can earn a place, but a strong
    //    non-core item can still outrank a weak core one, and a stale core item
    //    (the 4-day-old rumour) sinks. The guaranteed-but-capped core slot itself
    //    is awarded in render. The fold is then a plain threshold.
    const isFresh = it.age_hours <= floorFreshHours;
    const movingFast = velNorm >= velKeep;
    if (it.entity_floor && !it.muted && (isFresh || movingFast)) {
      it.confidence = Math.min(1, it.confidence + floorBoost);
    }

    // 5b) Developing: an evolving story (a transfer saga, a rumour that keeps
    //     moving) — a cluster that has persisted across polls (it was surfaced
    //     before, so `prev` exists) and has spanned more than ~a day. Flag it for
    //     the "Developing" badge, and when it's still active give it a small
    //     bounded lift so a live saga isn't aged out on a day with no new article.
    const ageDays = it.first_seen ? (now - it.first_seen) / 8.64e7 : 0;
    it.days_active = Math.max(1, Math.round(ageDays));
    it.developing = !it.muted && !!prev && ageDays >= 1;
    if (it.developing && (isFresh || movingFast)) {
      it.confidence = Math.min(1, it.confidence + (rc.developing_boost ?? 0.05));
    }

    it.above_fold = !it.muted && it.confidence >= fold;

    // Log a story point only for surfaced catches + discussion items (movement
    // evidence for the weekly + future velocity) — not the whole firehose.
    if (!it.muted && (it.above_fold || DISCUSSION.has(it.source_type))) {
      storyRows.push({ cluster_id: it.id, ts: now, score: it.rawScore, headline: it.title, domain: it.domain });
    }
  }

  // Per-(source, domain) firehose cap: within ONE feed's items in ONE domain, the
  // lower-ranked tail gets a graded confidence penalty — so a single high-volume
  // feed (Football Italia in the transfer window) can't flood a section OR push its
  // 4th/5th item into Headlines / Top 20. Penalty, not removal (demote-never-drop):
  // capped items still surface below the fold. Runs BEFORE the fold is finalised.
  const capN = (config.scoring && config.scoring.source_cap) ?? 3;
  const capPenalty = (config.scoring && config.scoring.source_cap_penalty) ?? 0.6;
  const groups = new Map();
  for (const it of items) {
    if (it.muted) continue;
    const k = (it.source || "?") + "|" + it.domain;
    let arr = groups.get(k);
    if (!arr) { arr = []; groups.set(k, arr); }
    arr.push(it);
  }
  for (const arr of groups.values()) {
    if (arr.length <= capN) continue;
    arr.sort((a, b) => b.confidence - a.confidence);
    for (let r = capN; r < arr.length; r++) {
      arr[r].confidence = Math.max(0, arr[r].confidence * Math.pow(capPenalty, r - capN + 1));
      arr[r].source_capped = true;
    }
  }
  // Re-finalise the fold after the cap so capped firehose items drop below it.
  for (const it of items) it.above_fold = !it.muted && it.confidence >= fold;

  await bulkInsertSamples(db, sampleRows);
  await bulkLogStories(db, storyRows);
  return items;
}
