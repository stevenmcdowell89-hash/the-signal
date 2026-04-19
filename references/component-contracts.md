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
| Foreword | `sec` (light bg) | Short prose, 50-80 words |
| Reading Paths | `sec session-section` | Three `.col-card` items in a `.dual-col` or standalone list: 2-min / 10-min / 30-min paths |
| Main Story | `sec world-section sec-opener` | Long-form prose broken up with `split-60-40` (images + sidebars), `entry-stat`, `pull-quote`, `dyk`, `timeline`, `stat-bar`, `compare-panel`. Multiple sub-sections with `<h3>` headers |
| Meanwhile | `sec world-section` | See universal pattern above |

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

## The Blueprint

| Section | Section class | Pattern |
|---|---|---|
| Foreword | `sec` (light bg) | Short prose |
| The Goal | `sec world-section sec-opener` | `entry-stat` for target, `split-60-40` with `.sidebar` |
| Current State | `sec session-section` | Prose + `.sidebar` or `.compare-panel` (current vs target) |
| Decision Points | `sec world-section` | `.compare-panel` for each decision (Option A vs Option B), repeated. This is the core section |
| Phased Plan | `sec session-section` | `.timeline` > `.timeline-node` per phase |
| Tools & Resources | `sec history-section sec-opener` | `.also-cards` grid |
| Risks & Pitfalls | `sec world-section` | `.timeline` with risk items |
| First Steps This Week | `sec session-section` | `.timeline` or numbered prose |
| Meanwhile | `sec world-section` | See universal pattern above |

## The Field Guide

| Section | Section class | Pattern |
|---|---|---|
| Quick Orientation | `sec world-section sec-opener` | Map image (sourced, not AI), `split-60-40` with key facts sidebar |
| Category Sections | `sec shelf-section sec-opener` (food), `sec session-section` (activities), etc. | `.also-cards` for option grids, `.compare-panel` for head-to-heads, `.stat-bar` for prices, `.sidebar` for tips, `.dyk` for trivia. Use `tier-hot`/`tier-warm`/`tier-note` for ranking |
| The Don't-Miss List | `sec world-section` | Numbered list or `.also-cards` with the absolute must-dos |
| Meanwhile | `sec world-section` | See universal pattern above |
