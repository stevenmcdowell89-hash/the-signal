# Spec slice — triggers

_This file consolidates the triggers/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## priority-1-calendar

- **Research depth matters.** This format lives or dies on completeness. Source from: official park/resort websites and menus (source-of-truth for what exists today, prices, opening hours), TripAdvisor and Google reviews, travel blogs (DFBguide, TravelMamas, park-specific forums, family-travel and solo-travel blogs), Reddit (r/Efteling, r/themeparks, r/foodtravel, destination-specific subs), YouTube food tours and vlogs, Instagram and TikTok location tags, food-blogger Substacks, and any Dutch/regional-language sources where relevant. Cross-reference at least three source types per major venue to catch seasonal menus, recently closed spots, new openings, and the gap between marketing copy and what diners actually report. **Imagery follows the same diversity rule:** traveller photos from blogs, Reddit photo threads, well-credited Flickr/Instagram posts, and food-tour video stills are all in scope alongside official press shots — quality and credit are the bar, not source pedigree. **The photo carries the sensory load that the prose does not** — see the Factual write-up rule. A specific, well-credited shot of the actual dish on the actual plate does work the writing must not attempt.
- **Audience callouts — stated as venue character, never as reader instruction.** A sidebar or icon system can flag places by their general character: "family-friendly", "adult-oriented evening spot", "buggy-friendly", "late-night", "walk-in welcome", "booking essential". These are facts about the venue, not directions to the reader. Banned: "perfect for your son", "your 10-year-old will love", "great for the kids" — the reader's family composition is invisible per Gate 1A. The reader can apply venue character to their own circumstances; the magazine never does it for them.
- **Tone is conversational, not instructional.** Phrases like "worth building an evening around", "the pick when you want something quiet after a loud day", "the kind of place that rewards a long lunch" frame venues by their general character without addressing the reader directly. Banned: "one for each of you", "you and your partner", "take the kids", "if you've been waiting for…" — these all violate Gate 1A. Write as if any reader of the magazine might be heading to this trip; the warmth comes from venue-level specificity, not from second-person address.
- **Images do heavy lifting.** Food photography isn't supporting content — it's the reason to turn the page. Every Unmissable gets a strong image. Major meal-slot sections get at least one. Lean toward bigger images, less whitespace, more visual momentum. The reader is scrolling on a tablet with coffee — make it a pleasure to look at.
- Use `.also-cards` for option grids, `.compare-panel` for head-to-head comparisons (e.g. two similar restaurants), `.stat-bar` for price ranges, `.sidebar` for tips ("book 2 weeks ahead" / "queue is shortest at 11:30"), `.big-number` for standout stats, `.dyk` for food trivia, `.tier-hot`/`.tier-warm`/`.tier-note` for ranking tiers.
- Use 10-14 component types. Images are critical — food photography sells the recommendations.
- Best for: theme park food guides, city eating guides, resort dining guides — any trip where finding the right places to eat is a meaningful part of the experience.

All special editions use the same design system and component library. Use sidebars, stat bars, DYK boxes, card stacks, collapsible sections generously — a special edition with no visual furniture is a wall of prose.

---

## Auto-Triggered Specials



---

## priority-2-event

The workflow's **scout step** (step 2 in SKILL.md) evaluates these triggers with 2-4 quick searches **before** committing to any full research pass. This prevents wasting research on a standard weekly that gets discarded. The reader never requests these — they appear as a surprise, like a magazine supplement. **All formats remain manually triggerable at any time** in addition to their auto-triggers.

### The "Meanwhile..." Section

When a special edition replaces the standard weekly, it must include a **"Meanwhile..."** section before the Footer. This ensures the reader never misses a week of news.

- 12-18 bullet points covering the week's biggest stories across all fixed-section areas: world news, tech/gaming, sport (results, tables, key stories), entertainment, and any breaking news.
- **Every item must include a linked source** so the reader can go deeper on anything that matters to them.
- Format: bold headline + one sentence + linked source. Compact, scannable.
- Use `.also-list` with `.tier-hot` / `.tier-warm` / `.tier-note` tiers to signal importance.
- This is a catch-up safety net, not a section to linger in. Keep it tight.

### Auto-Trigger Logic



---

## priority-3-safety

Evaluate during the **scout step** (before full research). Priority order — highest wins. Only one special per week.

**Priority 1 — Calendar-Fixed Triggers (predictable, always fire)**

| Trigger | Format | When |
|---|---|---|
| Half-year mark | Rewind — "H1 in Review" | Last Sunday of June (defer if within 7 days of a trip — see trip-aware rules) |
| Year-end | Rewind — "The Year in Review" | Last Sunday of December |
| **Trip food guide (food-focused, always)** | **Field Guide** | ~6 weeks before an `upcoming_trips` entry with food-research value. **MANDATORY:** read § The Field Guide in full before any planning or writing — see the 14 headline rules at the top of that section. |
| Trip approaching | Countdown | 2-3 weeks before an `upcoming_trips` entry in state file |

**Priority 2 — Event-Driven Triggers (detected during research)**

| Trigger | Format | Detection |
|---|---|---|
| Serie A season concluded | Season Review — Serie A | Research finds final matchday results |


---

## guardrails

| **Trip food guide (food-focused, always)** | **Field Guide** | ~6 weeks before an `upcoming_trips` entry with food-research value. **MANDATORY:** read § The Field Guide in full before any planning or writing — see the 14 headline rules at the top of that section. |
| Trip approaching | Countdown | 2-3 weeks before an `upcoming_trips` entry in state file |

**Priority 2 — Event-Driven Triggers (detected during research)**

| Trigger | Format | Detection |
|---|---|---|
| Serie A season concluded | Season Review — Serie A | Research finds final matchday results |
| Premier League season concluded | Season Review — Premier League | Research finds final matchday results |
| Major tournament concluded | Season Review — [Tournament] | Research finds final/closing ceremony |
| A major product launch this week | Deep Dive or Versus | Research finds a significant launch in a core interest (Switch 2, major game, new console, etc.) |
| Two competing products launched/announced close together | Versus | Research finds a natural head-to-head |

**Priority 3 — Editorial Picks (the safety net against dry spells)**

If no Priority 1 or 2 trigger has fired in the last 5 weeks, the editor picks a special from the pool below. These are evergreen — they don't depend on external events:

| Format | Example Topics |
|---|---|---|


---

## search-checklist

## Search Checklist

Run the **core groups** every issue. Run **rotating groups** only when that section is selected for the issue.

### Core Groups (every issue)

**Group 1 — News & Geopolitics:** dominant running story, world news, UK / national politics, NI news briefly. Within this group, the scout phase MUST explicitly check for: (a) any UK / Irish / Scottish / Welsh / European elections held in the past 7 days (general, devolved, council aggregate); (b) live PM or opposition-leader leadership challenges (MPs calling for resignation, named challengers emerging, union pressure); (c) Cabinet-level resignations or sackings; (d) major government policy events (Budget, headline legal rulings, immigration policy changes). If any of (a)-(d) fired in the last 7 days, that story is automatically a candidate for Lead 1 unless an even bigger world story crowds it out. See the UK / national politics rule in this spec for the full Lead-grade vs parish-pump test.

**Group 2 — Tech & Gaming:** Nintendo Switch 2, Steam Deck, GeForce Now, consumer AI tools, Pixel/Xiaomi/e-readers, LEGO news and releases, gaming news and releases

**Group 3 — Football & Sport:** First, check: are World Cup qualifiers, Euro qualifiers, World Cup finals, Euros, CL/EL knockout stages, or other major tournaments active this week? If yes, search for those first — they lead the section. Then search domestic (Juventus + Serie A, Premier League) only for significant news. If no tournament is active, search Serie A + Juventus, Premier League, CL/EL (in season), golf majors/Ryder Cup (when in season).

**Group 4 — Culture & Entertainment:** new movies and TV releases, Star Wars news, synthwave/retrowave/electronic music

**Group 5 — Fitness (for The Session):** running articles (race prep, 10k training, zone 2), gym/strength training (concurrent training, body recomposition, structured programming), kettlebell/StrongFirst/Dan John, mobility and recovery science, wearable/Garmin training data interpretation, nutrition for cutting while training

**Group 6 — Features & Evergreen (rotate):** gaming retrospectives, Reddit notable threads (r/NintendoSwitch, r/Juve, r/fantasybooks, r/kettlebell, r/running, r/fitness, r/StarWars, r/lego, r/Garmin), great long-reads from any era

**Images:** source via image search for every major section.

### Rotating Groups

Search groups for rotating sections are in `references/sections.md`. Only search the groups for sections appearing in this issue.

---


