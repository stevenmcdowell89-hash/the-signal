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

## Batch 3 — Daily D-2 (daily-ness structural moves) ⬜
Per-item read state; "what changed since yesterday" developing-delta (extend
`story_log` in `score.js`) + "Still developing" thread; One Big Thing lead;
save-for-later (half the daily→weekly bridge).

## Batch 4 — Daily D-3 (bridge & content depth) ⬜
`GET /api/daily/digest?since=7d` endpoint; consolidate `picks`/`top20` then add a
community digest + optional saga/delta passes under the shared cap; skim-vs-
understand (keep hook + why); football saga + fixtures rail; smartMerge default;
morning/evening framing.

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
