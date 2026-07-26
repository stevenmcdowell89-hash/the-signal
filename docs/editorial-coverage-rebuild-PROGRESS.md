# Editorial Coverage Rebuild — PROGRESS

Build ledger for `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md`.
Each WP appends to its own section. Do not rewrite another WP's entry.

**Status key:** `PENDING` · `IN PROGRESS` · `DONE` · `BLOCKED` · `PARTIAL`

## Ledger

| WP | Title | Status | Defects | Notes |
|----|-------|--------|---------|-------|
| WP-1 | Data contracts (foundation) | PENDING | A B C D E | must land before all others |
| WP-2 | Editorial prose spec | PENDING | A C D E | |
| WP-3 | Structure of record + stitcher + CSS | PENDING | A C D | |
| WP-4 | Rendered-issue checks | PENDING | A B D E | after WP-3 |
| WP-5 | Upstream production aids | PENDING | A C D E | after WP-3 |
| WP-6 | Image taxonomy + specificity doctrine | PENDING | E | |
| WP-7 | Daily inputs | PENDING | D | |
| WP-8 | Asset provenance + licence safety | PENDING | E | |
| WP-9 | Pipeline phase wiring | PENDING | C D | |
| WP-10 | Verification harness | PENDING | all | last |

## Expected-failure ledger

Issue #18 (`issues/signal_weekly_2026-07-26.html`) is the regression fixture and is **frozen**.
These failures are the proof the checks work and are **not** to be repaired.

| Check | Expected on #18 | Recorded |
|-------|-----------------|----------|
| caption-vintage (SPEC §3.9) | FAIL at Long Read FIG 03 — `capture_year` 2007, band claims 2021, year absent from `.plate-cap .txt` | pending |
| image shape budget (SPEC §3.8) | FAIL — Pixel & Byte leads on `key_art`; Long Read carries no `diagram\|map\|chart\|artefact` | pending |
| long-read vintage (SPEC §3.4) | FAIL — no `data-vintage` attribute | pending |

---

## WP-1 — Data contracts (foundation)

_No entries yet._

## WP-2 — Editorial prose spec

_No entries yet._

## WP-3 — Structure of record + stitcher + CSS

_No entries yet._

## WP-4 — Rendered-issue checks

_No entries yet._

## WP-5 — Upstream production aids

_No entries yet._

## WP-6 — Image taxonomy + specificity doctrine

_No entries yet._

## WP-7 — Daily inputs

_No entries yet._

## WP-8 — Asset provenance + licence safety

_No entries yet._

## WP-9 — Pipeline phase wiring

_No entries yet._

## WP-10 — Verification harness

_No entries yet._

---

## Handoff notes

Cross-WP requests land here — a WP that needs a change in a file it does not own records it, and the
orchestrator routes it.

_No entries yet._
