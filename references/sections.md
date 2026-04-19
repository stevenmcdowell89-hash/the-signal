# The Signal — Section Reference

> Source of truth: `assets/weekly-template.html` and `assets/styles.css`.
> Read this file in full when selecting rotating sections. It is small enough to read entirely.

This file documents every section that can appear in a Signal issue: its position, default ground, required components, minimum density, and search groups for the research phase.

---

## Cover

**Position:** 1 of 13 (always first)
**Ground:** Dark (always — Cover and Colophon bookend the issue)
**Section data attribute:** `data-section="cover"`

### What goes in

- Full-bleed hero image with `.parallax` class on the container div (not the `<img>`).
- A `.cover__scrim` overlay for legibility.
- A `.cover__ambient` div — the slow 22-second accent glow that sits above the scrim.
- A `.dispatch-seal` with `data-num`, `data-month`, and `data-year` attributes. **The seal appears only on Cover and Colophon.**
- `.cover__meta-top` bar with issue number and date (sans label).
- `.cover__body` containing:
  - `.cover__eyebrow.eyebrow--wide` — label like "THIS WEEK'S LEAD"
  - `h1.cover__headline.ln` — 2–5 words, split across `<br>` lines. One key word wrapped in `<em>` for italic accent. JS staggers each line on load.
  - `p.cover__dek` — 1–2 sentences setting up the issue's tone. Italic display type.
- `.cover__meta-bottom` containing:
  - `.cover__tags` with `.cover__tag` spans; one `.cover__tag--accent` for the primary topic.
  - `.cover__scroll-hint` — "SCROLL" label with animated arrow glyph.

### Components

```html
<section class="cover" data-section="cover">
  <div class="cover__hero parallax">
    <img src="[URL]" alt="[ALT]">
  </div>
  <div class="cover__scrim" aria-hidden="true"></div>
  <div class="cover__ambient" aria-hidden="true"></div>
  <div class="dispatch-seal" data-num="[N]" data-month="[MONTH]" data-year="MMXXVI" aria-hidden="true"></div>
  <div class="cover__meta-top">
    <span>SUNDAY MAGAZINE · NO. [N]</span>
    <span>[DD MONTH] MMXXVI</span>
  </div>
  <div class="cover__body">
    <div class="cover__eyebrow eyebrow--wide">THIS WEEK'S LEAD</div>
    <h1 class="cover__headline ln">
      Line one<br><em>accent</em><br>line three
    </h1>
    <p class="cover__dek">[Dek text]</p>
  </div>
  <div class="cover__meta-bottom">
    <div class="cover__tags">
      <span class="cover__tag cover__tag--accent">[PRIMARY]</span>
      <span class="cover__tag">[TAG]</span>
    </div>
    <div class="cover__scroll-hint" aria-hidden="true">SCROLL</div>
  </div>
</section>
```

---

## Contents — The Ledger of the Week

**Position:** 2 of 13
**Ground:** Paper
**Section data attribute:** `data-section="contents"`

### What goes in

One `.contents-ledger__row` per section in the issue. Each row has a `.contents-ledger__num` (arabic, zero-padded: 01, 02…), a `.contents-ledger__title` with one `<em>` on the key word, and a `.contents-ledger__meta` (topic, read time, page reference).

At the foot of the section, an `.index-strip` provides a horizontal navigation bar with one `.index-strip__item` per section. Mark the active section `.is-current`.

Standard gutter marks: `.gutter-mark.gutter-mark--tl`, `--tr`, `--bl`. Spine label: `· CONTENTS · INSIDE THIS ISSUE`.

The section head is always: `The <em>ledger</em><br>of the week.` — do not vary this.

### Components

`.contents-ledger`, `.contents-ledger__row`, `.contents-ledger__num`, `.contents-ledger__title` (with `<em>`), `.contents-ledger__meta`, `.index-strip`, `.index-strip__item`, `.index-strip__item.is-current`.

---

## The Lead

**Position:** 3 of 13
**Ground:** Paper by default. Flip to dark only for lead stories where cinematic gravity is warranted (a death, a disaster, a war milestone). If you flip the Lead to dark, also reconsider the Lead Pull-Break below.
**Section data attribute:** `data-section="lead"`

### What goes in

The longest read in the issue. 500–800 words of body copy. Minimum density:
- ≥ 600 words body
- ≥ 2 pull quotes (one in marginalia, one in the pull-break that follows)
- ≥ 1 stat or datum
- ≥ 1 image (in the feature-band hero or marginalia)
- Drop cap on the opening paragraph

Structure: `feature-band--with-marginalia` containing a `.feature-band__rail` with section number and label, a `.feature-band__body` with the article prose, and an `aside.marginalia` with supporting notes.

The `.feature-band__body` should have `.lead` as an additional class for the taller minimum height. Open with `p.body-lead` containing a `span.dropcap` wrapping the first letter.

Marginalia contains: one `.marginalia__note` (label + body) for context, one `blockquote.marginalia__pull` for a key quote, a second `.marginalia__note` for "See also", and optionally a `.marginalia__footnote` for source caveats.

End the section with `span.folio-watermark` for the section number glyph.

### Components

`.feature-band`, `.feature-band--with-marginalia`, `.feature-band__rail`, `.feature-band__rail-num`, `.feature-band__rail-label`, `.feature-band__body`, `.feature-band__body.lead`, `.body-lead`, `.dropcap`, `.marginalia`, `.marginalia__note`, `.marginalia__note-label`, `.marginalia__note-body`, `.marginalia__pull`, `.marginalia__footnote`, `.folio-watermark`.

---

## Lead Pull-Break

**Position:** 4 of 13
**Ground:** Dark by default (contrasts paper Lead). Flip to paper if Lead was flipped to dark.
**Section data attribute:** `data-section="lead-pull"`
**Additional class on section:** `pull-break reveal`

### What goes in

One giant accent quote from the Lead story. The `.pull-break__q-open` and `.pull-break__q-close` are decorative quote marks that peek from the corners. The `blockquote.pull-break__quote.ln` gets JS line-stagger. One key phrase wrapped in `<em>`. Attribution line below.

### Components

`.pull-break`, `.pull-break__q-open`, `.pull-break__q-close`, `.pull-break__quote`, `.pull-break__attribution`.

---

## The Week

**Position:** 5 of 13
**Ground:** Paper
**Section data attribute:** `data-section="week"`

### What goes in

A brief chronological roundup of the week's most significant news events. 5–7 dated items. Each item is a `.timeline-row` with a `.timeline-row__date` (Mon DD format) and a `.timeline-row__body` containing an `h5` headline and a `p` of 1–2 sentences carrying an editorial verdict. Accent italic optional per item.

Use `timeline-rows--condensed` class on the wrapper for the tighter spacing variant.

Minimum density: ≥ 5 items, each with a clear opinion or framing beyond the bare fact.

Standard gutter marks and spine label.

### Components

`.timeline-rows`, `.timeline-rows--condensed`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body`.

---

## The Shelf

**Rotating — every 2–3 weeks**
**Default ground:** Dark
**Section data attribute:** `data-section="shelf"`

### What goes in

Books: fiction, non-fiction, essay, memoir, reissue. 5–7 cards in a fan-spread deck. Below the deck, a `.brief-grid` of 3 brief-cards: "The Pick", "Pair With", and "Skip Unless".

Fan-spread cards use: `.fan-spread__card-kicker` (number and genre), `.fan-spread__card-image` with `<img>`, `.fan-spread__card-title` with `<em>`, `.fan-spread__card-body` (the editorial take — minimum 2 sentences of opinion), `.fan-spread__card-meta` (author name).

Each brief-card must carry ≥ 3 sentences of genuine opinion — not a summary, a verdict.

No spoilers for Malazan, Cosmere, or Star Wars. If the reader is mid-series, the Shelf may note "later in the series" without any detail.

Transition to this section: use a `.ribbon` with `.ribbon__track` and `.ribbon__item` elements between The Week and The Shelf.

### Components

`.fan-spread`, `.fan-spread__deck`, `.fan-spread__card`, `.fan-spread__card-image`, `.fan-spread__card-kicker`, `.fan-spread__card-title`, `.fan-spread__card-body`, `.fan-spread__card-meta`, `.brief-grid`, `.brief-card`, `.brief-card__kicker`, `.brief-card__title`, `.brief-card__body`, `.brief-card__byline`.

### Search Groups

New releases (fiction, non-fiction, essay, memoir), reissues in print, audiobook and podcast releases, reader recommendations, Booker/prizes news.

---

## The Pantry

**Rotating — every 2–3 weeks**
**Default ground:** Paper
**Section data attribute:** `data-section="pantry"`

### What goes in

Food and recipes. 3–5 recipe plates in a horizontal scroll-snap strip. Each plate has a sequential number, a food photograph, a caption head (the dish name), and optional stat and body elements.

Plate stat format: `span.plate__stat-num.count-up` with `data-target` and optional `data-suffix`. Label below in `span.plate__stat-label`.

Below the plate-strip, a `.brief-grid` with one or two `.brief-card` elements for pantry notes, storage tips, or ingredient observations.

Minimum density: 3–5 plates, each with a real opinion on the recipe (not just a method note). At least one plate should have a `.plate__stat-num.count-up` stat.

Focus on high-protein cooking, meal prep, one-pan/batch dishes. No low-effort content.

### Components

`.plate-strip`, `.plate-strip__track`, `.plate`, `.plate__number`, `.plate__frame`, `.plate__caption`, `.plate__caption-head`, `.plate__stat`, `.plate__stat-num.count-up`, `.plate__stat-label`, `.plate__body`, `.plate__quote`, `.brief-grid`, `.brief-card`.

### Search Groups

Recipes by protein/calorie target, batch cooking, high-protein meal prep, ingredient of the week, food science, restaurant reviews (NI + UK), seasonal produce.

---

## This Week in History

**Rotating — every 2–3 weeks**
**Default ground:** Paper with dossier scheme (`data-scheme="dossier" style="--accent:#b8902a;"`)
**Section data attribute:** `data-section="history"`

### What goes in

4–6 historical events dated to the same calendar week, across different decades and centuries. Each as a `.timeline-row` with year as the date, a title `h5`, and 2–3 sentences of context carrying an editorial angle — why this matters now, not just what happened then.

Preferably UK-flavoured or with a global angle that resonates today. Standard gutter marks and spine label.

### Components

`.timeline-rows`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body`.

Section data: `data-scheme="dossier" style="--accent:#b8902a;"` on the `<section>` element.

### Search Groups

On-this-day sites, Wikipedia "on this day", UK history events, world events from the same calendar week across decades.

---

## The Workshop

**Rotating — every 3–4 weeks**
**Default ground:** Dark with dossier scheme (`data-scheme="dossier" style="--accent:#b8902a;"`)
**Section data attribute:** `data-section="workshop"`

### What goes in

Training, fitness equipment, home gym, or tech gear. Feature-band structure (without the full marginalia aside — use `feature-band__margin` for the image and supporting cards).

The `.feature-band__margin` holds: a `.feature-band__hero.parallax` image with `img.pan` and a caption, a `.pull-quote-card` with a key editorial quote, a `.chart-card.dark` for a visual data representation (training volume, spec comparison), and optionally a `.datum-card` for a key stat.

Body copy: 400+ words with ≥ 2 subheadings. Drop cap on opening. Opinion is mandatory — this is not a press release.

### Components

`.feature-band`, `.feature-band__rail`, `.feature-band__rail-num`, `.feature-band__rail-label`, `.feature-band__body`, `.feature-band__margin`, `.feature-band__hero`, `.feature-band__hero-caption`, `.pull-quote-card`, `.pull-quote-card__attribution`, `.chart-card`, `.chart-card__kicker`, `.chart-card__title`, `.chart-card__svg`, `.chart-card__foot`, `.datum-card`, `.datum-card__label`, `.datum-card__value`, `.datum-card__note`, `.dropcap`, `.body-lead`.

### Search Groups

Ibex programme updates, home gym equipment, kettlebell training, running gear, Garmin features, Pliability updates, fitness science papers, gym nutrition, AI training tools.

---

## The Toolkit

**Rotating — every 3–4 weeks**
**Default ground:** Dark
**Section data attribute:** `data-section="toolkit"`

### What goes in

Apps, software, services, or physical tools. 4–6 cards in a fan-spread deck. Below, a `.brief-grid` with two brief-cards: "Pick of the week" and "Retired" (a tool that's been dropped, and why).

Same card structure as The Shelf: image, kicker, title with `<em>`, body (≥ 3 sentences opinion), meta (category/platform).

Covers Android apps, browser extensions, AI consumer tools, productivity services, Notion/Kindle Scribe templates, Etsy tools.

### Components

`.fan-spread`, `.fan-spread__deck`, `.fan-spread__card`, `.fan-spread__card-image`, `.fan-spread__card-kicker`, `.fan-spread__card-title`, `.fan-spread__card-body`, `.fan-spread__card-meta`, `.brief-grid`, `.brief-card`, `.brief-card__kicker`, `.brief-card__title`, `.brief-card__body`, `.brief-card__byline`.

### Search Groups

Android apps (new releases, updates), AI consumer tools, browser extensions, productivity apps, Notion templates, Kindle Scribe tools, Etsy digital products, app reviews.

---

## The Ledger

**Rotating — every 3–4 weeks**
**Default ground:** Dark
**Section data attribute:** `data-section="ledger"`

### What goes in

Numbers and finance. The centrepiece is a `.dash` grid of 4–6 `.dash__cell` elements, each with a `.dash__hint` label, a `.dash__num` containing a `.count-up` span, a `.dash__l` description line, and a `.dash__delta` showing change direction and magnitude.

Below the dash, a two-column grid of two `.chart-card.dark` elements: one with an SVG line chart showing the 12-month arc of the key metric, one as a "Verdict" card with 3–4 sentences of editorial interpretation.

Optionally: `.contents-ledger__row` elements for a structured data table, and `.timeline-row` entries for key fiscal dates.

Minimum density: ≥ 4 dash stats, ≥ 1 chart, ≥ 200 words of interpretation.

### Components

`.dash`, `.dash__cell`, `.dash__hint`, `.dash__num`, `.dash__l`, `.dash__delta`, `.count-up`, `.chart-card`, `.chart-card__kicker`, `.chart-card__title`, `.chart-card__svg`, `.chart-card__foot`, `.datum-card`, `.contents-ledger`, `.contents-ledger__row`, `.timeline-row`.

### Search Groups

UK inflation (ONS), Bank of England base rate, ISA rates, Monzo/Revolut/Starling product updates, HMRC news, housing market data, FIRE community discussions, BTC/gold spot prices, employment data.

---

## The Long Game

**Rotating — monthly (every 4 weeks)**
**Default ground:** Paper
**Section data attribute:** `data-section="longgame"`

### What goes in

A retrospective or macro-trend piece. 5-point timeline of milestones (years as dates in `.timeline-row__date`) paired with a `.chart-card` showing the shape of the data over time. Closes with a `.hero-quote` block for the defining long-horizon statement.

The timeline and chart-card sit in a two-column grid (template uses `display:grid; grid-template-columns: 1.2fr 1fr`).

Minimum density: 5 timeline entries × 2–3 sentences each, 1 chart, 1 hero-quote, editorial verdict paragraph.

### Components

`.timeline-rows`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body`, `.chart-card`, `.chart-card__kicker`, `.chart-card__title`, `.chart-card__svg`, `.chart-card__foot`, `.hero-quote`, `.hero-quote__glyph`, `.hero-quote__text`, `.hero-quote__attribution`.

### Search Groups

Macroeconomic data (10-year arcs), FIRE movement history, UK housing data, inflation history, global tech adoption curves, markets retrospectives.

---

## The Itinerary

**Rotating — every 3–4 weeks; increases frequency near confirmed trips**
**Default ground:** Paper with cool accent (`data-accent="cool"`)
**Section data attribute:** `data-section="itinerary"`

### What goes in

Travel planning or trip retrospective. The primary visual is a `.plan-infographic` containing an SVG route diagram with `.plan-infographic__label` overlays (positioned with inline `style="top:%; left:%;"`) and a `.plan-infographic__caption` at the foot.

Below the infographic, a `.timeline-rows` of daily itinerary entries: date as "DAY 01 / DAY 02" in `.timeline-row__date`, place name as `h5`, and 2–3 sentences of editorial angle in `p`.

Section data attributes: `data-accent="cool"` and `data-scheme="ember"`.

When a trip is approaching (from `upcoming_trips` in state file), expand coverage and increase cadence.

### Components

`.plan-infographic`, `.plan-infographic__title`, `.plan-infographic__svg`, `.plan-infographic__label`, `.plan-infographic__caption`, `.timeline-rows`, `.timeline-row`, `.timeline-row__date`, `.timeline-row__body`.

### Search Groups

Destination guides, Efteling park information, Beekse Bergen safari resort, Netherlands family travel, theme park news, European train/flight routes, travel packing, travel fintech (Revolut abroad).

---

## Down the Rabbit Hole

**Position:** Fixed but conditional (appears when due per 3–4 week cadence)
**Ground:** Dynamic — choose whichever contrasts with the preceding section. If the section directly before is dark, use paper. If the section before is paper, use dark. Default is dark.
**Section data attribute:** `data-section="rabbithole"`

### What goes in

A single strange, deep, or obsessive topic: sustained for 600 words with a clear editorial position. Not a summary. This is the long read — the piece the reader comes back to on Monday morning.

Structure identical to The Lead: `feature-band--with-marginalia` with rail, body (`.lead` class for taller minimum height), and aside marginalia. Drop cap on opening. Marginalia contains Source, a margin pull quote, Further reading, and a footnote.

Closes with `span.folio-watermark` containing a "?" glyph.

The pull-break that follows (position 10) must match the Rabbit Hole ground.

Minimum density: 600 words, ≥ 2 pull quotes, ≥ 1 stat, ≥ 1 image.

### Components

`.feature-band`, `.feature-band--with-marginalia`, `.feature-band__rail`, `.feature-band__body`, `.feature-band__body.lead`, `.body-lead`, `.dropcap`, `.marginalia`, `.marginalia__note`, `.marginalia__note-label`, `.marginalia__note-body`, `.marginalia__pull`, `.marginalia__footnote`, `.folio-watermark`.

---

## Rabbit Hole Pull-Break

**Position:** 10 of 13
**Ground:** Matches the Rabbit Hole ground (paper or dark — flip with it).
**Section data attribute:** `data-section="rh-pull"`
**Additional class:** `pull-break reveal`

One accent quote from the Rabbit Hole long read. Same structure as the Lead Pull-Break: `.pull-break__q-open`, `blockquote.pull-break__quote.ln` with `<em>`, `.pull-break__attribution`.

---

## Editor's Note

**Position:** 11 of 13
**Ground:** Paper (always)
**Section data attribute:** `data-section="note"`

### What goes in

A brief personal sign-off from "The Editors" before the Colophon. Two-column layout: left column is the display heading (`h2.editors-note__left.ln` — 3 short lines with `<em>`), right column is `.editors-note__right` containing an `.eyebrow` date stamp, a `p.dek` setting context, 1–2 body paragraphs with editorial voice, and a `.editors-note__signoff` closing line ("— The Editors").

### Components

`.editors-note`, `.editors-note__left`, `.editors-note__right`, `.editors-note__signoff`.

---

## Colophon

**Position:** 12 of 13 (always last)
**Ground:** Dark (always — mirrors Cover)
**Section data attribute:** `data-section="colophon"`

### What goes in

The `.dispatch-seal` appears here for the second (and last) time. Four-column `.colophon__grid` inside `.colophon`:

1. **Masthead block** — `.colophon__masthead-title` (The `<em>Signal</em>`), `.colophon__masthead-sub`, `.colophon__about`
2. **In this issue** — `.colophon__list` with one `li` per section, each using a `.tag` span for the section number and a short descriptor
3. **Sources** — `.colophon__list.colophon__sources` with ≥ 6 `li` entries, each with a `.source-title` span and an `<a href>` with the real URL
4. **About** — `.colophon__about` paragraphs describing The Signal and its type setting

Closes with `.colophon__footer` carrying the copyright line and "NEXT ISSUE · SUNDAY 06:40".

### Components

`.colophon`, `.colophon__grid`, `.colophon__block`, `.colophon__masthead-title`, `.colophon__masthead-sub`, `.colophon__about`, `.colophon__list`, `.colophon__sources`, `.colophon__footer`, `.dispatch-seal`.

---

## Component Palettes for Rotating Sections — Summary Table

| Section | Ground | Scheme | Primary Component | Secondary Components |
|---------|--------|--------|-------------------|----------------------|
| The Shelf | Dark | ember | `.fan-spread` | `.brief-grid`, `.brief-card` |
| The Pantry | Paper | ember | `.plate-strip` | `.brief-card` |
| This Week in History | Paper | dossier (brass `#b8902a`) | `.timeline-rows` | — |
| The Workshop | Dark | dossier (brass `#b8902a`) | `.feature-band` | `.chart-card`, `.datum-card`, `.pull-quote-card` |
| The Toolkit | Dark | ember | `.fan-spread` | `.brief-grid`, `.brief-card` |
| The Ledger | Dark | ember | `.dash` | `.chart-card`, `.datum-card` |
| The Long Game | Paper | ember | `.timeline-rows` | `.chart-card`, `.hero-quote` |
| The Itinerary | Paper | ember + cool accent | `.plan-infographic` | `.timeline-rows` |

---

## Search Groups for Rotating Sections

When a rotating section is selected, search these groups during the research pass in addition to the core groups.

**The Shelf:** new book releases (fiction, non-fiction, essay, memoir), reissues, audiobook new titles, shortlists and prize news, podcast season launches.

**The Pantry:** high-protein recipes, meal prep ideas, batch cooking, seasonal ingredients UK, restaurant openings/closures NI and UK, food science.

**This Week in History:** on-this-day databases, UK Parliament history, Wikipedia "on this day", world war anniversaries, significant births/deaths in calendar week.

**The Workshop:** Ibex training programme, kettlebell training science, home gym equipment reviews, running shoe releases, Garmin watch updates, Pliability app news, fitness nutrition.

**The Toolkit:** Android app updates and new releases, AI consumer tool launches, productivity app reviews, Notion template marketplace, browser extension reviews, Kindle Scribe updates, Etsy digital shop analytics.

**The Ledger:** ONS inflation release, Bank of England rate decisions, ISA and savings rates, Monzo/Revolut/Starling product news, HMRC announcements, UK housing index, FIRE/personal finance community.

**The Long Game:** macroeconomic data archives, FRED or ONS long-run datasets, FIRE movement evolution, tech adoption curves, long-run sports performance data.

**The Itinerary:** Efteling park events and news, Beekse Bergen Safari Resort information, Netherlands travel guides, European theme park rankings, family travel packing, Revolut travel features, Dutch rail and transport.
