# The Signal — Implementation Progress (July 2026 recommendations)

_Tracks the implementation of `docs/signal-final-recommendations-2026-07.md`. This
is the living status log: what shipped, what decisions were made, and what remains.
Updated as each batch lands on `claude/signal-recommendations-2026-07-x1v7xu`._

**Approach:** work is batched by the build order in §4 of the recommendations and
delegated to focused subagents (one batch at a time, each tested and committed) so
each change is isolated, verifiable, and git-clean. Concrete code changes (the
daily pipeline, the frontend) are tested with node harnesses; editorial/spec
changes (the weekly rebuild, specials) are validated with the repo's Python
validators and consistency checks.

## Status legend
- ✅ done & committed · 🚧 in progress · ⬜ not started

---

## Batch 1 — Daily D-1 bugs & fast wins ✅

Commit: _Daily D-1: fix push, reconcile cadence, source-count chip, voiced Start-here_

| Item | What changed | Decision |
|---|---|---|
| Dead significance push | `notify.js:pickSignificant()` now reads `state.top20` (was the retired `state.top_catches`, which silently killed the daily's only push). Exported for unit testing. | — |
| Reconcile cadence | Removed the dead advisory `cadence_hours` entirely (config default, Settings input + readonly display, `/api/health`) and corrected `OPERATIONS.md`/`wrangler.jsonc` to state the real **every-10-min cron**. | Chose **delete + fix docs** over "make it a skip-gate": the 10-min tick is load-bearing (Reddit per-IP rotation depends on it), so a 3h skip-gate would break the design. A no-op "how often" control is dishonest, so it's gone. |
| Render `source_count` | `catchEl` shows a "◆ N sources" chip when `source_count >= 2`. | — |
| Start here → tappable/voiced/linked | `render.js` emits `start_here` as `{id,title,why,link}`; `why` seeds from the mechanical hook and `editorial.js` backfills the curated "why it matters" from Picks/Top 20 when the item also cleared those passes. `index.html` renders each as a link with its reason (back-compat with old string form). | Reuses the lead `why` already computed (per B4), with a hook fallback so it works with AI off. |
| Today & Tonight config-driven | `render.js:todayAndTonight()` gates on `topic_weights[d].today_tonight` (seeded true for football/gaming/film_tv; profile bumped to v7) instead of the hardcoded `football||film_tv||gaming`. Falls back to the old set when no topic has flagged in. | — |

**Test:** `scratchpad/test-d1.mjs` — 12 assertions, all passing (start_here shape,
config-driven + fallback Today & Tonight, source_count passthrough, `pickSignificant`
reading `top20` and ignoring the retired field).

---

## Batch 2 — Weekly W-1 (voice & the person) ✅

Commit: _Weekly W-1: The Letter, Gate 1A split, kill the aphorism tic, retire entry-pattern rotation_

Spec-only phase (no code pipeline change) — all edits land in the `the-signal`
skill's editorial spec, its sliced views, the compliance checklist, and the weekly
foreword template. **No script gate added or removed** — this phase RETIRES checks,
per §5 of the recommendations. Bumped skill to **v8.35.0**.

| Item | What changed | Decision |
|---|---|---|
| The Letter replaces the Foreword | Weekly opening movement is now **The Letter** — a named Editor in first-person ("I") stating the week's thesis and connecting dots across domains (~120–200 words, "— The Editor"). Updated `editorial-spec.md` (new § The Letter + Fixed list + exempted-sections list), `spec/weekly.md`, `spec/global.md`, `sections.md`, `compliance-checklist.md`, and rewrote `assets/template-parts/05-foreword.html`. | Kept the **same `foreword` chapter_id + `.foreword` markup/drop-cap** (renamed + re-voiced, not re-plumbed) so the navigator anchor, stitcher, and `validate-issue.py` are unaffected. Added a small `.foreword .letter-signoff` CSS rule (a `<div>`, not a `<p>`, to escape the per-paragraph drop-cap). **Specials keep their own Foreword** — W-1 is weekly-only. |
| Split Gate 1A | 1A now has two halves: **1A(i)** reader stays invisible (no "you"/"your son"/profile callbacks); **1A(ii)** the Editor's first-person voice is explicitly PERMITTED. Updated `compliance-checklist.md` § 1A + the Cardinal Rule in `editorial-spec.md` and `spec/global.md`. | **No script enforces 1A** (it's a manual reading pass — confirmed by grep of `scripts/`), so the split is spec/checklist-only. Reframed the rule as "no *second-person* reader address", not "no first person". |
| Kill the per-section aphorism structurally | § Editorial Voice (both `editorial-spec.md` + `spec/global.md`) now caps genuine aphorisms at **one per issue**, drops any "every section ends on a line" expectation, and forbids reprinting the **Angle box as a pull-quote** (noted on the Angle/Pull-quote rows of the component palette in both files). | Method = remove the requirement, not add a gate (List 1 W3 "method dropped, goal kept"). |
| Retire entry-pattern-rotation enforcement | Removed the "no two adjacent articles open the same way" mandate from `editorial-spec.md` + `spec/weekly.md` and the Gate 2 "Entry pattern rotation" checklist item. Entry patterns are now a **palette**, not a rota; plain prose is a first-class opener. | The rotation rule was a source of the mechanical tic; no script enforced it, so retirement is spec + checklist only. |
| "Daily carried the facts, here's the layer" opener | Documented as the **standard opener** for any live-news section (§ Article Structure in `editorial-spec.md` + `spec/global.md`), with an explicit rule that the machinery stays invisible in prose (never narrate "the daily carried X" / "you already know"). | Promoted factor-2's existing Cardinal-Rule note into a standing, named opener rule. |

**Validation:** all 9 skill Python scripts `ast.parse` clean; `validate-issue.py
--format weekly --skip-image-urls` on `issues/signal_weekly_2026-07-05.html` →
PASS (exit 0), confirming the template/CSS rename didn't break structural/anchor
checks. Grep-swept the spec + checklist: no dangling "Entry pattern rotation"
mandate or weekly "Foreword" reference remains (remaining `Foreword` hits are all
special-edition formats, which are out of scope for W-1).

## Batch 3 — Daily D-2 (daily-ness structural moves) ✅

Commit: _Daily D-2: read-state, developing-delta + Still developing, One Big Thing lead, save-for-later_

The daily's structural moves — three client-only (read-state, One Big Thing,
save-for-later) and one that flows through the engine (the developing-delta). **No
new AI/model dependency, no new AI pass** (honours §2c) — the delta is a mechanical
comparison of two logged signal tiers.

| Item | What changed | Decision |
|---|---|---|
| Per-item read state | `index.html`: opened item ids persist in `localStorage` (`signal-brief-read`); read cards get `.is-read` → dim + collapse (body/footer/delta fold away, title stays) so the brief visibly shrinks through the day. Marked on card open. | **Capped** at 500 ids (`capIds` keeps the most-recent, drops the oldest front) so the set can't grow unbounded. Kept **independent of the "N new since HH:MM" watermark** (that keys off `first_seen`, untouched). |
| Developing-delta — the one content move | `story_log` extended with a **`signal` column** (the last-surfaced signal tier); `score.js` sets `it.signal_tier` (`high`/`low`/`neutral` via `signalTierOf`) and, for a **developing** cluster whose tier moved since its last logged point, attaches `it.delta = { was, now, was_label, now_label, prev_headline }`. `render.js` exposes `delta`/`signal_tier` on every item and builds a capped `state.developing` (developing items **with** a delta). `index.html` renders a delta line and a **"Still developing"** group. | **Schema:** one idempotent `ALTER TABLE story_log ADD COLUMN signal TEXT` (mirrors the existing `source_count` pattern); `getLastStoryPoints` tries the signal-aware SELECT and **falls back** to the legacy columns on an old DB, so a missing column degrades gracefully instead of throwing. **Phrasing:** domain-agnostic `signalPhrase` — `high→confirmed`, `low→rumoured`, `neutral→reported` (renders "was rumoured → now confirmed"). Chose general words over football-specific ("here we go") since the delta spans all domains. |
| One Big Thing lead | `index.html`: `headlines[0]` promoted into a distinct `.lead` block (bigger serif type, `why` always shown, source-count + Developing + delta inline). The remaining headlines render below starting at rank 2; **the lead is not repeated** in that list, and any "Still developing" item already shown as lead/headline is de-duped out. | Purely a render move — no state change; the lead reads from the existing `state.headlines`. |
| Save-for-later | `index.html`: a ☆/★ star on every card (and the lead) toggles a `localStorage` list (`signal-saved`) storing **`{id,title,link,ts,domain,domain_label,saved_at}`** — enough for a later weekly digest to consume. A **"Saved"** tab (shown only when non-empty) lists them newest-first. | **localStorage-first with a clean seam** for a later KV/cross-device path (B4/W-4 bridge). Capped at 300. Star click `preventDefault`+`stopPropagation` so it never navigates or marks-read. |

**Test:** `scratchpad/test-d2.mjs` — a 20-assertion node harness with an in-memory
D1 stub (`.prepare().bind().all()/run()` + `.batch()`) whose `story_log` persists
across two `scoreBatch` runs: asserts the delta is computed when a cluster's signal
tier changes across runs (low→high, phrased "rumoured→confirmed"), that
`state.developing` surfaces the moved item but **not** a developing item without a
delta, and that `publicItem.delta` is `null` (shape unchanged) for unmoved items —
**20/20 passing**. Regression: `scratchpad/test-d1.mjs` **12/12 still passing**.
Client-only pieces (read-state capping, save, One Big Thing/lead rendering) can't be
browser-run here — verified via `node --check` on the extracted inline `<script>`
(parses clean) plus self-review; the testable pure logic (`signalPhrase`,
`signalTierOf`, delta computation) is covered by the harness.

## Batch 4 — Daily D-3 (bridge & content depth) ✅

Commit: _Daily D-3: consolidate picks/top20 → one curation call, daily→weekly digest endpoint, community digest, skim-vs-understand, morning/evening, smartMerge default_

Consolidate FIRST (per §2c), then add only distinct new jobs — **net AI-pass count
is unchanged**: `picks`+`top20` (2 model calls) → **one** `curate` call; added
**community digest** (1). The football-saga / written-delta AI line was **deliberately
NOT added** (mechanical D-2 delta already does that job — the correct §2c call).

| Item | What changed | Decision |
|---|---|---|
| **Consolidate `picks`/`top20`** | New `curateEditorial` makes ONE `callModel` over the UNION of both candidate pools, producing a single ranked "why it matters" set. Headlines = the breadth-eligible subset (capped to `picks.count`); Top 20 = the cross-everything subset (capped to `top20.count`) — two VIEWS of one call. Removed `editPicks`/`curateTop20`, `picksSystem`/`top20System`, the `editorial:picks`/`editorial:top20` KV keys (→ `editorial:curate`). Spend logged under `curate`. | **Back-compat:** kept `ai.picks.enabled`/`ai.top20.enabled` as the per-SURFACE toggles — the merged call is scoped to only the enabled surfaces' candidates, and each surface is left mechanical when its toggle is off. No reader toggle is silently dropped. Added a shared `ai.curate` block (model/interval/guidance, guidance falls back to top20→picks). Health card keeps its `picks`/`top20` keys, driven from the one call's per-surface status. |
| **Daily→weekly digest** | `GET /api/daily/digest?since=7d` (open read, wired in `_worker.js`). Reads `story_log` via new `db.getStoryLogSince` + optional `db.getItemsByIds` for links. Pure `functions/daily/digest.js`: `parseSince` (7d/72h/90m/bare-number-days, clamped 1h–60d) + `assembleDigest`. Returns `{ since, since_ms, generated_at, counts, surfaced:[…], moved:[{id,title,domain,was,now,was_label,now_label,…}], saga_lines:[…] }`. | **`moved`** = clusters whose first→last non-null D-2 signal tier differs (rumoured→confirmed). Mechanical `saga_lines` one-liners so the weekly (W-4) has them without an AI pass. **Graceful:** missing table/column/DB → empty arrays, never a 500 (matches `getLastStoryPoints`' legacy-column fallback). |
| **Community digest** | New `communityDigest` pass over `state.communities`: "what Reddit/HN/Bluesky are arguing about today" → `state.community_digest`. Own toggle (`ai.community`), shared cap, cached by community-set hash + 45-min throttle. Rendered above the Communities feed in `index.html`; Settings card + health row added. | Distinct job vs the per-edition briefs (those summarise a domain section; this reads the community sources as one conversation). One cached pass, ≥3 posts required. |
| **Football saga / written developing-delta line** | **NOT added — SKIPPED.** | Correct §2c call: the mechanical D-2 delta already renders "was rumoured → now confirmed" + the "Still developing" thread, domain-agnostically and with no model cost. An AI saga one-liner would be redundant. The digest endpoint's mechanical `saga_lines` feed the weekly instead. |
| **Skim vs understand** | `catchEl` now shows `why` as the visible line AND, when a distinct `hook` also exists, an expandable "+ what's new" toggle reveals the hook instead of dropping it. Collapses under read-state. | Both lines reachable; skim stays one line. |
| **Morning / evening framing** | `render.js` stamps `state.edition_phase` (`morning` before ~13:00 UTC, else `evening`) + `state.edition.phase`. `index.html` frames the masthead status ("This morning/evening · Caught up · HH:MM") and titles the developing thread "What moved since this morning" in the evening. | Small, mechanical; UTC hour (reader is UK). Content is the same living surface. |
| **smartMerge default** | **Enabled by default** (`ai.merge.enabled: true`). | **Decision:** enable-by-default over the entity-merge extension. The guards make it safe — same-domain groups only, candidate-capped, no-op on any failure — and it FOLDS the merged members' `source_count`+`links` into the survivor rather than truly losing the story. Existing saved configs that explicitly saved merge off keep their choice (merge default only reaches fresh/untouched configs), so no brief silently loses content. |

**Test:** `scratchpad/test-d3.mjs` — 38 assertions, all passing: `parseSince`
(7d/72h/90m/number/invalid/clamp); `assembleDigest` (moved reflects tier change,
empty→empty, null-signal surfaced-not-moved, saga_lines); the digest **handler**
with an in-memory D1 stub (moved/surfaced, empty DB→empty+200, no-DB→200); the
**consolidated curate** pass with a stubbed `callModel` (AI-off leaves mechanical
Headlines/Top 20 untouched; one stubbed call orders + attaches `why` to BOTH
surfaces; the Top-20-only back-compat toggle path); the **community digest**
(off→no-op, on→writes `state.community_digest`, <3 posts→no-op). Regression:
`test-d1.mjs` **12/12** and `test-d2.mjs` **20/20** still pass. `node --check`
clean on all touched JS + both HTML inline scripts.

## Batch 5 — Weekly W-2/W-3/W-4 (the rebuild) ✅
The weekly rebuild landed in three phases (W-2, W-3, W-4). **All three done** —
the batch is complete. W-4 (below) was the final phase: it closed the daily→weekly
bridge on real data, consolidated the patch-stack into one Editorial Charter, and
closed the gate ledger at exactly three ship-quality gates.

### Weekly W-2 — Service & continuity ✅
Commit: _Weekly W-2: The Desk + "Do This Week", The Threads, The Week in Numbers, retire cadence-floor + deficit-promotion_

Spec + scaffold + two script-rule removals. Bumped skill to **v8.36.0**. A prior
partial run had staged — uncommitted — the `editorial-spec.md` / `sections.md` /
`component-contracts.md` edits, the template-parts (`13a-the-desk.html`,
`15a-the-threads.html`, `15b-week-in-numbers.html`), the CSS
(`15a-service-continuity.css`), and a `check_rotating_cadence` no-op stub. This
batch **completed and cleaned that up**: deleted the dead `_resolve_rotating_state`
helper + `ROTATING_SECTION_CADENCE` / `CHAPTER_ID_TO_ROTATING_KEY` maps + the
inline cadence tests (leaving the script's other rules intact), regenerated the
sliced spec views via `slice-spec.sh`, added the "Do This Week" pin to the
standalone `14-session.html`, updated `SKILL.md` / `CHANGELOG.md` / the schema /
the compliance checklist, and verified the two validations.

| Item | What changed | Decision |
|---|---|---|
| The Desk (service department) | New department grouping four rotating **service columns** — The Session, The Ledger (rebrand of "Money"), The Itinerary (rebrand of "Places"), The Toolkit — **1–2 per issue**. Spec in `editorial-spec.md` (§ The Desk + Fixed/Rotating + Cadence Table) → sliced to `spec/weekly.md`; briefs in `sections.md`; chapter_ids in `chapter-plan-schema.md`. New template-part `13a-the-desk.html`; CSS in `15a-service-continuity.css`. | Grouped as a **department, not a merge** — each column is a standalone `<section>` (`.ledger-section` etc.) carrying its own accent/brief and a shared "The Desk — [Column]" label; 1–2 render per issue. Columns picked by "most overdue **and** has actionable service news", not a cadence clock. Rebrand is **reader-facing only** — state keys stay `the_money`/`the_places` for continuity. |
| "Do This Week" pin | Mandatory closing element of **every** Desk column: `.do-this-week` > `.dtw-label`/`.dtw-action`/`.dtw-why` — one concrete action + the why + the stated criterion (not vibes). Contract in `component-contracts.md`; in `13a-the-desk.html` (all four columns) + `14-session.html`; CSS in `15a-service-continuity.css`. | The pin **auto-tints to the host column's accent** via `var(--section-accent)` (already set per section in `04-layout-sections.css` for session/ledger/itinerary/toolkit), so writers add no CSS. Exempt from the one-aphorism cap; renders with JS off. |
| The Threads (continuity engine) | New reader-facing "previously on…" section off `ongoing_stories`, extended beyond World to named sagas across all domains + the reader's life-threads (`training_phase`, `upcoming_trips`). Spec § The Threads; contract + template-part `15a-the-threads.html`; CSS `15a-service-continuity.css`. | **`ongoing_stories` made DUAL-USE:** the topic-lock suppression backstop (`check-topic-lock.py`) and the existing Ongoing-tracker box are **kept unchanged**; The Threads *additionally* reads the same records. `.thread-saga` (from ongoing_stories) vs `.thread-life` (the person). It's a recap, not a Lead — **no** Do-This-Week pin. Stood up as a section now; formally joins the CLOSE movement in W-3. |
| The Week in Numbers | Small personal stat strip near the top: Garmin miles + training block (`training_phase`), FPL rank, the Juventus result, one money number (from The Ledger). Spec names each source. Contract + template-part `15b-week-in-numbers.html`; CSS `15a-service-continuity.css`. | Reuses `.stat-bar`/`.stat`; kept **distinct** from the Colophon's Issue-in-Numbers (a boxed note in the spec forbids merging). Numbers come from `signal-state.json` / the D-3 digest where available. |
| Retire cadence-floor + deficit-promotion | Removed old planner **rule 7** (hard cadence floor) and **rule 8** (deficit promotion) from `validate-chapter-plan.py`: the `check_rotating_cadence` fn, the `_resolve_rotating_state` helper, the `ROTATING_SECTION_CADENCE` / `CHAPTER_ID_TO_ROTATING_KEY` maps, the `deficit_override_reason` escape hatch, and the inline cadence tests. Compliance-checklist §§ 1L/1M and the spec's Selection Rule 6 now carry a single editorial line — *each domain surfaces at least monthly* — **with no enforcement**. | Per §5 gate ledger — retire, don't add. The Threads owns continuity, so a quiet domain no longer needs a forced-include gate. **Did not touch** the other rules in the script (section shape, long-shelf, release-radar, sub-format, key-facts, discovery quota — they belong to later phases). |

**Validation:** `ast.parse` clean on `validate-chapter-plan.py`; inline `--test`
suite **53/53** (cadence tests removed). `validate-issue.py --format weekly
--skip-image-urls` on `issues/signal_weekly_2026-07-05.html` → **PASS (exit 0)** —
the spec/template/CSS additions don't touch the already-rendered issue. Grep-swept:
no dangling "deficit promotion" / "hard cadence floor" mandate in the spec or
checklist; remaining "Money"/"Places" hits are all rebrand-context ("was 'Money'").

### Weekly W-3 — The spine & the Long Read ✅
Commit: _Weekly W-3: four-movement spine + Caught Up + single Long Read, ~40% length cut, ~12-component palette, retire topic-lock/theme-clustering/plain-English-random-sample_

Spec-heavy reorganisation + one validator relaxation + a new component + CSS + two
script deletions. Bumped skill to **v8.37.0**. No new templates (the Long Read reuses
the existing `08-anchor-piece` slot; Caught Up / case-against are markup contracts + CSS).

| Item | What changed | Decision |
|---|---|---|
| Four-movement spine | `editorial-spec.md` § Section Structure gains a "Four-Movement Architecture" block + § The Week, Composed / § Caught Up / § The Long Read; Fixed-list regrouped by movement; re-sliced to `spec/weekly.md`; `compliance-checklist.md` Coverage rewritten around the movements; `sections.md`. | **I OPEN** (Letter → The Week, Composed → Week in Numbers → **Caught Up**) · **II LONG READ** (one anchor) · **III ROUNDS** (Touchline, Pixel & Byte, Screen & Sound, Bookmark books rail, The Desk) · **IV CLOSE** (Threads → Rabbit Hole → On the Radar → Do This Week → Colophon; ends on a verb + a human line). Branded identities kept; **Long Shelf retired** (on-ramp → The Week, Composed; wildcards → Letter/Long Read). World is no longer a standalone round (breadth → Caught Up, depth → Long Read). |
| Single Long Read | Movement II is exactly ONE deep anchor, rotating subject, reusing `08-anchor-piece` (`.is-anchor`). Absorbs the old Saga / Deep-Dive-lite / evergreen-feature impulses. | No new template — reuses the existing anchor slot. The whole-issue Deep Dive special is untouched (the Long Read is a *movement*, not a format). |
| Stop forcing two deep anchors | `validate-chapter-plan.py` `check_section_shape` **relaxed**: removed the "must have a Lead or `yield_reason`" hard-fail. A round may be a Lead, a plain Catch-Up, picks, or a silent yield. Piece well-formedness + Catch-Up no-namedrops still enforced. Two inline tests flipped to `expect_pass=True`; docstring/header + `chapter-plan-schema.md` `pieces` + checklist 1G updated. | The single Long Read carries the deep work, so the per-section considered-piece backbone is redundant bulk. Kept the Lead/Catch-Up shape *available*, not mandatory-deep. |
| Caught Up + retire breadth-safety-net | New `.caught-up` (≤8-line, non-expandable) contract + CSS `15b-open-argument.css`. The per-section "one-line safety-net headlines" job removed from § Article Structure / § Section Rules / Search-Checklist / checklist. | Completeness is a *fixed 8-line budget* up front, not an open drawer in every section. Renders complete JS-off (no expand affordance to break). |
| The case against | New `.case-against` > `.ca-label`/`.ca-body` — Semafor-style sourced counter-argument. Palette row #12 + `component-contracts.md` + CSS. | Available only **where a section carries a real argument** (usually the Long Read); a real position, never a strawman (Borrowed angles, our voice). Section-accent, JS-off. |
| Length ~40% cut | `~6,000–9,000-word` target replaces "~20–30 pages" in § Identity + Standard Weekly overview (→ sliced). | A real target the four-movement spine is built to hit; past ~9k = reverted to old bulk. |
| Palette → tight ~12 | § Component Quick Reference rewritten: **12 surviving** — Angle · Pull quote · Stats row · Did You Know · Split layout · Image (hero/offset) · Also cards · Rating dots · Category dot · Results strip · Read-next · **The case against**. ~30 others marked **removed inline** (no graveyard file; CSS retained for specials). Always-on structural components (watermark, opener, reveal, count-up, `.foreword`/`.caught-up`/`.do-this-week`/`.the-threads`/`.week-in-numbers`) listed separately, not counted in the 12. | Decisive trim — the sprawling palette invited slot-filling. |
| Retire topic-lock | **`check-topic-lock.py` deleted**; its Gate-1 grep + the § Topic Lock machinery gutted (heading kept so the slicer still resolves `02b-topic-lock`); SKILL Phase-7 invocation + the `lead_history` append instruction removed. `ongoing_stories` now feeds **ONLY The Threads** + the Colophon "Next Week" note — the suppression role is **intentionally dropped** in favour of the continuity recap (said so in the spec). | Per §5 gate ledger. The Threads owns continuity; suppression-by-gate is redundant. |
| Retire theme-clustering | **`check-theme-clustering.py` deleted**; SKILL Phase-7 invocation + Key-Rules backstop references removed. | The four-movement spine (one Long Read + brisk rounds) removes the structural cause; one of the ~8 scripts §5 collapses. |
| Retire plain-English random-sample (weekly) | The standalone 3-random-paragraph weekly reading pass retired in `SKILL.md`, `quality-rubric.md`, and `editorial-spec.md` (v8.30 "not Deep-Dive-only" note narrowed). Folded into the holistic read arriving in W-4. | The **Deep Dive / literary-special** reading pass + trope lists are kept as calibration. |

**Validation:** `ast.parse` clean on `validate-chapter-plan.py`; inline `--test` **53/53**;
`slice-spec.sh` exit 0, **0 FAILs**, four movements confirmed in `spec/weekly.md`;
`validate-issue.py --format weekly --skip-image-urls` on
`issues/signal_weekly_2026-07-05.html` → **PASS (exit 0)** (an old issue predating the
movements; it isn't structurally rejected — validate-issue.py checks structure/back-link/
placeholders/CSS/navigator, none of which changed). Grep-swept: no dangling
topic-lock/theme-clustering/two-deep-anchors/breadth-safety-net/plain-English-random-sample
live references; palette lists exactly 12.

**Deferrals:** The Week, Composed and Caught Up are specified as markup contracts + CSS but
have **no dedicated template-part** (they reuse `.foreword`-adjacent / `.sec-opener` styling and
a plain list) — a scaffolded template-part can follow if wanted. The **holistic editorial-quality
read** that replaces the retired plain-English weekly gate lands in **W-4** (the gate ledger
collapses to three there); until then the weekly has no standalone prose-performance gate.

### Weekly W-4 — Personalization loop & consolidation ✅
Commit: _Weekly W-4: Saved This Week bridge, one Editorial Charter, gate ledger closed to three_

The FINAL phase of the July weekly rebuild. Spec + sliced views + checklist +
one state field + one validator assertion; two scripts deleted. Bumped skill to
**v8.38.0**. No new templates (synthesis-by-juxtaposition reuses existing
blockquote/`.source-strip` vocabulary; the stats assertion is code, not markup).

| Item | What changed | Decision |
|---|---|---|
| **Saved This Week — the daily→weekly bridge** | New `saved_this_week` array in `state/signal-state.json` (`{title, url, domain, saved_at, daily_why, saga?}` + a `_note` documenting it; `saved_last_week` kept for reference). Documented in `editorial-spec.md` § The daily→weekly bridge (→ carried into the Charter): weekly generation reads `GET /api/daily/digest?since=7d` (`{surfaced, moved, saga_lines}`) **plus** `saved_this_week` when composing The Letter and The Threads. | **The Letter** consumes `digest.moved` + `digest.saga_lines` + `saved_this_week` (the week's thesis / cross-domain dots — the strongest thread is where a *moved* story and a *saved* item rhyme). **The Threads** matches `saved_this_week` + `digest.saga_lines` against `ongoing_stories` topics/aliases to pick + prioritise saga recaps. Populated by the D-2 save-for-later affordance; consumed **read-only**. **Enriches, never a hard dependency** — empty/absent falls back to `ongoing_stories` + bundle. Machinery stays invisible per the Cardinal Rule. |
| **Synthesis-by-juxtaposition** | Documented as a **prose technique** (not a new component) in `editorial-spec.md` § Synthesis-by-juxtaposition: 2–4 **attributed** conflicting excerpts in sequence for contested World/Long-Read material (now in Caught Up / the Long Read). | Attribution mandatory (traces to bundle `opinion` facts); excerpts must genuinely conflict; **no connective sentence** telling the reader what to conclude (that's the hollow-connective trope). Reuses blockquote / `.source-strip` — a contract can be added later if a visually distinct block is ever wanted. |
| **One Editorial Charter (consolidation)** | New `## Editorial Charter` at the top of `editorial-spec.md` (north-star + the standing rules as they NOW are) → sliced to `spec/global.md § charter` (added `extract_heading` for it in `slice-spec.sh`). The v8.13→v8.38 version narrative **removed** from `editorial-spec.md`'s top blockquotes **and** from `SKILL.md` L21's patch paragraph — history now lives in `CHANGELOG.md` only. | The living spec reads as **one charter, not a patch pile**. CHANGELOG history preserved (not deleted). SKILL.md L21 is now a lean charter/CHANGELOG pointer + a one-paragraph current-state summary. |
| **GATE LEDGER — exactly three** | `compliance-checklist.md` now **opens** with the three-gate ledger table; the detailed Gate 1/2/3 content is reframed as **reading aids** feeding those gates, not additional gates. | **(1) Image-URL verification chain** — `validate-issue.py` image checks + `auto-repair-images.py`. **(2) Markup contracts** — `validate-issue.py` structural/placeholder/back-link/markup + component-variety, **folding in the Issue-in-Numbers stats assertion**. **(3) One holistic editorial-quality read** — Phase 9.5 reframed from observational scorer to the third gate (blocking-ish; Phase 10 still always publishes), judging *did this issue tell him what the week added up to, and give him one thing to do?* `validate-research-bundle.py` + `validate-chapter-plan.py` are **upstream production aids, NOT ship gates** (said so explicitly). |
| **Issue-in-Numbers stats assertion** | Added `check_issue_in_numbers_stats` to `validate-issue.py` (wired into the universal checks): fails if the Colophon's `.colophon-stats` numeric figures are **all identical** or **all equal the issue number** (the 13/13/13/13 placeholder defect). Documented in `editorial-spec.md` § Block 1 + the ledger. | **A lightweight markup-safety assertion inside the markup gate — NOT a new standalone script** (per List 1 W9's reframe). No-ops on specials (no Colophon). |
| **Delete prose-rhythm + visual-smoke-test** | `check-prose-rhythm.py` and `visual-smoke-test.py` **deleted**; phase invocations removed from `SKILL.md` (Phase 7.75 + 7.8), the gate-discipline list, and the CI workflow (`.github/workflows/issue-validation.yml`). | Prose-rhythm's "paragraph wall" intent → **gate 3** (the holistic read). Visual-smoke's image-safety intent (old D3/D6/D7) → **gate 1** (`validate-issue.py` extension check + `auto-repair-images.py` dedup — self-contained, no import of the deleted script); its holiday-chrome intent (D1/D2/D4/D5) → **gate 2** (holiday activation/components + Gate-1E greps + the stitcher override). |

**Validation:** `ast.parse` clean on `validate-issue.py` (+ `auto-repair-images.py` unaffected).
`validate-issue.py --format weekly --skip-image-urls` on `issues/signal_weekly_2026-07-05.html`
→ **PASS (exit 0)**; the new `issue-in-numbers` check reads `[6900, 12, 90, 10, 40]` (issue #15)
→ distinct, PASS. `slice-spec.sh` exit 0, **0 FAILs**, charter present in `spec/global.md`.
Grep-swept: `compliance-checklist.md` presents exactly the three ship-quality gates; **no
dangling live references** to `check-prose-rhythm` / `visual-smoke-test` (only "deleted/folded"
context) anywhere in SKILL/spec/checklist/CI.

**Deferrals (unchanged from W-3):** The Week, Composed + Caught Up still have no dedicated
template-part (reuse existing styling). Synthesis-by-juxtaposition ships as prose-only (no
distinct markup) by design. The `saved_this_week` field is documented + wired in the spec/state
but the daily side that *populates* it (D-2 localStorage → KV/endpoint sync) remains a Stream-2
work-item; the weekly consumes it read-only and degrades gracefully when it's empty.

## Batch 6 — Cross-cutting + Specials + Sources + D-4 ⬜
- **Cross-cutting:** H3 weekly-as-front-door hero · H4 `prefers-color-scheme`
  seam · H6 reciprocal cross-stream links · H7 Settings Reader/Engine split · H8
  auto-generate archive from a manifest.
- **Specials:** S1 resolve the three ghost formats · S2 fold Lookahead into the
  weekly · S3 enforce reader-invisibility + fact-provenance on light formats · S4
  merge recommendation cluster to two (Next + Guide) · S5 simplify trigger stack ·
  S6 hard length ceilings in `validate-issue.py`.
- **Sources:** wire the new per-domain feeds into `feeds.js`, seed the Bluesky
  starter set, add subreddits sparingly as `tier:small`; **scrub every remaining
  Reddit Data API / OAuth reference** per §Hard constraints.
- **D-4 polish:** client-side search · per-domain header line · read-time · RSS
  velocity blind-spot note.

### Sources + Reddit scrub ✅ (Part C wired; OAuth path removed)
**Reddit Data API / OAuth scrub (§Hard constraints) — COMPLETE, grep clean.**
`grep -rniE 'REDDIT_CLIENT|client_secret|reddit.*oauth|api/v1/access_token' functions/`
returns **nothing**. Removed from `functions/daily/ingest.js`: the `_redditToken`
cache, the `redditAppToken(env)` function (read `REDDIT_CLIENT_ID`/`SECRET`, POST
`reddit.com/api/v1/access_token`), and the entire `oauth.reddit.com/.../hot` +
`Bearer` fetch branch of `ingestRedditFeed` — leaving the public `.rss` path as the
sole (and now unconditional) implementation; dropped the now-unused `env` arg from
`ingestRedditFeed` and its caller. Comments in `ingest.js` / `feeds.js` /
`pipeline.js` reworded so `.rss`-only + size-tiered rotation reads as the
**permanent** design, not a pending/temporary workaround. `OPERATIONS.md` already
carried the correct "no API" framing — left as-is.

**Source expansion (Part C wired into `feeds.js`).** New per-domain totals
(`STARTER_FEEDS` RSS/HN went 29 → **94**; `STARTER_REDDIT` 34 → **43**;
`STARTER_BLUESKY` 0 → **4**; `defaultConfig().sources` = **137**):

| domain | rss/hn | reddit | bsky | | domain | rss/hn | reddit | bsky |
|---|---|---|---|---|---|---|---|---|
| world | 9 | 0 | 0 | | football | 9 | 4 | 1 |
| local (NI) | 6 | 2 | 0 | | gaming | 13 | 7 | 1 |
| tech_devices | 5 | 4 | 0 | | ai_engineering | 9 | 0 | 1 |
| finance | 6 | 4 | 0 | | books | 5 | 5 | 1 |
| fitness | 5 | 5 | 0 | | film_tv | 6 | 2 | 0 |
| history | 4 | 2 | 0 | | golf | 5 | 1 | 0 |
| lego | 5 | 1 | 0 | | travel | 4 | 3 | 0 |
| music | 3 | 2 | 0 | | podcasts | 0 | 1 | 0 |

**Bluesky seed** (`STARTER_BLUESKY`, was the single biggest gap — zero): the four
verified handles — `fabriziorom.bsky.social` (Fabrizio Romano, football, 0.85),
`wario64.bsky.social` (Wario64, gaming, 0.9), `reactorsff.bsky.social` (Reactor SFF,
books, 0.5), `simonwillison.net` (AI, 0.7). Ingest validates each and drops
non-resolving handles.

**Subreddits** added sparingly + all `tier:small` (9 thin-domain fills): r/belfast,
r/patientgamers, r/Stormlight_Archive, r/printSF, r/trailrunning, r/kettlebell,
r/kobo, r/UKInvesting, r/Efteling. (r/StarWarsLeaks deliberately **omitted** —
spoiler/leak risk; r/pcgaming skipped to stay sparing.)

Feeds flagged `conv`/anti-bot in Part C are **added-and-validated** (pipeline drops
dead feeds gracefully, logs `dead:N`) rather than pre-excluded, incl. Reuters, AP,
Economist, Belfast Telegraph, 17th Shard, Locus, `starwars.com/news/feed` (may 404 —
Star Wars News Net remains the working default). Tests: `test-sources.mjs` 897/897;
D-1/2/3 regressions 12/20/38 all green; 5 new feeds spot-fetched → 200 + valid XML.

The rest of Batch 6 (cross-cutting H3–H8, specials S1–S6, D-4 polish) remains ⬜.

---

## Hard constraints being honoured
- **No Reddit Data API / OAuth, ever.** Reddit is public per-subreddit `.rss` only;
  the size-tiered rotation is permanent. Batch 6 scrubs any lingering
  `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` references.
- **Rebuild wins over incremental patches** for the weekly.
- **Sources are wired in by the implementer**, not handed to the owner.
- **No new gates**; retire to the three in §5.
