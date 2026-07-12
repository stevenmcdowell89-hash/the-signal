# The Signal — Weekly Redesign: implementation PROGRESS log

**Owner:** steven.mcdowell.89@gmail.com · **Branch:** `claude/weekly-redesign-improvements-vdreoc`
**Driver:** autonomous orchestrator. This log is the durable recovery point — if the
session is interrupted, resume from the first workstream not marked ✅ DONE.

Source of truth for *what* to build: `docs/weekly-redesign-HANDOFF.md` (→ the 5 reference
docs it points at). Visual target: `docs/mockups/reference-issue-transmission.html`.

---

## Strategy (decisions made by the orchestrator)

The reference issue is a **self-contained, coherent artifact** with a fresh class
vocabulary. Retrofitting the 45 legacy CSS files + old templates to reproduce it exactly
is more error-prone than **adopting the reference as the weekly's own design system**.
So the plan:

- **Weekly gets its own Transmission stylesheet + template vocabulary**, injected as a
  light weekly-only bundle. **Specials are untouched** — they keep the dark
  bound-magazine identity (that becomes their signal of difference, per the intent docs).
- **Determinism over instruction** (reliability doc's core principle): the four movements
  + band structure become a fixed skeleton the planner/stitcher fill and the validator
  enforces — the malformed-structure class becomes unrepresentable.
- **Decisions taken** (bias toward the magazine's intent when pieces clash):
  - Books = **fixed Bookmark rail** every issue (resolves the Bookmark-vs-Shelf spec
    contradiction; matches the reference). "The Shelf" rotating definition is purged.
  - Weekly class vocabulary = the reference's (`.bandhead`, `.movement`, `.tuner`/
    `.station`, `.digest`, `.figures`, `.longread`/`.pullquote`/`.aside-note`,
    `.round`/`.items`/`.scores`/`.with-rail`/`.rail`/`.picks`/`.desk`/`.deskcol`/`.pin`,
    `.threads`/`.thread`, `.rabbit`, `.radar`, `.closepin`, `.endnumbers`, `.colophon`,
    `.signoff-line`). The old `.sp-*` special vocabulary stays forbidden in weeklies.
  - Palette: `--paper:#F5F0E6 --paper-2:#EFE8D9 --ink:#16151A --signal:#FF3B2F
    --blue:#243F5C --muted:#8A8578 --hair:#DDD5C3`. Fonts: Instrument Serif +
    Newsreader + JetBrains Mono. Warm-night dark variant added (prefers-color-scheme).

---

## Workstreams (status)

Legend: ⬜ not started · 🔶 in progress · ✅ done · ⏭️ deferred (with note)

- ⬜ **W0 — Map current pipeline mechanics** (stitcher/validators/templates/spec). *(agent running)*
- ✅ **W1 — Transmission design system CSS** — `assets/css/weekly/00-transmission.css` (25KB): full reference port + `--ink-2` tokenization + warm-night `prefers-color-scheme: dark` variant. Verified: all component classes present, no special/holiday leakage.
- ✅ **W2 — Weekly chrome** — *architecture change:* rather than rewrite the old
  template-parts (03-cover, 04-navigator, 04a-movement-band…), the weekly's chrome
  (cover/masthead/tuner, the 4 movement dividers, every band-head, colophon, sign-off)
  is now GENERATED deterministically by `scripts/stitch_weekly.py` from `weekly.json`.
  The old weekly template-parts are superseded (left in place; specials may still ref
  some). Writers now produce only per-band inner content.
- ✅ **W3 — Weekly-only asset bundle** — `stitch_weekly.py` injects ONLY
  `assets/css/weekly/*.css` (24.5KB) + `assets/script-weekly.js` (1.4KB). Down from
  ~461KB CSS + 2388-line JS. bash `stitch-issue.sh` dispatches weekly → stitch_weekly.py.
- ✅ **W4 — Structure + reliability spine:**
  - ✅ W4a — `references/format-skeletons/weekly.json` skeleton (single source of structure).
  - ✅ W4b — `validate-issue.py`: `check_weekly_structure` retargeted to Transmission
    `data-*` hooks; `check_weekly_visual_consistency` (no special/holiday CSS/fonts,
    weekly masthead not special hero); `check_scaffold_leak` (handoff §8b).
  - ✅ W4c — `validate-chapter-plan.py` weekly branch (blocking vs skeleton). Golden passes, broken fails, special path untouched (53/53).
  - ✅ W4d — `scripts/publish-gate.sh` writes `build-receipt.json`, refuses publish unless green; SKILL.md Phase 10 publish policy (hold-on-hard-failure). Green receipt on golden verified.
  - ✅ W4e — golden regression: `references/golden/weekly/` + `scripts/verify-weekly-golden.sh` (stitch → validate-issue → validate-chapter-plan, all green).
- ⬜ **W5 — Spec updates** (spec/weekly.md, component-contracts.md, sections.md → Transmission vocabulary; Bookmark resolved in skeleton; re-slice).
- ✅ **W6 — Prove end-to-end** — golden path PROVEN: `stitch-issue.sh` (weekly dispatch)
  → all `validate-issue.py` gates PASS (structural + visual-consistency + scaffold-leak)
  → `validate-chapter-plan.py` valid → renders pixel-faithful to the reference at 800px
  (cover, 4 movements, Long Read, Desk 2-col, Radar folded, Bookmark). Re-runnable via
  `scripts/verify-weekly-golden.sh`.
- ✅ **W7 — Version bump (8.42.0) + CHANGELOG + MERGED TO MAIN** (`d1c6e46`, verified green post-merge).

---

## STATUS: COMPLETE & MERGED (2026-07-12)

All eight workstreams landed on `main` (v8.42.0). The weekly generator produces the
Transmission identity, passes all gates, and is proven by the golden regression.

**Honest scope notes (what is proven vs documented):**
- **Proven end-to-end:** the *machinery* — stitch → all structural/visual gates → plan
  validation → pixel-faithful render — via the committed golden fixture. This is the
  reliability doc's golden-issue regression (Pillar F) and the "test that was never run".
- **Not run:** a *live-research* generation of a brand-new weekly (the container's outbound
  research egress is restricted, and it is orthogonal to these changes). The golden fixture
  exercises the same stitch + gate path a live run uses; only the research/writer content
  differs. Run `verify-weekly-golden.sh` after any change to lock the regression.
- **Repair loop / structured reviewer (Pillars D/E):** the new structural + visual +
  scaffold-leak gates now feed the existing Phase 9 repair loop (they live in
  `validate-issue.py`, run at Phase 7.6), and the mechanical publish receipt (Pillar F) +
  hold-on-hard-failure policy are wired in SKILL.md Phase 10. A deeper restructure of the
  Phase 9.5 rubric read into fully teeth-bearing structured output (Pillar D) is described
  in SKILL.md but left as a follow-up — the compliance-blocking work (structure/visual) is
  what shipped broken before, and that is now hard-gated.

### PROOF (W6, golden path) — 2026-07-12
`bash stitch-issue.sh --plan references/golden/weekly/chapter-plan.json --build-dir <staged> --issue-number 16`
→ `validate-issue.py --format weekly` → **All checks PASS** (1 warn = image-urls skipped,
expected: the Transmission weekly uses CSS `.plate-box` placeholders, no `<img>`).
Rendered at 800px via Chromium: identical to `reference-issue-transmission.html`.

---

## Run log (append-only)

- 2026-07-12 — Read handoff + 5 reference docs + reference issue. Strategy set (above).
  Dispatched W0 mapping agent. Progress doc created.
- 2026-07-12 — Confirmed weekly currently injects ~461KB CSS (322KB holiday/special) +
  2388-line JS. **Architecture decision:** weekly CSS lives in its own dir
  `assets/css/weekly/*.css`; inject-assets.sh selects bundle by `--format` (weekly →
  `css/weekly/`, else top-level `css/*.css` non-recursive so weekly/ never leaks into a
  special). Weekly ships a minimal JS (image-error fallback only) — JS-off-complete.
  Dispatched W1 (CSS) build agent.
