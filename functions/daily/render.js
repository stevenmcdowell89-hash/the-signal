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

export function buildState(items, meta, now) {
  // Split muted out entirely; everything else is demote-never-drop.
  const live = items.filter((i) => !i.muted);

  const aboveFold = live.filter((i) => i.above_fold);
  const belowFold = live.filter((i) => !i.above_fold);

  // Top Catches: 3–5, ranked, cross-domain. Rank alone carries "read first" —
  // no narrative orientation line (§4.3). Bias toward domain diversity.
  const ranked = aboveFold.slice().sort((a, b) => b.confidence - a.confidence);
  const top = [];
  const topDomains = new Set();
  for (const it of ranked) {
    if (top.length >= 5) break;
    if (top.length >= 3 && topDomains.has(it.domain)) continue;
    top.push(it);
    topDomains.add(it.domain);
  }
  const topIds = new Set(top.map((t) => t.id));

  // Domain sections: dynamic — only domains with above-fold catches appear, in
  // fixed order. Items already in Top Catches are not repeated.
  const sectionItems = aboveFold.filter((i) => !topIds.has(i.id));
  const byDomain = {};
  for (const it of sectionItems) {
    (byDomain[it.domain] ||= []).push(it);
  }

  const sections = [];
  const alsoDomains = [];
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
        items: list.map(publicItem),
      });
    }
  }

  return {
    generated_at: now,
    status: {
      caught_up: true,
      time: new Date(now).toISOString(),
    },
    today_tonight: todayAndTonight(live, now),
    top_catches: top.map(publicItem),
    sections,
    also: alsoDomains,
    // Tappable tail: the full retained set below the fold (§4.6). Demote, never
    // drop — a ranking mistake costs a scroll, not a missed story.
    below_fold: belowFold
      .sort((a, b) => b.confidence - a.confidence)
      .map(publicItem),
    footer: {
      kept: live.length,
      scanned: meta.scanned,
      sources: meta.sources,
      below_fold_count: belowFold.length,
      enrichment: meta.enrichment, // { on, degraded, reason }
    },
  };
}
