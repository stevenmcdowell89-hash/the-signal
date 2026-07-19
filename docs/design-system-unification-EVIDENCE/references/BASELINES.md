# WP-1 — FROZEN REFERENCE PACKS · BASELINES (2026-07-19)

These three packs (countdown, field-guide, mockup) are the frozen comparison
standard for every Part-5 parity gate, forever. Parity verifiers receive them
READ-ONLY. Regenerating any pack requires an orchestrator decision recorded in
PROGRESS. Produced by the WP-0-gated harness (tools/render.mjs +
tools/measure-issue.mjs); screenshots are uncurated harness output.

| reference | viewport | body words | ev/screen | longest 0-event run | chrome overlap | table trunc | h-scroll | motion els | reduced-motion els |
|---|---|---|---|---|---|---|---|---|---|
| countdown | 1440x900 | 6616 | 1.75 | 1 | FAIL | ok | ok | 185 | 3 |
| countdown | 390x844 | 6616 | 1.15 | 2 | FAIL | ok | ok | 187 | 3 |
| field-guide | 1440x900 | 14497 | 1.46 | 5 | ok | ok | ok | 913 | 0 |
| field-guide | 390x844 | 14497 | 0.79 | 4 | FAIL | ok | ok | 913 | 0 |
| mockup | 1440x900 | 1279 | 2.13 | 0 | ok | ok | ok | 0 | 0 |
| mockup | 390x844 | 1279 | 1.49 | 1 | ok | ok | ok | 0 | 0 |

## Event mix (byType)

- **countdown 1440x900**: {'chart': 2, 'statband': 2, 'plate': 7, 'figure': 55, 'ephemera': 19, 'quote': 7, 'marquee': 1, 'ledger': 1, 'cheatsheet': 1}
- **countdown 390x844**: {'chart': 1, 'statband': 2, 'plate': 7, 'figure': 55, 'ephemera': 19, 'quote': 7, 'marquee': 1, 'ledger': 1, 'cheatsheet': 1}
- **field-guide 1440x900**: {'figure': 53, 'statband': 3, 'ephemera': 12, 'plate': 4, 'quote': 3, 'marquee': 5, 'ledger': 23, 'cheatsheet': 2}
- **field-guide 390x844**: {'statband': 3, 'figure': 53, 'ephemera': 12, 'plate': 4, 'quote': 3, 'marquee': 5, 'ledger': 23, 'cheatsheet': 2}
- **mockup 1440x900**: {'plate': 3, 'ephemera': 2, 'ledger': 4, 'figure': 8, 'statband': 2}
- **mockup 390x844**: {'plate': 3, 'ephemera': 2, 'ledger': 4, 'figure': 8, 'statband': 2}

## Part-1 / review comparison (WP-1 gate)

- **Countdown @1440: 1.75 ev/screen** — gate floor ≥1.5 MET; review hand-measured
  1.69 (delta +0.06, within tolerance).
- **Field guide @1440: 1.46 ev/screen** — review hand-measured 1.06 (delta
  +0.40). Tool counts every ranked-entry plate the hand count sampled;
  within the ±0.4 stated tolerance.
- **Mockup @1440: 2.13 ev/screen** — no prior baseline exists; this measurement
  BECOMES the baseline.
- Known true reference flaws carried into the baseline (documented WP-0):
  countdown reduced-motion violation (3 els, hol-shimmer); chrome-overlap
  flags on countdown/field-guide echo review-documented caption/cover flaws.
  The unified system must beat the references on these, not merely match.

## File census

Each pack: render/1440/cover.png + depth-0..7.png (9), render/390/ same (9),
render/dark-1440.png, render/render-manifest.json, metrics.json — verified
present for all three packs; no missing files.
