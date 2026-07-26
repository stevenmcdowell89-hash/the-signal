# WP-2 — Editorial prose spec

**Owner:** WP-2 of `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md`.
**Files touched (both exclusively owned by WP-2, nothing else):**

- `.claude/skills/the-signal/references/editorial-spec.md` — 9 new/rewritten blocks, `+46 −5` lines
  against the pre-WP-2 state (the orchestrator's WIP snapshots `9d354c9` / `2f76818` captured them
  mid-flight).
- `.claude/skills/the-signal/references/sections.md` — 10 new/rewritten blocks.

**Version marker:** `(v8.44, WP-2)`, following the house convention (`(v8.37, W-3)`,
`WP-8/8.1 (v8.43)` in `chapter-plan-schema.md`). 19 marked blocks across the two files.

`docs/editorial-coverage-rebuild-PROGRESS.md` was **not** edited (build rule 5).
Issue #18 was **not** modified (build rule 3) — it is cited as evidence throughout.

---

## What changed, section by section

### A — evergreen anchors must read as features

**`editorial-spec.md` § The Long Read (v8.37, W-3)** — new block *"Vintage — news or evergreen — is a
first-class editorial decision"*. Makes `vintage` a required plan decision taken **before** the
standfirst, and states what each value means and renders:

- `vintage: "news"` — subject moved inside the coverage window; `data-vintage="news"`, no
  `.lr-vintage`, `.byline` keeps `· DD MON YYYY`.
- `vintage: "evergreen"` — a **standing story**; `material_span` + `latest_development` required;
  renders `data-vintage="evergreen"` + the mono `.lr-vintage` standing-story dateline
  (`NOT THIS WEEK · A STANDING STORY · 1901–2021 · LATEST DEVELOPMENT MAR 2021`) and a **date-free
  `.byline`**. The `MON YYYY` expansion of `latest_development: "2021-03"` is stated because the
  stitcher does it (`stitch_weekly.py::month_year`).
- **The Letter must introduce it as a feature**, in a sentence of its own, on a paragraph carrying
  `data-lr-framing="feature"`. Explicit prohibition on folding it into the week's-news paragraph.
- **An evergreen anchor's datums do not go in The Week in Numbers** — no `week_in_numbers.rows[]`
  entry may take `source_band` = the `long_read` chapter when `vintage == "evergreen"`.
- *Why the field exists* — the #18 anchor failure, with the three verified artefacts quoted (byline
  `BY THE EDITOR · THE LONG READ · 26 JUL 2026`; The Letter's "*a corroded lump of bronze pulled from
  a Greek shipwreck turned out … to have been a computer*" closing the news paragraph; `Antikythera
  Fragments · 82` filed between `Leaders in a Decade · 7` and `Iran's SCO Deals`). Records explicitly
  that the pre-existing prose advice was insufficient because the stitcher had no field to read.

A writer reading **only** the editorial spec gets all of this without opening the SPEC; the SPEC is
cited for provenance, never as the place the rule lives.

**`editorial-spec.md` § The Week in Numbers** and **`sections.md` § The Week in Numbers** — `source_band`
documented (`chapter_id` of a chapter in this plan, or the literal `"state"`), with the evergreen hard
exclusion restated where the band's own writer will read it.

**`sections.md` § The Letter** — the `data-lr-framing="feature"` obligation with the #18 sentence as the
worked counter-example, because the Letter's writer reads this brief and not § The Long Read.

### C — cover demotion

**`sections.md` § Cover** — two new blocks:

1. *"What the cover leads on is a declared decision"* — `issue_meta.cover_leads_on` (`"news"` |
   `"long_read"`) + `issue_meta.lead_rationale` (≥120 chars, names what was considered **and
   rejected**). States that **`cover_leads_on: "long_read"` is a normal week, not an exception** — a
   strong feature taking the cover on a thin news week is what a Sunday magazine does — and notes the
   stitcher leads the tuner station list with the Long Read on that value. Documents
   `cover_lead_ledger[]` (12 covers, `{issue, date, topic_family, one_line, led_on}`) and why it
   replaced `last_cover_lead`: one week of history cannot show a rut, and UK politics led 6 of 9.
   The rut rule is stated with its exact trigger and the `lead_override_reason` ≥80-char escape.
   **Explicitly not a suppression gate**, with the load-bearing distinction spelled out: the retired
   gate removed a subject from *eligibility*; the rut rule requires a *written justification* and
   removes nothing. Closes with "if a rut recurs, strengthen the demotion — do not add a check."
2. **Demotion principle** — written by analogy with the Touchline's at the same heading level.
   Demoted leads fall to **THE CLOSE**: a Threads recap **plus** a two-line policy ledger
   (`demoted_lead_ledger` → `.mx-ledger[data-mx-event="ledger"][data-role="demoted-lead"]`, two rows
   of what moved / what did not / what it waits on, in the quieter voice). Carries the owner's
   judgement verbatim and argues the alternatives down: kept near the front the cover reads hedged;
   cut outright is the retired gate's failure mode; falling to the close covers it at the weight it
   now earns.

**`editorial-spec.md` § What to Lead With** — the principle-level counterpart: `cover_leads_on`,
`lead_rationale`, the ledger, the rut rule, the not-a-gate paragraph, and a pointer to
`sections.md` for the shape. Split deliberately — principles in the spec, per-band rules in the
section reference, no duplication of the markup.

**`sections.md` § Topic Families & Recent Leads** — a blockquote under the *retired* sliding-window cap
saying the rut rule is **not** its revival, and that `lead_history` (a story-thread record) is not
interchangeable with `cover_lead_ledger` (which follows the rendered covers). This prevents a reader
of the retirement notice concluding the new rule contradicts it.

**`sections.md` § The Threads** — a bullet pointing the demoted-lead ledger at this band, since the
Threads writer needs it and the doctrine lives under § Cover.

### D — sport

**`sections.md` § The Touchline** — the largest change. Four new blocks:

1. **"Two jobs, not one"** — states the structural cause (a single job description in ≤600 words, so
   the narrative job wins and coverage collapses to whatever supplies a table) and raises prose to
   **500–800 words**, with *"this raises prose; it does not cut furniture"*.
2. **Job 1 — the results ledger.** Comprehensive, calendar-driven, results-of-record: every tracked
   event that **concluded** since the previous `research_cut_at` (`issue_meta.window.from`), one row
   each; forward fixtures are the separate `fixtures_lookahead` in On the Radar and must not carry
   `data-role="results-ledger"`. Rows carry `data-sport`; **≥2 distinct sports whenever ≥2 concluded**
   (`results_ledger_multi_sport`). *"A ledger row costs about twelve words … there is no editorial
   economy in which 'no room' is the honest reason the ledger carried one competition."* Sourced from
   `sports_calendar[]`, not feed volume. Events concluding after the cut become **open loops**, not
   gaps. Standings are polymorphic (`data-table-kind` ∈ `league`·`medal`·`gc`·`leaderboard`·
   `championship`) — a card with one shape could only show league sports. `.mx-dial` is **optional**
   and retargetable, "not a reason for motorsport to lead".
   Also encodes the SPEC §3.11 sport-token amendment: `data-sport` is **sport-level, never
   competition-level, and never `multi_sport`** (legal only in `sports_calendar[].sport`, barred as an
   `interest_depth` key).
3. **Job 2 — one lead story.** One, chosen by the existing hierarchy, **allowed to yield**.
4. **Hierarchy audit (finding: the hierarchy is right, it was bypassed).** Recorded as a blockquote
   *"do not rewrite it"*: Round 11 of 24 is **priority 6** (not a title decider, so not priority 2);
   a UK-hosted multi-sport games is **priority 2**; #18 led on the former, gave one race five
   furniture bands plus a Letter mention, never mentioned the latter, carried **zero** golf in the
   window containing The Open's final round, and cricket is **zero across all 16 issues**. Conclusion:
   strengthen demotion and the scan, do not re-rank.
5. **Demotion, the other direction** — the missing half. Priority 6 yields to 1–3 without negotiation;
   *"it produced a fresh table" is not a priority*; **one competition does not take multiple furniture
   objects**; depth weighted by `interest_depth` with motorsport `results_only` explained in the
   owner's words (*"nice to know big results, I don't need a minute by minute"*) and the fact that
   motorsport is **not in the reader profile** (`spec/global.md` § The Reader names football and golf);
   **an absent `interest_depth` key means unset, never `off`** — cricket/cycling/athletics/tennis/rugby
   are covered on news value.
6. **The scan list at the old `sections.md:134` is replaced** by a calendar-driven three-question scan
   answered from `sports_calendar` (what concluded in-window / what is running / what opens next
   week), plus the domestic beat and structural stories. The replacement states *why*: of the five
   entries on the old list only one returns a fresh table-shaped result every week of its season, so a
   rule meant to broaden coverage narrowed it; and the list omitted cycling, cricket, athletics,
   swimming and multi-sport games entirely.

Also updated in that brief: the markup bullet (results ledger + polymorphic scorecard alongside the
retained `.scores` grid), the golf bullet (now names `majors_only` and the #18 zero-coverage fact), the
Companion list (F1-only → golf/cricket/cycling/athletics/rugby/tennis/motorsport/governance), and the
considered-piece backbone (the ledger is **not** the considered piece and runs regardless).

**`editorial-spec.md` § Search Checklist → Group 3** rewritten from *"Football & Sport"* (a competition
list) to *"Sport — calendar-first"*, the same three questions, with the `needs_verification` and
absent-key rules. Required: leaving the old Group 3 in place would have directly contradicted the new
`sections.md` scan.

**`editorial-spec.md` § Section Rules → The Touchline** bullet rewritten to carry the ledger/lead split,
the 500–800 target, `data-sport`/`≥2 sports`, `data-table-kind`, and the `interest_depth` absent-key
rule.

### D (continued) — the Sunday hole

**`editorial-spec.md` § Content Standards**, immediately beside the run-date / fact-provenance rules:

- **"Sunday timing"** amended — Sunday's own results are usually *not* knowable at research time.
- **"7-day freshness rule" → "Freshness rule"** — news must be inside the **coverage window**, and the
  unqualified *"evergreen features are fine when clearly framed as features"* is replaced: framing is
  now an artifact (`vintage`), not an aspiration.
- **New: the coverage window is knowability-based** — `(previous research_cut_at, now]`, opening at
  state `research_cut_at` (→ `issue_meta.window.from`) and closing at `issue_meta.research_cut_at`
  (= `window.to`). *"'Sunday is inside the week we cover' is the sentence that lost the World Cup
  final: the day was inside the range, the result was not yet in the world."*
- **New: `upcoming` facts become open loops the next issue is obliged to close** — the `open_loops[]`
  record and all its fields, the maturity rule, both enforcement layers
  (`facts[].resolves_loop` at the bundle, `data-resolves-loop` in the HTML), and `dropped` as the
  honest terminal state.
- **New sub-bullet: why the rule is counter-intuitive.** States plainly that the anti-fabrication
  machinery is *working* and must not be relaxed — but that refusal on its own is a memory hole: the
  result is unreportable this week (unknowable) and stale next week (outside the calendar week), so it
  is never reported. Cites #17's explicit upcoming fact and #18's silence. *"A weekly of record does
  not get to lose a World Cup final because it kicked off four hours after the researcher stopped
  reading."*
- **New sub-bullet: how to write the pending mention so it survives** — name the event, date and
  participants; vague anticipation cannot be resolved and should not be written.

### E — images

**`editorial-spec.md` § Standard Weekly → the weekly visual floor** — new block **"Which image — rank by
information gained, not by source pedigree (B9)"**, added as B9 to the existing B1–B8 series:

- `shows` is declared per candidate and is **orthogonal to `source_type`** — a press kit can supply
  `gameplay` *or* `key_art`, so the domain is not the choice. Full 11-value enum listed.
- The ranked hierarchy, verbatim from SPEC §3.13: actual thing happening → diagram/map/chart →
  artefact/document → in_engine → **key_art / product_shot / portrait, last resort and never a lead**.
- The owner's framing quoted (*"every time we talk about a game we just get cover art, that's the
  boring and safe shape — gameplay images etc are much more interesting"*), plus the Antikythera cost
  (the 2021 Freeth *Scientific Reports* figures were CC BY on an already-whitelisted domain; Commons
  supplied a 2007 perspex model instead) and the Steam `screenshots[]` / `shared.fastly.steamstatic.com`
  point that the gap was the reflex, not the source list.
- The mechanical floors `validate-issue.py` holds, stated as living **inside the existing gates** (the
  ledger stays at three).
- **"The bar is quality and credit, not source pedigree"** carried across to the weekly, naming the
  Countdown (`:721`) and Field Guide (`:887`) precedent explicitly as the rule the weekly never
  inherited, with the WP-6 source additions (`open_access_journal`, Getty Open Content, Rijksmuseum,
  Smithsonian, Europeana, Gallica/BnF, NYPL, Wellcome, British Library on Flickr, David Rumsey).
- **The Wikimedia cap is retired** — `wikimedia_max_pct` / `wikimedia_max_count` named as gone, with
  the reason (a ceiling reads as a target) and the replacement (`min_distinct_shapes: 3`, a floor on
  shapes not a cap on a domain).
- **Every figure carries its machine record** — `data-shows` / `data-capture-year` / `data-licence` /
  `data-allows-derivatives`, the caption-vintage rule (`.plate-cap .txt`, excluding `.credit`) with
  #18's FIG 03 as the failing example, and the ND / `allows_derivatives: false` no-crop rule.

**`editorial-spec.md` § Content Standards → "Images mandatory"** rewritten: ranked by information
gained, key art/product shots/posed portraits last resort and never a lead, "Wikimedia Commons is one
source among many and no longer the default", the bar is quality and credit.

---

## Identifier cross-check

Every identifier used was checked **by name** against SPEC §3 and
`references/spec/data-contracts.md`. Command:

```
for id in …; do grep -c -- "$id" SPEC; grep -c -- "$id" data-contracts.md; grep -ch -- "$id" <my two files>; done
```

**Plan fields (SPEC §3.1):** `issue_meta.research_cut_at` ✓ · `issue_meta.window.from` / `.to` ✓ ·
`issue_meta.cover_leads_on` (`"news"` | `"long_read"`) ✓ · `issue_meta.lead_rationale` ✓ ·
`issue_meta.lead_override_reason` ✓ · `long_read.vintage` (`"news"` | `"evergreen"`) ✓ ·
`material_span` ✓ · `latest_development` ✓ · `week_in_numbers.rows[].key` ✓ ·
`week_in_numbers.rows[].source_band` ✓ (value set per WP-1's correction: a `chapter_id` in this plan,
or the literal `"state"` — used exactly that way).

**Bundle fields (SPEC §3.2):** `facts[].status` (`"happened"` | `"upcoming"`) ✓ ·
`facts[].resolves_loop` ✓ · `image_candidates[].shows` ✓ · `.capture_year` ✓ ·
`.licence.{holder, code, url, allows_derivatives}` ✓. *(I never name `url` for a bundle candidate —
WP-1's handoff note 1 records the real key is `url_or_keyword`; my prose does not reference either, so
there is nothing to get wrong.)*

**State keys (SPEC §3.5):** `research_cut_at` ✓ · `open_loops[]` with `id`, `claim`,
`expected_resolution_date`, `band`, `issue_opened`, `status`, `resolution` ✓ · `cover_lead_ledger[]`
with `issue`, `date`, `topic_family`, `one_line`, `led_on` ✓ · `sports_calendar[]` with `event`,
`sport`, `start`, `end`, `importance`, `reader_relevant`, `needs_verification` ✓ · `used_image_urls` ✓ ·
`interest_depth` values `full` · `majors_only` · `results_only` · `off` ✓, **and the absent-key =
unset rule** stated in three places (§ Group 3, § Section Rules → Touchline, § The Touchline).

**Rendered attributes (SPEC §3.4):** `data-vintage` ✓ · `.lr-vintage` ✓ · `.byline` ✓ ·
`data-lr-framing="feature"` ✓ · `data-shows` ✓ · `data-capture-year` ✓ · `data-licence` ✓ ·
`data-allows-derivatives` ✓ · `.plate-img` / `.plate-img.lead` ✓ · `.plate-cap .txt` / `.credit` ✓ ·
`.mx-ledger` ✓ · `data-mx-event="ledger"` ✓ · `data-role="results-ledger"` ✓ · `.mx-ledger__row` ✓ ·
`data-sport` ✓ · `.mx-scorecard` ✓ · `data-table-kind` ∈ `league`·`medal`·`gc`·`leaderboard`·
`championship` ✓ · `data-resolves-loop` ✓ · `data-role="demoted-lead"` ✓ · `data-role="long-read"` ✓.

**`shows` enum (SPEC §3.3), all eleven:** `event_photo` · `gameplay` · `in_engine` · `key_art` ·
`product_shot` · `portrait` · `diagram` · `map` · `chart` · `artefact` · `document` ✓.

**Skeleton / WP-6 identifiers:** `touchline.target_words` `{min: 500, max: 800}` ✓ (verified against
the live `weekly.json`) · `standings_card` ✓ · `dial_signature` ✓ · `quote_objects` ✓ · `ticket` ✓ ·
`results_ledger_multi_sport` ✓ · `min_distinct_shapes: 3` ✓ · `open_access_journal` ✓ ·
`wikimedia_max_pct` / `wikimedia_max_count` named only as **retired** ✓.

**Two deliberate deviations from the SPEC's literal text, both toward the live implementation:**

1. SPEC §3.11 names the furniture component `furniture_layer.components.fixtures_ledger` and says it
   *becomes* the results ledger. WP-3 has **renamed the key to `results_ledger`** in the live
   `weekly.json` (its note: *"Renamed from `fixtures_ledger` by SPEC §3.11; no script keyed on the old
   name"*), and split forward fixtures into a new `fixtures_lookahead` for On the Radar. My prose uses
   `results_ledger` and `fixtures_lookahead` and records the rename inline, because the doctrine must
   name what the skeleton actually contains. Not an improvised contract — the rename is WP-3's, inside
   its own file.
2. SPEC §3.4's `.lr-vintage` example shows `LATEST DEVELOPMENT MAR 2021` while `latest_development` is
   `YYYY-MM`. I state the placeholder as `<MON YYYY>` and note the stitcher expands it, matching
   `stitch_weekly.py::month_year()`. No field name changed.

**One WP-3 emission I deliberately did *not* put in prose:** `stitch_weekly.py` emits
`data-cover-leads-on` on the cover, which is **not in SPEC §3.4**. Rather than invent doctrine around
an un-specced attribute I documented only the *behaviour* (on `cover_leads_on: "long_read"` the station
list leads with the Long Read). See handoff note 1.

---

## Contradiction grep

| Old rule | Command | Result |
|---|---|---|
| The `sections.md:134` scan list | `grep -n "Olympics buildup\|golf (PGA / DP World" sections.md editorial-spec.md` | **1 hit, and it is the replacement's own citation** of the retired list ("the previous rule told the researcher to scan 'golf, F1, Olympics buildup, rugby, tennis'"). The operative rule is gone; it survives only as quoted evidence of why. |
| The unqualified *"evergreen features are fine when clearly framed as features"* | `grep -n "clearly framed as features" *.md` | **2 hits, both explicitly superseding it** — the Freshness rule ("'clearly framed as features' is no longer left to the writer's good intentions") and the § Long Read *why the field exists* note. No unqualified instance remains. |
| The Wikimedia cap | `grep -in "wikimedia_max\|Wikimedia" editorial-spec.md sections.md` | **8 hits, none of them the cap.** One is the retirement notice naming `wikimedia_max_pct` / `wikimedia_max_count` as gone. **Deliberately retained (out of WP-2's scope, and still correct):** `:708` / `:736` / `:751` — Countdown/Field Guide *source lists* where Commons is one option among a wide net (the permissive rule I am carrying across, not the cap); `:1329`–`:1336` — Image-caption integrity, the Commons-filename-must-match-caption rule and the credit format; `:1346` — the verification chain's Commons `/thumb/` fabrication trap. None sets a ceiling on Commons usage. |
| The retired suppression gates | `grep -io "check-[a-z-]*\.py" editorial-spec.md sections.md \| sort -u` | Only `check-topic-lock.py` and `check-theme-clustering.py`, and every mention is a **retirement** statement. I added two *new* statements that they stay retired (§ What to Lead With; § Cover) and one blockquote that the rut rule is not a revival of the sliding-window cap. No gate reintroduced. |
| Fixtures vs results in the ledger | — | `sections.md` now states forward fixtures are `fixtures_lookahead` in On the Radar and must **not** carry `data-role="results-ledger"`, matching WP-3's component note. No band claims both jobs. |

`git status --short` at hand-off shows **only** `sections.md` uncommitted from WP-2 — my
`editorial-spec.md` edits were swept into the orchestrator's WIP snapshots `9d354c9` / `2f76818`
while in flight. Other paths in `git status` belong to WP-3 / WP-6 / WP-11 running concurrently.
**No file outside WP-2's two was touched.**

---

## What's left

Nothing in WP-2's brief is unfinished. Three things are deliberately *not* here:

- **No mechanical check was added.** WP-2 owns doctrine only; every enforcement sentence attributes the
  check to WP-4/WP-5 and states it lands inside the existing three gates.
- **The priority hierarchy was not rewritten.** The audit found it correct and bypassed; per the brief
  the fix is stronger demotion + a calendar-driven scan, recorded as a "do not rewrite" blockquote so
  a future reader does not re-open it.
- **`sections.md` § The World This Week** still carries pre-v8.37 Ongoing-Story-Tracker machinery for a
  band that is no longer a fixed weekly round. Pre-existing, unrelated to the five defects, and
  rewriting it would have been scope creep.

---

## Handoff notes

1. **→ orchestrator / WP-3: `data-cover-leads-on` is emitted but not in SPEC §3.4.**
   `stitch_weekly.py` stamps `data-cover-leads-on` on the cover (its own docstring says so). It is a
   sensible attribute and probably wants canonicalising in §3.4 alongside `data-vintage`, but WP-2 did
   not write doctrine around an identifier the interface does not contain. Either add it to §3.4 or
   drop it; right now `editorial-spec.md` and `sections.md` describe only the behaviour.

2. **→ orchestrator: SPEC §3.11 still names `fixtures_ledger`.** WP-3 renamed the live key to
   `results_ledger` and added `fixtures_lookahead`, both correct and both better than the SPEC's
   wording. §3.11's bullet is now stale text. WP-2's prose follows the live skeleton. Worth a one-line
   SPEC correction so WP-4/WP-10 do not key off the old name.

3. **→ owner / orchestrator (no WP owns this): The Week in Numbers has drifted from "personal" to
   "news datums", and `source_band` documents the drift without resolving it.** `editorial-spec.md`
   § The Week in Numbers (v8.36) and `sections.md` define the band as *the reader's* week — Garmin
   miles, FPL rank, the Juve result, one money number. #18 shipped it as five **news** datums (Pole
   Margin, Championship Lead, Bank Rate, Leaders in a Decade, Antikythera Fragments, Iran's SCO Deals)
   with not one personal number. SPEC §3.1's `source_band` field, and its worked example
   (`"Pole Margin", source_band: "touchline"`), *accepts* band-sourced rows — so the contract now
   legitimises the drift. WP-2 wrote the rule the SPEC specifies (rows declare their source; a
   band-sourced row must have moved in-window; evergreen long-read rows are barred) and added a line
   that the strip "should still read as the reader's week, not a second news digest" — but **whether
   the band is personal, mixed, or news is an editorial call above WP-2's pay grade** and it is not one
   of the five defects. If the answer is "personal", the fix is a floor on `source_band: "state"` rows,
   which is a WP-5 check and a SPEC amendment.

4. **→ WP-7: the sport-token list is the vocabulary, and the daily's `sport` catch-all is not.**
   `sections.md` § The Touchline now tells writers that `data-sport` takes a canonical sport token from
   `data-contracts.md` § Sport tokens and that `multi_sport` is forbidden there. WP-1's mapping table
   already says the daily's routing domain is a separate namespace — no action needed unless
   `profile.js` starts emitting tokens that have no home in the ledger list.

5. **→ WP-4: two doctrine statements assume checks that must actually exist**, or the prose overclaims:
   the `week_in_numbers` evergreen exclusion (no row with `source_band` = the `long_read` chapter when
   `vintage == "evergreen"` — this is a **plan**-level check, so WP-5 rather than WP-4), and the
   `data-sport="multi_sport"` hard fail per the SPEC §3.11 amendment. Both are written as enforced.
