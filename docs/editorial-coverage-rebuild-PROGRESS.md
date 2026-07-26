# Editorial Coverage Rebuild — PROGRESS

Build ledger for `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md`.
Each WP appends to its own section. Do not rewrite another WP's entry.

**Status key:** `PENDING` · `IN PROGRESS` · `DONE` · `BLOCKED` · `PARTIAL`

## Ledger

| WP | Title | Status | Defects | Notes |
|----|-------|--------|---------|-------|
| WP-1 | Data contracts (foundation) | DONE | A B C D E | 3 rounds; contracts + state seed + `cyber_privacy` + 22 sport tokens. 9 handoffs, 1 resolved, 8 routed |
| WP-2 | Editorial prose spec | DONE | A C D E | 13 blocks across 2 files, `(v8.44, WP-2)`; ~50 identifiers verified byte-for-byte. Raises R-2 + 2 naming divergences |
| WP-3 | Structure of record + stitcher + CSS | DONE | A C D | golden regenerated, `verify-weekly-golden.sh` exits 0 (re-run by orchestrator). Caught WP-8's placeholder-stamping bug |
| WP-4 | Rendered-issue checks | IN PROGRESS | A B D E | owns 6 of 12 acceptance criteria; implements against §3.4a as-built |
| WP-5 | Upstream production aids | DONE | A C D E | 2 rounds; `KeyError` fixed, criteria #1/#4/#5 firing, 6 handoffs closed, 76/76 self-tests |
| WP-6 | Image taxonomy + specificity doctrine | DONE | E | `shows` enum canonical; found the missing Steam akamai host and the mistyped Springer domain |
| WP-7 | Daily inputs | DONE | D | 9 feeds + 5 domains, all URLs 200-verified; keyword sets regressed over 3286 titles |
| WP-8 | Asset provenance + licence safety | DONE | E | manifest 438 entries, 13 URLs recovered from git history; ND refusal armed but cannot fire on #18 (frozen, licences unpopulated) |
| WP-9 | Pipeline phase wiring | DONE | C D | 4 rounds; window + open loops wired, 4 stale cap claims retired, researcher brief gained shape intent |
| WP-10 | Verification harness | PENDING | all | last; owes handoff 6 (needs an `open` loop fixture) |
| WP-11 | Daily routing | DONE | D | 3 lists changed, 4 audited and left alone; behaviourally verified against real blobs. Raises open risk R-1 |
| WP-12 | Skill version + changelog | PENDING | — | added mid-build; runs last, after WP-10 |

## Open risks

Things the build surfaced that are **not** defects in this work but are now more consequential
because of it. Recorded rather than silently fixed — each needs an owner decision.

| # | Risk | Raised by | Status |
|---|------|-----------|--------|
| R-2 | **`source_band` legitimises a drift nobody decided on.** The Week in Numbers was specified (v8.36) as the *personal* stat strip rendered from `state/signal-state.json` — training volume, spending, the reader's own week in figures. Issue #18's table is mostly news datums instead: pole margin, Bank Rate, leaders-in-a-decade. SPEC §3.1's `source_band` field, added so an evergreen datum can be kept out of "Datums of the Week", quietly *ratifies* that drift by making a news-band source a legal value. The mechanical fix for defect A works either way, but whether the section should be personal again is an editorial question this build should not answer by accident. | WP-2 | **open — owner decision** |
| R-1 | **The daily's Headlines has no guaranteed news slot**, and now has four more eligible sport domains (`sport`, `cricket`, `cycling`, `athletics`). The crowding is bounded but not zero, so a heavy sport day could push world news off the front. This is a pre-existing property of `render.js`'s Headlines composition, not something WP-11 introduced — WP-11 correctly declined to change the `NEWS = {world, finance}` guarantee, because adding sport there would let a cricket item satisfy the news slot and make *world* evictable, which is worse. Fixing it properly means a guaranteed-news-slot design, which is a product decision about the daily brief and outside this SPEC's scope. | WP-11 | **open — owner decision** |

**Orchestrator owns this file from 2026-07-26.** WP-1 wrote here during rounds 1–2 while it was the
only agent running; with several WPs now reporting concurrently, all others write
`docs/editorial-coverage-rebuild-EVIDENCE/WP-<N>.md` instead and the orchestrator merges.

## Expected-failure ledger

Issue #18 (`issues/signal_weekly_2026-07-26.html`) is the regression fixture and is **frozen**.
These failures are the proof the checks work and are **not** to be repaired.

| Check | Expected on #18 | Recorded |
|-------|-----------------|----------|
**Result: Issue #18 now exits 1 with 5 failures (was 0).** Two of the three predictions were **wrong**, and
WP-4 corrected them rather than forcing the predicted outcome. Recorded as measured, not as hoped:

| Check | Predicted | **Measured** |
|-------|-----------|--------------|
| caption-vintage (§3.9) | FAIL at FIG 03 | **WRONG — inert.** #18 declares *no figure attributes at all*, so there is no `data-capture-year` to compare and the check correctly WARNs that it cannot speak. Criterion #3 is instead proven on #18's **own FIG 03 caption wording** with only the capture year added: `2007 < claim 2021` fires, the credit-span year is correctly not counted, the SPEC's suggested rewrite passes, `""` is legal, `"c. 2007"` fails |
| image shape budget (§3.8) | FAIL via Pixel & Byte `key_art` lead | **FAIL, different route.** Distinct-shapes 0/3 and the Long Read's missing information figure. The `key_art` clause also cannot speak — same root cause: no declared shapes |
| long-read vintage (§3.4) | FAIL — no `data-vintage` | **FAIL as predicted** |
| — | *(unpredicted)* | **FAIL `figure-provenance` 11/11** |
| — | *(unpredicted)* | **FAIL `cover-leads-on`** |

The common root cause behind both wrong predictions is worth keeping: **#18 carries no rebuild-era
figure attributes**, so every check keyed to them is inert on it rather than failing. The shape budget
still catches it by counting *declared* shapes against the floor — which is the more robust route, since
it fails on absence rather than requiring a specific bad value to be present.

**Archive sweep: 34 files, 0 regressions on pre-existing checks.** #16/#17 stay green via an archive
exemption (no rebuild-era attribute present at all).

---

## WP-1 — Data contracts (foundation)

**2026-07-26 — DONE.** SPEC §3.1, §3.2, §3.3, §3.5, §3.12 implemented as written. Field names,
enum values and required/optional status are exactly as specified; two places where the SPEC's prose
did not match the repo are recorded in § Handoff notes rather than silently re-specified.

**Files touched (3, all WP-1-owned):**

1. `.claude/skills/the-signal/references/chapter-plan-schema.md` — +110/−1 (the one deletion is a
   typo fix inside a line this WP added). Added, per SPEC §3.1, all enforced by
   `validate-chapter-plan.py` (WP-5):
   - `issue_meta.research_cut_at` (ISO8601 UTC instant, weekly-required, copied from state)
   - `issue_meta.window` `{from, to}` (weekly-required; `to` == `research_cut_at`, `from` == previous cut)
   - `issue_meta.cover_leads_on` — enum `news` | `long_read` (weekly-required)
   - `issue_meta.lead_rationale` — weekly-required, `minLength: 120`, must name what was rejected
   - `issue_meta.lead_override_reason` — conditionally required (≥80 chars) only when the rut rule §3.6 trips
   - chapter-level `vintage` (enum `news` | `evergreen`), `material_span` (`YYYY–YYYY`, en-dash) and
     `latest_development` (`YYYY-MM`) on the `long_read` chapter; the latter two required iff evergreen
   - chapter-level `rows[]` on `week_in_numbers`, each row requiring `key` + `source_band`
   - a new worked example (§ Coverage-Window / Cover-Lead / Vintage Example) and a note in
     § Topic Family Enumeration declaring that enumeration the single vocabulary for state's
     `cover_lead_ledger[].topic_family`
   - Conditional-requirement style follows the file's existing convention (stated in the field
     `description`, enforced by the validator) rather than JSON-Schema `required`, because
     `issue_meta.required[]` is format-agnostic and these fields are weekly-only.
2. `.claude/skills/the-signal/references/spec/data-contracts.md` — **new**, 347 lines. The single
   reference for the machine records that cross phase boundaries: research-bundle additions (§3.2),
   the full `shows` enum with the definitions the checks depend on (§3.3, cross-referenced to
   `references/image-source-types.json` as its canonical home — WP-6 canonicalises, WP-1 documents),
   the chapter-plan additions (pointer to the schema file), all six state additions (§3.5) with
   producer/consumer per field, the `interest_depth` value set, and a § Seed provenance section
   recording what every seeded value is grounded in.
3. `state/signal-state.json` — +137/−0, purely additive. New keys: `research_cut_at`, `open_loops`,
   `cover_lead_ledger`, `sports_calendar`, `used_image_urls`, `interest_depth`.
   - `research_cut_at`: `2026-07-26T02:10:00Z` (the SPEC §3.5 literal; consistent with — and bounded
     above by — `state/quality-log.jsonl`'s #18 entry at `2026-07-26T02:51:16Z`). WP-9 overwrites at
     next publish.
   - `open_loops`: the two matured-and-lost loops from issue #17, `loop_2026-07-19_wc-final` and
     `loop_2026-07-19_open-final-round`, both `status: "dropped"` with a `resolution` recording that
     they were never reported in the weekly of record. Grounded: #17 carries the WC final as an
     upcoming fact and #18 has no result; The Open is absent from both issues (#17 has no golf at
     all). These give WP-5/WP-10 real matured loops to test §3.7 against.
   - `cover_lead_ledger`: 10 entries, #18 → #9, newest first, read off the rendered covers in
     `issues/` with numbers/dates from `archive-manifest.json`. `topic_family` values all verified
     present in `validate-chapter-plan.py`'s closed enumeration.
   - `sports_calendar`: 4 entries, every one `needs_verification: true`, no venues/fixtures/results —
     The Open Championship (2026-07-16→19), Commonwealth Games Glasgow 2026 (2026-07-23→08-02),
     Premier League 2026-27 opening (2026-08-21), Serie A 2026-27 opening (2026-08-23). The two
     football dates are grounded in state's own `recent_next_week_themes`.
   - `used_image_urls`: `{}` — WP-8 populates from issue #19 onward (nothing can be back-filled:
     `mirror-images.py` discarded the URLs).
   - `interest_depth`: `motorsport: results_only`, `football: full`, `golf: majors_only`.

**Verification (commands and results):**

```
$ python3 -c "import json; json.load(open('state/signal-state.json')); print('JSON OK')"
JSON OK
$ python3 -m json.tool state/signal-state.json > /dev/null && echo "json.tool OK"
json.tool OK

# key-set comparison against HEAD — no pre-existing key removed or altered
$ python3 - <<'PY'
old = json.loads(git show HEAD:state/signal-state.json); new = json.load(open(...))
PY
missing: []
changed: []
added: ['research_cut_at', 'open_loops', 'cover_lead_ledger', 'sports_calendar', 'used_image_urls', 'interest_depth']
old keys: 36 new keys: 42

$ git diff --numstat -- state/signal-state.json .claude/.../chapter-plan-schema.md
110	1	.claude/skills/the-signal/references/chapter-plan-schema.md
137	0	state/signal-state.json          # additive only

# all 7 fenced ```json blocks in chapter-plan-schema.md still parse
$ python3 -  # re.findall(r'```json\n(.*?)```') → json.loads each
json blocks: 7 → 0 OK 1 OK 2 OK 3 OK 4 OK 5 OK 6 OK

# every seeded topic_family is in the validator's closed enumeration
$ python3 -  # parse TOPIC_FAMILIES from validate-chapter-plan.py
missing from validator enum: set()
```

`git status --porcelain` shows only WP-1's three files as changed/added (plus `functions/daily/*`,
which is **WP-7 working in parallel** — not touched by WP-1).

**Left undone / deliberate scope calls:**

- ~~Issue #8 (2026-05-10) is **not** in `cover_lead_ledger` (so the ledger holds 10, not 12): its cover
  led on the Instructure/Canvas breach and the closed topic-family enumeration has **no family for a
  cybersecurity/data-breach story**. Mis-filing it would have corrupted the rut rule's input. The
  ledger therefore starts at #9. The enumeration gap is a real finding — see § Handoff notes.~~
  **RESOLVED by the follow-up below (SPEC §3.5 amendment, authorised 2026-07-26).**
- `sports_calendar` is deliberately short (4 entries). Per SPEC §3.12 nothing was seeded that could
  not be grounded, so the UEFA Champions League 2026-27 league phase, the remaining F1 rounds after
  the August break, and autumn athletics/cricket set-pieces are **listed as Phase-0 gaps inside
  `data-contracts.md`** instead of being invented. Note two grounded absences: the Ryder Cup is
  biennial (2027), and all four men's golf majors concluded before the research cut.
- No fixtures were written for WP-10; `state/quality-log.jsonl` and issue #18 were read only.

### Follow-up (2026-07-26, WP-1 resumed) — `cyber_privacy` + issue #8 backfill

Authorised by the SPEC §3.5 amendment "Topic-family enumeration gap (WP-1 finding, authorised
2026-07-26)", which accepts handoff note 3 and keeps the change with WP-1 because both files are
WP-1-owned. Rationale of record: leaving #8 unclassified silently narrowed the rut rule's input,
which is the exact mechanism the rule exists to catch — a ledger with a hole in it under-reports
repetition.

1. `.claude/skills/the-signal/references/chapter-plan-schema.md` (+3/−1) — added **`cyber_privacy`**
   to the closed Topic Family Enumeration, in the `news_geopolitics` cluster, with a scoped
   definition: *a breach, ransomware attack, state-backed intrusion, surveillance programme or
   privacy/data-protection ruling, where the story is the compromise or the regulation of personal
   data at scale* (Instructure/Canvas, 275M records, Issue #8 = the type case). Explicitly narrow:
   a product launch, app feature, AI tool or platform-policy change stays in `tablets_phones` /
   `consumer_ai` / `generative_ai_consumer` / `ai_search` / `streaming_tech` / `smart_home` even when
   it has a security or privacy angle, so the new family cannot swallow ordinary consumer-tech or AI
   stories. Placed in the news cluster because the reader meets these as world news.
2. `state/signal-state.json` (+7/−0) — backfilled issue **#8** (`2026-05-10`,
   `topic_family: "cyber_privacy"`, `one_line: "Finals week, no platform — 275 million student
   records claimed in the Canvas breach"`, `led_on: "news"`) as the oldest entry. `one_line` is read
   off that issue's World lead ("Finals week, no platform", "275 million records claimed"). The
   ledger now holds **11 entries, #18 → #8**, newest first.

**Re-run verification:**

```
$ python3 -c "import json; json.load(open('state/signal-state.json')); print('JSON OK')"
JSON OK
$ python3 -m json.tool state/signal-state.json > /dev/null && echo "json.tool OK"
json.tool OK

# key-set diff vs the PRE-WP-1 baseline (01e5fdf), not just HEAD
pre-WP-1 baseline keys: 36 now: 42
missing vs baseline: []
altered vs baseline: []
added vs baseline: ['research_cut_at', 'open_loops', 'cover_lead_ledger', 'sports_calendar', 'used_image_urls', 'interest_depth']
$ git diff 01e5fdf --numstat -- state/signal-state.json
144	0	state/signal-state.json          # still purely additive: 0 deletions

ledger len: 11 order: [18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8]
newest-first: OK
ledger families not in doc enum: set()
ledger families not in validator enum (WP-5 handoff): {'cyber_privacy'}
```

The last line is the one open consequence: `validate-chapter-plan.py` carries its own hardcoded
`TOPIC_FAMILIES` set (line ~153) and does not yet contain `cyber_privacy`. That file is WP-5's —
recorded as handoff note 7. Issue #18 untouched; `functions/daily/*`, `scripts/*` and
`assets/cached/*` in the working tree are WP-7/WP-8 in flight, not WP-1.

## WP-2 — Editorial prose spec

_No entries yet._

## WP-3 — Structure of record + stitcher + CSS

_No entries yet._

## WP-4 — Rendered-issue checks

_No entries yet._

## WP-5 — Upstream production aids

_No entries yet._

## WP-6 — Image taxonomy + specificity doctrine

_No entries yet._

## WP-7 — Daily inputs

_No entries yet._

## WP-8 — Asset provenance + licence safety

_No entries yet._

## WP-9 — Pipeline phase wiring

_No entries yet._

## WP-10 — Verification harness

_No entries yet._

---

## Handoff notes

Cross-WP requests land here — a WP that needs a change in a file it does not own records it, and the
orchestrator routes it.

### From WP-1

1. **→ WP-5 (and WP-8): the research bundle's URL key is `url_or_keyword`, not `url`.** SPEC §3.2's
   comment says the existing candidate fields are "url, verified, source_constraint, role". The keys
   actually in the bundle — the ones `validate-research-bundle.py` reads today (lines ~287–348) — are
   **`url_or_keyword`**, `verified`, `source_type`, `context`, and optional `direct_cdn`. `role` and
   `source_constraint` belong to the *chapter plan's* `images_needed[]`, not the bundle. The three new
   field names (`shows`, `capture_year`, `licence`) are unaffected; only the parenthetical is wrong.
   Recorded in `references/spec/data-contracts.md` § Research bundle. No file outside WP-1's ownership
   was changed.
2. **→ WP-5: `week_in_numbers.rows[].source_band` needs one value beyond band ids.** SPEC §3.1 shows
   only a band id (`"touchline"`), but `chapter-plan-schema.md` (v8.36) defines The Week in Numbers as
   the *personal* stat strip that renders from `state/signal-state.json`, so its personal rows have no
   originating band. WP-1 documented the value set as **the `chapter_id` of a chapter present in the
   plan, or the literal `"state"`**. `validate-chapter-plan.py` must accept `"state"`, otherwise the
   contract is unsatisfiable for the section as specified elsewhere.
3. **RESOLVED 2026-07-26 — → orchestrator / owner (no WP owns this): the closed topic-family
   enumeration has no family for cybersecurity / data-breach news.** Issue #8's cover lead (the
   Instructure/Canvas breach, 275M records) cannot be classified, so it was left out of
   `cover_lead_ledger`. Adding a family is a spec amendment (`chapter-plan-schema.md` § Topic Family
   Enumeration says so explicitly) and is outside the SPEC's scope, so WP-1 did not invent one. If it
   is wanted, candidate name: `cyber_privacy`.
   → **Authorised** in SPEC §3.5 ("Topic-family enumeration gap", 2026-07-26) and implemented by WP-1
   (resumed): `cyber_privacy` added to the enumeration, issue #8 backfilled, ledger now 11 entries
   #18 → #8. See § WP-1 → Follow-up. Leaves note 7 below as its only open consequence.
4. **→ WP-9: `interest_depth` has three keys, and an absent key is not `off`.** Only the sports the
   owner has weighted are seeded (motorsport, football, golf). The reader profile
   (`references/spec/global.md` § The Reader) lists only football and golf as sport interests, so the
   sports WP-7 is adding feeds for (cricket, cycling, athletics) have **no** `interest_depth` key.
   Treat an absent key as *unset* — cover on news value — never as `off`, or the invisible-sport
   problem (defect D) reappears in a new place. Rule stated in
   `references/spec/data-contracts.md` § `interest_depth`.
5. **→ WP-9: `research_cut_at` needs a real write.** The seeded value is the SPEC §3.5 literal
   (`2026-07-26T02:10:00Z`), which the repo can bound but not confirm (the #18 quality-log entry is
   `2026-07-26T02:51:16Z`, i.e. post-writing). The publish step must overwrite it with a measured
   instant, and Phase 0 must copy the *previous* value into `issue_meta.window.from`.
6. **→ WP-4/WP-5/WP-10: the two seeded `open_loops` are `dropped`, not `open`.** They are honest
   history (never reported; #18 is frozen), and a dropped loop does not mature — so they will **not**
   by themselves make the §3.7 gates fire. A fixture with `status: "open"` and a past
   `expected_resolution_date` is needed to demonstrate acceptance criteria #5 and #6.
7. **→ WP-5: add `cyber_privacy` to `TOPIC_FAMILIES` in `validate-chapter-plan.py` (~line 153).** The
   validator carries its own hardcoded copy of the closed enumeration. WP-1 added the family to
   `chapter-plan-schema.md` § Topic Family Enumeration (news_geopolitics cluster) under the SPEC §3.5
   amendment and used it for issue #8 in `cover_lead_ledger`, so until the validator's set is updated
   the two copies disagree: a plan (or a rut-rule cross-check) using `cyber_privacy` would hard-fail as
   "not in the closed enumeration". One-line change; `validate-chapter-plan.py` is WP-5's file, so
   WP-1 did not touch it. Verified divergence:
   `ledger families not in validator enum: {'cyber_privacy'}`.
