# WP-0 smoke sweep — final verdict table (2026-07-19)

Produced by tools/measure-issue.mjs + tools/render.mjs (harness output, uncurated).
Screenshots: <target>/render/{1440,390}/depth-*.png + cover + dark-1440.png.

| target | viewport | body words | ev/screen | longest 0-event run | chrome overlap | table trunc | doc h-scroll | motion elems | reduced-motion elems |
|---|---|---|---|---|---|---|---|---|---|
| attempt2-flat-redress-deep-dive | 1440x900 | 18260 | 0.79 | 3 | ok | ok | ok | 137 | 0 |
| attempt2-flat-redress-deep-dive | 390x844 | 18335 | 0.5 | 6 | FAIL | FAIL | ok | 139 | 0 |
| attempt2-stub-flat-season-review | 1440x900 | 526 | 2.99 | 0 | FAIL | ok | ok | 0 | 0 |
| attempt2-stub-flat-season-review | 390x844 | 526 | 2.7 | 0 | FAIL | FAIL | ok | 0 | 0 |
| countdown | 1440x900 | 6616 | 1.75 | 1 | FAIL | ok | ok | 38 | 3 |
| countdown | 390x844 | 6616 | 1.15 | 2 | FAIL | ok | ok | 187 | 3 |
| field-guide | 1440x900 | 14497 | 1.46 | 5 | FAIL | ok | ok | 913 | 0 |
| field-guide | 390x844 | 14497 | 0.79 | 4 | FAIL | ok | ok | 913 | 0 |

## Reading the table against the WP-0 gate
- **countdown (known-good reference):** 1.75 ev/screen @1440 — meets the ≥1.5 calibration bar (review hand-measured 1.69). Chrome-overlap FAILs are TRUE findings documented in the July review (cover/subtitle collision, caption overlap mid-reveal); reduced-motion=3 is a TRUE violation (`hol-shimmer` heat-haze ungated — see tools/README-measure.md). h-scroll: geometric overflow only (tilted ephemera), no real user scroll — flag correctly False.
- **attempt2-stub-flat-season-review (negative, F-18/F-19/F-20):** 526 body words (claimed 542 / "2.81 ev/screen"); census reads 2.99 ev/screen — density-by-stub confirmed, caught by Law-3 word floor in validate-issue.py, NOT by density alone (this is why averages alone never pass). Fixed-pill chrome overlap FAIL at both widths; mid-word table truncation FAIL @390; zero motion (tier2 format → Law-5 FAIL).
- **attempt2-flat-redress-deep-dive (negative, F-20):** 0.79/0.50 ev/screen (DD floor 0.7 — fails @390), longest zero-event run 3 @1440 / 6 @390 (Law-2 distribution FAIL both), overlap+truncation FAIL @390. Flatness itself is adjudicated by the Part-5 parity gate.
- **field-guide:** 1.46 ev/screen @1440; overlap findings echo the review's known caption/chrome flaws; reduced-motion clean.

## Known limitations (honest)
- Motion census counts vary run-to-run with scroll timing (countdown 38 vs 186 @1440 across runs); presence/absence verdicts are stable, magnitudes are not — treat counts as ordinal, not exact.
- Event census on legacy pages is heuristic (selector map in tools/README-measure.md); new-system pages should emit [data-mx-event] for exact counting.
- "Mid-word" truncation is geometric inference (no OCR of cut glyphs).
