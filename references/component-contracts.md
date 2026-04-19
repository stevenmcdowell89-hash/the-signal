# Component Contracts — Required Patterns

This is the law. Every class used in an issue must be listed here or visible in `assets/weekly-template.html`. If it's not here, it doesn't exist. Do not invent or reuse classes from prior issues. This file supersedes any memory of older prototypes.

Every HTML snippet below is pulled directly from the template or verified against `assets/styles.css`. Before adding any class to an issue that is not listed here, grep `styles.css` for it first. If it does not exist in the CSS, do not use it.

Two fonts only: **Fraunces** (display and body serif) and **Geist** (sans-serif). No other typefaces. No inline `style="font-family: ..."` anywhere.

---

## Universal Components

---

### Masthead (`.mast`)

Fixed-position, always present in every issue. Three-column grid. Mix-blend-mode: difference (inverts over light/dark content). The time "06:40" is literal and never changes. Issue number and date update per issue.

```html
<header class="mast" role="banner">
  <div class="mast__left">
    <span class="mast__dot" aria-hidden="true"></span>
    <span class="mast__left-text">
      <span>· THE SIGNAL</span>
      <span class="sub">A Sunday magazine</span>
    </span>
  </div>
  <div class="mast__centre">The Signal · Sunday</div>
  <div class="mast__right">
    <div class="line1">SUNDAY 06:40 · NO. [ISSUE_NUMBER] · [DD MONTH]</div>
    <div class="line2">MMXXVI</div>
  </div>
</header>
```

Classes verified: `.mast`, `.mast__left`, `.mast__dot`, `.mast__left-text`, `.mast__centre`, `.mast__right`, `.line1`, `.line2`.

---

### Cover (`.cover`)

Full-bleed dark section. Always first. No section `class="sec"` wrapper — Cover uses `.cover` directly.

```html
<section class="cover" data-section="cover">
  <div class="cover__hero parallax">
    <img src="[COVER_IMAGE_URL]" alt="[COVER_IMAGE_ALT]">
  </div>
  <div class="cover__scrim" aria-hidden="true"></div>
  <div class="cover__ambient" aria-hidden="true"></div>

  <div class="dispatch-seal"
       data-num="[ISSUE_NUMBER]"
       data-month="[MONTH]"
       data-year="MMXXVI"
       aria-hidden="true"></div>

  <div class="cover__meta-top">
    <span>SUNDAY MAGAZINE · NO. [ISSUE_NUMBER]</span>
    <span>[DD MONTH] MMXXVI</span>
  </div>

  <div class="cover__body">
    <div class="cover__eyebrow eyebrow--wide">THIS WEEK'S LEAD</div>
    <h1 class="cover__headline ln">
      [HEADLINE_LINE_1]<br>
      [HEADLINE_<em>ACCENT_WORD</em>]<br>
      [HEADLINE_LINE_3]
    </h1>
    <p class="cover__dek">[DEK — 1–2 sentences, italic display.]</p>
  </div>

  <div class="cover__meta-bottom">
    <div class="cover__tags">
      <span class="cover__tag cover__tag--accent">[PRIMARY_TAG]</span>
      <span class="cover__tag">[TAG_2]</span>
      <span class="cover__tag">[TAG_3]</span>
    </div>
    <div class="cover__scroll-hint" aria-hidden="true">SCROLL</div>
  </div>
</section>
```

Classes verified: `.cover`, `.cover__hero`, `.parallax`, `.cover__scrim`, `.cover__ambient`, `.dispatch-seal`, `.cover__meta-top`, `.cover__body`, `.cover__eyebrow`, `.eyebrow--wide`, `.cover__headline`, `.ln`, `.cover__dek`, `.cover__meta-bottom`, `.cover__tags`, `.cover__tag`, `.cover__tag--accent`, `.cover__scroll-hint`.

**Rules:**
- `.parallax` goes on the `div.cover__hero` container, not on the `<img>` itself.
- `<em>` wraps exactly one key word in the headline.
- The `.dispatch-seal` here is one of exactly two allowed instances (the other is in the Colophon).
- `.cover__ambient` is always `aria-hidden="true"`.

---

### Section Wrapper (`.sec`)

Every section after the Cover uses `.sec` with either `.dark` or `.paper`. Never both. Optional `data-scheme` and `data-accent` attributes on the section element override the palette for that section only.

```html
<!-- Paper section (default for most rotating sections) -->
<section class="sec paper" data-section="[NAME]" data-scheme="ember">
  <span class="gutter-mark gutter-mark--tl"></span>
  <span class="gutter-mark gutter-mark--tr"></span>
  <span class="gutter-mark gutter-mark--bl"></span>
  <span class="spine-label">· [NUM] · [SECTION NAME]</span>
  <!-- section content -->
  <span class="folio-watermark" aria-hidden="true">[NUM]</span>
</section>

<!-- Dark section -->
<section class="sec dark" data-section="[NAME]" data-scheme="ember">
  <span class="spine-label">· [NUM] · [SECTION NAME]</span>
  <!-- section content -->
</section>

<!-- Dossier scheme override (Workshop, History) -->
<section class="sec dark" data-section="workshop" data-scheme="dossier" style="--accent:#b8902a;">
  <!-- content -->
</section>

<!-- Accent sub-variant (Itinerary) -->
<section class="sec paper" data-section="itinerary" data-accent="cool" data-scheme="ember">
  <!-- content -->
</section>
```

**Gutter marks** (decorative corner marks — paper sections only): `.gutter-mark.gutter-mark--tl`, `.gutter-mark.gutter-mark--tr`, `.gutter-mark.gutter-mark--bl`.

**Spine label:** `.spine-label` — a vertically-running label on the left edge. Content: `· [NUM] · [SECTION NAME]`. For right-aligned variant: add `.spine-label--right`.

**Folio watermark:** `.folio-watermark` — a large semi-transparent section number in the corner. Used in The Lead (`1`) and Rabbit Hole (`?`).

Classes verified: `.sec`, `.dark`, `.paper`, `.gutter-mark`, `.gutter-mark--tl`, `.gutter-mark--tr`, `.gutter-mark--bl`, `.spine-label`, `.spine-label--right`, `.folio-watermark`.

---

### Section Eyebrow (`.section-eyebrow`)

Appears near the top of every section, below the spine label and before the section head. Two spans: a section label on the left and a category/number on the right.

```html
<div class="section-eyebrow reveal">
  <span>01 — The Lead</span>
  <span class="section-eyebrow__num">World</span>
</div>
```

Classes verified: `.section-eyebrow`, `.section-eyebrow__num`.

---

### Feature Band (`.feature-band`)

The primary long-form layout component. Used in The Lead, The Workshop, The Rabbit Hole, and optionally The Long Game. Always contains a `.feature-band__rail` (vertical section number + label on the left edge), a `.feature-band__body` (main prose), and optionally a `.feature-band__margin` (image + supporting cards) or a full `aside.marginalia`.

```html
<!-- Feature band with marginalia (Lead, Rabbit Hole) -->
<div class="feature-band feature-band--with-marginalia reveal">
  <div class="feature-band__rail">
    <span class="feature-band__rail-num">01</span>
    <span class="feature-band__rail-label">THE LEAD · WORLD</span>
  </div>

  <div class="feature-band__body lead">
    <p class="body-lead">
      <span class="dropcap">L</span>[Opening sentence with <em>italic accent</em>.]
    </p>
    <p>[Body paragraph.]</p>
    <h3>[Subheading]</h3>
    <p>[Body paragraph.]</p>
    <h3>[Subheading]</h3>
    <p>[Body paragraph.]</p>
  </div>

  <aside class="marginalia" aria-label="Margin notes">
    <div class="marginalia__note">
      <div class="marginalia__note-label">Context</div>
      <p class="marginalia__note-body">[2–3 sentences of background.]</p>
    </div>
    <blockquote class="marginalia__pull">[Key sentence, possibly with <em>italic</em>.]</blockquote>
    <div class="marginalia__note">
      <div class="marginalia__note-label">See also</div>
      <p class="marginalia__note-body">[Cross-reference.]</p>
    </div>
    <p class="marginalia__footnote"><sup>1</sup>[Source caveat.]</p>
  </aside>
</div>
```

```html
<!-- Feature band with margin column (Workshop) -->
<div class="feature-band reveal">
  <div class="feature-band__rail">
    <span class="feature-band__rail-num">05</span>
    <span class="feature-band__rail-label">WORKSHOP · BLOCK [N]</span>
  </div>
  <div class="feature-band__body">
    <p class="body-lead"><span class="dropcap">W</span>[Opening.]</p>
    <h3>[Subhed]</h3>
    <p>[Paragraph.]</p>
  </div>
  <aside class="feature-band__margin">
    <figure class="feature-band__hero parallax">
      <img src="[URL]" class="pan" alt="[ALT]">
      <figcaption class="feature-band__hero-caption">[Caption]</figcaption>
    </figure>
    <!-- chart-card, pull-quote-card, datum-card go here -->
  </aside>
</div>
```

Classes verified: `.feature-band`, `.feature-band--with-marginalia`, `.feature-band__rail`, `.feature-band__rail-num`, `.feature-band__rail-label`, `.feature-band__body`, `.feature-band__body.lead`, `.feature-band__margin`, `.feature-band__hero`, `.feature-band__hero-caption`, `.body-lead`, `.dropcap`, `.marginalia`, `.marginalia__note`, `.marginalia__note-label`, `.marginalia__note-body`, `.marginalia__pull`, `.marginalia__footnote`.

---

### Pull Break (`.pull-break`)

A full-bleed interlude section between major sections. Used after The Lead and after the Rabbit Hole. The section element carries both the ground class and `pull-break reveal` as additional classes.

```html
<section class="sec dark pull-break reveal" data-section="lead-pull" data-scheme="ember">
  <span class="pull-break__q-open" aria-hidden="true">"</span>
  <span class="pull-break__q-close" aria-hidden="true">"</span>
  <blockquote class="pull-break__quote ln">[One sentence. Possibly with <em>italic phrase</em>.]</blockquote>
  <div class="pull-break__attribution">[NAME] · [SOURCE]</div>
</section>
```

The ground (dark or paper) must contrast the section immediately before it. If the Lead is paper, the pull-break is dark. If the Rabbit Hole is paper (flipped for contrast), the Rabbit Hole pull-break is also paper — matching the Rabbit Hole, not contrasting it.

Classes verified: `.pull-break`, `.pull-break__q-open`, `.pull-break__q-close`, `.pull-break__quote`, `.pull-break__attribution`.

---

### Pull Quote Card (`.pull-quote-card`)

A standalone card-style quote. Used in the `.feature-band__margin` column (Workshop). Not a section-level interlude — that is `.pull-break`.

```html
<blockquote class="pull-quote-card">
  "[Quote text]"
  <div class="pull-quote-card__attribution">[Name · Source]</div>
</blockquote>
```

Classes verified: `.pull-quote-card`, `.pull-quote-card__attribution`.

---

### Hero Quote (`.hero-quote`)

A large radial-accented quote block used at the end of The Long Game section. Different from a pull-break — it sits within the section, not between sections.

```html
<div class="hero-quote mt-48">
  <span class="hero-quote__glyph" aria-hidden="true">"</span>
  <blockquote class="hero-quote__text">[One sentence, with <em>accented word</em> near the end.]</blockquote>
  <div class="hero-quote__attribution">[NAME] · [SOURCE]</div>
</div>
```

Classes verified: `.hero-quote`, `.hero-quote__glyph`, `.hero-quote__text`, `.hero-quote__attribution`.

---

## Visual Pieces

---

### Fan-Spread (`.fan-spread`)

A deck of overlapping cards fanned out like playing cards. Used in The Shelf (books) and The Toolkit (apps/tools). 5–7 cards. The CSS positions them automatically by `:nth-child` up to the 7th card; do not set `transform` inline.

```html
<div class="fan-spread reveal">
  <div class="fan-spread__deck">
    <article class="fan-spread__card">
      <div class="fan-spread__card-kicker">01 · Fiction</div>
      <div class="fan-spread__card-image">
        <img src="[COVER_URL]" alt="[TITLE]">
      </div>
      <h4 class="fan-spread__card-title"><em>[Title]</em></h4>
      <p class="fan-spread__card-body">[Editorial take — ≥ 2 sentences of opinion.]</p>
      <div class="fan-spread__card-meta">[Author · Publisher]</div>
    </article>
    <!-- repeat for cards 02–07 -->
  </div>
</div>
```

Cards have hover behaviour (CSS). Do not add `data-fan` or custom JS hooks — the CSS owns the fanning. Never nest a fan-spread inside another fan-spread.

Classes verified: `.fan-spread`, `.fan-spread__deck`, `.fan-spread__card`, `.fan-spread__card-image`, `.fan-spread__card-kicker`, `.fan-spread__card-title`, `.fan-spread__card-body`, `.fan-spread__card-meta`.

---

### Plate Strip (`.plate-strip`)

A horizontal scroll-snap gallery of recipe plates (or gear items). 3–6 plates. The track scrolls on overflow-x; do not constrain its width. Plates use variable density: some have only a caption, some add stat, body, and quote.

```html
<div class="plate-strip reveal">
  <div class="plate-strip__track">

    <!-- Minimal plate: number + image + caption -->
    <figure class="plate">
      <div class="plate__number">01</div>
      <div class="plate__frame">
        <img src="[URL]" alt="[ALT]">
      </div>
      <figcaption class="plate__caption">
        <div class="plate__caption-head">[Dish Name]</div>
        [1–2 sentence caption.]
      </figcaption>
    </figure>

    <!-- Full-density plate: + stat + body + quote -->
    <figure class="plate">
      <div class="plate__number">02</div>
      <div class="plate__frame">
        <img src="[URL]" alt="[ALT]">
      </div>
      <figcaption class="plate__caption">
        <div class="plate__caption-head">[Dish Name]</div>
        [Caption text.]
        <div class="plate__stat">
          <span class="plate__stat-num count-up" data-target="35" data-suffix=" min">35 min</span>
          <span class="plate__stat-label">Total time</span>
        </div>
        <p class="plate__body">[2–3 sentences of method or note.]</p>
        <blockquote class="plate__quote">[A verdict or pull from the recipe.]</blockquote>
      </figcaption>
    </figure>

  </div>
</div>
```

Classes verified: `.plate-strip`, `.plate-strip__track`, `.plate`, `.plate__number`, `.plate__frame`, `.plate__caption`, `.plate__caption-head`, `.plate__stat`, `.plate__stat-num`, `.count-up`, `.plate__stat-label`, `.plate__body`, `.plate__quote`.

The `.count-up` class on `.plate__stat-num` requires a `data-target` attribute with a numeric value. Optional `data-suffix` (e.g. `" min"`, `"°"`) and `data-prefix`.

---

### Ribbon (`.ribbon`)

An animated marquee strip used as a transition between sections. The CSS drives the 40-second linear infinite animation automatically once `.ribbon__track` is present — no JS required. Use `.ribbon.reverse` for an opposite-direction second ribbon.

```html
<!-- Forward ribbon -->
<div class="ribbon" aria-hidden="true">
  <div class="ribbon__track">
    <span class="ribbon__item">THE SIGNAL · NO. [N]</span>
    <span class="ribbon__item">SUNDAY MAGAZINE · [DATE]</span>
    <span class="ribbon__item">A QUIET READ WITH COFFEE</span>
    <span class="ribbon__item">· THE SHELF · THE PANTRY ·</span>
    <span class="ribbon__item">SUNDAY 06:40</span>
  </div>
</div>

<!-- Reverse ribbon (pair for double-row effect) -->
<div class="ribbon reverse" aria-hidden="true">
  <div class="ribbon__track">
    <span class="ribbon__item">HISTORY · MEMORY · TIME</span>
    <span class="ribbon__item">· RETURN TO THE PRESENT ·</span>
    <span class="ribbon__item">THE SIGNAL · SUNDAY 06:40</span>
  </div>
</div>
```

Classes verified: `.ribbon`, `.ribbon__track`, `.ribbon__item`. The `.reverse` modifier is applied as an additional class on `.ribbon`.

Use at least one ribbon per issue. Ribbons sit between sections in the document flow — not inside a `.sec` wrapper.

---

### Dash (`.dash`)

A grid of numeric stat cells. Primary component for The Ledger section. 4–6 cells.

```html
<div class="dash reveal">
  <div class="dash__cell">
    <span class="dash__hint">Inflation</span>
    <span class="dash__num">
      <span class="count-up" data-target="2.8" data-suffix="%" data-decimals="1">2.8%</span>
    </span>
    <span class="dash__l">Year on year, April print.</span>
    <span class="dash__delta">▲ 0.1pp</span>
  </div>
  <!-- repeat for each stat cell -->
</div>
```

The `.count-up` inside `.dash__num` requires `data-target` (numeric), optional `data-suffix`, optional `data-prefix`, optional `data-decimals`. The fallback text inside the span is what displays before JS runs.

Classes verified: `.dash`, `.dash__cell`, `.dash__hint`, `.dash__num`, `.dash__l`, `.dash__delta`, `.count-up`.

---

### Timeline (`.timeline-rows`)

A vertically-stacked list of dated events. Used in The Week (condensed variant), The Long Game, The Itinerary, This Week in History, and The Ledger (for fiscal date markers).

```html
<div class="timeline-rows reveal">
  <div class="timeline-row reveal">
    <div class="timeline-row__date reveal">MON 14</div>
    <div class="timeline-row__body reveal">
      <h5>[Event Title]</h5>
      <p>[1–3 sentences with editorial verdict.]</p>
    </div>
  </div>
  <!-- repeat -->
</div>
```

For the condensed variant (The Week), add `.timeline-rows--condensed` to the wrapper — this reduces the vertical spacing.

Classes verified: `.timeline-rows`, `.timeline-rows--condensed`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body`.

---

### Datum Card (`.datum-card`)

A small self-contained stat card. Used in the Workshop margin and as grid elements in The Ledger.

```html
<div class="datum-card">
  <div class="datum-card__label">Weekly mileage</div>
  <div class="datum-card__value">
    <span class="count-up" data-target="32" data-suffix="km">32km</span>
  </div>
  <div class="datum-card__note">vs. prior 28km</div>
</div>
```

Classes verified: `.datum-card`, `.datum-card__label`, `.datum-card__value`, `.datum-card__note`.

---

### Chart Card (`.chart-card`)

A card containing a kicker, title, inline SVG, and a source footer. Used in The Workshop, The Ledger, and The Long Game. The `.dark` modifier adjusts the card's background and border for dark-ground sections.

```html
<div class="chart-card dark reveal">
  <div class="chart-card__kicker">Twelve-month arc</div>
  <h4 class="chart-card__title">[Chart Title]</h4>
  <svg class="chart-card__svg" viewBox="0 0 320 180" xmlns="http://www.w3.org/2000/svg">
    <!-- Grid lines -->
    <g stroke="currentColor" stroke-width="0.5" opacity="0.2">
      <line x1="0" y1="140" x2="320" y2="140"/>
      <line x1="0" y1="90"  x2="320" y2="90"/>
      <line x1="0" y1="40"  x2="320" y2="40"/>
    </g>
    <!-- Data line -->
    <polyline
      points="0,120 60,100 120,85 180,70 240,55 300,35"
      fill="none"
      stroke="var(--accent)"
      stroke-width="2"/>
  </svg>
  <div class="chart-card__foot">[Source] · units noted</div>
</div>
```

SVG must use `stroke="var(--accent)"` for the data line so it respects scheme overrides. Never hardcode a hex for the data line.

Classes verified: `.chart-card`, `.chart-card__kicker`, `.chart-card__title`, `.chart-card__svg`, `.chart-card__foot`.

---

### Brief Card (`.brief-card`)

A card used in grid layouts below fan-spreads or plate-strips. Three standard grid positions: "The Pick", "Pair With", "Skip Unless" (for The Shelf); "Pick of the week", "Retired" (for The Toolkit); "Pantry note" (for The Pantry).

```html
<div class="brief-grid mt-48">
  <article class="brief-card reveal">
    <div class="brief-card__kicker">01 · The pick</div>
    <h4 class="brief-card__title">[Title]</h4>
    <p class="brief-card__body">[3–4 sentences of Signal's verdict — opinion, not summary.]</p>
    <div class="brief-card__byline">By [Author] · [Publisher]</div>
  </article>
  <!-- additional brief-cards -->
</div>
```

Classes verified: `.brief-card`, `.brief-card__kicker`, `.brief-card__title`, `.brief-card__body`, `.brief-card__byline`, `.brief-grid`.

---

### Index Strip (`.index-strip`)

A horizontal navigation bar. Used in the Contents section and optionally elsewhere. Mark the current section `.is-current`.

```html
<div class="index-strip" aria-hidden="true">
  <span class="index-strip__item">Lead</span>
  <span class="index-strip__item is-current">Contents</span>
  <span class="index-strip__item">Week</span>
  <span class="index-strip__item">Shelf</span>
  <!-- etc. -->
</div>
```

Classes verified: `.index-strip`, `.index-strip__item`, `.index-strip__item.is-current`.

---

### Contents Ledger (`.contents-ledger`)

The structured table of contents. One row per section. Arabic numbers only.

```html
<div class="contents-ledger">
  <div class="contents-ledger__row">
    <span class="contents-ledger__num">01</span>
    <span class="contents-ledger__title">The <em>Lead</em></span>
    <span class="contents-ledger__meta">World · 8 min read · P. 02</span>
  </div>
  <!-- repeat for each section -->
</div>
```

Classes verified: `.contents-ledger`, `.contents-ledger__row`, `.contents-ledger__num`, `.contents-ledger__title`, `.contents-ledger__meta`.

---

### Plan Infographic (`.plan-infographic`)

A 16:10 ratio diagram for routes, schedules, or timelines. Primary component for The Itinerary. The SVG contains path data and circle markers; labels are absolutely-positioned `div.plan-infographic__label` elements with inline `style="top:%; left:%;"` for positioning.

```html
<div class="plan-infographic reveal">
  <h4 class="plan-infographic__title">
    [Itinerary Title]<br><em>[Date Range]</em>
  </h4>
  <svg class="plan-infographic__svg" viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg">
    <path d="M 80 300 Q 220 150 360 200 T 560 120"
          fill="none"
          stroke="var(--accent)"
          stroke-width="2"
          stroke-dasharray="4 4"/>
    <circle cx="80"  cy="300" r="6" fill="var(--accent)"/>
    <circle cx="360" cy="200" r="6" fill="var(--accent)"/>
    <circle cx="560" cy="120" r="6" fill="var(--accent)"/>
  </svg>
  <div class="plan-infographic__label" style="top:62%; left:10%;">
    <span>START</span>
    <span class="val">[POINT_A]</span>
  </div>
  <div class="plan-infographic__label" style="top:44%; left:50%;">
    <span>STOP</span>
    <span class="val">[POINT_B]</span>
  </div>
  <div class="plan-infographic__caption">ROUTE · [N] LEGS · [KM] KM</div>
</div>
```

SVG strokes must use `var(--accent)`. Never hardcode a colour in the SVG for data elements.

Classes verified: `.plan-infographic`, `.plan-infographic__title`, `.plan-infographic__svg`, `.plan-infographic__label`, `.plan-infographic__caption`. The `.val` class inside labels is verified in CSS.

---

### Dispatch Seal (`.dispatch-seal`)

A rotating SVG seal. Appears **exactly twice** per issue: on the Cover and on the Colophon. Never elsewhere. The JS draws the circular arc text from the `data-*` attributes.

```html
<div class="dispatch-seal"
     data-num="[ISSUE_NUMBER]"
     data-month="[MONTH]"
     data-year="MMXXVI"
     aria-hidden="true"></div>
```

Classes verified: `.dispatch-seal`. The inner `.dispatch-seal__ring`, `.dispatch-seal__hub`, and `.dispatch-seal__arc-text` elements are generated by JS — do not write them manually.

---

## Section-Specific Rules

---

### The Lead

- Ground: paper by default. Flip to dark only for cinematic/sombre lead stories.
- Component: `.feature-band.feature-band--with-marginalia`.
- Body: `.feature-band__body.lead` (adds extra minimum height).
- Opening paragraph: `p.body-lead` with `span.dropcap` wrapping the first letter.
- Minimum density: 500–800 words body, ≥ 2 pull quotes, ≥ 1 stat, ≥ 1 image.
- Folio watermark: `span.folio-watermark` with content `1` at section end.

---

### The Week

- Ground: paper.
- Component: `.timeline-rows.timeline-rows--condensed`.
- 5–7 `.timeline-row` items, each with a `Mon DD` date and a `p` carrying ≥ 1 opinion sentence.
- No images required (The Week is text-only by design).

---

### The Shelf

- Ground: dark.
- Primary component: `.fan-spread` with 5–7 `.fan-spread__card` items.
- Secondary component: `.brief-grid` with 3 `.brief-card` items (The Pick, Pair With, Skip Unless).
- Each fan-spread card body: ≥ 2 sentences of editorial take.
- Each brief-card: ≥ 3 sentences of genuine verdict.
- Image: each fan-spread card must have a `.fan-spread__card-image` with an `<img>`.
- No spoilers for Malazan, Cosmere, Star Wars.

---

### The Pantry

- Ground: paper.
- Primary component: `.plate-strip` with 3–5 `.plate` items.
- Secondary component: `.brief-grid` with 1–2 `.brief-card` items.
- ≥ 1 plate must have a `.plate__stat-num.count-up` with `data-target`.
- Each plate must carry an editorial sentence in the caption — not just method notes.

---

### The Workshop

- Ground: dark.
- Scheme: dossier (`data-scheme="dossier" style="--accent:#b8902a;"` on `<section>`).
- Component: `.feature-band` (not `--with-marginalia`; uses `feature-band__margin` instead).
- Margin contains: `.feature-band__hero.parallax` with `img.pan`, `.pull-quote-card`, `.chart-card.dark`, and optionally `.datum-card`.
- Body: ≥ 400 words, ≥ 2 subheadings, drop cap, ≥ 1 opinion paragraph.

---

### The Toolkit

- Ground: dark.
- Scheme: ember (default).
- Primary component: `.fan-spread` with 4–6 `.fan-spread__card` items.
- Secondary: `.brief-grid` with 2 `.brief-card` items ("Pick of the week" and "Retired").
- Card categories: apps, tools, objects, services, sites — label in `.fan-spread__card-kicker`.

---

### The Ledger

- Ground: dark.
- Primary component: `.dash` with 4–6 `.dash__cell` items.
- Secondary: two `.chart-card.dark` items in a two-column grid.
- Every `.dash__num` must contain a `.count-up` span with a real `data-target`.
- Source every stat: attribute inline, confirm URL in colophon sources.

---

### The Long Game

- Ground: paper.
- Primary component: `.timeline-rows` with 5 entries (years as dates).
- Secondary: `.chart-card` (paper variant — no `.dark` modifier).
- Closes with: `.hero-quote` block.
- Two-column layout (timeline left, chart right): use `display:grid; grid-template-columns: 1.2fr 1fr; gap: 48px;` as inline style on the grid container.
- ≥ 2 sentences per timeline entry; editorial angle mandatory.

---

### The Itinerary

- Ground: paper.
- Accent: cool (`data-accent="cool"` on the `<section>` element).
- Primary component: `.plan-infographic` with SVG route diagram.
- Secondary: `.timeline-rows` with daily entries (DAY 01, DAY 02...).
- SVG colours: use `var(--accent)` only.
- When a trip is approaching: expand to 5 daily entries and add contextual notes.

---

### This Week in History

- Ground: paper.
- Scheme: dossier (`data-scheme="dossier" style="--accent:#b8902a;"` on `<section>`).
- Component: `.timeline-rows` with 4–6 entries (years as dates).
- Each entry: 2–3 sentences with an editorial angle — why it resonates now.
- Standard gutter marks.

---

### Down the Rabbit Hole

- Ground: dynamic (contrast the preceding section).
- Component: `.feature-band.feature-band--with-marginalia`.
- Body: `.feature-band__body.lead` — minimum 600 words.
- Drop cap required.
- Folio watermark: `span.folio-watermark` with content `?`.
- The pull-break that follows must match the Rabbit Hole's ground (not contrast it).

---

### Editor's Note

- Ground: paper.
- Component: `.editors-note` with `.editors-note__left` (display heading) and `.editors-note__right` (body).
- Closing: `.editors-note__signoff` — "— The Editors".
- Standard gutter marks.

---

### Colophon

- Ground: dark (always).
- `.dispatch-seal` appears here (second of exactly two allowed instances).
- `.colophon` wraps `.colophon__grid` which contains exactly 4 `.colophon__block` elements:
  1. Masthead (`.colophon__masthead-title`, `.colophon__masthead-sub`, `.colophon__about`)
  2. In this issue (`.colophon__list` with `.tag` spans)
  3. Sources (`.colophon__list.colophon__sources` with ≥ 6 `<li>` entries; each has `.source-title` and `<a href>`)
  4. About (`.colophon__about` paragraphs)
- Closes with `.colophon__footer`.

```html
<section class="sec dark" data-section="colophon" data-scheme="ember">
  <span class="spine-label">· 12 · COLOPHON</span>
  <div class="dispatch-seal" data-num="[N]" data-month="[MONTH]" data-year="MMXXVI" aria-hidden="true"></div>
  <div class="colophon">
    <div class="colophon__grid">
      <div class="colophon__block">
        <span class="eyebrow">The masthead</span>
        <h3 class="colophon__masthead-title">The <em>Signal</em></h3>
        <div class="colophon__masthead-sub">A Sunday magazine · No. [N]</div>
        <p class="colophon__about">[About paragraph.]</p>
      </div>
      <div class="colophon__block">
        <span class="eyebrow">In this issue</span>
        <ul class="colophon__list">
          <li><span class="tag">01 · Lead</span>[Short section title]</li>
          <!-- repeat -->
        </ul>
      </div>
      <div class="colophon__block">
        <span class="eyebrow">Sources</span>
        <ul class="colophon__list colophon__sources">
          <li>
            <span class="source-title">[Source Name]</span>
            <a href="https://..." target="_blank" rel="noopener">https://...</a>
          </li>
          <!-- ≥ 6 entries -->
        </ul>
      </div>
      <div class="colophon__block">
        <span class="eyebrow">About</span>
        <p class="colophon__about">[About The Signal — purpose, cadence, type.]</p>
      </div>
    </div>
    <div class="colophon__footer">
      <span>© MMXXVI · THE SIGNAL · NO. [N]</span>
      <span>NEXT ISSUE · SUNDAY 06:40</span>
    </div>
  </div>
</section>
```

Classes verified: `.colophon`, `.colophon__grid`, `.colophon__block`, `.colophon__masthead-title`, `.colophon__masthead-sub`, `.colophon__about`, `.colophon__list`, `.colophon__sources`, `.colophon__footer`.

---

## Motion Binding Rules

These rules are non-negotiable. The JS in `assets/script.js` picks up these classes and applies the corresponding behaviour.

| Class | Where applied | Effect | Required? |
|-------|--------------|--------|-----------|
| `.parallax` | `div.cover__hero` | Slow downward scroll parallax on hero image | **Required on cover hero** |
| `.parallax` | `figure.feature-band__hero` | Same, in Workshop margin | Recommended |
| `.reveal` | All major content blocks, section eyebrows, feature bands, fan-spreads, plate-strips | Fade-up on IntersectionObserver (20% threshold) | **Required on all major blocks** |
| `.count-up` + `data-target` | `.dash__num` contents, `.plate__stat-num`, `.datum-card__value` contents | Animates numeric display from 0 to target on entry (0.8s) | **Required on all numeric stats** |
| `.ln` | Section heads, cover headline, pull-break quote | JS splits by `<br>` into `span` elements and staggers entry | **Required on all section heads** |
| `.pan` | `img` inside `.feature-band__hero` | Shifts object-position on scroll for a slow vertical pan | Optional |
| `.dropcap` | Opening paragraph span | Settles in on scroll via `.dropcap.in` | Required where used |
| `.grain` | Fixed full-viewport `div` | CSS noise overlay; always present | **Required in body (one instance)** |
| `.colour-flood` | Fixed full-viewport `div` | JS animates clip-path transitions between sections | **Required in body (one instance)** |
| `.progress-bar` | Fixed `div` | Tracks scroll progress | Required |
| `.back-to-top` | `button` before `</body>` | Appears after scrolling | Required |

`prefers-reduced-motion` is respected throughout the JS. Animations are suppressed or significantly reduced when the media query fires. Do not override this in inline styles.

---

## Scheme and Accent Overrides

The default scheme is applied at the body level:
```html
<body data-scheme="ember" data-ground="dark">
```

Section-level overrides use data attributes on the `<section>` element. Never override the body-level scheme mid-issue; always override at the section level.

```html
<!-- Dossier (brass accent) — Workshop and This Week in History -->
<section class="sec dark" data-scheme="dossier" style="--accent:#b8902a;">

<!-- Accent sub-variant — Itinerary (cyan) -->
<section class="sec paper" data-scheme="ember" data-accent="cool">

<!-- Accent sub-variant — Pantry or food-themed (orange) -->
<section class="sec paper" data-scheme="ember" data-accent="food">
```

Available accent sub-variants (verified in CSS):
- `cool` → `#48cae4` (cyan — use for Itinerary)
- `wild` → `#c9a84c` (amber)
- `food` → `#e8a838` (orange — use for Pantry if desired)
- `nature` → `#9dbf6a` (green)
- `urban` → `#7a9aaf` (slate)

Never set a bare hex in an inline style for a colour property other than `--accent`. The CSS variable system handles all palette expressions. If a hex is not in the ember, dossier, blueprint, or midnight palette definitions in `styles.css`, it does not belong in the issue.

---

## Template Placeholders

The template uses two inject markers that must be present in the generated HTML and absent in the final delivered file:

```html
<!-- In <head>, after Google Fonts link: -->
<!-- INJECT:CSS -->

<!-- Just before </body>: -->
<!-- INJECT:JS -->
```

The build script at `scripts/inject-assets.sh` replaces these markers with the full contents of `assets/styles.css` and `assets/script.js` respectively. The generator writes these markers into the HTML; the build script replaces them. After injection, neither marker should remain in the file.

Do not attempt to link or embed the CSS and JS files directly. The inject mechanism is the only supported delivery method. The generator must never read `styles.css` or `script.js` into context during issue generation — only the markers are written.

---

## Utility Classes

These exist in the CSS and may be applied where appropriate:

```
.mt-0  .mt-16  .mt-24  .mt-32  .mt-48  .mt-64  .mt-80
.mb-16  .mb-24  .mb-32  .mb-48
.center  .right
.accent   (color: var(--accent))
.muted    (color: var(--muted))
.display  (font-family: var(--display))
.sans     (font-family: var(--sans))
.italic
.upper    (uppercase + letter-spacing)
.sr-only  (visually hidden, screen-reader accessible)
.divider  (horizontal rule)
.container  .wrap  .wrap-tight
```

Use margin utilities (`mt-48`, `mb-32`) on elements inside sections instead of inline `margin-top` or `margin-bottom` style values.
