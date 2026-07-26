// The Signal — daily: render the state blob (§4 output & home).
//
// A continuous living surface, not dated issues. This builds the JSON the home
// renders: masthead/status, Today & Tonight, Top Catches, dynamic domain
// sections, Also, the tappable tail (below-fold), and the footer stat. The home
// (index.html) and service worker consume this verbatim.

const DOMAIN_LABELS = {
  world: "World",
  local: "Local (NI)",
  gaming: "Gaming",
  football: "Football",
  tech_devices: "Tech & Devices",
  ai_engineering: "Tech / AI",
  golf: "Golf",
  // Sport beyond football/golf (WP-11). Labels mirror profile.js DOMAIN_META
  // exactly, so the fallback reads the same as the config-driven path.
  sport: "More Sport",
  cricket: "Cricket",
  cycling: "Cycling",
  athletics: "Athletics",
  motorsport: "Motorsport",
  lego: "LEGO",
  books: "Books",
  film_tv: "Film & TV",
  music: "Music",
  fitness: "Fitness",
  finance: "Money",
  travel: "Travel & Parks",
  history: "History",
  podcasts: "Listening",
};
// DOMAIN_LABELS is now only a FALLBACK — labels/editions/order are config-driven
// (config.profile.topic_weights[d].label/.edition + config.editions), resolved in
// buildState so a domain added in Settings flows through with no code change.

// Discussion context for an item, derived from its links (which persist as JSON,
// so no schema change): the liveliest discussion/post thread + its comment count.
function discussionFromLinks(links) {
  let best = null;
  for (const l of links || []) {
    if (l.type !== "discussion" && l.type !== "post") continue;
    if (!best || (l.count || 0) > (best.count || 0)) best = l;
  }
  if (!best) return null;
  return { url: best.url, label: best.label || null, comments: best.count ?? null };
}

function publicItem(it) {
  let links = it.links;
  if (typeof links === "string") {
    try { links = JSON.parse(links); } catch { links = []; }
  }
  return {
    id: it.id,
    title: it.title,
    summary: it.summary || null,
    hook: it.hook || null,
    register: it.register || null,
    domain: it.domain,
    domain_label: it.domain_label || null,
    edition: it.edition || null,
    links: links || [],
    entity_floor: !!it.entity_floor,
    entity_id: it.entity_id || null,
    source_type: it.source_type || null,
    source_count: it.source_count || 1,
    status: it.developing ? "developing" : null,
    days_active: it.developing ? (it.days_active || null) : null,
    // Developing-delta (D-2): what changed since this cluster was last surfaced
    // ({ was, now, was_label, now_label }). Null for items that haven't moved a
    // tier — so the state shape is unchanged for the vast majority of cards.
    delta: it.delta || null,
    signal_tier: it.signal_tier || null,
    discussion: discussionFromLinks(links),
    confidence: Math.round((it.confidence || 0) * 100) / 100,
    first_seen: it.first_seen,
    published: it.published,
  };
}

// Pick the best out-link URL for an item, mirroring the front-end's firstLink
// preference order (discussion → article → post → feed). Used so Start-here lines
// are tappable straight to the story.
function primaryLinkUrl(it) {
  let links = it.links;
  if (typeof links === "string") { try { links = JSON.parse(links); } catch { links = []; } }
  links = Array.isArray(links) ? links : [];
  const order = ["discussion", "article", "post", "feed"];
  for (const type of order) { const l = links.find((x) => x.type === type); if (l && l.url) return l.url; }
  return (links[0] && links[0].url) || it.canonical_url || null;
}

// "Today & Tonight" — only items with an ACTUAL date/time signal: fixtures with a
// kickoff/time, airings/releases dated today/tonight. A bare "v"/"vs" or a topic
// tag is not enough (those swept in a Nike-v-Adidas feature, a season review and
// a how-to-watch explainer). A feature/explainer is rejected even if it mentions
// a day, so the strip stays events-only; everything else stays in the brief.
const TT_DATED = /\b(tonight|today|this (?:evening|afternoon)|kick[- ]?off|\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\d{1,2}:\d{2}\b|(?:gmt|bst|cet|et|utc)\b|out now|releases? (?:today|tonight)|premier(?:es|ing) (?:today|tonight)|launch(?:es|ing) (?:today|tonight))\b/i;
const TT_FEATURE = /\b(how to watch|where to watch|review|rank(?:ed|ing)|best |worst |season review|explain(?:ed|er)|preview|predict(?:ion|ed)?|opinion|why |everything you need)\b/i;
// Which domains carry dated events belongs in config, not code: a topic opts in
// with `topic_weights[d].today_tonight: true`. Falls back to the original
// football/film/gaming set when no topic has flagged in (so an un-migrated config
// behaves exactly as before).
function todayAndTonight(items, now, tw) {
  const out = [];
  const flagged = new Set(Object.keys(tw || {}).filter((d) => tw[d] && tw[d].today_tonight));
  const eligible = flagged.size
    ? (d) => flagged.has(d)
    : (d) => d === "football" || d === "film_tv" || d === "gaming";
  // "Today" in a title only means today if the item is ACTUALLY from today — a
  // 2-day-old post saying "releases today" is stale. Gate on the item's real date
  // (publish time, or first-seen if undated) being within the last ~18h.
  const freshCut = now - 18 * 3.6e6;
  for (const it of items) {
    if (it.muted) continue;
    if (!eligible(it.domain)) continue;
    const when = it.published ?? it.first_seen ?? 0;
    if (when < freshCut) continue;
    const title = it.title || "";
    if (!TT_DATED.test(title) || TT_FEATURE.test(title)) continue;
    out.push(publicItem(it));
    if (out.length >= 6) break;
  }
  return out;
}

// Topic de-dup for Top Catches: collapse near-identical headlines (three
// Juventus-rumour variants that differ by a word — "swoop" vs "deal") to one
// strip entry. Token-set overlap is robust to that single-word drift in a way an
// exact signature is not. This is a safety net on top of ingest clustering.
const SIG_STOP = new Set([
  "the", "a", "an", "of", "to", "in", "on", "for", "and", "is", "are", "as",
  "at", "by", "with", "from", "this", "that", "new", "will", "after", "over",
  "eye", "eyes", "set", "out", "up", "has", "have", "deal", "move", "bid",
]);
function topicTokens(it) {
  return new Set(
    (it.title || "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 3 && !SIG_STOP.has(w))
  );
}
function tokenJaccard(a, b) {
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const t of a) if (b.has(t)) inter++;
  return inter / (a.size + b.size - inter);
}

// Fairness caps so no single high-volume domain (football in the transfer
// window) can crowd the brief or evict low-weight domains (World, Money, Books).
const SECTION_CAP = 5;       // "the few things to know" per topic (the rest roll up below)
const PER_SOURCE_SECTION = 3; // ≤N items from one source in a section (anti-firehose)
const PER_DOMAIN_BELOW = 30; // below-fold items kept per domain before the global cap
const BELOW_TOTAL_CAP = 400; // overall below-fold ceiling (keeps the state a brief)

export function buildState(items, meta, now, config) {
  const rc = (config && config.recency) || {};
  const maxCatchHours = rc.top_catch_max_hours || 30;
  const blend = rc.top_catch_recency_blend ?? 0.35;

  // Config-driven domain → label / edition / order. A topic carries its own
  // `label` + `edition` (config.profile.topic_weights[d]); editions are an ordered
  // config list. Unknown/unset → "more" catch-all + title-cased key. So a domain
  // added in Settings appears in its chosen edition with no code change.
  const tw = ((config && config.profile) || {}).topic_weights || {};
  const editionsList = (config && config.editions) || [{ id: "more", label: "More" }];
  const editionIds = new Set(editionsList.map((e) => e.id));
  const editionRank = {};
  editionsList.forEach((e, i) => { editionRank[e.id] = i; });
  const titleCase = (d) => String(d || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const labelFor = (d) => (tw[d] && tw[d].label) || DOMAIN_LABELS[d] || titleCase(d);
  const editionFor = (d) => {
    const e = tw[d] && tw[d].edition;
    return e && editionIds.has(e) ? e : "more";
  };
  const domainSort = (a, b) => {
    const ea = editionRank[editionFor(a)] ?? 99, eb = editionRank[editionFor(b)] ?? 99;
    if (ea !== eb) return ea - eb;
    const wa = (tw[a] && tw[a].weight) || 0, wb = (tw[b] && tw[b].weight) || 0;
    if (wb !== wa) return wb - wa;
    return a < b ? -1 : 1;
  };

  // Split muted out entirely; everything else is demote-never-drop.
  const live = items.filter((i) => !i.muted);
  // Bake edition + display label onto every item so the front-end groups by a
  // value it's handed (no hardcoded domain lists there either). publicItem reads these.
  for (const it of live) { it.edition = editionFor(it.domain); it.domain_label = labelFor(it.domain); }

  const aboveFold = live.filter((i) => i.above_fold);
  const belowFold = live.filter((i) => !i.above_fold);

  // Top Catches: up to 5, ranked, cross-domain. Eligibility is ABOVE THE FOLD —
  // the fold (confidence ≥ threshold, folding in relevance × register × recency)
  // is the quality bar. Among those, order by a recency-blended score so a fresh
  // strong item can lead a stale strong one. This is what keeps a fresh-but-empty
  // community post (a Reddit self-post with no upvotes/relevance, well below the
  // fold) out of the lead — only on-topic/popular items clear the fold. Diversity
  // caps keep one team/source/topic from owning the strip.
  const catchScore = (i) => (1 - blend) * (i.confidence || 0) + blend * (i.recency_score ?? 1);
  const ranked = aboveFold
    .filter((i) => (i.age_hours == null || i.age_hours <= maxCatchHours))
    .sort((a, b) => catchScore(b) - catchScore(a));

  const TOP_N = 5;
  const NEWS = new Set(["world", "finance"]);
  const top = [];
  const inTop = new Set();
  const perDomain = {};
  const perSource = {};
  const topToks = [];
  let floorCount = 0;
  const tryAdd = (it) => {
    if (top.length >= TOP_N || inTop.has(it.id)) return false;
    if ((perDomain[it.domain] || 0) >= 2) return false;       // ≤2 per domain
    if (it.source && (perSource[it.source] || 0) >= 1) return false; // ≤1 per source
    if (it.entity_floor && floorCount >= 1) return false;     // ≤1 core slot
    const toks = topicTokens(it);
    if (topToks.some((t) => t.domain === it.domain && tokenJaccard(t.set, toks) >= 0.6)) return false;
    top.push(it);
    inTop.add(it.id);
    perDomain[it.domain] = (perDomain[it.domain] || 0) + 1;
    if (it.source) perSource[it.source] = (perSource[it.source] || 0) + 1;
    if (it.entity_floor) floorCount++;
    topToks.push({ domain: it.domain, set: toks });
    return true;
  };
  for (const it of ranked) { if (top.length >= TOP_N) break; tryAdd(it); }

  // Swap the weakest evictable slot for a guaranteed pick (used for the one core
  // slot and the one news slot, so neither the firehose nor a quiet world day
  // erases them). `evictable` protects the other guarantee from being displaced.
  const guarantee = (pred, evictable) => {
    if (top.some(pred)) return;
    const cand = ranked.find((i) => pred(i) && !inTop.has(i.id));
    if (!cand) return;
    let worstIdx = -1, worst = Infinity;
    for (let k = 0; k < top.length; k++) {
      if (!evictable(top[k])) continue;
      const sc = catchScore(top[k]);
      if (sc < worst) { worst = sc; worstIdx = k; }
    }
    if (worstIdx === -1) {
      if (top.length < TOP_N) { top.push(cand); inTop.add(cand.id); }
      return;
    }
    inTop.delete(top[worstIdx].id);
    top[worstIdx] = cand;
    inTop.add(cand.id);
  };
  // One guaranteed-but-capped core slot (a fresh floor item, if any).
  guarantee((i) => i.entity_floor, (s) => !NEWS.has(s.domain) && !s.entity_floor);
  // One guaranteed top-news slot, independent of the floor (C1).
  guarantee((i) => NEWS.has(i.domain), (s) => !s.entity_floor && !NEWS.has(s.domain));

  top.sort((a, b) => catchScore(b) - catchScore(a));
  const topIds = new Set(top.map((t) => t.id));

  // Domain sections: dynamic — only domains with above-fold catches appear, in
  // fixed order. ALL above-fold items appear in their domain section (the
  // Headlines lead is a separate breadth array, so nothing is hidden behind it).
  // Each section is capped (SECTION_CAP); the overflow is reachable below the fold.
  const sectionItems = aboveFold;
  const byDomain = {};
  for (const it of sectionItems) {
    (byDomain[it.domain] ||= []).push(it);
  }

  const sections = [];
  const alsoDomains = [];
  const overflow = [];
  for (const d of Object.keys(byDomain).sort(domainSort)) {
    const edition = editionFor(d);
    // News & Money is "what's the news TODAY" — gate to fresh and order by date
    // (a half-step looser than Headlines). Stale above-fold news drops below the
    // fold via overflow. Other editions stay confidence-ordered (browsing).
    let list;
    if (edition === "news_money") {
      const fresh = [], stale = [];
      for (const it of (byDomain[d] || [])) {
        ((it.age_hours == null || it.age_hours <= maxCatchHours) ? fresh : stale).push(it);
      }
      overflow.push(...stale);
      list = fresh.sort((a, b) => (b.published || b.first_seen || 0) - (a.published || a.first_seen || 0));
    } else {
      list = (byDomain[d] || []).sort((a, b) => b.confidence - a.confidence);
    }
    if (!list.length) continue;
    if (list.length <= 1) {
      // Low-volume domain → "Also" one-liner (§4.5).
      alsoDomains.push({ domain: d, edition, label: labelFor(d), item: publicItem(list[0]) });
    } else {
      // Per-source cap so one high-volume feed (e.g. Football Italia) can't own a
      // section: keep ≤PER_SOURCE_SECTION from any single source; everything that
      // doesn't fit (section cap or source cap) drops below the fold. `list` is
      // already sorted by confidence, so the kept items are the strongest.
      const picked = [];
      const perSrc = {};
      for (const it of list) {
        const src = it.source || "?";
        if (picked.length < SECTION_CAP && (perSrc[src] || 0) < PER_SOURCE_SECTION) {
          perSrc[src] = (perSrc[src] || 0) + 1;
          picked.push(it);
        } else {
          overflow.push(it);
        }
      }
      sections.push({
        domain: d,
        edition,
        label: labelFor(d),
        items: picked.map(publicItem),
      });
    }
  }

  // Per-interest completeness: every interest with content surfaces at least one
  // line — even on a quiet day when its best item is below the fold — so the brief
  // feels complete per-interest (the "I've seen everything in my niche today" job)
  // instead of silently dropping a whole domain. The loud days are unchanged; this
  // only adds the quiet domains that the fold would otherwise erase.
  const represented = new Set([
    ...sections.map((s) => s.domain),
    ...alsoDomains.map((a) => a.domain),
    ...top.map((t) => t.domain),
  ]);
  const bestByDomain = {};
  for (const it of live) {
    if (topIds.has(it.id)) continue;
    const d = it.domain;
    if (!bestByDomain[d] || catchScore(it) > catchScore(bestByDomain[d])) bestByDomain[d] = it;
  }
  for (const d of Object.keys(bestByDomain).sort(domainSort)) {
    if (represented.has(d) || !bestByDomain[d]) continue;
    alsoDomains.push({ domain: d, edition: editionFor(d), label: labelFor(d), item: publicItem(bestByDomain[d]), quiet: true });
  }

  // Below the fold (§4.6): demote, never drop. Per-domain fairness FIRST so a
  // 112-item football firehose can't evict World/Money/Books past the global
  // cap — every domain that pulled articles keeps a slice. Section overflow
  // (strong items that didn't fit their capped section) folds in here too.
  const belowPool = belowFold.concat(overflow).filter((i) => !topIds.has(i.id));
  const grouped = {};
  for (const it of belowPool) (grouped[it.domain] ||= []).push(it);
  let belowKept = [];
  for (const d of Object.keys(grouped)) {
    belowKept.push(
      ...grouped[d].sort((a, b) => b.confidence - a.confidence).slice(0, PER_DOMAIN_BELOW)
    );
  }
  belowKept = belowKept.sort((a, b) => b.confidence - a.confidence).slice(0, BELOW_TOTAL_CAP);

  // Edition framing: a dated header + a mechanical "Start here" (the top fresh
  // catch titles) so the brief reads like a morning edition, not a feed.
  let dateLabel = "";
  let hour = 0;
  try {
    dateLabel = new Date(now).toLocaleDateString("en-GB", {
      weekday: "long", day: "numeric", month: "long",
    });
    hour = new Date(now).getUTCHours(); // reader is UK (UTC/BST) — UTC hour is close enough
  } catch (_) {}
  // Morning / evening framing (D-3, mechanical): before ~1pm the brief is the
  // morning lead; after, it's the evening "what moved since this morning" recap.
  // The front-end reflects this in the masthead/status line only — the content is
  // the same living surface either way.
  const edition_phase = hour < 13 ? "morning" : "evening";

  // Communities (§ Reddit/HN/Bluesky): every community-sourced live item, ranked,
  // so "catch up on everything from Reddit/HN in one place" misses nothing — not
  // fold-limited. Grouped by source on the home.
  // Ordered by confidence (relevance + popularity), NOT recency — so an on-topic
  // or upvoted thread ranks above a fresh-but-empty self-post.
  const COMMUNITY_SRC = new Set(["reddit", "hn", "bluesky"]);
  const communities = live
    .filter((i) => COMMUNITY_SRC.has(i.source_type))
    .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
    .slice(0, 80)
    .map(publicItem);

  // Headlines: the genuinely BIG stories — ranked by BIGNESS (breadth × confidence),
  // not raw interest score. Cross-domain, capped ≤2/domain, deduped. Eligibility is
  // broadened beyond News/Sport (which, on a football/gaming-heavy day, collapsed
  // Headlines to ~2): a story qualifies if it's corroborated (≥2 feeds), a News/Sport
  // item, a core-entity catch, a confirmed/official item, OR genuinely strong in ANY
  // domain (confidence ≥ headline_strong_conf). The ≤2/domain cap + dedup keep it a
  // real headline set — a spread of the day's biggest things — not "top scores
  // across everything", while still letting a strong Gaming/Books/Tech story lead.
  // WP-11: the sport half of this set was football+golf only, so a Test match, a
  // grand-tour GC swing or a world record could not qualify as a big Sport story
  // however big it was. `motorsport` is deliberately EXCLUDED: `interest_depth:
  // "results_only"` means a race win still reaches Headlines via corroboration
  // (≥2 feeds) or a confirmed/official title, but a session-by-session item does
  // not get the free pass the other sports get.
  const NEWS_SPORT = new Set([
    "world", "local", "finance",
    "football", "golf", "sport", "cricket", "cycling", "athletics",
  ]);
  // Importance = breadth-lifted confidence + a bonus for a high-signal (confirmed/
  // official) story, so a genuinely consequential item leads — not whatever the
  // firehose pushed up. confidence already folds in the content-led signal tiers.
  const sc = (config && config.scoring) || {};
  const signalBonus = sc.headline_signal_bonus ?? 0.15;
  const strongConf = sc.headline_strong_conf ?? 0.75; // bar for a non-News/Sport story to lead
  const importance = (i) =>
    (i.confidence || 0) * (1 + 0.25 * Math.min(3, (i.source_count || 1) - 1)) +
    (i.signal_high ? signalBonus : 0);
  const headlineMax = (config && config.headline_max) || 8;
  const headlineEligible = (i) =>
    (i.source_count || 1) >= 2 ||        // corroborated across ≥2 of the reader's feeds
    NEWS_SPORT.has(i.domain) ||          // a genuinely big News/Sport story
    i.entity_floor ||                    // a core must-not-miss entity
    i.signal_high ||                     // confirmed/official/announced
    (i.confidence || 0) >= strongConf;   // genuinely strong in any domain (gaming, books, tech…)
  const hRanked = aboveFold
    .filter((i) => (i.age_hours == null || i.age_hours <= maxCatchHours) && headlineEligible(i))
    .sort((a, b) => importance(b) - importance(a));
  const headlines = [];
  const hToks = [];
  const hDomain = {};
  for (const it of hRanked) {
    if (headlines.length >= headlineMax) break;
    if ((hDomain[it.domain] || 0) >= 2) continue;
    const toks = topicTokens(it);
    if (hToks.some((t) => tokenJaccard(t, toks) >= 0.45)) continue;
    headlines.push(it);
    hDomain[it.domain] = (hDomain[it.domain] || 0) + 1;
    hToks.push(toks);
  }

  // Top 20 across everything — one trustworthy ranked feed (the content-led
  // ranking + firehose cap make this meaningful). Cross-domain, importance-ranked,
  // diversity-capped (≤3/domain, ≤2/source) and deduped so no single team/feed owns it.
  const t20Ranked = live
    .filter((i) => (i.confidence || 0) > 0)
    .sort((a, b) => importance(b) - importance(a));
  // Build a wider pool (≤30): the first 20 are the mechanical Top 20 (the degrade
  // target); the full pool is the candidate set the AI-curate pass orders from.
  const top20wide = [];
  const t20Toks = [];
  const t20Dom = {};
  const t20Src = {};
  for (const it of t20Ranked) {
    if (top20wide.length >= 30) break;
    if ((t20Dom[it.domain] || 0) >= 3) continue;
    if (it.source && (t20Src[it.source] || 0) >= 2) continue;
    const toks = topicTokens(it);
    if (t20Toks.some((t) => tokenJaccard(t, toks) >= 0.45)) continue;
    top20wide.push(it);
    t20Dom[it.domain] = (t20Dom[it.domain] || 0) + 1;
    if (it.source) t20Src[it.source] = (t20Src[it.source] || 0) + 1;
    t20Toks.push(toks);
  }
  const top20 = top20wide.slice(0, 20);

  // "Still developing" (D-2): the small recurring thread of stories the reader is
  // FOLLOWING — developing clusters whose signal tier moved since they were last
  // surfaced (they carry a `delta`). Ranked by confidence, capped so it stays a
  // thread, not a feed. Empty on a day when nothing moved a tier.
  const developing = live
    .filter((i) => i.developing && i.delta)
    .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
    .slice(0, 6)
    .map(publicItem);

  return {
    generated_at: now,
    status: {
      caught_up: true,
      time: new Date(now).toISOString(),
    },
    edition: { date_label: dateLabel, phase: edition_phase },
    edition_phase,
    editions: editionsList,
    top20: top20.map(publicItem),
    // Start here — tappable, voiced, linked (not bare titles). `why` seeds from the
    // mechanical hook here; augmentEditorial backfills the curated "why it matters"
    // for any of these that also land in Picks/Top 20, so it reuses the lead's reason.
    start_here: top.slice(0, 3).map((t) => ({
      id: t.id,
      title: t.title,
      why: t.hook || null,
      link: primaryLinkUrl(t),
    })),
    today_tonight: todayAndTonight(live, now, tw),
    headlines: headlines.map(publicItem),
    developing,
    // Wider breadth-eligible pool the AI Editor's Picks pass curates from (when on);
    // ignored by the front-end. Already importance-sorted (hRanked).
    headline_candidates: hRanked.slice(0, 16).map(publicItem),
    // Wider Top-20 pool the AI-curate pass orders from (when on); stripped after, ignored by the front-end.
    top20_candidates: top20wide.map(publicItem),
    sections,
    also: alsoDomains,
    communities,
    below_fold: belowKept.map(publicItem),
    footer: {
      kept: live.length,
      scanned: meta.scanned,
      sources: meta.sources,
      below_fold_count: belowFold.length,
      enrichment: meta.enrichment, // { on, degraded, reason }
    },
  };
}
