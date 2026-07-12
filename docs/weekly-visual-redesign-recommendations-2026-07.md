# The Signal — Weekly Visual Redesign (recommendations for the implementer)

**Status: RECOMMENDATIONS — hand-off for another instance to implement.** A
ground-up visual review of the **weekly**, motivated by the owner's read: *"we
tried something fancier with the specials, brought some across to the weeklies,
and ended up with a weird halfway that just doesn't work."* This is a design
spec, not code. It is grounded in three inputs, all done for this review:
1. **Rendered covers** (headless Chromium screenshots of the shipped weekly
   `signal_weekly_2026-07-12.html` and the `deep-dive_2026-06-30` special);
2. a **CSS/template audit** of the live design system;
3. **wider editorial-design research** (Monocle / Kinfolk / Guardian / NYT
   systems; type, palette, grid references — cited in §7).

Companion docs: `docs/weekly-first-run-handoff-2026-07-12.md` (structure) and
`docs/weekly-reliability-rebuild-design-2026-07.md` (reliability). Visual, structural
and reliability work should land together — see §8.

---

## 1. The diagnosis — why it's a "weird halfway"

There are **three visual idioms fighting inside one weekly**, plus a delivery
problem:

**Idiom 1 — the (aspirational) warm-paper weekly.** Cormorant Garamond serif,
section watermarks, warm section grounds. But the "warm paper" is a lie: the
tokens `--paper #FAFAF8` / `--warm #F5F4F0` are **cool near-white grey, not
cream**. The genuinely warm creams (`#F4ECDC`) live only in the *specials*.

**Idiom 2 — the specials' "bound-magazine" grammar** (CSS slices 23–32) — and
it's genuinely good: full-bleed alternating `sp-ground-paper` / `sp-ground-ink`
chapter grounds (the value-shift on scroll *is* the transition), roman-numeral
chapter chrome, giant background folios, three-column spreads with marginalia,
and two strong disciplines — **ground-discipline** (islands may not self-paint a
background) and **readability-lock** (a self-painting element locks its own text
colour). Bits of this leaked into the weekly body (earlier weeklies literally used
`sp-spread` / `sp-marginalia` / `sp-folio`).

**Idiom 3 — the brand-new service/continuity boxes I added in the W-2/W-3 rebuild**
(`.caught-up`, `.do-this-week`, `.the-threads`/`.thread`, `.week-in-numbers`,
`.case-against`, in slices `15a`/`15b`). These are generic **rounded grey "app
cards"** — `background: rgba(0,0,0,.02–.035)`, `border-radius:6px`, a DM-Sans 11px
uppercase label, a left accent border. They match **neither** the warm-paper
weekly **nor** the specials, use cold rgba-black tints instead of any warm tone,
and **violate the specials' own ground-discipline**. This is the concrete
"weird halfway" — and it's on me: the structural rebuild shipped without a visual
system, so the new sections defaulted to app-callout styling. *(Owning this: the
W-rebuild fixed content architecture but introduced a third visual language.)*

**Plus a delivery problem.** The build injects the **entire special + holiday
CSS and 11 fonts** (8 of them decorative holiday faces — Alfa Slab One, Anton,
Bowlby One, Yellowtail, Caveat, Cinzel… — the weekly never uses) into every
weekly. Result: weeklies **ballooned from ~168KB (clean, 3 fonts) to ~600KB**, and
a JS `sp-chapter-beads` progress rail renders on every edition. The opposite of a
calm object.

**And the cover** (rendered, `02-cover.css`): a **dark plum/aubergine full-viewport
hero** with rose/ember radial glows, a 5px gradient top-bar, a giant tilted serial
numeral, a wax seal — **and it animates** (drifting gradients, animated grain,
staggered tag fade-ins). It is visually **the same template as a Deep Dive cover**
(compare the two renders). So the weekly opens on a screen of moody special-edition
drama — and prints **"SEVENTEEN CHAPTERS · ONE SITTING"** on it — before any
warm-paper content begins.

### The one-sentence root cause
**The weekly has no visual system of its own.** The specials evolved a strong,
distinct grammar; the weekly borrowed the special's *cover* wholesale, leaked bits
of the special's *body* grammar, never made its "warm paper" actually warm,
carries ~20 competing section colour-worlds, and then had a third "app-card" idiom
bolted on by the rebuild. It's backwards from how magazines work: **the weekly
should be the constant, quiet, recognisable thing; the special the rare dramatic
break.** Right now the weekly cosplays the special every week, so neither reads as
what it is.

---

## 2. The current system, inventoried (so the redesign is precise)

- **Type (actual):** Cormorant Garamond (serif — heads *and* body), DM Sans
  (labels/UI), JetBrains Mono (dates/labels). Cormorant is a delicate,
  high-contrast Garamond — fine for display, **too thin/high-contrast for body**,
  which reads screen-y at reading size. Scale (`04-layout-sections.css`): h2 36 /
  h3 22 italic / h4 13 DM uppercase / body 21 / cover-brand 60–80 / drop-cap
  64–72. **Two drop-cap systems** (`.foreword p::first-letter` @64 and
  `.dropcap::first-letter` @72).
- **Palette (`00-tokens.css`):** paper `#FAFAF8` / warm `#F5F4F0` (both cool),
  ink `#111119`, accents rose `#E8384F` + ember `#FF6D3A`, **plus ~20 per-section
  palettes** (Touchline linen/navy/green; Screen dark-purple `#14121E` / neon-pink
  `#FF2D78`; Shelf dark-brown/gold; Session light-green; History parchment; +
  rotating toolkit-cyan / ledger-amber / itinerary-coral / listen dark-brass /
  saga purple-gold…). Neon accents (`#FF2D78`) are screen colours.
- **Section chrome (per `.sec`):** 48–60px padding + a 140px serif **watermark**
  @4% + a 4px accent top-bar + a **full-width 8px saturated gradient divider**
  (`hr.divider.dv-*`) + gradient overlays — repeated 20 colour-ways. Loud.
- **Weekly component kit (~12, the palette):** `.angle`, `.pull-quote`,
  `.stat-bar>.stat`, `.dyk`, `.split-60-40`, `.hero-bleed`/`.img-offset`,
  `.also-cards`, `.rating`, `.radar-cat`, `.results-strip`, `.read-next`,
  `.case-against`.
- **Navigator (`04-navigator.html`):** out of sync — still lists retired sections
  (World / Gaming / Football / Film-TV / Books / Fitness / History), **no cards for
  The Letter, Caught Up, The Long Read, The Desk, The Threads** — the four-movement
  spine is not represented.

---

## 3. The redesign — one warm-paper system (north star)

**Direction: a "warm literary journal"** — the calm, tactile, print-behaving
Sunday read the north star always described, with light **section-coding
discipline** (labels + numbers, not colour fields) borrowed from a modern-editorial
approach. Restraint *is* the system. The weekly becomes the constant; the specials
keep their bound-magazine drama as the deliberate, rare break.

### 3.1 Type
- **Display:** **Fraunces** (variable — optical-size + soft/wonk axes; warm,
  literary, scales cover→section-head). Replaces Cormorant for display. *(Keeping
  Cormorant is an option, but only for display and only if warmed; its thin body
  weights are part of the screen-y feel.)*
- **Body:** a robust on-screen reading serif — **Source Serif 4** (or Newsreader /
  Literata). Body **19–20px, line-height 1.6–1.65, measure 62–68ch** (65 sweet
  spot). Suppress widows/orphans; enable hyphenation.
- **Labels/eyebrows:** keep **DM Sans** (uppercase, letter-spaced, ~13px, muted
  ink). **Data/dates:** keep **JetBrains Mono**, sparingly.
- **Scale:** Major-Third **1.25** (base 20 → 20/25/31/39/49/61/76). One drop-cap
  system, not two.

### 3.2 Palette — make the paper actually warm; one accent, not twenty
- **Light (warm paper):** paper **`#FAF6EC`** (true cream), raised panel
  `#F3EEE0`, ink `#16161D`, muted ink `#57544C`, hairline `#E4DDCB`. **One accent:**
  terracotta/coral `#C1502E` (with ember `#E4572E` as its brighter sibling); gold
  `#B8860B` as a *rare* secondary. **Retire the neon accents (`#FF2D78`,
  `#FF6D3A`-as-primary) and the ~20 per-section palettes.**
- **Warm-night (prefers-color-scheme: dark):** warm charcoal **`#1A1815`** (not
  the current cold plum, not pure black), raised `#232019`, text `#E8E2D4`, muted
  `#A39B88`, hairline `#332F27`, accent lightened to `#E8774A`.
- Section identity comes from **an eyebrow label + number in the accent**, never a
  full-width coloured band or background. Dark section inversions
  (Touchline/Screen/Shelf) are **retired** or reduced to a single deliberate device
  — not 3–4 jarring mid-magazine flips (the tokens already confess this jars).

### 3.3 Section identity & rhythm — one quiet language
Replace *watermark + 8px gradient bar + 4px accent bar + gradient overlay* (all
firing at once) with **one** signal:
- **Eyebrow/kicker:** DM Sans uppercase, ~13px, letter-spaced, muted ink, carrying
  the movement + section ("III · THE ROUNDS — THE TOUCHLINE").
- **Section head:** Fraunces, one weight.
- **Divider:** ONE motif everywhere — a hairline rule with a small accent tick.
  Retire the `dv-*` saturated gradient bars and the special ground-alternation
  from the weekly (ground-alternation stays a *special* device).
- Differentiate sections by **grid rhythm and image treatment**, not colour.

### 3.4 Component grammar — kill the third idiom
Re-skin the new service/continuity boxes (`.caught-up`, `.do-this-week`,
`.the-threads`, `.week-in-numbers`, `.case-against`) from grey app-cards into
**warm-paper hairline cards**: cream/raised-cream ground (or no ground — just a
hairline top rule + the eyebrow), warm hairline border, the single accent for the
label/rule, ink text. **Adopt the specials' two disciplines for the weekly too:**
ground-discipline (components don't self-paint cold backgrounds) and
readability-lock. The "Do This Week" pin should feel like a *letterpress margin
note*, not a UI alert.

### 3.5 Cover — give the weekly its own constant masthead
- **Weekly cover = a constant, recognisable, warm-paper masthead.** Same face,
  size, position every week (recognition is the ritual). Warm paper ground (not
  dark), the "The Signal." lockup, issue no. + date, **3–5 coverlines in a fixed
  hierarchy**, one restrained hero motif. **No animation** (drifting gradients /
  grain / fade-ins retired on the weekly). Reconcile the stale `82vh` vs `100vh`
  cover-height regression — and consider a shorter cover so content starts sooner
  (opening on a full screen of hero is part of the "not a calm object" feel).
- **Specials keep the dark, full-bleed, dramatic cover** as their signal of
  difference. The two must no longer share one template.

### 3.6 Navigator
Rebuild `04-navigator.html` for the **four-movement spine** (The Letter · Caught Up
· The Long Read · the Rounds incl. The Desk · The Threads · On the Radar…) — it
currently lists retired sections and omits every new one.

### 3.7 Delivery / weight (part of "a calm object")
- **Stop injecting special + holiday CSS and the 8 decorative holiday fonts into
  weeklies.** Ship a **weekly-only CSS+font bundle** (~150KB, 3 fonts) — the
  stitcher/`inject-assets.sh` should include special/holiday layers only for those
  formats. Target back down to ~150KB from ~600KB.
- Drop the JS `sp-chapter-beads` rail from the weekly (or make it a quiet
  weekly-appropriate element). Keep the **JS-off-renders-complete** contract.

---

## 4. The weekly ↔ special relationship (the thing to get right)
Define a **shared DNA** and a **deliberate divergence**, so they read as siblings,
not clones:
- **Shared:** the "The Signal." masthead lockup, the type system, the single accent
  family, the hairline-and-eyebrow section language, warm paper as the base.
- **Weekly-only:** the constant warm masthead cover; quiet sections; brisk rounds;
  no ground-alternation; no folios/marginalia.
- **Special-only:** the dramatic dark full-bleed cover; the bound-magazine body
  grammar (ground-alternation, chapter chrome, folios, three-column spreads,
  marginalia). These become a *rare treat*, earned by the format — which also makes
  specials feel special again.

---

## 5. Three concrete direction options (pick one; recommend B)
- **A · Quiet Broadsheet** — near-monochrome ink-on-cream; accent only on section
  numbers/rules; tight 1.25 scale, dense-but-airy columns; hairline dividers. Most
  restrained (NYT/Guardian discipline).
- **B · Warm Literary Journal (recommended)** — Fraunces display + Source Serif 4
  body; generous whitespace, 66ch measure, big margins; the single coral accent
  used once per section. Slow, tactile — the truest fit for "coffee on a Sunday."
  Borrow B's *section-coding discipline* from C.
- **C · Modern Editorial** — DM Sans labels doing more work; stronger grid
  contrast; Monocle-style A/B/C section coding; gold+coral duo on labels only. More
  structured, magazine-forward.

---

## 6. Suggested implementation order (for another instance)
1. **One design-token layer as the single source of truth** (`00-tokens.css`
   rewritten): the warm-paper palette, the one accent, the type scale, the spacing
   rhythm. Everything else references it. Delete the ~20 section palettes.
2. **Weekly cover** — new constant warm masthead (`02-cover.css` / `03-cover.html`);
   split special cover onto its own path.
3. **Section chrome + dividers** — collapse to the one eyebrow+hairline language;
   retire watermarks / 8px gradient bars / dark inversions from the weekly.
4. **Re-skin the service/continuity components** (`15a`/`15b`) to warm hairline
   cards under a weekly ground-discipline.
5. **Type swap** (Fraunces + reading-serif body); unify drop-caps.
6. **Navigator rebuild** for the four movements.
7. **Build/weight** — weekly-only asset bundle in `inject-assets.sh`/stitcher.
8. **Dark warm-night variant** (prefers-color-scheme), matching the home (H4).

## 7. Research sources (cited)
Cohesion-by-system: Monocle ([magculture](https://magculture.com/blogs/journal/monocle-redesigned)),
Kinfolk ([magculture](https://magculture.com/blogs/journal/kinfolk-18)),
Guardian five-pillar colour ([design system](https://guardian.github.io/theguardian.design/)),
NYT three-face system. Type: Fraunces (variable literary display), Source
Serif 4 / Newsreader / Literata (on-screen reading serifs); Major-Third scale
([type-scale](https://www.pacgie.com/type-scale)); measure 62–68ch, line-height
1.6–1.65. Palette: warm-paper/sepia editorial neutrals; warm-dark for night
reading. Masthead-as-constant ([Fabrik](https://fabrikbrands.com/branding-matters/graphic-design/what-is-a-magazine-masthead-magazine-masthead-design/)).
Avoid per-section colour bands ("riot of colours" — [Guardian critique](https://theconversation.com/new-look-guardian-is-a-riot-of-modern-tabloid-colours-but-its-still-the-paper-i-know-90057)).

## 8. Coordinate with the other two workstreams
- **Structure** (`…first-run-handoff…`): the redesign should style the **four
  movements** as first-class visual bands, and The Desk as one nested department —
  so structure and visuals reinforce each other.
- **Reliability** (`…reliability-rebuild-design…`): fold a **visual-consistency
  assertion** into the structural gate — e.g. weekly must not load special/holiday
  CSS or the 8 holiday fonts; no `sp-*` body components in a weekly; the cover uses
  the weekly masthead, not the special hero. Then a visual regression can't
  silently return.

## 9. Key files
`assets/css/00-tokens.css`, `02-cover.css`, `04-layout-sections.css`,
`19-phase2-typography.css`, `15a-service-continuity.css`, `15b-open-argument.css`,
`19-chapter-beads.css`, `23–32-*` (specials), `36–44` (holiday);
`template-parts/03-cover.html`, `04-navigator.html`, `05-foreword.html`,
`13a-the-desk.html`, `15a-the-threads.html`, `15b-week-in-numbers.html`;
`scripts/inject-assets.sh` + `stitch-issue.sh` (asset injection / weight);
`references/spec/global.md` (§ Visual Design, editorial body kit, ground-discipline),
`references/spec/weekly.md`.

**One-line summary for the implementer:** the weekly has no visual system — it
wears the special's dramatic dark cover every week, never made its "warm paper"
warm, carries ~20 clashing section colour-worlds, ships 600KB of injected
special+holiday CSS/fonts, and the rebuild bolted a third "app-card" idiom on top.
Give the weekly ONE warm-literary-journal system (true cream paper, Fraunces +
reading-serif, a single accent, eyebrow+hairline section language, a constant warm
masthead), re-skin the service components into warm hairline cards, ship a
weekly-only ~150KB bundle, and reserve the dark bound-magazine drama for specials —
so the weekly is finally the calm, constant Sunday object and specials feel special
again.
