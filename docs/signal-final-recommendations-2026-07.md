# The Signal — Final Consolidated Recommendations (implementation-ready)

_July 2026. This is the single source of truth. It merges the two prior review documents into one plan and resolves every clash between them. **Where the incremental fixes clash with the ground-up rebuild, the rebuild wins.**_

**Supersedes for planning purposes:**
- `docs/signal-recommendations-2026-07.md` (the incremental tiered review — "List 1")
- `docs/signal-weekly-redesign-and-daily-sources-2026-07.md` (the ground-up rebuild + daily enhancements + source list — "List 2")

Keep both prior docs for detail and reference — in particular **List 2 Part C holds the full per-domain source URLs** this plan points to. But when List 1 and List 2 disagree, follow this document.

**For the implementer:** this is a recommendations/scope document, not code. It is sequenced so you can implement it in order. File paths are given as anchors, not prescriptions. Two standing instructions:
1. **Bias to the rebuild.** The weekly is a redesign, not a patch. Do not re-add machinery this plan says to retire.
2. **Sources are yours to add, not the owner's.** The daily source expansion (Part 3 / §Sources) is an implementation work-item — wire the feeds in and validate them on ingest. Do **not** hand the owner a list to paste into Settings.

---

## 1. Guiding principles (both lists agree on these)

1. **The weekly is the anchor.** One living daily wrapped around a Sunday centrepiece, with specials as rare interruptions of the anchor. (`manifest.json` already frames it as two streams — "The Brief, daily — and The Read.")
2. **Rebalance from compliance to quality.** The system optimises for "didn't break," not "is good." The rebuild's north star is one question: _did this issue tell the reader what the week added up to, and give him one thing to do?_
3. **Retire gates, don't add them.** The weekly rebuild collapses ~8 compliance scripts to **three** (see §5 Gate Ledger). Any recommendation whose method was "add a check" is reconsidered against this.
4. **Put a person in the personal magazine** (weekly) and **make the daily a story you're following** (daily continuity).
5. **The daily and weekly must actually share data** — the bridge is asserted today but no bytes flow.

---

## 2. Reconciliation — what changes when the two lists combine

### 2a. Dropped or reframed FROM LIST 1 (because the rebuild supersedes them)

| List 1 item | Verdict | Why |
|---|---|---|
| **W2 "target 8–9 sections, not 12–13"** | **Dropped / superseded** | The rebuild's four-movement architecture (one Long Read, ~6–9k words, ~12-component kit) is more specific and more aggressive. Implement the movements, not a section count. |
| **W3 "add a document-level voice-tic gate"** | **Method dropped; goal kept** | Do **not** add a new gate. Kill the tic **structurally**: remove the rule that every section must end on a line (cap one aphorism per issue) and forbid the Angle-as-pull-quote. The recurring tic disappears at the source, per the gate-retirement principle. |
| **W8 "fix the on-ramp / collapse Navigator + Long Shelf"** | **Absorbed / superseded** | Movement I (The Letter → The Week, Composed → Caught Up) replaces the triple table-of-contents on-ramp outright. The Long Shelf as a concept is gone; its discovery-wildcard value moves into the Letter and the Long Read. |
| **W9 "add an Issue-in-Numbers validation gate"** | **Reframed — not a new gate** | The 13/13/13/13 defect is real, but fold a one-line "stats aren't identical / aren't the issue number" assertion into the surviving markup-safety gate. No standalone script. |
| **W11 "add a weekly-coherence (throughline) metric"** | **Absorbed** | Coherence-as-one-read is exactly what the single holistic quality read (the one surviving editorial gate) judges. No separate metric. |
| **W10 "add a new 'Connection' signature feature"** | **Downgraded to optional** | The rebuild already designates **Down the Rabbit Hole** as _the_ signature ritual, and synthesis-by-juxtaposition already delivers the "connect two stories" value. Don't add a competing rubric; if wanted later, it's a flavour of the Long Read, not a new section. |
| **H2 "wire the observational scorer into the repair loop"** | **Reframed** | Don't bolt the old scorer onto the old 8-gate stack. Under the rebuild the **holistic quality read replaces** the scorer-plus-compliance-scripts as the quality mechanism (§5). The intent — act on quality, don't just observe it — is honoured by making that read blocking-ish, not by re-plumbing the old scorer. |

Everything else in List 1 survives and is folded in below.

### 2b. Merged (same idea in both lists — implement once)

| Merged item | From |
|---|---|
| **Start here → tappable, voiced, linked; Today & Tonight config-driven** | List 1 **B4** + List 2 **B-T1d** |
| **Morning / evening edition framing** | List 1 **B11** + List 2 **B-T2h** |
| **The daily→weekly bridge** (digest endpoint + save-for-later + "Saved This Week" feeding the weekly) | List 1 **H1/H5/B5/B6** + List 2 rebuild's personalization loop |
| **Kill the weekly voice tic** (structural, per 2a) | List 1 **W3/W4** + List 2 rebuild voice rules |

### 2c. One tension to hold: consolidate vs add AI passes (daily)

List 1 **B7** says consolidate the daily's 7 AI passes (`picks`/`top20` overlap); List 2 adds new content passes (community digest, developing-delta line, saga one-liner). **Resolution:** consolidate the redundant passes **first**, then add the new ones only where they have a distinct job. Net AI-pass count should not balloon — fold new jobs into the consolidated structure, keep the shared monthly spend cap authoritative.

---

## 3. The consolidated plan

### STREAM 1 — THE WEEKLY (the anchor; the rebuild)

Implement as the four-phase migration from List 2 §A4. This is the centrepiece; do it in order.

**Phase W-1 — Voice & the person (first, near-zero structural risk)**
- Replace the author-less Foreword with **The Letter**: a named "Editor" speaking first-person — the week's thesis, dots connected across domains. Split Gate 1A so the **reader** stays invisible (no "your son/your trip") but the **Editor** is visible (first-person allowed for the Editor voice).
- **Kill the mandatory per-section aphorism** (remove the "every section ends on a line" requirement; cap one genuine aphorism per issue) and **forbid the Angle-box-reprinted-as-pull-quote**. This is the structural fix for weakest=voice (five issues running), and it replaces List 1's proposed new gate.
- Make the "daily carried the facts, here's the layer" move a **standard section opener** for any section touching live news (but keep the machinery invisible — never narrate "the daily carried X" in prose).
- _Retire:_ the per-section closer/aphorism check and entry-pattern-rotation enforcement.

**Phase W-2 — Service & continuity**
- Stand up **The Desk** — the restored service department, rotating columns **The Session** (fitness), **The Ledger** (money/fintech/Etsy), **The Itinerary** (travel/parks/NI), **The Toolkit** (tech/Android/e-ink) — each ending in a **"Do This Week"** pin (one concrete, do-it-this-week action with the why attached, criteria stated not vibes). Rebrand generic Money→Ledger, Places→Itinerary.
- Launch **The Threads** — the continuity engine — off `ongoing_stories`, **extended beyond World**: named sagas with "previously on…" callbacks across all domains (Iran endgame, Antonelli's title run) _and_ the reader's life-threads (marathon build in `training_phase`, the Efteling trip). Today `ongoing_stories` only _suppresses_ topics for topic-lock; flip it into a reader-facing asset.
- Add **The Week in Numbers** — a small personal strip (Garmin miles + training block, FPL rank, the Juventus result, one money number).
- _Retire:_ the deficit-promotion and hard-cadence-floor validators — replace with a simple "each domain at least monthly" editorial checklist.

**Phase W-3 — The spine & the Long Read**
- Adopt the **four-movement architecture**: I THE OPEN (Letter → The Week, Composed → **Caught Up**, a hard-capped 8-line non-expandable digest) · II THE LONG READ (exactly **one** deep anchor per issue, rotating subject) · III THE ROUNDS (Touchline, Pixel & Byte, Screen & Sound + a Bookmark books rail, The Desk) · IV THE CLOSE (The Threads → Down the Rabbit Hole → On the Radar → **Do This Week** → Colophon; issue ends on a verb + a human line).
- **Stop forcing two deep anchors per section.** The single Long Read absorbs the old Saga, Deep-Dive-lite, and evergreen-feature impulses.
- Add **Caught Up** and retire the breadth-safety-net-in-every-section rule (Caught Up now discharges completeness up front).
- Add the Semafor **"The case against"** callout where a section carries a real argument.
- **Cut length ~40%** (target ~6–9k words) and **trim the component palette to a tight ~12**.
- _Retire:_ the topic-lock sliding-window machinery and its Gate-1 grep — The Threads now _owns_ continuity as a feature, so suppression-by-gate is redundant.

**Phase W-4 — Personalization loop & consolidation**
- Add the **"Saved This Week"** reader input (a lightweight state field) feeding The Letter and The Threads — the true daily→weekly bridge (depends on the daily save-for-later, Stream 2).
- Use **synthesis-by-juxtaposition** in World and the Long Read: 2–4 **attributed** conflicting excerpts in sequence; the arrangement carries the meaning.
- Collapse the v8.13→v8.34 patch-stack into **one clean editorial charter** and delete the retired gates (§5).

**Weekly also-carried from List 1 (fold into the phases above):** editor's letter (W1→W-1), propagate synthesis (W2 intent→W-3), continuity (W5→W-2), service layer (W6→W-2), daily bridge (W7→W-4), Issue-in-Numbers assertion (W9 reframed→markup gate).

---

### STREAM 2 — THE DAILY (bugs → structure → content → sources)

**Tier D-1 — bugs & fast wins (do first; small, real)**
- **Fix the dead significance push** — `functions/daily/notify.js:pickSignificant()` reads `state.top_catches` (no longer emitted); point it at `state.top20`. Restores the daily's only notification.
- **Reconcile cadence** — honour `config.cadence_hours` as a real skip-gate, or delete it and fix OPERATIONS.md ("3h" → the real 10-min cron).
- **Render `source_count`** — it's computed, drives ranking, and is shipped in `publicItem` but never displayed. Add a "◆ N sources" chip in `catchEl` when `source_count ≥ 2`. Near-free trust+importance cue. _(List 2 B-T1a — highest value-per-effort.)_
- **Start here: tappable, voiced, linked; Today & Tonight config-driven** — carry `{title, why, link}` into `start_here` (reuse the lead `why` already computed) and replace the hardcoded `football||film_tv||gaming` gate in `todayAndTonight` with a topic-config flag. _(Merged B4 + B-T1d.)_

**Tier D-2 — the daily-ness structural moves**
- **Per-item read state** — persist opened item ids in localStorage; dim/collapse read cards so the brief visibly shrinks through the day.
- **"What changed since yesterday" on developing items** — persist last-surfaced headline/signal-tier per cluster (extend `story_log` in `score.js`) and render the delta ("was _linked with_ → now _here we go_"), promoted into a small recurring "Still developing" thread. **This is the daily's one content move** — it turns a re-ranked leaderboard into a story you're following. Mechanical v1, no new AI dependency.
- **A genuine "One Big Thing" lead** — promote `headlines[0]` into a distinct lead block (bigger type, `why` always shown, source-count + Developing inline).
- **Save-for-later** — a star/save affordance (localStorage first; KV if cross-device). This is also half the daily→weekly bridge.

**Tier D-3 — the bridge & content depth (investment)**
- **The daily→weekly digest endpoint** — `GET /api/daily/digest?since=7d` reading `story_log`/`items` from D1: what surfaced and _moved_ this week. The weekly consumes this (Stream 1 W-4) so its "already-informed reader" premise runs on real data. **Foundational — schedule before/with weekly Phase W-4.**
- **Consolidate the AI editorial layer first, then extend** (per §2c): merge `picks`/`top20`; then add a **community digest** (what Reddit/HN/Bluesky are arguing about today) and the optional written developing-delta / **football saga** one-liners as distinct, non-redundant passes under the shared spend cap.
- **Skim vs understand** — keep both `hook` (what's new) and `why` (why it matters) on the card, expandable.
- **Football saga tracker + a fixtures/results rail** in the Sport edition (football is the most-weighted live interest but has no continuity structure).
- **Stronger default cross-source dedup** — enable `smartMerge` by default or extend entity-merge beyond football; consider semantic clustering later.
- **Morning / evening framing** — use `generated_at` hour for a morning lead vs an evening "what moved since this morning" recap. _(Merged B11 + B-T2h.)_

**Tier D-4 — polish**
- Client-side search · per-domain "one thing to know" header line · "by the numbers" chip · tap-source-count-to-list-sources · daily cost/quality history log · warmer hook register for `colour`/`discovery` items only · retire the Reddit rotation workaround once the Data API is approved · fix/note the RSS velocity blind spot (constant `rawScore` ⇒ velocity always 0 for RSS; add a cross-feed "burst" signal).

**Daily source expansion — see §Sources below (an implementation work-item).**

---

### STREAM 3 — SPECIAL EDITIONS

The rebuild reinforces List 1's direction: specials should be the rare, sharply-distinct **interruptions** of the anchor, while the picks-style content folds **into** the weekly (the Bookmark rail and Do This Week already absorb it).

- **S1. Resolve the three ghost formats** (Rewind, Season Review, Lookahead never shipped) — fire each once in a defined window or demote to documented-but-dormant.
- **S2. Cut/fold Lookahead into the weekly** — overlaps the weekly's Release Radar + On the Radar. Reinforced by the rebuild.
- **S3. Enforce the reader-invisibility (Gate 1A) + fact-provenance passes on the light formats** (the audio-drama Starter Kit leaks second person; a Shortlist cited a suspicious stat).
- **S4. Merge the recommendation cluster to two** — keep **Next**; fold **Shortlist + Starter Kit** into one "Guide" (beginner mode = One-Week Plan, category mode = Lens + Cheat Sheet). Cite the retired Blueprint as precedent.
- **S5. Simplify the trigger stack** — collapse `deep_dive_schedule` into P1/P2/P3, or drop the never-fired P3.
- **S6. Wire hard length ceilings into `validate-issue.py`** (Field Guide ~14.6k, retired WWI DD ~24k — too long for "Sunday with coffee").
- **S7/S8 (polish).** Audit the nine signature moments + removed-components graveyard; reconcile the holiday motion layer with the "paper-and-ink, JS-off renders complete" contract.

_Note: the Deep Dive stays the flagship; the weekly's new single **Long Read** does not replace it — the Long Read is a weekly movement, the Deep Dive remains a whole-issue interruption._

---

### CROSS-CUTTING / HOLISTIC

- **H3. Make the weekly the home's front door** — a persistent "This Sunday · The Read" hero above the tabs; daily + specials become feeds underneath.
- **H4. De-jolt the seam** — honour `prefers-color-scheme` on the home so it's continuous with the warm-paper issues.
- **H6. Reciprocal cross-stream links** — Brief → "This Sunday's Read"; weekly → "Following up on the week's threads."
- **H7. Split Settings into "Reader" and "Engine"** — give the reader real controls (text size, theme, notification cadence); keep the token-gated pipeline console separate.
- **H8. Auto-generate the archive from a manifest** (sibling to `extract-issue-meta.py`) — kills the stale hand-maintained counts and unlocks search/grouping/read-state.
- **Polish:** "new since your last visit" banner across all three streams · reader typography controls in issues · estimated read time per weekly feature · protect the Sunday delivery slot.

---

## 4. Suggested build order across streams

1. **Daily D-1 bugs** (push, cadence, `source_count`, Start-here) — hours, real, unblocks trust in the daily.
2. **Weekly W-1** (The Letter + kill the aphorism) — highest reader-felt payoff, near-zero risk; moves the quality signal immediately.
3. **Daily D-3 digest endpoint + D-2 save-for-later** — foundational bridge; must exist before weekly W-4.
4. **Weekly W-2** (The Desk + The Threads + Week in Numbers).
5. **Daily D-2 developing-delta + One Big Thing** — the daily's content move.
6. **Weekly W-3** (four-movement spine + Long Read + Caught Up; ~40% length cut; palette trim; gate retirement).
7. **Cross-cutting H3/H4/H6** (weekly as front door, seam, cross-links).
8. **Weekly W-4** (Saved This Week loop; editorial-charter consolidation).
9. **Specials S1–S6**, **Daily D-3 remainder + D-4**, **Cross-cutting H7/H8**, **source expansion** — as capacity allows.

---

## 5. Gate ledger (weekly) — what goes, what stays

**Retire** (folded into structure or the holistic read): per-section closer/aphorism check · entry-pattern-rotation enforcement · deficit-promotion validator · hard-cadence-floor validator · topic-lock sliding-window machinery + its Gate-1 grep · theme-clustering script · the standalone plain-English random-sample check · the observational-only scorer as a bolt-on. Do **not** add List 1's proposed voice-tic gate or Issue-in-Numbers gate.

**Keep exactly three:**
1. **Image-URL verification chain** (real safety — broken images ship otherwise).
2. **Markup contracts** (rendering safety; fold the trivial "stats aren't identical" assertion here).
3. **One holistic editorial-quality read** — replaces the ~8 compliance scripts; judges the single question: _did this issue tell him what the week added up to, and give him one thing to do?_ This is where the old scorer's intent lives, made to matter.

---

## Sources — an implementation work-item (NOT handed to the owner)

The daily source expansion is **implementation work**, not a paste-into-Settings list for the owner. The implementer:
- Adds the new feeds to `functions/daily/feeds.js` (the seeded defaults) and/or seeds them into `DAILY_CONFIG` KV, tagged by `domain` with the suggested weights.
- **Validates each on ingest** — the pipeline already drops dead feeds gracefully and logs `dead:N`; anti-bot 403s that block a browser check typically resolve server-side, so add-and-validate rather than pre-excluding.
- Adds new **subreddits sparingly and as `tier:small`** (the config already had to restructure when 36 subreddit polls tripped Reddit's rate limit).
- Seeds the **Bluesky starter set** (currently zero handles — the single biggest gap), beginning with the verified handles.

**The complete per-domain source list, URLs, weights, verification status, and cautions are in `docs/signal-weekly-redesign-and-daily-sources-2026-07.md` Part C.** Priority order for the implementer:

1. **Core-interest, verified, highest value first** — Juvefc.com, Fabrizio Romano (Bluesky), Get Italian Football News (football); Nintendo Everything, GoNintendo, IGN, PlayStation.Blog (gaming); 17th Shard, Locus (books); DC Rainmaker, Marathon Handbook (fitness); Simon Willison, Import AI (AI).
2. **Thin-domain fills** — Al Jazeera, RTÉ, Belfast Telegraph (world/NI); Good e-Reader, Android Police (tech); Golf.com; /Film, ScreenRant (film/TV); The Rest Is History (history).
3. **Breadth remainder** — the rest of Part C, per domain.
4. **Bluesky** — seed the verified handles, expand after they prove out.

Gap-analysis summary (which domains are thinnest → highest priority): **football, books, fitness, world, NI-local, AI, and Bluesky (zero)** are the priorities; gaming/finance/tech are medium; history/film/golf/lego/travel/music are lower. No new `topic_weights` domain key is needed — every candidate maps onto an existing domain.

---

## What is explicitly out of scope for the implementer

- Do **not** re-introduce retired gates or add new ones (§5).
- Do **not** hand the owner sources to add manually (§Sources).
- Do **not** implement the weekly as an incremental patch on the current 12-section structure — implement the rebuild (Stream 1).
- Preserve wholesale: the high prose floor, fact density, sourcing rigour, the image-integrity chain, the branded section identities (Touchline / Pixel & Byte / Screen & Sound), Down the Rabbit Hole, reading-time badges, and the editorial cover.
