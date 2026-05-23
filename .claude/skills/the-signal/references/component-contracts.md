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

### Footer
```html
<footer class="footer" id="footer">
  <div class="footer-brand">The Signal<span>.</span></div>
  <div class="footer-issue">[Format] · Issue #[N] · [Date]</div>
  <p class="footer-note">[Closing note]</p>
</footer>
```

### Colophon (Standard Weekly — end of issue, before Footer)
```html
<section class="colophon" id="colophon">
  <div class="colophon-mast">The Signal<span>.</span></div>
  <div class="colophon-sub">Issue in Numbers · Next Week · A Fact</div>
  <div class="colophon-grid">
    <div class="colophon-block">
      <div class="colophon-block-label">Issue in Numbers</div>
      <ul class="colophon-stats">
        <li><strong>[N]</strong> words</li>
        <li><strong>[N]</strong> sections</li>
        <li><strong>[N]</strong> links</li>
        <li><strong>[N]</strong> images</li>
        <!-- If anchor ran: -->
        <li>Anchor: <strong>[Section Name]</strong></li>
      </ul>
    </div>
    <div class="colophon-block colophon-next">
      <div class="colophon-block-label">Next Week</div>
      <p>[1-2 sentences teasing what's coming — tracked story, rotating section due, event on horizon. Editor's note tone.]</p>
    </div>
    <div class="colophon-block colophon-fact">
      <div class="colophon-block-label">A Fact</div>
      <p>[One curious fact unrelated to this issue's stories. 20-40 words. Verifiable, genuinely interesting.]</p>
    </div>
  </div>
  <div class="colophon-sign">Issue #[N] · [Date] · [Standing tagline]</div>
</section>
```
**Placement:** between On the Radar and the Footer. Single full-width block on paper background. Standard weekly only — special editions already have their own sign-off via Meanwhile.

### Anchor Piece (Standard Weekly — every 4th issue)

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

**Usage:** 1-3 per issue across long-form articles. Floats right on desktop, stacks inline on tablet/mobile. Never inside compact tables, also-cards, compare panels, or timelines. Best inside plain prose runs in World, Screen & Sound, The Shelf, or special-edition main stories.

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
| Foreword | `sec` (light bg) | Short prose, 50-80 words. Drop-cap on first paragraph. |
| The Lens | `sec world-section sec-opener` | Prose (150-250 words) explaining the criteria. Optional `.sidebar-float` or `.dyk` with a key principle. Keep it tight — this frames, it doesn't lecture. |
| The Shortlist — tier headers | (within `sec shelf-section sec-opener`) | Use `<h3>` tier labels: "Top Picks", "Strong Picks", "Wildcards". Styled with `.section-label` or inline accent colour. |
| The Shortlist — Top Picks (2-3) | (within same section) | `split-60-40`: left = `entry-quote` or `pull-quote` hook + paragraphs + key detail line (price/link); right = `<img>` + `.sidebar` with stats. One pick gets a "Top Pick" badge (use `.entry-stat` with star icon). Separate picks with `.dyk`, `.breather`, `.stat-bar` |
| The Shortlist — Strong Picks (2-3) | (within same section) | `dual-col` or sequential `.split-60-40` with smaller sidebars. Still opinionated, still has stats, just less space per pick. Image optional. |
| The Shortlist — Wildcards (1-2) | (within same section) | `split-60-40` or `split-40-60` (reversed for visual variety). Each needs a "Why this is here" callout — use `.dyk` or `.entry-question` component. |
| Also Worth Knowing | `sec session-section` | `.also-cards` grid with 4-8 `.also-card` items. Each card: name, 1-2 sentences, key stats line. This correctly uses the multi-item 2-col grid. |
| The Cheat Sheet | `sec history-section sec-opener` | HTML `<table>` with `.compare-table` class, or a `.compact-grid`. All picks (main 7 + Also Worth Knowing) with key attributes as columns. Topic-dependent columns. Designed as a reference card. |
| Meanwhile | `sec world-section` | See universal pattern above |

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
| Foreword | `sec` (light bg) | Short prose |
| Full Narrative | `sec world-section sec-opener` | Long-form with `split-60-40`, `pull-quote`, `entry-stat`, `timeline` for key moments |
| Data & Stats | `sec` (light bg) | `.stat-bar`, `big-number-row`, tables, `.compact-grid` |
| Ratings | `sec shelf-section sec-opener` | `.also-cards` with rating dots per item, `compare-panel` for highs vs lows |
| What's Next | `sec session-section` | Prose + `.sidebar` |
| Meanwhile | `sec world-section` | See universal pattern above |

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
| Foreword | `sec` (light bg) | Short prose |
| The Period in Numbers | `sec world-section sec-opener` | `.stat-bar`, `big-number-row`, multiple `entry-stat` |
| Highs | `sec shelf-section sec-opener` | `.also-cards` for items, rating dots, `pull-quote` |
| Lows | `sec world-section` | `.also-cards`, `entry-quote` |
| What We Missed | `sec session-section` | `.timeline` or `.also-cards` |
| What Stuck | `sec history-section sec-opener` | `split-60-40`, `pull-quote` |
| Picks of the Period | `sec shelf-section sec-opener` | `.also-cards` with rating dots |
| Meanwhile | `sec world-section` | See universal pattern above |

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
