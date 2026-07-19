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

## WP-0 — Gates first — ✅ GATE PASS (2026-07-19, independent verifier)

**Shipped:**
- `tools/measure-issue.mjs` + `tools/render.mjs` + `tools/lib/` (Builder A):
  HTTP-served, SW-blocked, both viewports, smooth-scroll; Law-2 event census
  (heuristic selector map + `[data-mx-event]` support); distribution,
  chrome-overlap, h-scroll (real-scroll test, not scrollWidth inflation),
  mid-word truncation, motion + reduced-motion census. Docs:
  `tools/README-measure.md`.
- `validate-issue.py` extensions (Builder B): F-14 scaffold + strategy
  vocabulary (visible prose only), Law-3 floors / Law-9 voices / F-16 for
  `data-mx` issues; hygiene: TEST files deleted, F-17 `restricted` type,
  guide/next/blueprint vocabulary reconciled.
- Negative fixtures staged; smoke sweep committed:
  `docs/design-system-unification-EVIDENCE/WP-0/smoke/SUMMARY.md` +
  `validator-calibration.md`.

**Notable true findings on the references (kept, not suppressed):**
- Countdown violates reduced-motion: `hol-shimmer` heat-haze ungated (3 els).
- Countdown/field-guide chrome-overlap FAILs echo review-documented flaws.

**Orchestrator spot-check:** smoke screenshots opened personally — real
renders; stub's fixed-pill overlap visible at 390/depth-2. Recorded in the
WP-0(a,d) commit message.

**Incidents (process, not evidence):** Builder A repeatedly stalled by
parking work in background waits (68 min lost); orchestrator watcher bug
(`pgrep -f` matching its own command line) hid sweep completion for ~2.5 h.
Mitigation now standing: subagents run measurement in foreground with long
timeouts; no pgrep-based waits.

**Gate:** independent verifier (non-builder) running — re-executes tools
fresh on countdown + stub, revalidates all known-bad/clean files, audits
evidence docs; verdict to `EVIDENCE/WP-0/gate-verdict.md`. WP-0 is not done
until that verdict is PASS.

**Gate verdict:** `EVIDENCE/WP-0/gate-verdict.md` — WP-0 GATE: PASS.
Independent verifier reproduced all 8 validator verdicts, re-ran the harness
fresh (zero structural divergence), audited 6 screenshots + all three evidence
docs, ran synthetic negative controls, and proved the pre-WP-0 validator
false-greened the flat-redress fixture (exit 0 → exit 1 now). One stale
filename pointer in README-measure.md found and fixed post-verdict.

---

## WP-1 — Reference capture — ✅ GATE PASS (2026-07-19)

**Shipped:** frozen reference packs at `EVIDENCE/references/{countdown,field-guide,mockup}/`
(each: metrics.json + cover + 8 depths × both widths + dark render, uncurated
harness output) + `references/BASELINES.md`.

**Gate (verified by orchestrator, non-builder):** countdown @1440 measures
1.75 ev/screen ≥ 1.5 floor (review hand-measure 1.69, Δ+0.06); field-guide
1.46 (Δ+0.40, at stated tolerance edge — tool counts every ranked plate);
mockup 2.13 becomes its own baseline. Orchestrator opened mockup depth-2
personally: real render, objects-on-a-surface standard confirmed.

**Incident:** WP-1 builder agent died after finishing all render/measure runs
but before writing BASELINES.md; orchestrator wrote the summary doc directly
from the committed metrics (mechanical transcription, no builder judgment
involved). Packs are FROZEN from this commit; regeneration requires a
PROGRESS-recorded decision.
