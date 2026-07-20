# WP-9 — INDEPENDENT CLOSEOUT AUDIT REPORT

**Auditor:** WP-9 independent closeout auditor (built none of this).
**Date:** 2026-07-20
**Branch:** `claude/design-system-unification-orchestrate-fauubj`
**Method:** Part 6 §5 audit + WP-9. Every check below was **reproduced**, not trusted —
tools re-run fresh, screenshots opened, numbers recomputed. No commits/push. Foreground only.

**Bottom line:** No false greens. Every negative fixture still FAILS, every clean
control / golden / live publish-gate PASSES, every screenshot is a real render matching
its scorecard claim, and the spot-checked PROGRESS claims reproduce true — **with one
non-blocking documentation-staleness discrepancy** (WP-3's recorded CSS bundle byte
figures are ~5.3 KB below the current tree; both bundles remain comfortably under budget
and the budget gate still passes). Details in Task 7 and the itemized list at the end.

---

## TASK 1 — Negative-fixture suite still bites (Part 6 §4, load-bearing)

Current `validate-issue.py` run on every retained negative fixture. **Each must exit 1.**

| Fixture | Format | Expected | Observed | Verdict |
|---|---|---|---|---|
| `tools/fixtures/negative/attempt2-stub-flat-season-review.html` | season-review | exit 1 | **exit 1** — 5 FAILs: law3-word-floor (542 < 6,500), f14-strategy-vocab (`FURNITURE-FIRST`), law9-voices (0 < 5), law9-self-quotes (2 > 1), special-variety (0 < 5) | ✅ STILL FAILS |
| `tools/fixtures/negative/attempt2-flat-redress-deep-dive.html` | deep-dive | exit 1 | **exit 1** — 2 FAILs: law9-self-quotes (6 > 1), special-variety (0 distinct mx-event types < 6) | ✅ STILL FAILS |
| `issues/signal_rewind_2026-07-12.html` | rewind | exit 1 (Issue #[N]) | **exit 1** — f14-scaffold-tokens: `issue-number-placeholder` (`Issue #[N]`) + image-urls-static (2 extension-less Nintendo URLs) | ✅ STILL FAILS |
| `issues/signal_deep-dive_2026-05-26.html` | deep-dive | exit 1 (ch-tokens) | **exit 1** — f14-scaffold-tokens: `ch1-1…ch2-1` ×27, `viz_1…viz_5`, `research bundle` ×5 + length-ceiling (24,376 > 20,000) | ✅ STILL FAILS |
| `issues/countdown-wcq.html` | countdown | exit 1 (tool-credit) | **exit 1** — f14-scaffold-tokens: `Created with Perplexity Computer` ×2 + holiday-activation/components FAILs | ✅ STILL FAILS |

Seeded-bad motif packs via `tools/motif/validate-motif-pack.py` — **each must exit 1.**

| Pack | Expected | Observed | Verdict |
|---|---|---|---|
| `bad-acts-four.json` | exit 1 | **exit 1** — REJECT [ACT-ARITHMETIC] 4 acts (bar 1–3) | ✅ REJECTS |
| `bad-art-oversize.json` | exit 1 | **exit 1** — REJECT [ART-BYTE-CAP] pattern 16,215 B > 8,192 | ✅ REJECTS |
| `bad-contrast.json` | exit 1 | **exit 1** — REJECT [CONTRAST-AA] #999 on #aaa = 1.23:1 < 4.5 | ✅ REJECTS |
| `bad-font.json` | exit 1 | **exit 1** — REJECT [FONT-WHITELIST] "Papyrus" off-whitelist | ✅ REJECTS |

**Task 1 result: no negative fixture passes. Gate has NOT regressed. All 9 bite.**

---

## TASK 2 — Clean controls still pass

| Issue | Format | Expected | Observed | Verdict |
|---|---|---|---|---|
| `issues/signal_weekly_2026-07-19.html` | weekly | exit 0 | **exit 0** — 1 warning, PASS | ✅ PASS |
| `issues/signal_countdown_2026-06-14.html` | countdown | exit 0 | **exit 0** — 3 warnings (legacy CDN-hostname warns only), PASS | ✅ PASS |

---

## TASK 3 — Goldens

| Check | Expected | Observed | Verdict |
|---|---|---|---|
| `verify-weekly-golden.sh` — legacy weekly golden | pass | stitched, validated, plan-valid | ✅ PASS |
| `verify-weekly-golden.sh` — mx-weekly golden (WP-8) | byte-identical + pass | **byte-identical ✓**, 4 real voices (Zverev/Sinner/Myers/Tuchel), 7,951 w | ✅ PASS |
| script exit | 0 | **GOLDEN REGRESSION PASS, exit 0** | ✅ PASS |
| `render-motif-pack.py --check-golden` trip-efteling | byte-identical | **GOLDEN OK** | ✅ PASS |
| … matchday-worldcup | byte-identical | **GOLDEN OK** | ✅ PASS |
| … dossier-byzantium | byte-identical | **GOLDEN OK** | ✅ PASS |

Both legacy AND mx-weekly goldens pass; all 3 motif goldens byte-identical.

---

## TASK 4 — Live special is real & green (`signal_season-review_2026-07-20.html`)

**publish-gate.sh --format season-review --skip-image-urls → GREEN (exit 0).** Every gate exit 0:
validate-issue (2 warns, PASS), image-diversity (n/a), rendered-measure, rendered-metrics.

**Fresh `measure-issue.mjs` re-run vs committed `EVIDENCE/WP-7/parity-candidate-sr/metrics.json`:**

| Metric | Committed | My fresh re-measure | Match | Threshold |
|---|---|---|---|---|
| ev/screen @1440 | 1.95 | **1.95** | ✅ | ≥ 0.9 ✅ |
| events @1440 | 71 | **71** | ✅ | |
| body words | 7,472 | **7,472** | ✅ | ≥ 6,500 ✅ |
| words/screen @1440 | 204.9 | **204.9** | ✅ | ≤ 210 ✅ |
| chrome-overlap pairs | 0 | **0** | ✅ | 0 ✅ |
| motion census | 140 | **140** | ✅ | > 0 ✅ |
| reduced-motion census | 0 | **0** | ✅ | 0 ✅ |
| h-scroll / truncation | false / 0 | **false / 0** | ✅ | |

Fresh numbers reproduce the committed metrics **exactly**. (validate-issue reports 7,645
Law-3 words — a different, chrome-inclusive counter — likewise clears the 6,500 floor.)

**4 committed screenshots opened (paths `EVIDENCE/WP-7/parity-candidate-sr/{1440,390}/`):**

| Screenshot | What I saw | Verdict |
|---|---|---|
| `1440/cover.png` | Poster cover: dot-grid/starfield ground, ghosted "26" numeral, script "the biggest world cup ever played" + giant chunk "ONE HUNDRED"/outlined "FOUR", gold ampersand, trophy circle. Multi-voice type. | ✅ real poster, not blank |
| `1440/depth-3.png` | Starfield ground; tilted cream **fixture ticket-card** (FIXTURE/DATE/SCORE mono rows, gold spine); "bronze, loudly" hand-annotation **roundel stamp** overlapping the gold display headline "THE TEN-GOAL GOODBYE". | ✅ objects on a surface |
| `1440/depth-5.png` | Act-2 **cream checker ground**; **quote-object** (Scaloni "He is pure history…" + mono attribution); two green/gold **award stamps** ("PERFORMANCE IN DEFEAT", "MATCH OF…"). | ✅ scorecards/quotes real |
| `390/depth-4.png` | Parchment checker; grade-chip **scorecard/ledger cards** (A+, D3 AET, verdict prose) + **quote-object** (Pedro "Bubista" Brito, Cape Verde). | ✅ real furniture, not flat boxes |

Genuine dark-starfield → cream-checker act arc visible. Not blanks, not flat boxes.

---

## TASK 5 — Densified weekly (WP-8)

The committed candidate's source HTML was a builder scratchpad file (not a repo issue); the
shipped `signal_weekly_2026-07-19.html` is the legacy non-mx build. The densified build is
preserved byte-reproducibly as the **committed mx-weekly golden**
(`references/golden/weekly-mx/expected.html`, `data-mx` tier1). I re-measured that.

| Metric | Committed `parity-candidate-weekly-metrics.json` | My fresh re-measure of mx-weekly golden | Match |
|---|---|---|---|
| ev/screen @1440 | 0.86 | **0.86** | ✅ (band 0.8–1.0) |
| events | 32 | **32** | ✅ |
| body words | 7,763 | **7,763** | ✅ |
| words/screen @1440 | 209.33 | **209.33** | ✅ (≤210) |
| motion / reduced | 20 / 0 | **20 / 0** | ✅ |
| overlap / h-scroll / trunc | 0 / false / 0 | **0 / false / 0** | ✅ |

**3 committed screenshots opened (`EVIDENCE/WP-8/parity-candidate-weekly-render/`):**

| Screenshot | What I saw | Verdict |
|---|---|---|
| `1440/cover.png` | Unmistakably Transmission: **cream paper**, serif "The Signal" masthead (black + red italic), radio-waveform rule, "A PERSONAL WEEKLY · RECEIVED & TUNED", FM-frequency STATION LIST, ghosted "017" folio. | ✅ Transmission, no bleed |
| `1440/depth-3.png` | Cream paper; new **`.mx-ledger` fixtures block** (dated result rows, red mono chips: Sinner d. Zverev, Spain v Argentina, Belgian GP RACE DAY) + **`.mx-quote` object** (Zverev, red spine). All in weekly palette/faces. | ✅ real furniture |
| `390/depth-2.png` | Cream paper, serif (Newsreader) body, disciplined measure — Long Read. | ✅ Transmission at 390 |

No scene-grounds, no display-font/scene-ground bleed, no skin bleed. Cream paper + serif
masthead throughout. Real densification furniture in the weekly's own identity.

---

## TASK 6 — Screenshot spot-audit across WPs + flat-negative contrast

| Screenshot | What I saw | Verdict |
|---|---|---|
| `WP-2/parity-candidate-dd/render/1440/depth-2.png` | Parchment cross-hatch ground; taped **INDEX CARD** (typewriter fill, "margin note · File VI", "THE SIGNAL ARCHIVE"); red **ring-stamp** "THE GREAT SIEGE 717–718" with hand annotation; mono chapter kicker + seam. | ✅ objects on a surface |
| `WP-2/parity-candidate-dd/render/1440/depth-4.png` | Parchment ground; taped index card ("margin note · File X"); green mono kicker "AN ALPHABET FOR THE SLAVS". | ✅ objects on a surface |
| `WP-3/parity-candidate-countdown-event/render/1440/depth-2.png` | Indigo **starfield** ground; two tilted/pinned cream ride cards (numbered plates 06/07, quote pulls, WHERE/WHY rows, credits); two **real tilted photographs** (Efteling dusk, gothic ride) in white photo-frames; pushpinned card bleeding off bottom edge. | ✅ objects on a surface |
| `WP-3/parity-candidate-dd-editorial/render/1440/depth-3.png` | Parchment ground; framed **map fragment** + credit; script kicker; red **ring-stamp** "MEDIEVAL APEX 1025 BASIL II DIES" + hand annotation; pushpinned **self-made bar chart** with hand caption. | ✅ objects on a surface |
| **Contrast:** `WP-0/smoke/attempt2-stub-flat-season-review/render/1440/depth-2.png` | Flat cream page, **no scene-ground/texture**; a single hairline-bordered "THE 48-TEAM FORMAT" rectangle; flat stat numbers; one thin ring-stamp; back-pill overlapping content. The "load of squares." | ⬅ categorically different |

**Every WP-2/WP-3 candidate shows objects on textured surfaces — tilted, taped/pinned,
shadowed, overlapping, with real photos/maps/self-made charts and hand-annotated stamps.
The attempt-2 negative is flat hairline boxes on a flat page. The system's output is
categorically different from the flat negative** — exactly what the scorecards claimed.

---

## TASK 7 — Cross-check 5 PROGRESS claims vs reality

| # | PROGRESS claim | Reproduction | Verdict |
|---|---|---|---|
| 1 | WP-6: "validate-chapter-plan 76/76" | `validate-chapter-plan.py --test` → **"76/76 tests passed. PIPELINE TEST: PASS"** (exit 0) | ✅ TRUE |
| 2 | WP-6: "MX-TIMING rejects before-final Season Review" | Wrote the verbatim attempt-#2 plan (WC event `end_date 2026-07-19`, `status in_progress`, publish `2026-07-19`) → **2 named `[MX-TIMING]` errors**: status must be 'concluded'; "ends 2026-07-19 but publishes 2026-07-19 — must be CONCLUDED STRICTLY BEFORE publish date… the attempt-#2 failure this gate exists to make impossible." | ✅ TRUE |
| 3 | WP-7: live SR "7,645 words … publish-gate GREEN in place" | validate-issue Law-3 = **7,645 words**; publish-gate re-run **GREEN** (Task 4) | ✅ TRUE |
| 4 | WP-8: "0.86 ev/screen @1440" densified | Fresh measure of committed mx-weekly golden = **0.86 ev/screen @1440** exactly (Task 5) | ✅ TRUE |
| 5 | WP-3: "editorial 102.4KB/120, event 96.5KB/160" | Bundles recomputed the way the stitcher does (`"\n".join`, utf-8): **editorial 110,278 B = 107.7 KB**, **event 104,313 B = 101.9 KB**. Both **under budget** (gate still PASSES), but the recorded byte figures are **~5.3 KB stale** — a shared core layer grew after WP-3 (identical +5.3 KB delta on both bundles ⇒ a `core/*` file, consistent with WP-5 motion expanding `14-motion.css`). | ⚠️ BUDGET CLAIM TRUE / recorded numbers STALE |

Supporting spot-checks (not among the 5, for confidence):
- WP-8 "weekly CSS … 45.9 KB": `weekly-mx/10-mx-weekly.css` = 18.7 KB atop ~25 KB base ≈ 44–46 KB — roughly reproduces.
- WP-7 "8 named voices": validate-issue's markup counter reports **11** distinct quote-objects (its
  attribution parse is noisy, e.g. fragment "n"); both the tool count and any hand count clear the
  Law-9 floor of 5. Labeling nuance only — non-blocking.

---

## DISCREPANCIES (itemized) — none are false greens

1. **WP-3 recorded CSS bundle bytes are stale.** PROGRESS/WP-3 records editorial **102.4 KB** and
   event **96.5 KB**; the current tree bundles to **107.7 KB** and **101.9 KB** (the exact figure the
   stitcher's `css_total` gate would emit). Both remain under the 120 KB / 160 KB budgets, so the
   **budget gate verdict ("budgets met") still holds and does not false-green** — but the literal
   recorded numbers no longer reproduce. Cause: a shared `core/*` CSS layer grew ~5.3 KB after the
   WP-3 measurement (same delta on both bundles), consistent with WP-5 motion. **Impact: none on
   shipping / gate correctness; the PROGRESS WP-3 line should be refreshed to 107.7/101.9 KB.**
2. **(Minor, non-blocking)** PROGRESS/WP-7 "8 named voices" vs validate-issue's markup count of 11
   (noisy attribution parse). Both clear the Law-9 floor of 5. No gate affected.

No negative fixture passed. No golden drifted. No live/clean gate flipped. No screenshot was a
blank or a flat box. No false PASS was found. The only discrepancy is a stale documentation number
whose underlying gate still passes.

---

## VERDICT

**WP-9 AUDIT: DISCREPANCIES FOUND**

Itemized: (1) WP-3's recorded CSS bundle byte figures (102.4 KB / 96.5 KB) do not reproduce against
the current tree (107.7 KB / 101.9 KB) — a stale documentation number, **not a false green**: both
bundles are still under budget and the budget gate still passes. (2) WP-7 "8 named voices" vs the
validator's 11 — a labeling nuance, both above floor.

Everything the audit is designed to catch held: **every retained negative fixture still FAILS**
(exit 1), **every clean control, both goldens, all 3 motif goldens, and the live Season Review
publish-gate PASS**, fresh measurements reproduce the committed WP-7 and WP-8 metrics **exactly**,
every opened screenshot is a **real render matching its scorecard claim** (scorecards, quote-objects,
poster cover, Transmission furniture — categorically unlike the flat attempt-2 negative), and the
core PROGRESS gate claims (76/76 plan tests, MX-TIMING before-final rejection, live-SR words +
publish-gate GREEN, 0.86 ev/screen densified weekly) **reproduce true**. **No false green exists.**
The single blocking-criteria miss is the stale WP-3 bundle number, surfaced here rather than
smoothed over per Part 6 §5.
