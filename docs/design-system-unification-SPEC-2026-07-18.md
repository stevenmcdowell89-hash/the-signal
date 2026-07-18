# THE SIGNAL — DESIGN SYSTEM UNIFICATION SPEC v2

**Date:** 18 July 2026 (v2 — full rewrite after two failed implementation attempts; supersedes v1 entirely)
**Status:** BINDING CONTRACT for an orchestrator running subagents.
**Owner intent, verbatim:** the holiday-system quality (Field Guide 05-17, Countdown 06-14) becomes the basis for ALL weeklies and specials, de-themed. "I don't want some half designed crap shipping… the whole design needs to have quality and consistency baked in." And, after attempt #2: "visually this is just a load of squares, it's nothing like that trip countdown. there's no movement."

**How this document is organized:** eight parts. Part 1 (Design Laws) + Part 2 (Architecture) + Part 3 (Failure Registry) are the standing context every subagent receives. Part 4 defines the work packages (WP-0…WP-9), each self-contained enough to hand to a builder subagent. Part 5 is the DESIGN-PARITY GATE — the phase that checks output against what we actually want. Part 6 is the anti-gaming/evidence protocol. Part 7 is editorial/content requirements. Part 8 is orientation (file map, environment).

**Why v2 exists — the two failures this spec must make impossible:**
- Attempt #1 read "the weekly must not change" as excluding the weekly from the upgrade. (Fixed by Law 11 and WP-8.)
- Attempt #2 shipped a 542-word "Season Review" claiming "publish-gate GREEN, 2.81 events/screen, 390px pass" — while the artifact had a fixed pill overlapping content at every scroll depth, a table truncating mid-word, "FURNITURE-FIRST" printed in the cover meta, zero external voices, zero photos, zero motion, and every component rendered as a flat hairline-bordered rectangle. Every one of those false claims now has a named failure (F-18, F-19, F-20), a mechanical gate, and an independent-verification requirement.

---

# PART 1 — DESIGN LAWS (the north star; every visual gate scores against these)

The bar is `issues/signal_countdown_2026-06-14.html` and `issues/signal_field-guide_2026-05-17.html`, rendered — not their theme, their QUALITIES. The reference mockup `docs/mockups/unification-furniture-kit-mockup.html` shows the qualities de-themed. These twelve laws are binding. Each is written to be scoreable PASS/FAIL by a verifier looking at rendered screenshots.

**LAW 1 — SCENOGRAPHY: objects on a surface, never boxes on a page.**
Every ephemera object carries ≥2 of: rotation (1–3°), fastener (tape/pin/stamp/photo-corner), shadow or paper texture, scene-ground behind it, overlap with a neighboring element. Every act has a SCENE ground (gradient sky, starfield, pattern field, visible grain) — a flat single-color background behind an entire act is a FAIL. At least one object per chapter breaks the column grid (tilted, bleeding off-edge, or overlapping a boundary). Verifier's verbatim question at every gate: **"Objects on a surface, or boxes on a page?"** — "boxes" fails. Reference: the countdown at 390px puts a starfield with sparkle glyphs behind PLAIN BODY TEXT; that is the minimum ambient standard for event-skin acts.

**LAW 2 — DENSITY WITH DISTRIBUTION.**
Designed visual events per screen (event = one of: captioned figure/`<img>`; ephemera object; ledger/table block; stat band; quote-object with named source; numbered plate/act opener; self-made chart/diagram/map; marquee/act-divider; cheat-sheet. NOT: drop caps, hairlines, subheads, bold runs):
| Format | floor–target | Words/screen max |
|---|---|---|
| Weekly | 0.8–1.0 | 210 |
| Deep Dive | 0.7–0.9 | 220 |
| Rewind / Season Review | 0.9–1.1 | 210 |
| Versus / Guide / Next | 0.8–1.0 | 210 |
| Trip specials | 1.0–1.3 | 210 |
Distribution: **no run of 3+ consecutive screens with zero events** (measured on the rendered page at 1440×900 and 390×844; screens = pageHeight/viewportHeight). Max 4–5 consecutive paragraphs without an event. Averages alone never pass — distribution must pass too.

**LAW 3 — LENGTH: density by shortness is a FAIL.**
Body-copy word floors (excluding chrome/captions): Weekly 6,000 · Deep Dive 8,000 · Season Review 6,500 · Rewind 7,000 · Versus 4,500 · Guide 3,500 · Next 3,000 · Countdown 4,500 · Field Guide 6,000. Cautionary precedent: attempt #2's 542-word stub "passed" density. An issue below floor fails regardless of any other metric.

**LAW 4 — ARC: the scroll travels.**
1–3 palette acts per issue, each with its own ground; the act transition is a designed moment (transit band, gold seam, crossfade), not a background-color swap. Reference: countdown's indigo-night → cream-savannah shift. Editorial specials express this in ink terms (paper-white → parchment/sepia tints); the weekly may use its existing band rhythm.

**LAW 5 — MOTION: tiered, furniture-attached, verified.**
Tier per format: tier0 print-still (Deep Dive): hairline draw-ins + ghost-numeral parallax only. tier1 calm (Weekly, Rewind, Next, Guide): rise-on-scroll + object settles (cards "tape down" with ~1° settle, ledger rows tick in sequentially, sparklines draw). tier2 event (trip specials, Season Review, Versus): stamp-slam, marquee, flips, act crossfade. One signature moment per format: Versus = verdict stamp slams per round; Season Review = leaderboard rows climb into place; Rewind = Memory Test columns reveal in sequence; Weekly = dial-needle sweep on band entry; Countdown = flips. Hard rules: motion attaches to furniture, never running text; `prefers-reduced-motion` honored by every animation; JS-off renders 100% of content; no scroll-jacking. **A tier1+ issue where nothing visibly moves during a real scroll capture is a FAIL** (attempt #2 shipped zero perceptible motion).

**LAW 6 — OBJECT FICTION: every fact-block wears its kit.**
Each issue declares ONE kit (Part 2 §2.4), uses 2–3 object types from it plus the universal fasteners. Facts, quotes, and data ship as kit objects — a quote is a postcard/strip with a named source, a result is a ticket stub or scorecard, a comparison is a chalkboard/programme spread — never as a generic bordered `<div>`. Generic bordered boxes carrying content that a kit object exists for = FAIL.

**LAW 7 — COVERS: poster-grade, owned per format.**
Each format has one owned cover gesture (Field Guide owns its giant "44"; Deep Dive: oversized ghosted numeral or map fragment; Rewind: the year-band; Next: route-card timeline; Season Review: bracket/trophy motif). Event-skin covers are posters (multi-voice type, illustration/plate, arc text); no two formats may render visually interchangeable covers; cover reads `var(--mx-accent)`, never a hard-coded accent. The three-identical-dark-covers pattern of the old editorial system is the named anti-goal.

**LAW 8 — TYPE: six voices, disciplined.**
The six type roles all appear across an issue; the cover uses ≥3 distinct voices; mono micro-labels ≥0.72rem; body measure ≤68ch (attempt-observed violations: 0.66rem labels, 1,270px measures). Playfulness lives in display/furniture; body text stays disciplined.

**LAW 9 — TRUST: the magazine has arguments, not experiences.**
Three lanes: EXPERIENCED (taste/feel/being-there) — never first-person, only named verbatim quotes, no invented consensus; ANALYZED — own opinions allowed with working shown; CURATED — selection/reader-fit fully allowed. Minimum named external voices per issue: Weekly ≥4 · Deep Dive ≥5 (historians/primary sources count) · Season Review ≥5 · Rewind ≥3 · trip specials ≥6 · Versus/Guide/Next ≥3. Every voice renders as a quote-object at least once. Self-quotes ("— THE SIGNAL") do not count and are capped at 1 per issue. Each quote max 2 renderings; each fact max 2 tellings. (Attempt #2 shipped ZERO external voices and two self-quotes.)

**LAW 10 — CRAFT FLOOR.**
At 390×844: no document-level horizontal scroll; fixed chrome (back pill, masthead, progress) never overlaps content at any scroll depth — reserve space or hide-on-scroll; tables never truncate mid-word at rest (stack or scroll-wrap with visible affordance); ephemera images are real `<img>` (object-fit) or `role="img"`+`aria-label`; token-level dark mode; minimal print sheet; WCAG AA contrast per act. (Attempt #2 failures: pill overlapped content at every depth; table columns cut mid-word.)

**LAW 11 — IDENTITY: three skins, each itself.**
Transmission (weekly): identity permanently protected — palette, type stack, 800px printed-object chassis, radio conceit — but the weekly IS upgraded: it reaches its Law-2 budget via core furniture through an alias block (mockup spread 2 is the reference; a weekly whose density doesn't change is a FAIL of the engagement, not a success). Editorial skin (Deep Dive/Rewind/Versus/Guide/Next): bookish gravitas kept; motif surface capped at palette-arc + one pattern + one cover gesture; scenography expressed in paper-and-ink (archival objects, not theme park). Event skin (trip specials, Season Review): full holiday-descended treatment.

**LAW 12 — HONESTY: evidence or it didn't happen.**
No gate claim without committed artifacts (Part 6). A discovered false PASS voids the phase and triggers re-verification of all prior gates by fresh subagents. (Attempt #2 recorded "GREEN" evidence that was false on first human look.)

---

# PART 2 — ARCHITECTURE (target state)

### 2.1 Layers
```
L0 css/core/         FURNITURE CORE — extracted from the holiday layers' ~83% universal bucket
   00-contract.css   --mx-* tokens + neutral defaults + six type roles
   10-ephemera.css   framed-object chassis (photo/content window + fastener + hand caption + credit),
                     polaroid→pinned card, postcard→mail card, stamp/seal, ticket, coaster;
                     SCENOGRAPHY DEFAULTS BUILT IN: rotation/tape/shadow are component defaults, not opt-ins
   11-ledgers.css    facts <dl> rows, ranked entries + rank chips, tier pills, stat bands, cheat-sheet, scorecard
   12-plates.css     numbered plates, anchor blocks, zig-zag entries, don't-miss chips
   13-chrome.css     ONE masthead, cover scaffolds (incl. poster), kicker, act opener + SCENE-GROUND utilities
                     (starfield, gradient-sky, pattern-field, grain), transit band, marquee, countdown grid
   14-motion.css     tiers via [data-motion="tier0|tier1|tier2"], signature-moment hooks
   15-responsive.css 390px stacking, chrome reservation, table wrap affordances, type floors
L1 css/skin-*/       transmission (existing weekly CSS byte-identical + ~20-line --mx alias block) ·
                     editorial (23–31 rebased under body[data-skin], :not() chains deleted, 32 split,
                     Lookahead deleted) · event (halves rhythm, transit, hype norms)
L2 motif pack        per-issue token block + ≤4 art slots, generated from validated JSON; never repo CSS
```
Bundle budgets: editorial special ≤120KB CSS, event special ≤160KB, weekly stays ≤~30KB. Legacy 00–22 ships nowhere. One masthead per bundle. Neutral `mx-` class names (weekly's forbidden-marker gate must never false-fire).

### 2.2 Token contract (~30 custom properties)
`--mx-paper/-ink/-accent/-accent-2/-support-1/-support-2/-hair` per act via `section[data-act]`; type roles `--mx-t-chunk/-tall/-script/-hand/-serif/-mono` from a ~15-family whitelist, **self-hosted** as subsetted woff2 under `assets/fonts/` (Google Fonts links are a proven runtime failure; one §gate render runs network-disabled); art slots `--mx-pattern`, `--mx-glyph` (currentColor, via `mask-image: var()` — this one indirection replaces all per-venue rules in layer 33), `--mx-band`; cover plate via markup injection. Plan-time validation: AA contrast per act pair, whitelist membership, byte caps, currentColor requirement.

### 2.3 Motif pack JSON
```json
{ "id":"worldcup-scorecard-2026", "acts":[{...},{...}],
  "type":{"chunk":"…","tall":"…","script":"…","hand":"…","serif":"…","mono":"…"},
  "pattern":"chequer.svg", "glyph":"trophy-stamp.svg", "band":null, "cover_plate":"inline-or-null",
  "grain":"halftone", "kit":"matchday", "motion":"tier2" }
```

### 2.4 Ephemera kits (one per issue; 2–3 object types + universal fasteners)
dossier (history): index cards, telegram slips, folder tabs, wax letters, map fragments, catalogue labels, coin roundels, margin notes · broadcast (weekly): wire chips, ticket stub, dial, rolodex cards, due-date card, till receipt, stamp corner, forecast chips · scrapbook (Rewind/annual): taped memory cards, photo corners, calendar tear-offs, sticker-album cells, report cards, certificates, cassette labels · matchday (football): match tickets, fixtures ledger, table card, SVG lineup pitch, programme card, pennant, turnstile stamp, clipping card · scorecard (golf majors): 18-hole card, red/black leaderboard, hole-diagram SVG, yardage page, trophy stamp · paddock (F1): timing tower, track map, tyre chips, pit board · inventory (gaming): box labels, achievement badges, save-file card, spec ledgers · cinema (screen/sound): admit-one, film strips, TV-guide rows, setlist, sleeve corner · library (books): bookplate, catalogue card, due-date slip · logbook (training): bib card, splits ledger, route ribbon.
Sport hierarchy (owner steer): football lead; golf majors + marquee events above F1; verify profile weights match.

---

# PART 3 — FAILURE REGISTRY (F-1…F-20; closeout table mandatory)

Design: **F-1** density collapse (DD 0.37 ev/screen) · **F-2** one cover template + hard-coded ember accent (`25-special-cover.css`) · **F-3** dual `.mast` (21-chrome vs 28-special-masthead) · **F-4** 176× `:not()` scoping tax (layers 23–32) · **F-5** ~444KB full-bundle shipping incl. deleted-format CSS (`stitch-issue.sh:330-334` glob; Lookahead block in 32) · **F-6** ephemera invisible to screen readers (92 vs 4 background/img countdown) · **F-7** zero dark/print in 23–44 · **F-8** mobile chrome shatter + pill overlap + table truncation + marginalia overhang · **F-9** 1,270px measures · **F-10** motion locked to two formats; spec text false · **F-11** three conflicting `--paper/--ink` namespaces · **F-12** 0.66rem micro-type.
Process: **F-13** spec rot (pre-flight/specials/contracts/Gate-1E teach the deleted v8.21 system) · **F-14** hand-authored chrome shipped `Issue #[N]`; scaffold-token classes: `ch\d+-\d+` in prose, `viz_\d`, "research bundle", `#[N]`, tool credits, raw CDN hostnames, **and internal strategy vocabulary ("furniture-first", "motif pack", kit/skin/phase names) in reader copy** · **F-15** designed-but-never-instantiated components (`.cheat-sheet`, B2 infographic) · **F-16** dead external hotlinks (Next 10/10) · **F-17** Getty/Shutterstock mislabeled `press_kit`.
New from attempt #2: **F-18 density gamed by stub** — 542 words @ "2.81 ev/screen" (AC: Law 3 floors wired into `validate-issue.py` for `data-mx` issues; the 542-word artifact retained as a negative fixture that must FAIL) · **F-19 false gate claims** — "GREEN" recorded against an artifact failing Laws 1/2/3/5/9/10 on first look (AC: Part 6 evidence protocol in force; the WP-0 gate suite demonstrably fails all retained negative fixtures) · **F-20 flat boxes** — every component an upright hairline rectangle (AC: Law 1 + Part 5 parity gate; the flat artifact retained as a negative fixture that must FAIL the parity gate).

---

# PART 4 — WORK PACKAGES (assign each to a builder subagent; every WP ends with its gate + Part 6 evidence)

Order: WP-0 → WP-1 → WP-2 → (WP-3 ∥ WP-4) → WP-5 → WP-6 → WP-7 → WP-8 → WP-9. Standing context for every builder: Parts 1–3 + Part 8. Builders never verify their own WP (Part 6).

**WP-0 — GATES FIRST (tooling before any art).** Build the measurement/verification suite before anything can claim green:
(a) `tools/measure-issue.mjs`: renders a served issue at 1440×900 + 390×844, smooth-scrolls, outputs `metrics.json` — words, events/screen (Law-2 closed list, via DOM selectors + `<img>` census), distribution (longest zero-event run in screens), chrome-overlap detection (fixed elements intersecting content at N scroll depths), doc-level H-scroll, mid-word table truncation (element scrollWidth > clientWidth without wrap affordance), motion census (computed animations fired during scroll; reduced-motion respected).
(b) Scaffold/strategy-vocabulary greps + Law-3 word floors + Law-9 voice minimums wired into `validate-issue.py` for `data-mx` issues; external-src image check (F-16).
(c) Negative-fixture harness: retained bad artifacts (542-word stub; flat-boxes season review; Rewind with `#[N]`; a deliberately flat re-dress) — **every gate must FAIL its negative fixture; a gate that has never failed anything is unproven and its PASSes don't count.**
(d) Evidence ledger skeleton (Part 6) + screenshot harness (`tools/render.mjs` exists on the attempt-2 branch; audit and reuse).
(e) Phase-0 hygiene: delete public TEST files; fix `image-source-types.json`; reconcile format vocabulary (guide/next in, blueprint out) across schema + both validators.
*Gate: every tool runs on both a known-good reference (countdown) and every negative fixture with correct verdicts, output committed.*

**WP-1 — REFERENCE CAPTURE.** Shoot the standard for the parity gate: countdown, field guide, and mockup at both widths, smooth-scrolled, 8 depths each + covers + one dark render; measure them with `measure-issue.mjs` (baseline metrics.json). Commit to `docs/design-system-unification-EVIDENCE/references/`. These are the frozen comparison packs every parity verifier receives.
*Gate: reference metrics reproduce the Part 1 table within tolerance (countdown ≥1.5 ev/screen measured by the tool — if the tool can't see the countdown's density, the tool is wrong, fix it before proceeding).*

**WP-2 — FURNITURE CORE.** Extract per §2.1 with **scenography as component defaults** (a `.mx-card` ships tilted/taped/shadowed unless explicitly flattened; scene-ground utilities in 13-chrome; Law 8 floors in CSS). Real-`<img>` ephemera contract (F-6). Simultaneously prune pre-flight.md / specials.md / component-contracts.md / Gate-1E to the live system only (F-13) — same WP, not deferred.
*Gate: a re-dressed copy of a shipped Deep Dive and a re-dressed holiday copy both render through the core; measure-issue on the DD re-dress: ≥0.7 ev/screen, no 3-screen dead run; PARITY GATE (Part 5) on the DD re-dress; docs contain zero deleted-class references (grep list committed); OWNER CHECKPOINT #1: send before/after screenshots, wait for sign-off before WP-3+.*

**WP-3 — SKINS + BUNDLING + DARK/PRINT.** Editorial rebase (delete `:not()` chains, split 32, delete Lookahead), event skin, transmission alias block (weekly byte-identical — `verify-weekly-golden.sh` green), per-format manifests in both stitchers, dark + print for core+skins, self-hosted fonts.
*Gate: bundle budgets met; one masthead per bundle; weekly golden byte-identical; dark/print/network-disabled renders pass; parity gate re-run on the WP-2 fixtures under each skin.*

**WP-4 — MOTIF MECHANISM + PACKS.** Generalize layer 33 (`data-act`, `var(--mx-glyph)`), pack JSON schema + validators (AA contrast, whitelist, byte caps, act arithmetic), build reference packs: one trip pack, one matchday/Season-Review pack, one dossier pack. Goldenize.
*Gate: pack swap re-themes the same fixture with zero repo-CSS diff; a seeded-bad pack (failing contrast, off-whitelist font, oversized art) is rejected by the validator.*

**WP-5 — MOTION.** Implement tiers + signature moments + object settles per Law 5, re-scoped opt-in.
*Gate: scroll-capture video or frame-sequence at both widths shows tier-appropriate motion firing; reduced-motion render shows none; JS-off render content-complete; the flat negative fixture still fails.*

**WP-6 — DETERMINISTIC PIPELINE.** Format skeletons (acts, chapters, structural hooks, per-chapter `visual_events` in the Law-2 vocabulary), planned-density + Law-3 floors in `validate-chapter-plan.py`, `stitch_specials.py` (writer fills interiors only; per-skin vocabulary gate; chrome unrepresentably correct), rendered gates from WP-0 wired into publish-gate, **editorial-timing sanity check** (a plan whose format requires a concluded event fails validation if the event hasn't concluded by publish date — attempt #2 scheduled a Season Review the morning BEFORE the final).
*Gate: end-to-end test issue on a test topic passes all gates; post-publish toolchain (extract-issue-meta, build-archive-manifest, extract-covers, inject-pwa, post-publish.sh) runs clean on it; archive card/cover/PWA cache verified; seeded-bad plans (under-floor words, missing events, wrong-date format) all rejected.*

**WP-7 — FIRST LIVE SPECIAL.** Full content per Part 7 (real research bundle, Law-9 voices, format's killer feature — for Season Review: The Scorecards, results/bracket furniture from the matchday kit, awards tied to moments, the reader's angle). Full gate suite + Part 5 parity + OWNER CHECKPOINT #2: cover + two mid-scroll shots (both widths) sent for sign-off BEFORE publish.
*Gate: everything green with evidence; owner sign-off recorded.*

**WP-8 — WEEKLY DENSIFICATION.** Core furniture into the weekly via alias block + skeleton/band changes (mockup spread 2 reference): fixtures ledger, ticket object, standings card, quote-objects, one chart card. Identity untouched. Golden regenerated once, deliberately.
*Gate: measured 0.8–1.0 ev/screen; parity-gate verifier confirms "unmistakably Transmission"; new golden committed; full §craft pass.*

**WP-9 — CLOSEOUT.** F-1…F-20 table with evidence links; fresh-subagent re-verification sweep of every gate (Part 6 §audit); remaining items explicitly listed out-of-scope-with-reason. Nothing silently dropped.

---

# PART 5 — THE DESIGN-PARITY GATE (the check against what we want)

Runs: end of WP-2, WP-3, WP-5, WP-7, WP-8 — and before ANY live publish, forever. This is the gate that answers the owner's question — "is this what we had in mind?" — before the owner has to.

**Protocol:**
1. **Inputs to the verifier:** (a) the candidate's screenshot set (both widths, 8 smooth-scroll depths, cover, one dark render — produced by the harness, not hand-picked); (b) the frozen WP-1 reference packs (countdown, field guide, mockup); (c) Part 1 verbatim; (d) the candidate's `metrics.json`. NOTHING ELSE — no build context, no diff, no builder notes, no knowledge of what changed or what "should" pass.
2. **Verifier is never the builder.** Spawn fresh, with different-model diversity from the builder where available. Two independent verifiers for WP-7/WP-8 (pre-publish); one elsewhere.
3. **Scorecard:** each of the twelve Laws scored PASS/FAIL **with quoted visual evidence per score** (screenshot filename + what is seen). Unanswerable = FAIL, not skip. Plus three verbatim questions, answered in one sentence each before any scoring: "Objects on a surface, or boxes on a page?" · "Does the scroll travel, or is it one flat ground?" · "Would a reader who loved the trip countdown recognize this as the same magazine's craft?"
4. **Side-by-side requirement:** the verifier must place candidate and reference screenshots at the same width next to each other for Laws 1, 2, 4, 7 and state the differences explicitly. Comparing from memory = protocol violation.
5. **Pass criteria:** all twelve Laws PASS. A single FAIL blocks the gate. There are no waivable laws; scope exceptions exist only where a Law itself states one (e.g., editorial-skin restraint cap in Law 11).
6. **Disagreement/spot-check:** where two verifiers disagree, or on every WP-7/8 run regardless, the ORCHESTRATOR personally opens ≥6 of the candidate screenshots and records its own one-paragraph verdict in the evidence ledger. The orchestrator never relays a verifier PASS it hasn't spot-checked.
7. **Calibration proof:** before its first live use, the parity gate must fail both retained negative fixtures (the flat season review, the stub) and pass the countdown reference. A parity gate that hasn't demonstrated both verdicts is not yet a gate.

---

# PART 6 — EVIDENCE & ANTI-GAMING PROTOCOL

1. **Evidence ledger:** `docs/design-system-unification-EVIDENCE/<wp-id>/` — screenshots (harness-produced, all depths, never curated), `metrics.json`, validator outputs, parity scorecards, owner-checkpoint records. The PROGRESS doc links every gate claim to ledger paths. **A gate claim with no ledger entry is by definition false.**
2. **Measured, never asserted:** density, distribution, word counts, overlap, truncation, motion census come from `tools/measure-issue.mjs` output committed to the ledger — never from a subagent's prose estimate.
3. **Builder/verifier separation:** the subagent that built a WP never runs its gate. Verifiers receive only the Part 5 inputs.
4. **Negative fixtures forever:** the gate suite runs the retained bad artifacts on every WP gate; if any negative fixture ever passes any gate, stop — the gate regressed, and all PASSes since its last calibration are void.
5. **False-green protocol:** any PASS later shown false (by owner, orchestrator spot-check, or audit) voids its WP gate, requires a fresh-subagent re-run of that WP's full gate, and a fresh-subagent audit of every prior WP's ledger (do the artifacts actually show what the scorecards claim?). Record the incident in PROGRESS under "False greens" — hiding one is the terminal offense against this spec.
6. **Orchestrator duties:** maintain PROGRESS per WP (shipped / gate evidence links / decisions where spec was silent / honest known-gaps); spot-check per Part 5 §6; never mark a WP done with a failing, skipped, or unproven gate "to keep moving"; sequence so the skill files are never mid-refactor when an unattended publish run could fire.
7. **Definition of DONE for the engagement:** all WP gates green with ledger evidence · F-1…F-20 closeout table complete · parity gate passed on one live special AND the densified weekly · both owner checkpoints signed off · no open false-green incidents.

---

# PART 7 — EDITORIAL & CONTENT REQUIREMENTS (per issue, enforced at plan + publish)

1. Law-3 word floors; Law-9 voice minimums and lanes; quote/fact dedupe (≤2 renderings / ≤2 tellings).
2. **Format-date sanity:** Season Review requires the season/tournament CONCLUDED before publish date; Countdown requires the event in the future; Rewind bounded to its period. Wired into plan validation (WP-6).
3. Killer features are mandatory, not optional: Deep Dive = The Argument + Keep Digging; Season Review = The Scorecards (8–12) + awards-tied-to-moments + what-changes-next; Rewind = The Memory Test (graded next period); Versus = criteria-first + per-round verdicts + committed conditional verdict; Next = the On-Ramp; Guide = One-Week Plan (beginner) / The Lens + Cheat Sheet (category). An issue missing its killer feature fails plan validation.
4. Personalisation floor: ≥1 reader-specific bridge per special (drawn from state: clubs, podcasts, trips, training); Rewind/Season Review include the reader's own angle as a chapter-level element, second person, never "the reader's".
5. Images: local-first (`assets/cached/`), credited; sport = furniture-first (football/golf photo-locked; fixture ledgers, brackets, scorecards, sparklines); gaming/TV/history/trips = photo-capable per press-kit/archive economics; every stat named-source or confidence-tagged; prices/hours carry "as of <date>".

# PART 8 — ORIENTATION (for every subagent's context)

**Read order:** this spec → `docs/special-editions-review-2026-07-18.md` (validated evidence base: density table, CSS autopsy ~83/9/8% universal/parametric/disposable, quality-log audit) → `docs/mockups/unification-furniture-kit-mockup.html` in a browser → both holiday issues RENDERED at 390px → `scripts/stitch_weekly.py` + `references/format-skeletons/weekly.json` (the deterministic model) → `scripts/stitch-issue.sh` (the concatenator being replaced).
**Component→source map:** token block 36:46–89 · masthead 36§02 · covers 36§03/03b · countdown grid 36§04 · halves/acts 36§06–07 · transit 36§08 · polaroid 36§09+41 · postcard 36§10+41 · stamp 36§11+41 · anchor 36§12 · zig-zag entries 36§12b/§13 · marquee 36§15 · chalkboard 36§16 · meal-slot ranked entries 40 (the `--slot-*` double-token pattern = extraction template) · ticket/coaster/banner/pull-object 41 · stat band 43 · drop cap/fleuron/ribbon 44 · responsive 37 · motion 38/39 (crossfade endpoint colors → act tokens) · venue mechanism 33 (venue token VALUES live in the countdown issue head ~lines 107–113) · DISPOSABLE: 42 all, Pieck/balloon/silhouette blocks in 36, 33's two glyph data-URIs.
**Prior-attempt branch** `claude/design-system-unification-phase-0-qo2f9s`: contains reusable WP work (core CSS files, motif validator, render tools, manifests) AND the false-green Season Review. Audit before reuse; nothing from it is trusted until it passes the WP-0 gate suite. Its 542-word artifact and the flat re-dress become negative fixtures.
**Environment:** Chromium `/opt/pw-browsers/chromium`, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, never `playwright install`; playwright module at `/opt/node22/lib/node_modules/playwright`; serve over HTTP not file:// (root-absolute asset paths); block/ignore the service worker (it hijacks navigations); judge reveal-blankness only from smooth-scroll captures; outbound network is proxied and Google Fonts has been observed blocked — self-host.
**Publication continuity (owner-amended):** the owner may direct immediate live cutover; absent that, old pipeline stays the live path until a WP fully lands. Either way ONLY green-gated artifacts publish; the sole fallback is full old-system rendering — never a partial new-system artifact.
