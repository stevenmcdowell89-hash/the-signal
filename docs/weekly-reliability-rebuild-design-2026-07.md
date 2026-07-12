# The Signal — Weekly Reliability Rebuild (design spec for the implementer)

**Status: DESIGN — hand-off for another instance to implement.** This document is
authored by the planning instance; it is a spec, not code. It defines how to make
the weekly (and every format) **reliably deliverable on a Sunday** without the
reader being pulled in as editor. Read alongside:
- `docs/weekly-first-run-handoff-2026-07-12.md` — the concrete defects that
  motivated this (weekly ran 16 flat sections; Rewind repeated ~6 events / thin
  research pool). This rebuild must make those classes of failure *impossible to
  ship*, not just documented.
- `docs/signal-final-recommendations-2026-07.md` §5 — the three-gate ledger (this
  design reconciles with it explicitly, see §7).
- `.claude/skills/the-signal/SKILL.md` — the phase pipeline (Phase 0→10) and the
  "gate discipline" rule.

## The owner's constraints (non-negotiable, from the brief)
1. **The reader is the reader, not the editor.** The magazine must be **delivered**
   — the Sunday slot matters. No workflow that depends on the reader diagnosing or
   approving each issue.
2. **Quality is paramount.** A delivered-but-bad issue is a failure (the reader
   skips the week either way). Correctness must be enforced, not hoped for.
3. **Multiple rounds of auto-repair are acceptable (within reason).** Solve
   quality with a bounded automated loop *before* the issue reaches the reader.

The tension between 1 and 2 is resolved by the publish policy in §6.

---

## 1. Why it's flaky (root causes — grounded in the current pipeline)

The pipeline (SKILL.md Phase 0→10) is: decide format → research (3/3a/3b) → plan
(4) → write (5, subagent fan-out) → stitch (6) → gates (7/7.5/7.6/7.7/8) → repair
(9, round 0 = images only) → holistic read (9.5) → deliver+publish (10). The
failure modes:

1. **Structure is generated, not deterministic.** The planner *decides* the
   chapter list and the writers *produce* sections; the stitcher assembles
   whatever they produced. Nothing makes the weekly's four movements / section
   nesting / count a fixed skeleton. → the 16-flat-sections, missing-movement-band,
   Desk-not-nested failure (handoff §1–7) is a direct consequence.
2. **There is no real quality signal — SKILL.md admits it** (v8.23 rationale:
   "the pipeline has no quality signal — only compliance gates… a clean gate
   record cannot distinguish 'as good as Opus' from 'quietly worse'"). The gates
   check markup, images, release dates, banned vocab — **not** repetition, section
   count, movement adherence, research breadth, or "does this read as one Sunday
   sit-down". The single holistic read (Phase 9.5) is one orchestrator prose
   judgment with no rubric and no teeth; it missed both of this week's failures.
3. **The repair loop only repairs images.** Phase 9 "round 0" is
   `auto-repair-images.py`. There is no structured repair for structural or content
   defects — because there are no checks that *detect* them to repair against.
4. **Publish isn't mechanically gated.** "Gate discipline" is a *prompt rule* ("the
   orchestrator MUST run the gate and honour the exit code"), not a machine
   enforcement. The Rewind shipped this morning **despite failing `validate-issue.py`
   on images** — proof the prompt rule can be (and was) bypassed. Nothing outside
   the orchestrator's own compliance blocks a bad commit.
5. **The spec is large and self-contradictory.** Thousands of lines of mostly-soft
   "should" rules across editorial-spec + 6 slices + sections + contracts +
   checklist + pre-flight, with live contradictions (Bookmark-vs-Shelf, handoff
   §4). Contradictions guarantee run-to-run variance.
6. **The generator is never regression-tested.** No issue is generated against a
   fixed input and asserted before a spec change ships — so spec edits (like the
   W-rebuild) reach Sunday unverified (handoff §5).

**Diagnosis in one line:** the weekly leaves *structure* and *quality* to
probabilistic generation, detects neither mechanically, repairs only images, and
ships on a prompt-honour system. Reliability requires making structure
deterministic, giving quality a real signal, repairing against both in a bounded
loop, and gating publish mechanically.

---

## 2. Design principles

1. **Determinism over instruction.** Anything that can be a fixed skeleton or a
   script MUST be, not a "should" the model re-derives weekly. (Same philosophy as
   "kill the tic structurally" — enforce by construction, not by rule.)
2. **Detect → repair → re-verify, before the reader.** Every defect class that has
   ever shipped gets a mechanical check; a failure triggers *targeted* repair and
   re-verification, looped, not a human ping.
3. **Publish is earned, not assumed.** An issue ships only when a machine-checkable
   receipt says every gate is green — enforced *outside* the orchestrator prompt.
4. **A real quality signal, not just compliance.** An independent, rubric-scored
   read that can fail an issue for *being bad*, not just for broken markup.
5. **Small, consistent spec.** One structural source of truth; resolve
   contradictions; delete soft rules the skeleton now enforces.
6. **Test the generator, not just the output.** A golden-issue regression so spec
   changes are verified before Sunday.

---

## 3. The architecture (six pillars)

### Pillar A — Deterministic format skeleton (kills the structural failure class)
Define each format's structure as **data, not prose**: a
`references/format-skeletons/<format>.json` (start with `weekly.json`) that is the
single source of truth for structure, consumed by BOTH the planner and the
stitcher and a new structural validator. For the weekly it encodes:
- the **four movements** in order (OPEN / LONG READ / ROUNDS / CLOSE), each a
  required band;
- the **sections inside each movement**, with **nesting** — e.g. `the_desk` is a
  **container** with 1–2 `column` child-slots (Session/Ledger/Itinerary/Toolkit);
  `screen_sound` **contains** `release_radar` (not a sibling);
- per-section **cardinality** (`min`/`max` runs — e.g. Long Read exactly 1; Desk
  columns 1–2; rotating non-Desk 1–2);
- a **navigator-entry ceiling** (~13) and the canonical order.

The **planner (Phase 4)** must emit a chapter plan that *validates against the
skeleton* — it fills content decisions into fixed slots; it cannot invent a flat
16-section list. The **stitcher (Phase 6)** assembles strictly in skeleton order
with the correct nesting (Desk wraps its columns; Release Radar renders inside
Screen & Sound). Because the skeleton is authored once and applied mechanically,
**the model can no longer get the structure wrong** — the class of failure in
handoff §1–7 becomes unrepresentable.

Restore `validate-chapter-plan.py` to a **blocking** structural gate against the
skeleton (it was demoted to "upstream aid" in W-3; that demotion is part of why
structure drifted). This does not violate the gate ledger — see §7.

### Pillar B — Structural ship gate (blocking; folds into gate 2 "markup contracts")
A new check in / alongside `validate-issue.py --format <fmt>` that asserts the
**stitched** issue matches the skeleton:
- all required movement bands present;
- navigator-entry count within `[min, ceiling]`;
- containers nested correctly (Desk = one entry wrapping its columns; no Desk
  column as a top-level nav entry; Release Radar inside Screen & Sound);
- exactly one Long Read.
Exit-code gate. A structural mismatch is **not shippable**.

### Pillar C — Content-quality checks (blocking; mechanical, cheap)
Add the checks that would have caught this week, as blocking gates:
- **Repetition detector** — flags cross-section repeated facts/sentences/n-grams
  (the Rewind class: the same event told 3–4×). Threshold-tuned; a repeated
  load-bearing fact across ≥2 sections fails. (This recovers the *intent* of the
  retired theme-clustering gate mechanically — see §7.)
- **Scaffold/placeholder detector** — extend the placeholder check to catch
  bracketed `[...]` template tokens, unfilled scaffold headings (`Pick title`,
  `[Title of the pick]`), and stray spec/comment text rendered as body (handoff
  §8b). No scaffolding may ship.
- **Research-breadth floor** at **Phase 3b** (`validate-research-bundle.py`) — the
  bundle's event corpus must span ≥N domains / ≥M distinct events for panoramic
  formats (Rewind, Year-in-Review). An under-researched retrospective fails here,
  before writing, like an under-sourced Deep Dive (handoff §8d).

### Pillar D — A real quality signal (replaces the toothless holistic read)
Phase 9.5 becomes a **structured, independent, rubric-scored read**, not one vibe
judgment:
- Run it as a **fresh reviewer subagent** (a reader who did NOT write the issue —
  Opus, per the model-floor rule), given a **concrete rubric** and required to
  return **structured output**: a pass/fail per rubric dimension plus a specific,
  located defect list. Rubric dimensions (score each, cite evidence):
  1. **One-sitting coherence** — does it read as a single Sunday sit-down with a
     throughline, or a pile of sections?
  2. **No repetition / each section earns its place** — is anything said twice;
     does any section fail to add?
  3. **Answers landed** — leads deliver, no hedging/hollow connective sentences.
  4. **Voice** — The Letter is a person; no mechanical tics.
  5. **Service** — at least one concrete "Do This Week" the reader can act on.
- The reviewer's structured defect list is the **input to the repair loop** (§E),
  not advice to a human. A `fail` on dimension 1 or 2 blocks publish and triggers
  targeted repair.
- Keep it honest: the reviewer must *quote* the offending text for each defect
  (same discipline as the no-taste rule), so "looks fine" can't pass a bad issue.

### Pillar E — The bounded verify → auto-repair loop (the core; replaces human back-and-forth)
Wrap Phases 7–9.5 in an explicit loop the orchestrator runs autonomously:
```
build the issue
for round in 1..MAX_REPAIR_ROUNDS:      # MAX ≈ 3–4 ("within reason")
    run ALL gates: structural (B), content-quality (C), image chain,
                   markup, + the rubric read (D)
    collect the located defect list (union of all failures)
    if no defects: break            # clean → eligible to publish
    dispatch TARGETED repair for each defect class:
       - structural  → re-plan against the skeleton / re-stitch
       - repetition  → regenerate the offending sections with a
                       "these facts are already used elsewhere" exclusion list
       - thin corpus → re-open research at the right altitude (Pillar C/§8d),
                       then re-plan
       - scaffold    → strip/fill the leaked tokens
       - images      → auto-repair-images.py (existing round 0)
       - quality     → regenerate the specific weak chapter per the rubric note
    re-stitch
```
Each repair is **surgical** (regenerate the failing chapter/section, not the whole
issue) so rounds are cheap and converge. Log each round to the quality log
(`log-quality.sh`) so convergence is measurable. This is the mechanism that turns
"reader finds it broken → back-and-forth → skip the week" into "the pipeline fixes
itself before Sunday."

### Pillar F — Mechanical publish gate + golden-issue regression
- **Publish receipt (mechanical, outside the prompt).** Phase 10 writes a
  machine-readable `build-receipt.json` (which gates ran, exit codes, repair
  rounds, final verdict). The **publish step** (`post-publish.sh` / the CI
  workflow `.github/workflows/issue-validation.yml`) refuses to commit/announce an
  issue whose receipt is not all-green. This closes root cause #4 — a bad issue
  cannot ship even if the orchestrator's prompt-honour is bypassed (as the Rewind
  was). No `--skip-*` past a real failure on the publish path.
- **Golden-issue regression.** Commit a fixed research bundle fixture + expected
  structural assertions; a CI job (or a `make verify-generator`) generates against
  it and asserts the skeleton + gates. Run it on any spec/skeleton change so
  regressions are caught before Sunday, not by the reader (root cause #6).

---

## 6. Publish policy (resolving deliver-vs-quality, per the owner)

The loop (§E) makes a clean issue the overwhelming common case. For the residual,
tier the fallback by **defect severity**, so the reader is protected but the slot
is still (almost always) filled:

- **Hard-safety failures** (broken images, broken markup, structural mismatch,
  leaked scaffolding, or a quality-read fail on **coherence/repetition**): these
  are the failures that make an issue *embarrassing to open*. After
  `MAX_REPAIR_ROUNDS` unresolved → **do NOT publish**; hold the issue and send the
  owner a **push notification** ("this week's issue needs a look — held, not
  shipped") with the receipt. Better silent than broken — this is the "quality is
  paramount" side.
- **Soft residuals only** (all hard gates green; the rubric flags a minor,
  non-repetition weakness after the loop): **deliver** the best version on time
  (the "reader needs it" side), and record the residual in the build log only (not
  surfaced to the reader). The Sunday slot is filled with a solid — if not
  perfect — issue.

Tune `MAX_REPAIR_ROUNDS` (≈3–4) and the severity split so holds are rare. The
notification path already exists (the significance-push plumbing / VAPID); reuse
it for the "held" alert. Never make the reader the editor: the only reader-facing
action is an optional "held — regenerate now?" nudge, never a diagnosis.

---

## 7. Reconciliation with the three-gate ledger (§5 of the recommendations)

The July rebuild collapsed the compliance scripts to **three ship-quality gates**
(image chain · markup contracts · one holistic read) to stop *soft-compliance-script
accretion*. This rebuild **honours that spirit** and does not reintroduce the
retired soft gates (topic-lock, prose-rhythm, etc.). It reconciles as follows:
- **Structure becomes deterministic (Pillar A/B), not a new gate.** You cannot
  "fail" a structure you did not author; the skeleton + stitcher enforce it by
  construction. The structural *check* is an assertion **inside gate 2 (markup
  contracts)** — the ledger already folds "structural/markup" there.
- **The content-quality checks (Pillar C) fold into gate 2** (scaffold/placeholder,
  repetition = a markup/rendering-integrity concern) **and Phase 3b** (research
  breadth = an upstream production aid, not a ship gate).
- **Gate 3 (the holistic read) gets teeth (Pillar D)** — it becomes the real
  quality signal the ledger *intended* it to be ("did this issue add up"), just
  made structured, independent, and repair-driving instead of a lone vibe check.
- **Net: still three ship-quality gate *categories*.** The reliability comes from
  determinism + a real quality signal + a bounded repair loop + a mechanical
  publish receipt — not from a pile of new compliance scripts. The retired gates
  stay retired.

---

## 8. Also fix (from the 2026-07-12 handoff — this rebuild is the vehicle)
- **Weekly structure** (handoff §1–7) → Pillars A/B make it unrepresentable.
- **Rewind repetition + thin pool** (handoff §8a/§8d) → Pillar C research-breadth
  floor + the repetition detector + the Rewind's own retrospective research mode
  (fresh 6-month-altitude research, NOT re-mining the weeklies — see handoff §8d as
  corrected).
- **Placeholder/spec-text leak** (§8b) → Pillar C scaffold detector.
- **Shipped-despite-failing-gate** (§8c) → Pillar F mechanical publish receipt.
- **Spec contradictions** (Bookmark vs Shelf, §4) → resolve as part of authoring
  the format skeleton (Pillar A makes the skeleton the single structural truth).

---

## 9. Suggested implementation order (highest reliability-per-effort first)
1. **Pillar F publish receipt** — cheapest, stops bad issues shipping *today*
   (mechanical gate on publish; no more Rewind-style bypass).
2. **Pillar A weekly skeleton + Pillar B structural gate** — kills the structural
   failure class; restore `validate-chapter-plan.py` to blocking against the
   skeleton.
3. **Pillar C checks** — repetition + scaffold detectors, research-breadth floor.
4. **Pillar E repair loop** — wire the targeted repair around the gates + reviewer.
5. **Pillar D structured reviewer** — the real quality signal (can land alongside
   E; E needs D's defect list to repair against, so build D's schema first).
6. **Golden-issue regression (F)** + **spec de-contradiction / skeletonise the
   other formats**.

## 10. Relevant paths (for the implementer)
- Pipeline + gate discipline: `.claude/skills/the-signal/SKILL.md` (Phase 0→10;
  the loop wraps 7–9.5; Step Zero model floor still applies).
- Structure source of truth (new): `references/format-skeletons/weekly.json`;
  planner (`validate-chapter-plan.py`), stitcher (`scripts/stitch-issue.sh`),
  structural gate (`scripts/validate-issue.py`) all read it.
- Gates: `scripts/validate-issue.py`, `scripts/validate-research-bundle.py`,
  `scripts/validate-chapter-plan.py`, `scripts/check-image-diversity.sh`,
  `scripts/auto-repair-images.py`.
- Quality log: `scripts/log-quality.sh`, `scripts/render-quality-page.py`.
- Publish/CI: `scripts/post-publish.sh`, `.github/workflows/issue-validation.yml`,
  `.github/workflows/notify-on-publish.yml`.
- Spec (edit source, re-slice): `references/editorial-spec.md` → `slice-spec.sh` →
  `references/spec/*.md`; `references/compliance-checklist.md`.

**One-line summary for the implementer:** make the weekly's structure a
deterministic skeleton the planner/stitcher fill (so it can't come out malformed),
give quality a real rubric-scored independent read, wrap the gates in a bounded
targeted auto-repair loop that runs before the reader, and gate publish on a
machine-checkable receipt — so a good issue is delivered every Sunday without the
reader ever acting as editor, and a broken one is held-and-flagged rather than
shipped.
