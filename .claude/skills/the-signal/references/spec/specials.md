# Spec slice — specials

_This file consolidates the specials/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Content-first contract (non-negotiable)
Every motion component below obeys these rules. Never ship a special edition that violates any of them:
- **No scroll hijacking, ever.** Native scroll speed and direction are untouched.
- **No motion on body copy.** Only chrome, openers, and decorative layers animate. Prose is always static.
- **Stagger reveals cap at 400ms total.** Word-level reveals use 40ms delays and stop after ~10 words.
- **`prefers-reduced-motion` disables every decorative animation.** The controller short-circuits after the splash cleanup.
- **JS-off still renders a complete issue.** All motion is additive — the issue must be fully readable with scripts disabled.
- **Word counts and section depth are not reduced to make room for motion.** Motion sits around content, not in place of it.
- **Format-variable intensity.** Countdown / Versus / Rewind go loud. Deep Dive / Blueprint / Field Guide stay quiet (splash + ticker + manifesto only).



---

## cover

### Authoring a special edition
1. On `<body>`, add `is-special` and `data-special="<format>"` where format is one of: `countdown`, `rewind`, `versus`, `season-review`, `deep-dive`, `blueprint`, `starter-kit`, `shortlist`, `field-guide`.
2. **For Countdown only:** add `data-dday-start="N"` on `<body>` where N is the number of days between the issue date (today, when generating) and the event. The D-day badge displays this authored value statically — a magazine issue is a snapshot and the badge must agree with the prose, forever. Compute N at generation time as `(trip_date - today)` in days. The Countdown auto-trigger fires 2-3 weeks before a trip, so N is typically 14-21. If generating a prototype or back-dated issue, use the fictional issue-date reference. (Optional: also add `data-trip-date="YYYY-MM-DD"` for human reference, but it does NOT drive a live countdown at runtime.) The previous scroll-scrubbing pattern (`data-dday-start` + `data-dday-end` interpolated by scroll percentage) has been removed — a scroll-driven countdown is nonsensical.
3. Include the components from the component list below as appropriate for the format. Each component has a documented HTML contract in `component-contracts.md` (or inline in the CSS).
4. Inject assets with `scripts/inject-assets.sh` as normal.


### Component list
**Chrome (tier 1 — all special editions):**
- `.sp-splash` — full-bleed pre-roll wash with format glyph, self-dismisses after 2.2s
- `.mast-ticker` — horizontal marquee masthead replacing the static masthead
- `.sp-format-badge` — rotated ◆ format label, fixed top-right
- `.sp-footer-card` with arc notch + ◆ seal — closing card

**Scroll motion (tier 2 — loud formats):**
- `.sp-parallax` with `.p-bg` / `.p-mid` / `.p-fg` layers — layered parallax on hero and section openers
- `.sp-stagger` with `.sp-word` children — word-by-word reveal on h2 openers (400ms cap)
- `.sp-wipe` with three `.sp-wipe-layer` children (l1/l2/l3) — contained colour-wipe transitions between sections. The wipe container is `overflow: hidden` and `contain: layout paint` — it never extends past content width and cannot push surrounding columns during transition.
- `.sp-dday` — Countdown-only live days-to-go badge, top-left, reads `data-trip-date` from `<body>`, does NOT scrub with scroll

**Layout breakouts (tier 3 — loud formats):**
- `.sp-manifesto` — oversized foreword
- `.sp-bignum` — full-width statement number
- `.sp-gallery` — broken editorial gallery
- `.sp-diptych` — split-screen contrast layout
- `.sp-marquee` — source-strip marquee at end of issue

**Cover kinetic (opt-in):**
- `.cover-kinetic` with `.k-bold` / `.k-italic` / `.k-outline` — three overlapping title layers that collide on arrival

**Body-embedded components (tier 4 — inside article sections, not between them):**
- `.sp-scroll-image` (+ `.is-fullbleed` variant) — hero image that can drop into any section mid-article. Image has subtle parallax (±20px) within its frame as it scrolls through viewport. Supports `<figcaption>` with `<cite>` for credit.
- `.sp-inline-figure` (+ `.is-left` / default right) — half-width floating figure alongside body copy. Reveals with fade + 20px slide when scrolled into view. Collapses to full-width at ≤820px.
- `.sp-image-strip` with `.sp-strip-track` — 3-image horizontal strip that drifts sideways as the page scrolls vertically. Echoes the landonorris.com horizontal-in-vertical motion.
- `.sp-pullquote-huge` — oversized full-column italic pull quote with ornamental quote mark, top+bottom rules. Breaks up long prose blocks. Contains `<p>` and optional `<cite>`.
- `.sp-number` (inline) and `.sp-number-block` / `.sp-number-huge` (block) — count-up stat callouts. Add `data-to="N"` (with optional comma formatting) to trigger the animation when scrolled into view. Can be used inline in prose: `<span class="sp-number" data-to="74">74</span>`.
- `.sp-marginalia` (with `data-side="left|right"`) — fact/stat chip that floats in from the margin. Parent must be `position: relative` (all sections already are). Falls back to inline breakout at ≤1200px.
- `.sp-kicker` — class for h3/h4 sub-headings inside long articles. Reveals with 10px slide + fade when entering view. Keeps body reading flow intact.
- `.sp-image-quote` — photo with overlaid italic pull quote. For "what people say about X" breakouts. Image is darkened (brightness 0.55) so text sits over it cleanly.
- `.sp-curtain` with `.sp-curtain-panel` — vertical curtain-drop transition between sections. Half the height of `.sp-wipe` (60px). Drops, then retracts 700ms later. Use sparingly for rhythm variety.
- `.sp-chapter-number` with `.sp-chapter-num` + `.sp-chapter-label` — oversized roman/arabic numeral that precedes a long section. Adds typographic weight without needing imagery. Good opener for internal chapters.




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
| Starter Kit | Getting into Malazan, Specialty coffee from scratch, Fantasy Premier League for beginners, Home kettlebell training, Starting on Etsy |
| Deep Dive | The history of a favourite game franchise, A deep look at a training methodology, The state of e-readers in 2026, Serie A tactical evolution |
| Versus | V60 vs AeroPress, Two fitness approaches, Two e-readers, Two budget tablets |
| Blueprint | Home gym next phase, 10k training plan options, Etsy store growth paths |

**The editorial picks pool ensures there's always a viable special available.** The editor selects the most timely or interesting option from the pool. Over time, used topics are tracked in the state file to avoid repeats.

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

### Chapter gate (MANDATORY for every chapter on every special edition — v8.5, sticky scroll model)

**The chapter gate is the single most important element in a special edition.** It is the digital equivalent of turning a page in a real magazine — a viewport-locking moment that unambiguously says *"a new chapter starts here"*. It is the permanent, unmissable signal the reader can spot at any scroll speed.

**Mandatory on:** every `[data-sp-chapter]` in every special edition. If a chapter does not open with `.sp-chapter-gate`, the issue fails Gate 2.

**Structure:**
```
<aside class="sp-chapter-gate"
       data-chapter-num="V"
       data-chapter-title="BEEKSE BERGEN"
       data-chapter-arc="Act III — the wild">
  <p class="scg-deck">Five days inside Europe's largest safari park, and a hotel where the lions wake you up.</p>
</aside>
```
Place the gate **immediately before** the chapter section's opening `<section data-sp-chapter="…">` tag. The controller auto-builds the black panel and drives the scroll-progress reveal.

**How it behaves (v8.5 sticky scroll model):**
- The gate is a 160vh scroll track containing a `position: sticky` full-bleed black panel (`#0A0E17`) that locks to the viewport for ~1 screen-height of scroll.
- As the reader scrolls *through* the gate, a `--scg-progress` CSS variable runs 0 → 1. The four text layers are revealed in sequence:
  - **0.10 → 0.30** arc label fades in
  - **0.25 → 0.55** Roman numeral scales + fades in (coral)
  - **0.45 → 0.70** chapter title fades in (reserved typeface)
  - **0.65 → 0.88** deck line fades in (italic, on the black)
- When scroll passes the end of the track, the panel unsticks and the next chapter is revealed underneath.
- **No cream "breath" zones before or after.** The previous chapter butts straight up against the black cover; the next chapter appears straight out of it. The pause is *time* (scroll-hold), not *whitespace*.
- **Reduced-motion / no-JS fallback:** panel collapses to a static full-bleed black band (~52vh) with all four text layers fully visible. No sticky, no progress driver. Same visual anchor, no motion.

**Four text layers, all live inside the black panel (v8.5):**
1. **Arc label** — italic, small, muted bone (e.g. "Act III — the wild")
2. **Roman numeral** — display size (72–180px), coral, reserved typeface
3. **Chapter title** — medium, letter-spaced caps, bone, reserved typeface
4. **Deck line** — italic, dim bone, one sentence (mandatory)

**Three elements reserved exclusively for the gate (never used elsewhere):**
1. The **full-bleed black panel** (`.scg-strip`). If you see one, it means "new chapter". Nothing else in the magazine uses this.
2. The **chapter-title typeface** (`var(--sp-chapter-ff)` — Space Grotesk). Banned from pull-quotes, kickers, stats, sidebars, covers, navigators.
3. **Display-size Roman numerals** (72–180px). The wax seal's small ornamental numeral is the only other Roman numeral permitted.

**Required attributes:**
- `data-chapter-num` — Roman numeral (I, II, III…). Required.
- `data-chapter-title` — chapter name in CAPS (e.g. `BEEKSE BERGEN`). Required.
- `data-chapter-arc` — the narrative-arc label. Required on Countdown, Deep Dive, Rewind, Season Review. Optional on Versus / Starter Kit / Blueprint / Shortlist / Field Guide.
- `<p class="scg-deck">…</p>` — **mandatory one-line deck**. A sentence that tells the reader *what this chapter will do for them*. Not a subtitle, not a description — a promise. See deck-writing rules below.

**The deck line — what makes it good:**
- One sentence. Italic. Max ~20 words.
- Answers: *"why should I read this chapter?"* not *"what is this chapter?"*
- Concrete, not abstract. "Five days inside Europe's largest safari park" > "An overview of our stay".
- Never restates the chapter title.

**Examples (good):**
- *By the Numbers* → "The trip in eleven figures — before the prose starts."
- *Logistics* → "Everything you need to stop thinking about once you land."
- *Facts & Folklore* → "The stories the locals tell, and the ones the guidebooks don't."
- *Wonder Hotel* → "Sleeping inside the fairy tale — what two nights in room 312 is really like."
- *Mood Board* → "Five images that tell you what a week here actually looks like."

**Narrative-arc labels (required on long-form specials):**
- **Countdown** (typically 9–11 chapters): Act I (hype setup — By the Numbers, Event in Depth) → Act II (centrepiece hype — Top Attractions, Accommodation, Mood Board) → Act III (softer hype — What to Watch/Read/Play, Five Moments Worth the Trip) → Coda (Before You Go: compressed logistics + surprising facts + On the Radar)
- **Deep Dive** (8–10 chapters): Premise → Evidence I → Evidence II → Counterargument → Verdict
- **Rewind** (chronological): Year-by-year or phase-by-phase labels
- **Season Review**: Opening Acts → Mid-Season → Finale → Verdict
Map every chapter to its arc beat and put the label in `data-chapter-arc`. This is how the reader keeps orientation through ten chapters.



---

## imagery-budget

### Imagery budget — MANDATORY for loud special editions

A Countdown / Versus / Rewind issue **must not** have entire sections that are walls of text. The previous pattern (front-loaded imagery in the opening then plain prose for the rest) is banned. Apply the following rule at generation time:

**Every major body section (Foreword excepted) must include at least ONE of:**
- A `.sp-scroll-image`, `.sp-inline-figure`, `.sp-image-quote`, or `.sp-image-strip` (imagery)
- A `.sp-number-block`, `.sp-pullquote-huge`, `.sp-bignum`, or `.sp-chapter-number` (high-impact typographic component)
- A `.sp-gallery` or `.sp-diptych` (multi-image layout)

**In addition, across the whole issue:**
- At least **2 sections** use a multi-image component (gallery, diptych, or image-strip)
- At least **3 sections** use `.sp-scroll-image` or `.sp-inline-figure` for embedded imagery
- At least **2 sections** use `.sp-pullquote-huge` to break up prose
- Long prose sections (>500 words) include `.sp-kicker` on h3/h4 headings
- Long prose sections include at least one `.sp-marginalia` or inline `.sp-number` callout
- Section transitions alternate between `.sp-wipe` and `.sp-curtain` for rhythm variety — don't use the same transition twice in a row

These are minimums — more is fine. Research images for EVERY major section, not just the cover topic.



---

## editorial-body-kit

### Editorial body kit — MANDATORY rules for loud special editions

The tier-4 imagery budget addresses *what's in* each chapter. The tier-5 editorial body kit addresses *how each chapter is structured*. Both apply.

**Per-chapter:**
- Every chapter wrapper carries `.sp-ground-paper` or `.sp-ground-ink`. Chapters alternate ground value — never two paper chapters in a row, never two ink chapters in a row. The shift IS the transition; this replaces the need for a `.sp-wipe` or `.sp-curtain` between alternating-ground chapters (use those between same-ground chapters or for rhythm variety only).
- Every chapter opens with a `.sp-chapter-chrome` strip carrying its roman numeral, name, and slug.
- Every chapter contains at least one `.sp-folio` watermark for typographic depth.
- Any chapter ≥800 words MUST use a `.sp-spread` layout (rail + body + margin). Shorter chapters may use a single-column body but still need at least one `.sp-brief`, `.sp-hero-quote`, or `.sp-dash` mid-prose.
- Every chapter ends with a `.sp-signoff` line.

**Across the issue:**
- At least 1 `.sp-pull-break` for a major rhythm break (typically between the second and third chapter)
- At least 1 `.sp-bridger` interlude inside a long chapter
- At least 1 `.sp-dash` instead of an italicised list of stats anywhere stats are presented
- Section headings inside `.sp-spread-body` use the `§` section mark automatically (built into the CSS)
- First paragraph of each `.sp-spread-body` gets a 110px italic accent drop cap automatically (built into the CSS) — do not manually wrap the first letter


### Editorial motion layer (tier 5.5) — MANDATORY for loud special editions

The tier-5 body kit gives the magazine its structure. The tier-5.5 motion layer (in `28-special-motion-editorial.css` + matching JS controllers in `assets/script.js`) gives it kinetic life. Inspired by adapted motion vocabulary from landonorris.com (wipe-band reveals, scroll drift, staggered entries) — translated into editorial idiom. **Most of it is automatic** — applied by the JS controllers on scroll. A few patterns require explicit class application.

**Automatic — no markup changes required:**
- `.sp-folio` watermarks drift ±60px on scroll (subtle parallax, via `--sp-folio-y`)
- `.sp-chapter-chrome` opens with a sequenced wipe (numeral → hair → name → slug, staggered)
- `.sp-dash-cell`s stagger in 90ms apart
- `.sp-tl-row`s stagger in down the timeline
- `.sp-hero-quote` lifts in with the corner glyph drifting in opposite direction
- `.sp-brief` slides in with its accent rule scaling vertically from 0
- `.sp-pull-break` corner quote marks scale in from opposite corners
- `.sp-bridger` three columns enter staggered
- `.sp-spread` rail and margin slide in from opposite sides as body fades up
- `.sp-spread-body` first letter (drop cap) pops in with a slight scale
- `.sp-signoff` scale-in finale
- `.sp-caption-strip` hairline rule draws across
- All in-prose `<a>` links get an underline-draw on hover (background-size 0% → 100%)
- Native `scroll-behavior: smooth` on the document
- Ground-seam accent hairline appears between alternating-ground chapters
- Paper-bg components (`.sp-brief`, `.sp-hero-quote`, `.sp-bridger`, `.sp-margin`) automatically lock to ink text colour even when nested in `.sp-ground-ink` chapters (readability lock — no need to add `.sp-island` manually)

**Explicit class application — REQUIRED on loud specials:**
- **`.sp-band`** is THE signature move (the Lando wipe-band reveal). Every chapter chrome's `.sp-eyebrow` and `.sp-chapter-name` MUST carry `.sp-band`. Every `.sp-signoff` label MUST carry `.sp-band`. Every standalone `.sp-eyebrow` kicker above a major component title gets `.sp-band`. The JS auto-wraps the inner text into `.sp-band-t` on the first observation.
- **`.sp-band sp-band-thin`** — lighter underline-sweep variant. Apply to dashboard `.sp-dash-hint` kickers and caption-strip eyebrows where you want the sweep without hiding the text.
- **`.sp-spine`** — decorative inline SVG hairline that draws itself in (`stroke-dashoffset` animation) when scrolled into view. Add 1-2 per long chapter inside the `.sp-margin` column or `.sp-rail` to add typographic depth without weight. Pattern: `<svg class="sp-spine" viewBox="0 0 2 200"><path d="M1 0 V200" /></svg>` (or a curve). Lives decoratively in the margins, never near body text.

**Reduced-motion:** All tier-5.5 motion is wrapped in a `@media (prefers-reduced-motion: reduce)` kill switch — animations collapse to instant, transforms reset, decorative drift disabled. Content-readable state always reachable without motion.




---

## signature-moments

### Signature moments — ONE per format (mandatory)

Each special edition format has exactly one signature moment — a single visual element readers will remember and describe to someone else. They are not interchangeable. Including a Countdown's hourglass in a Versus issue would dilute both. Use the prescribed component for the format and no other.

| Format | Component | Where it lives | Required content hook |
|---|---|---|---|
| Countdown | `.sp-sand-clock` | Cover, below masthead | `data-total="<days>" data-remaining="<days>"` on the wrapper |
| Rewind | `.sp-memory-wall` | Fixed right gutter (desktop), strip above sections (mobile) | One `<div class="mw-cell" data-item-id="…" style="background-image:url(…)">` per item; each prose section gets `data-reveals="id1,id2"` |
| Versus | `.sp-fault-line` | Sticky vertical line spanning all comparison sections | `data-max-shift="90"` on the line; each paragraph in the comparison `<p data-lean="-2"…+2>`; verdict element `data-verdict="a"\|"b"` |
| Season Review | `.sp-form-tape` | Top of the issue + repeated at top of each chapter | Each chapter `<section data-results="W,W,D,L,W" data-result-from="0">…</section>`; tape pre-renders one `.ft-pill` per fixture |
| Deep Dive | `.sp-thread-pull` | Fixed left margin (desktops ≥ 1100px only) | Wrapper element `[data-tp-track]` defines the scroll range; markers `<g class="tp-marker" data-at="0.42">…</g>` inside the SVG carry concept-tag text |
| Blueprint | `.sp-build-meter` | Sticky top of viewport, below masthead | One `.bm-cell` per phase in the meter; each phase section `<section data-phase="0">…</section>` |
| Starter Kit | `.sp-cold-start` | Cover/opener, gates the prose | One word, split into `<span class="cs-letter">K</span>` per letter. Wrap the rest of the issue in `.sp-cs-after` |
| Shortlist | `.sp-deck-reveal` | Mid-issue picks block | A `.sp-deck` with one `.dk-card` per pick (#1 first / on top); scroll triggers `<div data-deck-step="1">…</div>` peel cards |
| Field Guide | `.sp-pinboard` | Cover/opener (sticky 100vh) | A `.sp-pinboard` with `.pb-stage` background image + `.pb-pin`/`.pb-label` pairs (`--x:38%; --y:52%`); prose sections referring to a pin add `data-pin-id="<id>"` to trigger pulse |

**Authoring rules:**
- Pick the right one for the format. One per issue. Don't mix.
- Always provide the data hook listed above; without it, the component renders inert (which is the safe fallback).
- All nine moments degrade gracefully under `prefers-reduced-motion` and on missing JS.
- **Mobile gating:** `sp-thread-pull` hides below 1100px; `sp-memory-wall` collapses to a horizontal strip below 900px; everything else adapts.
- **No content sacrificed.** If the moment doesn't fit the issue's content shape (e.g. a Versus issue with no clear A/B paragraphs), skip the moment rather than force the structure.



---

## chapter-transitions

### Chapter transitions + ambient (format-agnostic)

These components compose with the existing `.sp-wipe`, `.sp-curtain`, ground alternation, and chrome — they are punctuation, not replacements. Available to every special edition format.

**Transitions (use sparingly — these create a deliberate reading pause):**

- **`.sp-stat-curtain`** — full-viewport overlay rises with one hero stat or epigraph, then retracts. Use at **most twice per issue** at moments where a hard pause is editorially earned (chapter break before the centrepiece, before the verdict). Markup: `<div class="sp-stat-curtain" id="sc-1"><p class="scu-stat">23,400</p><p class="scu-caption">Roller-coaster runs in 2025</p></div>` plus a trigger `<div data-curtain-for="sc-1"></div>` placed at the chapter end where it should fire.
- **`.sp-page-fold`** — bottom 40vh folds upward via 3D rotateX. Use **only at paper↔ink chapter handoffs** to dramatise the ground swap. Markup: wrap the boundary in `<div class="sp-page-fold-wrap"><div class="sp-page-fold" style="--sp-ground-prev: var(--sp-paper);"></div><div class="sp-page-fold-shadow"></div></div>`. Set `--sp-ground-prev` to the outgoing chapter's ground colour token. Maximum 2 per issue.

**Ambient (these run continuously and become part of the issue's atmosphere):**

- **`.sp-chapter-beads`** — fixed right-gutter bead strip, one per chapter, with within-chapter progress connector. **Universal: works on standard weekly AND every special edition.** Markup: a single `<aside class="sp-chapter-beads" aria-hidden="true"></aside>` near the end of `<body>` (already included in `template-parts/19-closing.html`). **Chapter discovery order:** (1) elements with `[data-sp-chapter]` — typical for specials; (2) fallback to `.mag > section.sec` — used by every standard-weekly section. **Title resolution:** `[data-sp-chapter-title]` → first `<h2>` text → section `id` (title-cased) → `Chapter N`. Accent colour auto-cascades: `--sp-accent` on specials, `--accent` on standards. **Mobile (≤ 820px):** collapses to a thin vertical line with no labels. Click a bead to scroll to that chapter.
- **`.sp-horizon`** — bottom-edge strip bleeds the next chapter's ground colour upward as within-chapter progress nears 100%. Markup: a single `<div class="sp-horizon" aria-hidden="true"></div>` near the end of `<body>`. Each chapter element must carry `data-sp-chapter` AND `data-sp-ground-color="#hex"` so the next chapter's colour is known.

**Authoring contract for ambient:**
- Both ambient components share the same per-chapter progress calculation (one rAF loop, zero duplicated work). Adding `.sp-horizon` for free if you've already added `.sp-chapter-beads`.
- Both require chapters to be marked with `data-sp-chapter` on the section root and `data-sp-chapter-title` for tooltips (specials). **Standard editions need no mark-up** — beads auto-discover from `<section class="sec">`. `data-sp-ground-color` is required only if you use `.sp-horizon` (special editions only).
- Reduced-motion: beads stay (active state only, no fill animation); horizon collapses to a static 2vh strip near chapter end.



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


> See `formats/countdown.md` for the full hype-chapter spec. This file is a cross-format summary.

**Hype-chapter visuals** are opt-in CSS modifiers (`32-hype-variants.css`) that dial back default special-edition chrome on chapters where excitement — not literary depth — is the job.

## When to use hype modifiers

Apply on:
- Countdown hype chapters: Top Attractions, Accommodation, Mood Board, Five Moments Worth the Trip, By the Numbers (when image-led)
- Field Guide: The Opening, The Unmissables

**Never apply on literary formats:** Deep Dive, Versus, Rewind, Season Review — these keep full default chrome.

## The four modifiers

1. **`.sp-chapter-gate.is-hype`** — compact gate: 60vh track (vs 110vh), 40vh hold (vs 100vh), layers solid by progress 0.08 (vs 0.20)
2. **`[data-sp-chapter].is-hype`** — re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, `.why-its-here`. All global lockdown elements unchanged.
3. **`.sp-ground-gallery`** — neutral slate ground (#1A1E27) for image-first chapters (Mood Board primary, optionally Field Guide Opening). NOT pitch black.
4. **`.unmissables` / `.unmissable`** — Field Guide Unmissables pattern: 6-10 full-width editorial beats, each = hero image + sensory prose + "Why It's Here" coral kicker + mono `<dl>` practical footer. Drop-cap forbidden on picks.


---

## readability-locks


**CSS layer:** `34-readability-locks.css` (Tier 10, runs last in cascade).

Some self-painting components lose identity when nested inside `[data-sp-chapter]` because Tier 7's ground-discipline lockdown is over-aggressive. This layer re-locks each component to a fixed background+text pair regardless of the chapter ground above it.

| Component | Lock |
|---|---|
| `.sp-marginalia` | Always cream-bg + ink-text |
| `.sp-pull-break` | Always dark-bg + bone-text |
| `.sp-pullquote-huge` text | Set explicitly per chapter ground |

**Why this matters for writers:** if you use these components in the markup (which you should, per pre-flight.md), the CSS will handle contrast automatically. You do NOT need to add inline styles or ground overrides. Just use the canonical markup and the lock layer handles it.

**Markup contracts (Gate 1E):** the lockdown only works when markup matches the contract. See `global/04-markup-contracts.md` and `references/pre-flight.md` § Canonical markup snippets.


---

## portrait-spread


**CSS:** `26-special-editorial.css`. The three-column `.sp-spread` layout adapts at ≤980px.

## Portrait behaviour

At ≤ 980px, `.sp-spread` becomes `display: flow-root; position: relative`.

- **Rail** (`.sp-rail`): `position: absolute; top:0; bottom:0; left:0; width: 60/44px` — runs full spread height as decorative chapter-side chrome.
- **Margin aside** (`.sp-margin`): reparented via the portrait-spread-reparenter IIFE in `script.js` to be first child of `.sp-spread-body`; floats right (190/128px) with `shape-outside: margin-box`. Body is `flow-root` with left padding (78/58px) to clear the rail. Prose flows around the margin and reclaims full reading width once it ends.
- **Ink grounds**: the margin paints a solid paper-tinted background so ink-on-paper text stays legible.

## Markup contract

```html
<div class="sp-spread">
  <div class="sp-rail" aria-hidden="true"></div>
  <aside class="sp-margin">
    <!-- marginalia content -->
  </aside>
  <div class="sp-spread-body">
    <!-- prose, drop cap on first <p> -->
  </div>
</div>
```

**Never stack:** portrait is the canonical read. The three-column desktop layout is a bonus, not the target.


---

## holiday-identity

## Holiday Identity (v8.12 — Countdown and Field Guide only)

The Countdown and Field Guide formats use a **separate visual identity** from every other special edition. Where Deep Dive, Rewind, Versus, Season Review, Blueprint, Starter Kit, and Shortlist all share the default special-edition chrome (sticky chapter gate, paper/ink grounds, coral lockdown, restrained editorial register), Countdown and Field Guide do not. The default chrome reads as "serious magazine"; holiday issues need to read as "trip scrapbook, building excitement."

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


