# THE SIGNAL — DESIGN SYSTEM UNIFICATION · PROGRESS LOG

Companion to `docs/design-system-unification-SPEC-2026-07-18.md` (the contract) and
`docs/special-editions-review-2026-07-18.md` (the validated review). This log records,
per phase: what shipped, gate evidence, decisions taken where the spec was silent, and an
honest known-gaps list. Per spec §11, the owner should never have to discover a gap
themselves — if it exists, it is written here.

---

## Phase 0 — Hygiene prerequisites — ✅ COMPLETE (2026-07-18)

Small, do-first hygiene. No CSS/HTML rendering surface, so the §9 rendered-review
screenshot protocol does not apply (nothing visual changed); the applicable §9 items are
"run all validators + goldens" and "weekly golden after every phase regardless" — both run
and green below.

### What shipped

1. **Deleted the two public TEST field-guide files** (spec §10 Phase 0; review rec 32):
   - `test_signal_field-guide_2026-05-17.html` (repo root)
   - `issues/TEST-signal_field-guide_2026-05-17.html`
   - Verified: no code, manifest, or archive reference to either file anywhere in the repo
     before deletion (`grep -rIl` clean), so nothing breaks downstream.

2. **Added the F-14 scaffold-token hard-fail greps to the publish gate.** New
   `check_scaffold_tokens()` in `scripts/validate-issue.py`, wired into the universal check
   list, so it runs inside `publish-gate.sh` → `validate-issue.py` and honours the exit code.
   Matches VISIBLE PROSE ONLY (comments/`<style>`/`<script>` and then all tags stripped), so
   legitimate scaffold anchors (`id="ch2-1"`, `href="#ch2-1"`) and documentation examples
   inside comments never trip it. Patterns:
   - `#[N]` / `[N]` — issue-number placeholder
   - `ch\d+-\d+` — chapter-ID reference narrated in prose
   - `viz_\d+` — research-viz caption token
   - `research bundle` — pipeline phrase in prose
   - `Created with … Computer` — tool-credit leak (see Decisions)

3. **Fixed F-17 — Getty/Shutterstock mislabelled `press_kit`.** In
   `references/image-source-types.json`: added a new `restricted` source type and reclassified
   `media.gettyimages.com` and `image.shutterstock.com` to it. Both diversity consumers —
   `scripts/check-image-diversity.sh` and `scripts/validate-research-bundle.py` — now **warn**
   on a restricted source and **exclude** it from source-type diversity counting (same
   treatment as `unknown`/`ambiguous`). The diversity "menu" printed in failure messages no
   longer advertises `restricted` as a target.

4. **Reconciled the format vocabulary — `guide` + `next` in, `blueprint` out — across all
   four sources** the spec names (schema + both validators + specials.md authoring list):
   - `scripts/validate-chapter-plan.py`: `VALID_FORMATS` gains `guide`, `next`; loses
     `blueprint`. `FORMAT_EXECUTION_MODE` gains `guide` (parallel); loses `blueprint`. The
     execution-mode mismatch message and the is-hype permissive comment updated to match. Added
     inline tests: a valid `guide` plan PASSES, a valid `next` plan PASSES, a retired
     `blueprint` plan is REJECTED.
   - `references/chapter-plan-schema.md`: `guide` added to the format enum (`next` was already
     present; `blueprint` already absent).
   - `references/spec/specials.md`: `guide` added to the `data-special="<format>"` authoring
     list (line 28).
   - `scripts/validate-issue.py`: already carried `guide` + `next` and no `blueprint` — no
     change required; confirmed consistent.

### Gate evidence (spec §10 Phase 0 gate)

**"Greps demonstrably fire on the known-bad archive examples":** `publish-gate.sh` verdict —
- `signal_rewind_2026-07-12.html` → **RED** (scaffold-tokens: `#[N]` ×1)
- `signal_deep-dive_2026-05-26.html` → **RED** (scaffold-tokens: `ch2-1` ×30, `viz_3` ×5,
  `research bundle` ×5)
- `countdown-wcq.html` → **RED** via `validate-issue.py` (tool-credit leak ×1)
- `signal_weekly_2026-07-13.html` (clean control) → **GREEN**
- Full 30-file archive re-scan: exactly the three known-bad files fail `scaffold-tokens`;
  every clean weekly, both holiday issues, both deep dives without leaks, Next, Versus,
  Starter Kit, Shortlist all pass — no false positives.

**"A Guide chapter plan passes Phase 4 validation":**
- `validate-chapter-plan.py --test` → **56/56 tests passed** (includes the new
  guide-passes / next-passes / blueprint-rejected cases).
- A real 3-chapter Guide plan run through `main()` → `PASS … Format: guide | Execution:
  parallel`, exit 0.

**F-17 behaviour verified:** synthetic issue with a `media.gettyimages.com` `<img>` →
diversity gate emits the restricted warning, classifies it `restricted`, does not count it
toward the 3-type diversity minimum.

**Mandatory cross-phase gates:**
- `verify-weekly-golden.sh` → **GOLDEN REGRESSION PASS** (weekly output byte-identical /
  valid; new scaffold-tokens check passes on the golden weekly).
- `py_compile` clean on all three edited Python scripts.

### Decisions made where the spec was silent

- **F-14 lives inside `validate-issue.py`, not a standalone grep script.** The spec says
  "hard-fail greps in the publish gate"; `publish-gate.sh` already runs `validate-issue.py`
  and honours its exit code, so adding the check there (DOM-only, alongside the existing
  `check_scaffold_leak`) makes the greps hard-fail in the gate without a new moving part.
- **`next` execution_mode left unpinned.** `next` has never carried a fixed execution mode
  (it was absent from `FORMAT_EXECUTION_MODE` historically) and is a manual-only, single-lane
  progression format; a Next plan may declare either mode. `guide` IS pinned to `parallel`,
  matching its parents (`shortlist` + `starter_kit`, both parallel).
- **F-17 introduces a real `restricted` type rather than deleting the mapping.** Keeping the
  domains mapped (as `restricted`) means the gate actively *warns* when a Getty/Shutterstock
  comp slips in, instead of silently treating it as an unknown domain.
- **Added the "Created with … Computer" tool-credit grep beyond the spec's explicit F-14
  token list.** The review (Part 5 §1) names tool credits as a leak class the publish gate
  should catch, the sequencing addendum folds review rec #8 into F-14, the phrase is confined
  to one archive file (`countdown-wcq`) with zero legitimate use, and it strictly strengthens
  the gate. Logged here as a deliberate, low-risk extension.

### Known gaps (explicit, not silently dropped)

- **Broader production-leakage classes from review rec #8 are NOT yet hard-failed:** raw
  CDN-hostnames used as photo credits, and empty rating/stat boxes. Both are
  false-positive-prone in a plain grep (legitimate credits contain hostnames; empty-box
  detection needs DOM-structure logic) and deserve a rendered-review budget before landing in
  the publish gate. Deferred, not forgotten — candidates for a follow-up hygiene pass.
- **`lookahead` remains a recognised slug** in the schema enum, `validate-issue.py`
  `SPECIAL_FORMATS`, and the specials.md authoring list. Its removal (and the deletion of its
  ~300 lines of retired CSS) is explicitly Phase 3 scope (F-5, "Lookahead deleted"); removing
  the slug now would break back-compat validation of the archive before the CSS cleanup. Left
  in place deliberately for this phase.
- **`guide` still has no owned CSS accent / cover gesture and no `data-special` styling.**
  That is Phase 2/3 scope (F-2 covers, skin-editorial). Phase 0 only unblocks the *plan* gate
  so a Guide can be planned; a Guide should not be *run* until the new system lands (per the
  review's sequencing addendum).

### Files touched (Phase 0)

- `test_signal_field-guide_2026-05-17.html` (deleted)
- `issues/TEST-signal_field-guide_2026-05-17.html` (deleted)
- `.claude/skills/the-signal/scripts/validate-issue.py`
- `.claude/skills/the-signal/references/image-source-types.json`
- `.claude/skills/the-signal/scripts/check-image-diversity.sh`
- `.claude/skills/the-signal/scripts/validate-research-bundle.py`
- `.claude/skills/the-signal/scripts/validate-chapter-plan.py`
- `.claude/skills/the-signal/references/chapter-plan-schema.md`
- `.claude/skills/the-signal/references/spec/specials.md`
- `docs/design-system-unification-PROGRESS.md` (this file)

---

## Phase 1 — Token shim / furniture-reuse proof on a Deep Dive copy — ✅ GATE GREEN (2026-07-18)

Contained proof that the holiday "furniture" reads only `--hol-*` tokens, so an editorial
token alias reskins it into paper-and-ink and lifts a Deep Dive's pacing density — without
losing content or reading as a theme park.

### What shipped (all under `docs/mockups/phase1/`, prototype-only — never a live path)
- **`mx-phase1-shim.css`** — the token alias block (`--hol-*` → the editorial
  `23-special-tokens.css` contract) plus de-scoped ports of the real holiday furniture as
  neutral `.mx-*` classes: **numbers band, facts ledger, quote-object, stamp seal, cheat-sheet
  (F-15 — instantiated, previously CSS-comment-only), act-opener, framed figure with a real
  `<img>` (F-6)**. The loud display/script/hand faces are deliberately aliased onto the bookish
  serif/sans (no Bowlby One / Yellowtail / Caveat) — the de-theming that keeps editorial
  gravitas. §8 craft floor baked in the day the components were extracted: 68ch measure (F-9),
  0.72rem type floor (F-12), token-level dark (F-7), print sheet, 390px stacking (F-8),
  reduced-motion honoured (§5).
- **`signal_deep-dive_2026-06-30-redressed.html`** + **`-baseline.html`** — a re-dressed COPY
  of the Byzantium Deep Dive and a matched baseline. Furniture (10 chapter ledgers, 10
  quote-objects, a numbers band, an 8-row cheat-sheet) built **only from the issue's own
  facts** (trust rule — no invention; a subagent extracted verbatim facts/quotes per chapter).
- Reproducible via `inject_p1.py` + `dd-furniture.json`; reusable render harness persisted at
  `docs/mockups/tools/{render.mjs,shot_furn.mjs}`.

### Gate evidence (spec §10 Phase 1 gate + §9 protocol)
- **Rendered density ≥0.7:** measured on the rendered DOM, **0.51 → 0.73 events/screen**
  (baseline 37 events / 72.8 screens → re-dressed 59 / 81.1). Words/screen 255 → 240. Clears
  the ≥0.7 floor.
- **Identity reads paper-and-ink (NOT theme-park):** a fresh-eyes art-director subagent, given
  the screenshots cold (not told what they "should" be), returned verdict *"restrained,
  paper-and-ink editorial magazine — NOT loud or theme-park … the bones are good."* Its top-3
  fixes were applied (see below).
- **§9 full pass:** cover + scroll-depth + dark-emulation + reduced-motion + 390px mobile
  captured and **read**. Numbers band, ledger, quote-object, cheat-sheet all render bookish in
  light and coherent in dark; mobile stacks single-column with **no horizontal page overflow**
  (docW == winW == 390). Screenshots in scratchpad `out/` (final__*, finalD__*, finalM__*,
  baseline__*).
- **Adversarial pass:** fresh-eyes visual QA (above) + the change is CSS/prototype only. Its
  three findings — (1) sticky masthead 86%-translucent so body text smeared through it,
  (2) top-left nav/progress collision + a stray glyph, (3) a faint redundant corner stamp —
  were **all legacy deep-dive chrome**, not furniture; fixed in the prototype by hiding the
  legacy running `.mast` and the redundant `.stamp-fixed` (keeping one legible seal). The
  proper fixes are F-3 (one masthead) / F-8 (mobile chrome) in Phases 2–3.
- **Mandatory cross-phase:** `verify-weekly-golden.sh` **PASS** (byte-identical); chapter-plan
  `--test` 56/56; re-dressed prototype passes the Phase 0 scaffold-token gate.

### Decisions where the spec was silent
- **Faithful reuse, not a fresh kit.** The furniture is the *real* holiday components,
  de-scoped from `body[data-special="countdown"]` and fed the editorial alias — this proves
  the "~83% universal bucket reads only tokens" claim directly, not by analogy to the mockup.
- **`mx-*` naming = the sanctioned reuse vocabulary (the Phase 1 "one-line amendment").** The
  furniture uses `mx-*` class names, which are **not** in `validate-issue.py`'s
  `WEEKLY_FORBIDDEN_STYLE_MARKERS` (that gate bans `hol-*`/theme tokens on weeklies). So reused
  furniture never trips the weekly holiday-marker check — no code change needed, recorded here
  as the amendment. Phase 2 renames `hol-*` → `mx-*` at the source.
- **Prototype freeze block.** The shim neutralises the legacy scroll-reveal/parallax/sticky
  machinery so every frame renders complete — a live demonstration of the §5 "JS-off renders
  100% complete content" contract and a preview of Phase 2's opt-in `[data-motion]` re-scope.
- **The shim was RELOCATED out of `assets/css/`** the moment it was clear `stitch-issue.sh`
  globs `assets/css/*.css` into every special bundle — leaving it there would have polluted
  live issues on the next Sunday run (a publication-continuity violation). It now lives only in
  `docs/mockups/phase1/` and is inlined into the prototype.

### Known gaps (explicit)
- Bespoke ledgers/quotes were authored for the 10 content chapters; the mechanical density
  (0.73) is measured across the whole re-dressed issue. Sufficient for the proof and the gate.
- Legacy deep-dive chrome (dual `.mast` F-3, corner nav F-8) and its lack of native dark (F-7)
  are Phase 2/3 deliverables — the prototype patches them, it does not fix the source.
- Fresh-eyes' fair caution — the legacy teal section-tag fights the coral accent (two accent
  hues) — is an F-11 (token unification) / F-2 (accents) item for Phases 2–3.

### Owner checkpoint
Per spec §10, the before/after screenshots (desktop + mobile, light + dark) were sent to the
owner as the single deliberate taste sign-off. The user's standing instruction ("do the
remaining phases, sequentially") is taken as authorisation to proceed into Phase 2; the
before/after is surfaced so the aesthetic direction can still be redirected cheaply.

---

## Phase 2 — Furniture-core extraction — 🟡 IN PROGRESS (foundation built + verified, STAGED not wired)

**Publication-continuity hold (§11):** today is Saturday 18 July; The Signal publishes tomorrow
(Sunday 19 July). Phase 2 is the first phase that would touch the live skill, so it is being
built **isolated from the live pipeline** and its live wiring + doc pruning are held until after
the Sunday boundary. Nothing below ships tomorrow.

### Built + verified so far (all in `assets/css/core/`, a subdirectory the live stitchers'
non-recursive `assets/css/*.css` glob does NOT pick up — proven: live special bundle still 47
files, weekly golden byte-identical):
- **`00-contract.css`** — the full `--mx-*` token contract (§4.2): ~30 properties, six type
  roles (whitelist stacks with system fallbacks so text is readable network-off), art slots
  (`--mx-pattern/-glyph/-band`, glyph via `mask-image` currentColor — the single indirection
  that replaces all legacy per-venue rules), neutral **AA-safe** paper-and-ink defaults, the
  `data-act="2"` palette swap (replaces `.hol-half--two` overrides), **token-level dark (F-7)**,
  print, reduced-motion backstop, **68ch measure cap (F-9)**, **0.72rem type floor (F-12)**.
- **`10-ephemera.css`** — framed-object chassis (pinned card, mail card, quote-object, stamp
  seal + glyph-mask variant, ticket stub, fasteners, hand-caption, credit, framed figure) with
  the **real-`<img>` F-6 contract** as primary and `role="img"`+`aria-label` documented.
- **`11-ledgers.css`** — facts `<dl>`, numbers/stat band, ranked entries + rank chips, tier
  pills, and the **cheat-sheet (F-15)** — all reading only `--mx-*`.

### Gate evidence so far
- **Core re-dresses a real editorial issue:** `docs/mockups/phase2/` re-dresses a COPY of the
  Byzantium Deep Dive **from the core** (`data-mx` on `<body>` + the three core layers inlined,
  furniture from the issue's own facts). Rendered furniture (numbers band, ledger, quote-object,
  cheat-sheet) is visually equivalent to the Phase 1 shim, in the core's restrained default
  accent — screenshots `scratchpad/out/core__*`. This satisfies the editorial half of the Phase 2
  gate ("a re-dressed editorial special copy renders pixel-plausibly from the core").
- `verify-weekly-golden.sh` **PASS**; core CSS brace-balanced; core invisible to live bundles.

### Remaining Phase 2 work (lands AFTER Sunday, per §11)
- Core layers `12-plates.css`, `13-chrome.css` (**one masthead — F-3**, cover incl. poster
  variant with the F-8 collision fix, kicker, act opener, transit, marquee, countdown grid,
  drop-cap/fleuron/ribbon), `14-motion.css` (38+39 re-scoped to `[data-motion]` tiers — F-10),
  `15-responsive.css` (37 generalised; F-8/F-9 fixes).
- Holiday half of the gate: re-dress a **holiday** copy (Countdown) from the core.
- Doc pruning (the overdue S7/S8): `pre-flight.md`, `specials.md`, `component-contracts.md`,
  Gate 1E rewritten to teach ONLY the live system (F-13) — this touches live guidance, so it is
  explicitly held to the post-Sunday landing.
- Full §9 pass (dark + reduced-motion + 390px + adversarial) on both re-dressed copies.

### Decisions
- **`assets/css/core/` chosen as the home now** (its real §3 destination) rather than a throwaway
  dir, because it is provably outside the live glob — so the built work is already in place for
  Phase 3's manifest wiring, with zero live-bundle risk in the meantime.
- Class rename `hol-*` → `mx-*` done at the source in the core (the archive is unaffected — shipped
  issues carry their CSS inline).

---

## Phases 3–6 — not started

See spec §10. Phase 3 (skins + per-format manifests + bundling) wires the core into the live path
and is gated on the Phase 2 completion above landing cleanly after the Sunday boundary.
