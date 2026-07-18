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

## WP-0 — GATES FIRST — 🟡 IN PROGRESS (gate pending fresh-verifier run)

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

### In flight (builder subagent)
- WP-0(b) validator wiring: Law-3 floors + Law-9 voice minimums (data-mx-gated) + scaffold/
  strategy-vocab greps (universal) + F-16 external-src confirmation, into `validate-issue.py`.
- WP-0(c) four negative fixtures (stub SR, flat-boxes SR, rewind-scaffold, flat re-dress + dead
  hotlink) + fixtures README mapping fixture→gate→expected verdict.
- WP-0(d) evidence-ledger skeleton (`EVIDENCE/wp-0…wp-9/` + README, Part 6 §1).

### Gate (NOT YET RUN)
*Spec WP-0 gate: every tool runs on the known-good countdown AND every negative fixture with correct
verdicts, output committed.* Will be run by a **fresh verifier** (builder ≠ gate-runner, Part 6 §3):
every negative fixture must FAIL; the countdown must pass the mechanical checks; outputs committed to
`EVIDENCE/wp-0/`. Orchestrator spot-check to follow. **WP-0 is not done until this passes.**

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

---

## WP-1 … WP-9 — ⬜ NOT STARTED

## FALSE GREENS
None recorded. (Part 6 §5: any PASS later shown false is logged here — hiding one is the terminal
offense against this spec.)
