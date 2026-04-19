# The Signal — Visual Language

The aesthetic layer. A catalogue of type, colour, chrome, motion, and components — applied on top of The Signal's existing editorial structure. This file does not change The Signal's structure in any way.

## Prime directive

> The Signal stays The Signal. This file describes how it *looks*, not how it's *built* — and what it looks like is Signal's own, not a rehash of its sources.

Every decision below is tagged as one of:

- **LIFT** — the mechanic (not the specific) is borrowed, and correctly adapted to Signal
- **SIGNAL'S OWN** — decided fresh for Signal
- **DROP** — present in the sources but wrong for Signal; do not copy

The two sources are:
- `The-Signal-Special-Edition.html` — the design prototype. Donor of component library, type moves, chrome vocabulary.
- `landonorris.com` — the motion + restraint reference. Donor of scroll mechanics, accent-as-withholding, parallax, colour-adaptive chrome.

---

## 0. Hard drops (before anything else)

These elements are in the sources. They do not belong in The Signal. Never copy them, never port their equivalents:

| From | Specific element | Why it's dropped |
|---|---|---|
| Prototype | Roman numerals as section markers (I, II, III…) | Signal has 8–12 named sections per issue, not 7 chapters. Numbering them `I–XII` is cosplay. Sections are titled by name. |
| Prototype | "Dispatch" / "Chapter" vocabulary | Signal's vocabulary already exists: issue, section, The Shelf, The Pantry, etc. |
| Prototype | `§NNN LOAD · SIGNAL` preloader text | Direct port of "LOAD NORRIS" pun. Signal gets its own load-state (see §7) or none. |
| Prototype | "Medallion break" interstitial with roman numerals | It's a divider in service of numbered chapters. Signal doesn't number chapters. |
| Prototype | "Hand-set · long-form · one-sitting read" tagline tone | Wrong register for a Sunday magazine. |
| Prototype | Four-font stack (Instrument Serif + Fraunces + Geist + JetBrains Mono) | Too many families; dilutes the contrast. Signal uses two (see §1). |
| Lando | Lime `#D2FF00` accent | Racing/streetwear, wrong for Sunday reading. Signal's accent is ember (see §2). |
| Lando | "LOAD NORRIS" preloader | Name-specific pun. |
| Lando | 3D floating helmet hero motion | Specific to an F1 driver. |
| Lando | Signature-as-logo stamp | Lando has one; Signal doesn't need one. |
| Lando | "STORE" CTA | Signal has no store. |
| Lando | "ALWAYS BRINGING THE FIGHT" footer voice | Wrong register. |
| Lando | McLaren orange `#FF6B00` secondary accent | Not relevant. |
| Lando | Topographic "blob" lines (Lando's helmet livery extracted) | They *mean* something specific on Lando's site. For Signal, decorative contour lines are fine *as texture*, but they're not borrowed from Lando's livery. |

---

## 1. Type system [LIFT + SIGNAL'S OWN]

**Two families only.** Maximum contrast. No third font ever.

```
--display: 'Fraunces', 'Instrument Serif', Georgia, serif;  /* editorial serif, variable weight + italic */
--sans:    'Geist', system-ui, -apple-system, sans-serif;   /* clean grotesque, variable weight */
--serif:   var(--display);                                   /* body uses the same serif family */
```

- **Display serif** handles: masthead title, section heads, dropcaps, pull quotes, oversized numerals, body copy, inline italic accent emphasis.
- **Sans** handles: all small UI — eyebrows, kickers, bylines, captions, stat labels, chrome labels, nav. Tracked wide (`letter-spacing: 0.18–0.28em`), uppercase for labels.
- **No monospace family.** Sans at 10–11px with wide tracking replaces everything the prototype used mono for. [LIFT from Lando — Lando has no mono either; mono reads "terminal", sans-wide-tracked reads "editorial print".]

**Type role map:**

| Role | Font | Style | Size range |
|---|---|---|---|
| Section head | display | regular, italic accent emphasis | `clamp(56px, 7.5vw, 128px)` |
| Cover headline | display | regular, italic accent emphasis | `clamp(72px, 13vw, 220px)` |
| Sub-hed / kicker headline | display | italic | ~40–56px |
| Body paragraph | serif | 400 / line-height 1.6 | 18–20px |
| Dropcap | display | italic, accent colour, floats left | ~140px |
| Pull quote | display | italic | 28–84px depending on slot |
| Oversized numerals (stats, plate numbers, dates) | display | italic, accent colour | 56–112px |
| Eyebrow / kicker / byline / chrome label | sans | uppercase, 0.24–0.28em tracking, 500 weight | 10–11px |
| Caption / locator | sans | uppercase, 0.22em tracking, 500 weight | 10px |

**Type rules:**
- `text-wrap: balance` on heads.
- `text-wrap: pretty` on body paragraphs and deks.
- `letter-spacing: -0.02em` on display at size ≥ 56px.
- **Inline italic accent is the primary emphasis tool.** `<em>` in body copy renders as display italic in accent colour inline, no bar, no highlight, no background. [LIFT from Lando — italic coloured words inside body. Replaces the prototype's highlight bars.]

---

## 2. Palette [LIFT + SIGNAL'S OWN]

Working default: **ember** scheme. Other schemes available for special editions if content warrants, but weekly defaults to ember unless overridden.

```
ember (default)   bg #0c0a08 · paper #f1ead9 · ink #0c0a08 · accent #d2411e · muted #8a7f6a
dossier           bg #15140f · paper #e8e1cf · ink #15140f · accent #b8902a · muted #7f7560
blueprint         bg #0a1626 · paper #ece4d0 · ink #0a1626 · accent #ff6a1f · muted #6f7f95
midnight          bg #050505 · paper #eceae4 · ink #050505 · accent #7ee0b3 · muted #7a7a74
```

Tokens (same names across all schemes):
```
--bg         deep base — dark sections, chrome
--paper      warm off-white — paper-ground sections, body text
--ink        dark ink text on paper ground (same value as --bg)
--accent     the single accent, always italic display or small labels
--accent-ink readable ink on accent background
--muted      secondary chrome grey
--rule       1px hairline on dark ground
--rule-paper 1px hairline on paper ground
```

### 2.1 Accent-as-withholding [LIFT from Lando]

This is the most important palette rule. Accent is a scarce resource, not a texture.

- Accent appears in **no more than ~8% of on-screen area** at any scroll position.
- Accent runs in body copy are **never longer than three words**.
- Each accent appearance should read as **punctuation** — a mark, a signal — not as decoration.
- Where the prototype paints accent borders on sidebars, rails, and bars everywhere: **reduce**. Keep accent on numerals, on italic emphasis, on key labels, on the pulsing dot, on the § glyph before feature subheads. Not on rule lines, not on every eyebrow, not on sidebar frames.
- When in doubt, strip an accent instance. If the page still works, the instance was decoration.

### 2.2 Alternating grounds [LIFT from prototype]

Every issue alternates dark and paper grounds across consecutive sections. Never two consecutive sections on the same ground. This is the primary rhythm tool.

### 2.3 Per-section accent shifts [LIFT from `original-special.html`]

For special editions with many sections of different character (e.g. a Countdown visiting two different destinations and many logistical topics), a section can shift its `--accent` within the scheme's family by setting `data-accent` on the section wrapper:

```css
[data-scheme="ember"] [data-accent="wild"]   { --accent: #c9a84c; } /* warmer gold */
[data-scheme="ember"] [data-accent="cool"]   { --accent: #48cae4; } /* cold transit */
[data-scheme="ember"] [data-accent="food"]   { --accent: #e8a838; } /* amber */
```

`--bg` and `--paper` stay consistent across the issue; only accent shifts. Replicates the per-section colour worlds in `original-special.html`.

---

## 3. Chrome [LIFT + SIGNAL'S OWN]

Signature decoration. Always background. Never the point. Three chrome devices, used lightly, as chosen for Signal:

### 3.1 Sunday timestamp + issue number [SIGNAL'S OWN]

The masthead reads, in sans uppercase:

```
left:   · THE SIGNAL           centre: (italic display) The Signal · Sunday   right: SUNDAY 06:40 · NO. 47 · 19 APRIL
        A Sunday magazine                                                             MMXXVI
```

The time `06:40` is the Signal's reading-ritual identity. It doesn't change per issue (it's not "now" — it's when the reader sits down with coffee). [SIGNAL'S OWN.] The issue number and date update per issue.

Masthead uses `mix-blend-mode: difference` to stay legible against any scroll position ground. [LIFT from prototype.]

Pulsing accent dot beside the far-left label. [LIFT from prototype.]

### 3.2 Dispatch seal (lightly) [LIFT mechanic, SIGNAL'S OWN content]

Rotating SVG circular seal, top-right, fixed. **Only on the cover section and the colophon section** — not every page. Arc text reads:

```
· THE SIGNAL · SUNDAY MAGAZINE · NO. 47 · APRIL MMXXVI ·
```

Italic display monogram in the hub: the issue number (e.g. `№ 47`). 28s linear rotation. Pauses on `prefers-reduced-motion`. [Mechanic LIFT from prototype; content SIGNAL'S OWN.]

### 3.3 Newsprint gutter marks [LIFT + SIGNAL'S OWN]

On paper-ground sections, faint hairline column gutter marks appear at section edges — like the fold registration marks on a broadsheet. Rendered as 1px rule-paper lines, ~48px long, at section-corner ± 32px offset. Three corners per section (top-left, top-right, bottom-left). The fourth corner is where the next section's chrome begins, implying continuity. [SIGNAL'S OWN — no direct source analogue; fits the editorial voice.]

### 3.4 Other chrome elements (used where useful, not everywhere)

- **Giant folio watermark** — display italic letter at 320–820px, `opacity: 0.04`, bottom-right. Used sparingly on feature sections. [LIFT from prototype, used more selectively.]
- **§ glyph** — accent-coloured, italic, before H3 subheads *inside feature body only*. [LIFT from prototype.]
- **Vertical spine labels** — sans 10px, wide-tracked, `writing-mode: vertical-rl`, beside long-form feature bodies. [LIFT from prototype.]
- **Contour paper texture** — faint SVG data-URI pattern, `body::after` on paper-ground sections. Not Lando's helmet blobs — Signal's version uses horizontal staff-line contours, loosely evoking printed-page rules. Opacity ≤ 0.08. [SIGNAL'S OWN.]
- **Film grain** — fixed, full-viewport, `mix-blend-mode: overlay`, opacity 0.5, SVG fractal noise. One line, always on. [LIFT from prototype.]

---

## 4. Component vocabulary [LIFT from prototype + SIGNAL'S OWN additions]

Each component is a **variable-density slot**. It has a minimum spec and expands to hold content. Content never shrinks to fit a component.

### 4.1 Components lifted from the prototype

| Component | What it looks like | Density rule |
|---|---|---|
| **Feature band** | 3-col grid: 110px dark rail + body column (dropcap + § subheads) + 340px margin (quote card + datum cards). | Body min 500 words. Margin carries ≥ 2 of {pull quote, datum, chart-card, brief}. If body runs long, it continues; the margin sticks. |
| **Pull break** | Full-bleed dark band, giant accent quotes peeking in from corners, centred display pull quote. | Used once per long feature, never twice in a row. |
| **Plate strip** | Horizontal scroll-snap gallery: italic plate number + frame (image) + caption. | **Now variable density.** Each plate has a required top (number) and frame, and a caption slot that expands: `{2-line caption}` OR `{caption + stat}` OR `{caption + stat + body paragraph + pull quote}`. Plates within one strip can be uneven. |
| **Timeline rows** | 2-col grid: italic display date on left, serif body on right, accent dot marker. Bounded in accent-tinted band. | Body per row min 2 sentences. Can hold 3–15 rows. |
| **Stat row** | 4-col band on accent-tinted paper: italic giant numeral + sans label per cell. | Min 3 cells, max 6. Each cell can carry {number + label} OR {number + label + sub-hint + delta}. |
| **Editor's note** | Two-panel: giant stacked display headline with italic accent on key word (left) + body column with eyebrow + dek + text (right). | Body min 250 words. |
| **Contents ledger** | Italic roman monograms? **No.** Section titles in serif on hairlines, right-aligned meta (tags). Numbering by Signal's own convention (e.g. `01 · 02 · 03`, not `I · II · III`). | One row per section in the issue. |
| **Ribbon ticker** | Marquee band of sans labels, accent separators. Paired opposite directions as `.reverse` for double-row. | Used at major transitions only. |
| **Colophon** | 4-col grid end matter: masthead block, in-this-issue, sources (with real URLs), about. | Unchanged from current Signal. Restyled type only. |

### 4.2 Components I missed in draft 1 — now included [LIFT from prototype]

| Component | What it looks like | Signal use |
|---|---|---|
| **Brief card** | Accent-tinted sidebar, 6px left accent bar, kicker + display H4 + body + byline. | Toolkit item, Shelf one-liner, sidebar context in any feature |
| **Hero quote card** | Oversized quote with accent radial gradient bg + peeking quote glyph. | Opinion block, reader letter reply, pull from interview |
| **Dash (stat dashboard)** | Auto-fit cells, each with `hint` eyebrow + italic numeral + serif `l` label + accent `delta`. | Ledger, Wallet, performance numbers, KPI-style sections |
| **Chart card** | Bordered card with kicker + H4 + SVG chart + foot meta line. Has `.dark` variant for dark-ground sections. | Long Game retrospective data, Ledger trend, Wallet chart |
| **Plan infographic** | 16:10 aspect, dark ground, grid-bg + SVG overlays + small sans labels with italic display value highlights. | Itinerary route map, Workshop diagram, Field Guide floor plan |

### 4.3 Components added for Signal [SIGNAL'S OWN]

| Component | What it looks like | Why Signal needs it |
|---|---|---|
| **Fan-spread card deck** | 5–7 small cards, each rotated ±5–25°, overlapping in a hand-of-cards arrangement. Hover lifts the top card. | Shelf (book covers), Toolkit (app screenshots), Itinerary (photo postcards). [LIFT mechanic from Lando's social-cards section; Signal uses it for Shelf-type grids.] |
| **Index strip** | Horizontal compressed list of section names with hairline separators, sans uppercase, current-section highlighted in accent. | Running mid-page index, shown mid-scroll on long issues as a reader locator. |
| **Marginalia column** | Narrow right-column running alongside feature body: small sans notes, quote pulls, footnotes, related-issue back-references. | Adds density to features without thinning body. Replicates a newspaper's slip column. |

### 4.4 Components *not* included [DROP]

- **Bridger** as the prototype writes it (3-col dark-rail + body + sidebar, padding 100px) — the thing I overused in v8. It's redundant with Feature Band and it's what created the sameness problem. Explicitly removed from the kit. If a feature is short, use Editor's Note or Brief Card; if it's long, use Feature Band.
- **`.hl` highlight bars** — replaced by inline italic accent in body (`<em>`).

---

## 5. Motion [LIFT + SIGNAL'S OWN]

Two categories. **Continuous scroll-linked** (the thing that makes scrolling feel designed — the brief's weakest part last draft) and **discrete entry** (fades and reveals on intersection).

### 5.1 Continuous scroll-linked motion [LIFT from Lando, missing from prototype, missing from draft 1]

| Move | How it works | Applies to |
|---|---|---|
| **Parallax on hero portraits** | Hero image translates at 0.6× scroll rate while body content translates at 1×. Creates depth without the section changing size. | Cover photo, feature hero photos |
| **Section-to-section colour flood** | As a new section enters viewport, its `bg` colour progressively takes over from the previous section's — not a crossfade, not a gradient mask. Implemented via a fixed full-viewport `::before` layer whose colour is the *next section's* bg, and whose `clip-path` opens from the top edge as the next section enters. Reads as a flood, like the Lando off-white → dark olive → near-black → cream transitions. | Every section boundary |
| **Sticky images with scrolling captions** | In feature bands, the hero image becomes `position: sticky` while captions and body paragraphs scroll past. Image un-sticks when the next section's boundary crosses. | Feature body blocks |
| **Count-up numerals** | Stats in the stat-row and dash animate their value from 0 → final over 800ms, triggered when the numeral enters viewport 30%. Respect `prefers-reduced-motion`. | Every italic numeral in `.stat`, `.dash`, `.datum` |
| **Colour-adaptive nav** | Masthead wordmark switches between paper and bg values based on which ground the scroll position is over. Implemented via IntersectionObserver tagging sections with their ground, masthead reads current. | Masthead, always |
| **Footer-rising-card** | The colophon section is wrapped in a rounded-rectangle panel (radius 16px) that rises into view from below the previous section's bottom edge as the reader approaches it. The rounded top is visible against the previous section before full entry. | Colophon only |
| **Image progressive reveal** | Inside a feature, a tall portrait image has its `object-position` shift from 0% to 100% as it scrolls through viewport, effectively panning the image crop. | Editorial photos in features |
| **Cover photo scale-down** | Cover hero eases from `scale(1.08)` to `scale(1)` as scroll passes 30vh, signals "you've left the cover". | Cover only |

### 5.2 Discrete entry motion [LIFT from prototype]

| Move | Trigger | Spec |
|---|---|---|
| **Line-by-line head entry** | IntersectionObserver 25% | Heads split to `.ln > span` lines; opacity 0→1, translateY 14px→0, 60ms stagger, 600ms ease-out |
| **Dropcap settle** | Entry | Accent dropcap fades in with micro-scale (0.94→1) after body text has drawn |
| **Plate hover** | Pointer | `translateY(-8px) rotate(-0.3deg)`, 500ms cubic-bezier(.2,.8,.2,1). |
| **Ribbon scroll** | Constant | 40s linear infinite, paired ribbons run opposite directions via `.reverse`. |
| **Seal rotation** | Constant | 28s linear infinite. Pauses on `prefers-reduced-motion`. |
| **Pulsing dot** | Constant | 2s ease-in-out, opacity 1→0.35→1. |

### 5.3 Load-state [SIGNAL'S OWN]

No preloader text pun. No `§NNN LOAD · SIGNAL` dispatch flash. Instead:

- On first paint, the body is `opacity: 0`.
- The masthead + seal draw in first (150ms fade).
- Then the cover photo fades in (400ms).
- Then the cover headline lines enter one by one (stagger 60ms).
- No full-screen flash of accent colour. No "LOADING".
- Total pre-reader load feel: ~1 second. Calm.

Reasoning: Signal is read with coffee, not raced to. Preloader text would be wrong register. [SIGNAL'S OWN.]

### 5.4 Reduced motion

Honour `prefers-reduced-motion: reduce`:
- Disable: seal rotation, ribbon scroll, parallax, scale-down, scroll-linked sticky transforms, count-up numerals.
- Keep: simple fade entries (reduced to opacity-only), pulsing dot (or disable if user has vestibular concerns).
- Colour flood transitions become instant swaps at section boundary instead of progressive.

---

## 6. Content density [SIGNAL'S OWN — with teeth]

The brief's non-negotiable rule: **content never shrinks to fit the visuals; visuals grow to fit the content.**

### 6.1 Per-section minimum density

These minimums apply to every section in every issue. Failing any = not shippable.

| Section type | Minimum density |
|---|---|
| Lead feature (Down the Rabbit Hole, special-edition feature) | 600 words body + ≥ 2 pull quotes + ≥ 1 datum/stat + ≥ 1 image |
| Secondary feature (The Workshop, The Long Game) | 400 words + ≥ 1 pull quote + ≥ 1 datum + ≥ 1 image |
| List-forward (The Shelf, The Toolkit, The Pantry) | ≥ 4 items, each with ≥ 3 sentences of opinion + image |
| Numeric (The Ledger, The Wallet) | ≥ 4 stats + ≥ 1 chart OR ≥ 200 words of interpretation |
| Timeline (This Week in History, The Long Game, Itinerary) | ≥ 5 dated rows, each row ≥ 2 sentences |
| Short-form (The Week, news brief) | ≥ 5 items, each 1 sentence minimum |
| Cover | Headline (2–5 words with italic emphasis) + ≥ 3 meta lines + image |
| Editor's note (specials only) | ≥ 250 words body + display stacked headline |
| Colophon | Masthead block + in-this-issue list + ≥ 6 sources with URLs + about-the-signal paragraph |

### 6.2 If the component can't hold the content, change the component

The v8 failure mode was: section has 500 words of real content → bridger slot has ~180 words → trim to ~180 → content dies. **The fix:** pick a component that holds 500 words (feature band), or grow the plate's caption slot, or split to two components. Never trim the content.

### 6.3 Opinion density

Signal is opinionated. Every section with items (Shelf, Toolkit, Pantry, Itinerary, Radar) must carry ≥ 1 sentence of editorial verdict per item. Bare description = not Signal.

---

## 7. Structure (unchanged — this is the part that stays Signal's)

This file does not speak to:
- Which sections appear in an issue → `editorial-spec.md`, `sections.md`, state file
- Cadence of rotating sections → state file
- Special-edition formats (Deep Dive, Countdown, Field Guide, Season Review, Versus, Rewind, Starter Kit, Blueprint) → `editorial-spec.md`
- Research rules, compliance gates, reader profile → `editorial-spec.md`, `compliance-checklist.md`

When generating, build the issue the same way as today. Then, at markup time, pick treatments from §4 and §5 for each section based on its type. Different section types get different treatments — that's where cross-section variety comes from.

---

## 8. Target viewport

- **Primary:** tablet landscape ~1194×834 and portrait ~834×1194, vertical scroll, iPad / 10–13" tablets.
- **Secondary:** mobile portrait ~390×844.
- **Not targets:** desktop, print, A4 page, TV.

Never design as if it's a printed page. Never horizontal-snap-chapter mode (the prototype's default `data-nav`). Always vertical long-form.

---

## 9. Application map — Signal sections → components

Default mapping. A section can override for a given issue if content calls for it.

| Signal section | Default component(s) |
|---|---|
| Cover | Cover |
| The Lead / world (weekly) | Feature band + pull break + marginalia |
| The Week (news brief) | Timeline rows, condensed (each row 1-sentence) |
| The Shelf | Fan-spread card deck + brief cards below |
| The Pantry | Plate strip + brief card for sidebar recipe note |
| The Workshop | Feature band (dossier scheme) + chart card in margin |
| The Itinerary | Plan infographic + timeline rows |
| The Ledger | Dash + chart card |
| The Wallet | Dash + feature band for interpretation |
| The Long Game | Timeline rows + chart card |
| The Toolkit | Fan-spread card deck + brief cards |
| This Week in History | Timeline rows (dossier scheme) |
| Down the Rabbit Hole | Feature band + pull break + facsimile signoff + marginalia |
| Colophon | Colophon |

Special-edition format overrides:
- **Countdown** — alternating dark/paper feature bands per destination + dash + timeline rows (logistics) + plate strip (menu / packing) + plan infographic (route) + colophon. Per-destination accent shift.
- **Field Guide** — feature band per location + plate strips for neighbourhoods + timeline for day-by-day + dash.
- **Deep Dive** — single subject as one long feature band + multiple pull breaks + dash + plate strip of artefacts + marginalia.
- **Season Review** — dash up top + plate strip (highlights) + timeline rows (turning points) + feature band (verdict).
- **Versus** — split-screen cover + two parallel feature bands + dash comparison + timeline.
- **Rewind** — timeline rows dominant + plate strip of artefacts + feature band wrap.

---

## 10. Self-check before shipping any issue

Ask every question. Any "no" → fix before delivery.

- [ ] Does this issue have the same sections The Signal would have had *without* this visual language?
- [ ] Do ≥ 4 distinct component treatments from §4 appear in this issue?
- [ ] Does no single component appear more than twice in the issue? (Guards against bridger-sameness.)
- [ ] Does the issue alternate dark and paper grounds across consecutive sections?
- [ ] Does every section meet its minimum density from §6.1?
- [ ] Does every list-item have ≥ 1 opinion sentence?
- [ ] Does the issue use ≥ 2 continuous scroll-linked motion moves from §5.1?
- [ ] Does accent colour occupy ≤ 8% of any on-screen position?
- [ ] Are there zero roman numerals as section markers, zero "Dispatch" / "Chapter" vocabulary, zero preloader pun text?
- [ ] Is the issue read at 1194×834 *and* 834×1194 and feels right at both?
