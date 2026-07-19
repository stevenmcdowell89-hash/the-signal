# measure-issue.mjs / render.mjs — WP-0 measurement & screenshot harness

Tools for the design-system unification gates (spec:
`docs/design-system-unification-SPEC-2026-07-18.md`, Part 4 WP-0, Part 6
evidence protocol). Everything a gate claims about density, distribution,
words, overlap, truncation or motion must come from these tools' committed
output — never from prose estimates.

## Usage

```sh
node tools/measure-issue.mjs <issue-path-or-url> --out <dir>   # writes <dir>/metrics.json
node tools/render.mjs       <issue-path-or-url> --out <dir>   # writes screenshots + render-manifest.json
```

Both tools:

- serve the **repo root over HTTP** on an ephemeral port (never `file://`),
  so root-absolute asset paths (`/assets/...`) resolve. A target outside the
  repo is served from its own directory with a warning.
- **neutralize the service worker**: `navigator.serviceWorker.register` is
  stubbed via an init script, `/sw.js` requests are aborted, and the context
  is created with `serviceWorkers: 'block'`.
- **abort every cross-origin request** (Google Fonts etc. are blocked in this
  environment anyway; aborting keeps runs fast and deterministic). Navigation
  waits on `domcontentloaded` + fixed settle waits, never `networkidle`.
- use the pinned Chromium at `/opt/pw-browsers/chromium` and the Playwright
  module at `/opt/node22/lib/node_modules/playwright`. No `playwright install`.
- render at **1440x900 and 390x844** and run a **stepwise smooth-scroll pass**
  (~0.7 viewport per step, fixed 140 ms waits) over the whole page before
  measuring/shooting, so reveal-on-scroll content has fired. Nothing is judged
  from an unscrolled state.

### render.mjs output

```
<out>/1440/cover.png            viewport shot at scroll 0 (pre-scroll state)
<out>/1440/depth-0..7.png       8 evenly spaced depths from top to bottom,
<out>/390/cover.png, depth-0..7 taken AFTER the full smooth-scroll pass
<out>/dark-1440.png             one prefers-color-scheme: dark cover render
<out>/render-manifest.json      page heights, depth positions, file list
```

Depth positions are fixed at `i/7 * maxScroll` — harness-chosen, never
curated.

## metrics.json contents (per viewport)

- `words.bodyCopy` — visible text word count, excluding **chrome**
  (masthead, nav, footer, back pill, progress bar, back-to-top, folio badge,
  subscribe block) and **captions/credits** (`figcaption`, `[class*="caption"]`,
  `[class*="credit"]`, `[class*="__cite"]`) and `[aria-hidden="true"]`
  subtrees. Text inside designed objects (quotes, ledgers, stat bands) IS
  body copy — Law 3 excludes only chrome and captions.
- `events` — the Law-2 designed-visual-events census (below), with each
  counted event's `type`, `selector`, `matchedBy`, `label`, `y` and `h` so a
  verifier can audit every single count.
- `events.perScreen`, `words.perScreen`, `screens = pageHeight/viewportHeight`.
- `distribution` — screens are fixed bins of one viewport height; an event
  covers every bin its box intersects. Reports `emptyScreens`,
  `longestZeroEventRun`, and `law2DistributionFail` (run >= 3).
- `chromeOverlap` — at 10 evenly spaced scroll depths (spec requires >= 8),
  every `position: fixed`/`sticky` element that is visible (display/visibility/
  opacity checked) is intersected against visible text-bearing/content
  elements (`p, h1-h6, li, dt, dd, blockquote, td, th, img, figure`).
  An intersection counts when it is >= 12 px in BOTH dimensions (so a 3 px
  progress bar doesn't fire; a 34 px pill over a paragraph does). Fixed
  `pointer-events: none` layers covering >= 85% of the viewport are treated as
  decorative scene/grain overlays, excluded from pairs but listed in
  `decorativeFullViewportOverlaysExcluded`.
- `horizontalScroll` — flags only h-scroll a READER actually experiences:
  `flag` is true when (a) `scrollWidth > clientWidth + 1` (`geometricOverflow`),
  AND (b) an attempted `scrollingElement.scrollLeft = 50` reads back > 0
  (`scrollLeftAfterAttempt`), AND (c) `overflow-x` on `html`/`body` is not
  `hidden`/`clip` (`overflowXSuppressed`). Tilted/bleeding ephemera behind an
  overflow-suppressed root overflow geometrically but cannot be scrolled to —
  that is reported via `geometricOverflow`/`maxContentRightPx` (informational;
  transforms and marquee tracks can legitimately exceed the viewport), not via
  the flag. A page that hides real content behind `overflow-x: clip` is caught
  by the truncation detector instead.
- `tableTruncation` — three detectors over `table, th, td, .cheat-sheet`:
  1. `clipped-in-place`: `scrollWidth > clientWidth + 2` with no scrollable
     overflow on the element and no scroll-wrap ancestor;
  2. `scroll-wrap-no-visible-affordance`: the table sits in an
     `overflow-x: auto|scroll` wrapper that is cut at rest but renders **no
     horizontal scrollbar** (`offsetHeight − clientHeight − borders < 6`) —
     Law 10 requires the affordance to be *visible*; an overlay-scrollbar
     scroll-wrap is indistinguishable from a hard clip at rest.
     `nowrapCells` reports how many cells force `white-space: nowrap`
     (mid-word cut evidence);
  3. `clipped-by-ancestor`: a table sticking out past an
     `overflow-x: hidden|clip` ancestor.
- `motion` — census of elements that had a CSS animation or transition with
  `duration > 0` actually running/finished during the scroll pass, sampled
  via `document.getAnimations()` after every scroll step. Chrome elements are
  excluded (the progress bar's `width` transition would otherwise make every
  issue "animated"). `metrics.reducedMotion` repeats the pass in a context
  with `prefers-reduced-motion: reduce` emulated — what still animates there
  is a Law-5 violation.

## Event census — closed list and selector map

**Mode 1 (preferred):** if the document contains any `[data-mx-event]`
elements, ONLY those are counted (`type` = the attribute value). The future
furniture system emits these markers; hand-rolled pages don't get to invent
their own census.

**Mode 2 (heuristic):** DOM selector map, calibrated against the rendered
markup of `issues/signal_countdown_2026-06-14.html`,
`issues/signal_field-guide_2026-05-17.html` and
`docs/mockups/unification-furniture-kit-mockup.html` (the `hol-*`, `kit-*`
and `mx-*` vocabularies):

| Law-2 type | selectors |
|---|---|
| captioned figure (composite photo objects first, then generic) | `.hol-wonder, .hol-anchor, .hol-unmissable, .pick, figure`, plus standalone `img` >= 120x90 px |
| ephemera object | `.hol-polaroid, .hol-postcard, .hol-ticket, .ticket, .mx-ticket, .hol-stamp, .kit-stamp, .mx-stamp, .hol-coaster, .kit-card, .mx-card` |
| ledger/table block | `.hol-chalkboard, .hol-meal-slot__entry, .kit-ledger, .mx-ledger, .fixtures, .standings, .scorecard, .memory-test, .mtest, table` (tables need >= 2 rows) |
| stat band | `.hol-trip-numbers, .kit-stats, .mx-numbers, .stat-band, .hol-countdown, .hol-tminus, .vs-scoreboard` |
| quote-object with named source | `.hol-pull, .hol-pull--big, .kit-quote, .mx-quote, blockquote, .sp-pullquote-huge` — counted ONLY if a non-empty `cite`/`[class*="cite"]`/`[class*="source"]`/`[class*="attribution"]` descendant exists |
| numbered plate / act opener | `.mx-plate, .kit-plate, .hol-half__opener, .hol-kicker-strip, .sp-chapter-gate, .chapter-head, .hol-opening` |
| self-made chart/diagram/map | `svg, canvas, .dial` — only when rendered >= 200x120 px (excludes icons/fasteners) |
| marquee / act divider | `.hol-marquee, .hol-transit, .mx-transit` |
| cheat sheet / summary furniture | `.cheat-sheet, .mx-cheat, .kit-cheat, .hol-dont-miss, .keep-digging, .on-ramp, .week-plan` |

Explicitly NOT counted (per Law 2): drop caps, hairlines, subheads, bold
runs, fleurons (`.hol-dropcap`, `.hol-fleuron` match nothing above).

Census rules, in order:

1. anything inside the chrome selector list is skipped;
2. invisible elements (CSS visibility / zero rects) are skipped;
3. **outermost wins** — a candidate nested inside an already-counted
   candidate is skipped, so a polaroid inside a counted wonder-card composite
   is one event, not two, and a `table` inside a counted `.mx-cheat` is one;
4. size gates: generic candidates >= 48x28 px, images >= 120x90, svg/canvas
   >= 200x120;
5. quote-objects must carry a named source (Law-2 wording; Law 9 polices
   *who* the source is separately — `— THE SIGNAL` still counts here).

## Calibration results (smoke runs, committed under
`docs/design-system-unification-EVIDENCE/WP-0/smoke/`)

See each `<name>/metrics.json` (+ `<name>/render/`) for the full audit trail.
Headline numbers from the final tool version are recorded in the smoke
summary committed alongside the evidence
(`docs/design-system-unification-EVIDENCE/WP-0/smoke/SUMMARY.md`).
The WP-1 calibration bar — the countdown must measure >= 1.5 events/screen —
is met at 1440x900. The 542-word stub shows its true word count, its pill
overlap and its cheat-table truncation; the flat re-dress shows its
distribution failure.

## Known limitations (honest list)

- **Heuristic census is vocabulary-bound.** Mode 2 knows the `hol-*`,
  `kit-*`, `mx-*` and legacy special-issue class families. A page using a
  brand-new vocabulary without `data-mx-event` markers will under-count.
  The system being built must emit `data-mx-event` (Mode 1) to be exempt
  from heuristics.
- **Fonts are fallback fonts.** External requests are aborted (Google Fonts
  is blocked in this environment), so geometry (page height, screens,
  y-positions) reflects fallback-font layout. Word counts are unaffected;
  densities can differ by a few percent from a font-loaded render. The
  unified system self-hosts fonts, which will remove this delta.
- **Motion census is sampled**, after every ~0.7-viewport scroll step.
  Transitions shorter than ~150 ms can finish between samples and be missed;
  hover-only transitions never fire under this harness. Counts are of
  *elements* that animated, not of animation instances. Infinite ambient
  animations (grain shimmer, drifts) count — they are motion actually firing.
  Pseudo-element animations (`::before`/`::after`) are attributed to their
  host element by `document.getAnimations()`.
- **The countdown genuinely violates reduced motion (3 elements).** Under
  `prefers-reduced-motion: reduce` the countdown still animates
  `hol-shimmer` on `.theme-heat-haze::after` (three heat-haze sections —
  `section.hol-half--two` and two inner `.theme-heat-haze` sections). The
  `@keyframes hol-shimmer` rule (issue line ~7410) is applied outside any
  reduced-motion gate. This is a true finding in the reference, not a census
  artifact — the unified system must gate every animation (Law 5).
- **"Mid-word" truncation is inferred, not read.** The detectors are
  geometric (overflow with no visible affordance) plus `nowrapCells` as
  mid-word evidence; the tool does not OCR the cut glyphs.
- **Overlap is geometric.** A translucent fixed element over content counts
  the same as an opaque one (opacity < 0.05 and the decorative full-viewport
  exception aside). Note the references themselves record back-pill/folio
  overlaps at 390 px — the current back pill does not hide on scroll; this is
  an honest measurement, not a tool bug, and it is why Law 10 demands
  reserve-or-hide chrome in the new system.
- **Distribution counts real prose deserts wherever they are** — including a
  reference's closing "Meanwhile…" digest (the field guide ends with ~4
  screens of plain prose and measures a 5-screen zero-event run at 1440).
  The tool reports what is on the page; gates decide what passes.
- **Determinism:** steps, waits and depths are fixed; on a heavily loaded
  machine the motion element count can wobble slightly (sampling), and
  countdown-clock text changes wording between runs. Structural metrics
  (words, events, distribution, overlap, truncation) are stable across runs.
- Screens are computed from the *final* page height after the scroll pass; a
  page that grows while scrolling is measured at its settled height.
