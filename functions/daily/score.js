// The Signal — daily: the triage engine (§3 Tier 1 steps 3–7).
//
// "The engine, not the sources, is the value." This is the source-agnostic core:
// per-source baseline normalisation, velocity, profile-weighted ranking, the
// named-entity floor, mutes/special-handling, and the fold.

import {
  addSourceSample, sourceBaselineCut, lastStoryPoint, logStory,
} from "./db.js";

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
  let best = 0;
  const tw = profile.topic_weights || {};
  // Prefer the item's own domain weighting, but scan all domains so a
  // cross-domain item (e.g. HN tagged ai_engineering but about gaming) still
  // surfaces under the right interest.
  let bestDomain = item.domain;
  for (const [domain, spec] of Object.entries(tw)) {
    let hits = 0;
    for (const kw of spec.keywords) if (h.includes(lc(kw))) hits++;
    if (hits === 0) continue;
    const sat = 1 - Math.pow(0.6, hits); // diminishing returns
    const s = spec.weight * sat;
    if (s > best) {
      best = s;
      bestDomain = domain;
    }
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
// `items` are clustered items (from dedup). Mutates them with score fields.
export async function scoreBatch(db, items, config, now) {
  const profile = config.profile;
  const extraMutes = config.mutes || [];
  const baselineWindow = now - 1000 * 60 * 60 * 24 * 30;

  // 1) record source samples + compute each source's baseline cut once.
  const cuts = new Map();
  for (const it of items) {
    await addSourceSample(db, it.source, it.rawScore, now);
  }
  const sources = [...new Set(items.map((i) => i.source))];
  for (const s of sources) {
    cuts.set(s, await sourceBaselineCut(db, s, baselineWindow));
  }

  for (const it of items) {
    // 2) per-source baseline normalisation (§3.3): how significant for THIS
    //    source vs its trailing top-15% cut.
    const cut = cuts.get(it.source);
    if (cut && cut > 0) {
      it.baseline_score = Math.max(0, Math.min(1, it.rawScore / (cut * 1.5)));
    } else {
      // No history yet (RSS or new source): lean on recency.
      const ageH = (now - (it.published || now)) / 3.6e6;
      it.baseline_score = ageH < 6 ? 0.7 : ageH < 24 ? 0.5 : 0.3;
    }

    // 3) velocity (§3.4): Δscore/Δhr vs the last logged point for this cluster.
    const prev = await lastStoryPoint(db, it.id, now);
    if (prev && prev.ts) {
      const dh = Math.max(0.25, (now - prev.ts) / 3.6e6);
      it.velocity = Math.max(0, (it.rawScore - prev.score) / dh);
    } else {
      it.velocity = 0;
    }
    const velNorm = Math.min(1, it.velocity / 20);

    // 4) profile-weighted ranking (§3.6) + entity floor + mutes.
    // For an already-enriched item the saved profile_score carries Tier-2's
    // semantic relevance (judged once); keep it if it beats the mechanical
    // pass so a good hook doesn't drop below the fold on the next poll.
    const loadedProfile = it.profile_score || 0;
    const pr = scoreProfile(it, profile, extraMutes);
    it.profile_score = it.enriched ? Math.max(pr.score, loadedProfile) : pr.score;
    it.entity_floor = pr.entityFloor;
    it.muted = pr.muted;

    // 5) confidence: blend interest, source-significance and velocity, scaled by
    //    the source weight. Demote (UK politics etc.) halves it.
    let conf =
      0.55 * it.profile_score +
      0.30 * it.baseline_score +
      0.15 * velNorm;
    conf *= 0.6 + 0.4 * (it.weight || 0.5);
    if (pr.demote) conf *= 0.4;
    if (it.muted) conf = 0;
    // Named-entity floor bypasses ranking — pinned above the fold (§4).
    if (it.entity_floor && !it.muted) conf = Math.max(conf, 0.95);
    it.confidence = Math.max(0, Math.min(1, conf));

    // 6) the fold (§3.7): above-fold = over the confidence threshold (not a
    //    fixed count). Entity-floor items are always above.
    it.above_fold = !it.muted && (it.entity_floor || it.confidence >= config.fold_threshold);

    // Log the story point for the weekly's movement evidence + future velocity.
    if (!it.muted) {
      await logStory(db, it.id, it.rawScore, it.title, it.domain, now);
    }
  }

  return items;
}
