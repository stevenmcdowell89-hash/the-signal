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

## Batch 5 — Weekly W-2/W-3/W-4 (the rebuild) ⬜
The Desk (rotating service columns + "Do This Week"); The Threads continuity
engine; The Week in Numbers; four-movement architecture (OPEN / LONG READ /
ROUNDS / CLOSE); Caught Up; single Long Read; "The case against" callout; ~40%
length cut; ~12-component palette; Saved This Week loop; editorial-charter
consolidation. **Gate ledger:** retire to exactly three (image-URL chain, markup
contracts, one holistic quality read).

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

---

## Hard constraints being honoured
- **No Reddit Data API / OAuth, ever.** Reddit is public per-subreddit `.rss` only;
  the size-tiered rotation is permanent. Batch 6 scrubs any lingering
  `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` references.
- **Rebuild wins over incremental patches** for the weekly.
- **Sources are wired in by the implementer**, not handed to the owner.
- **No new gates**; retire to the three in §5.
