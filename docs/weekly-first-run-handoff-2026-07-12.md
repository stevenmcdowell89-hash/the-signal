# Weekly rebuild — first-run adherence handoff (2026-07-12)

**Purpose.** The first weekly generated against the rebuilt spec
(`signal_weekly_2026-07-12.html`, skill v8.37/v8.38) came out **structurally
wrong** — it delivered ~16 reader-visible sections in a partially-applied
four-movement frame. This document states the **original design intent**, the
**exact section target**, the **defects observed in the shipped issue**, and the
**spec ambiguities** that let it happen, so another instance can fix the spec +
enforcement and regenerate. Read alongside `docs/signal-final-recommendations-2026-07.md`
(§ STREAM 1) and `.claude/skills/the-signal/references/spec/weekly.md` (L27–64,
the canonical order).

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

**One-line summary for the next instance:** the four-movement weekly should render
**4 movements and ~11–13 navigator sections, with The Desk as ONE nested
department running 1–2 columns and Release Radar folded into Screen & Sound**; the
first run instead produced 14 flat sections with 2 movement bands missing and the
Desk exploded into 3 — fix the spec ambiguities (esp. Bookmark vs The Shelf),
enforce the structure in `validate-issue.py` (markup gate), then regenerate and
actually inspect.
