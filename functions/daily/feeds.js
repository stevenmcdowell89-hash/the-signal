// The Signal — daily: starter feed set (§8 of the build prompt).
//
// Every feed is tagged by `domain` (must match a key in the interest profile's
// topic_weights) and carries a per-source `weight` multiplier. `stable: true`
// marks the feeds the build prompt verified; the rest are conventional paths
// that are validated on first ingest and dropped gracefully if dead.
//
// This is only the *default* set seeded into KV on first run. After that the
// live source list lives in DAILY_CONFIG and is edited in-app — never here.
//
// Reddit (P2) and Bluesky handles are intentionally absent: Reddit waits on
// the Data API approval (Phase 2), Bluesky handles are the reader's to add.

export const STARTER_FEEDS = [
  // ---- World (0.4) ----
  { id: "bbc-news", type: "rss", domain: "world", weight: 0.4, url: "https://feeds.bbci.co.uk/news/rss.xml", stable: true, name: "BBC News" },
  { id: "bbc-world", type: "rss", domain: "world", weight: 0.4, url: "https://feeds.bbci.co.uk/news/world/rss.xml", stable: true, name: "BBC World" },
  { id: "guardian-world", type: "rss", domain: "world", weight: 0.4, url: "https://www.theguardian.com/world/rss", name: "Guardian World" },

  // ---- Gaming (0.9) ----
  { id: "eurogamer", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.eurogamer.net/feed", name: "Eurogamer" },
  { id: "nintendo-life", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.nintendolife.com/feeds/latest", name: "Nintendo Life" },
  { id: "push-square", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.pushsquare.com/feeds/latest", name: "Push Square" },
  { id: "rps", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.rockpapershotgun.com/feed", name: "Rock Paper Shotgun" },

  // ---- Football (0.85) ----
  { id: "bbc-football", type: "rss", domain: "football", weight: 0.85, url: "https://feeds.bbci.co.uk/sport/football/rss.xml", stable: true, name: "BBC Sport Football" },
  { id: "guardian-football", type: "rss", domain: "football", weight: 0.85, url: "https://www.theguardian.com/football/rss", name: "Guardian Football" },
  { id: "football-italia", type: "rss", domain: "football", weight: 0.85, url: "https://football-italia.net/feed/", name: "Football Italia" },

  // ---- Tech & Devices (0.75) ----
  { id: "9to5google", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://9to5google.com/feed/", name: "9to5Google" },
  { id: "android-authority", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://www.androidauthority.com/feed/", name: "Android Authority" },
  { id: "the-verge", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://www.theverge.com/rss/index.xml", name: "The Verge" },

  // ---- Tech/AI & Engineering (0.7) ----
  { id: "cloudflare-blog", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://blog.cloudflare.com/rss/", stable: true, name: "Cloudflare Blog" },
  { id: "svpg", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://www.svpg.com/articles/feed/", name: "SVPG" },

  // Hacker News (auto) — serves both gaming-adjacent and AI/engineering; tagged
  // ai_engineering, re-domained per item at ingest by keyword if it clearly fits
  // another domain. Fetched via the Algolia front-page API (JSON, no parsing).
  { id: "hn", type: "hn", domain: "ai_engineering", weight: 0.7, url: "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=50", stable: true, name: "Hacker News" },

  // ---- Golf (0.45) ----
  { id: "bbc-golf", type: "rss", domain: "golf", weight: 0.45, url: "https://feeds.bbci.co.uk/sport/golf/rss.xml", stable: true, name: "BBC Sport Golf" },

  // ---- LEGO (0.45) ----
  { id: "brickset", type: "rss", domain: "lego", weight: 0.45, url: "https://brickset.com/feed", name: "Brickset" },
  { id: "brothers-brick", type: "rss", domain: "lego", weight: 0.45, url: "https://www.brothers-brick.com/feed/", name: "Brothers Brick" },

  // ---- Books / Fantasy (0.5, NO SPOILERS) ----
  // brandonsanderson.com no longer exposes a public RSS feed (404 on first
  // ingest) — disabled so it isn't reported dead every run. Reactor + the
  // Cosmere/Sanderson named-entity floor surface his news from other feeds.
  { id: "brandon-sanderson", type: "rss", domain: "books", weight: 0.5, url: "https://www.brandonsanderson.com/feed/", name: "Brandon Sanderson", enabled: false },
  { id: "reactor", type: "rss", domain: "books", weight: 0.5, url: "https://reactormag.com/feed/", name: "Reactor" },

  // ---- Film / TV (0.4) ----
  // starwars.com/news/feed was retired (404); Star Wars News Net is the
  // working community-news replacement.
  { id: "starwars", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.starwarsnewsnet.com/feed", name: "Star Wars News Net" },
  { id: "whats-on-netflix", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.whats-on-netflix.com/feed/", name: "What's on Netflix" },

  // ---- Music / synthwave (0.3) ----
  { id: "newretrowave", type: "rss", domain: "music", weight: 0.3, url: "https://newretrowave.com/feed/", name: "NewRetroWave" },

  // ---- Fitness / Training (0.4, news/gear only) ----
  { id: "runners-world", type: "rss", domain: "fitness", weight: 0.4, url: "https://www.runnersworld.com/rss/all.xml/", name: "Runner's World" },

  // ---- UK Finance / Fintech (0.5) ----
  // Monzo's blog RSS was retired (404); Monevator is the standard UK
  // personal-finance feed and a better default anchor for the domain.
  { id: "monevator", type: "rss", domain: "finance", weight: 0.5, url: "https://monevator.com/feed/", name: "Monevator" },

  // ---- Travel / Theme Parks (0.4) ----
  // §8 says "validate a theme-park news feed". Blooloop is the conventional
  // industry feed; validated on first ingest, dropped if dead.
  { id: "blooloop", type: "rss", domain: "travel", weight: 0.4, url: "https://blooloop.com/feed/", name: "Blooloop" },

  // Home / Self-hosting (0.35) has no Phase-1 RSS in §8 (Reddit-only, P2). Left
  // empty until a starter feed is added in-app or Reddit lands.
];

// Bluesky handles are the reader's to add in-app. This empty stub documents the
// shape the config expects; ingest skips the type cleanly when the list is empty.
// { id, type: "bluesky", domain, weight, handle: "transferjourno.bsky.social", name }
export const STARTER_BLUESKY = [];

// Reddit subreddits (§8 P2). The community layer — where transfer rumours, game
// announcements, training texture and match quirks live before they reach a
// headline. Ingested read-only (top/day). Works now via public JSON; uses the
// OAuth Data API automatically when REDDIT_CLIENT_ID/SECRET are set as Worker
// secrets. `url` carries the subreddit so it's editable in Settings like any
// source. The drafted set from docs/reddit-data-api-application.md.
// Seeded DISABLED: the structure ships ready (and editable in Settings) but stays
// off until the reader turns it on. Enabling works immediately via public JSON
// (the "way around" the API lead time); when REDDIT_CLIENT_ID/SECRET are set it
// uses the approved OAuth Data API automatically. Off by default keeps the brief's
// independent value clean if Reddit rate-limits the Worker's egress IPs.
const RS = (sub, domain, weight) => ({
  id: `r-${sub.toLowerCase()}`, type: "reddit", domain, weight, enabled: false,
  url: `https://www.reddit.com/r/${sub}`, name: `r/${sub}`,
});
export const STARTER_REDDIT = [
  // Gaming
  RS("NintendoSwitch", "gaming", 0.85), RS("Games", "gaming", 0.85),
  RS("SteamDeck", "gaming", 0.85), RS("MonsterHunter", "gaming", 0.8),
  RS("paradoxplaza", "gaming", 0.8), RS("BaldursGate3", "gaming", 0.8),
  // Football
  RS("Juve", "football", 0.85), RS("seriea", "football", 0.8),
  RS("soccer", "football", 0.8), RS("FantasyPL", "football", 0.75),
  // Tech & devices
  RS("Android", "tech_devices", 0.72), RS("Xiaomi", "tech_devices", 0.72),
  RS("eink", "tech_devices", 0.7),
  // Books
  RS("Cosmere", "books", 0.55), RS("Fantasy", "books", 0.5), RS("Malazan", "books", 0.55),
  // Film / TV
  RS("StarWars", "film_tv", 0.45), RS("television", "film_tv", 0.4),
  // Music
  RS("outrun", "music", 0.35), RS("synthwave", "music", 0.3),
  // Fitness
  RS("running", "fitness", 0.45), RS("AdvancedRunning", "fitness", 0.45),
  RS("weightroom", "fitness", 0.45),
  // Finance
  RS("UKPersonalFinance", "finance", 0.55), RS("Monzo", "finance", 0.5), RS("fintech", "finance", 0.45),
  // Golf · LEGO · Travel · Home/Self-hosting
  RS("golf", "golf", 0.45), RS("lego", "lego", 0.5),
  RS("themeparks", "travel", 0.45), RS("wdw", "travel", 0.4),
  RS("selfhosted", "home_selfhosting", 0.4), RS("homeassistant", "home_selfhosting", 0.4),
];
