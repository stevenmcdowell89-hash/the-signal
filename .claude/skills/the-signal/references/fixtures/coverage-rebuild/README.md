# Fixtures — editorial coverage rebuild

Permanent fixtures for `scripts/test-coverage-gates.sh`, the harness that re-proves the twelve
acceptance criteria in `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md` §4.

Owned by **WP-10**. Nothing else in the repo reads this directory; nothing in this directory writes
anywhere except a temp dir the harness owns.

Run the harness, not these files directly:

```
bash .claude/skills/the-signal/scripts/test-coverage-gates.sh
bash .claude/skills/the-signal/scripts/test-coverage-gates.sh --list
bash .claude/skills/the-signal/scripts/test-coverage-gates.sh 3 8 --keep
```

---

## Why most of the fixtures are generated, not committed

`build-fixtures.py` derives 29 rendered-issue fixtures from **frozen Issue #18**
(`issues/signal_weekly_2026-07-26.html`) by single-point mutation, and eight state fixtures from the
real `state/signal-state.json`. Committing the outputs would put ~4.5 MB of near-identical 141 KB HTML
in the repo and bury the one line that matters in each file. Committing the *mutations* instead makes
the whole matrix readable — one screen per criterion — and it fails loudly if an anchor ever moves,
because `one()` asserts the anchor exists before replacing it.

The trade is real and worth naming: a generated fixture depends on its input. That is acceptable here
precisely because the input is **frozen by the SPEC** (§1.3), and it is checked: the harness records
`sha256[:16]` of Issue #18 and the state file before and after every run and asserts they are
unchanged.

Everything too small to be worth generating is committed literally, with a comment at the top saying
which criterion it serves and what the *one* variable is.

---

## What is here

| Path | Serves | What it is |
|---|---|---|
| `build-fixtures.py` | 1–8 | The generator. `--out DIR` writes `weekly/`, `states/`, `plans/`, `bundles/`. Reads Issue #18 and the real state, writes neither. |
| `check-daily-routing.mjs` | 11 | Harness helper (not a fixture — it lives here because the §2 ownership map gives WP-10 only this tree and the harness script). Runs the real `parseFeed` + `scoreProfile` over the RSS fixtures, with every source path a parameter so the same assertions run against the shipped daily and against the pre-rebuild one out of git. |
| `html/diversity-one-shape.html` | 12 | Firing: 3 domains, 3 source types, every plate `key_art`. |
| `html/diversity-three-shapes.html` | 12 | Passing: **identical** domains and source types; only the shapes differ. |
| `html/diversity-bad-enum.html` | 12 | Firing: 3 distinct shapes, one of them the typo `screenshot`. |
| `html/diversity-all-key-art.html` | 12 | The regression the retired Wikimedia ceilings could not see: Commons at 25%, inside the old caps, every image key art. |
| `html/cover-nd.html` | 9 | Firing: a cover whose source is `allows_derivatives: false`. |
| `html/cover-permissive.html` | 9 | Passing: same shape, a source that permits derivatives. |
| `html/cover-unknown-licence.html` | 9 | Boundary: an `UNKNOWN` licence — warn by default, refuse under `--strict-licence`. |
| `json/cover-licences.json` | 9 | The §3.10-shaped manifest staged into the sandbox for the three cover fixtures. |
| `rss/bbc-{cricket,cycling,athletics}-sample.xml` | 11 | Minimal but structurally real RSS 2.0, read by the **real** parser. Offline by design. |

### Generated (not committed) — see `build-fixtures.py` for the exact one-line delta of each

- **`weekly/pass.html`** — Issue #18 **plus the SPEC 2026-07-26 contract markup it predates**. This is
  the "corrected fixture" of criteria #3 and #8. Every other weekly fixture is `pass.html` with
  exactly one thing broken.
- `weekly/vintage-*` (6) — criterion #2, the rendered vintage contract in both directions.
- `weekly/capvintage-*` (3) — criterion #3. The firing case is **Issue #18's own shipped FIG 03
  caption wording** with only the capture year added, which is the exact defect the owner spotted.
- `weekly/shapes-*` (8) — criterion #8, one clause of the §3.8 budget each.
- `weekly/ledger-*` (4), `weekly/loop-resolved.html` — criteria #6 and #7.
- `weekly/table-kind-*`, `weekly/provenance-missing.html` — §3.4 markup contracts.
- `states/weekly-*` (4) — full state copies with one key replaced (`validate-issue.py` reads several
  state keys at once, so a partial state would exercise its tolerance paths instead of the rule).
- `states/open-loop-matured.json`, `states/rutted-*.json`, `states/empty.json` — minimal standalone
  objects: the two upstream validators read one key each, and a ten-line ledger is readable.
- `plans/weekly-*.json` (8), `bundles/*.json` (3).

---

## The `open` loop fixture, and why it had to be built

`state/signal-state.json` seeds two `open_loops` and **both are `status: "dropped"`** — honest
history, because neither the World Cup final nor The Open was ever reported in the weekly of record
and Issue #18 is frozen. **A dropped loop does not mature**, so those seeds cannot make the §3.7 gates
fire, however the run date is set. WP-1 flagged this three times and SPEC §4 makes it WP-10's job.

Two fixtures answer it, and both carry a loop that is *not yet due* alongside the matured one, so the
harness can prove maturity is real rather than decorative:

- `states/open-loop-matured.json` (criterion #5, the bundle gate): one matured (`open`, due
  2026-07-19), one open but due 2026-08-02, and one **`dropped` with a past due date** — which must
  not mature. That last entry is the fixture's whole point.
- `states/weekly-matured-loop.json` (criterion #6, the rendered gate): one matured, one due
  2026-08-30. The harness runs the same HTML and the same state at `--run-date 2026-07-18` and
  requires a pass.

---

## Invented data is labelled as invented

Two fixtures need a calendar event or a loop that the real seed cannot supply — the seeded
`sports_calendar` has no football event ending inside any July window, and the real loops are dropped.
Every such row is prefixed **`FIXTURE DATA — not a real event`**, so it can never be read as a fact of
record if it is ever grepped out of context. The `rss/bbc-cycling-sample.xml` titles are prefixed
`Fixture item, not a result` for the same reason: unlike the cricket and athletics fixtures, whose
titles are live headlines quoted from `EVIDENCE/WP-7.md` §3.3, there was no recorded cycling headline
to quote, so those two lines are written to exercise the keyword set and name no rider and no outcome.

No fixture asserts a 2026 sporting result, a venue, or a fixture date that the repo does not already
carry.

---

## Adding a fixture

1. If it is a rendered weekly, add the mutation to `build-fixtures.py` — do **not** commit HTML
   derived from Issue #18. Use `one()` so a moved anchor is loud.
2. If it is small and standalone, commit it under `html/`, `json/` or `rss/` with a leading comment
   naming the criterion and the single variable.
3. Add the assertion to `test-coverage-gates.sh` in the criterion's section, with **both** a firing
   and a passing case. A check that has only ever been seen to pass has not been seen to work.
4. Re-run the harness. It must still report 12 of 12.
