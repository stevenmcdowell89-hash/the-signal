// The Signal — daily: render the state blob (§4 output & home).
//
// A continuous living surface, not dated issues. This builds the JSON the home
// renders: masthead/status, Today & Tonight, Top Catches, dynamic domain
// sections, Also, the tappable tail (below-fold), and the footer stat. The home
// (index.html) and service worker consume this verbatim.

const DOMAIN_LABELS = {
  world: "World",
  gaming: "Gaming",
  football: "Football",
  tech_devices: "Tech & Devices",
  ai_engineering: "Tech / AI",
  golf: "Golf",
  lego: "LEGO",
  books: "Books",
  film_tv: "Film & TV",
  music: "Music",
  fitness: "Fitness",
  finance: "Money",
  travel: "Travel & Parks",
  history: "History",
  podcasts: "Listening",
  home_selfhosting: "Home / Self-hosting",
};

// Fixed domain order so sections are stable issue-to-issue (a quiet domain is
// simply absent — no padding, §4.4).
const DOMAIN_ORDER = [
  "world", "gaming", "football", "tech_devices", "ai_engineering", "books",
  "film_tv", "music", "golf", "lego", "fitness", "finance", "travel",
  "history", "podcasts", "home_selfhosting",
];

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
    links: links || [],
    entity_floor: !!it.entity_floor,
    confidence: Math.round((it.confidence || 0) * 100) / 100,
    first_seen: it.first_seen,
    published: it.published,
  };
}

// Lightweight "Today & Tonight" extraction: dated/imminent fixtures & releases
// surfaced from the catches (kept simple in Phase 1 — pattern match on dated
// language). Each links out (§5).
function todayAndTonight(items, now) {
  const out = [];
  const re = /(tonight|today|kick[- ]?off|vs\.?|v\b|fixtures?|premiere|out now|releases? today|launch(es)? today)/i;
  for (const it of items) {
    if (it.muted) continue;
    if ((it.domain === "football" || it.domain === "film_tv" || it.domain === "gaming") && re.test(it.title)) {
      out.push(publicItem(it));
    }
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
const SECTION_CAP = 8;       // items shown in a domain's All-view section
const PER_DOMAIN_BELOW = 30; // below-fold items kept per domain before the global cap
const BELOW_TOTAL_CAP = 400; // overall below-fold ceiling (keeps the state a brief)

export function buildState(items, meta, now, config) {
  const rc = (config && config.recency) || {};
  const maxCatchHours = rc.top_catch_max_hours || 30;
  const blend = rc.top_catch_recency_blend ?? 0.35;

  // Split muted out entirely; everything else is demote-never-drop.
  const live = items.filter((i) => !i.muted);

  const aboveFold = live.filter((i) => i.above_fold);
  const belowFold = live.filter((i) => !i.above_fold);

  // Top Catches: 3–5, ranked, cross-domain. Only genuinely fresh items are
  // eligible (no 4-day-old item can lead). Order blends confidence with recency
  // so a fresh strong story beats a slightly-stronger-but-older one. Cap at 2
  // per domain AND dedupe by topic signature so the strip stays varied.
  const catchScore = (i) => (1 - blend) * (i.confidence || 0) + blend * (i.recency_score ?? 1);
  const eligible = aboveFold.filter((i) => (i.age_hours == null || i.age_hours <= maxCatchHours));
  const ranked = eligible.slice().sort((a, b) => catchScore(b) - catchScore(a));
  const top = [];
  const perTop = {};
  const topToks = [];
  for (const it of ranked) {
    if (top.length >= 5) break;
    if ((perTop[it.domain] || 0) >= 2) continue;
    const toks = topicTokens(it);
    // Skip a same-domain headline that substantially overlaps one already in.
    if (topToks.some((t) => t.domain === it.domain && tokenJaccard(t.set, toks) >= 0.6)) continue;
    top.push(it);
    perTop[it.domain] = (perTop[it.domain] || 0) + 1;
    topToks.push({ domain: it.domain, set: toks });
  }
  const topIds = new Set(top.map((t) => t.id));

  // Domain sections: dynamic — only domains with above-fold catches appear, in
  // fixed order. Items already in Top Catches are not repeated. Each section is
  // capped (SECTION_CAP); the overflow is still reachable below the fold (under
  // that domain's sub-tab), it just doesn't bury the cross-domain All view.
  const sectionItems = aboveFold.filter((i) => !topIds.has(i.id));
  const byDomain = {};
  for (const it of sectionItems) {
    (byDomain[it.domain] ||= []).push(it);
  }

  const sections = [];
  const alsoDomains = [];
  const overflow = [];
  for (const d of DOMAIN_ORDER) {
    const list = (byDomain[d] || []).sort((a, b) => b.confidence - a.confidence);
    if (!list.length) continue;
    if (list.length <= 1) {
      // Low-volume domain → "Also" one-liner (§4.5).
      alsoDomains.push({ domain: d, label: DOMAIN_LABELS[d] || d, item: publicItem(list[0]) });
    } else {
      sections.push({
        domain: d,
        label: DOMAIN_LABELS[d] || d,
        items: list.slice(0, SECTION_CAP).map(publicItem),
      });
      if (list.length > SECTION_CAP) overflow.push(...list.slice(SECTION_CAP));
    }
  }

  // Below the fold (§4.6): demote, never drop. Per-domain fairness FIRST so a
  // 112-item football firehose can't evict World/Money/Books past the global
  // cap — every domain that pulled articles keeps a slice. Section overflow
  // (strong items that didn't fit their capped section) folds in here too.
  const belowPool = belowFold.concat(overflow);
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
  try {
    dateLabel = new Date(now).toLocaleDateString("en-GB", {
      weekday: "long", day: "numeric", month: "long",
    });
  } catch (_) {}

  return {
    generated_at: now,
    status: {
      caught_up: true,
      time: new Date(now).toISOString(),
    },
    edition: { date_label: dateLabel },
    start_here: top.slice(0, 3).map((t) => t.title),
    today_tonight: todayAndTonight(live, now),
    top_catches: top.map(publicItem),
    sections,
    also: alsoDomains,
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
