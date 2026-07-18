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

## Phases 1–6 — not started

See spec §10 for the phase gates. Phase 1 (token shim on a Deep Dive copy) is next; it carries
the single deliberate owner taste-checkpoint before the expensive Phase 2 extraction.
