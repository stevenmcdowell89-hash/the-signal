# Furniture Core — component catalog (`assets/css/core/`)

The theme-neutral furniture layer (L0) every skin sits on. Extracted from the
holiday layers' universal bucket per the design-system unification spec §2.1.
All class names are `mx-`-prefixed; nothing here collides with the weekly's
`sp-*`/`hol-*` marker gates.

**Load order (all seven, always):**

```
core/00-contract.css   tokens · six voices · base register · Law-8 floors
core/10-ephemera.css   framed objects: cards, mail card, stamp, ticket, coaster, quote, shelf
core/11-ledgers.css    facts ledger, ranked entries, rank chips, tier pills, stat band, cheat-sheet, scorecard
core/12-plates.css     numbered plates, anchor blocks, zig-zag entries, don't-miss
core/13-chrome.css     masthead, covers, kicker, act opener, scene grounds, transit, marquee, countdown
core/14-motion.css     motion tiers + signature hooks + global reduced-motion gate
core/15-responsive.css 390px stacking, chrome reservation, table policy, floor re-assertion
```

Working proof: `tools/fixtures/core-kitchen-sink.html` uses every component
across two acts. Render it with `tools/render.mjs`; measure with
`tools/measure-issue.mjs`.

---

## 1 · Activation and the act system

```html
<body data-mx data-motion="tier1" data-mx-chrome="pill">
  …
  <section data-act="night" class="mx-ground-starfield mx-ground-grain">
    <div class="mx-wrap"> …act content… </div>
  </section>
</body>
```

- `data-mx` on `<body>` switches the core on.
- `data-motion="tier0|tier1|tier2"` picks the motion tier (see §7).
- `data-mx-chrome="pill"` declares that the archive back pill ships on this
  page; core then reserves the top-left zone (masthead/cover padding) and
  fades the pill out on scroll (`15-responsive`). **Never ship the pill
  without this attribute.**
- Every act is a `section[data-act="…"]` that remaps the `--mx-*` palette for
  its subtree. Acts are declared per issue (skin or motif pack), e.g.:

```css
[data-act="night"] {
  --mx-paper:#141b33; --mx-ink:#f0e9d6; --mx-accent:#d9b66a; /* …etc */
}
```

**Law 1: an act's ground is never a flat single colour.** Stack exactly one
scene-ground utility on each act section:

| class | paints |
|---|---|
| `.mx-ground-starfield` | two offset dot grids + sparse sparkles from act tokens |
| `.mx-ground-gradient-sky` | vertical wash paper → accent/support mixes |
| `.mx-ground-pattern` | tiled `--mx-pattern` art (hatch fallback when unset); add `mx-ground-pattern--has-art` when a pack supplies art |
| `.mx-ground-grain` | SVG turbulence grain overlay, opacity `--mx-grain` |

Grounds may combine (e.g. `mx-ground-starfield mx-ground-grain`). Keep act
content inside `.mx-wrap` (it carries the z-index that sits above grounds).

## 2 · Token contract (~30 custom properties, `00-contract.css`)

Palette (re-scopable per act): `--mx-paper` `--mx-ink` `--mx-ink-soft`
`--mx-accent` `--mx-accent-ink` `--mx-accent-2` `--mx-accent-2-ink`
`--mx-support-1` `--mx-support-2` `--mx-hair`.

Object surfaces: `--mx-card` `--mx-card-ink` `--mx-card-edge`
`--mx-card-window` `--mx-tape` `--mx-ghost` `--mx-quote-bg` `--mx-shadow`
`--mx-hand-ink` `--mx-stamp-ink`.

Art slots (motif packs): `--mx-pattern` (tile), `--mx-glyph` (currentColor via
`mask-image`, use with `.mx-glyph`), `--mx-band`, `--mx-grain` (opacity).

Scenography: `--mx-tilt` (base object rotation; components vary it via
`nth-of-type`).

Type voices (family indirection only — self-hosted files are the bundler's
job): `--mx-t-chunk` `--mx-t-tall` `--mx-t-script` `--mx-t-hand`
`--mx-t-serif` `--mx-t-mono` (+ `--mx-t-body` convenience). Never link
remote fonts.

Law-8 floors, baked in as CSS defaults: `--mx-micro: 0.72rem` (every core
micro-label uses `font-size: max(0.72rem, var(--mx-micro))`), `--mx-measure:
62ch` with a hard `min(…, 68ch)` cap on `.mx-body`.

Dark mode is token-level: a `prefers-color-scheme: dark` block remaps the
neutral tokens on `[data-mx]` (acts keep their declared palettes);
`data-mx-scheme="dark"` forces it, `data-mx-scheme="locked"` opts a page out.

## 3 · Scenography contract (Law 1)

**Every ephemera object ships with ≥2 scenography cues by default** —
rotation (1–3°, varied per `nth-of-type`), a fastener rendered as a
pseudo-element (no extra markup), and a shadow on card stock. Flattening is
an explicit opt-out: add **`.mx-flat`** (kills tilt + fastener, softens
shadow). There is no upright shadowless default, and no markup you can forget
that produces one.

**Real-image contract (F-6):** a photo slot is a real `<img src alt>`
(object-fit: cover) inside the object's window; CSS-drawn art uses
`role="img"` + `aria-label` on the window element. Never a bare
background-image div.

## 4 · Event census contract

Every countable component instance carries `data-mx-event="<type>"` on its
outermost element. `tools/measure-issue.mjs` prefers these markers over
heuristics. Types (closed list): `figure` · `ephemera` · `ledger` ·
`statband` · `quote` · `plate` · `chart` · `marquee` · `cheatsheet`.

Default attribution: `.mx-card`/`.mx-card--mail`/`.mx-stamp`/`.mx-ticket`/
`.mx-coaster` → `ephemera` (a chart inside a card window → `chart`);
`.mx-quote` → `quote`; `.mx-ledger`/`.mx-ranked`/`.mx-scorecard` → `ledger`;
`.mx-numbers`/`.mx-countdown` → `statband`; `.mx-plate`/`.mx-actopen` →
`plate`; `.mx-anchor`/`.mx-zig__entry` → `figure`; `.mx-transit`/
`.mx-marquee` → `marquee`; `.mx-cheat`/`.mx-dontmiss` → `cheatsheet`.
Chrome (`.mx-mast`, `.mx-footer`, kickers) is never marked.

## 5 · Ephemera (`10-ephemera.css`)

### Pinned/taped card (polaroid descendant)
```html
<figure class="mx-card" data-mx-event="ephemera">
  <div class="mx-card__window">
    <img src="/assets/cached/img.jpg" alt="What the reader sees">
  </div>
  <figcaption class="mx-card__caption">hand-written caption line</figcaption>
  <span class="mx-card__credit">Photo · Named Source</span>
</figure>
```
Variants: `--pin` (pushpin), `--corner` (photo corners), `--ruled`
(index-card ruling; put `<div class="mx-typed"><b>KEY:</b> value…</div>` in
the window), `--wide` (420px). CSS-drawn window:
`<div class="mx-card__window" role="img" aria-label="…">…css art…</div>`.

### Mail card (postcard descendant)
```html
<figure class="mx-card--mail" data-mx-event="ephemera">
  <div class="mx-mail__front">
    <span class="mx-mail__greet">Greetings from</span>
    <span class="mx-mail__place">Scarborough</span>
  </div>
  <div class="mx-mail__back">Hand-written message on ruled lines…</div>
</figure>
```
Airmail border + tilt + hard offset shadow are the default cues.

### Stamp / seal (currentColor roundel)
```html
<div class="mx-stamp" data-mx-event="ephemera">
  <span>Wien Hbf · Gleis 11</span><b>21:27</b><span>Nightjet 233</span>
</div>
```
Colour variants: `--support`, `--brass`; or set `--mx-stamp-ink`.

### Ticket (perforated stub + punch holes)
```html
<div class="mx-ticket" data-mx-event="ephemera">
  <div class="mx-ticket__main">
    <span class="mx-ticket__meta">North Bay Railway · Est. 1931</span>
    <span class="mx-ticket__event">Peasholm → Scalby Mills</span>
    <span class="mx-ticket__meta mx-ticket__row"><span>Fare</span><span>£4.50 · as of July 2026</span></span>
  </div>
  <div class="mx-ticket__stub">
    <div class="mx-stamp"><span>N.B.R.</span><b>RIDE</b><span>№ 0451</span></div>
  </div>
</div>
```

### Coaster
```html
<div class="mx-coaster" data-mx-event="ephemera">
  <span>Harbour Bar · knickerbocker glory · £6.20</span>
</div>
```
Variants `--accent`, `--accent2`.

### Quote object (Law 9 — named source mandatory)
```html
<figure class="mx-quote" data-mx-event="quote">
  <blockquote>Verbatim words only.</blockquote>
  <figcaption>— <b>Named Person</b> · where they said it</figcaption>
</figure>
```

### Hand note & layout surfaces
`<span class="mx-note">hand-written marginalia</span>` ·
`.mx-shelf` (scatter surface — children get alternating offsets/tilts) ·
`.mx-twocol` + `.mx-twocol__aside` (copy beside objects).

## 6 · Ledgers (`11-ledgers.css`)

Component-local `--mxl-*` tokens (the layer-40 double-token pattern) map from
act tokens at each component's top — remap one block to restyle.

### Facts ledger
```html
<div class="mx-ledger" data-mx-event="ledger">
  <div class="mx-ledger__caption">Ledger · One Train, Filed</div>
  <dl><dt>Train</dt><dd>Nightjet 233 …</dd><dt>Verdict</dt><dd>…</dd></dl>
</div>
```

### Ranked entries + rank chips + tier pills
```html
<div class="mx-ranked" data-mx-event="ledger">
  <h3 class="mx-ranked__title">Chip shops, ranked.</h3>
  <ol class="mx-ranked__list">
    <li class="mx-ranked__entry">
      <div class="mx-ranked__head">
        <span class="mx-rank"></span>  <!-- auto-numbers 01, 02… -->
        <h4 class="mx-ranked__name">The Magpie Café</h4>
        <span class="mx-tier mx-tier--hot">Go</span>
      </div>
      <p>Verdict copy.</p>
      <dl class="mx-ranked__facts"><dt>Queue</dt><dd>40 min at noon</dd></dl>
    </li>
  </ol>
</div>
```
Tier pills: `--hot` / `--warm` / `--note`. `.mx-rank` also works inside
`.mx-zig__card` (auto-numbers per zig list).

### Stat band
```html
<div class="mx-numbers" data-mx-event="statband">
  <div class="mx-numbers__cell">
    <span class="mx-numbers__num">1.5m</span>
    <span class="mx-numbers__label">Riders a year</span>
    <span class="mx-numbers__sub">ÖBB network, 2024</span>
  </div> <!-- ×3–6; grid is 3-up, 2-up ≤560px -->
</div>
```
`--loud` variant sets chunk numerals (event acts).

### Cheat-sheet
```html
<div class="mx-cheat" data-mx-event="cheatsheet">
  <div class="mx-cheat__head">The Cheat Sheet · One Saturday, Solved</div>
  <div class="mx-cheat__cols">
    <div class="mx-cheat__col">
      <span class="mx-tier mx-tier--hot">Morning</span>
      <h5>Item</h5><p>Advice.</p>
    </div> <!-- ×3 -->
  </div>
</div>
```

### Scorecard (results/standings on card stock)
```html
<div class="mx-scorecard" data-mx-event="ledger">
  <h4 class="mx-scorecard__title">Tour de France · GC</h4>
  <table>
    <tr class="is-lead"><td class="mx-scorecard__pos">01</td><td>POGAČAR</td><td class="mx-scorecard__gap">YELLOW</td></tr>
  </table>
</div>
```
`--wide` variant (560px) for multi-column tables — see table policy §8.

## 7 · Plates & set pieces (`12-plates.css`)

### Numbered plate
```html
<header class="mx-plate" data-mx-event="plate">
  <div class="mx-plate__ghost" aria-hidden="true">IX</div>
  <span class="mx-plate__no">FILE 09</span>
  <h2 class="mx-plate__title">The Trains That Refused to Die</h2>
  <p class="mx-plate__dek">Serif-italic dek, ≤44ch.</p>
</header>
```
`--loud` swaps title/ghost to the chunk voice.

### Anchor (feature block; the chapter's grid-breaker)
```html
<article class="mx-anchor" data-mx-event="figure">
  <div class="mx-anchor__media"><img src="…" alt="…"></div>
  <div class="mx-anchor__copy">
    <h3 class="mx-anchor__title">The Grand at 159</h3>
    <p class="mx-anchor__dek">Serif italic dek.</p>
    <div class="mx-anchor__meta"><span>Opened <b>24 July 1867</b></span></div>
  </div>
  <div class="mx-anchor__badge">hand-written badge</div>
  <div class="mx-anchor__note">hand-script margin note</div>
</article>
```

### Zig-zag entries (ranked picks, alternating sides)
```html
<div class="mx-zig">
  <article class="mx-zig__entry" data-mx-event="figure">
    <div class="mx-zig__media"><img src="…" alt="…"></div>
    <div class="mx-zig__card">
      <div class="mx-zig__head">
        <span class="mx-rank"></span>
        <h3 class="mx-zig__title">The Caledonian Sleeper</h3>
      </div>
      <p class="mx-zig__quote">“Serif-italic lede.”</p>
      <dl class="mx-zig__meta"><dt>Route</dt><dd>…</dd></dl>
    </div>
  </article> <!-- even entries auto-reverse -->
</div>
```

### Don't-miss chips
```html
<aside class="mx-dontmiss" data-mx-event="cheatsheet">
  <span class="mx-dontmiss__kicker">don't miss</span>
  <h3 class="mx-dontmiss__title">Four things worth the detour</h3>
  <ol class="mx-dontmiss__list">
    <li><b>The lead,</b> then the reason. </li> <!-- ×3–5, chips auto-number -->
  </ol>
</aside>
```

## 8 · Chrome (`13-chrome.css`) + craft rules

### Masthead — ONE per bundle
```html
<header class="mx-mast">
  <span class="mx-mast__title">The Signal<span class="mx-mast__stop">.</span></span>
  <span class="mx-mast__badge">Special Edition</span>
  <span class="mx-mast__meta">№ 21 · Sunday 19 July 2026</span>
</header>
```

### Cover scaffold (poster-grade, Law 7)
```html
<section class="mx-cover mx-ground-starfield mx-ground-grain" data-act="night">
  <div class="mx-cover__ghost" aria-hidden="true">21</div>
  <div class="mx-cover__script-ghost" aria-hidden="true">overnight</div>
  <div class="mx-cover__inner">
    <div class="mx-cover__sig"><span>The Signal</span><span>Trip Special</span><span>№ 21</span></div>
    <span class="mx-cover__overline">a berth on the</span>
    <h1 class="mx-cover__title">Night <span class="mx-cover__amp">&amp;</span> <span class="mx-cover__outline">Tide</span></h1>
    <p class="mx-cover__dek">…</p>
    <div class="mx-cover__pills"><span>Act I · …</span><span>Act II · …</span></div>
  </div>
</section>
```
`.mx-cover--poster` centres everything in a double-ruled frame and takes an
optional `.mx-cover__plate` SVG art slot. The cover must use ≥3 voices
(overline script + title chunk + sig mono here); accents always come from
`var(--mx-accent)` — never hard-code.

### Kicker, kicker strip, act opener
`.mx-kicker` (eyebrow with trailing rule) ·
`.mx-kickerstrip` > `__inner`/`__title`/`__sub`/`__meta` (between cover and
first act) ·
`.mx-actopen` (`data-mx-event="plate"`) > `__no`/`__title`/`__hand`.

### Transit band (the designed act transition, Law 4)
```html
<div class="mx-transit" data-mx-event="marquee">
  <div class="mx-transit__side mx-transit__side--left">
    <div class="mx-transit__mega" aria-hidden="true">NIGHT</div>
    <div class="mx-transit__label">
      <span class="mx-transit__hand">leaving</span>
      <span class="mx-transit__name">The Sleepers</span>
    </div>
  </div>
  <div class="mx-transit__center"><div class="mx-transit__card">Change Here</div></div>
  <div class="mx-transit__side mx-transit__side--right">…mirror…</div>
</div>
```

### Marquee
```html
<div class="mx-marquee" data-mx-event="marquee" aria-hidden="true">
  <div class="mx-marquee__track">
    <span>Phrase one</span><span>Phrase two</span>
    <span>Phrase one</span><span>Phrase two</span> <!-- duplicate set once -->
  </div>
</div>
```
Static by default; drifts only under tier1/tier2 (14-motion).

### Countdown grid
```html
<div class="mx-countdown" data-mx-event="statband">
  <div class="mx-countdown__grid">
    <div class="mx-countdown__cell"><span class="mx-countdown__num" data-cd="days">27</span><span class="mx-countdown__unit">Days</span></div>
    <!-- hours / minutes / seconds -->
  </div>
  <div class="mx-countdown__target">Departure · 15 August</div>
</div>
```
No ambient shimmer exists and none may be added outside the reduced-motion
gate.

### Table policy (Law 10)
Tables **wrap or stack, never scroll-truncate**: cells wrap at word
boundaries; `.mx-ledger` stacks ≤560px; scorecards go full-width. Chromium's
overlay scrollbars occupy no layout height, so a scroll-wrapped table can
never show the craft gate's required visible affordance — a table that
overflows its container is a bug to fix in the table, not to wrap. The
`.mx-tablewrap` shell (+ author-supplied `.mx-tablewrap__hint`) exists only
to keep an overflowing table from breaking the document while it gets fixed.

## 9 · Motion tiers (`14-motion.css` + `assets/mx-motion.js`)

The WP-5 controller (`assets/mx-motion.js`, ~8KB; the stitcher ships it on
data-mx issues INSTEAD of the legacy 96KB `script.js`) auto-targets core
component classes — **no per-issue motion markup is required**:

- `tier0` print-still (Deep Dive): plates/act openers/pulls/ledgers/stat
  bands/quotes/sources get `.mx-draw` (an overlay hairline draws in via
  `::after`; content itself is never hidden) + `.mx-plate__ghost` parallax
  driven by `--mx-par`. Nothing else moves.
- `tier1` calm: `.mx-card`/`.mx-ticket`/`.mx-coaster`/`.mx-note`/`.mx-stamp`
  → `.mx-settle` (tape down, lands on own tilt); `.mx-quote`/`.mx-pull`/
  `.mx-anchor`/`.mx-plate`/`.mx-actopen`/`.mx-zig__entry`/`.mx-chart` →
  `.mx-rise`; ledgers/ranked/scorecards/stat bands/cheat cols/don't-miss/
  countdown cells → `.mx-seq` containers whose `.mx-row` children tick in
  `--mx-i` order; `.mx-chartline` (svg path with `pathLength="1"`) draws;
  hover settles + slow marquee.
- `tier2` event: tier1 plus stamp-slam (`.mx-stamp` → `.mx-slam`, one hard
  step), full-speed marquee, countdown-numeral flips, and the act crossfade
  at transit seams (controller injects `.mx-seam--out/--in` into the
  `data-act` neighbours of each `.mx-transit` and drives `--mx-seam`;
  gradient endpoints are act tokens, per Part 8).

Reveals: the controller stamps `data-mx-motion-ready` on `<html>` and
`.is-in` + `data-mx-inview` on furniture entering the viewport — every
initial-hidden rule is gated on that attribute, so **JS-off renders 100% of
content**. Stagger delays are capped with `min()` so tails resolve fast.

Signature moments (classes the WP-6 skeletons place): `.mx-sig-stamp-slam`
(Versus verdict slam) · `.mx-sig-rows-climb` (Season Review leaderboard
rows climb) · `.mx-sig-cols-reveal` (Rewind Memory-Test columns in
sequence) · `.mx-sig-dial-sweep` (Weekly needle sweep — hook only until
WP-8; binds `.mx-dial__needle`/`[data-mx-needle]`) · countdown flips fire
automatically on `.mx-countdown` under tier2 (`data-mx-target="ISO date"`
opts into live ticking with re-flips).

`prefers-reduced-motion` is honored at BOTH layers: the controller no-ops
entirely (and drops `data-mx-motion-ready` if the preference flips
mid-read), and the global CSS gate kills every animation/transition under
`[data-mx]`. Motion attaches to furniture, never running text; no
scroll-jacking.

## 10 · Checklist for a new page

1. `<body data-mx data-motion="…" data-mx-chrome="pill">` (pill attr iff the
   back pill ships).
2. One `.mx-mast`. One cover. Acts as `section[data-act]`, each with a
   ground utility and its token block; act transitions via `.mx-transit`
   (or a designed seam), never a bare background swap.
3. Every countable component carries its `data-mx-event` type.
4. Photos are real `<img>` with alt; CSS art is `role="img"` + label.
5. Quotes have named sources. Prices/hours carry "as of `<date>`".
6. Don't flatten objects unless `.mx-flat` is a deliberate choice.
7. Verify with `tools/render.mjs` + `tools/measure-issue.mjs` before any
   gate claim.
