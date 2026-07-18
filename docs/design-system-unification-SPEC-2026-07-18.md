# THE SIGNAL — DESIGN SYSTEM UNIFICATION SPEC

**Date:** 18 July 2026
**Status:** APPROVED DIRECTION — ready for implementation by a fresh instance
**Owner intent (verbatim steer):** the holiday-system quality (Field Guide, Countdown 2026-06-14) becomes the basis for ALL weeklies and specials, de-themed, without losing content. "I don't want some half designed crap shipping tomorrow I need to keep going back and pointing out issues. The whole design needs to have quality and consistency baked in."
**Companion docs:** `docs/special-editions-review-2026-07-18.md` (the validated review this spec grows out of). Read it first.

---

## 0. HOW TO WORK ON THIS (read before anything else)

This spec is the contract. The implementing instance must follow the phase gates in §10 — **no phase's output touches a live issue until that phase's full acceptance checklist is green and the rendered-review protocol (§9) has been run and passed.** The failure mode this spec exists to prevent is exactly the one in the project's history: systems shipped at 80%, defects found by the reader, spec documents left contradicting the code. Specifically:

1. **Never trust "it should work" — render it.** Every visual change is verified by loading real HTML in the sandbox Chromium (`/opt/pw-browsers/chromium` via Playwright, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, never `playwright install`), screenshotting at 1440×900 AND 390×844, and **reading the screenshots**. Serve over local HTTP, not `file://` (root-absolute `/assets/cached/` paths break under file://; the service worker also hijacks same-context navigations — use fresh contexts).
2. **Never trust the self-reported quality log as acceptance evidence.** `state/quality-log.jsonl` was independently audited on 2026-07-18 and found inflated ~+0.4 overall (+1.4 on its flagship claim), with density rubber-stamped at 5 and no live score ever below the repair threshold. Acceptance = mechanical gates + rendered review + the goldens, not a score.
3. **Update spec docs in the same change as the code.** Half the current mess is spec files teaching a component system deleted in v8.21 (see F-13). If a change makes a doc stale, fixing the doc is part of that change, not a follow-up.
4. **The weekly: identity protected, densification IN SCOPE.** Read this precisely — it has been misread once already. The owner's goal is holiday-bar quality for "ALL weeklies and specials"; the weekly is not exempt from the upgrade. Three distinct guarantees with different lifetimes:
   (a) **Transmission's IDENTITY is protected permanently** — palette, type stack, the 800px printed-object chassis, the radio conceit. The weekly never becomes a skin of the event chassis, and `weekly/00-transmission.css` is never redesigned as part of this work.
   (b) **During Phases 0–5 the weekly's rendered output is FROZEN** — `scripts/verify-weekly-golden.sh` must pass byte-identical after every phase. This is a tripwire so system-building can't accidentally break Sunday's issue, not a statement that the weekly stays as-is forever.
   (c) **In Phase 6 the weekly DELIBERATELY gains core furniture** — ledgers, ticket/ephemera objects, quote-objects, chart cards — through the Transmission alias block and skeleton/band changes, to hit its §6 density budget (0.8–1.0 events/screen). The mockup's spread 2 (Touchline: match ticket, fixtures ledger, GC standings card — unmistakably still the weekly) is the reference for what this looks like. The golden is then regenerated ONCE, intentionally, as a gated part of that change, and the §9 protocol runs on the new golden.
   Net: "the weekly must not change" is true only of its identity and only mid-build. A weekly that looks identical in density after Phase 6 means the work is NOT done.
5. **When a decision isn't covered here, prefer the restrained option** and log the decision in the progress doc (§11). Editorial specials keep bookish gravitas; the failure mode to avoid is every issue looking like a theme park.

---

## 1. EVIDENCE BASE (measured, 2026-07-18 — do not re-litigate)

Rendered-review density measurements (designed visual events per screen / words per screen):

| Issue | Events/screen | Words/screen |
|---|---|---|
| Countdown 06-14 (holiday system) | **1.69** | 139 |
| Field Guide 05-17 (holiday system) | **1.06** | 209 |
| Weekly 07-13 (Transmission) | ~0.9 (uneven) | ~180 |
| Rewind 07-12 (editorial special) | 0.75 | ~230 |
| Deep Dive 06-30 (editorial special) | **0.37** | 255 |

CSS autopsy of the holiday layers (33, 36–44; 4,931 lines / 198.3 KB total):
- **~83% (~4,100 lines) UNIVERSAL** — theme-free furniture already reading only `--hol-*` tokens, bare-class selectors (`.hol-polaroid` etc., only the token block and chrome-disable block are body-scoped). This bucket IS the quality: polaroid/postcard/stamp/ticket/coaster ephemera, ranked-entry plates + tier pills, facts `<dl>` ledgers, stat bands, quote objects, six-face type roles, marquee, act/transit rhythm, all motion.
- **~9% (~460 lines) PARAMETRIC** — reusable once hard-coded values become inputs: the token block values, venue-theming mechanism in 33 (per-venue ground/accent/watermark — mechanism is exactly a motif-pack runtime, crippled only by `[data-venue="efteling"]`-style closed enumeration and data-URI art baked into rules), half-ground recipes, motif watermark layers, act-2 recolour blocks, palette-crossfade endpoint colors.
- **~8% (~370 lines) DISPOSABLE** — destination art: all of 42 (savannah), giraffe/elephant band, Anton Pieck trees, filigree corners, balloons, the two venue glyph data-URIs (10.2 KB), plus castle SVG in issue markup and `--eft-*`/`--bee-*` values defined in issue heads.

Production economics: the Countdown took 22 pipeline calls vs 16–22 for a weekly. Holiday quality was NOT more machine — it was ~70 verified press-kit images (a trips-only luxury), the verification chain (now standard), and discipline already written into the spec but unenforced.

A working proof-of-concept mockup demonstrating the de-themed kit in three motifs (Byzantium dossier / weekly Touchline / Rewind scrapbook) is committed at **`docs/mockups/unification-furniture-kit-mockup.html`** — self-contained (fonts embedded as data URIs, hence ~2.1 MB), screenshot-verified at 1440px and 390px, zero photography. Open it in a browser before writing any core CSS: its techniques (token-scoped furniture, act shifts, CSS-drawn objects — the solidus coin, ticket stub, memory cards — one shared kit restyled per spread by a scoped custom-property block) are the reference implementation for §4. Known shortfalls vs the real holiday issues, so you don't inherit them as targets: it runs ~0.7–1.0 events/screen (not 1.69), has no scroll motion, and spread 2 has unbalanced whitespace under the ticket column that a production pass should fill with another ephemera object.

---

## 2. NAMED FAILURE REGISTRY

Every failure below is real, evidenced, and **must be fixed by (or impossible after) this work**. Each carries an acceptance criterion (AC). The implementing instance must produce a final table mapping each F-# to the commit/change that resolved it.

### Design-system failures
- **F-1 — Density collapse in editorial specials.** Deep Dive 0.37 events/screen; 3,000–5,000px unbroken paragraph runs; three of four random scroll depths land on bare text columns. *AC: planned + rendered density ≥ the §6 floor for every format; density validated mechanically per §8.*
- **F-2 — One cover template across editorial specials.** Deep Dive / Rewind / Next covers are the same dark card + white serif + orange italic. `25-special-cover.css` hard-codes `--accent-ember` on `.cover-eyebrow`, `.cover-title em`, `.cover-meta strong` for every format, so per-format accents only tint the background pool; Rewind/Shortlist/Next all share default rose anyway. *AC: covers read `var(--accent)`/motif tokens; each active format has one owned cover gesture; no two formats render identical covers.*
- **F-3 — Dual `.mast` contract.** `21-chrome.css:14` (fixed grid, mix-blend-mode) vs `28-special-masthead.css:22` (flex) — both ship in every special. *AC: exactly one masthead component in the shipped bundle of any issue.*
- **F-4 — The `:not()` selector tax.** 176 occurrences of `body.is-special:not([data-special="countdown"]):not([data-special="field-guide"])` across layers 23–32; every new format multiplies the chain. *AC: zero opt-out `:not()` format scoping in the new layers; scoping is opt-in via `body[data-skin]`.*
- **F-5 — Full-bundle shipping.** Every special inlines all ~444 KB of CSS 00–44 (`stitch-issue.sh:330-334` globs everything): deep dives carry savannah giraffes; every special carries ~300 lines of RETIRED Lookahead styles (the most-styled format in `32-special-format-flair.css`). *AC: per-format manifests; an editorial special ships ≤ ~120 KB CSS, an event special ≤ ~160 KB; Lookahead CSS deleted; legacy 00–22 ships nowhere (archived issues carry their CSS inline — verify one before assuming, then rely on it).*
- **F-6 — Ephemera accessibility hole.** Countdown: 92 CSS `background-image` declarations vs 4 real `<img>`; Field Guide: 80 vs 14. Screen readers see almost nothing. *AC: the extracted ephemera components take a real `<img>` child (`object-fit: cover`) as the primary contract, `role="img"` + `aria-label` as the documented fallback; the image gate counts them.*
- **F-7 — No dark mode, no print for specials.** Transmission has token-level dark (`00-transmission.css` §~833); layers 23–44 have zero `prefers-color-scheme` and no `@media print`. *AC: the furniture core and both skins have token-level dark variants and a minimal print sheet (hide chrome/progress, un-dark covers), verified by rendered screenshots in dark emulation.*
- **F-8 — Mobile chrome shatter.** At 390px the Rewind/Versus/Next sticky headers wrap into overlapping debris colliding with the back pill; `.marginalia` overhangs the viewport ~10px (clipped) and crushes to one-word-per-line on Next desktop; Countdown poster cover collides with its own subtitle/meta (worst mobile page in the archive); postcard quote strips crush to ~170px columns. *AC: single-line responsive header ≤480px; no component overhang; poster cover contained at both widths; postcards stack full-width <480px; all verified by 390px screenshots.*
- **F-9 — Cream-act measure blowout.** Some Countdown act-2 paragraphs run ~1,270px edge-to-edge. *AC: global body-copy measure cap ~68ch enforced in the core.*
- **F-10 — Motion locked to two formats + spec lies about it.** Motion layers (38/39, ~990 lines) are body-scoped to countdown/field-guide; meanwhile the editorial spec's "no motion in the non-holiday system" claim is already false (v8.24 reveals/parallax exist). *AC: motion re-scoped to opt-in `[data-motion]` tiers per §5; spec text matches reality; `prefers-reduced-motion` and JS-off-renders-complete verified for every tier.*
- **F-11 — Token namespace drift.** Three+ `--paper`/`--ink`/`--rose` definitions with different values (editorial 23, Transmission, site `styles.css`), venue tokens defined in issue heads. *AC: one `--mx-*` contract (§4.2); skins alias into it; no same-name/different-value collisions in any shipped bundle.*
- **F-12 — Type-size floor violations.** Mono micro-labels at 0.66–0.7rem (≈10.5–11.2px). *AC: ≥0.72rem floor in the core; grep-verifiable.*

### Process/spec failures (this work must not reproduce them)
- **F-13 — Spec rot.** `references/pre-flight.md` §3 gives copy-paste snippets of classes removed in v8.21; `spec/specials.md` mandates four sections of deleted machinery its own removal list bans; compliance Gate 1E greps police the dead vocabulary while live components have none; `component-contracts.md` has duplicate sections and a "Universal Cover" contract banning markup `specials.md` mandates; `spec/triggers.md` holds three verbatim copies of the trigger stack. *AC: after each phase, every touched doc teaches only the live system; Gate 1E rewritten for the new components; the S7/S8 pruning completed as part of Phase 2, not deferred again.*
- **F-14 — Hand-authored chrome shipped a template placeholder.** The Rewind masthead reads literally `Issue #[N] · 12 July 2026`; it also shipped past a failing image gate. *AC: specials get deterministic stitcher-owned chrome (§7); placeholder tokens (`#[N]`, `[N]`, `ch\d+-\d+` in prose, `viz_\d`, "research bundle") are hard-fail greps in the publish gate.*
- **F-15 — Unused designed components.** `.cheat-sheet` exists only in a CSS comment; the B2 signature infographic is a standing option never exercised. *AC: cheat-sheet instantiated as a real component in the core with a contract + skeleton slot.*
- **F-16 — Dead external imagery.** Next: 10/10 images are dead external hotlinks; Rewind has a text-wrap hole around one. *AC: local-first images enforced (mirror step mandatory); validator fails a non-`assets/cached/` `src` outside documented exceptions.*
- **F-17 — Getty/Shutterstock laundered as "press_kit"** in `references/image-source-types.json`. *AC: reclassified as restricted; diversity gate warns.*

---

## 3. TARGET ARCHITECTURE

```
L0  css/core/            FURNITURE CORE (extract of the ~4,100-line universal bucket; est. ~3,300 after dedupe)
    00-contract.css      --mx-* token contract + neutral defaults + six type roles
    10-ephemera.css      framed-object chassis: polaroid→"pinned card", postcard→"mail card", stamp roundel,
                         ticket stub, coaster, tape/pin/staple fasteners, hand-caption, credit line
    11-ledgers.css       facts <dl> rows, ranked entries + rank chips, tier pills, stat bands, chalk/price rows,
                         cheat-sheet (NEW — instantiate F-15)
    12-plates.css        numbered plates, anchor blocks, zig-zag entry systems, don't-miss chips
    13-chrome.css        ONE masthead, cover scaffolds (incl. poster variant), kicker, act opener, transit band,
                         marquee, countdown grid, drop cap/fleuron/ribbon
    14-motion.css        38+39 re-scoped to [data-motion="calm|event"] opt-in tiers (§5)
    15-responsive.css    37 generalized; the F-8/F-9 fixes live here
L1  css/skin-*/          FAMILY SKINS (exactly one per issue)
    skin-transmission/   = existing weekly/00-transmission.css BYTE-IDENTICAL + a ~20-line alias block
                           (--mx-paper: var(--paper); …). The weekly is NOT a skin of the holiday chassis.
    skin-editorial/      = 23–31 rebased under body[data-skin="editorial"]; :not() chains deleted (F-4);
                           32 split (cross-format picks/grids → core; per-format killer features stay;
                           Lookahead deleted); motif surface CAPPED at palette-arc + one pattern + one cover gesture
    skin-event/          = the holiday chassis: halves rhythm, act-opener scale, transit, hype density norms
L2  motif pack           per-issue token block + ≤4 art slots, generated from JSON (§4.3); inline in the issue;
                         NEVER new CSS in the repo per issue
```

Class naming: the extraction renames `hol-*` → neutral `mx-*` (or similar) names. Zero archive risk: shipped issues carry their CSS inline. The weekly's holiday-marker bans in `weekly.json.visual_consistency` stay in force and must never fire against core class names — pick names accordingly.

### 4.2 The `--mx-*` token contract (~30 custom properties)
Palette: `--mx-paper --mx-ink --mx-accent --mx-accent-2 --mx-support-1 --mx-support-2 --mx-hair` per act (`section[data-act="2"]` re-declares). Type roles (whitelist of ~15 families): `--mx-t-chunk --mx-t-tall --mx-t-script --mx-t-hand --mx-t-serif --mx-t-mono`. Art slots as custom properties: `--mx-pattern` (tiled watermark SVG), `--mx-glyph` (stamp/watermark, `currentColor`-based, fed via `mask-image: var(--mx-glyph)` — this single indirection replaces all per-venue rules in 33), `--mx-band` (optional edge scene), cover plate via markup injection. Machine checks at plan time: WCAG AA contrast for every act's paper/ink and accent/ground pairs; font whitelist membership; art-slot byte caps; `currentColor` requirement on SVG slots.

**Font delivery — decide in Phase 2, recommendation: self-host.** Whitelisted families should be subsetted woff2 under `assets/fonts/` with `@font-face` in the core, not Google Fonts `<link>`s: the render environment has already demonstrated Google Fonts being blocked at runtime (the reference mockup had to embed fonts as data URIs to survive), the PWA promises offline reading via `sw.js`, and shipped issues should not carry a third-party runtime dependency. Whatever is decided, the §9 protocol must include one render with external network disabled — text must remain fully readable on fallback stacks.

### 4.3 Motif pack JSON (planner-facing; validated)
```json
{ "id": "byzantium-dossier-2026",
  "acts": [ { "paper":"#F4ECDC","ink":"#2B1B33","accent":"#8E1F3B","accent_2":"#C9962E","ground":"paper" }, { } ],
  "type": { "chunk":"…","tall":"…","script":"…","hand":"Caveat","serif":"…","mono":"…" },
  "pattern":"mosaic-tessera.svg", "glyph":"coin-stamp.svg", "band":null, "cover_plate":null,
  "grain":"none", "kit":"dossier", "motion":"tier0" }
```
`kit` selects the ephemera vocabulary (§4.4); `motion` the tier (§5). Reference packs to build and goldenize in Phase 4: the next trip (event skin) and one non-travel proof (Season Review or F1-class, editorial/event as designed).

### 4.4 Ephemera kits (one per issue; 2–3 object types max per issue)
All kits are fictions over the same chassis (frame + content window + fastener + hand caption + credit). Approved vocabulary:
- **dossier** (history deep dives): archival index card, telegram/dispatch slip with stamped time, file-folder tab dividers, wax-seal letter (component exists in template-parts), map fragment, museum catalogue label, coin/medal roundel, margin annotations.
- **broadcast** (weekly): wire-brief chips, ticket stub, tuning dial, rolodex card, library due-date card (Bookmark), till receipt (The Desk), postage-stamp corner (The Letter), forecast chips (Radar).
- **scrapbook / annual** (Rewind, Season Review): taped memory cards, photo-corner mounts, calendar tear-offs, sticker-album cells (filled vs empty), report-card grades, certificates/rosettes, cassette/VHS labels.
- **matchday** (football): match ticket, fixtures ledger, league-table card, SVG lineup dot-pitch, programme cover card, pennant band, turnstile stamp, clipping card.
- **scorecard** (golf majors — NOTE owner steer: football is the lead sport; golf majors and marquee events rank ABOVE F1; check the profile interest weights reflect this): 18-hole scorecard ledger, leaderboard card (red/black numbers), hole diagram SVG with yardage, yardage-book page, trophy stamp.
- **paddock** (F1, when used): timing tower, track map SVG, tyre chips, pit board.
- **inventory** (gaming): cartridge/box label, achievement badges, save-file card from real playtime, spec ledgers.
- **cinema** (screen & sound): admit-one stub, film-strip frames, TV-guide row, setlist card, sleeve corner.
- **library** (books): bookplate, catalogue card, due-date slip.
- **logbook** (training/personal): race-bib card, split-times ledger, route ribbon, kit checklist.

---

**SCENOGRAPHY RULE (added 18 July after the first flat-boxes failure):** furniture is objects on a surface, not boxes on a page. The first new-system artifact rendered every component as an upright hairline-bordered rectangle — flat, unrotated, untextured, unlayered — and read as "a load of squares" (owner's words). Mechanically failable requirements: (1) every ephemera object carries >=2 of {rotation (1-3deg), fastener (tape/pin/stamp), shadow or paper texture, scene-ground behind it, overlap with a neighboring element}; (2) every act has a SCENE ground (gradient sky, starfield, pattern field, grain — cf. the countdown's starfield sitting behind plain body text), never a flat single-color fill; (3) at least one object per chapter breaks the column grid (tilted, bleeding, or overlapping); (4) the §9 fresh-eyes reviewer answers one added question verbatim: "objects on a surface, or boxes on a page?" — 'boxes' is a gate FAIL. The reference bar is issues/signal_countdown_2026-06-14.html rendered at 390px: even its plainest text viewport sits on a scene.

## 5. MOTION GRAMMAR

Motion is a motif-pack field, opt-in, tiered. Attach to furniture, never body text.
- **tier0 print-still** (Deep Dive default): hairline draw-in, faint ghost-numeral parallax. Nothing else.
- **tier1 calm** (weekly, Rewind, Next): existing rise-on-scroll; object settles (card "tape-down" ~1° settle, ledger rows tick in sequentially, sparklines draw).
- **tier2 event** (trip issues, Season Review): stamp-slam, marquee, flips, act palette crossfade (generalize the `--hm-edge` dial — the mechanism is generic; only endpoint colors are baked today).
Signature moment per format (exactly one): Versus = verdict stamp slams per round + scoreboard tick; Season Review = leaderboard rows climb; Rewind = Memory Test columns reveal in sequence; Weekly = dial needle sweep on band entry; Countdown keeps flips.
Hard rules (each is a gate): `prefers-reduced-motion` honored by every animation; JS-off renders 100% complete content; no scroll-jacking; no motion on running text; scroll-reveal must not leave blank frames on teleport-scroll worse than today (test both smooth and jumped scroll in the rendered review).

---

## 6. DENSITY & PACING BUDGETS (planned, validated, rendered-verified)

| Format | Events/screen floor–target | Words/screen max |
|---|---|---|
| Weekly | 0.8–1.0 | 210 |
| Deep Dive | 0.7–0.9 | 220 |
| Rewind / Season Review | 0.9–1.1 | 210 |
| Versus / Guide / Next | 0.8–1.0 | 210 |
| Trip specials (Countdown/Field Guide) | 1.0–1.3 | 210 |

Rules: no more than 4–5 consecutive paragraphs without a designed visual event (figure, ledger, quote-object, ephemera, stat band); body-copy measure ≤ ~68ch; every Deep Dive/Rewind/Next ends with a cheat-sheet. 1.69 was a ceiling that took ~70 press-kit images — never a target outside trips. Sport density is furniture-first (football/golf are photo-locked domains); photo density is for gaming/TV/history/trips.

**Length floors are part of the density gate (added 18 July after the first gaming attempt):** events/screen achieved by cutting length below the format's floor is a FAIL, not a pass. Word floors (body copy, excluding chrome): Weekly 6,000 (exists); Deep Dive 8,000; Season Review 6,500; Rewind 7,000; Versus 4,500; Guide 3,500; Next 3,000; Countdown 4,500; Field Guide 6,000. `validate-issue.py` must enforce these for `data-mx` issues alongside the density gate. Cautionary example: the first "gate-green" new-system issue (19 July Season Review draft) hit "2.81 events/screen" at **542 words** — a stub, not an issue. Also add to the scaffold-grep class: internal strategy vocabulary in reader copy ("furniture-first", "motif pack", skin/kit/phase names) — the same leak class as `ch1-1`, new vocabulary.

**Visual-event counting rule (the density gates are unenforceable without one — use this):** a visual event is one of: captioned figure/`<img>`, ephemera object card, ledger/table block, stat band, quote-object (styled blockquote with named source), numbered plate/act opener, self-made chart/diagram, marquee or act-divider band, cheat-sheet. NOT events: drop caps, hairline rules, inline bold, unstyled blockquotes, subheads. Screens = rendered page height ÷ 900px (desktop) as measured in the §9 protocol; planned-density estimate at plan time = target words ÷ 250 per screen. A cluster of 2–3 ephemera in one viewport counts per object, but the ≥1-per-1.5-screens floor is about *distribution* — the validator must also flag any 3+-screen run with zero events, or the average can be gamed by front-loading.

Trust-rule intersection (owner steer, non-negotiable): **the magazine has arguments, not experiences.** Three lanes: EXPERIENCED (sensory/being-there — never first-person; only named verbatim quotes; no invented consensus), ANALYZED (own opinion allowed with working shown), CURATED (selection/reader-fit fully allowed). Every borrowed voice is also furniture (quote-object with named source) — density and trust reinforce. Dedupe: each quote rendered once (twice max), each fact twice max.

---

## 7. PIPELINE REQUIREMENTS

1. **Format skeletons for specials** (`references/format-skeletons/<format>.json`) modeled on `weekly.json`: acts, chapters, structural hooks (`data-act`, `data-chapter`, `data-role="transit"`), invariants (one transit max; acts 1–3; no two consecutive same-ground chapters), and **per-chapter `visual_events` arrays** in a closed vocabulary (`ledger | ephemera_cluster | plate_run | stamp | pull_object | numbers_band | act_break | marquee | menu | cheat_sheet`).
2. **Planned-density validation** in `validate-chapter-plan.py`: computed events per estimated screen must meet §6 floors; motif pack validated (contrast, whitelist, byte caps, act arithmetic); the format vocabulary reconciled everywhere (`guide` and `next` added; `blueprint` deleted) — a spec-compliant plan for ANY active format must pass Phase 4 (this is currently false for Guide/Next).
3. **`stitch_specials.py`** mirroring `stitch_weekly.py` ("the writer cannot affect structure, only fill content"): stitcher owns cover, masthead, act openers, transit, plates, motif token block, colophon; writers fill chapter interiors; per-skin vocabulary gate rejects out-of-skin classes. This makes F-14 unrepresentable.
4. **Per-format CSS manifests** in the stitchers (core + one skin + motif block). Kill the `assets/css/*.css` glob.
5. **Rendered-density + hygiene gate** in `validate-issue.py`: count furniture/`<img>` per estimated screen post-stitch; hard-fail scaffold tokens (F-14 list), non-local image src (F-16), duplicate `<img src>` with differing alts, quote text appearing >2×.
6. **Goldens:** keep `verify-weekly-golden.sh` green and byte-identical throughout; add golden fixtures per skin and for the two reference motif packs; add a `verify-specials-golden.sh` equivalent.

---

## 8. ACCESSIBILITY & CRAFT FLOOR (applies to every component the day it's extracted)

Real `<img>` in ephemera (F-6); WCAG AA contrast enforced per act; type floor 0.72rem (F-12); measure cap 68ch (F-9); dark mode + print (F-7); reduced-motion + JS-off complete (§5); no horizontal document scroll at 390px; single-line mobile chrome (F-8); wide content scrolls inside its own container; alt text or `aria-label` on every meaningful visual.

---

## 9. RENDERED-REVIEW PROTOCOL (mandatory per phase; no exceptions)

1. Build the phase's test artifact — **prototype on COPIES of shipped issues** (e.g. re-dress `signal_deep-dive_2026-06-30.html` with the new core), never on a live/pending issue.
2. Serve over HTTP; render in Chromium; capture desktop 1440×900 + mobile 390×844: cover, plus viewport shots at ≥4 scroll depths using SMOOTH scrolling (jumped scroll under-triggers reveal observers — re-shoot smooth before judging blankness), plus dark-mode emulation shots, plus a `prefers-reduced-motion` pass.
3. **Read every screenshot.** Check against: density floor, measure cap, chrome integrity at 390px, contrast, no blank frames, no overlap/crush, cover gesture present.
4. Compute the density metric (events/screen) on the rendered DOM and record it in the progress doc next to the §6 target.
5. Run all validators + goldens. `verify-weekly-golden.sh` after every phase regardless of what the phase touched.
6. **Adversarial pass:** run a code review (e.g. `/code-review` at high effort) on the diff AND spawn a fresh-eyes subagent to visually QA the screenshots without being told what "should" be there — its complaints are treated as findings, not noise.
7. Only after 1–6 are green may the phase's output be used in a real issue — and the first real issue using it gets the same protocol run on the shipped artifact before publishing.

---

## 10. PHASES, in order — each independently shippable, each gated

**Phase 0 — Hygiene prerequisites** (small, do first): delete the two public TEST field-guide files; add the scaffold-token greps to the publish gate (F-14 list); fix `image-source-types.json` (F-17); reconcile the format vocabulary (`guide`/`next` in, `blueprint` out) across schema + both validators + specials.md authoring list.
*Gate: greps demonstrably fire on the known-bad archive examples; a Guide chapter plan passes Phase 4 validation.*

**Phase 1 — Quick win, contained:** token shim proving furniture reuse on a COPY of a shipped Deep Dive (map `--hol-*` surface onto editorial tokens; port ledger, quote-object, stamp, numbers band, cheat-sheet). One-line spec amendment so gates don't flag reused classes.
*Gate: rendered density on the re-dressed copy ≥0.7; full §9 protocol; identity still reads paper-and-ink (fresh-eyes agent confirms it does NOT read as a theme-park page).*
*Checkpoint: after this gate passes, SEND THE OWNER the before/after screenshots (desktop + mobile) for a taste sign-off before starting Phase 2. This is the single deliberate human checkpoint in the plan — the extraction is expensive, so the aesthetic direction gets confirmed while changing course is still cheap. Do not accumulate more ask-the-owner moments than this one; everything else is covered by the gates.*

**Phase 2 — Furniture-core extraction + spec pruning (the overdue S7/S8 together, not separately):** build `css/core/` per §3 with neutral names, `--mx-*` contract, F-6/F-9/F-12 fixes baked in; simultaneously prune pre-flight.md, specials.md, component-contracts.md, Gate 1E to teach ONLY the live system.
*Gate: a re-dressed editorial special copy and a re-dressed holiday copy both render pixel-plausibly from the core (screenshot compare vs originals — layout equivalent, no regressions); docs contain zero references to removed classes (grep list in the phase notes); §9 full pass.*

**Phase 3 — Skins + bundling:** skin-editorial rebase (delete `:not()` chains F-4, split 32, delete Lookahead F-5), skin-event, skin-transmission alias block (weekly BYTE-IDENTICAL), per-format manifests in both stitchers, dark/print variants (F-7).
*Gate: bundle sizes within F-5 budgets; one masthead per bundle (F-3); weekly golden byte-identical; dark + print screenshots pass; §9 full pass.*

**Phase 4 — Motif mechanism + reference packs:** generalize 33 (`data-act`, `var(--mx-glyph)` slots), pack JSON schema + validation, build the two reference packs, goldenize them.
*Gate: a pack swap re-themes the same fixture HTML with ZERO CSS diffs in the repo; contrast/whitelist validators demonstrably reject a deliberately-bad pack; §9 full pass on both packs.*

**Phase 5 — Planned density + deterministic specials:** skeletons with `visual_events`, planned-density validation, `stitch_specials.py`, rendered-density gate, motion re-scope to tiers (F-10) with signature moments.
*Gate: a full special generated end-to-end through the new pipeline on a test topic hits its §6 floor in the rendered measurement; `Issue #[N]`-class failures unrepresentable (stitcher owns chrome); reduced-motion and JS-off passes; **the post-publish toolchain runs cleanly on the new-system artifact** — `scripts/extract-issue-meta.py`, `scripts/build-archive-manifest.py`, `scripts/extract-covers.py`, `scripts/inject-pwa.py`, `scripts/post-publish.sh` — and the archive card, cover thumbnail, and PWA pre-cache entries render correctly (these scripts parse issue DOM/metadata; a new structure can break them silently); §9 full pass.*

**Phase 6 — First live issues + failure-registry closeout:** first real special on the new system, then **the weekly densification** — core furniture (ledgers, ephemera objects, quote-objects, chart cards) added via the Transmission alias block + skeleton/band changes to reach the weekly's §6 budget (0.8–1.0 events/screen), identity untouched, mockup spread 2 as reference. This is the one sanctioned change to the weekly's rendered output: regenerate the weekly golden deliberately as part of this gated change (see §0.4c). Produce the F-1…F-17 closeout table with evidence links.
*Gate: shipped artifacts pass §9 (including the densified weekly — measured events/screen ≥0.8, fresh-eyes agent confirms it still reads unmistakably as Transmission); the new weekly golden is committed with the change; the closeout table is complete; every remaining open item is explicitly listed as out-of-scope-with-reason in the progress doc (nothing silently dropped).*

---

## 11. WORKING AGREEMENTS FOR THE IMPLEMENTING INSTANCE

- Maintain `docs/design-system-unification-PROGRESS.md`: per phase — what shipped, gate evidence (screenshot filenames, validator output), decisions made where this spec was silent, and an honest "known gaps" list. The owner should never have to discover a gap themselves; if it exists, it's written down.
- Never mark a phase done with a failing or skipped gate "to keep moving." A skipped gate is a phase failure by definition — the history of this repo (Rewind shipped past a failing image gate; TEST files shipped alongside a weekly) is the cautionary tale.
- Do not redesign Transmission, do not re-theme editorial gravitas away, do not invent new formats — that's out of scope. Scope is: one furniture core, three skins, motif packs, planned density, and the failure registry closed.
- **Publication continuity — OWNER OVERRIDE, 18 July 2026:** the original rule here ("never straddle a Sunday mid-refactor; if a phase can't land cleanly before a Sunday, it waits") is **rescinded by the owner**: *"we build it now. I want tomorrow's issue to look the way we want."* The flip to the new system happens immediately and the 19 July issue ships ON it. This moves the deadline — it does not waive a single gate. The §9 render protocol, the publish gate, the density measurement, and the post-publish toolchain check all run on tomorrow's artifact BEFORE it publishes. One hard rule survives: if the gates are not green at publish time, the fallback is the OLD system rendering in full — never a partially-styled new-system artifact. The gates decide what ships; tonight's job is to make the new system pass them. Phases 5 and 6 execute together for this issue; their gate criteria still apply individually and get recorded individually in the progress doc.
- Anti-goals: no new CSS per issue after Phase 4; no component without a contract in component-contracts.md; no doc left describing the old system; no acceptance based on `quality-log.jsonl`.

---

## 12. ORIENTATION APPENDIX — where everything lives (so the autopsy isn't redone)

**Read in this order:** this spec → `docs/special-editions-review-2026-07-18.md` → `docs/mockups/unification-furniture-kit-mockup.html` (in a browser) → the two holiday issues (`issues/signal_countdown_2026-06-14.html`, `issues/signal_field-guide_2026-05-17.html`) rendered, not just read → `scripts/stitch_weekly.py` + `references/format-skeletons/weekly.json` (the deterministic model to replicate) → `scripts/stitch-issue.sh` (the concatenator to replace).

**Component → source location map** (all under `.claude/skills/the-signal/assets/css/`):

| Component | Source | Extraction notes |
|---|---|---|
| Token block (20 palette + 8 type tokens) | 36:46–89 | Becomes `00-contract.css` defaults; values → motif packs |
| Chrome-disable block | 36:91–157 | DELETE — only exists because of full-bundle shipping (F-5) |
| Masthead band | 36 §02 | Merge with the F-3 resolution — one masthead |
| Cover stage + collage / poster cover + arch text | 36 §03 / §03b | Poster cover has the F-8 collision — fix during extraction |
| Countdown grid + flip | 36 §04 | tier2 motion |
| Kicker strip / half structure + act opener / transit band | 36 §05 / §06–07 / §08 | The act system — `data-act` replaces `.hol-half--two` overrides |
| Motif watermark layers (`theme-celestial/tracks/heat-haze`) | 36 §06b | Mechanism → `--mx-pattern` slot; payloads → packs |
| **Polaroid** (tape, captions, tilts) | 36 §09 + 41 variants | The framed-object chassis; add real `<img>` child (F-6) |
| **Postcard** (ruled quote strip) | 36 §10 + 41 | F-8 mobile stacking fix during extraction |
| **Stamp/seal roundel** | 36 §11 + 41 | tier2 stamp-slam attaches here |
| Anchor feature block / wonders zig-zag + meta `<dl>` / unmissable | 36 §12 / §12b / §13 | The ledger-bearing entry systems |
| Don't-miss chips / marquee / chalkboard menu / meanwhile closer | 36 §14 / §15 / §16 / §17–18 | |
| Meal-slot ranked entries + tier pills | 40 (~300 lines) | Already double-tokened via local `--slot-*` — the extraction template |
| Ticket stub, coaster, banner, pull-quote object | 41 | |
| Stat band, T-minus banner | 43 | |
| Drop cap, fleuron, margin mark, ribbon tab | 44 | |
| Responsive/touch layer | 37 | Generalize into `15-responsive.css` |
| Scroll motion (entrances, parallax, stamp-slam, marquee physics) | 38 (~620 lines) | Re-scope to `[data-motion]` (F-10) |
| Motion extras + act palette crossfade (`--hm-edge` dial) | 39 | Endpoint colors → act tokens |
| Venue theming mechanism (ground/accent/watermark/tag) | 33 | The motif-pack runtime prototype; venue enumeration → `data-act`/slots; venue token VALUES live in the countdown issue head (~lines 107–113), not in the skill |
| Savannah scene / Pieck trees / balloons / venue glyphs | 42, 36 §06b payloads, 33 data-URIs | DISPOSABLE — do not extract |
| Editorial cover (hard-coded ember = F-2) / editorial masthead (F-3) / format flair incl. dead Lookahead (F-5) | 25 / 28 / 32 | 32 splits: cross-format → core, killer features → skin, Lookahead → deleted |
| Weekly bundling + writer-vocabulary gate | `stitch_weekly.py:316–319`, `:367` (`_weekly_sp_gate`) | The pattern `stitch_specials.py` replicates |
| Special bundling glob (the F-5 source) | `stitch-issue.sh:330–334` | Replace with manifests |

**Environment facts the next instance will otherwise rediscover painfully:** Chromium at `/opt/pw-browsers/chromium` (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, never `playwright install`); issues must be served over HTTP (root-absolute `/assets/cached/` paths break under `file://`); the service worker hijacks same-context navigations — use fresh browser contexts; teleport-scrolling under-triggers reveal observers, so judge blankness only from smooth-scroll captures; outbound fetches go through the proxy and Google Fonts has been observed blocked.
