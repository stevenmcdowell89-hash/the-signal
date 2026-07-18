# THE SIGNAL — DESIGN SYSTEM UNIFICATION · PROGRESS LOG

Orchestrator's running record for `docs/design-system-unification-SPEC-2026-07-18.md` (v2, the
binding contract). Companion evidence lives under `docs/design-system-unification-EVIDENCE/`.

Per Part 6 §6 this log records, per work package: what shipped · gate evidence (ledger paths) ·
decisions taken where the spec was silent · honest known-gaps. Per Part 6 §1 **a gate claim with
no ledger entry is by definition false** — every "green" here must link to committed evidence.
No WP is marked done with a failing, skipped, or unproven gate.

**Branch:** `claude/design-system-unification-review-bfh8al`, based on the v2-spec commit of `main`.
**Prior-attempt branch (`claude/design-system-unification-phase-0-qo2f9s`): NOT REUSED.** Owner
directive, 2026-07-18: "nothing is reusable, you are starting from now." Audit finding that
motivated it: that branch recorded Phases 0–6 "green" but **never built the measurement harness
(`measure-issue.mjs`)** — every density/distribution/overlap/motion claim rested on prose
estimate, exactly failure F-19. Its Season Review is the flat false-green this spec exists to make
impossible. We build the gate suite first, from scratch, and trust no number that the suite has
not produced.

---

## WP-0 — GATES FIRST — ✅ COMPLETE · GATE GREEN (independent verifier, 2026-07-18)

Tooling before any art. The measurement/verification suite must exist and be proven — against a
known-good reference AND against retained negative fixtures — before anything can claim green.

### Shipped so far

**WP-0(e) — Phase-0 hygiene — ✅ (commit: hygiene).**
- Deleted the two public TEST field-guide files (`test_signal_field-guide_2026-05-17.html`,
  `issues/TEST-signal_field-guide_2026-05-17.html`); verified unreferenced before deletion.
- F-17: added a `restricted` source type to `references/image-source-types.json`; reclassified
  `media.gettyimages.com` + `image.shutterstock.com` from `press_kit` → `restricted`. BOTH
  diversity consumers (`check-image-diversity.sh`, `validate-research-bundle.py`) now warn on a
  restricted source and exclude it from source-type diversity counting.
- Format-vocabulary reconciliation (guide/next in, blueprint out) across `validate-chapter-plan.py`
  (`VALID_FORMATS` + `FORMAT_EXECUTION_MODE`, guide pinned parallel, next left unpinned),
  `chapter-plan-schema.md` enum. `lookahead` slug left in place deliberately — its removal is F-5 /
  WP-3 scope (deleting the slug now would break archive back-compat before the CSS deletion).
- Evidence: `validate-chapter-plan.py --test` → 53/53; JSON + `py_compile` clean.

**WP-0(a) — `tools/measure-issue.mjs` — ✅ built + calibrated (commit: harnesses).**
Renders a served issue at 1440×900 and 390×844, warms one-way scroll-reveals, smooth-scrolls, and
emits `metrics.json`: words · events/screen (Law-2 closed-list selectors — legacy `hol-/sp-/dd-`
union + forward-compat `mx-`, nesting-deduped, scoped to rendered nodes so shared-`<style>`
phantoms never count) · distribution (longest zero-event run in screens + per-screen series) ·
chrome-overlap (fixed/sticky chrome obscuring content centres via `elementFromPoint`) · doc-level
H-scroll · table truncation · motion census (Web-Animations running count + furniture
transform/opacity deltas, with a reduced-motion control pass).
- Calibration (ledger: `EVIDENCE/wp-0/calibration/countdown.metrics.json`): countdown reads
  **desktop 2.11 ev/screen** (clears the WP-1 ≥1.5 tool-sees-density floor), mobile 1.40 (above the
  1.0–1.3 trip target); H-scroll false, truncation 0, chrome-overlap 0; furniture_moved 3→0 under
  reduced-motion. The tool sees the countdown's density.

**WP-0(d) — `tools/render.mjs` — ✅ built (commit: harnesses).** Non-curated screenshot set (cover
+ 8 smooth-scroll depths + dark + reduced-motion) at both widths for the Part 5 parity gate.

**WP-0(b) — validator wiring — ✅.** Into `validate-issue.py`: `is_mx_issue()` detector; Law-3
`MX_LENGTH_FLOORS` (all 9 formats, data-mx-gated) folded into `check_length_band`; Law-9
`check_voice_minimums` (data-mx-gated, first-cut heuristic — distinct named external sources via
`data-quote-source`/`<cite>`/dash-attribution, self-quotes excluded, prefers FAIL on ambiguity);
`check_scaffold_tokens` (F-14, ALL issues, visible-prose-only). F-16 dead-hotlink detection
confirmed already covered by `check_image_urls` (no duplication added). `py_compile` clean.

**WP-0(c) — four negative fixtures — ✅** (`EVIDENCE/negative-fixtures/`): stub SR, flat-boxes SR,
rewind-scaffold, flat re-dress + dead hotlink; README maps each fixture → gate → expected verdict.

**WP-0(d) — evidence-ledger skeleton — ✅** (`EVIDENCE/README.md` + `wp-0…wp-9/`, Part 6 §1).

### Gate — ✅ GREEN (independent verifier; ledger: `EVIDENCE/wp-0/gate/`)
*Spec WP-0 gate: every tool runs on the known-good countdown AND every negative fixture with correct
verdicts, output committed.* Run by a **fresh verifier** (not the builder, Part 6 §3), raw output
committed to `EVIDENCE/wp-0/gate/`:
- **countdown** (reference): `measure` desktop **2.113 ev/screen** (≥1.5); `validate-issue.py` exit 0;
  does NOT trip scaffold-tokens; mx-only checks correctly skip the legacy reference.
- **stub-season-review**: `length-floor` FAIL (522<6500) + `voice-minimums` FAIL (0<5); measure 0
  ev/screen — TRUE low density (rendered: 522 words, scrollHeight 1382), not a gamed number.
- **flat-boxes-season-review**: `voice-minimums` FAIL while `length-floor` **PASSES** (6931≥6500);
  measure 0 ev/screen, longest-zero-run 19/33 screens (rendered: 6924 words, scrollHeight 16570).
- **rewind-scaffold-tokens**: `scaffold-tokens` FAIL on `#[N]`/`[N]`/`ch2-1`/`viz_3`/"research
  bundle"/"furniture-first".
- **flat-redress-deepdive**: `image-urls` FAIL on the dead hotlink; measure 0.28/0.16 ev/screen.
- **Render-failure guard:** every fixture's low reading is a TRUE render (non-zero words +
  scrollHeight) — no load-failure masquerading as 0.
- **Regressions:** `verify-weekly-golden.sh` exit 0 (orchestrator-run + verifier-run); scaffold/voice
  checks do NOT false-fire on the clean golden weekly; `validate-chapter-plan.py --test` 53/53.
- **Eyeball:** flat-boxes screenshot is a genuine stack of hairline-bordered boxes (real F-20 artifact).

**Orchestrator spot-check:** personally ran `verify-weekly-golden.sh` → PASS (the key regression risk);
reviewed the full `validate-issue.py` diff (floor/voice tables match the spec exactly, patterns tightly
anchored, data-mx gating protects the archive); accept the verifier's raw evidence. WP-0 gate GREEN.

### Decisions where the spec was silent
- **New Law-3 floors and Law-9 voice minimums gate on `data-mx` issues only.** The spec (WP-0b, F-18)
  scopes them to `data-mx` issues; this also honours the existing rationale that applying floors to
  legacy formats would retroactively red-flag the archive. Scaffold/strategy-vocab greps (F-14) apply
  to ALL issues — leaked scaffolding is always a defect.
- **Measurement granularity:** ephemera/plates/figures/quotes/dividers count per-object; stat
  bands/ledgers/tables/cheat-sheets count once per container (nesting-dedup skips their rows/cells) —
  a 12-cell band is one event, not twelve, matching Law-2's "stat band = one event" wording.

### Known gaps (explicit)
- Law-9 voice check is a first-cut mechanical heuristic; it will be recalibrated in WP-6 against the
  real quote-object markup that lands in WP-2. Documented at the check site.
- Motion census reports a high always-on animation count on the countdown even under reduced-motion
  (decorative loops not gated by `prefers-reduced-motion`); the meaningful discriminator is
  `furniture_moved` (3→0). The reduced-motion *gate* is WP-5 scope; census merely needs to function.
- The negative fixtures, being offline stubs with zero components, also (correctly) trip `back-link`
  and `special-variety` beyond their targeted gates — additional TRUE failures, documented in the
  fixtures README so "isolated" is not misread as "sole failure."
- `measure-issue.mjs` and `validate-issue.py` word counts differ slightly (~1%, different tokenizers,
  e.g. countdown 7523 vs 7594); both land the same side of every floor/ceiling, so no gate impact.
  Left as-is; the validator count is authoritative for Law-3, the measure count for density.

---

## WP-1 — REFERENCE CAPTURE — ✅ COMPLETE · GATE GREEN (2026-07-18)

Froze the standard for the parity gate. Ledger: `EVIDENCE/references/`.
- **Baseline metrics** (`*.metrics.json`), desktop ev/screen: countdown **2.113**, field-guide
  **1.701**, mockup **2.245** — all reproduce the Part-1 "holiday issues are the dense bar"
  finding; countdown clears the WP-1 ≥1.5 tool-sees-density floor. `measure-issue.mjs` gained
  `kit-*` selectors for the mockup; countdown re-verified UNCHANGED at 2.113 (no tool regression).
- **Frozen screenshot packs** — 63 non-curated shots (21 each: cover + 8 smooth-scroll depths ×2
  widths + dark ×2 + reduced-motion), harness-produced, eyeball-confirmed real designed furniture
  at both widths. These are the frozen comparison set every parity verifier receives.
- **Honest note:** the field-guide reference measures a 6-screen longest-zero-event run at desktop
  (heavy-prose format, 15k words) and 0.915 ev/screen at mobile — an honest measurement of the
  existing artifact, not a gate on it; Law-2's distribution rule binds the NEW issues we produce.

## WP-2 … WP-9 — 🟡 WP-2 IN PROGRESS

## FALSE GREENS
None recorded. (Part 6 §5: any PASS later shown false is logged here — hiding one is the terminal
offense against this spec.)
