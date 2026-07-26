# WP-9 — Pipeline phase wiring

**Date:** 2026-07-26 · **Branch:** `claude/signal-antikythera-article-lzzlup`
**SPEC:** `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md` §1, §2, §3.1, §3.5, §3.6, §3.7, §3.12, §4
**Defects:** C, D (D1 the calendar coverage window, D2 the abandoned `upcoming` fact)
**Files touched:** `.claude/skills/the-signal/SKILL.md` only (+170/−8 — every deletion is a line rewritten in place)

---

## What changed

WP-1 built the data structures; nothing read or wrote them. WP-9 is the wiring, and it is
documentation-of-record for the pipeline: it names which phase reads which state key, which phase
writes it, and what breaks when a write is skipped. Nine edits, all inside the established phase
numbering and the existing three-gate ledger. **No fourth ship gate** (SPEC §1 non-goals): the new
mechanical checks are named as living inside `validate-research-bundle.py` (upstream aid),
`validate-chapter-plan.py` (upstream aid) and `validate-issue.py` (gate 2).

1. **§ The current state, in one paragraph** — one sentence added: coverage is bounded by instants,
   not calendar days; every `upcoming` fact opens a loop; Phase 0 reads six state keys and Phase 10
   writes them back.
2. **§ Workflow pipeline one-liner** — `Phase 0 (decide format)` → `Phase 0 (read state → coverage
   window + open loops + cover-lead ledger + sports calendar → decide format)`.
3. **Phase 0a** — a producer/consumer table for the six coverage keys, and an instruction to read
   `references/spec/data-contracts.md` at Phase 0 alongside state.
4. **Phase 0a-window (new)** — computes `(previous research_cut_at, now]`. Carries the D1 diagnosis
   (issue #17 carried the final 12× as upcoming; #18's result count is zero; #16 published on a
   Monday and is the only issue that ever reported a Sunday result) and the intended visible
   consequence: a Sunday conclusion lands in the *next* window by construction, with an explicit
   "do not widen the window to tidy a dateline" instruction.
5. **Phase 0a-loops (new)** — matured-loop rule (`open` ∧ `expected_resolution_date <= today`),
   mandatory resolutions, the owing `band`, and the honest-drop path.
6. **Phase 0a-ledger (new)** — computes the last-4 `led_on:"news"` tally per `topic_family`, passes
   the whole ledger to the planner, and states at length that this is **not** a restored topic-lock.
7. **Phase 0a-calendar (new)** — verify `needs_verification: true` entries against a source before
   the planner relies on them; three buckets (concluded in-window → mandatory results-ledger row /
   running → standings / opens next week → On the Radar); the `interest_depth` absent-key rule; the
   dates-vs-instants edge case.
7b. **Phase 0a-calendar + 3a + 5 — the sport-token namespaces** (SPEC §3.11 amendment,
   commit `a73ac68`, landed mid-WP and picked up here): `sports_calendar[].sport` may be
   `multi_sport` because it classifies an *event*, but a **result belongs to a sport**, so a
   `multi_sport` entry is briefed as several results and the ledger renders one row per discipline
   with a **specific** `data-sport`. `data-sport="multi_sport"` is documented as forbidden in all
   three places the token is produced (calendar bucket, researcher brief, writer brief), with the
   reason: it would collapse ten sports into one token and let a two-row ledger pass the
   `results_ledger_multi_sport` invariant while conveying no breadth. Points at
   `references/spec/data-contracts.md` § Sport tokens as canonical; does not restate the token list.
8. **Phase 0f** — scout against the window instants, and treat matured loops + concluded-in-window
   events as already-committed coverage.
9. **Phase 3a** — four numbered obligations in the researcher brief (window instants; matured loops
   as mandatory `resolves_loop` facts; the three calendar buckets; `upcoming` facts must be dated
   because their `date` *is* the expected resolution date). Explicitly adds **no** bundle field
   beyond WP-1's contract.
10. **Phase 3a-verify step 6** — stamps the measured research cut when the bundle freezes;
    monotonic, moves forward only, single source of truth at `/tmp/signal-build/window.json`.
11. **Phase 3b** — invocation gains `--state /tmp/the-signal/state/signal-state.json`; the
    matured-loop bundle check named as a check *inside* the existing upstream aid.
12. **Phase 4** — the planner's required `issue_meta` emissions (`research_cut_at`, `window`,
    `cover_leads_on`, `lead_rationale`, `lead_override_reason` when rutted), `long_read.vintage` +
    `material_span`/`latest_development`, `week_in_numbers.rows[].source_band`; all four Phase-0
    products passed inline; "the planner's obligation is prose, not avoidance".
13. **Phase 5** — the owing band renders `data-resolves-loop="<id>"`; the Touchline ledger is
    results-of-record with `data-sport` per row; no decorative carried-forward captions.
14. **Phase 6** — the cover dateline derives from `issue_meta.window`, not from a one-week range
    ending on the issue date. **Handoff to WP-3** (see below).
15. **Phase 7.5 step 6** — the human-judgement counterpart: does the issue state the matured loop's
    result, on an element with `data-resolves-loop`.
16. **Phase 7.6** — the loop/ledger/caption/shape checks named inside gate 2, with the
    `--state`/`--run-date` invocation, and an explicit note that the *check* is what SPEC §3.7 fixes
    if WP-4's flag names differ. **Handoff to WP-4** (see below).
17. **Phase 10** — the five-item "Coverage continuity writes" block (the mandatory
    `research_cut_at` overwrite first, and why the fix is inert without it), the `used_image_urls`
    read-back-from-disk ordering hazard, `assets/cached/manifest.json` in the push list, and the
    step-1a provenance note.
18. **§ State Tracking** — the six keys added to the state-shape snapshot; a new
    **§ Coverage continuity** with a key → read-by → written-by → failure-mode table and the
    `cover_lead_ledger` vs `lead_history` vs topic-lock distinction; six new bullets in the
    "After generation, update:" list.
19. **§ Pipeline scripts and references table** — a row for `references/spec/data-contracts.md`.

---

## Phase → reads → writes

| Phase | Reads | Writes / produces |
|---|---|---|
| **0a** | `state/signal-state.json` (full), `references/spec/data-contracts.md` | — |
| **0a-window** | `state.research_cut_at` | `/tmp/signal-build/window.json` = `{from: prev cut, to: now, research_cut_at: now}` |
| **0a-loops** | `state.open_loops[]` | the matured list + the owing `band` per loop |
| **0a-ledger** | `state.cover_lead_ledger[]` | the whole ledger + the last-4 `led_on:"news"` tally; a *rutted* flag |
| **0a-calendar** | `state.sports_calendar[]`, `state.interest_depth`, web sources | confirmed entries; three buckets (concluded / running / opens next week) |
| **0f** | the window, the matured list, the concluded bucket | landscape-shift context for 3a |
| **3a (researcher)** | window instants, matured loops, calendar buckets, `interest_depth` | `research-bundle.json` — `facts[].resolves_loop` for every matured loop; ledger facts per concluded event; dated `upcoming` facts |
| **3a-verify** | the bundle | the bundle rewritten; **advances** `window.json.research_cut_at` to the freeze instant (forward only) |
| **3b** | bundle + `--state` | exit code; matured-loop-without-`resolves_loop` = hard fail |
| **4 (planner)** | `window.json`, matured loops (+ band), calendar buckets, `cover_lead_ledger` + tally, bundle | `chapter-plan.json` — `issue_meta.research_cut_at`, `.window{from,to}`, `.cover_leads_on`, `.lead_rationale`, `.lead_override_reason` (rutted only); `long_read.vintage`/`material_span`/`latest_development`; `week_in_numbers.rows[].source_band` |
| **5 (writers)** | the chapter brief incl. its owed loops | band HTML with `data-resolves-loop`, results-ledger rows with `data-sport` |
| **6 (stitch)** | `issue_meta.window` | the cover dateline (`[DATE RANGE]`) |
| **7.5** | matured list, bundle `upcoming` facts, run date | FAIL list walked by the orchestrator |
| **7.6** | HTML + `state.open_loops`, `state.used_image_urls` | exit code (gate 2) |
| **9 / 9.5** | unchanged | unchanged |
| **10 (publish)** | `window.json`, the issue, the plan | **`state.research_cut_at`** ← measured instant (overwrite); **`state.open_loops`** ← resolve / drop-with-reason / append one per `upcoming` fact; **`state.cover_lead_ledger`** ← prepend, trim to 12 (weeklies only); **`state.sports_calendar`** ← prune ended, append source-confirmed; **`state.used_image_urls`** ← at step 1a by `mirror-images.py` (WP-8), so state is re-read from disk before the push |
| — | — | **`state.interest_depth`** is never written by the pipeline (owner-set) |

**Loop derivation, no new contract.** A new loop's `expected_resolution_date` is the `upcoming`
fact's own `date`; `claim` is the fact's claim; `band` is the `chapter_id` the planner routed it to;
`id` is `loop_<expected_resolution_date>_<slug>`. Nothing was added to the bundle's `facts[]` shape
beyond WP-1's `resolves_loop`.

---

## How the rut rule is kept from reading as a restored suppression gate

Stated three times, in the three places a future reader would land:

1. **Phase 0a-ledger** — a side-by-side: topic-lock *forbade* a subject from leading (the pipeline
   decided by refusal); the rut rule is *an input plus a forced written justification* (the planner
   decides, in prose). Names the actual v8.37 defect — `lead_history` written-but-read-by-nothing,
   `last_cover_lead` giving the planner one week of view, UK politics leading 6 of 9 covers unseen.
2. **Phase 4** — "the planner's obligation is prose, not avoidance… Do not brief it as a
   prohibition, and do not re-add topic-lock."
3. **§ State Tracking → Coverage continuity** — `cover_lead_ledger` (rendered-cover record, read by
   0a-ledger + `validate-chapter-plan.py`) vs `lead_history` (story-thread record, still read by
   nothing, unchanged) vs topic-lock (deleted, stays deleted), plus the tripwire: *"If a future
   reader finds themselves adding a rule that prevents a lead, that is the retired gate coming back
   under a new name."*

---

## Consistency checks run, and their results

Verification for this WP is consistency, not execution (SKILL.md is prose-of-record).

**1. Every state key referenced exists in `state/signal-state.json`.**

```
$ python3 - # membership test per key against the seeded state
  research_cut_at          in SKILL=Y  in state=Y
  open_loops               in SKILL=Y  in state=Y
  cover_lead_ledger        in SKILL=Y  in state=Y
  sports_calendar          in SKILL=Y  in state=Y
  used_image_urls          in SKILL=Y  in state=Y
  interest_depth           in SKILL=Y  in state=Y
  last_cover_lead          in SKILL=Y  in state=Y
  ongoing_stories          in SKILL=Y  in state=Y
  last_issue_number        in SKILL=Y  in state=Y
  last_issue_date          in SKILL=Y  in state=Y
  open_loops subfields missing: []          # id claim expected_resolution_date band issue_opened status resolution
  cover_lead_ledger subfields missing: []   # issue date topic_family one_line led_on
  sports_calendar subfields missing: []     # event sport start end importance reader_relevant needs_verification
```

`lead_history` is nested inside `ongoing_stories[]` entries, not top-level — confirmed
(`ongoing_stories[0] keys: [aliases, last_development, last_status, lead_history, promotion_note,
section, topic, weeks_as_lead, weeks_as_ongoing]`); SKILL.md refers to it as
`ongoing_stories[].lead_history` accordingly. Note: **not** every `ongoing_stories` entry carries
`lead_history` (`all(...)` → `False`), which is consistent with v8.37 making it optional.

**2. Every field the planner is told to emit exists in `chapter-plan-schema.md`.**

```
$ for f in research_cut_at window cover_leads_on lead_rationale lead_override_reason vintage \
           material_span latest_development source_band design_system word_budget images_needed; \
  do grep -c "$f" .../references/chapter-plan-schema.md; done
  research_cut_at: 6      window: 6            cover_leads_on: 4      lead_rationale: 4
  lead_override_reason: 3 vintage: 8           material_span: 5       latest_development: 4
  source_band: 7          design_system: 5     word_budget: 4         images_needed: 10
```

All present. `source_band`'s accepted value set (a `chapter_id` in this plan **or** the literal
`"state"`) is quoted from WP-1's clarification, not re-specified.

**3. No retired phase or gate is named as live.**

```
$ grep -n "check-topic-lock|check-theme-clustering|check-prose-rhythm|visual-smoke-test|Phase 7.8|Phase 7.75|deep_dive_schedule" SKILL.md
```
Every hit is inside existing "RETIRED / deleted / REMOVED" framing, or inside the new text where the
mention is explicitly *"stays deleted"*. No new text invokes a retired script or phase. The phases
WP-9 names — 0a, 0a-window, 0a-loops, 0a-ledger, 0a-calendar, 0f, 3a, 3a-verify, 3b, 4, 5, 6, 7.5,
7.6, 10 — are all live in the v8.42/v8.43 pipeline. Cross-checked against
`.claude/skills/the-signal/scripts/` (20 scripts present; none of the retired four exist) and the
CHANGELOG's v8.36/v8.37/v8.38 retirement entries.

**4. The Phase 0a-window snippet executes as written**, verbatim against the real state file:

```
$ python3 - <<'PY'   # the snippet from Phase 0a-window, state path swapped for the local checkout
{"from": "2026-07-26T02:10:00Z", "to": "2026-07-26T11:21:59Z", "research_cut_at": "2026-07-26T11:21:59Z"}
```

`from` is WP-1's seeded cut; `to` is a real measured instant. The matured-loop computation as
documented returns **`[]`** against the seeded state (`statuses: ['dropped','dropped']`) — which is
correct and matches WP-1's handoff note 6: a dropped loop does not mature, so WP-10 still needs an
`open` fixture with a past `expected_resolution_date` to make the §3.7 gates fire.

**5. Headings ordered and unique.** `grep -n "^#"` confirms the four new `### 0a-*` sub-sections sit
between `0a` and `0b`, and that no existing heading was renamed or removed.

**6. File ownership.**

```
$ git status --short
 M .claude/skills/the-signal/SKILL.md          # WP-9 — the only file this WP touched
 M .claude/skills/the-signal/references/editorial-spec.md        # WP-2, parallel
 M .claude/skills/the-signal/references/image-source-types.json  # WP-6, parallel
 M .claude/skills/the-signal/scripts/stitch_weekly.py            # WP-3, parallel
?? .claude/skills/the-signal/assets/css/weekly/01-coverage-rebuild.css  # WP-3, parallel

$ git diff --numstat -- .claude/skills/the-signal/SKILL.md
170  8   .claude/skills/the-signal/SKILL.md
```

All 8 deletions verified as lines rewritten in place (`git diff -U0 | grep '^-'`) — no content
dropped. WP-9 committed nothing itself; the orchestrator's WIP snapshot `9d354c9` ("WP-2, WP-3, WP-6,
WP-9 in flight") captured the bulk of these edits mid-flight, so a later `git status` shows only the
subsequent delta (`4/2`, the three sport-token edits made after the SPEC amendment landed). Both HEAD
and the working tree contain all 32 references to the new sub-sections — verified with
`git show HEAD:….md | grep -c` vs `grep -c` on the working copy (32 = 32). Every other modified path
belongs to a parallel WP (WP-1-followup `data-contracts.md`, WP-2 `sections.md`/`compliance-checklist.md`,
WP-3 `weekly.json` + weekly-mx CSS, WP-11 `dedup.js`).

**7. Every script path SKILL.md invokes resolves.** All 20 skill-dir scripts named in the file exist
in `.claude/skills/the-signal/scripts/`; `post-publish.sh`, `mirror-images.py` and
`extract-covers.py` resolve against the **repo-root** `scripts/` (which is what Phase 10 step 1a says:
"from the repo root"). No invocation names a deleted script.

---

## Findings — SPEC / WP-1 contract text that is wrong (reported, not re-specified)

1. **SPEC §3.1's inline comment on `research_cut_at` contradicts its own example, and
   `chapter-plan-schema.md` inherits the error.** §3.1 reads
   `"research_cut_at": "2026-07-26T02:10:00Z",   // ISO8601, from state; the window's opening bound`
   — but the same block's `window` is `{from: "2026-07-19T02:14:00Z", to: "2026-07-26T02:10:00Z"}`,
   i.e. `research_cut_at == window.to`, the **closing** bound. `chapter-plan-schema.md` line ~139
   repeats it: *"Copied from `research_cut_at` in state/signal-state.json, which the previous publish
   wrote"* — which describes `window.from`, not `research_cut_at`; the next sentence of the same
   description then correctly calls it *"the closing bound of this issue's coverage window and the
   opening bound of the next one"*, and the schema's worked example
   (`research_cut_at: 2026-08-02…`, `window: {from: 2026-07-26…, to: 2026-08-02…}`) is
   unambiguous. SPEC §3.5 (*"written at publish; opens the next window"*) and the WP-9 brief agree
   with the examples. **WP-9 wired the examples**: `window.from` ← state (previous publish's value),
   `research_cut_at` = `window.to` = this run's measured instant, persisted at publish. Two comment
   strings should be corrected by their owners (SPEC §3.1's `// … from state; the window's opening
   bound`; the schema's *"Copied from … which the previous publish wrote"*). No field name, value or
   requirement was changed.
2. **Nothing else.** WP-1's field names, enums, required/optional status and the two documented
   corrections (`url_or_keyword`; `source_band: "state"`) were taken as written.

---

## Left undone / deliberate scope calls

- **No version bump, no CHANGELOG entry.** SKILL.md's header reads `Version 8.42.0` while Phase 5
  already documents v8.43 features, so the version line was already trailing; `CHANGELOG.md` is not
  a WP-9 file (unowned by the ownership map). New text is tagged *"(coverage rebuild, SPEC §…)"*
  instead of a version. The orchestrator should decide the version + CHANGELOG entry for the whole
  rebuild in one go.
- **Phase 9.5 (the holistic read) was deliberately not touched.** Adding "was last week's promised
  result delivered?" to gate 3 would mean changing the scorer's brief and `quality-rubric.md`, which
  SPEC §5 puts out of scope. The obligation is already enforced mechanically at 3b and 7.6 and by
  judgement at 7.5.
- **`sports_calendar.needs_verification` is never flipped `true` → `false` by a verification run.**
  Entries seeded `true` stay `true` and are re-verified before each reliance (bounded, because only
  entries touching the window or the coming week are verified). Only Phase-0-appended entries land
  with `false`, meaning "confirmed against a source when added". This avoids contradicting SPEC
  §3.12's *"every seeded entry gets `needs_verification: true`"* while keeping the per-run cost flat.
- **No truncation rule invented for `open_loops`.** Terminal (`resolved`/`dropped`) entries stay as
  the record; they no longer mature so they cost nothing. If the array becomes unwieldy, that is a
  WP-1 contract decision, not a wiring one.
- **Executable verification of the wiring is WP-10's.** Nothing in SKILL.md is machine-checked, so
  the honest test of this WP is a real Phase-0-to-10 run — the first one produces the first measured
  `research_cut_at` and the first populated `used_image_urls`.

---

## Handoff notes

### From WP-9

1. **→ WP-3 (`stitch_weekly.py`, `stitch-issue.sh`): the cover dateline must derive from
   `issue_meta.window`.** SKILL.md Phase 6 currently documents `[DATE RANGE]` as *"a one-week range
   ending on the issue date for weeklies"* (v8.18.1). Under SPEC §3.5 the dateline and the coverage
   claim are the same object, so the substitution must render `issue_meta.window{from,to}`. WP-9
   documented the new behaviour and stated that where the stitched dateline and the window disagree,
   **the window wins and the stitcher is the bug** — but the code change is in WP-3's file. Until it
   lands, the rendered dateline can overstate what was knowable even though the plan is correct.
2. **→ WP-4 (`validate-issue.py`): needs the state path and the run date.** The §3.7 rendered check
   ("a matured loop's id has no `data-resolves-loop`") and the §3.8 cross-issue lead-image budget
   both require `state/signal-state.json`; the maturity rule requires a run date. Today's CLI has
   neither (`html_path`, `--format`, `--multi-venue`, `--skip-image-urls`, `--image-timeout`,
   `--workers`, `--strict`). SKILL.md documents the invocation as
   `--state <path> --run-date <today>`, mirroring the flag names SPEC §3.7 fixes for
   `validate-research-bundle.py`. **Please use those two names**; if you must differ, tell the
   orchestrator so the Phase 7.6 invocation line is corrected (the check is normative, the flag
   spelling is not).
3. **→ WP-5 (`validate-research-bundle.py`): `--state` does not exist yet.** SPEC §3.7 fixes the
   invocation as `--run-date <today> --state state/signal-state.json`; SKILL.md Phase 3b now passes
   `--state /tmp/the-signal/state/signal-state.json` (the *cloned repo's* state, so the loops the
   validator matures are the ones Phase 0a-loops read). The flag must exist and must be tolerant of
   an absent/empty `open_loops` (no loops = no failure).
4. **→ orchestrator / owner: two contract comment strings are wrong** — see § Findings 1. The
   behaviour is unambiguous from the examples and was wired that way; only the prose misleads.
   `chapter-plan-schema.md` is WP-1's file and SPEC §3.1 is the orchestrator's.
5. **→ WP-10: the seeded loops still cannot demonstrate §3.7.** Confirmed independently here — the
   matured computation documented at Phase 0a-loops returns `[]` against seeded state because both
   loops are `dropped`. WP-1's handoff note 6 stands; a fixture with `status: "open"` and a past
   `expected_resolution_date` is required for acceptance criteria #5 and #6. A useful second fixture:
   a `window.json` whose `from` is a week old, so the concluded-in-window bucket is non-empty.
6. **→ owner (judgement call, not a build task): the first real run rewrites `research_cut_at`.**
   The seeded `2026-07-26T02:10:00Z` is the SPEC literal. Issue #19's Phase 0 will open its window
   there, which means anything that became knowable between #18's *actual* research cut and that
   literal is either double-covered or missed by a margin of minutes-to-an-hour. That is the
   cheapest possible one-off cost of switching the mechanism on, and it does not recur.
