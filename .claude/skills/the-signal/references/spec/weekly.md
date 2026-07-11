# Spec slice — weekly

_This file consolidates the weekly/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Standard Weekly (default)
The full Sunday edition. **Target ~6,000–9,000 words (v8.37, W-3 — roughly a 40% cut from the old ~20-30-page issue).** This is a real target, not just guidance: the four-movement spine (one Long Read, brisk rounds, an 8-line Caught Up) is built to land in this band. It is still shaped by *movements and per-piece shape*, not a rigid quota — flex to the news, yield thin rounds rather than padding — but an issue drifting well past ~9k words has reverted to the old two-anchors-everywhere bulk and should be cut back to the spine. The deep length lives in the single Long Read; the rounds stay short. Section order per the four movements above.



---

## sections

## Section Structure (Standard Weekly)

Sections are divided into **fixed** (appear every issue, except where noted) and **rotating** (appear on a cadence, selected per issue). Each issue includes the fixed sections plus **2-3 rotating sections**. The Navigator adapts to show only the sections present in that issue. The issue ends with a Colophon (sign-off block) before the Footer — see § End-of-Issue Colophon.

> **Why 2-3 rotating slots (v8.27, was 3-4 in v8.16).** The v8.16 roster grew to 14 rotating sections by *splitting* (The Listen out of The Shelf, The Local out of The Itinerary, plus Brickyard / Saga / Lab / Channel), which made several sections compete for the same content and let one interest flood an issue. v8.27 redesigns the roster around the reader's actual interest-domains — one home per domain — collapsing to **5 rotating sections plus one trigger-driven section**. Fewer sections + fewer slots = less slot-filling pressure and a shorter, less-padded issue, back toward the "good era" size.

### Four-Movement Architecture (v8.37, W-3 — the spine)

The weekly is organised as **four movements**. The movements are the spine; the branded sections below live *inside* them (identities unchanged — Touchline, Pixel & Byte, Screen & Sound, The Desk, The Threads all keep their names and CSS). The order below is the canonical issue order. **The issue ends on a verb and a human line** — a "Do This Week" and the Colophon's sign-off, not an aphorism.

- **I · THE OPEN** — discharge completeness up front, then hand off.
  - **The Letter** — the signed editor's letter (§ The Letter). The week's thesis, dots connected across domains.
  - **The Week, Composed** — a short editor-shaped orientation to the issue: the week arranged into two or three thematic strands (what the issue holds and how it hangs together). It **replaces the old triple on-ramp** (Navigator + Long Shelf + Foreword-as-contents); the Navigator chrome still renders for jump-links, but the *reading* on-ramp is this one composed paragraph, not three overlapping tables of contents. ~80–140 words.
  - **Caught Up** — a hard-capped **8-line, non-expandable** digest of the week's missable news across domains (§ Caught Up). This is where completeness is discharged: eight lines, then done. Because Caught Up carries the breadth, **no downstream section owes a "safety-net headline" backstop** — the old breadth-safety-net-in-every-section rule is retired (see § Caught Up).
- **II · THE LONG READ** — exactly **ONE** deep anchor per issue, subject rotating week to week (uses the `08-anchor-piece` slot). This single Long Read is the issue's one considered centre of gravity: it **absorbs the old Saga, Deep-Dive-lite, and evergreen-feature impulses**. There is no second mandated deep anchor anywhere else in the issue — the rounds carry the week's news at whatever depth the material earns, not a forced considered-piece backbone (§ Article Structure).
- **III · THE ROUNDS** — the week's domains, briskly. **The Touchline** (sport), **Pixel & Byte** (gaming + LEGO), **Screen & Sound** (with Release Radar), a **Bookmark** books rail (the lightweight books shelf — what to read, a few picks with a line each; the deep book piece, when there is one, is the Long Read, not here), and **The Desk** (1–2 service columns, each closing on its "Do This Week" pin). The rounds are rounds — news and picks, not essays.
- **IV · THE CLOSE** — continuity, then forward, then act, then sign off.
  - **The Threads** — the continuity engine (§ The Threads): "previously on…" recaps of the named sagas and the reader's life-threads.
  - **Down the Rabbit Hole** — the signature discovery ritual (recurring sidebar; `references/sections.md`).
  - **On the Radar** — the forward calendar.
  - **Do This Week** — the issue's single strongest actionable pin surfaces here as the closing beat (the Desk columns each carry their own; this is the one the reader leaves on).
  - **Colophon** — Issue in Numbers · Next Week · A Fact · the sign-off line.

> **The movements group the existing sections — they are not new sections.** The Long Shelf concept is absorbed by The Week, Composed (its discovery-wildcard value moves into The Letter and the Long Read); the deep-anchor rotation across sections is replaced by the single Long Read. Everything else keeps its identity and moves under the movement it belongs to.

### Fixed vs Rotating

**Fixed (every issue), grouped by movement (v8.37):**
- **I · THE OPEN:** Cover, Navigator (jump-link chrome), **The Letter**, **The Week, Composed** (the on-ramp — replaces the Long Shelf; see § The Week, Composed), **The Week in Numbers** (the personal stat strip — see § The Week in Numbers), **Caught Up** (the 8-line completeness digest — see § Caught Up).
- **II · THE LONG READ:** **The Long Read** — exactly ONE deep anchor, rotating subject (`08-anchor-piece` slot; see § The Long Read).
- **III · THE ROUNDS:** The Touchline, Pixel & Byte (gaming + LEGO), Screen & Sound (with Release Radar), the **Bookmark** books rail, **The Desk** (1–2 service columns; see § The Desk). *(The World This Week is not a fixed round — world coverage leads in Caught Up and, on weeks it earns the depth, as the Long Read.)*
- **IV · THE CLOSE:** **The Threads** (the continuity engine — see § The Threads), Down the Rabbit Hole (if due), On the Radar, Do This Week (the closing pin), Colophon, Footer.

The Long Shelf is retired as a section — its on-ramp job passes to The Week, Composed and its wildcards to The Letter / the Long Read. The World This Week is no longer a standalone fixed round: its safety-net breadth lives in Caught Up, its depth (when the week earns it) in the Long Read.

> **Yield rather than fill (v8.34).** The "yield when the week is thin, don't pad it to appear" principle applies to **every** fixed section: a fixed section whose week offers only catch-up — the recap the daily already delivered — **yields** that week rather than running a roundup to fill the slot. The mandatory element is the considered piece (§ Article Structure), not the section's mere presence. (For Desk columns the analogue is: run the column only when its domain has real service news, and each column that runs still closes on a "Do This Week" pin.)

**The Desk (service department — the home for all service content, v8.36).** The Desk groups four **service columns**, of which **1–2 appear per issue** — picked by which domain is most overdue *and* has real service news to act on this week:
- **The Session** (fitness) — keeps its existing fitness brief and content rules.
- **The Ledger** (money / personal finance / consumer fintech / side-hustle & Etsy) — the rebrand of the former "Money" rotating section; same three streams, new name (the CSS `.ledger-section` / `--ledger-*` tokens already exist).
- **The Itinerary** (travel / theme parks / NI-local) — the rebrand of the former "Places" rotating section; same content.
- **The Toolkit** (tech / Android / e-ink) — keeps its existing tech brief.

The Session and The Toolkit are **no longer standalone fixed sections** — they are Desk columns alongside The Ledger and The Itinerary. Each Desk column that runs **ends in a "Do This Week" pin** (see § The Desk below): exactly one concrete, do-it-this-week action with the *why* attached and the selection **criteria stated, not vibes**.

**Rotating, non-Desk (cadence-based, pick 1-2 per issue on top of the Desk columns):** The Shelf (books), This Week in History, Listening (podcasts + audio drama + music). These three are *not* service columns and carry no "Do This Week" pin — they are discovery/reflection, not the service desk.

**Trigger-driven (no cadence timer):** The Saga (lore deep-dive). It does NOT rotate on a clock — it runs only on a *reason*: a live public peg the researcher finds (a finale aired, a new book/season in a series the reader follows released, an author AMA), or a private peg the reader supplies (`currently_reading` / `currently_watching` in state, or a manual "run a Saga on …" trigger). See its brief in `references/sections.md` and the trigger note under § Auto-Triggered Specials.

See **Rotation Mechanics** below for scheduling rules.

### The Desk — the service department (v8.36)

The Desk is the restored **service department**: the one place in the issue whose job is not to inform but to help the reader *do* something this week. It groups four rotating **service columns** — **The Session** (fitness), **The Ledger** (money), **The Itinerary** (travel/parks/NI), **The Toolkit** (tech) — and **1–2 run per issue**, chosen by which domain is most overdue *and* has real, actionable service news (not by a cadence clock alone). A domain with nothing actionable this week yields rather than padding to appear. Full column briefs live in `references/sections.md` § The Desk.

**The "Do This Week" pin — the mandatory closing element of every Desk column.** Every Desk column that runs **ends on exactly one "Do This Week" pin**: a single concrete, do-it-this-week action, with the *why* attached and the **selection criteria stated, not vibes**. The pin names the specific thing and says why *that* one — not a hedge.

- **Good:** "Move your emergency fund to Chase Saver at 4.75% AER — it's the top easy-access rate right now with no intro-bonus cliff."
- **Bad:** "Consider a high-interest savings account." (no named product, no stated criterion, not do-it-this-week).

One pin per column, always last. Markup: a `.do-this-week` block (see `references/component-contracts.md`). The pin is service, not an aphorism — it is exempt from the one-aphorism-per-issue cap and is *not* the section's Lead.

### The Threads — the continuity engine (v8.36)

**The Threads** is a fixed, reader-facing continuity section built off the state file's `ongoing_stories` — extended **beyond World** to named sagas across **all** domains, plus the reader's own **life-threads**. It is the "previously on…" of the magazine: each thread is a few lines of situation-report recap with a link, so a story the reader has been half-following snaps back into focus.

- **Two kinds of thread:**
  1. **Named sagas** (from `ongoing_stories`, any domain): an Iran-endgame thread, a Serie A / Antonelli title-run thread, a long-running show arc, a Switch-2-ecosystem thread — whatever the state file is tracking as live. Each gets a short "previously on / where it stands now" recap and a link.
  2. **Life-threads** (the person in the personal magazine): the marathon build from state `training_phase`, the upcoming trip from state `upcoming_trips` (e.g. the Efteling trip) — the reader's own ongoing arcs, recapped the same way ("Week 6 of the block; long run up to 18 miles; taper starts…").
- **`ongoing_stories` now feeds ONLY The Threads (v8.37, W-3 — the topic-lock suppression role is dropped).** In v8.36 `ongoing_stories` was dual-use: the Topic-Lock suppression backstop *and* The Threads' data source. W-3 **retires the suppression backstop** (§ Topic Lock — the sliding-window cap and `check-topic-lock.py` are gone). `ongoing_stories` is now a single-purpose, reader-facing asset: The Threads reads it to recap named sagas across all domains. `training_phase` + `upcoming_trips` additionally feed the life-threads. Dropping suppression-by-gate in favour of The Threads' recap is deliberate — a story that keeps recurring is *recapped*, not hidden.
- **Voice:** situation-report + "previously on" recap tone — factual, compact, each thread a few lines and a link. No new opinion or invented angle; it is a *recap*, not a Lead. It does not carry a "Do This Week" pin (that is the Desk's job).
- **Placement:** part of the closing movement — after the rounds, near On the Radar (continuity flows naturally into the forward calendar).

### The Week in Numbers — the personal stat strip (v8.36)

**The Week in Numbers** is a small, fixed, compact **personal** stat strip near the top of the issue: a handful of numbers about *the reader's* week, not the news. Drawn from state and the week's results:

- **Garmin miles + current training block** (from state `training_phase`) — e.g. "31.2 mi · Base block, wk 6".
- **FPL rank** — the reader's Fantasy Premier League overall rank movement.
- **The Juventus result** — the week's Juve scoreline.
- **One money number** — a single figure from The Ledger's world (a savings rate, an Etsy month, an ISA milestone).

It uses the existing `.stat-bar` / `.stat` component vocabulary (compact, not a full section). 4–5 stats, quietly personal.

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
- **Markup:** keep the existing `.foreword` block and its drop-cap (the CSS and the navigator anchor are unchanged); The Letter is the same slot, renamed and re-voiced. The navigator card reads "The Letter".
- One genuine aphorism is allowed across the whole issue (see § Editorial Voice); if you spend it, spend it here or in the Long Read — not as a per-section habit.

### The Week, Composed — the on-ramp (v8.37, W-3)

A short editor-shaped orientation that follows The Letter: the week arranged into **two or three thematic strands** — what the issue holds and how it hangs together — in ~80–140 words. It is the **single reading on-ramp**, replacing the old triple-table-of-contents pile-up (Navigator + Long Shelf + Foreword-as-contents). The Navigator chrome still renders for jump-links; The Week, Composed is the *prose* orientation. It carries the discovery-wildcard flavour the Long Shelf used to (one line can point at something off the beaten track). No new markup required — a titled paragraph block; reuse the `.foreword`-adjacent editorial styling or a plain `.sec-opener`.

### Caught Up — the 8-line completeness digest (v8.37, W-3)

**Caught Up** is a hard-capped, **8-line, non-expandable** digest in Movement I that discharges the week's completeness up front. Eight lines, one per missable item, each a single tight line (a specific fact + a link) across the reader's domains — world, sport, gaming, tech, culture. Then it stops.

- **Hard cap: 8 lines, never more, and non-expandable** — no "…and 6 more", no collapsible, no companion list. If there are more than eight things, the ninth wasn't missable enough. The cap is the point: completeness is a *fixed budget*, not an open drawer.
- **It replaces the breadth-safety-net-in-every-section rule.** Historically every fixed section's Catch-Up had to carry "one-line safety-net headlines" so demoting a story out of a Lead never dropped it. Caught Up now owns that job for the whole issue: the week's big headlines survive *here*, in one place, up front. **Downstream sections no longer carry safety-net headlines** — the rounds cover their domain's real news at the depth it earns and nothing more (§ Article Structure; the safety-net clause is retired).
- **Voice:** flat, factual, fast — the anti-essay. No angle, no synthesis (that is the Letter's and the Long Read's job). Each line reads like a wire headline the reader can act on or ignore.
- **Markup:** a `.caught-up` block — a titled list of ≤8 `<li>` items, each with a link. Renders complete with JS off (no expand affordance exists to break).

### The Long Read — the single deep anchor (v8.37, W-3, supersedes the deprecated Anchor-Piece Rotation)

Movement II is **one** deep anchor per issue — the issue's sole considered centrepiece, subject rotating week to week (world one week, a game or a training idea or a book the next). It uses the existing `08-anchor-piece` slot (`.is-anchor` on its `<section>` and its Navigator `.toc-row`), opens with a strong opener, and runs long enough to earn the space (typically 900–1,800 words; longer when the subject genuinely warrants). It **absorbs the old Saga, Deep-Dive-lite, and evergreen-feature impulses** — those are no longer separate deep beats scattered across the issue; the deep work concentrates here. Exactly one runs; there is no second mandated anchor. (The whole-issue Deep Dive special is unaffected — the Long Read is a weekly *movement*, the Deep Dive is a whole-issue interruption.)

### Synthesis-by-juxtaposition — a prose technique for contested material (v8.38, W-4)

**Synthesis-by-juxtaposition** is the magazine's technique for World-adjacent and other **genuinely contested** material — now that world coverage lives in **Caught Up** and, when the week earns it, the **Long Read**. Instead of the Editor adjudicating a dispute (which would breach the Cardinal rule against inventing a thesis), the piece places **2–4 short, ATTRIBUTED, genuinely conflicting excerpts in sequence** and lets **the arrangement carry the meaning**. The reader draws the conclusion the ordering implies; the magazine never states it.

- **Attribution is mandatory and load-bearing.** Every excerpt names its source (outlet, analyst, named commentator) and traces to the research bundle as an `opinion` fact with a real `quote` (§ Key Rules → Borrowed angles; RT-22). An unattributed or invented "some argue…" excerpt is a fabrication fail — this technique **only** works with real, citable disagreement.
- **The excerpts must genuinely conflict.** Two takes that agree, or a strawman set up to be knocked down, defeat the purpose. Choose views that actually diverge (the hawk and the regional analyst; the launch-day rave and the considered pan) so the *gap between them* is the content.
- **The arrangement is the argument — so order deliberately.** Sequence for the reading you want the *juxtaposition* (not your narration) to produce: e.g. confident claim → the fact that complicates it → the quieter view that reframes both. Do not add a connective sentence telling the reader what to conclude ("what this really shows is…") — that is the hollow-connective-sentence trope and it collapses the technique back into invented thesis.
- **It is a prose technique, not a new component.** No new markup or CSS: render the excerpts with the existing vocabulary — a short run of attributed `<blockquote>`s, or the `.source-strip` / image-quote pattern — inside Caught Up's context or the Long Read's body. It counts against the ~12-component palette only insofar as it reuses those existing components. If a future issue needs a visually distinct stacked-juxtaposition block, add a contract to `references/component-contracts.md` then — until then it is prose.
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
| The Shelf | Every 2-3 weeks | Since last appearance | Books (primary), narrative history. Catch-up rule: covers full gap |
| This Week in History | Every 2-3 weeks | Current week | History is date-bound |
| Listening | Every 3-4 weeks | Since last appearance | Podcasts + audio drama + music (absorbs the old Listen + Channel) |

**Trigger-driven (NOT on this table):** **The Saga** (lore deep-dive) has no cadence timer — it runs on a live peg, not a clock. See § Auto-Triggered Specials → "The Saga (trigger-driven)" and its brief in `references/sections.md`.

**Folded away in v8.27–v8.36 (do not schedule — they no longer exist as standalone sections):** The Workshop and The Lab fold into **The Session** (training science + gear are now angles within it); LEGO folds into **Pixel & Byte**; The Listen + The Channel → **Listening**; the old Long Game + Wallet + Ledger names → **The Ledger** (v8.36, the rebrand of "Money"); the old Itinerary + Local names → **The Itinerary** (v8.36, the rebrand of "Places"). The Session and The Toolkit are no longer standalone fixed sections — they are **Desk service columns** (v8.36; see § The Desk).

### Selection Rules

1. **Check the state file** (`signal-state.json`) for `rotating_sections` — each entry has `last_appeared` date.
2. **Pick the most overdue sections first.** If The Shelf last appeared 3 weeks ago and Listening 2 weeks ago, The Shelf has priority. For **Desk columns**, weigh overdue-ness *together with* whether the domain has real, actionable service news this week (§ The Desk).
3. **Cap at 1-2 non-Desk rotating sections per issue** (on top of the 1–2 Desk columns) to maintain pacing. Rotating sections should be substantive (300-600 words each, except The Shelf which can be longer). The issue's bulk comes from the fixed sections' considered pieces; rotating sections add variety on top, not bulk. Fewer slots is deliberate (v8.27) — it keeps the issue from padding.
4. **The Itinerary overrides normal cadence** when a trip is approaching — that Desk column appears every issue or every other issue in the lead-up. Check state file for `upcoming_trips`.
5. **Don't force it.** If research for a rotating section (or a Desk column) turns up nothing worthwhile, skip it even if it's overdue. The cadence is a guide, not a mandate.
6. **Each domain at least monthly (editorial checklist, not a gate).** Over any ~4-issue stretch aim for each rotating domain — The Shelf, This Week in History, Listening, and each Desk column (The Session, The Ledger, The Itinerary, The Toolkit) — to appear at least once; this is editorial judgement, not a planner-enforced floor. The old hard-cadence-floor and deficit-promotion validators are **retired (v8.36)** — domain cadence is now this checklist line, not a planner gate. The Threads owns continuity (§ The Threads), so a domain being quiet in the rotation no longer needs a forced-include gate to keep its story alive. The Saga is excluded from the checklist — it is trigger-driven, not on a cadence (see Cadence Table).
7. **Default research window when `last_appeared` is null.** When a rotating section appears for the first time after a state file reset (or first-ever appearance), its research window defaults to "past 4 weeks" — NOT open-ended. Prevents the first appearance of a section from surfacing months-old news (e.g. the Revolut-from-March bug). Override via explicit `initial_research_window_weeks` field in state if the editor wants different.

### Placement: Interleave, Don't Stack

**Rotating sections must be woven between fixed sections, not dumped at the end.** They should feel like natural parts of the issue, not an appendix. Each rotating section has a preferred placement slot:

| Rotating Section | Preferred Slot | Reasoning |
|---|---|---|
| The Week in Numbers | Movement I — after The Week, Composed / before Caught Up | A quick personal read-out to open on |
| The Shelf | Between Screen & Sound and The Desk (original position) | Natural flow from entertainment to books |
| Listening | Between Screen & Sound and The Desk | Pairs with entertainment, breaks before the service desk |
| **The Desk** *(1–2 service columns)* | Between Screen & Sound / The Shelf and The Threads | The service department sits in the "act on it" cluster before the close |
| This Week in History | Between The Desk and On the Radar (original position) | Reflective close before the forward-looking calendar |
| The Threads | Between the rounds and On the Radar (part of the close) | Continuity recap flows naturally into the forward calendar |
| The Saga *(trigger-driven)* | Between Screen & Sound and The Shelf | Sits in the "story" cluster when a peg fires it |

**Within The Desk:** the 1–2 running columns sit together as the service department. The Ledger and The Itinerary read well mid-issue as a breather between dense sections; The Session and The Toolkit close the department. Each column ends on its "Do This Week" pin.

**When 2-3 rotating sections appear in the same issue:**
- Spread them across different slots — never place two rotating sections back-to-back.
- If two sections share a preferred slot, move one to its alternate position.
- The read-next connectors chain naturally through whatever sections are present.

**Each rotating section uses the full visual toolkit.** They are not second-class citizens:
- Every rotating section gets a `.sec-watermark`, section divider (`hr.divider.dv-[name]`), section-label, and a navigator card.
- Each uses at least 2-3 different component types (see component palette below).
- Background colours and accent colours are defined in CSS (`--[name]-bg`, `--[name]-accent`).
- Use `.reveal` animations on key elements.


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

**The weekly kit is a tight ~12 load-bearing components (v8.37, W-3 — trimmed from ~50).** The sprawling palette was part of what bloated the issue: every extra component invited another slot to fill. The standard weekly now reaches for **these twelve** and no more. No two consecutive sections use the same layout pattern; aim for 8–12 distinct types across the issue.

| # | Component | Class(es) | When to use |
|---|---|---|---|
| 1 | The Angle box | `.angle` | The one sharp claim in a piece that carries a real argument. **Never reprint as a pull-quote (banned voice-tic).** |
| 2 | Pull quote | `.pull-quote` (+`.centered`, +`.wide`) | 2–3 per issue to break prose. A real quote or a genuinely resonant line — never a minted aphorism, never the Angle box verbatim. |
| 3 | Stats row | `.stat-bar` > `.stat` > `.stat-num.count-up` | Key numbers for a story (also the base of The Week in Numbers). |
| 4 | Did You Know | `.dyk` | 3–5 scattered, section-aware colours. |
| 5 | Split layout | `.split-60-40`, `.split-40-60` | Text beside an image or a sidebar — the default two-column break. |
| 6 | Image (hero / offset) | `.hero-bleed`, `.img-offset` | Section-opening full-bleed image, or a 60%-width image the text wraps around. Every round wants at least one image. |
| 7 | Also cards | `.also-cards` > `.also-card` | 2-col card grid for 4+ short items (picks, the Bookmark rail). |
| 8 | Rating dots | `.rating` > `.dot.filled`/`.dot` | Reviews in Screen & Sound and the Bookmark rail. |
| 9 | Category dot | `.radar-cat` (+`.film`,`.game`,`.tv`,`.lego`,`.tech`,`.book`,`.music`) | Release Radar and On the Radar rows. |
| 10 | Results strip | `.results-strip` > `.result-card` | Match results with large scores (Touchline). |
| 11 | Read-next | `.read-next` | Section-to-section teaser link that chains the movements. |
| 12 | The case against | `.case-against` > `.ca-label`/`.ca-body` | **The Semafor-style counter-argument callout (v8.37).** Available **where a section carries a real argument** (usually the Long Read, occasionally a round with a genuine thesis): a short, honest "here's the strongest case the other way" box. Not decoration — only where there's a real argument to answer. Section-aware accent. See `references/component-contracts.md`. |

**Always-on structural components (not counted in the twelve — they render where their section requires them, not as palette choices):** `.sec-watermark`, `.sec-opener`, `.reveal` (leaf elements only — never on containers), `.count-up`, and the fixed-section components `.foreword` (The Letter), `.caught-up` (Caught Up), `.do-this-week` (each Desk column's closing pin), `.the-threads` (The Threads), `.week-in-numbers` (The Week in Numbers). These are required by their movements and don't compete for palette slots.

**Removed from the weekly kit (v8.37 — no separate graveyard file; recorded here).** These are retired from the *standard weekly* palette (CSS is retained for special editions, which keep their own component lists — nothing is deleted from `assets/css/`): Sidebar (`.sidebar`), Quick takes (`.dual-col`), Compact takes (`.compact-take`), Margin note (`.margin-note`), Big number (`.big-number`), Display stat (`.display-stat`), Mini data viz (`.sparkline`), Card stack (`.card-stack`), Timeline (`.timeline`), Collapsible (`<details.collapsible>`), Image montage (`.img-montage`), Float image (`.img-float-left`), Also list plain (`.also-list`), Watermark-as-choice, Book cards (`.book-card` — fold into image + rating dots), Workout card (`.workout-card`), Year badge (`.year-badge`), Platform badge (`.platform-badge`), Inset divider (`.divider.inset`), Breather band (`.breather`), Also-list tiers (`.tier-*`), Compare panel (`.compare-panel`), Floated sidebar (`.sidebar-float`), Grain overlay (`.grain-overlay`), Chapter chrome (`.chapter-chrome`), Folio watermark (`.folio-watermark`), Pull-break (`.pull-break`), Marginalia (`.marginalia`), Ember period (`.mast-period`). The four **entry-opener variants** (`.entry-stat` / `.entry-quote` / `.entry-bullets` / `.entry-question`) remain available as *openers* (plain prose is the default; use one only when the content genuinely leads with a number / quote / three facts / a live question) but are not counted among the twelve.

**Entry patterns are a palette, not a rota (v8.35 — rotation enforcement retired).** The `.entry-stat`, `.entry-quote`, `.entry-bullets`, `.entry-question` and plain-prose openings are available whenever one genuinely fits the material — reach for the one the piece earns, never to satisfy a rotation. The old "no two adjacent articles may open the same way" mandate is **retired**: forcing a different opener each time was a source of the mechanical voice-tic W-1 kills at the source. Plain prose is a first-class opening; use a stat/quote/bullet/question opener only when the content actually leads with a number, a real quote, three facts, or a live question.

**Breather band usage:** place 1-2 breather bands per issue between particularly dense sections. Use light variant between light/warm backgrounds, dark variant between dark backgrounds (Touchline, Screen & Sound, Shelf). Don't overuse — they're breathing room, not filler.

**Rotation rule:** no 3+ screen-heights of unbroken prose anywhere. Vary which sections use split layouts, where pull quotes appear, whether history uses timeline or bullets, which also-lists use card variant. Use sidebar-float as an alternative to split layouts. Use compare panels where a natural comparison exists. (Visual variety across the issue is still the goal; article *openings* are no longer on a forced rota — see the entry-pattern note above.)

---


