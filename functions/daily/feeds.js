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
// Reddit is served ONLY via the public per-subreddit `.rss` endpoints (see
// STARTER_REDDIT + ingest.js). The authenticated Data API is not available and is
// not an option, permanently. Bluesky handles are seeded below (STARTER_BLUESKY)
// and expanded in-app.

export const STARTER_FEEDS = [
  // ---- World (0.4) ----
  { id: "bbc-news", type: "rss", domain: "world", weight: 0.4, url: "https://feeds.bbci.co.uk/news/rss.xml", stable: true, name: "BBC News" },
  { id: "bbc-world", type: "rss", domain: "world", weight: 0.4, url: "https://feeds.bbci.co.uk/news/world/rss.xml", stable: true, name: "BBC World" },
  { id: "guardian-world", type: "rss", domain: "world", weight: 0.4, url: "https://www.theguardian.com/world/rss", name: "Guardian World" },
  { id: "aljazeera-all", type: "rss", domain: "world", weight: 0.4, url: "https://www.aljazeera.com/xml/rss/all.xml", stable: true, name: "Al Jazeera" },
  { id: "france24-en", type: "rss", domain: "world", weight: 0.4, url: "https://www.france24.com/en/rss", stable: true, name: "France 24 English" },
  { id: "ap-topnews", type: "rss", domain: "world", weight: 0.4, url: "https://feeds.apnews.com/rss/apf-topnews", name: "AP Top News" },
  { id: "reuters-world", type: "rss", domain: "world", weight: 0.4, url: "https://www.reutersagency.com/feed/?best-topics=world&post_type=best", name: "Reuters World" },
  { id: "dw-en", type: "rss", domain: "world", weight: 0.4, url: "https://rss.dw.com/rdf/rss-en-all", name: "DW English" },
  { id: "economist-intl", type: "rss", domain: "world", weight: 0.4, url: "https://www.economist.com/international/rss.xml", name: "Economist International" },

  // ---- Local — Northern Ireland (0.5) ----
  { id: "bbc-ni", type: "rss", domain: "local", weight: 0.5, url: "https://feeds.bbci.co.uk/news/northern_ireland/rss.xml", stable: true, name: "BBC News NI" },
  { id: "belfast-telegraph", type: "rss", domain: "local", weight: 0.5, url: "https://www.belfasttelegraph.co.uk/news/northern-ireland/rss/", name: "Belfast Telegraph NI" },
  { id: "irish-news", type: "rss", domain: "local", weight: 0.5, url: "https://www.irishnews.com/rss/", name: "Irish News" },
  { id: "news-letter", type: "rss", domain: "local", weight: 0.5, url: "https://www.newsletter.co.uk/rss", name: "News Letter" },
  { id: "rte-news", type: "rss", domain: "local", weight: 0.5, url: "https://www.rte.ie/feeds/rss/?index=/news/", stable: true, name: "RTÉ News" },
  { id: "thejournal", type: "rss", domain: "local", weight: 0.5, url: "https://www.thejournal.ie/feed/", stable: true, name: "TheJournal.ie" },

  // ---- Gaming (0.9) ----
  { id: "eurogamer", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.eurogamer.net/feed", name: "Eurogamer" },
  { id: "nintendo-life", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.nintendolife.com/feeds/latest", name: "Nintendo Life" },
  { id: "push-square", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.pushsquare.com/feeds/latest", name: "Push Square" },
  { id: "rps", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.rockpapershotgun.com/feed", name: "Rock Paper Shotgun" },
  { id: "nintendo-everything", type: "rss", domain: "gaming", weight: 0.9, url: "https://nintendoeverything.com/feed/", stable: true, name: "Nintendo Everything" },
  { id: "gonintendo", type: "rss", domain: "gaming", weight: 0.9, url: "https://gonintendo.com/feeds/all.xml", stable: true, name: "GoNintendo" },
  { id: "nintendo-wire", type: "rss", domain: "gaming", weight: 0.9, url: "https://nintendowire.com/feed/", stable: true, name: "Nintendo Wire" },
  { id: "ign-games", type: "rss", domain: "gaming", weight: 0.9, url: "https://feeds.feedburner.com/ign/games-all", stable: true, name: "IGN Games" },
  { id: "pc-gamer", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.pcgamer.com/rss/", stable: true, name: "PC Gamer" },
  { id: "kotaku", type: "rss", domain: "gaming", weight: 0.9, url: "https://kotaku.com/rss", stable: true, name: "Kotaku" },
  { id: "gamespot-news", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.gamespot.com/feeds/game-news/", name: "GameSpot News" },
  { id: "polygon", type: "rss", domain: "gaming", weight: 0.9, url: "https://www.polygon.com/rss/index.xml", name: "Polygon" },
  { id: "playstation-blog", type: "rss", domain: "gaming", weight: 0.9, url: "https://blog.playstation.com/feed/", stable: true, name: "PlayStation.Blog" },

  // ---- Football (0.85) — core; Juventus / Serie A prioritised ----
  { id: "bbc-football", type: "rss", domain: "football", weight: 0.85, url: "https://feeds.bbci.co.uk/sport/football/rss.xml", stable: true, name: "BBC Sport Football" },
  { id: "guardian-football", type: "rss", domain: "football", weight: 0.85, url: "https://www.theguardian.com/football/rss", name: "Guardian Football" },
  { id: "football-italia", type: "rss", domain: "football", weight: 0.85, url: "https://football-italia.net/feed/", name: "Football Italia" },
  { id: "juvefc", type: "rss", domain: "football", weight: 0.85, url: "https://www.juvefc.com/feed/", stable: true, name: "Juvefc.com" },
  { id: "gifn", type: "rss", domain: "football", weight: 0.85, url: "https://www.getfootballnewsitaly.com/feed/", name: "Get Italian Football News" },
  { id: "bwrao", type: "rss", domain: "football", weight: 0.85, url: "https://www.blackwhitereadallover.com/rss/index.xml", name: "Black & White & Read All Over" },
  { id: "forza-italian", type: "rss", domain: "football", weight: 0.85, url: "https://forzaitalianfootball.com/feed/", name: "Forza Italian Football" },
  { id: "sempremilan", type: "rss", domain: "football", weight: 0.85, url: "https://sempremilan.com/feed", stable: true, name: "SempreMilan" },
  { id: "guardian-football-weekly", type: "rss", domain: "football", weight: 0.85, url: "https://www.theguardian.com/football/series/footballweekly/podcast.xml", name: "Guardian Football Weekly" },

  // ---- Tech & Devices (0.75) ----
  { id: "9to5google", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://9to5google.com/feed/", name: "9to5Google" },
  { id: "android-authority", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://www.androidauthority.com/feed/", name: "Android Authority" },
  { id: "the-verge", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://www.theverge.com/rss/index.xml", name: "The Verge" },
  { id: "android-police", type: "rss", domain: "tech_devices", weight: 0.75, url: "https://www.androidpolice.com/feed/", stable: true, name: "Android Police" },
  { id: "good-ereader", type: "rss", domain: "tech_devices", weight: 0.72, url: "https://goodereader.com/blog/feed", stable: true, name: "Good e-Reader" },

  // ---- Tech/AI & Engineering (0.7) ----
  { id: "cloudflare-blog", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://blog.cloudflare.com/rss/", stable: true, name: "Cloudflare Blog" },
  { id: "svpg", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://www.svpg.com/articles/feed/", name: "SVPG" },
  { id: "simon-willison", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://simonwillison.net/atom/everything/", stable: true, name: "Simon Willison's Weblog" },
  { id: "import-ai", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://jack-clark.net/feed/", stable: true, name: "Import AI" },
  { id: "openai-news", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://openai.com/blog/rss.xml", stable: true, name: "OpenAI News" },
  { id: "anthropic-news", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://www.anthropic.com/rss.xml", name: "Anthropic News" },
  { id: "ars-technica", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://arstechnica.com/feed/", name: "Ars Technica" },
  { id: "the-batch", type: "rss", domain: "ai_engineering", weight: 0.7, url: "https://www.deeplearning.ai/the-batch/feed/", name: "The Batch (DeepLearning.AI)" },

  // Hacker News (auto) — serves both gaming-adjacent and AI/engineering; tagged
  // ai_engineering, re-domained per item at ingest by keyword if it clearly fits
  // another domain. Fetched via the Algolia front-page API (JSON, no parsing).
  { id: "hn", type: "hn", domain: "ai_engineering", weight: 0.7, url: "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=50", stable: true, name: "Hacker News" },

  // ---- Golf (0.45) ----
  { id: "bbc-golf", type: "rss", domain: "golf", weight: 0.45, url: "https://feeds.bbci.co.uk/sport/golf/rss.xml", stable: true, name: "BBC Sport Golf" },
  { id: "golf-com", type: "rss", domain: "golf", weight: 0.45, url: "https://golf.com/feed/", stable: true, name: "Golf.com" },
  { id: "no-laying-up", type: "rss", domain: "golf", weight: 0.45, url: "https://nolayingup.com/blog?format=rss", name: "No Laying Up" },
  { id: "bunkered", type: "rss", domain: "golf", weight: 0.45, url: "https://www.bunkered.co.uk/feed", name: "bunkered" },
  { id: "golf-digest", type: "rss", domain: "golf", weight: 0.45, url: "https://www.golfdigest.com/feed/rss", name: "Golf Digest" },

  // ---- LEGO (0.45) ----
  { id: "brickset", type: "rss", domain: "lego", weight: 0.45, url: "https://brickset.com/feed", name: "Brickset" },
  { id: "brothers-brick", type: "rss", domain: "lego", weight: 0.45, url: "https://www.brothers-brick.com/feed/", name: "Brothers Brick" },
  { id: "jays-brick-blog", type: "rss", domain: "lego", weight: 0.45, url: "https://jaysbrickblog.com/feed/", stable: true, name: "Jay's Brick Blog" },
  { id: "new-elementary", type: "rss", domain: "lego", weight: 0.45, url: "https://www.newelementary.com/feeds/posts/default?alt=rss", name: "New Elementary" },
  { id: "the-brick-fan", type: "rss", domain: "lego", weight: 0.45, url: "https://www.thebrickfan.com/feed/", name: "The Brick Fan" },

  // ---- Books / Fantasy (0.5, NO SPOILERS) ----
  // brandonsanderson.com no longer exposes a public RSS feed (404 on first
  // ingest) — disabled so it isn't reported dead every run. Reactor + 17th Shard +
  // the Cosmere/Sanderson named-entity floor surface his news from other feeds.
  { id: "brandon-sanderson", type: "rss", domain: "books", weight: 0.5, url: "https://www.brandonsanderson.com/feed/", name: "Brandon Sanderson", enabled: false },
  { id: "reactor", type: "rss", domain: "books", weight: 0.5, url: "https://reactormag.com/feed/", name: "Reactor" },
  { id: "17th-shard", type: "rss", domain: "books", weight: 0.55, url: "https://www.17thshard.com/forum/discover/6.xml/", name: "17th Shard" },
  { id: "locus", type: "rss", domain: "books", weight: 0.5, url: "https://locusmag.com/feed/", name: "Locus Magazine" },
  { id: "grimdark", type: "rss", domain: "books", weight: 0.5, url: "https://www.grimdarkmagazine.com/feed/", name: "Grimdark Magazine" },

  // ---- Film / TV (0.4) ----
  // starwars.com/news/feed was retired (404); Star Wars News Net is the
  // working community-news replacement. The official feed is re-added below and
  // validated on ingest — dropped gracefully if it's still dead.
  { id: "starwars", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.starwarsnewsnet.com/feed", name: "Star Wars News Net" },
  { id: "whats-on-netflix", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.whats-on-netflix.com/feed/", name: "What's on Netflix" },
  { id: "slashfilm", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.slashfilm.com/feed/", stable: true, name: "/Film" },
  { id: "screenrant", type: "rss", domain: "film_tv", weight: 0.4, url: "https://screenrant.com/feed/", stable: true, name: "ScreenRant" },
  { id: "collider", type: "rss", domain: "film_tv", weight: 0.4, url: "https://collider.com/feed/", stable: true, name: "Collider" },
  { id: "starwars-official", type: "rss", domain: "film_tv", weight: 0.4, url: "https://www.starwars.com/news/feed", name: "StarWars.com" },

  // ---- History (0.35) ----
  { id: "historyextra", type: "rss", domain: "history", weight: 0.35, url: "https://www.historyextra.com/feed/", name: "HistoryExtra" },
  { id: "rest-is-history", type: "rss", domain: "history", weight: 0.35, url: "https://feeds.megaphone.fm/GLT4787413333", stable: true, name: "The Rest Is History" },
  { id: "history-today", type: "rss", domain: "history", weight: 0.35, url: "https://www.historytoday.com/feed/rss.xml", name: "History Today" },
  { id: "fall-of-civilizations", type: "rss", domain: "history", weight: 0.35, url: "https://feeds.buzzsprout.com/975519.rss", name: "Fall of Civilizations" },

  // ---- Music / synthwave (0.3) ----
  { id: "newretrowave", type: "rss", domain: "music", weight: 0.3, url: "https://newretrowave.com/feed/", name: "NewRetroWave" },
  { id: "fixt-neon", type: "rss", domain: "music", weight: 0.3, url: "https://www.fixtstore.com/blogs/news.atom", name: "FiXT Neon" },
  { id: "iron-skullet", type: "rss", domain: "music", weight: 0.3, url: "https://www.ironskullet.com/feeds/posts/default?alt=rss", name: "Iron Skullet" },

  // ---- Fitness / Training (0.4, news/gear/method) ----
  { id: "runners-world", type: "rss", domain: "fitness", weight: 0.4, url: "https://www.runnersworld.com/rss/all.xml/", name: "Runner's World" },
  { id: "dc-rainmaker", type: "rss", domain: "fitness", weight: 0.4, url: "https://www.dcrainmaker.com/feed", stable: true, name: "DC Rainmaker" },
  { id: "marathon-handbook", type: "rss", domain: "fitness", weight: 0.4, url: "https://marathonhandbook.com/feed/", stable: true, name: "Marathon Handbook" },
  { id: "stronger-by-science", type: "rss", domain: "fitness", weight: 0.4, url: "https://www.strongerbyscience.com/feed/", name: "Stronger by Science" },
  { id: "irunfar", type: "rss", domain: "fitness", weight: 0.4, url: "https://www.irunfar.com/feed", name: "iRunFar" },

  // ---- UK Finance / Fintech (0.5) ----
  // Monzo's blog RSS was retired (404); Monevator is the standard UK
  // personal-finance feed and a better default anchor for the domain.
  { id: "monevator", type: "rss", domain: "finance", weight: 0.5, url: "https://monevator.com/feed/", name: "Monevator" },
  { id: "sifted", type: "rss", domain: "finance", weight: 0.5, url: "https://sifted.eu/feed", stable: true, name: "Sifted" },
  { id: "finextra", type: "rss", domain: "finance", weight: 0.5, url: "https://www.finextra.com/rss/headlines.aspx", stable: true, name: "Finextra Headlines" },
  { id: "moneysavingexpert", type: "rss", domain: "finance", weight: 0.5, url: "https://www.moneysavingexpert.com/news/feed/", name: "MoneySavingExpert News" },
  { id: "be-clever-cash", type: "rss", domain: "finance", weight: 0.5, url: "https://becleverwithyourcash.com/feed/", name: "Be Clever With Your Cash" },
  { id: "pensioncraft", type: "rss", domain: "finance", weight: 0.5, url: "https://pensioncraft.com/feed/", name: "PensionCraft" },

  // ---- Travel / Theme Parks (0.4) ----
  { id: "blooloop", type: "rss", domain: "travel", weight: 0.4, url: "https://blooloop.com/feed/", name: "Blooloop" },
  { id: "theme-park-insider", type: "rss", domain: "travel", weight: 0.4, url: "https://www.themeparkinsider.com/rss.cfm", name: "Theme Park Insider" },
  { id: "looopings", type: "rss", domain: "travel", weight: 0.4, url: "https://www.looopings.nl/feed/", name: "Looopings" },
  { id: "coaster101", type: "rss", domain: "travel", weight: 0.4, url: "https://www.coaster101.com/feed/", name: "Coaster101" },
];

// Bluesky — the reader-facing social layer, seeded with the verified handles from
// the source review (Part C C4) and expanded in-app. Ingest validates each handle
// against the public XRPC API and drops any that don't resolve.
// Shape: { id, type: "bluesky", domain, weight, handle: "name.bsky.social", name }
export const STARTER_BLUESKY = [
  { id: "bsky-fabrizioromano", type: "bluesky", domain: "football", weight: 0.85, handle: "fabriziorom.bsky.social", name: "Fabrizio Romano" },
  { id: "bsky-wario64", type: "bluesky", domain: "gaming", weight: 0.9, handle: "wario64.bsky.social", name: "Wario64" },
  { id: "bsky-reactor", type: "bluesky", domain: "books", weight: 0.5, handle: "reactorsff.bsky.social", name: "Reactor (SFF)" },
  { id: "bsky-simonwillison", type: "bluesky", domain: "ai_engineering", weight: 0.7, handle: "simonwillison.net", name: "Simon Willison" },
];

// Reddit — the community layer (transfer rumours, announcements, training
// texture, match quirks). Each subreddit is its own source with a SIZE `tier`
// (big | medium | small), set per-row in Settings. Slots scale with size: big
// subs are polled individually and kept deep; medium and small subs compete in
// their own peer POOLS (one combined `.rss` each) so a small sub only earns a slot
// when it beats other small subs (see ingest.js). Reddit is public hot `.rss` ONLY
// — the Data API / OAuth is not available and is not an option, permanently, and
// the size-tiered rotation (pipeline.js) that keeps polls under Reddit's per-IP
// rate limit is a permanent part of the design. Add new subs sparingly and as
// `tier:small`. Defaults below are a starting point — re-tier any sub in Settings.
const RS = (sub, domain, weight, tier) => ({
  id: `r-${sub.toLowerCase()}`, type: "reddit", domain, weight, tier,
  url: `https://www.reddit.com/r/${sub}`, name: `r/${sub}`,
});
export const STARTER_REDDIT = [
  // BIG — own poll, kept deep
  RS("soccer", "football", 0.85, "big"), RS("Games", "gaming", 0.85, "big"),
  RS("NintendoSwitch", "gaming", 0.85, "big"), RS("Android", "tech_devices", 0.72, "big"),
  RS("StarWars", "film_tv", 0.45, "big"),
  // MEDIUM — medium pool
  RS("seriea", "football", 0.85, "medium"), RS("SteamDeck", "gaming", 0.85, "medium"),
  RS("Fantasy", "books", 0.55, "medium"), RS("television", "film_tv", 0.45, "medium"),
  RS("running", "fitness", 0.45, "medium"), RS("UKPersonalFinance", "finance", 0.55, "medium"),
  RS("Xiaomi", "tech_devices", 0.72, "medium"), RS("golf", "golf", 0.45, "medium"),
  RS("lego", "lego", 0.5, "medium"), RS("Cosmere", "books", 0.55, "medium"),
  // SMALL — small pool
  RS("Juve", "football", 0.85, "small"), RS("FantasyPL", "football", 0.75, "small"),
  RS("MonsterHunter", "gaming", 0.8, "small"), RS("paradoxplaza", "gaming", 0.8, "small"),
  RS("BaldursGate3", "gaming", 0.8, "small"), RS("eink", "tech_devices", 0.7, "small"),
  RS("Malazan", "books", 0.55, "small"), RS("outrun", "music", 0.35, "small"),
  RS("synthwave", "music", 0.3, "small"), RS("AdvancedRunning", "fitness", 0.45, "small"),
  RS("weightroom", "fitness", 0.45, "small"), RS("Monzo", "finance", 0.5, "small"),
  RS("fintech", "finance", 0.45, "small"), RS("themeparks", "travel", 0.45, "small"),
  RS("wdw", "travel", 0.4, "small"), RS("history", "history", 0.4, "small"),
  RS("AskHistorians", "history", 0.4, "small"), RS("podcasts", "podcasts", 0.35, "small"),
  RS("northernireland", "local", 0.5, "small"),
  // SMALL — new thin-domain fills (added sparingly as tier:small per §Sources)
  RS("belfast", "local", 0.5, "small"), RS("patientgamers", "gaming", 0.8, "small"),
  RS("Stormlight_Archive", "books", 0.55, "small"), RS("printSF", "books", 0.5, "small"),
  RS("trailrunning", "fitness", 0.45, "small"), RS("kettlebell", "fitness", 0.45, "small"),
  RS("kobo", "tech_devices", 0.7, "small"), RS("UKInvesting", "finance", 0.5, "small"),
  RS("Efteling", "travel", 0.4, "small"),
];
