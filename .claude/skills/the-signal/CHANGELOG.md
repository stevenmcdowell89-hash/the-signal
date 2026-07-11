# The Signal — Changelog

8.39.0 — Special editions rationalised (STREAM 3, items S1–S6, from
  `docs/signal-final-recommendations-2026-07.md` § STREAM 3). The weekly rebuild left
  the special formats untouched; this pass resolves the ghost formats, merges the
  recommendation cluster, simplifies the trigger stack, and wires hard length ceilings.
  The Deep Dive stays the flagship; the weekly's single Long Read does NOT replace it.
  Spec (source `editorial-spec.md`) + re-sliced `spec/*.md` + checklist + one validator.
  No new gates beyond the length ceiling (folded into the existing markup/ship gate).

  - **S1 — the three ghost formats resolved (Rewind, Season Review, Lookahead — never
    shipped).** Rewind → **ACTIVE, calendar-scheduled**: its P1 last-Sunday-of-June/December
    window stands; never shipping was a trip-deferral artefact, not a missing trigger.
    Season Review → **ACTIVE, event-scheduled**: fires as a P2 event when a followed season's
    final result is detected; never shipping was a supply gap. Lookahead → **RETIRED/FOLDED**
    (see S2). Each carries an explicit `Status:` marker at the top of its § in the spec.
  - **S2 — Lookahead cut/folded into the weekly.** It overlapped the weekly's Release Radar +
    On the Radar; the rebuild folds forward-looking picks *into* the anchor. Marked
    RETIRED/FOLDED in the format § and in the manual-only-formats note; intent routed to the
    weekly's radar sections + the Colophon Next-Week note. `lookahead` slug stays
    validator-recognised for the two archived drafts.
  - **S3 — Gate 1A (reader-invisibility) + fact-provenance scoped onto the light formats.**
    The audio-drama Starter Kit leaked second person through its One-Week Plan / On-Ramp prose;
    a Shortlist cited an unsourced stat. `compliance-checklist.md` § 1A now names Guide (both
    modes) + Next as in-scope, and a new § "The Guide / Next — light recommendation formats"
    adds the reader-invisibility, fact-provenance (RT-22), and research-bundle checks. 1A stays
    split (reader invisible; Editor first-person allowed, W-1/v8.35).
  - **S4 — recommendation cluster merged to two.** Kept **Next**; folded **Shortlist +
    Starter Kit** into one **Guide** (beginner mode = One-Week Plan; category mode = Lens +
    Cheat Sheet). New § The Guide in the spec; both old §§ retained with FOLDED markers; P3
    pool table + KNOWN_FORMATS updated (`guide` added; `shortlist`/`starter-kit` kept for
    back-compat, marked folded). Precedent cited: the retired Blueprint (v8.22).
  - **S5 — trigger stack simplified: `deep_dive_schedule` collapsed into P1/P2/P3.** The
    standalone quarterly Deep-Dive timer (a `next_due`/`cadence_weeks` state-machine on top of
    the trigger stack) is retired; Deep Dive now fires only via P2 (major launch), P3 (dry-spell
    pool), or manual request. `deep_dive_backlog` is kept as the topic queue; residual
    `deep_dive_schedule` objects are inert.
  - **S6 — hard per-format length ceilings wired into `validate-issue.py`.** New
    `LENGTH_CEILINGS` map + `check_length_ceiling` (a ship FAIL folded into the existing gate,
    not a new script): deep-dive 20k, rewind 15k, season-review 13k, field-guide 12k, weekly
    11k, countdown 11k, versus 10k, lookahead 8k, guide/starter-kit 7.5k, next 7k, shortlist
    6.5k. Formats without a ceiling report OK (never crash). Verified: the ~15k Field Guide and
    the ~24k retired Deep Dive both trip it; the shipping 18.6k Deep Dive passes.
  - **S7/S8 — deferred** (polish): the nine-signature-moments / removed-components-graveyard
    audit and the holiday-motion-vs-JS-off reconciliation were not done this pass.

8.38.0 — Personalization loop, charter consolidation & the THREE-gate ledger (weekly W-4,
  the FINAL phase of the July rebuild, from `docs/signal-final-recommendations-2026-07.md`
  § STREAM 1 Phase W-4 + §5 the Gate Ledger). Ends the weekly rebuild: the daily→weekly
  bridge runs on real data, the patch-stack becomes one charter, and the gate ledger closes
  at exactly three ship-quality gates. Spec + sliced views + checklist + state field +
  one validator assertion; two scripts deleted; JS-off rendering intact.

  - **"Saved This Week" — the daily→weekly bridge (personalization loop).** New lightweight
    `saved_this_week` array in `state/signal-state.json` (shape: `{title, url, domain,
    saved_at, daily_why, saga?}`), populated by the daily save-for-later affordance (D-2),
    consumed READ-ONLY by weekly generation. Documented in `editorial-spec.md` § The
    daily→weekly bridge: weekly generation reads `GET /api/daily/digest?since=7d` (`{surfaced,
    moved, saga_lines}`, D-3) **plus** `saved_this_week` when composing **The Letter** (reads
    `digest.moved` + `digest.saga_lines` + `saved_this_week` for the week's thesis and the
    cross-domain dots) and **The Threads** (matches `saved_this_week` + `digest.saga_lines`
    against `ongoing_stories` to pick and prioritise saga recaps). Enriches, never a hard
    dependency; machinery stays invisible per the Cardinal Rule.
  - **Synthesis-by-juxtaposition** documented as a **prose technique** (no new component):
    2–4 ATTRIBUTED conflicting excerpts placed in sequence, the arrangement carrying the
    meaning, for contested World/Long-Read material (now in Caught Up / the Long Read).
    Attribution mandatory (traces to bundle `opinion` facts); the excerpts must genuinely
    conflict; no connective sentence telling the reader what to conclude. Reuses the existing
    blockquote / `.source-strip` vocabulary. `editorial-spec.md` § Synthesis-by-juxtaposition.
  - **The patch-stack consolidated into ONE Editorial Charter.** New `## Editorial Charter`
    at the top of `editorial-spec.md` (north-star + the standing rules as they NOW are),
    sliced into `spec/global.md § charter`. The v8.13→v8.38 version-by-version narrative is
    removed from `editorial-spec.md`'s top blockquotes and from `SKILL.md`'s L21 patch
    paragraph — it lives in this CHANGELOG only (history preserved, not lost). The living
    spec now reads as one charter, not a patch pile.
  - **THE GATE LEDGER — exactly THREE ship-quality gates (§5).** `compliance-checklist.md`
    now opens with the three-gate ledger table and nothing else ships-blocks:
    1. **Image-URL verification chain** — `validate-issue.py` image-URL HEAD + static
       extension checks **+** `auto-repair-images.py` (duplicate/unbundled/page-URL repair). KEEP.
    2. **Markup contracts** — `validate-issue.py` structural/placeholder/back-link/markup +
       component-variety checks, **now folding in the Issue-in-Numbers stats assertion**
       (`check_issue_in_numbers_stats`: stats aren't all identical / aren't just the issue
       number — the 13/13/13/13 placeholder defect; a lightweight markup-safety assertion,
       NOT a new script). KEEP.
    3. **One holistic editorial-quality read** — the Phase 9.5 reading pass, reframed from
       observational scorer to **the third gate** (blocking-ish: a north-star NO is a repair
       target within the 3-round budget; Phase 10 still always publishes). Judges the single
       question: *did this issue tell him what the week added up to, and give him one thing
       to do?* Replaces the ~8 compliance scripts; absorbs the prose-rhythm, theme-clustering,
       topic-lock, plain-English, and scorer intents.
  - **`check-prose-rhythm.py` and `visual-smoke-test.py` DELETED**, phase invocations removed
    (SKILL.md Phase 7.75 + 7.8, the CI workflow, the gate-discipline list). Prose-rhythm's
    "paragraph wall" intent → gate 3 (the holistic read). Visual-smoke-test's image-safety
    intent (old D3/D6/D7) → gate 1 (`validate-issue.py` extension check + `auto-repair-images.py`
    dedup, which is self-contained); its holiday-chrome intent (old D1/D2/D4/D5) → gate 2
    (`validate-issue.py` holiday activation/components + Gate-1E greps + the stitcher override).
  - **Upstream production aids, explicitly NOT ship gates:** `validate-research-bundle.py`
    (anti-fabrication / sourcing rigour — preserved wholesale) and `validate-chapter-plan.py`'s
    remaining structural checks. They gate the bundle / plan, not the shipped issue.
  - Preserved wholesale per the out-of-scope section: prose floor, fact density, sourcing
    rigour, the image-integrity chain, branded identities, Down the Rabbit Hole, reading-time
    badges, editorial cover. Did NOT add List 1's voice-tic or Issue-in-Numbers standalone gates.

8.37.0 — The spine & the Long Read (weekly W-3, from `docs/signal-final-recommendations-2026-07.md`
  § STREAM 1 Phase W-3). Reorganises the weekly into a four-movement spine, cuts length
  ~40%, trims the component palette to a tight ~12, and retires three gates. Spec +
  sliced views + checklist + schema + one validator relaxation + new component-contract +
  CSS; two scripts deleted; JS-off rendering intact.

  - **Four-movement architecture** (`editorial-spec.md` § Section Structure → new
    "Four-Movement Architecture", + § The Week, Composed / § Caught Up / § The Long Read;
    re-sliced `spec/weekly.md`; `compliance-checklist.md` Coverage; `sections.md`):
    **I THE OPEN** (The Letter → The Week, Composed → The Week in Numbers → **Caught Up**,
    an 8-line non-expandable digest) · **II THE LONG READ** (exactly ONE deep anchor,
    rotating subject, `08-anchor-piece` slot — absorbs the old Saga / Deep-Dive-lite /
    evergreen-feature impulses) · **III THE ROUNDS** (Touchline, Pixel & Byte, Screen &
    Sound + a Bookmark books rail, The Desk) · **IV THE CLOSE** (The Threads → Down the
    Rabbit Hole → On the Radar → Do This Week → Colophon; ends on a verb + a human line).
    Branded identities kept; the Long Shelf is retired (its on-ramp job → The Week,
    Composed; wildcards → The Letter / the Long Read).
  - **Considered-piece-in-every-section backbone RETIRED.** The single Long Read carries
    the deep work; rounds carry the week's news at the depth the material earns.
    `validate-chapter-plan.py`'s `check_section_shape` no longer hard-fails a round that
    lacks a Lead/yield (piece well-formedness + the Catch-Up no-namedrops rule still
    enforced). `chapter-plan-schema.md` `pieces` description + `compliance-checklist.md`
    1G updated.
  - **Caught Up (8-line cap) added; the breadth-safety-net-in-every-section rule retired.**
    Caught Up discharges completeness up front, so rounds no longer carry safety-net
    headlines. New `.caught-up` contract + CSS.
  - **The Semafor "The case against" callout** added — `.case-against` component
    (`component-contracts.md` + CSS `15b-open-argument.css`), a sourced counter-argument
    box available where a section carries a real argument.
  - **Length cut ~40% → ~6,000–9,000-word target** (was "~20–30 pages"), and the
    **component palette trimmed to a tight ~12** (Angle, Pull quote, Stats row, Did You
    Know, Split layout, Image, Also cards, Rating dots, Category dot, Results strip,
    Read-next, The case against). The rest marked removed inline in § Component Quick
    Reference (no graveyard file; CSS retained for special editions).
  - **Three gates retired:** `check-topic-lock.py` (topic-lock sliding-window) **deleted**
    + its Gate-1 grep removed — `ongoing_stories` now feeds ONLY The Threads; the
    suppression role is intentionally dropped in favour of the continuity recap.
    `check-theme-clustering.py` **deleted**. The standalone plain-English random-sample
    **weekly** reading pass retired (folded into the holistic read arriving in W-4; the
    Deep Dive / literary-special reading pass is unchanged). All phase-pipeline
    invocations removed from `SKILL.md`; `quality-rubric.md` note updated.
  - Preserved wholesale: prose floor, fact density, sourcing rigour
    (`validate-research-bundle`), the image-integrity chain (`validate-issue` image checks
    + `auto-repair-images`), branded identities, Down the Rabbit Hole, reading-time badges,
    the editorial cover, and JS-off rendering.

8.36.0 — Service & continuity (weekly W-2, from `docs/signal-final-recommendations-2026-07.md`
  § STREAM 1 Phase W-2). Restores the service layer and stands up a reader-facing
  continuity engine, and RETIRES two planner validators (per the §5 gate ledger).
  Spec + new template-parts + CSS + two script-rule removals; JS-off rendering intact.

  - **The Desk — the restored service department** (`editorial-spec.md` § The Desk +
    Fixed/Rotating + Cadence Table, `sections.md`, `spec/weekly.md`, `component-contracts.md`).
    Groups four rotating **service columns** — **The Session** (fitness), **The Ledger**
    (money — rebrand of "Money"), **The Itinerary** (travel/parks/NI — rebrand of "Places"),
    **The Toolkit** (tech) — of which **1–2 run per issue**, chosen by which domain is most
    overdue *and* has real, actionable service news. **Each column closes on a mandatory
    "Do This Week" pin** (`.do-this-week` > `.dtw-label`/`.dtw-action`/`.dtw-why`): one
    concrete do-it-this-week action, the why attached, the selection criterion stated — not
    vibes. New template-part `13a-the-desk.html` (the four columns, each closing on the pin;
    also referenced from `14-session.html`); CSS in new `15a-service-continuity.css`
    (section-accent-inheriting pin) + a cross-ref note in `12-section-session.css`. The
    Ledger/Itinerary rebrand is reader-facing — CSS classes `.ledger-section`/`.itinerary-section`
    and tokens already existed; state keys stay `the_money`/`the_places`.
  - **The Threads — the continuity engine** (`editorial-spec.md` § The Threads,
    `component-contracts.md`, new template-part `15a-the-threads.html`, CSS `15a-service-continuity.css`).
    A fixed reader-facing "previously on…" section off `ongoing_stories`, extended beyond
    World to named sagas across all domains, plus the reader's life-threads (`training_phase`,
    `upcoming_trips`). **`ongoing_stories` is now DUAL-USE:** the topic-lock suppression
    backstop (`check-topic-lock.py`) and the existing Ongoing-tracker box are unchanged; The
    Threads additionally surfaces the same records. It is a recap, not a Lead — no "Do This
    Week" pin.
  - **The Week in Numbers — personal stat strip** (`editorial-spec.md` § The Week in Numbers,
    `sections.md`, `component-contracts.md`, new template-part `15b-week-in-numbers.html`, CSS
    `15a-service-continuity.css`). A small strip near the top: Garmin miles + training block
    (`training_phase`), FPL rank, the Juventus result, one money number from The Ledger — the
    spec states each number's source. Reuses `.stat-bar`/`.stat`; kept distinct from the
    Colophon's Issue-in-Numbers (both ship, never merge).
  - **Retired: hard-cadence-floor (old rule 7) + deficit-promotion (old rule 8)** in
    `scripts/validate-chapter-plan.py` — the two `check_rotating_cadence` rules, the roster
    cadence map, the state-resolution helper, the `deficit_override_reason` escape hatch, and
    their inline tests are all removed (53/53 remaining tests pass; the other rules untouched).
    Compliance-checklist §§ 1L/1M and the spec's Selection Rules replace them with a single
    **editorial checklist line, not a gate**: *each domain surfaces at least monthly.* The
    Threads now owns continuity, so a quiet domain no longer needs a forced-include gate.

8.35.0 — Voice & the person (weekly W-1, from `docs/signal-final-recommendations-2026-07.md`
  § STREAM 1 Phase W-1). Puts a person in the personal magazine and kills the recurring
  voice-tic at the source. No new gate or validator — this phase RETIRES checks (per the
  §5 gate-ledger direction). All changes are spec + compliance-checklist + the weekly
  foreword template; the three surviving script gates are untouched.

  - **The Letter replaces the author-less Foreword** (`editorial-spec.md` § The Letter,
    `spec/weekly.md`, `sections.md`, `assets/template-parts/05-foreword.html`). The weekly
    opens on a signed editor's letter: a named **Editor** in the first person ("I") states
    the week's thesis and connects the dots across domains (~120–200 words, "— The Editor").
    Same `foreword` chapter_id and `.foreword` markup/drop-cap, renamed and re-voiced; the
    navigator card reads "The Letter". Added `.foreword .letter-signoff` CSS (a `<div>`, so it
    escapes the per-paragraph drop-cap). Specials keep their own Foreword — weekly-only change.
  - **Gate 1A split** (`compliance-checklist.md` § 1A; Cardinal Rule in `editorial-spec.md`
    + `spec/global.md`). 1A(i) keeps the *reader* invisible (no "you"/"your son"/profile
    callbacks); 1A(ii) explicitly PERMITS the Editor's first-person voice. The rule is now
    "no second-person reader address", never "no first person". No script enforces 1A (it is
    a manual reading pass), so the split is spec-only.
  - **Per-section aphorism/closer tic killed structurally** (§ Editorial Voice in both
    `editorial-spec.md` and `spec/global.md`; component palette in `editorial-spec.md` +
    `spec/weekly.md`). Sections need not "land on a line"; at most ONE genuine aphorism per
    issue. The Angle box may never be reprinted as a pull-quote. No gate added — the tic is
    removed by removing the requirement, per List 1 W3's "method dropped, goal kept".
  - **Two checklist checks retired:** the per-section closer/aphorism expectation and the
    **entry-pattern-rotation** rule. Entry patterns (`.entry-stat`/`.entry-quote`/`.entry-bullets`/
    `.entry-question`/prose) are now a palette to reach for when the material fits, not a forced
    rota. Removed the Gate 2 "Entry pattern rotation" checklist item and the mandate from
    `editorial-spec.md` + `spec/weekly.md`.
  - **"Daily carried the facts, here's the layer"** documented as the STANDARD opener for any
    live-news section (§ Article Structure in `editorial-spec.md` + `spec/global.md`), with the
    machinery kept invisible in prose (never narrate "the daily carried X" / "you already know").

8.34.0 — Weekly refocus (a scope/spine change, not a feature). The daily brief now
  reliably owns week-in-the-loop catch-up, so the weekly is reframed to add the layer
  time gives — synthesis across the week, and roundups that combine items that arrived
  piecemeal — for a reader who arrives already informed. Three edits, all by adjusting
  existing principles and one existing gate (no new rule, no new script — per the
  anti-accretion meta-rule):

  - **Identity** (`editorial-spec.md` § Identity) names the division: the daily owns the
    week's catch-up; the weekly's news job is no longer to report what happened but to add
    synthesis and combined-picture roundups, alongside the evergreen / recommendations /
    discovery it already does.
  - **Section spine inverted** (§ Article Structure + § Fixed vs Rotating + § Key Rules →
    Section Rules). The mandatory element of a fixed section is now the **considered piece**
    (synthesis, a roundup with a *named* layer, an angle, or a feature); the Catch-Up drops
    to **optional grounding context**, never exhaustive coverage. A fixed section with only
    catch-up to offer **yields** that week (it's the daily's job) rather than running a
    roundup to fill the slot — the Toolkit's existing yield principle generalised to every
    fixed section.
  - **Two-factor Lead test reference point moved** (§ Article Structure). Factor 1 (did it
    move this week) is unchanged. Factor 2 now asks whether the piece adds the layer the
    daily couldn't — the week's arc tied together, or the combined picture across separate
    items — instead of "beat the BBC headline." Kept profile-invisible per the Cardinal
    Rule; "inventing an angle to fill the slot is never the answer" and "padding a thin
    topic is banned" preserved verbatim.

  - `scripts/validate-chapter-plan.py` — `check_section_shape` adjusted (no new script): it
    now requires a considered piece (a `lead`) OR a `yield_reason`, and **hard-fails a
    section that offers only a Catch-Up roundup** (it must yield). A bare considered piece
    with no Catch-Up now passes. Docstring, header comment, and inline tests updated; the
    two inverted cases flipped and a catch-up-with-yield_reason case added (60/60 pass).
  - Propagated into the sliced views (`references/spec/global.md`, `weekly.md`, and the
    weekly-overview line in `formats.md`) by hand rather than re-running `slice-spec.sh`,
    because `specials.md`/`formats.md` carry v8.31 content not present in `editorial-spec.md`
    that a full re-slice would clobber (pre-existing drift, flagged for separate repair).
  - Aligned the coupled rule-statements that the gate enforces so they don't contradict it:
    `references/chapter-plan-schema.md`, `references/pre-flight.md` (RT-18), and
    `references/compliance-checklist.md` (1G). Per-section structure lines in
    `references/sections.md` reframed to the considered-piece backbone.
  - Untouched: all voice/craft (Cardinal Rule, Lens-not-Filter, Borrowed-angles, plain-
    English gate + trope lists), research machinery, the quality rubric/scorer, all
    compliance gates/scripts and the Step-Zero model gate, Release Radar, all specials,
    the reader profile, taste rules, and the visual/imagery/markup contracts.

8.33.0 — Enforced the "Return to The Signal" back-link button. The fixed top-left
  pill that returns the reader to the archive index was added to the stitch pipeline
  in v8.22.15 (injected after `<body>`), but its presence was never *verified* — not
  by the stitcher's own post-write checks, not by the `validate-issue.py` gate. So any
  issue assembled through a path that skipped or bypassed that single injection step
  shipped without the button, and nothing caught it. Three issues had silently lost it
  (`signal_next_2026-05-31`, `signal_weekly_2026-06-01`, `signal_weekly_2026-06-07`).
  No new gate script — the existing validator and stitcher were extended (per the
  no-accretion meta-rule).

  - `scripts/validate-issue.py` — new universal `check_back_link()` gate (runs for
    every format, alongside `check_structure`). Hard-fails if the `<!-- the-signal:back -->`
    marker is absent, if there's no `.signal-back-to-archive` anchor in the DOM, or if
    that anchor's `href` isn't `../` (the archive index). Asserts both marker and anchor
    so a half-present block also fails. The button's presence is now a hard ship
    requirement independent of how the HTML was assembled.
  - `scripts/stitch-issue.sh` — the post-write verification block now asserts the back
    link landed (marker + `signal-back-to-archive` anchor), turning a silent injection
    miss into a hard stitch failure.
  - `references/compliance-checklist.md` — documented the back link in the mechanized
    coverage list and added a Gate 2 → Technical item pointing at the `back-link` gate.
  - **Retrofit:** injected the back link into the three issues that had shipped without
    it. All 24 archived issues now carry it exactly once, placed right after `<body>`.

8.32.0 — Visual fixes surfaced by a Starter-Kit test run (TV for a 10-year-old who'd
  finished all Dragon Ball and all Star Wars). CSS + visual-contract only; no gate, no
  editorial/narrative-rule changes (those were considered and deliberately left out —
  these fixes are scoped to visuals).

  - **`.pick` layout (CSS).** `assets/css/32-special-format-flair.css` — the pick
    component was a rigid two-column grid (`14rem 1fr`), which stretched the image
    column to the full row height: a short image beside a tall body left a dead empty
    strip ("empty half page"), and a pick with no image reserved 14rem of empty space
    and squashed the text. Replaced with a **float layout** — the lead media floats
    (left, right on alternating picks) and the body wraps beside it then reflows to full
    width below; `.pick::after` clearfix contains it; `.pick-stats` gets a BFC so its
    bordered box sits cleanly beside the float; narrow-width rule stacks the image on top.
    Fixes both bugs and is robust to a missing image. Affects every `.pick` format
    (Starter Kit, Shortlist, Next).
  - **`.bignum-row` responsive (CSS).** `assets/css/29-special-callouts.css` — added a
    two-up (then one-up) narrow-width fallback so 3–4 big-number rows don't squash.
  - **Per-pick image coverage.** `spec/formats.md` starter-kit + SKILL.md Phase 3a:
    every Essentials pick must carry a real, sourced image; research must find one per
    named title (the test bundle had art for only 3 of 6 picks).
  - **`.pick` markup contract.** `references/component-contracts.md` — added the
    cross-format `.pick` contract: figure-wrapped `.pick-img` (no bare `<img>`), documents
    the float behavior.

8.31.0 — Enforced visual-component variety for non-holiday special editions.
  Per-format visual richness was never an enforced rule — only soft "use 8-14
  component types" guidance in formats.md, a manual checklist item, and an
  observational quality score that never blocks. The one place "this format must
  actually contain these components" was hard-enforced was `check_holiday_components`
  in `validate-issue.py`, and it covered only the two holiday formats. So a special
  could ship as a plain page and pass every gate, and the special-edition Starter
  Kit had drifted far thinner than the beloved old Starter Kits (audio-dramas #4,
  switch2-coop #7). The holiday formats are excellent and were left untouched.

  - `scripts/validate-issue.py` — new `check_special_component_variety()` gate
    (parallels `check_holiday_components`): counts distinct presentational component
    GROUPS in the rendered body (via `body_text_only`, immune to the inlined CSS
    bundle) and hard-fails a non-holiday special below a per-format floor
    (deep-dive/rewind/starter-kit = 9; versus/season-review/shortlist/lookahead/next
    = 7 — guidance lower bound minus 1). Scaffold/animation/modifier classes are
    excluded; a component counts once. Allow-list + floor are single dicts, tunable.
  - `scripts/validate-issue.py` — fixed a pre-existing bug in `SPECIAL_FORMATS`:
    added live slugs `lookahead` and `next` (a `lookahead` issue previously died at
    "unknown format") and removed retired `blueprint`.
  - `assets/css/32-special-format-flair.css` — Starter Kit enrichment: two new
    distinctive components, `.sk-mistake` (Common Mistakes callout list with ringed ×
    badge + `.sk-mistake-fix` line) and `.sk-takeaway` (single-line conviction band),
    and accent changed off the low-contrast `--bone-soft` to warm `--accent-tan`.
  - Docs (visual portions only — no written-content rules touched): `references/spec/
    formats.md` (Starter Kit kit + gated-floor note), `references/spec/specials.md`
    (SK flair + the cross-format floor table), `references/component-contracts.md`
    (HTML contracts for `.sk-mistake` / `.sk-takeaway`), `references/compliance-
    checklist.md` (variety item → mechanized pointer), `SKILL.md` (Phase 7.6 now lists
    the variety check).
  Verified: the two shipped Deep Dives PASS (12 and 10 ≥ floor 9); a stripped
  plain-page special FAILS; a Starter Kit reaches 9 with the documented kit and fails
  at 7; the old `.mag`-template Starter Kits auto-detect as weekly and are not gated;
  holiday issues are exempt. No shipped non-holiday special regresses.

8.30.0 — Deliver, don't gesture: filler, hedged answers, the dropped Release Radar.
  A third no-publish test weekly (1 June 2026, all gates green) read "a good bit
  better" but surfaced three delivery failures. Fixed at source, spec-only (no
  issue regeneration), no new scripts:

  A — Deliver, don't gesture (two failures, one root cause: the magazine
  *performs* a quality instead of having it). (1) Hollow connective sentences —
  "that framing is what makes this a discovery rather than a headline" — that
  comment on the content instead of adding to it. (2) The hedged answer — the
  Session "how many sets?" lead had the numbers (67 studies, ~0.24%/set, the
  inverted-U) then dissolved the takeaway into "somewhere in the region of ten
  to twenty…". The principle ("every sentence adds information"; "answer the
  posed question, never left hanging") already existed; what was missing was
  REACH — the plain-English reading-pass was Deep-Dive-only. Fixes:
  - SKILL.md Phase 7 plain-English spot check: scope Deep-Dive-only -> ALL
    formats (weeklies now get the same honest read). One-line scope change.
  - editorial-spec trope list (+ SKILL.md): name the hollow connective sentence
    and the hedged answer as explicit failures; rescoped as all-format guidance.
  - Answer-the-question rule sharpened: LAND the answer (state the number/range);
    caveats go in an aside, never wrapped around the answer.
  - pre-flight self-audit folded into existing RTs (no new RT); quality-rubric
    notes both score down on voice. No new script (a regex can't judge hollowness).

  B — Release Radar reinstated as first-class and enforced. It was real in the
  spec but only "tail content" of Screen & Sound with NO schema field and NO
  validator check, so it silently dropped from the test issue. Now:
  - chapter-plan-schema.md: a required weekly `release_radar` chapter with a
    `radar_items` array (15-20 entries, {title,category,date,status,link,note},
    >=4 categories), reusing the v8.29 status tag; rendered after screen_sound.
  - validate-chapter-plan.py: check_release_radar() (mirrors check_long_shelf_items)
    + a weekly-presence check (a weekly with no release_radar hard-fails) + 4 inline
    tests; test harness auto-injects a valid radar into weekly fixtures (59/59 green).
  - editorial-spec § Section Rules + sections.md: elevated from "tail content" to a
    mandatory enforced element; On the Radar stays events-only.
  - SKILL.md researcher/planner briefs + component-contracts.md radar markup contract.
  Reuses the existing validator — no new gate script.

8.29.0 — Fact provenance moved upstream: close the prose trust holes.
  v8.28 named the failure (the Monaco "Norris on pole" result asserted before
  qualifying; a State-of-Play showcase written as "delivered" before it aired)
  but left the "has this happened / who said it?" judgment where it kept
  leaking: in the writer's head, mid-sentence, checked against the issue's
  cover date. Two structural root causes, fixed at source — NOT a new gate
  (the § Key Rules meta-rule forbids accreting scripts; the two existing gates
  were extended instead):

  CAUSE 1 — the judgment lived downstream, in the prose. Fix: facts are now
  STRUCTURED RECORDS in research-bundle.json, decided upstream by the
  researcher while the sources are open:
    { "claim", "status": "happened|upcoming", "date", "source_url",
      "type": "fact|opinion", "speaker"+"quote" (iff opinion) }
  The writer renders the pre-decided `status` tag (upcoming ⇒ forthcoming,
  never past tense) rather than re-judging it. The planner copies the records
  into each chapter's `key_facts` (now string OR structured, back-compatible).

  CAUSE 2 — the temporal gate compared against the issue's COVER date, so an
  event between the pipeline run and the cover Sunday looked safely past. Fix:
  re-anchor on the RUN date (when facts were knowable).

  Enforcement (existing gates extended, no new script):
  - `validate-research-bundle.py` — new `facts[]` block + `--run-date`:
    rejects a fact missing claim/status/date/source_url; a `status:"happened"`
    fact dated AFTER the run date (can't have happened yet); a `type:"opinion"`
    fact with no real speaker+quote (you may only NAME a commentator when the
    real words are in the bundle — otherwise the borrowed angle is voiced
    unattributed in our own voice).
  - `check-release-dates.sh` — takes a run-date (defaults to today) and the
    bundle path; anchors the result check on the run date and lists every
    `status:"upcoming"` fact so the agent confirms the prose renders it as
    forthcoming.
  - `validate-chapter-plan.py` — validates structured `key_facts` records
    (shape + status/date/source + opinion provenance); bare strings still pass.
  Spec: global.md gains a "Fact provenance chain" (the prose analog of the
  image verification chain) + run-date anchoring in §Content Standards and the
  "naming needs a quote" rule in §Borrowed angles; SKILL.md Phase 3a/3b/7.5,
  chapter-plan-schema, pre-flight RT-22, and compliance-checklist 1B updated.

8.28.0 — Substance & trust: stop the magazine writing confident fluff.
  v8.27 fixed *what* gets covered; a no-publish test weekly (7 June 2026)
  then read as "a lot of editorialising, telling me little" — invented
  angles (a Screen & Sound essay on "the year Star Wars went quiet" that
  said nothing), padding (3000 words for a 30-second idea), generic
  catch-up that named a beat without the fact ("Juventus transfer latest"),
  an empty Shelf (placeholder titles), and — worst — a fabricated result:
  the Monaco companion asserted "Norris on pole" for qualifying that hadn't
  happened, then built two paragraphs of analysis on it.

  Diagnosed to TWO root causes and fixed at source (not patched per-symptom):

  CAUSE 1 — structure demanded generation. A lead-per-section + word floors
  made the writer invent angles and pad. Fixes:
  - The **Lead is now optional**: a section may be pure Catch-Up (facts) with
    no Lead. `check_section_shape` allows 0 leads; a companion requires a lead;
    a bare lead with no second element still fails; an empty section fails.
  - **Word floors relaxed** to sanity minimums (lead 150 / companion 120, were
    300/200) — length follows the material; padding to a band is banned.
  - New Cardinal rule **"Borrowed angles, our voice"**: the magazine never
    invents an opinion/thesis/counterargument; it borrows ones real
    commentators hold (from research) and voices them as its own — no quoting,
    no attribution duty, no robotic "X said Y". Not everything needs an angle
    (gaming releases, the cut-piece "state the studies" form are better as
    plain facts); a posed question is answered from sources. Replaces the
    "Opinions mandatory" line and the per-section "culture critic / reviewer"
    instructions.
  - Fallback hierarchy: sourced angle → state the facts → yield. Catch-Up items
    must carry a real specific fact or be cut. Recommendation sections with no
    real items yield rather than invent.

  CAUSE 2 — nothing verified inbound facts (images were a fortress, facts wide
  open). Fixes:
  - The writer states only facts in the research bundle (RT-22 already; now
    reinforced in § Content Standards + Gate 1B).
  - **Temporal check**: a stated result/fixture/standing must have happened by
    the issue date and trace to a source — `check-release-dates.sh` extended
    from media-only to results/fixtures (+ takes an issue-date arg); Gate 1B
    gains a hard "no result that hasn't happened" check. Closes the Monaco class.

  PROCESS — the test issue was starved because the researcher was spawned as a
  read-only `Explore` agent that couldn't write the bundle, so its real
  findings were lost and rebuilt lossily from a summary. Fix: researcher spawns
  as a **writable `general-purpose`** agent; new Phase 3a-guard verifies the
  bundle file exists and re-runs research rather than hand-rebuilding; the
  researcher brief now demands specific facts + real viewpoints, not beat-labels.

  SPECIALS — the Cardinal rule reaches every format; the interpretive chapters
  reconciled: Deep Dive "The Argument", Rewind "The Throughline", Versus "The
  Verdict" must reflect a frame real coverage supports, not an invented thesis.
  The Field Guide was already compliant and is the template.

  CONSOLIDATION (governance meta-rule — every change leaves the corpus the same
  size or smaller): the one Cardinal rule replaced four per-section opinion
  blurbs and collapsed the Gate 2 banned-phrase list; the new substance rules
  folded into RT-18/RT-22 rather than adding RTs. Net line count across
  editorial-spec + references + pre-flight held at/below the pre-v8.28 baseline
  (3481 lines). Validator: 50/50.

  Files: `references/editorial-spec.md` (+ re-slice), `references/sections.md`,
  `references/pre-flight.md`, `references/compliance-checklist.md`,
  `references/quality-rubric.md`, `references/chapter-plan-schema.md`,
  `scripts/validate-chapter-plan.py` (+ tests), `scripts/check-release-dates.sh`,
  `SKILL.md`. No CSS/template changes; no new gate scripts.

8.27.0 — Editorial reset: a reduction, not a feature. The magazine had
  drifted from its purpose — "save the reader from trawling the feeds:
  catch what he missed and tell him what he's interested in." An audit of
  five May weeklies found ~35–45% of a typical issue was recap of the
  already-known (Starmer led the World section three weeks running, each a
  holding pattern), the discovery/evergreen half was genuinely good, and
  the damage was concentrated in the forced fixed Leads and a hollowed-out
  body. Root causes: the v8.15 mandatory two-deep-anchor Lead + Companion
  spent the section budget on depth and starved the catch-up roundup; a
  v8.x over-correction made UK politics "Lead-grade, cover fully" (it had
  originally been banned as noise); the roster had grown to 14 rotating
  sections by splitting, so one interest could flood an issue; and
  governance was patch-on-patch (two reactive rules added the same day the
  bad issue shipped). This release changes the few settings that force the
  recap and folds the patches into durable principles. It does NOT touch
  the ~40% that works, adds no new gate scripts, and leaves the template /
  CSS / visual system and the formats roster alone.

  Four moves:

  1. The Lead earns its slot by reward-per-attention, not "most important".
     Two-factor test (both required): did it move this week (a datable
     development, not a holding pattern) AND can we add something beyond the
     headline he already has. Promoted to a Cardinal-tier rule in
     editorial-spec § Key Rules ("What to Lead With") and § Article
     Structure. Search Group 1 no longer auto-promotes any story (incl. UK
     politics) to a Lead-1 candidate — it must pass the test like anything
     else. The topic-lock script + development test remain the mechanical
     backstop.

  2. UK / national politics back to OUT BY DEFAULT. In only for a genuine
     landscape shift (an election result that changes the picture, a
     government actually falling) that also passes the two-factor test;
     reshuffles, leadership will-he-won't-he, resignation-call counts,
     Stormont process, polling chatter are out (a one-line safety-net
     mention at most). The "Lead-grade — cover fully" framing is deleted.

  3. Section shape is now Lead + Catch-Up (retires the v8.15 two-anchor
     mandate). One angled Lead + a substantive Catch-Up roundup of missable
     domain news (every item what/why/link — no bare namedrops) plus
     one-line safety-net headlines so demoting a known story out of the
     Lead never drops it. The Companion becomes optional. Sections may run
     short or yield. Enforced by the rewritten `check_section_shape` in
     `validate-chapter-plan.py` (Lead + a second substantive element:
     Catch-Up roundup, Companion, or explicit yield_reason; namedrop
     Catch-Up items hard-fail) and Gate 1G / Gate 2 in the checklist. No
     hard word target any more — issues flex to the news.

  4. Roster redesigned from the reader's interest-domains (one home per
     domain), collapsing 14 rotating sections to 5 + 1 trigger-driven:
       - Fixed: World · Pixel & Byte (gaming + LEGO) · The Toolkit (tech &
         tools — fixed-but-yields, full gap-coverage on return) · The
         Touchline · Screen & Sound · The Session (absorbs Workshop + Lab).
       - Rotating (pick 2-3, was 3-4): The Shelf · This Week in History ·
         Listening (Listen + Channel) · Money (Long Game + Wallet + Ledger)
         · Places (Itinerary + Local).
       - The Saga is now TRIGGER-DRIVEN, not on a 6-week clock: it runs on a
         public peg the researcher finds (a finale aired, a new book/season
         in a followed series, an author AMA) or a private peg the reader
         supplies (`currently_reading` / `currently_watching` in state, or a
         manual trigger). Generalised principle written into the spec:
         sections that depend on private context are reader-triggerable, not
         calendar-driven (the same reason Next and Lookahead are
         manual-only).

  Governance: the freshness / topic-lock (v8.18→v8.25) / theme-clustering
  (v8.26) patches collapse into one "what to lead with" principle, with a
  meta-rule — when an issue disappoints, adjust the principle, don't bolt on
  another rule or script. A `novelty` dimension is added to the quality
  rubric (Phase 9.5, observational, no new gate) to measure "did the Lead
  tell him something he already knew?" going forward.

  Files: `references/editorial-spec.md` (master; slices regenerated via
  `scripts/slice-spec.sh`), `references/sections.md`,
  `references/chapter-plan-schema.md`, `scripts/validate-chapter-plan.py`
  (+ tests, all 47 pass), `references/compliance-checklist.md`,
  `references/quality-rubric.md`, `state/signal-state.json` (new roster +
  `currently_reading` / `currently_watching`), `SKILL.md`. No CSS/template
  changes; no new scripts.

8.24.0 — Editorial-quality signal: a measured rubric, logged and surfaced.
  Follow-up to 8.23.0. The model-policy rewrite exposed a deeper gap:
  the pipeline has NO quality signal. Every gate (Phases 3b–8) checks
  compliance — markup, dates, image sourcing, performing prose — and a
  clean record proves an issue is *shippable*, not *good*. The cost
  log's zero-retry history was being read as quality evidence; it isn't.
  Compliance and quality are different things, and nothing measured the
  second.

  New: a quality rubric scored every run, logged, and made visible.

  - `references/quality-rubric.md` — five 1–5 dimensions (voice,
    density, structure, opening, throughline) anchored to REAL archive
    examples (the WWI Deep Dive performing essayism; the 24 May weekly's
    structural incoherence; strong openers as the 5-anchors). Scorer
    must always name the weakest dimension + a one-line reason, so the
    log is actionable. Honest caveats baked in: sibling-scorer bias,
    scorer-model-as-instrument, and a required ~monthly human anchor.

  - Phase 9.5 (new) — a DEDICATED scorer agent (not the orchestrator,
    not a writer on the issue) scores the post-repair artifact and emits
    JSON. Observational only — never gates or reverts a publish; Phase
    10's always-publish rule is untouched.

  - `scripts/log-quality.sh` — appends the scorer JSON to
    `state/quality-log.jsonl` (injects ts, computes overall) and
    regenerates the page.

  - `scripts/render-quality-page.py` — bakes the log into a static,
    reader-facing `quality.html` at the repo root. The log lives under
    state/ (excluded from the deployed site by .assetsignore), so the
    page is regenerated at publish time, same pattern as index.html.

  - `quality.html` + a header link from `index.html` ("Editorial
    quality →") — a readable table of every scored issue, score-coloured,
    with a summary strip including AVERAGE BY WRITER MODEL.

  - `scripts/quality-summary.sh` — terminal view (overall, by writer
    model, by dimension, weakest-frequency, --since).

  Why writer_model is stamped on every row: it turns the model-tier
  question 8.23.0 left open ("does a stronger writer actually write a
  better magazine?") from a judgment call into an evidence base that
  accumulates. Seeded with 3 honest backfill scores (WWI Deep Dive 3.8,
  24 May weekly 3.5, 17 May Field Guide 4.2) from sampled prose, flagged
  backfill:true so they read as indicative, not live-pipeline scores.

  Phase 10 publish push list now includes quality.html +
  state/quality-log.jsonl. No template/CSS/pipeline-shape changes to
  issue output.

8.23.0 — Model policy: standardise on Opus 4.8, invert the burden of proof.
  Opus 4.8 (1M context) shipped. Two problems with the old model
  policy surfaced:

  (1) The Step Zero gate (`verify-orchestrator-model.sh`) was an
      EXACT-string pin on `claude-opus-4-7[1m]`. A 4.8 1M session —
      a strictly stronger model — would FAIL the gate and abort the
      pipeline before Phase 0. The gate is meant to stop a *downgrade*
      (the 24 May 2026 harness fallback to Opus 4.6), not forbid an
      upgrade. Fixed: the gate is now an allowlist FLOOR accepting
      both `claude-opus-4-7[1m]` and `claude-opus-4-8[1m]`; append
      newer Opus 1M ids as they ship, never remove the floor.

  (2) The per-role model choices (researcher/writer/repair on
      Sonnet/Haiku) were set to limit cost under a cost-throttled
      orchestrator, justified by the claim "Sonnet performs at the
      same quality as Opus once the planner has done the hard
      thinking." That claim was never tested. The pipeline has NO
      quality signal — only compliance gates. The cost log's
      zero-retry, zero-repair history proves the cheap roles stay
      *compliant*; it says nothing about whether the prose is as
      *good* as a stronger model would write. Compliance and quality
      are different things, and the system is structurally blind to
      the second.

  Burden of proof inverted. New policy: a role keeps a cheaper model
  ONLY if its work is mechanical enough that model strength provably
  cannot affect the output. No LLM role clears that bar — the
  genuinely mechanical work (stitching, validators, image
  substitution) is already deterministic scripts with no model.
  Every subagent role does generation or judgment a stronger model
  could do better, undetectably. So all primaries are now Opus 4.8
  (orchestrator, researcher, planner, writer, repair); Sonnet 4.6 is
  retained as an availability/rate-limit FALLBACK only, never the
  default. Haiku dropped from the chains. Re-run this analysis when
  the next Opus ships rather than inheriting it.

  Changed: `scripts/verify-orchestrator-model.sh` (allowlist floor),
  SKILL.md Step Zero + Model Selection table + rationale + Phase 3a/5/9
  spawn lines + pitfall #1. No template, CSS, or pipeline-shape
  changes — issue output structure is unchanged.

8.11.0 (current — installed version on Claude Code)

8.9.1 — Hype-chapter visual variants (cheap, opt-in).
  Problem: the default special-edition chrome (full-viewport
  chapter gate, coral accent lockdown, paper/ink grounds) is tuned
  for literary formats (Deep Dive, Rewind). On hype chapters
  — Countdown's Top Attractions / Accommodation / Mood Board / Five
  Moments, and Field Guide's The Opening + The Unmissables — the
  same chrome dampens the pages it should amplify.

  New `32-hype-variants.css` adds four CSS-only, opt-in surfaces:
    (A) `.sp-chapter-gate.is-hype` — compact gate (60vh track,
        40vh sticky hold, layers solid by progress 0.08).
    (B) `[data-sp-chapter].is-hype` — narrowly re-permits coral on
        `.sp-number`, `.sp-number-huge`, `.sp-kicker`,
        `.sp-brief-kicker`, `.unmissables .sp-datum-value`, and
        `.why-its-here`. Global accent lockdown otherwise unchanged.
    (C) `.sp-ground-gallery` — third ground type alongside paper/ink,
        neutral slate #1A1E27, legal only on image-first chapters
        (Mood Board primary, optional for Five Moments and Field
        Guide's Opening).
    (D) `.unmissables` / `.unmissable` — Field Guide Unmissables
        pattern. 6–10 picks as full-width editorial beats (NOT
        card grid); per pick: hero image, sensory prose, "Why It's
        Here" coral kicker, mono `<dl>` practical footer (price,
        booking, timing, walk). Drop-cap forbidden on picks.

  No template changes, no JS changes, no new dependencies. Literary
  formats keep the full default chrome. Reduced-motion fallback for
  the compact gate included (~36vh static band). Editorial-spec
  adds a new "Hype-chapter visuals — opt-in modifiers" block after
  the "Hype over homework" principle, listing all four surfaces and
  when to apply them.

8.9.0 — Field Guide realigned as shared hype-and-practical read.
  Field Guide is no longer a phone-in-park reference dump; it is a
  shared Sunday read on a tablet with coffee, 45/55 hype-to-practical
  ratio (acceptable band 40/60 to 50/50), hype front-loaded. Canonical
  section order: Cover → Foreword → The Opening → The Unmissables →
  Quick Orientation → Sections by category → Meanwhile → Footer. The
  Opening is a prose-only atmospheric lead (400–600 words, no lists,
  no prices). The Unmissables is the emotional centrepiece (1,500–
  2,500 words, 6–10 picks, sensory write-up + "Why It's Here" +
  image + small practical footer per pick). Countdown section softened
  so it no longer positions Field Guide as pure-practical dumping
  ground. Compliance checklist's Field Guide block fully rewritten
  (13 new bullets: shared-read framing, Opening present, Unmissables
  promoted to front, section order, ratio check, meal slots, full
  spectrum, multi-venue balance, whole-estate research, voice cues,
  image density, practical detail in prose, DFBguide voice discipline,
  theming callouts). Component contracts add Opening + Unmissables
  rows, reorder to canonical sequence, remove Don't-Miss List row
  (absorbed into Unmissables). No breaking changes to author workflow.

8.8.1 — Whole-estate research rule.
  Editorial-spec addition: before writing any chapter about a
  venue, map the full estate, not just the marquee feature.
  Default searches surface the headline ("Beekse Bergen safari",
  "Center Parcs lodges") and stop there, producing issues that
  undersell the trip. The rule: read the official site's site-map
  / "what's on" / "things to do" pages in full, list every zone,
  every restaurant, every activity, every facility, and make sure
  coverage reflects what the venue actually is. Worked examples
  in spec: Beekse Bergen (safari + Speelland + Safari Resort
  hotel + Lake Beekse Bergen), Center Parcs (lodges + pool
  complex + activities + restaurant village), Disneyland Paris
  (two parks + Disney Village + hotel estate). Compliance
  checklist adds a matching whole-estate research check at
  Gate 2. Applies to every travel format, not just Countdown.

8.8.0 — Countdown reframed around hype, not homework.
  Structural change to the Countdown special edition: the format
  now optimises for anticipation rather than planning. Logistics
  demoted from a standalone chapter to a short coda. Four new
  chapter types introduced — By the Numbers (hype opener after
  Foreword), Top Attractions (or venue-equivalent: safari ranked,
  animal encounters, corners of the resort), Mood Board (dense
  visual-only chapter), Five Moments Worth the Trip (short
  third-person editorial, one image per moment, no first-person
  voice). New canonical order: Cover → Foreword → By the Numbers
  → Event in Depth → Top Attractions → Accommodation → Mood Board
  → Watch/Read/Play → Five Moments Worth the Trip → [day-by-day
  only if supplied] → Before You Go (merged logistics + surprising
  facts) → On the Radar → Footer.

  Three new hard rules govern the format:
  (a) Hype over homework. If a chapter reads as a checklist or
      how-to, it's in the wrong format — content belongs in a
      Field Guide. Total logistics content across the issue
      capped at ~400 words.
  (b) Visuals-first, tiered by chapter type. Narrative chapters
      need 3+ real credited images; Mood Board needs 8–12;
      stat-led and coda chapters need 1+; Five Moments needs one
      per moment. If a chapter can't hit its tier, it's cut or
      reshaped.
  (c) Equal hype weight for multi-venue trips. Every venue gets
      equal hype weight, but the shape of the hype can differ to
      match what each venue is (theme park → rides ranked; safari
      resort → animal encounters ranked). Measured mechanically:
      words per venue and images per venue must sit within 60/40
      across the issue. Rebalance before delivery.

  Compliance checklist updated with nine new Countdown checks
  covering every principle above, including a MECHANICAL
  multi-venue balance check at Gate 2. Chapter-arc mapping
  relaxed from rigid 10 to 9–11 chapters to accommodate the
  new beats. Accommodation chapter positioning updated (mid-issue
  after Top Attractions, no longer adjacent to the removed
  Logistics chapter). No CSS or template changes — this is an
  editorial-layer change only; all existing visual components
  continue to serve the new chapter types.

8.7.3 — Full-viewport cover + accommodation-chapter guardrail +
        visual-features auto-apply audit.
  Three small things, one of them a spec entry only:
  (a) Cover height. The `.cover` base rule was `min-height: 82vh`
      and the mobile override at ≤720px dropped it to `72vh`. Both
      left the first chapter's gate peeking up from below the fold
      at the moment the page loaded — a magazine cover that isn't
      a full page isn't a cover. Bumped to `min-height: 100vh;
      min-height: 100dvh; box-sizing: border-box` on both the
      base rule (21-chrome.css §19B) and the ≤720px override.
      `100dvh` is the dynamic-viewport unit that accounts for the
      mobile URL bar collapsing — the cover stretches to whichever
      window height is actually visible. Verified on 800×1200
      tablet (1.000 ratio) and 412×915 phone (1.000 ratio).
  (b) Accommodation chapter content. The test Countdown labelled
      chapter IV "WONDER HOTEL" in its gate but the actual
      section was a two-park diptych/transition with no hotel
      coverage. This is a research/labelling problem, not a CSS
      problem. Added a new paragraph to editorial-spec.md §The
      Countdown making the rule explicit: a chapter gate that
      names a property is a promise — either do the research
      (400–600 words + 4+ images + a gallery per property) or
      relabel the chapter to what it actually covers. "A diptych
      or transition section is NOT an accommodation chapter."
  (c) Visual-features auto-apply audit. Added the new "Visual
      features — auto-apply guarantee" section to editorial-spec.md
      §Special Editions, enumerating every tier-5 / tier-5.5 /
      tier-6 component and whether it applies automatically
      (CSS/JS), via a class contract, or via markup. Purpose:
      confirm to the author that the features hardened over
      v8.0–8.7 will continue to fire on every future special
      edition without needing to be re-requested.
  Version bump: 8.7.2 → 8.7.3. No breaking changes to author
  markup; existing issues regenerate identically. Save with
  `save_custom_skill` and regenerate the countdown preview.

8.7.2 — Full-length decorative rail + legible ink-ground margin.
  Problem (tablet screenshot on ink-ground chapter):
  (a) The left rail, floated with `min-height: 100%`, only ran
      as tall as its own content (~680px on a 3600px spread),
      leaving a ~2900px gap beneath it. The decorative vertical
      line + chapter spine stopped short of the chapter end.
      Reader feedback: "the left margin is fine to run the
      length of the article — it's decorative."
  (b) The right margin aside, styled as a near-transparent
      paper tint on ink grounds, left the ink-on-paper text
      (kicker, quote, attrib, datum labels) rendering as
      near-black on near-ink — unreadable. Feedback: "colours
      gone, tough to read now."
  Fix:
  (a) Rail switched from float to `position: absolute` with
      `top: 0; bottom: 0; left: 0`, so it always stretches to
      the full spread height regardless of prose length. The
      spread gets `position: relative` to anchor it. Body is
      still `flow-root` with left padding (78px tablet / 58px
      phone) to clear the rail. The margin aside still floats
      right inside the body, so prose continues to reclaim
      width when the margin ends — no regression to v8.7.1.
      Two later gutter rules (ground-level horizontal gutter
      @≤1024px and @≤600px) that re-set `.sp-spread-body`
      padding without a left value were updated to preserve
      rail clearance.
  (b) `.sp-ground-ink .sp-spread-body > .sp-margin` now paints
      a solid paper-tinted background (same `color-mix` recipe
      as legacy paper-backed islands — sidebar, also-card,
      angle-box). Border-left returns to coral. Existing text
      colour inheritance (`--sp-ink-on-paper`, `--sp-mute-paper`)
      is now correct against a paper island, so the whole
      margin reads cleanly on ink-ground chapters.
  Files touched:
    • assets/css/26-special-editorial.css — rail absolute
      positioning at ≤ 980px, ink-ground margin paper-tinted
      background, gutter padding fixes at ≤ 1024px and ≤ 600px.
  Verified on 800px tablet and 412px phone: rail runs full
  spread height (gap ≤ 2px vs spread bottom), margin content
  legible against paper tint, drop-cap and prose clear of rail.
8.7.1 — Reclaim empty margin column + earlier gate reveal.
  Problem (412px phone screenshot, feedback):
  (a) The portrait 3-col spread used CSS grid, so when the margin
      column's content (marginalia quote + datum stats) ended,
      its grid cell kept reserving that tall pink block down to
      the full spread height. The prose column next to it was
      visibly narrower than necessary for the entire tail of
      the chapter — "the third column runs out of content
      early\u2026 if there's a way to then take up that space too so
      we don't get like the screenshot".
  (b) Gate reveal window (v8.7: arc 0.05–0.18, numeral 0.12–0.30,
      title 0.22–0.40, deck 0.40–0.58) still let the fully-black
      panel sit on-screen with no text at the start of the sticky
      hold — "I can have the black background entirely on screen
      with no text".
  Fix:
  (a) Portrait spread rebuilt as a magazine-style float layout.
      `.sp-spread` becomes `display: flow-root` at ≤ 980px. Rail
      floats left (60px tablet / 44px phone). The margin aside is
      reparented via JS to be the first child of `.sp-spread-body`
      and floats right (190px tablet / 128px phone) with
      `shape-outside: margin-box`. Prose flows around both floats
      and reclaims full reading width once the margin ends —
      verified on 412px portrait with 4 000+ px of prose
      width-reclaim beneath an 800px margin block.
  (b) Gate reveal thresholds pulled much earlier: arc 0.00–0.06,
      numeral 0.02–0.10, title 0.06–0.14, deck 0.10–0.20. All
      four layers are fully solid by 20% of the sticky hold, so
      80% of the gate shows the fully-revealed chapter title.
  Files touched:
    • assets/css/26-special-editorial.css — float layout at
      ≤ 980px and ≤ 560px, selectors now target
      `.sp-spread-body > .sp-margin`.
    • assets/css/31-chapter-gate.css — new reveal thresholds.
    • assets/script.js — new Portrait Spread Reparenter IIFE
      inserted before the Universal Chapter Gate controller.
      Listens to DOMContentLoaded, resize (debounced 120ms), and
      the `(max-width: 980px)` MediaQueryList; idempotent.
  Portrait contract preserved: 3-col layout still works down to
  ≈ 380px; nothing is landscape-only.
8.7 — Portrait-native 3-col spread + gate title timing fix.
  Problem (portrait phone + tablet screenshots):
  (a) the three-column `.sp-spread` (rail + prose + marginalia)
      collapsed to a single column at ≤ 980px. This rebuilt the
      chapter body as "stacked rail → full-width prose → full-
      width marginalia". In portrait that made the marginalia
      pull-quote + stats look like an orphaned standalone
      section, and erased the rail's role as chapter-side
      chrome. Reader feedback: "3 column spread just work in
      portrait. no treats in landscape. all we have designed
      must work in portrait".
  (b) Gate title reveal window was too late. Arc faded in at
      progress 0.10–0.30, numeral 0.25–0.55, title 0.45–0.70,
      deck 0.65–0.88 — so at mid-sticky-hold (progress ≈ 0.5)
      the chapter title was still at ≈ 20% opacity. On the
      tablet read this looked like the gate was permanently
      faded, never solid.
  + 26-special-editorial.css: the 980px and 560px media blocks
    no longer stack the spread. Instead, `grid-template-columns`
    becomes `60px 1fr 200px` at ≤ 980px and `44px 1fr 130px`
    at ≤ 560px. The rail keeps its vertical writing-mode and
    rotated spine label. The margin column keeps its pull-quote
    + stats but with compact type (17px quote, 44px datum on
    tablet; 14px quote, 32px datum on phone). On a 412px phone
    the three columns resolve to 44 / 238 / 130 — tight but
    readable, no stack. The foot label (location) is hidden on
    phone to preserve rail width.
  + 31-chapter-gate.css: reveal thresholds compressed. Arc
    0.05–0.18, numeral 0.12–0.30, title 0.22–0.40, deck
    0.40–0.58. By the time the sticky panel is half-way through
    its hold, all four layers are fully solid. Verified on an
    800x1200 viewport: at scroll-progress 0.584, measured
    opacities = arc 1.00 / numeral 1.00 / title 1.00 / deck
    1.00. Matches the reader's "titles should be solid during
    the hold, not still fading" expectation.
  + Standing rule documented: portrait is canonical. No
    component may be landscape-only. Every design decision is
    evaluated portrait-first. The old "stack at 980px" habit
    is retired.
  Net effect: rail + prose + marginalia behave like a magazine
  spread at every width, including 412px portrait phone. Gate
  titles read as solid chapter openers at normal reading pace.

8.6 — Tablet polish after first real tablet read.
  Problem (tablet screenshots, Xiaomi Pad 8 ~800px portrait):
  (a) random white/cream bands appearing BETWEEN chapters
      (between the gate's black panel and the next chapter's
      ground), (b) the full-bleed .sp-pull-break between
      Logistics and Mood Board was painting body cream behind
      a dark pullquote card (isolated black island on cream
      moat), (c) the "— end of chapter N —" signoff stacked
      on top of the v8.5 sticky gate (two separators doing
      the same job), (d) duplicate internal .sp-chapter-chrome
      eyebrows ("Chapter V · feature spread") collided with
      the gate's own title and went off-by-one against it
      (reader perceived as "Efteling cut in two"), (e) arc
      labels "Act I / Act II / Act III / Coda" and chapter
      titles "A Manifesto / Interlude / Facts & Folklore"
      read as pretentious.
  + 31-chapter-gate.css bumped to v8.6 (SEAM CLOSE).
    Track height reduced 160vh → 110vh (100vh sticky hold +
    10vh tail). Track background forced to #0A0E17 so any
    post-release slack is invisible. Critically:
    `section[data-sp-chapter] { display: flow-root }` added
    to establish a block formatting context and contain the
    48px top/bottom margins of .sp-spread / .sp-dash /
    .sp-timeline / etc. that were escaping the section via
    margin-collapse and exposing the body cream between
    sections. Also `.sp-pull-break-wrap { display: flow-root;
    padding: 64px 0; width: 100vw; margin-left: calc(50% -
    50vw) }` so the standalone pull-break between chapters
    sits on its own ground (inherits from the NEXT chapter)
    and the dark card never floats on body cream. This was
    the root cause of the "random white bands".
  + All 10 "— end of chapter N —" signoff markers removed from
    chapter content. The sticky gate is now the sole chapter
    separator.
  + All 11 redundant internal .sp-chapter-chrome blocks
    removed. They were duplicating the gate's label with
    off-by-one numbering (gate said III, chrome said IV),
    and the duplicate is what made "Efteling" appear cut in
    two on tablet.
  + Arc labels renamed: Act I → "Part 1 — the promise";
    Act II → "Part 2 — the fairy tale"; Act III → "Part 3 —
    the wild"; Coda → "Notes — …". Chapter title language
    swept: A MANIFESTO → THE PLAN, FACTS & FOLKLORE → ODDS
    & ENDS, INTERLUDE (bridger side-label) → TWO TEMPER-
    AMENTS. MOOD BOARD, BY THE NUMBERS, LOGISTICS, MEANWHILE
    kept. Section id #manifesto → #the-plan.
  + editorial-spec.md § Chapter gate updated — sticky track
    is now 110vh not 160vh; "display:flow-root on every
    section[data-sp-chapter]" promoted to a hard rule
    (prevents margin-collapse from exposing body cream);
    arc-label vocabulary rewritten (Part 1/2/3 / Notes
    replacing Acts/Coda); "no end-of-chapter signoff — the
    gate IS the separator" added to the rules.
  + Standing-rule reminder documented: trip is named by the
    venue(s) ("Efteling & Beekse Bergen"), never by the admin
    locator ("Kaatsheuvel"). Factual uses of the town name
    inside prose remain OK.
  Net effect on tablet: no cream peek-through between
  chapters; no duplicate chapter labels; chapter titles and
  arc labels sound like a weekend reading journal, not a
  theatre programme.

8.5 — Chapter gate switched to a sticky scroll model.
  Problem: the v8.4 gate was 80vh split as 40vh breath → 20vh
  black strip → 20vh breath. On a real scroll-read the two
  cream breath zones read as dead whitespace, especially when
  the previous chapter also ended on a cream ground (black
  → cream → black → cream sandwich), and the preceding chapter's
  closing decoration (chapter-chrome watermark, "— end of
  chapter N —" colophon) stacked into the top breath. Reader
  feedback: "big blocks of white between a chapter ending and
  the new one starting" + "space to breathe doesn't seem to
  work, it's just ugly when looking in isolation".
  + 31-chapter-gate.css rewritten. Cream breath zones DELETED.
    Gate is now a 160vh scroll track containing a position:
    sticky full-bleed black panel (#0A0E17) that locks to the
    viewport for ~1 screen-height of scroll. Previous chapter
    butts straight up against the black; next chapter appears
    straight out of it. The pause is TIME, not whitespace.
  + Four text layers (arc, Roman numeral, chapter title, deck)
    all live on the black panel now — the deck moved from the
    bottom-breath cream zone INTO the panel.
  + Scroll-timed reveal driven by --scg-progress CSS variable
    (0..1). Arc fades in 0.10–0.30, numeral scales + fades
    0.25–0.55, title fades 0.45–0.70, deck fades 0.65–0.88.
    Clamp-based CSS, no keyframes.
  + script.js chapter-gate controller rewritten. Still builds
    the .scg-strip from data-attrs, but now runs a requestAnim-
    ationFrame progress loop that maps scrollY-through-gate to
    --scg-progress for every gate currently near the viewport.
    IntersectionObserver gates the loop to visible gates only.
    2.5s safety backstop still present.
  + Reduced-motion / no-JS fallback: gate collapses to a static
    52vh full-bleed black band with all four layers fully
    visible. No sticky, no progress driver, no motion. Same
    visual anchor.
  + Mobile: track height drops from 160vh to 140vh so the
    viewport-lock doesn't feel endless on portrait.
  + editorial-spec.md § Chapter gate rewritten for the sticky
    model — replaces "three zones (80vh total)" with the
    scroll-progress timing map and the four-layers-on-black
    structure. v8.4 ground discipline, accent lockdown, and
    stat budget rules unchanged.
  + SKILL.md asset-map row for 31-chapter-gate.css updated.
  + script.js region description updated to v8.5.
  Net effect: scrolling through a chapter break now feels like
  a page-turn in a magazine app — the world stops, the chapter
  announces itself, the world resumes. No cream moat.

8.4 — Chapter gate + ground discipline + accent lockdown.
  Problem: on quick skim, readers couldn't tell where one chapter
  ended and the next began. Pull-quotes, briefs, and stat panels
  each painted their own cream/ink backgrounds, fragmenting every
  chapter into a patchwork of inverted boxes. The coral accent was
  used everywhere (masthead, datums, kickers, numerals, badges),
  so it had stopped meaning "new chapter".
  + New `31-chapter-gate.css` (tier 7): `.sp-chapter-gate` is an
    80vh dedicated chapter opener with three zones: 40vh outgoing
    breath → 20vh full-bleed BLACK strip (always #0A0E17, regardless
    of grounds) carrying arc + Roman numeral + chapter title →
    20vh incoming breath with mandatory italic deck line. The
    black strip is the permanent, unmissable "new chapter" cue the
    reader's eye learns to read at any scroll speed. Reduced-motion
    safe, tablet + mobile rebalanced.
  + script.js: universal chapter-gate controller (lines ~298-373).
    Auto-builds the .scg-strip from `data-chapter-num` /
    `data-chapter-title` / `data-chapter-arc` attributes on the
    aside. Reveal on scroll (IntersectionObserver, threshold 0.25).
    2.5s safety backstop. Adds `sp-motion-ready` to body so the
    staged reveal can run.
  + 00-tokens.css: new `--sp-chapter-ff` (Space Grotesk) reserved
    for the gate only, `--sp-accent-primary` (coral, gate +
    countdown badge + progress bar only), `--sp-accent-secondary`
    (slate, paper-ground demotion), `--sp-accent-secondary-ink`
    (bone, ink-ground demotion).
  + template-parts/00-head-open.html: Space Grotesk added to the
    Google Fonts URL (300, 400, 500, 700).
  + Ground discipline (CSS-enforced in 31-chapter-gate.css): any
    `.sp-ground-paper` or `.sp-ground-ink` class applied to a
    component nested inside `[data-sp-chapter]` is neutralised to
    transparent/inherit. Components no longer flip ground inside
    a chapter. Only `.sp-pull-break` remains allowed as a
    full-bleed ground-painter.
  + Accent lockdown (CSS-enforced): coral is demoted on every
    common component class (sp-datum, sp-number, sp-number-huge,
    sp-kicker, sp-brief-kicker, sp-dash-cell strong, sp-pull-break
    corner quotes, sp-spread h2, sp-eyebrow) when inside a chapter
    wrapper. Paper chapters get slate; ink chapters get bone. The
    gate numeral, countdown D-day badge, and progress bar are the
    only surviving coral users.
  + editorial-spec.md: new "Chapter gate" section (mandatory per
    chapter, with deck-writing rules and arc-label map for
    Countdown/Deep Dive/Rewind/Season Review); new "Ground
    discipline" hard rule; new "Accent lockdown" hard rule; new
    "Stat budget" hard cap (≤ 12 stat-heavy blocks per issue:
    max 1 curtain, 1 dash, 6 sp-number, 4 sp-datum). Gate 2
    compliance fails if a chapter opens without `.sp-chapter-gate`.

8.3 — Universal chapter beads + sp-sticky-pin component.
  + Chapter beads are now UNIVERSAL: they work on standard
    weekly editions as well as every special edition. CSS in
    30-transitions-ambient.css lifted the `body.is-special`
    gate from the beads ruleset and introduced a --beads-accent
    token that cascades sp-accent (specials) → accent (standards).
    Activation class on <body> changed from sp-beads-ready (only
    set on is-special bodies) to plain sp-beads-ready.
  + script.js: beads controller promoted from the special-edition
    IIFE into a UNIVERSAL base-controller IIFE that runs on every
    issue. Auto-discovers chapters in this order: [data-sp-chapter]
    (specials) → .mag > section.sec (standards). Title resolution:
    data-sp-chapter-title → first <h2> text → section id (title-cased)
    → "Chapter N". The old special-edition beads IIFE short-circuits
    with `return` to avoid duplicate wiring. sp-horizon stays
    special-edition-only (needs ground metadata standards lack).
  + template-parts/19-closing.html: <aside class="sp-chapter-beads">
    now ships in every issue by default. Controller no-ops cleanly
    on issues with only one chapter.
  + New component `.sp-sticky-pin` (29-signature-moments.css):
    held-attention moment — a single portrait or pull-quote that
    pins to the column for ~1.5 viewports while prose flows past,
    with a thin accent rule growing as within-section progress.
    Variants: --portrait (right-float image, default), --quote
    (left-border pull quote), --left (mirrors to left margin).
    Mobile (≤ 820px) collapses to inline figure, no stick.
  + script.js: sp-sticky-pin controller in the universal base
    section. Enforces max-one-per-issue (extras auto-demoted to
    inline figures). Skips wiring on mobile. Drives --spin-progress
    on the pin from parent-section scroll.
  + editorial-spec.md: beads entry rewritten to document universal
    behaviour + standard auto-discovery. New "Held-attention moment"
    subsection with the five enforced rules for sp-sticky-pin.
    Chrome positioning table extended with sticky-pin row.

8.2 — Signature moments + chapter transitions + ambient layers.
  + 29-signature-moments.css (tier 6): one signature moment per
    special-edition format. sp-sand-clock (Countdown),
    sp-memory-wall (Rewind), sp-fault-line (Versus), sp-form-tape
    (Season Review), sp-thread-pull (Deep Dive), sp-build-meter
    (Blueprint), sp-cold-start (Starter Kit), sp-deck-reveal
    (Shortlist), sp-pinboard (Field Guide). Each gated by
    body.is-special[data-special="<format>"]. Reduced-motion
    fallback on every component.
  + 30-transitions-ambient.css (tier 6): format-agnostic chapter
    transitions and ambient layers. sp-stat-curtain (full-viewport
    hero stat, max twice per issue), sp-page-fold (3D rotateX
    page-curl at paper↔ink handoffs, max 2 per issue),
    sp-chapter-beads (right-gutter progress strip), sp-horizon
    (bottom-edge bleed of next chapter's ground colour).
  + script.js: controllers for all of the above, inside the
    special-edition IIFE. Shared rAF tick loop for beads + horizon.
  + editorial-spec.md: Signature moments section + Chapter
    transitions + ambient section with component contracts and
    when-to-use rules. Chrome positioning ground rules extended.
  + Deferred for later review: sp-margin-sweep, sp-iris,
    sp-vignette-breath, sp-grain, sp-locus, sp-type-weight
    (would either flatten the paper/ink identity or overlap with
    existing components). sp-freeze-frame deferred (overlaps with
    curtain + stat-curtain).

8.1 — Page-level horizontal overflow guard.
  Bug: a thin white/cream vertical strip appeared down the
  right edge of the page on tablet. Cause: decorative components
  (.sp-folio with `right: -3vw`, .sp-margin in collapsed-spread
  layouts, occasional parallax background images) extended a few
  px past the viewport, triggering a horizontal scroll context.
  Page scrollWidth was 824px on an 800px viewport, exposing the
  `body { background: #E8E6E1 }` cream behind .mag.

  + 01-base.css: added `html, body { overflow-x: clip }` and
    `overflow-x: clip` on `.mag` itself. `clip` is preferred over
    `hidden` because it doesn't create a new scroll context, so
    `position: sticky` and similar continue to work. Verified
    page scrollWidth now equals viewport width exactly.

8.0 — Tablet ground-level horizontal gutter.
  Bug: chapter contents (bullet lists, plain paragraphs, big
  numerals, briefs not inside an .sp-spread) sat flush against
  the viewport edge on tablet and mobile because the chapter
  wrappers (.sp-ground-paper / .sp-ground-ink) are full-bleed
  by design and only a 960px max-width on .mag was saving the
  desktop view.

  + 26-special-editorial.css: added @media (max-width: 1024px)
    and (max-width: 600px) blocks that pad direct children of
    .sp-ground-paper / .sp-ground-ink (and of their .p-fg
    parallax foreground layer) with safe-area-aware horizontal
    padding (28px tablet / 20px mobile). Exempts intentionally
    full-bleed components: .sp-spread, .sp-pull-break, .sp-folio,
    .sp-gallery, .sp-image-strip, .sp-scroll-image, plus the
    parallax background/mid layers.
  + Bumped .sp-spread-body padding from 24px → 32px on tablet,
    and from default → 24px on mobile.
  + Capped .sp-number-huge and .sp-bignum-num font sizes on
    tablet so giant numerals don't bleed off the left edge.

7.9 — Tablet column-width fix.
  + 24-special-motion.css: added @media (601-1024px) override
    widening .sp-manifesto-text from `max-width: 20ch` (collapsed
    to ~360px on tablet) to `min(90vw, 640px)`. Same fix for
    .sp-diptych-body which had `max-width: 32ch`.
  + 25-special-body.css: same tablet override applied to
    .sp-pullquote-huge p (was 20ch) and .sp-image-quote
    blockquote p (was 22ch).
  + editorial-spec.md (Output paragraph): documented the reader's
    Xiaomi Pad 8 (~800px portrait) sitting between the 820px and
    600px breakpoints, and the standing rule that any new ch-bound
    centred display component must ship with a tablet override in
    the same patch.
  The bug: `clamp(30px, 5vw, 64px)` font + `max-width: 20ch` looks
  fine on desktop (font hits 64px, ch is wide) and on phone (font
  hits 30px but viewport is narrow), but on tablet the font sits
  at ~40px and 20ch becomes ~360px stranded in an 800px viewport
  with huge wasted side margins.

7.8 — Countdown editorial rules locked in.
  + editorial-spec.md (Countdown section): added title rule (use the
    reader's name for the trip — "Efteling & Beekse Bergen" not
    "Kaatsheuvel", "Walt Disney World" not "Lake Buena Vista"). Cover,
    masthead ticker, navigator, foreword and footer all use the trip
    name; the locator only appears once as supporting context.
  + editorial-spec.md (Countdown section): added itinerary rule —
    never invent a day-by-day plan. Only include the day-by-day chapter
    when the reader has supplied one. Otherwise drop it entirely and
    lean harder on event-in-depth, logistics, mood-board, surprising
    facts. A guessed itinerary undersells the trip.
  + editorial-spec.md (Countdown section): added no-filler-chapters
    rule. Word count is a target not a floor. Cut any chapter without
    genuine content.
  + editorial-spec.md (Countdown section): added MANDATORY accommodation
    chapter when the reader has named a hotel/lodge/resort. Each
    property gets rooms + dining + facilities + activities + "what's
    near it on foot" + "why pay the premium". Multiple properties get
    parallel treatment. Hotels are the most photogenic content in the
    issue — 4–6 images per property minimum.
  + editorial-spec.md (Countdown section): added travel-imagery rule.
    Target 25–40 images across the issue (hotels contribute 8–12).
    Every venue/room/restaurant/activity chapter carries ≥2 images
    (hero + detail). Mix establishing shots with detail shots. Every
    image captioned with what + where + credit. Source from official
    press kits, Wikimedia, credited Flickr — never AI-generated.
  + compliance-checklist.md: new Countdown section with checks for
    all five rules above.
7.7 — Legacy island lock generalisation + image-failure safety net.
  + 26-special-editorial.css: island readability lock now covers ALL
    legacy paper-backed islands inside .sp-ground-ink — .also-card,
    .also-card-label, .also-card-title, .also-list, .angle-box, .dyk,
    .pull-quote, .sidebar-float — each gets its own cream background
    and ink-on-paper text so kicker/body stays legible in ink chapters.
    Fixes the “four modes” cards rendering as pink-on-pink ghost text.
  + 25-special-body.css: new .sp-img-failed graceful-degradation rule.
    When an image fails to load (404, 429 rate-limit, CORS, offline)
    the empty figure frame collapses to a 1px rule and the figcaption
    italicises — no more huge empty cream boxes where a hero image
    should be.
  + script.js: image-failure watcher tags any <img> inside
    .sp-scroll-image / .sp-inline-figure / .sp-image-quote that fails
    to load (checked on complete-with-zero-dimensions, load, and error).
    Auto-applies .sp-img-failed to the containing figure.
  + countdown HTML: switched the Noord-Brabant location map from the
    /thumb/ PNG (intermittent 429s from upload.wikimedia.org) to the
    direct SVG URL. SVG is served uncached and has been reliable in
    testing.
7.6 — Mobile motion fix + sidebar readability extension.
  + script.js: loosened tier-5.5 IntersectionObserver thresholds
    (default 0.01, rootMargin 150px 0px 150px 0px) so small kickers/
    briefs reliably fire on mobile; all 13 tier-5.5 observer overrides
    and tier-4 makeRevealer thresholds dropped to 0.01.
  + script.js: REPLACED the 7.5 blanket 2.5s safety timer that killed
    scroll-triggered motion. New smart multi-layer safety net:
    catchUpAboveViewport() reveals only elements at/above current
    viewport (threshold = innerHeight + 200), called at 600ms initial,
    again after 1.2s scroll-idle, and 8s backstop. Elements below the
    viewport stay hidden so their entrance animation still plays when
    scrolled into view. Motion restored end-to-end.
  + script.js: safety map extended to include tier-4 selectors
    (.sp-kicker, .sp-inline-figure, .sp-pullquote-huge, .sp-marginalia).
  + 26-special-editorial.css: island readability lock extended to
    legacy .sidebar / .sidebar-label / .sidebar-title / .sidebar li
    when nested inside .sp-ground-ink. Sidebar now paints its own
    cream background with ink-on-paper text inside ink chapters
    (fixes ghost cream-on-cream text in Beekse/Efteling chapters).
7.5 — Tier 5.5 motion layer + mobile readability gate.
  + 28-special-motion-editorial.css (wipe-band reveal, chapter-chrome sequenced
    reveal, folio scroll drift, stat-dash stagger, timeline row stagger, hero-quote
    lift, brief slide-in, pull-break corner quote reveal, bridger stagger, spread
    rail+margin slide-in, drop-cap pop, spine SVG line draw, caption-strip hairline
    draw, underline-draw links, ground-seam accent hairlines, reduced-motion kill)
  + 14 IntersectionObserver controllers in script.js (tier-5.5 IIFE)
  + MOBILE FIX: all opacity:0 initial states gated behind body.sp-motion-ready;
    JS adds the class on init plus a 2.5s safety timer force-applies every -in
    class. Without JS / on a stalled observer (common on mobile) content stays
    fully visible. No more black voids or ghost-text briefs.
  + .sp-island readability lock in 26-special-editorial.css pins brief / hero-quote
    / bridger / margin-quote / datum text to ink-on-paper inside ink grounds
  + editorial-spec.md: tier-5.5 motion section + ABSOLUTE ban on self-quoting
    (quotes must be real, sourced, and attributed)
  + compliance-checklist.md: Gate 1B extended with self-quote grep targets
7.3 — Enhancement 22: decorative chrome adopted from signal-weekly-v2.
  + 22-decorative.css (grain, chapter-chrome, folio-watermark, pull-break, marginalia)
  + 04-navigator-toc.html (opt-in TOC-style navigator, fully scoped)
  + ember period (.mast-period, .brand-period) on masthead + cover wordmark
  + guidance comments in 9 section template parts
