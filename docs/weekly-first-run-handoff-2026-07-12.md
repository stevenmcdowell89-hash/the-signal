# Weekly rebuild — first-run adherence handoff (2026-07-12)

**Purpose.** Two issues generated the morning of 2026-07-12 came out badly and
need another instance to fix the spec + enforcement and regenerate:
1. **The weekly** (`signal_weekly_2026-07-12.html`, Issue #16) — **structurally
   wrong**: ~14–16 flat sections in a partially-applied four-movement frame (§1–7).
2. **The Rewind H1-2026 review** (`signal_rewind_2026-07-12.html`) — **content
   dreadful**: its research pool was far too narrow (a 6-month, all-domains review
   written from ~6 recency-biased events — the **root cause**, §8d), which it then
   padded by re-narrating those events 3–4× across too many overlapping lenses
   (§8a); PLUS leaked placeholder/spec text (§8b), PLUS it fails the ship gate on
   images yet shipped anyway (§8c).

Both share a root cause: **the rebuilt/reactivated formats were never
generated-and-inspected end-to-end** — only spec-consistency-checked and (for the
weekly) run through `validate-issue.py` on an *old* issue (§5). This document
states the **original intent**, the **exact targets**, the **observed defects**,
and the **spec ambiguities**. Read alongside `docs/signal-final-recommendations-2026-07.md`
(§ STREAM 1 + STREAM 3) and `.claude/skills/the-signal/references/spec/weekly.md`
(L27–64, the canonical order) and `references/spec/specials.md` / `formats.md`
(Rewind).

---

## 1. Original intent (what a correct weekly is)

The rebuild reorganises the weekly into **exactly four movements** (the spine),
with the branded sections living *inside* them. It is a **collapse**, not an
addition: one Long Read, ~6–9k words, a tight palette. Key intents:

- **Four movements, always:** `I · THE OPEN` → `II · THE LONG READ` →
  `III · THE ROUNDS` → `IV · THE CLOSE`. Each movement opens with its band.
- **Exactly ONE Long Read** per issue (the single deep anchor; absorbs the old
  Saga / Deep-Dive-lite / evergreen-feature impulses). No second mandated deep
  anchor anywhere.
- **The Desk is a single service *department*, not a set of sections.** It groups
  four service columns — The Session (fitness), The Ledger (money), The Itinerary
  (travel/parks/NI), The Toolkit (tech). **Only 1–2 columns run per issue**,
  chosen by which domain is most overdue *and* has real, actionable service news;
  a domain with nothing to act on **yields**. → **The Desk = ONE navigator entry
  with 1–2 columns nested inside it.** It is NOT 3–4 standalone sections.
- **Release Radar lives INSIDE Screen & Sound**, not as its own section.
- **Yield rather than fill:** any fixed section whose week is thin yields rather
  than padding. So a real issue is usually *fewer* sections than the maximum.
- **Ends on a verb + a human line** (Do This Week → Colophon sign-off), never an
  aphorism.

The intent is explicitly **not** "all service columns every week" — that would be
content-thin, which the 1–2-per-issue rule exists to prevent.

---

## 2. How many sections there should be (the exact target)

Count at three levels — do not conflate them:

**A) Movements: EXACTLY 4.** THE OPEN, THE LONG READ, THE ROUNDS, THE CLOSE. All
four bands must render.

**B) Navigator entries (the "sections" a reader perceives): target ~11–13.**
The canonical fixed content sections, each = ONE navigator entry:

| # | Section | Movement | Notes |
|---|---|---|---|
| 1 | The Letter | OPEN | signed editor's letter |
| 2 | Caught Up | OPEN | 8-line hard-capped digest |
| 3 | The Long Read | LONG READ | exactly one |
| 4 | The Touchline | ROUNDS | sport |
| 5 | Pixel & Byte | ROUNDS | gaming + LEGO |
| 6 | Screen & Sound | ROUNDS | **Release Radar is inside this — not a separate entry** |
| 7 | Books rail | ROUNDS | ONE entry (see ambiguity §4 — "Bookmark" vs "The Shelf") |
| 8 | **The Desk** | ROUNDS | **ONE entry; 1–2 columns nested inside; NOT 3–4 entries** |
| 9 | The Threads | CLOSE | continuity engine |
| 10 | On the Radar | CLOSE | forward calendar |

Plus **1–2 non-Desk rotating** sections (This Week in History, Listening) → **+1
to +2**. Short beats/openers that are **not** counted as their own chapters and
should not inflate the count: The Week, Composed (~80–140w on-ramp), The Week in
Numbers (stat strip), Down the Rabbit Hole (small sidebar, if due), Do This Week
(closing pin), Colophon (footer block). Cover / Navigator / Footer are chrome.

**So: 4 movements · ~10 fixed content sections · +1–2 rotating = ~11–13 navigator
entries.** On a thin week (sections yielding) it can be fewer. It should **not**
exceed ~13.

**C) Component palette: ~12** load-bearing components (see weekly.md § Component
Quick Reference; structural always-on components are separate).

---

## 3. What actually shipped (the defects) — `issues/signal_weekly_2026-07-12.html`

Measured from the generated file:
- **~6,954 words** ✅ (length cut landed, within the 6–9k target).
- **One Long Read** ✅.
- **14 navigator cards** ❌ (target ~11–13, and the composition is wrong below).
- **Only 2 of 4 movement bands rendered** ❌ — `THE OPEN` and `THE LONG READ`
  present; **`THE ROUNDS` and `THE CLOSE` missing**.
- **The Desk exploded into 3 standalone sections** ❌ — The Session, The Toolkit,
  and The Itinerary each rendered as their own navigator entry instead of ONE
  Desk entry with 1–2 nested columns. (It also ran **3** columns, over the 1–2
  cap.)
- **Release Radar rendered as its own section** ❌ (item 8) instead of inside
  Screen & Sound.
- **Books rendered as "The Shelf"** (the rotating name) rather than the fixed
  "Bookmark" rail — a symptom of the §4 ambiguity.

Net: the generator **layered the new movement elements on top of the old section
list instead of collapsing them** — new sections (The Letter, Caught Up, Long
Read, The Desk heading, The Threads, Week in Numbers, Do This Week) are all
present, but the *consolidation* (nesting, folding, movement banding, column cap)
was only half-applied. Correcting the three structural defects (fold Release
Radar, collapse the 3 Desk entries → 1, drop over-cap column) brings 14 → ~11.

---

## 4. Spec ambiguities that let this happen (FIX THESE IN THE SPEC)

1. **Books is defined twice, contradictorily.** weekly.md L34/L49 list a fixed
   **"Bookmark" books rail** inside THE ROUNDS; L64 lists **"The Shelf (books)"**
   as a *non-Desk rotating* section. Both cover books. Decide ONE model (a fixed
   lightweight Bookmark rail every issue, OR a rotating Shelf) and purge the
   other from the spec + sections.md + the cadence table. The generator picked
   "The Shelf", suggesting the rotating definition is winning by accident.
2. **The Desk's "one entry, columns nested" is stated in prose but not enforced
   structurally.** There is no template/navigator rule that makes the Desk a
   container; nothing stops the columns from rendering as siblings with their own
   nav cards. Make The Desk a structural container (single nav anchor; columns
   are sub-headings within it).
3. **The four movement bands are described but not required.** Nothing asserts all
   four render. Two went missing with no error.
4. **The 1–2 Desk-column cap and "Release Radar inside Screen & Sound" are soft
   prose**, not checked. The generator exceeded/ignored both.

---

## 5. The testing gap (root cause of it shipping)

The weekly rebuild (batches W-1…W-4) was validated by:
- spec internal consistency (`slice-spec.sh`, grep sweeps), and
- `validate-issue.py --format weekly` **passing on an OLD, pre-rebuild issue**.

**No new issue was generated against the new spec and inspected.** For a
prompt-driven generator that is the *only* test that catches adherence failures
(movement bands, Desk nesting, column cap, Release Radar fold). `validate-issue.py`
checks placeholders / structure / back-link / navigator variant / image URLs — it
does **not** check any of the four-movement structural intents. So the rebuild
passed its checks while the actual output was wrong. Closing this gap =
(a) encode the structural intents as checks, and (b) actually generate + inspect.

---

## 6. Recommended remediation (for the next instance)

1. **Resolve the §4 spec ambiguities first** (esp. Bookmark vs The Shelf) — the
   generator can't be consistent while the spec is.
2. **Add a weekly structural check to `validate-issue.py`** — inside the existing
   **markup-contracts gate** (NOT a new gate; the ledger stays at three, per
   `docs/signal-final-recommendations-2026-07.md` §5). Assert, for
   `--format weekly`:
   - all **four movement bands** present (THE OPEN / THE LONG READ / THE ROUNDS /
     THE CLOSE);
   - **exactly one** Long Read anchor;
   - **The Desk is one section** with **≤2 columns** nested (fail on ≥3 Desk
     columns or Desk columns rendered as top-level nav entries);
   - **Release Radar** appears within Screen & Sound, not as a top-level section;
   - **navigator entry count ≤ ~13**.
   This would have caught this morning's issue automatically.
3. **Regenerate `signal_weekly_2026-07-12.html`** against the fixed spec + new
   check, and **inspect the output** (the missing end-to-end test). Iterate the
   spec wording until it renders 4 clean movements and ~11–13 nav entries with
   The Desk nested. Decide whether the corrected issue **replaces** the shipped
   file or sits beside it (`...-v2.html`) — confirm with the owner
   (steven.mcdowell.89@gmail.com) before overwriting a published issue.
4. Consider making the **holistic quality read** (gate 3) explicitly ask "are all
   four movements present and is The Desk a single nested department?" so intent,
   not just markup, is judged.

---

## 7. Relevant paths

- Spec (source of truth): `.claude/skills/the-signal/references/editorial-spec.md`
  → sliced to `references/spec/weekly.md` (L27–64 canonical order, L189+ cadence,
  L327 always-on components) via `scripts/slice-spec.sh` (edit the source, re-slice).
- Section briefs: `references/sections.md` (§ The Desk + the four column briefs).
- Component contracts: `references/component-contracts.md`
  (`.do-this-week`, `.the-threads`, `.week-in-numbers`).
- Templates: `assets/template-parts/` (`13a-the-desk.html`, `15a-the-threads.html`,
  `15b-week-in-numbers.html`, `08-anchor-piece.html` = Long Read slot).
- Ship gate: `scripts/validate-issue.py` (KNOWN_FORMATS ~L50, `--format` ~L803,
  `--skip-image-urls` ~L806) — add the structural check here.
- Shipped issue under review: `issues/signal_weekly_2026-07-12.html`.
- Skill version + changelog: `SKILL.md` L21, `CHANGELOG.md`.

---

## 8. ALSO BROKEN THIS MORNING: the Rewind special (`signal_rewind_2026-07-12.html`)

The reader gave up 3 pages in — "it spent 3 pages repeating the same thing over
and over." Three distinct, confirmed defects:

**8d. THE ROOT CAUSE — the research pool was far too narrow (fix this first).**
The repetition in 8a is a *symptom*. The real problem: a 6-month, all-domains
retrospective was written from a **recency-biased handful of ~6 events**, then
padded across ~9 lenses. Structural de-dup will NOT fix this — 6 events told once
each is still a thin half-year review. Why it happened:
- **The Rewind format spec has no corpus-gathering step.** `formats.md`/`editorial-spec.md`
  (§ Rewind) specify the *output* (chapters, the Throughline, the Memory Test,
  8–12k words) in detail but never say **how to assemble the period's material**.
  The generic research phase (`pre-flight.md` Phase 3) is scoped to *this issue's
  subject* — fresh web research + fact/image sourcing for a week's content — not to
  systematically enumerating six months of events across every domain.
- **So the generator fell back to what's cheap in reach:** the recency-scoped
  state arrays (`recent_facts`: 12, `ongoing_stories`: 3, `recent_next_week_themes`:
  4) and a thin fresh pass. Every repeated event in the shipped issue is from the
  **last few weeks** (Starmer/landslide, the F1 record, the grand slam, the Man
  City draw) — the tell that it drew from recent memory, not the half-year.
- **Do NOT "fix" this by re-mining the weeklies.** The 16 archived weeklies are the
  *in-the-moment* record; aggregating them yields a **recap** of what was already
  said, in the weekly's in-the-moment framing — not a retrospective. **6 months is
  a different lens.** The Rewind's job is *hindsight*: what actually defined the
  half-year, what **stuck vs faded** (things that felt huge in April and evaporated;
  quiet things that turned out to matter), and the emergent **throughline** you can
  only see at distance. Re-narrating weekly coverage produces exactly the flat,
  repetitive "greatest-hits" the reader gave up on. The daily's D1 data can't help
  either (only ~14 days retained).

**Fix (do this before the structural de-dup):** give the Rewind its **own research
mode — a fresh retrospective pass at the 6-month altitude**, specced distinctly
from the weekly's this-week sourcing. Per domain, research what *defined the period
with hindsight*: mid-year/half-year retrospectives are abundant and exactly the
right altitude — "games of 2026 so far", mid-season league assessments, F1
half-term reports, best-books-of-the-year-so-far, world-news half-year reviews —
alongside the reader's own tracked interests over the window. Judge **what stuck vs
what faded**, don't restate the in-the-moment take. Gate it with a **breadth floor
at Phase 3b** (corpus must span ≥N domains / ≥M distinct events) so an
under-researched Rewind fails like an under-sourced Deep Dive rather than shipping
and repeating itself. The weeklies, if consulted at all, are only a light
memory-jog of the reader's *personal* throughlines (the trip, the training block,
the title race he was following) — never the corpus to recap.

**8a. Chronic cross-section repetition (the reader's complaint — a SYMPTOM of 8d).** The Rewind runs
~9 overlapping retrospective lenses — **The Period in Numbers, The Highs, The Lows,
Beyond the Results, What We Missed, The Memory Test, Picks of the Period, The
Changing of the Guard, Meanwhile** — and they all draw from the same small pool of
H1 headline events, so the *same facts* are retold 3–4 times. Measured repeated
phrases across the one issue:
- "…less than two years after a landslide…" **×4**
- "Keir Starmer resigned as prime minister…" **×3**
- "…the afternoon Manchester City could only draw…" **×3**
- "no driver in the sport's history had…" **×3**
- "a first grand slam at the fourth…" **×3**
Root cause: too many lenses over too few events, and **no cross-section
de-duplication rule** ("an event told in one lens must not be re-told in another").
Note: the **theme-clustering gate that could have flagged this was retired
(deleted) in W-3** — its intent was meant to move into the single holistic quality
read (§5 of the recommendations), but that read is a manual/prompt step and was
never exercised on this issue.

**8b. Leaked placeholder + spec text (confirmed in the DOM).** The shipped issue
contains unfilled template scaffolding and spec instructions as *visible* content:
- `<h3>Pick title</h3>`
- `<h3 class="only-one-pick">[Title of the pick]</h3>`
- `World is always photo-led (default). 1–2 other sections per issue may promote…`
  (a spec/comment line rendered as body text).
`validate-issue.py`'s placeholder check did **not** catch any of these tokens.

**8c. It isn't even shippable — but it shipped.** Running the ship gate on it:
`validate-issue.py --format rewind` **FAILS** (`image-urls-static`: 2 Nintendo
**page** URLs used as `<img src>`, no image extension). So the issue went live
without passing its own ship gate (published with `--skip-image-urls`, or the gate
was bypassed). That is a process failure independent of the content.

**Remediation for the Rewind (next instance):**
1. **Cut the retrospective lenses down** — pick ~4–5 that each do a *distinct* job
   (e.g. Numbers, The Highs/Lows as one balanced ledger, The Memory Test, Picks),
   and add a hard rule: **each event appears in exactly one lens.** The Rewind's
   job is a *curated* look back, not the same 8 stories through 9 filters.
2. **Fix the placeholder scaffolding** in the Rewind template/spec (`Pick title`,
   `[Title of the pick]`) and stop spec/comment text leaking into the body; and
   **extend `validate-issue.py`'s placeholder check** to catch bracketed `[...]`
   scaffold tokens and stray spec lines.
3. **Do not publish on a validator FAIL** — the automation must block, not
   `--skip-image-urls` its way past a real image failure.
4. **Reconsider whether Rewind should have auto-fired at all** — Specials batch S1
   reactivated it (calendar-scheduled) but it was **never generated-and-inspected**
   (same gap as §5). Until it's fixed + inspected, consider demoting it back to
   dormant so it doesn't auto-publish a bad issue next window.

Relevant paths: `references/spec/specials.md`, `references/spec/formats.md`,
`references/spec/triggers.md` (Rewind format + its trigger), the Rewind
template-parts under `assets/template-parts/`, and `scripts/validate-issue.py`.

---

**One-line summary for the next instance:** the four-movement weekly should render
**4 movements and ~11–13 navigator sections, with The Desk as ONE nested
department running 1–2 columns and Release Radar folded into Screen & Sound**; the
first run instead produced 14 flat sections with 2 movement bands missing and the
Desk exploded into 3 — fix the spec ambiguities (esp. Bookmark vs The Shelf),
enforce the structure in `validate-issue.py` (markup gate), then regenerate and
actually inspect.
