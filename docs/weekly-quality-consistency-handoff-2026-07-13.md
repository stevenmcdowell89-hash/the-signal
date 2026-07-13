# Weekly quality-consistency handoff — length + images (2026-07-13)

**Purpose.** The first weekly generated on the new v8.42 "Transmission" code came
out **too lean** (~3,960 words against the 6,000–9,000 target) and with **zero
images**. Both defects passed every automated gate silently, and both were fixed
*by hand* for the shipped issue (`signal_weekly_2026-07-13.html`, Issue #16 —
expanded to ~6.3k words + real images by hand-feeding fat briefs and running a
separate image-sourcing pass). **Left to the normal pipeline, the next weekly
regresses to thin + imageless.** This document states *why* that happens (the
systemic gaps), *what to change* to make length + images the pipeline default,
and *in what order* — so a future instance can address it durably.

This is a **plan, not a patch**: no code was changed producing it. Read it
alongside `docs/weekly-first-run-handoff-2026-07-12.md` (the earlier *structural*
first-run handoff — movements/Desk), `docs/signal-final-recommendations-2026-07.md`
(§5 the three-gate ledger), `.claude/skills/the-signal/SKILL.md` (Phases 3a/4/5,
7.6, 7.7, 9.5, 10), and `references/quality-rubric.md`.

All file:line citations are from the tree at the time of writing — re-verify
before editing, as line numbers drift.

---

## 0. TL;DR for the next instance

1. The 6–9k target is **never allocated per band**; every band is floored
   *downward* and encouraged to "yield," so the arithmetic lands ~4,000 words.
   **No gate has a word floor** — `validate-issue.py` checks only the 11,000
   ceiling.
2. Images are **gathered but never placed**: the sole weekly image component
   `.plate-img` is *defined as an empty CSS placeholder box* ("never a bare
   `<img>`") in both the contract and the golden fixture writers copy. Every
   image gate only inspects images that already exist, so **0 images passes
   trivially**.
3. The **golden fixture is a weak exemplar** (2,364 words, 0 images) and the
   regression certifies it as known-good — which also means it will *fail on
   itself* the instant you add a floor. Golden + floors must ship together.
4. The one **quality gate (Gate 3 / Phase 9.5) is structurally blind** to both
   defects: no image dimension, "density" scores facts-not-length, no exit code,
   and the rubric says "observational, never blocks" (contradicting SKILL.md).
5. **Highest-leverage fix:** turn length and image-count into **hard build
   gates** inside the existing markup-contracts gate (no new gate), flip
   `.plate-img` to a real-image contract, and rebuild the golden as a full,
   illustrated issue — **in one change**.

---

## 1. What shipped vs the target (measured)

Issue #16 (`issues/signal_weekly_2026-07-13.html`) — **after** the hand-revision:

| Metric | Measured | Target |
|---|---|---|
| Body words | ~6,150 (first pass: **3,960**) | 6,000–9,000 |
| Images (`<img>`) | **4** (first pass: **0**) | see §5 (recommend 8–12) |
| Cover image | **0** | 1 (recommend) |
| Movement bands | 4/4 ✅ | 4 |
| Long Read words | 2,087 ✅ | one deep anchor |
| Ends on verb + human line | ✅ | required |

**Where the 4 images sit:** Long Read ×2 (captioned + credited), Pixel & Byte ×1,
Screen & Sound ×1. **Everything else is image-free** — no cover art, and the
entire OPEN and CLOSE movements plus Touchline (sport), Bookmark (books) and
This-Week-in-History carry nothing.

**The verdict from the editorial review:** the *prose* is a genuine premium
Sunday magazine (a 2,087-word Long Read with a real pullquote and a "Case
Against" steelman; specific sport scorelines with live quotes; honest hedging on
the ISA-allowance rumour; a "previously on" Threads device). The *object* is a
lean typographic paper. **The entire gap between the two is visual.** The writing
playbook barely needs changing; the image budget needs to roughly triple and to
start with a cover.

---

## 2. Root cause A — leanness is arithmetic, not accident

The weekly is assembled by `scripts/stitch_weekly.py` against
`references/format-skeletons/weekly.json`; each writer authors only one band's
inner content. The 6–9k target exists **only as a single global number** and is
never decomposed into per-band shares, while every downstream pressure pushes
*down*:

| Where | File:line | What it does |
|---|---|---|
| Issue target (global only) | `references/editorial-spec.md:16` | "Target ~6,000–9,000 words… Padding a thin idea to a floor is banned" |
| Refuses a per-band quota | `references/spec/weekly.md:11` | "shaped by movements and per-piece shape, not a rigid quota — yield thin rounds rather than padding" |
| Per-chapter budget is soft | `references/chapter-plan-schema.md:156-160` | `target_word_count` "is **not a hard cap** — cut if content doesn't support it"; min is 100 |
| Floors point *down* | `references/chapter-plan-schema.md:244-251` | `word_count_target.min` = "sanity floor only: lead 150, companion 120" |
| Backbone retired | `references/chapter-plan-schema.md:228` | A round may run "nothing (a silent yield) — none of these hard-fails" |
| Yield-not-fill | `references/spec/weekly.md:89` | a thin section "**yields** that week rather than running a roundup" |
| No padding floor | `references/sections.md:456` (RT-18 §3) | "Length follows the material… **no padding floor**" |
| Only mandated long piece | `references/spec/weekly.md:201` | Long Read "typically 900–1,800 words"; "no second mandated anchor" |
| Skeleton has no length field | `references/format-skeletons/weekly.json` | **no word/length field on any band** |

**The arithmetic:** one Long Read (900–1,800) + Letter (~150) + 8-line digest +
brisk yield-happy rounds each floored at 150 ≈ **~4,000 words**. Nothing pushes
any writer *up*, and no writer is told its *share* of the 6–9k. That is the
observed 3,960.

**No floor gate anywhere.** `validate-issue.py`'s `check_length_ceiling`
(`:1117-1144`) tests only `words > ceiling`; the weekly ceiling is 11,000
(`LENGTH_CEILINGS`, `:67-80`). There is no floor branch. `validate-chapter-plan.py`
never sums or floors a word budget for weeklies (`check_weekly_plan`, `:767-929`).

---

## 3. Root cause B — images are gathered but never placed

The chain enforces that image candidates **exist in the bundle**, but nothing
enforces that any are **placed in the issue**, and the sole weekly image
component is a placeholder box.

**The "16 gathered, 0 placed" trace:**

1. **Phase 3a** — researcher gathers ≥16 verified image URLs into
   `research-bundle.json → image_candidates` (`SKILL.md:190`,
   `references/spec/global.md:333`, `references/image-source-types.json:164`
   `min_unique_candidates`).
2. **Phase 3a-verify / 3b** — the bundle gate requires the 16 to **exist in the
   bundle** (`SKILL.md:203-230`). This is the *last* point images are mandatory
   — and it only guarantees a JSON file has them.
3. **Phase 4 (planner)** — `chapter-plan-schema.md:168-189` `images_needed` is a
   required field that **may be empty** (`world`/`toolkit` examples show `[]`);
   `weekly.json` declares **no image slot on any band**; there is **no planner
   step routing bundle candidates to bands**.
4. **Phase 5 (writer)** — the only image-capable weekly component, `.plate-img`,
   is defined as an **empty placeholder glyph box, "never a bare `<img>`"** in
   `references/component-contracts.md:132-147` *and* in the golden fixture
   writers copy verbatim, `references/golden/weekly/chapters/long_read.html:22-28`
   (`<span class="glyph">FIG. 01 · THE EMPTY DESPATCH BOX</span>`). Layer 4
   (`global.md:339`) says *if* you place an image use a bundle URL — it never
   says place one.
5. **Phase 7.6 / 7.7 (gates)** — both only inspect images already in the DOM, so
   zero `<img>` → both pass trivially.

**Every image gate passes at zero images:**

| Gate | File:line | Why 0 images passes |
|---|---|---|
| URL HEAD-check | `validate-issue.py:617-620` | `if not urls: report.warn(...); return` — WARN, not FAIL |
| Static page-URL check | `validate-issue.py:585-614` | empty loop → returns clean |
| Diversity | `scripts/check-image-diversity.sh:60-62` | `if not urls: … sys.exit(0)` |
| Publish receipt | `scripts/publish-gate.sh:65-69` | diversity only invoked `if grep -q '<img '` |
| Caption integrity (Gate 1F) | `compliance-checklist.md:178-184` | `caps >= imgs*0.85` is vacuous at 0 (0 ≥ 0) |
| Component variety | `validate-issue.py:444-474` | weekly is exempt (`floor = None`, `:449-450`) |

The CSS *does* now support real images (`.plate-img img` at
`assets/css/weekly/00-transmission.css:451`; `.plate-cap .credit` at `:488`) —
but that capability is documented **nowhere** as available/required, and the
contract still says "never a bare `<img>`." That one sentence is the load-bearing
thing to change.

---

## 4. Root cause C — the golden fixture, and Root cause D — Gate 3 is blind

**C — the weak golden actively blocks the fix.** `scripts/verify-weekly-golden.sh`
stitches `references/golden/weekly/chapters/*.html` (2,364 words, 0 images) and
asserts it **passes `validate-issue.py --format weekly`** (`:39`), then prints
"GOLDEN REGRESSION PASS." That contract **codifies thin + imageless as
known-good.** It is self-locking: add a 6,000-word or image floor and the
regression fails *on its own golden*. So the golden is not a passive miss — it is
an active barrier, and it trains every future maintainer that "green" tolerates a
half-length imageless issue. **Fix: rebuild the golden to ≥6,000 words with real
captioned/credited images, committed in the same change as the floors.**

**D — the one quality gate cannot see either defect.** Gate 3 (Phase 9.5 holistic
read, `compliance-checklist.md:11`) is a **manual/prompt step with no exit code**;
`publish-gate.sh` does not invoke it. Its rubric (`references/quality-rubric.md`):

- has **no image dimension at all** — a 0-image issue loses no points anywhere;
- scores **"density" as facts-per-paragraph, not length** (`:81-96`) — a tight
  4,000-word issue can score 4–5;
- states "**scoring is observational… never blocks or reverts a publish**"
  (`:14-16`), which **contradicts** SKILL.md's "blocking-ish / made to matter"
  reframe (`SKILL.md:387`).

Word count and image count are the **two most mechanizable defects in the whole
pipeline.** Leaving them to a soft read that structurally can't measure them is
the core mismatch. They must be **numbers, not judgement.**

**Other silent-pass gaps found (worth fixing while in here):**
- Component-variety floor never applies to weeklies (`validate-issue.py:449-450`)
  — no mechanical stop on a visually barren weekly.
- The Colophon "Issue in Numbers" stats are self-consistency-checked only
  (`validate-issue.py:808-863`), never compared to the real body — a natural
  *source of truth* for a word/image floor, currently unused.
- The ship gate runs **non-strict** (`publish-gate.sh:62`), so the one WARN that
  could surface imagelessness under `--strict` in CI is neutralised at ship time
  (CI is post-publish and non-blocking anyway).

---

## 5. The improvement plan

Two buckets: **(A) prevent regression / enforce consistency**, and **(B) raise
the ceiling / new ideas**. Guiding principle from premium weeklies (see §6):
**fix the container before you fill it** (flatplan + standing per-section
budgets), and **encode "what good looks like" as a golden + checklist** so any
generation run reproduces the standard.

### Part A — prevent regression (enforce consistency)

**A1 — Word-count *floor* in the markup gate.** Extend `check_length_ceiling` →
`check_length_band` in `validate-issue.py:1117-1144` with a `LENGTH_FLOORS` dict
beside the ceilings (weekly ≈ **6,000**; set per-format floors below each
target's lower bound to avoid false fails). Add a `words < floor` → `report.fail`
branch mirroring the existing ceiling branch. Lives **inside the existing
markup-contracts gate** — no new gate, honouring the three-gate ledger. Already
wired into `main()` and consumed by `publish-gate.sh`, so it becomes
unbypassable.

**A2 — Image-presence floor, independent of `--skip-image-urls`.** Add
`check_image_floor(html, fmt)` with a per-format `MIN_IMAGES` map (weekly ≈
**8–10**), registered in `main()`. Add a **`long_read_has_image` invariant** to
`weekly.json`'s invariants block so an imageless Long Read hard-fails the way a
missing movement band already does. Must run **even offline** (the sandbox blocks
HEAD-checks) so the floor holds regardless of egress. Forces one decision: do CSS
placeholder "plates" count as images? **Recommend no** — require true `<img>` in
feature bands.

**A3 — Flip `.plate-img` from placeholder to real-image contract.** *Highest-
leverage content change.* In `component-contracts.md:132-147`, replace the "never
a bare `<img>`" placeholder-only definition with the real-image form the CSS
already supports (`.plate-img > img` + `.plate-cap` carrying `.fig`/`.txt`/
`.credit`). Keep the empty `.plate-box` glyph **only** as an explicit "no
verified image available" fallback. Until this sentence changes, writers keep
emitting empty boxes because that is what the contract tells them to do.

**A4 — Replace the weak golden with a full, illustrated one.** Rebuild
`references/golden/weekly/chapters/` to ≥6,000 words with real captioned/credited
`<img>`s (swap the `THE EMPTY DESPATCH BOX` placeholder in `long_read.html` for a
worked real-`<img>` example). Because the regression runs `--skip-image-urls`,
the URLs need not resolve live, but the markup must be present and well-formed.
**Commit in the same change as A1/A2** or the regression fails on its own golden.
Issue #16 is a ready-made strong exemplar to derive it from.

**A5 — Allocate the word budget per band (fix the cause, not the symptom).** Add
a `target_words` field to each band in `weekly.json` so required bands *sum* into
6–9k (Long Read 1,400–2,000; each Round 350–600; Letter 120–200; Desk
250–400/column). Reframe `chapter-plan-schema.md:156` `target_word_count` from
"not a hard cap" to "the band's allocated share; the planner MUST allocate shares
summing ≥6,000," and add an issue-level `word_budget` to `issue_meta`. Add one
line to `spec/weekly.md:11` / `editorial-spec.md:16`: the target is *allocated
per band by the planner*, not left to each writer independently; "length follows
the material" governs trimming a *given* allocation, not whether to attempt it.
Clarify `sections.md:456` that "no padding floor" means don't pad *beyond* the
material — a writer landing far under its share flags the planner for more
research, not ship short. **A1 catches the failure; A5 prevents it upstream.**

**A6 — Route bundle images to bands + tell writers to place them.** Require the
planner to populate `images_needed` (≥1, `alt_required:true`) for the Long Read
and every feature/history band, drawing `role`/`source_constraint` from bundle
candidates; add a planner step "assign ≥1 `image_candidate` to the Long Read and
each feature band." Add one line to the Phase 5 writer brief (`SKILL.md:239-241`):
*bands whose plan carries `images_needed` MUST emit a real `<img>` from
`image_candidates`, with credit; the Long Read must place ≥1.* Today Layer 4
(`global.md:339`) only governs *which URL* to use if you use one — never *that*
you must.

**A7 — Give Gate 3 an image dimension + reconcile the contradiction.** Add a 7th
rubric dimension (visual richness / illustration) to `quality-rubric.md` so the
quality log tracks imagery; split "density" into *information density* vs *length
adequacy*. Resolve the SKILL.md-vs-rubric contradiction (`SKILL.md:387` vs
`quality-rubric.md:14-16`): decide whether the holistic read is observational-only
or can trigger a repair round, and make both files agree. Gate 3 stays the
*judgement* layer; A1/A2 are the *measurement* layer.

**A8 — Per-issue "flatplan checklist" as a Gate-2 reading aid.** A short
mechanical pre-ship checklist mirroring copy-desk QA: image count ≥ floor, cover
present, each Round >400w has ≥1 image, no band under its allocated share,
captions on every image, reader-profile domains covered on rotation (**LEGO was
silently dropped in #16** despite being in the profile). Surfaces gaps the way a
flatplan does before ship.

### Part B — raise the ceiling (new ideas from premium weeklies)

Realistic for a pipeline that sources real images + generates text.

- **B1 — Ship a cover image every issue.** Biggest single upgrade: every
  comparator (New Yorker, Monocle, Guardian Weekly) opens on a picture; The
  Signal's masthead is purely typographic. A stable, recognisable cover treatment
  makes issues feel like one continuous premium publication.
- **B2 — One signature full-page infographic per issue.** The Economist's
  *Graphic Detail* model — one chart, plain-language insight-first title, fixed
  house palette, weekly. Promote one "Week in Numbers" figure into a proper
  standing data-viz. (The repo's `dataviz` skill fits this.)
- **B3 — Enforce visual rhythm.** In any band >800 words: a subhead every 3–5
  paragraphs, ≥1 pull quote per ~1,000 words at 1.5–2× body, captions on every
  image — checkable in the markup gate. (Recovers the retired prose-rhythm gate's
  intent.)
- **B4 — Per-band image density ~2 images / 1,000 words (text-led floor).** For a
  ~7.5k-word, ~13-section issue that's ~15–20 visuals with every feature getting
  an opening image. The Long Read's existing 2-per-2k rhythm is the template —
  make it the rule.
- **B5 — A recurring illustrated column with fixed spot-art identity** (Economist
  KAL logic). This-Week-in-History is the natural candidate — a standing archival-
  image treatment turns it into a familiar visual ritual.
- **B6 — Book covers on the Bookmark rail.** Near-mandatory in the genre; #16's
  Bookmark shows none and is the thinnest Round. Apply the specials' per-title
  image-sourcing floor (Starter Kit: "every pick has an image") to weekly
  Bookmark.
- **B7 — A photo-led section per issue** — one deliberately image-led spread
  (photo essay, or a map for a geographic story) balancing the text-led bands.
- **B8 — Target 6.8–7.5k, not the 6.0k floor.** #16 sits *at* the floor; aim
  mid-band so a light news week still clears target. Codify #16's best move (Long
  Read ≥1,800w with a pullquote *and* a "Case Against" counter-reading) as a
  **required** Long Read element, not a happy accident.

---

## 6. Why — what premium weeklies do (research backing)

Premium weeklies hold quality with two structural moves that map cleanly onto an
automated pipeline:

1. **Fix the container before filling it.** A **flatplan** assigns every section a
   *standing* page/word budget that must be filled every issue, owned by one
   editor across the whole issue; thinness is structurally impossible because the
   container is defined before content is commissioned. Working figures: spread ≈
   400–500 words after images; front-of-book brief ≈ 300–600; factual feature ≈
   1,200–2,000; big feature ≈ 1,500–2,500. (Sources: Andrew Noakes "Planning &
   producing a magazine"; flat-plan.com; X-Ray Mag word-count guide.)
2. **Encode "what good looks like."** A written **style bible + style sheet with
   worked examples**, a per-issue **copy-edit checklist** (pros do two passes at
   different speeds), an **art director signing off on imagery**, and a **golden/
   reference issue to diff against** — exactly the anti-regression tools for
   different writers (or generation runs) producing different sections. (Sources:
   Nxtbook style-guide guide; Dragonfly copyediting checklist; DINFOS Copy
   Editor's QA Guide.)

**Image density norms:** the recurring floor is **1–2 images per 1,000 words for
text-heavy content**, and the closest thing to a hard rule is **every feature
gets an opening image** (Publitas; 123RF). The Economist runs a signature full-
page data-viz (*Graphic Detail*) every week; recurring columns keep a stable
spot-art identity (KAL). **Visual rhythm:** subhead every 3–5 paragraphs in
articles >1,500 words; ~one pull quote per 800–1,000 words at 1.5–2× body;
body measure 45–75 characters; captions ~85–90% of body size (Typography Master;
Fonts.com "Entry Points"). Shipping "few or none" images is far below any
premium-weekly norm.

**The mapping is direct:** the two failure modes flagged (too short, too few
images) are precisely the two things flatplans + image floors exist to prevent,
and they are the two most mechanizable defects in the pipeline. Make them **hard
build gates**, not stylistic choices.

---

## 7. Sequencing (one ordering trap)

Dependencies matter:

1. **A3 + A4 together first** (real-image contract + rebuilt golden) — establishes
   what "good" looks like and unblocks the floors.
2. **Then A1 + A2 + A5 + A6** (floors + budget allocation + image routing) — the
   golden now passes them; a thin/imageless issue now fails.
3. **Then A7 + A8 + Part B** (quality-gate + checklist + ceiling-raisers).

> ⚠️ **Do not add the word/image floors (A1/A2) before rebuilding the golden
> (A4).** The regression harness runs the floors against its own golden, so a
> 2,364-word / 0-image golden fails the instant the floors land. **Floors and
> golden must ship in one change.**

**Single highest-leverage move:** turn length and image-count from "achieved when
a human hand-feeds fat briefs" into **hard build gates** (A1–A4), inside the
existing markup-contracts gate — no new gate, no violation of the three-gate
ledger.

---

## 8. Relevant paths

- Ship gate (add the floors here): `.claude/skills/the-signal/scripts/validate-issue.py`
  (`check_length_ceiling` ~L1117; `check_image_urls` ~L617; `LENGTH_CEILINGS` ~L67).
- Publish receipt: `.claude/skills/the-signal/scripts/publish-gate.sh`.
- Golden regression: `.claude/skills/the-signal/scripts/verify-weekly-golden.sh`.
- Golden fixture (rebuild): `.claude/skills/the-signal/references/golden/weekly/chapters/`.
- Weekly skeleton (single source of truth — add `target_words` / image invariant):
  `.claude/skills/the-signal/references/format-skeletons/weekly.json`.
- Image component contract (flip `.plate-img`): `references/component-contracts.md` (~L132).
- Weekly CSS (real-image support already present): `assets/css/weekly/00-transmission.css`
  (`.plate-img img` ~L451; `.plate-cap .credit` ~L488).
- Plan schema (per-band budget + `images_needed`): `references/chapter-plan-schema.md`.
- Plan validator: `.claude/skills/the-signal/scripts/validate-chapter-plan.py`
  (`check_weekly_plan` ~L767).
- Diversity gate: `.claude/skills/the-signal/scripts/check-image-diversity.sh`.
- Specs: `references/editorial-spec.md` (source) → sliced `references/spec/weekly.md`,
  `references/spec/global.md` (image-integrity, fact-provenance).
- Section briefs: `references/sections.md` (RT-18 §3 ~L456).
- Quality rubric (add image dimension; reconcile with SKILL.md): `references/quality-rubric.md`.
- Pipeline: `.claude/skills/the-signal/SKILL.md` (Phases 3a/4/5, 7.6, 7.7, 9.5, 10).
- The issue under review: `issues/signal_weekly_2026-07-13.html` (Issue #16).
- Prior structural handoff: `docs/weekly-first-run-handoff-2026-07-12.md`.

---

**One-line summary for the next instance:** the new weekly defaults to ~4,000
words and 0 images because the 6–9k target is never allocated per band and the
sole image component is a placeholder box — both pass every gate because there is
no length floor and no image floor anywhere; fix it by rebuilding the golden as a
full illustrated issue, flipping `.plate-img` to a real-image contract, and
adding a word-floor + image-floor inside the existing markup-contracts gate (in
one change so the regression moves with them), then allocate the word budget
per band and route bundle images to bands so length + images become pipeline
defaults rather than hand-fed exceptions.
