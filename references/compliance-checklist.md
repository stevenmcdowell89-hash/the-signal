# The Signal — Compliance Checklist

Run through every item before delivering an issue. Fix any failures before sharing.

---

## Volume, Length, and Visual Richness

- [ ] The issue is at least 5,000 words (target 6,000–8,000+)
- [ ] The issue fills 20–30 rendered pages — the reader should have more content than they can read in 45 minutes
- [ ] Every major section has at least one relevant image (game art, match photo, film still, product shot, book cover)
- [ ] Section breaks are visually obvious — the reader knows which section they're in at a glance while scrolling on a tablet
- [ ] The overall design feels like a personal Sunday magazine, not a work newsletter

## Content Placement

- [ ] Every section has both feature pieces AND one-liner scan items (not just one or two items per section)
- [ ] Screen & Sound has a comprehensive Release Radar (15–20+ items across ALL categories: film, TV, games, LEGO, tech, books, music)
- [ ] The Release Radar covers all categories — not just film/TV
- [ ] The Touchline leads with tables and scores — reference data comes FIRST, then narrative
- [ ] The Touchline includes Champions League results when CL games were played that week
- [ ] The Touchline includes Serie A top 6 and PL top 6 league tables
- [ ] Serie A coverage extends beyond Juve — title race, relegation, notable stories across the league
- [ ] Golf majors or big sport stories appear in The Touchline when relevant
- [ ] LEGO product news appears in Pixel & Byte, not Screen & Sound (unless it's a LEGO film/show)
- [ ] This Week in History is present (it appears every week, no exceptions)
- [ ] History section prefers ancient/medieval/classical — not defaulting to modern/WW2
- [ ] Local NI "nice" stories are in "Also This Week" at most — never given prominent placement
- [ ] The Session contains only sourced content from real articles — no generic fitness advice
- [ ] Music is covered only when relevant — NOT treated as a mandatory fixed section
- [ ] Disney Parks/Efteling news appears in Screen & Sound when found
- [ ] No "Other Signals" section exists — all items distributed into relevant "Also" lists

## Foreword

- [ ] 50–80 words maximum
- [ ] Mentions no more than two topics — finds the one thread
- [ ] Does not use "meanwhile", "elsewhere", or "also this week"
- [ ] Does not restate the cover contents in prose form

## Coverage Gaps (most common failure mode)

- [ ] Star Wars is mentioned — search specifically every week
- [ ] Books content is present (new releases, recommendations, short fiction, or a feature)
- [ ] Fitness content is present — if no news, use an evergreen feature, or omit The Session entirely
- [ ] Podcasts the reader follows are cross-referenced (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions)
- [ ] Android/tablet/Pixel/Xiaomi/e-reader content is surfaced when relevant
- [ ] Switch 2, Steam Deck, GeForce Now news is covered when relevant
- [ ] Reddit was consulted as a source for at least some content
- [ ] The issue has a mix of news AND features/evergreen — not purely news
- [ ] More than one substantial world news story has depth (even when one story dominates)
- [ ] Screen & Sound has opinions — not just press release summaries
- [ ] Images are present and sourced — the reader was never expected to add them

## The Wildcard Rule

- [ ] The issue includes 2–3 items the reader didn't ask for — surprises, unexpected domains, discoveries
- [ ] 2 of 8 Long Shelf items are genuine wildcards outside the core interest profile
- [ ] The issue is NOT entirely predictable from the interest list
- [ ] "Taste is a lens, not a filter" — excellent things outside comfort zone are surfaced

## Magazine Voice, Not Personal Assistant

- [ ] No "what this means for you" framing anywhere in the issue
- [ ] No "your son will love this" or "perfect for a 10-year-old" sprinkled through prose — these belong ONLY in dedicated sidebars ("Family Picks", "For the Kids")
- [ ] Articles are not reframed around the reader's personal situation — write like a magazine journalist
- [ ] Personal context shapes what gets selected and how much space it gets — it does NOT narrate the prose
- [ ] The personalisation is in the selection, not the prose

## Did You Know Boxes

- [ ] 3–5 Did You Know boxes are scattered throughout the issue
- [ ] They are surprising and interesting — not forced or trivial
- [ ] DYK boxes adapt to their section — warm yellow on light backgrounds, turf-tinted on Touchline, neon-tinted on Screen & Sound, gold-tinted on The Shelf

## Content Quality

- [ ] Angle boxes are reserved for genuinely significant stories (geopolitics, major tech shifts) — not every story
- [ ] Story depth matches significance — mid-tier stories are quick takes or one-liners, not full articles
- [ ] Fitness section avoids generic advice ("stay hydrated", "warm up properly") — sourced from named publications only
- [ ] Football section gives narrative, not match reports — the reader already knows the scores
- [ ] Tech section explains what things mean for the user, not just what was announced
- [ ] Any "work exception" story would genuinely make the reader message a colleague on Monday
- [ ] The issue has opinions throughout — it's a personal magazine, not a corporate one
- [ ] Podcast cross-references link to actual episodes, not speculative mentions

## Navigation & Wayfinding

- [ ] Reading progress bar is present — thin gradient bar at the top of the viewport (JS-powered)
- [ ] Back-to-top button is present — floating button (bottom-right) appears after scrolling past the cover, links to navigator
- [ ] Navigator cards use anchor links (`href="#sectionId"`) with matching `id` attributes on each section
- [ ] Smooth scrolling is enabled globally (`scroll-behavior: smooth`)
- [ ] Top 1–2 navigator cards use `.nav-card.lead` (spanning two columns with optional thumbnail)
- [ ] Read time indicators (`.read-time`) are present on navigator cards where appropriate
- [ ] The JavaScript block from the template is included at the bottom of the issue for progress bar and back-to-top functionality

## Layout Components & Visual Variety

**Minimum 8–12 different component types per issue.** No two consecutive sections should use the same layout pattern.

### Core components (use every issue)
- [ ] Pull quotes (`.pull-quote`) — at least 3–4 across the issue to break prose rhythm. Use `.centered` or `.wide` variants for variety.
- [ ] Sidebar boxes (`.sidebar`) — curated lists ("Family Picks", "Context", "Juve Players Involved")
- [ ] Did You Know boxes — 3–5 scattered, section-aware colours
- [ ] Category dots (`.radar-cat`) in Release Radar and On the Radar
- [ ] Year badges (`.year-badge`) in history items
- [ ] Workout cards (`.workout-card`) in The Session when present

### Layout variation (use 3–4 of these per issue, rotate)
- [ ] At least one split layout (`.split-60-40` or `.split-40-60`) is used somewhere in the issue
- [ ] At least one compact-take or compact-grid is used for secondary stories
- [ ] At least one card stack (`.card-stack`) is used for reviews/comparisons (Screen & Sound or Shelf)
- [ ] At least one margin note (`.margin-note`) is used for a sidebar annotation
- [ ] At least one also-list uses the `.also-cards` variant instead of plain bullets
- [ ] The Long Shelf uses `.longshelf-grid` for two-column layout
- [ ] Book cards use `.book-grid` for side-by-side layout

### Visual furniture (use 2–3 of these per issue, rotate)
- [ ] At least 2–3 big-number callouts (`.big-number`) pull out dramatic stats mid-article
- [ ] At least one section uses a watermark label (`.sec-watermark`) for visual depth
- [ ] At least one section uses a section opener (`.sec-opener`) for a dramatic start
- [ ] Mini data visualisations (sparklines, pos-change arrows, mini-bars) are used where data supports it
- [ ] Rating dots (`.rating`) are used for review content in Screen & Sound or The Shelf

### Animation & interaction
- [ ] `.reveal` class is applied to key elements (section headers, stat bars, big numbers, images, angle boxes)
- [ ] `.count-up` class is applied to stat-bar numbers and big-number callouts
- [ ] At least one collapsible section (`<details>`) is used for optional-depth content
- [ ] Read-next connectors (`.read-next`) are present between at least 3 major sections

### Variation rhythm check
- [ ] No 3+ screen-heights of unbroken prose anywhere in the issue
- [ ] No two consecutive sections use the same layout pattern
- [ ] Components are rotated from previous issues — check what was used last time
- [ ] Inset dividers (`.divider.inset`) used occasionally for breathing room

## Image Treatments

- [ ] No AI-generated images
- [ ] No generic stock photography
- [ ] All images have alt text and source/credit captions
- [ ] Hero images use `.hero-img` (rounded) for within-section images
- [ ] At least one full-bleed hero (`.hero-bleed`) per issue
- [ ] Float images (`.img-float-left`) used for book covers, album art
- [ ] At least one image montage (`.img-montage`) or offset image (`.img-offset`) per issue for variety
- [ ] Not every image is the same full-width rectangle — vary sizes and treatments

## Typography & Contrast

- [ ] h3 headlines use semi-bold 600 weight — clearly differentiated from h2 at 700
- [ ] h3.minor variant (italic) is used for lower-priority sub-stories
- [ ] `.sub-label` (DM Sans) is used for secondary headers — distinct from JetBrains Mono section labels
- [ ] Body text on dark sections (Touchline, Screen & Sound, Shelf) uses `rgba(255,255,255,.8)` — not full white
- [ ] League tables use alternating row opacity for readability
- [ ] Score treatment in results strip uses 18px for visual weight
- [ ] Body line-height is 1.65 (tighter than Foreword's 1.75 for density in news sections)

## Format and Responsiveness

- [ ] Sections vary in tone — different register by topic area
- [ ] Sections don't bleed into each other visually — clear separation with backgrounds, dividers, spacing
- [ ] All sources are linked
- [ ] The navigator matches the actual content of the issue
- [ ] The HTML template's CSS, fonts, colours, and component styles are correctly applied
- [ ] Special editions use sidebars, callout boxes, stat bars, and DYK boxes generously — not walls of prose
- [ ] Two responsive breakpoints are present: 820px (portrait tablet) and 600px (phone)
- [ ] League tables are wrapped in `.table-wrap` for horizontal scrolling on small screens
- [ ] Navigator grid, Long Shelf grid, and book grids stack to single-column on small screens

## Synthesis

- [ ] Related stories across different sections are connected (e.g., an AI story that affects gaming)
- [ ] Local NI stories with wider context have that context mentioned
- [ ] Cross-section references are present where natural
