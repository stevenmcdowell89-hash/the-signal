# WP-0(b)+(e) — validate-issue.py extension: calibration evidence

**Builder:** WP-0 builder B · **Date:** 2026-07-19 · **Branch:** `claude/design-system-unification-orchestrate-fauubj`
**Scope:** spec Part 4, WP-0 items (b) and (e). Commands are reproducible; every number below came from a real run, not an estimate (Law 12).

## What was added to `validate-issue.py`

All new checks preserve the existing exit-code contract (0 pass / 1 fail / 2 bad invocation) and report through the same `Report` class `publish-gate.sh` already consumes.

| Check | Scope | Behavior |
|---|---|---|
| `f14-scaffold-tokens` | every issue, **visible prose only** (comments → `<style>`/`<script>` → tags stripped, in that order) | hard-fails `#[N]` / `Issue #[N]`, `ch\d+-\d+` narrated in prose, `viz_\d`, the phrase "research bundle", tool-credit leaks ("Created with … Computer", "Perplexity Computer") |
| `f14-cdn-hostnames` | every issue, visible prose | curated CDN/asset-host patterns (cloudfront, akamaihd, staticflickr, imgix, libemaweb, presspage, gettyimages, shutterstock, `cdn.*`, `media./static./images.*` …). **FAIL on new-system (`data-mx`) issues, WARN on legacy** — see limitation 3 |
| `f14-strategy-vocab` | every issue, visible prose | hard-fails "furniture-first", "motif pack", "design system", event/editorial/transmission "skin" compounds, kit-name+"kit" compounds (dossier/matchday/broadcast/scrapbook/scorecard/paddock/inventory/cinema/library/logbook), `WP-0..9`, "Phase 0", "ev/screen", "publish-gate", "parity gate". "Phase 1–6" only fires within ±120 chars of other strategy vocabulary — see calibration note 2 |
| `law3-word-floor` | **`data-mx` issues only** | Law-3 body-copy floors (weekly 6000 · deep-dive 8000 · season-review 6500 · rewind 7000 · versus 4500 · guide/shortlist/starter-kit 3500 · next 3000 · countdown 4500 · field-guide 6000). Words counted on visible prose minus `<figcaption>`/`<caption>`; format resolved from `data-format` attr > resolved `--format`/`data-special` > filename slug |
| `law9-voices` + `law9-self-quotes` | `data-mx` issues only | distinct named external voices in quote-objects (`<blockquote>` / `class*="quote"` elements) with visible attribution (`<cite>`, attribution-classed child, or trailing em-dash line), keyed on the pre-comma name segment, casefolded. Floors: weekly ≥4, deep-dive ≥5, season-review ≥5, rewind ≥3, countdown/field-guide (trip) ≥6, versus/guide/next/shortlist/starter-kit ≥3. "— THE SIGNAL" never counts and >1 rendering is a separate FAIL |
| `f16-external-img-src` | `data-mx` issues only | any `<img>` src starting `http(s)://` or `//` is a hard fail, offenders listed. Legacy issues keep the existing reachability checks instead |

New-system detection: `data-mx` on the real `<html>` or `<body>` tag (post-`</head>`, comment-stripped), or `data-skin` on `<body>`.

## Per-file verdict table

Full run: `python3 .claude/skills/the-signal/scripts/validate-issue.py <file> --skip-image-urls` (network URL checks skipped — sandboxed environment; all new checks are network-free). Compared against the unmodified HEAD validator run on the same files the same way.

Legend: **HEAD fails** = failing checks under the pre-WP-0 validator (pre-existing, not this work). **NEW fails** = checks added by this work that fail. Verdict Δ = did the exit code change.

| File | HEAD exit | HEAD fails (pre-existing) | NEW fails (this work) | Exit now | Δ |
|---|---|---|---|---|---|
| issues/signal_countdown_2026-06-14.html (holiday ref) | 0 | — | — | **0** | none |
| issues/signal_field-guide_2026-05-17.html (holiday ref) | 1 | length-ceiling (~15k > 12k cap, pre-existing & deliberate per its own comment) | — | 1 | none |
| issues/signal_weekly_2026-07-13.html | 0 | — | — | **0** | none |
| issues/signal_weekly_2026-07-19.html | 0 | — | — | **0** | none |
| issues/signal_deep-dive_2026-05-31.html | 0 | — | — | **0** | none |
| issues/signal_deep-dive_2026-06-30.html | 0 | — | — | **0** | none |
| issues/signal_next_2026-05-31.html | 0 | — | — | **0** | none |
| issues/signal_rewind_2026-07-12.html | 1 | image-urls-static | **f14-scaffold-tokens** (`Issue #[N]` ×1) | 1 | expected new FAIL ✔ |
| issues/signal_deep-dive_2026-05-26.html | 1 | length-ceiling | **f14-scaffold-tokens** (ch-tokens ×27 narrated, viz_ ×5, "research bundle" ×5) | 1 | expected new FAIL ✔ |
| issues/countdown-wcq.html | 1 | 9 pre-existing (old-format file auto-detected as weekly) | **f14-scaffold-tokens** (tool-credit "Created with Perplexity Computer") | 1 | expected new FAIL ✔ |
| tools/fixtures/negative/attempt2-stub-flat-season-review.html | 1 | special-variety | **law3-word-floor** (542 < 6,500) · **law9-voices** (0 external < 5) · **law9-self-quotes** (2 > 1) · **f14-strategy-vocab** ("FURNITURE-FIRST" in cover meta) | 1 | expected new FAILs ✔ |
| tools/fixtures/negative/attempt2-flat-redress-deep-dive.html | **0** | — (passed everything at HEAD — the F-19 problem in miniature) | **law9-self-quotes** (6 "— The Signal" renderings > 1). law3 passes (18,861 wds), law9-voices passes exactly (5), f16 passes (18 local imgs) | **1** | fixture now fails a gate ✔ |
| issues/signal_weekly_2026-04-05 … 07-05 (13 pre-Transmission weeklies) | 1 | 8–10 pre-existing each (weekly-structure/*, weekly-visual/*, image-floor, length-floor…) | — | 1 | none |
| issues/countdown-efteling, issue-1, issue-2, shortlist-switch2-solo, starterkit-*, versus-tlm-ibex | 1 | 8–11 pre-existing each (old ad-hoc files, auto-detected weekly) | — | 1 | none |
| issues/versus-sanguli-clodia.html | 1 | special-variety | — | 1 | none |
| issues/signal_weekly_2026-06-21.html | 1 | issue-in-numbers + 8 weekly-structure/visual | — | 1 | none |
| issues/TEST-signal_field-guide_2026-05-17.html | 0 | — | — | *deleted (WP-0e)* | — |

**Net effect of the new checks on exit codes: only `attempt2-flat-redress-deep-dive.html` changed verdict (0→1). Every other new FAIL landed on a file already failing for its own pre-existing reasons, and every clean file stayed clean.** The three expected known-bads (rewind `#[N]`, deep-dive 05-26 scaffold leaks, countdown-wcq tool credit) all fire on exactly the expected pattern.

New WARN-level findings (PASS preserved): `f14-cdn-hostnames` warns on signal_countdown_2026-06-14 + signal_field-guide_2026-05-17 (`cdn.libemaweb.com`, `content.presspage.com` in visible credit lines — true findings, deliberately warn-only on legacy) and signal_weekly_2026-06-07 (`media.formula1.com`).

## Fixture note (task item 3)

`attempt2-stub-flat-season-review.html` already carries `<body … data-mx="page" data-skin="event" …>` on its real body tag, so the Law-3 check applies to it as-is. **No fixture was modified and no tools/fixtures/ special-casing was added** — the data-mx path covers it.

## False-positive calibration (survey-driven + one iteration)

Calibration was done by surveying every candidate pattern against the visible prose of all 31 issues + 2 fixtures *before* finalizing the regexes, then re-running the full suite. Findings that shaped the design:

1. **Tool credits:** "created with" appears in legitimate prose — signal_weekly_2026-04-26 has "the tension it **created with** Washington". Pattern made case-sensitive and anchored to a tool shape (`Created with … Computer`, named AI tools). **One post-hoc iteration:** the first draft also matched bare "Perplexity"; narrowed to "Perplexity Computer" because the magazine covers consumer-AI news (`ai_search` topic family) and a future weekly could legitimately name the company.
2. **Phase names:** bare "Phase 1–6" false-fires on real archive prose — issue-1.html ("Gaza… **Phase 1** of the US-backed 20-point plan"), versus-tlm-ibex.html ("Hybrid Maintenance **Phase 3** sessions/week"). Resolution: "Phase 1–6" needs another strategy term within ±120 chars; "Phase 0" and `WP-N` always fire. Verified: both archive files pass; a synthetic "Phase 3 skin rollout of the motif pack" fires.
3. **CDN hostnames:** a generic hostname matcher is unusable — legacy issues legitimately cite publisher domains in credits (goal.com, formula1.com, allears.net…), and both holiday references carry genuine CDN hosts in visible credit lines. Resolution: curated CDN/asset-host list; hard-fail scoped to `data-mx` issues, WARN on legacy. This keeps the mandated "both holiday issues PASS" while still surfacing the finding.
4. **"skin":** only flagged in event/editorial/transmission compounds per the work order — bare "skin(s)" never fires.
5. Law-3 / Law-9 / F-16 scoped to `data-mx` so 30+ legacy archive issues can't be retro-failed (mirrors the existing `LENGTH_FLOORS` weekly-only precedent in the same file).

After the survey-driven design, the **first full-suite run already produced the exact target verdict set**; the only regex change after any full run was the Perplexity narrowing in (1).

## Other WP-0(e) work verified here

- `validate-chapter-plan.py --test`: **57/57 self-tests pass**, including 4 new tests (blueprint rejected; guide valid parallel; next valid sequential; next+parallel rejected).
- `python3 -m py_compile` clean on: validate-issue.py, validate-chapter-plan.py, validate-research-bundle.py. `bash -n` clean on check-image-diversity.sh. image-source-types.json parses.
- F-17: Getty/Shutterstock reclassified `restricted`. Verified with synthetic fixtures: check-image-diversity.sh warns and a page whose only diversity beyond restricted is 2 types now **FAILS** (restricted excluded from the count); validate-research-bundle.py warns per-entry and excludes restricted from its diversity count.
- TEST-file deletion: whole-repo grep (code, manifests, archive-manifest.json, sw.js, functions/, _worker.js) found **zero references** to either `test_signal_field-guide_2026-05-17.html` or `issues/TEST-signal_field-guide_2026-05-17.html` (the only near-hit was the JSON key `latest_weekly`). Both deleted via `git rm`.

## Known limitations (no overclaiming)

1. **Law-9 is a markup-level count.** It trusts attribution text as written; it cannot know whether a quote is verbatim, real, or invented — that stays a Part-6 human/verifier duty, and the check's own output says so. Attribution extraction is heuristic (`<cite>` > attribution-classed child > trailing em-dash line); an exotic quote markup with none of these counts as "unattributed" and is reported as such. `class*="quote"` regions are bounded at 1,200 chars because regex cannot balance tags.
2. **Law-3 counts visible prose minus figcaption/caption only** — masthead/nav/chrome words are included, so the measured number slightly overstates true body copy and the floor errs *lenient*. It can never spuriously fail a compliant issue; a stub (542 words) is caught regardless.
3. **`--strict` promotes the legacy CDN warning to a failure** (pre-existing strict semantics apply to all warnings). publish-gate.sh runs non-strict, so this doesn't change the ship path.
4. **`f14-strategy-vocab` accepts a residual risk** that a future tech/design article legitimately says "design system" or "motif pack" in reader copy. Zero hits in the current archive; if it ever false-fires the fix is editorial rephrasing or a scoping decision recorded then — not silently weakening the gate now.
5. **signal_field-guide_2026-05-17 fails `length-ceiling` under HEAD and under this build alike** (~15k words vs the 12k cap its own comment says was tuned to trip it). Pre-existing, out of WP-0 scope, left untouched; all *new* checks pass on it.
6. The flat-redress fixture's principal gate remains the Part-5 parity gate (Laws 1/5 — flatness/motion, which a static text validator cannot see). Its new `law9-self-quotes` failure here is a bonus true positive, not the fixture's full indictment.
7. Word/voice checks were validated against the current corpus; new-system markup (WP-2 furniture) may introduce quote-object classes not containing "quote" — if so, `_QUOTE_CLASS_OPEN_RE` needs the new class stem added, and the calibration here must be re-run.
