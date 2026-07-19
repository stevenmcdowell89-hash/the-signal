# WP-0 GATE — INDEPENDENT VERIFICATION VERDICT

**Verifier:** independent WP-0 gate verifier (not the builder; Part 6 §3) · **Date:** 2026-07-19
**Branch:** `claude/design-system-unification-orchestrate-fauubj` @ `b9d8cfc`
**Method:** every number below was re-produced by the verifier's own foreground runs (validator + `measure-issue.mjs`); nothing was trusted from committed evidence until reproduced. Fresh harness output kept at the verifier scratchpad (`verify/countdown/metrics.json`, `verify/stub/metrics.json`).

Gate criterion under test (Part 4, WP-0): *"every tool runs on both a known-good reference (countdown) and every negative fixture with correct verdicts, output committed"* — plus Part 6 §4 (a gate that has never failed anything is unproven).

## 1. Validator runs (fresh, this verifier, full network checks — no `--skip-image-urls`)

| # | File | Expected | Observed (fresh run) | Verdict |
|---|---|---|---|---|
| 1 | tools/fixtures/negative/attempt2-stub-flat-season-review.html | exit 1; Law-3 (542 < 6,500), Law-9 voices 0 < 5, self-quote cap, strategy-vocab "FURNITURE-FIRST" | exit 1, 5 FAILs: `law3-word-floor` (542 < 6,500), `law9-voices` (0 < 5), `law9-self-quotes` (2 > 1), `f14-strategy-vocab` (FURNITURE-FIRST ×1), `special-variety` | **PASS** |
| 2 | tools/fixtures/negative/attempt2-flat-redress-deep-dive.html | exit 1; at least the self-quote cap | exit 1, 2 FAILs: `law9-self-quotes` (6 > 1), `image-urls` (18/18 local files missing — fixture sits outside `assets/`); law3 passes at 18,861 wds, law9-voices passes at exactly 5 | **PASS** |
| 3 | issues/signal_rewind_2026-07-12.html | exit 1 on `Issue #[N]` scaffold token | exit 1; `f14-scaffold-tokens` (issue-number-placeholder ×1, 'Issue #[N]') + pre-existing `image-urls-static` | **PASS** |
| 4 | issues/signal_deep-dive_2026-05-26.html | exit 1 on ch-token/viz/research-bundle leaks | exit 1; `f14-scaffold-tokens` (ch-tokens ×27, viz_ ×5, "research bundle" ×5) + pre-existing `length-ceiling` | **PASS** |
| 5 | issues/countdown-wcq.html | exit 1 on tool-credit leak | exit 1; `f14-scaffold-tokens` ('Created with Perplexity Computer' ×2) + 9 pre-existing weekly-structure/visual/image FAILs | **PASS** |
| 6 | issues/signal_weekly_2026-07-19.html | exit 0 | exit 0 — all 25 checks PASS | **PASS** |
| 7 | issues/signal_weekly_2026-07-13.html | exit 0 | exit 0 — all checks PASS | **PASS** |
| 8 | issues/signal_countdown_2026-06-14.html | exit 0; legacy CDN credits warn-only | exit 0; `f14-cdn-hostnames` correctly WARN-only ("legacy issue — warning only": cdn.libemaweb.com, content.presspage.com) | **PASS** |

All eight verdicts landed exactly as the gate requires. Every new gate has demonstrably failed at least one real artifact (Part 6 §4 satisfied).

## 2. Measurement harness — fresh re-runs vs committed evidence

Re-measured by this verifier with `node tools/measure-issue.mjs … --out <scratchpad>` (foreground, own runs):

| Metric | Fresh (verifier) | Committed (smoke/) | Match |
|---|---|---|---|
| countdown 1440: words / events / ev-screen / screens / zero-run | 6,616 / 95 / **1.75** / 54.42 / 1 | 6,616 / 95 / 1.75 / 54.42 / 1 | exact |
| countdown 1440: overlap fails / trunc / h-scroll / reduced-motion | true / false / false / **3** (`hol-shimmer` on heat-haze) | true / false / false / 3 | exact |
| countdown 390: words / ev-screen / zero-run / overlap / trunc | 6,616 / 1.15 / 2 / true / false | same | exact |
| countdown 1440 motion elements | 183 | 38 | declared-nondeterministic (see §4) |
| countdown 390 motion elements | 187 | 187 | exact |
| stub 1440: words / events / ev-screen / overlap / trunc / motion | **526** / 16 / 2.99 / **true** / false / **0** | 526 / 16 / 2.99 / true / false / 0 | exact |
| stub 390: words / ev-screen / overlap / trunc / motion | 526 / 2.7 / **true** / **true** / 0 | same | exact |

Gate expectations all confirmed by fresh measurement: countdown ev/screen @1440 = 1.75 ≥ 1.5; stub = 526 body words; stub chromeOverlap.fails = true at BOTH widths; stub tableTruncation.fails = true @390; stub motion.animatedElements = 0 at both widths. No density divergence (all Δ = 0.00), no verdict flips.

Not re-measured (out of the two-target minimum): flat-redress and field-guide. Their SUMMARY.md rows were cross-checked against their committed `metrics.json` — every cell matches (flat-redress 18,260/18,335 wds, 0.79/0.50 ev/screen, zero-runs 3/6, overlap+trunc FAIL @390 only; field-guide 14,497 wds, 1.46/0.79, zero-runs 5/4, 913 motion elems, reduced 0).

## 3. Screenshot audit (6 committed renders opened)

- `smoke/countdown/render/1440/cover.png` — real render: indigo-night poster cover, arc "GREETINGS FROM" type, sun illustration, castle silhouette, flip-clock 00s. Not blank.
- `smoke/countdown/render/390/depth-3.png` — real mid-scroll capture: rotated polaroid with hand caption + credit crossing an act boundary (cream→indigo). Reveal content fired (smooth-scroll pass worked).
- `smoke/countdown/render/dark-1440.png` — renders (page is natively dark; visually similar to light cover, as expected).
- `smoke/attempt2-stub-flat-season-review/render/1440/depth-2.png` — confirms F-20: upright hairline rectangles ("THE 48-TEAM FORMAT" box, flat rules), flat single-color ground, no rotation/fastener/shadow anywhere.
- `smoke/attempt2-stub-flat-season-review/render/390/depth-4.png` — **back pill visibly overlapping** the "INTERMISSION" band text — the committed overlap FAIL is real, on-screen.
- `smoke/attempt2-stub-flat-season-review/render/390/cover.png` — pill over cover; cover meta literally prints "FURNITURE-FIRST", corroborating the validator's strategy-vocab FAIL.

All opened screenshots are genuine rendered pages; the stub's set visibly shows the flat boxes and the overlapping pill.

## 4. Evidence-doc audit (SUMMARY.md, validator-calibration.md, README-measure.md)

Claims checked line-by-line against this verifier's own runs:

| Claim | Check | Result |
|---|---|---|
| SUMMARY table rows (all 8) | fresh runs (countdown, stub) + metrics.json cross-check (other two) | all numbers correct |
| SUMMARY: "review hand-measured 1.69" for countdown | `docs/special-editions-review-2026-07-18.md` line 49 | present, matches |
| README: countdown violates reduced-motion, 3 elements, `hol-shimmer` on heat-haze | fresh `reducedMotion` census | confirmed: exactly 3, `hol-shimmer`, `.theme-heat-haze`/`hol-half--two` |
| README: field guide 5-screen zero-event run @1440 | committed field-guide metrics.json | confirmed (5) |
| Calibration: flat-redress "passed everything at HEAD" (F-19 in miniature) | re-ran the pre-WP-0 validator (`git show e6fce5f:…validate-issue.py`) on the fixture with `--skip-image-urls` | confirmed: exit 0, "2 warning(s). PASS." — now exit 1 |
| Calibration: `validate-chapter-plan.py --test` 57/57 | ran it | confirmed: "57/57 tests passed. PIPELINE TEST: PASS" |
| Calibration: TEST files deleted (WP-0e) | `ls issues/ | grep -i TEST` | confirmed: none |
| Calibration per-file verdict table (8 files in my scope) | fresh runs | failure sets match exactly (e.g. countdown-wcq 9 pre-existing + 1 new = 10 observed) |

**Discrepancies found:**

1. **Stale filename in tools/README-measure.md (~line 147):** cites `docs/design-system-unification-EVIDENCE/WP-0/smoke/SMOKE-RESULTS.md`; no such file exists — the committed summary is `smoke/SUMMARY.md`. The referenced content exists and its numbers are correct; only the pointer is wrong. Graded a documentation defect, not an F-19 false-evidence claim: no measurement, verdict, or gate outcome is misrepresented, and the intended referent was located and verified true. **Should be fixed (one-line edit) before WP-1.**
2. **Countdown 1440 motion element count nondeterminism:** committed 38 vs fresh 183. Both README-measure.md ("counts can wobble") and SUMMARY.md ("countdown 38 vs 186 @1440 across runs; treat counts as ordinal, not exact") disclose exactly this. Presence/absence verdict (motion > 0) is stable; not a finding against the evidence.
3. Word-count deltas between validator (542) and harness (526) for the stub, and validator (18,861) vs harness (18,260) for the flat-redress, are explained methodology differences (harness excludes chrome; validator's floor errs lenient) and are disclosed in the calibration doc's limitations. Not findings.

No false metric, no false verdict, no unverifiable substantive claim was found in any of the three audited documents.

## 5. Negative-control of the validator (synthetic, this verifier)

- **Synthetic `data-mx` season-review** (208 words, zero quotes, one external `<img src="https://…">`): exit 1, failing `law3-word-floor` (208 < 6,500), `law9-voices` (0 < 5), and `f16-external-img-src` (1 external src) — each for exactly the right reason.
- **Identical file WITHOUT `data-mx`** (legacy path): `law3-word-floor`, `law9-voices`, `f16-external-img-src` did NOT fire despite 208 words / zero quotes / external img — legacy exemption works as designed (fails only on back-link + special-variety, unrelated legacy checks).

## 6. Verdict

Every prescribed check landed exactly as expected: 8/8 validator verdicts correct; both fresh harness runs reproduce the committed metrics with zero divergence on all structural numbers; the committed screenshots are real and visibly show the failures the metrics claim; every audited evidence claim reproduced true; the validator demonstrably fails a fresh synthetic bad artifact for the right reasons while exempting legacy files as designed; and the pre-WP-0 validator's false-green on the flat-redress fixture (exit 0 → now exit 1) proves the new gates catch something the old ones did not.

One documentation defect (stale `SMOKE-RESULTS.md` filename in README-measure.md) is recorded above and should be corrected; it misdirects a reader to a wrong path but misrepresents no evidence and does not touch the gate criterion.

**WP-0 GATE: PASS**
