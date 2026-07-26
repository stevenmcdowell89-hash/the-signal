# WP-1 — Data contracts (foundation) (SPEC §3.1, §3.2, §3.3, §3.5, §3.11, §3.12)

**Date:** 2026-07-26
**Branch:** `claude/signal-antikythera-article-lzzlup`
**Status:** DONE (three rounds: initial build, then two authorised follow-ups)
**Files touched (exclusive, nothing else):**
- `.claude/skills/the-signal/references/chapter-plan-schema.md`
- `.claude/skills/the-signal/references/spec/data-contracts.md` *(new)*
- `state/signal-state.json`

Rounds 1–2 were also recorded in `docs/editorial-coverage-rebuild-PROGRESS.md` before the coordinator
took that file over; this file is now WP-1's single evidence record.

---

## Round 1 — the contracts (summary)

**`chapter-plan-schema.md`** (+110/−1) — added, per SPEC §3.1, all enforced by
`validate-chapter-plan.py` (WP-5): `issue_meta.research_cut_at`, `issue_meta.window{from,to}`,
`issue_meta.cover_leads_on` (`news`|`long_read`), `issue_meta.lead_rationale` (≥120 chars),
`issue_meta.lead_override_reason` (≥80 chars, only when the rut rule §3.6 trips); chapter-level
`vintage` (`news`|`evergreen`), `material_span` (`YYYY–YYYY`, en-dash) and `latest_development`
(`YYYY-MM`) on `long_read`, the latter two required iff evergreen; chapter-level `rows[]` on
`week_in_numbers` requiring `key` + `source_band`. Plus a worked example and a note making
§ Topic Family Enumeration the single vocabulary for `cover_lead_ledger[].topic_family`. Conditional
requirements are expressed in field `description`s (the file's existing convention) rather than
JSON-Schema `required`, because `issue_meta.required[]` is format-agnostic and these are weekly-only.

**`references/spec/data-contracts.md`** (new) — the cross-phase machine records: bundle additions
`image_candidates[].shows` / `.capture_year` / `.licence{holder,code,url,allows_derivatives}` and
`facts[].resolves_loop` (§3.2); the full 11-value `shows` enum with check-relevant definitions (§3.3),
cross-referenced to `references/image-source-types.json` as its canonical home (WP-6 canonicalises,
WP-1 documents); all state additions with producer/consumer per field; the `interest_depth` value set;
and a § Seed provenance section grounding every seeded value.

**`state/signal-state.json`** (additive only) — new keys `research_cut_at`, `open_loops`,
`cover_lead_ledger`, `sports_calendar`, `used_image_urls`, `interest_depth`. Highlights:
`open_loops` seeds the two matured-and-lost loops from issue #17 (`loop_2026-07-19_wc-final`,
`loop_2026-07-19_open-final-round`), both `status: "dropped"` with a `resolution` recording that they
were never reported in the weekly of record; `sports_calendar` seeds 4 entries, every one
`needs_verification: true`, no venues/fixtures/results; `used_image_urls` starts `{}` (nothing can be
back-filled — `mirror-images.py` discarded the URLs); `interest_depth` = motorsport `results_only`,
football `full`, golf `majors_only`.

Six SPEC/reality mismatches were reported rather than improvised. The two that other WPs must act on:
the bundle's URL key is **`url_or_keyword`**, not `url` (§3.2's parenthetical is wrong;
`source_constraint`/`role` are *plan* fields), and `week_in_numbers.rows[].source_band` needs the
literal `"state"` alongside band ids or the section as defined in `chapter-plan-schema.md` (v8.36)
cannot be expressed.

---

## Round 2 — `cyber_privacy` + issue #8 backfill (authorised, SPEC §3.5 amendment)

Round 1 left issue #8 (2026-05-10, the Instructure/Canvas breach cover lead) out of
`cover_lead_ledger` because the closed topic-family enumeration had no family for it. The coordinator
authorised the gap-fill: leaving #8 unclassified silently narrowed the rut rule's input, which is the
exact mechanism the rule exists to catch — a ledger with a hole in it under-reports repetition.

1. `chapter-plan-schema.md` (+3/−1) — **`cyber_privacy`** added to the closed Topic Family Enumeration,
   in the `news_geopolitics` cluster: *a breach, ransomware attack, state-backed intrusion,
   surveillance programme or privacy/data-protection ruling, where the story is the compromise or the
   regulation of personal data at scale* (Instructure/Canvas, 275M records = the type case).
   Deliberately narrow — a product launch, app feature, AI tool or platform-policy change stays in
   `tablets_phones` / `consumer_ai` / `generative_ai_consumer` / `ai_search` / `streaming_tech` /
   `smart_home` even when it has a security or privacy angle.
2. `state/signal-state.json` (+7/−0) — issue **#8** backfilled as the oldest entry
   (`topic_family: "cyber_privacy"`, `one_line: "Finals week, no platform — 275 million student
   records claimed in the Canvas breach"`, `led_on: "news"`), read off that issue's World lead.
   **Ledger now 11 entries, #18 → #8**, newest first.

Open consequence, for WP-5: `validate-chapter-plan.py` carries its own hardcoded `TOPIC_FAMILIES` set
(~line 153) and does **not** contain `cyber_privacy`, so the two copies of the enumeration disagree
until WP-5 adds it. Verified: `ledger families not in validator enum: {'cyber_privacy'}`.

---

## Round 3 — sport tokens (authorised, SPEC §3.11 amendment)

WP-7 flagged that `sports_calendar[].sport` used `multi_sport` while the daily's catch-all domain is
`sport`. That inconsistency hid a real loophole in the §3.11 `results_ledger_multi_sport` invariant:
if a games' rows could carry `data-sport="multi_sport"`, ten sports collapse into one token, and a
ledger of `[motorsport, multi_sport]` passes "≥2 distinct `data-sport` values" while delivering none of
the breadth the invariant exists to force — i.e. the F1-saturation defect (41 term-hits vs 0) passing
its own check. Canonicalisation was assigned to WP-1.

**Changed:** `references/spec/data-contracts.md` only — a new § Sport tokens, plus three
cross-references (the contract table at the top, § `sports_calendar[]`, § `interest_depth`) and a line
in § Seed provenance.

### 3.1 Three namespaces, related not merged

| Namespace | Question | Where |
|---|---|---|
| **Sport token** (canonical) | *Which sport is this result?* | `data-sport`; `sports_calendar[].sport`; `interest_depth` keys |
| **Daily domain** | *Which edition/section does this item route to?* | `functions/daily/profile.js` `DOMAINS`/`DOMAIN_META` (WP-7) |
| **Topic family** | *Which editorial beat is this piece on?* | `chapter-plan-schema.md` § Topic Family Enumeration |

Topic families are competition-level (`premier_league`, `golf_majors`, `f1`) because they classify a
*piece*; sport tokens are sport-level (`football`, `golf`, `motorsport`) because they classify a
*result*. The names are not forced to match across namespaces — they answer different questions.

### 3.2 The closed sport-token list (22 tokens)

`football` · `golf` · `cricket` · `cycling` · `athletics` · `motorsport` · `rugby` · `tennis` ·
`boxing` · `mma` · `snooker` · `darts` · `gaelic_games` · `swimming` · `diving` · `gymnastics` ·
`netball` · `hockey` · `ice_hockey` · `horse_racing` · `basketball` · `american_football`

Lowercase `snake_case`, singular, the **sport** and never the competition (`football` not
`premier_league`; `motorsport` not `f1`).

Derivation, so the list is auditable rather than invented:
- `football`, `golf` — the reader profile's stated sports (`references/spec/global.md` § The Reader).
- `cricket`, `cycling`, `athletics`, `motorsport` — WP-7's new daily domains (`profile.js`).
- the remaining 16 — exactly the sports named in the keyword set of WP-7's general `sport` catch-all
  (rugby, tennis, boxing, UFC/MMA, snooker, darts, GAA, swimming/diving, gymnastics, netball, hockey,
  ice hockey, horse racing, NFL, NBA), so everything the daily can surface has somewhere to land in a
  results ledger.
- `golf`, `football`, `multi_sport` — the values already in WP-1's `sports_calendar` seed.

**Extension:** closed with an extension path. A new token is appended **here, by WP-1**, with a
one-line reason (same discipline as a new `topic_family`), and no consumer needs a code change.
Consumers therefore treat the list as advisory-but-canonical: WP-4 **MUST hard-fail** `multi_sport`,
and **SHOULD warn, not fail**, on an unlisted token — the Commonwealth Games long tail
(weightlifting, judo, squash) must not block a ship; the warning is the prompt to extend.

### 3.3 The `multi_sport` rule, as written

- **Legal in exactly one place:** `sports_calendar[].sport`, because it classifies an **event** (a
  games), where "which sport" has no single answer and the planner needs the whole games on one row.
- **Forbidden as `data-sport` in rendered HTML — WP-4 must reject it.** A *result* always belongs to a
  specific sport; rows derived from a multi-sport games carry `athletics`, `swimming`, `boxing`, …
  One-line reason recorded in the doc: it would collapse ten sports into one token, so
  `[motorsport, multi_sport]` would satisfy `results_ledger_multi_sport` while delivering no breadth.
- **Also forbidden as an `interest_depth` key** — a games is a calendar event, not a standing coverage
  depth; depth is expressed per constituent sport or left unset.

### 3.4 Daily domain → sport token mapping

| Daily domain (`DOMAIN_META` label) | Sport token(s) |
|---|---|
| `football` ("Football") | `football` |
| `golf` ("Golf") | `golf` |
| `cricket` ("Cricket") | `cricket` |
| `cycling` ("Cycling") | `cycling` |
| `athletics` ("Athletics") | `athletics` |
| `motorsport` ("Motorsport") | `motorsport` |
| `sport` ("More Sport" — catch-all) | any of `rugby`, `tennis`, `boxing`, `mma`, `snooker`, `darts`, `gaelic_games`, `swimming`, `diving`, `gymnastics`, `netball`, `hockey`, `ice_hockey`, `horse_racing`, `basketball`, `american_football` — resolved per item, never carried through as a token |

Six domains are 1:1 with their tokens. The `sport` catch-all is **1:many** and has **no token of its
own**: it is a routing bucket for every sport without a domain, kept keyword-disjoint from the specific
domains by WP-7. Multi-sport meets route to `sport` (the Olympics/Commonwealth keywords live there) and
then resolve, per result, to the specific sport — the `multi_sport` prohibition seen from the daily's
side. The mapping is a routing convenience, not an identity: neither side gets renamed to match.

### 3.5 Did the `sports_calendar` seed need changing?

**No.** Its three `sport` values are `golf`, `football` (both listed tokens) and `multi_sport` on the
Commonwealth Games row — now explicitly the one legal use. The row is left as seeded; its *results*
will be tagged per sport. `state/signal-state.json` was **not** modified in round 3.

---

## Verification (all rounds, final re-run)

```
$ python3 -c "import json; json.load(open('state/signal-state.json')); print('JSON OK')"
JSON OK
$ python3 -m json.tool state/signal-state.json > /dev/null && echo "json.tool OK"
json.tool OK

# additive-only check against the pre-WP-1 baseline 01e5fdf (not merely HEAD)
pre-WP-1 baseline keys: 36 now: 42
missing vs baseline: []
altered vs baseline: []
added vs baseline: ['research_cut_at', 'open_loops', 'cover_lead_ledger', 'sports_calendar', 'used_image_urls', 'interest_depth']
$ git diff 01e5fdf --numstat -- state/signal-state.json
144	0	state/signal-state.json          # 0 deletions — purely additive

# ledger integrity
ledger len: 11 order: [18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8]
newest-first: OK
ledger families not in doc enum: set()
ledger families not in validator enum (WP-5 handoff): {'cyber_privacy'}

# every fenced ```json block in chapter-plan-schema.md still parses
json blocks: 7 → all OK

# sport tokens: parse the list out of data-contracts.md and check every state value against it
token count: 22   (no duplicates)
calendar sport values: ['golf', 'multi_sport', 'football', 'football']
calendar values not token and not multi_sport: set()
interest_depth keys: ['motorsport', 'football', 'golf']
interest_depth keys not tokens: set()
```

Issue #18 and `state/quality-log.jsonl` were read only, never modified.

---

## Open handoffs from WP-1

| # | To | Item |
|---|---|---|
| 1 | WP-5, WP-8 | The bundle's URL key is **`url_or_keyword`**, not `url` (SPEC §3.2's parenthetical is wrong; `source_constraint`/`role` are chapter-plan fields). |
| 2 | WP-5 | `week_in_numbers.rows[].source_band` must accept the literal `"state"` alongside band ids, or the section as defined in `chapter-plan-schema.md` (v8.36) is unsatisfiable. |
| 3 | — | **RESOLVED** in round 2: `cyber_privacy` added, #8 backfilled. |
| 4 | WP-9 | `interest_depth` has three keys; an absent key means **unset**, never `off` (cricket/cycling/athletics have no key). |
| 5 | WP-9 | `research_cut_at` is seeded from the SPEC literal; publish must overwrite it with a measured instant and Phase 0 must copy the previous value into `issue_meta.window.from`. |
| 6 | WP-4, WP-5, WP-10 | The two seeded `open_loops` are `dropped`, so they do not mature — acceptance criteria #5/#6 need a fixture with `status: "open"` and a past `expected_resolution_date`. |
| 7 | WP-5 | Add `cyber_privacy` to `TOPIC_FAMILIES` in `validate-chapter-plan.py` (~line 153). |
| 8 | WP-4 | Hard-fail `data-sport="multi_sport"`; warn (do not fail) on a `data-sport` outside the 22-token list in `data-contracts.md` § Sport tokens. |
| 9 | WP-3 | Writers/stitcher must emit a specific sport token on every `.mx-ledger__row`, including rows derived from a multi-sport games. |
