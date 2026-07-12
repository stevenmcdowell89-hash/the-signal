# Spec slice — weekly

_This file consolidates the weekly/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Standard Weekly (default)
The full Sunday edition, published as **The Transmission** — the weekly's constant identity (see § Section Structure → The Transmission identity). **Target ~6,000–9,000 words (v8.37, W-3 — roughly a 40% cut from the old ~20-30-page issue).** This is a real target, not just guidance: the four-movement spine (one Long Read, brisk rounds, an 8-line Caught Up) is built to land in this band. It is still shaped by *movements and per-piece shape*, not a rigid quota — flex to the news, yield thin rounds rather than padding — but an issue drifting well past ~9k words has reverted to the old two-anchors-everywhere bulk and should be cut back to the spine. The deep length lives in the single Long Read; the rounds stay short. Section order per the four movements above.

**Build model (v8.42 — deterministic stitch).** The weekly is assembled by `scripts/stitch_weekly.py` against the skeleton at `references/format-skeletons/weekly.json` (the structure of record). The stitcher **generates all chrome deterministically** — the tuner cover with its station list, the four movement dividers, every band-head, the waveform-rule dividers, the colophon and the sign-off. **Writers produce only per-band inner content** in the component vocabulary below (§ Component Quick Reference), one band per writer, written to `/tmp/signal-build/chapters/<band_id>.html` with **no `<section>` wrapper, no band-head, no movement divider** — the stitcher owns all of that. The canonical visual/markup target is `docs/mockups/reference-issue-transmission.html`, and the golden fixture at `references/golden/weekly/` is a real valid issue (plan + one inner-content file per band).



---

## sections

## Section Structure (Standard Weekly)

Sections are divided into **fixed** (appear every issue, except where noted) and **rotating** (appear on a cadence, selected per issue). Each issue includes the fixed sections plus **2-3 rotating sections**. The Navigator adapts to show only the sections present in that issue. The issue ends with a Colophon (sign-off block) before the Footer — see § End-of-Issue Colophon.

> **Why 2-3 rotating slots (v8.27, was 3-4 in v8.16).** The v8.16 roster grew to 14 rotating sections by *splitting* (The Listen out of the books rail, The Local out of The Itinerary, plus Brickyard / Saga / Lab / Channel), which made several sections compete for the same content and let one interest flood an issue. v8.27 redesigns the roster around the reader's actual interest-domains — one home per domain — collapsing the pool right down (books are **not** in it — they are the fixed Bookmark rail; see below). Fewer sections + fewer slots = less slot-filling pressure and a shorter, less-padded issue, back toward the "good era" size.

### The Transmission identity (v8.39 — the weekly's constant look)

The weekly is **The Transmission**: a single, constant **warm-cream paper object** that never changes costume week to week. It is the reader's Sunday-morning tuner — received and tuned, not staged. The identity is fixed and load-bearing:

- **Palette:** `--paper #F5F0E6` / `--ink #16151A` / signal-vermilion `--signal #FF3B2F` / `--blue #243F5C` (plus `--paper-2 #EFE8D9`, `--muted`, `--hair`). Vermilion is the one accent — used sparingly, per § Accent lockdown.
- **Type:** **Instrument Serif** (display / masthead / numerals), **Newsreader** (body serif), **JetBrains Mono** (mono eyebrows, codes, labels). No other families.
- **Furniture:** **waveform-rule dividers** (`.wave` SVG frequency rules, plus the `.tickrule`) between movements and around the Long Read; a **tuner-style cover** whose contents are a **"station list"** (`.tuner` > `.station` coverlines, each with a `.freq` and a name); **band-code section eyebrows** (`BAND NN — TITLE` in mono); an oversized `.folio` numeral; the `.masthead` wordmark ("The *Signal*").
- **A warm-night dark variant** is the only theme shift — a night reading of the *same* paper object, never a different costume.

**The weekly loads ONLY its own light bundle** — `assets/css/weekly/*.css` and the three Transmission fonts above. It **never** loads the special/holiday CSS layers, the special/holiday decorative fonts, or any `.sp-*` / `.hol-*` component. **The dark, dramatic bound-magazine treatment (`body.is-special`, `.cover-poster`, `.sp-*`, the ~20 per-section palette tokens, sticky-scroll chapter gates, ground alternation) is RESERVED FOR SPECIALS** and is forbidden in a weekly. `validate-issue.py --format weekly`'s visual-consistency gate hard-fails a weekly that ships any special/holiday marker (see `weekly.json` → `visual_consistency`).

### Four-Movement Architecture (v8.37, W-3 — the spine)

The weekly is organised as **four movements**, and each movement holds an ordered set of **bands** (the reader-facing sections). The movements are the spine; the bands live *inside* them. `references/format-skeletons/weekly.json` is the **structure of record** — the movement/band order, band ids, runtimes, requiredness and per-band component are all declared there, and the stitcher, the plan validator, and `validate-issue.py --format weekly` all read it. The order below is the canonical issue order. **The issue ends on a verb and a human line** — a Do This Week and the Colophon's sign-off, not an aphorism.

- **I · THE OPEN** (`data-movement="open"`) — discharge completeness up front, then hand off.
  - **The Letter** (band `the_letter`) — the signed editor's letter (§ The Letter). The week's thesis, dots connected across domains. Component: `.letter`.
  - **The Week in Numbers** (band `week_in_numbers`) — the compact **personal** ledger of the reader's week (§ The Week in Numbers). Component: `.figures`.
  - **Caught Up** (band `caught_up`) — a hard-capped **8-line, non-expandable** digest of the week's missable news across domains (§ Caught Up). This is where completeness is discharged: eight lines, then done. Because Caught Up carries the breadth, **no downstream section owes a "safety-net headline" backstop** — the old breadth-safety-net-in-every-section rule is retired (see § Caught Up). Component: `.digest` (`<ol>`, HARD cap 8 `<li>`).
- **II · THE LONG READ** (`data-movement="long-read"`) — exactly **ONE** deep anchor per issue (band `long_read`, carrying `data-role="long-read"`), subject rotating week to week. This single Long Read is the issue's one considered centre of gravity: it **absorbs the old Saga, Deep-Dive-lite, and evergreen-feature impulses**. There is no second mandated deep anchor anywhere else in the issue — the rounds carry the week's news at whatever depth the material earns, not a forced considered-piece backbone (§ Article Structure). Component: `.lr-title` + `.lr-body`.
- **III · THE ROUNDS** (`data-movement="rounds"`) — the week's domains, briskly, in this order:
  - **The Touchline** (`touchline`, sport) — `.lead` + `.scores` + `.items`.
  - **Pixel & Byte** (`pixel_byte`, gaming + LEGO) — `.items`.
  - **Screen & Sound** (`screen_sound`, watch & listen) — `.with-rail` = `.items` + the **Release Radar** rail (`<aside class="rail" data-role="release-radar">`). Release Radar is this rail and **never its own band**.
  - **Bookmark** (`bookmark`) — the fixed lightweight **books rail** every issue (`.picks`): what to read, a few picks with a line each. The deep book piece, when there is one, is the Long Read, not here.
  - **1–2 rotating** (`rotating_1`, `rotating_2`) — picked from the non-Desk pool (This Week in History, Listening) or the trigger-driven Saga. Component: `.items`.
  - **The Desk** (`the_desk`) — ONE service department (`data-role="desk"`) holding **1–2 columns** (`.deskcol[data-desk-column]`), each closing on its Do This Week `.pin`. Never 3+ columns; never a column as its own band. Component: `.desk`.
  - The rounds are rounds — news and picks, not essays.
- **IV · THE CLOSE** (`data-movement="close"`) — continuity, then forward, then act, then sign off.
  - **The Threads** (`the_threads`) — the continuity engine (§ The Threads): "previously on…" recaps of the named sagas and the reader's life-threads. Component: `.threads`.
  - **Down the Rabbit Hole** (`rabbit_hole`) — the signature discovery ritual, when due. Component: `.rabbit`.
  - **On the Radar** (`on_the_radar`) — the forward calendar. Component: `.radar` (`<ul>`).
  - **Do This Week** (`do_this_week`) — the issue's single strongest actionable pin surfaces here as the closing beat (the Desk columns each carry their own; this is the one the reader leaves on). Component: `.closepin`.
  - **Colophon** (`colophon`) — the issue accounted for: four `.endnumbers > .cell`. The stitcher appends the `.colophon` footer + `.signoff-line` sign-off after it.

> **The bands are the sections — the movements just group them.** "The Week, Composed" is retired: its on-ramp job is now done by the tuner cover's **station list** (the deterministic navigator) plus The Letter; the deep-anchor rotation across sections is replaced by the single Long Read. Books are the fixed **Bookmark** rail, never a rotating shelf (see § Fixed vs Rotating). Everything else keeps its identity and moves under the movement it belongs to.

**Chrome vs. content — the writer contract (v8.39).** Everything above the band's inner content is **chrome the stitcher generates deterministically** from `weekly.json`: the tuner cover + station list, the four movement dividers, every band-head (`BAND NN — TITLE` + runtime), the waveform-rule dividers, and the colophon footer + sign-off. **A writer is assigned one band and writes ONLY that band's inner content HTML** — the components named above — to `/tmp/signal-build/chapters/<band_id>.html`. That file has **no `<section>` wrapper, no band-head, and no movement divider**; the stitcher wraps it. The only structural hooks a writer adds inside their content are the two the validators key on: **`data-role="release-radar"`** on the Screen & Sound rail, and **`data-desk-column`** on each Desk column. See § Component Quick Reference for the exact inner markup per band, and `references/golden/weekly/chapters/` for a real example of each.

### Enforced structural invariants (validate-issue.py --format weekly)

These structural rules are **HARD-CHECKED by the markup gate**, not soft prose — `scripts/validate-issue.py --format weekly` now FAILs (does not merely warn) on each violation, inside the existing markup-contracts gate (the ledger stays at three gates). They key on the **invisible `data-*` structural hooks** the stitcher emits (declared in `weekly.json` → `structural_hooks` / `invariants`), so the gate is decoupled from display class names:

1. **All FOUR movements render** — THE OPEN / THE LONG READ / THE ROUNDS / THE CLOSE. The set of `data-movement` values on the `.movement` dividers must equal `{open, long-read, rounds, close}`; the check reports which are missing.
2. **EXACTLY ONE Long Read anchor** — exactly one element carrying `data-role="long-read"`. Fails on 0 or >1.
3. **The Desk is ONE nested department** — exactly one `data-role="desk"`, holding **1 or 2** `data-desk-column` elements (never 3+, never 0), and **never** a column as its own band or navigator station. Fails if any band carries `data-band` in `{session, ledger, itinerary, toolkit}`, or any station links to one.
4. **Release Radar renders INSIDE Screen & Sound** — `data-role="release-radar"` must exist and be a descendant of the `screen_sound` band; it must **never** be its own band (`data-band="release_radar"`) or navigator station. (On the Radar, band `on_the_radar`, is a separate, unaffected section.)
5. **Navigator ceiling** — the reader-facing navigator entries (`data-station` coverlines on the cover tuner) must be **between 4 and 13**.
6. **Caught Up cap** — the `.digest` carries at most **8** `<li>` items.

The **visual-consistency gate** (also hard-checked; `weekly.json` → `visual_consistency`) additionally fails a weekly that loads any special/holiday CSS marker or font, uses any `.sp-*` body component, or ships the special dark hero instead of the `.masthead` Transmission wordmark. Together these encode the four-movement + constant-identity intents that shipped broken on the 2026-07-12 first run (two movements missing, the Desk exploded into 3 standalone sections, Release Radar as its own section). See `docs/weekly-first-run-handoff-2026-07-12.md`.

### Fixed vs Rotating

**Fixed (every issue), grouped by movement (v8.39):** (the deterministic cover + tuner station list is chrome the stitcher generates — it is not a band a writer authors.)
- **I · THE OPEN:** **The Letter** (`the_letter`), **The Week in Numbers** (the personal ledger — see § The Week in Numbers), **Caught Up** (the 8-line completeness digest — see § Caught Up).
- **II · THE LONG READ:** **The Long Read** (`long_read`, `data-role="long-read"`) — exactly ONE deep anchor, rotating subject (see § The Long Read).
- **III · THE ROUNDS:** The Touchline, Pixel & Byte (gaming + LEGO), Screen & Sound (with the Release Radar rail), the **Bookmark** books rail, 1–2 rotating bands, **The Desk** (1–2 service columns; see § The Desk). *(The World This Week is not a fixed round — world coverage leads in Caught Up and, on weeks it earns the depth, as the Long Read.)*
- **IV · THE CLOSE:** **The Threads** (the continuity engine — see § The Threads), Down the Rabbit Hole (if due), On the Radar, Do This Week (the closing pin), Colophon (the stitcher appends the sign-off footer).

The old "Long Shelf" / "The Week, Composed" on-ramp is retired — the tuner cover's **station list** now does the navigator job and The Letter carries the orientation. Books are the fixed **Bookmark** rail in THE ROUNDS, never a rotating shelf. The World This Week is no longer a standalone fixed round: its safety-net breadth lives in Caught Up, its depth (when the week earns it) in the Long Read.

> **Yield rather than fill (v8.34).** The "yield when the week is thin, don't pad it to appear" principle applies to **every** fixed section: a fixed section whose week offers only catch-up — the recap the daily already delivered — **yields** that week rather than running a roundup to fill the slot. The mandatory element is the considered piece (§ Article Structure), not the section's mere presence. (For Desk columns the analogue is: run the column only when its domain has real service news, and each column that runs still closes on a "Do This Week" pin.)

**The Desk (service department — the home for all service content, v8.36).** The Desk groups four **service columns**, of which **1–2 appear per issue** — picked by which domain is most overdue *and* has real service news to act on this week:
- **The Session** (fitness) — keeps its existing fitness brief and content rules.
- **The Ledger** (money / personal finance / consumer fintech / side-hustle & Etsy) — the rebrand of the former "Money" rotating section; same three streams, new name (the CSS `.ledger-section` / `--ledger-*` tokens already exist).
- **The Itinerary** (travel / theme parks / NI-local) — the rebrand of the former "Places" rotating section; same content.
- **The Toolkit** (tech / Android / e-ink) — keeps its existing tech brief.

The Session and The Toolkit are **no longer standalone fixed sections** — they are Desk columns alongside The Ledger and The Itinerary. Each Desk column that runs **ends in a "Do This Week" pin** (see § The Desk below): exactly one concrete, do-it-this-week action with the *why* attached and the selection **criteria stated, not vibes**.

**Rotating, non-Desk (cadence-based, pick 1-2 per issue on top of the Desk columns):** This Week in History, Listening (podcasts + audio drama + music). These are *not* service columns and carry no "Do This Week" pin — they are discovery/reflection, not the service desk. (Books are no longer a rotating section — they are the fixed **Bookmark** rail in THE ROUNDS every issue; see § THE ROUNDS.)

**Trigger-driven (no cadence timer):** The Saga (lore deep-dive). It does NOT rotate on a clock — it runs only on a *reason*: a live public peg the researcher finds (a finale aired, a new book/season in a series the reader follows released, an author AMA), or a private peg the reader supplies (`currently_reading` / `currently_watching` in state, or a manual "run a Saga on …" trigger). See its brief in `references/sections.md` and the trigger note under § Auto-Triggered Specials.

See **Rotation Mechanics** below for scheduling rules.

### The Desk — the service department (v8.36)

The Desk is the restored **service department**: the one place in the issue whose job is not to inform but to help the reader *do* something this week. It groups four rotating **service columns** — **The Session** (fitness), **The Ledger** (money), **The Itinerary** (travel/parks/NI), **The Toolkit** (tech) — and **1–2 run per issue**, chosen by which domain is most overdue *and* has real, actionable service news (not by a cadence clock alone). A domain with nothing actionable this week yields rather than padding to appear. Full column briefs live in `references/sections.md` § The Desk.

**The "Do This Week" pin — the mandatory closing element of every Desk column.** Every Desk column that runs **ends on exactly one "Do This Week" pin**: a single concrete, do-it-this-week action, with the *why* attached and the **selection criteria stated, not vibes**. The pin names the specific thing and says why *that* one — not a hedge.

- **Good:** "Move your emergency fund to Chase Saver at 4.75% AER — it's the top easy-access rate right now with no intro-bonus cliff."
- **Bad:** "Consider a high-interest savings account." (no named product, no stated criterion, not do-it-this-week).

One pin per column, always last. Markup: each Desk column (`.deskcol[data-desk-column]`) ends in a `.pin` (`.pinlbl` label + `.act` action line + `.why` rationale); the issue's single strongest pin also repeats as the standalone `.closepin` in Do This Week. The pin is service, not an aphorism — it is exempt from the one-aphorism-per-issue cap and is *not* the section's Lead.

### The Threads — the continuity engine (v8.36)

**The Threads** is a fixed, reader-facing continuity section built off the state file's `ongoing_stories` — extended **beyond World** to named sagas across **all** domains, plus the reader's own **life-threads**. It is the "previously on…" of the magazine: each thread is a few lines of situation-report recap with a link, so a story the reader has been half-following snaps back into focus.

- **Two kinds of thread:**
  1. **Named sagas** (from `ongoing_stories`, any domain): an Iran-endgame thread, a Serie A / Antonelli title-run thread, a long-running show arc, a Switch-2-ecosystem thread — whatever the state file is tracking as live. Each gets a short "previously on / where it stands now" recap and a link.
  2. **Life-threads** (the person in the personal magazine): the marathon build from state `training_phase`, the upcoming trip from state `upcoming_trips` (e.g. the Efteling trip) — the reader's own ongoing arcs, recapped the same way ("Week 6 of the block; long run up to 18 miles; taper starts…").
- **`ongoing_stories` now feeds ONLY The Threads (v8.37, W-3 — the topic-lock suppression role is dropped).** In v8.36 `ongoing_stories` was dual-use: the Topic-Lock suppression backstop *and* The Threads' data source. W-3 **retires the suppression backstop** (§ Topic Lock — the sliding-window cap and `check-topic-lock.py` are gone). `ongoing_stories` is now a single-purpose, reader-facing asset: The Threads reads it to recap named sagas across all domains. `training_phase` + `upcoming_trips` additionally feed the life-threads. Dropping suppression-by-gate in favour of The Threads' recap is deliberate — a story that keeps recurring is *recapped*, not hidden.
- **Voice:** situation-report + "previously on" recap tone — factual, compact, each thread a few lines and a link. No new opinion or invented angle; it is a *recap*, not a Lead. It does not carry a "Do This Week" pin (that is the Desk's job).
- **Placement:** part of the closing movement — after the rounds, near On the Radar (continuity flows naturally into the forward calendar).
- **Markup:** the `.threads` component — one `.thread` per recap (`.ep` episode tag + `<h3>` + `.prev` "previously" line + a `<p>` "where it stands now, Next: …").

### The Week in Numbers — the personal stat strip (v8.36)

**The Week in Numbers** is a small, fixed, compact **personal** stat strip near the top of the issue: a handful of numbers about *the reader's* week, not the news. Drawn from state and the week's results:

- **Garmin miles + current training block** (from state `training_phase`) — e.g. "31.2 mi · Base block, wk 6".
- **FPL rank** — the reader's Fantasy Premier League overall rank movement.
- **The Juventus result** — the week's Juve scoreline.
- **One money number** — a single figure from The Ledger's world (a savings rate, an Etsy month, an ISA milestone).

It renders as the Transmission `.figures` component — a `.figures-frame` with a `.fig-caption`, one `.fig-row` per number (`.fig-label` = `.k` key + `.d` description, beside a `.fig-val`), and a `.fig-foot`. 4–5 rows, quietly personal.

> **Distinct from the Colophon's "Issue in Numbers" (v8.36).** The Week in Numbers is about **the reader's week** (his miles, his rank, his team's result). The Colophon's Block 1 "Issue in Numbers" (§ End-of-Issue Colophon) is about **the issue itself** (word count, sections, links, images). **Keep both** — they measure different things; never merge them or let one's stats leak into the other.

### The daily→weekly bridge — the digest + Saved This Week (v8.38, W-4)

The daily and the weekly **share real data** — this is the personalization loop that makes the weekly's "already-informed reader" premise run on bytes, not assertion. When composing the issue, weekly generation reads **two** inputs from the daily side, in **Phase 0/3** (before The Letter and The Threads are written):

1. **The daily digest endpoint — `GET /api/daily/digest?since=7d`** (Daily D-3). Returns `{ surfaced, moved, saga_lines, ... }`: what the daily brief *surfaced* this week and, crucially, what **moved** (a story that changed signal-tier — "was *linked with* → now *here we go*") plus per-saga one-liners. This is the machine-generated record of the week's arc.
2. **Saved This Week — the reader's own input** (a lightweight state field, below). What the reader chose to *keep* from the daily brief this week. This is the human signal on top of the machine signal.

**Where each is consumed:**

- **The Letter** reads `digest.moved` + `digest.saga_lines` + `saved_this_week` to find **the week's thesis and the cross-domain dots**. The Editor's job in The Letter is to connect what moved with what the reader cared enough to save — the strongest thread through the week is usually where a *moved* story and a *saved* item rhyme. (The machinery stays invisible per the Cardinal Rule — never write "you saved this" or "the daily carried X".)
- **The Threads** reads `digest.saga_lines` + `saved_this_week` (matched against `ongoing_stories` topics/aliases) to decide **which sagas to recap and how far they moved** since last week, and to surface a saved thread the reader is actively following even if `ongoing_stories` hadn't flagged it. A saved item that maps to a tracked saga raises that thread's priority in The Threads.

**The `saved_this_week` state field (shape).** A lightweight array in `state/signal-state.json`, populated by the daily save-for-later affordance (Daily D-2) and consumed read-only by the weekly. Cleared/rotated after each weekly ships (keep the last issue's set for reference under `saved_last_week` if useful). Shape:

```json
"saved_this_week": [
  {
    "title": "Antonelli confirmed at Mercedes for 2027",
    "url": "https://...",
    "domain": "touchline",
    "saved_at": "2026-07-08",
    "daily_why": "the seat the paddock spent all spring guessing about",
    "saga": "antonelli-title-run"
  }
]
```

- `title`, `url` — the saved item (carry the daily's `{title, why, link}` straight through).
- `domain` — maps to a weekly section/round for routing (`touchline`, `pixel_byte`, `world`, …).
- `saved_at` — ISO date; lets the weekly weight recent saves.
- `daily_why` — the `why` the daily already computed (reused, not re-derived).
- `saga` — optional; the `ongoing_stories` topic slug this item belongs to, if any. When present, The Threads uses it to raise that thread's recap priority.

If `saved_this_week` is empty or the digest endpoint returns nothing (a quiet week, or the daily was down), The Letter and The Threads fall back to `ongoing_stories` + the research bundle as before — the bridge **enriches**, it is never a hard dependency.


For individual section content rules, voice notes, and research guidance, see `references/sections.md`. Only read sections appearing in this issue.

### The Letter — the opening movement (v8.35, replaces the author-less Foreword)

The weekly opens on **The Letter**: a signed editor's letter in place of the old author-less Foreword. A **named Editor speaking in the first person** ("I") sets out **the week's thesis** — what the week added up to — and **connects the dots across domains** (the world story that rhymes with a gaming shift, the training idea that lands the same week as a football result). It is the one place the magazine has a visible human behind it; the branded feel is kept, not softened.

- **Length:** ~120–200 words. It is an *opening movement*, not a full essay — say the thesis, draw two or three threads together, and hand off to the issue.
- **Voice:** first-person **Editor** voice is explicitly permitted here (see § Key Rules → The Cardinal Rule and Gate 1A: the Editor is visible; the *reader* stays invisible). Sign it off "— The Editor". Never address or describe the reader ("you", "your son", "as a Juventus fan") — that is still a Gate 1A leak.
- **Markup:** the Transmission `.letter` component — `<h2>` title, a `.kicker` line, a drop-cap opener (`<p class="first">`), body paragraphs, then the `.sig` ("— The Editor") + a mono `.sigline` transmitted-date stamp. The band-head chrome and navigator station are generated by the stitcher.
- One genuine aphorism is allowed across the whole issue (see § Editorial Voice); if you spend it, spend it here or in the Long Read — not as a per-section habit.

> **"The Week, Composed" is retired (v8.39).** The old triple on-ramp (Navigator + Long Shelf + Foreword-as-contents) collapsed to a single composed paragraph in W-3, and in the Transmission rebuild collapses further: the tuner cover's **station list** is now the deterministic navigator, and The Letter carries the reading orientation. There is no separate "Week, Composed" band — do not author one.

### Caught Up — the 8-line completeness digest (v8.37, W-3)

**Caught Up** is a hard-capped, **8-line, non-expandable** digest in Movement I that discharges the week's completeness up front. Eight lines, one per missable item, each a single tight line (a specific fact + a link) across the reader's domains — world, sport, gaming, tech, culture. Then it stops.

- **Hard cap: 8 lines, never more, and non-expandable** — no "…and 6 more", no collapsible, no companion list. If there are more than eight things, the ninth wasn't missable enough. The cap is the point: completeness is a *fixed budget*, not an open drawer.
- **It replaces the breadth-safety-net-in-every-section rule.** Historically every fixed section's Catch-Up had to carry "one-line safety-net headlines" so demoting a story out of a Lead never dropped it. Caught Up now owns that job for the whole issue: the week's big headlines survive *here*, in one place, up front. **Downstream sections no longer carry safety-net headlines** — the rounds cover their domain's real news at the depth it earns and nothing more (§ Article Structure; the safety-net clause is retired).
- **Voice:** flat, factual, fast — the anti-essay. No angle, no synthesis (that is the Letter's and the Long Read's job). Each line reads like a wire headline the reader can act on or ignore.
- **Markup:** the `.digest` component — an `<ol class="digest">` of **≤8** `<li>`, each a single `<p><b>Label.</b> …</p>` (a bold domain label + the tight line). HARD cap 8, enforced by the markup gate. Renders complete with JS off (no expand affordance exists to break).

### The Long Read — the single deep anchor (v8.37, W-3, supersedes the deprecated Anchor-Piece Rotation)

Movement II is **one** deep anchor per issue — the issue's sole considered centrepiece, subject rotating week to week (world one week, a game or a training idea or a book the next). It is the `long_read` band (its section carries `data-role="long-read"`, the hook the "exactly one Long Read" invariant checks), opens with a strong opener, and runs long enough to earn the space (typically 900–1,800 words; longer when the subject genuinely warrants). It **absorbs the old Saga, Deep-Dive-lite, and evergreen-feature impulses** — those are no longer separate deep beats scattered across the issue; the deep work concentrates here. Exactly one runs; there is no second mandated anchor. (The whole-issue Deep Dive special is unaffected — the Long Read is a weekly *movement*, the Deep Dive is a whole-issue interruption.)

- **Markup:** the Transmission long-read vocabulary — a `.lr-title` header (mono eyebrow, `<h2>` with an `<em>` accent, a `.stand` standfirst, a mono `.byline`) followed by `.lr-body` (drop-cap `p.first`, then paragraphs, with `.pullquote`, `.plate-img` captioned images, and an optional `.aside-note` = **The Case Against** counter-argument, all drawn from the body as the material earns them).

### Synthesis-by-juxtaposition — a prose technique for contested material (v8.38, W-4)

**Synthesis-by-juxtaposition** is the magazine's technique for World-adjacent and other **genuinely contested** material — now that world coverage lives in **Caught Up** and, when the week earns it, the **Long Read**. Instead of the Editor adjudicating a dispute (which would breach the Cardinal rule against inventing a thesis), the piece places **2–4 short, ATTRIBUTED, genuinely conflicting excerpts in sequence** and lets **the arrangement carry the meaning**. The reader draws the conclusion the ordering implies; the magazine never states it.

- **Attribution is mandatory and load-bearing.** Every excerpt names its source (outlet, analyst, named commentator) and traces to the research bundle as an `opinion` fact with a real `quote` (§ Key Rules → Borrowed angles; RT-22). An unattributed or invented "some argue…" excerpt is a fabrication fail — this technique **only** works with real, citable disagreement.
- **The excerpts must genuinely conflict.** Two takes that agree, or a strawman set up to be knocked down, defeat the purpose. Choose views that actually diverge (the hawk and the regional analyst; the launch-day rave and the considered pan) so the *gap between them* is the content.
- **The arrangement is the argument — so order deliberately.** Sequence for the reading you want the *juxtaposition* (not your narration) to produce: e.g. confident claim → the fact that complicates it → the quieter view that reframes both. Do not add a connective sentence telling the reader what to conclude ("what this really shows is…") — that is the hollow-connective-sentence trope and it collapses the technique back into invented thesis.
- **It is a prose technique, not a new component.** No new markup or CSS: render the excerpts with the existing Transmission vocabulary — a short run of attributed `<blockquote>`s, or a `.pullquote` with its `.attr` — inside the Long Read's `.lr-body` (or, tightly, as two attributed lines in a Caught Up item). If a future issue needs a visually distinct stacked-juxtaposition block, add a contract to `references/component-contracts.md` then — until then it is prose.
- **Where it belongs.** Caught Up (a single tight juxtaposition of two attributed lines on the week's most-contested story) and the Long Read (a fuller 3–4-excerpt sequence when the anchor is a genuine dispute). It replaces the retired impulse to write a World section that adjudicated — the magazine arranges the disagreement instead of resolving it.



---

## rotating

## Rotation Mechanics

Each issue includes the **fixed sections** (including **The Desk** with 1–2 service columns) plus **1-2 non-Desk rotating sections** selected based on cadence and editorial judgement.

### Cadence Table (v8.36 — The Desk service columns + non-Desk rotating)

**The Desk service columns (pick 1–2 per issue — see § The Desk):** chosen by which domain is most overdue *and* has real, actionable service news this week. The cadence below is guidance for "most overdue", not a hard clock.

| Desk column | Target Cadence | Research Window | Notes |
|---|---|---|---|
| The Session | Roughly every other issue | Since last appearance | Fitness (absorbs the old Workshop + Lab as angles). Closes on a "Do This Week" pin |
| The Ledger | Every 3-4 weeks | Since last appearance | Personal finance + consumer fintech + side-hustle/Etsy (was "Money"). Closes on a "Do This Week" pin |
| The Itinerary | Every 3-4 weeks (more near trips) | Since last appearance + forward 2-4 weeks for events | Travel + theme parks + NI local (was "Places"). Closes on a "Do This Week" pin |
| The Toolkit | Roughly every other issue | Since last appearance | Tech / Android / e-ink (yields strictly when thin). Closes on a "Do This Week" pin |

**Non-Desk rotating sections (pick 1–2 per issue):**

| Section | Target Cadence | Research Window | Notes |
|---|---|---|---|
| This Week in History | Every 2-3 weeks | Current week | History is date-bound |
| Listening | Every 3-4 weeks | Since last appearance | Podcasts + audio drama + music (absorbs the old Listen + Channel) |

**Trigger-driven (NOT on this table):** **The Saga** (lore deep-dive) has no cadence timer — it runs on a live peg, not a clock. See § Auto-Triggered Specials → "The Saga (trigger-driven)" and its brief in `references/sections.md`.

**Folded away in v8.27–v8.36 (do not schedule — they no longer exist as standalone sections):** The Workshop and The Lab fold into **The Session** (training science + gear are now angles within it); LEGO folds into **Pixel & Byte**; The Listen + The Channel → **Listening**; the old Long Game + Wallet + Ledger names → **The Ledger** (v8.36, the rebrand of "Money"); the old Itinerary + Local names → **The Itinerary** (v8.36, the rebrand of "Places"). The Session and The Toolkit are no longer standalone fixed sections — they are **Desk service columns** (v8.36; see § The Desk).

### Selection Rules

1. **Check the state file** (`signal-state.json`) for `rotating_sections` — each entry has `last_appeared` date.
2. **Pick the most overdue sections first.** If This Week in History last appeared 3 weeks ago and Listening 2 weeks ago, History has priority. For **Desk columns**, weigh overdue-ness *together with* whether the domain has real, actionable service news this week (§ The Desk).
3. **Cap at 1-2 non-Desk rotating sections per issue** (on top of the 1–2 Desk columns) to maintain pacing. Rotating sections should be substantive (300-600 words each). The issue's bulk comes from the fixed sections' considered pieces; rotating sections add variety on top, not bulk. Fewer slots is deliberate (v8.27) — it keeps the issue from padding.
4. **The Itinerary overrides normal cadence** when a trip is approaching — that Desk column appears every issue or every other issue in the lead-up. Check state file for `upcoming_trips`.
5. **Don't force it.** If research for a rotating section (or a Desk column) turns up nothing worthwhile, skip it even if it's overdue. The cadence is a guide, not a mandate.
6. **Each domain at least monthly (editorial checklist, not a gate).** Over any ~4-issue stretch aim for each rotating domain — This Week in History, Listening, and each Desk column (The Session, The Ledger, The Itinerary, The Toolkit) — to appear at least once; this is editorial judgement, not a planner-enforced floor. (Books are not on this checklist: they are the fixed **Bookmark** rail that runs every issue, not a rotating domain.) The old hard-cadence-floor and deficit-promotion validators are **retired (v8.36)** — domain cadence is now this checklist line, not a planner gate. The Threads owns continuity (§ The Threads), so a domain being quiet in the rotation no longer needs a forced-include gate to keep its story alive. The Saga is excluded from the checklist — it is trigger-driven, not on a cadence (see Cadence Table).
7. **Default research window when `last_appeared` is null.** When a rotating section appears for the first time after a state file reset (or first-ever appearance), its research window defaults to "past 4 weeks" — NOT open-ended. Prevents the first appearance of a section from surfacing months-old news (e.g. the Revolut-from-March bug). Override via explicit `initial_research_window_weeks` field in state if the editor wants different.

### Placement: Interleave, Don't Stack

**Rotating sections must be woven between fixed sections, not dumped at the end.** They should feel like natural parts of the issue, not an appendix. Each rotating section has a preferred placement slot:

| Rotating Section | Preferred Slot | Reasoning |
|---|---|---|
| The Week in Numbers | Movement I — after The Letter / before Caught Up | A quick personal read-out to open on |
| **Bookmark** *(fixed books rail — not rotating)* | Between Screen & Sound and The Desk | The lightweight books rail runs every issue; natural flow from entertainment to books |
| Listening | Between Screen & Sound and The Desk | Pairs with entertainment, breaks before the service desk |
| **The Desk** *(1–2 service columns)* | Between Screen & Sound / Bookmark and The Threads | The service department sits in the "act on it" cluster before the close |
| This Week in History | Between The Desk and On the Radar (original position) | Reflective close before the forward-looking calendar |
| The Threads | Between the rounds and On the Radar (part of the close) | Continuity recap flows naturally into the forward calendar |
| The Saga *(trigger-driven)* | Between Screen & Sound and Bookmark | Sits in the "story" cluster when a peg fires it |

**Within The Desk:** the 1–2 running columns sit together as the service department. The Ledger and The Itinerary read well mid-issue as a breather between dense sections; The Session and The Toolkit close the department. Each column ends on its "Do This Week" pin.

**When 2-3 rotating sections appear in the same issue:**
- Spread them across different slots — never place two rotating sections back-to-back.
- If two sections share a preferred slot, move one to its alternate position.
- The read-next connectors chain naturally through whatever sections are present.

> **Band order is fixed by the skeleton (v8.39).** In the Transmission build the movement/band order is deterministic (`weekly.json`), so the placement above is now realised by which skeleton slot a pick fills, not by hand-placing sections: the 1–2 non-Desk rotating picks occupy the **`rotating_1` / `rotating_2`** slots inside THE ROUNDS (between Bookmark and The Desk), the trigger-driven Saga fills a rotating slot when a peg fires, and the stitcher emits every band-head, divider and station-list entry. The planner's job is *selection* (which rotating domains run this week) — placement follows from the slot.

**Every band wears the one constant identity.** Rotating bands are not visually distinct costumes — they render in the same warm Transmission chrome as every other band (band-code eyebrow, waveform dividers, vermilion accent). There are **no per-section background/accent tokens** in the weekly (those `--[name]-bg` / `--[name]-accent` tokens are special-edition machinery, forbidden here). A rotating band's inner content uses the round vocabulary — typically the `.items` list — with at least a couple of distinct component types across the issue so no two consecutive bands read the same.


### Research Scoping

Only research topics for the rotating sections selected for this issue. This saves time and keeps research focused. Fixed sections always get researched. The search checklist below marks which groups are always-run vs conditional.

---



---

## anchor-piece

## Anchor-Piece Rotation (deprecated v8.15)

Removed. Replaced by the Lead + Companion structure (see § Article Structure). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

---



---

## search-checklist

## Search Checklist

Run the **core groups** every issue. Run **rotating groups** only when that section is selected for the issue.

### Core Groups (every issue)

**Group 1 — News & Geopolitics:** dominant running story, world news. **UK / national politics is out by default** (see the UK / national politics rule in § Key Rules) — scan for it only to catch the rare genuine landscape shift (an election *result* that changes the picture, a government actually falling) and to surface a one-line safety-net mention of any big Westminster story in **Caught Up** (the issue's 8-line news-breadth digest — no longer a per-section Catch-Up job). **No story is auto-promoted to the Lead.** A UK-politics development — even a leadership challenge or a cabinet resignation — is *not* automatically a Lead-1 candidate (the v8.x auto-promote mandate was the direct engine of the Starmer ×3 run). It is covered like anything else, and it leads only if it passes the two-factor Lead test (§ Article Structure: did it move this week AND can we add the layer the daily couldn't). The news-breadth floor (Lens-not-Filter) still holds: a genuinely big world story always gets *covered*, in the Lead if it clears the test, otherwise as a Catch-Up line.

**Group 2a — Gaming (for Pixel & Byte, every issue):** Nintendo Switch 2, Steam Deck / Steam Machine, GeForce Now, high-quality tablet games, plus generalist gaming (the biggest game of the year gets covered even if it's not on Switch) — what came out this week + highlights of the next month + *new* rumours-with-analysis. LEGO news and releases (LEGO now lives in Pixel & Byte as an occasional "play" beat).

**Group 2b — Tech & tools (for The Toolkit, when it runs):** consumer tech (Pixel/Xiaomi/e-readers, wearables hardware as consumer news), consumer AI tools, Android apps / tablet productivity / workflows. The Toolkit yields when thin; when it runs, cover the full gap since its last appearance.

**Group 3 — Football & Sport:** First, check: are World Cup qualifiers, Euro qualifiers, World Cup finals, Euros, CL/EL knockout stages, or other major tournaments active this week? If yes, search for those first — they lead the section. Then search domestic (Juventus + Serie A, Premier League) only for significant news. If no tournament is active, search Serie A + Juventus, Premier League, CL/EL (in season), golf majors/Ryder Cup (when in season).

**Group 4 — Culture & Entertainment:** new movies and TV releases, Star Wars news, synthwave/retrowave/electronic music

**Group 5 — Fitness (for The Session):** running articles (race prep, 10k training, zone 2), gym/strength training (concurrent training, body recomposition, structured programming), kettlebell/StrongFirst/Dan John, mobility and recovery science, wearable/Garmin training data interpretation, nutrition for cutting while training

**Group 6 — Features & Evergreen (rotate):** gaming retrospectives, Reddit notable threads (r/NintendoSwitch, r/Juve, r/fantasybooks, r/kettlebell, r/running, r/fitness, r/StarWars, r/lego, r/Garmin), great long-reads from any era

**Images:** source via image search for every major section.

### Rotating Groups

Search groups for rotating sections are in `references/sections.md`. Only search the groups for sections appearing in this issue.

---



---

## image-budget

## Component Quick Reference

**The weekly kit is per-band (v8.39 — the Transmission vocabulary).** The old sprawling `.split-60-40` / `.stat-bar` / `.dyk` / `.also-cards` / `.results-strip` palette is **retired for the weekly** — it belonged to the pre-Transmission chrome. Every band now has **one canonical inner component** (a few carry sub-parts), and a writer produces exactly that inner markup for their band. The stitcher owns everything around it. The reference for exact markup is `docs/mockups/reference-issue-transmission.html`; a working example of every band is in `references/golden/weekly/chapters/`.

**Per-band inner content — what the writer produces** (no `<section>`, no band-head, no divider):

| Band | Component | Inner markup the writer authors |
|---|---|---|
| **The Letter** | `.letter` | `<h2>` · `.kicker` · drop-cap `<p class="first">` · body `<p>`s · `.sig` ("— The Editor") · mono `.sigline` date stamp |
| **The Week in Numbers** | `.figures` | `.figures-frame` > `.fig-caption` + N × `.fig-row` (`.fig-label` = `.k` key + `.d` gloss, beside `.fig-val`; use `<small>` unit and `.win` for a highlight) + `.fig-foot` |
| **Caught Up** | `.digest` | `<ol class="digest">` of **≤8** `<li><p><b>Label.</b> …</p></li>` (**HARD cap 8**) |
| **The Long Read** | `.lr-title` + `.lr-body` | `.lr-title` (mono eyebrow · `<h2>` with `<em>` · `.stand` · mono `.byline`) then `.lr-body` (drop-cap `p.first`, paragraphs, `.pullquote` with `.attr`, `.plate-img` = `.plate-box` + `.plate-cap`, optional `.aside-note` = **The Case Against**) |
| **The Touchline** | `.lead` + `.scores` + `.items` | `.lead` (with a `.drop` opener) · `.scores` > `.score`(`.wide`) cards · `.items` > `li` (mono `.freq` + `<h3>` + `<p>`) |
| **Pixel & Byte** | `.items` | `.items` > `li` (`.freq` + `<h3>` + `<p>`) |
| **Screen & Sound** | `.with-rail` | `.with-rail` = `.items` + `<aside class="rail" data-role="release-radar">` (`.rail__label` + N × `.rail-item` with `.when` / `.what`). **Release Radar is this rail — never its own band.** |
| **Bookmark** | `.picks` | `<ul class="picks">` > `li` (`.spine` + `<h3>` + `.meta` + `<p>`) — a few book picks, a line each |
| **The Desk** | `.desk` | `.desk` > 1–2 × `.deskcol[data-desk-column]`, each `<h3>` + mono `.sub` + `<p>`s, **closing on a `.pin`** (`.pinlbl` + `.act` + `.why`). ONE department, 1–2 columns, NEVER 3+ |
| **The Threads** | `.threads` | `.threads` > `.thread` (mono `.ep` + `<h3>` + `.prev` + `<p>` with `<b>Next:</b>`) |
| **Down the Rabbit Hole** | `.rabbit` | `.rabbit` (mono `.lbl` + `.chain` of `.node` / `.arrow` + a `<p>`) |
| **On the Radar** | `.radar` | `<ul class="radar">` > `li` (mono `.date` + `.ev` with a `<b>` lead) |
| **Do This Week** | `.closepin` | `.closepin` (`.pinlbl` + `.act` + `.why`) — ends on a verb + a human line |
| **Colophon** | `.endnumbers` | `.endnumbers` > 4 × `.cell` (mono `.k` + `.v` with an `<em>` accent) |

**Structural hooks the writer must include:** `data-role="release-radar"` on the Screen & Sound rail, and `data-desk-column` on each Desk column. These are the only invisible hooks a writer adds; the stitcher supplies the rest (`data-movement`, `data-band`, `data-role="long-read"`, `data-station`).

**Shared inline atoms** (used inside the components above, not standalone bands): `.mono` (mono caps eyebrow/label), `.serif` (Instrument Serif display), and the `.wave` / `.tickrule` dividers — but the dividers are **chrome the stitcher places**, never authored inside band content.

**The special `.sp-*` vocabulary is FORBIDDEN in weeklies** (it is the special/holiday bound-magazine kit). So are the retired pre-Transmission weekly classes (`.split-60-40`, `.stat-bar`, `.dyk`, `.also-cards`, `.results-strip`, `.angle`, `.foreword`, `.caught-up`, `.do-this-week`, `.the-threads`, `.week-in-numbers`, `.sec-watermark`, `.nav-card`, `.reveal`, `.count-up`, …). A weekly that ships any of these fails the visual-consistency gate.

**Variety within the constant identity.** The identity is constant, but the reading should not feel monotonous: no 3+ screen-heights of unbroken prose (the Long Read breaks itself with a `.pullquote`, a `.plate-img`, and the `.aside-note`); the rounds alternate between the list vocabulary (`.items`) and the framed vocabularies (`.scores`, `.with-rail`, `.picks`, `.desk`); and the vermilion accent stays rare (§ Accent lockdown).

---


