// The Signal — daily: the interest profile (§7).
//
// BUILT from The Signal's editorial spec (`.claude/skills/the-signal/references/
// editorial-spec.md`, `references/sections.md`, `references/spec/*.md`) — not a
// hand-written list. It deliberately errs broad: the daily's job includes
// "things that *might* interest him", so adjacent/peripheral topics are captured
// with low weights. Over-inclusion is cheap (prunable in-app); under-inclusion is
// the failure mode.
//
// This is the DEFAULT seeded into DAILY_CONFIG on first run. After that it is
// edited in-app and read live — never here. The reader is expected to review and
// tune it (per §12).
//
// Shape: { named_entity_floor[], topic_weights{}, special_handling{}, mutes[] }
//
//  - named_entity_floor: tight (~6–10), the genuine emphasised core. Items
//    touching these bypass ranking and never sit below the fold (§4).
//  - topic_weights: broad. domain -> { weight, keywords[] }. The mechanical
//    scorer (Tier 1) matches item titles against keywords, weighted.
//  - special_handling: per-domain suppression (books/film spoilers, fitness
//    diet-targeting, finance speculation, UK-politics-out-by-default).
//  - mutes: global drop patterns (flair/topic/category).

export const PROFILE = {
  // ---- Named-entity floor (the genuine core; bypasses ranking) ----
  // Kept tight per §7.5. Obvious anchors (Juventus, Switch 2, Steam Deck, the
  // reader's current phone = Xiaomi 17 Ultra, his primary book series = the
  // Cosmere) plus the two most-emphasised franchises in the spec (Star Wars,
  // Malazan) and the recurring trip anchor (Efteling).
  named_entity_floor: [
    { id: "juventus", label: "Juventus", patterns: ["juventus", "juve", "bianconeri"] },
    { id: "switch2", label: "Nintendo Switch 2", patterns: ["switch 2", "switch2", "nintendo switch 2"] },
    { id: "steam-deck", label: "Steam Deck", patterns: ["steam deck", "steamdeck", "steam machine"] },
    { id: "xiaomi-17-ultra", label: "Xiaomi 17 Ultra", patterns: ["xiaomi 17 ultra", "xiaomi 17", "17 ultra"] },
    { id: "cosmere", label: "Cosmere / Sanderson", patterns: ["cosmere", "brandon sanderson", "stormlight", "mistborn"] },
    { id: "malazan", label: "Malazan", patterns: ["malazan", "steven erikson", "book of the fallen"] },
    { id: "star-wars", label: "Star Wars", patterns: ["star wars", "mandalorian", "ahsoka", "andor", "skeleton crew"] },
    { id: "efteling", label: "Efteling", patterns: ["efteling", "beekse bergen"] },
  ],

  // ---- Topic weights (broad; mechanical scorer matches keywords) ----
  // Weights track prominence in the spec. Keys MUST match feed `domain` tags
  // (feeds.js) so feed-coverage stays in sync (§7.7).
  topic_weights: {
    // CENTRAL domains (high weight)
    gaming: {
      weight: 0.9,
      keywords: [
        "nintendo", "switch", "playstation", "ps5", "xbox", "steam", "valve",
        "geforce now", "monster hunter", "baldur's gate", "zelda", "mario",
        "metroid", "pokemon", "final fantasy", "paradox", "indie game", "rpg",
        "roguelike", "co-op", "soulslike", "game pass", "eshop", "demo", "review",
        "trailer", "gameplay", "speedrun", "remaster", "remake", "expansion", "dlc",
      ],
    },
    football: {
      weight: 0.85,
      keywords: [
        "football", "juventus", "juve", "bianconeri", "serie a", "premier league",
        "champions league", "europa league", "transfer", "signing", "loan",
        "fixture", "scudetto", "inter", "milan", "napoli", "roma", "lazio",
        "atalanta", "fiorentina", "arsenal", "manchester", "liverpool", "chelsea",
        "tottenham", "world cup", "euros", "qualifier", "penalty", "manager",
        "sacked", "lineup", "squad", "matchday", "fantasy pl", "fpl",
      ],
    },
    fitness: {
      weight: 0.4,
      keywords: [
        "strength training", "hypertrophy", "kettlebell", "strongfirst", "dan john",
        "running", "10k", "marathon", "zone 2", "lactate threshold", "vo2",
        "concurrent training", "gymnastics rings", "landmine", "mobility",
        "recovery", "garmin", "hrv", "body battery", "training readiness",
        "programming", "rpe", "progressive overload", "home gym", "barbell",
        "squat rack", "stronger by science", "examine", "nuckols", "galpin",
        "ibex", "pliability",
      ],
    },
    world: {
      weight: 0.4,
      keywords: [
        "war", "ceasefire", "election", "geopolitics", "sanctions", "treaty",
        "nato", "un ", "summit", "conflict", "diplomacy", "outbreak", "earthquake",
        "wildfire", "flood", "breakthrough", "iran", "ukraine", "china", "russia",
        "gaza", "israel", "eu ", "tariff", "trade deal", "protest", "coup",
      ],
    },
    // SECONDARY domains
    tech_devices: {
      weight: 0.75,
      keywords: [
        "pixel", "xiaomi", "android", "google", "samsung", "oneplus",
        "e-reader", "kindle", "kobo", "boox", "tablet", "wearable", "smartwatch",
        "whoop", "oura", "fitbit", "earbuds", "foldable", "chipset", "snapdragon",
        "tensor", "battery life", "update", "rollout", "leak", "hands-on",
      ],
    },
    ai_engineering: {
      weight: 0.7,
      keywords: [
        "ai ", "artificial intelligence", "llm", "chatgpt", "openai", "claude",
        "anthropic", "gemini", "perplexity", "copilot", "on-device", "model",
        "agent", "assistant", "image generation", "cloudflare", "workers", "edge",
        "open source", "self-host", "api", "productivity app", "todoist", "notion",
        "obsidian", "automation",
      ],
    },
    finance: {
      weight: 0.5,
      keywords: [
        "monzo", "revolut", "starling", "isa", "pension", "savings", "vanguard",
        "trading 212", "interest rate", "cashback", "current account",
        "fintech", "open banking", "etsy", "passive income", "side hustle",
        "print on demand", "kindle scribe", "template", "marketplace",
      ],
    },
    books: {
      weight: 0.5,
      keywords: [
        "fantasy", "sci-fi", "science fiction", "epic fantasy", "novel",
        "release date", "preorder", "publishing", "author", "sequel", "trilogy",
        "reactor", "tor", "wheel of time", "dungeon crawler", "litrpg",
        "audiobook", "narrator", "cover reveal", "book deal", "anniversary edition",
      ],
    },
    golf: {
      weight: 0.45,
      keywords: [
        "golf", "pga", "dp world tour", "liv golf", "ryder cup", "the open",
        "us open", "masters", "augusta", "rory mcilroy", "scottie scheffler",
        "leaderboard", "tee time", "major",
      ],
    },
    lego: {
      weight: 0.45,
      keywords: [
        "lego", "brickset", "minifigure", "set reveal", "retiring", "ucs",
        "icons", "technic", "modular", "brick", "ideas set", "gwp",
      ],
    },
    film_tv: {
      weight: 0.4,
      keywords: [
        "netflix", "disney+", "disney plus", "apple tv", "hbo", "max ",
        "prime video", "trailer", "season", "renewed", "cancelled", "premiere",
        "box office", "marvel", "dc ", "streaming", "series finale", "casting",
        "director", "synthwave", "retrowave",
      ],
    },
    travel: {
      weight: 0.4,
      keywords: [
        "theme park", "disney parks", "disneyland", "disney world", "efteling",
        "rollercoaster", "ride", "new attraction", "annual pass", "family trip",
        "flight deal", "europe", "netherlands", "expansion", "opening", "resort",
      ],
    },
    music: {
      weight: 0.3,
      keywords: [
        "synthwave", "retrowave", "outrun", "darksynth", "newretrowave", "fixt",
        "lakeshore", "soundtrack", "score", "vinyl", "reissue", "album", "single",
        "ep ", "label", "bandcamp",
      ],
    },
    history: {
      weight: 0.35,
      keywords: [
        "ancient", "roman", "medieval", "archaeology", "excavation", "artefact",
        "empire", "dynasty", "manuscript", "anniversary", "historian",
        "pre-history", "classical", "byzantine", "renaissance",
      ],
    },
    podcasts: {
      weight: 0.3,
      keywords: [
        "podcast", "audio drama", "episode", "football weekly", "the bunker",
        "history of rome", "revolutions", "audible", "bbc sounds", "pocket casts",
      ],
    },
    home_selfhosting: {
      weight: 0.35,
      keywords: [
        "self-host", "selfhosted", "home assistant", "homelab", "raspberry pi",
        "nas", "docker", "home automation", "smart home",
      ],
    },
  },

  // ---- Special handling (§7.6) ----
  special_handling: {
    books: {
      // Release / news / author-updates only; suppress plot / leaks / spoilers.
      suppress_patterns: [
        "spoiler", "ending explained", "who dies", "death of", "plot twist",
        "theory", "leak", "leaked chapter", "recap", "ending of", "fate of",
      ],
      note: "No spoilers ever. Release/news/author-updates only.",
    },
    film_tv: {
      suppress_patterns: [
        "ending explained", "spoiler", "who dies", "post-credit", "recap",
        "every easter egg", "death of", "plot twist explained",
      ],
      note: "No spoilers in surfaced lines.",
    },
    fitness: {
      // News / gear / method only; no diet/calorie/body-composition targeting.
      suppress_patterns: [
        "lose belly", "lose weight fast", "calorie", "diet plan", "drop ",
        "shred", "six-pack", "summer body", "fat loss", "skinny",
        "before and after", "transformation",
      ],
      note: "News/gear/method only. No diet/calorie/body-composition targeting.",
    },
    finance: {
      suppress_patterns: [
        "crypto", "bitcoin", "ethereum", "get rich", "day trading", "forex",
        "mlm", "guaranteed returns", "to the moon", "meme stock",
      ],
      note: "Sensible long-term/consumer angle only; no speculation.",
    },
    world: {
      // UK / national politics out by default — only a genuine landscape shift.
      demote_patterns: [
        "reshuffle", "leadership challenge", "cabinet", "poll", "by-election",
        "pmqs", "backbench", "stormont", "westminster", "labour mps", "tory mps",
      ],
      note: "UK/national process politics out by default; demote heavily.",
    },
  },

  // ---- Global mutes (§5/§7) ----
  mutes: [
    "sponsored", "advertisement", "deal of the day", "discount code",
    "horoscope", "celebrity gossip", "royal family", "kardashian",
    "tiktok trend", "gone viral", "you won't believe", "win a ",
  ],
};
