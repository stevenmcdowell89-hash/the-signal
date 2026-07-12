# The Signal — Visual Identity, from first principles (ground-up design spec)

**Status: DESIGN — hand-off for another instance to implement.** A **ground-up
visual identity** for the weekly, designed *from the magazine's stated intent*,
not reverse-engineered from the current CSS. This **supersedes** the reactive
`docs/weekly-visual-redesign-recommendations-2026-07.md` as the primary design
direction; that doc is retained only for its **current-state audit** and its
"what to leave behind" inventory (§7 here points to it). Companion docs:
`…first-run-handoff…` (structure), `…reliability-rebuild-design…` (reliability).

**Why a second visual doc.** The first one audited what the weekly *does now* and
prescribed cleanup — reactive. This one starts from what The Signal *is and is
for* (primary-source intent, Part 1), derives design principles that each trace to
that intent (Part 2), and designs the system from those principles (Part 3). The
current implementation is a reference for what to *avoid*, never the driver.

---

## Part 1 — The intent (the magazine, in its own words)

Everything below is quoted/distilled from the spec (`editorial-spec.md` = EC,
`spec/global.md` = G, `sections.md` = SEC, `docs/signal-final-recommendations…` =
REC, `SKILL.md`).

- **Purpose.** *"A weekly personal Sunday-morning magazine for **one reader** — not
  a news digest"* (EC). Its job is *"the **layer time gives**: synthesis across the
  week… roundups… evergreen features, recommendations, curiosity, and reference
  data"* — because *"the daily owns the week's catch-up"* and by Sunday the reader
  *"arrives already informed."* The north-star, verbatim everywhere: **"Did this
  issue tell him what the week added up to, and give him one thing to do?"**
- **The reader (design for this person).** A tech-literate professional in
  **Northern Ireland with a 10-year-old son**, reads on a **Xiaomi Pad 8 tablet
  (~800px portrait)**, *"wants analysis, context, and the stories behind the
  stories,"* does **NOT** want work content, celebrity, royals, or generic advice.
  Interests: world affairs, Nintendo/Switch, **Juventus & Serie A**, consumer tech
  & AI, LEGO, **fantasy/sci-fi (Malazan, Cosmere — no spoilers)**, synthwave,
  **fitness (a live marathon build)**, history, **Disney parks/Efteling trips**, UK
  fintech. His life is tracked *live* — the marathon block, the Efteling trip, the
  Juventus result, his FPL rank.
- **The ritual.** *"Read on a **Sunday morning with coffee**."* *"30–45 minutes of
  selective reading from a 60–90 minute issue."* The intended object: *"a perfectly
  curated Flipboard combined with a great Sunday supplement and a weekly planner."*
  It must **end on action** — *"a **verb and a human line**, never an aphorism."*
- **Voice.** *"Reader invisible, Editor visible."* A **named Editor** speaks in the
  first person — The Letter states the week's thesis and connects the dots.
  *"Confident and opinionated, but the opinion is borrowed, not invented."*
- **Values (the sacred).** One deep centre, brisk rounds; *considered over
  comprehensive* (*"padding a thin idea to a floor is banned"*); *personal not
  generic*; substance & trust (*"a wrong image with a confident caption is worse
  than no image at all"*); a guaranteed discovery floor (*"taste is a lens, not a
  filter"*); **a person in the personal magazine**; ends on *something to do*.
- **What it is NOT.** *"A magazine, **not a news digest**."* Not the daily brief;
  not a feed re-list; not clickbait; not a content-mill of forced sections
  (*sections "yield rather than fill"*); not padded prose.
- **Distinctiveness.** The daily→weekly relationship; the branded section
  identities (**Touchline / Pixel & Byte / Screen & Sound**); **Down the Rabbit
  Hole** as *the* signature ritual; the four-movement spine; **reading-time
  badges**; the **editorial cover**.
- **Stated aesthetic intent (not just implementation).** A **"bound-magazine
  feel"** (a paper object). The **"paper-and-ink — renders complete with JavaScript
  off"** contract (it must behave like *print*, not a web app). Warm-paper
  continuity (the home should feel *"continuous with the warm-paper issues"*).

---

## Part 2 — Design principles (each derived from the intent)

1. **A printed object, not a web page.** *(from "a magazine, not a news digest" +
   "bound-magazine feel" + "paper-and-ink, JS-off renders complete")* The whole
   system must read as a considered, printed thing you hold — paper stock, ink,
   typographic craft, generous margins — and be **complete and beautiful with zero
   JavaScript**. No animation, no scroll-triggered reveals, no progress rails, no
   app chrome. Motion is not a tool here; the page is paper.
2. **Warm and unhurried — a Sunday treat.** *(from the coffee ritual, 30–45 min)*
   Calm, warm, tactile, generous whitespace, a slow reading pace. The emotional
   register is *pleasure and ease*, not information density.
3. **Tablet-portrait-first, held in one hand.** *(from Xiaomi Pad 8, ~800px
   portrait)* The primary canvas is **~800px portrait**, a single reading column,
   thumb-reachable. Design *there* first; desktop is the secondary case. Type,
   measure, margins, image sizing all tuned to that device and posture (coffee in
   the other hand).
4. **Quiet confidence — craft carries it.** *(from "confident but borrowed",
   considered)* The magazine earns gravitas through typography and restraint, not
   decoration. No shouting colour, no neon, no drama on the weekly.
5. **One deep centre; the rest is brisk.** *(from "one deep centre, brisk rounds")*
   The visual rhythm must *express* depth-vs-brevity: the Long Read is an immersive,
   full-measure spread; the rounds are scannable, compact, briskly typeset. The
   reader should *feel* the gear-change, not just read it.
6. **A person is behind it.** *(from "Editor visible", personal, life-threads)* The
   Editor's presence is a design element — the signed Letter, a human hand. The
   personal threads (the marathon, the trip, the FPL rank) get warm, intimate,
   almost-handwritten-adjacent treatment, not dashboard tiles.
7. **Section identities are a family, not a riot.** *(from "keep the branded
   identities" + restraint)* Touchline / Pixel & Byte / Screen & Sound etc. must
   stay recognisable **and** harmonious. Identity comes from a **disciplined code**
   (a section mark + one tint on the eyebrow), never a full-page colour field. One
   family, many members — not twenty competing worlds.
8. **It ends on something you can do.** *(from "a weekly planner", "one thing to
   do", "ends on a verb")* The service/action elements ("Do This Week", the Close)
   are designed as *considered planner notes* — the satisfying, actionable close of
   a Sunday sit-down — not UI alerts.

---

## Part 3 — The visual system (designed from the principles)

### 3.1 Materiality & mood — the paper object *(P1, P2, P4)*
- **True warm paper**, not cool grey: base stock a soft cream (**~`#FAF4E8`**),
  with a subtly warmer "second stock" for set-apart matter. Ink a **warm near-black**
  (**~`#1E1A17`**), never pure `#000`. The feeling is uncoated paper under a warm
  morning light.
- **Ink discipline:** body ink, a muted "pencil" grey for secondary/labels, and
  **one** accent. That's the whole ink set.
- **No gloss, no glow.** Retire radial glows, gradient bars, animated grain. Any
  texture is a *whisper* (an optional faint paper grain as a static asset, if any).

### 3.2 The reading canvas & grid — tablet-portrait-first *(P3, P2)*
- Design column for **~800px portrait**: a **single reading column**, body measure
  **~62–68ch**, generous side margins so the text block feels *set on a page*.
- A shared **vertical rhythm** (baseline multiples) governs all spacing so the
  whole issue breathes consistently — the "set in one press" feeling.
- The **Long Read** may use the full measure and larger images; the **rounds** sit
  in a tighter, more compact rhythm (see 3.6). Desktop widens the margins, never
  the measure (long lines break the reading).

### 3.3 Type — editorial gravitas, tablet-legible *(P1, P4, P2)*
The current Cormorant-for-body is delicate/high-contrast and reads screen-y at
size — wrong for a warm paper long read. Recommended (Google-Fonts-available):
- **Display / masthead / section heads:** **Fraunces** (variable — optical size,
  soft/wonk axes; a warm literary serif with real character; scales cover→heads).
- **Body:** a sturdy on-screen reading serif — **Source Serif 4** (or Newsreader /
  Literata). Body **~19–20px, line-height 1.6–1.65** on the tablet.
- **Eyebrows / labels / section codes:** **DM Sans** (uppercase, letter-spaced,
  muted) — keep it, it's a good editorial label face.
- **Data (dates, the Week-in-Numbers figures, reading-time):** **JetBrains Mono**,
  sparingly — a "typewritten datum" accent that suits the personal/planner tone.
- **Scale:** Major Third **1.25**. **One** drop-cap system (retire the duplicate).
- Suppress widows/orphans; hyphenate the body.

### 3.4 Colour & section identity — a family, one accent *(P4, P7)*
- **One primary accent** — a warm terracotta/coral (**~`#C0502E`**), with a deep
  gold (**~`#B08010`**) as a rare secondary. **Retire the neon** (`#FF2D78`, etc.)
  and the **~20 per-section palettes**.
- **Section identity via a disciplined code, not colour fields:** each branded
  section gets (a) a small **section mark/monogram** and (b) **one restrained tint**
  used *only* on the eyebrow label + the section number + a hairline tick — never a
  full-width band or a page background. So Touchline still *feels* like Touchline,
  but the page stays one warm paper. Think Monocle's letter-coded departments, not
  the Guardian's colour riot.
- **Dark section inversions** (the current mid-issue Touchline/Screen dark flips)
  are **retired** — or reduced to at most *one* deliberate, format-appropriate
  device, never 3–4 jarring flips.
- **Warm-night mode** *(prefers-color-scheme: dark, matching the home per REC H4):*
  warm charcoal (**~`#1A1613`**, not cold plum, not pure black), warm off-white
  text, hairlines in warm brown, accent lightened. Night reading, still paper.

### 3.5 The cover & masthead — the "my magazine" ritual *(P2, P6, distinctiveness)*
- The weekly cover is a **constant, recognisable, warm editorial cover** — the
  ritual object the reader returns to every Sunday. **Same masthead lockup, face,
  position every week.** Warm paper ground (not the current dark plum hero), the
  *The Signal.* wordmark, issue no. + date, a fixed **coverline hierarchy** (a lead
  line + 3–4 secondaries), and **one** restrained hero motif (a single image or a
  typographic cover — not a dark animated field). **No animation.** Shorten it so
  content begins sooner (opening on a full screen of hero fights the "calm object"
  feel).
- **Reading-time badge** kept and redesigned into the system (a quiet mono datum,
  "34 min · one sitting") — it's house furniture that serves the ritual (you know
  the sitting you're committing to).
- **Specials keep the dramatic, dark, full-bleed cover** — that becomes their
  signal of difference (see Part 5). The weekly must stop borrowing it.

### 3.6 The depth-vs-brevity rhythm — one centre, brisk rounds *(P5)*
- **The Long Read** is typeset as the issue's *spread*: full measure, larger
  Fraunces head, a drop-cap opening, room to breathe, generous figures — it should
  visually announce "settle in."
- **The Rounds** (Touchline, Pixel & Byte, Screen & Sound, the books rail, The
  Desk) are typeset **brisk and scannable**: tighter rhythm, smaller heads, list-
  and card-forward, short items with what/why/link. The reader should *see* these
  are quick.
- **Caught Up** (the 8-line digest) is the most compact of all — a clean numbered
  or ruled list, deliberately plain, "everything that moved, in eight lines."

### 3.7 Component grammar — paper elements, not app cards *(P1, P6, P8)*
Re-conceive the service/continuity/discovery components as **paper-object
elements**, replacing the grey rounded "app cards":
- **"Do This Week" pin** → a **planner margin-note**: a hairline-ruled block or a
  ledger line with the accent, an actionable imperative set apart like a note
  scribbled in a Sunday planner. Warm, not an alert box.
- **The Threads** → a **"previously on…" ledger**: a quiet ruled list of the running
  sagas + the reader's life-threads, intimate and continuous (P6). No grey box.
- **The Week in Numbers** → a **personal stat strip** in mono figures on paper — a
  typewritten line of the reader's week (miles, FPL, the Juventus score), "quietly
  personal," not dashboard tiles.
- **Down the Rabbit Hole** (the signature ritual) → its **own distinctive, warm
  treatment** — the one place a little visual character is *earned*, because it's
  the signature. A curiosity aside, marked with the section mark, that feels like a
  hand-drawn "…and if that interests you, go here."
- **The Case Against** → a set-apart counter-argument on the "second stock" tint
  with a hairline rule — considered, not a warning callout.
- All of these obey a **weekly ground-discipline** (borrowed from the specials):
  components do **not** self-paint cold backgrounds; if a component sets a ground it
  uses a warm paper tone and **locks its own ink** (readability-lock).

### 3.8 Motion & weight *(P1)*
- **Effectively no motion.** Paper doesn't animate. Retire drifting gradients,
  grain animation, tag fade-ins, the JS chapter-bead rail. The page is complete and
  still with JS off — which it must be anyway.
- **A calm object is a light one.** Ship a **weekly-only asset bundle (~150KB, 3
  fonts)** — stop injecting the special + holiday CSS and the 8 decorative holiday
  fonts into every weekly (~600KB today). Weight is part of the feel.

---

## Part 4 — What to leave behind (from the current-state audit)
The reactive doc (`…visual-redesign-recommendations…`) has the full inventory; the
headlines to *discard*: the dark animated special-style cover on the weekly; the
~20 per-section colour palettes + neon accents; the watermark + 8px gradient-bar +
4px accent-bar + overlay stack firing at once; the mid-issue dark inversions; the
duplicate drop-cap systems; the JS bead rail; the injected special/holiday CSS +
fonts; and the grey "app-card" service components (the third idiom the W-rebuild
introduced).

## Part 5 — Weekly ↔ special: shared DNA, deliberate divergence
- **Shared DNA (so they're siblings):** the *The Signal.* masthead, the type
  system, the single warm accent family, warm paper, the eyebrow+hairline section
  language.
- **Weekly = the constant:** warm editorial cover, quiet sections, brisk rounds, no
  ground-alternation, no folios.
- **Special = the rare break:** the dramatic dark full-bleed cover, and the
  bound-magazine body grammar (ground-alternation, chapter chrome, folios,
  three-column spreads, marginalia) — *earned* by the format, which makes specials
  feel special again. The weekly borrowing it every week is what broke both.

## Part 6 — Direction & recommendation
Three coherent expressions of the above (pick one): **A — Quiet Broadsheet**
(near-monochrome, most restrained); **B — Warm Literary Journal** (Fraunces +
reading-serif, generous, tactile — the truest fit for "coffee on Sunday");
**C — Modern Editorial** (labels/section-coding doing more work, more structured).
**Recommend B**, adopting C's disciplined section-coding — restraint as the system,
warmth as the mood, the tablet page as the canvas.

## Part 7 — Implementation & coordination (for the next instance)
1. **Author a single design-token layer as the source of truth** (`00-tokens.css`
   rewritten): the warm-paper palette, the one accent + section tints, the type
   scale, the baseline rhythm, the tablet-portrait canvas. Everything references it.
2. Build **on the tablet-portrait target first** (~800px), then widen margins for
   desktop.
3. Rebuild in this order: **tokens → cover/masthead → section language & dividers →
   re-skin the service/continuity/discovery components → type swap + unify drop-caps
   → navigator (four movements) → weekly-only asset bundle → warm-night mode.**
4. **Coordinate:**
   - *Structure* (`…first-run-handoff…`): style the four movements as first-class
     bands; The Desk as one nested department. Visuals and structure reinforce.
   - *Reliability* (`…reliability-rebuild-design…`): add a **visual-consistency
     assertion** to the structural gate — a weekly must not load special/holiday
     CSS or the holiday fonts, must not use `sp-*` body components, and must use the
     weekly masthead not the special hero. Then the halfway can't silently return.
5. **Key files:** `assets/css/00-tokens.css`, `02-cover.css`, `04-layout-sections.css`,
   `19-phase2-typography.css`, `15a-service-continuity.css`, `15b-open-argument.css`,
   `19-chapter-beads.css`; `template-parts/03-cover.html`, `04-navigator.html`,
   `05-foreword.html`, `13a-the-desk.html`, `15a-the-threads.html`,
   `15b-week-in-numbers.html`; `scripts/inject-assets.sh` + `stitch-issue.sh`;
   `references/spec/global.md` (§ Visual Design), `references/spec/weekly.md`.

**One-line summary for the implementer:** design the weekly as a *printed object for
a Sunday morning, held on an ~800px tablet with coffee* — true warm cream paper,
warm ink, Fraunces + a reading serif, ONE accent with disciplined per-section
coding (a mark + a tint on the eyebrow, never a colour field), a constant warm
editorial cover (the dark bound-magazine drama reserved for specials), the Long
Read as the one immersive spread against brisk scannable rounds, the
service/continuity/discovery elements as warm paper planner-notes not grey app
cards, no motion, and a light ~150KB weekly-only bundle — so every visual choice
serves what The Signal *is*: a considered, personal, unhurried magazine, not a news
app wearing a special's costume.
