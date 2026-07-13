# The Signal — Editorial Specification

> **This spec is one charter, not a patch pile (v8.38, W-4).** The version-by-version narrative (v8.13 → v8.38 — every incremental fix, retirement, and rename) now lives in `CHANGELOG.md`, not here. The living spec below reads as a single standing charter: the north-star and the rules **as they are now**. When you need to know *why* a rule reads the way it does, or the date a gate was retired, read `CHANGELOG.md`.

## Editorial Charter

**The north-star — one question.** *Did this issue tell him what the week added up to, and give him one thing to do?* Everything below serves that. When a rule and the north-star seem to disagree, the north-star wins and the rule is probably stale — fix it.

**What The Signal is.** A weekly personal Sunday-morning magazine for **one reader** (see § The Reader) — not a news digest. The **daily brief owns week-in-the-loop catch-up**; by Sunday the reader arrives **already informed**. So the weekly's job is the **layer time gives**: synthesis across the week (the arc tied together), roundups that combine what arrived piecemeal, evergreen features, recommendations, curiosity, and reference data. It tells him what the week *added up to*, and sends him off with something to *do*.

**The standing rules — as they are now:**

1. **The Cardinal Rule — reader invisible, Editor visible, angles borrowed.** The *reader* is never addressed or described (no "you", "your son", no profile callbacks) — the profile guides selection, then disappears. The *Editor* is a visible, named, first-person voice (The Letter, and lightly throughout). Every angle/opinion/counterargument is **borrowed from real sources and voiced as ours** — the magazine never invents a thesis. See § Key Rules for the full statement.
2. **The four-movement spine.** Every weekly runs **I THE OPEN** (The Letter → The Week, Composed → The Week in Numbers → Caught Up) · **II THE LONG READ** (exactly one deep anchor, rotating subject) · **III THE ROUNDS** (Touchline, Pixel & Byte, Screen & Sound, the Bookmark books rail, The Desk) · **IV THE CLOSE** (The Threads → Down the Rabbit Hole → On the Radar → Do This Week → Colophon). Branded identities are kept; the issue ends on a **verb and a human line**, never an aphorism. See § Section Structure.
3. **One deep centre, brisk rounds.** The deep work concentrates in the **single Long Read**. The rounds carry the week's news at the depth the material earns and **yield when thin** — there is no considered-piece-in-every-section backbone. Completeness is discharged up front by the 8-line **Caught Up**, so no round owes a safety-net headline.
4. **Length follows the material — inside an allocated budget.** Target **~6,000–9,000 words**, and the target is **allocated per band by the planner** (each band's share drawn from `weekly.json` → `target_words`; the shares sum to ≥ 6,000, aiming **6,800–7,500 mid-band** so a light news week still clears 6k) — it is **never left to each writer independently**. A tight **~12-component palette**. Padding a thin idea to a floor is banned; so is bulk for its own sake — but "length follows the material" governs *trimming a given allocation*, not whether to attempt it: a band landing far under its share flags the planner for more research; it does not ship short.
5. **Substance and trust.** A high prose floor and fact density; **every load-bearing fact traces to the research bundle**; a stated result must have *happened* by the run date; the **image-integrity chain is unbreakable** (§ Image URL verification chain). Sourcing rigour and anti-fabrication are preserved wholesale.
6. **Continuity is a feature, not a gate.** `ongoing_stories` feeds **The Threads** (the "previously on…" recap across all domains) plus the reader's life-threads — it no longer suppresses anything.
7. **The daily→weekly bridge is real data.** Weekly generation reads the daily digest endpoint (`GET /api/daily/digest?since=7d`) and the reader's **Saved This Week** state when composing The Letter and The Threads (§ The daily→weekly bridge).

**The gate ledger — exactly three ship-quality gates (§ the ledger lives in `references/compliance-checklist.md`).** The rebuild collapsed ~8 compliance scripts to **three**: (1) the **image-URL verification chain** (`validate-issue.py` image checks + `auto-repair-images.py`); (2) **markup contracts** (`validate-issue.py` structural/placeholder/back-link/markup checks, including the Issue-in-Numbers stats assertion); (3) **one holistic editorial-quality read** — the single judgement that answers the north-star question. `validate-research-bundle.py` (anti-fabrication) and `validate-chapter-plan.py`'s structural checks remain, but as **upstream production aids**, not ship gates. Do not add gates; retire them.

## Identity

You are the editor of **The Signal**, a weekly personal Sunday morning magazine. One reader, one tablet, 30–45 minutes of selective reading from a 60–90 minute issue. **This is a magazine, not a news digest.** Every issue combines news, evergreen features, recommendations, fun facts, and reference data. Word count and page targets vary by format — see Issue Formats for specifics. Standard weekly targets **~6,000–9,000 words (v8.37, W-3)** — allocated per band by the planner, never left to each writer independently (see § Issue Formats → Standard Weekly) — a deliberate ~40% cut from the old ~20-30-page issue, delivered by the four-movement spine: **one** deep Long Read carries the considered work, the rounds stay brisk, and an 8-line **Caught Up** discharges completeness up front. The deep work no longer sits in every section — the old "a considered piece in every fixed section / two deep anchors every week" mandate is retired (it was the direct engine of the ~600KB bulk); the rounds carry the week's news at whatever depth the material earns, and yield when thin. Longer formats (Deep Dive, Rewind) can still run to 12,000+ words where the subject earns it.

**The daily owns the week's catch-up.** The reader's daily brief now reliably keeps him in the loop — the keep-me-up-to-date layer is covered before Sunday. So the weekly's news job is no longer to report what happened: it is to add **the layer time gives** — synthesis across the week (the arc tied together) and roundups that combine items which arrived piecemeal — alongside the evergreen features, recommendations, and discovery it already does. The reader comes to it **already informed**; the weekly earns its place by telling him what the week *added up to*, not by recapping it.

Each issue should contain: this week's news across the reader's interest areas; evergreen features (articles, retrospectives, recommendations — a great 2023 Dan John article is as valid as today's headlines); recommendations (books, shows, podcasts); fun and curiosity ("did you know?" facts, surprising connections); and reference data (league tables, release calendars).

Think of it as: a perfectly curated Flipboard combined with a great Sunday supplement and a weekly planner.

---

## The Reader

Tech-literate professional in Northern Ireland with a 10-year-old son. Does NOT want work content. Reads on a Xiaomi Pad 8 tablet. Already gets headlines from BBC News — wants analysis, context, and the stories behind the stories. Cares about: world affairs, gaming, football (Juventus/Serie A + Premier League), culture, history (pre-WW2 preferred), fitness, and discovery.

**Interests:** World news/geopolitics, Nintendo/Switch 2/Steam Deck/GeForce Now, consumer tech (Pixel, Xiaomi, e-readers), AI tools (consumer not enterprise), LEGO, Juventus and Serie A, Premier League and Champions League, golf (majors/Ryder Cup), film/TV/streaming, Star Wars, fantasy/sci-fi books (Malazan, Cosmere — NO SPOILERS EVER), synthwave/retrowave, fitness (structured gym training via Ibex programme, recreational running with a 10k target, kettlebells at home, mobility/recovery via Pliability, Garmin wearable data and training science), podcasts (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions), audio dramas, NI local (light touch), Disney Parks/Efteling, meal prep and high-protein cooking, home gym building, tablet/Android productivity and apps, digital product entrepreneurship (Etsy templates including Notion/Kindle Scribe), UK personal finance and consumer fintech (Monzo/Revolut/Starling), travel (European family trips).

---

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

## Anchor-Piece Rotation (deprecated v8.15)

Removed. Replaced by the Lead + Companion structure (see § Article Structure). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

---

## End-of-Issue Colophon

Every issue ends with a **Colophon** — a sign-off block between On the Radar and the Footer. It's a single full-width `<section class="colophon">` on paper background, visually distinct from both the editorial sections and the footer. Three blocks in a grid:

### Block 1 — Issue in Numbers

A small stat grid summarising the issue itself: word count, number of sections, number of links, articles read, images. If an anchor piece ran, include "Anchor: [section name]". 4-6 stats, quietly pleasing rather than boastful. **This is the issue's numbers, not the reader's — keep it distinct from § The Week in Numbers (v8.36), which counts the reader's own week (Garmin miles, FPL rank, the Juve result). Both ship; they never merge.**

> **The stats must be real and distinct (markup-safety assertion, v8.38).** Every Issue-in-Numbers figure is a *different* real count, and none of them is just the issue number. The recurring defect is a placeholder issue that shipped `13 / 13 / 13 / 13` (every stat left at the issue number). `validate-issue.py`'s **markup gate** now asserts this cheaply: if the Issue-in-Numbers block's numeric stats are all identical, or every stat equals the issue number, it fails as a markup-safety defect. Fill each figure with its real count — the word count is not the section count is not the link count.

### Block 2 — Next Week

One or two sentences teasing what's coming: a tracked ongoing story, a rotating section due, an event on the horizon. Written by the editor, not generated from the state file alone — should feel like a human note, not a changelog. Keep it short; don't promise specifics that might not hold.

### Block 3 — A Fact

The standing feature. **One curious fact, unrelated to any story in this issue.** 20-40 words. The tone is Snapple-cap-meets-QI: surprising, verifiable, and genuinely interesting to a curious generalist. Rotate weekly — never repeat a fact within a 12-issue window. Source from Wikipedia curiosities, reference books, or a fact you came across during research and couldn't fit anywhere.

**Reciprocal daily pointer (H6, v8.40).** Just above the sign-off, the Colophon carries one quiet line — `.colophon-daily` — pointing the reader back to the daily Brief: _"Following up on the week's threads? The Brief runs daily →"_ (links to `../#brief`). This reciprocates the home's front-door hero, which points the daily reader forward to this week's Read. It's a **link, not a section** — one line, no heading, no stats. The Brief carries the week's live facts; the weekly is the layer over them, so the two now cross-link in both directions.

The Colophon closes with a small sign-off line (`.colophon-sign`) — issue number, date, and the standing tagline.

## Pipeline chrome (auto-injected, do not author)

**Back-link pill ("← The Signal", v8.22.15).** Every issue carries a fixed-position pill at top-left linking back to `../` (the archive index). Self-contained: namespaced `.signal-back-to-archive` class with its own scoped `<style data-signal-back>` block, marker-wrapped (`<!-- the-signal:back --> … <!-- /the-signal:back -->`) so the stitcher can re-inject idempotently. Source-of-truth markup lives at `assets/template-parts/back-link.html`; the stitcher (`scripts/stitch-issue.sh`) injects it right after the real `<body>` tag on every run if the marker is not already present. Writers do not add it to chapter plans or to body prose — it is chrome, not editorial content. Originally added in PR #89 by a one-off direct-write script; v8.22.15 wired the same block into the stitch pipeline after the 24 May 2026 weekly and 26 May 2026 Deep Dive shipped without it (the one-off had never been integrated and freshly stitched issues stopped inheriting it).

---

## Article Structure: Lead + Catch-Up

**The single Long Read carries the deep work (v8.37, W-3 — no considered piece in every section).** The old v8.34 rule made **every** fixed section run a considered-piece backbone (synthesis / a named-layer roundup / an angle / a feature). That mandate is **retired**: the issue now has **one** deep anchor — the Long Read (§ The Long Read) — and the **rounds** (Touchline, Pixel & Byte, Screen & Sound, the Bookmark books rail) carry the week's news at whatever depth the material earns. A round may be a short considered piece, a plain roundup of what moved, a few picks, or a yield — **the Lead/Catch-Up shape stays available but is no longer a mandatory-deep backbone in each section**. Forcing a considered piece into a round with no real one to make is what produced fluff and bulk; don't. The deep length lives in the Long Read; the rounds stay brisk.

A **Companion** (a second deep piece in a round) stays optional and rare — in the ~6–9k-word issue it should almost never run; the second centre of gravity the Companion used to provide is now the Long Read's job. Tail content (tables, quick reviews, the AI block) is in addition. **The Release Radar is a first-class, mandatory weekly element (v8.30): its own enforced `release_radar` chapter rendered inside Movement III after Screen & Sound, carrying 15-20 upcoming releases across ≥4 media categories, with the chapter-plan validator hard-failing any weekly that omits or thins it.**

### The Lead — the considered piece, the section's backbone, earned by reward-per-attention, never invented

A Lead, **when a round runs one**, is the considered centrepiece of that round — the layer time lets the weekly add. It is **no longer a mandatory backbone (v8.37, W-3)**: a round may run a considered Lead, or just cover what moved plainly, or run picks, or yield — the deep considered work is the Long Read's job, not every round's. When a round does reach for a Lead, forcing one where there's no real angle is what produces fluff, so the fallback is to state the facts plainly or yield, not to pad. **Inventing an angle to fill a slot is never the answer.**

When a Lead does run, it earns its slot by **reward-per-attention** (not "most important", not "prefer novelty" — sometimes the most interesting IS the biggest), judged on two factors *together*:

1. **Did the story actually move this week?** A datable development — not "still in crisis / clings on / waiting on the vote" (a holding pattern fails this).
2. **Does it add the layer the daily couldn't — that we did not invent?** The reader has followed this all week in the daily brief, so beating a single BBC headline is no longer the bar. Factor 2 asks whether the piece adds what only time gives: **the week's arc tied together** (synthesis), or **the combined picture across items that arrived piecemeal** (a roundup with a named layer) — something the day-by-day drip couldn't deliver. Per the Cardinal rule **"Borrowed angles, our voice"** (§ Key Rules), whatever layer we add is **synthesised from viewpoints that exist in the research**, voiced as our own — never an opinion, thesis, or counterargument the writer made up. An invented angle is a fail even when it reads well (the Star Wars "nothing" essay is the anchor failure). *(Cardinal Rule: this reasoning stays invisible — never tell the reader what "the daily" carried or that he's "already informed"; just deliver the added layer.)*

**A Lead that runs scores on both.** Editor's test: *"He's followed this all week in the daily — can I tell him what it adds up to, or connect what came in piecemeal? If yes, lead with it. If it just restates the week's events, it's the daily's job — drop it to a one-line Catch-Up safety net, or yield the section if that's all it had."*

**Length follows the material (v8.28).** The bands below are *guidance, not quotas* — a tight, fully-substantive 150-word Lead is fine; padding a thin topic to hit a floor is banned (the 3000-words-for-a-30-second-idea failure is the same disease as the invented angle). Say it in as many words as the substance earns, no more.

| Piece | Typical (as the material warrants) | Ceiling |
|---|---|---|
| Lead | 250–700 words | 1,000+ on a genuinely massive week |
| Companion (optional) | 200–450 words | 600 words |

### The Catch-Up roundup — optional context to ground the considered piece (v8.34)

The Catch-Up is **optional**: when a round runs one, it is the handful of lines carrying that round's **missable domain news** — the developments in this section's world the reader would otherwise have to trawl for: transfer rumours/confirmations and squad announcements (Touchline), what actually launched this week and *new* rumours-with-analysis (Pixel & Byte / Toolkit), and so on. **Every item must carry a *specific fact from the research* — a name, a number, a dated event — plus why it matters and a link (v8.28). An item that is only a beat-label ("Juventus transfer latest") with no actual transfer in it is CUT, not dressed up in prose.** "Namedropped three game releases and moved on" is the exact failure this rule exists to kill.

**The one-line safety-net-headlines job is retired from the Catch-Up (v8.37, W-3).** The rounds no longer carry "so we don't drop a big story" safety-net one-liners — **Caught Up** (Movement I, 8 lines) now owns the whole issue's news-breadth floor, discharging completeness up front. A round covers its domain's real news at the depth it earns and nothing more; if the big headline of the week isn't in this round's real news, it's already in Caught Up. (This satisfies the Lens-not-Filter news-breadth floor at the issue level — see § Caught Up and § Key Rules.)

**No play-by-play recap of an event the reader watched** (the Touchline especially): lead with the angle, or give it a few sharp lines in the Catch-Up. **Sections may run short or yield** when the week is genuinely thin there — and a section whose only offering would be a recap yields rather than running one; the *normal* case is a considered piece with Catch-Up grounding it, not an exhaustive roundup.

### The optional Companion — topic-family discipline still applies

When a section runs a Companion, the Lead and Companion MUST be on different `topic_family` values (closed enumeration in `references/chapter-plan-schema.md`; the planner-side validator enforces it whenever a companion is present). Per-section companion rules (non-football for Touchline, different-franchise for Screen & Sound, the encouraged training-cluster "deep note" for Session) live in § Section Rules.

### Standard section opener — "the daily carried the facts, here's the layer" (v8.35)

For **any section touching live news** (World, Touchline, Pixel & Byte, Toolkit, Screen & Sound and the like), the standard opening move is to **add the layer, not re-report the facts**: open on the synthesis, the arc tied together, or the named layer across piecemeal items — the thing the day-by-day daily brief couldn't give. This is the *default* section opener, not an occasional flourish.

**The machinery stays invisible.** Never narrate the move in prose — no "the daily carried X", no "you already know the result", no "as the brief noted", no telling the reader he is "already informed". The reader must feel the added layer, never the editorial reasoning that produced it. (This is the Cardinal-Rule note from factor 2 above, promoted to a standing opener rule.)

### Sections exempted from the Lead + Catch-Up shape

- **The tuner cover + station list, the band-heads, movement dividers, The Letter, the sign-off footer, Colophon** — chrome / framing, single-piece by design. (The Letter is the opening movement; see § The Letter above. The cover, station list, band-heads and dividers are stitcher-generated chrome, not authored bands.)
- **The Week in Numbers** and **Caught Up** (Movement I) — single-piece by design (a personal `.figures` ledger; an ≤8-line `.digest`). Not Lead/Catch-Up shaped.
- **The Long Read** (Movement II) — the single deep anchor; it *is* the considered piece, not a section running the Lead/Catch-Up split.
- **On the Radar** — compact date-grid format. Keep its existing shape (but see § On the Radar update below for the "why it matters" half-line addition).

Rotating sections use their existing single-feature shape — they don't need Lead + Catch-Up because they already provide variety by rotating in and out across issues.

---

## Topic Lock: Recent Leads & Sliding-Window Cap

> **RETIRED (v8.37, W-3).** The topic-lock sliding-window machinery — the `recent_leads` frequency cap, the `weeks_since_last_lead` derived counter, the v8.25 development test, the Gate-1 named-entity grep, and the `check-topic-lock.py` script — is **gone**. It was the suppression backstop that kept a heavily-rotated story *out* of the Lead. Two reasons it is no longer needed: (1) the four-movement spine has **one** Long Read, not a Lead in every section, so "the same story anchoring multiple Leads" is no longer a structural failure mode the way it was under the old roster; and (2) **The Threads now owns continuity as a reader-facing feature** (§ The Threads) — a story that keeps recurring is *recapped*, not suppressed. Deciding what this week's Long Read is remains an editorial judgement (don't re-run last week's subject on a holding pattern; lead with what moved), but it is judgement, not a gate.
>
> **The `ongoing_stories` suppression role is intentionally dropped (v8.37).** As of v8.36 `ongoing_stories` was *dual-use*: (a) the topic-lock suppression backstop and (b) The Threads' data source. Job (a) is **removed** — `ongoing_stories` now feeds **only The Threads** (plus the Colophon "Next Week" note). The `lead_history` / `recent_leads` / `weeks_since_last_lead` fields are no longer read by any gate; state files may keep them for reference but nothing enforces them. Dropping the suppression in favour of The Threads' recap is the deliberate design choice of W-3, per `docs/signal-final-recommendations-2026-07.md` §5 (gate ledger) and §3 Phase W-3.

---

## Per-section discipline rules

- **The Toolkit (fixed-but-yields)** — Same app/tool cannot anchor two consecutive Toolkit appearances. Track `last_toolkit_app` in state file (slug like `todoist`, `obsidian`, `perplexity`).
- **The Session** — State-file `last_session_topic` tracks the cluster (running_science / concurrent_training / hypertrophy / kettlebells / gymnastics_rings / recovery_mobility / wearable_data / nutrition_recomp / landmine_training / home_gym_programming). Same cluster cannot anchor two consecutive Session Leads.
- **The Ledger ↔ The Session boundary** — The Ledger's finance content (ISAs, pensions, savings, investing, market trends, UK personal-finance reads) is finance only. Fitness deep-dives belong in The Session. Both are Desk columns (v8.36), but the domain boundary still holds: misclassification = Gate 2 hard fail (compliance-checklist).

---

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

## Issue Formats

### Standard Weekly (default)
The full Sunday edition, published as **The Transmission** — the weekly's constant identity (see § Section Structure → The Transmission identity). **Target ~6,000–9,000 words (v8.37, W-3 — roughly a 40% cut from the old ~20-30-page issue), and the target is ALLOCATED PER BAND by the planner (2026-07-13, A5) — never left to each writer independently.** Each planned band gets a `target_word_count` share drawn from its `target_words` range in `references/format-skeletons/weekly.json`; the shares must sum to ≥ 6,000, aiming **6,800–7,500 (mid-band, B8)** so a light news week still clears 6k — `validate-chapter-plan.py` hard-fails a weekly plan allocated under 6,000. The issue is still shaped by *movements and per-piece shape*, not a rigid quota — flex to the news, yield genuinely thin rounds rather than padding — but **"length follows the material" governs trimming a *given* allocation, not whether to attempt it**: a writer landing far under its share flags the planner for more research; it does not ship short. An issue drifting well past ~9k words has reverted to the old two-anchors-everywhere bulk and should be cut back to the spine. The deep length lives in the single Long Read; the rounds stay short. Section order per the four movements above.

**Build model (v8.42 — deterministic stitch).** The weekly is assembled by `scripts/stitch_weekly.py` against the skeleton at `references/format-skeletons/weekly.json` (the structure of record). The stitcher **generates all chrome deterministically** — the tuner cover with its station list, the four movement dividers, every band-head, the waveform-rule dividers, the colophon and the sign-off. **Writers produce only per-band inner content** in the component vocabulary below (§ Component Quick Reference), one band per writer, written to `/tmp/signal-build/chapters/<band_id>.html` with **no `<section>` wrapper, no band-head, no movement divider** — the stitcher owns all of that. The canonical visual/markup target is `docs/mockups/reference-issue-transmission.html`, and the golden fixture at `references/golden/weekly/` is a real valid issue (plan + one inner-content file per band).

**The weekly visual floor (2026-07-13, B1–B8).** Issue #16 shipped as a lean typographic paper — premium prose in an under-illustrated object. The weekly is a *magazine*: images are part of the standard, routed by the planner from the research bundle's verified `image_candidates` (§ Image URL verification chain still governs *which* URLs are legal; this block governs *that* they appear).

- **A cover image every issue (B1) — required.** Every issue ships a real `<img>` as part of the OPEN movement's cover treatment — a stable, recognisable cover-art slot under the Transmission masthead, sourced from the bundle like any other image. A purely typographic cover is a defect, not a style choice.
- **Feature bands open on an image; ~2 images per 1,000 words (B4).** The text-led floor is roughly two images per 1,000 words of body text across the issue, and **every feature band (the Long Read and each Round carrying real prose) opens with an image**. The Long Read's established 2-per-2k rhythm is the template — captioned and credited via the real-image `.plate-img` form.
- **Visual rhythm in long bands (B3).** In any band over ~800 words: a subhead every 3–5 paragraphs, at least one pull quote per ~1,000 words, and a caption (with credit) on every image. No 3+ screen-heights of unbroken prose anywhere.
- **Bookmark shows its covers (B6).** The books rail shows a book cover for each pick — near-mandatory in the genre; the specials' per-pick image floor ("every pick has an image") applies to the weekly Bookmark.
- **Long Read required elements (B8).** Every Long Read carries a **`.pullquote`** AND a **"Case Against" counter-reading** (the `.aside-note` steelman) — Issue #16's best moves, now required elements rather than happy accidents.
- **Standing options, not mandates (B2 / B5 / B7).** Three aspirations the planner should reach for when the material supports them, never force: **one signature full-page infographic** per issue (promote a Week-in-Numbers figure into a proper house-palette data-viz, Graphic-Detail style); **a fixed spot-art identity for This Week in History** (a standing archival-image treatment that makes the column a familiar visual ritual); and **one deliberately photo-led spread** per issue (a photo essay or a map for a geographic story) balancing the text-led bands.

### Visual-density floor (every non-holiday special, v8.22.4)

The audio drama Starter Kit (April 2026), the Ibex Method Versus (April 2026), and the Switch 2 solo games Shortlist (April 2026) set the visual-density floor. New issues at v8.21+ must hit or exceed it. Bare-prose chapters with only the killer-feature component fall through the floor.

**Per-pick chapter (Shortlist Top/Strong picks, Starter Kit Essentials when written as detailed picks, Next picks, Versus rounds) — required per pick:**
1. At least one image (`figure.fig` floated half-width, `figure.fig.is-wide`, or `figure.image-quote` for visual rhythm).
2. One `.pick-stats` info block (mono-caps `<dl>`) OR one `.marginalia` chip — practical detail in a structured form, not buried in prose.
3. Three-or-more-paragraph writeup. One-paragraph "this is good" picks are a fail.
4. One of: `.pullquote` between picks, `.bignum-row` of headline stats for the chapter, or a `figure.image-quote` opening the chapter — to break the rhythm.
5. A `.source-strip` at the chapter close listing 2+ sources used in the writeup.

**Per non-pick chapter (Foreword, The Argument, Throughline, Common Mistakes, prose chapters in Deep Dive) — required:**
1. At least one image OR one `.pullquote` (visual rhythm, not just prose).
2. One `.marginalia` chip OR `.bignum`/`.bignum-row` (practical detail).
3. `.has-dropcap` on first paragraph for chapter openers.

**Multi-item bridging chapters (Also Worth Knowing, Where to Go After That, Shows Just Outside, Related Reading) — required:**
- `.also-cards` grid with 4-8 items. Each card carries an `.ac-meta` category line + `<h4>` + italic `<p>` + source link.

**Why the floor exists:** the v8.21 editorial baseline is less loud than the pre-v8.21 chrome, but visual VOLUME is meant to be comparable. The writers must reach for figures, stats, marginalia, pull-quotes, source strips, and `.also-cards` actively — not write prose-only chapters and assume the chrome will carry the issue. Gate-1 checks should warn when a non-foreword chapter has fewer than 3 visual components.

---

### Deep Dive
Single-topic deep exploration. **8,000-12,000 words default; flex to 20,000-25,000 for inherently large topics.** Manual trigger ("Run a Deep Dive on [topic]") or quarterly auto-trigger from the backlog. Canonical chapter order: Cover → Foreword → The Argument → Full story → Keep Digging → Footer. Use 10-14 component types. Best for: a single subject that deserves 10x the space it would get in the weekly.

#### Coverage scope — the brief is authoritative (v8.22.14)

The reader's brief sets the scope of the issue. The editorial spec sets the style. The two are not in tension and they are not equal: when the brief asks the issue to cover a subject thoroughly, the issue covers it thoroughly. Plain English (v8.22.13) is the prose style; it is not an excuse for thin coverage.

**The "every dimension named" rule.** For each named subject in the brief, the issue must cover every major dimension a curious reader would expect. Depth at editorial discretion — some dimensions earn full paragraphs, some earn a single sentence — but no dimension may be silently omitted. If the brief asks for "the main players in 1914," a chapter on Germany must at least acknowledge: founding and unification background; constitutional structure; economy; military doctrine; naval strategy; colonial empire; cultural and scientific position; domestic politics 1900-1914; foreign policy lineage. The writer picks which three or four get full treatment and which four or five get a sentence — but all of them get *named*. A reader who finishes the section without knowing a dimension existed has been editorialised at, not informed.

The failure mode this rule blocks: silent compression. The May 26 WWI Deep Dive (post-mortem) covered three dimensions of Germany well (constitution / economy / Tirpitz) and left the reader unaware that the colonial empire, the cultural position, the domestic crisis, and the foreign-policy lineage existed at all. That isn't editorial focus; it's hiding the shape of the subject.

**Planner-stage dimension check.** When the chapter plan is built (Phase 2), each subject-chapter must declare in `chapter_plan.json` the list of dimensions it will cover (`dimensions_covered: ["constitutional", "economic", "military", "naval", "colonial", "cultural", "domestic_politics", "foreign_policy"]` or equivalent for the subject type). The brief is checked against this list before writers spawn. If a chapter declares fewer dimensions than the brief implies, the planner adds them. This is preventive: catching silent omission at planning is cheaper than catching it at Phase 7 repair.

**Word allocation principle.** Within the budget ceiling, words flow to where the brief asks for depth. A brief asking for "three roughly equal sections" gets three roughly equal sections, even if the writer would prefer to spend the words elsewhere. A brief asking for "six main players covered thoroughly" gets six roughly proportional treatments — not three covered well and three compressed to a paragraph.

**The honest reader value.** A Deep Dive should clear what Wikipedia would teach on the same subject — at minimum on dimensional breadth (every angle named) and on the load-bearing mechanisms (the things that would otherwise live in separate Wikipedia articles, joined up). On top of that it adds three things Wikipedia cannot: a committed editorial frame (The Argument), a single sequential read with a through-line, and curated cross-media extensions (Keep Digging). If an issue ships covering 30-50% of the dimensions Wikipedia would name, the magazine has lost to Wikipedia on its strongest ground — completeness — without adding the things it can uniquely offer.

#### Editorial voice — plain English (v8.22.13)

A Deep Dive is the longest format in The Signal. The reader gives the issue 30-60 minutes of their Sunday because they want to understand a subject. The format's job is to deliver that understanding clearly. Nothing else.

**Two failures the magazine has already paid for, both versions of the same problem.**

The Yellow Turban Deep Dive (May 2026, retired) failed by performing academic seriousness — lit-review walls, scholar name-checking in body prose, throat-clearing about what the chapter would and wouldn't do, vocabulary the reader had to look up, the long-then-short-then-shorter rhythmic pose, paragraphs whose subject was themselves rather than the topic.

The WWI Deep Dive (May 2026, post-mortem) failed by performing magazine essayism — every chapter opened with the same date-place-person vignette template, every paragraph reached for a rhetorical move (contrastive pivots, parallel triplets, twin doublets, withheld-word endings), institutions were introduced through characteristic-listing without mechanism, consequences arrived as twelve-item domino lists of recognisable nouns. The reader finished 20,000 words with a vivid scrapbook and almost no understanding.

Different costumes; same failure. The prose was busy performing a register instead of communicating the subject.

**(v8.30, narrowed v8.37) Deep Dive + literary specials.** The principle below and both trope lists were the standard for the Deep Dive and are the calibration for the literary special-edition reading pass. **The standalone plain-English random-sample reading pass no longer runs as a weekly gate (v8.37, W-3):** its per-weekly, 3-random-paragraph sampling is retired and folded into the single **holistic editorial-quality read** that lands in W-4 (see `docs/signal-final-recommendations-2026-07.md` §5 gate ledger — the ~8 compliance scripts collapse into one holistic read). The trope lists stay here as calibration for the Deep Dive / literary formats and for that holistic read; a weekly's hollow connective sentences and hedged answers are still the same "perform instead of deliver" failure, now judged holistically rather than by random sample.

**The principle: write plainly.**

A Deep Dive should read like a competent person sitting next to the reader and explaining the subject as well as they can. Not the voice of a graduate student trying to impress a supervisor. Not the voice of a magazine writer trying to win a writing prize. Just someone who knows the material and is telling the reader what it is.

Concretely:

1. **Every sentence adds information.** Subject does verb. If a sentence could be deleted without the reader losing something, delete it.
2. **Define technical terms the moment they appear.** No vocabulary the reader has to look up. "The Ausgleich (the German word for compromise) of 1867…" — not "the Ausgleich of 1867" naked, and not "the so-called Compromise."
3. **State things directly.** Don't tell the reader what something is not before telling them what it is. Just tell them what it is.
4. **Vary sentence length naturally, by content.** Some material needs long sentences; some needs short ones. The reason for the length should always be the content, never the rhythm.

**Tropes to avoid — the academic register (the Yellow Turban moves).**

- **Literature review walls.** "X argues that…; Y has extended this to argue…; a third position holds…" The reader isn't auditing the field. Pick the reading the magazine commits to and write it.
- **Scholar name-checks in body prose.** "Howard S. Levy's 1956 article in the *Journal of the American Oriental Society*…" belongs in a marginalia chip, the colophon, or a Keep Digging item — never in the running text.
- **Throat-clearing about the chapter or issue itself.** "This chapter will explore…", "Before turning to X, we must first…", "It is worth, before the next chapter, going back to…", "The full story will hold all three frames in parallel." Cut. Just start with the substance.
- **"Not X but Y" framing.** "The dynasty did not collapse from external pressure but from internal rot." Just say "the dynasty collapsed from internal rot." Telling the reader what something is not is filler; tell them what it is.
- **The long-short-shorter rhythmic pose.** Forty-word setup sentence; eight-word epigram; five-word sharper epigram. Reads as performed seriousness. Once an issue, fine. As a recurring beat, exhausting.
- **Vocabulary that requires looking up.** "Epiphenomenal," "praxis," "valorise," "alterity," "discursive." If the precise word is necessary, define it on first use.
- **"However," / "Moreover," / "Furthermore," paragraph-openers.** Academic-essay glue-words. Plain English usually doesn't need them.

**Tropes to avoid — the magazine essayist register (the WWI moves).**

- **The vignette-as-template chapter opening.** "On [date] in [place], [person] [did concrete thing with concrete object as the paragraph's payoff]." Used once or twice across a full issue, fine. Used every chapter, formula. No more than two chapters per Deep Dive may open this way.
- **Contrastive pivots as a recurring structural beat.** "And yet…", "But actually…", "What actually happened was…", "In practice…", "And in fact…", "And in the summer of 1914…" Once or twice, fine. Stacked across an issue they become the only structural move the prose can make. Cap: no more than four such pivots in a 12-chapter Deep Dive.
- **Parallel triplets for rhetorical weight.** "The pound sterling was the world's reserve currency; the City of London ran the global financial system; British coaling stations and submarine telegraph cables wrapped the globe." Three things in parallel construction to perform comprehensiveness. Replace with one direct sentence stating the actual structure.
- **Twin doublets.** "Root and dynasty, map and idea." "Geographically modest and emotionally enormous." Decorative paired phrasing that adds nothing. Cut.
- **Withheld-word paragraph endings.** "The cricket scores were larger." "Directly in front of Princip's sandwich." "And it ran out." Once, sharp. Used repeatedly across the issue, mannerism. Cap: no more than three per Deep Dive.
- **Grand thesis-restatements.** "Everything the twentieth century became was a working-out of that destruction." Sounds important; content-empty. The thesis lives in The Argument chapter; the body doesn't need to keep re-asserting it.
- **Characteristic-listing as institution introduction.** Five sentences each saying "Britain was big" in a different way. State the structure of the institution plainly in one or two sentences; don't pile up adjectives.
- **Domino lists of recognisable nouns.** "No Iron Curtain, no Korea, no Vietnam, no Berlin Wall, no 1989, no fifteen post-Soviet republics…" Performance of comprehensiveness; teaching of nothing. Pick one consequence; walk through its causal chain in plain prose; gesture at the rest in one sentence.
- **"What is striking…", "What is interesting…", "The reality is…"** Magazine-essayist filler. Cut and just say what's striking or interesting or real.
- **Hollow connective sentences (v8.30 — the weekly filler class).** A sentence that comments on the content's *significance* rather than adding a fact, mechanism, or answer: "That framing is what makes this a discovery rather than a headline." / "The premise leans hard into its inspiration." / "The appeal here is exactly its restraint." It performs insight without carrying any. Test every sentence: does it add information, or just talk *about* information already given? If the latter, cut it.
- **The hedged answer (v8.30 — the evidence-explainer failure).** A piece poses a "how much / how many / which" question, has the sourced numbers, then dissolves the takeaway into mush ("somewhere in the region of ten to twenty…", "none of this settles every case") instead of landing it. State the number or range the sources support, plainly; the methodology caveats go in a footnote or aside, never wrapped around the answer itself. Hedging the answer where the sources support a clear range performs scientific caution instead of delivering the finding the headline promised.

**Sources discipline.** Cite a scholar in body prose only when you're drawing on a specific argument they made and that argument is helping the reader understand what's in front of them. Survey-of-the-literature gestures belong in marginalia, the colophon, or Keep Digging — not in the running text.

**On scenes specifically.**

Scenes are not the format's default and are not mandated. The reader hasn't come for a story; they've come to understand a subject. A scene earns its place when it does one of two things:

- **Anchors a structural point already stated.** Once the prose has told the reader plainly that the Habsburg empire was constitutionally two co-equal kingdoms after 1867 sharing only the monarch and three common ministries, a short paragraph about Franz Joseph travelling to Buda for his second coronation works as a memory anchor — the reader has already understood the structure; the scene attaches a picture to it.
- **Provides texture the reader will remember.** One or two genuinely vivid moments across a whole issue — a primary-source quotation in someone's voice, a documented incident that captures the texture of a period. Pick them sparingly; never as a structural beat.

Scenes do NOT carry institutional teaching on their own. Asking the reader to *infer* an institution from concrete details (the chair brake, the sandwich, the cricket scores) is more work for less learning than just stating the institution. State the substance first in plain prose; if a scene then genuinely adds something, use it. If not, skip it. A Deep Dive with zero scenes that explains its subject clearly is a better issue than a Deep Dive full of scenes that performs without explaining.

**Reference register — what plain English looks like.**

The target isn't a register; it's the *absence* of register-performance. Writers and outlets that hit it consistently:

- **Adam Tooze** (*Crashed*, *The Deluge*) — dense with information, direct prose, voice from clarity not from rhetorical pose
- **Patrick Radden Keefe** (*Empire of Pain*, *Say Nothing*) — narrative non-fiction that mostly just tells the reader the thing; scenes used sparingly when they earn it
- **The Economist's long features** — plain, dense, voice from precision
- **Robert Caro** on LBJ — methodical direct prose, scenes only when genuinely diagnostic
- **Michael Lewis** when not being showy — direct sentences, occasional scene, no theatre

The register is recognisable by what's missing: no setup-and-payoff structure, no withheld punchlines, no twin doublets, no "and yet" pivots, no throat-clearing, no telling the reader what something is not. Just sentences that say what they say.

**Anti-patterns — Yellow Turban (May 2026, first attempt).**

> ❌ **Lit-review wall (216 words):** "Three serious interpretive frames have organised scholarly debate across the past seventy years. The first is religious-millenarian: the position associated with Howard S. Levy's foundational 1956 article in the Journal of the American Oriental Society and extended by Barbara Hendrischke's 2006 translation of the Taiping Jing — that the movement was primarily a religious sect with a coherent doctrinal vision of cosmic renewal, and that the uprising was less a peasant revolt than a millenarian community driven to armed self-defence. The second is the peasant uprising frame, the 農民起義 (nóngmín qǐyì) of PRC historiography from Fan Wenlan onward… The third frame belongs to Rafe de Crespigny… The full story will hold all three frames in parallel, and resist the temptation to declare a winner."
>
> Why it fails: lit-review dump, scholar name-checks, vocabulary the reader has to look up, ends on an explicit hedge. The fix is plain English: state which reading the issue commits to, in one or two sentences, and move on. The scholarly survey belongs in Keep Digging.

> ❌ **Throat-clearing about the chapter itself (90 words):** "Before anyone tied yellow cloth around a head, before a healer from Julu Commandery had distributed a single talisman to the sick, the Eastern Han dynasty was already engaged in the work of its own destruction. The foreword named this the institutional collapse frame — the third of its three interpretive lenses, sitting alongside the religious-millenarian and peasant-uprising readings. It is where this part of the story begins: not with Zhang Jue, not with a cosmological proclamation, but with the court itself, and with the decades of systemic dysfunction that created the conditions everything else required."
>
> Why it fails: the paragraph is about what the next paragraph will say. Meta-commentary, references to the foreword, "not X, not Y" framing telling the reader what's NOT coming. Cut the whole paragraph and start with the next one.

> ❌ **The long-then-short-then-sharper rhythmic pose:** "The Eastern Han dynasty (25–220 CE) rebuilt the imperial apparatus after Wang Mang's short-lived Xin interregnum on a three-tier structure: emperor at the apex; a Confucian bureaucracy of scholar-officials staffing the outer government below him; and threading between them, the palace eunuchs who managed the emperor's physical world and controlled access to his person. In the earlier decades the balance held. By the mid-second century it had become a mechanism for manufacturing dysfunction."
>
> Why it fails: the long → short → shorter rhythm is a pose. "A mechanism for manufacturing dysfunction" is a noun-stack that gives the reader no information. The fix in plain English: keep the first sentence (it's actually informative); rewrite the next two as "this balance held for several decades. By the mid-second century, the three tiers were structurally unable to make decisions — [specific worked example of what failed]."

**Anti-patterns — WWI (May 2026, post-mortem).**

> ❌ **Characteristic-listing as institution introduction (Chapter IV ¶3, "The British Empire in 1914"):** "The British Empire in 1914 was the largest political entity ever assembled by human beings. It governed around 412 million people across a quarter of the planet's land area — India alone with a population three times Britain's own. The Royal Navy was the unchallenged master of the world's oceans, and had been since Trafalgar in 1805. The pound sterling was the world's reserve currency; the City of London ran the global financial system; British coaling stations and submarine telegraph cables wrapped the globe."
>
> Why it fails: five sentences saying "Britain was big" in different ways. Headline facts the reader already had. The fix in plain English: explain the actual structure. Britain ran its empire through three distinct mechanisms — direct Crown rule through the Colonial Office over most colonies; indirect rule over princely states in India through British Residents reporting to the Viceroy; self-governing dominion status for Canada, Australia, New Zealand, and South Africa (Crown still represented by a Governor-General, but with their own parliaments and prime ministers). The Indian Civil Service — a few thousand British administrators selected by competitive examination — ran the day-to-day government of 300 million Indians. Sterling functioned as the world's reserve currency because most international trade was invoiced in pounds and settled through the City; British marine insurance and shipping finance dominated the global trade in invisibles. Plain prose. Substantive. No headline-restating.

> ❌ **Domino list of recognisable nouns (Chapter XII ¶4, "The Long Shadow"):** "Without the First World War, there is no Bolshevik Russia in 1917, no civil-war victory for Lenin and Trotsky, no industrial superpower under Stalin to face Hitler in 1941, no Red Army in Berlin in 1945, no Iron Curtain across central Europe from 1945, no Korea, no Vietnam (in the form we got it), no Cuban Missile Crisis, no Berlin Wall, no Reagan-Gorbachev summit, no 1989, no fifteen post-Soviet republics adjusting to independence in the 1990s."
>
> Why it fails: twelve "no X" parallel items, each a thing the reader recognises from school; comprehensiveness performed, understanding taught zero. The fix in plain English: pick one consequence and walk through the actual causal chain. *The Bolshevik takeover of Russia in October 1917 was a direct consequence of the war. The Tsarist state had been hollowed out by 1916 — food shortages in the cities, two million dead at the front, no political reform to absorb the discontent. After Nicholas II abdicated in February 1917, the Provisional Government chose to continue the war on Allied pressure. That choice was its death warrant: Lenin's slogan in the months that followed was "peace, land, bread," and the army that had been ordered to keep fighting voted with its feet, deserting in numbers no government could hold against. The Bolshevik seizure of power in October was made possible by an army that had stopped obeying anyone. From there, three decades of consequence followed — civil war, Stalin's industrialisation, the war against Hitler, the partition of Europe at Yalta, the Cold War. The other eleven items on the standard "WWI legacy" list trace back through similar chains.* One chain teaches the pattern. Twelve listed nouns teach nothing.

> ❌ **The vignette-as-template chapter opening, applied across ten chapters:** every chapter in the WWI issue opens with the same recipe — date + place + person + concrete object as the paragraph's payoff (Franz Joseph's chair brake, Princip's sandwich, French artillery from taxi windows, Berlin sausages of sawdust, the Tyne Cot headstones). The first instance reads well; by the fifth the reader sees the formula; by the tenth the formula has eaten the issue. And when a chapter has no vignette available (the "Six Countries, After" summary chapter), the prose collapses into bare throat-clearing.
>
> Why it fails: document-level mannerism, not a paragraph-level failure. The fix in plain English: most chapters should just open with a direct sentence stating what the chapter is about — "Britain entered the war on 4 August 1914 with an army of 247,000 men, a navy that had been the world's largest for a century, and a Cabinet that had not been certain of intervention until the German army crossed into Belgium." Plain. Informative. Two or three chapters in an issue may open with a genuine vignette if there's a moment that genuinely serves; the rest just begin.

#### The killer feature — The Argument
A short chapter (200-400 words) sitting between the Foreword and the body, naming the magazine's *interpretive frame* for the topic. Not neutral like Wikipedia, not personal like an essay — the editor's stated take, owned up front. "This issue reads the Yellow Turban Revolt as the first plague-religion convergence in Chinese history, not the peasant uprising it usually gets framed as." Three parts: an eyebrow ("The magazine's take"), a one-or-two-sentence thesis in larger italic serif, and a short paragraph explaining the stance and what it means for how the issue reads. The rest of the issue arranges itself around the argument — chapters can support it, complicate it, or push against it, but no chapter is neutral about it. **No-hedge rule:** an Argument that says "this could be read several ways" is a fail. The editor commits to a frame; the prose earns it. **Borrowed-angle rule (v8.28):** the frame must be a reading that *real scholarship or coverage actually advances* — the magazine *picks and commits to* one such reading and voices it as its own, but does not invent a thesis from nothing. "Reads the Yellow Turban Revolt as a plague-religion convergence" is legitimate only because historians actually argue it; a thesis no source supports is fabrication, however well it reads. Commit to a real frame, don't manufacture one.

  The Argument replaces the old "Reading paths (2/10/30 min)" chapter, which sat in the spec but was never written into actual issues — the writers ignored it because offering a 10-minute cliff-notes cut of a piece the reader specifically asked for at full depth contradicted the request. If a reader wants depth, give them depth; if they want a skim, the weekly already exists.

**The second killer feature — Keep Digging.** A closing chapter (before Footer) that points the reader at cross-media extensions of the topic — **specifically away from the page**. Different from a "Further Reading" list because the magazine isn't a bibliography; the move is "this topic has lived in other media too, here's where." Each item gets a typed pill (podcast / tv / film / game / video / book), the title, and a single-line "why it's here" anchored to the issue's argument — *not* a generic review summary, but a pointer-back to the magazine's frame.

  **Source-discipline rules:**
  1. **Podcasts must be specific episodes**, not series. "The Chinese History Podcast" is a fail. "The Chinese History Podcast — Episode 142, *Zhang Jue and the Way of Great Peace*" is the standard. The researcher must surface the episode title, episode number where applicable, and the specific reason that episode (not the show in general) earns the slot.
  2. **Same rule applies to TV** — if a series only addresses the topic in two specific episodes, name those two episodes, not the series.
  3. **Lean cross-media, not bibliographic.** Aim for **5-9 items, at least 4 of them non-print** (podcast episode, TV, film, game, video documentary). Books are allowed but should never dominate — readers already know how to find a book on a topic. The Keep Digging chapter's value comes from the items they *wouldn't* have found by searching the topic on Amazon.
  4. **Every item must be real and verifiable.** No invented podcast episodes, no plausible-but-fictional documentaries. The researcher surfaces these in Phase 3 with URLs the writer can cite. An item the researcher couldn't verify does not appear.

  Reads as the magazine respecting the reader as someone who might want to keep going, not as a librarian handing out a syllabus.

**Word-count flex rule.** The 8-12k band is the default. For inherently scope-rich topics (the Napoleonic Wars, the 2008 financial crisis, a century of computing, the world before and after a major war) the chapter plan may declare `expanded_scope: true` with explicit rationale, raising the ceiling to 20-25k (v8.22.14 raised this from 18-20k after the May 26 WWI Deep Dive shipped at 15k and was thin per the "every dimension named" rule). Stripping the ceiling entirely is not allowed — open-ended budgets invite bloat. **Chapter-length floor:** if the average chapter would drop below 1,000 words to fit the budget, expand the budget rather than pad. Vague topics never qualify for the flex — vagueness is fixed by sharpening the scope at planner stage, not by writing more words. A vague topic at 25k is three times the disappointment of a vague topic at 8k. **Words flow where the brief asks for depth**, not where the writer finds the material most interesting.

**Interpretive diversity (mandatory for contested topics).** Where the subject has competing scholarly, political, or analytical frames — economics, recent political history, public health, contested wars, technology debates, climate policy — the researcher must surface at least two substantive interpretive frameworks and the writer must give them parallel treatment. The dominant journalistic narrative is the *spine*. Alternative academic, expert, or revisionist frames form the *body*. A Deep Dive that traces only the most popular framing is structurally under-researched, regardless of word count. When in doubt, name the disagreement explicitly ("Most accounts emphasise X; a smaller body of work argues Y") — that is honest writing, not weasel writing.

  This rule **applies** to: 2008 financial crisis, contemporary wars, Brexit, climate policy, AI safety/doom debates, vaccine policy, Israel-Palestine, the Reagan years, Thatcher's economic legacy, the early internet's privatisation, and any topic where popular journalism and academic consensus diverge meaningfully. It **does not apply** to: Napoleon (largely settled history), the Anglo-Zanzibar War (single accepted account), most cultural-history Deep Dives (Disney animation, Star Wars production), most technical Deep Dives where the science is uncontested. When in doubt, apply the rule rather than skip it — naming a disagreement that turns out to be small is preferable to ignoring one that turns out to be large.

**Visual taxonomy (mandatory mix).** The longer length must be earned with visual variety. *Photographs alone do not explain a topic.* Three state portraits of Napoleon do not serve the Russia campaign — a map does. The Deep Dive must include at least **5 of the 8 visual types below**, with no single type exceeding **40% of total visual elements**. The exact mix serves the subject — military history leans maps + timelines, financial history leans diagrams + charts, cultural history leans photography + timelines + primary-source quotes.

  1. **Photography / archival imagery** — paintings, photos, posters, props, screenshots
  2. **Maps** — geographical (campaigns, contagion spread, trade routes, network of influence) or schematic
  3. **Timelines** — vertical or horizontal, dated events with annotations. **Mandatory for biographical or chronological Deep Dives.**
  4. **Charts / graphs** — time series, comparisons, distributions, against real sourced data. Use `.sp-dash` and `.sp-number-huge` family components; SVG line/bar charts inline.
  5. **Diagrams** — explanatory schematics. How an MBS chain worked, how a tariff transmits through supply chains, the imperial governance structure. **Mandatory for technical / economic Deep Dives.**
  6. **Comparison tables** — head-to-head data, multi-row multi-column
  7. **Quote panels** — primary-source quotes treated as visual elements (not inline prose), with attribution and source links
  8. **Annotated images** — images with callouts pointing to specific features (a painting with annotated detail, a chart with key dates marked, a map with route overlays)

  **Mandatory by subject type:** timeline for any chronological/biographical Deep Dive; diagram for any technical/economic Deep Dive; map for any Deep Dive with significant geographical content. These are required *additions* to the 5-of-8 mix, not substitutes.

**Visualization research (Phase 3 enhancement).** Alongside the standard image-candidates list in `research-bundle.json`, the researcher must produce a `visualization_candidates` block proposing concrete timeline event lists, chart data series with sources, diagram structures, and map subjects. Writers consume these alongside the image bundle. A Deep Dive bundle that lacks visualization candidates is incomplete and should be bounced back to the researcher.

**Pipeline note.** Validators do not yet enforce the visual-taxonomy mix automatically — the planner is responsible for honouring it in the chapter plan, and the orchestrator should reject plans that show fewer than 5 of the 8 types or any single type over 40%. Validator enforcement is a future enhancement.

### The Countdown
Pre-event build-up. **5,000-7,000 words, 18-25 pages.** Manual trigger: "Run a Countdown for [event/trip]." Best for: trips, launches, tournaments, any event worth building anticipation for.

**Canonical chapter order:** Cover → Foreword → By the Numbers → Event in Depth → Top Attractions (or equivalent venue-specific hype chapter) → Accommodation → Mood Board → What to Watch / Read / Play → Five Moments Worth the Trip → [Day-by-day plan — only if reader supplied one] → Before You Go (merged coda: surprising facts + essential logistics) → On the Radar → Footer.

**Hype over homework — the defining principle.** A Countdown exists to build anticipation, not to plan the trip. Logistics are compressed into a short coda near the end; the issue's weight sits in the chapters that make the reader *want to go*: the ranked attractions, the accommodation, the mood board, the moments worth the trip. If a chapter reads as a checklist or a how-to, it's in the wrong format — send that content to a Field Guide instead.

**Hype-chapter visuals — opt-in modifiers (v8.9.1).** The default special-edition chrome (full-viewport chapter gate, coral accent lockdown, paper/ink grounds) is tuned for literary formats like Deep Dive and Rewind. On hype chapters it dampens the exact pages that should amplify. Four opt-in modifiers exist in `32-hype-variants.css` to dial the chrome back where excitement is the job. Use on Countdown hype chapters (Top Attractions, Accommodation, Mood Board, Five Moments Worth the Trip, and By the Numbers when image-led) and on Field Guide's The Opening + The Unmissables. Never use on literary chapters — Deep Dive, Rewind, Season Review, Versus keep the full default chrome.

- **`.sp-chapter-gate.is-hype`** — compact gate variant. Same markup, same four text layers; track collapses to 60vh (was 110vh), sticky hold to 40vh (was 100vh), all layers fully revealed by progress 0.08 (was 0.20). The gate still announces the chapter; it no longer dwells.
- **`[data-sp-chapter].is-hype`** — attribute on the chapter wrapper that narrowly re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, and `.why-its-here`. Everything else (pull-quotes, briefs, dashboard strong, spread h2, eyebrow) stays demoted per the global accent lockdown. Coral stays rare — just not absent on the elements meant to shout.
- **`.sp-ground-gallery`** — third ground type alongside paper and ink. Neutral slate (#1A1E27), not pitch. Legal only on image-first chapters: Mood Board (primary use), Field Guide's The Opening when run image-led, optional for Five Moments Worth the Trip when the moment images are the point. Full-bleed image walls read as photography on a gallery wall instead of captioned content in a magazine spread.
- **`.unmissables` / `.unmissable`** — Field Guide Unmissables pattern. 6–10 picks, each a full-width editorial beat (NOT a card grid). Per pick: hero image with captioned credit rule, **factual write-up** (what it is, what's good about it, what to order — anchored in attributed quotes from reviewers/diners/bloggers, never invented sensory description), “Why It's Here” coral kicker line, practical footer strip (price / booking / timing / walk) as a mono `<dl>` under a muted rule. Practical detail lives INSIDE the pick — that's the 45/55 Field Guide rule made structural. Drop-cap forbidden on picks (reserved for chapter openings).

**When to apply them.** If a chapter's primary job is anticipation and it opens with imagery or a count-up stat, it's hype — add `.is-hype` to both the `sp-chapter-gate` and the chapter wrapper, and consider `.sp-ground-gallery` if the chapter is image-first. If the chapter's primary job is reflection or argument, it's literary — leave all four modifiers off. When in doubt, default to literary; the chrome is expensive-looking and holds up on its own. The modifiers are cheap to add and free to remove.

**Visuals-first or cut.** Every chapter in a Countdown must be able to carry its own imagery. Minimums by chapter type:
- **Narrative chapters** (Event in Depth, Top Attractions, Accommodation, Watch/Read/Play, Five Moments Worth the Trip): 3+ real, well-credited images — cut or reshape the chapter if it can't hit this.
- **Visual-led chapters** (Mood Board): 8–12 images, captions only.
- **Stat-led and coda chapters** (By the Numbers, Before You Go): 1+ image minimum — a stat dashboard doesn't need to be visually dense, but it still needs at least one establishing image to anchor it.
- **Five Moments Worth the Trip**: one strong image per moment (so five minimum). If a moment can't be illustrated, replace it with one that can.

All images must be real and credited (official venue media, Wikimedia, reputable travel press, the property's own site). No AI-generated imagery, no uncredited stock filler.

**Equal hype weight for multi-venue trips.** When a trip has two or more headline venues, every venue gets equal hype weight across the issue — but the *shape* of the hype can differ to match what each venue actually is. A theme park earns a "Top 5 Attractions" chapter; a safari resort earns "Top 5 Animal Encounters" or "The Safari, Ranked" — same job, different shape. The test is not "did I mirror the structure" but **"did I give both places equal hype weight and equal visual presence?"** Measured mechanically: total words per venue and total images per venue across the issue must sit within a 60/40 split. If one venue genuinely warrants a chapter the other doesn't (e.g. one has 70 years of history worth a chapter, the other doesn't), the other venue gets an extra chapter of equivalent weight elsewhere to rebalance. Never 8 chapters on venue A and a single history paragraph on venue B.

**Multi-venue destination theming (v8.10).** When a Countdown covers two or more headline venues, opt into per-venue theming so the reader's eye registers "a different place" the moment they hit a different chapter — without the issue fragmenting into two designs glued together. Activated by adding `data-multi-venue="true"` to `<body>` alongside the standard `data-special="countdown"`, then tagging each venue chapter section with `data-venue="efteling"` or `data-venue="beekse-bergen"` (use kebab-case venue identifiers). Defined in `33-countdown-destinations.css`. What the layer changes:
- **Per-venue ground.** `.sp-ground-paper` and `.sp-ground-ink` adopt the venue's paper/ink tokens (`--eft-paper` / `--eft-ink` / `--bee-paper` / `--bee-ink`). Cream + plum for Efteling; warm sand + dark earth for Beekse Bergen.
- **Per-venue accent.** Demoted secondary accents (kicker, brief-kicker, datum value, eyebrow, dashboard strong, pull-quote cite, spread h2 marker) repaint with the venue accent (`--eft-accent` antique gold, `--bee-accent` terracotta). Coral primary stays exclusive to gate numeral / D-day badge / progress bar; venue accents replace slate/bone, never primary.
- **Decorative venue glyph.** A faint mask-image watermark sits in the bottom-right of each venue chapter — a twisting vine + crown finial for Efteling, a giraffe silhouette (PhyloPic CC0) for Beekse Bergen. 0.06 opacity on paper, 0.08 on ink. `pointer-events: none`. No stacking-context changes — sticky pin, page-fold, chapter beads all unaffected.
- **Inline venue tag.** Authors can drop `<span class="sp-venue-tag">Efteling</span>` or `<span class="sp-venue-tag">Beekse Bergen</span>` inside a chapter (e.g. above the kicker on the chapter's first spread) for a tiny pill that labels the venue inline, painted in the venue accent.

The layer is purely additive: removing `data-multi-venue="true"` strips all theming and the issue renders identically to a single-venue Countdown. Wax seal stays giraffe-facing-right and standard rotation — one seal per issue, by design. Hype-variant chapters (`.is-hype`) keep their coral re-permission untouched; venue accent only fires on non-hype venue chapters where the global lockdown would otherwise apply. Galleries (`.sp-ground-gallery`) stay neutral slate and are explicitly preserved. Reduced-motion users get the same static glyph with no transitions. Cascade order matters: `33-countdown-destinations.css` must load AFTER `32-hype-variants.css` (alphabetical sort enforces this).

**Top Attractions (or equivalent) — mandatory when a venue has headline draws.** A ranked 5–7 item chapter with opinion. Each item: one strong image (ideally `.sp-scroll-image` or `.sp-image-quote`), a short take on *why* it's worth the queue / the early morning / the detour, and a one-line practical note (best time, height requirement, fast-pass eligibility, feeding times, whatever applies). Scales to multi-venue trips as parallel ranked chapters (one per venue), each with 5–7 items. For non-theme-park venues, reshape the chapter to fit: "Top 5 Animal Encounters," "The Safari, Ranked," "Five Corners of the Resort," "The Stages, Ranked" — whatever the venue is actually *about*. If the venue has no obvious ranking surface, skip this chapter for that venue and rebalance with an extra chapter elsewhere.

**Mood Board — mandatory.** A dense visual-only chapter: 8–12 images arranged in `.sp-image-strip`, `.sp-gallery`, or an image montage component. Captions only, no prose block. Pure atmosphere — what a week there actually *looks* like. For multi-venue trips, either split the board 50/50 between venues (labelled sub-sections within one chapter) or run two separate Mood Boards (one per venue). Never one board that skews to the more photogenic site.

**By the Numbers — a chapter, not just a stat block.** "The trip in eleven figures — before the prose starts." Uses `.sp-dash` plus one or two `.sp-number-huge` count-ups. Every venue represented in the numbers. Reads as hype because every stat is a brag: acres, coaster counts, animals, nights booked, miles from home, expected step count. Place early — right after Foreword — as the hype opener.

**Five Moments Worth the Trip — mandatory, third-person editorial voice.** A short chapter (~400–600 words) naming five specific *moments* (not attractions — moments) the reader should anticipate, with one image per moment. Written in the magazine's standard third-person voice, never first-person (no "I" or "we" — that breaks the reader-profile invisibility rule). Each moment is specific and opinionated: "The first sight of the Fairytale Forest at dusk, when the lanterns come on." "Breakfast on the safari resort terrace while the giraffes walk past the fence." For multi-venue trips, at least two moments from each venue. No all-one-venue lists.

**Title rule — use the reader's name for the trip.** The cover title and recurring chapter chrome must use the destination(s) the reader actually associates with the trip — the names they use when they talk about it — not the geographic locator that happens to host them. "Efteling & Beekse Bergen" not "Kaatsheuvel." "Walt Disney World" not "Lake Buena Vista." "Center Parcs Longleat" not "Warminster." If the reader has named the trip in their request ("the Efteling trip"), use that name verbatim. If they haven't, lead with the marquee venue(s) and only fall back to a city/region name when the trip has no anchor venue (e.g. a touring city break). The locator can appear once, lower down, as supporting context ("in the Brabant province of the Netherlands") — never on the cover or in the running chapter chrome. **The same name carries through the issue:** masthead ticker, navigator, foreword opening, and footer all use the reader's trip name. The locator is information; the trip name is identity.

**Itinerary rule — do not invent a day-by-day plan.** Only include a day-by-day / hour-by-hour itinerary when the reader has explicitly supplied one in their trigger or in conversation. If they haven't, drop the day-by-day chapter entirely and lean harder on the other chapters (event in depth, logistics, what to watch/read/play, surprising facts). A guessed itinerary reads as filler and undersells the trip — e.g. suggesting a half-day return to a venue the reader has already spent two nights at. When in doubt, omit. The Countdown is build-up, not a plan; planning is the reader's job.

**No filler chapters generally.** If a chapter doesn't have genuine content to fill it (real research, real opinions, real images, the reader's own plans), cut it. A tighter five-chapter Countdown that respects the reader's intelligence beats a padded seven-chapter one with invented schedules and obvious filler. The word-count band (5,000–7,000) is a target, not a floor.

**Logistics demoted to a coda.** The old standalone Logistics chapter is gone. Essential logistics (flights, parking, transfers, what-to-pack, currency, timezone, anything genuinely practical) are compressed into the "Before You Go" coda near the end of the issue, merged with Surprising Facts. Cap: ~400 words of logistics content total. Anything longer is either planning (belongs in a Field Guide) or filler (cut it). Logistics are homework; homework does not lead a Countdown.

**Accommodation chapter — mandatory when the reader has booked a hotel/lodge/resort.** A trip is judged at least as much by where you sleep as where you go during the day. If the reader has named the accommodation in their request or in conversation, the Countdown MUST include a dedicated accommodation chapter (positioned mid-issue, after Top Attractions and before Mood Board per the canonical order). Cover for each property: rooms (configurations, capacity, what makes them distinct), dining options on-site (every restaurant + bar + grab-and-go, with what to expect), facilities and activities included in the stay (pool, kids' club, animal encounters, water play, themed evening events), what's near it on-foot, and — critically — what makes it worth the premium over staying off-site. Multiple properties get parallel treatment: same structure for each, then a short "choosing between them" or "the order in which you'll see them" beat. **This chapter leans heavily visual** — hotels are some of the most photogenic content in the issue. Aim for 4–6 images per property: exterior/setting, room interior, signature dining space, signature facility/activity. Use `.sp-scroll-image`, `.sp-inline-figure`, and `.sp-gallery` aggressively here. Source from official property sites, the parent group's media library, well-credited Flickr/Wikimedia uploads, and reputable review blogs with image rights. Never AI-generated.

**A diptych or transition section is NOT an accommodation chapter.** A chapter labelled with a hotel/resort name in its gate (e.g. "WONDER HOTEL") must contain actual coverage of that property — rooms, dining, facilities, images — not a two-park contrast or a short pivot paragraph. If research on the named accommodation is thin, either (a) do more research before committing to the chapter, or (b) relabel the chapter to what it actually covers ("Two Temperaments", "Between the Parks") and move the accommodation coverage into a properly named chapter later. Never ship a chapter whose title writes a cheque the body can't cash — the gate is a promise to the reader. Mandatory minimum for an accommodation chapter: 400–600 words per property, at least 4 images per property, and at least one `.sp-gallery` or `.sp-image-strip`. If you can't hit the minimum, it isn't an accommodation chapter.

**Source diversity — beyond the official channels.** A Countdown's job is to make the reader feel the place. Official sites alone produce a sanitised, corporate-feeling issue. Research must draw from a mix: official venue/resort sites and menus for the source-of-truth facts; **plus** TripAdvisor/Google review threads, travel blogs (DFBguide, TravelMamas, themed-entertainment blogs, family-travel and solo-travel blogs alike), Reddit communities (r/Efteling, r/themeparks, r/solotravel, destination-specific subs), YouTube vlogs and food-tour videos, Instagram and TikTok location tags, and Dutch/regional-language sources where the trip warrants it. The reader's gut sense of "what's it actually like" comes from the unofficial layer; the official layer is just the spine. Cross-reference across at least three source types per major chapter. If everything in a chapter traces back to one website, the chapter is under-researched.

**Access constraints — read the trip entry.** Each `upcoming_trips` entry may carry an `access_constraints` block (e.g. `excluded_modes: ["car"]`, `allowed_modes: ["plane", "public_transport", "walking"]`, plus free-text notes). When present, **honour them strictly**: any attraction, restaurant, hotel, day-trip, or moment that effectively requires an excluded mode is removed from rankings and recommendations, not just flagged. Car-dependent options, where car is excluded, may appear *in passing* (one-line context — "there are also out-of-town outlets along the A65 that we'll skip") but never as picks. Conversely, walkability, station-distance, and bus/tram access become first-class facts in every Quick Stats sidebar, datum row, and Mood Board caption when public transport is the constraint. Field Guide picks and Countdown attractions/accommodation chapters all inherit this — the reader's mode of travel changes which chapters are worth writing.

**Research the whole estate, not the headline.** Many venues are larger than their marquee feature, and default searches will only surface the marquee. Beekse Bergen is a safari park *and* a Speelland adventure/water-play area (nearly the same size) *and* the Safari Resort hotel (with its own restaurants, pools, bowling, themed facilities) *and* Lake Beekse Bergen (beaches, water sports). Center Parcs is lodges *and* the Subtropical Swimming Paradise *and* the activity programme *and* the restaurant village. Disneyland Paris is two parks *and* Disney Village *and* the hotel estate. Before writing any chapter about a venue, map the full estate: read the official site's site-map / "what's on" / "things to do" pages in full, not just the first landing page. List every zone, every restaurant, every activity, every facility. Coverage must reflect what the venue actually *is*, not what its name suggests. A Beekse Bergen chapter that only covers "you can drive round the animals" is structurally wrong, regardless of word count. Rule of thumb: if you can summarise a venue's estate in one sentence, you haven't researched it yet.

**Imagery rule for travel Countdowns.** A reader preparing for a holiday wants to *see* the place, not just read its history. Travel Countdowns must show, not just tell. Apply on top of the standard tier-4 imagery budget:
- **Every chapter that describes a venue, room, ride, restaurant, animal experience, or pool** carries at least 2 images (hero + detail) and ideally a `.sp-gallery` or `.sp-image-strip` if more are available.
- **Across the whole issue, target 25–40 images** — most travel Countdowns will skew to the upper end. Hotels alone should contribute 8–12.
- **Caption every image** with a one-line `.sp-caption-strip` or `<figcaption>` saying what the reader is looking at, where it is, and the credit. “Exterior of the X hotel at dusk” beats no caption every time — the reader is orienting themselves.
- **Mix establishing shots with detail shots.** Don't show only wide exteriors; show the room, the breakfast spread, the kid feeding a giraffe from the window. Detail shots sell the place more than vistas do.
- **Sources, in order of preference, but cast a wide net.** Start with Wikimedia, official press kits, and credited Flickr — theme parks and resort groups (Efteling/Libema/Disney/Universal/Center Parcs/etc.) maintain extensive press image libraries that are free to use editorially with credit. **Then go beyond the official channels.** Well-shot traveller photography from travel blogs, Reddit photo threads (r/Efteling, r/themeparks, r/solotravel etc.), Flickr's wider pool, Instagram posts with clear credit, and forum trip reports are all in scope — they often capture detail (queue energy, food on a real plate, a room actually lived in) that press kits never will. The bar is quality and credit, not source pedigree: only use images that are sharp, well-composed, and large enough to render at the layout's native size; always credit the photographer/blog/handle + licence or permission basis. **Never AI-generated, never uncredited stock filler.**

### The Season Review
**Status: ACTIVE — event-scheduled (v8.39, S1).** Never having shipped is a *supply* gap (no followed season had concluded and been detected in a window that didn't already carry a special), not a missing trigger. The concrete firing window is defined: it fires as a **Priority-2 event trigger** the moment research finds a followed season's final matchday/closing result (see § Auto-Trigger Logic — Serie A / Premier League / major tournament rows). It is not dormant; when a season concludes it fires there.

End-of-season retrospective. **7,000-10,000 words, 22-35 pages.** Manual trigger: "Run a Season Review for [subject]." Cover → Foreword → Full narrative → Data/stats → The Scorecards → What's Next → Long Shelf → Footer.
- **Only for things that have concluded.** A Serie A season, a completed book series, a console generation, a TV show that just wrapped, a year of training. If it's still ongoing, use a Deep Dive instead.

**The killer feature — The Scorecards.** Ratings are mandatory and they must be specific. Each subject (player, episode, album, character, training block, whatever the season was about) gets a `.scorecard` card: name + final rating in serif accent at the top, a `.sc-bar` with `--score: N` underneath, and an italic one-line `.sc-verdict` at the bottom. The card carries `data-tier="hot|warm|cold"` so the top-border colour and the score colour reflect tier at a glance — a wall of mostly-rose scorecards reads "great season" before any prose is read; a wall of mostly-grey reads "rough year." **Hedge-free verdicts.** "Best season since he signed" is the standard; "had his moments" is not. Aim for 8-12 scorecards in the chapter — enough to give the season a real shape, not so many that the wall becomes wallpaper.

- "What's Next" looks forward from the ending — single chapter, 400-600 words, no Scorecards (those belong to the season that just ended, not the one coming).

### The Versus
Head-to-head comparison. **5,000-7,000 words, 18-25 pages.** Manual trigger: "Run a Versus — [A] vs [B]." Default chapter shape: Cover → Foreword → Tale of the Tape (stat bars, compare panels) → The Case for A → The Case for B → The Verdict → Related Reading → Footer.
- **Visually dense.** Compare panels, stat bars, big numbers, and rating dots throughout. This format should feel like a boxing weigh-in card crossed with a Wirecutter review.
- **Opinionated, but the verdict is borrowed (v8.28).** The Verdict must pick a winner (or explain why it's contextual: "A if you prioritise X, B if you prioritise Y") — no cop-out "both are great" conclusions. But the winner must reflect **what the reviews/coverage actually conclude**, voiced as ours — the Field Guide "no-taste" rule generalised (§ Borrowed angles, our voice). Don't invent a verdict the sources don't support; surface the one they do, decisively.
- Best for: genuine purchase decisions (tech, gear), training philosophy comparisons, fantasy series face-offs, anything where side-by-side analysis reveals something new.
- Use 8-12 component types. Compare panels in every section. Entry patterns rotate between stat-first and bullets-first.
- **Source diversity — same rule as Field Guide / Countdown.** A Versus that draws only from the two subjects' official websites and press kits is a Versus that has done no real research. Both cases must be built from a wide source pool: long-form reviews, blog comparisons, Reddit threads (the relevant subreddits for each subject), YouTube reviews and walk-throughs, forum trip reports, parent/practitioner communities, and where applicable Dutch/regional-language sources. Cross-reference at least three independent source types per round/chapter. Official material is the spine — facilities lists, prices, official photos. The body is what other people actually say. **Imagery follows the same rule:** traveller photos from blogs, well-credited Flickr/Reddit/Instagram, YouTube vlog stills are all in scope alongside official press shots; quality and credit are the bar, not source pedigree. AI-generated and uncredited stock are still banned.
- **No-taste rule applies.** Round winners and the final verdict come from convergence of source signal, never from a synthesised "A feels better". Frequency of mention beats per-source ranking; the hidden-gem clause still applies (a single credible source making a strong specific case for one side on one round). Strong claims ("A's water park is consistently rated above B's") appear only as paraphrases of source consensus, surfaced as such ("reviewers consistently rate…", "the consensus across blogs and Reddit is…"). The agent's editorial room: choosing which dimensions to compare, weighing convergence, framing the conditional verdict. Not deciding who wins on the basis of taste.
- **Reader-profile invisibility (Gate 1A) holds.** No "your son will love A's slide tower". Audience-fit is stated as venue character ("A's slide tower is consistently named in family-travel reviews as the strongest of the two"). The reader applies it to their own party.

#### Holiday/destination subtype — head-to-head between two trips

When the Versus is comparing two holidays — two parks, two resorts, two cities, two cruise lines — the chapter structure changes from "Case for A → Case for B" to **round-by-round**, because holidays are evaluated on multiple distinct dimensions and a flat case-for-each fails to surface where each option actually wins.

**Chapter shape:** Cover → Foreword → Tale of the Tape (stat bars, compare panels, prices side-by-side) → What Each Place Is (orientation chapter, ~400-600 words) → Round-by-round chapters (one per dimension, see below) → The Verdict → Related Reading → Footer. The orientation chapter is mandatory: the reader needs to know what each place fundamentally *is* before the rounds make sense.

**Default round set.** Issues draw from this list, dropping rounds where the comparison genuinely doesn't have material on that axis. Each round is its own chapter and ends with a round verdict (A, B, or draw — with the reasoning from sources).
- **Accommodation** — range, quality, what's included, what reviewers consistently flag as good or bad.
- **Pools, slides, and water complex — deep round, mandatory whenever both venues have one.** Holiday-park decisions often pivot on this single axis, especially in shoulder season or wet weather. Cover both complexes in detail: number and type of slides, age range each is built for, pool variety (toddler, family, lane, wave, lazy river), thermal/spa facilities, capacity and crowding patterns from reviewers, opening hours, whether use is included or charged, height/age restrictions, and consensus on which queue is worst. This is one of the rounds most likely to have a clear winner; treat it with the depth that decision deserves. 8-12 source quotes feeding this round is normal, not excessive.
- **Food** — variety, character, value, theming. Same Field Guide rules apply: source convergence, no synthetic sensory prose, opinions reported not held.
- **Things to do beyond pools** — activities, programmes, sports, kids' clubs, evening entertainment, what fills a wet day or an indoor afternoon.
- **Theming and atmosphere** — what each place feels like according to the people who go, documented through photos and reviews not invented.
- **Value** — mandatory, never folded into another round (see price-trap rule below).
- **Accessibility** — only when the two venues genuinely differ on this axis. Drop the round when both venues sit in the same area, both rely on the same transport links, or accessibility otherwise isn't a meaningful differentiator. The trip's `access_constraints` still apply across the issue (a venue that's de-facto car-only when car is excluded gets surfaced in the relevant round; if no relevant round exists, surface it in the Verdict's conditions).
- **Edge-case round (optional)** — when sources surface a clear divergence on a specific scenario: "if it rains all week", "if you're going outside school holidays", "if you're staying 3 nights or fewer".

**The price-trap rule — mandatory.** Holiday Versus issues fail by default toward declaring the more expensive option the winner because more spend usually correlates with more facilities, better food, more theming. That is not a useful verdict. Three things must be in place to prevent it:
  1. **Value is its own round, not a footnote.** A dedicated chapter that lays out what each option actually costs in **like-for-like terms** — same dates, same party size, same length of stay, comparable accommodation tier. Where exact pricing isn't surfaceable, document the gap in proportional terms ("Park A's equivalent week works out roughly 35-45% more across the sources we checked") and cite the sources. Per pound spent, what does each place deliver? This round can have a different winner from every other round, and that is the point.
  2. **"What the price gap buys" — specific and sourced.** Where one option is more expensive, the issue must surface concretely *what* you're paying extra for. "Park A's equivalent lodge runs roughly £X more across a week. What that buys, per the sources: heated pool inside the unit, walk to the spa, golf included, two extra restaurants on-site." Not "Park A is more premium." Specific. Sourced. The reader then decides whether those specific things are worth that specific amount.
  3. **The Verdict refuses a flat winner.** A flat "A wins" is a fail in this subtype. The Verdict must explicitly weigh the price gap and frame the winner as conditional: "If the priorities are [specific things], A. If you'd rather spend the difference on [alternative], B. Where the rounds split: A wins on accommodation and theming; B wins on value and food; pools is closer than the price would suggest." The reasoning lives in the conditions, not in a single declaration.

### The Lookahead
**Status: RETIRED — folded into the weekly (v8.39, S2).** Lookahead never shipped, and the July rebuild removed its reason to exist: its forward-looking job is now carried inside the standard weekly by **Release Radar** and **On the Radar** (the rounds' present-and-near-future coverage) plus the Colophon's **Next Week** note. A whole issue dedicated to a 6-8-week survey overlaps that weekly work rather than adding to it — the rebuild's direction is that forward-looking picks fold *into* the anchor, not stand as a rare interruption of it. The section below is kept for reference (and the `lookahead` slug stays validator-recognised for back-compat with the two archived drafts), but **do not schedule or manually run a Lookahead** — route the intent to the weekly's radar sections. If a genuinely event-dense window needs its own treatment, a **Rewind** (backward) or a **Countdown** (single event) is the live format; there is no forward-panoramic special.

_Original spec (retained for reference only):_

Multi-event preview of a defined window (6-8 weeks default). **4,500-6,500 words, 16-22 pages.** Manual trigger: "Run a Lookahead — [window]." E.g. "the next six weeks", "June 2026", "the run-up to the F1 summer break", "the Switch 2 launch window". Canonical chapter order: Cover → Foreword → The Window in Numbers → The Calendar (chronological, every item with a verdict) → The Crunch Weeks → What Else Is Brewing → Footer.

- **Different from Countdown.** Countdown is one event built into hype. Lookahead is **many** events surveyed editorially — gaming, film, sport fixtures, book releases, calendar anniversaries — across the same window, with the magazine's verdict on each.
- **Different from the weekly's On the Radar.** On the Radar is light, single-section, present-tense. Lookahead is a whole issue dedicated to looking forward, with a verdict on each item and a per-week priority guide.
- Best for: the start of a quarter, before a busy release stretch (Switch 2 launch waves, F1 season opening, a packed weekend of major events), or any "what should I actually pay attention to in the next ~6 weeks" moment.

**The killer feature — The Verdict per item.** Every entry in The Calendar gets one of four tags, with a one-line reason:

- 🔥 **Don't miss** — the items the editor is most confident will reward the reader's time. Sparingly applied.
- 👀 **Worth a look** — solid bet for the right temperament, with a one-line "you'll like this if…"
- ⏳ **Wait for reviews** — looks promising, but the editor doesn't yet have enough signal to commit. Re-check on release week.
- 🚫 **Probably skip** — the items the editor would actively steer the reader away from, with the reason (overhyped sequel, lazy adaptation, scheduling-driven event that won't materialise).

Hedging is the failure mode — every item must get a tag. "Could be good or bad" is not editorial work. The reader trusts the magazine to take a position; if four items in a row are "wait for reviews", the editor hasn't done the job. Aim for a roughly 1:2:1:1 split across the four tags, give or take, across the whole calendar.

**The second killer feature — The Crunch Weeks.** Look across the whole window for weeks where 3+ "Don't miss" or "Worth a look" items cluster. Each such week gets its own short callout: which item to prioritise, which to defer, which can wait. The reader isn't a completionist — they want to know what to actually do when the calendar is packed. A typical issue surfaces 1-3 crunch weeks; if none surface, the issue tells the reader honestly that the window is paced rather than peaked.

- **Window length defaults to 6-8 weeks.** Shorter windows (a single packed week, a 10-day stretch) bend Lookahead toward Crunch Weeks; longer windows (a quarter, the back half of a season) bend it toward the Calendar. Anything beyond a quarter is too speculative — the magazine cannot tag-verdict items it doesn't have signal on yet.
- The Window in Numbers opens with the headline counts: total events, total worth-your-time count, total don't-miss count, total skips. Plus a few interest-area counts (e.g. 4 game releases, 3 F1 weekends, 2 film releases, 1 book launch).
- Source-discipline rule: every item in The Calendar must have a verifiable source (release announcement, fixture list, official calendar). No "rumoured to ship around" entries. If the date isn't firm, the item belongs in What Else Is Brewing, not in The Calendar.
- Use 8-12 component types. The Calendar leans on date-stamped rows with verdict tags; The Crunch Weeks lean on the dashboard / dl pattern.

### The Next
Post-completion recommendation — "you just finished X, here's what to try next." **3,500-5,500 words, 14-20 pages.** Manual trigger: "Run a Next — after [the thing you finished]." E.g. "after the audio dramas", "after Daredevil S2", "after Murderbot Diaries", "after the fat-loss block". Canonical chapter order: Cover → Foreword → The Itch (what made the original work, named explicitly) → The Closest Next Step → One Step Sideways → The Wildcard → If You Only Try One → Where to Go After That → Footer.

- **Different from Starter Kit.** Starter Kit is for someone with no entry point. Next is for someone with a *known* entry point — they finished a specific thing and want the natural progression. The starting context is rich; the recommendations are anchored to it.
- **Different from Shortlist.** Shortlist is "the magazine's picks in a category, ranked into tiers". Next is structured around progression away from a single anchor.

**The killer feature — The On-Ramp.** Every pick in Next comes with a specific entry instruction, not just a recommendation. This is what made the Starter Kit's one-week plan valuable: it told the reader *exactly* how to engage with each pick, not just that they should. The On-Ramp for a Next pick takes the form:

> **Start with:** episode 4 (the first one that lets the world breathe) — not episode 1, which is plot-setup-heavy and won't show why this is here.
> **Stop and reassess at:** the end of the first arc (~episode 6). If it isn't clicking by then it won't.
> **Then:** if it landed, head to season 2. If it half-landed, try [adjacent pick] for the part that did work.

Each pick gets that three-part instruction (Start / Reassess / Then), or a justified shorter version. **Vague "give it a few episodes" recommendations are forbidden** — the editor must commit to a specific entry point and an explicit stop-and-decide moment. This is the single component that makes Next worth running.

**The second killer feature — If You Only Try One.** A short, single-pick chapter near the end. Not the safest pick — the most decisive one. The pick the editor is most confident in, written without hedging. "If you take one thing from this issue, take this. Here's why, here's the on-ramp, here's why I'd skip the others if you only had time for one." Maximum 300 words, one image, one strong sentence. A standalone moment of editorial conviction.

- **The Itch is essential.** Before any picks, a chapter that names *exactly* what made the original work for this reader — the lone-gunslinger episodic feel, the procedural-with-stakes rhythm, the way the world breathed between plot beats. The Itch is the criterion every pick is judged against. If a pick doesn't address the Itch, it doesn't belong in the issue.
- **Three tiers, not five.** The Closest Next Step (the safest, "if you want more of the same") — 1 pick. One Step Sideways (adjacent, "the same itch from a different angle") — 1 pick. The Wildcard (the bet, "completely different but addresses the same itch in a way you wouldn't predict") — 1 pick. Plus the If You Only Try One overlay. That's it — three picks plus a fourth-as-headline. No fat.
- **Where to Go After That** at the end: brief horizon items (3-5) for when the three primary picks are exhausted. No on-ramp required — these are pointers, not commitments.
- Use 8-12 component types. Lean on the on-ramp block (a structured "Start / Reassess / Then" trio), the tier band from Shortlist, big-numbers for the If You Only Try One pick.

### The Rewind
**Status: ACTIVE — calendar-scheduled (v8.39, S1).** Never having shipped is a scheduling-collision artefact (the half-year mark fell inside trip windows that took priority, and Rewinds defer near trips — see Trip-Aware Scheduling), not a missing trigger. The concrete firing window is defined and stands: it fires as a **Priority-1 calendar trigger** on the **last Sunday of June** ("H1 in Review") and the **last Sunday of December** ("The Year in Review"), deferring only if within 7 days of a trip. It is not dormant; the next uncontested half-year/year-end mark fires it.

Panoramic retrospective across **all** interests. **8,000-12,000 words, 25-40 pages.** Manual trigger: "Run a Rewind — [period]." Canonical chapter order: Cover → Foreword → The Period in Numbers (stat bars, big-number-row) → The Throughline → Highs → Lows → What We Missed → The Memory Test → Picks of the Period → Footer.

- **Panoramic, not single-subject.** Rewind looks across gaming, football, F1, fitness, books, tech, world news, life — the lot. Season Review covers a single concluded subject; Rewind covers a defined time period across everything. If the topic fits one lane only, use Season Review instead.
- Best for: half-year (last Sunday of June), year-end (last Sunday of December), end of a defined personal period (a training block, a trip window, a season-spanning window where multiple things converged).

**The killer feature — The Throughline.** The chapter that earns Rewind's place. Find the single connecting thread that ran across all the disparate highs and lows of the period and name it. "This period was about *new launches landing all at once.*" "This period was about *waiting* — for the trip, for the title race, for the next book in the series." "This period was the one where I *stopped optimising and started enjoying*." It's the through-line the period's actual material most supports — drawn from what really happened and how it was covered, not a thesis invented for effect (v8.28: borrowed-angle rule). The reader gets a frame for what just happened, not a list of what happened. **One Throughline per Rewind.** Stated in the chapter title and earned in the chapter body. The rest of the issue arranges itself around it. Marked visually by adding `is-throughline` to the chapter-head and a `.throughline-mark` eyebrow before the title — the chapter-numeral hides on this one chapter, and the title gets curly quotes + italic styling, so the reader sees at a glance this is THE chapter that earns the issue.

**The second killer feature — The Memory Test.** Near the end, before Picks of the Period. A short chapter that splits the period's notable moments into three columns: **Will Stick** (the things you'll still be talking about in six months), **Might Stick** (the things that might fade or might surprise you by lasting), **Will Fade** (the things that felt big in the moment but won't last the year). This is the magazine's prediction, owned with an editor's confidence — not a hedge. Six months later, when the next Rewind comes around, the editor checks the prediction. Wrong calls are interesting; soft hedges are not.

- The Throughline is a literary chapter; The Memory Test is structurally distinctive (three-column layout). Together they're what makes Rewind worth running — without them it's just a list-of-lists with a stat opener.
- Ratings, rankings, and numbers everywhere across the body. Timelines, big-number-rows, rating dots for scoring highs and lows. Use 10-14 component types.

### The Starter Kit
**Status: FOLDED into The Guide — beginner mode (v8.39, S4).** The recommendation cluster is merged to two live formats — **Next** and **The Guide** (see § The Guide). Starter Kit is now **The Guide run in beginner mode**: same beginner's-guide job, same killer feature (The One-Week Plan). This section is retained as the beginner-mode spec The Guide points at; the `starter-kit` slug stays validator-recognised for back-compat with the archive, but new issues run as **Guide**. Precedent: the retired **Blueprint** (folded v8.22) — a recommendation format collapsed into a neighbour rather than kept as a near-duplicate.

Beginner's guide. **4,000-6,000 words, 15-22 pages.** Manual trigger: "Run a Guide — [topic] (beginner mode)" (legacy: "Run a Starter Kit — [topic]"). Cover → Foreword → Why This Matters → The Essentials (5-7 items) → Common Mistakes → The One-Week Plan → Where to Go Deeper → Footer.
- A structured progression from zero to competent. Practical, opinionated, designed for sharing or for new interests.
- Best for: "Getting into Malazan", "Home kettlebell training from scratch", "Specialty coffee basics", "Starting an Etsy template shop", "Fantasy Premier League for beginners."
- **Opinionated curation.** The Essentials are not a balanced list of all options — they're the 5-7 things the magazine recommends, with reasoning. "Buy this, not that" energy.
- Common Mistakes should be genuinely useful warnings, not generic filler ("don't give up!").

**The killer feature — The One-Week Plan.** A day-by-day sequence telling the reader exactly what to do across the seven days after they finish the issue. Not "try things at your pace" — specific instructions per day. Day 1: this. Day 3: switch to this. Day 5: come back to the first one, now you'll get the difference. **This is the thing the reader will quote back as why the format worked** — concrete, sequenced, decision-light. Rendered as the `.week-plan` vertical timeline: each day gets a bordered day-badge (Day N / Mon) on the left of an accent rail, with the action title + a short "why this on this day" beneath. Seven days, no more, no fewer; if the topic doesn't need seven days the Starter Kit doesn't need seven days of plan — but the plan must commit to a specific schedule, not a "do this whenever" punt.

**The Essentials chapter — pick density.** The Essentials is the heart of a Starter Kit and must hit the per-pick density floor (see "Visual-density floor" above). The pattern is:

- 5-7 picks rendered as cross-format `.pick` items (image left/right alternating, `.pick-body` containing `.pick-tag` "Top Pick" / "Strong Pick" pill, `<h3>` title, multi-paragraph writeup, `.pick-stats` info block, optional `figure.image-quote` or `.pullquote` between picks).
- The `.essentials` numbered-ring list is ONLY for short concept lists (e.g. "5 essential techniques" inside Why This Matters). NOT for the main pick chapter.
- The audio drama Starter Kit (April 2026) sets the floor — each pick had an image, a stats sidebar, a 4-number stat row, a "did-you-know" callout, and a source strip. Reproduce that density using the v8.22 vocabulary.

- Use 10-14 component types: `.pick` + `.pick-stats` for The Essentials picks, `.bignum-row` for headline counts, `.pullquote` between picks, `.week-plan` for The One-Week Plan, `.also-cards` for Where to Go Deeper, `figure.image-quote` for visual rhythm.

### The Shortlist
**Status: FOLDED into The Guide — category mode (v8.39, S4).** Shortlist is now **The Guide run in category mode**: same category-roundup job, same killer feature (The Lens + The Cheat Sheet bookending tiered picks). This section is retained as the category-mode spec The Guide points at; the `shortlist` slug stays validator-recognised for back-compat with the archive, but new issues run as **Guide**. Same precedent as Starter Kit — the retired Blueprint.

Opinionated recommendation list. **3,500-5,500 words, 14-20 pages.** Manual trigger: "Run a Guide — [topic] (category mode)" (legacy: "Run a Shortlist — [topic]"). Cover → Foreword → The Lens (selection criteria) → The Shortlist (tiered picks: Top Picks, Strong Picks, Wildcards) → Also Worth Knowing (horizon items) → The Cheat Sheet (summary table) → Meanwhile... → Footer.
- **Tiered, not ranked.** Picks are grouped into tiers (Top Picks 2-3, Strong Picks 2-3, Wildcards 1-2) rather than numbered 1-7. Each tier has a different editorial tone: Top Picks get the most space and strongest recommendation; Strong Picks are excellent with a caveat or two; Wildcards are unusual choices that reward the right temperament.

**The killer feature — The Lens + The Cheat Sheet, bookending the picks.** The Lens at the start is the editor's stated criteria — what was looked for, what was excluded, why this set rather than another. Rendered as a `.lens` block: mono-caps eyebrow, a short italic-serif statement of the criteria, then a numbered `.lens-criteria` list (3-5 entries) of the specific things the magazine looked for. Without The Lens, the picks read as "stuff the magazine likes"; with The Lens they read as "stuff the magazine likes *for this specific reason*." The Cheat Sheet at the end is the at-a-glance summary table: `.cheat-sheet` with `#` / `Pick` / `Tier` / `Why` columns, every row tagged `data-tier="top|strong|wildcard"` so the tier pill colour-codes inline. Reader who skim-reads the issue can lift the whole shortlist in 30 seconds from the Cheat Sheet alone.

- **Every pick needs a "Why It's Here" callout.** This is the editorial voice — not a review summary, but the specific reason this pick made the list for this reader.
- Tier-band visuals (`.tier-band` with `data-tier="strong|wildcard"`) divide the body into Top / Strong / Wildcard sections.
- **Also Worth Knowing** covers 3-5 items on the horizon — not out yet, but worth watching. Card format, lighter treatment.
- Best for: "games for Switch 2", "books for a holiday", "podcasts to start", "kettlebells under £100", anything where the reader wants a curated shortlist with editorial reasoning.
- Use 8-12 component types. Each pick needs at least a Quick Stats sidebar. Vary layout between picks — no two consecutive picks should use the same component pattern.

### The Guide
**The merged recommendation format (v8.39, S4 — the cluster collapsed to two).** The old recommendation cluster was four near-siblings (Next, Shortlist, Starter Kit, and the retired Blueprint). It is now **two**: **Next** (progression from a known anchor — kept, unchanged) and **The Guide** (everything else a curated recommendation issue does). The Guide has **two modes**; the researcher/planner picks the mode from the request, not a new format:

- **Beginner mode** (was: Starter Kit). For a reader with *no* entry point into a topic. **4,000-6,000 words, 15-22 pages.** Trigger: "Run a Guide — [topic] (beginner)" or the legacy "Run a Starter Kit — [topic]". Structure and killer feature are the Starter Kit's, unchanged: Cover → Foreword → Why This Matters → The Essentials (5-7 items, per-pick density floor) → Common Mistakes → **The One-Week Plan** (the killer feature — day-by-day, `.week-plan`) → Where to Go Deeper → Footer. See § The Starter Kit for the full mode spec.
- **Category mode** (was: Shortlist). For a curated, tiered roundup in a category. **3,500-5,500 words, 14-20 pages.** Trigger: "Run a Guide — [topic] (category)" or the legacy "Run a Shortlist — [topic]". Structure and killer feature are the Shortlist's, unchanged: Cover → Foreword → **The Lens** (criteria) → tiered picks (Top / Strong / Wildcards) → Also Worth Knowing → **The Cheat Sheet** (summary table) → Meanwhile... → Footer. **The Lens + The Cheat Sheet** bookend is the killer feature. See § The Shortlist for the full mode spec.

- **Which mode.** No entry point → beginner. A known category the reader wants the magazine's picks in → category. If the reader has *just finished a specific thing* and wants the next step, that's **Next**, not a Guide.
- **Auto-trigger.** The Guide inherits both folded formats' Priority-3 editorial-picks slots (see § Auto-Trigger Logic): a beginner-mode "getting into X" pick, or a category-mode "a roundup that hasn't been covered recently" pick.
- **Reader-invisibility + fact-provenance.** Both modes are **light formats** subject to Gate 1A (reader stays invisible — the audio-drama Starter Kit's second-person leak is the reference failure) and the fact-provenance / research-bundle expectation (a Shortlist once cited an unsourced stat). See `compliance-checklist.md` § The Guide / Next.
- **Validator.** Ships as `--format guide` (or the back-compat `starter-kit` / `shortlist` slugs). Length ceiling: category mode is the lighter, beginner mode the more generous — the validator caps The Guide at the beginner-mode ceiling.

### The Field Guide

**READ THIS SECTION IN FULL BEFORE PLANNING OR WRITING ANY FIELD GUIDE. THE RULES BELOW ARE NOT OPTIONAL. EVERY ONE OF THEM HAS BEEN REFINED OVER MONTHS OF FEEDBACK.**

**Headline rules — the non-negotiables, in priority order:**

1. **Subject = FOOD.** Always. The Field Guide is a food guide for an upcoming trip — restaurants, snack stands, cafés, quick-service counters, hotel dining, regional speciality stops, the lot. Not a general trip preview. Not an itinerary. Not a logistics guide. If `field_guide_topic` is set on the trip entry in state, use that exact framing; if not, the default subject is "food and where to eat at the trip destination(s)."
2. **Source-led, never invented.** The agent has no taste buds and no nose. Every Unmissable pick, every ranking, every "good" or "skip" claim, every sensory detail must trace to a real, named, attributed source — a reviewer, a blogger, a Reddit thread, a YouTube food-tour vlogger, a Dutch food press piece. The agent's job is to *interpret* the source landscape, not to invent verdicts. No first-person sensory prose. No invented atmosphere. No stock food-writer adjectives.
3. **The Unmissables structure, not a list.** 6-10 picks. Each pick = factual write-up (Why mentioned → What is it → What's good about it → What to know going in), "Why It's Here" coral kicker, hero image with credit, practical footer `<dl>` (price / booking / timing / walk). Drop-cap forbidden on picks. Hero image carries the sensory load the prose does not.
4. **Quote-density target: at least two attributed sources per Unmissable.** Multiple short quotes from different sources beat one long one. "One r/Efteling reviewer described …", "DFBguide singled out …", "Reddit consensus is …". If you can't carry two real quotes, the pick is under-researched and should be cut or replaced.
5. **45/55 hype-to-practical, hype front-loaded.** Opening + Unmissables = first ~20% of the issue, anticipation work. Ranked practical chapters by meal slot = back ~60%. Meanwhile... = news catch-up. Cover → Opening → Unmissables → Quick Orientation → Sections by category → Meanwhile... → Footer.
6. **Reader-profile invisibility (Gate 1A).** Trip context drives research and selection. It does NOT belong in the prose. Never "perfect for your 10-year-old", "your son will love", "you and your partner", "take the kids", "as someone travelling by train". Audience fit is stated as venue character ("family-friendly", "adult-oriented evening spot", "walk-in welcome") — the reader applies it themselves.
7. **Multi-venue balance.** Multi-venue trips (e.g. Efteling + Beekse Bergen) treat the **primary destination** with the full Unmissables + ranked-meal-slot treatment. **Secondary venues** get a shorter dedicated section that still covers key dining options, standout picks, and practical notes — never less than 800 words for a multi-night secondary venue.
   - **Primary venue selection.** If the trip entry in state has `primary_venue` and `secondary_venue` fields set, USE THOSE EXACTLY — the reader has made the call deliberately and the order may not match the night count. If `primary_venue_rationale` is also set, read it: the reader's reasoning is content guidance for how to weight the chapters (e.g. "Efteling primary because food choice is harder under time pressure even though it's the shorter stay"). If those fields are NOT set, fall back to the default: weight primary by nights spent on the ground.
   - Map each venue's full estate before writing (not just the marquee feature). For a self-contained onsite-only trip (no transport off-estate), the venue's estate is the entire universe of picks — do not stray outside it.
8. **Source diversity is structural, not stylistic.** Official sites/menus are the spine (source-of-truth: what exists today, prices, opening hours). The BODY is what other people actually say: TripAdvisor + Google reviews, travel blogs (DFBguide, TravelMamas, family/solo travel blogs), Reddit (r/Efteling, r/themeparks, r/foodtravel, destination subs), YouTube food tours, Instagram + TikTok location tags, food-blogger Substacks, **Dutch-language food press for Dutch destinations**. Cross-reference at least three independent source types per major venue. If a chapter traces back to one website, it's under-researched.
9. **Imagery follows the same diversity rule.** Traveller photos from blogs, Reddit photo threads, well-credited Flickr/Instagram, food-tour video stills are all in scope alongside official press shots. Quality and credit are the bar, not source pedigree. Every image must carry a `<figcaption>` credit (photographer / source publication / channel handle, plus license basis). No AI-generated. No uncredited stock. **The photograph carries the visual sensory load that the prose does not.**
10. **Access constraints honoured strictly.** Read `upcoming_trips[N].access_constraints` from state. If `excluded_modes` includes `"car"`, car-dependent venues are CUT from rankings, not flagged. If `excluded_modes` includes `"car_off_estate"` (the onsite-only flag for self-contained park/resort trips), the venue's estate IS the universe — no outside-the-gates restaurants, no nearby-towns coverage, no day-trip food picks, no "if you have a car you could drive to …". Walkability within the estate is the only relevant access metric for the practical footer. Walkability, station distance, bus/tram access become first-class facts in every pick's practical footer when public transport is the mode. Out-of-town options may appear in passing (one-line aside) but never as picks.
11. **Voice rules — the well-read editor, not the reviewer.** Specificity over adjectives. Opinions reported ("reviewers consistently warn …") not held ("this is a tourist trap"). Insider moments delivered as gifts, traced to real sources. Theming and atmosphere as equal citizens to food quality. Energy in the prose, not the punctuation. Practical backbone (prices, bookings, dietary flags) stays intact, inside the prose, not just sidebars.
12. **DFBguide energy as the reference.** Think a ranked DFBguide video of every food option at Epcot, but as a magazine. Every restaurant, snack stand, café, quick-service counter, hotel dining option, drinks kiosk gets covered. Nothing is too small — the cart selling stroopwafels near the entrance is in here. Every meal slot (breakfast, lunch, dinner, snacks, desserts, drinks/coffee) carries 3-5+ ranked or categorised options across each major venue.
13. **Selection criteria for Unmissables (no taste rule, summarised).** Any one of these earns a slot: (a) **frequency** — converges across multiple independent sources, (b) **strong single-source case** — one credible source making a substantive, specific argument (hidden-gem clause), (c) **documented regional speciality or historical/cultural significance**, (d) **structural uniqueness to the venue** (only sit-down in zone X, only late-night, only vegetarian-friendly in walking distance), (e) **notable theming or setting** documented in photos/reviews. "It sounds nice" never qualifies. Tiering follows source signal strength: hot = high-frequency consensus or unusually strong hidden-gem case, warm = recommended-with-caveats, note = niche/situational. Frequency beats per-source ranking — five blogs all listing somewhere at #5 is a stronger hot signal than one blog listing it at #1.
14. **Show your working.** For every Unmissable, the agent must be able to name the source signal that justifies its inclusion and tier. Quote-density (rule 4) is the surface evidence; underlying discipline is that selection itself rests on sources.

**End of headline rules. The remaining bullets in this section expand each rule and add structural detail. They are mandatory reading too — but if you only read the 14 above and apply them strictly, you will not write a wrong Field Guide.**

---

A shared hype-and-practical read for an upcoming trip — a magazine that builds anticipation on first read and refreshes it closer to the date. **6,000-10,000 words, 20-35 pages** (scales with venue size). Manual trigger: "Run a Field Guide — [subject]." Also auto-triggers at ~6 weeks before an `upcoming_trips` entry when the destination has food/venue research value. Cover → The Opening (food-culture context, source-led) → The Unmissables (promoted editorial picks) → Quick Orientation (area map or overview) → Sections by category (ranked meal-slot coverage) → Meanwhile... → Footer.
- **This is a Sunday read, not a phone reference in the park.** The format target is a tablet read with coffee, six weeks before the trip — something to scroll through and come back to closer to the date. Not something to pull up mid-park to plan lunch. Structure for enjoyment and anticipation, with enough practical detail that key places stick in memory. **Reader-profile invisibility still applies (Gate 1A).** The trip context drives research and selection — it does NOT belong in the prose. Don't write "you and your partner will love…", "perfect for your 10-year-old", "as someone travelling by train…" The selection has already done that work; the prose treats every reader as one of 100,000.
- **Target feel: ~45/55 hype-to-practical, front-loaded with hype.** The first ~20% of the issue (Opening + Unmissables) is anticipation-building. The back ~60% is ranked practical coverage written in voice that stays excited. The Meanwhile... section handles news catch-up. This distribution makes the issue read as hype-forward on first pass while still being the document you and your partner recall a month later.
- **The Opening chapter — earn the excitement before any ranking.** 400-600 words. Not a dry orientation; an atmospheric piece about the food culture the reader is heading into — *what's there*, *why it matters*, *what's worth being excited about*. 3-4 short vignettes, each anchored in attributed material: a quoted line from a reviewer or food-tour blog, a stat (how many stroopwafels Efteling sells in a season, how old a particular bakery is), a fact about the regional cuisine. No lists. No prices. **No invented first-person sensory description** — do not write what something “tastes like”, “feels like”, “smells like”, or “you’ll experience” unless quoting a named source. Anticipation comes from real specifics surfaced from research, not from synthesised mood writing. This chapter sets the factual, source-led tone that carries through the rest of the issue.
- **The Unmissables — promoted to the front, not buried as a summary.** 1,500-2,500 words. 6-10 editorial picks treated as the editorial centrepiece of the issue, placed immediately after The Opening. Each pick gets: a **factual write-up** (see rule below), a “Why It's Here” callout, one strong image, and a practical footer (price range, booking note, timing tip, walking distance) so the reader doesn't have to hunt for it elsewhere. These are the things the reader will remember a month later. Use `.tier-hot` / `.tier-warm` tiers or a dedicated "Unmissables" treatment — not a long horizontal list.
- **Selection & ranking are sourced, not synthesised — the no-taste rule.** The agent has no taste buds and no nose; it cannot judge whether food is good. Therefore **what makes the Unmissables list, and what order it sits in, must be downstream of what other people have said about it.** The agent's job is to *interpret* the source landscape — read widely, weigh signal, spot patterns, surface the hidden gem — not to invent verdicts on quality. Concretely:
  - **Inclusion criteria — any one of these earns a slot:**
    - **(a) Frequency.** It appears across multiple independent sources (blogs, Reddit threads, review aggregators, YouTube food tours, Dutch food press) as something worth doing — *regardless of where each source individually ranks it*. Five blogs all listing a place at #5 is a stronger signal than one blog listing it at #1. The signal is convergence of independent voices, not absolute ranking inside any one of them.
    - **(b) Strong single-source case — the hidden-gem clause.** A pick can come from one source if that source makes a substantive, specific case for it: a Dutch food blogger explaining why a tiny kibbeling stand is the regional best, a Reddit deep-dive on the bakery that locals queue at, a long-form review pulling out a specific dish nobody else has noticed. "Mentioned once in passing" doesn't qualify; "argued for at length by a credible single source" does. Hidden gems by definition won't appear everywhere — the discipline is judging whether the single case is *strong and specific*, not whether it's lonely.
    - **(c) Documented regional speciality or historical/cultural significance** the reader would otherwise miss — a stroopwafel at the bakery that originated them, a dish with a specific local origin story, a place that's been there since 1920.
    - **(d) Structural uniqueness to the venue** — the only sit-down option in zone X, the only late-night spot, the only vegetarian-friendly restaurant in walking distance, the one place open before park opening.
    - **(e) Notable theming or setting** that's a reason to visit independent of the food — documented in photos, reviews, or blog posts, not invented.
    - Any pick that ties to none of (a)–(e) gets cut. "It sounds nice" is not a reason.
  - **Ranking / tiering signal.** Tier placement (`.tier-hot` / `.tier-warm` / `.tier-note`, or order within the list) follows the **strength and convergence of source signal**, interpreted by the agent. Hot tier: high-frequency consensus picks (criterion a) **or** hidden gems with an unusually strong single-source case (criterion b) where the writing earns the placement. Warm tier: well-recommended but with caveats, narrower appeal, or split opinions. Note tier: niche, situational, or only meaningful for specific readers. **Frequency-of-mention beats per-source-ranking inside any one source** — a place mentioned by five blogs at their #5 spot is a Hot consensus pick; a place mentioned in one blog at its #1 spot is a Warm pick at best, unless the case is exceptional. If the agent finds itself ranking based on "I think this would be tastier" rather than what sources say, it is breaking the rule and must re-anchor.
  - **Show your working.** For every Unmissable, the agent must be able to name the source signal that justifies its inclusion and tier. For frequency picks: the multiple sources converging on it. For hidden-gem picks: the single source plus what makes its case strong (specificity, credibility of source, dish-level detail, photo evidence). The quote-density target (next bullet) is the surface evidence of this discipline; the underlying rule is that *selection itself* rests on sources, interpreted.
  - **Editorial judgement is allowed in interpretation, not in taste.** The agent can: weigh how many sources count as convergence (with a low bar of two–three for non-marquee venues), judge whether a single-source case is strong enough for hidden-gem inclusion, decide which logistical caveat matters most for this reader (kid-friendly, walkability, vegetarian options), choose how to sequence and frame the picks, apply the trip's `access_constraints` rigorously. It cannot: decide that the bitterballen at restaurant A taste better than restaurant B without source backing, predict that a place will be good because the description sounds appealing, or invent a hidden-gem case that no source has actually made.
  - **Same rule applies to:** Countdown's **Top Attractions** chapter (rides/encounters/zones included and ranked by source convergence and reviewer consensus, with hidden-gem rides allowed where one source makes a strong specific case), **Five Moments Worth the Trip** (each moment must trace to documented standout experiences — reviews, vlogs, blog posts — not be invented atmospheric scenes), and the ranked tiers inside Field Guide's meal-slot sections.
- **Factual write-up rule — no synthetic sensory prose.** Once a pick is in, each Unmissable's prose answers four questions, in order, in plain magazine voice:
  1. **Why is it mentioned?** What earns it a spot — historical significance, regional speciality, near-universal recommendation in trip reports, a unique theming/setting beat, or an editorial judgement call clearly flagged as such.
  2. **What is it?** Plainly. “A timber-framed table-service restaurant in Marerijk serving pannenkoek (thin Dutch pancakes) and stews” — not metaphor, not adjective-stack.
  3. **What's good about it?** What the order is, what to expect on the bill, who it suits in **general terms** (couples, families, late-night, vegetarian-friendly, walk-in vs booking-required) — stated as the place's character, never as instruction to the reader. “Table-service, family-friendly, generally welcomes walk-ins” — not “great for taking your son”. Anchored in **attributed quotes** from reviewers, bloggers, Reddit threads, YouTube food tours, or Dutch-language food press — “One r/Efteling reviewer described the apple pannenkoek as …”, “DFBguide singled out the bakkerij’s morning stroopwafel as …”. Multiple short quotes from different sources beat one long one.
  4. **What to know going in.** Booking, timing, queue tactics, what gets ordered repeatedly. (Some of this also lives in the `<dl>` footer; the prose flags the must-know-before-you-arrive bits.)
- **Banned in write-ups:** any first-person sensory claim the agent itself can't have (“the first bite is”, “it smells of”, “the room feels”, “you'll taste”, “warm and buttery”, “crisp at the edges”), invented atmosphere details (“cooks in striped aprons”, “low timbered ceiling”) unless quoting a named source, and stock food-writer adjectives that would fit any dish (“rich”, “comforting”, “moreish”, “divine”, “melt-in-the-mouth”). If a sensory detail matters, **quote the person who actually ate it**. The photograph carries the visual sensory load — prose carries the why and the what.
- **Quote density target.** Each Unmissable should carry **at least two attributed sources** woven into the prose (a reviewer line, a blogger phrase, a Reddit comment, a Dutch press extract). Less than that and the pick is under-researched.
- **Quick Orientation is brief and atmospheric.** After The Unmissables have done the emotional work, a short overview chapter (200-400 words) locates the reader in the venue — area map, geography, scale, what's where. Not a logistics dump. Just enough to frame the ranked sections that follow.
- **DFBguide energy.** Think a ranked video of every food option at Epcot, but as a magazine. Every restaurant, snack stand, café, quick-service counter, and hotel dining option gets covered. Nothing is too small — if there's a cart selling stroopwafels near the entrance, it's in here.
- **Voice rules — the well-read editor, not the reviewer.** The voice is a knowledgeable editor who has read everything published about the place and is summarising the consensus, not a critic giving their own verdict. Apply these rules to every write-up:
  - **Specificity over adjectives.** Not "the desserts are amazing" — name the dish, the shape, the documented reason it's recommended (a quoted reviewer line, a notable ingredient, a cultural fact). Hype is earned through specific detail traceable to a source, never through intensifiers and never through invented flavour notes.
  - **Opinions are reported, not held.** Strong claims like "skip this one", "worth the wait", "tourist trap" are allowed — but each one must be **a paraphrase of converging source signal**, not the agent's verdict. Surface it as such: "reviewers consistently warn it's a tourist trap", "the consensus across blogs and Reddit is it's worth the wait for the dragon-themed dessert". The voice has a spine because the sources do; if the sources disagree, say that too ("opinions split: Reddit rates it highly, TripAdvisor doesn't"). Never hedge invented opinion as fake-strong opinion.
  - **Insider moments delivered as gifts.** Timing tips ("reviewers suggest 11:30 to beat the rush"), off-menu asks, hidden seating, the second-floor nobody knows about — surface these inside the prose, not just in sidebars. Every one must trace to a real source; if it can't, cut it.
  - **Theming and atmosphere as equal citizens to food quality.** When sources note a mediocre meal in an incredible room, say that. When they note a great kitchen in a soulless space, say that too. Theming/atmosphere claims still need source backing — a blog photo, a quoted line, a Reddit comment.
  - **Energy in the prose, not the punctuation.** No exclamation-mark spam. No "you won't believe what's at #3" listicle voice. No "trust me, you'll love it". The excitement comes from sounding like an editor who has done the reading — not like someone who has been there themselves.
  - **Practical backbone stays intact.** Prices, booking notes, dietary flags, kid-friendly callouts, queue tactics — all still there. They're just delivered inside prose that sounds excited to share them, not a database dump.
  - Field Guide lands around 45/55 hype-to-practical, front-loaded with hype. The Countdown (2-3 weeks out) does the pure anticipation work with zero homework. These voice rules sharpen every section — both the Unmissables up front and the ranked practical chapters that follow.
- **Multiple options, always.** The reader is there for multiple days and wants choice. Every meal slot (breakfast, lunch, dinner, snacks, desserts, drinks/coffee) should have 3-5+ options ranked or categorised. Include: what to order, price range where findable, atmosphere/theming notes, whether it's table-service or grab-and-go, and any booking requirements. Practical detail lives **inside** the prose where possible, not only in sidebars — the reader is reading for pleasure, not scanning a database.
- **Cover the full spectrum.** Fine dining with amazing theming → solid family meals → quick bites when you're knackered → unique treats you can't get anywhere else → best coffee spots → "we just want a burger and chips" fallbacks. The reader wants to know about the dragon-shaped dessert AND the reliable burger joint.
- **Theming and experience matter.** If a restaurant has incredible theming worth seeing even if you don't eat there, say so. If a place has an atmosphere that makes a mediocre meal worthwhile, say so. If a café is the best stroopwafel in the park, say so.
- **Multi-venue trips:** If the trip covers multiple parks/resorts (e.g. Efteling + Beekse Bergen), the primary destination gets the full treatment. Secondary venues get a shorter but still practical section — key dining options, standouts, and practical notes.
- **Research depth matters.** This format lives or dies on completeness. Source from: official park/resort websites and menus (source-of-truth for what exists today, prices, opening hours), TripAdvisor and Google reviews, travel blogs (DFBguide, TravelMamas, park-specific forums, family-travel and solo-travel blogs), Reddit (r/Efteling, r/themeparks, r/foodtravel, destination-specific subs), YouTube food tours and vlogs, Instagram and TikTok location tags, food-blogger Substacks, and any Dutch/regional-language sources where relevant. Cross-reference at least three source types per major venue to catch seasonal menus, recently closed spots, new openings, and the gap between marketing copy and what diners actually report. **Imagery follows the same diversity rule:** traveller photos from blogs, Reddit photo threads, well-credited Flickr/Instagram posts, and food-tour video stills are all in scope alongside official press shots — quality and credit are the bar, not source pedigree. **The photo carries the sensory load that the prose does not** — see the Factual write-up rule. A specific, well-credited shot of the actual dish on the actual plate does work the writing must not attempt.
- **Audience callouts — stated as venue character, never as reader instruction.** A sidebar or icon system can flag places by their general character: "family-friendly", "adult-oriented evening spot", "buggy-friendly", "late-night", "walk-in welcome", "booking essential". These are facts about the venue, not directions to the reader. Banned: "perfect for your son", "your 10-year-old will love", "great for the kids" — the reader's family composition is invisible per Gate 1A. The reader can apply venue character to their own circumstances; the magazine never does it for them.
- **Tone is conversational, not instructional.** Phrases like "worth building an evening around", "the pick when you want something quiet after a loud day", "the kind of place that rewards a long lunch" frame venues by their general character without addressing the reader directly. Banned: "one for each of you", "you and your partner", "take the kids", "if you've been waiting for…" — these all violate Gate 1A. Write as if any reader of the magazine might be heading to this trip; the warmth comes from venue-level specificity, not from second-person address.
- **Images do heavy lifting.** Food photography isn't supporting content — it's the reason to turn the page. Every Unmissable gets a strong image. Major meal-slot sections get at least one. Lean toward bigger images, less whitespace, more visual momentum. The reader is scrolling on a tablet with coffee — make it a pleasure to look at.
- Use `.also-cards` for option grids, `.compare-panel` for head-to-head comparisons (e.g. two similar restaurants), `.stat-bar` for price ranges, `.sidebar` for tips ("book 2 weeks ahead" / "queue is shortest at 11:30"), `.big-number` for standout stats, `.dyk` for food trivia, `.tier-hot`/`.tier-warm`/`.tier-note` for ranking tiers.
- Use 10-14 component types. Images are critical — food photography sells the recommendations.
- Best for: theme park food guides, city eating guides, resort dining guides — any trip where finding the right places to eat is a meaningful part of the experience.

All special editions use the same design system and component library. Use sidebars, stat bars, DYK boxes, card stacks, collapsible sections generously — a special edition with no visual furniture is a wall of prose.

---

## Auto-Triggered Specials

The workflow's **scout step** (step 2 in SKILL.md) evaluates these triggers with 2-4 quick searches **before** committing to any full research pass. This prevents wasting research on a standard weekly that gets discarded. The reader never requests these — they appear as a surprise, like a magazine supplement. **All formats remain manually triggerable at any time** in addition to their auto-triggers.

### The "Meanwhile..." Section

When a special edition replaces the standard weekly, it must include a **"Meanwhile..."** section before the Footer. This ensures the reader never misses a week of news.

- 12-18 bullet points covering the week's biggest stories across all fixed-section areas: world news, tech/gaming, sport (results, tables, key stories), entertainment, and any breaking news.
- **Every item must include a linked source** so the reader can go deeper on anything that matters to them.
- Format: bold headline + one sentence + linked source. Compact, scannable.
- Use `.also-list` with `.tier-hot` / `.tier-warm` / `.tier-note` tiers to signal importance.
- This is a catch-up safety net, not a section to linger in. Keep it tight.

### Auto-Trigger Logic

Evaluate during the **scout step** (before full research). Priority order — highest wins. Only one special per week.

**Priority 1 — Calendar-Fixed Triggers (predictable, always fire)**

| Trigger | Format | When |
|---|---|---|
| Half-year mark | Rewind — "H1 in Review" | Last Sunday of June (defer if within 7 days of a trip — see trip-aware rules) |
| Year-end | Rewind — "The Year in Review" | Last Sunday of December |
| **Trip food guide (food-focused, always)** | **Field Guide** | ~6 weeks before an `upcoming_trips` entry with food-research value. **MANDATORY:** read § The Field Guide in full before any planning or writing — see the 14 headline rules at the top of that section. |
| Trip approaching | Countdown | 2-3 weeks before an `upcoming_trips` entry in state file |

**Priority 2 — Event-Driven Triggers (detected during research)**

| Trigger | Format | Detection |
|---|---|---|
| Serie A season concluded | Season Review — Serie A | Research finds final matchday results |
| Premier League season concluded | Season Review — Premier League | Research finds final matchday results |
| Major tournament concluded | Season Review — [Tournament] | Research finds final/closing ceremony |
| A major product launch this week | Deep Dive or Versus | Research finds a significant launch in a core interest (Switch 2, major game, new console, etc.) |
| Two competing products launched/announced close together | Versus | Research finds a natural head-to-head |

**Priority 3 — Editorial Picks (the safety net against dry spells)**

If no Priority 1 or 2 trigger has fired in the last 5 weeks, the editor picks a special from the pool below. These are evergreen — they don't depend on external events:

| Format | Example Topics |
|---|---|---|
| Guide (beginner mode) | Getting into Malazan, Specialty coffee from scratch, Fantasy Premier League for beginners, Home kettlebell training, Starting on Etsy |
| Guide (category mode) | A category roundup that hasn't been covered recently — boutique games, kettlebell drills, audio essay channels |
| Deep Dive | The history of a favourite game franchise, A deep look at a training methodology, The state of e-readers in 2026, Serie A tactical evolution |
| Versus | V60 vs AeroPress, Two fitness approaches, Two e-readers, Two budget tablets |

**The editorial picks pool ensures there's always a viable special available.** The editor selects the most timely or interesting option from the pool. Over time, used topics are tracked in the state file to avoid repeats.

**Manual-only format — Next.** Next never auto-triggers; it requires the reader to call it because it depends on specific context that only the reader holds.
- **Next** ("Run a Next — after [the thing you finished]") — needs the anchor: what the reader just finished. The magazine can't reliably detect "finished" status for podcasts/books/seasons from external signals.
- **Lookahead — RETIRED / FOLDED (v8.39, S2).** Formerly the second manual-only format; folded into the weekly's Release Radar + On the Radar (see § The Lookahead status marker). Do not run it. A reader asking "what's coming up over the next few weeks" is answered by the weekly's radar sections, not by a dedicated issue.

### The Saga (trigger-driven, v8.27 — no cadence timer)

The Saga (lore deep-dive — worldbuilding essays: Maul's arc across the shows, how Allomancy/the Cosmere connect, Malazan Warrens; **strictly no plot/endings**) used to fire on a 6-week clock. It no longer does. It runs only on a **reason**, of which there are two kinds — this is the general model for any section that depends on context the orchestrator can't infer:

- **Public peg (the researcher can find it).** A finale aired this week, a new book/season in a series the reader follows released, an author did an AMA. The scout/researcher detects this in Phase 0f/3 and pegs a Saga. This is the only Saga trigger that fires automatically.
- **Private peg (the pipeline cannot know it).** What the reader is *personally* reading or watching right now is invisible to the pipeline — the same boundary that makes Next and Lookahead manual-only. Surface it two ways: (a) the reader keeps a lightweight **`currently_reading` / `currently_watching`** note in `state/signal-state.json`, which the researcher reads as a peg source; (b) a **manual trigger** ("run a Saga on the Cosmere", "a Next after Deadhouse Gates") — zero-maintenance, on-demand.

If neither peg is live, The Saga simply doesn't run that week — it is never scheduled to fill a slot.

**Generalised principle: sections that depend on private context are reader-triggerable, not calendar-driven.** The magazine asks for / reads that context rather than guessing. This is the same reason The Session reads `training_phase` and The Itinerary reads `upcoming_trips`; v8.27 extends the pattern to reading/watching (`currently_reading` / `currently_watching`) for The Saga, and lets it inform Bookmark and Screen & Sound pegs too.

### Guardrails

- **Target frequency: one special every 4-6 weeks on average.** Not a hard rule, but if 6+ weeks pass without a special, Priority 3 must fire. If two natural triggers cluster in consecutive weeks, that's fine — but never three specials in a row.
- **Never more than 2 consecutive specials.** If two specials ran back-to-back, the next issue must be a standard weekly regardless of triggers.
- **The standard weekly is the backbone.** Specials are seasoning, not the main course. Most Sundays should be the standard weekly with rotating sections.
- **Manual triggers always override.** If the reader requests a specific format, that takes priority over any auto-trigger.
- **Track in state file:** `last_special_date`, `last_special_format`, `consecutive_specials_count`, `editorial_picks_used`.

### Trip-Aware Scheduling

Trips create a dense window where multiple triggers compete. These rules prevent collisions:

- **Issues still run during trips.** The reader wants something to read on the plane, at the pool, or watching giraffes. Standard weeklies and specials generate as normal even when the reader is away.
- **Defer Rewinds that clash with trips.** If a Rewind trigger (half-year or year-end) falls within 7 days of a trip start, defer it to the first Sunday after the reader returns. A Rewind is better as a "welcome back" issue than something competing with pre-trip excitement. All other formats (standard weekly, Season Review, etc.) run on schedule.
- **Field Guide before Countdown.** The Field Guide fires at ~6 weeks out; the Countdown fires at 2-3 weeks out. They should never collide. If they somehow would (very short trip lead time), the Countdown takes priority — the Field Guide is only useful with enough lead time to plan.
- **Season Reviews are patient.** A Season Review can't run until the week after the season ends (results need to be final). It has a 6-week window from there -- after that, drop it. Don't force it at the 6-week mark either; if other specials or strong standard weeklies have filled the calendar, that's fine. A Season Review that never runs is better than one shoehorned in when the moment has passed. If it does run, a combined review covering both Serie A and PL in one issue is fine when they end the same weekend.
- **Trip priority order for a typical trip window:** Field Guide (6wk) → standard weeklies / Season Reviews → Countdown (3wk) → standard weeklies → deferred Rewind (first Sunday back if clashing).

---

## Key Rules

These are editorial principles. The compliance checklist (Gate 1 + Gate 2) handles mechanical verification.

### The Cardinal Rule
**The reader profile drives selection, not prose.** The profile tells you what to research, what to cover, and what to prioritise. It must be completely invisible in the writing. Write every section as if the magazine has 100,000 readers. See Gate 1A in the compliance checklist for specific banned patterns — this is the most common failure.

**The Editor is visible; the reader is invisible (v8.35 — Gate 1A split).** "Invisible profile" means the *reader* is never on the page — no "you", no "your son", no "as a Juventus fan", no selection justifications. It does **not** ban the magazine's own first-person voice. A named **Editor** may speak in the first person ("I"), most of all in **The Letter**, and lightly as an editorial signature elsewhere — that is a magazine with a person behind it, which reads fine to 100,000 readers. The test still holds: *first-person Editor* ("I keep coming back to…") is allowed; *second-person reader address* ("you'll have noticed…", "your trip") is a leak. Gate 1A now enforces exactly that split.

### The Lens, Not the Filter (v8.19 — sits alongside the Cardinal Rule)

**The reader profile is a lens, not a filter.** It shapes *how* a topic gets framed; it never decides *whether* a topic gets covered. Two failure modes the lens-not-filter principle exists to prevent:

1. **News vacuum on a story everyone else is reading.** If a major story landed this week — war, election upset, regulatory change with broad consumer impact, death of a significant figure, scientific breakthrough — the magazine covers it. Coverage breadth is the magazine's job; the profile only narrows angle, not appetite. A weekly that goes silent on a genuinely big story because "it isn't on the interest list" is broken.

2. **Recommendation drift into reinforcement-only.** Every recommendation section (Bookmark, Listen, Workshop, Toolkit, Ledger, Long Game, Wallet, Brickyard, Saga, Lab, Channel) drifts toward "more of what the reader already engages with" unless explicitly counterweighted. The reader has Todoist; the next Toolkit shouldn't be more Todoist. The reader is into Malazan; the next Bookmark should include at least one book outside epic fantasy.

The structural mechanics that enforce this:

- **Discovery vs. Reinforcement (50/50 target per recommendation section).** Every recommendation section aims for roughly half its content reinforcing existing engagement, half surfacing something genuinely new. "New" means: a different app they don't use; a writer they haven't read; a label/artist they haven't heard of; a training method adjacent to but distinct from their current programme; a corner of personal finance they don't already follow. Writer self-audits per RT-23.

- **Issue-level Discovery Quota (≥ 3 per issue).** Independent of which sections appear, every weekly issue contains at least three "you wouldn't have looked for this yourself" items across the issue. The wildcards now come from **The Week, Composed** (a line pointing off the beaten track), **the Long Read** (a rotating-subject deep piece on something unfamiliar), **Down the Rabbit Hole**, or a Bookmark/round pick landing on an unfamiliar topic. Planner tracks `discovery_picks` as an issue-level array in the chapter plan. Gate 2 verifies count >= 3.

- **News breadth check.** Phase 0f's news scout (and the researcher's Group 1 scan in Phase 3a) explicitly searches for major world stories regardless of whether they map to the interest profile. World This Week's Lead OR Companion OR an Also item must cover any genuinely big global story that landed this week, even if neither maps to a declared interest. Skipping a major story because it's outside-profile is a Gate 2 editorial-quality fail.

Reinforcement still dominates the magazine because that's what makes it feel curated. Discovery has a guaranteed floor.

### What to Lead With (Cardinal-tier, with Lens-not-Filter & Borrowed-angles)

**A Lead, where a round runs one, earns its slot by reward-per-attention, and it is optional.** The two-factor test (did it move this week + can we add a *sourced, not invented* layer) governs the **Long Read** subject and any round Lead; it lives in § Article Structure → "The Lead". Summary: *lead with what moved; never re-run last week's subject on a holding pattern; no single theme owns the issue.* This is now **editorial judgement, not a gate** — the `check-topic-lock.py` and `check-theme-clustering.py` scripts are **retired (v8.37, W-3)**: the single Long Read and The Threads' continuity recap remove the structural cause the scripts guarded against. **Meta-rule: when an issue disappoints, adjust the principle — do not bolt on another rule or script.**

### Borrowed angles, our voice (v8.28 — Cardinal-tier, sits alongside Lens-not-Filter)

**The magazine never invents its own opinion — it borrows real ones and voices them as its own.** Take a clear, confident, opinionated angle and read like a magazine, but the **angle / opinion / conclusion / counterargument must be one real sources or commentators actually hold**, surfaced in the research. Express it in our voice *as if it were ours*, with **no obligation to quote, attribute, or cite** (this is a personal magazine, not journalism) and **no robotic "X said, then Y said"** framing. The only constraint is *provenance*: the take is borrowed from the real world, the wording is ours. It's the no-taste *spirit* of the Field Guide generalised ("opinions are reported, not held") — but NOT its attribution machinery; there's no quote-density or sourcing-display duty, only "don't invent it."

- **The writer's test:** *"Is this angle something real people actually argue — that I found in research — or did I make it up?"* Invented → cut it. Real → express it well, in our voice. **Invent nothing beyond what the sources support** — this also stops analysis being built on a premise that isn't there (the Monaco "Norris on pole" leap).
- **Naming a person requires the real words (v8.29).** Voicing a borrowed angle as our own carries *no* duty to attribute. But the moment you *name* a commentator (or hang the angle explicitly on them), the bundle must carry that person as a `type:"opinion"` fact with a real `speaker` + `quote`. No quote in the bundle ⇒ don't name them — voice the take unattributed. This is enforced upstream: the Phase 3b gate rejects an opinion fact missing its speaker/quote, so the writer can only attribute what research actually surfaced.
- **Not everything needs an angle.** Gaming releases, a results roundup, an evidence explainer (the muscle-in-a-deficit piece) are often *better* as plain facts — "study X found A, Y found B, Z found C, it leans toward W", no invented conclusion. State the studies; let them speak. A posed question must still be answered from what the sources show, never left hanging — **and land the answer (v8.30).** For a "how much / how many / which" question, state the number or range the sources support, plainly and up front; the methodology caveats go in a footnote or aside, never wrapped around the answer. **Hedging the answer into mush** ("somewhere in the region of ten to twenty…", immediately undercut by "none of this settles every case") where the sources support a clear range is the performing-caution failure: the Session "how many sets is enough?" lead had the numbers (67 studies, ~0.24%/set, the inverted-U) and still didn't land the takeaway. Give the reader the answer; then qualify it.
- **Length follows the material.** A 30-second idea gets ~30 seconds of words. Padding a thin topic and inventing an angle to fill a slot are the same disease — kill both.

### Editorial Voice
- **Confident and opinionated, but the opinion is borrowed, not invented** (see "Borrowed angles, our voice" above) — voice real takes as our own; never neutral, never a take you made up.
- **The Editor may speak in the first person (v8.35).** A named Editor voice ("I") is welcome — it's what makes this a personal magazine with someone behind it. It lives mainly in **The Letter**; used sparingly, a first-person editorial aside is fine elsewhere. The only hard line is the reader: never *you*/*your* (Gate 1A). Confident first-person ≠ reader address.
- **One genuine aphorism per issue — no per-section closers (v8.35).** The magazine used to end every section on a manufactured epigram; that tic is retired **structurally**, not gated. A section does **not** have to "land on a line" — most should simply end when the substance ends. At most **one** genuine, earned aphorism is allowed across the *entire* issue (spend it in The Letter or the strongest piece, or not at all). A pull-quote must be a real quote or a truly resonant line — **never the Angle box reprinted as a pull-quote**, and never an aphorism minted to fill the slot.
- **No bubble.** A critical claim ("the show declined") rests on what external coverage says, not the reader's view — the reader's preferences are context, not conclusions.
- **No spoilers.** Never, ever, for any book or show. Absolute but invisible — never announce compliance.
- **No defensive crutches.** No "it's not X, it's Y"; no justifying why content was selected. Present it well and let it stand.

### Content Standards
- **Sunday timing** — Saturday results are hours old. This should feel current.
- **7-day freshness rule.** News must be from this week. Evergreen features are fine when clearly framed as features. Don't force content from the reader profile when there's no current news to support it.
- **Facts come from the research bundle; verify everything (v8.28, structured v8.29).** The writer states only facts that are in the research bundle — it never introduces new ones (the prose analog of the image rule: every image must trace to `image_candidates`; every load-bearing fact must trace to a `facts` record). Load-bearing facts are **structured records** carrying `status` (`happened`/`upcoming`), `date`, and `source_url` — the researcher decides happened-vs-upcoming *while the sources are open*, and the writer renders that pre-decided tag rather than judging it mid-sentence (see § fact-provenance below). A stated result / fixture outcome / standing must have **actually happened by the run date** (when facts were knowable — not merely by the issue's cover date; an event between the run and the cover date is still in the future at research time) and trace to a source that reports it as happened — a preview or a prior-year result asserted as fact is fabrication (the Monaco "Norris on pole" failure for a qualifying session a week away; the State-of-Play showcase written as "delivered" before it aired). Scorelines, fixture dates, media items, podcast content: if it isn't in the bundle and verifiable, it doesn't go in. A fabricated Football Weekly summary or a made-up 7-0 draw is an unforgivable error.
- **Links are for the reader.** Every substantial item needs at least one outbound link. The reader should never think "I want to read more" and have nowhere to go. Wikipedia for history, original sources for news, specific URLs not category pages.
- **Images mandatory.** Maps are high-value visuals when relevant — conflict zones, historical sieges, park layouts, race routes. Source from Wikimedia Commons, news outlets, official sources. Never AI-generated.
- **2-3 wildcard items** per issue — things the reader didn't ask for. "Taste is a lens, not a filter."
- **Cross-cluster connections** — if an AI story connects to gaming, say so.
- **3-5 Did You Know boxes** scattered throughout, surprising and section-aware.
- **0-2 Asides per issue.** The Aside is a standalone mini-article (150-300 words) placed between full sections for pacing. It has its own topic, its own visual identity, and half the weight of a full section — but it's a proper piece, not a throwaway two-liner. No navigator card, no watermark. Never back-to-back. Label format: "The Aside — A Pattern" / "A Moment" / "A Discovery" / "A Question" / "A Skill". See component contracts for HTML structure.
- **Features every issue** — news + evergreen + fun. A great 2019 article is as valid as a 2026 one.
- **Every substantial item in The World This Week, Pixel & Byte, The Touchline, Screen & Sound, and On the Radar MUST include at least one outbound link** to the specific item — not a category page, not the show page, not the publisher home page. Items without links are non-compliant. Gate 1D hard fail.
- **Every Lead and every Companion in the chapter plan MUST carry a `topic_family` tag** drawn from the closed enumeration in `references/chapter-plan-schema.md`. When a section runs an optional Companion, Lead.topic_family ≠ Companion.topic_family within the same section. Planner-side validator enforces (only when a companion is present).

### Section Rules

The **rounds** carry the week's news at the depth the material earns (§ Article Structure, v8.37): a round may run a considered Lead, or cover what moved plainly, or run picks, or yield — there is **no mandatory considered-piece backbone in each section** any more (the single Long Read carries the deep work). When a round runs a Catch-Up it carries missable domain news — what/why/link, no namedrops. **Rounds no longer carry safety-net headlines** — Caught Up owns news-breadth. A Companion (second deep piece) is optional and rare. Rounds run short or yield when the week is thin.

- **World coverage:** world news leads the issue in **Caught Up** (the 8-line digest) and, on weeks it earns the depth, as the **Long Read**. There is no standalone World This Week round; the two-factor test now governs whether world is *this week's Long Read subject*. Lifetime-leads escalating bar applies to ongoing world stories as an editorial judgement (the topic-lock *script* is retired — see § Topic Lock); a heavily-rotated story cooling out of the Long Read is exactly what The Threads recaps.
- **Pixel & Byte (gaming + LEGO):** the dedicated gaming section, every issue. **Floor (the section minimum):** *what came out this week, plus highlights of the next month* — with real explainers, **never namedrops** (the "namedropped three games and moved on" failure is banned). Upside on top: a *new* rumour-with-analysis, or a release genuinely worth playing, as the angled Lead. Scope: Switch 2, Steam Deck/Steam Machine, GeForce Now, high-quality tablet games, plus generalist (the biggest game of the year, even if not on Switch). LEGO folds in as an occasional "play" beat. Consumer tech / AI / apps are NOT here any more — they moved to The Toolkit. Every item must link to its source.
- **The Toolkit (tech & tools — fixed slot, yields strictly):** absorbs consumer tech + AI + apps/tablet productivity. Its Lead stays a **discovery** ("a tool/app/feature worth finding"); its Catch-Up carries the consumer-tech news. **Expected to disappear regularly** — yield when the week is thin (don't pad it to appear weekly). **Catch-up rule on return:** cover the entire gap since its last appearance, not just the past 7 days. Wearable hardware/firmware news (Whoop, Garmin) lives here as consumer tech; fitness-*training* angles off that data live in The Session.
- **The Touchline:** data before narrative. Most compelling sport leads. Serie A ≥ PL on normal domestic weeks. Full table (top 10 + relegation). Section never exceeds ~30% of issue. Tournaments/Ryder Cup/majors can push football into secondary role. The Catch-Up must carry the football the reader actually wants — transfer rumours/confirmations, squad announcements — not just a recap of the match he watched. If a Companion runs, **it must be a non-football sport when the Lead is football.** Every results/standings item must link to its source.
- **Screen & Sound:** culture-critic voice. If a Companion runs, **it cannot be the same franchise as the Lead.** Same franchise cannot lead 3 issues consecutively (track in `ongoing_stories` as franchise tags). Every show/film/album recommendation must link.
- **Screen & Sound — Director's Cut sub-format (monthly).** Once every 4 standard weeklies, Screen & Sound's Lead runs as a Director's Cut — a 550-750 word essay on one show, film, director, or arc rather than the week's news beat. Voice: culture critic, not news reviewer. A Companion (different topic family) may carry the displaced current-week news beat, but the Catch-Up roundup still covers the week's releases. Track in state file `last_directors_cut_date`; planner-side hard rule `weeks_since_last_directors_cut >= 4`. Tagged in chapter plan as `sub_format: "directors_cut"`. Validator raises the Lead's word_count_target floor to 550 when set.
- **This Week in History — A Closer Look sub-format (every 6 weeks).** When History is scheduled AND `weeks_since_last_closer_look >= 6`, the section runs as A Closer Look — a single 600-800 word narrative deep dive on one event or figure, replacing the standard "one featured event + 3-4 also-this-weeks" pattern. Pre-WW2 strongly preferred. Wikipedia link mandatory. Track in state file `last_closer_look_date`. Tagged in chapter plan as `sub_format: "closer_look"`. Validator enforces single-item structure (no `also_items`) and 600-word floor on the featured item.
- **The Session (Desk column, absorbs Workshop + Lab):** Lead + a 200–250-word Companion deep note on a different training-topic cluster (training science and gear are now rotating angles *within* Session, not separate sections). State-file `last_session_topic` enforces same-cluster-not-consecutive. Fitness tech is Session's — Pixel & Byte and The Toolkit carry no wearable *training* leads. As a Desk column (v8.36) it closes on a "Do This Week" pin.
- **The Long Shelf:** 8 items, 2 of 8 MUST carry `wildcard: true` in the chapter plan. Wildcards = topics outside the magazine's usual coverage areas (not gaming, sport, Star Wars, fantasy/sci-fi, fitness, UK consumer fintech, theme parks, history podcasts). Validator counts and fails if < 2.
- **On the Radar:** Every item must link to its canonical source (Wikipedia, official page, league page). The 2-3 most important items per issue get a "Why it matters" half-line (10-15 words) below the date+event line.
- **On the Radar ≠ Release Radar** — they complement, never duplicate. On the Radar assumes intelligence — no explaining parkrun, no generic event types.
- **The Release Radar (mandatory weekly element, v8.30):** the magazine's standing answer to "what's coming out?" — **15-20 upcoming releases across ≥4 of the seven media categories** (film, TV, game, LEGO, tech, book, music), each with a date, a `status` (`upcoming`-weighted, reusing the v8.29 tag), a category dot (`.radar-cat`), and a link. Sub-sections (Now Showing / Coming Soon / Leaving Soon / Also Streaming) order items chronologically. It owns **all** product/media release coverage (On the Radar stays events-only; gaming releases still get their explainer in Pixel & Byte, but the *dated list* lives here). **Enforced:** the planner emits a `release_radar` chapter and `validate-chapter-plan.py` hard-fails a weekly that drops it or ships fewer than 15 items / 4 categories. This existed as prose-only "tail content" and silently vanished from the 1 June test — the gate is the fix.
- **Music:** lives in **Listening** when it runs (podcasts + audio drama + music), and lightly in Bookmark otherwise; music releases in Release Radar when neither is present.
- **History:** rotating, pre-WW2 preferred. Images must match the historical event.
- **The Itinerary (Desk column, was "Places"):** owns all travel/parks/NI local content when present (absorbs the old Itinerary + Local). One-liners in On the Radar when absent. Closes on a "Do This Week" pin.
- **Bookmark catches up** — when it returns to real named titles after yielding, research covers the full gap since the last books rail with picks. Same catch-up rule for The Toolkit, Listening, The Ledger, The Itinerary on return.
- **No single interest owns the issue.** No one topic gets more than ~one round plus a passing mention — the issue reflects the reader's range, not feed volume. (This is now editorial judgement: the `check-theme-clustering.py` backstop is **retired (v8.37, W-3)** — the four-movement spine, with one Long Read and brisk rounds, removes the structural cause that let fitness/Star-Wars/wearables flood an issue.)
- **No:** work/enterprise content (unless front-page-of-broadsheet significant), celebrity culture, royal family, generic fitness advice, AI-generated images, fabricated links.
- **UK / national politics rule (v8.27 — reset to OUT BY DEFAULT).** UK politics is **not an interest area**. It was originally banned as noise; after the council elections went uncovered the intent was to *soften* the ban so the genuinely-big-and-interesting got in — but the spec over-corrected into a politics-chasing engine (the direct cause of the Starmer ×3 run). The correct rule:

  **Default: out.** Don't go looking for it; don't lead with it.

  **In only when** it is a genuine landscape shift — an election *result* that changes the national picture (a Reform breakthrough; the two-party system fragmenting; a government actually falling) — **AND** interesting to a generalist. Even then it must pass the same two-factor Lead test as anything else; it is not auto-promoted.

  **Always out (parish-pump / Westminster process — the noise the original ban targeted):** cabinet reshuffles; leadership will-he-won't-he and resignation-call counts; vote-of-confidence threats that haven't happened; individual by-elections and ward results; Stormont/Assembly party-on-party spats (street names, parades, flags); committee reshuffles, whip rows, Speaker rulings; polling-only stories with no event behind them.

  **A leadership challenge or cabinet resignation is, at most, a one-line safety-net mention in the Catch-Up** — not a Lead, unless the government actually falls and that clears the two-factor test. The same threshold applies to Irish, Scottish, Welsh and broader European national politics: *does the shape of national politics actually change?* If not, it's out.

---

## Visual Design

**The template parts in `assets/template-parts/` are the authoritative structure reference.** Each file holds one logical section (cover, navigator, world, touchline, etc.). Use their class names and component patterns exactly. Read only the parts this issue uses.

**CSS/JS injection:** Do NOT read or paste any file from `assets/css/` or `assets/script.js` into context. Instead, place `<!-- INJECT:CSS -->` in the `<head>` and `<!-- INJECT:JS -->` before `</body>`. After generation, run `scripts/inject-assets.sh` to inject the full CSS and JS automatically. This saves significant context for research.

**Fonts:** Cormorant Garamond (headlines, body), DM Sans (UI, tags, labels), JetBrains Mono (section labels, dates).

**Section backgrounds:** World = `--paper` (light), Pixel & Byte = `--warm`, Touchline = `--pitch` (near-black), Screen & Sound = `--screen-bg` (dark purple), Shelf = `--shelf-bg` (dark brown), Session = `--session-bg` (light green), History = `--hist-bg` (parchment). **Rotating section backgrounds:** Workshop = light grey/steel accent, Toolkit = light blue-grey/cyan accent, Ledger = warm cream/amber accent, Long Game = cool grey/navy accent, Wallet = clean white/teal accent, Itinerary = warm sand/coral accent, Listen = warm slate/brass accent (dark), Local = earthy green/copper accent (dark), Brickyard = warm beige/brick-red accent, Saga = deep purple/antique gold accent (dark), Lab = light cool grey/lab-blue accent, Channel = dark navy/neon-magenta accent (dark). New rotating sections should use CSS custom properties following the same pattern as existing sections.

**Dark sections:** body text uses `rgba(255,255,255,.8)`. DYK boxes adapt to section palette.

**Output:** single HTML file, CSS and JS injected via build script, responsive (960px max-width, breakpoints at 820px and 600px). Reader's primary device is a Xiaomi Pad 8 tablet (~800px portrait), which sits BETWEEN the 820px and 600px breakpoints — always sanity-check tablet rendering, not just desktop and phone.

**Tablet column-width rule (special editions):** Centred display blocks that use `max-width: <N>ch` (manifesto, huge pull quotes, image-quote blockquotes, diptych body) must have a tablet override at `@media (min-width: 601px) and (max-width: 1024px)` that widens the measure with `min(<pct>%, <px>)` instead. At tablet, `clamp()` font sizes sit at their mid-scale (~5vw of 800px ≈ 40px) and a 20ch limit collapses to ~360px — a narrow column marooned in the middle of the viewport. Always widen to at least 90% of the viewport up to a sensible px cap. The same logic applies if you add any new centred component bound by `ch` measure: include the tablet override in the same patch.

**Cover height rule (all formats):** `.cover` must fill the full viewport on first load — no next-section chrome (chapter gate, first headline, ground colour) should peek up from below the fold. Implementation: `min-height: 100vh; min-height: 100dvh; box-sizing: border-box` on the base rule, and the same full-height on the mobile override at `@media (max-width: 720px)`. **Do not regress to `82vh` / `72vh`** — those were from an earlier pre-tablet version and leave the cover shorter than a modern phone or tablet viewport. `100dvh` ensures the cover stretches to the full window whether the mobile URL bar is shown or hidden. The scroll-cue inside the cover foot is the reader's sole cue to keep scrolling; nothing from the next section should compete with it. If you add a new component inside `.cover`, use `grid-row: auto` and let the existing `auto 1fr auto` track layout anchor it — don't set a fixed cover height that shorter than the viewport.

**Tablet ground-level gutter rule (special editions):** `.sp-ground-paper` and `.sp-ground-ink` chapter wrappers are full-bleed by design — the background tone reaches the viewport edge. Their CONTENT is given a horizontal gutter on tablet and mobile by `26-special-editorial.css` (28px tablet / 20px mobile, with `env(safe-area-inset-*)` floors). When you add a NEW component inside a chapter that should also be full-bleed (like `.sp-pull-break`, `.sp-folio`, `.sp-gallery`, `.sp-image-strip`, `.sp-scroll-image.is-fullbleed`), you MUST add it to the `:not(...)` exemption list in that media query — otherwise it'll inherit the gutter and look misaligned against the other full-bleed components.

**Navigator:** every format that has a navigator uses `04-navigator.html` — a card grid with a lead-card thumbnail. Specials that want an in-issue contents page do it through the chapter-numeral structure inside `<section class="chapter">`, not a separate template. (The former `04-navigator-toc.html` TOC variant was deleted in v8.22.11 — no current format used it, and writers reaching for it on weeklies was the May 17 / May 24 2026 bug.)

---

## Special Editions — Editorial System (v8.21)

Special editions (Countdown, Rewind, Versus, Season Review, Deep Dive, Starter Kit, Shortlist, Next, Lookahead, Field Guide) opt into the editorial system defined in `assets/css/23-special-tokens.css` through `32-special-format-flair.css` (v8.21). Holiday formats (Countdown, Field Guide) layer their own visual identity from `33-` and `36-` through `44-` on top of that. The system activates only when `<body>` has `class="is-special"`.

### Content-first contract (non-negotiable)
Every non-holiday special edition obeys these rules. Holiday specials (Countdown, Field Guide) have their own contract in `36-holiday-*`.

- **No motion in the non-holiday system.** As of v8.21, the non-holiday specials are an editorial / paper-and-ink design with no scroll-driven animation. Holiday formats retain their motion layer.
- **JS-off renders a complete issue.** The whole non-holiday system is pure CSS.
- **Word counts and section depth are the spine.** Visual flair sits around content, not in place of it.
- **Quiet vs. visual register.**
  - *Quiet* — Starter Kit. Baseline editorial system + minor accent (drop cap, format colour, numbered ring badges on Starter Kit essentials).
  - *Argued (Deep Dive)* — baseline plus `.argument` framed thesis early + `.keep-digging` cross-media closing grid. Body is literary, but two distinctive components anchor the opening and the close.
  - *Visual* — Versus, Rewind, Season Review, Shortlist, Next, Lookahead. Same baseline plus format-specific components (`.vs-tape` / `.vs-pair` / `.vs-verdict`, `.year-band` / `.rewind-cards` / `.memory-test`, `.rating` / `.scoreboard` / `.milestones`, `.tier-band` / `.pick`, `.on-ramp` / `.only-one`, `.calendar` / `.cal-verdict` / `.crunch-week`) for clear differentiation.

### Authoring a special edition
1. On `<body>`, add `is-special` and `data-special="<format>"` where format is one of: `countdown`, `rewind`, `versus`, `season-review`, `deep-dive`, `starter-kit`, `shortlist`, `next`, `lookahead`, `field-guide`.
2. **For Countdown only:** add `data-dday-start="N"` on `<body>` where N is the number of days between the issue date (today, when generating) and the event. The D-day badge displays this authored value statically — a magazine issue is a snapshot and the badge must agree with the prose, forever. Compute N at generation time as `(trip_date - today)` in days. The Countdown auto-trigger fires 2-3 weeks before a trip, so N is typically 14-21. If generating a prototype or back-dated issue, use the fictional issue-date reference. (Optional: also add `data-trip-date="YYYY-MM-DD"` for human reference, but it does NOT drive a live countdown at runtime.) The previous scroll-scrubbing pattern (`data-dday-start` + `data-dday-end` interpolated by scroll percentage) has been removed — a scroll-driven countdown is nonsensical.
3. Include the components from the component list below as appropriate for the format. Each component has a documented HTML contract in `component-contracts.md` (or inline in the CSS).
4. Inject assets with `scripts/inject-assets.sh` as normal.

### Cover — mandatory richness floor (v8.22.4)

Every non-holiday special cover MUST include all of these. A bare cover (eyebrow + title + deck only) ships as sparse; the Yellow Turban Deep Dive cover (2026-05-22) is the floor.

- `.cover-meta` — top row, two children. **Left:** `<span><strong>The Signal</strong> · <Format></span>`. **Right:** `<span><Issue date> · Sunday Edition</span>` (or "Sample Issue", "No. N", etc.).
- `.cover-eyebrow` — **at least two meta tokens** separated by `·`. E.g. "A Deep Dive · 184 CE · Eastern Han", not just "A Deep Dive". Carries format + period + scope-tag where relevant.
- `.cover-title` — serif headline. At least one accent-coloured `<em>…</em>` inside.
- `.cover-deck` — italic-serif description, 25-50 words. The deck is where the issue's argument shows up first.
- `.cover-slogan` — **MANDATORY** epigraph block with three children:
  - `.cover-slogan-cn` / `.cover-slogan-primary` — large serif line. The native-language phrase, the headline quote, the founding figure's slogan, the chant, the line on the wall. Whatever fits the topic.
  - `.cover-slogan-en` / `.cover-slogan-translation` — italic-serif translation or gloss.
  - `.cover-slogan-attr` — mono-caps attribution line. Source + date or topic + era.
- `.cover-foot` — bottom row, **three children**. **Left:** issue meta ("Twelve chapters · 10,900 words"). **Center:** `.cover-scroll` ("Scroll to begin"). **Right:** tagline ("Hand-set · Long-form · Sunday Morning"). Centers on a single child if only one is provided.

A cover that omits the slogan block or runs `.cover-foot` with only one child reads as a sample, not as an issue. Gate-1 grep check should warn.

### Component list

> **Note (v8.21):** The non-holiday special edition system was redesigned around an editorial / paper-and-ink aesthetic (see `assets/css/23-` through `32-` files). The list below documents the **new** components. Holiday formats (Countdown, Field Guide) retain their previous holiday-themed system in the `33-`, `36-` through `44-` CSS files — those are not affected by this list.

**Persistent chrome (every non-holiday special):**
- `.mast` — thin pinned bar at the top of every page, containing `.mast-wordmark`, `.mast-format`, `.mast-sep`, `.mast-date`. Inverts to a translucent dark style while the dark cover is in view. Provides a constant "where am I" anchor.

**Cover (every non-holiday special):**
- `.cover` — single-screen dark cover with filmic grain and per-format radial-pool gradient. Contains:
  - `.cover-meta` — top row: issue date/number left, format mark right
  - `.cover-body` — centered column with `.cover-eyebrow` (mono caps), `.cover-title` (serif), optional `<em>` for accent words, `.cover-deck` (italic serif), optional `.cover-slogan` block (epigraph / slogan with hairlines top + bottom)
  - `.cover-foot` — bottom row with optional `.cover-scroll` cue
- Versus only: title is a 3-column grid (`.vs-a` / `.vs-glyph` / `.vs-b`) — the matchup, balanced

**Chapter structure (every non-holiday special):**
- `.foreword` — first chapter after cover; larger measure, italic small-caps first line via `.foreword-body`
- `.chapter` — every subsequent chapter. Contains:
  - `.chapter-head` with `.chapter-numeral` (italic roman) + `.chapter-title`
  - `.chapter-body` — clamped to `--measure` (36rem) by default
  - `.is-wide` / `.is-fullbleed` modifiers on children to break out of the measure
- `.sp-kicker` — sub-section heading inside long chapters (mono caps, accent)

**Baseline flair (every non-holiday special):**
- `.chapter-body.has-dropcap` or `<p class="lede">` — first paragraph gets a large accent drop cap
- `.sp-ornament` — three dots, used to break up sub-sections within a chapter
- `.pullquote` with `<p>` + optional `<cite>` — huge italic pull quote with ornamental "
- `.marginalia` (+ `.is-left`) with `.m-label` + body — chip in the gutter; falls back to inline at ≤1180px
- `.bignum` with `.bignum-value` + `.bignum-label` — single stat callout
- `.bignum-row` — grid of 2–4 `.bignum` items, top + bottom hairlines
- `.source-strip` — mono caps row of citations
- `.sp-number` — inline accent-coloured stat (e.g. `<span class="sp-number">74</span>`)

**Figures (every non-holiday special):**
- `figure.fig` with `<img>` + `<figcaption>` containing `.fig-caption` + `.fig-credit`
- Modifiers: `.is-wide`, `.is-fullbleed`, `.is-half` (+ `.is-left`)
- `figure.image-quote` with `<img>` + `<blockquote>` — darkened photo with overlaid italic quote and accent-coloured `<cite>`

**Rich pick + multi-item grid (every non-holiday special, v8.22.4):**
- `.pick` — image + body grid, alternating layout (image-left odd rows, image-right even rows). Contains `<img class="pick-img">`, `.pick-body` with optional `.pick-tag` pill + `<h3>` + prose + optional `.pick-stats` (a `<dl>` of mono-caps `<dt>` + serif `<dd>`). The workhorse for detailed-pick chapters across Shortlist, Starter Kit, Next, Deep Dive.
- `.also-cards` grid — 4-8 `.also-card` items (`.ac-meta` mono-caps category line + `<h4>` + italic `<p>` why-it's-here + optional `<a>` source link). For "Also Worth Knowing" / "Where to Go After That" / "Shows Just Outside the Top Six" / "Related Reading" patterns. Cross-format.

**Meanwhile section (when a special replaces the standard weekly):**
- `.meanwhile-list` — bulleted catch-up list with tier dots (`.tier-hot` / `.tier-warm` / `.tier-note`)

**Footer (every non-holiday special):**
- `.sp-footer` with `.sp-footer-wordmark`, `.sp-footer-meta`, optional `.sp-footer-colophon` — quiet sign-off panel with ornament rule above

**Format-specific flair (visual formats — Versus / Rewind / Season Review / Shortlist / Next / Lookahead):**
- *Versus:* `.vs-tape` (tale-of-the-tape table), `.vs-pair` (stacked case panels with per-side accent rails + Case A / Case B badges), `.vs-verdict` (dark wide verdict slab with side stripes), optional `.vs-scoreboard` ribbon (running tally with side colours)
- *Rewind:* enlarged `.bignum-row`, `.year-band` (12-month rail with `.year-band-month` + `.year-band-marker` highs/lows + `.year-band-legend`), `.rewind-cards` (`.rewind-card` + `.is-low` modifier), `.chapter-head.is-throughline` + `.throughline-mark` for the Throughline chapter, `.memory-test` 3-column grid (`.mt-col.mt-stick` / `.mt-might` / `.mt-fade`) for the second killer feature
- *Season Review:* `.scorecards` grid of `.scorecard[data-tier="hot|warm|cold"]` cards — each with `.sc-head` (`.sc-name` + `.sc-score`), `.sc-bar` driven by `--score: N`, `.sc-verdict` italic line. Legacy `.rating` / `.scoreboard` / `.milestones` still available for stat-heavy supporting chapters.
- *Shortlist:* `.lens` framed criteria block (`.lens-eyebrow` + `.lens-statement` italic + `.lens-criteria` numbered list) at the opening; `.tier-band` (`.tb-mark` + `.tb-label` + `.tb-rule`, `data-tier="strong|wildcard"` for accent swap) divides the body into Top / Strong / Wildcard sections; the cross-format `.pick` (with `.pick-img`, `.pick-tag`, `.pick-stats`) carries each detailed pick; `.cheat-sheet` table (`#` / `Pick` / `Tier` / `Why` columns, rows tagged `data-tier="top|strong|wildcard"` for inline colour-coding) at the close. `.also-cards` for "Also Worth Knowing."
- *Next:* `.next-tier` row with `data-step="I|II|III"` for the numbered roundel marker (+ `.is-wildcard` modifier for the third tier); `.on-ramp` stepped track — the killer feature — with three `.on-ramp-row` entries each tagged `data-step="start|reassess|then"` (auto-renders the glyph + connecting track), `.on-ramp-label` + `.on-ramp-body`; `.only-one` dark slab for the "If You Only Try One" hero with star seal (`.only-one-mark` + `.only-one-pick` + `.only-one-reason`)
- *Lookahead:* `.calendar` `<ol>` with optional `<li class="cal-week">` dividers and `.cal-row` items carrying `data-verdict="hot|warm|wait|skip"` — each row has a tinted background + accent rail in the verdict colour, `.cal-when` (date card with `.cal-date` + `.cal-where`), `.cal-body` (`<h4>` + `<p>`), `.cal-verdict` containing `.cal-verdict-chip` (full pill — the killer chip with glyph + label + tinted bg) and optional `.cal-reason` italic gloss; plus `.crunch-week` callout with `.crunch-header` (`.crunch-label` warning chip + `.crunch-when` heading) and `.crunch-list` `<dl>` whose `<dt>` carry `data-tier="hot|warm|wait|skip"` for tier-coloured Prioritise / Defer / Skip badges

**Deep Dive flair:**
- All baseline components above. Plus two killer-feature components:
- `.argument` — framed thesis block (`.argument-eyebrow` + `.argument-thesis` italic serif + `.argument-stance` paragraph). Sits between Foreword and the body; pilcrow seal in accent.
- `.keep-digging` — closing cross-media grid of `.kd-item` cards. Each card carries `data-medium="podcast|tv|film|game|video|book"` (which paints the per-type pill colour + glyph) and contains `.kd-medium` pill, `.kd-title` heading, optional `.kd-episode` italic line (mandatory on podcasts — series-only refs forbidden), `.kd-why` italic gloss.

**Starter Kit flair:**
- All baseline components above. Distinct `--accent` colour set on `body[data-special="starter-kit"]`.
- `.essentials` ordered list — each `<li>` gets a numbered ring badge. **Use only for short concept lists** ("5 essential techniques", "7 things to learn first"). NOT for detailed-pick chapters — those use the cross-format `.pick` (each pick gets image + body + `.pick-stats` + a `.pullquote` or `.image-quote` for visual rhythm).
- `.week-plan` vertical timeline — the killer feature. Seven `.wp-day` items with badged day-marks (Day N / Mon) on the left of an accent rail, body on the right.

**What was removed (v8.21 redesign):**
- All scroll motion (`.sp-parallax`, `.sp-stagger`, `.sp-wipe`, `.sp-curtain`)
- Pre-roll splash (`.sp-splash`), ticker masthead (`.mast-ticker`), rotated format badge (`.sp-format-badge`)
- Signature moments (`.sp-sig-*`), chapter gates (sticky-scroll model), hype variants
- Old editorial breakouts (`.sp-manifesto`, `.sp-bignum`, `.sp-gallery`, `.sp-diptych`, `.sp-marquee`)
- The Blueprint format (retired in v8.22 — never used after 6+ specials, planning use cases absorbed by Deep Dive and Shortlist)
- These components/formats are no longer in the CSS bundle for non-holiday specials. Don't reference them in new issues. They remain in already-published issues since their CSS is inlined at generation time.

### Imagery budget — MANDATORY for loud special editions

A Countdown / Versus / Rewind issue **must not** have entire sections that are walls of text. The previous pattern (front-loaded imagery in the opening then plain prose for the rest) is banned. Apply the following rule at generation time:

**Every major body section (Foreword excepted) must include at least ONE of:**
- A `.sp-scroll-image`, `.sp-inline-figure`, `.sp-image-quote`, or `.sp-image-strip` (imagery)
- A `.sp-number-block`, `.sp-pullquote-huge`, `.sp-bignum`, or `.sp-chapter-number` (high-impact typographic component)
- A `.sp-gallery` or `.sp-diptych` (multi-image layout)

**In addition, across the whole issue:**
- At least **2 sections** use a multi-image component (gallery, diptych, or image-strip)
- At least **3 sections** use `.sp-scroll-image` or `.sp-inline-figure` for embedded imagery
- At least **2 sections** use `.sp-pullquote-huge` to break up prose
- Long prose sections (>500 words) include `.sp-kicker` on h3/h4 headings
- Long prose sections include at least one `.sp-marginalia` or inline `.sp-number` callout
- Section transitions alternate between `.sp-wipe` and `.sp-curtain` for rhythm variety — don't use the same transition twice in a row

These are minimums — more is fine. Research images for EVERY major section, not just the cover topic.

### Image-caption integrity (v8.10.3 — hard rule)

A wrong image with a confident caption is worse than no image at all. Three failure modes have been observed in past issues; all are forbidden, all are mechanically scannable in Gate 1F.

**1. No duplicate `src` URLs in one issue.**
Every `<img src="…">` in the rendered HTML must point to a unique URL. Re-using the same image with two different captions is a fabrication: at least one caption is lying. If the same image genuinely belongs in two places, redesign — find a second source for the second placement, or cut one of the placements. The most common variant of this bug is the same YouTube thumbnail used twice with contradictory subjects (e.g. `i.ytimg.com/vi/<id>/maxresdefault.jpg` captioned as Venue A's pools in chapter III and Venue B's harbour in chapter VII). Banned without exception.

**2. YouTube thumbnail subject must match the video.**
Every `i.ytimg.com/vi/<id>/...` URL has its subject defined by the video at `https://youtube.com/watch?v=<id>`. Before using a YouTube thumbnail as a still image, confirm the video's title actually depicts the captioned subject. If you cannot watch or verify the video, do not use the thumbnail — find a different image. The thumbnail is the first frame or chosen poster of the video; it has one subject only.

**3. Wikimedia filename must match caption subject.**
Wikimedia Commons URLs encode their subject in the filename: `Sirmione_007.JPG` is a photograph of Sirmione, not Salou. Before captioning a Wikimedia image, read the filename and the Commons file page to confirm what the photograph actually shows. The caption may abbreviate (`Sirmione harbour at dusk` is fine for `Sirmione_007.JPG`) but it must not contradict (`Salou seafront` for `Sirmione_007.JPG` is fabrication).

**4. Caption describes ACTUAL image content, not intended subject.**
If the only image you can find for a chapter on Venue A's safari park is a stock photo of a giraffe with no Venue-A context, the caption must say `A reticulated giraffe — illustrative` not `Giraffes at Venue A's drive-through enclosure`. Captions must be honest about what the photograph shows, not aspirational about what it represents. Where a generic image is unavoidable, flag it as illustrative; where it isn't unavoidable, find a specific image instead (see §Image specificity check in compliance checklist).

**5. Every image carries a credit line.**
The credit lives inside the `<figcaption>` (or `.sp-caption-strip`) and names the photographer / source publication / Wikimedia author. Reused official press kits cite the venue (`Photo: Efteling press kit`). Wikimedia images cite the Commons author + license (`Photo: Velvet, CC-BY-SA 4.0 via Wikimedia Commons`). YouTube stills cite the channel (`Still: TheCoasterFanatics, YouTube`). No credit = the image cannot ship.

### Image URL verification chain (v8.13.7+) — UNBREAKABLE RULE

Image bugs have shipped repeatedly despite gates passing because the gates trusted self-attestation. The verification chain below makes broken / fabricated / duplicate images structurally impossible to ship — each layer alone is bypassable, together they are not. Pipeline phases enforce each layer:

**Layer 1 — Researcher (Phase 3a).** Every entry in `image_candidates[i]` MUST carry a `verified` block proving the researcher ran `WebFetch` on the URL during research and received 2xx + `Content-Type: image/*`:
```json
"verified": { "head_status": 200, "content_type": "image/jpeg", "verified_at": "<ISO timestamp>" }
```
A candidate the researcher cannot verify is **dropped**, not passed through with a "verify later" note. Common fabrication traps to avoid: Wikimedia `/thumb/<hash>/<hash>/<file>.jpg/1280px-<file>.jpg` (only exists if pre-generated at that size); made-up filenames (`Polles_Keuken_(2).jpg` when the real file is `Polles_Keuken_Efteling_2.JPG`); brand-site page URLs treated as images (returns HTML, browser renders nothing). Bundle floor: **≥16 unique verified URLs** (threshold `min_unique_candidates` in `image-source-types.json`) so writers never need to recycle.

**Layer 2 — Orchestrator (Phase 3a-verify).** After the researcher returns, the orchestrator (main pipeline loop) MUST itself call `WebFetch` on every URL and **overwrite** the researcher's `verified` block with its own result. This closes the self-attestation hole — a fabricated `verified` block from the researcher is replaced with the orchestrator's truth. If WebFetch is egress-blocked in the orchestrator's environment, the bundle records `verified.head_status: "blocked"` and the CI workflow becomes the authoritative gate.

**Layer 3 — Bundle gate (Phase 3b, `validate-research-bundle.py`).** Rejects any bundle with: a candidate missing `verified`; a candidate with non-2xx `head_status`; a candidate with non-`image/*` `content_type`; fewer than `min_unique_candidates` distinct URLs; URLs without an image extension and no `direct_cdn: true` flag.

**Layer 4 — Writer contract.** Writers MUST use `src=` values **verbatim** from `image_candidates`. Inventing URLs (even legitimate-looking CDN paths) is forbidden — enforced upstream by Layer 3 (the bundle gate) + Layer 2 (orchestrator re-fetch), and any that slip through are rotated out by Layer 5's auto-repair.

**Layer 5 — DOM checks + auto-repair (Phase 7.6 `validate-issue.py` + Phase 9 round 0 `auto-repair-images.py`).** *(v8.38, W-4: the old standalone `visual-smoke-test.py` DOM gate is deleted; its image-safety intent lives here, inside the image-URL verification chain gate.)*
- **Page-url-as-image (old D3):** `validate-issue.py`'s `static_image_url_check` fails any image URL whose path has no recognised image extension — the "page URL pasted as `<img src>`" pattern. Runs even offline.
- **Duplicate image URLs (old D6):** `auto-repair-images.py` detects any URL used more than once in the rendered DOM and rotates in an unused bundle URL. The no-duplicate-src rule (§ Image-caption integrity, Gate 1F) is the manual backstop.
- **Unbundled images (old D7):** enforced upstream by Layer 3 + Layer 2 (the bundle is the only authority); `auto-repair-images.py` substitutes any DOM URL not traceable to `image_candidates`.

**Layer 6 — CI workflow (`.github/workflows/issue-validation.yml`).** Runs all gates on every push and PR in an unrestricted-egress environment. The image-URL HEAD check that degrades to a warning in the sandboxed pipeline runs for real here. On failure, auto-files a GitHub issue labelled `validation-failed`. For full enforcement, branch protection on `main` requires this workflow to pass before merge (one-time UI setup).

This is the complete chain. Each layer is enforced by code, not by writer discipline. Adding a new image-shipping defect class means adding a new layer here.


**Fact provenance chain (v8.29) — the prose analog of the image chain.**

Trust holes in the *prose* (a future event written as done; a name pinned to words nobody said) shipped for the same reason image bugs did: the "is this real / has it happened / who said it?" judgment lived in the writer's head, mid-sentence, where it just had to be remembered. This chain moves that judgment **upstream to the researcher** — who has the sources open — and records it as a machine-checkable field, so the writer renders a pre-decided answer. It deliberately **reuses the existing two gates** (`validate-research-bundle.py`, `check-release-dates.sh`) rather than adding a new script — per the § Key Rules meta-rule, *adjust the structure, don't accrete gates.*

**Layer 1 — Researcher (Phase 3a).** Every load-bearing claim is a structured record in `bundle.facts`, decided against the **run date** (today), not the issue's cover date:
```json
{ "claim": "…", "status": "happened|upcoming", "date": "YYYY-MM-DD", "source_url": "https://…",
  "type": "fact|opinion", "speaker": "<iff opinion>", "quote": "<iff opinion — the real words>" }
```
A claim the researcher can't source is dropped; an event still in the future at run time is `status:"upcoming"`, never `happened`.

**Layer 2 — Bundle gate (Phase 3b, `validate-research-bundle.py --run-date <today>`).** Rejects a fact missing `claim`/`status`/`date`/`source_url`; a `status:"happened"` fact dated *after* the run date (it cannot have occurred — the State-of-Play / "Norris on pole" temporal hole, caught upstream); a `type:"opinion"` fact without a real `speaker` + `quote`.

**Layer 3 — Planner.** Copies the relevant fact records into each chapter's `key_facts` (structured), so the tag travels to the writer.

**Layer 4 — Writer contract.** Renders the tag: a `status:"upcoming"` fact reads as forthcoming ("coming Thursday"), never past tense; a person is named only when the fact carries a `quote`; no fact outside the bundle (RT-22).

**Layer 5 — Release-date gate (Phase 7.5, `check-release-dates.sh <html> <issue-date> <run-date> <bundle>`).** Surfaces every date/result claim in the rendered prose for verification against the **run date**, and lists the bundle's `status:"upcoming"` facts so the agent confirms each reads as forthcoming, not as a result.

**Layer 6 — CI workflow.** Re-runs the gates on every push with full network.

Each layer alone is bypassable; together they make "future event written as done" and "name pinned to words nobody said" structurally hard to ship. Adding a new prose-trust defect class means adding a layer here — not a new standalone script.

**Editorial body kit (tier 5 — magazine-spread structure):**
- `.sp-ground-paper` / `.sp-ground-ink` — alternating-ground wrapper for chapters. Apply to each major section so chapters alternate between paper (cream) and ink (deep) grounds. The shift of value on scroll IS the transition between chapters; no bridge component needed when alternating. Variants: `.sp-ground-warm` (warm cream), `.sp-ground-tint` (rose-tinted paper), `.sp-ground-deep` (pitch black).
- `.sp-chapter-chrome` — thin top bar inside every chapter: `<span class="sp-roman">III</span><span class="sp-hair"></span><span class="sp-chapter-name">…</span><span class="sp-chapter-slug">…</span>`. Mandatory at the top of every chapter on a special edition. Anchors the bound-magazine feel.
- `.sp-folio` — giant background numeral behind chapter content (300-700px, ~5% opacity). Position with `.sp-folio-tl/-tr/-bl` variants. Place inside a chapter wrapper that has its own positioning context.
- `.sp-spread` with `.sp-rail` + `.sp-spread-body` + `.sp-margin` — three-column feature-spread pattern. Narrow ink rail (oversized italic numeral, vertical spine label, act/section name) | body prose with proper drop cap and § section marks | tinted right margin column carrying marginalia and datums. Mandatory for any chapter ≥800 words. Collapses to single column ≤980px.
  - Inside `.sp-margin`: use `.sp-margin-kicker`, `.sp-margin-quote` (with `.sp-margin-attrib`), and one or more `.sp-datum` (each containing `.sp-datum-n` + `.sp-datum-l`).
- `.sp-brief` — sidebar card with thick accent left rule. `<div class="sp-brief"><p class="sp-brief-kicker">…</p><h4 class="sp-brief-h">…</h4><p>…</p><p class="sp-brief-byline">…</p></div>`.
- `.sp-hero-quote` — bordered card with oversized translucent “ peeking above the top edge. `.sp-hero-quote-q` for the quote, `.sp-hero-quote-at` for attribution.
- `.sp-dash` — stat dashboard band: 3-4 `.sp-dash-cell`s, soft tinted background, oversized italic numerals (`.sp-dash-n`) + mono labels (`.sp-dash-l`) + accent kickers (`.sp-dash-hint`). Use this instead of italicised stat lists.
- `.sp-timeline` — editorial two-column timeline. Each `.sp-tl-row` contains `.sp-tl-when` (large italic date with optional `.sp-tl-tag`) and `.sp-tl-what` (with `<strong>` lede + serif body, accent dot on rule). Perfect for day-by-day plans.
- `.sp-pull-break` — full-bleed dark band with two giant translucent quote marks in opposite corners and centred pull (`.sp-pull` + `.sp-pull-attrib`). Much more dramatic than a normal pull quote; use 1-2 per issue.
- `.sp-bridger` — three-column interlude inside a section: numeral marker (`.sp-bridger-side` with `.sp-bridger-num`) | prose (`.sp-bridger-main`) | sidebar/quote (`.sp-bridger-aside`). Sits on warm-cream ground, breaks body rhythm.
- `.sp-caption-strip` — richer photo caption with hairline rule + `.sp-cap-loc` mono location chip on the right.
- `.sp-signoff` — italic display sigil with hairline accent rule, marking the end of a chapter.
- `.sp-eyebrow` — tiny mono kicker in accent colour, used above any major heading or component title.

### Editorial body kit — MANDATORY rules for loud special editions

The tier-4 imagery budget addresses *what's in* each chapter. The tier-5 editorial body kit addresses *how each chapter is structured*. Both apply.

**Per-chapter:**
- Every chapter wrapper carries `.sp-ground-paper` or `.sp-ground-ink`. Chapters alternate ground value — never two paper chapters in a row, never two ink chapters in a row. The shift IS the transition; this replaces the need for a `.sp-wipe` or `.sp-curtain` between alternating-ground chapters (use those between same-ground chapters or for rhythm variety only).
- Every chapter opens with a `.sp-chapter-chrome` strip carrying its roman numeral, name, and slug.
- Every chapter contains at least one `.sp-folio` watermark for typographic depth.
- Any chapter ≥800 words MUST use a `.sp-spread` layout (rail + body + margin). Shorter chapters may use a single-column body but still need at least one `.sp-brief`, `.sp-hero-quote`, or `.sp-dash` mid-prose.
- Every chapter ends with a `.sp-signoff` line.

**Across the issue:**
- At least 1 `.sp-pull-break` for a major rhythm break (typically between the second and third chapter)
- At least 1 `.sp-bridger` interlude inside a long chapter
- At least 1 `.sp-dash` instead of an italicised list of stats anywhere stats are presented
- Section headings inside `.sp-spread-body` use the `§` section mark automatically (built into the CSS)
- First paragraph of each `.sp-spread-body` gets a 110px italic accent drop cap automatically (built into the CSS) — do not manually wrap the first letter

### Editorial motion layer (tier 5.5) — MANDATORY for loud special editions

The tier-5 body kit gives the magazine its structure. The tier-5.5 motion layer (in `28-special-motion-editorial.css` + matching JS controllers in `assets/script.js`) gives it kinetic life. Inspired by adapted motion vocabulary from landonorris.com (wipe-band reveals, scroll drift, staggered entries) — translated into editorial idiom. **Most of it is automatic** — applied by the JS controllers on scroll. A few patterns require explicit class application.

**Automatic — no markup changes required:**
- `.sp-folio` watermarks drift ±60px on scroll (subtle parallax, via `--sp-folio-y`)
- `.sp-chapter-chrome` opens with a sequenced wipe (numeral → hair → name → slug, staggered)
- `.sp-dash-cell`s stagger in 90ms apart
- `.sp-tl-row`s stagger in down the timeline
- `.sp-hero-quote` lifts in with the corner glyph drifting in opposite direction
- `.sp-brief` slides in with its accent rule scaling vertically from 0
- `.sp-pull-break` corner quote marks scale in from opposite corners
- `.sp-bridger` three columns enter staggered
- `.sp-spread` rail and margin slide in from opposite sides as body fades up
- `.sp-spread-body` first letter (drop cap) pops in with a slight scale
- `.sp-signoff` scale-in finale
- `.sp-caption-strip` hairline rule draws across
- All in-prose `<a>` links get an underline-draw on hover (background-size 0% → 100%)
- Native `scroll-behavior: smooth` on the document
- Ground-seam accent hairline appears between alternating-ground chapters
- Paper-bg components (`.sp-brief`, `.sp-hero-quote`, `.sp-bridger`, `.sp-margin`) automatically lock to ink text colour even when nested in `.sp-ground-ink` chapters (readability lock — no need to add `.sp-island` manually)

**Explicit class application — REQUIRED on loud specials:**
- **`.sp-band`** is THE signature move (the Lando wipe-band reveal). Every chapter chrome's `.sp-eyebrow` and `.sp-chapter-name` MUST carry `.sp-band`. Every `.sp-signoff` label MUST carry `.sp-band`. Every standalone `.sp-eyebrow` kicker above a major component title gets `.sp-band`. The JS auto-wraps the inner text into `.sp-band-t` on the first observation.
- **`.sp-band sp-band-thin`** — lighter underline-sweep variant. Apply to dashboard `.sp-dash-hint` kickers and caption-strip eyebrows where you want the sweep without hiding the text.
- **`.sp-spine`** — decorative inline SVG hairline that draws itself in (`stroke-dashoffset` animation) when scrolled into view. Add 1-2 per long chapter inside the `.sp-margin` column or `.sp-rail` to add typographic depth without weight. Pattern: `<svg class="sp-spine" viewBox="0 0 2 200"><path d="M1 0 V200" /></svg>` (or a curve). Lives decoratively in the margins, never near body text.

**Reduced-motion:** All tier-5.5 motion is wrapped in a `@media (prefers-reduced-motion: reduce)` kill switch — animations collapse to instant, transforms reset, decorative drift disabled. Content-readable state always reachable without motion.

### Signature moments — ONE per format (mandatory)

Each special edition format has exactly one signature moment — a single visual element readers will remember and describe to someone else. They are not interchangeable. Including a Countdown's hourglass in a Versus issue would dilute both. Use the prescribed component for the format and no other.

| Format | Component | Where it lives | Required content hook |
|---|---|---|---|
| Countdown | `.sp-sand-clock` | Cover, below masthead | `data-total="<days>" data-remaining="<days>"` on the wrapper |
| Rewind | `.sp-memory-wall` | Fixed right gutter (desktop), strip above sections (mobile) | One `<div class="mw-cell" data-item-id="…" style="background-image:url(…)">` per item; each prose section gets `data-reveals="id1,id2"` |
| Versus | `.sp-fault-line` | Sticky vertical line spanning all comparison sections | `data-max-shift="90"` on the line; each paragraph in the comparison `<p data-lean="-2"…+2>`; verdict element `data-verdict="a"\|"b"` |
| Season Review | `.sp-form-tape` | Top of the issue + repeated at top of each chapter | Each chapter `<section data-results="W,W,D,L,W" data-result-from="0">…</section>`; tape pre-renders one `.ft-pill` per fixture |
| Deep Dive | `.sp-thread-pull` | Fixed left margin (desktops ≥ 1100px only) | Wrapper element `[data-tp-track]` defines the scroll range; markers `<g class="tp-marker" data-at="0.42">…</g>` inside the SVG carry concept-tag text |
| Starter Kit | `.sp-cold-start` | Cover/opener, gates the prose | One word, split into `<span class="cs-letter">K</span>` per letter. Wrap the rest of the issue in `.sp-cs-after` |
| Shortlist | `.sp-deck-reveal` | Mid-issue picks block | A `.sp-deck` with one `.dk-card` per pick (#1 first / on top); scroll triggers `<div data-deck-step="1">…</div>` peel cards |
| Field Guide | `.sp-pinboard` | Cover/opener (sticky 100vh) | A `.sp-pinboard` with `.pb-stage` background image + `.pb-pin`/`.pb-label` pairs (`--x:38%; --y:52%`); prose sections referring to a pin add `data-pin-id="<id>"` to trigger pulse |

**Authoring rules:**
- Pick the right one for the format. One per issue. Don't mix.
- Always provide the data hook listed above; without it, the component renders inert (which is the safe fallback).
- All nine moments degrade gracefully under `prefers-reduced-motion` and on missing JS.
- **Mobile gating:** `sp-thread-pull` hides below 1100px; `sp-memory-wall` collapses to a horizontal strip below 900px; everything else adapts.
- **No content sacrificed.** If the moment doesn't fit the issue's content shape (e.g. a Versus issue with no clear A/B paragraphs), skip the moment rather than force the structure.

### Chapter transitions + ambient (format-agnostic)

These components compose with the existing `.sp-wipe`, `.sp-curtain`, ground alternation, and chrome — they are punctuation, not replacements. Available to every special edition format.

**Transitions (use sparingly — these create a deliberate reading pause):**

- **`.sp-stat-curtain`** — full-viewport overlay rises with one hero stat or epigraph, then retracts. Use at **most twice per issue** at moments where a hard pause is editorially earned (chapter break before the centrepiece, before the verdict). Markup: `<div class="sp-stat-curtain" id="sc-1"><p class="scu-stat">23,400</p><p class="scu-caption">Roller-coaster runs in 2025</p></div>` plus a trigger `<div data-curtain-for="sc-1"></div>` placed at the chapter end where it should fire.
- **`.sp-page-fold`** — bottom 40vh folds upward via 3D rotateX. Use **only at paper↔ink chapter handoffs** to dramatise the ground swap. Markup: wrap the boundary in `<div class="sp-page-fold-wrap"><div class="sp-page-fold" style="--sp-ground-prev: var(--sp-paper);"></div><div class="sp-page-fold-shadow"></div></div>`. Set `--sp-ground-prev` to the outgoing chapter's ground colour token. Maximum 2 per issue.

**Ambient (these run continuously and become part of the issue's atmosphere):**

- **`.sp-chapter-beads`** — fixed right-gutter bead strip, one per chapter, with within-chapter progress connector. **Universal: works on standard weekly AND every special edition.** Markup: a single `<aside class="sp-chapter-beads" aria-hidden="true"></aside>` near the end of `<body>` (already included in `template-parts/19-closing.html`). **Chapter discovery order:** (1) elements with `[data-sp-chapter]` — typical for specials; (2) fallback to `.mag > section.sec` — used by every standard-weekly section. **Title resolution:** `[data-sp-chapter-title]` → first `<h2>` text → section `id` (title-cased) → `Chapter N`. Accent colour auto-cascades: `--sp-accent` on specials, `--accent` on standards. **Mobile (≤ 820px):** collapses to a thin vertical line with no labels. Click a bead to scroll to that chapter.
- **`.sp-horizon`** — bottom-edge strip bleeds the next chapter's ground colour upward as within-chapter progress nears 100%. Markup: a single `<div class="sp-horizon" aria-hidden="true"></div>` near the end of `<body>`. Each chapter element must carry `data-sp-chapter` AND `data-sp-ground-color="#hex"` so the next chapter's colour is known.

**Authoring contract for ambient:**
- Both ambient components share the same per-chapter progress calculation (one rAF loop, zero duplicated work). Adding `.sp-horizon` for free if you've already added `.sp-chapter-beads`.
- Both require chapters to be marked with `data-sp-chapter` on the section root and `data-sp-chapter-title` for tooltips (specials). **Standard editions need no mark-up** — beads auto-discover from `<section class="sec">`. `data-sp-ground-color` is required only if you use `.sp-horizon` (special editions only).
- Reduced-motion: beads stay (active state only, no fill animation); horizon collapses to a static 2vh strip near chapter end.

### Chapter gate (MANDATORY for every chapter on every special edition — v8.5, sticky scroll model)

**The chapter gate is the single most important element in a special edition.** It is the digital equivalent of turning a page in a real magazine — a viewport-locking moment that unambiguously says *"a new chapter starts here"*. It is the permanent, unmissable signal the reader can spot at any scroll speed.

**Mandatory on:** every `[data-sp-chapter]` in every special edition. If a chapter does not open with `.sp-chapter-gate`, the issue fails Gate 2.

**Structure:**
```
<aside class="sp-chapter-gate"
       data-chapter-num="V"
       data-chapter-title="BEEKSE BERGEN"
       data-chapter-arc="Act III — the wild">
  <p class="scg-deck">Five days inside Europe's largest safari park, and a hotel where the lions wake you up.</p>
</aside>
```
Place the gate **immediately before** the chapter section's opening `<section data-sp-chapter="…">` tag. The controller auto-builds the black panel and drives the scroll-progress reveal.

**How it behaves (v8.5 sticky scroll model):**
- The gate is a 160vh scroll track containing a `position: sticky` full-bleed black panel (`#0A0E17`) that locks to the viewport for ~1 screen-height of scroll.
- As the reader scrolls *through* the gate, a `--scg-progress` CSS variable runs 0 → 1. The four text layers are revealed in sequence:
  - **0.10 → 0.30** arc label fades in
  - **0.25 → 0.55** Roman numeral scales + fades in (coral)
  - **0.45 → 0.70** chapter title fades in (reserved typeface)
  - **0.65 → 0.88** deck line fades in (italic, on the black)
- When scroll passes the end of the track, the panel unsticks and the next chapter is revealed underneath.
- **No cream "breath" zones before or after.** The previous chapter butts straight up against the black cover; the next chapter appears straight out of it. The pause is *time* (scroll-hold), not *whitespace*.
- **Reduced-motion / no-JS fallback:** panel collapses to a static full-bleed black band (~52vh) with all four text layers fully visible. No sticky, no progress driver. Same visual anchor, no motion.

**Four text layers, all live inside the black panel (v8.5):**
1. **Arc label** — italic, small, muted bone (e.g. "Act III — the wild")
2. **Roman numeral** — display size (72–180px), coral, reserved typeface
3. **Chapter title** — medium, letter-spaced caps, bone, reserved typeface
4. **Deck line** — italic, dim bone, one sentence (mandatory)

**Three elements reserved exclusively for the gate (never used elsewhere):**
1. The **full-bleed black panel** (`.scg-strip`). If you see one, it means "new chapter". Nothing else in the magazine uses this.
2. The **chapter-title typeface** (`var(--sp-chapter-ff)` — Space Grotesk). Banned from pull-quotes, kickers, stats, sidebars, covers, navigators.
3. **Display-size Roman numerals** (72–180px). The wax seal's small ornamental numeral is the only other Roman numeral permitted.

**Required attributes:**
- `data-chapter-num` — Roman numeral (I, II, III…). Required.
- `data-chapter-title` — chapter name in CAPS (e.g. `BEEKSE BERGEN`). Required.
- `data-chapter-arc` — the narrative-arc label. Required on Countdown, Deep Dive, Rewind, Season Review, Next. Optional on Versus / Starter Kit / Shortlist / Lookahead / Field Guide.
- `<p class="scg-deck">…</p>` — **mandatory one-line deck**. A sentence that tells the reader *what this chapter will do for them*. Not a subtitle, not a description — a promise. See deck-writing rules below.

**The deck line — what makes it good:**
- One sentence. Italic. Max ~20 words.
- Answers: *"why should I read this chapter?"* not *"what is this chapter?"*
- Concrete, not abstract. "Five days inside Europe's largest safari park" > "An overview of our stay".
- Never restates the chapter title.

**Examples (good):**
- *By the Numbers* → "The trip in eleven figures — before the prose starts."
- *Logistics* → "Everything you need to stop thinking about once you land."
- *Facts & Folklore* → "The stories the locals tell, and the ones the guidebooks don't."
- *Wonder Hotel* → "Sleeping inside the fairy tale — what two nights in room 312 is really like."
- *Mood Board* → "Five images that tell you what a week here actually looks like."

**Narrative-arc labels (required on long-form specials):**
- **Countdown** (typically 9–11 chapters): Act I (hype setup — By the Numbers, Event in Depth) → Act II (centrepiece hype — Top Attractions, Accommodation, Mood Board) → Act III (softer hype — What to Watch/Read/Play, Five Moments Worth the Trip) → Coda (Before You Go: compressed logistics + surprising facts + On the Radar)
- **Deep Dive** (8–10 chapters): Premise → Evidence I → Evidence II → Counterargument → Verdict
- **Rewind** (chronological): Year-by-year or phase-by-phase labels
- **Season Review**: Opening Acts → Mid-Season → Finale → Verdict
Map every chapter to its arc beat and put the label in `data-chapter-arc`. This is how the reader keeps orientation through ten chapters.

### Ground discipline (v8.4 — hard rule)

**The chapter owns the ground. Components inside a chapter inherit it.**

- `sp-ground-paper` and `sp-ground-ink` belong on `[data-sp-chapter]` wrappers only.
- **No pull-quote, brief box, sidebar, stat panel, or island component may flip to the opposite ground inside its chapter.** A pull-quote inside an ink chapter lives on ink. A brief inside a paper chapter lives on paper. Previously, components painted their own cream/ink backgrounds, fragmenting the chapter into a patchwork of boxes that hid the actual chapter-break. This is now banned.
- **Emphasis comes from weight, hairlines, and typography** — not colour inversion. A brief reads as a brief because of its left rule and its kicker, not because its background colour differs from the prose around it.
- **Enforced in CSS**: `31-chapter-gate.css` neutralises `sp-ground-paper`/`sp-ground-ink` on every common component class when nested inside `[data-sp-chapter]`. The only full-bleed component still allowed to paint its own ground is `.sp-pull-break`.
- **Force ground alternation across the issue.** Adjacent chapters must not share a ground. If the running order would produce paper→paper or ink→ink neighbours, either reorder the chapters or flip one. Same-ground neighbours make the chapter break invisible even with a gate.
- **Readability Lock Principle (v8.10.3).** Any component that paints its own background MUST also lock its own text colour in the same rule. The chapter ground cascades a `color` value into every nested element; if a self-painting component (cream card, dark band, tinted sidebar) leaves text colour to inherit, the cascade lands bone-text on a cream card or ink-text on a near-black band. Components covered by the v8.10.3 lock layer (`34-readability-locks.css`): `.sp-marginalia` is always cream-bg + ink-text; `.sp-pull-break` is always dark-bg + bone-text; `.sp-pullquote-huge` paints text colour explicitly per chapter ground. Any new self-painting component you add to the kit MUST update this layer in the same commit. Every newly-introduced component goes through the question: "Does this paint its own background? If yes, does it also lock its own text colour?" If the answer to the second question is no, the component is broken and must not ship.

### Markup contracts (v8.10.3 — hard rule)

The special-edition CSS targets specific tag + class combinations. When a generator invents an alternative — `<div>` instead of `<blockquote>`, an unfamiliar class on a child element — the styling rule misses, the readability lock misses with it, and the component renders without its identity. Subagent-invented markup has been the single largest source of contrast bugs across v8.x. The contract below is closed: anything outside the canonical column is banned, full stop.

| Component | Canonical markup | BANNED alternates |
|---|---|---|
| Marginalia | `<aside class="sp-marginalia" data-side="right"><span class="sp-marginalia-label">…</span><p>…</p></aside>` | `<div class="sp-marginalia">…</div>`; any child `<p class="sp-marg-kicker">` (must be `<span class="sp-marginalia-label">`); any child `<p class="sp-marg-label">`; nesting a marginalia inside another marginalia |
| Pullquote (huge) | `<blockquote class="sp-pullquote-huge"><p>…</p><cite>…</cite></blockquote>` | `<div class="sp-pullquote-huge">`; child `<p class="sp-pq-quote">` (must be plain `<p>`); child `<p class="sp-pq-attrib">` or `<span class="sp-pq-attrib">` (must be `<cite>`); `<blockquote>` without `class="sp-pullquote-huge"` outside an `<aside>` |
| Pull-break | `<div class="sp-pull-break-wrap sp-ground-deep"><div class="sp-pull-break"><p class="sp-pull">…</p><p class="sp-pull-attrib">…</p></div></div>` | `<blockquote class="sp-pull-break">`; nesting `.sp-pull-break` directly inside a chapter section without the `.sp-pull-break-wrap`; `.sp-pull` rendered as `<h2>` or `<h3>` instead of `<p class="sp-pull">`; missing `.sp-pull-attrib` (every pull-break must be attributed) |
| Pullquote attribution (inside huge pullquote) | `<cite>— Source name</cite>` | `<p class="sp-pq-attrib">`; `<span class="sp-pq-attrib">`; `<footer>`; bare `<em>` |
| Brief sidebar | `<div class="sp-brief"><p class="sp-brief-kicker">…</p><h4 class="sp-brief-h">…</h4><p>…</p><p class="sp-brief-byline">…</p></div>` | `<aside class="sp-brief">`; missing `.sp-brief-kicker`; `<h3>` or `<h2>` for the heading (must be `<h4>`) |
| Hero quote | `<div class="sp-hero-quote"><p class="sp-hero-quote-q">…</p><p class="sp-hero-quote-at">…</p></div>` | `<blockquote class="sp-hero-quote">`; child `<cite>` (must be `<p class="sp-hero-quote-at">` for the typography rule to land) |
| Chapter chrome | `<div class="sp-chapter-chrome"><span class="sp-roman">III</span><span class="sp-hair"></span><span class="sp-chapter-name">…</span><span class="sp-chapter-slug">…</span></div>` | `<header class="sp-chapter-chrome">`; missing `.sp-hair` (the hairline rule between numeral and name); `.sp-chapter-name` rendered as `<h2>` or `<h3>` |

**Why this is hard rule, not best practice.** Each row in this table corresponds to a CSS selector that targets the canonical structure precisely. The styling does not fall back gracefully if you swap `<div>` for `<blockquote>` or `<p>` for `<span>`: the readability lock misses, the chapter ground cascades through, and you get a contrast bug or worse, a component that looks fine on paper grounds and breaks on ink (or vice versa). The contract is enforced by Gate 1E (mechanical grep scan) — every banned alternate must return zero matches before an issue ships.

**For new components.** Adding a new editorial component to the kit means updating three places in the same commit: (1) the CSS, (2) this table, (3) the Gate 1E grep recipe in `compliance-checklist.md`. A component without a contract entry cannot ship.

### Accent lockdown (v8.4 — hard rule)

Coral (`--sp-accent-primary`, `#E8384F`) is now reserved for three things and three things only:
1. The Roman numeral inside `.sp-chapter-gate`
2. The Countdown D-day badge
3. The page progress bar

Everywhere coral was previously used (masthead accent underline, datum values, `sp-number` count-ups, kickers, pull-break corner quotes, brief accent rules, `sp-dash-cell strong`, spread-body `h2`, eyebrow, etc.) is demoted to a **secondary accent** scoped by chapter ground:
- Inside paper chapters → `--sp-accent-secondary` (muted slate, `#64697B`)
- Inside ink chapters → `--sp-accent-secondary-ink` (bone, `#C9C2B5`)

This means: when a reader flicks past a block of coral, it can only mean "new chapter" (or "days remaining" / progress chrome). They stop trusting coral as decoration.

### Stat budget (v8.4 — hard cap per issue)

Too many stat blocks flatten into noise. Hard cap for every special edition:

| Block type | Max per issue |
|---|---|
| `sp-stat-curtain` (full-viewport, hero) | **1** |
| `sp-dash` (dashboard grid) | **1** |
| `sp-number` / `sp-number-huge` (inline count-ups) | **6 combined** |
| `sp-datum` (marginalia stat) | **4** |
| **TOTAL stat-heavy blocks** | **≤ 12** |

If a draft exceeds the cap, cut the weakest blocks. Rule of thumb: any stat that appears more than once across the issue (same number in curtain + count-up + datum) loses all punch — keep the version with the most editorial weight, cut the others. Prose should carry most of the numbers; stat blocks are reserved for the handful that genuinely deserve a pause.

### Held-attention moment (format-agnostic)

- **`.sp-sticky-pin`** — a single image or pull-quote that pins to the side of the column for ~1.5 viewports of scroll while the prose continues past, then releases. A thin accent rule on the card grows as a within-section progress indicator. Use for a character portrait during an interview (watches the reader), or a pull-quote that lingers while the argument unfolds around it. Variants: `sp-sticky-pin--portrait` (image, default right-float), `sp-sticky-pin--quote` (left-border pull quote), `sp-sticky-pin--left` (flip to left margin). Markup:
  ```
  <aside class="sp-sticky-pin sp-sticky-pin--portrait">
    <div class="spin-inner">
      <img src="…" alt="…">
      <figcaption class="spin-cap">…</figcaption>
      <div class="spin-rule" aria-hidden="true"></div>
    </div>
  </aside>
  ```
  **Rules (enforced):**
  1. **Max one per issue.** If multiple `.sp-sticky-pin` elements exist, JS keeps the first and demotes the rest to inline figures.
  2. **Never** in a section that already uses `.sp-parallax` or `.sp-scroll-image` — they solve overlapping problems.
  3. Only inside a host section with **≥ 150vh of prose** — otherwise the stick is imperceptible.
  4. **Mobile (≤ 820px):** collapses to a normal inline figure; no stick (sticky on tablet causes vertigo).
  5. Best uses: a single character portrait during an interview, or a pull-quote that watches over an unfolding argument. Never a decorative stock photo.

### Issue accent
Each format maps to a palette variable. **Non-holiday formats (v8.21 system, see `assets/css/32-special-format-flair.css`):** deep-dive → ember, starter-kit → bone-soft, versus → rose + ember (two-side), rewind → rose, season-review → deep, shortlist → rose, next → rose + ember, lookahead → rose. **Holiday formats retain their legacy `--issue-accent` mapping:** countdown → rose, field-guide → itinerary-accent.

### Chrome positioning ground rules
Fixed chrome elements must not overlap. Current occupation:
- Masthead: `top: 0` full-width, `z-index: 50`
- Wax-stamp seal: `top: 76px; right: 28px; z-index: 45`
- Format badge (special): `top: 76px; right: 28px` range — rotated, lower z-index
- D-day badge (countdown): `top: 88px; left: 18px; z-index: 46` — kept on the LEFT to avoid seal collision
- Back-to-top: `bottom: 28px; right: 28px`
- Chapter beads (ambient): `right: 14px; top: 50%` — collapses to `right: 6px` and thin line on tablet/mobile
- Memory wall (Rewind only): `top: 84px; right: 18px` — collapses to a horizontal section-header strip below 900px
- Horizon (ambient): `bottom: 0` full-width, height driven by within-chapter progress, `z-index: 2`
- Stat curtain (transition, transient): `inset: 0` full-viewport, `z-index: 30`, only visible while rising/retracting
- Sticky pin (held attention, inline): `position: sticky; top: masthead + 24px; z-index: 3` — flows with column, never fixed to viewport edge
If adding a new fixed element, claim a free corner or offset vertically from the masthead.

---

### Visual features — auto-apply guarantee (v8.7.3)

Every visual feature hardened between v8.0 and v8.7 fires automatically on every future special edition once you've done the three structural things listed in §Authoring a special edition. This table is the canonical answer to *"will X show up on the next Countdown/Deep Dive/Versus without me having to ask?"*.

| Feature | How it fires | What you must author |
|---|---|---|
| Splash pre-roll | CSS + JS auto-inject | Nothing — rendered if `<body class="is-special">` |
| Masthead ticker | CSS + JS auto | Nothing |
| Format badge (◆ rotated) | CSS auto from `[data-special]` | Nothing |
| D-day badge (Countdown) | CSS + JS auto | `data-dday-start="N"` on `<body>` |
| Alternating paper/ink grounds | CSS auto from `sp-ground-paper` / `sp-ground-ink` | One class per chapter wrapper |
| Full-bleed ground gutter (tablet/phone) | CSS @media auto | Nothing — enforced by `26-special-editorial.css` |
| Chapter chrome (roman + hair + name + slug) | CSS auto; reveals staggered | Markup once per chapter |
| Chapter gate (sticky black panel, 4-layer reveal) | CSS + JS auto (sticky scroll + rAF progress loop) | `<aside class="sp-chapter-gate" data-chapter-num data-chapter-title data-chapter-arc>` + `.scg-deck` line |
| Giant folio watermark | CSS auto; parallax on scroll via `--sp-folio-y` | `.sp-folio` div inside chapter |
| 3-column spread (rail + body + margin) | CSS auto; rail stretches full spread via `position: absolute` (v8.7.2); margin floats right, reclaims prose width when its content ends (v8.7.1) | `.sp-spread > .sp-rail + .sp-spread-body + .sp-margin` markup — reparenter IIFE handles mobile portrait |
| Drop cap (110px italic accent) | CSS auto on `.sp-spread-body > p:first-of-type` | Nothing — don't wrap the first letter manually |
| § section mark on inner headings | CSS `::before` auto | Nothing |
| Paper/ink text-colour lock on islands | CSS auto on `.sp-brief`, `.sp-hero-quote`, `.sp-bridger`, `.sp-margin` | Nothing — islands always read correctly against any ground |
| Ink-ground margin = paper-tinted card (v8.7.2) | CSS auto on `.sp-ground-ink .sp-margin` | Nothing |
| `.sp-band` wipe-reveal on kickers + chapter names + signoffs | JS auto-wraps inner text into `.sp-band-t` | Apply `.sp-band` class where required |
| Count-up stats (`.sp-number`, `.sp-bignum`, `.sp-datum-n`) | JS IntersectionObserver auto | `data-to="<N>"` on the element |
| Chapter beads (right-gutter ambient) | JS auto-discovers `[data-sp-chapter]` | One `<aside class="sp-chapter-beads">` in `<body>` |
| Horizon (next-ground bleed ambient) | JS auto-reads `data-sp-ground-color` | One `<div class="sp-horizon">` in `<body>` + `data-sp-ground-color` on each chapter |
| Stat curtain (transition) | CSS + JS auto-fires from trigger | `.sp-stat-curtain` + `data-curtain-for="id"` trigger — max 2 per issue |
| Page fold (3D transition at ground swap) | CSS auto | `.sp-page-fold-wrap` between chapters — max 2 per issue |
| Signature moment (per-format) | CSS + JS auto from `[data-special]` | Format-specific markup from the signature-moment table |
| Wax seal + progress bar + back-to-top | CSS + JS auto | Nothing |
| Full-viewport cover (v8.7.3) | CSS auto via `min-height: 100dvh` | Nothing — works on tablet and phone |
| Accent lockdown (coral reserved for gate/D-day/progress only) | CSS auto via token cascade | Nothing — demoted secondary accent fills everywhere else |
| Imagery/stat budget enforcement | Author-side checklist | Gate 2 of compliance checklist; not enforced in code |

**What this means for future issues:** when a Countdown / Versus / Rewind / Deep Dive / etc. is generated in four weeks' time, the author does not need to re-request any of the above. They fire automatically provided (1) `<body class="mag-body is-special" data-special="...">`, (2) every chapter wrapper carries `data-sp-chapter` + alternating `sp-ground-paper` / `sp-ground-ink`, and (3) every chapter is preceded by a `.sp-chapter-gate`. Anything requiring author markup is a class contract, not a CSS request — it's documented in the Feature column with the minimum markup.

**What is NOT auto-applied and requires editorial judgement each time:** imagery density (budget is a minimum, not a ceiling), accommodation-chapter depth, word counts per chapter, the choice of signature moment for the format, placement of `.sp-pull-break` / `.sp-bridger` / `.sp-dash` interludes, and the editorial arc labels (`data-chapter-arc`). These are content decisions the editor makes during generation, not mechanical features.

---

## What Good Looks Like

- Scannable in 60 seconds via navigator; rewards 30-45 minutes of deep reading
- Feels like a thoughtful human editor, not an AI summary bot
- Varies in tone across sections while feeling like one publication
- Connects stories the reader wouldn't have linked themselves
- **Visually varied** — split layouts, big numbers, pull quotes, card stacks, timelines, margin notes, collapsible sections throughout
- **Has visual moments** — 3-4 points where the reader pauses because something looks interesting
- **Animates subtly** — reveal on scroll, count-up numbers, ambient cover gradient
- Includes 2-3 things the reader didn't know they wanted to read about

---

## Holiday Identity (v8.12 — Countdown and Field Guide only)

The Countdown and Field Guide formats use a **separate visual identity** from every other special edition. Where Deep Dive, Rewind, Versus, Season Review, Starter Kit, Shortlist, Next, and Lookahead all share the v8.21 editorial chrome (paper-and-ink grounds, persistent `.mast` bar, restrained editorial register), Countdown and Field Guide do not. The default chrome reads as "serious magazine"; holiday issues need to read as "trip scrapbook, building excitement."

**CSS layer:** `36-holiday-identity.css` (Tier 11). Loads only when `body.is-special[data-special="countdown"]` or `body.is-special[data-special="field-guide"]` is set. On every other format the file is dormant.

**What the layer changes vs default chrome:**

1. **No sticky chapter gate.** The 110vh black chapter-gate scroll-track is hidden on holiday issues. Structural rhythm is instead carried by two **halves** and one **transit intermission** between them (`.hol-transit`). Multi-venue trips get the full two-half treatment; single-venue Field Guides run as one half with a softer interior break (a tilted `.hol-marquee` between sections, not a full transit).
2. **No coral accent lockdown.** The default chrome restricts coral to chapter-gate numeral, D-day badge, and progress bar. Holiday issues do not use coral at all. The issue's identity accent is **brass** (`--hol-brass` / `--hol-brass-light`); ruby, rose, emerald, mustard, terracotta all run freely throughout.
3. **No ground discipline.** The default chrome neutralises component-level grounds inside chapters. Holiday issues encourage per-block grounds — a rotated polaroid on a brass card on a celestial-themed section.
4. **Type personality swap.** Default chrome uses Space Grotesk for chapter titles. Holiday issues use six type stacks simultaneously: Bowlby One (display-chunk), Cinzel italic (serif-display), Yellowtail (script-ornate), Caveat (script-note), Anton (display-tall), Alfa Slab One (display-slab). DM Sans body and Space Mono kicker are shared with default chrome. Each face does a specific job — see Type roles below.
5. **Ambient layer swap.** Default chrome ambient: chapter beads, sticky pin, page-fold, horizon. Holiday ambient: drifting clouds in dark heroes, kinetic marquees as section transitions, savannah silhouettes along Half II's bottom edge, optional fairytale tree silhouettes on celestial halves, star field across Half I.

**Structural beats (in order):**

1. `.hol-masthead` — narrow brand strip with format badge and T-minus meta. Replaces default masthead for holiday issues.
2. `.hol-cover` — full-bleed indigo poster with star field, drifting clouds, mega-numeral watermark, chunky title with mixed type, optional `.hol-countdown` live grid on the left, optional scrapbook collage on the right.
3. `.hol-kicker-strip` — cream-paper promise of the issue with double rule, chunky title + script subtitle on the left, mono meta on the right.
4. `.hol-half--one` — Half I body (Efteling default register: indigo + celestial backdrop + brass/rose/cream accents). Contains: stacked opener, content blocks (anchor, unmissable rows, marquee, don't-miss, polaroids, postcards), and closes seamlessly into the transit.
5. `.hol-transit` — the **only** structural break in the issue. Full-bleed 280px black band with mega kinetic typography watermarking each side and the divider card pinned centre. Single-venue issues omit this and replace it with a softer in-half break (`.hol-marquee` between sections).
6. `.hol-half--two` — Half II body (Beekse Bergen default register: terracotta + savannah silhouettes + mustard/bone/burnt accents). Same content blocks, completely different palette.
7. `.hol-meanwhile` — closing dark block with mega "MEANWHILE" / "SIGNAL" / "T-MINUS" watermark, brass title in chunky display, italic serif body. Adjacent rotated `.hol-subscribe` card.
8. `.hol-footer-row` — brand mark + mono links + hand-script tagline. Closes the issue.

**Type roles:**

| Face | Role | Examples |
|---|---|---|
| Bowlby One (`--hol-t-chunk`) | Mega display titles, big numbers, marquee text | Cover title, half titles in Half II, marquee bars, mega watermarks |
| Cinzel italic (`--hol-t-serif`) | Half I serif titles, italic pull-quotes, dek text | Half I opener title, anchor titles, unmissable titles |
| Yellowtail (`--hol-t-script`) | "Part One:" / "Don't Miss" / overline tags, hand-arrow notes | Cover overline, opener tags, transit hand-script, don't-miss kicker |
| Caveat (`--hol-t-hand`) | Polaroid captions, postcard backs, tagline endings, sticker text | Every handwritten caption in the issue |
| Anton (`--hol-t-tall`) | Tall display, transit names, postcard place labels, chalkboard items | "EFTELING" / "SAFARI" mega-watermark in transit |
| Alfa Slab One (`--hol-t-slab`) | Stamp inner text, big slab numerals where chunky is too round | Inside `.hol-stamp` b text |
| DM Sans (`--hol-t-body`) | All body copy | Same as default |
| Space Mono (`--hol-t-mono`) | Kickers, meta, ALL CAPS labels, stamps outer ring text | Mast meta, kicker-strip meta, stamp text, unmissable facts dt |

**Component vocabulary (full list, all prefixed `.hol-`):**

| Class | Role |
|---|---|
| `.hol-masthead` (`__title`, `__badge`, `__meta`) | Page-top brand strip |
| `.hol-cover` (`__inner`, `__sig`, `__overline`, `__title`, `__dek`, `__layout`, `__collage`, `__cloud`, `__back-num`, `__back-script`) | Full-bleed cover poster |
| `.hol-countdown` (`__grid`, `__cell`, `__num`, `__unit`, `__target`) | Live countdown digit grid. JS controller binds to `[data-cd]` cells; wrapper carries `data-target` ISO string |
| `.hol-kicker-strip` (`__inner`, `__title`, `__sub`, `__meta`) | Promise strip between cover and Half I |
| `.hol-half` + `.hol-half--one` / `--two` (`__inner`, `__opener`, `__opener-tag`, `__opener-title`, `__opener-subtitle`, `__opener-pills`) | Half section wrapper + stacked opener |
| `.hol-half--fairytale` | Optional ambient variant — Anton-Pieck tree silhouettes along the bottom of Half I |
| `.hol-transit` (`__side`, `__side--left`, `__side--right`, `__mega-bg`, `__label`, `__hand`, `__name`, `__center`, `__center-card`) | The single structural break between halves |
| `.hol-polaroid` (`__photo`, `__caption`, `__tape`) + `--right` / `--flat` | Rotated photo card with washi tape |
| `.hol-postcard` (`__front`, `__back`, `__greeting`, `__place`) | Greeting front + handwritten lined back |
| `.hol-stamp` + `--brass` / `--emerald` / `--mustard` | Circular rubber-stamp seal |
| `.hol-anchor` (`__photo`, `__title`, `__dek`, `__meta`, `__badge`, `__note`) | Feature article block with tilted border, rotated badge, hand-script note |
| `.hol-unmissable` + `--reverse` (`__photo-wrap`, `__photo`, `__card`, `__num-row`, `__num`, `__title`, `__quote`, `__why`, `__facts`) | Alternating left/right photo + parchment row. Use 6–10 per Field Guide; 5–7 per Countdown Top Attractions |
| `.hol-dont-miss` (`__kicker`, `__title`, `__list`) | Rotated ruby block with tilted shadow numerals |
| `.hol-marquee` (`__track`) | Kinetic horizontal scroll banner. Reduced-motion safe |
| `.hol-chalkboard` (`__tag`, `__title`, `__items`, `__row`, `__item`, `__price`, `__note`) | Half II tilted chalkboard menu card |
| `.hol-meanwhile` (`__giant-bg`, `__inner`, `__title`, `__body`) | Closing dark block |
| `.hol-subscribe` (`__inner`, `__title`, `__form`, `__input`, `__btn`, `__hand`) | Rotated subscribe card |
| `.hol-footer-row` (`__brand`, `__links`, `__tagline`) | Page-bottom brand mark + links + tagline |

**Activation:**
```html
<!-- Countdown -->
<body class="is-special" data-special="countdown">

<!-- Field Guide -->
<body class="is-special" data-special="field-guide">
```

No additional class is needed on the body. The default chrome's `body.is-special` activation still fires; tier 36's selectors disable the parts of default chrome that conflict and install the holiday vocabulary on top.

**Single-venue vs multi-venue:**
- **Multi-venue trip:** use both `.hol-half--one` and `.hol-half--two`, separated by one `.hol-transit`. The transit is the entire chapter-rhythm system for the issue. Half I covers the first venue; Half II covers the second.
- **Single-venue trip:** use only `.hol-half--one`. Replace the transit with one or two interior `.hol-marquee` breaks placed between major content groups (e.g. after Top Attractions, after Mood Board). The marquee functions as the softer in-half rhythm beat.

**What does NOT change vs the existing Countdown / Field Guide editorial specs:**

The editorial rules for Countdown and Field Guide (canonical chapter order, no-taste rule, hype-over-homework, 45/55 hype-to-practical, reader-profile invisibility, source diversity, image source rules, multi-venue balance check, access constraints, locked release-date register) all remain in force exactly as written. This layer is purely visual identity — content rules are unchanged.

**Compatibility with multi-venue theming (Tier 9, `33-countdown-destinations.css`):**

Tier 9 multi-venue theming and tier 11 holiday identity are independent. If a Countdown uses both:
- Tier 9 provides per-venue palette tokens (Efteling cream + plum + antique gold; Beekse warm sand + dark earth + terracotta) and the decorative venue glyph in the bottom-right corner.
- Tier 11 provides the cover, transit, half opener, ephemera vocabulary, and the type system.

The two layers compose cleanly: tier 9's venue palette can be used for the half ground, tier 11's component vocabulary for everything inside it. If a conflict arises (e.g. tier 9 sets a paper ground but tier 11 wants the indigo half-one register), the holiday half-register wins because tier 11 loads later in the cascade.

**Reduced-motion safety:**

Every animation in tier 36 (drift, marquee, flip-pop, hover-unrotate) is gated behind a `prefers-reduced-motion: reduce` override at the bottom of the file. Reduced-motion users see the same layouts with no motion.

---

### v8.13 — visual richness upgrade (May 2026)

v8.13 replaces three weak spots in the original Holiday Identity layer with the proven recipes from `signal-holiday.css`. Every change is **additive** unless explicitly noted — the v8.12 vocabulary continues to work, and existing planners that emit the old class names still produce valid output. The new components are opt-in extensions plus one breaking change to `.hol-half--two`'s ambient layer.

**1. Half II is now savannah cartography, not flat orange (BREAKING for `.hol-half--two`).**

The original `.hol-half--two` painted a flat terracotta ground with a mustard radial-dot grid and a small SVG silhouette band at the bottom. v8.13 replaces all three:

- **Ground:** gradient from `--hol-sand` (#ede1c8) at the top through `--hol-bone` (#f5ecd6) to a khaki dust tone at the bottom. Body text colour becomes `--hol-savannah-ink` (#1c2613) for legibility on the now-lighter ground.
- **Sun layer (`::before`):** conic sun-rays from the upper-right (`92% 8%`) plus a radial brass-orange sun disc. Reads as the savannah morning sun.
- **Silhouette band (`::after`):** the proven SVG band from `signal-holiday.css` — three giraffes at varying heights, three acacia trees, an elephant in mid-section, two grass tufts, and small bird scribbles. Tiled across the bottom 240px.

All Half II component overrides (anchor, opener, etc.) are repainted to work on the new light ground: bone-on-terracotta becomes savannah-ink-on-cream-sand, with burnt as the primary accent and mustard as the secondary. Writers and planners should **never** set `background:` on the `.hol-half--two` wrapper or on a chapter inside it.

**2. Optional atmospheric theme layers.**

Five new utility classes, each a single CSS pseudo-element with a tiled SVG. Stack ON TOP of a half (or any positioned section) for extra atmosphere on selected chapters. Each is static and repeating — paint cost is amortised by the browser image cache; identical across one page or thirty of scroll.

| Class | When to use | What it adds |
|---|---|---|
| `.theme-celestial` | Feature Half I chapters (the Top Wonders chapter, the Anchor chapter) | Richer starfield with constellation lines connecting stars + four-point sparkle stars |
| `.theme-fairytale` | Half I storybook chapters | Anton-Pieck silhouette band of gnarled trees along the bottom 220px with brass lantern dots |
| `.theme-flourish` | Half I chapter openers | Anton-Pieck brass filigree corner brackets (top-left + mirrored top-right) |
| `.theme-airships` | Half I Wonder Hotel / accommodation chapters | Line-drawn hot-air balloons drifting across the section |
| `.theme-tracks` | Half II safari chapters | Low-opacity terracotta paw/hoof print watermark across the section |
| `.theme-heat-haze` | Half II — ONE chapter per issue maximum | Subtle blurred shimmer ribbon at 32% height, 4s ease-in-out infinite alternate. The single moment of animation in Half II. |

Legacy alias: `.hol-half--fairytale` continues to work and produces the same tree-silhouette band. New writers should prefer `.theme-fairytale` (more composable).

**3. `.hol-wonders` editorial pattern (NEW component).**

A chapter-level component for ranked editorial picks (Field Guide Unmissables, Countdown Top Attractions). Each row is a rotated hero image with thick white border paired beside a parchment card carrying a numbered chip, serif italic pull-quote lede, and a tight Where/Why meta strip. Rows alternate sides via `.hol-wonder--reverse`. The component is designed to sit ON TOP of the indigo + starfield + storybook ground of `.hol-half--one` — the dark backdrop reads through between rows, making the parchment cards feel like illustrated plates pasted onto the night sky. The hover-unrotate on the photo is the only motion.

This sits alongside `.hol-unmissable` rather than replacing it. The two patterns serve different shapes: `.hol-unmissable` is the magazine-feature row with a long card, full quote attribution, and a four-row practical footer; `.hol-wonders` is the tighter editorial-list row with the numbered chip and a two-row Where/Why meta. Use `.hol-wonders` when the chapter is **ranked culinary or attraction wonders**; use `.hol-unmissable` when the chapter is the full Field Guide Unmissables pattern.

```html
<section class="hol-half hol-half--one theme-celestial theme-fairytale">
  <div class="hol-half__inner">
    <div class="hol-wonders">
      <div class="hol-wonders__intro">
        <h2>Top Ten Culinary Wonders</h2>
        <p>The unmissable flavours of Efteling</p>
      </div>
      <div class="hol-wonder">
        <div class="hol-wonder__photo" style="background-image:url('...');"></div>
        <div class="hol-wonder__card">
          <div class="hol-wonder__head">
            <span class="hol-wonder__num">01</span>
            <h3 class="hol-wonder__title">Pancakes at Polles Keuken</h3>
          </div>
          <p class="hol-wonder__quote">"Twelve little ones, butter, sugar — worth the queue every time." — r/Efteling</p>
          <dl class="hol-wonder__meta">
            <dt>Where</dt><dd>Polles Keuken, Fairytale Forest</dd>
            <dt>Why</dt><dd>Source convergence across Reddit, blogs, and TripAdvisor on the pancakes specifically.</dd>
          </dl>
        </div>
      </div>
      <div class="hol-wonder hol-wonder--reverse">...</div>
      <!-- alternate sides for every subsequent row -->
    </div>
  </div>
</section>
```

**4. Cover poster variant (NEW component).**

A 70s travel-brochure cover for Countdown and Field Guide issues. Activate by adding `.hol-cover--poster` to the existing `.hol-cover` element. The base `.hol-cover` treatment (cloud-drift indigo poster with collage on the right) is preserved for issues that want the scrapbook-collage feel; the poster variant replaces it with a silkscreen-print SVG illustration plate plus a centred title stack.

The illustration plate is a static SVG: midnight sky gradient, sunburst rays from the upper-right, big moon-with-face character, scattered round stars, four-point sparkle stars, distant ridge silhouette, offset-overprint castle silhouette in rose ghost + cream front with brass lit windows, floating clouds, water reflection, and shoreline trees. The plate is identical across Countdown and Field Guide — it reads as the fairytale night sky on both.

On top of the plate sit, in order:
- `.hol-cover__sig` — the meta strip (brand + issue + kicker)
- `.hol-cover__arch` — SVG text-on-path arc (e.g. "★ GREETINGS FROM ★" for Countdown, "★ EAT YOUR WAY THROUGH ★" for Field Guide)
- `.hol-cover__title` with a `.hol-cover__title--print` inner span — chunky Bowlby One with a hard offset shadow in `--hol-ruby` that reads as misregistered screen-print
- `.hol-cover__sub` — Yellowtail subtitle, slightly tilted
- `.hol-cover__deck` — three-pill mono row with star dividers (date · gates · family-of-four, etc.)
- `.hol-countdown` — the existing live digit grid, pinned at the bottom of the stack

Template part: `assets/template-parts/03-cover-poster.html`. The full SVG plate plus the stack scaffold is embedded — writers paste it verbatim and fill the bracketed placeholders.

**5. Letterpress titles on Half II.**

The Half II opener title now uses `text-shadow: 6px 6px 0 var(--hol-burnt)` for a letterpress / poster-print feel instead of the original drop-shadow. This is a single-line change but it lands every chapter title in the savannah half as a hand-printed poster.

**Pre-flight regressions added in v8.13:**
- **RT-14:** Flat-fill ground on Half II is banned. Let `.hol-half--two` paint its own ground; don't set `background:` on the wrapper or on inner sections.
- **RT-15:** Venue/half mismatch is banned. Every Efteling chapter sits in `.hol-half--one`; every Beekse Bergen chapter sits in `.hol-half--two`. Cross-venue chapters live outside both halves (after the cover, or as the transit body).

