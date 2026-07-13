# Component Contracts — Required Patterns by Format

This reference defines the exact HTML component patterns for every section in every issue format. When generating HTML, follow these contracts precisely. **Never invent class names** — if a class isn't listed here or in the template file, it doesn't exist in the CSS.

---

## Universal Components (All Formats)

### Cover
```html
<header class="cover" id="top">
  <div class="cover-noise"></div>
  <div class="cover-grain"></div>
  <div class="cover-issue" style="position:relative;z-index:2">[DATE] · Issue #[N] · Sunday Edition [· Format Special]</div>
  <div class="cover-brand" style="position:relative;z-index:2">The Signal<span>.</span></div>
  <div class="cover-headline" style="position:relative;z-index:2">[Headline text]</div>
  <!-- Optional subtitle: -->
  <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:rgba(255,255,255,.35);margin-top:12px;position:relative;z-index:2;letter-spacing:1px;">[Subtitle]</div>
  <div class="cover-tags">
    <span class="tag">[Tag 1]</span>
    <span class="tag">[Tag 2]</span>
    <!-- 6-10 tags -->
  </div>
</header>
```
**Wrong patterns:** `<section class="cover">`, `cover-tag`, `cover-body`, `cover-kicker`, `cover-sub`, `cover-brand-dot`, `cover-top-bar` — none exist in CSS.

> **For the WEEKLY (Transmission), do NOT hand-write this cover.** `scripts/stitch_weekly.py` GENERATES the Transmission cover — the `.masthead` wordmark, waveform, lead, dataline, and folio — from the plan's `cover` block. A weekly writer never emits cover markup. The markup above is the **special-format** cover only.

### Navigator
```html
<section class="nav-section" id="nav">
  <h2>What's Inside</h2>
  <div class="nav-grid">
    <a href="#[section-id]" class="nav-card [color]" style="text-decoration:none">
      <div class="nav-card-tag">
        <span class="nav-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">[icon path]</svg></span>
        [Section Name]
      </div>
      <h3>[Card Title]</h3>
      <p>[Card description]</p>
      <div class="read-time">[N] min</div>
    </a>
    <!-- Repeat for each section -->
  </div>
</section>
```
**Color classes:** `world`, `tech`, `shelf`, `screen`, `session`, `history`, `football`. Each applies a left-border accent colour.
**Wrong patterns:** `nav-card-num`, `nav-card-title`, `nav-card-desc`, `section-label` as navigator heading — none exist or are wrong elements.

> **For the WEEKLY (Transmission), there is no hand-written navigator.** `scripts/stitch_weekly.py` GENERATES the cover **tuner** ("station list") from each chapter's `nav_coverline` / `nav_coverline_html` field — one `.station[data-station]` row per nav band present, in skeleton order. Writers supply only the coverline text in the plan; they never emit `.nav-grid` / `.nav-card` / `.tuner` / `.station` markup. The `.nav-section` / `.nav-card` markup above is the **special-format** navigator only.

### Footer
```html
<footer class="footer" id="footer">
  <div class="footer-brand">The Signal<span>.</span></div>
  <div class="footer-issue">[Format] · Issue #[N] · [Date]</div>
  <p class="footer-note">[Closing note]</p>
</footer>
```

## Standard Weekly (Transmission) — writer band-content contracts

> **Architecture — read this first.** A standard weekly is assembled by `scripts/stitch_weekly.py`, which GENERATES all chrome deterministically from `format-skeletons/weekly.json`: the cover/masthead/tuner, the four movement dividers, every band-head, the colophon bar, and the sign-off. **A weekly writer produces ONLY the inner content of ONE band**, written to `/tmp/signal-build/chapters/<band_id>.html`. That file has **NO `<section>` wrapper, NO band-head, NO movement divider, NO cover** — the stitcher wraps it. Every contract below therefore shows the **INNER markup only**; copy the shape from the golden fixture at `references/golden/weekly/chapters/<band_id>.html` and the reference render at `docs/mockups/reference-issue-transmission.html`.
>
> **Mandatory structural hooks** (the validator keys on these, decoupled from display classes):
> - `data-role="release-radar"` on the Screen & Sound rail `<aside>`.
> - `data-desk-column` on each Desk column `<div class="deskcol">`.
>
> **Forbidden in weeklies:** the special/holiday `.sp-*` and `.hol-*` vocabularies, and the retired weekly classes — `.movement-band`, `.the-desk`, `.desk-column`, `.caught-up` / `.cu-list`, `.week-in-numbers` / `.stat-bar`, `.nav-card`, `.radar-grid` / `.radar-row` / `.radar-cat` / `.radar-platform`, `.do-this-week`, `.thread-recap`, `.section-label`, `.sec-watermark`. **None of these exist in the Transmission stylesheet** (they are superseded for the weekly). Use only the classes named in the contracts below.

### The Letter — `the_letter` (content: `letter`)
The editor's note. Inner markup only; the stitcher wraps it in `<section class="letter">`.
```html
<h2>[The turn of the week, in one line.]</h2>
<p class="kicker">[Italic sub-line — the week's throughline.]</p>
<p class="first">[Opening paragraph. p.first gets the drop-cap automatically — no extra markup for the cap.]</p>
<p>[One or two more paragraphs.]</p>
<p class="sig">— The Editor</p>
<p class="mono sigline">TRANSMITTED SUNDAY · [DD MON YYYY]</p>
```
Shape: `h2` + `p.kicker`, one `p.first` (drop-cap) then plain `p`s, closing `p.sig` and `p.mono.sigline`.

### The Week in Numbers — `week_in_numbers` (content: `figures`)
The personal ledger panel — the reader's week, metered. `.figures` > `.figures-frame` holding a `.fig-caption`, 4–6 `.fig-row`s, and a `.fig-foot`.
```html
<div class="figures">
  <div class="figures-frame">
    <div class="fig-caption"><span>TABLE I · <b>[PANEL TITLE]</b></span><span>№[NNN]</span></div>
    <div class="fig-row">
      <div class="fig-label">
        <span class="k">[Metric name]</span>
        <span class="d">[italic gloss — what it means this week]</span>
      </div>
      <div class="fig-val">31.2<small>mi</small></div>
    </div>
    <!-- 4–6 .fig-row total. Use <small> for the unit; wrap the number in .win for the signal-red highlight -->
    <div class="fig-foot"><span>[CARRIED FORWARD…]</span><span>[TOTALS SINCE…]</span></div>
  </div>
</div>
```

### Caught Up — `caught_up` (content: `digest`, HARD cap 8)
The completeness digest: `<ol class="digest">` with **≤ 8 `<li>`** — one missable item each, a bolded dateline/label then a flat factual line. The cap is structural: never a ninth `<li>`, never collapsible. Wire-headline register, no synthesis.
```html
<ol class="digest">
  <li><p><b>[Dateline.]</b> [One tight factual line.]</p></li>
  <!-- ≤ 8 <li> total — HARD cap -->
</ol>
```

### The Long Read — `long_read` (content: `longread`, exactly one per issue)
The single feature: a `.lr-title` block then a `.lr-body` prose column. Optional inline breaks — `.pullquote`, `.plate-img`, `.aside-note`.
```html
<div class="lr-title">
  <div class="mono" style="color:var(--signal);">[EYEBROW]</div>
  <h2>[Headline with an <em>accent</em> word]</h2>
  <p class="stand">[Standfirst — one or two sentences.]</p>
  <p class="mono byline">BY THE EDITOR · [PLACE] · [DATE]</p>
</div>
<div class="lr-body">
  <p class="first">[Opening paragraph — auto drop-cap via p.first.]</p>
  <p>[body…]</p>

  <div class="pullquote">
    [A resonant line.]
    <span class="attr">[ATTRIBUTION]</span>
  </div>

  <p class="noindent">[first paragraph after a break — .noindent suppresses the run-on indent]</p>

  <div class="plate-img">
    <img src="[verified bundle URL or /assets/cached/<hash>.jpg]" alt="[What the picture shows, concretely — a reader with images off must lose nothing]" loading="lazy">
    <div class="plate-cap">
      <span class="mono fig">FIG. 01</span>
      <span class="txt">[Italic caption — what this is and why it's here.]<span class="credit">[SOURCE · LICENCE — e.g. NASA / AT&amp;T · public domain · Wikimedia Commons]</span></span>
    </div>
  </div>

  <div class="aside-note">
    <div class="lbl mono">THE CASE AGAINST · <b>THE OTHER READING</b></div>
    <h4>[The counter-case, in a line.]</h4>
    <p>[The strongest honest counter-argument, sourced from real coverage — never a strawman.]</p>
  </div>
</div>
```
`.aside-note` is the weekly's honest counter-argument device (the old "case against"), used only where there is a real argument to answer — usually here. The Long Read MUST carry ≥1 real image plate (validator invariant `long_read_has_image`; the golden carries two) — see the `.plate-img` contract below.

### The image plate — `.plate-img` (the weekly's image component, all bands)
**A plate is a real `<img>`, captioned and credited.** This is the form the shipped exemplar (`issues/signal_weekly_2026-07-13.html`, 10 worked plates) and the golden fixture use everywhere an image appears — Long Read figures, the issue's cover plate, and the lead image on a Round:
```html
<div class="plate-img">
  <img src="[verified bundle URL or mirrored /assets/cached/<hash>.jpg]" alt="[Meaningful description of the picture]" loading="lazy">
  <div class="plate-cap">
    <span class="mono fig">FIG. 01</span>
    <span class="txt">[Italic caption.]<span class="credit">[SOURCE · LICENCE]</span></span>
  </div>
</div>
```
Rules:
- **The `<img>` is mandatory in the plate and always wrapped** — `.plate-img > img`, never a bare `<img>` floating in prose. Every image carries a non-empty, concrete `alt` and `loading="lazy"`.
- **Every plate is captioned + credited**: `.plate-cap` holds a mono `.fig` tag (`FIG. 01` / `FIG. 02` numbered in the Long Read; a plain `FIG.` on Round lead plates; `COVER` on the cover plate) and an italic `.txt` caption whose last child is a `<span class="credit">` naming source and licence.
- **Variants:** `.plate-img.lead` is the wider band-opening plate — use it for the issue's cover plate (top of the OPEN movement's first band) and as the opening image of a Round (Touchline, Pixel & Byte, Screen & Sound, This Week in History). A portrait/archival plate may cap its width inline (e.g. `style="max-width:340px;"`).
- **`src` discipline:** only verified `image_candidates` URLs from the research bundle, or their mirrored `/assets/cached/<hash>.jpg` copies. Direct image files only (`.jpg/.png/.webp` — the static gate fails page-URLs used as images). Never AI-generated, never hotlinked guesses.
- **Budget:** the weekly hard-fails under 8 real `<img>` tags (`image-floor`), and the Long Read hard-fails with zero (`long_read_has_image`). Bands whose plan carries `images_needed` MUST place them.

**Fallback — the empty `.plate-box` glyph (exceptional).** ONLY when no verified image is available for a slot may a plate ship as the drawn placeholder box:
```html
<div class="plate-img">
  <div class="plate-box"><span class="glyph">FIG. 01 · [LABEL]</span></div>
  <div class="plate-cap">
    <span class="mono fig">FIG. 01</span>
    <span class="txt">[Italic caption.]</span>
  </div>
</div>
```
An empty `.plate-box` is not a picture: it does **not** count toward the 8-image floor or the Long Read image invariant, and a writer reaching for it on a planned `images_needed` slot must flag the planner for another candidate rather than ship the box silently.

### The Touchline — `touchline` (content: `round` — `scores` + `items`)
Sport. An intro `.lead` (opening with a `.drop` clause), an optional `.scores` grid for the marquee result, then an `.items` list of quick rows.
```html
<p class="lead"><span class="drop">[Opening clause]</span> — [the rest of the intro].</p>

<div class="scores">
  <div class="score wide">
    <span class="mono tag">[FREQ · COMPETITION · STAGE]</span>
    <h3>[The headline result]</h3>
    <p>[One or two lines. <span class="num">[score / verdict]</span>]</p>
  </div>
  <!-- plain .score cells pair two-up; .score.wide spans full width -->
</div>

<ul class="items">
  <li>
    <span class="freq">101.2</span>
    <div>
      <h3>[Item headline]</h3>
      <p>[One or two lines. <b>[tag]</b>]</p>
    </div>
  </li>
  <!-- more .items li -->
</ul>
```

### Pixel & Byte — `pixel_byte` (content: `round` — `items`)
Gaming. A plain `.items` list — same row shape as The Touchline's items (`.freq` + `<div><h3>…</h3><p>…</p></div>`).
```html
<ul class="items">
  <li>
    <span class="freq">110.1</span>
    <div><h3>[Headline]</h3><p>[One or two lines. <b>[tag]</b>]</p></div>
  </li>
  <!-- more li -->
</ul>
```

### Screen & Sound — `screen_sound` (content: `round` — `with-rail`; contains Release Radar)
Watch & listen, with the **Release Radar as its side rail — never its own band**. `.with-rail` holds an `.items` list plus an `<aside class="rail" data-role="release-radar">`. The **`data-role="release-radar"` hook is mandatory** (validator-enforced: the radar must be a descendant here and must never render as its own band or nav station).
```html
<div class="with-rail">
  <ul class="items" style="margin-top:0;">
    <li>
      <span class="freq">120.5</span>
      <div><h3>[Headline]</h3><p>[One or two lines. <b>[tag]</b>]</p></div>
    </li>
    <!-- a couple of items -->
  </ul>

  <aside class="rail" data-role="release-radar" aria-label="Release Radar">
    <div class="rail__label">
      <span class="mono t">RELEASE RADAR</span>
      <span class="mono">DATED</span>
    </div>
    <div class="rail-item">
      <span class="when">[OUT NOW · DD MON]</span>
      <span class="what"><b>[Title]</b><i>[medium · detail]</i></span>
    </div>
    <!-- several .rail-item; dated, chronological -->
  </aside>
</div>
```

### Bookmark — `bookmark` (content: `round` — `picks`)
The fixed books rail every issue. (There is **no** rotating "The Shelf"; the deep book piece, when there is one, is the Long Read.) `<ul class="picks">` of coloured-`.spine` rows, **each pick showing its real book jacket** (2026-07-13 handoff B6 — near-mandatory in the genre; sourced like any plate image, e.g. Open Library / publisher jacket art).
```html
<ul class="picks">
  <li>
    <span class="spine" aria-hidden="true"></span>
    <span class="jacket"><img src="[verified jacket URL or /assets/cached/<hash>.jpg]" alt="Book cover of [Title] by [Author], [what the art shows]" loading="lazy"></span>
    <div>
      <h3>[Book / pick title]</h3>
      <p class="meta">[Genre · shape · note]</p>
      <p>[Why it's on the nightstand — two or three lines.]</p>
    </div>
  </li>
  <!-- typically 3 picks; spine colour is CSS-assigned by row position -->
</ul>
<p class="picks-credit mono">JACKETS · [SOURCE — e.g. OPEN LIBRARY COVERS · PUBLISHER EDITIONS]</p>
```
The closing `.picks-credit` mono line credits the jacket source for the rail in one place (jackets don't take individual `.plate-cap`s).

### The Desk — `the_desk` (content: `desk`)
The service department: **ONE** `.desk` container holding **1–2** `.deskcol` columns (drawn from Session / Ledger / Itinerary / Toolkit) — **NEVER 3+**, and never a column as its own band or nav entry. Each column carries the mandatory **`data-desk-column`** hook and **ends on a `.pin`** (its Do-This-Week action).
```html
<div class="desk">
  <div class="deskcol" data-desk-column>
    <h3>[Department name — e.g. The Session]</h3>
    <span class="mono sub">[DOMAIN · CONTEXT]</span>
    <p>[The read — what moved, why it matters. <b>[key number]</b>.]</p>
    <div class="pin">
      <div class="pinlbl mono">DO THIS WEEK · <b>[DEPARTMENT]</b></div>
      <p class="act">[The one concrete, named action — imperative, no hedge.]</p>
      <p class="why">[The criterion that makes THIS the pick — stated, not vibes.]</p>
    </div>
  </div>
  <!-- optionally ONE more .deskcol; 1–2 total, never 3+ -->
</div>
```

### The Threads — `the_threads` (content: `threads`)
"Previously on…" continuity (recap, not service — no pin). `.threads` > `.thread` rows: an `.ep` tag, then a title, a `.prev` recap line, and the current-state paragraph.
```html
<div class="threads">
  <div class="thread">
    <span class="ep">[SAGA · NAME  /  LIFE-THREAD · NAME]</span>
    <div>
      <h3>[Thread title]</h3>
      <p class="prev">Previously: [where it stood].</p>
      <p>[Where it stands now. <b>Next:</b> [what to watch].]</p>
    </div>
  </div>
  <!-- typically 3–6 threads -->
</div>
```

### Down the Rabbit Hole — `rabbit_hole` (content: `rabbit`)
The discovery ritual. A framed `.rabbit` block: a `.lbl`, a two-node `.chain` (from what you love → where you fall), then the prose invitation.
```html
<div class="rabbit">
  <span class="mono lbl">YOU LIKE THIS → SO TRY THIS</span>
  <div class="chain">
    <div class="node">
      <span class="mono cap">BECAUSE YOU LOVE</span>
      <span class="nm serif">[the known thing]</span>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="node">
      <span class="mono cap">YOU MIGHT FALL INTO</span>
      <span class="nm serif">[the rabbit hole]</span>
    </div>
  </div>
  <p>[The invitation — one rich paragraph. <em>Italic</em> for emphasis.]</p>
</div>
```

### On the Radar — `on_the_radar` (content: `radar`)
The forward calendar (distinct from the Release Radar, which lists media inside Screen & Sound; this lists dated events). `<ul class="radar">` of `.date` + `.ev` rows.
```html
<ul class="radar">
  <li>
    <span class="date">[MON · DD MON]</span>
    <span class="ev"><b>[Event]</b> — [why it matters, briefly].</span>
  </li>
  <!-- several rows -->
</ul>
```

### Do This Week — `do_this_week` (content: `closepin`)
The issue's single strongest action, pinned. One `.closepin`: a label, the action (`.act`, ends on a verb), and the human `.why` line.
```html
<div class="closepin">
  <div class="pinlbl mono">THE STRONGEST ACTION · <b>PIN IT TO THE FRIDGE</b></div>
  <p class="act">[The one action — imperative, concrete.]</p>
  <p class="why">[Why this one and why now — a human closing line.]</p>
</div>
```

### Colophon — `colophon` (content: `endnumbers`)
The issue accounted for: an `.endnumbers` grid of exactly **4** `.cell`s. The stitcher renders the colophon bar and sign-off after it — the writer supplies only the four cells.
```html
<div class="endnumbers">
  <div class="cell">
    <span class="mono k">[LABEL]</span>
    <span class="v serif">[value with an <em>accent</em> word]</span>
  </div>
  <!-- exactly 4 .cell -->
</div>
```

### Anchor Piece (SUPERSEDED for the weekly — legacy `.nav-card` vocabulary)

> **Superseded for the Standard Weekly (Transmission).** The `.is-anchor` / `.nav-card` / `.toc-row` / `.sec` vocabulary below does **not** exist in the Transmission stylesheet and is **not** produced by `stitch_weekly.py`. In the rebuilt weekly there is no anchor section and no navigator cards — emphasis comes from the movement/band spine and the Long Read. This block is retained only as historical reference; do not emit it in a weekly.

The anchored section adds `.is-anchor` to its `<section>` and its matching `.toc-row` in the Navigator:

```html
<!-- In Navigator: -->
<a href="#pixel" class="nav-card tech toc-row is-anchor"> ... </a>

<!-- Section: -->
<section class="sec tech-section is-anchor" id="pixel"> ... </section>
```

The anchored section opens with a stat-led or quote-led opener (see below) and runs 1.5-2× the normal lead article length.

### Section Opener Variants (use before `<h2>`)

```html
<!-- Stat-led (anchor pieces, occasional non-World openers) -->
<div class="opener-lead stat">
  <div class="stat-unit">
    <div class="stat-num">47</div>
    <div class="stat-label">[1-3 word label]</div>
  </div>
  <div class="stat-unit">
    <div class="stat-num">£2.4bn</div>
    <div class="stat-label">[label]</div>
  </div>
  <!-- 2-3 stat-units total -->
</div>
<h2>[Section heading]</h2>

<!-- Quote-led -->
<div class="opener-lead quote">
  “[A punchy, attributed quote that frames the section.]”
  <cite>— [Source]</cite>
</div>
<h2>[Section heading]</h2>
```

**Rotation rule (light):** World is always photo-led (default: hero image or watermark + h2). 1-2 other sections per issue may use stat-led or quote-led. Never use on more than 3 sections in a single issue.

### Drop-cap and Lead-in (long-form opener treatments)

```html
<p class="dropcap"><span class="lead-in">The first three to six</span> words sit in small-caps DM Sans bold while the very first letter lifts to 72px in the section's accent colour. Only use on the opening paragraph of a lead article, not on shorter items.</p>
```

- `.dropcap` on `<p>` — renders the first letter large in the section's accent colour.
- `.lead-in` on a `<span>` wrapping the first 3-6 words — small-caps DM Sans bold.
- Can be used together or independently. One per section maximum.

### Margin Note

```html
<aside class="margin-note">
  [Tufte-style aside — a genuinely useful observation, source note, or tangent. 15-40 words.]
</aside>
```

**Usage:** 1-3 per issue across long-form articles. Floats right on desktop, stacks inline on tablet/mobile. Never inside compact tables, also-cards, compare panels, or timelines. Best inside plain prose runs in World, Screen & Sound, Bookmark, or special-edition main stories.

### Meanwhile Section (Special Editions Only)
```html
<section class="sec world-section" id="meanwhile">
  <div class="sec-watermark">Meanwhile</div>
  <div class="sec-gradient-overlay"></div>
  <span class="section-label" style="color:var(--rose)">Meanwhile... — The Week's News</span>
  <h2>What Else Happened</h2>
  <p>[Intro line]</p>

  <div class="also" style="border-top:none;margin-top:0;padding-top:0;">
    <div class="also-title">[Category: World / Gaming / Sport / Entertainment]</div>
    <ul class="also-list">
      <li class="tier-hot"><strong>[Headline]</strong> — [One sentence]. <a href="[url]" style="color:var(--rose)">[Source]</a></li>
      <li class="tier-warm"><strong>[Headline]</strong> — [One sentence]. <a href="[url]" style="color:var(--rose)">[Source]</a></li>
      <li class="tier-note"><strong>[Headline]</strong> — [One sentence]. <a href="[url]" style="color:var(--rose)">[Source]</a></li>
    </ul>
  </div>
  <!-- Repeat for each category -->
</section>
```

---

## Key Container Rules

| Container | Purpose | Correct use | Wrong use |
|---|---|---|---|
| `.also-cards` | 2-column card grid | Multiple small summary cards (4+ items) | Wrapping a single detailed item |
| `.card-stack` | Horizontal scroll carousel | Multiple small cards in a row (3+) | Wrapping a single detailed item |
| `.split-60-40` | Asymmetric 2-column | One detailed item: text left, image+sidebar right | — |
| `.split-40-60` | Asymmetric 2-column (reversed) | One detailed item: sidebar left, text right | — |
| `.dual-col` | Symmetric 2-column | Two equal mini-articles side by side | Single items |
| `.timeline` | Vertical timeline | Sequential items (history, plans, steps, mistakes) | — |
| `.compare-panel` | Side-by-side comparison | Two things being compared (head-to-head) | Individual items that aren't comparisons |

**The golden rule:** if you're presenting one detailed item, use `.split-60-40`. If you're presenting multiple summary items, use `.also-cards` or `.card-stack`. Never mix these up.

---

## Starter Kit

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose, 50-80 words. Drop-cap on first paragraph. |
| Why This Matters | `sec world-section` | Prose + `.sidebar-float` or `.split-60-40` with a Signal Take callout |
| Essentials — overview grid | `sec shelf-section sec-opener` | `.also-cards` with all 5-7 items as small `.also-card` summary cards (fills 2-col grid correctly) |
| Essentials — each pick | (within same section) | `split-60-40`: left = `entry-quote` or `entry-bullets` + paragraphs + co-op/link line; right = `<img>` + `.sidebar` with stats. Separate picks with `.dyk`, `.breather`, `.pull-quote`, `.stat-bar` |
| Common Mistakes | `sec world-section` | `.timeline` > `.timeline-node` > `.timeline-date` ("Mistake 01") + `.timeline-content`. Split into two `.timeline` groups with a `.pull-quote` between them |
| One-Week Plan | `sec session-section` | `.timeline` > `.timeline-node` > `.timeline-date` ("Day 1" / "Monday") + `.timeline-content` with goal at end |
| Where to Go Deeper | `sec history-section sec-opener` | `.also-cards` grid with multiple `.also-card` items |
| Meanwhile | `sec world-section` | See universal pattern above |

## The Shortlist

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `chapter` | Short prose, 50-80 words. Drop-cap on first paragraph. |
| The Lens | `chapter` | `.lens` framed block — `.lens-eyebrow` ("The Lens") + `.lens-statement` italic + numbered `.lens-criteria` list. Followed by optional prose for context. |
| Top Picks | `chapter` | `.tier-band` with `data-tier` absent (defaults to top / rose) + `.tb-mark` ✦ + `.tb-label` "Top Picks". Each pick uses `.pick` alternating image/body layout + `.pick-tag` pill |
| Strong Picks | `chapter` | `.tier-band data-tier="strong"` (ember) + `.pick` items |
| Wildcards | `chapter` | `.tier-band data-tier="wildcard"` (teal) + `.pick` items |
| Also Worth Knowing | `chapter` | Horizon list (3-5 items) — `.also-cards` grid |
| The Cheat Sheet | `chapter` | `.cheat-sheet` table — see contract below |
| Meanwhile | `chapter` | See universal pattern above |

### The Lens contract

```html
<div class="lens">
  <div class="lens-eyebrow">The Lens</div>
  <p class="lens-statement">Picked for [the criteria, in one sentence]. Excluded anything that [counter-criterion, in another sentence].</p>
  <ol class="lens-criteria">
    <li>What we looked for, point 1.</li>
    <li>What we looked for, point 2.</li>
    <li>What disqualified candidates we considered.</li>
  </ol>
</div>
```

### The Cheat Sheet contract

```html
<table class="cheat-sheet">
  <thead><tr><th>#</th><th>Pick</th><th>Tier</th><th>Why</th></tr></thead>
  <tbody>
    <tr data-tier="top">     <td>1</td><td>Pick name</td><td>Top Pick</td>   <td>One-line why.</td></tr>
    <tr data-tier="top">     <td>2</td><td>Pick name</td><td>Top Pick</td>   <td>One-line why.</td></tr>
    <tr data-tier="strong">  <td>3</td><td>Pick name</td><td>Strong Pick</td><td>One-line why.</td></tr>
    <tr data-tier="wildcard"><td>4</td><td>Pick name</td><td>Wildcard</td>   <td>One-line why.</td></tr>
  </tbody>
</table>
```

`data-tier` accepts `top | strong | wildcard` — paints the tier-cell colour + the leading-rail under the rank number.

## The Aside (All Formats)

The Aside is a standalone mini-section placed between full sections for pacing. It has no navigator card and no watermark. 0-2 per issue, never forced, never back-to-back.

| Variant | Section class | Pattern |
|---|---|---|
| Image aside | `sec` (light/warm bg, distinct from neighbours) | `<section class="sec" style="background:var(--warm);padding:2.5rem 0">` with `<span class="section-label" style="color:var(--ember)">The Aside — [Topic Type]</span>` + `<h2>[Title]</h2>` + `.split-60-40` or `.split-40-60`: one side prose (150-300 words), other side `<img>`. Optional `.dyk` or `.pull-quote` inline. |
| Prose aside | `sec` (light/warm bg, distinct from neighbours) | Same section wrapper. Standalone prose with `.img-float-left` for a small image, or no image if text-only. A single `.pull-quote` or `.dyk` can substitute for the image. |

**Key constraints:**
- No `.sec-watermark`, no navigator card — this is not a full section
- Background must differ from both adjacent sections (use inline `style` override if needed)
- `section-label` format: "The Aside — A Thing" / "The Aside — A Moment" / "The Aside — A Discovery" / "The Aside — A Question" / "The Aside — A Skill"
- No `id` attribute needed (not linked from navigator)
- Keep component count minimal: 1-2 components max per Aside

## Deep Dive

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `chapter` | Short prose, 50-80 words |
| The Argument | `chapter` | `.argument` framed block — `.argument-eyebrow` ("The magazine's take") + `.argument-thesis` (large italic serif, the thesis) + `.argument-stance` (paragraph) |
| Main Story | `chapter` (×N) | Long-form prose. Body components: `.pullquote`, `.marginalia`, `.bignum`, `.bignum-row`, `figure.fig`, `figure.image-quote`, `.sp-ornament`, `.sp-kicker` |
| Keep Digging | `chapter` | `.keep-digging` cross-media grid of `.kd-item` cards |
| Meanwhile | `chapter` | See universal pattern above (only if the Deep Dive is replacing the standard weekly) |

### The Argument contract

```html
<div class="argument">
  <div class="argument-eyebrow">The magazine's take</div>
  <p class="argument-thesis">This issue reads the Yellow Turban Revolt as the first plague-religion convergence in Chinese history, not the peasant uprising it usually gets framed as.</p>
  <p class="argument-stance">Stance paragraph (~80-150 words) explaining what that frame buys, what it costs, and how the rest of the issue works around it. No hedging — the editor commits.</p>
</div>
```

### Keep Digging contract

Cross-media closing chapter. **Lean non-print** — aim for 5-9 items with at least 4 across `podcast / tv / film / game / video`. Books are allowed but should never dominate.

```html
<div class="keep-digging">
  <article class="kd-item" data-medium="podcast">
    <span class="kd-medium">Podcast</span>
    <h4 class="kd-title">The History of China Podcast</h4>
    <span class="kd-episode">Episode 49 — "The Yellow Turbans"</span>
    <p class="kd-why">Chris Stewart's hour-long narrative covers Zhang Jue's rise and the rebellion's collapse in a single sitting — the cleanest audio overview that doesn't bury the religious dimension.</p>
  </article>
  <article class="kd-item" data-medium="film">
    <span class="kd-medium">Film</span>
    <h4 class="kd-title">Red Cliff (2008)</h4>
    <p class="kd-why">John Woo's two-part epic on the war that finished off the Han — the direct sequel to the Yellow Turban story.</p>
  </article>
  <!-- … -->
</div>
```

`data-medium` accepts `podcast | tv | film | game | video | book`. **Podcasts must always carry a `<span class="kd-episode">` line naming the specific episode** — series-only references are forbidden. The same rule applies to TV where only a couple of episodes touch the topic. Every item must be real and verifiable; the researcher surfaces these in Phase 3 with URLs.

### The special cover contract (v8.24 — all non-holiday specials)

A bare title + deck cover reads as unfinished. The full cover:

```html
<header class="cover" id="top">
  <div class="cover-meta"><span>Deep Dive</span><span>31 May 2026</span></div>
  <div class="cover-body">
    <p class="cover-eyebrow">Section / series mark</p>
    <h1 class="cover-title">The headline with an <em>accent</em> word</h1>
    <p class="cover-deck">A one-to-two sentence deck — what the issue is.</p>
    <div class="cover-slogan"><p>A single epigraph line — the thesis in one breath.</p></div>
    <div class="cover-tags">
      <span class="tag">Key theme</span><span class="tag">Another</span>
      <span class="tag">Five to eight</span><span class="tag">keyword pills</span>
    </div>
  </div>
  <div class="cover-foot">
    <span class="cf-left">Left meta — e.g. "Twelve chapters · one sitting"</span>
    <span class="cover-scroll">Begin reading ↓</span>
    <span class="cf-right">Right meta — e.g. "Augustus → Nero · sourced"</span>
  </div>
</header>
```

`.cover-tags` (5–8 short keyword pills) and the three-part `.cover-foot` are required on every non-holiday special. `.mast` precedes the cover as before.

### Layout-variety components (v8.24 — break up the prose)

A literary special (Deep Dive, Versus, Rewind, Season Review) must not be an unbroken column. Within `.chapter-body`, mix these to land a visual break every 2–4 paragraphs:

| Component | Markup | Use for |
|---|---|---|
| Floated figure | `<figure class="fig is-half">` (add `.is-left` to alternate) | a portrait/coin/object beside the prose; text wraps |
| Gutter marginalia | `<aside class="marginalia"><span class="m-label">Label</span><p>…</p></aside>` | a short context note / definition; floats into the RIGHT gutter |
| Image-quote | `<figure class="image-quote"><img …><blockquote><p>quote</p><cite>— src</cite></blockquote></figure>` | a portrait with a primary-source line across it |
| Stat row | `<div class="bignum-row"><div class="bignum"><div class="bignum-value">15,000</div><div class="bignum-label">…</div></div>…</div>` | 2–4 headline numbers |
| Pull-quote | `<blockquote class="pullquote"><p>…</p><cite>— …</cite></blockquote>` | a resonant line on its own |
| Parallax band | `<figure class="fig is-wide sp-parallax-band"><div class="sp-band-frame"><img …></div><figcaption>…</figcaption></figure>` | ONE big cinematic SCENE image per issue — sits in a fixed-height slot and pans behind it on scroll |

**Parallax discipline.** The `.sp-parallax-band` is the *only* element that parallaxes, and it is reserved for **one or two genuinely cinematic full-width SCENE photos/paintings per issue** (a battlefield, an assassination scene, a wide cityscape) — never portraits, busts, coins, maps, charts or diagrams (those stay static and whole, so nothing crops). The `<img>` MUST be wrapped in `<div class="sp-band-frame">` so the caption stays outside the clip. Do not put `.sp-parallax-band` on more than ~2 figures; over-using it makes the issue seasick.

Do **not** use the retired `.sp-spread`/`.sp-rail` three-column layout (the empty left rail wastes space). Marginalia always floats right.

## The Countdown

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose |
| Event Overview | `sec world-section sec-opener` | `split-60-40` with image + `.sidebar` (key facts), `stat-bar` for numbers |
| Logistics | `sec session-section` | `.timeline` for schedule/itinerary, `.sidebar` for tips, `.dyk` for facts |
| What to Watch/Read/Play | `sec shelf-section sec-opener` | `.also-cards` grid (multiple items) |
| Day-by-Day Plan | `sec session-section` | `.timeline` > `.timeline-node` per day |
| Surprising Facts | `sec history-section sec-opener` | `.dyk` boxes, `entry-stat`, prose |
| Meanwhile | `sec world-section` | See universal pattern above |

## The Season Review

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `chapter` | Short prose |
| Full Narrative | `chapter` (×N) | Long-form prose. Body components: `.pullquote`, `.marginalia`, `figure.fig`, `.bignum-row` for headline counts |
| The Scorecards | `chapter` | `.scorecards` grid of `.scorecard[data-tier]` cards — see contract below |
| What's Next | `chapter` | Single-chapter forward look, 400-600 words, no scorecards |
| Meanwhile | `chapter` | See universal pattern above |

### Scorecard contract

```html
<div class="scorecards">
  <article class="scorecard" data-tier="hot">
    <div class="sc-head">
      <h4 class="sc-name">Lautaro Martínez</h4>
      <div class="sc-score">8.4</div>
    </div>
    <div class="sc-bar" style="--score: 84"></div>
    <p class="sc-verdict">Best season since he signed; deserved the Scudetto MVP.</p>
  </article>
  <article class="scorecard" data-tier="warm">…</article>
  <article class="scorecard" data-tier="cold">…</article>
</div>
```

`data-tier` accepts `hot | warm | cold` — paints the top-border colour, the `.sc-score` colour, and the `.sc-bar` gradient. `--score` is `0-100`; the bar fills that percentage. Aim for 8-12 scorecards per Season Review.

## The Starter Kit

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `chapter` | Short prose |
| Why This Matters | `chapter` | Prose, 200-300 words; close with an optional `.sk-takeaway` conviction band — see contract below |
| The Essentials | `chapter` | Detailed picks (5-7) as cross-format `.pick` + `.pick-stats`; the `.essentials` numbered-ring list is only for short concept sub-lists |
| Common Mistakes | `chapter` | `.sk-mistake` callout list (ringed × badge + optional `.sk-mistake-fix` line) — see contract below |
| The One-Week Plan | `chapter` | `.week-plan` vertical timeline — see contract below |
| Where to Go Deeper | `chapter` | `.also-cards` grid (3-5 items) |
| Meanwhile | `chapter` | See universal pattern above |

### The One-Week Plan contract

The killer feature. Seven `.wp-day` items in an ordered list, day-badged on the left, instruction body on the right. Each day must commit to a specific action — vague "experiment with what you've learned" entries are forbidden.

```html
<ol class="week-plan">
  <li class="wp-day">
    <div class="wp-day-mark">
      <span class="wp-day-num">Day 1</span>
      <span class="wp-day-name">Mon</span>
    </div>
    <div class="wp-day-body">
      <h4 class="wp-day-title">Listen to Wolf 359, episodes 1–4</h4>
      <p>Why this entry point: episode 4 is the first one that gives the world room to breathe; the first three are scene-setting.</p>
    </div>
  </li>
  <li class="wp-day">
    <div class="wp-day-mark"><span class="wp-day-num">Day 2</span><span class="wp-day-name">Tue</span></div>
    <div class="wp-day-body"><h4 class="wp-day-title">Pause; reflect</h4><p>If Wolf 359 didn't grab you by episode 4, jump to Day 3 — try The Magnus Archives instead.</p></div>
  </li>
  <!-- … through Day 7 -->
</ol>
```

### Common Mistakes contract

A `.sk-mistake` list. Each `<li>` gets a ringed × badge; the warning is the lead text, and an optional `.sk-mistake-fix` span gives the "do this instead" correction (rendered with a → marker). Warnings must be genuinely useful and specific — not generic "don't give up".

```html
<ul class="sk-mistake">
  <li>Starting with the most acclaimed series first — you'll burn out on density before you've built the listening habit.
    <span class="sk-mistake-fix">Start with a tight, plot-driven show and earn the harder ones.</span>
  </li>
  <li>Treating every episode as mandatory — completionism kills the casual entry point.
    <span class="sk-mistake-fix">Skip the filler arcs; the on-ramp matters more than coverage.</span>
  </li>
</ul>
```

### The Takeaway contract

An optional single-line conviction band closing Why This Matters. One mono eyebrow + one italic sentence on a hairline-bordered paper band. The lighter, paper-ground cousin of Deep Dive's `.argument` — use once, not repeatedly.

```html
<div class="sk-takeaway">
  <span class="sk-takeaway-mark">The Takeaway</span>
  <p>You don't need to listen to everything — you need the three that prove the medium is worth your commute.</p>
</div>
```

### The Pick component (cross-format — Starter Kit Essentials, Shortlist, Next)

A rich recommendation block. The image **floats** and the writeup wraps beside it, then reflows to full width once it clears the image bottom — so a short image next to long text leaves **no dead column** (and a pick with no image is simply full-width text). The image MUST be a `figure`-wrapped `.pick-img` — **never a bare `<img>`** (a bare img breaks the float hook and the caption/credit contract). Image side alternates automatically by pick order; on narrow screens it stacks on top. Every Essentials pick must carry a real, sourced image.

```html
<article class="pick">
  <figure class="fig pick-img-fig">
    <img class="pick-img" src="…" alt="…">
    <figcaption class="fig-caption">Caption <span class="fig-credit">Source</span></figcaption>
  </figure>
  <div class="pick-body">
    <span class="pick-tag">Top Pick</span>
    <h3>Pick title</h3>
    <p>Multi-paragraph writeup…</p>
    <aside class="pick-stats">
      <dl>
        <dt>Seasons</dt><dd>3</dd>
        <dt>Episodes</dt><dd>61</dd>
        <dt>Rating</dt><dd>TV-Y7</dd>
        <dt>Where</dt><dd>Netflix</dd>
      </dl>
    </aside>
  </div>
</article>
```

## The Rewind

## The Versus

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose |
| Tale of the Tape | `sec world-section sec-opener` | `.compare-panel` (the core component), `.stat-bar`, `big-number` |
| The Case for A | `sec shelf-section sec-opener` | `split-60-40` with image, `entry-stat`, `entry-bullets`, `pull-quote` |
| The Case for B | `sec session-section` | `split-60-40` with image, `entry-stat`, `entry-bullets`, `pull-quote` |
| The Verdict | `sec world-section` | `.compare-panel` summary, prose with strong editorial opinion |
| Meanwhile | `sec world-section` | See universal pattern above |

## The Rewind

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `chapter` | Short prose |
| The Period in Numbers | `chapter` | `.bignum-row`, `.year-band` 12-month rail with high/low markers |
| The Throughline | `chapter` | `.chapter-head.is-throughline` with `.throughline-mark` eyebrow + italic curly-quoted title — see contract below. The chapter that names what the period was about. |
| Highs | `chapter` | `.rewind-cards` grid of `.rewind-card` items |
| Lows | `chapter` | `.rewind-cards` grid with `.is-low` modifier on cards |
| What We Missed | `chapter` | Prose with `.pullquote` and `.marginalia` |
| The Memory Test | `chapter` | `.memory-test` 3-column grid (`.mt-col.mt-stick` / `.mt-might` / `.mt-fade`) — Rewind's second killer feature |
| Picks of the Period | `chapter` | `.rewind-cards` grid |
| Meanwhile | `chapter` | See universal pattern above |

### The Throughline contract

```html
<section class="chapter">
  <header class="chapter-head is-throughline">
    <div class="throughline-mark">The Throughline</div>
    <h2 class="chapter-title">A year of new launches</h2>
  </header>
  <div class="chapter-body">
    <p>The chapter that names what this period was actually about…</p>
  </div>
</section>
```

`is-throughline` on the chapter-head hides the chapter-numeral and italicises the chapter title with curly quotes painted in accent. The `.throughline-mark` eyebrow sits above the title with rule marks either side of it. Use on exactly one chapter per Rewind.

## The Next

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose |
| The Itch | `chapter` | Prose — names exactly what made the original work for this reader. Single anchor for every pick that follows |
| The Closest Next Step | `chapter` | `<div class="next-tier" data-step="I">Closest Next Step</div>` + pick prose + `.on-ramp` block |
| One Step Sideways | `chapter` | `<div class="next-tier" data-step="II">One Step Sideways</div>` + pick prose + `.on-ramp` block |
| The Wildcard | `chapter` | `<div class="next-tier is-wildcard" data-step="III">The Wildcard</div>` + pick prose + `.on-ramp` block |
| If You Only Try One | `chapter` | `.only-one` dark slab with star seal — single pick, no hedging, ~200-300 words |
| Where to Go After That | `chapter` | Brief horizon list (3-5 items), no on-ramp required |
| Meanwhile | `chapter` | See universal pattern above |

### On-Ramp markup contract

Every pick in Next includes one `.on-ramp` block. The block renders as a stepped track with three glyphed nodes (▶ Start / ⏸ Reassess / → Then) connected by a vertical accent line. Each row must carry `data-step="start|reassess|then"` so the correct glyph paints.

```html
<div class="on-ramp">
  <div class="on-ramp-row" data-step="start">
    <span class="on-ramp-label">Start with</span>
    <span class="on-ramp-body">Episode 4 — the first one that lets the world breathe.</span>
  </div>
  <div class="on-ramp-row" data-step="reassess">
    <span class="on-ramp-label">Reassess at</span>
    <span class="on-ramp-body">End of the first arc, ~episode 6.</span>
  </div>
  <div class="on-ramp-row" data-step="then">
    <span class="on-ramp-label">Then</span>
    <span class="on-ramp-body">If it landed, head to season 2.</span>
  </div>
</div>
```

## The Lookahead

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose framing the window |
| The Window in Numbers | `chapter` | `.bignum-row` — total events / don't-miss count / worth-a-look count / skip count |
| The Calendar | `chapter` | `.calendar` `<ol>` of `.cal-row` entries with `data-verdict`; optional `<li class="cal-week">` dividers between weeks |
| The Crunch Weeks | `chapter` | One `.crunch-week` callout per dense week — warning chip + `.crunch-list` `<dl>` with tier-coloured Prioritise / Defer / Skip badges |
| What Else Is Brewing | `chapter` | Brief horizon items without firm dates — `.also-list` style |
| Meanwhile | `chapter` | See universal pattern above |

### Calendar row contract

```html
<ol class="calendar">
  <li class="cal-week">Week of 14 Jun</li>
  <li class="cal-row" data-verdict="hot">
    <div class="cal-when">
      <span class="cal-date">14 Jun</span>
      <span class="cal-where">Football · PL</span>
    </div>
    <div class="cal-body">
      <h4>Arsenal vs Manchester City — title race decider</h4>
      <p>Two games left, two points apart. This is the one.</p>
    </div>
    <div class="cal-verdict">
      <span class="cal-verdict-chip">Don't miss</span>
      <span class="cal-reason">Title decider on the second-to-last weekend.</span>
    </div>
  </li>
</ol>
```

`data-verdict` must be one of `hot` / `warm` / `wait` / `skip` — the chip glyph (★ / ◉ / ⏱ / ✕), the row's left rail colour, and the row's background tint all paint from this attribute.

### Crunch Week contract

```html
<aside class="crunch-week">
  <div class="crunch-header">
    <span class="crunch-label">Crunch week</span>
    <h4 class="crunch-when">Week of 14 Jun</h4>
  </div>
  <dl class="crunch-list">
    <dt data-tier="hot">Prioritise</dt><dd>Title decider — can't be re-experienced.</dd>
    <dt data-tier="wait">Defer</dt><dd>Canadian GP — strong race, no championship stakes.</dd>
    <dt data-tier="skip">Skip</dt><dd>The Long Walk — sits in "wait for reviews".</dd>
  </dl>
</aside>
```

## The Field Guide

Field Guide is a shared hype-and-practical read (45/55 ratio, hype front-loaded). Section order below is canonical — The Opening and The Unmissables MUST come before Quick Orientation so the first ~20% of the issue is hype-dominant.

| Section | Section class | Pattern |
|---|---|---|
| The Opening | `sec foreword-section sec-opener` | Atmospheric lead (400–600 words). Prose-only with 1–2 establishing images. **No `.also-cards`, no `.stat-bar`, no prices, no lists.** Sets the emotional register for the trip |
| The Unmissables | `sec shelf-section sec-opener` | Emotional centrepiece (1,500–2,500 words, 6–10 picks). Use `.tier-hot` treatment or a dedicated `.unmissables` pattern. Each pick = sensory write-up + "Why It's Here" angle + image + small practical footer (price, booking, timing). Practical detail lives inside the prose, not as a bolt-on card grid |
| Quick Orientation | `sec world-section sec-opener` | Map image (sourced, not AI), `split-60-40` with key facts sidebar |
| Category Sections | `sec shelf-section sec-opener` (food), `sec session-section` (activities), etc. | `.also-cards` for option grids, `.compare-panel` for head-to-heads, `.stat-bar` for prices, `.sidebar` for tips, `.dyk` for trivia. Use `tier-hot`/`tier-warm`/`tier-note` for ranking |
| Meanwhile | `sec world-section` | See universal pattern above |

---

## Holiday Identity — Countdown + Field Guide ONLY (v8.12)

Countdown and Field Guide use a separate visual identity from every other special edition. The component patterns above for these two formats are SUPERSEDED by the `.hol-*` vocabulary below.

**Activation:** `<body class="is-special" data-special="countdown">` or `data-special="field-guide"`.

**On these two formats, the default chrome above is hidden by tier 36 CSS.** Using `.sp-chapter-gate`, `.sp-spread`, `.sp-pull-break`, `.sp-marginalia`, `.sp-brief`, `.sp-dash`, `.sp-chapter-chrome`, or `.unmissables` / `.unmissable` will produce blank stretches in the rendered output.

**The structural shape:** masthead → cover → kicker strip → Half I (`.hol-half--one`) → transit (`.hol-transit`, multi-venue only) → Half II (`.hol-half--two`, multi-venue only) → meanwhile (`.hol-meanwhile`). Single-venue issues drop the transit and Half II, replacing them with 1–2 interior `.hol-marquee` breaks within Half I.

### Canonical markup index

| Component | Class | Purpose |
|---|---|---|
| Masthead | `.hol-masthead` | Page-top brand strip with format badge + meta |
| Cover | `.hol-cover` | Full-bleed indigo poster (cover hero) |
| Cover collage | `.hol-cover__collage` | Absolutely-positioned scrapbook on the cover right side |
| Live countdown | `.hol-countdown` | Live tick grid driven by JS (Countdown format primarily) |
| Kicker strip | `.hol-kicker-strip` | Cream-paper promise of the issue between cover and Half I |
| Half | `.hol-half` + `--one` / `--two` | The major structural unit. Two per multi-venue issue, one per single-venue |
| Half opener | `.hol-half__opener` | Big stacked title for each half (tag + serif title + skewed subtitle + pills) |
| Transit | `.hol-transit` | Single cinematic break between Half I and Half II (multi-venue only) |
| Polaroid | `.hol-polaroid` | Rotated photo card with washi tape + handwritten caption |
| Postcard | `.hol-postcard` | Indigo greeting front + handwritten lined back |
| Stamp | `.hol-stamp` (+ `--brass` / `--emerald` / `--mustard`) | Circular rubber-stamp seal |
| Anchor | `.hol-anchor` | Feature article block with tilted border + rotated badge + script note |
| Unmissable row | `.hol-unmissable` (+ `--reverse`) | Alternating photo + parchment card row. Field Guide picks live here |
| Don't miss | `.hol-dont-miss` | Rotated ruby block with tilted shadow numerals |
| Marquee | `.hol-marquee` | Kinetic horizontal scroll banner (also the single-venue rhythm beat) |
| Chalkboard | `.hol-chalkboard` | Half II tilted menu/list card |
| Meanwhile | `.hol-meanwhile` | Closing dark block with mega watermark |
| Subscribe | `.hol-subscribe` | Rotated subscribe card inside `.hol-meanwhile` |
| Footer row | `.hol-footer-row` | Page-bottom brand + links + hand-script tagline |

### Full snippets

See `references/pre-flight.md` § 3 *Canonical Markup Snippets* → *Holiday issue scaffold*. The snippets there are the contract — copy-paste, never invent variations.

### Anti-patterns (Countdown + Field Guide only)

- `<div class="sp-chapter-gate">` — does not render on holiday issues. Tier 36 hides it.
- `<aside class="sp-marginalia">` — use `.hol-stamp` or `.hol-polaroid` instead.
- `<div class="sp-spread">` — holiday issues do not use the three-column spread. Use `.hol-half__inner` plus content components.
- `<div class="unmissables">...<div class="unmissable">` — holiday issues use `.hol-unmissable` (one row at a time, alternating sides).
- `<section data-sp-chapter ...>` — not needed; holiday halves are plain `<section class="hol-half hol-half--one">` and `<section class="hol-half hol-half--two">`.
- Coral colour anywhere (`#E8384F`, `var(--sp-accent-primary)`) — not used on holiday issues. Use brass (`var(--hol-brass)` or `var(--hol-brass-light)`) for the primary accent role.
- More than one `.hol-transit` in an issue — exactly one for multi-venue, none for single-venue.
- Two halves of the same type in one issue — `.hol-half--one` then `.hol-half--one` again is wrong. Half I is always indigo/celestial; Half II is always terracotta/savannah.

### Half/Transit decision tree

```
Is the issue a Countdown or Field Guide?
├── No  → use the default chrome patterns above (sp-chapter-gate, sp-spread, etc).
└── Yes → does the trip have 2+ headline venues?
          ├── Yes (e.g. Efteling + Beekse Bergen):
          │   Cover → Kicker → Half I (--one) → Transit → Half II (--two) → Meanwhile
          └── No (single venue):
              Cover → Kicker → Half I (--one) with 1-2 interior marquee breaks → Meanwhile
```
