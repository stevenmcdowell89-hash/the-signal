# THE SIGNAL — DESIGN SYSTEM UNIFICATION · PROGRESS LOG (v2 engagement)

Companion to `docs/design-system-unification-SPEC-2026-07-18.md` (v2, the binding
contract). This log records, per work package: what shipped, gate evidence (ledger
links), decisions taken where the spec was silent, and honest known gaps. A gate
claim with no ledger entry is by definition false (Part 6 §1).

Evidence ledger root: `docs/design-system-unification-EVIDENCE/`

## Standing orchestration decisions (recorded 2026-07-19, session start)

1. **Prior attempt branch** (`claude/design-system-unification-phase-0-qo2f9s`):
   per owner directive ("nothing done before is reusable") this engagement treats
   the branch as a source of **negative fixtures and audit material only**. No
   code, CSS, tooling, or validator work is carried forward; everything is built
   fresh on this branch and must pass the WP-0 gate suite on its own.
   Staged fixtures:
   - `tools/fixtures/negative/attempt2-stub-flat-season-review.html` — the
     attempt-2 Season Review (F-18 stub / F-19 false greens / F-20 flat boxes).
   - `tools/fixtures/negative/attempt2-flat-redress-deep-dive.html` — the
     attempt-2 flat DD re-dress ("load of squares").
   - `issues/signal_rewind_2026-07-12.html` — live archive file carrying a
     literal `Issue #[N]` (F-14); used in place as a known-bad calibration input.
2. **Owner checkpoints #1 (WP-2) and #2 (WP-7)** conflict with the owner's
   session directive "no feedback from me until done". Resolution: checkpoint
   materials (before/after screenshots, cover + mid-scroll shots) are produced
   exactly as specified, committed to the ledger at the checkpoint moment, and
   flagged in this log — but the engagement proceeds without blocking on
   sign-off. Both checkpoint packets are presented to the owner in the final
   report for retroactive sign-off. This is the only spec deviation, and it is
   owner-directed.
3. **Builder/verifier separation** is enforced via separate subagents; the
   orchestrator commits all work (builders never run git) and spot-checks per
   Part 5 §6.
4. **Publication continuity:** no live publish occurs from this engagement
   without the full gate suite green; the 19-July weekly already shipped on the
   old system before this session.

## False greens

(none recorded)

---

## WP-0 — Gates first — IN PROGRESS (2026-07-19)

- Builder A (measurement harness: `tools/measure-issue.mjs`, `tools/render.mjs`,
  smoke runs) — running.
- Builder B (validate-issue.py wiring: F-14 scaffold + strategy vocab, Law-3
  floors, Law-9 voices, F-16; phase-0 hygiene: TEST files, F-17
  image-source-types, format vocabulary) — running.
- Gate: pending. Will be run by a fresh verifier subagent (never the builders),
  with negative-fixture verdicts committed under
  `docs/design-system-unification-EVIDENCE/WP-0/`.
