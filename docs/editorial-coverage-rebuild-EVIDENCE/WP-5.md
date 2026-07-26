# WP-5 — Upstream production aids

**SPEC:** `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md` §1, §2, §3.1, §3.2, §3.6, §3.7, §3.8,
§3.11, §3.14, §4.
**Files touched (exclusive, both mine):**

- `.claude/skills/the-signal/scripts/validate-research-bundle.py`
- `.claude/skills/the-signal/scripts/validate-chapter-plan.py`

Nothing else. No repo fixtures were added (see § Handoff notes → WP-10).
`docs/editorial-coverage-rebuild-PROGRESS.md` was **not** edited.

**Both scripts remain upstream production aids, not ship gates (SPEC §1).** No fourth ship gate was
added. Exit codes are unchanged (0 pass / 1 fail / 2 usage) and every failure report now names the
distinction explicitly — a hard fail here is a **PRODUCTION HALT** (the planner or the writers do not
spawn), never a ship failure, and the three gates are still `validate-issue.py`'s image checks, its
markup contracts, and the Phase 9.5 holistic read.

---

## 0. PRIORITY ZERO — the live breakage, fixed

WP-6 retired `wikimedia_max_pct` / `wikimedia_max_count` from `thresholds` in
`references/image-source-types.json` into an auditable `retired_thresholds` record (SPEC §3.14).
`validate-research-bundle.py` read both **unguarded** at its Rule 2, so Phase 3b crashed in-tree.

**Reproduced** against the state WP-6 handed over (`37bf00b`, "WP-6 DONE"), run against the current
lookup file:

```
$ python3 $S/head-mirror/scripts/prewp5-validate-research-bundle.py \
      $S/bundle-repro-keyerror.json --run-date 2026-07-26
Traceback (most recent call last):
  File ".../prewp5-validate-research-bundle.py", line 524, in <module>
    main()
  File ".../prewp5-validate-research-bundle.py", line 458, in main
    if wm > thresholds["wikimedia_max_count"]:
            ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'wikimedia_max_count'
exit=1
```

**Fixed.** Both reads are deleted. Rule 2 is now a comment block recording *why* the ceilings went
(a ceiling with no matching floor reads as a target) and forbidding their reinstatement, and the rule
is replaced by a `min_distinct_shapes` **floor** over `image_candidates[].shows`. The `shows` enum and
the threshold are **read from the lookup file**, exactly as WP-6's `check-image-diversity.sh` reads
them (`lookup["shows"]["values"].keys()`, `thresholds["min_distinct_shapes"]`,
`information_figure_shapes`, `last_resort_shapes`) — no second copy of the enum exists in this script,
so the two cannot drift. Wikimedia is still bound by Rule 1 (the RT-5 single-domain cap) like any other
domain.

Same command, same input, same flags, on the fixed script:

```
$ python3 .claude/skills/the-signal/scripts/validate-research-bundle.py \
      $S/bundle-repro-keyerror.json --run-date 2026-07-26
=== Phase 3b: validate-research-bundle.py (upstream production aid — NOT one of the three ship gates) ===
run-date (facts/loops anchor):  2026-07-26
facts entries:                  0
image_candidates entries:       2
valid URL entries:              2
by source type:                 {'wikimedia': 2}
by shape (what they SHOW):      {'event_photo': 2}
distinct shapes:                1 (floor 3)
open loops (§3.7):              not checked (no --state)
…
FAIL — rule violations:
  Shape diversity: 1 distinct `shows` value(s) (['event_photo']) < minimum of 3 (thresholds.min_distinct_shapes).
    This FLOOR replaced the retired wikimedia_max_pct / wikimedia_max_count CEILINGS (SPEC §3.14):
    …
  RT-5 hard fail: upload.wikimedia.org provides 2/2 images (100.0%). Cap is 50%.
  Source-type diversity: 1 types represented (['wikimedia']) < minimum of 3.
  Unique-URL minimum: 2 < required 16.
exit=1
```

No `KeyError`; the gate runs and reports. The exit-1 is the fixture being deliberately bad (one shape,
one domain, two URLs) — every rule that fires there is a pre-existing rule plus the new shape floor.

`grep` confirms no live read of either retired key remains in either of my files (the four hits are
prose: the docstring's retirement note and the Rule 2 comment).

---

## 1. What changed — `validate-research-bundle.py`

| Rule | Status | Detail |
|---|---|---|
| Fabricated / keyword URLs, page URLs, `verified` block, RT-5, source-type diversity, unique-URL floor, ambiguous/restricted handling | **unchanged** | Read before extending; not one weakened. |
| Facts gate F1–F4 (claim/status/date/source_url, the **temporal catch** F3, opinion provenance F4) | **unchanged** | F3 is the "Norris on pole" catch; untouched. |
| Rule 2 (Wikimedia ceilings) | **deleted** | Replaced by the shape floor — § 0 above. |
| §3.2 `shows` | **new** | REQUIRED; hard-fails a value outside the canonical enum (a typo'd shape is invisible to WP-4's §3.8/§3.9 budgets). |
| §3.2 `capture_year` | **new** | REQUIRED integer, `1400 … run-date year`; `null` legal only when `shows ∈ {diagram, chart}` (then a warning, see § Findings 2). |
| §3.2 `licence{holder, code, url, allows_derivatives}` | **new** | All four required; `code: UNKNOWN` warns; `allows_derivatives: false` warns that `extract-covers.py` will refuse to crop it (§3.10). |
| §3.14 `min_distinct_shapes` | **new** | Bundle-wide floor over `shows`. |
| §3.2 `facts[].resolves_loop` | **new** | F5: non-empty string when present; with `--state`, an id matching no loop is a hard fail (it is a foreign key, not a label). |
| §3.7 `--state` | **new flag** | Matured loop (`status: "open"` and `expected_resolution_date <= run_date`) with no matching `resolves_loop` = hard fail. |

`--state` semantics, per WP-9's handoff 3: tolerant of an absent/empty `open_loops` (no loops = no
failure, with an explicit warning that the check found nothing rather than passing); an explicitly
passed path that is missing or unparseable is **exit 2**, so a mistyped path can never look like a
pass. Without `--state` the script prints `ADVISORY: … the SPEC §3.7 open-loop resolution rule did NOT
run`. The flag spelling matches SKILL.md Phase 3b line 302 verbatim
(`--run-date <today> --state /tmp/the-signal/state/signal-state.json`).

## 2. What changed — `validate-chapter-plan.py`

All new rules are inside the **weekly** branch (`check_weekly_plan`), so special/mx plans are
untouched. New rules 14–19:

14. **§3.1 issue_meta** — `research_cut_at` (UTC ISO8601 instant, and **must equal** `window.to`),
    `window{from,to}` (instants, `from < to`), `cover_leads_on ∈ {news, long_read}`,
    `lead_rationale` ≥ 120 chars, `lead_override_reason` well-formed if present.
15. **§3.1 long_read vintage** (acceptance #1) — `vintage` required; `material_span` (en-dash
    `YYYY–YYYY`) + `latest_development` (`YYYY-MM`) required iff `evergreen` and forbidden when
    `news`; `latest_development` must fall inside `material_span`; the three fields on any other
    chapter are rejected (one anchor, one vintage).
16. **§3.1 week_in_numbers rows** — `rows[]` required and non-empty; each row needs `key` and
    `source_band`, where `source_band` is the `chapter_id` of a chapter **present in this plan** or
    the literal **`"state"`** (handoff 2).
17. **§3.6 the rut rule** (acceptance #4) — below.
18. **§3.11 sport tokens** — wherever the plan declares a result's `sport`: `multi_sport` hard-fails;
    an off-list token **warns**. The 22 tokens are **parsed** from
    `references/spec/data-contracts.md` § The closed sport-token list (WP-1 says appending a token
    needs no consumer code change), with a built-in fallback used only with a loud warning. Anything
    under a `sports_calendar` key is skipped — that is the one namespace where `multi_sport` is legal.
19. **(warn)** a weekly `pieces[].topic_family` outside the closed enumeration. Weekly plans never ran
    `check_section_shape`, so this field was previously unvalidated for weeklies; the rut rule reads
    it, and it cannot match a family it does not recognise. Warn, not fail — this was not in scope as
    a blocking rule.

Plus **handoff 7**: `cyber_privacy` added to `TOPIC_FAMILIES` (news_geopolitics cluster), with the
reason inline. The two copies of the enumeration now agree.

The rut rule, in full, fails only when **all three** hold: the same `topic_family` appears as
`led_on: "news"` in ≥3 of the last 4 `cover_lead_ledger` entries; **and** the plan sets
`cover_leads_on: "news"` on that family; **and** `lead_override_reason` is absent or under 80 chars.
It is **overridable by construction** — 80 characters of written reasoning and the plan passes, with no
approval step — and the failure message says so in capitals. When the override is present and
sufficient the plan passes with an audit *warning* recording that the rut was acknowledged. Missing or
unreadable state → the rule is **skipped with a warning**, never silently passed. Leading on
`long_read` breaks the rut by itself and the rule returns early.

## 3. Evidence — acceptance criterion #1 (a weekly plan omitting `vintage` is rejected)

Fixtures: `plan-weekly-valid.json` (a fully valid 13-band weekly) and `plan-no-vintage.json`
(identical, with `vintage` / `material_span` / `latest_development` deleted from the `long_read`
chapter — a single-field delta).

**Firing case:**

```
$ python3 .claude/skills/the-signal/scripts/validate-chapter-plan.py $S/plan-no-vintage.json
NOTE — 8 warning(s) (non-blocking):
…
FAIL — 1 error(s) found in '…/plan-no-vintage.json':

  [1] [VINTAGE] chapters[3] ('long_read'): missing required 'vintage' (SPEC §3.1) — 'news' (a
      development of THIS week) or 'evergreen' (a standing story whose material predates the issue).
      Without it the stitcher stamps the issue date on the anchor and the validator cannot tell news
      from feature, which is defect A: an evergreen Long Read that reads as breaking news.

PRODUCTION HALT, not a ship failure. This is an upstream production aid (SPEC §1),
not a fourth ship gate …
exit=1
```

**Passing case** (same plan, `vintage: "evergreen"` + `material_span: "1901–2021"` +
`latest_development: "2021-03"`):

```
$ python3 .claude/skills/the-signal/scripts/validate-chapter-plan.py $S/plan-weekly-valid.json
PASS — '…/plan-weekly-valid.json' is valid.
  Format: weekly  |  Execution: parallel  |  Chapters: 13
exit=0
```

Related, same rule, both directions:

```
$ python3 … $S/plan-news-vintage-with-span.json
  [1] [VINTAGE] chapters[3]: 'material_span' is forbidden when vintage='news' (chapter-plan-schema.md)…
  [2] [VINTAGE] chapters[3]: 'latest_development' is forbidden when vintage='news' …
exit=1
```

## 4. Evidence — acceptance criterion #4 (the rut rule)

Fixture state `state-rutted.json`: `cover_lead_ledger` whose last 4 entries carry
`uk_politics/news`, `uk_politics/news`, `space_exploration/long_read`, `uk_politics/news` → 3 of 4.
The plan leads on news with a `uk_politics` lead piece. (The **real** repo state is *not* rutted —
`uk_politics` appears once as `news` in its last 4 — so the baseline plan passes against it, which is
the pre-condition for this being a real test and not an artefact.)

**Firing case — no override reason:**

```
$ python3 … $S/plan-weekly-valid.json --state $S/state-rutted.json
FAIL — 1 error(s) found in '…/plan-weekly-valid.json':

  [1] [RUT] cover-lead rut (SPEC §3.6): topic_family ['uk_politics'] appears as led_on='news' in [3]
      of the last 4 cover_lead_ledger entries, and this plan sets cover_leads_on='news' on the same
      family [family resolved from chapters[].pieces[role='lead'].topic_family (derived)], with no
      lead_override_reason (>= 80 chars required).
        THIS IS NOT A BAN. Lead on it again if the news warrants it — set
      issue_meta.lead_override_reason to >= 80 characters saying why THIS week's development earns the
      cover over everything else that was available, and the plan passes. … Do not resolve it by
      suppressing the story.
exit=1
```

**Passing case (a) — the override is written (164 chars). Nothing else changed:**

```
$ python3 … $S/plan-rut-overridden.json --state $S/state-rutted.json
  (9) [RUT] rut acknowledged and overridden in writing: ['uk_politics'] led on news in [3] of the
      last 4 covers and this plan leads on news again. lead_override_reason is present (164 chars),
      so the plan PASSES — that is the rule working as designed, not a loophole.
PASS — '…/plan-rut-overridden.json' is valid.
exit=0
```

**Passing case (b) — the rut is on a family this plan does not lead on (`state-rutted-other.json`,
`us_politics` 3 of 4). The rule must not fire:**

```
$ python3 … $S/plan-weekly-valid.json --state $S/state-rutted-other.json
PASS — '…/plan-weekly-valid.json' is valid.
exit=0
```

## 5. Evidence — acceptance criterion #5 (a matured open loop with no resolving fact)

Fixture state `state-open-loop.json` carries three loops: one **matured**
(`loop_2026-07-19_wc-final-open`, `status: "open"`, ERD 2026-07-19 ≤ run date), one open but not yet
due (ERD 2026-08-02), one `dropped` with a past ERD (which must **not** mature). Both bundles carry 16
clean candidates across 4 domains and 4 shapes, so the only variable is the resolving fact.

**Firing case:**

```
$ python3 .claude/skills/the-signal/scripts/validate-research-bundle.py \
      $S/bundle-loop-unresolved.json --run-date 2026-07-26 --state $S/state-open-loop.json
=== Phase 3b: validate-research-bundle.py (upstream production aid — NOT one of the three ship gates) ===
run-date (facts/loops anchor):  2026-07-26
facts entries:                  1
image_candidates entries:       16
by source type:                 {'wikimedia': 4, 'open_access_journal': 4, 'government': 4, 'press_kit': 4}
by shape (what they SHOW):      {'event_photo': 4, 'diagram': 4, 'artefact': 4, 'gameplay': 4}
distinct shapes:                4 (floor 3)
open loops in state:            3 (1 matured on or before 2026-07-26)
matured loop ids:               ['loop_2026-07-19_wc-final-open']

FAIL — rule violations:
  §3.7 MATURED LOOP UNRESOLVED: 'loop_2026-07-19_wc-final-open' — expected resolution 2026-07-19, on
  or before the run date 2026-07-26, status=open.
    claim: World Cup final, Spain v Argentina, MetLife
    owed by band: 'touchline' (opened in issue 17).
    No facts[] entry carries resolves_loop='loop_2026-07-19_wc-final-open'. … This is defect D: the
    World Cup final was carried as upcoming and the result never reported.
exit=1
```

**Passing case** — identical bundle plus one fact carrying
`resolves_loop: "loop_2026-07-19_wc-final-open"`:

```
$ python3 … $S/bundle-loop-resolved.json --run-date 2026-07-26 --state $S/state-open-loop.json
open loops in state:            3 (1 matured on or before 2026-07-26)
matured loop ids:               ['loop_2026-07-19_wc-final-open']

PASS — research bundle complies with image-integrity, image-provenance (shows/capture_year/
licence), fact-provenance and open-loop-resolution rules.
exit=0
```

**Tolerance, as WP-9 required** (and confirming WP-1's handoff 6 — the two seeded loops are `dropped`
and do not mature, which is why the fixture above exists):

```
$ python3 … $S/bundle-loop-unresolved.json --run-date 2026-07-26 --state state/signal-state.json
open loops in state:            2 (0 matured on or before 2026-07-26)
PASS …                                                                       exit=0

$ echo '{}' > $S/state-empty.json && python3 … --state $S/state-empty.json
open loops in state:            0 (0 matured on or before 2026-07-26)
  state carries no `open_loops[]` — SPEC §3.7 has nothing to mature this run. That is legal (a first
  run, or a week that opened no loops), not a pass mark.
PASS …                                                                       exit=0

$ python3 … --state /nope/state.json
ERROR: --state /nope/state.json not found                                    exit=2
```

## 6. Evidence — §3.2 bundle fields, §3.11 sport tokens, §3.1 window / rows

**§3.2, one bundle carrying nine deliberate defects** (`bundle-bad-records.json`):

```
$ python3 … $S/bundle-bad-records.json --run-date 2026-07-26 --state $S/state-open-loop.json
Warnings:
  entry[3]: capture_year is null on a 'diagram' — legal ONLY for a SYNTHETIC figure …
  entry[4]: licence.code is UNKNOWN. Legal in the bundle and a signal to the planner NOT to build on it …
  entry[5]: licence.allows_derivatives is false (an ND licence). … extract-covers.py will REFUSE to crop …

FAIL — rule violations:
  facts[1]: resolves_loop='loop_typo_9999' matches no id in state.open_loops[] (known ids: […])
  entry[0]: missing required `shows` (SPEC §3.2) …
  entry[1]: shows='in-engine' is not in the canonical enum ['artefact', 'chart', 'diagram', 'document',
            'event_photo', 'gameplay', 'in_engine', 'key_art', 'map', 'portrait', 'product_shot'] …
  entry[2]: capture_year is null but shows='artefact'. Null is legal ONLY when shows ∈ ['diagram','chart'] …
  entry[4]: licence is missing required key 'allows_derivatives'.
  entry[4]: licence.holder='' must be a non-empty string …
  entry[4]: licence.url='not-a-url' must be an http(s) URL to the licence deed.
  entry[6]: missing required `capture_year` (SPEC §3.2) …
  entry[7]: capture_year=2031 is outside 1400–2026. An image cannot be captured after the run date.
exit=1
```

**§3.11** (`plan-multi-sport.json` — one ledger row tagged `multi_sport`, one tagged `lawn_bowls`):

```
  (9) [SPORT-TOKENS] plan.chapters[4].results_ledger[1].sport='lawn_bowls' is not in the canonical
      sport-token list (22 tokens, references/spec/data-contracts.md § Sport tokens). WARNING, not a
      failure — the multi-sport-games long tail (lawn bowls, para events) must never block a ship. …
FAIL — 1 error(s):
  [1] [SPORT-TOKENS] plan.chapters[4].results_ledger[0].sport='multi_sport' is forbidden as a RESULT's
      sport (SPEC §3.11). It is legal in exactly one place — state's sports_calendar[].sport …
exit=1
```

The "22 tokens" in that message is the count **parsed live** from `data-contracts.md`; no fallback
warning was emitted, so the parse worked against WP-1's real list.

**§3.1 `source_band`** — the literal `"state"` alone passes (handoff 2); a band absent from the plan
fails:

```
$ python3 … $S/plan-source-band-state.json     → PASS   exit=0
$ python3 … $S/plan-source-band-absent.json
  [1] [WIN-ROWS] chapters[1].rows[0].source_band='rotating_1' is neither the literal 'state' nor the
      chapter_id of a chapter present in this plan. Bands in this plan: [… 13 ids …]. A row cannot
      claim provenance from a band the issue does not carry.                 exit=1
```

**§3.1 window** (`plan-bad-window.json`, `window.to` moved a day and the rationale cut to 33 chars):

```
  [1] [WINDOW] issue_meta.research_cut_at=2026-08-02T02:10:00Z disagrees with
      issue_meta.window.to=2026-08-03T02:10:00Z. They are the same instant by definition …
  [2] [COVER-LEAD] issue_meta.lead_rationale is 33 chars, below the 120-char floor. …
exit=1
```

**Handoff 7** — a plan leading on `cyber_privacy` now passes instead of hard-failing as
"not in the closed enumeration":

```
$ python3 … $S/plan-cyber-privacy.json         → PASS   exit=0
```

## 7. No existing check weakened

```
$ python3 .claude/skills/the-signal/scripts/validate-chapter-plan.py --test
…
76/76 tests passed.
PIPELINE TEST: PASS
```

All 76 pre-existing inline cases (legacy special schema, mx skeleton-driven checks, timing sanity,
personalisation floor, release radar, sub-formats, discovery quota, key_facts provenance) still pass
unchanged. In the bundle validator the temporal catch (F3), the `verified`-block rule, the page-URL
rule, RT-5 and the unique-URL floor were read before extending and are byte-for-byte unchanged.

```
$ python3 -m py_compile .claude/skills/the-signal/scripts/validate-research-bundle.py \
                        .claude/skills/the-signal/scripts/validate-chapter-plan.py
BOTH_COMPILE_OK
```

## 8. Repo state

```
$ git status --short
 M .claude/skills/the-signal/scripts/validate-chapter-plan.py    ← WP-5
 M .claude/skills/the-signal/scripts/validate-issue.py             (WP-4, in flight)

$ git diff --numstat
635  4   .claude/skills/the-signal/scripts/validate-chapter-plan.py
11   0   .claude/skills/the-signal/scripts/validate-issue.py

$ git log --oneline -1 -- .claude/skills/the-signal/scripts/validate-research-bundle.py
eb58747 WP-3 DONE: vintage rendering, Touchline restructure, golden regenerated
$ git diff --stat -- .claude/skills/the-signal/scripts/validate-research-bundle.py
(empty)
```

`validate-research-bundle.py` does **not** appear as modified because the orchestrator's mid-flight
snapshot (`eb58747`) swept up WP-5's completed edits to it; HEAD and the working tree are identical for
that file, and its 926 lines are WP-5's version (verified by re-running the fixed script above and by
`git diff` being empty). The only other modified path belongs to WP-4, running in parallel. The 4
deleted lines in `validate-chapter-plan.py` are the retired-Rule-2-free docstring lines and the
`MX_DEFAULT_STATE_PATH` definition rewritten in place as `DEFAULT_STATE_PATH` + a back-compat alias —
no content dropped. Nothing committed; the orchestrator commits.

## 9. Handoffs closed

| Handoff | Status |
|---|---|
| **WP-6 §7.1** — delete the two retired-threshold reads, replace with `min_distinct_shapes` over `shows` | **closed** (§0) |
| **WP-9 note 3** — `--state` does not exist on `validate-research-bundle.py`; must tolerate absent/empty `open_loops` | **closed** (§1, §5) |
| **WP-1 note 1** — the bundle's URL key is `url_or_keyword`, not `url` | **closed** — every new read keys off `url_or_keyword`; no `c["url"]` exists anywhere in the script |
| **WP-1 note 2** — `source_band` must accept the literal `"state"` | **closed** (§6) |
| **WP-1 note 6** — the seeded loops are `dropped`, so a fixture with `status: "open"` is needed | **closed for WP-5's half** — fixture built, both directions shown (§5) |
| **WP-1 note 7** — add `cyber_privacy` to `TOPIC_FAMILIES` | **closed** (§6) |

## 10. Findings — SPEC / contract text that is wrong or incomplete (reported, not re-specified)

1. **SPEC §3.6's rut rule is specified against a field no contract carries.** The rule needs "this
   plan sets `cover_leads_on: "news"` **with that same `topic_family`**", but nothing in §3.1,
   `chapter-plan-schema.md` or `data-contracts.md` § Chapter plan carries the *cover lead's*
   `topic_family`: `cover_leads_on` distinguishes news-vs-long_read only, and
   `cover_lead_ledger[].topic_family` is written at **publish** (SKILL.md Phase 10) from the
   orchestrator's reading of the rendered cover. So the validator cannot be handed the family.
   Implemented resolution, documented in the code and deliberately conservative:
   (a) `issue_meta.cover_lead_topic_family` if the planner supplies it — **not a contract field
   today**; accepted so an explicit declaration always wins, and nothing is rejected for omitting it;
   (b) otherwise the families of the plan's `role: "lead"` pieces, the pool the cover lead is drawn
   from; (c) if neither resolves, a **warning** that the rule could not be evaluated — never a
   failure, because demanding prose about a choice the planner never stated would be worse than not
   checking. **Request to WP-1/orchestrator:** add `issue_meta.cover_lead_topic_family` (REQUIRED when
   `cover_leads_on == "news"`) to §3.1 and the schema. It is the one field that makes §3.6 exact, and
   it is also what Phase 10 currently re-derives by hand.
2. **`capture_year: null` is conditioned on something no field records.** SPEC §3.2 and
   `data-contracts.md` both say null is legal only when `shows ∈ {diagram, chart}` **and the asset is
   synthetic**, but the bundle carries no `synthetic` flag. The enum half is enforced as a hard fail;
   the synthetic half is emitted as a warning naming it as taken on the researcher's word. If the
   distinction should be machine-checkable, WP-1 needs a field.
3. **SKILL.md line 943 (WP-9's file) still advertises the retired thresholds** as live rules of this
   script: *"Wikimedia ≤30%/≤4"* in the pipeline-scripts table. Stale since WP-6; the row should read
   `min_distinct_shapes` (shape floor) + `--state` open-loop resolution. Not my file — reported.
4. **`chapter-plan-schema.md` says `material_span`/`latest_development` are "forbidden when
   `vintage == "news"`" and `vintage` is "forbidden on every other chapter", without saying who
   enforces it.** I made both hard fails (a news anchor carrying span metadata means the declaration
   and the material disagree; two vintage declarations render two contradictory `data-vintage`
   attributes). If either was meant to be advisory, say so and I will downgrade.
5. **Pre-existing, unrelated to this build:** the weekly branch of `validate-chapter-plan.py` has
   never validated `pieces[]` at all — `check_section_shape` runs only on the legacy/special path, so
   a weekly plan's `topic_family`, word floors and Catch-Up "no bare namedrops" rule are unenforced
   for weeklies. I added a **warning** for off-enum weekly `topic_family` (rule 19) because the rut
   rule reads that field, and stopped there: converting the whole shape check to weekly plans is a
   scope decision, not mine to take mid-build.

## 11. Left undone / notes

1. **Fixtures live in the scratchpad, not the repo** — as instructed. Two generators plus their
   output: `make-fixtures.py` (bundles + states) and `make-plans.py` (weekly plans), under
   `/tmp/claude-0/-home-user-the-signal/81541fa2-7765-5cd6-810f-5027bff091c8/scratchpad`. **WP-10
   should own permanent versions** under `references/fixtures/coverage-rebuild/`; the ones worth
   keeping, by acceptance criterion:
   - #1: `plan-weekly-valid.json` (baseline, passes) + `plan-no-vintage.json` (one-field delta).
   - #4: `state-rutted.json` + `plan-rut-overridden.json` + `state-rutted-other.json` (the
     must-not-fire case, which is the one that proves it is not a suppression gate).
   - #5: `state-open-loop.json` + `bundle-loop-unresolved.json` / `bundle-loop-resolved.json`. This
     state fixture also serves WP-4's acceptance #6 — one `open` loop with a past ERD, one open-but-
     not-due, one `dropped` with a past ERD.
   - the regression that would have caught this build's breakage: `bundle-repro-keyerror.json`.
   The plan fixtures are generated rather than hand-written because a valid weekly plan needs all ten
   required bands and a ≥6,000-word allocation; keep the generator if the fixtures are adopted.
2. **The rut rule cannot be demonstrated against real state**, by design: the real
   `cover_lead_ledger`'s last 4 entries put `uk_politics` on `news` once. That is a *good* property —
   the check is not firing on live data — and it is why acceptance #4 needs a fixture ledger.
3. **`min_distinct_shapes` is enforced twice, deliberately and on different objects**: over the
   *bundle's* `image_candidates[].shows` here (so the planner has shapes to route), and over the
   *rendered* `data-shows` by WP-6's `check-image-diversity.sh` (so the writers actually used them).
   Neither substitutes for the other — a bundle can offer four shapes and the issue still render one.
4. **Not done, deliberately:** per-band shape budgets (§3.8), the caption-vintage rule (§3.9), the
   rendered loop check and `data-sport` in HTML are all WP-4's — this WP checks the plan and the
   bundle, upstream, and never opens the rendered issue.
5. **Issue #18 was not touched**, and no check here reads it: #18 is a rendered artefact, and both of
   my scripts run before any HTML exists.
6. **No version bump / CHANGELOG entry** — WP-12 owns those.
