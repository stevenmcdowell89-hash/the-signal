# Spec slice — specials

_This file consolidates the specials/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Content-first contract (non-negotiable)
Every non-holiday special edition obeys these rules. Holiday specials (Countdown, Field Guide) have their own contract in `36-holiday-*`.

- **No motion in the non-holiday system.** As of v8.21, the non-holiday specials are an editorial / paper-and-ink design with no scroll-driven animation. Holiday formats retain their motion layer.
- **JS-off renders a complete issue.** The whole non-holiday system is pure CSS.
- **Word counts and section depth are the spine.** Visual flair sits around content, not in place of it.
- **Quiet vs. visual register.**
  - *Quiet* — Starter Kit. Baseline editorial system + minor accent (drop cap, format colour, numbered ring badges on Starter Kit essentials).
  - *Argued (Deep Dive)* — baseline plus `.argument` framed thesis early + `.keep-digging` cross-media closing grid. Body is literary, but two distinctive components anchor the opening and the close.
  - *Visual* — Versus, Rewind, Season Review, Shortlist, Next, Lookahead. Same baseline plus format-specific components (`.vs-tape` / `.vs-pair` / `.vs-verdict`, `.year-band` / `.rewind-cards` / `.memory-test`, `.rating` / `.scoreboard` / `.milestones`, `.tier-band` / `.pick`, `.on-ramp` / `.only-one`, `.calendar` / `.cal-verdict` / `.crunch-week`) for clear differentiation.



---

## cover

### Authoring a special edition
1. On `<body>`, add `is-special` and `data-special="<format>"` where format is one of: `countdown`, `rewind`, `versus`, `season-review`, `deep-dive`, `guide`, `starter-kit`, `shortlist`, `next`, `lookahead`, `field-guide`. (2026-07 WP-0 vocabulary reconciliation: `guide` is the merged recommendation format — v8.39 S4 — with `starter-kit`/`shortlist` kept as archive back-compat slugs; `blueprint` is retired — v8.22 — and must not be used; `lookahead` is retired/folded — v8.39 S2 — its slug survives only for the two archived drafts.)
2. **For Countdown only:** add `data-dday-start="N"` on `<body>` where N is the number of days between the issue date (today, when generating) and the event. The D-day badge displays this authored value statically — a magazine issue is a snapshot and the badge must agree with the prose, forever. Compute N at generation time as `(trip_date - today)` in days. The Countdown auto-trigger fires 2-3 weeks before a trip, so N is typically 14-21. If generating a prototype or back-dated issue, use the fictional issue-date reference. (Optional: also add `data-trip-date="YYYY-MM-DD"` for human reference, but it does NOT drive a live countdown at runtime.) The previous scroll-scrubbing pattern (`data-dday-start` + `data-dday-end` interpolated by scroll percentage) has been removed — a scroll-driven countdown is nonsensical.
3. Include the components from the component list below as appropriate for the format. Each component has a documented HTML contract in `component-contracts.md` (or inline in the CSS).
4. Inject assets with `scripts/inject-assets.sh` as normal.


### Component list

> **Note (v8.21):** The non-holiday special edition system was redesigned around an editorial / paper-and-ink aesthetic (see `assets/css/23-` through `32-` files). The list below documents the **new** components. Holiday formats (Countdown, Field Guide) retain their previous holiday-themed system in the `33-`, `36-` through `44-` CSS files — those are not affected by this list.

**Persistent chrome (every non-holiday special):**
- `.mast` — thin pinned bar at the top of every page, containing `.mast-wordmark`, `.mast-format`, `.mast-sep`, `.mast-date`. Inverts to a translucent dark style while the dark cover is in view. Provides a constant "where am I" anchor.

**Cover (every non-holiday special):**
- `.cover` — single-screen dark cover with filmic grain and per-format radial-pool gradient. Contains:
  - `.cover-meta` — top row: issue date/number left, format mark right
  - `.cover-body` — centered column with `.cover-eyebrow` (mono caps), `.cover-title` (serif), optional `<em>` for accent words, `.cover-deck` (italic serif), optional `.cover-slogan` block (epigraph / slogan with hairlines top + bottom)
  - `.cover-foot` — bottom row with optional `.cover-scroll` cue
- Versus only: title is a 3-column grid (`.vs-a` / `.vs-glyph` / `.vs-b`) — the matchup, balanced

**Chapter structure (every non-holiday special):**
- `.foreword` — first chapter after cover; larger measure, italic small-caps first line via `.foreword-body`
- `.chapter` — every subsequent chapter. Contains:
  - `.chapter-head` with `.chapter-numeral` (italic roman) + `.chapter-title`
  - `.chapter-body` — clamped to `--measure` (36rem) by default
  - `.is-wide` / `.is-fullbleed` modifiers on children to break out of the measure
- `.sp-kicker` — sub-section heading inside long chapters (mono caps, accent)

**Baseline flair (every non-holiday special):**
- `.chapter-body.has-dropcap` or `<p class="lede">` — first paragraph gets a large accent drop cap
- `.sp-ornament` — three dots, used to break up sub-sections within a chapter
- `.pullquote` with `<p>` + optional `<cite>` — huge italic pull quote with ornamental "
- `.marginalia` (+ `.is-left`) with `.m-label` + body — chip in the gutter; falls back to inline at ≤1180px
- `.bignum` with `.bignum-value` + `.bignum-label` — single stat callout
- `.bignum-row` — grid of 2–4 `.bignum` items, top + bottom hairlines
- `.source-strip` — mono caps row of citations
- `.sp-number` — inline accent-coloured stat (e.g. `<span class="sp-number">74</span>`)

**Figures (every non-holiday special):**
- `figure.fig` with `<img>` + `<figcaption>` containing `.fig-caption` + `.fig-credit`
- Modifiers: `.is-wide`, `.is-fullbleed`, `.is-half` (+ `.is-left`)
- `figure.image-quote` with `<img>` + `<blockquote>` — darkened photo with overlaid italic quote and accent-coloured `<cite>`

**Rich pick + multi-item grid (every non-holiday special, v8.22.4):**
- `.pick` — image + body grid, alternating layout (image-left odd rows, image-right even rows). Contains `<img class="pick-img">`, `.pick-body` with optional `.pick-tag` pill + `<h3>` + prose + optional `.pick-stats` (a `<dl>` of mono-caps `<dt>` + serif `<dd>`). The workhorse for detailed-pick chapters across Shortlist, Starter Kit, Next, Deep Dive.
- `.also-cards` grid — 4-8 `.also-card` items (`.ac-meta` mono-caps category line + `<h4>` + italic `<p>` why-it's-here + optional `<a>` source link). For "Also Worth Knowing" / "Where to Go After That" / "Shows Just Outside the Top Six" / "Related Reading" patterns. Cross-format.

**Meanwhile section (when a special replaces the standard weekly):**
- `.meanwhile-list` — bulleted catch-up list with tier dots (`.tier-hot` / `.tier-warm` / `.tier-note`)

**Footer (every non-holiday special):**
- `.sp-footer` with `.sp-footer-wordmark`, `.sp-footer-meta`, optional `.sp-footer-colophon` — quiet sign-off panel with ornament rule above

**Format-specific flair (visual formats — Versus / Rewind / Season Review / Shortlist / Next / Lookahead):**
- *Versus:* `.vs-tape` (tale-of-the-tape table), `.vs-pair` (stacked case panels with per-side accent rails + Case A / Case B badges), `.vs-verdict` (dark wide verdict slab with side stripes), optional `.vs-scoreboard` ribbon (running tally with side colours)
- *Rewind:* enlarged `.bignum-row`, `.year-band` (12-month rail with `.year-band-month` + `.year-band-marker` highs/lows + `.year-band-legend`), `.rewind-cards` (`.rewind-card` + `.is-low` modifier), `.chapter-head.is-throughline` + `.throughline-mark` for the Throughline chapter, `.memory-test` 3-column grid (`.mt-col.mt-stick` / `.mt-might` / `.mt-fade`) for the second killer feature
- *Season Review:* `.scorecards` grid of `.scorecard[data-tier="hot|warm|cold"]` cards — each with `.sc-head` (`.sc-name` + `.sc-score`), `.sc-bar` driven by `--score: N`, `.sc-verdict` italic line. Legacy `.rating` / `.scoreboard` / `.milestones` still available for stat-heavy supporting chapters.
- *Shortlist:* `.lens` framed criteria block (`.lens-eyebrow` + `.lens-statement` italic + `.lens-criteria` numbered list) at the opening; `.tier-band` (`.tb-mark` + `.tb-label` + `.tb-rule`, `data-tier="strong|wildcard"` for accent swap) divides the body into Top / Strong / Wildcard sections; the cross-format `.pick` (with `.pick-img`, `.pick-tag`, `.pick-stats`) carries each detailed pick; `.cheat-sheet` table (`#` / `Pick` / `Tier` / `Why` columns, rows tagged `data-tier="top|strong|wildcard"` for inline colour-coding) at the close. `.also-cards` for "Also Worth Knowing."
- *Next:* `.next-tier` row with `data-step="I|II|III"` for the numbered roundel marker (+ `.is-wildcard` modifier for the third tier); `.on-ramp` stepped track — the killer feature — with three `.on-ramp-row` entries each tagged `data-step="start|reassess|then"` (auto-renders the glyph + connecting track), `.on-ramp-label` + `.on-ramp-body`; `.only-one` dark slab for the "If You Only Try One" hero with star seal (`.only-one-mark` + `.only-one-pick` + `.only-one-reason`)
- *Lookahead:* `.calendar` `<ol>` with optional `<li class="cal-week">` dividers and `.cal-row` items carrying `data-verdict="hot|warm|wait|skip"` — each row has a tinted background + accent rail in the verdict colour, `.cal-when` (date card with `.cal-date` + `.cal-where`), `.cal-body` (`<h4>` + `<p>`), `.cal-verdict` containing `.cal-verdict-chip` (full pill — the killer chip with glyph + label + tinted bg) and optional `.cal-reason` italic gloss; plus `.crunch-week` callout with `.crunch-header` (`.crunch-label` warning chip + `.crunch-when` heading) and `.crunch-list` `<dl>` whose `<dt>` carry `data-tier="hot|warm|wait|skip"` for tier-coloured Prioritise / Defer / Skip badges

**Deep Dive flair:**
- All baseline components above. Plus two killer-feature components:
- `.argument` — framed thesis block (`.argument-eyebrow` + `.argument-thesis` italic serif + `.argument-stance` paragraph). Sits between Foreword and the body; pilcrow seal in accent.
- `.keep-digging` — closing cross-media grid of `.kd-item` cards. Each card carries `data-medium="podcast|tv|film|game|video|book"` (which paints the per-type pill colour + glyph) and contains `.kd-medium` pill, `.kd-title` heading, optional `.kd-episode` italic line (mandatory on podcasts — series-only refs forbidden), `.kd-why` italic gloss.

**Starter Kit flair:**
- All baseline components above. Distinct `--accent` colour set on `body[data-special="starter-kit"]`.
- `.essentials` ordered list — each `<li>` gets a numbered ring badge. **Use only for short concept lists** ("5 essential techniques", "7 things to learn first"). NOT for detailed-pick chapters — those use the cross-format `.pick` (each pick gets image + body + `.pick-stats` + a `.pullquote` or `.image-quote` for visual rhythm).
- `.week-plan` vertical timeline — the killer feature. Seven `.wp-day` items with badged day-marks (Day N / Mon) on the left of an accent rail, body on the right.

**What was removed (v8.21 redesign):**
- The entire pre-v8.21 special-edition chrome: all scroll motion, the pre-roll splash, the ticker masthead, the rotated format badge, the per-format signature moments, the sticky-scroll chapter gates, the hype variants, the three-column spread layout, and the old editorial breakout components.
- The Blueprint format (retired in v8.22 — never used after 6+ specials, planning use cases absorbed by Deep Dive and Shortlist).
- None of that vocabulary is in the CSS bundle for non-holiday specials any more. Use ONLY the component list above — a class that isn't in this list, `component-contracts.md`, or the current CSS does not exist, and inventing one is a Gate-2 markup failure. Already-published issues keep rendering because their CSS is inlined at generation time; never copy component markup from a pre-v8.21 archive issue.




---

## meanwhile

## Auto-Triggered Specials

The workflow's **scout step** (step 2 in SKILL.md) evaluates these triggers with 2-4 quick searches **before** committing to any full research pass. This prevents wasting research on a standard weekly that gets discarded. The reader never requests these — they appear as a surprise, like a magazine supplement. **All formats remain manually triggerable at any time** in addition to their auto-triggers.

### The "Meanwhile..." Section

When a special edition replaces the standard weekly, it must include a **"Meanwhile..."** section before the Footer. This ensures the reader never misses a week of news.

- 12-18 bullet points covering the week's biggest stories across all fixed-section areas: world news, tech/gaming, sport (results, tables, key stories), entertainment, and any breaking news.
- **Every item must include a linked source** so the reader can go deeper on anything that matters to them.
- Format: bold headline + one sentence + linked source. Compact, scannable.
- Use `.also-list` with `.tier-hot` / `.tier-warm` / `.tier-note` tiers to signal importance.
- This is a catch-up safety net, not a section to linger in. Keep it tight.

### Auto-Trigger Logic

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
| Premier League season concluded | Season Review — Premier League | Research finds final matchday results |
| Major tournament concluded | Season Review — [Tournament] | Research finds final/closing ceremony |
| A major product launch this week | Deep Dive or Versus | Research finds a significant launch in a core interest (Switch 2, major game, new console, etc.) |
| Two competing products launched/announced close together | Versus | Research finds a natural head-to-head |

**Priority 3 — Editorial Picks (the safety net against dry spells)**

If no Priority 1 or 2 trigger has fired in the last 5 weeks, the editor picks a special from the pool below. These are evergreen — they don't depend on external events:

| Format | Example Topics |
|---|---|---|
| Guide (beginner mode) | Getting into Malazan, Specialty coffee from scratch, Fantasy Premier League for beginners, Home kettlebell training, Starting on Etsy |
| Guide (category mode) | A category roundup that hasn't been covered recently — boutique games, kettlebell drills, audio essay channels |
| Deep Dive | The history of a favourite game franchise, A deep look at a training methodology, The state of e-readers in 2026, Serie A tactical evolution |
| Versus | V60 vs AeroPress, Two fitness approaches, Two e-readers, Two budget tablets |

**The editorial picks pool ensures there's always a viable special available.** The editor selects the most timely or interesting option from the pool. Over time, used topics are tracked in the state file to avoid repeats.

**Manual-only format — Next.** Next never auto-triggers; it requires the reader to call it because it depends on specific context that only the reader holds.
- **Next** ("Run a Next — after [the thing you finished]") — needs the anchor: what the reader just finished. The magazine can't reliably detect "finished" status for podcasts/books/seasons from external signals.
- **Lookahead — RETIRED / FOLDED (v8.39, S2).** Formerly the second manual-only format; folded into the weekly's Release Radar + On the Radar (see § The Lookahead status marker). Do not run it. A reader asking "what's coming up over the next few weeks" is answered by the weekly's radar sections, not by a dedicated issue.

### The Saga (trigger-driven, v8.27 — no cadence timer)

The Saga (lore deep-dive — worldbuilding essays: Maul's arc across the shows, how Allomancy/the Cosmere connect, Malazan Warrens; **strictly no plot/endings**) used to fire on a 6-week clock. It no longer does. It runs only on a **reason**, of which there are two kinds — this is the general model for any section that depends on context the orchestrator can't infer:

- **Public peg (the researcher can find it).** A finale aired this week, a new book/season in a series the reader follows released, an author did an AMA. The scout/researcher detects this in Phase 0f/3 and pegs a Saga. This is the only Saga trigger that fires automatically.
- **Private peg (the pipeline cannot know it).** What the reader is *personally* reading or watching right now is invisible to the pipeline — the same boundary that makes Next and Lookahead manual-only. Surface it two ways: (a) the reader keeps a lightweight **`currently_reading` / `currently_watching`** note in `state/signal-state.json`, which the researcher reads as a peg source; (b) a **manual trigger** ("run a Saga on the Cosmere", "a Next after Deadhouse Gates") — zero-maintenance, on-demand.

If neither peg is live, The Saga simply doesn't run that week — it is never scheduled to fill a slot.

**Generalised principle: sections that depend on private context are reader-triggerable, not calendar-driven.** The magazine asks for / reads that context rather than guessing. This is the same reason The Session reads `training_phase` and The Itinerary reads `upcoming_trips`; v8.27 extends the pattern to reading/watching (`currently_reading` / `currently_watching`) for The Saga, and lets it inform Bookmark and Screen & Sound pegs too.

### Guardrails

- **Target frequency: one special every 4-6 weeks on average.** Not a hard rule, but if 6+ weeks pass without a special, Priority 3 must fire. If two natural triggers cluster in consecutive weeks, that's fine — but never three specials in a row.
- **Never more than 2 consecutive specials.** If two specials ran back-to-back, the next issue must be a standard weekly regardless of triggers.
- **The standard weekly is the backbone.** Specials are seasoning, not the main course. Most Sundays should be the standard weekly with rotating sections.
- **Manual triggers always override.** If the reader requests a specific format, that takes priority over any auto-trigger.
- **Track in state file:** `last_special_date`, `last_special_format`, `consecutive_specials_count`, `editorial_picks_used`.

### Trip-Aware Scheduling

Trips create a dense window where multiple triggers compete. These rules prevent collisions:

- **Issues still run during trips.** The reader wants something to read on the plane, at the pool, or watching giraffes. Standard weeklies and specials generate as normal even when the reader is away.
- **Defer Rewinds that clash with trips.** If a Rewind trigger (half-year or year-end) falls within 7 days of a trip start, defer it to the first Sunday after the reader returns. A Rewind is better as a "welcome back" issue than something competing with pre-trip excitement. All other formats (standard weekly, Season Review, etc.) run on schedule.
- **Field Guide before Countdown.** The Field Guide fires at ~6 weeks out; the Countdown fires at 2-3 weeks out. They should never collide. If they somehow would (very short trip lead time), the Countdown takes priority — the Field Guide is only useful with enough lead time to plan.
- **Season Reviews are patient.** A Season Review can't run until the week after the season ends (results need to be final). It has a 6-week window from there -- after that, drop it. Don't force it at the 6-week mark either; if other specials or strong standard weeklies have filled the calendar, that's fine. A Season Review that never runs is better than one shoehorned in when the moment has passed. If it does run, a combined review covering both Serie A and PL in one issue is fine when they end the same weekend.
- **Trip priority order for a typical trip window:** Field Guide (6wk) → standard weeklies / Season Reviews → Countdown (3wk) → standard weeklies → deferred Rewind (first Sunday back if clashing).

---



---

## chapter-gate

### Chapter gate — RETIRED (v8.21)

The v8.5 sticky-scroll chapter gate (the full-viewport black panel that opened every chapter) was deleted in the v8.21 redesign along with the rest of the pre-v8.21 chrome; it exists in no current CSS, and no current format opens chapters with a gate. Chapter breaks on non-holiday specials are now carried by the `.chapter-head` chrome (numeral + title) in the Component list above; holiday issues carry structure with halves and the transit (§ Holiday Identity). Canonical chapter orders and narrative-arc guidance live per-format in `references/spec/formats.md`. Superseded by the unified core — see `references/core-components.md`.



---

## imagery-budget

### Imagery budget — MANDATORY for loud special editions

A Versus / Rewind / Season Review issue **must not** have entire chapters that are walls of text. The previous pattern (front-loaded imagery in the opening then plain prose for the rest) is banned. (Holiday formats — Countdown, Field Guide — carry their own, higher image budgets in § Holiday Identity and the format specs.) Apply the following rule at generation time, using the LIVE v8.21 component kit only:

**Every chapter (Foreword excepted) must include at least ONE of:**
- Imagery: `figure.fig` (with `.is-wide` / `.is-fullbleed` / `.is-half` as fits) or `figure.image-quote`
- A high-impact typographic component: `.pullquote`, `.bignum` / `.bignum-row`, or an inline `.sp-number` stat
- A rich container: `.pick` (+ `.pick-stats`) or an `.also-cards` grid

**In addition, across the whole issue:**
- At least **3 chapters** carry embedded imagery (`figure.fig` or `figure.image-quote`)
- At least **2 chapters** use `.pullquote` to break up prose
- At most 1–2 figures carry `.sp-parallax-band` (the single cinematic scene image — see the parallax discipline in `component-contracts.md`)
- Long prose chapters (>500 words) include `.sp-kicker` sub-headings
- Long prose chapters include at least one `.marginalia` aside or inline `.sp-number` callout

These are minimums — more is fine; `validate-issue.py`'s `special-variety` gate hard-fails a special that deploys too few distinct component types. Research images for EVERY major chapter, not just the cover topic.



---

## editorial-body-kit

### Editorial body kit — RETIRED (v8.21)

The pre-v8.21 "editorial body kit" (tier-5 spread structure) and its tier-5.5 motion layer were deleted in the v8.21 paper-and-ink redesign; none of that vocabulary exists in the current CSS bundle. Chapter structure is now the `.chapter` / `.chapter-head` / `.chapter-body` contract in the Component list above, and the non-holiday system ships with no scroll-driven motion. Superseded by the unified core — see `references/core-components.md`.



---

## signature-moments

### Signature moments — RETIRED (v8.21)

The per-format signature-moment components were deleted in the v8.21 redesign and are not in the current CSS bundle. Format differentiation now comes from the per-format flair kits in the Component list above (and, for Countdown / Field Guide, the Holiday Identity layer). Superseded by the unified core — see `references/core-components.md`.



---

## chapter-transitions

### Chapter transitions + ambient (format-agnostic)

The pre-v8.21 transition components (stat curtains, page folds, wipes) were deleted in the v8.21 redesign; chapter rhythm on non-holiday specials now comes from the chapter chrome itself (`.chapter-head`, grounds, `.sp-ornament` breaks). One ambient component survives:

- **`.sp-chapter-beads`** — fixed right-gutter bead strip, one per chapter, with within-chapter progress connector (CSS `19-chapter-beads.css`, JS controller in `assets/script.js`). Special editions only — the Transmission weekly ships its own light chrome and does not load this bundle. Markup: a single `<aside class="sp-chapter-beads" aria-hidden="true"></aside>` near the end of `<body>` (already included in `template-parts/19-closing.html`). **Title resolution:** first `<h2>` text → section `id` (title-cased) → `Chapter N`. **Mobile (≤ 820px):** collapses to a thin vertical line with no labels. Click a bead to scroll to that chapter. Reduced-motion: beads stay, active state only.



---

## multi-venue


> See `formats/countdown.md` for the full Countdown spec; this file is a cross-format summary of multi-venue rules that live inside that section.

Multi-venue trips (e.g. Efteling + Beekse Bergen) get parallel treatment:
- Equal hype weight: words and images per venue sit within a 60/40 split.
- Each venue's full estate is researched, not just the marquee feature.
- A `data-multi-venue="true"` body flag activates per-venue palette tokens.
- Tier 33 (`33-countdown-destinations.css`) provides Efteling and Beekse Bergen
  palettes; Tier 36 (`36-holiday-identity.css`) provides the two-half + transit
  structural rhythm. The two layers compose.

For Field Guides, multi-venue rules live in `formats/field-guide.md`
(headline rule 7 — multi-venue balance).


---

## hype-chapter-visuals


The pre-v8.21 hype-chapter modifier system was deleted with the rest of the old special-edition chrome; its CSS file no longer exists. Hype register on Countdown / Field Guide is now carried entirely by the Holiday Identity layer (`.hol-*` components + `.theme-*` ambients — see § holiday-identity) and by the hype components in `43-holiday-hype.css` / `44-holiday-sprinkles.css`. Literary formats (Deep Dive, Versus, Rewind, Season Review) use the v8.21 editorial kit with no hype variants. Superseded by the unified core — see `references/core-components.md`.


---

## readability-locks


The pre-v8.21 readability-lock CSS layer was deleted with the old chrome; its CSS file no longer exists. In the live v8.21 editorial system, each self-painting component locks its own text colour in its own rules — use the canonical markup from `references/component-contracts.md` (Gate 1E) and contrast is handled; never add inline styles or ground overrides. Superseded by the unified core — see `references/core-components.md`.


---

## portrait-spread


The pre-v8.21 three-column spread layout was deleted in the v8.21 redesign; no current CSS or JS implements it. Chapters are a single measured column (`.chapter-body`, 36rem) with `.is-wide` / `.is-fullbleed` breakouts; `.marginalia` floats into the right gutter and falls back inline at narrow widths (see the Component list in § cover). Superseded by the unified core — see `references/core-components.md`.


---

## holiday-identity

## Holiday Identity (v8.12 — Countdown and Field Guide only)

The Countdown and Field Guide formats use a **separate visual identity** from every other special edition. Where Deep Dive, Rewind, Versus, Season Review, Starter Kit, Shortlist, Next, and Lookahead all share the v8.21 editorial chrome (paper-and-ink grounds, persistent `.mast` bar, restrained editorial register), Countdown and Field Guide do not. The default chrome reads as "serious magazine"; holiday issues need to read as "trip scrapbook, building excitement."

**CSS layer:** `36-holiday-identity.css` (Tier 11). Loads only when `body.is-special[data-special="countdown"]` or `body.is-special[data-special="field-guide"]` is set. On every other format the file is dormant.

**What the layer changes vs default chrome:**

1. **No sticky chapter gate.** The 110vh black chapter-gate scroll-track is hidden on holiday issues. Structural rhythm is instead carried by two **halves** and one **transit intermission** between them (`.hol-transit`). Multi-venue trips get the full two-half treatment; single-venue Field Guides run as one half with a softer interior break (a tilted `.hol-marquee` between sections, not a full transit).
2. **No coral accent lockdown.** The default chrome restricts coral to chapter-gate numeral, D-day badge, and progress bar. Holiday issues do not use coral at all. The issue's identity accent is **brass** (`--hol-brass` / `--hol-brass-light`); ruby, rose, emerald, mustard, terracotta all run freely throughout.
3. **No ground discipline.** The default chrome neutralises component-level grounds inside chapters. Holiday issues encourage per-block grounds — a rotated polaroid on a brass card on a celestial-themed section.
4. **Type personality swap.** Default chrome uses Space Grotesk for chapter titles. Holiday issues use six type stacks simultaneously: Bowlby One (display-chunk), Cinzel italic (serif-display), Yellowtail (script-ornate), Caveat (script-note), Anton (display-tall), Alfa Slab One (display-slab). DM Sans body and Space Mono kicker are shared with default chrome. Each face does a specific job — see Type roles below.
5. **Ambient layer swap.** Default chrome ambient: chapter beads, sticky pin, page-fold, horizon. Holiday ambient: drifting clouds in dark heroes, kinetic marquees as section transitions, savannah silhouettes along Half II's bottom edge, optional fairytale tree silhouettes on celestial halves, star field across Half I.

**Structural beats (in order):**

1. `.hol-masthead` — narrow brand strip with format badge and T-minus meta. Replaces default masthead for holiday issues.
2. `.hol-cover` — full-bleed indigo poster with star field, drifting clouds, mega-numeral watermark, chunky title with mixed type, optional `.hol-countdown` live grid on the left, optional scrapbook collage on the right.
3. `.hol-kicker-strip` — cream-paper promise of the issue with double rule, chunky title + script subtitle on the left, mono meta on the right.
4. `.hol-half--one` — Half I body (Efteling default register: indigo + celestial backdrop + brass/rose/cream accents). Contains: stacked opener, content blocks (anchor, unmissable rows, marquee, don't-miss, polaroids, postcards), and closes seamlessly into the transit.
5. `.hol-transit` — the **only** structural break in the issue. Full-bleed 280px black band with mega kinetic typography watermarking each side and the divider card pinned centre. Single-venue issues omit this and replace it with a softer in-half break (`.hol-marquee` between sections).
6. `.hol-half--two` — Half II body (Beekse Bergen default register: terracotta + savannah silhouettes + mustard/bone/burnt accents). Same content blocks, completely different palette.
7. `.hol-meanwhile` — closing dark block with mega "MEANWHILE" / "SIGNAL" / "T-MINUS" watermark, brass title in chunky display, italic serif body. Adjacent rotated `.hol-subscribe` card.
8. `.hol-footer-row` — brand mark + mono links + hand-script tagline. Closes the issue.

**Type roles:**

| Face | Role | Examples |
|---|---|---|
| Bowlby One (`--hol-t-chunk`) | Mega display titles, big numbers, marquee text | Cover title, half titles in Half II, marquee bars, mega watermarks |
| Cinzel italic (`--hol-t-serif`) | Half I serif titles, italic pull-quotes, dek text | Half I opener title, anchor titles, unmissable titles |
| Yellowtail (`--hol-t-script`) | "Part One:" / "Don't Miss" / overline tags, hand-arrow notes | Cover overline, opener tags, transit hand-script, don't-miss kicker |
| Caveat (`--hol-t-hand`) | Polaroid captions, postcard backs, tagline endings, sticker text | Every handwritten caption in the issue |
| Anton (`--hol-t-tall`) | Tall display, transit names, postcard place labels, chalkboard items | "EFTELING" / "SAFARI" mega-watermark in transit |
| Alfa Slab One (`--hol-t-slab`) | Stamp inner text, big slab numerals where chunky is too round | Inside `.hol-stamp` b text |
| DM Sans (`--hol-t-body`) | All body copy | Same as default |
| Space Mono (`--hol-t-mono`) | Kickers, meta, ALL CAPS labels, stamps outer ring text | Mast meta, kicker-strip meta, stamp text, unmissable facts dt |

**Component vocabulary (full list, all prefixed `.hol-`):**

| Class | Role |
|---|---|
| `.hol-masthead` (`__title`, `__badge`, `__meta`) | Page-top brand strip |
| `.hol-cover` (`__inner`, `__sig`, `__overline`, `__title`, `__dek`, `__layout`, `__collage`, `__cloud`, `__back-num`, `__back-script`) | Full-bleed cover poster |
| `.hol-countdown` (`__grid`, `__cell`, `__num`, `__unit`, `__target`) | Live countdown digit grid. JS controller binds to `[data-cd]` cells; wrapper carries `data-target` ISO string |
| `.hol-kicker-strip` (`__inner`, `__title`, `__sub`, `__meta`) | Promise strip between cover and Half I |
| `.hol-half` + `.hol-half--one` / `--two` (`__inner`, `__opener`, `__opener-tag`, `__opener-title`, `__opener-subtitle`, `__opener-pills`) | Half section wrapper + stacked opener |
| `.hol-half--fairytale` | Optional ambient variant — Anton-Pieck tree silhouettes along the bottom of Half I |
| `.hol-transit` (`__side`, `__side--left`, `__side--right`, `__mega-bg`, `__label`, `__hand`, `__name`, `__center`, `__center-card`) | The single structural break between halves |
| `.hol-polaroid` (`__photo`, `__caption`, `__tape`) + `--right` / `--flat` | Rotated photo card with washi tape |
| `.hol-postcard` (`__front`, `__back`, `__greeting`, `__place`) | Greeting front + handwritten lined back |
| `.hol-stamp` + `--brass` / `--emerald` / `--mustard` | Circular rubber-stamp seal |
| `.hol-anchor` (`__photo`, `__title`, `__dek`, `__meta`, `__badge`, `__note`) | Feature article block with tilted border, rotated badge, hand-script note |
| `.hol-unmissable` + `--reverse` (`__photo-wrap`, `__photo`, `__card`, `__num-row`, `__num`, `__title`, `__quote`, `__why`, `__facts`) | Alternating left/right photo + parchment row. Use 6–10 per Field Guide; 5–7 per Countdown Top Attractions |
| `.hol-dont-miss` (`__kicker`, `__title`, `__list`) | Rotated ruby block with tilted shadow numerals |
| `.hol-marquee` (`__track`) | Kinetic horizontal scroll banner. Reduced-motion safe |
| `.hol-chalkboard` (`__tag`, `__title`, `__items`, `__row`, `__item`, `__price`, `__note`) | Half II tilted chalkboard menu card |
| `.hol-meanwhile` (`__giant-bg`, `__inner`, `__title`, `__body`) | Closing dark block |
| `.hol-subscribe` (`__inner`, `__title`, `__form`, `__input`, `__btn`, `__hand`) | Rotated subscribe card |
| `.hol-footer-row` (`__brand`, `__links`, `__tagline`) | Page-bottom brand mark + links + tagline |

**Activation:**
```html
<!-- Countdown -->
<body class="is-special" data-special="countdown">

<!-- Field Guide -->
<body class="is-special" data-special="field-guide">
```

No additional class is needed on the body. The default chrome's `body.is-special` activation still fires; tier 36's selectors disable the parts of default chrome that conflict and install the holiday vocabulary on top.

**Single-venue vs multi-venue:**
- **Multi-venue trip:** use both `.hol-half--one` and `.hol-half--two`, separated by one `.hol-transit`. The transit is the entire chapter-rhythm system for the issue. Half I covers the first venue; Half II covers the second.
- **Single-venue trip:** use only `.hol-half--one`. Replace the transit with one or two interior `.hol-marquee` breaks placed between major content groups (e.g. after Top Attractions, after Mood Board). The marquee functions as the softer in-half rhythm beat.

**What does NOT change vs the existing Countdown / Field Guide editorial specs:**

The editorial rules for Countdown and Field Guide (canonical chapter order, no-taste rule, hype-over-homework, 45/55 hype-to-practical, reader-profile invisibility, source diversity, image source rules, multi-venue balance check, access constraints, locked release-date register) all remain in force exactly as written. This layer is purely visual identity — content rules are unchanged.

**Compatibility with multi-venue theming (Tier 9, `33-countdown-destinations.css`):**

Tier 9 multi-venue theming and tier 11 holiday identity are independent. If a Countdown uses both:
- Tier 9 provides per-venue palette tokens (Efteling cream + plum + antique gold; Beekse warm sand + dark earth + terracotta) and the decorative venue glyph in the bottom-right corner.
- Tier 11 provides the cover, transit, half opener, ephemera vocabulary, and the type system.

The two layers compose cleanly: tier 9's venue palette can be used for the half ground, tier 11's component vocabulary for everything inside it. If a conflict arises (e.g. tier 9 sets a paper ground but tier 11 wants the indigo half-one register), the holiday half-register wins because tier 11 loads later in the cascade.

**Reduced-motion safety:**

Every animation in tier 36 (drift, marquee, flip-pop, hover-unrotate) is gated behind a `prefers-reduced-motion: reduce` override at the bottom of the file. Reduced-motion users see the same layouts with no motion.

---

### v8.13 — visual richness upgrade (May 2026)

v8.13 replaces three weak spots in the original Holiday Identity layer with the proven recipes from `signal-holiday.css`. Every change is **additive** unless explicitly noted — the v8.12 vocabulary continues to work, and existing planners that emit the old class names still produce valid output. The new components are opt-in extensions plus one breaking change to `.hol-half--two`'s ambient layer.

**1. Half II is now savannah cartography, not flat orange (BREAKING for `.hol-half--two`).**

The original `.hol-half--two` painted a flat terracotta ground with a mustard radial-dot grid and a small SVG silhouette band at the bottom. v8.13 replaces all three:

- **Ground:** gradient from `--hol-sand` (#ede1c8) at the top through `--hol-bone` (#f5ecd6) to a khaki dust tone at the bottom. Body text colour becomes `--hol-savannah-ink` (#1c2613) for legibility on the now-lighter ground.
- **Sun layer (`::before`):** conic sun-rays from the upper-right (`92% 8%`) plus a radial brass-orange sun disc. Reads as the savannah morning sun.
- **Silhouette band (`::after`):** the proven SVG band from `signal-holiday.css` — three giraffes at varying heights, three acacia trees, an elephant in mid-section, two grass tufts, and small bird scribbles. Tiled across the bottom 240px.

All Half II component overrides (anchor, opener, etc.) are repainted to work on the new light ground: bone-on-terracotta becomes savannah-ink-on-cream-sand, with burnt as the primary accent and mustard as the secondary. Writers and planners should **never** set `background:` on the `.hol-half--two` wrapper or on a chapter inside it.

**2. Optional atmospheric theme layers.**

Five new utility classes, each a single CSS pseudo-element with a tiled SVG. Stack ON TOP of a half (or any positioned section) for extra atmosphere on selected chapters. Each is static and repeating — paint cost is amortised by the browser image cache; identical across one page or thirty of scroll.

| Class | When to use | What it adds |
|---|---|---|
| `.theme-celestial` | Feature Half I chapters (the Top Wonders chapter, the Anchor chapter) | Richer starfield with constellation lines connecting stars + four-point sparkle stars |
| `.theme-fairytale` | Half I storybook chapters | Anton-Pieck silhouette band of gnarled trees along the bottom 220px with brass lantern dots |
| `.theme-flourish` | Half I chapter openers | Anton-Pieck brass filigree corner brackets (top-left + mirrored top-right) |
| `.theme-airships` | Half I Wonder Hotel / accommodation chapters | Line-drawn hot-air balloons drifting across the section |
| `.theme-tracks` | Half II safari chapters | Low-opacity terracotta paw/hoof print watermark across the section |
| `.theme-heat-haze` | Half II — ONE chapter per issue maximum | Subtle blurred shimmer ribbon at 32% height, 4s ease-in-out infinite alternate. The single moment of animation in Half II. |

Legacy alias: `.hol-half--fairytale` continues to work and produces the same tree-silhouette band. New writers should prefer `.theme-fairytale` (more composable).

**3. `.hol-wonders` editorial pattern (NEW component).**

A chapter-level component for ranked editorial picks (Field Guide Unmissables, Countdown Top Attractions). Each row is a rotated hero image with thick white border paired beside a parchment card carrying a numbered chip, serif italic pull-quote lede, and a tight Where/Why meta strip. Rows alternate sides via `.hol-wonder--reverse`. The component is designed to sit ON TOP of the indigo + starfield + storybook ground of `.hol-half--one` — the dark backdrop reads through between rows, making the parchment cards feel like illustrated plates pasted onto the night sky. The hover-unrotate on the photo is the only motion.

This sits alongside `.hol-unmissable` rather than replacing it. The two patterns serve different shapes: `.hol-unmissable` is the magazine-feature row with a long card, full quote attribution, and a four-row practical footer; `.hol-wonders` is the tighter editorial-list row with the numbered chip and a two-row Where/Why meta. Use `.hol-wonders` when the chapter is **ranked culinary or attraction wonders**; use `.hol-unmissable` when the chapter is the full Field Guide Unmissables pattern.

```html
<section class="hol-half hol-half--one theme-celestial theme-fairytale">
  <div class="hol-half__inner">
    <div class="hol-wonders">
      <div class="hol-wonders__intro">
        <h2>Top Ten Culinary Wonders</h2>
        <p>The unmissable flavours of Efteling</p>
      </div>
      <div class="hol-wonder">
        <div class="hol-wonder__photo" style="background-image:url('...');"></div>
        <div class="hol-wonder__card">
          <div class="hol-wonder__head">
            <span class="hol-wonder__num">01</span>
            <h3 class="hol-wonder__title">Pancakes at Polles Keuken</h3>
          </div>
          <p class="hol-wonder__quote">"Twelve little ones, butter, sugar — worth the queue every time." — r/Efteling</p>
          <dl class="hol-wonder__meta">
            <dt>Where</dt><dd>Polles Keuken, Fairytale Forest</dd>
            <dt>Why</dt><dd>Source convergence across Reddit, blogs, and TripAdvisor on the pancakes specifically.</dd>
          </dl>
        </div>
      </div>
      <div class="hol-wonder hol-wonder--reverse">...</div>
      <!-- alternate sides for every subsequent row -->
    </div>
  </div>
</section>
```

**4. Cover poster variant (NEW component).**

A 70s travel-brochure cover for Countdown and Field Guide issues. Activate by adding `.hol-cover--poster` to the existing `.hol-cover` element. The base `.hol-cover` treatment (cloud-drift indigo poster with collage on the right) is preserved for issues that want the scrapbook-collage feel; the poster variant replaces it with a silkscreen-print SVG illustration plate plus a centred title stack.

The illustration plate is a static SVG: midnight sky gradient, sunburst rays from the upper-right, big moon-with-face character, scattered round stars, four-point sparkle stars, distant ridge silhouette, offset-overprint castle silhouette in rose ghost + cream front with brass lit windows, floating clouds, water reflection, and shoreline trees. The plate is identical across Countdown and Field Guide — it reads as the fairytale night sky on both.

On top of the plate sit, in order:
- `.hol-cover__sig` — the meta strip (brand + issue + kicker)
- `.hol-cover__arch` — SVG text-on-path arc (e.g. "★ GREETINGS FROM ★" for Countdown, "★ EAT YOUR WAY THROUGH ★" for Field Guide)
- `.hol-cover__title` with a `.hol-cover__title--print` inner span — chunky Bowlby One with a hard offset shadow in `--hol-ruby` that reads as misregistered screen-print
- `.hol-cover__sub` — Yellowtail subtitle, slightly tilted
- `.hol-cover__deck` — three-pill mono row with star dividers (date · gates · family-of-four, etc.)
- `.hol-countdown` — the existing live digit grid, pinned at the bottom of the stack

Template part: `assets/template-parts/03-cover-poster.html`. The full SVG plate plus the stack scaffold is embedded — writers paste it verbatim and fill the bracketed placeholders.

**5. Letterpress titles on Half II.**

The Half II opener title now uses `text-shadow: 6px 6px 0 var(--hol-burnt)` for a letterpress / poster-print feel instead of the original drop-shadow. This is a single-line change but it lands every chapter title in the savannah half as a hand-printed poster.

**Pre-flight regressions added in v8.13:**
- **RT-14:** Flat-fill ground on Half II is banned. Let `.hol-half--two` paint its own ground; don't set `background:` on the wrapper or on inner sections.
- **RT-15:** Venue/half mismatch is banned. Every Efteling chapter sits in `.hol-half--one`; every Beekse Bergen chapter sits in `.hol-half--two`. Cross-venue chapters live outside both halves (after the cover, or as the transit body).


