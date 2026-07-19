# WP-1 — FROZEN REFERENCE PACKS: BASELINES

**Date:** 2026-07-19 · **Branch:** `claude/design-system-unification-orchestrate-fauubj`
**Produced by:** `tools/render.mjs` + `tools/measure-issue.mjs` (the WP-0-gated harness, unmodified), foreground runs on this branch. Every number below is copied from the committed `metrics.json` files in this directory — nothing is a prose estimate (Part 6 §2). Screenshots are uncurated harness output at fixed depths.

| Reference | Source file | Pack |
|---|---|---|
| Countdown | `issues/signal_countdown_2026-06-14.html` | `references/countdown/` |
| Field Guide | `issues/signal_field-guide_2026-05-17.html` | `references/field-guide/` |
| Mockup | `docs/mockups/unification-furniture-kit-mockup.html` | `references/mockup/` |

---

## FROZEN — read this first

**These packs are FROZEN.** Parity verifiers (Part 5) receive them read-only as the standard of comparison, forever. Regenerating, replacing, or editing any file in `references/` requires an explicit orchestrator decision recorded in `docs/design-system-unification-PROGRESS.md`. A parity run against a silently regenerated pack is invalid.

---

## Baseline table (from `<ref>/metrics.json`)

| Reference | Viewport | Body words | Screens | Events | Ev/screen | Words/screen | Longest 0-event run | Dist FAIL (run≥3) | Chrome overlap | Table trunc | Doc h-scroll | Motion elems | Reduced-motion elems |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| countdown | 1440×900 | 6,616 | 54.42 | 95 | **1.75** | 121.6 | 1 | no | **FAIL** (4 pairs) | ok (0) | ok | 185 | **3** |
| countdown | 390×844 | 6,616 | 81.88 | 94 | 1.15 | 80.8 | 2 | no | **FAIL** (12 pairs) | ok (0) | ok | 187 | **3** |
| field-guide | 1440×900 | 14,497 | 72.05 | 105 | **1.46** | 201.2 | **5** | **yes** | ok (0 pairs)¹ | ok (0) | ok | 913 | 0 |
| field-guide | 390×844 | 14,497 | 133.30 | 105 | 0.79 | 108.8 | 4 | **yes** | **FAIL** (14 pairs) | ok (0) | ok | 913 | 0 |
| mockup | 1440×900 | 1,279 | 8.91 | 19 | **2.13** | 143.6 | 0 | no | ok (0) | ok (0) | ok | 0² | 0 |
| mockup | 390×844 | 1,279 | 12.74 | 19 | 1.49 | 100.4 | 1 | no | ok (0) | ok (0) | ok | 0² | 0 |

Events by type (identical at both widths unless noted):

| Reference | figure | ephemera | ledger | statband | quote | plate | chart | marquee | cheatsheet |
|---|---|---|---|---|---|---|---|---|---|
| countdown | 55 | 19 | 1 | 2 | 7 | 7 | 2 (1 @390)³ | 1 | 1 |
| field-guide | 53 | 12 | 23 | 3 | 3 | 4 | 0 | 5 | 2 |
| mockup | 8 | 2 | 4 | 2 | 0 | 3 | 0 | 0 | 0 |

¹ The WP-0 smoke run recorded chrome-overlap FAIL for field-guide @1440; this frozen run records 0 pairs. Overlap @1440 on the field guide is run-sensitive — the smoke finding was a caption/chrome intersection caught mid-reveal at one of the 10 sampled depths. The @390 FAIL (back pill / folio over content, 14 pairs) is stable and is the review-documented true finding. Treat field-guide 1440 overlap as borderline-transient, 390 overlap as a hard reference fact.
² The mockup is a static docs file with no JS and no CSS scroll animation — 0 motion elements is a true measurement, not a tool failure. Motion norms are demonstrated by the two shipped references, not by the mockup.
³ Chart census (svg/canvas ≥200×120 px) loses one countdown chart below the size gate at 390. Quote-object census here is Law-2 (named source present); Law-9 lane policing is the validator's job.

## Comparison against Part 1 / review expectations

| Check | Expected | Measured | Delta | Verdict |
|---|---|---|---|---|
| **WP-1 gate: countdown ≥1.5 ev/screen @1440** | ≥1.5 (review hand-measured **1.69**) | **1.75** | +0.06 vs hand count | **PASS** |
| Field guide ev/screen @1440 | ~**1.06** (review hand count) | **1.46** | **+0.40** — at the ±0.4 tolerance edge | recorded, explained below |
| Mockup | no prior baseline exists | 2.13 @1440 / 1.49 @390 | — | **this table BECOMES the baseline** |
| Countdown words/screen | 139 (review, from screenshots) | 121.6 | −17 | consistent direction (fallback fonts, below) |
| Field guide words/screen | 209 (review) | 201.2 | −8 | within noise |
| Reproducibility vs WP-0 smoke (countdown, field-guide) | smoke values | words/events/ev-screen/zero-runs identical to `WP-0/smoke/SUMMARY.md` | 0.00 on all structural metrics | exact |

**The +0.40 field-guide delta, explained (tool vs hand count):** (a) the heuristic census counts each of the field guide's 23 ledger blocks and 53 figure objects individually, where the review's screenshot hand-count grouped composite spreads as single "events"; (b) external fonts are aborted by the harness, so the page lays out in fallback fonts — the page is shorter, screens fewer, ev/screen higher. Both effects push the tool's number up uniformly across runs: WP-0 smoke measured the identical 1.46, and this run reproduces every smoke structural metric exactly. The tool is self-consistent; the delta is census-methodology + font-metrics, not drift. Candidates at parity gates are measured by the same tool with the same census, so comparisons are like-for-like.

**True reference findings preserved (documented in WP-0, reproduced here):**
- Countdown violates reduced motion: 3 elements (`hol-shimmer` heat-haze, ungated — `tools/README-measure.md`). The unified system must gate every animation (Law 5).
- Field guide has a real 5-screen zero-event run @1440 (closing "Meanwhile…" prose digest) — the reference itself fails Law-2 distribution there. References set the *craft* bar; their known flaws are documented, not emulated. The unified system must beat the references on these, not merely match them.
- Countdown back-pill/folio chrome overlaps at both widths (no hide-on-scroll) — why Law 10 demands reserve-or-hide chrome in the new system.

## File census (sanity check)

Expected per pack: `metrics.json` + `render/1440/cover.png` + `render/1440/depth-0..7.png` (8) + `render/390/cover.png` + `render/390/depth-0..7.png` (8) + `render/dark-1440.png` + `render/render-manifest.json` = 21 files.

| Pack | Files present | Missing |
|---|---|---|
| countdown | 21/21 | none |
| field-guide | 21/21 | none |
| mockup | 21/21 | none |

57 PNGs total; every expected file exists and is non-zero. Mockup renders verified visually (e.g. `mockup/render/1440/depth-2.png`: taped index cards, CSS coin roundel, sourced Judith Herrin quote-object on a plum gradient scene ground) — its asset paths resolve correctly under the harness's repo-root HTTP server.

### Known anomaly — blank depth frames (honest list; Law 12)

10 of the 48 depth PNGs are solid-background blanks:

- `countdown/render/1440/depth-0.png`, `countdown/render/390/depth-0.png`
- `field-guide/render/1440/depth-0.png`, `field-guide/render/1440/depth-3.png`
- `field-guide/render/390/depth-0,2,3,5,6,7.png` (6 of 8 — worst case)
- mockup: none.

**Cause (probed, not guessed):** `render.mjs` shoots each depth 450 ms after an instant `scrollTo` jump. Both reference pages re-run reveal-on-scroll transitions after a teleport jump, and their safety force-reveal fires at ~2.6 s — so a 450 ms shot at an unlucky depth catches content at opacity 0. Probe evidence (WP-1 builder scratchpad, reproduced twice, byte-identical): countdown 1440 y=0 shot at +450 ms = 5,854 B blank; the same position at +3.45 s = 240,859 B — exactly the size of the fully-rendered `cover.png`. Field-guide 390 y=47856: 2,742 B blank at +450 ms → 84,464 B rendered at +3.45 s. **The content is really on the page; the blanks are a harness settle-time transient.** The blanks are deterministic (byte-identical to the WP-0 smoke run's), so the packs are reproducible as-is.

**Impact & recommendation:** metrics are unaffected (measure-issue samples during/after the smooth pass, and this run reproduces smoke exactly). For *visual* parity comparison, countdown 1440 loses 1 of 8 depths and field-guide 390 loses 6 of 8 — verifiers doing Law 1/2/4/7 side-by-sides at 390 should lean on `field-guide/render/390/cover.png`, `depth-1`, `depth-4`, and the 1440 set. If the orchestrator wants full 390 coverage, the fix is a one-line settle bump (~3,000 ms) in `render.mjs` post-jump wait + a recorded-in-PROGRESS regeneration decision — these packs stay frozen until that decision is made.

## Regeneration record (2026-07-19, orchestrator decision)

All three render packs (+ the stub negative-fixture pack) were regenerated ONCE
after the WP-1 builder's anomaly finding: render.mjs's 450ms post-jump settle
undershot the pages' ~2.6s reveal safety-net, leaving 10/48 depth frames blank.
Fix: settle raised to 3000ms (tools/render.mjs, commented). Post-regeneration
census: zero depth frames under 20KB; previously-blank field-guide 390/depth-5
opened by the orchestrator and confirmed fully rendered. metrics.json files were
NOT touched (measure-issue.mjs uses its own smooth-scroll pass and was correct
throughout). Packs are FROZEN from this point.
