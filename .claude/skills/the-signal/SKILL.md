---
name: the-signal
description: >-
  Generate issues of The Signal, a weekly personal magazine designed to be
  read on a Sunday morning with coffee. Use when asked to run, generate,
  create, or schedule The Signal, or when the user mentions "the signal",
  "signal magazine", "sunday magazine", "personal magazine", "run the
  signal", "deep dive", "countdown", "season review", "versus", "rewind",
  "starter kit", "shortlist", "next", "after", "lookahead", or "field
  guide" in the context of their personal weekly reading. Supports
  multiple issue formats: standard weekly, deep dive, countdown, season
  review, versus, rewind, starter kit, shortlist, next, lookahead, and
  field guide. Includes HTML template, editorial spec, and a compliance
  checklist.
---

# The Signal

Generate issues of The Signal — a weekly personal magazine for Sunday morning reading.

Version 8.35.0. See `CHANGELOG.md` next to this file for the full version-by-version history of editorial and visual changes. Editorial substance is defined in `references/editorial-spec.md` and its sliced views in `references/spec/`. This file describes only **how the pipeline runs on Claude Code**. **v8.35 — Voice & the person (weekly W-1):** the weekly's author-less **Foreword becomes The Letter** — a named Editor speaking in the first person, stating the week's thesis and connecting the dots across domains (same `foreword` slot/`.foreword` markup, renamed and re-voiced). **Gate 1A is split:** the *reader* stays invisible (no "you"/"your son"/profile callbacks) but the *Editor's* first-person voice is explicitly permitted — 1A is now "no second-person reader address", not "no first person". The mandatory per-section aphorism/closer tic is **killed structurally** (no new gate): sections need not "land on a line", at most one genuine aphorism is allowed per issue, and the Angle box may never be reprinted as a pull-quote. **Two checklist checks retired** — the per-section closer/aphorism expectation and the entry-pattern-rotation rule (entry patterns are now a palette, not a forced rota). "Daily carried the facts, here's the layer" is documented as the standard opener for any live-news section, with the machinery kept invisible in prose. No script gate added or removed; the changes are spec + checklist + the weekly foreword template. **v8.34 — weekly refocus (scope + spine):** with the daily brief now reliably owning week-in-the-loop catch-up, the weekly is reframed to add the layer time gives — synthesis across the week and roundups combining piecemeal items — for a reader who arrives already informed. Three edits, all by adjusting existing principles/gates (no new rule, no new script): Identity names the daily/weekly division; the section spine is **inverted** so the mandatory element of a fixed section is the **considered piece** (synthesis / a named-layer roundup / an angle / a feature) with the Catch-Up dropping to optional grounding (a catch-up-only section now yields — `validate-chapter-plan.py`'s `check_section_shape` was adjusted to require the considered-piece backbone, not the catch-up spine); and the two-factor Lead test keeps factor 1 (did it move) but moves factor 2's reference point from "beat the BBC headline" to "what the informed reader already absorbed from the daily — does this add the week's arc, or the combined picture?" The craft/research/quality/compliance machinery is unchanged. **v8.33 — back link enforced:** the fixed top-left "Return to The Signal" archive button is now a hard ship requirement. It was injected by the stitcher since v8.22.15 but never verified, so issues built off the happy path silently lost it; `validate-issue.py` now has a universal `back-link` gate (marker + `.signal-back-to-archive` anchor → `../`) and the stitcher fails loudly if its own injection doesn't land. **v8.30 — deliver, don't gesture:** the Phase 7 plain-English read now runs on **every format** (was Deep-Dive-only), and its trope list names two weekly failures — the **hollow connective sentence** ("that framing is what makes this a discovery") and the **hedged answer** (a "how many?" lead that has the numbers but dissolves the takeaway into "somewhere in the region of…"). The answer-the-question rule now says *land* the answer; caveats go in an aside. And **Release Radar is reinstated as a first-class, enforced weekly chapter** — `validate-chapter-plan.py` hard-fails a weekly that drops it or ships fewer than 15 upcoming releases across 4+ media categories (it silently vanished from the 1 June test because nothing enforced it). No new gate script; the existing validator and reading-pass were extended. **v8.29 — fact provenance moved upstream:** load-bearing facts are now **structured `facts` records** carrying `status` (`happened`/`upcoming`), `date`, and `source_url` (plus `speaker`+`quote` for opinions). The researcher decides happened-vs-upcoming *while the sources are open*; the writer renders the pre-decided tag instead of judging it mid-prose. The bundle gate (`validate-research-bundle.py --run-date`) rejects a `happened` fact dated in the future and an `opinion` fact with no quote; the release-date gate (`check-release-dates.sh`) now anchors on the **run date**, not the issue's cover date, closing the State-of-Play / "Norris on pole" temporal hole. No new gate script — the two existing gates were extended (per the no-accretion meta-rule). **v8.28 — substance & trust:** the Lead is now *optional* (a section can be pure facts), length follows the material (no padding to a floor), the magazine **borrows angles from real sources and never invents its own** (new Cardinal rule), facts must trace to the research bundle and a stated result must have *happened* by the issue date, and the **researcher spawns as a writable `general-purpose` agent** (the read-only `Explore` agent couldn't write the bundle, starving issues of facts). **v8.27 (prior) is the editorial reset** — two-factor Lead, Lead + Catch-Up shape, one-home-per-domain roster (fixed: World · Pixel & Byte · Toolkit · Touchline · Screen & Sound · Session; rotating: Shelf · History · Listening · Money · Places; Saga trigger-driven), UK politics out-by-default, 2-3 rotating slots. Pipeline phases unchanged.

## STEP ZERO — verify orchestrator model BEFORE ANYTHING ELSE

**The orchestrator MUST run on an Opus 1M-context model at or above the 4.7 floor — currently `claude-opus-4-7[1m]` or `claude-opus-4-8[1m]` (4.8 preferred).** No smaller model can complete the pipeline end-to-end without context overflow during Phase 5 writer fan-out. The gate is a **floor, not a pin**: it blocks a *downgrade* (the 24 May 2026 weekly failed because the Claude Code on the Web harness silently fell back to Opus 4.6 and compaction fired mid-pipeline), but a newer/stronger Opus 1M passes. When Anthropic ships a newer Opus 1M, append it to the `ALLOWED` array in `verify-orchestrator-model.sh` — never remove the floor.

**Before doing literally anything else — no state read, no tool research, no chat reply about the task** — the orchestrator MUST perform these three steps in order:

1. **State the model in the first user-visible message.** The orchestrator's first output text must start with the literal line:

   > **Orchestrator model: `<exact-model-id-from-system-prompt>`**

   Where `<exact-model-id-from-system-prompt>` is the value verbatim from the orchestrator's system prompt under "Environment" → "The exact model ID is …". This visible handshake lets the reader sanity-check at a glance before any work begins.

2. **Run the verify-model script as the first tool call.** Pass the same model identifier:

   ```bash
   bash .claude/skills/the-signal/scripts/verify-orchestrator-model.sh "<exact-model-id-from-system-prompt>"
   ```

   The script exits 0 if the model is at or above the floor (`claude-opus-4-7[1m]` or `claude-opus-4-8[1m]`), exits 1 otherwise with an error message. **Exit code is the gate** — same rule as every other script gate in this workflow (see "Gate discipline" below).

3. **On non-zero exit, abort.** Reply with the verbatim message:

   > The Signal pipeline requires the orchestrator to run on Opus 1M context at or above the 4.7 floor (`claude-opus-4-7[1m]` or `claude-opus-4-8[1m]`). This session is on `<observed-model-id>`, which cannot reliably hold the full pipeline state through Phase 5. Re-trigger the routine with the correct model — the schedule preference may not have been honoured by the harness this run. Aborting before Phase 0.

   Do not proceed even if the reader says "do it anyway" — the reader has pre-authorised the refusal by including this rule in the spec.

This is the ONLY check that comes before Phase 0a (state read). Once the script exits green, log "Orchestrator model verified" and proceed to "Model Selection" below for subagent dispatch rules, then to Phase 0.

**Why honor-system can't be avoided here.** Model selection happens at the Claude Code harness layer, which the skill can't override. The skill's job is to prevent a wrong-model run from damaging the live site — refusing at Step Zero is the strongest stop-the-bleeding measure available. The actual fix for harness-ignored model preferences is at the Claude Code on the Web routine layer, not in this repo.

## Model Selection

The Signal runs as a multi-subagent pipeline. Each role has different reasoning needs, so models are selected by **role intent** with **fallback chains** — never by hard-coded model name. When Claude releases a stronger or cheaper model, advance the chain.

| Role | Primary | Fallback | Why this intent |
|---|---|---|---|
| **Orchestrator** | Opus 4.8 1M | — | See Step Zero above. No fallback. Holds full pipeline state through Phase 5 AND makes the Phase 7 plain-English prose judgment. |
| **Researcher** | Opus 4.8 | Sonnet 4.6 | Web search + synthesis. URL verification is mechanical, but fact selection, framing, and image-candidate quality are judgment — a weaker model could quietly hand writers a thinner bundle and no gate would notice. |
| **Planner** | Opus 4.8 | Sonnet 4.6 | Structured reasoning, JSON output, hard constraints. The role where premium reasoning was always acknowledged to matter most. |
| **Writer** (any format) | Opus 4.8 | Sonnet 4.6 | The writer's model choice is, by definition, the single largest influence on the prose — and the prose is the product. |
| **Repair** | Opus 4.8 | Sonnet 4.6 | Fires only when something subtle slipped *every* gate — exactly the moment you want maximum capability, not a cheaper model. |

**Rationale (v8.23 — burden of proof inverted).** Earlier versions assigned cheaper models (Sonnet/Haiku) to the researcher, writer, and repair roles to limit cost under a cost-throttled orchestrator, on the asserted basis that *"Sonnet performs at the same quality as Opus once the planner has done the hard thinking."* **That assertion was never tested.** The pipeline has no quality signal — only compliance gates (markup, image diversity, release dates, banned vocab, the plain-English check). A clean gate record cannot distinguish "as good as Opus" from "quietly worse in ways no gate measures"; the cost log's zero-retry history proves compliance, not quality. With orchestrator cost no longer the binding constraint, the policy is now inverted: **a role stays on a cheaper model ONLY if its work is mechanical enough that model strength provably cannot affect the output.** No LLM role clears that bar — the genuinely mechanical work (stitching, validation, image substitution) is already done by deterministic scripts with no model at all. Every subagent role does generation or judgment a stronger model could do better, undetectably. So every primary is Opus 4.8; cheaper models survive only as availability/rate-limit fallbacks, never as the default. Re-run this analysis (don't just inherit it) when the next Opus ships.

**Spawning.** Use the `Agent` tool with `subagent_type` and the optional `model` parameter:
- Researcher → `subagent_type: "general-purpose"` (web research that **writes the bundle file**), `model: "opus"` (fallback `"sonnet"`). **NOT `Explore`** — Explore is read-only in some harnesses and cannot write `research-bundle.json`; using it strands the research and forces a lossy hand-rebuild (the v8.28 failure). The researcher must be a writable agent.
- Planner → `subagent_type: "general-purpose"`, `model: "opus"` (fallback `"sonnet"`).
- Writer → `subagent_type: "general-purpose"`, `model: "opus"` (fallback `"sonnet"`).
- Repair → `subagent_type: "general-purpose"`, `model: "opus"` (fallback `"sonnet"`).

**Override.** If the reader explicitly says "use the top model" or "lean cheaper", honour the override across the **subagent** chain. The orchestrator-level requirement at Step Zero is not overridable — it exists to prevent the May 24 failure mode, where the orchestrator itself ran on a model too small to hold pipeline state.

## Workflow

The Signal runs ONE pipeline for every issue — standard weekly or special edition. The format is decided in Phase 0; Phases 3–10 then run for every format. The format only changes WHICH chapters get written and HOW writers are sequenced (parallel vs sequential), not WHICH phases run.

The pipeline: Phase 0 (decide format) → Phase 3 (researcher subagent) → **Phase 3a-verify (orchestrator WebFetch every URL — v8.13.8)** → Phase 3b (research-bundle validator) → Phase 4 (planner subagent + validator) → Phase 5 (writer subagents, parallel or sequential) → Phase 6 (stitch) → Phase 7 (per-chapter Gate 1) → Phase 7.5 (release-date check) → **Phase 7.6 (structural + asset validator — `validate-issue.py`)** → Phase 7.7 (image-source diversity — `check-image-diversity.sh`) → **Phase 7.8 (DOM visual smoke test — `visual-smoke-test.py`)** → Phase 8 (stitched-issue Gate) → Phase 9 (repair if needed) → **Phase 9.5 (editorial-quality scoring — observational, logs the quality signal)** → Phase 10 (deliver + publish + CI verification).

There is NO separate "lightweight" path. Standard weeklies run the full pipeline same as specials. Build dir is `/tmp/signal-build/`, cleared at the start of every run.

> **Environment note.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repository at `stevenmcdowell89-hash/the-signal` is the only durable store — state, issues, and the cost log all live there. Per-session paths like `/tmp/signal-build/` are scratch only.

> **Gate discipline (MANDATORY).** Every script-backed gate in this workflow — `verify-orchestrator-model.sh` (Step Zero), `validate-chapter-plan.py`, `validate-research-bundle.py`, `stitch-issue.sh` (which embeds the holiday-activation rewrite + banned-vocabulary scan + holiday scaffold override + holiday half-wrap reorganisation), `check-release-dates.sh`, `validate-issue.py`, `check-image-diversity.sh`, and `visual-smoke-test.py` — is **run by the orchestrator itself**, not delegated to a subagent. The gate's verdict is its **exit code**, full stop. A subagent claiming "gate X passed" is not acceptable evidence — the orchestrator must invoke the script via `bash` or `python3`, read the printed report, and read the exit code before advancing. If a subagent reports success but the orchestrator did not run the gate, the orchestrator runs it now. This rule exists because subagents have been observed reporting "gate passed" for gates they never invoked.

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
- Pick the next format from the P3 rotation (Shortlist, Starter Kit, Versus, Deep Dive on a non-trip topic). Read `recent_special_formats` from state — pick the format that has not appeared in the last 6 specials. If multiple formats tie, pick the one with the strongest topic surfaced during 0d. **Next and Lookahead are manual-only** and never enter P3 — they require reader-supplied context (the thing just finished / the window to survey) that the orchestrator cannot infer.
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
- **Parallel mode** (Countdown, Field Guide, Shortlist, Starter Kit, Lookahead, weekly): writer subagents in Phase 5 spawn in one batch.
- **Sequential mode** (Deep Dive, Versus, Rewind, Season Review, Next): writer subagents in Phase 5 spawn one at a time, each reading its predecessor's output to maintain throughline. Next is sequential because every pick has to be judged against The Itch named in the opening chapter, and the On-Ramp for each pick benefits from knowing what the previous pick covered.

### Phase 3a — Researcher subagent
Spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). **Do NOT use `Explore`** — it is read-only in some harnesses and cannot write the bundle file; the researcher MUST be able to write `/tmp/signal-build/research-bundle.json` itself. In the prompt, tell it to read `references/spec/global.md` (sections `key-rules` and `image-integrity`), `references/spec/triggers.md` (full file — short), and the matching format section in `references/spec/formats.md` (H2 anchor for the issue's format). Pass committed format + state snapshot inline. The subagent does all web research and writes `/tmp/signal-build/research-bundle.json`.

**The bundle carries FACTS, not beat-labels (v8.28).** Substance in the issue is bounded by substance in the bundle — a thin bundle guarantees a fluffy issue. So the researcher must gather, for every section it touches: **specific facts** (named people, dated events, numbers, actual results that have already happened) AND, where an angle is wanted, the **real viewpoints commentators actually hold** (so the writer can voice a *borrowed* angle, never an invented one — see editorial-spec § "Borrowed angles, our voice"). Concretely: a catch-up item is "Juventus sign [name] from [club] for [fee] (3 June)", never "Juventus transfer latest"; a recommendation is a real, named, linked title, never a placeholder ("researcher to confirm"). If a beat has no real specific, drop it — do not hand the writer a label to dress up. Each load-bearing fact carries its source URL (the same discipline as image candidates). For The Saga, read state `currently_reading`/`currently_watching` as peg sources. **Release Radar (mandatory weekly, v8.30):** the researcher must also gather the upcoming-releases set — **15-20 dated releases across ≥4 of {film, tv, game, lego, tech, book, music}**, each with a date, a `status` (`upcoming`-weighted), and a link — so the planner can fill the required `release_radar` chapter. A weekly with a thin/absent Release Radar set is incomplete (the validator will reject the plan). Bundle fields: sources, **structured `facts` (see below)**, image candidates with attribution, per-section lead-candidates + catch-up items (each with a specific fact + why + link), **`release_radar` items**, ongoing-story status, training-phase context.

**MANDATORY (v8.29) — the `facts` array is a structured provenance record, not loose strings.** The researcher decides *while the sources are open* whether each load-bearing claim has **happened** or is **upcoming**, and records that decision as a machine-checkable field — moving the "has this happened / who said it?" judgment upstream, out of the writer's prose (where it has repeatedly leaked: the State-of-Play showcase written as "delivered" before it aired; the Monaco "Norris on pole" asserted before qualifying). Every load-bearing fact is an object in `bundle.facts`:
```json
{
  "claim": "PlayStation State of Play airs, incl. FF7 Rebirth reveals",
  "status": "upcoming",                 // "happened" | "upcoming" — decided NOW, against today (the run date)
  "date": "2026-06-05",                 // ISO date of the event/claim
  "source_url": "https://blog.playstation.com/…",
  "type": "fact",                       // "fact" (default) | "opinion"
  "speaker": "Lando Norris",            // REQUIRED iff type=="opinion"
  "quote": "the car felt alive today"   // REQUIRED iff type=="opinion" — the real words
}
```
Rules the Phase 3b gate enforces (`validate-research-bundle.py --run-date <today>`): `claim`/`status`/`date`/`source_url` present; **a `status:"happened"` fact dated after the run date is rejected** (it can't have happened yet — tag it `upcoming` or drop it); a `type:"opinion"` fact must carry a real `speaker` **and** `quote` (you can only *name* a person, or hang a borrowed angle on them, when the real words are in the bundle — otherwise the angle is voiced unattributed in our own voice; see editorial-spec § "Borrowed angles, our voice"). The planner copies the relevant fact records into each chapter's `key_facts`, so the writer renders a pre-decided tag rather than judging it mid-sentence.

**MANDATORY (v8.13.7) — Researcher MUST verify every image URL with WebFetch.** For each candidate, run WebFetch on the URL. Accept it ONLY if the response is 2xx and `Content-Type` starts with `image/`. Record the result inline on the candidate as:
```json
"verified": { "head_status": 200, "content_type": "image/jpeg", "verified_at": "<ISO timestamp>" }
```
If the URL is a brand-site PAGE (returns `text/html`), open it with WebFetch and find the real `<img src>` CDN URL in the markup — use THAT URL, not the page URL. If you cannot find a working URL for a subject, DROP the candidate from the bundle. Do not ship `"verify later"` notes. The bundle must surface at least 16 distinct verified URLs (per `thresholds.min_unique_candidates`) so writers don't recycle. **Per-pick image coverage (v8.32):** for recommendation formats (Starter Kit Essentials, Shortlist, Next), surface **at least one real image per recommended title** — actively search the official/press/show site, TMDB, and Wikimedia for *each named pick*, not just the ones that surface easily — so no pick ships imageless (the audio-drama Starter Kit floor: every pick had an image). In an egress-restricted run the URL is recorded `blocked` for CI to re-verify, but a real direct image URL must still be found for every pick.

Common fabrication traps to avoid:
- Wikimedia `/wiki/commons/thumb/<hash>/<hash>/<file>.jpg/1280px-<file>.jpg` — only exists if a thumbnail at that exact size was pre-generated. Use the canonical `/wiki/commons/<hash>/<hash>/<file>.jpg` or `Special:FilePath/<file>?width=N` instead.
- Made-up filenames (e.g. `Efteling_-_Polles_Keuken_(2).jpg` when the real file is `Polles_Keuken_Efteling_2.JPG`). Confirm exact spelling via `site:commons.wikimedia.org "File:..."`.
- Brand-site page slugs (e.g. `https://www.efteling.com/en/park/restaurants/polles-keuken`) — those are HTML pages, not images. The validator rejects them with no extension AND no image content-type.

**Cost log:** after the researcher returns, run `bash scripts/log-call.sh researcher <model> <issue_id> - 0 ok` (one call). See § Cost Logging.

### Phase 3a-guard — bundle-exists check (MANDATORY, v8.28)

Before anything else after the researcher returns, the orchestrator verifies `/tmp/signal-build/research-bundle.json` **exists and is non-empty** (`test -s` / parses as JSON with populated section arrays). If it is missing or empty — the read-only-`Explore` failure mode — the orchestrator does **NOT** reconstruct the bundle from the agent's chat summary (that hand-rebuild is lossy and is what produced the fluffy v8.28 test issue). It re-spawns the researcher as a **writable `general-purpose`** agent, or, only if the agent's reply contains the complete bundle JSON verbatim, writes that JSON to the file unchanged. A summary is not a bundle.

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
Run `python3 scripts/validate-research-bundle.py /tmp/signal-build/research-bundle.json --run-date <today>` (pass today's date — the date the pipeline is actually running — so the facts temporal gate anchors correctly). The script enforces the `image_candidates` rules from `references/spec/global.md` image-integrity:

- Every `url_or_keyword` must be an `http(s)://` URL (keywords are rejected — they force writers to invent URLs, the RT-16 trap).
- ≥3 of the 5 source types represented (press_kit / government / archive / news_cdn / wikimedia — see `references/image-source-types.json`).
- Wikimedia ≤4 entries AND ≤30% of total (whichever is smaller). Any single domain >50% is RT-5 hard fail.
- Ambiguous domains like `live.staticflickr.com` require an explicit `source_type` field on the candidate.

It **also** enforces the `facts` provenance rules (v8.29 — see Phase 3a and `references/spec/global.md` § fact-provenance): each fact carries `claim`/`status`/`date`/`source_url`; a `status:"happened"` fact dated after `--run-date` is rejected (it can't have happened yet); a `type:"opinion"` fact must carry a real `speaker` + `quote`. An absent/empty `facts` array warns (acceptable for a fact-thin issue) but a malformed entry hard-fails.

**Non-zero exit code = research is not shippable to writers.** Re-spawn the researcher with the failure report inlined into the prompt. The researcher uses WebSearch / WebFetch to find verified URLs from the under-represented source types and rewrites `image_candidates`. Re-validate. Max 2 retries before escalating to the reader. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

This gate exists because the 17 May test issue shipped with 14 fabricated image URLs (writers constructed URLs because the bundle gave them keywords like "Wikimedia Commons: Keir Starmer"). Catching the broken bundle upstream costs one extra script run; catching the fabrications downstream costs a full writer re-run plus image substitution work.

### Phase 4 — Planner subagent + validator gate
Spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). Pass the path to `research-bundle.json`. In the prompt, tell it to read `references/chapter-plan-schema.md`, `references/pre-flight.md`, and the planner's spec slice: `references/spec/global.md` sections `identity`, `key-rules`, `markup-contracts`, `accent-lockdown`, `stat-budget`; plus the format's H2 anchor in `references/spec/formats.md`; plus `references/spec/specials.md` section `overview` if special edition. The subagent writes `/tmp/signal-build/chapter-plan.json`. **For weeklies (v8.30): the plan MUST include a `release_radar` chapter** (rendered after `screen_sound`) with a `radar_items` array of 15-20 entries across ≥4 categories — `validate-chapter-plan.py` hard-fails a weekly that omits it. The planner pulls these from the bundle's `release_radar` items; the writer (Phase 5) renders the chapter using the `.radar-cat` category-dot markup.

Run `python scripts/validate-chapter-plan.py`. **If invalid:** re-spawn planner with the validator's error report (max 2 retries). After 2 retries, advance the planner fallback chain (Opus → Sonnet) and try once at the next tier.

**Cost log:** after each planner attempt, run `bash scripts/log-call.sh planner <model> <issue_id> - <retry_count> <outcome>`. Outcome is `validator_fail` if validator rejected and another retry is coming, `ok` if the plan passed, `escalated` if the fallback chain ran out. See § Cost Logging.

### Phase 5 — Writer subagents (format-aware)
Read `chapter-plan.json`. For each chapter, spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). In the prompt, pass: the pre-flight.md path, the chapter brief (one chapter object from the plan), the research-bundle.json path, plus the H2 anchor reference for the issue's format inside `references/spec/formats.md`. Writers also read `references/spec/global.md` sections `markup-contracts`, `ground-discipline`, `accent-lockdown`.

**WEEKLY FORMAT (`weekly`):** writers MUST read `references/component-contracts.md` § Weekly and `references/sections.md`. Weekly sections use the section-component vocabulary: `.split-60-40` / `.split-40-60`, `.sidebar` / `.sidebar-float` / `.sidebar-title`, `.stat-bar` / `.entry-stat`, `.dyk` / `.dyk-title`, `.also-list` / `.also-cards` / `.also-card`, `.pull-quote`, `.compare-panel`, `.timeline` / `.timeline-node`, `.entry-bullets`, `.entry-quote`, `.entry-question`. The special-edition `.sp-*` vocabulary (`.sp-spread`, `.sp-marginalia`, `.sp-rail`, `.sp-margin`, `.sp-pullquote-huge`, `.sp-brief`, `.sp-brief-kicker`, `.sp-spread-body`, `.sp-dash`, `.sp-chapter-gate`, `.sp-chapter-chrome`, `.sp-pull-break`, `.sp-manifesto`, `.sp-bignum`, `.sp-gallery`, `.sp-diptych`) is **forbidden in weekly issues** — those classes are scoped to `body.is-special` selectors and render unstyled on a standard weekly. **The stitcher gate enforces this — any weekly chapter containing those tokens fails the stitch.** Writers reaching for specials.md by mistake is the bug that broke the 24 May 2026 weekly.

**NON-HOLIDAY SPECIAL FORMATS (`deep_dive`, `versus`, `rewind`, `season_review`, `starter_kit`, `shortlist`, `next`, `lookahead`):** writers MUST read `references/spec/specials.md` § `cover` → "Component list" for the v8.21 editorial system: persistent `.mast` chrome, `.cover` / `.chapter` / `.chapter-body` structure, baseline flair (`.pullquote`, `.marginalia`, `.bignum`, `.sp-ornament`, `.sp-eyebrow`, `.has-dropcap`), figures (`.fig`, `.image-quote`), per-format flair components for the visual formats (`.vs-tape` / `.vs-pair` / `.vs-verdict`, `.year-band` / `.rewind-cards`, `.rating` / `.scoreboard` / `.milestones`, `.tier-band` / `.pick`). The old `sp-*` vocabulary (`.sp-chapter-gate`, `.sp-spread`, `.sp-pull-break`, `.sp-manifesto`, `.sp-bignum`, `.sp-gallery`, `.sp-diptych`, `.sp-marquee`, `.sp-parallax`, `.sp-wipe`, `.sp-stagger`, `.sp-splash`, `.mast-ticker`, `.sp-format-badge`, signature-moments `.sp-sig-*`, hype `.is-hype`) was retired in v8.21 — those classes are no longer in the CSS bundle and will render unstyled. **HOLIDAY FORMATS ONLY (`countdown`, `field_guide`):** writers read `references/spec/specials.md` § `holiday-identity` for the `.hol-*` component map. Holiday formats retain their motion/identity layer in CSS files `33-` and `36-` through `44-`. Each writer outputs `/tmp/signal-build/chapters/<chapter_id>.html` (chapter-only, no scaffold).

**Cover, navigator, foreword, colophon, footer chapters are FULL writer-agent chapters — not orchestrator-written.** Every chapter in the plan, including the front-matter and back-matter, gets a spawned writer Agent with pre-flight + brief + research bundle. The orchestrator does NOT write chapter content inline by hand. If a chapter is templated (scaffold-derived) it goes in `scaffold_parts_used` and the stitcher concatenates it directly; if it's authored content it goes through Phase 5. Don't mix. The 24 May 2026 weekly shipped with orchestrator-written cover/navigator/foreword/colophon/footer because the planner initially listed them as scaffold parts and the orchestrator then wrote them directly — neither path applied pre-flight or compliance gates. Either fully scaffold (template-only with no per-issue prose) or fully writer-agent (with the full Phase 5 → Phase 7 chain).

- **Parallel mode** (Countdown, Field Guide, Shortlist, Starter Kit, Lookahead, weekly): spawn all writers in one batch — issue every `Agent` call in a single message.
- **Sequential mode** (Deep Dive, Versus, Rewind, Season Review, Next): spawn writers one at a time. After each chapter completes, the next writer reads its predecessor's output to maintain throughline.

**Cost log:** after each writer returns, run `bash scripts/log-call.sh writer <model> <issue_id> <chapter_id> 0 ok`. One call per chapter. See § Cost Logging.

### Phase 6 — Stitch
Run `bash scripts/stitch-issue.sh --plan /tmp/signal-build/chapter-plan.json --out signal_<format>_<date>.html --issue-number <N>`. Stitcher concatenates chapters, wraps in scaffold, injects CSS (alphabetical cascade) and JS deterministically. The `--issue-number` arg is required for standard weeklies (it's substituted into the footer `Issue #[N]` placeholder) and should be the value `last_issue_number + 1` from state. For specials, pass `--issue-number ""` (empty) or omit — specials don't carry issue numbers and the footer uses the format/topic header instead. **v8.18.1:** the stitcher now also substitutes `[DATE RANGE]` (computed as a one-week range ending on the issue date for weeklies, or the single date for specials) and `[Date]` (pretty-formatted issue date) placeholders from the head-open and footer templates. Writers don't touch these; the stitcher owns them. **v8.13.3:** for `countdown` and `field_guide` formats, stitch-issue.sh auto-rewrites the `<body>` tag to `<body class="is-special" data-special="<format>">` (the activation that switches on tier 11/12/13/14 CSS + JS), runs a banned-vocabulary grep gate (`sp-chapter-gate`/`sp-spread`/`sp-pull-break`/`sp-marginalia`/`sp-brief`/`sp-dash`/`sp-chapter-chrome`/`unmissables`/`unmissable`) and exits non-zero if any are found, and runs a positive-structure check that fails the stitch if no `.hol-half` is present. Writers cannot accidentally ship a holiday issue without the Holiday Identity activation.

**v8.13.4 fix:** the body-rewrite regex is now anchored to `</head>` (not the first `<body>` in the document). The scaffold `00-head-open.html` contains a documentation comment with an example body tag (`<body class="is-special" data-special="countdown"> (or field-guide).`), and a naive `count=1` regex matches that example FIRST and silently leaves the real `<body>` bare. Anchoring to `</head>` guarantees we rewrite the real DOM tag. If you edit stitch-issue.sh, preserve this anchoring.

**v8.22.5 weekly gate.** Symmetric to the holiday gate: for `weekly` format issues, the stitcher scans chapter bodies for special-edition `.sp-*` vocabulary tokens (`sp-spread`, `sp-marginalia`, `sp-rail`, `sp-margin`, `sp-pullquote-huge`, `sp-brief`, `sp-brief-kicker`, `sp-dash`, `sp-chapter-gate`, `sp-manifesto`, `sp-bignum`, `sp-gallery`, `sp-diptych`) and exits non-zero if any are found. Those classes are scoped to `body.is-special` selectors and render unstyled on a standard weekly. The 24 May 2026 weekly shipped with all of these in its chapter bodies — this gate stops the next one. Action on fail: re-run Phase 5 writers with the weekly-vocabulary brief.

**v8.22.5 `[YEAR]` substitution.** The stitcher now substitutes `[YEAR]` (in addition to `[Date]`, `[DATE RANGE]`, `[N]`) from the issue's pretty date. `01-masthead.html` uses `[YEAR]` in its right-meta tag; previously the literal shipped and got sed-fixed in Phase 9. Now handled in stitch.

**Plan-level multi-venue flag.** If `issue_meta.multi_venue` is `true` in chapter-plan.json, the stitcher additionally stamps `data-multi-venue="true"` on the rewritten body. This activates tier-9 per-venue scoping for Countdown (and is harmless on Field Guide, which uses the `.hol-half--one`/`--two` structure instead). The planner sets this flag for issues with two named venues; do not set it manually.

### Phase 7 — Per-chapter Gate 1 (during pipeline)
Each chapter has already self-audited via pre-flight.md. Now grep-scan every chapter HTML for the Gate 1 hard-fail patterns from `references/compliance-checklist.md` (1A reader-profile leaks, 1B fabrication markers, 1C staleness, 1E markup contracts, 1F image-caption integrity). Any failure → enter repair flow.

**Topic-lock — the "what's new" test (v8.25 — weeklies and a special's Meanwhile).** Run `python3 scripts/check-topic-lock.py <stitched-html> --state <state.json> --issue-date <YYYY-MM-DD>`. It enforces both topic-lock tests from `references/spec/global.md` § 02b-topic-lock: (a) the frequency cap (`recent_leads >= 3` must rest), and (b) the **development test** — a topic that led the immediately preceding issue may not re-lead on a holding pattern ("still in crisis", "waiting on the by-election", "clings on") unless `ongoing_stories[topic].last_development` names a specific datable development within the last 7 days. Non-zero exit = the Lead is a regurgitation; **re-plan the Lead** (demote the topic to the tracker box / Companion / Also and lead with a story that actually moved this week). This caught the 17–31 May 2026 three-week Starmer run, which the old frequency-only rule missed. **The orchestrator runs this directly and reads the exit code.** Also: at Phase 0 the planner must recompute `recent_leads` from the `issues/` archive (don't trust the cached counter — a dropped `lead_history` append silently disables the cap), and the writer's Lead must be *about* the named development, not the standing situation.

**Theme-clustering — no single theme owns the issue (v8.26 — weekly only).** Run `python3 scripts/check-theme-clustering.py <stitched-weekly-html>`. It scores each section's body against topic-theme keyword sets and fails if any one theme owns **3+ sections with 2+ of them rotating/discretionary** (the fixed news flow — the week's big story in the World Lead + On the Radar — is exempt). Non-zero exit = re-angle or swap a rotating section so the issue isn't a single-topic special. This caught the 31 May 2026 weekly where The Workshop + The Toolkit + the Pixel & Byte lead all landed on wearables/recovery (alongside the fixed Session). **The orchestrator runs this directly and reads the exit code;** the planner should also pre-check it when picking rotating sections so a re-plan isn't needed. See `references/spec/weekly.md` § rotating-selection rule 8.

**Plain-English spot check — ALL formats (v8.30; was Deep-Dive-only at v8.22.13, which let weekly filler/hedging through — the 1 June test).** The worst prose failure is not a markup violation; it's prose that performs a register instead of communicating — a Deep Dive performing seriousness/essayism, or a weekly padding a section with hollow connective sentences ("that framing is what makes this a discovery") and hedging its own answers ("somewhere in the region of…"). Different costumes, same failure: gesturing instead of delivering. The fix is the same for every format: write plainly, and land the point.

After the Gate 1 grep, the orchestrator picks **3 random body paragraphs** from substantive body chapters (skip front/back-matter — cover, navigator, foreword, colophon, footer — and pure-list sections like the Long Shelf / Release Radar / On the Radar; on a Deep Dive also skip Argument / Keep-Digging) and asks itself, honestly, one question:

> "Is this prose performing in any way that's getting between the reader and the information? Could it be plainer and still say what it says?"

Performance is anything from either trope list in `references/editorial-spec.md` § Deep Dive → "Editorial voice — plain English (v8.22.13)":
- **Academic-register tropes:** lit-review walls; scholar name-checks in body prose; throat-clearing about the chapter itself; "not X but Y" framing; long-then-short-then-shorter rhythmic pose; vocabulary the reader has to look up; "However" / "Moreover" / "Furthermore" paragraph-openers.
- **Magazine-essayist tropes:** the vignette-as-template chapter opening; contrastive pivots as recurring beats ("And yet…", "But actually…", "What actually happened was…"); parallel triplets for rhetorical weight; twin doublets; withheld-word paragraph endings; grand thesis-restatements; characteristic-listing as institution introduction; domino lists of recognisable nouns; "What is striking…" / "What is interesting…" essayist filler.
- **Hollow connective sentences (v8.30 — the weekly filler class).** A sentence that comments on the content's *significance* instead of adding a fact, mechanism, or answer: "That framing is what makes this a discovery rather than a headline." / "The premise leans hard into its inspiration." / "The appeal here is exactly its restraint." Test: does it add information, or just talk about the information already given? If the latter, cut it.
- **The hedged answer (v8.30).** A piece poses a "how much / how many / which" question, has the sourced numbers, then dissolves the answer into mush — "somewhere in the region of ten to twenty…", "none of this settles every case" — instead of landing it. State the number/range the sources support plainly; caveats go in an aside, never wrapped around the answer.

If 2+ of the 3 sampled paragraphs are performing, the chapter goes to repair. The pass bar is *plain* — sentences that say what they say without rhetorical pose. If a paragraph could be simplified and would still say everything it currently says, it's performing.

**Repair brief.** If a chapter fails, the repair instruction is one sentence: *Rewrite the failing paragraphs in plain English — direct subject-verb-object sentences, every sentence adding information, no tropes from either trope list in the spec. State the substance directly. A scene is appropriate only if it anchors a structural point already stated plainly, never as a load-bearing teaching unit.* After repair, the gate re-runs on a fresh paragraph sample.

**Document-level check** also runs at Phase 7: list every chapter's opening sentence. If more than two chapters open with the date-place-person vignette template ("On [date] in [place], [person] [did concrete thing]"), the issue fails for formula mannerism. Repair: rewrite the over-budget openings as direct sentences stating what each chapter is about. A vignette earns its place only when the moment genuinely serves the chapter's content — never as a structural recipe.

This is the only Phase 7 gate that doesn't have a script — by design. A regex can't measure whether prose is performing. The orchestrator gives itself the honest read. The negative examples in `editorial-spec.md` (Yellow Turban and WWI shipped paragraphs) are the calibration — if a sampled paragraph reads like any of those, it fails.

### Phase 7.5 — Release-date + result sanity check (mandatory before publish)
Run `bash scripts/check-release-dates.sh <stitched-html-path> <issue-date> <run-date> /tmp/signal-build/research-bundle.json`. The script surfaces every claim of a date/relative-time near a media name (TV, film, game, book, album), every locked-register entry (Andor, Tales of the [Jedi/Empire/Underworld], Skeleton Crew, Acolyte, Maul: Shadow Lord, Mandalorian and Grogu), **and (v8.28) every stated sports result / fixture outcome / standing**. Pass **both** the issue cover date and the **run date** (today — when facts were knowable); the result check anchors on the run date, not the cover date, because the temporal hole lives in the gap between them (pipeline runs Monday, issue dated the coming Sunday, the event lands Thursday — on/before the cover date yet still in the future at research time). Passing the bundle path lets the script list every `status:"upcoming"` fact so you can confirm the prose renders each as forthcoming, never as a result. Output is written to `/tmp/signal-date-claims.txt`.

The agent then walks the report. For each surfaced claim:
1. If it matches a locked-register entry in `references/compliance-checklist.md` (1B), verify the date in the HTML matches the locked date exactly. Mismatches are automatic FAIL.
2. If it does not match the register, run a quick web search (`<show name> release date` is sufficient for a single check) and verify YEAR. Wrong year or already-aired-when-framed-as-upcoming is automatic FAIL.
3. If a relative-time phrase is used ("last September", "this summer", "coming next month") without explicit year context, treat as suspect by default — verify or rewrite.
4. **(v8.28) For every sports result / standing:** confirm the event actually occurred on or before the **run date** (when facts were knowable — not merely on or before the issue's cover date) and traces to a source reporting it as happened. A result asserted for an event still in the future at run time (the Monaco "Norris on pole" failure — qualifying the day before the race; or a showcase that lands later in the issue week) is automatic FAIL — cut it or rewrite as upcoming.
5. **(v8.29) For every bundle fact tagged `status:"upcoming"`** (listed in the report when the bundle path is passed): confirm the prose renders it as forthcoming, never past tense. The researcher already decided it hasn't happened; the writer must honour that tag.

Fix every FAIL before proceeding to Phase 8. The release-date class of error is the single most-cited fabrication category in reader feedback (Andor S2 framed as current; Tales of the Underworld framed as upcoming when it aired in 2025; Andor S2 end-date wrong by months). This phase is non-skippable.

### Phase 7.6 — Structural + asset validator (mandatory before publish)

Run `python3 scripts/validate-issue.py <stitched-html-path> --format <format>` and, when applicable, add `--multi-venue` for issues with two or more named venues.

The script performs five classes of check:

1. **Structural well-formedness** — doctype, `</html>`, `</body>` present.
2. **Banned literal placeholders** in the rendered DOM (NOT inside `<style>`/`<script>`/`<!-- -->`): `src="..."`, `src="…"`, `href="#TODO"`, `[PLACEHOLDER]`, `[TODO]`, `[DATE RANGE]`, `[YEAR]`, `PASTE contents of`, `See assets/script.js`, `<!-- INJECT:CSS -->`, `<!-- INJECT:JS -->`. These ship invisibly through other gates if not checked.
3. **Holiday activation** (for `countdown` / `field-guide`): the real `<body>` tag (the one after `</head>`, not an example in a comment) must carry `class="is-special"` and `data-special="<format>"`. The required holiday components (`.hol-masthead`, `.hol-cover`, `.hol-half`) must be present at least once each (BEM child classes count: `hol-masthead__title` implies the masthead block exists). For multi-venue issues, `data-multi-venue="true"` must be on the body and at least two distinct `data-venue=` attributes must be present.
4. **Non-holiday special component variety** (`deep-dive`, `versus`, `rewind`, `season-review`, `shortlist`, `starter-kit`, `lookahead`, `next`): the rendered body must deploy at least the per-format floor of distinct presentational component types (9 for deep-dive/rewind/starter-kit; 7 for the rest). This turns the "use N-M component types" guidance into a hard gate so a special cannot ship as a plain page. Scaffold, animation, and layout-modifier classes don't count. Holiday formats are exempt (covered by check 3).
5. **Image URL HEAD-checks** — every `<img src="…">` and inline `background-image: url(…)` URL in the DOM is HEAD-requested in parallel (5s timeout, accepts 2xx/3xx, falls back to range-GET for servers that reject HEAD with 403/405/501). Fail-list any 4xx/5xx/timeout/DNS. URLs inside `<style>` (the inlined stylesheet) are intentionally NOT checked — those are skill-controlled, not writer-introduced.

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

### Phase 7.75 — Prose-rhythm (literary specials only — mandatory before publish)

Run `python3 scripts/check-prose-rhythm.py <stitched-html>` for literary special formats (deep_dive, versus, rewind, season_review). It walks each chapter and counts body paragraphs since the last **visual** break (figure, pull-quote, gutter marginalia, stat row, image-quote, ornament, table, list, card) — a text sub-heading does NOT count. **Non-zero exit (any chapter > 9 such paragraphs) = a paragraph wall; not shippable as-is.** Fix by adding visual breaks to the offending chapters (the planner should have briefed enough; if not, the repair writer adds a marginalia / image-quote / stat row / pull-quote / ornament every 2–4 paragraphs). This gate exists because the WW1 Deep Dive shipped chapters with 15–20 unbroken paragraphs. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

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
If gates STILL fail after auto-repair (or fail in non-image ways — release-date errors, ground discipline, accent leaks, banned phrases), spawn ONE repair `Agent` (`subagent_type: "general-purpose"`, `model: "opus"`, fallback `"sonnet"`) per round. Pass the chapter HTML + the specific failure report + the bundle. Repair re-writes the chapter; re-stitch; re-run auto-repair-images.py; re-run gates. Cost log: `bash scripts/log-call.sh repair <model> <issue_id> <chapter_id> <round> <outcome>` (record the model actually used — `opus`, or `sonnet` if the fallback fired).

**After 3 rounds — PROCEED to Phase 10 regardless of remaining gate failures.** Do NOT escalate to the reader. The pipeline publishes the best-effort issue. The orchestrator records the remaining defects in the closing summary; the CI workflow files a tracking GitHub issue for visibility (informational, not blocking).

**Bundle-exhaustion case.** If `auto-repair-images.py` reports "bundle exhausted" (cannot substitute all defects), one of the round 1–3 repairs should re-spawn the **researcher** with an inline "find N more verified image URLs for venue X" brief, append the new candidates to the bundle, then re-run auto-repair. Only fall back to "ship with duplicates" after this researcher-extension also failed within the 3-round budget.

**Cost log:** after each repair attempt, run `bash scripts/log-call.sh repair <model> <issue_id> <chapter_id> <round_number> <outcome>`. Outcome is `gate_fail` if the gate still fails and another round is coming, `ok` if the chapter now passes, `escalated` if all 3 rounds exhausted. See § Cost Logging.

### Phase 9.5 — Editorial quality scoring (observational, before publish)

This is the pipeline's only **quality** signal. Every gate before it (Phases 3b, 7–8) measures *compliance* — did the issue break a rule? None of them can tell whether the issue is actually *good*, which is the magazine's entire reason to exist. Phase 9.5 closes that blind spot, and it scores the **post-repair artifact** — the exact HTML about to ship.

**Spawn a dedicated scorer `Agent`** (`subagent_type: "general-purpose"`, `model: "opus"`, fallback `"sonnet"`). It is NOT the orchestrator and NOT any writer that worked on this issue — a producer grading its own work drifts generous. In the prompt, pass the path to the final stitched HTML and tell it to read `references/quality-rubric.md` (the full rubric, with its archive-anchored examples) and nothing else. It scores the five dimensions (voice, density, structure, opening, throughline — `throughline` is `null` for parallel formats) and returns ONE JSON object exactly as specified in the rubric's "The JSON the scorer emits" section, including the mandatory `weakest` dimension and one-sentence `note`.

The orchestrator then runs:
```bash
bash scripts/log-quality.sh '<scorer-json>'
```
which injects `ts`, computes `overall`, appends one line to `state/quality-log.jsonl`, and regenerates the public `quality.html` page. Set `writer_model` to the model the writers actually ran on this issue (the whole point is to compare writer models over time) and `scorer_model` to the scorer's model id.

**This is observational, not a gate.** A low score never blocks or reverts the publish — Phase 10's cardinal rule (always publish) is absolute. Phase 9.5 exists to accumulate the signal, not to add a failure mode. Over a dozen issues the log answers what no single read can: did the stronger writer model actually score higher? Which dimension is chronically weakest (i.e. where the *spec* should change, not the model)? Review with `bash scripts/quality-summary.sh`. See § Editorial Quality below.

### Phase 10 — Deliver + publish (always publishes; CI is post-hoc)

**Cardinal rule (v8.13.8):** Phase 10 ALWAYS publishes. Phase 9 has already done up to 3 rounds of self-healing repair; whatever survived is what ships. The reader gets a new issue every Sunday — degraded if necessary, broken-imperfect rather than missing. Last week's issue remains accessible at `/issues/<previous-filename>.html` via `index.html`, so the live site never lacks content even if this week's has minor defects.

**Stage the final HTML** to scratch first. Filename: `signal_weekly_YYYY-MM-DD.html` for standard weeklies, `signal_<format>_YYYY-MM-DD.html` for specials (e.g. `signal_countdown_2026-06-07.html`). The scratch copy is `/tmp/signal-build/<filename>`; the durable copy lives in the repo (step 2 below).

**Update state file at `/tmp/the-signal/state/signal-state.json`** per the State Tracking section: increment `last_issue_number` (standard weekly only), update `last_issue_date`, `last_issue_format`, `section_topics_recently`, rotating `last_appeared` fields, ongoing-stories status, training-phase if a block boundary crossed, `recent_facts`, `recent_next_week_themes`. For specials: also update `last_special_date`, `last_special_format`, `consecutive_specials_count`, and append to `recent_special_formats` (then trim to last 6).

**Publish to GitHub Pages.** Repository: `stevenmcdowell89-hash/the-signal`. Live site: https://stevenmcdowell89-hash.github.io/the-signal/. The repo was already cloned in Phase 0a; do not re-clone.

1. Copy the issue HTML into `/tmp/the-signal/issues/<filename>.html`.
1a. **Mirror images + generate cover** (offline-PWA + archive thumbnail). Run `bash scripts/post-publish.sh issues/<filename>.html` from the repo root. The script (a) downloads every external image referenced by the new issue into `/assets/cached/<hash>.<ext>` and rewrites the issue HTML to reference the local copies, and (b) extracts a cover thumbnail at `/assets/covers/<slug>.jpg` for the archive page. Idempotent. Failed image downloads leave the original URL intact so the issue still works online. Add any new files under `/assets/cached/` and `/assets/covers/` to the publish push list. The PWA snippet and reading-progress tracker are already baked into `template-parts/` so no per-issue injection is needed.
1b. **Refresh the quality page.** Phase 9.5 already appended this issue's score via `log-quality.sh` (which regenerates `quality.html`). If you skipped or re-ran scoring, run `python3 scripts/render-quality-page.py` once more from the repo root so `quality.html` reflects the full `state/quality-log.jsonl`. Both `quality.html` and `state/quality-log.jsonl` go in the publish push list.
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
   - Call `mcp__github__push_files` with `owner: "stevenmcdowell89-hash"`, `repo: "the-signal"`, `branch: "main"`, the commit `message` (see below), and `files` listing every changed path with its contents read from disk. Standard-run files: `issues/<filename>.html`, `index.html`, `state/signal-state.json`, `quality.html`, `state/quality-log.jsonl`. Plus the cost log if it lives in the repo (`state/cost-log.jsonl`).
   - **Commit message format:** `Issue #N — <date range>: <headlines>` for standard weeklies; `<Format> — <Topic>: <date>` for specials.
   - If MCP push fails, fall back to plain `git push` from inside the cloned repo — credentials may be configured.
5. Confirm publication by stating the GitHub Pages URL for the new issue in the closing summary. Include a note if Phase 9 had remaining defects (e.g. "Note: shipped with N image substitutions after auto-repair could not fully clear the bundle. CI will track."). Push notifications to installed PWAs are fired automatically by `.github/workflows/notify-on-publish.yml` on any push to `main` that adds a new `issues/*.html` file — the pipeline does not need to call `/api/notify` itself.
6. **Do NOT wait for CI; do NOT revert on CI red.** CI (`.github/workflows/issue-validation.yml`) runs automatically and files a tracking issue if it finds defects the pipeline missed. The tracking issue is informational — the reader (audience, not engineer) is not required to act on it. The previous week's issue stays accessible via `index.html` so the site never degrades.

**Why we publish even on red:** the reader's weekly Sunday read is the product. A new issue with imperfect images is preferable to no new issue. Phase 9's 3-round budget is the defence; if 3 rounds couldn't fix it, additional rounds rarely would. Better to ship and surface the residual issue in CI than to gate the audience's reading on a defect-resolution loop.

**Why state lives in the repo.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repo is the only path that's visible from every session, and it gives you version history of every state change for free.

**The deliverable is the published GitHub Pages URL** + a record of any Phase 9 residual defects, not a perfect issue. The reader receives the URL in the closing summary.

### Operational pitfalls (post-mortem catalog — 24 May 2026)

These all bit a real pipeline run on 24 May 2026. Read this section once before every full pipeline run.

1. **Confirm the model BEFORE Phase 0.** The orchestrator must be Opus 1M at or above the 4.7 floor (4.8 preferred). If the harness selects 4.6 or a Sonnet tier, context will overflow during Phase 5 (writer fan-out across 16 chapters), a compaction will happen, and live state will be lost. Check the model banner at start; if it's below the floor, abort and restart with explicit `/model claude-opus-4-8[1m]`.

2. **Don't pass `--verify-network --write-back` to `validate-research-bundle.py` in an egress-blocked environment.** That combo overwrites valid `blocked:egress` verification markers with hard failures and forces a full re-research. The flag pair is only safe in environments where the verifier can actually hit the CDNs. In egress-blocked sandboxes, use `--verify-network` alone (read-only verification) or skip the verifier in that mode entirely.

3. **Front-matter chapters are FULL writer-agent chapters.** Cover, navigator, foreword (the weekly's foreword slot is **The Letter**, v8.35 — same `foreword` chapter_id + `05-foreword.html` template, re-voiced), colophon, footer go through Phase 5 + Phase 7 like every other chapter. Don't list them in `scaffold_parts_used` and then write them inline in the orchestrator — that path skips pre-flight and the per-chapter gates. If a chapter is templated, it must be 100% template (no per-issue prose); anything authored goes through the spawned-agent path.

4. **`blocked:egress` URLs are research CANDIDATES, not shippable.** In an egress-blocked environment the researcher cannot verify URLs, so it records them as `blocked:egress`. The planner / writer should treat these as "needs verification by CI" — and the pipeline must NOT trust them blindly. Phase 9 auto-repair rotates from the verified pool only; `blocked:egress` URLs that fail in CI should be replaced from the verified bundle in the next round, not shipped as-is. If the verified bundle is thin, defer the publish rather than ship with `blocked:egress` placeholders.

5. **Add new image-source domains to the registry as they appear.** When a writer or researcher uses a domain not in `references/image-source-types.json`, Phase 7.7 advisories will mention it. Add the mapping in the same PR as the issue that introduced the domain — don't kick the can. The 24 May 2026 run added 12 domains (`phil.cdc.gov`, `i.guim.co.uk`, `static.independent.co.uk`, `lumiere-a.akamaihd.net`, etc.) mid-pipeline; build them into the registry so the next run finds them.

6. **Publish via `git push` from `/home/user/the-signal`, NOT via `mcp__github__push_files`.** The MCP push-files tool can't carry payloads larger than ~250KB inline, and any modern Signal issue is 100KB-700KB. The git remote at `/home/user/the-signal` is wired through a local proxy (`127.0.0.1:<port>`) that handles auth transparently. Use the standard `git add / git commit / git push origin main` flow. The MCP tool is for small files (state JSON, index updates) only.

7. **Notify workflow needs to exist BEFORE the publish that should trigger it.** The 22 May 2026 Yellow Turban Deep Dive shipped without notifications because the notify workflow was added 8 hours later. Notify workflow exists now — verify it stays in `main` before any publish.

8. **Pre-cache works via the push-notification path; the user does NOT need to open the PWA.** Two separate SW precache paths exist and they get confused with each other in post-mortems:

   - **`deepPrecacheIssue(url)` — push-triggered, the intended path for new issues.** When the notify workflow fires (on a push to `main` touching `issues/*.html`), it POSTs to `/api/notify`, which sends a push to subscribed devices. The SW's `push` event handler calls `event.waitUntil(deepPrecacheIssue(url))` BEFORE showing the notification — so it fetches the issue HTML + every `/assets/cached/` and `/assets/covers/` image, writes them to ISSUE_CACHE + IMAGE_CACHE, and only then shows the OS notification. By the time the user sees the notification (or even if they don't tap it), the issue is fully offline-ready. **No PWA open required.**

   - **`precacheFromIndex()` — page-open path, secondary.** Fires on SW install and on the `PRECACHE_ALL` message that `index.html` sends on `navigator.serviceWorker.ready`. Crawls `/index.html` dynamically for `<a href="issues/…">` links and pre-fetches anything not already cached. This is the safety net for devices that missed the push (push subscription dropped, app permission revoked, push delivery delayed). No static asset manifest — it's pure runtime discovery.

   **If pre-cache "didn't happen" for a new issue, the failure is at step 1, 2, or 3 of the push chain:**
   1. Notify workflow didn't fire on the publish push (workflow file missing on `main` at publish time, or path filter didn't match — the workflow is `on: push: paths: ['issues/*.html']`).
   2. Workflow fired but `/api/notify` returned non-2xx (auth, KV, VAPID config). PR #100 surfaces the response body in workflow logs — check the run output.
   3. Push delivered to the SW but the SW errored in `deepPrecacheIssue` (e.g. issue URL gave a redirected response — fixed in v119; or an image domain isn't reachable). `/sw-status` on the device shows ISSUE_CACHE contents.

   Verifying after publish: GitHub → Actions → notify-on-publish run for the publish commit (green = step 1+2 OK), then `/sw-status` on the device to confirm step 3 wrote the issue + its images into ISSUE_CACHE + IMAGE_CACHE.

   The 24 May 2026 post-mortem item that said "pre-cache not working — the SW needs a SW update with the new URL in its asset manifest" is incorrect; both paths above are dynamic. The actual cause was the notify workflow's role + this confusion, not a missing manifest.

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

## Editorial Quality (the quality signal)

The cost log answers "what did this issue cost?" The quality log answers the question the cost log structurally **cannot**: "was the issue any good?" Every gate in Phases 3b–8 is a *compliance* check — it catches rule-breaks (bad markup, fabricated dates, mono-sourced images, performing prose). A clean gate record proves the issue is *shippable*, not that it's *good*; the two are different things, and a magazine's whole reason to exist is the second one. This is the system that measures it.

**How it works.** At Phase 9.5 a dedicated scorer agent (never the orchestrator, never a writer on this issue) scores the post-repair artifact against `references/quality-rubric.md` — five 1–5 dimensions (voice, density, structure, opening, throughline) anchored to real archive examples, plus a mandatory `weakest` dimension and one-line `note`. The orchestrator pipes the scorer's JSON to `bash scripts/log-quality.sh`, which computes `overall`, appends to `state/quality-log.jsonl`, and regenerates `quality.html`.

**Where it lives + is visible.**
- `state/quality-log.jsonl` — append-only log, committed to the repo alongside `cost-log.jsonl`. Override path via `SIGNAL_QUALITY_LOG`.
- `quality.html` — a static, baked page at the repo root, served on the live site and linked from `index.html` ("Editorial quality →"). It can't read `state/` at runtime (`.assetsignore` excludes it), so the page is regenerated from the log at publish time, same pattern as `index.html`. This is the reader-facing view — a readable table of every scored issue.
- `bash scripts/quality-summary.sh [--since YYYY-MM-DD]` — terminal view.

**Why `writer_model` is stamped on every row.** This is the payoff. The model-selection policy (see § Model Selection) was rewritten on the principle that we can't *prove* a cheaper writer hurts quality because nothing measured it. This log is that missing instrument: once issues written by different models are scored, `quality-summary.sh` shows average overall *by writer model* — turning the model-tier question from a judgment call into an evidence-based one. Re-run that comparison when the next model ships rather than re-arguing it.

**The honest caveats (don't oversell this).** A sibling-model scorer removes the producer's bias, not all bias; the scorer model is itself part of the instrument (a score shift can be the magazine changing or the grader changing — hence `scorer_model` on every row); and the only thing that keeps it honest long-term is a ~monthly **human anchor** score (`scorer_model: "human"`) to detect drift. It is a trend instrument, not a verdict on any one issue. Scoring is observational — it never gates or reverts a publish.

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
    "the_listening": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_money": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_places": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_saga": { "last_appeared": null, "trigger_driven": true }
  },
  "the_toolkit": { "last_appeared": null },
  "currently_reading": null,
  "currently_watching": null,
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
3. If standard weekly: select 2-3 rotating sections based on cadence priority (most overdue first), from {the_shelf, this_week_in_history, the_listening, the_money, the_places}. The Saga is NOT picked here — it runs only when a peg fires it (public peg found in research, or a private peg from `currently_reading`/`currently_watching` or a manual trigger). The Toolkit is a fixed-but-yields section, not a rotating pick — include it when there's tech news (covering the full gap since its last appearance), yield it when the week is thin.
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
   - `ongoing_stories` — update weeks_as_lead/weeks_as_ongoing counts, promote/demote/drop stories as needed, add new entries if a topic has now led for 2 consecutive weeks. **v8.18:** if a topic anchored any fixed section's Lead this issue (OR was the Meanwhile #1 beat of a special), append the issue date to its `lead_history` array. `lead_history` is never trimmed — entries age out of the sliding window automatically when the planner computes `recent_leads` (count within last 26 weeks). **This append is mandatory and must happen the same run — a dropped entry silently disables the topic-lock cap (it let UK politics lead three weeks running, 17–31 May 2026). The planner reconciles `lead_history` against the `issues/` archive at Phase 0, so a miss self-corrects, but record it correctly here too.** **v8.25:** also carry `aliases` (lowercased entity tokens for matching — e.g. `["starmer","westminster","labour","makerfield"]`) and, whenever the topic leads, `last_development` = `{ "date": "<issue-date>", "what": "<one line: the specific datable thing that changed this week>" }`. If the topic is re-leading and you cannot fill `last_development` with a real development from the last 7 days, it should NOT be leading — demote it (see § 02b-topic-lock Test 1).
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
| `23-special-tokens.css` | **Non-holiday special editions only (v8.21)** — design tokens: paper / ink palette, accent set (`--accent-rust`, `--accent-ochre`, `--accent-jade`, `--accent-blood`, `--accent-ink`), serif/sans/mono stack, measure (`--measure: 36rem`), spacing scale. Scoped to `body.is-special:not([data-special="countdown"]):not([data-special="field-guide"])`. |
| `24-special-base.css` | **Non-holiday special editions only** — base typography: serif body, link underline, paragraph rhythm, default H2/H3/H4, reading-progress bar, `.sp-eyebrow`. |
| `25-special-cover.css` | **Non-holiday special editions only** — dark filmic cover with grain overlay and per-format accent radial pool. Components: `.cover`, `.cover-meta`, `.cover-body`, `.cover-eyebrow`, `.cover-title`, `.cover-deck`, optional `.cover-slogan` block, `.cover-foot`. |
| `26-special-chapter.css` | **Non-holiday special editions only** — chapter structure: `.foreword`, `.chapter`, `.chapter-head` (`.chapter-numeral` + `.chapter-title`), `.chapter-body` with measure, `.is-wide` / `.is-fullbleed` modifiers, `.sp-kicker`, `.reading-paths` cards. |
| `27-special-figure.css` | **Non-holiday special editions only** — figures and captions: `figure.fig` (+ `.is-wide`, `.is-fullbleed`, `.is-half`, `.is-half.is-left`), `figcaption` with `.fig-caption` + `.fig-credit`, `figure.image-quote` with darkened photo + overlaid italic quote. |
| `28-special-masthead.css` | **Non-holiday special editions only** — persistent pinned chrome bar at the top of every page. `.mast` containing `.mast-wordmark`, `.mast-format`, `.mast-sep`, `.mast-date`. Inverts on dark cover. |
| `29-special-callouts.css` | **Non-holiday special editions only** — baseline editorial flair available to every format. Drop cap via `.has-dropcap` / `<p class="lede">`, `.sp-ornament`, `.pullquote`, `.marginalia` (+ `.is-left`), `.bignum`, `.bignum-row`, `.source-strip`, inline `.sp-number`. |
| `30-special-meanwhile.css` | **Non-holiday special editions only** — the "Meanwhile…" catch-up section used when a special replaces the standard weekly. `.meanwhile-list` with `.tier-hot` / `.tier-warm` / `.tier-note` dots. |
| `31-special-footer.css` | **Non-holiday special editions only** — closing footer card. `.sp-footer` with `.sp-footer-wordmark`, `.sp-footer-meta`, `.sp-footer-colophon`. Ornament rule above. |
| `32-special-format-flair.css` | **Non-holiday special editions only — per-format components.** Sets `--accent` per format. Quiet adds: Blueprint blueprint-grid bleed, Starter Kit ringed numbered `.essentials` list. Visual formats: Versus (`.vs-tape`, `.vs-pair`, `.vs-verdict`, three-column cover title with `.vs-glyph`), Rewind (enlarged `.bignum-row`, `.year-band` with month markers, `.rewind-cards`), Season Review (`.rating` bars with `--score`, `.scoreboard` table, `.milestones` grid), Shortlist (`.tier-band` with `data-tier`, `.pick` with alternating image/body grid). |
| `33-countdown-destinations.css` | **Tier 9 — Holiday only. Multi-venue Countdown destination theming.** Activated by `body[data-special="countdown"][data-multi-venue="true"]` and per-chapter `data-venue="efteling"`/`"beekse-bergen"`. Per-venue grounds and accent, decorative glyph as ::after mask-image watermark, `.sp-venue-tag` inline pill. |
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
| `04-navigator.html` | navigator grid — **canonical for every format that has a navigator**. Card grid with lead-card thumbnail. Specials that want an in-issue contents page use the chapter-numeral structure inside `<section class="chapter">`, not a separate template. The former `04-navigator-toc.html` TOC-style variant was deleted in v8.22.11 — no current format used it, and writers reaching for it on weeklies was the May 17 / May 24 2026 bug. |
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
| `scripts/validate-issue.py` | **Phase 7.6 mandatory post-stitch gate.** Verifies structural well-formedness, banned-placeholder absence, holiday activation (body class + `data-special` + `.hol-masthead`/`.hol-cover`/`.hol-half` presence), **non-holiday special component variety** (per-format floor of distinct presentational components — stops a plain-page special), and image-URL reachability (HEAD requests in parallel). Exits non-zero on any failure. The orchestrator runs this directly and reads the exit code — subagent self-reports of "passed" are not acceptable. See Phase 7.6 in the workflow above. |
| `scripts/validate-research-bundle.py` | **Phase 3b mandatory upstream gate.** Reads `research-bundle.json` and enforces image_candidates rules: real URLs not keywords, ≥3 source types represented, Wikimedia ≤30%/≤4, RT-5 single-domain ≤50%, ambiguous-domain `source_type` annotation. Blocks the planner from spawning until research is corrected — the strongest prevention against the URL-fabrication / mono-sourcing chain. Uses `references/image-source-types.json`. |
| `scripts/check-image-diversity.sh` | **Phase 7.7 mandatory post-stitch gate.** Classifies every image domain in the stitched HTML via the lookup table and enforces the same diversity rules as Phase 3b. Defence in depth — catches writers omitting bundle images and skewing the final ratio, or new domains slipping in. Sandbox-aware: unknown domains warn rather than fail. |
| `references/image-source-types.json` | Lookup table mapping domain → source type (press_kit / government / archive / news_cdn / wikimedia) plus the threshold values. Edit when a new recurring source appears in research. Both Phase 3b and 7.7 gates read this file. |
| `scripts/log-call.sh` | Fire-and-forget logger — main loop calls this after each subagent returns. Appends one JSON line to the cost log (default `/tmp/the-signal/state/cost-log.jsonl`, override via `SIGNAL_COST_LOG`). Errors are silent so logging never blocks the pipeline. |
| `scripts/auto-repair-images.py` | **Phase 9 round-0 programmatic repair.** Takes stitched HTML + research-bundle.json, identifies image defects (duplicates D6, unbundled D7, page-URL-as-image D3) and substitutes unused bundle URLs in-place. Pure Python — no subagent dependency. Exits 0 on clean / fully-repaired, 1 on partial (bundle exhausted). The orchestrator's Phase 9 loop absorbs partial failures via the 3-round budget; after 3, Phase 10 ships anyway. |
| `scripts/cost-summary.sh` | Reads the cost log and prints a per-issue and aggregate breakdown (calls per role, model usage, retry rate, validator/gate failures, escalations). Run after a few issues to validate the model fallback chains. |
| `references/quality-rubric.md` | The editorial-quality rubric scored at Phase 9.5: five 1–5 dimensions (voice, density, structure, opening, throughline) anchored to real archive examples, plus the scorer's JSON contract and the honest caveats. The pipeline's only quality signal — everything else is compliance. |
| `scripts/log-quality.sh` | Phase 9.5 logger. Takes the scorer agent's JSON (arg or stdin), injects `ts`, computes `overall`, appends one line to the quality log (default `state/quality-log.jsonl`, override via `SIGNAL_QUALITY_LOG`), and regenerates `quality.html`. Non-fatal on error. |
| `scripts/render-quality-page.py` | Bakes `state/quality-log.jsonl` into the static, reader-facing `quality.html` at the repo root (the log isn't served at runtime — `.assetsignore` excludes `state/`). Called by `log-quality.sh`; safe to re-run standalone. Paths overridable via `SIGNAL_QUALITY_LOG` / `SIGNAL_QUALITY_PAGE`. |
| `scripts/quality-summary.sh` | Terminal view of the quality log: average overall, **average by writer model** (the model-tier comparison), per-dimension averages, weakest-dimension frequency. `--since YYYY-MM-DD` to floor by date. |

**Rules for CSS edits:**
- Never reorder or rename files — alphabetical order is the cascade.
- A new component fits into an existing file if the category matches; otherwise add a new file with a numeric prefix that slots it in the right cascade position.
- After any CSS edit, you can verify the build still works by running `bash scripts/inject-assets.sh` on a dummy HTML file with the two placeholder comments.

**`assets/script.js`** — single file, four logical regions:
1. **Universal base controllers** (lines 1–~445): progress bar, back-to-top, count-up, reveal observer, wax-stamp chapter numeral tracker, chapter beads (v8.3, every issue, auto-discovers chapters), sticky pin (v8.3, scroll progress driver, max-one-per-issue enforcer), chapter gate (v8.5, auto-builds from `data-chapter-num`/`-title`/`-arc`, rAF scroll-progress loop, IntersectionObserver-gated, reduced-motion + 2.5s safety backstop). Run on every issue.
2. **Special-edition motion controller** (~line 375+): parallax, stagger words, colour-wipes, D-day live countdown, sp-stat-curtain, sp-page-fold, sp-horizon piggyback, per-format signature moments. IIFE-wrapped, short-circuits unless `body.is-special` and `prefers-reduced-motion` is not set.
3. **Holiday Identity countdown controller** (v8.12, end of file): live tick on `.hol-countdown` cells (`[data-cd="days|hours|mins|secs"]`) driven by ISO `data-target` on the wrapper. Runs only on `body.is-special` AND `data-special` ∈ `{countdown, field-guide}`.
4. **Holiday Motion controller + Motion Extras controller** (v8.13.1 / v8.13.2, end of file): scroll-driven motion paired with `38-/39-holiday-motion*.css`. Tags every major `.hol-*` block with `.hm-rise`, opts in stagger delays, releases CSS safety guard via `body.hol-motion-ready`, installs IntersectionObserver reveal + rAF parallax + touch-tap unrotate + marquee touch-drag pause + folio-badge palette swap, plus eight extras (edge crossfade, count-up, ken-burns, tape-twitch, Don't Miss count-up, marquee burst, typewriter, half-ground parallax). 2.4s safety backstop force-sets `.is-in` on every `.hm-rise` if observers fail. Reduced-motion safe.
