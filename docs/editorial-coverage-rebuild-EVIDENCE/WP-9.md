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

---

# WP-9 follow-up (2026-07-26) — stale Wikimedia caps removed from SKILL.md

Coordinator follow-up after WP-5 and WP-6 completed. `SKILL.md` advertised the **retired**
`wikimedia_max_pct: 30` / `wikimedia_max_count: 4` ceilings as live rules. This matters more than a
doc nit because SKILL.md is what the **researcher and planner actually read**: a ceiling that still
reads as live is how the deleted rule comes back — fill Commons up to 30% and stop, which is defect E.

Source of truth read (not edited): `references/image-source-types.json` (WP-6 — live `thresholds`
are `single_domain_max_pct: 50`, `min_distinct_source_types: 3`, `min_distinct_shapes: 3`,
`min_unique_candidates: 16`, `max_uses_per_url: 1`; the two Wikimedia caps sit in
`retired_thresholds` with their reasons), `scripts/validate-research-bundle.py` and
`scripts/check-image-diversity.sh` (WP-5/WP-6 — both carry explicit "DO NOT reinstate" comments and
neither reads the caps), `references/compliance-checklist.md` § Image specificity check (WP-6's
information-gained hierarchy).

## Every hit audited

| Line | Hit | Verdict | Action |
|---|---|---|---|
| 275 | Wikimedia `thumb/` URL-construction trap | **legitimate** | unchanged |
| 276 | `site:commons.wikimedia.org "File:…"` spelling check | **legitimate** | unchanged |
| 305 | `wikimedia` as one of the 5 **source types** (`min_distinct_source_types`) | **legitimate — live** | unchanged |
| **306** | "Wikimedia ≤4 entries AND ≤30% of total (whichever is smaller)" | **STALE** | replaced (below) |
| 318 | historical anecdote — the 17 May issue's fabricated "Wikimedia Commons: Keir Starmer" keywords | **legitimate** | unchanged |
| **446** | "Wikimedia ≤30% of images AND ≤4 entries (whichever is smaller)" | **STALE** | replaced (below) |
| **943** | `validate-research-bundle.py` row: "Wikimedia ≤30%/≤4" | **STALE** | replaced (below) |
| 945 | `image-source-types.json` row: "plus the threshold values" | **stale-adjacent** (vague, pre-`shows`) | rewritten to name the live thresholds + the `shows` enum + `retired_thresholds` |
| 272 | per-pick coverage "search … TMDB, and Wikimedia for *each named pick*" | **legitimate** | unchanged |
| 272 | `min_unique_candidates: 16` | **legitimate — live** | unchanged |

No fourth *cap* claim existed; hit 945 was the only additional one worth rewriting, and one gap was
found that the grep would not have caught (below). `50%` survives in all three places — RT-5's
`single_domain_max_pct` is **not** retired, and each mention now says so explicitly.

## What each became

- **Phase 3b (was 306)** — five bullets: RT-5 ≤50% (marked *not retired*); **≥3 distinct `shows`
  values across `image_candidates[]`** (`min_distinct_shapes`), with the 11-value enum listed and
  pointed at `image-source-types.json` as canonical; an explicit **RETIRED** paragraph naming both
  withdrawn keys, where they now live (`retired_thresholds`), and the reason in one line — *a ceiling
  with no matching floor reads as a target*; and the information-gained hierarchy (rank 1 event
  photo/gameplay → rank 5 key art, never a lead) with the Halo #18 failure as the worked case.
- **Phase 7.7 (was 446)** — RT-5 ≤50% and `min_distinct_source_types: 3` kept; the cap line replaced
  by **≥3 distinct `data-shows`** with the two failure modes WP-6's script actually implements
  (**no** `data-shows` at all = fail, unlabelled figures cannot be counted; a value outside the enum
  = fail). Adds the point that kills the ceiling's rationale: #18 cleared source-type diversity
  comfortably *while* leading on key art — domain diversity never fixed this.
- **Reference table (was 943)** — the row now reads "≥3 source types, RT-5 ≤50%, **≥3 distinct
  `shows`**, ambiguous-domain annotation, plus `shows`/`capture_year`/`licence` and the open-loop
  check (`--state`)", and states the ceilings are retired and unread.
- **Reference table (945)** — now names the live thresholds explicitly, identifies the file as the
  **one** home of the `shows` enum ("a shape value in a script but not in this file is the taxonomy
  drifting again"), and marks `retired_thresholds` as history, not a live read.
- **Phase 3a — the gap grep would have missed.** The *researcher brief* had no shape instruction at
  all: it told the researcher to surface 16 verified URLs and nothing about what those images should
  show. Removing a ceiling without stating the floor where the researcher reads would have left the
  brief silent. Added a MANDATORY paragraph: `shows` / `capture_year` / `licence` per candidate, the
  **floor** of ≥3 distinct shapes, the shapes to hunt (the paper's own figures on the already-mapped
  `media.springernature.com`; Steam `appdetails` `screenshots[]` on the already-mapped Steam CDNs; a
  map or chart where prose cannot show the thing), rank 5 never leads, and "**no Wikimedia quota in
  either direction**".

## Checks run

```
$ grep -n "Wikimedia|wikimedia|30%|≤4|≤30|wikimedia_max" SKILL.md
  → 9 hits: 275, 276, 305, 308, 318, 451, 947, 949 + one in-body retirement notice.
    Every remaining Wikimedia mention is a URL trap, the source-type menu, the 2026-05-17
    anecdote, or a "these are RETIRED, do not reinstate" statement. No live cap claim remains.
$ grep -n "50%" SKILL.md          → 3 hits, all RT-5, all annotated "not retired".
$ grep -n "min_distinct_shapes"   → 5 hits (Phase 3b ×2, Phase 7.7, both table rows).
$ python3 - # all 11 `shows.values` keys from image-source-types.json present in SKILL.md
  enum size: 11 → missing from SKILL.md: []
$ python3 - # hierarchy ranks cross-checked against shows.specificity_hierarchy
  rank1 [event_photo, gameplay] · rank2 [diagram, map, chart] · rank3 [artefact, document]
  · rank4 [in_engine] · rank5 last resort  → matches SKILL.md's five rungs exactly.
$ git diff --numstat 796a4d5 -- SKILL.md   → 12  6   (baselined on the named commit, not stash)
$ git status --short                        → SKILL.md only (WP-9); other paths are parallel WPs.
```

**`--state` spelling: MATCHES.** WP-5 shipped `ap.add_argument("--state", default=None, …)`
(`validate-research-bundle.py:582`), whose help text names WP-9's Phase 3b invocation directly.
SKILL.md line 304 reads `--run-date <today> --state /tmp/the-signal/state/signal-state.json` — the
cloned repo's state, so the loops the validator matures are the ones Phase 0a-loops read. No change
needed. `--run-date` also matches (line 576).

## New handoff note

7. **→ WP-6 (`image-source-types.json` vs `compliance-checklist.md`): `portrait` and `never_lead`
   disagree.** The machine record has `shows.never_lead_shapes: ["key_art", "product_shot"]`, but the
   checklist's rewritten hierarchy puts `portrait` on the same rank-5 rung and says that rung is
   "LAST RESORT, and never a lead figure" — and the Pope worked example is precisely a *portrait*
   used wrongly. SKILL.md documents the mechanical claim as WP-6 shipped it (`key_art` /
   `product_shot` may never lead) and adds that a portrait should not lead either, so the doc is
   honest either way. If the intent is that a posed portrait cannot lead a band, `portrait` belongs
   in `never_lead_shapes` so WP-4 can enforce it; today it is prose-only. Both files are WP-6's.

---

# WP-9 follow-up 2 (2026-07-26) — `cover_lead_topic_family` copied into the ledger

Coordinator follow-up after WP-1 completed. `issue_meta.cover_lead_topic_family` is a new
weekly-required plan field (WP-1 in `chapter-plan-schema.md`; WP-5 enforcing it). Read as source of
truth, not edited: the schema's field description (line ~165) and
`validate-chapter-plan.py:_plan_cover_lead_families` (line ~1237 ff.).

## Phase 10 wording (item 3 of the Coverage continuity writes)

The ledger entry is now `{issue, date, topic_family, one_line, led_on}` where **`topic_family` is
COPIED VERBATIM from `issue_meta.cover_lead_topic_family`** and `led_on` from
`issue_meta.cover_leads_on`. Added a paragraph headed **"Copied — not re-derived from the rendered
cover, and not inferred from the lead piece,"** which states the failure mode rather than just the
rule: the rut rule **intersects** the plan's family against the ledger's families, so if the two
sides are produced by different routes they can disagree on any week where a story has two
defensible families (`uk_politics` vs `economy_markets`; `olympics` vs `football`) — and when they
disagree the intersection empties, so the rule **passes having checked nothing**. A green no-op is
worse than an absent check because it reads as coverage. Copying makes both sides carry the same
value by construction rather than by coincidence. The paragraph also records that the field is
**weekly-required and enum-checked** (omitted or out-of-enum hard-fails the plan), that the
validator's resolution chain — explicit field, else the `role: "lead"` piece families — survives
only as the compatibility path for pre-field plans, and that because the value is copied, the
Phase-4 enum check *is* the ledger's guarantee: an unrecognised family cannot reach state without
failing the plan first (the route by which issue #8's breach fell out of the ledger before
`cyber_privacy` existed).

## The two consistency checks

1. **Phase 4 — the field list DID predate the field. Fixed.** The list emitted
   `research_cut_at`, `window`, `cover_leads_on`, `lead_rationale`, `lead_override_reason` and no
   family. Added `cover_lead_topic_family` as a bullet between `cover_leads_on` and
   `lead_rationale`, naming it as the field the rut rule matches against the ledger, noting Phase 10
   copies it, and recording the weekly-required + enum-checked enforcement.
   *Correction made during this pass:* a first draft said an omitted field lets a plan "sail past"
   the rut rule. That is wrong against what WP-5 shipped — `check_weekly_coverage_meta` hard-fails
   the omission, and the fallback chain only prevents a crash for older plans. Both the Phase 4 and
   Phase 10 wordings were corrected to match the shipped validator.
2. **Phase 0a-ledger — checked, and genuinely needs no change.** It reads
   `state.cover_lead_ledger[]`, tallies `topic_family` where `led_on == "news"` across the last 4,
   and passes ledger + tally to the planner. That logic is provenance-agnostic: it consumes whatever
   value the row carries, and the change makes those values *more* reliable, not different in shape
   or vocabulary (same closed enumeration on both sides). Nothing edited in that sub-section.
   **Two related descriptions elsewhere were stale, though, and grep found them:**
   - § Coverage continuity called `cover_lead_ledger` a *"rendered-cover record"* — true of the
     seeded rows #18→#9 (which had to be read off the covers, since those issues shipped before the
     field existed) but false going forward, and precisely the phrasing that would license someone
     to re-derive the family. Rewritten to "cover-lead-of-record — one row per rendered weekly
     cover, but each row's `topic_family` copied from that issue's
     `issue_meta.cover_lead_topic_family`", with the #19-onward cutover stated.
   - The "After generation, update:" bullet and the Phase-0a key table now both name the copy source.

## Checks run

```
$ python3 - # field + enum presence
  cover_lead_topic_family in schema: True | hits in SKILL.md: 5
  cyber_privacy in schema enum: True | in SKILL.md: True
$ grep -n "cover_lead_ledger" SKILL.md   → 9 hits; every one that describes provenance now says
                                            "copied from issue_meta.cover_lead_topic_family".
$ sed -n '1246,1262p' validate-chapter-plan.py   # shipped resolution order read, not assumed:
    explicit field wins (enum-checked, hard-fail out-of-enum) → role="lead" piece families
    → compatibility path only; WP-5's own comment names WP-9's Phase 10 copy as the reason
    both sides "carry the same value by construction".
$ git diff --numstat 370341e -- SKILL.md   → 9  4   (baselined on the named commit, not stash)
$ git status --short → SKILL.md (WP-9) + WP-5/WP-6 script paths (parallel WPs, untouched here).
```

No new handoff notes. WP-1's field, WP-5's enforcement and WP-9's copy now agree.

---

# WP-9 follow-up 3 (2026-07-26) — line 274's stale parenthetical, and the never-lead sweep

Coordinator follow-up after WP-6 completed. Source of truth read, not edited:
`references/image-source-types.json` § `shows` (all four derived lists), SPEC §3.8 § "Never-lead,
resolved 2026-07-26", and `scripts/validate-issue.py` (WP-4's implementation).

## Line 274 — the parenthetical is DELETED, and the sentence rewritten

The stale parenthetical was mine, from the previous round: *"(`shows.never_lead_shapes` in the lookup
file; the checklist prose puts `portrait` in the same rung, so do not lead on one either)"*. It
existed **only** to work around an unreconciled discrepancy — WP-6's machine list then read
`never_lead_shapes: ["key_art", "product_shot"]` while the checklist's rank-5 prose included
`portrait`, so the doc hedged rather than pick a side. WP-6 has since reconciled all four lists
(`never_lead_shapes` and `last_resort_shapes` are both now `[key_art, product_shot, portrait]`) and
SPEC §3.8 resolved the question outright, so the hedge refers to a disagreement that no longer
exists. **Deleted rather than rewritten** — a parenthetical whose only job was to paper over a
contradiction has no residual content once the contradiction is gone.

The surrounding sentence now states the resolved rule positively: rank 5 is `key_art` ·
`product_shot` · `portrait`; **`key_art` and `portrait` may never be a lead figure, issue-wide, in
any band** (key art is the logo; a posed portrait is the person *not* doing the thing);
`product_shot` may lead **only where the band's subject is the product itself** — hardware, never a
game, software or service band, where it is a box standing in for something that moves. Kept the
"candid at an event is `event_photo`, not `portrait`" discriminator, because that is the line the
random-Pope-photo failure actually crossed.

## Drift found and fixed — 3 of the 4 citation sites were wrong

| Site | Said | Now says |
|---|---|---|
| **274** (Phase 3a researcher brief) | rank 5 named; *"`key_art` and `product_shot` may never lead"* + the workaround hedge on `portrait` | rank 5 = all three; `key_art`/`portrait` never lead **issue-wide**; `product_shot` conditional on the band's subject being the product |
| **311** (Phase 3b hierarchy) | *"(5) key art / product shot / posed portrait — last resort, and **never a lead figure**"* — flatly, which overstates `product_shot` | rung membership unchanged; never-lead split into the issue-wide pair + the conditional |
| **425** (Phase 7.6 shape budgets) | *"no `key_art` leading **Pixel & Byte**"* — the pre-resolution letter of §3.8, band-scoped and `key_art`-only | at most one `key_art` in Pixel & Byte **plus** no `key_art`/`portrait` as any band's lead issue-wide, `product_shot` conditional; also added the Touchline `event_photo` rule, which was missing from this list |
| **454** (Phase 7.7) | Wikimedia retirement + shape floor only — makes no never-lead claim | unchanged, correctly |

The pattern in all three: my earlier edits were written against §3.8's *original* letter (Pixel &
Byte, `key_art` only) and WP-6's *then*-current machine list, so they were narrower than the resolved
rule in one direction and broader in another (`product_shot`).

## Verification

```
$ python3 - # WP-6's reconciled lists, read from image-source-types.json
  never_lead_shapes:   ['key_art', 'product_shot', 'portrait']
  last_resort_shapes:  ['key_art', 'product_shot', 'portrait']
  rank 5:              ['key_art', 'product_shot', 'portrait']  "LAST RESORT, never a lead."
  information_figure_shapes: ['diagram', 'map', 'chart', 'artefact']
$ grep -n "key_art leading|key art leading|key_art may not|only key" SKILL.md   → no output (clean)
$ grep -n "never lead|never a lead|may never|rank 5|last resort" SKILL.md        → 2 hits (274, 311),
    both stating the resolved three-way rule; no band-scoped or key_art-only survivor.
$ git diff --numstat fd32ba6 -- SKILL.md   → 3  3   (baselined on the named commit, not stash)
```

**Cross-checked against WP-4's implementation** (`validate-issue.py`, read only):
`NEVER_LEAD_FALLBACK = ("key_art", "product_shot", "portrait")` with
`CONDITIONAL_LEAD_SHAPES = ("product_shot",)` and `hard_never = tuple(s for s in never_lead if s not
in CONDITIONAL_LEAD_SHAPES)` — i.e. `key_art`/`portrait` hard-fail as leads issue-wide while
`product_shot` is treated conditionally. **SKILL.md now describes exactly what the validator
enforces**, so no handoff note is needed: the JSON's flat `never_lead_shapes` is deliberately the
plain reading, and WP-4 carries the §3.8 conditional in code with a comment saying so.

No new handoff notes. WP-6's lists, SPEC §3.8, WP-4's enforcement and SKILL.md's prose now agree.
