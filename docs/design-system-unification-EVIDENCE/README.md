# The Signal — Design System Unification: Evidence Ledger

This directory is the **evidence ledger** for the unification engagement
(SPEC `docs/design-system-unification-SPEC-2026-07-18.md`, Part 6).

> **A gate claim with no ledger entry is by definition false.** (Part 6 §1)
> Density, distribution, word counts, overlap, truncation, and motion are
> **measured** by `tools/measure-issue.mjs` and committed here — never asserted
> from a subagent's prose estimate (Part 6 §2).

## Layout

```
design-system-unification-EVIDENCE/
  README.md                  ← this file (ledger contract)
  negative-fixtures/         ← retained bad artifacts + their fail-map (Part 6 §4)
  wp-0/ … wp-9/              ← one directory per work package
    calibration/             ← reference/known-good metrics (wp-0 holds countdown baseline)
```

### What each `wp-N/` directory holds

Per work package, as its gate runs produce them:

- **screenshots/** — harness-produced (`tools/render.mjs`), **all depths, never
  curated**: both widths (1440×900 + 390×844), 8 smooth-scroll depths, cover,
  one dark render. Hand-picking frames is a protocol violation (Part 5 §1).
- **metrics.json** — `tools/measure-issue.mjs` output: words, events/screen,
  longest zero-event run, chrome-overlap, h-scroll, table-truncation, motion.
- **validator outputs** — `validate-issue.py` / `validate-chapter-plan.py`
  run logs for the WP's candidate artifact(s).
- **parity-scorecards/** — Part 5 design-parity gate scorecards (twelve Laws,
  PASS/FAIL with quoted visual evidence per score; verifier ≠ builder).
- **owner-checkpoint/** — checkpoint records where the WP requires sign-off
  (OWNER CHECKPOINT #1 at WP-2, #2 at WP-7).

## Rules of the ledger (Part 6)

1. **Measured, never asserted** — the numbers come from the tools, committed here.
2. **Builder ≠ verifier** — the subagent that built a WP never runs its gate;
   verifiers receive only the Part 5 inputs.
3. **Negative fixtures forever** — every WP gate re-runs the retained bad
   artifacts in `negative-fixtures/`. If any negative fixture ever PASSES any
   gate, STOP: the gate regressed and all PASSes since its last calibration are
   void.
4. **False-green protocol** — any PASS later shown false voids its WP gate,
   forces a fresh-subagent re-run of that WP's full gate plus a fresh-subagent
   audit of every prior WP's ledger, and is recorded under "False greens" in
   PROGRESS. Hiding one is the terminal offense against the spec.

## Current contents

- `wp-0/calibration/countdown.metrics.json` — known-good baseline: the countdown
  reference measures **2.11 ev/screen** desktop. If a tool cannot see the
  countdown's density, the tool is wrong and must be fixed before it gates
  anything (SPEC WP-1 gate).
- `negative-fixtures/` — the four WP-0 calibration fixtures and their
  fixture→gate→verdict map. See `negative-fixtures/README.md`.
