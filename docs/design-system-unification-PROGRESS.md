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

**WP-1 addendum (regeneration decision):** WP-1 builder completed after all and
found 10/48 depth PNGs blank (render.mjs 450ms settle vs ~2.6s page reveal
safety-net). Orchestrator raised settle to 3000ms and regenerated all three
reference render packs + the stub fixture pack once; zero blanks remain
(<20KB census), previously-blank frame visually confirmed real. Recorded in
BASELINES.md. Builder also replaced the orchestrator's minimal BASELINES.md
with its fuller version (numbers identical) — kept.

---

## WP-2 — Furniture core + doc prune — ✅ GATE PASS (2026-07-19)

**Shipped:** css/core/00–15 (79KB, scenography-as-default, mx- neutral) +
01-fonts.css with self-hosted woff2 (pulled forward from WP-3 so Law 8 was
judged on real typography); core-components.md catalog; F-13 doc prune
(zero dead-class refs, slice-spec idempotent); re-dress gate fixtures
(DD 0.98/0.73 ev/screen, countdown 2.13/1.43, both validator-green);
data-mx-aware validator gates (mx-variety, holiday-check skip, data-format
autodetect) with full Part 6 §4 recalibration (all negatives still fail).

**Parity gate (Part 5, fresh verifier, blindfold protocol):**
`EVIDENCE/WP-2/parity-scorecard-dd.md` — WP-2 PARITY: PASS, twelve/twelve
laws, 16 candidate + 8 reference screenshots viewed, true side-by-sides for
Laws 1/2/4/7. Three verbatim questions answered "objects on a surface /
the scroll travels / same magazine's craft".

**Orchestrator spot-check (Part 5 §6):** I opened cover, 1440 depth-2/-3/-4,
390 depth-6, dark-1440 myself. Verdict: the re-dress is unambiguously
objects-on-a-surface — taped/ruled index cards with typewriter fills, the
Great Siege ring-stamp with hand annotation, framed credited figures — on
continuously textured parchment grounds with a real act arc. It reads as the
countdown's craft translated to ink. The verifier's PASS is consistent with
what I saw. One polish note carried to WP-3: dark-mode masthead flips to
cream while the cover act stays dark — token-correct, legible, but review
in the WP-3 dark pass.

**Owner checkpoint #1:** packet committed at `EVIDENCE/WP-2/checkpoint-1/`
(before = shipped DD renders; after = parity candidate). Proceeding per
standing decision #2; retroactive sign-off requested in the final report.

---

## WP-3 — Skins + bundling + dark/print — ✅ GATE PASS (2026-07-19)

Editorial/event/transmission skins (zero :not(), F-8/F-12 fixed in ports),
manifest bundling in stitch-issue.sh (budgets hard-fail: editorial 102.4KB/120,
event 96.5KB/160; one-masthead enforced; legacy glob untouched — archive
pipeline verified working), chrome tokens (dark stays dark), 16-print.css,
network-disabled render zero external requests, weekly golden byte-identical
throughout. Parity gate: event candidate 12/12 PASS first try (judged better
than frozen original on craft; tier2 moments pending WP-5 as scoped);
editorial candidate FAILED first scoring on words/screen 222.7>220 —
remediated with desktop reading air in the skin (219.0), fully re-rendered,
re-scored 12/12 PASS by a fresh verifier (EVIDENCE/WP-3/parity-scorecards.md).
The gate catching a real 1.2% breach and forcing remediation is the system
working as designed.

---

## WP-4 — Motif mechanism + packs — ✅ GATE PASS (2026-07-19)

tools/motif/ (validator: CONTRAST-AA/FONT-WHITELIST/ART-BYTE-CAP/
ACT-ARITHMETIC/CURRENTCOLOR/KIT/MOTION/GRAIN; deterministic renderer with
goldens); 3 reference packs green (trip-efteling from real venue tokens,
matchday-worldcup, dossier-byzantium); stitch PACK= integration. Gate:
pack swap re-themes same fixture, git diff 0 CSS files (orchestrator
re-verified visually); 4 seeded-bad packs reject with named reasons —
retained under tools/fixtures/negative/motif/; packed metrics deltas 0.
Gaps handed to WP-5/6: cover_plate consumer, INJECT marker in scaffold,
act_map, accent-2 contrast pairs.

## WP-5 — Motion — ✅ GATE PASS (2026-07-19)

mx-motion.js (8.2KB, IO-driven, reduced-motion no-op, no scroll-jack)
replaces 96KB legacy script on mx path; tier0/1/2 behaviors + signature
hooks; seam crossfade colors = act tokens. Census: countdown 144/0-reduced,
DD 46/0; JS-off = JS-on word equality; flat negative gains zero mx
animations; weekly golden green. Parity (fresh verifier):
EVIDENCE/WP-5/parity-scorecards.md — BOTH candidates 12/12 PASS; burst
frames at both widths show mid-reveal→settled; body text pixel-static.
Orchestrator spot-check: burst-0/burst-1 opened personally — stamp slam
and polaroid tape-down visibly firing.

---

## WP-6 — Deterministic pipeline — ✅ GATE PASS (2026-07-20)

Skeletons (season-review/deep-dive/versus/rewind) with per-slot Law-2 event
quotas + killer-feature rule lists; validate-chapter-plan 76/76 (planned
density, Law-3 budgets, killer features, personalisation-with-state-evidence,
MX-TIMING — the attempt-#2 before-the-final Season Review is now rejected
with named text, orchestrator-reproduced); stitch_specials.py (writer
interiors only; chrome unrepresentable; per-skin vocabulary gate; pack
cover_plate consumed); publish-gate runs rendered WP-0 gates on data-mx
issues (check-rendered-metrics.py). E2E test Season Review GREEN through
the whole chain incl. post-publish dry-runs (extract-covers + inject-pwa
mx-compat fixes); 7 seeded-bad artifacts rejected. Weekly golden PASS.
Fixture: tools/fixtures/e2e/. Gaps: no skeletons yet for countdown/
field-guide/guide/next (named [MX-SKELETON] reject); per-type census at
plan time only.

## WP-7 — First live special — IN PROGRESS (2026-07-20)

Target: Season Review of the 2026 FIFA World Cup (concluded 2026-07-19:
Spain 1–0 Argentina aet, Torres 106') — publish 2026-07-20. Real research
bundle via web; matchday kit + matchday-worldcup pack; furniture-first.
To follow: dual independent parity verifiers, orchestrator ≥6-shot
spot-check, owner checkpoint #2 packet, publish decision per standing
decision #2 + the owner's prior live-cutover override.
