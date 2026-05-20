---
name: the-signal
description: >-
  Generate issues of The Signal, a weekly personal magazine designed to be
  read on a Sunday morning with coffee. Use when asked to run, generate,
  create, or schedule The Signal, or when the user mentions "the signal",
  "signal magazine", "sunday magazine", "personal magazine", "run the
  signal", "deep dive", "countdown", "season review", "versus", "rewind",
  "starter kit", "blueprint", "shortlist", or "field guide" in the context
  of their personal weekly reading. Supports multiple issue formats:
  standard weekly, deep dive, countdown, season review, versus, rewind,
  starter kit, blueprint, shortlist, and field guide. Includes HTML
  template, editorial spec, and a compliance checklist.
---

# The Signal

Generate issues of The Signal — a weekly personal magazine for Sunday morning reading.

Version 8.11.0. See `CHANGELOG.md` next to this file for the full version-by-version history of editorial and visual changes. Editorial substance is defined in `references/editorial-spec.md` and its sliced views in `references/spec/`. This file describes only **how the pipeline runs on Claude Code**.

## Model Selection

The Signal runs as a multi-subagent pipeline. Each role has different reasoning needs, so models are selected by **role intent** with **fallback chains** — never by hard-coded model name. When Claude releases a stronger or cheaper model, advance the chain.

| Role | Primary | Fallback | Why this intent |
|---|---|---|---|
| **Researcher** | Sonnet 4.6 | Haiku 4.5 | Web search + synthesis. Coverage and cost matter more than top reasoning. |
| **Planner** | Opus 4.7 | Sonnet 4.6 | Structured reasoning, JSON output, hard constraints. Logic dominates. |
| **Writer** (any format) | Sonnet 4.6 | Haiku 4.5 | Tight per-chapter brief from planner. Sonnet follows constraints reliably at low cost. |
| **Repair** | Sonnet 4.6 | — | Surgical fix to a failing chapter. Same skill as writer, narrower scope. |

**Rationale.** The planner is the only role where premium reasoning materially affects output (whole-issue coherence, validator-passing JSON, anti-overlap logic). Writers operate on a tight brief from a strong planner — Sonnet performs at the same quality as Opus once the planner has done the hard thinking. Researchers and repairers are even cheaper.

**Spawning.** Use the `Agent` tool with `subagent_type` and the optional `model` parameter:
- Researcher → `subagent_type: "Explore"` (read-only research/search), `model: "sonnet"`.
- Planner → `subagent_type: "general-purpose"`, `model: "opus"`.
- Writer → `subagent_type: "general-purpose"`, `model: "sonnet"`.
- Repair → `subagent_type: "general-purpose"`, `model: "sonnet"`.

**Override.** If the reader explicitly says "use the top model" or "lean cheaper", honour the override across the whole pipeline.

## Workflow

The Signal runs ONE pipeline for every issue — standard weekly or special edition. The format is decided in Phase 0; Phases 3–10 then run for every format. The format only changes WHICH chapters get written and HOW writers are sequenced (parallel vs sequential), not WHICH phases run.

The pipeline: Phase 0 (decide format) → Phase 3 (researcher subagent) → **Phase 3a-verify (orchestrator WebFetch every URL — v8.13.8)** → Phase 3b (research-bundle validator) → Phase 4 (planner subagent + validator) → Phase 5 (writer subagents, parallel or sequential) → Phase 6 (stitch) → Phase 7 (per-chapter Gate 1) → Phase 7.5 (release-date check) → **Phase 7.6 (structural + asset validator — `validate-issue.py`)** → Phase 7.7 (image-source diversity — `check-image-diversity.sh`) → **Phase 7.8 (DOM visual smoke test — `visual-smoke-test.py`)** → Phase 8 (stitched-issue Gate) → Phase 9 (repair if needed) → Phase 10 (deliver + publish + CI verification).

There is NO separate "lightweight" path. Standard weeklies run the full pipeline same as specials. Build dir is `/tmp/signal-build/`, cleared at the start of every run.

> **Environment note.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repository at `stevenmcdowell89-hash/the-signal` is the only durable store — state, issues, and the cost log all live there. Per-session paths like `/tmp/signal-build/` are scratch only.

> **Gate discipline (MANDATORY).** Every script-backed gate in this workflow — `validate-chapter-plan.py`, `validate-research-bundle.py`, `stitch-issue.sh` (which embeds the holiday-activation rewrite + banned-vocabulary scan + holiday scaffold override + holiday half-wrap reorganisation), `check-release-dates.sh`, `validate-issue.py`, `check-image-diversity.sh`, and `visual-smoke-test.py` — is **run by the orchestrator itself**, not delegated to a subagent. The gate's verdict is its **exit code**, full stop. A subagent claiming "gate X passed" is not acceptable evidence — the orchestrator must invoke the script via `bash` or `python3`, read the printed report, and read the exit code before advancing. If a subagent reports success but the orchestrator did not run the gate, the orchestrator runs it now. This rule exists because subagents have been observed reporting "gate passed" for gates they never invoked.

---

## Phase 0 — Read state + Decide format

This phase runs first every Sunday and decides what kind of issue today's run produces. It is mechanical wherever possible — calendar arithmetic and state lookups, not editorial judgement. Once it commits a format, the rest of the pipeline runs the same shape.

### 0a. Clone repo + read state + spec (mechanical)

**Clone the repo first.** State lives in the GitHub repo, not in the ephemeral container. The repo is the single source of truth.

```bash
cd /tmp && rm -rf the-signal && git clone https://github.com/stevenmcdowell89-hash/the-signal.git --depth 1
```

If `git clone` fails (network or auth), fall back to reading specific files with the `mcp__github__get_file_contents` tool against `stevenmcdowell89-hash/the-signal`.

Then read `/tmp/the-signal/state/signal-state.json` (full state). Read `references/editorial-spec.md` (full spec, from this skill). Do NOT yet read `references/sections.md`, `references/compliance-checklist.md`, or any file under `assets/css/`/`assets/script.js` — those load later by role.

**Legacy note:** the historical path `/home/user/workspace/signal-state.json` is no longer authoritative. The cloned repo at `/tmp/the-signal/state/signal-state.json` is the only state.

### 0b. P1 calendar check (mechanical, no web search)
P1 triggers are calendar-fixed. They always win. Compute against today's date and the state file:

- **Field Guide:** today is the Sunday closest to (`upcoming_trips[0].start` minus 6 weeks). Window: ±3 days.
- **Countdown:** today is the Sunday closest to (`upcoming_trips[0].start` minus 2-3 weeks). Window: ±3 days. If both Field Guide and Countdown could fire on the same Sunday, Field Guide wins (earlier in the trip arc).
- **Half-year Rewind:** today is the last Sunday of June. **Defer rule:** if `upcoming_trips[0]` overlaps that Sunday or the following week, defer to the first Sunday at least 5 days after the trip ends.
- **Year-end Rewind:** today is the last Sunday of December.
- **Season Review:** Serie A or PL closing weekend has just concluded (the league has played its final matchday in the last 7 days) AND no Season Review fired for that league this season.
- **Deep Dive (scheduled):** ALL of these must hold: (1) `deep_dive_schedule.next_due` is today or earlier; (2) `deep_dive_backlog` is non-empty; (3) no other P1 fires today; (4) today is not inside a trip window from `upcoming_trips`. If all four hold, pop the top non-`needs_sharpening` entry from `deep_dive_backlog`, commit to Deep Dive with that topic, set `deep_dive_schedule.last_fired = today`, advance `next_due` by `cadence_weeks[0]` weeks. If the top entry has `needs_sharpening: true`, skip it and try the next; if every remaining entry is `needs_sharpening`, fall back to a standard weekly and leave `next_due` unchanged so the user can resolve the sharpening on a manual pass.

If ANY P1 fires, commit to that format immediately. **Skip 0c, 0d, 0e.** Continue at Phase 3.

If multiple P1s fire on the same Sunday (rare): Field Guide > Countdown > Season Review > Rewind > Deep Dive.

### 0c. P1-corridor lockout for P3 (mechanical)
If no P1 fires today, compute whether today sits inside a P1 corridor: any Sunday within 4 weeks before OR 4 weeks after a P1-eligible Sunday counts as inside the corridor.

If today is inside a P1 corridor, set `p3_locked = true`. P3 cannot fire this Sunday — the schedule is already booked. (P2 can still fire on a genuinely big event — that override is independent of P3 cadence.)

If today is outside every P1 corridor, set `p3_locked = false`.

### 0d. P2 event-driven scout (light web search)
Run 2–4 targeted searches for major events that could warrant a special this week:
- Major game/film release that warrants a Versus or Deep Dive (Switch 2 anniversary, blockbuster sequel, AAA game launch with cultural noise)
- League/tournament conclusion that the rotation hasn't covered yet (e.g. an early Season Review for a finished European league)
- A topic that has accumulated enough running coverage to deserve a Deep Dive in its own right

**P2 trigger criteria:** the event must be (a) genuinely big, (b) audience-aligned with the reader profile, (c) NOT just a news beat that fits in a standard weekly's World/Touchline/Pixel & Byte sections. The bar is high — most weeks no P2 fires. When in doubt, default to standard weekly and cover the event as a section lead.

If a P2 fires, commit to that format and continue at Phase 3. Skip 0e.

### 0e. P3 cadence safety net (mechanical)
If no P1 or P2 fired AND `p3_locked = false`:
- Compute weeks since `last_special_date` from state.
- If ≥ 5 weeks, P3 fires.
- Pick the next format from the P3 rotation (Shortlist, Starter Kit, Blueprint, Versus, Deep Dive on a non-trip topic). Read `recent_special_formats` from state — pick the format that has not appeared in the last 6 specials. If multiple formats tie, pick the one with the strongest topic surfaced during 0d.
- Commit that format and continue at Phase 3.

If no P1, no P2, and (P3 is locked OR < 5 weeks since last special), commit to standard weekly (`format_committed = weekly`).

### 0f. News-of-the-week scout (weekly only, optional)
If the committed format is `weekly`, run a quick news scout now to surface trigger context that the researcher subagent will pick up in Phase 3a. **Group 1 News & Geopolitics scout MUST explicitly check:** (a) UK/Irish/Scottish/Welsh/European elections in past 7 days, (b) live PM or opposition-leader leadership challenges, (c) Cabinet-level resignations or sackings, (d) major government policy or headline legal rulings. See the UK / national politics rule in editorial-spec.md. Pass any landscape-shift findings to the researcher in Phase 3a as priority leads.

This scout is optional — the researcher subagent in Phase 3 will do its own news pass. The 0f scout exists so the main loop knows whether the issue is shaping up around a landscape-shift story (which influences cover headline framing and rotating-section selection).

### 0g. Route
Every format — weekly or any special — continues at **Phase 3** below. There is no second path.

---

## Phase 3 — Derive execution mode

From the committed format, derive `execution_mode`:
- **Parallel mode** (Countdown, Field Guide, Shortlist, Starter Kit, Blueprint, weekly): writer subagents in Phase 5 spawn in one batch.
- **Sequential mode** (Deep Dive, Versus, Rewind, Season Review): writer subagents in Phase 5 spawn one at a time, each reading its predecessor's output to maintain throughline.

### Phase 3a — Researcher subagent
Spawn an `Agent` with `subagent_type: "Explore"` and `model: "sonnet"` (fallback `"haiku"`). In the prompt, tell it to read `references/spec/global.md` (sections `key-rules` and `image-integrity`), `references/spec/triggers.md` (full file — short), and the matching format section in `references/spec/formats.md` (H2 anchor for the issue's format). Pass committed format + state snapshot inline. The subagent does all web research and writes `/tmp/signal-build/research-bundle.json` (sources, key facts, image candidates with attribution, ongoing-story status, training-phase context).

**MANDATORY (v8.13.7) — Researcher MUST verify every image URL with WebFetch.** For each candidate, run WebFetch on the URL. Accept it ONLY if the response is 2xx and `Content-Type` starts with `image/`. Record the result inline on the candidate as:
```json
"verified": { "head_status": 200, "content_type": "image/jpeg", "verified_at": "<ISO timestamp>" }
```
If the URL is a brand-site PAGE (returns `text/html`), open it with WebFetch and find the real `<img src>` CDN URL in the markup — use THAT URL, not the page URL. If you cannot find a working URL for a subject, DROP the candidate from the bundle. Do not ship `"verify later"` notes. The bundle must surface at least 16 distinct verified URLs (per `thresholds.min_unique_candidates`) so writers don't recycle.

Common fabrication traps to avoid:
- Wikimedia `/wiki/commons/thumb/<hash>/<hash>/<file>.jpg/1280px-<file>.jpg` — only exists if a thumbnail at that exact size was pre-generated. Use the canonical `/wiki/commons/<hash>/<hash>/<file>.jpg` or `Special:FilePath/<file>?width=N` instead.
- Made-up filenames (e.g. `Efteling_-_Polles_Keuken_(2).jpg` when the real file is `Polles_Keuken_Efteling_2.JPG`). Confirm exact spelling via `site:commons.wikimedia.org "File:..."`.
- Brand-site page slugs (e.g. `https://www.efteling.com/en/park/restaurants/polles-keuken`) — those are HTML pages, not images. The validator rejects them with no extension AND no image content-type.

**Cost log:** after the researcher returns, run `bash scripts/log-call.sh researcher <model> <issue_id> - 0 ok` (one call). See § Cost Logging.

### Phase 3a-verify — Orchestrator-side WebFetch (MANDATORY, v8.13.8)

The researcher subagent is trusted to call WebFetch, but its `verified` block is self-attested — a fabricated `{head_status: 200, content_type: "image/jpeg"}` passes Phase 3b just as easily as a real verification. To close this hole, the **orchestrator (you, the main pipeline loop)** MUST independently WebFetch every URL in `image_candidates` AFTER the researcher returns and BEFORE running Phase 3b.

For each `image_candidate[i]`:
1. Call `WebFetch(url)` directly using your own tool — not the subagent's.
2. Read the response status and `Content-Type`.
3. Replace the candidate's `verified` block with the orchestrator's actual result, including a `verified_by: "orchestrator"` marker.
4. If status is non-2xx OR Content-Type doesn't start with `image/`, **remove the candidate from the bundle**. Do not patch it through.
5. After the loop, rewrite the bundle and proceed to Phase 3b.

This is the only enforcement layer the researcher cannot fake. The CI workflow (`.github/workflows/issue-validation.yml`) re-checks every URL with full network access — fabricated `verified` blocks that pass orchestrator verification but fail CI will surface as a red ✗ on the publish commit (and an auto-filed GitHub issue).

If WebFetch fails for the orchestrator in a given environment (egress restricted on the URL's host), record `verified.head_status: "blocked"` and `verified.content_type: "blocked"` on the candidate, and rely on the CI workflow as the authoritative gate. The candidate is NOT dropped — it's flagged for CI to resolve.

### Phase 3b — Research-bundle validator (mandatory before planner spawns)
Run `python3 scripts/validate-research-bundle.py /tmp/signal-build/research-bundle.json`. The script enforces the `image_candidates` rules from `references/spec/global.md` image-integrity:

- Every `url_or_keyword` must be an `http(s)://` URL (keywords are rejected — they force writers to invent URLs, the RT-16 trap).
- ≥3 of the 5 source types represented (press_kit / government / archive / news_cdn / wikimedia — see `references/image-source-types.json`).
- Wikimedia ≤4 entries AND ≤30% of total (whichever is smaller). Any single domain >50% is RT-5 hard fail.
- Ambiguous domains like `live.staticflickr.com` require an explicit `source_type` field on the candidate.

**Non-zero exit code = research is not shippable to writers.** Re-spawn the researcher with the failure report inlined into the prompt. The researcher uses WebSearch / WebFetch to find verified URLs from the under-represented source types and rewrites `image_candidates`. Re-validate. Max 2 retries before escalating to the reader. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

This gate exists because the 17 May test issue shipped with 14 fabricated image URLs (writers constructed URLs because the bundle gave them keywords like "Wikimedia Commons: Keir Starmer"). Catching the broken bundle upstream costs one extra script run; catching the fabrications downstream costs a full writer re-run plus image substitution work.

### Phase 4 — Planner subagent + validator gate
Spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). Pass the path to `research-bundle.json`. In the prompt, tell it to read `references/chapter-plan-schema.md`, `references/pre-flight.md`, and the planner's spec slice: `references/spec/global.md` sections `identity`, `key-rules`, `markup-contracts`, `accent-lockdown`, `stat-budget`; plus the format's H2 anchor in `references/spec/formats.md`; plus `references/spec/specials.md` section `overview` if special edition. The subagent writes `/tmp/signal-build/chapter-plan.json`.

Run `python scripts/validate-chapter-plan.py`. **If invalid:** re-spawn planner with the validator's error report (max 2 retries). After 2 retries, advance the planner fallback chain (Opus → Sonnet) and try once at the next tier.

**Cost log:** after each planner attempt, run `bash scripts/log-call.sh planner <model> <issue_id> - <retry_count> <outcome>`. Outcome is `validator_fail` if validator rejected and another retry is coming, `ok` if the plan passed, `escalated` if the fallback chain ran out. See § Cost Logging.

### Phase 5 — Writer subagents (format-aware)
Read `chapter-plan.json`. For each chapter, spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "sonnet"` (fallback `"haiku"`). In the prompt, pass: the pre-flight.md path, the chapter brief (one chapter object from the plan), the research-bundle.json path, plus the H2 anchor reference for the issue's format inside `references/spec/formats.md`. Writers also read `references/spec/global.md` sections `markup-contracts`, `ground-discipline`, `accent-lockdown`. **HOLIDAY FORMATS ONLY (`countdown`, `field_guide`):** writers MUST ALSO read `references/spec/specials.md` § `holiday-identity` for the `.hol-*` component map and § `hype-chapter-visuals` if any chapter is hype-flagged. The default `sp-*` vocabulary (`.sp-chapter-gate`, `.sp-spread`, `.sp-pull-break`, `.sp-marginalia`, `.sp-brief`, `.sp-dash`, `.sp-chapter-chrome`, `.unmissables`/`.unmissable`) is HIDDEN by tier 11 (`36-holiday-identity.css`) on holiday issues — chapters using it render as blank stretches. Writers use `.hol-cover`, `.hol-half`, `.hol-transit`, `.hol-anchor`, `.hol-unmissable`, `.hol-polaroid`, `.hol-postcard`, `.hol-stamp`, `.hol-marquee`, `.hol-dont-miss`, `.hol-chalkboard`, `.hol-meanwhile`, `.hol-subscribe`, `.hol-footer-row`. Each writer outputs `/tmp/signal-build/chapters/<chapter_id>.html` (chapter-only, no scaffold).

- **Parallel mode** (Countdown, Field Guide, Shortlist, Starter Kit, Blueprint, weekly): spawn all writers in one batch — issue every `Agent` call in a single message.
- **Sequential mode** (Deep Dive, Versus, Rewind, Season Review): spawn writers one at a time. After each chapter completes, the next writer reads its predecessor's output to maintain throughline.

**Cost log:** after each writer returns, run `bash scripts/log-call.sh writer <model> <issue_id> <chapter_id> 0 ok`. One call per chapter. See § Cost Logging.

### Phase 6 — Stitch
Run `bash scripts/stitch-issue.sh --plan /tmp/signal-build/chapter-plan.json --out signal_<format>_<date>.html --issue-number <N>`. Stitcher concatenates chapters, wraps in scaffold, injects CSS (alphabetical cascade) and JS deterministically. The `--issue-number` arg is required for standard weeklies (it's substituted into the footer `Issue #[N]` placeholder) and should be the value `last_issue_number + 1` from state. For specials, pass `--issue-number ""` (empty) or omit — specials don't carry issue numbers and the footer uses the format/topic header instead. **v8.18.1:** the stitcher now also substitutes `[DATE RANGE]` (computed as a one-week range ending on the issue date for weeklies, or the single date for specials) and `[Date]` (pretty-formatted issue date) placeholders from the head-open and footer templates. Writers don't touch these; the stitcher owns them. **v8.13.3:** for `countdown` and `field_guide` formats, stitch-issue.sh auto-rewrites the `<body>` tag to `<body class="is-special" data-special="<format>">` (the activation that switches on tier 11/12/13/14 CSS + JS), runs a banned-vocabulary grep gate (`sp-chapter-gate`/`sp-spread`/`sp-pull-break`/`sp-marginalia`/`sp-brief`/`sp-dash`/`sp-chapter-chrome`/`unmissables`/`unmissable`) and exits non-zero if any are found, and runs a positive-structure check that fails the stitch if no `.hol-half` is present. Writers cannot accidentally ship a holiday issue without the Holiday Identity activation.

**v8.13.4 fix:** the body-rewrite regex is now anchored to `</head>` (not the first `<body>` in the document). The scaffold `00-head-open.html` contains a documentation comment with an example body tag (`<body class="is-special" data-special="countdown"> (or field-guide).`), and a naive `count=1` regex matches that example FIRST and silently leaves the real `<body>` bare. Anchoring to `</head>` guarantees we rewrite the real DOM tag. If you edit stitch-issue.sh, preserve this anchoring.

**Plan-level multi-venue flag.** If `issue_meta.multi_venue` is `true` in chapter-plan.json, the stitcher additionally stamps `data-multi-venue="true"` on the rewritten body. This activates tier-9 per-venue scoping for Countdown (and is harmless on Field Guide, which uses the `.hol-half--one`/`--two` structure instead). The planner sets this flag for issues with two named venues; do not set it manually.

### Phase 7 — Per-chapter Gate 1 (during pipeline)
Each chapter has already self-audited via pre-flight.md. Now grep-scan every chapter HTML for the Gate 1 hard-fail patterns from `references/compliance-checklist.md` (1A reader-profile leaks, 1B fabrication markers, 1C staleness, 1E markup contracts, 1F image-caption integrity). Any failure → enter repair flow.

### Phase 7.5 — Release-date sanity check (mandatory before publish)
Run `bash scripts/check-release-dates.sh <stitched-html-path>`. The script extracts every claim of a date or relative-time phrase adjacent to a media name (TV, film, game, book, album), plus any line that mentions a locked-register entry (Andor, Tales of the [Jedi/Empire/Underworld], Skeleton Crew, Acolyte, Maul: Shadow Lord, Mandalorian and Grogu). Output is written to `/tmp/signal-date-claims.txt`.

The agent then walks the report. For each surfaced claim:
1. If it matches a locked-register entry in `references/compliance-checklist.md` (1B), verify the date in the HTML matches the locked date exactly. Mismatches are automatic FAIL.
2. If it does not match the register, run a quick web search (`<show name> release date` is sufficient for a single check) and verify YEAR. Wrong year or already-aired-when-framed-as-upcoming is automatic FAIL.
3. If a relative-time phrase is used ("last September", "this summer", "coming next month") without explicit year context, treat as suspect by default — verify or rewrite.

Fix every FAIL before proceeding to Phase 8. The release-date class of error is the single most-cited fabrication category in reader feedback (Andor S2 framed as current; Tales of the Underworld framed as upcoming when it aired in 2025; Andor S2 end-date wrong by months). This phase is non-skippable.

### Phase 7.6 — Structural + asset validator (mandatory before publish)

Run `python3 scripts/validate-issue.py <stitched-html-path> --format <format>` and, when applicable, add `--multi-venue` for issues with two or more named venues.

The script performs four classes of check:

1. **Structural well-formedness** — doctype, `</html>`, `</body>` present.
2. **Banned literal placeholders** in the rendered DOM (NOT inside `<style>`/`<script>`/`<!-- -->`): `src="..."`, `src="…"`, `href="#TODO"`, `[PLACEHOLDER]`, `[TODO]`, `[DATE RANGE]`, `[YEAR]`, `PASTE contents of`, `See assets/script.js`, `<!-- INJECT:CSS -->`, `<!-- INJECT:JS -->`. These ship invisibly through other gates if not checked.
3. **Holiday activation** (for `countdown` / `field-guide`): the real `<body>` tag (the one after `</head>`, not an example in a comment) must carry `class="is-special"` and `data-special="<format>"`. The required holiday components (`.hol-masthead`, `.hol-cover`, `.hol-half`) must be present at least once each (BEM child classes count: `hol-masthead__title` implies the masthead block exists). For multi-venue issues, `data-multi-venue="true"` must be on the body and at least two distinct `data-venue=` attributes must be present.
4. **Image URL HEAD-checks** — every `<img src="…">` and inline `background-image: url(…)` URL in the DOM is HEAD-requested in parallel (5s timeout, accepts 2xx/3xx, falls back to range-GET for servers that reject HEAD with 403/405/501). Fail-list any 4xx/5xx/timeout/DNS. URLs inside `<style>` (the inlined stylesheet) are intentionally NOT checked — those are skill-controlled, not writer-introduced.

Non-zero exit code = the issue is **not shippable**. Fix the underlying defect (re-spawn the relevant writer with the failure report) and re-run from Phase 6. **The orchestrator runs this script directly and reads the exit code.** Subagent self-reports of "validate-issue passed" are not acceptable — the orchestrator runs `python3 scripts/validate-issue.py` itself.

Use `--skip-image-urls` ONLY when offline or when the entire issue is hand-curated (rare). Use `--strict` to promote warnings (CSS-class sanity, etc.) to failures.

**Egress-restricted environments.** Claude Code on the web runs in a managed container with a curated outbound-HTTPS allowlist (`x-deny-reason: host_not_allowed` for unlisted hosts). When every image URL fails identically with that signature, the validator degrades the image-urls check to a WARN with a "re-run elsewhere" note rather than a hard fail. Structural and activation checks are unaffected. The recommended pattern: let the orchestrator run `validate-issue.py` here for structural checks; before clicking "publish," run the validator once more from your local machine (or wire it into a GitHub Actions check on the issues directory) to get the real image-URL verdict.

This phase replaces what was previously an implicit "browse the issue manually" step that the orchestrator was skipping. The most common failure modes it catches:

- **Bare `<body>` tag** — root cause of "no background, no holiday styling" bugs. Even if `stitch-issue.sh` claims it rewrote the body, this gate re-verifies the result.
- **Missing `.hol-masthead` band** — a writer omitted the masthead snippet from the cover/kicker chapter.
- **Hallucinated image URLs** — a researcher subagent guessed plausible-looking CDN paths instead of fetching candidates.
- **Unreplaced writer placeholders** — `src="..."` slots a writer left in for "fill in later" but never filled.

### Phase 7.7 — Image-source diversity (mandatory before publish)
Run `bash scripts/check-image-diversity.sh <stitched-html-path>`. The script classifies every `<img src>` and `background-image` URL via `references/image-source-types.json` and enforces:

- No single domain >50% of images (RT-5 hard fail)
- Wikimedia ≤30% of images AND ≤4 entries (whichever is smaller)
- ≥3 distinct source types from the 5-type menu

Unknown domains (not in the lookup) trigger an advisory rather than a hard fail — extend `references/image-source-types.json` when a new recurring source appears.

**Non-zero exit code = the issue is not shippable.** Identify the over-represented domain, swap entries to under-represented source types (typically by extending research to press kits / government Flickr / archive hosts), update `research-bundle.json`, re-run the affected writer(s), re-stitch. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

This gate exists as a downstream catch for what Phase 3b missed — writers omitting some bundle images and skewing the final ratio, or new domains slipping in via writer prose that weren't in the bundle. The upstream validator (Phase 3b) is the primary defence; this is defence in depth.

### Phase 7.8 — DOM visual smoke test (mandatory before publish)
Run `python3 scripts/visual-smoke-test.py <stitched-html-path> --format <format> [--multi-venue] --bundle /tmp/signal-build/research-bundle.json`. A pure-Python DOM analyser that catches seven shipping-defect classes the earlier gates miss because they check structure or HTTP status, not what would render:

- **D1 duplicate chrome** — both the legacy `header.cover` / `div.mast` / `footer.footer` AND the holiday `.hol-cover` / `.hol-masthead` / `.hol-footer-row` present in the same DOM. Defence-in-depth alongside the stitcher's holiday scaffold override.
- **D2 un-wrapped venue chapters** — on holiday + multi-venue issues, venue chapters that are NOT DOM-descendants of the matching `.hol-half--N` wrapper.
- **D3 page-url-as-image** — any image reference whose URL has no recognised image extension (almost always a brand-site page URL pasted where a CDN URL was expected).
- **D4 orphan holiday elements** — a multi-venue holiday issue with NO `.hol-half` blocks at all.
- **D5 empty hero bands** — `.hol-cover` or `.hol-half__opener` with no visible text.
- **D6 duplicate image URLs** — any image URL used more than once in the rendered DOM. Default max = 1 (override with `--max-uses-per-url N`). Catches the recurring "writer ran out of bundle URLs and recycled" pattern.
- **D7 unbundled images** — when `--bundle <path>` is supplied, every image URL in the DOM must appear verbatim in `image_candidates`. Writers that invent URLs (even legitimate-looking CDN paths) fail this gate — the bundle is the only authority.

Runs without network, so it works in every environment (including the egress-restricted managed runtime where Phase 7.6's image-URL HEAD check degrades to a warning). **The orchestrator runs this script directly and reads the exit code** — non-zero = issue NOT shippable. **Always pass `--bundle`** so D7 is active; D6+D7 together are the unbreakable rule against the broken-images class.

This is the "browser-eye QA" replacement for environments without headless-Chromium. It's deliberately conservative — false negatives are possible, but the five detectors target the recurring failure modes that have shipped or nearly shipped in prior runs.

### Phase 8 — Stitched-issue Gate (Gate 3)
Cross-chapter checks: no two consecutive sections same component pattern, accent lockdown across chapters, link health, ongoing-story consistency. Plus Gate 2 editorial/visual quality. (Image-source diversity is enforced by Phase 7.7.) Fix any failures.

### Phase 9 — Self-healing repair (v8.13.8 — autonomous, max 3 rounds)

The reader is the **audience**, not a triage layer. Phase 9 must resolve gate failures itself; if it cannot, Phase 10 ships the best-effort issue anyway. Last week's issue stays accessible via `index.html` — a less-than-perfect new issue is preferable to no new issue.

**Round 0 — image defects auto-repair first (programmatic, no subagent).**
Run `python3 scripts/auto-repair-images.py <stitched-html> /tmp/signal-build/research-bundle.json`. This script rotates unused bundle URLs through every defective image slot in the rendered DOM (duplicates from D6, unbundled from D7, page-URLs from D3). It is pure Python — no subagent dependency. Exits 0 if all defects fixed, 1 if some are unfixable (bundle exhausted).

Why this runs first: image defects are mechanically fixable from the existing bundle, and the bundle is the only authority writers may use anyway. Running this BEFORE spawning expensive repair agents avoids wasting writer-round budget on what's really an asset-substitution problem.

After auto-repair runs, re-stitch is **not** needed (the script edits the stitched HTML in place); just re-run Phase 7.5/7.6/7.7/7.8 gates.

**Rounds 1–3 — targeted subagent repair for content defects.**
If gates STILL fail after auto-repair (or fail in non-image ways — release-date errors, ground discipline, accent leaks, banned phrases), spawn ONE repair `Agent` (`subagent_type: "general-purpose"`, `model: "sonnet"`) per round. Pass the chapter HTML + the specific failure report + the bundle. Repair re-writes the chapter; re-stitch; re-run auto-repair-images.py; re-run gates. Cost log: `bash scripts/log-call.sh repair sonnet <issue_id> <chapter_id> <round> <outcome>`.

**After 3 rounds — PROCEED to Phase 10 regardless of remaining gate failures.** Do NOT escalate to the reader. The pipeline publishes the best-effort issue. The orchestrator records the remaining defects in the closing summary; the CI workflow files a tracking GitHub issue for visibility (informational, not blocking).

**Bundle-exhaustion case.** If `auto-repair-images.py` reports "bundle exhausted" (cannot substitute all defects), one of the round 1–3 repairs should re-spawn the **researcher** with an inline "find N more verified image URLs for venue X" brief, append the new candidates to the bundle, then re-run auto-repair. Only fall back to "ship with duplicates" after this researcher-extension also failed within the 3-round budget.

**Cost log:** after each repair attempt, run `bash scripts/log-call.sh repair <model> <issue_id> <chapter_id> <round_number> <outcome>`. Outcome is `gate_fail` if the gate still fails and another round is coming, `ok` if the chapter now passes, `escalated` if all 3 rounds exhausted. See § Cost Logging.

### Phase 10 — Deliver + publish (always publishes; CI is post-hoc)

**Cardinal rule (v8.13.8):** Phase 10 ALWAYS publishes. Phase 9 has already done up to 3 rounds of self-healing repair; whatever survived is what ships. The reader gets a new issue every Sunday — degraded if necessary, broken-imperfect rather than missing. Last week's issue remains accessible at `/issues/<previous-filename>.html` via `index.html`, so the live site never lacks content even if this week's has minor defects.

**Stage the final HTML** to scratch first. Filename: `signal_weekly_YYYY-MM-DD.html` for standard weeklies, `signal_<format>_YYYY-MM-DD.html` for specials (e.g. `signal_countdown_2026-06-07.html`). The scratch copy is `/tmp/signal-build/<filename>`; the durable copy lives in the repo (step 2 below).

**Update state file at `/tmp/the-signal/state/signal-state.json`** per the State Tracking section: increment `last_issue_number` (standard weekly only), update `last_issue_date`, `last_issue_format`, `section_topics_recently`, rotating `last_appeared` fields, ongoing-stories status, training-phase if a block boundary crossed, `recent_facts`, `recent_next_week_themes`. For specials: also update `last_special_date`, `last_special_format`, `consecutive_specials_count`, and append to `recent_special_formats` (then trim to last 6).

**Publish to GitHub Pages.** Repository: `stevenmcdowell89-hash/the-signal`. Live site: https://stevenmcdowell89-hash.github.io/the-signal/. The repo was already cloned in Phase 0a; do not re-clone.

1. Copy the issue HTML into `/tmp/the-signal/issues/<filename>.html`.
1a. **Mirror images + generate cover** (offline-PWA + archive thumbnail). Run `bash scripts/post-publish.sh issues/<filename>.html` from the repo root. The script (a) downloads every external image referenced by the new issue into `/assets/cached/<hash>.<ext>` and rewrites the issue HTML to reference the local copies, and (b) extracts a cover thumbnail at `/assets/covers/<slug>.jpg` for the archive page. Idempotent. Failed image downloads leave the original URL intact so the issue still works online. Add any new files under `/assets/cached/` and `/assets/covers/` to the publish push list. The PWA snippet and reading-progress tracker are already baked into `template-parts/` so no per-issue injection is needed.
2. Update `/tmp/the-signal/index.html` — two changes:

   **(a) Promote the new issue to the hero slot.** Move whatever is currently in the `.hero` section (the `<a class="hero-card">`) down into the archive grid as its own `<li>` at the top of `<ul class="grid">`, converting its markup from hero-card to card. Then replace the hero with the new issue. The hero markup is:

   ```html
   <a class="hero-card" href="issues/<filename>" data-cover-slug="<slug>">
     <div class="hero-cover"></div>
     <div class="hero-body">
       <div class="hero-format">Issue #N · Standard Weekly</div>   <!-- or "<Format>" for specials -->
       <div class="hero-title"><date range or topic></div>
       <div class="hero-summary"><5-7 short headline fragments joined by commas></div>
       <div class="hero-cta">Read this issue</div>
     </div>
   </a>
   ```

   **(b) Card markup for the demoted previous issue** (added to the top of `<ul class="grid">`):

   ```html
   <li>
     <a class="card" href="issues/<filename>" data-cover-slug="<slug>">
       <div class="card-cover"></div>
       <div class="card-body">
         <div class="card-format">Issue #N · Standard Weekly</div>  <!-- or "<Format>" for specials -->
         <div class="card-title"><date range or topic></div>
         <div class="card-summary"><1-3 sentence summary></div>
         <div class="card-date"><start date> [· Special]</div>
       </div>
     </a>
   </li>
   ```

   Slug = the issue filename without `.html`. Cover images and reading-progress all flow from `data-cover-slug` automatically — no other markup needed.
3. Confirm `/tmp/the-signal/state/signal-state.json` reflects the updates above. The state file is committed alongside the issue HTML and archive index.
4. **Push via the GitHub MCP server** (preferred — works without git auth in this environment):
   - Call `mcp__github__push_files` with `owner: "stevenmcdowell89-hash"`, `repo: "the-signal"`, `branch: "main"`, the commit `message` (see below), and `files` listing every changed path with its contents read from disk. Three files in a standard run: `issues/<filename>.html`, `index.html`, `state/signal-state.json`. Plus the cost log if it lives in the repo (`state/cost-log.jsonl`).
   - **Commit message format:** `Issue #N — <date range>: <headlines>` for standard weeklies; `<Format> — <Topic>: <date>` for specials.
   - If MCP push fails, fall back to plain `git push` from inside the cloned repo — credentials may be configured.
5. Confirm publication by stating the GitHub Pages URL for the new issue in the closing summary. Include a note if Phase 9 had remaining defects (e.g. "Note: shipped with N image substitutions after auto-repair could not fully clear the bundle. CI will track.").
6. **Do NOT wait for CI; do NOT revert on CI red.** CI (`.github/workflows/issue-validation.yml`) runs automatically and files a tracking issue if it finds defects the pipeline missed. The tracking issue is informational — the reader (audience, not engineer) is not required to act on it. The previous week's issue stays accessible via `index.html` so the site never degrades.

**Why we publish even on red:** the reader's weekly Sunday read is the product. A new issue with imperfect images is preferable to no new issue. Phase 9's 3-round budget is the defence; if 3 rounds couldn't fix it, additional rounds rarely would. Better to ship and surface the residual issue in CI than to gate the audience's reading on a defect-resolution loop.

**Why state lives in the repo.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repo is the only path that's visible from every session, and it gives you version history of every state change for free.

**The deliverable is the published GitHub Pages URL** + a record of any Phase 9 residual defects, not a perfect issue. The reader receives the URL in the closing summary.

### Note on unbreakable enforcement

The pipeline runs in a sandbox that blocks outbound HTTPS to arbitrary hosts, so all in-pipeline image-URL gates degrade to advisories. The CI workflow at `.github/workflows/issue-validation.yml` is the only **structural** gate — it runs in an unrestricted environment on the same artifact about to be published.

**For true unbreakability** (CI failure blocks merge to `main`), enable branch protection in the GitHub repo settings:

> Settings → Branches → Branch protection rules → Add rule → Branch name pattern: `main` → tick "Require status checks to pass before merging" → select the `validate` job from the `validate-issue` workflow → Save.

Without that one-time setup, the CI workflow is loud-but-advisory: it shows red ✗ on the commit and opens a tracking issue, but does not stop publish. The orchestrator (this skill, future runs) is responsible for checking CI status in Phase 10 step 6 and reverting if red.

## Cost Logging

Every subagent call in the pipeline appends one line to the cost log via `scripts/log-call.sh`. This lets us answer "what did this issue actually cost?" after the fact, without instrumenting the subagent itself.

**Where the log lives.** Default path is `/tmp/the-signal/state/cost-log.jsonl` (committed to the repo alongside `signal-state.json`). Override via the `SIGNAL_COST_LOG` environment variable if running outside the cloned repo.

**Schema** (one JSON object per line):
```json
{"ts":"2026-05-03T08:14:22Z","role":"writer","model":"sonnet","issue_id":"weekly-2026-05-03","chapter_id":"world","retry":0,"outcome":"ok"}
```

**Fields:**
- `role`: `researcher` | `planner` | `writer` | `repair`
- `model`: the actual model identifier used (`opus` / `sonnet` / `haiku` — matters when fallback chains kicked in)
- `issue_id`: slug for the issue (e.g. `weekly-2026-05-03`, `countdown-efteling`)
- `chapter_id`: chapter slug for writer/repair calls; `-` otherwise
- `retry`: 0 for first call, 1+ for subsequent attempts
- `outcome`: `ok` | `validator_fail` | `gate_fail` | `escalated`

**Where to log:** the main loop calls `bash scripts/log-call.sh <role> <model> <issue_id> <chapter_id_or_dash> <retry> <outcome>` immediately after each subagent returns. Logging is fire-and-forget — errors never block the pipeline.

**Reviewing the log:**
- All issues: `bash scripts/cost-summary.sh`
- Single issue: `bash scripts/cost-summary.sh --issue weekly-2026-05-03`
- Date floor: `bash scripts/cost-summary.sh --since 2026-05-01`

The summary breaks calls down per issue by role and model, flags retries, and surfaces validator/gate failures + escalations across the fleet. After 4–6 real issues we'll have enough data to (a) confirm whether the role-intent fallback chains are sized right, (b) see which formats trigger the most repair rounds, (c) decide if any role should drop to a cheaper model or graduate to a more expensive one.

## State Tracking

### Issue Numbering

**Standard weeklies** use sequential numbering. Issue #1 was 15-21 March 2026. Each subsequent Sunday standard weekly increments `last_issue_number` by 1.

**Specials are NOT numbered.** They are referenced by format and topic only. Examples:
- "The Countdown -- Efteling & Beekse Bergen"
- "Field Guide -- Eating at Efteling"
- "Versus -- The Lyss Method vs Ibex Training"
- "Starter Kit -- Switch 2 Co-Op Games"
- "Shortlist -- Solo Games for Switch 2"

When a special edition runs, do NOT increment `last_issue_number`. The cover, footer, masthead, and wax seal of a special should display its format name and topic, never an issue number. The standard-weekly counter is preserved across specials.

When archiving in the GitHub Pages `index.html`:
- Standard weeklies: `Issue <#N> -- Standard Weekly`
- Specials: `<Format> -- <Topic>` with `Special edition -- <date or context>` in the meta line. No issue number.

The state file at `/tmp/the-signal/state/signal-state.json` has this shape:

```json
{
  "last_issue_number": 1,
  "last_issue_date": "2026-03-29",
  "last_issue_format": "weekly",
  "last_cover_lead": "World news topic",
  "topics_covered_recently": [],
  "section_topics_recently": {
    "world_leads": [],
    "session": [],
    "pixel_byte_lead": [],
    "screen_sound_lead": []
  },
  "rotating_sections": {
    "the_shelf": { "last_appeared": null, "cadence_weeks": [2, 3] },
    "this_week_in_history": { "last_appeared": null, "cadence_weeks": [2, 3] },
    "the_listen": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_workshop": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_toolkit": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_ledger": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_long_game": { "last_appeared": null, "cadence_weeks": [4, 4] },
    "the_wallet": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_itinerary": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_local": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_brickyard": { "last_appeared": null, "cadence_weeks": [4, 6] },
    "the_saga": { "last_appeared": null, "cadence_weeks": [6, 6] },
    "the_lab": { "last_appeared": null, "cadence_weeks": [4, 4] },
    "the_channel": { "last_appeared": null, "cadence_weeks": [6, 6] }
  },
  "down_the_rabbit_hole": { "last_appeared": null, "cadence_weeks": [3, 4] },
  "last_toolkit_app": null,
  "last_session_topic": null,
  "last_directors_cut_date": null,
  "last_closer_look_date": null,
  "training_phase": {
    "current_block": "Block 1: Race Prep + Fat Loss",
    "block_dates": "April 4 - May 3",
    "next_block": "Block 2: Fat Loss + Hypertrophy (May 4 - June 30)",
    "key_event": "10k race May 3",
    "focus": "concurrent training (4 lifts + 3 runs/week), hypertrophy in deficit, race prep",
    "post_june30": "hypertrophy at maintenance/surplus"
  },
  "ongoing_stories": [
    {
      "topic": "Iran War",
      "section": "world",
      "weeks_as_lead": 4,
      "weeks_as_ongoing": 0,
      "last_status": "lead",
      "lead_history": ["2026-03-15", "2026-03-22", "2026-04-05", "2026-04-19", "2026-05-03"]
    }
  ],
  "upcoming_trips": [
    {
      "destination": "Efteling + Beekse Bergen, Netherlands",
      "start": "2026-06-30",
      "end": "2026-07-07",
      "legs": [
        { "place": "Efteling", "start": "2026-06-30", "end": "2026-07-02", "nights": 2 },
        { "place": "Beekse Bergen Safari Resort", "start": "2026-07-02", "end": "2026-07-07", "nights": 5 }
      ],
      "access_constraints": {
        "excluded_modes": ["car"],
        "allowed_modes": ["plane", "public_transport", "walking", "taxi"],
        "notes": "Travelling by plane + public transport. Anything car-dependent should not be featured (mention only in passing). Walkability and station/bus access are first-class facts in every pick."
      },
      "field_guide_due": true,
      "countdown_due": true
    }
  ],
  "last_special_date": null,
  "last_special_format": null,
  "consecutive_specials_count": 0,
  "editorial_picks_used": [],
  "recent_facts": [],
  "recent_next_week_themes": [],
  "recent_special_formats": []
}
```

**`recent_facts`** — array of short tags (max 12) for the closing colophon "A Fact". Before writing each issue, read this list and pick a fact whose topic, era, and angle don't overlap with any of the last 12. After writing, append the new tag and trim to last 12. Example tags: `"Anglo-Zanzibar war"`, `"shortest filibuster"`, `"Roman calendar reform"`.

**`recent_next_week_themes`** — array of short tags (max 4) for the closing "Next Week" line. Before writing, read this list and avoid repeating phrasing patterns. After writing, append and trim to last 4.

**`recent_special_formats`** — array of recent specials (max 6 entries) tracking which P3 rotation formats have been used. Each entry: `{ "date": "YYYY-MM-DD", "format": "versus", "topic": "Sanguli vs Clodia" }`. Used by Phase 0e to pick the next P3 format — prefer formats not in the last 6. Append after every special edition (P1, P2, or P3 trigger), then trim to last 6. P1 specials (Field Guide, Countdown, Rewind, Season Review) are recorded but don't influence P3 rotation — they're calendar-driven, not rotation-driven; P3 picks among the rotation-eligible formats (Shortlist, Starter Kit, Blueprint, Versus, Deep Dive).

**`deep_dive_schedule` and `deep_dive_backlog`** (Deep Dive as a P1 trigger). Deep Dive runs on an approximately-quarterly cadence driven by a backlog. Schema:

- `deep_dive_schedule`: `{ cadence_weeks: [min, max], next_due: "YYYY-MM-DD", last_fired: "YYYY-MM-DD"|null, skip_if_no_backlog: true, rationale: "..." }`. Phase 0b checks `next_due` against today; if the date is reached and the trigger conditions hold (backlog non-empty, no other P1, not inside a trip window), a Deep Dive fires. After firing, set `last_fired = today` and `next_due = today + cadence_weeks[0]` weeks. If conditions don't hold on a Sunday where `next_due` has passed, defer one week — do NOT advance `next_due` until a Deep Dive actually fires.
- `deep_dive_backlog`: array of topic entries. Each entry: `{ topic, scope, added, priority, expanded_scope?, expanded_scope_rationale?, needs_sharpening? }`. `topic` is short ("The rise and fall of Napoleon"). `scope` is a 2-4 sentence brief describing what the Deep Dive should cover, what interpretive frames to surface, and what visual taxonomy is mandatory for this subject. `expanded_scope: true` raises the word ceiling per the spec's flex rule. `needs_sharpening: true` marks entries that are too vague to commission and must be resolved before the trigger picks them — Phase 0b skips those and tries the next.

Manual Deep Dives ("Run a Deep Dive on [topic]") are always available and bypass the schedule. After a manual Deep Dive, update `last_fired` and `next_due` as if it had been scheduled.

**Per-trip `access_constraints` (optional).** Each `upcoming_trips` entry may include an `access_constraints` block describing how the reader will travel. Fields:
- `excluded_modes` — array of transport modes the reader explicitly will not use on this trip (e.g. `["car"]`). Picks that effectively require any of these are removed from rankings, not flagged.
- `allowed_modes` — array of transport modes the reader is using. The Field Guide and Countdown elevate access by these modes (walkability, station distance, bus routes) into Quick Stats sidebars and pick footers.
- `notes` — free-text. Anything not captured by the structured fields (e.g. "prefer to avoid trains over 90min", "will rent bikes at the resort").

When this block is present, both the Field Guide and the Countdown honour it strictly per the editorial spec rule "Access constraints — read the trip entry". Constraints are per-trip, not per-reader — set them fresh on each new trip entry. Omit the block entirely if the reader has not specified.

When generating an issue:
1. Read state file at start
2. Evaluate auto-trigger logic (Priority 1 → 2 → 3) and guardrails
3. If standard weekly: select 3-4 rotating sections based on cadence priority (most overdue first)
4. Research accordingly (full groups for weekly, topic + light news pass for specials)
5. After generation, update:
   - `last_issue_date` (always)
   - `last_issue_format` (always)
   - `last_issue_number` (ONLY increment for standard weeklies; do NOT increment for specials)
   - `last_appeared` for each rotating section that appeared (standard weekly only)
   - `section_topics_recently` (always) -- append a short tag for each section's main topic this week (e.g. `session: ["race-day pacing"]`, `world_leads: ["Pope Africa visit", "$166bn tariff reversal"]`). Keep the last 4 entries per section. Before generating, the agent MUST read these and pick a different angle for any section that's running a related topic for 2+ consecutive weeks.
   - `down_the_rabbit_hole.last_appeared` (if it appeared as a sidebar)
   - `last_special_date` and `last_special_format` (if special edition)
   - `consecutive_specials_count` (increment if special, reset to 0 if weekly)
   - `editorial_picks_used` (append topic if Priority 3 was used)
   - `recent_facts` (always) — append the closing fact's short tag, trim to last 12
   - `recent_next_week_themes` (always) — append the closing "Next Week" line's short tag, trim to last 4
   - `ongoing_stories` — update weeks_as_lead/weeks_as_ongoing counts, promote/demote/drop stories as needed, add new entries if a topic has now led for 2 consecutive weeks. **v8.18:** if a topic anchored any fixed section's Lead this issue, append the issue date to its `lead_history` array. `lead_history` is never trimmed — entries age out of the sliding window automatically when the planner computes `recent_leads` (count within last 26 weeks).
   - `training_phase` — update if the current date has crossed a block boundary (Block 1 ends May 3, Block 2 ends June 30, post-holiday starts July)

## Scheduling

This skill is invoked manually by typing `/the-signal` (or by description match — e.g. "run the signal", "generate this week's Signal"). Claude Code on the web doesn't have a built-in cron equivalent that lives inside a skill. To run it automatically every Sunday morning, wire an external scheduler — a GitHub Actions workflow on `schedule: cron: '0 8 * * SUN'` that opens a Claude Code on the web session against this repo is the recommended pattern. Each manual or scheduled run follows the full workflow above. State file read at start, updated at end. Over a month, every interest cluster gets meaningful coverage at least twice.

## Asset Map (for editing sessions, not generation runs)

When the reader asks to tweak styling or structure rather than generate an issue, go directly to the right file — don't read the whole skill.

**CSS** — split across `assets/css/` in cascade order. Edit one file, don't read the whole directory. The build script concatenates alphabetically.

| File | Contains |
|---|---|
| `00-tokens.css` | `:root` custom properties (colours, section palettes) |
| `01-base.css` | reset, progress bar, back-to-top, utility classes |
| `02-cover.css` | cover header + ambient animation + grain |
| `03-navigator.css` | nav grid, nav cards, nav icons |
| `04-layout-sections.css` | foreword, dividers, generic section, watermark, gradient overlay |
| `05-components-stats.css` | stat bar, big number, display stat |
| `06-components-editorial.css` | angle box, pull quote, DYK, sidebar, also-list/cards |
| `07-components-layout.css` | dual-col, varied columns, hero, image montage, offset image |
| `08-section-world.css` | world section |
| `09-section-touchline.css` | touchline + sparkline + league tables + results |
| `10-section-screen.css` | screen & sound + card stack + rating dots |
| `11-section-shelf.css` | the shelf |
| `12-section-session.css` | the session |
| `13-section-history.css` | this week in history |
| `14-section-rotating.css` | workshop, toolkit, ledger, long game, wallet, itinerary, listen, local, brickyard, saga, lab, channel |
| `15-components-extras.css` | timelines, compact takes, margin notes, section icons, collapsibles, read-next |
| `16-animations.css` | scroll-triggered reveal, count-up |
| `17-section-longshelf-radar-footer.css` | long shelf, on the radar, footer |
| `18-components-entries.css` | entry patterns, breather bands, also-list tiers, compare panels, sidebar-float |
| `19-phase2-typography.css` | drop-cap, section opener variants, anchor piece flagging, colophon |
| `20-responsive.css` | `@media` queries |
| `21-chrome.css` | persistent masthead, full-bleed editorial cover, wax-stamp seal |
| `22-decorative.css` | Enhancement 22 — grain overlay, chapter-chrome, folio-watermark, pull-break, marginalia (all section-aware) |
| `23-special-chrome.css` | **Special editions only** — splash, ticker masthead, kinetic cover title, format badge, arc-notch footer card. See `editorial-spec.md` § Special Editions. |
| `24-special-motion.css` | **Special editions only** — layered parallax, stagger reveal, colour-wipe transitions, live D-day badge, manifesto, bignum, broken gallery, diptych, source marquee. See `editorial-spec.md` § Special Editions. |
| `25-special-body.css` | **Special editions only, tier 4** — body-embedded components (sp-scroll-image, sp-inline-figure, sp-image-strip, sp-pullquote-huge, sp-number/-huge, sp-marginalia, sp-kicker, sp-image-quote, sp-curtain, sp-chapter-number). Lives INSIDE article sections. See `editorial-spec.md` § Imagery Budget. |
| `26-special-editorial.css` | **Special editions only, tier 5** — editorial body kit (magazine-spread structure). Ground-aware tokens, alternating-ground wrappers (sp-ground-paper / sp-ground-ink), chapter chrome strip, folio watermarks, three-column feature spread (sp-spread + sp-rail + sp-margin), brief sidebar, hero-quote card, stat dashboard (sp-dash), editorial timeline (sp-timeline), full-bleed pull-break, three-column bridger, caption-strip, signoff, eyebrow, `.sp-island` readability lock. Portrait spread uses hybrid layout at ≤980px (rail absolute, margin reparented + floated right). See `editorial-spec.md` § Editorial body kit. |
| `28-special-motion-editorial.css` | **Tier 5.5** — editorial motion layer animating the tier-5 components. Wipe-band reveal, sequenced chapter-chrome entrance, folio scroll drift, stat-dash cell stagger, timeline row stagger, hero-quote lift, brief slide-in, pull-break corner-quote reveal, bridger stagger, spread rail+margin slide-in from opposite sides, drop-cap pop, spine SVG line draw, caption-strip hairline draw, underline-draw on in-prose links, ground-seam accent hairlines, reduced-motion kill switch. Mobile safety: every `opacity:0`/`translate` initial state is gated behind `body.sp-motion-ready` — JS adds the class on init plus a 2.5s safety timer. |
| `29-signature-moments.css` | **Tier 6** — format-specific signature moments: `sp-sand-clock` (Countdown), `sp-memory-wall` (Rewind), `sp-fault-line` (Versus), `sp-form-tape` (Season Review), `sp-thread-pull` (Deep Dive), `sp-build-meter` (Blueprint), `sp-cold-start` (Starter Kit), `sp-deck-reveal` (Shortlist), `sp-pinboard` (Field Guide). Each gated by `body.is-special[data-special="<format>"]`. Plus `sp-sticky-pin` (v8.3, format-agnostic) with `--portrait`/`--quote`/`--left` variants, max one per issue. |
| `30-transitions-ambient.css` | **Tier 6** — format-agnostic chapter transitions and ambient layers. `sp-stat-curtain` (full-viewport hero stat overlay) and `sp-page-fold` (3D rotateX page-curl at paper↔ink boundaries) are special-edition-only. `sp-chapter-beads` is UNIVERSAL (v8.3) — works on standard weekly AND every special edition; auto-discovers chapters from `[data-sp-chapter]` or `.mag > section.sec` fallback. `sp-horizon` stays special-edition-only. |
| `31-chapter-gate.css` | **Tier 7 (v8.7.1) — MANDATORY per-chapter opener (sticky scroll model + seam close) + ground discipline + accent lockdown.** `.sp-chapter-gate` is a 110vh scroll track (100vh sticky hold + 10vh tail) containing a `position: sticky` full-bleed black panel that locks for ~1 screen height of scroll. Reveal thresholds: arc 0.00–0.06, numeral 0.02–0.10, title 0.06–0.14, deck 0.10–0.20 — all four layers solid by 20% of the sticky hold. v8.6 seam close: `section[data-sp-chapter]` and `.sp-pull-break-wrap` get `display: flow-root` to contain block margins. Enforces ground discipline (sp-ground-paper/ink neutralised on components nested inside [data-sp-chapter]) and accent lockdown (coral demoted to slate on paper, bone on ink). |
| `32-hype-variants.css` | **Tier 8 (v8.9.1) — OPT-IN modifiers for hype-forward chapters** (Countdown hype chapters and Field Guide's Opening + Unmissables). (A) `.sp-chapter-gate.is-hype` — compact gate variant, track 60vh / sticky 40vh, layers solid by progress 0.08, numeral one size smaller. (B) `[data-sp-chapter].is-hype` — narrowly re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, `.why-its-here`. (C) `.sp-ground-gallery` — third ground type, neutral slate #1A1E27, legal only on image-first chapters. (D) `.unmissables`/`.unmissable` — Field Guide Unmissables pattern: 6–10 full-width editorial beats, hero image + sensory prose + "Why It's Here" coral kicker + mono `<dl>` practical footer. Drop-cap forbidden on picks. Never apply any of the four to literary formats. |
| `33-countdown-destinations.css` | **Tier 9 (v8.10) — Multi-venue Countdown destination theming.** OPT-IN, additive layer activated by `body[data-special="countdown"][data-multi-venue="true"]` and per-chapter `data-venue="efteling"`/`"beekse-bergen"`. Provides per-venue grounds, per-venue accent (kicker, brief-kicker, datum-value, eyebrow, dashboard strong, pull-quote cite, spread h2 marker repainted), decorative venue glyph as ::after mask-image watermark, `.sp-venue-tag` inline pill. No `isolation: isolate`, no `> *` resets, no animation overrides. `prefers-reduced-motion` guard. Glyphs stored inline. Source SVGs at `assets/glyphs/` with `ATTRIBUTION.md`. |
| `34-readability-locks.css` | **Tier 10 (v8.10.3) — Bug-fix layer for the contrast cascade.** Re-locks each self-painting component to a fixed bg+text pair regardless of chapter ground: `.sp-marginalia` always cream-bg + ink-text; `.sp-pull-break` always dark-bg + bone-text (Tier 7's `background: initial; color: initial` reset overridden); `.sp-pullquote-huge` text colour explicit per chapter ground. Plus defence-in-depth fallbacks for non-spec markup classes (`.sp-pq-quote`, `.sp-pq-attrib`, `.sp-marg-kicker`, `<div class="sp-pullquote-huge">`). Numeric prefix `34-` ensures last-in-cascade. |
| `36-holiday-identity.css` | **Tier 11 (v8.12) — Separate visual identity for Countdown + Field Guide.** Activates on `body.is-special[data-special="countdown"]` and `body.is-special[data-special="field-guide"]`. Dormant on every other format. Replaces (not augments) the default special-edition chrome on these two formats: hides `.sp-chapter-gate`, `.mast-ticker`, `.sp-splash`, `.sp-chapter-beads`, `.sp-sticky-pin`, `.sp-page-fold`, `.sp-horizon`; disables the coral accent lockdown and ground discipline inside `[data-sp-chapter]`. Installs the full `.hol-*` vocabulary. Six type stacks: Bowlby One, Cinzel italic, Yellowtail, Caveat, Anton, Alfa Slab One. Loaded conditionally via `<!-- HOLIDAY-FONTS-OPEN -->` block in `00-head-open.html`. Compatible with tier 9 multi-venue theming. |
| `37-holiday-portrait.css` | **Tier 12 (v8.13.1) — Portrait-tablet optimisations for the Holiday Identity layer.** Targets the 721–960px viewport band (Xiaomi Pad 8 portrait sits at 854px). Re-engineers components that fail in that gap: cover collage min-height, half-opener script tag becomes inline, transit intermission forced into vertical stack, anchor badge re-anchored inside rotated container, marquee negative-margin tightened, polaroid/postcard/chalkboard centred and width-capped, don't-miss numeral gutter compressed, meanwhile + subscribe stacked, savannah silhouette band height shortened. Touch-parity layer adds `:focus-within` and `.is-active` rules mirroring every `:hover` rotate-reset. |
| `38-holiday-motion.css` | **Tier 13 (v8.13.1) — Scroll-driven motion for the Holiday Identity layer.** Pairs with the HOLIDAY MOTION CONTROLLER in `script.js`. Single utility class `.hm-rise` (with `.from-left`/`.from-right`/`.delay-1..3` variants) auto-applied by JS to every major `.hol-*` block. Behaviours: `.hm-rise` fade-up + slide-in; cover parallax via `--hm-scroll`; `.hol-wonder`/`.hol-unmissable` slide photo and card in from opposite sides (mirrored for `--reverse`); `.hol-anchor` ken-burns + badge spring-rotate; `.hol-dont-miss` slam-in with overshoot; polaroid/postcard/stamp/chalkboard drop-in; transit center-card spring-in; marquee touch-drag pause; flip-pop on countdown seconds; folio-badge palette swap on Half I → Half II crossing. Safety guard `:not(.hol-motion-ready)` keeps everything visible if JS fails. |
| `39-holiday-motion-extras.css` | **Tier 14 (v8.13.2) — Extra motion layer for Countdown + Field Guide.** Eight extras on top of tier 13: edge crossfade between Half I and Half II via `--hm-edge`; countdown count-up on first viewport entry; anchor ken-burns on scroll via `--hm-progress`; polaroid tape-twitch keyframe at `.hm-landed`; Don't Miss numerals from CSS counter() to `attr(data-num)` for JS-driven count-up; marquee burst at first entry; typewriter reveal on `.hol-cover__dek`; half-ground parallax via `--hm-half-scroll`. Single rAF loop in script.js for efficiency; one-shot `.dataset.hm*` flags prevent re-firing. All motion gated behind `prefers-reduced-motion: reduce`. |

**Template** — split across `assets/template-parts/` by issue section. Each file is the HTML skeleton for that section, read-only reference.

| File | Contains |
|---|---|
| `00-head-open.html` | doctype, head, fonts, `<!-- INJECT:CSS -->`, `<body>`, progress bar |
| `01-masthead.html` | persistent masthead bar |
| `02-wax-seal.html` | rotating wax-stamp seal |
| `03-cover.html` | full-bleed editorial cover |
| `04-navigator.html` | navigator grid (default) |
| `04-navigator-toc.html` | navigator grid — TOC-style variant (Enhancement 22F, opt-in) |
| `05-foreword.html` | foreword block |
| `06-long-shelf.html` | the long shelf |
| `07-world.html` | the world this week (plus ongoing-story tracker patterns) |
| `08-anchor-piece.html` | anchor-piece rotation patterns (every 4th issue) |
| `09-pixel-byte.html` | pixel & byte |
| `10-touchline.html` | the touchline |
| `11-breather-band.html` | breather band separator |
| `12-screen-sound.html` | screen & sound |
| `13-shelf.html` | the shelf |
| `14-session.html` | the session |
| `15-history.html` | this week in history |
| `16-on-the-radar.html` | on the radar |
| `17-colophon.html` | end-of-issue colophon |
| `18-footer.html` | footer |
| `19-closing.html` | `.mag` close, back-to-top, `<!-- INJECT:JS -->`, `</body></html>` |

**Pipeline scripts and references** (v8.11.0+):

| Path | Purpose |
|---|---|
| `references/pre-flight.md` | Every writer subagent reads this before drafting. 12 regression triggers + canonical markup snippets + self-audit checklist. The primary defence — most failures are caught upstream here. |
| `references/chapter-plan-schema.md` | JSON Schema for the planner's output. Closed vocabulary for format and chapter_type. Documents the contract between planner and writers. |
| `references/spec/` | Sliced editorial-spec.md for tight per-role context. Five flat files: `global.md`, `weekly.md`, `specials.md`, `formats.md`, `triggers.md`. Each former subdir-file is now an H2 (`## <anchor>`) inside the consolidated file. `README.md` documents reading order per role and the H2 anchor index. |
| `scripts/slice-spec.sh` | Deterministic slicer. Re-runs idempotently after editorial-spec.md edits to refresh the sliced spec. |
| `scripts/validate-chapter-plan.py` | Mandatory gate between Phase 4 and Phase 5. Catches malformed plans, missing fields, broken cross-refs. |
| `scripts/stitch-issue.sh` | Deterministic chapter concatenation + scaffold wrap + CSS/JS inject. Replaces inject-assets.sh in the pipeline. |
| `scripts/inject-assets.sh` | Legacy single-file CSS/JS injector. Kept for ad-hoc edits outside the pipeline. |
| `scripts/check-release-dates.sh` | Phase 7.5 release-date sanity check. Surfaces every claim of a date/relative-time near a media name in the stitched HTML, plus any locked-register entry. Output written to `/tmp/signal-date-claims.txt`. The agent walks the report and verifies each claim against the locked register or a web search before publish. |
| `scripts/validate-issue.py` | **Phase 7.6 mandatory post-stitch gate.** Verifies structural well-formedness, banned-placeholder absence, holiday activation (body class + `data-special` + `.hol-masthead`/`.hol-cover`/`.hol-half` presence), and image-URL reachability (HEAD requests in parallel). Exits non-zero on any failure. The orchestrator runs this directly and reads the exit code — subagent self-reports of "passed" are not acceptable. See Phase 7.6 in the workflow above. |
| `scripts/validate-research-bundle.py` | **Phase 3b mandatory upstream gate.** Reads `research-bundle.json` and enforces image_candidates rules: real URLs not keywords, ≥3 source types represented, Wikimedia ≤30%/≤4, RT-5 single-domain ≤50%, ambiguous-domain `source_type` annotation. Blocks the planner from spawning until research is corrected — the strongest prevention against the URL-fabrication / mono-sourcing chain. Uses `references/image-source-types.json`. |
| `scripts/check-image-diversity.sh` | **Phase 7.7 mandatory post-stitch gate.** Classifies every image domain in the stitched HTML via the lookup table and enforces the same diversity rules as Phase 3b. Defence in depth — catches writers omitting bundle images and skewing the final ratio, or new domains slipping in. Sandbox-aware: unknown domains warn rather than fail. |
| `references/image-source-types.json` | Lookup table mapping domain → source type (press_kit / government / archive / news_cdn / wikimedia) plus the threshold values. Edit when a new recurring source appears in research. Both Phase 3b and 7.7 gates read this file. |
| `scripts/log-call.sh` | Fire-and-forget logger — main loop calls this after each subagent returns. Appends one JSON line to the cost log (default `/tmp/the-signal/state/cost-log.jsonl`, override via `SIGNAL_COST_LOG`). Errors are silent so logging never blocks the pipeline. |
| `scripts/auto-repair-images.py` | **Phase 9 round-0 programmatic repair.** Takes stitched HTML + research-bundle.json, identifies image defects (duplicates D6, unbundled D7, page-URL-as-image D3) and substitutes unused bundle URLs in-place. Pure Python — no subagent dependency. Exits 0 on clean / fully-repaired, 1 on partial (bundle exhausted). The orchestrator's Phase 9 loop absorbs partial failures via the 3-round budget; after 3, Phase 10 ships anyway. |
| `scripts/cost-summary.sh` | Reads the cost log and prints a per-issue and aggregate breakdown (calls per role, model usage, retry rate, validator/gate failures, escalations). Run after a few issues to validate the model fallback chains. |

**Rules for CSS edits:**
- Never reorder or rename files — alphabetical order is the cascade.
- A new component fits into an existing file if the category matches; otherwise add a new file with a numeric prefix that slots it in the right cascade position.
- After any CSS edit, you can verify the build still works by running `bash scripts/inject-assets.sh` on a dummy HTML file with the two placeholder comments.

**`assets/script.js`** — single file, four logical regions:
1. **Universal base controllers** (lines 1–~445): progress bar, back-to-top, count-up, reveal observer, wax-stamp chapter numeral tracker, chapter beads (v8.3, every issue, auto-discovers chapters), sticky pin (v8.3, scroll progress driver, max-one-per-issue enforcer), chapter gate (v8.5, auto-builds from `data-chapter-num`/`-title`/`-arc`, rAF scroll-progress loop, IntersectionObserver-gated, reduced-motion + 2.5s safety backstop). Run on every issue.
2. **Special-edition motion controller** (~line 375+): parallax, stagger words, colour-wipes, D-day live countdown, sp-stat-curtain, sp-page-fold, sp-horizon piggyback, per-format signature moments. IIFE-wrapped, short-circuits unless `body.is-special` and `prefers-reduced-motion` is not set.
3. **Holiday Identity countdown controller** (v8.12, end of file): live tick on `.hol-countdown` cells (`[data-cd="days|hours|mins|secs"]`) driven by ISO `data-target` on the wrapper. Runs only on `body.is-special` AND `data-special` ∈ `{countdown, field-guide}`.
4. **Holiday Motion controller + Motion Extras controller** (v8.13.1 / v8.13.2, end of file): scroll-driven motion paired with `38-/39-holiday-motion*.css`. Tags every major `.hol-*` block with `.hm-rise`, opts in stagger delays, releases CSS safety guard via `body.hol-motion-ready`, installs IntersectionObserver reveal + rAF parallax + touch-tap unrotate + marquee touch-drag pause + folio-badge palette swap, plus eight extras (edge crossfade, count-up, ken-burns, tape-twitch, Don't Miss count-up, marquee burst, typewriter, half-ground parallax). 2.4s safety backstop force-sets `.is-in` on every `.hm-rise` if observers fail. Reduced-motion safe.
