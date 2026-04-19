# The Signal — Editorial Specification

> Version 7.2 · Source of truth: `assets/weekly-template.html` + `assets/styles.css`

---

## Identity

The Signal is a Sunday magazine. Dense, opinionated, designed for one cup of coffee. It covers world news, sport, books, food, training, tech, travel, and data — whatever the week left on the desk — in a single long-form HTML issue built on the ember palette, Fraunces display type, Geist sans, and a motion-rich alternating-ground layout. It is not a newsletter. It does not exist to summarise; it exists to have a point of view.

Tone: a senior Sunday magazine journalist writing for any educated adult reader. Specific. Concrete. Willing to be wrong in print. Never hedges the way a bot would. British English throughout (colour, favour, programme, defence). Oxford comma is off. No headline-case in body copy.

---

## The Reader

The reader is a senior engineering manager based in Northern Ireland, working in UK banking/fintech. Age early-to-mid 30s, married, considering children, lives in a semi-detached house, runs a small family dog. Interests: World news/geopolitics, Nintendo/Switch 2/Steam Deck/GeForce Now, consumer tech (Pixel, Xiaomi, e-readers), AI tools (consumer not enterprise), LEGO, Juventus and Serie A, Premier League and Champions League, golf (majors/Ryder Cup), film/TV/streaming, Star Wars, fantasy/sci-fi books (Malazan, Cosmere — NO SPOILERS EVER), synthwave/retrowave, fitness (structured gym training via Ibex programme, recreational running with a 10k target, kettlebells at home, mobility/recovery via Pliability, Garmin wearable data and training science), podcasts (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions), audio dramas, NI local (light touch), Disney Parks/Efteling, meal prep and high-protein cooking, home gym building, tablet/Android productivity and apps, digital product entrepreneurship (Etsy templates including Notion/Kindle Scribe), UK personal finance and consumer fintech (Monzo/Revolut/Starling), travel (European family trips).

---

## The Cardinal Rule

**The reader profile is invisible in the prose.** Write as a general-interest Sunday magazine journalist for any educated adult. The reader profile drives TOPIC SELECTION — it never shows in voice, framing, or second-person address. No "as a banking engineering manager", no "your role in fintech", no "since you're tracking a 10k", no "fellow Malazan fan".

Violations of this rule are Gate 1 hard failures. Every violation must be fixed before delivery.

---

## Issue Structure (Standard Weekly)

The standard weekly contains exactly 13 structural positions, always in this order. Arabic numerals only; never Roman.

| # | Section | Ground | Key Components |
|---|---------|--------|----------------|
| 1 | **Cover** | Dark | `.cover`, `.cover__hero.parallax`, `.cover__scrim`, `.cover__ambient`, `.dispatch-seal`, `.cover__headline` with `<em>`, `.cover__tags`, `.cover__scroll-hint` |
| 2 | **Contents — The Ledger of the Week** | Paper | `.contents-ledger` rows; `.index-strip` at foot |
| 3 | **The Lead** | Paper by default | `.feature-band.feature-band--with-marginalia`, `.marginalia`, `.dropcap`, optional `.pull-break` |
| 4 | **Lead Pull-Break** | Dark (mirrors Lead contrast) | `.pull-break` with `.pull-break__q-open`, `.pull-break__quote`, `.pull-break__attribution` |
| 5 | **The Week** | Paper | `.timeline-rows.timeline-rows--condensed`; `.timeline-row` × 5–7 |
| 6 | **Rotating Section A** | Alternates with §5 | See Rotation Mechanics below |
| 7 | **Rotating Section B** | Alternates with §6 | See Rotation Mechanics below |
| 8 | **Rotating Section C** (optional) | Alternates with §7 | Only if 3 rotating selected |
| 9 | **Down the Rabbit Hole** | Dynamic — contrasts preceding section | `.feature-band.feature-band--with-marginalia` + `.marginalia` |
| 10 | **Rabbit Hole Pull-Break** | Matches Rabbit Hole ground | `.pull-break` |
| 11 | **Editor's Note** | Paper | `.editors-note` with `__left`, `__right`, `__signoff` |
| 12 | **Colophon** | Dark | `.colophon`, `.colophon__grid`, `.colophon__block` × 4, `.colophon__footer` |

**Ground alternation rule:** consecutive sections must not share the same ground. Lead is paper. Lead pull-break is dark. The Week is paper. First rotating section is dark. Subsequent sections flip each time. Rabbit Hole ground is chosen at generation time to contrast whatever section immediately precedes it. Colophon is always dark (bookending with Cover).

### Fixed vs Rotating

**Fixed sections** appear in every issue, always in position: Cover, Contents, The Lead, Lead Pull-Break, The Week, Down the Rabbit Hole (if due — see cadence below), Editor's Note, Colophon.

**Rotating sections** occupy positions 6–8. Pick 2–3 per issue from the pool below. Never pick more than 3 — crowding kills editorial focus.

---

## Rotation Mechanics

### Cadence Table

| Section | Cadence | Default Ground |
|---------|---------|----------------|
| The Shelf | Every 2–3 weeks | Dark |
| This Week in History | Every 2–3 weeks | Paper (dossier scheme) |
| The Pantry | Every 2–3 weeks | Paper |
| The Workshop | Every 3–4 weeks | Dark (dossier scheme) |
| The Toolkit | Every 3–4 weeks | Dark |
| The Ledger | Every 3–4 weeks | Dark |
| The Long Game | Monthly (every 4 weeks) | Paper |
| The Itinerary | Every 3–4 weeks; increases near trips | Paper |
| Down the Rabbit Hole | Every 3–4 weeks (sidebar/embedded long read) | Dynamic |

### Selection Rules

- Pick by who's most overdue first (compare `last_appeared` against cadence window in state file).
- Never select more than 3 rotating sections.
- Do not select more than 2 sections with the same default ground without adjusting one.
- Down the Rabbit Hole is selected separately; it sits in its own position (§9 above), not as one of the 2–3 rotating slots.

---

## Search Checklist

Run every week during the research phase. Never rely on training data; always search for live sources.

### Core Groups (every issue)

- **World news** — major geopolitical developments, conflict updates, diplomacy
- **UK news** — government, economy, cost of living, NHS, NI-specific if warranted
- **Sport** — Premier League results, Champions League, Serie A / Juventus, golf (majors and Ryder Cup in season)
- **Tech & Gaming** — Switch 2, Steam Deck, GeForce Now, Pixel, AI consumer tools
- **Entertainment** — streaming, film releases, TV
- **Training & Running** — fitness science, running, gym, Garmin data, Ibex programme news
- **UK Personal Finance** — rates, ISAs, Monzo/Revolut/Starling, HMRC, consumer fintech
- **Books** — new releases, reviews, publishing news (no spoilers for active series)

### Rotating Groups (per selected section)

Research the rotating group only when that section is selected for this issue.

- **The Shelf** — new book releases, reissues, essays, memoir, reader picks, podcast/audiobook releases
- **The Pantry** — recipes, food trends, high-protein cooking, meal prep, ingredient sourcing
- **The Workshop** — gym equipment, home gym, kettlebells, running gear, mobility tools, AI fitness tools
- **The Toolkit** — apps, productivity software, Android tools, browser extensions, AI consumer tools, Etsy/Notion templates
- **The Ledger** — inflation, interest rates, UK tax, ISAs, Monzo/Revolut/Starling updates, housing market, FIRE content
- **The Long Game** — macroeconomics, long-run data stories, markets history, FIRE movement arcs
- **The Itinerary** — destination guides, theme parks, family travel, European trips, training event prep
- **This Week in History** — on-this-day events, preferably UK-flavoured or with a global angle
- **Down the Rabbit Hole** — a single strange/deep topic to sustain 600 words with a clear editorial position

---

## Component Quick Reference

Components are defined fully in `component-contracts.md`. Quick map by section:

| Section | Primary Components |
|---------|-------------------|
| Cover | `.cover`, `.cover__hero`, `.cover__ambient`, `.dispatch-seal`, `.cover__headline em`, `.cover__tags` |
| Contents | `.contents-ledger__row`, `.index-strip__item` |
| The Lead | `.feature-band--with-marginalia`, `.marginalia`, `.dropcap`, `.body-lead` |
| Pull-Break | `.pull-break`, `.pull-break__q-open`, `.pull-break__quote`, `.pull-break__attribution` |
| The Week | `.timeline-rows--condensed`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body` |
| The Shelf | `.fan-spread`, `.fan-spread__card`, `.brief-grid`, `.brief-card` |
| The Pantry | `.plate-strip`, `.plate-strip__track`, `.plate`, `.plate__stat-num.count-up` |
| The Workshop | `.feature-band`, `.chart-card`, `.datum-card`, `.pull-quote-card` |
| The Toolkit | `.fan-spread`, `.fan-spread__card`, `.brief-grid`, `.brief-card` |
| The Ledger | `.dash`, `.dash__cell`, `.dash__num.count-up`, `.chart-card` |
| The Long Game | `.timeline-rows`, `.chart-card`, `.hero-quote` |
| The Itinerary | `.plan-infographic`, `.timeline-rows`, `.timeline-row` |
| This Week in History | `.timeline-rows`, `.timeline-row` (dossier scheme) |
| Rabbit Hole | `.feature-band--with-marginalia`, `.marginalia`, `.pull-break` |
| Editor's Note | `.editors-note`, `.editors-note__left`, `.editors-note__right`, `.editors-note__signoff` |
| Colophon | `.colophon`, `.colophon__grid`, `.colophon__block`, `.colophon__footer`, `.dispatch-seal` |

Transition markers between sections: `.ribbon` with `.ribbon__track` and `.ribbon__item` elements. Use at least one ribbon per issue; for a second ribbon, add `.reverse` to make the track animate in the opposite direction.

---

## Issue Formats

Nine formats are supported. The standard weekly is the default; specials are triggered by the auto-trigger logic below.

| Format | When | Description |
|--------|------|-------------|
| **Standard Weekly** | Default | Full rotating editorial; 2–3 rotating sections + all fixed sections |
| **Deep Dive** | By request or P2 trigger | Single topic as one extended long read. Lead expands to fill 70% of the issue. Rotating sections collapsed to 1 + The Week |
| **The Countdown** | 2–3 weeks before a trip | Trip-preparation focus. The Itinerary expanded; Workshop shifts to packing/gear. The Week retained |
| **The Season Review** | End of a major sporting/TV season | Extended retrospective on the season just ended. The Long Game format fills the rotating slot |
| **The Versus** | Head-to-head moment (product launch, fixture) | Two-track comparison structure. Fan-spread or plate-strip used for each side |
| **The Rewind** | Last Sunday of June / last Sunday of December | Mid-year or end-of-year retrospective. Dash data panel prominent; timeline-rows as spine |
| **The Starter Kit** | Picking up a new hobby/interest | Primer format: history, kit, terminology, first steps. Plate-strip for gear/kit |
| **The Blueprint** | How to build or set something up | Step-by-step structured piece. Plan-infographic or timeline-rows as backbone |
| **The Field Guide** | ~6 weeks before a confirmed trip | Destination deep-dive. Itinerary expanded; all other rotating sections subordinate |

---

## Auto-Triggered Specials

### Priority 1 — Calendar-Fixed (check first, every week)

- Last Sunday of June → **The Rewind** (mid-year)
- Last Sunday of December → **The Rewind** (end-of-year)
- Trip in `upcoming_trips` approximately 6 weeks away → **The Field Guide**
- Trip in `upcoming_trips` approximately 2–3 weeks away → **The Countdown**

### Priority 2 — Event-Driven

- Tournament final, season conclusion, major product launch, season premiere of a tracked show → format determined by the event type (Season Review, Deep Dive, The Versus)

### Priority 3 — Editorial Pick (lowest priority)

- Only fires if `last_special_date` is 5+ weeks ago and no P1 or P2 trigger fires.

### Guardrails

- Never run 3 consecutive specials.
- If the last two issues were both specials, force a standard weekly regardless of triggers.
- After a Field Guide or Countdown, the next issue must be a standard weekly.

### Trip-Aware Scheduling

**Upcoming trips in state file:**
- Efteling + Beekse Bergen, Netherlands. 2026-06-30 to 2026-07-07.
  - Efteling: 2 nights (30 Jun–2 Jul)
  - Beekse Bergen Safari Resort: 5 nights (2–7 Jul)
  - Field Guide due approximately 19 May 2026
  - Countdown due approximately 9 Jun 2026

**Current training phase (from state file):**
- Block 1 (Race Prep + Fat Loss): 4 April – 3 May. 10k race 3 May. Concurrent training (4 lifts + 3 runs/week).
- Block 2 (Fat Loss + Hypertrophy): 4 May – 30 June.
- Post-30 June: hypertrophy at maintenance/surplus (holiday recovery).

---

## Key Rules

### Editorial Voice

- Opinionated, specific, concrete. Every list item must carry at least one opinion sentence.
- British English spelling throughout. No Americanisms (color → colour, analyze → analyse, etc.).
- Oxford comma is off: "red, white and blue" not "red, white, and blue".
- No headline-case in body copy. Section heads use sentence case.
- Accent italic (`<em>`) on 1 key word per headline; 1–2 phrases per paragraph. No highlight bars, no bold-for-emphasis in body.
- No hedging adverbs ("quite", "somewhat", "perhaps arguably"). Take the position. You can be wrong.

### Content Standards

- Opinions are mandatory, not optional. A list without opinions is a list from a search engine.
- Do not fabricate statistics. Every numeric claim must cite its source (inline or in colophon sources block).
- Do not fabricate quotes. Every attributed quote must be sourced.
- No spoilers, ever, for: Malazan Book of the Fallen, Cosmere (all Sanderson), Star Wars (any era), or The Running Man.
- Ongoing stories carry a running counter ("Week 7 of the conflict") — check the state file for `ongoing_stories` and update weeks counts before writing.

### Section Rules

- Every major section (Lead, rotating sections, Rabbit Hole) requires at least one image.
- No two consecutive sections may use the same primary component (e.g. two back-to-back `.feature-band` without a ribbon or different visual piece between them).
- The `.dispatch-seal` appears only on the Cover and the Colophon. Nowhere else.
- The `.folio-watermark` sits inside the Lead and the Rabbit Hole for the section number.
- Pull-break sections (`sec dark pull-break` or `sec paper pull-break`) are not counted in the ground-alternation sequence — they are interludes.

---

## Visual Design

### Palette

- **Default scheme:** `ember` — `data-scheme="ember"` on `<body>`. Background `#0c0a08`, paper `#f1ead9`, accent `#d2411e`, ink `#0c0a08`, muted `#8a7f6a`.
- **Dossier scheme:** brass accent `#b8902a`. Use for The Workshop and This Week in History sections. Apply as `data-scheme="dossier" style="--accent:#b8902a;"` on the section element.
- **Blueprint scheme:** navy. Available but rare. Use sparingly for appropriate data-heavy specials.
- **Midnight scheme:** true black. Use for exceptionally sombre leads.
- Accent sub-variants via `data-accent`: `cool` (cyan, `#48cae4` — Itinerary), `wild` (amber), `food` (orange), `nature` (green), `urban` (slate). Set on the section element.
- Accent usage ≤ 8% of any section's visible area.
- Forbidden hexes: never use `#1B1B2F`, `#E8384F`, `#D2FF00`, or any McLaren orange. Never use `rgb()` inline if it isn't in the palette.

### Fonts

The stylesheet defines exactly two font families:
- `--display` / `--serif`: **Fraunces** (display and body serif). Loaded from Google Fonts.
- `--sans`: **Geist** (sans-serif, used for labels, eyebrows, metadata). Loaded from Google Fonts.

There is no monospace family. No other typefaces. Never reference Cormorant, DM Sans, JetBrains Mono, Instrument Serif, Inter, Newsreader, or IBM Plex Mono anywhere in the HTML or docs.

### Motion

All motion is implemented in `assets/script.js`. The generator must preserve the motion hooks; the JS file does the rest.

| Hook | Where used |
|------|-----------|
| `.parallax` | Cover hero image (required); feature-band hero images (recommended) |
| `.reveal` | All major content blocks; adds `in` class at 20% viewport intersection |
| `.count-up` + `data-target` | Numeric stats: `.dash__num`, `.plate__stat-num`, `.datum-card__value` |
| `.pan` | Images that should drift on scroll (object-position pan) |
| `.ln` | Section heads — JS splits by `<br>` and staggers line-by-line entry |
| `.ribbon` | Animated marquee; automatic via CSS once `.ribbon__track` is present |
| `.grain` | Fixed full-viewport film-grain layer; always present, `aria-hidden` |
| `.colour-flood` | Fixed full-viewport layer; JS drives clip-path transitions between section grounds |
| `.dropcap` | Settles in on scroll via `.dropcap.in` |

### Texture and Atmosphere

- Paper sections get a contour-paper SVG texture via `sec.paper::before` in CSS (automatic).
- Cover ambient drift: slow 22-second accent-glow cycle (`cover__ambient`).
- Dispatch seal rotates 28 seconds linear infinite (cover + colophon only).
- Ribbon marquees run at 40 seconds; `.reverse` ribbons animate in the opposite direction.
- Scroll progress bar: thin accent line at top of viewport, driven by JS.

---

## What Good Looks Like

A well-executed issue of The Signal has all of these qualities:

- **The prose has a spine.** Every section makes a claim. Every list item adds an opinion. The reader finishes each section knowing what The Signal thinks, not just what happened.
- **The layout breathes.** Dark and paper grounds alternate cleanly. No two consecutive sections share the same primary component. The ribbon and pull-break interludes provide rhythm.
- **Numbers are live.** Count-up stats fire on scroll. Every datum is sourced, attributed, and checked against something published this week.
- **The reader profile is invisible.** The Pantry contains good food writing, not "high-protein recipes for your gym goals". The Workshop is gear journalism, not "since you're training for a 10k".
- **Motion is present but not exhausting.** Cover parallax, at least one ribbon, at least two pull-breaks, count-ups on stats, reveal on all major blocks.
- **The Colophon earns its place.** Sources section has ≥ 6 entries with real URLs. The About paragraph says something true about what The Signal is for.
- **The dispatch seal appears exactly twice.** Once on the cover, once on the colophon. Never elsewhere.
