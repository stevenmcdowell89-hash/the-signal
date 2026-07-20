# WP-9 CLOSEOUT — Failure Registry F-1…F-20, with evidence

Every failure from Part 3 of the spec, its fix, and the committed evidence that
proves the fix. Evidence paths are under `docs/design-system-unification-EVIDENCE/`
(abbreviated `EV/`) unless noted. The independent audit (`WP-9/audit-report.md`)
re-verifies these claims by reproduction.

## Design failures

| ID | Failure | Fix | Evidence |
|---|---|---|---|
| **F-1** | Density collapse (Deep Dive 0.37 ev/screen) | Furniture core with scenography-as-default; densification measured | DD re-dress **0.98/0.73** ev/screen (`EV/WP-2/parity-candidate-dd`), live Season Review **1.95/1.45** (`EV/WP-7/parity-candidate-sr/metrics.json`); measured by `tools/measure-issue.mjs`, not asserted |
| **F-2** | One cover template + hard-coded ember accent (`25-special-cover.css`) | Poster cover scaffold reading `var(--mx-accent)`; per-format owned gestures in skeletons | Non-interchangeable covers: SR ghost-"26"+trophy, DD ghost-"1453", weekly masthead (`EV/WP-7`, `EV/WP-2`, `EV/WP-8` covers); parity Law 7 PASS all gates |
| **F-3** | Dual `.mast` (21-chrome vs 28-special-masthead) | ONE `.mx-mast` per bundle; one-masthead gate in `stitch-issue.sh` | Gate rejects any legacy masthead class or missing `.mx-mast`; bundles grepped clean (WP-3 report; audit §3) |
| **F-4** | 176× `:not()` scoping tax (layers 23–32) | Skins scope by `[data-skin]` descent — **zero** `:not()` | `grep -c ':not('` on skins = comment lines only (`assets/css/skins/*.css`) |
| **F-5** | ~444KB full-bundle ships deleted-format CSS | Per-format manifest bundling; budgets hard-fail in stitcher | editorial **102KB**/120 cap, event **96KB**/160 (`references/css-manifests/*.txt`, stitcher byte print) |
| **F-6** | Ephemera invisible to screen readers | Real-`<img>` (object-fit) or `role="img"`+`aria-label` contract baked into `core/10-ephemera.css` | `references/core-components.md` contract; live SR/DD use real `<img>`/labelled figures (F-16 check passes) |
| **F-7** | Zero dark/print in layers 23–44 | Token-level dark remap (core+skins) + `core/16-print.css` | dark-1440 renders every parity pack; print probe (WP-3 report); in both manifests |
| **F-8** | Mobile chrome shatter + pill overlap + table truncation + marginalia overhang | `15-responsive.css` pill reservation + hide-on-scroll; wrap-or-stack tables; marginalia rebased (no −10rem float) | `chromeOverlap.fails=false` / `tableTruncation` 0 across all candidate metrics both widths; the densified weekly FIXES the shipped weekly's own 390 pill overlap (`EV/WP-8` scorecard) |
| **F-9** | 1,270px measures | `.mx-body { max-width: min(var(--mx-measure), 68ch) }` | `core/00-contract.css`; parity Law 8 PASS |
| **F-10** | Motion locked to two formats; spec text false | Tiered motion all formats via `mx-motion.js` + `[data-motion]`; per-format tiers in skeletons | Census SR 140, DD 46, weekly 20; reduced-motion 0 everywhere (`EV/WP-5`, `EV/WP-7`, `EV/WP-8`) |
| **F-11** | Three conflicting `--paper/--ink` namespaces | Single `--mx-*` token contract; skins alias onto it | `core/00-contract.css`; transmission alias maps weekly tokens (`skin-transmission.css`) |
| **F-12** | 0.66rem micro-type | `--mx-micro` floored to `max(0.72rem, …)` on every micro-label | `core/00-contract.css`; weekly alias carries it (`EV/WP-8`) |

## Process failures

| ID | Failure | Fix | Evidence |
|---|---|---|---|
| **F-13** | Spec rot (docs teach deleted v8.21 system) | Prune pre-flight/specials/component-contracts/Gate-1E to live system | `EV/WP-2/doc-prune-report.md` — ~85-token dead-class regex greps **zero** across all four docs + spec source |
| **F-14** | Scaffold tokens + tool credits + strategy vocab in reader copy | `validate-issue.py` visible-prose checks; stitcher makes chrome unrepresentable by writers | Rewind `Issue #[N]`, DD `ch2-1`, countdown-wcq tool-credit all FAIL; strategy-vocab check; stub's "FURNITURE-FIRST" FAILs (`EV/WP-0`) |
| **F-15** | Designed-but-never-instantiated components | Every core component instantiated (kitchen-sink + re-dresses + live SR); weekly uses a curated deployed-only subset | `tools/fixtures/core-kitchen-sink.html` exercises all 9 event types; `weekly-mx/` ships only deployed classes |
| **F-16** | Dead external hotlinks | External-`src` `<img>` hard-fail for data-mx issues | `validate-issue.py` `f16-external-img-src`; live SR 0 photos (furniture-first), weekly 11/11 local |
| **F-17** | Getty/Shutterstock mislabeled `press_kit` | New `restricted` source type; both diversity consumers warn+exclude | `references/image-source-types.json` (`EV/WP-0/validator-calibration.md`) |
| **F-18** | Density gamed by 542-word stub | Law-3 word floors wired into `validate-issue.py`; the stub retained as a negative fixture that MUST fail | Stub FAILs `law3-word-floor` (542<6,500) + 4 more; retained `tools/fixtures/negative/attempt2-stub-flat-season-review.html` (`EV/WP-0/gate-verdict.md`) |
| **F-19** | False gate claims ("GREEN" on a failing artifact) | Part 6 evidence protocol in force; builder≠verifier; dual verifiers pre-publish; orchestrator spot-checks; WP-0 suite demonstrably fails all negatives | WP-0 gate proved the *old* validator false-greened the flat re-dress (exit 0→1); every WP gate scored by a fresh non-builder verifier with committed scorecard; `EV/WP-7` has TWO independent verifiers + orchestrator spot-check |
| **F-20** | Flat boxes — every component an upright hairline rectangle | Law 1 + Part 5 parity gate; scenography as component default (`.mx-flat` is the opt-out); flat fixtures retained and MUST fail parity | Scenography-default in `core/10-ephemera.css`; flat re-dress retained as negative fixture; every parity scorecard answers "objects on a surface" (`EV/WP-2,3,5,7,8`) |

## Out of scope, with reason (nothing silently dropped)

1. **Skeletons for countdown / field-guide / guide / next** — WP-6 delivered the
   spec's "at least 4" (season-review, deep-dive, versus, rewind). The other four
   formats' mx plans are rejected with a named `[MX-SKELETON]` error until their
   skeletons are authored (timing sanity still fires for countdown). Additive,
   non-blocking; a future issue in those formats needs its skeleton first.
2. **Weekly CSS bundle 45.9KB vs ~40KB target (+5.9KB)** — the curated
   five-component subset; far under the full core (~77KB) or editorial cap
   (120KB). Kept as the lean path (Law 11); flagged in `EV/WP-8`.
3. **Legacy golden not migrated to the mx path** — its real content carries 3
   named voices; the mx Law-9 floor is 4; fabricating a fourth is forbidden
   (Law 12). Backward-compat golden kept green; a NEW mx-weekly golden (real
   4-voice build) committed instead. Both in `verify-weekly-golden.sh`.
4. **Verbatim quote accuracy** — validators trust attribution markup; verbatim
   wording is a human-verify item (stated in each `law9-voices` output). Live SR
   and weekly quotes are real named people on real, widely-covered events.
5. **Legacy `assets/script.js` (96KB) on legacy issues** — replaced by the 8KB
   `mx-motion.js` on the data-mx path only; legacy archive keeps its script.
   Removing it repo-wide is archive-migration work beyond this engagement.
6. **Motif band slot / act_map field / accent-2 contrast pairs** — WP-4 gaps
   documented; non-blocking (band emits its own `.mx-transit` rule; contrast
   checked on the two rendering pairs). Future motif refinement.
7. **Per-type census at plan time only** — WP-6 gate enforces per-chapter event
   totals at render; per-type substitution within a chapter is checked at plan
   time (slot minima), not at render. Noted in WP-6 report.

## Definition of DONE (Part 6 §7) — status

- All WP gates green with ledger evidence — **yes** (WP-0…WP-8, this table + per-WP scorecards)
- F-1…F-20 closeout table complete — **this document**
- Parity gate passed on one live special AND the densified weekly — **yes** (`EV/WP-7` dual verifiers, `EV/WP-8`)
- Both owner checkpoints — **packets committed** (`EV/WP-2/checkpoint-1`, `EV/WP-7/checkpoint-2`); sign-off requested retroactively per standing decision #2 (owner directive "no feedback until done")
- No open false-green incidents — **none recorded** (see PROGRESS "False greens"); WP-9 independent audit confirms (`WP-9/audit-report.md`)
