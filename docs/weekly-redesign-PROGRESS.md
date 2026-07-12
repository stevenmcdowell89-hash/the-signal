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
- ⬜ **W1 — Transmission design system CSS** (token layer + all components + dark variant).
- ⬜ **W2 — Weekly template-parts rewrite** (cover/masthead, movements/bands, navigator/tuner, all sections).
- ⬜ **W3 — Weekly-only asset bundle** (stitch-issue.sh / inject-assets.sh: Transmission bundle only, ~150KB).
- ⬜ **W4 — Structure + reliability spine:**
  - W4a — `references/format-skeletons/weekly.json` skeleton.
  - W4b — `validate-issue.py` weekly structural + **visual-consistency** assertions (markup gate).
  - W4c — `validate-chapter-plan.py` restored to blocking against the skeleton.
  - W4d — publish receipt (`build-receipt.json`) + mechanical publish gate; bounded repair loop wired in SKILL.md.
  - W4e — golden-issue regression fixture.
- ⬜ **W5 — Spec updates** (spec/weekly.md, component-contracts.md, sections.md → Transmission vocabulary; resolve Bookmark vs Shelf; re-slice).
- ⬜ **W6 — Prove end-to-end** (generate/stitch a real weekly, inspect vs reference, all gates green).
- ⬜ **W7 — Version bump + CHANGELOG + merge to main.**

---

## Run log (append-only)

- 2026-07-12 — Read handoff + 5 reference docs + reference issue. Strategy set (above).
  Dispatched W0 mapping agent. Progress doc created.
