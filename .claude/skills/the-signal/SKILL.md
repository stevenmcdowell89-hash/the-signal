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

Version 8.42.0. This file describes only **how the pipeline runs on Claude Code**. The **editorial charter** — the north-star and the standing rules as they now are — lives at the top of `references/editorial-spec.md` (§ Editorial Charter); its sliced views are in `references/spec/`. The **full version-by-version history** (every incremental fix, retirement, and rename from v8.13 → v8.39) lives in `CHANGELOG.md` next to this file. Read the charter for *what the rules are*; read the CHANGELOG for *why and when they changed*. This SKILL.md no longer carries the patch narrative — it was consolidated into the charter + CHANGELOG in v8.38 (W-4) so the living spec reads as one charter, not a patch pile.

**The weekly is the "Transmission" identity + a deterministic spine (v8.42).** The standard weekly is now a distinct, self-contained visual + structural system — see `docs/weekly-redesign-HANDOFF.md` and the visual target `docs/mockups/reference-issue-transmission.html`. Three things changed and are load-bearing: **(1) Structure is deterministic, not generated.** `references/format-skeletons/weekly.json` is the single source of truth for the four movements + bands; the planner fills it, and **`scripts/stitch_weekly.py` (not the special concatenation path) generates ALL chrome** — cover/masthead/tuner, the four movement dividers, every band-head, the colophon, the sign-off — so the 2026-07-12 structural failures (movement bands missing, The Desk exploded into standalone sections, Release Radar as its own section) are **unrepresentable**. A weekly **writer produces only ONE band's inner content** to `/tmp/signal-build/chapters/<band_id>.html` (no `<section>`, no band-head, no divider). **(2) A weekly-only light bundle.** The weekly loads ONLY `assets/css/weekly/*.css` (~24KB) + `assets/script-weekly.js` (~1.4KB) — never the ~460KB special/holiday CSS or the holiday fonts. **(3) Enforced by construction + gate.** `validate-issue.py --format weekly` hard-checks the four-movement structure (via `data-movement`/`data-role`/`data-desk-column`/`data-station` hooks) AND visual-consistency (no special/holiday CSS or fonts, no `.sp-*` body components, the Transmission masthead not the special dark hero) + a scaffold-leak check. Books are the fixed **Bookmark** rail every issue (the Bookmark-vs-Shelf contradiction is resolved: there is no rotating "The Shelf"). The dark bound-magazine treatment is now **reserved for specials** (their signal of difference). Regression: `scripts/verify-weekly-golden.sh` stitches the committed golden fixture and asserts all gates green; publish is gated by `scripts/publish-gate.sh` (a machine-checkable receipt — Pillar F). Specials are unchanged by this rebuild.

**The current state, in one paragraph.** The weekly is a **four-movement spine** — **I THE OPEN** (The Letter → The Week, Composed → The Week in Numbers → Caught Up) · **II THE LONG READ** (exactly one deep anchor, rotating subject) · **III THE ROUNDS** (Touchline, Pixel & Byte, Screen & Sound + a Bookmark books rail, The Desk, each Desk column closing on a "Do This Week" pin) · **IV THE CLOSE** (The Threads → Down the Rabbit Hole → On the Radar → Do This Week → Colophon; the issue ends on a verb + a human line). Target **~6,000–9,000 words**, a tight **~12-component palette**. **The core furniture layer is ON BY DEFAULT (v8.43, WP-8/8.1):** every weekly distributes the five core furniture objects + the dial signature across its bands (`design_system: "mx"`) to reach the Law-2 density budget (0.8–1.0 events/screen) with calm tier-1 motion — identity untouched (same masthead, palette, three faces, 800px chassis). See Phase 5 § "FURNITURE LAYER" and `references/format-skeletons/weekly.json` § `furniture_layer`. The **daily→weekly bridge is live data** — weekly generation reads `GET /api/daily/digest?since=7d` and the reader's `saved_this_week` state when composing The Letter and The Threads (§ The daily→weekly bridge). **Coverage is bounded by instants, not by calendar days (coverage rebuild, `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md` §3.5/§3.7).** The window is `(previous research_cut_at, now]` — a *knowability* window — and every `status:"upcoming"` fact opens an **open loop** in state that the next issue is obliged to resolve. Before this, a day could be "inside the covered week" while its results were unknowable at research time, so a Sunday-concluding event (the World Cup final; The Open) was gate-checked as upcoming and then abandoned — five verification layers refusing to guess a result and no counterpart obligation to report it once it happened. Phase 0 now reads six state keys (`research_cut_at`, `open_loops`, `cover_lead_ledger`, `sports_calendar`, `interest_depth`, `used_image_urls`) and Phase 10 writes them back; see Phase 0a and § State Tracking → Coverage continuity. **Synthesis-by-juxtaposition** (2–4 attributed conflicting excerpts in sequence) is the technique for contested World/Long-Read material. The **gate ledger is exactly three ship-quality gates** (§5 of `docs/signal-final-recommendations-2026-07.md`; presented in `references/compliance-checklist.md`): **(1)** the image-URL verification chain (`validate-issue.py` image checks + `auto-repair-images.py`), **(2)** markup contracts (`validate-issue.py` structural/placeholder/back-link/markup checks, including the Issue-in-Numbers stats assertion), and **(3)** one holistic editorial-quality read (Phase 9.5) that answers the single question — *did this issue tell him what the week added up to, and give him one thing to do?* `validate-research-bundle.py` (anti-fabrication) and `validate-chapter-plan.py`'s structural checks remain as **upstream production aids**, not ship gates. The retired gates (topic-lock, theme-clustering, prose-rhythm, visual-smoke-test, per-section aphorism/closer, deficit-promotion, hard-cadence-floor, the standalone plain-English random-sample weekly pass, and the observational-only scorer as a bolt-on) are gone — do not reintroduce them.

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

The pipeline: Phase 0 (read state → **coverage window + open loops + cover-lead ledger + sports calendar** → decide format) → Phase 3 (researcher subagent) → **Phase 3a-verify (orchestrator WebFetch every URL — v8.13.8)** → Phase 3b (research-bundle validator) → Phase 4 (planner subagent + validator) → Phase 5 (writer subagents, parallel or sequential) → Phase 6 (stitch) → Phase 7 (per-chapter Gate 1) → Phase 7.5 (release-date check) → **Phase 7.6 (structural + asset validator — `validate-issue.py`: the image-URL verification chain gate + the markup-contracts gate)** → Phase 7.7 (image-source diversity — `check-image-diversity.sh`) → Phase 8 (stitched-issue Gate) → Phase 9 (repair if needed — round 0 is `auto-repair-images.py`) → **Phase 9.5 (the holistic editorial-quality read — the third ship-quality gate)** → Phase 10 (deliver + publish + CI verification). *(v8.38, W-4: Phase 7.8 DOM visual-smoke-test and Phase 7.75 prose-rhythm are removed — their intent folded into the markup gate and the holistic read respectively; see §5 gate ledger.)*

There is NO separate "lightweight" path. Standard weeklies run the full pipeline same as specials. Build dir is `/tmp/signal-build/`, cleared at the start of every run.

> **Environment note.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repository at `stevenmcdowell89-hash/the-signal` is the only durable store — state, issues, and the cost log all live there. Per-session paths like `/tmp/signal-build/` are scratch only.

> **Gate discipline (MANDATORY).** Every script-backed gate in this workflow — `verify-orchestrator-model.sh` (Step Zero), `validate-chapter-plan.py`, `validate-research-bundle.py`, `stitch-issue.sh` (which embeds the holiday-activation rewrite + banned-vocabulary scan + holiday scaffold override + holiday half-wrap reorganisation), `check-release-dates.sh`, `validate-issue.py`, and `check-image-diversity.sh` — is **run by the orchestrator itself**, not delegated to a subagent. The gate's verdict is its **exit code**, full stop. A subagent claiming "gate X passed" is not acceptable evidence — the orchestrator must invoke the script via `bash` or `python3`, read the printed report, and read the exit code before advancing. If a subagent reports success but the orchestrator did not run the gate, the orchestrator runs it now. This rule exists because subagents have been observed reporting "gate passed" for gates they never invoked.

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

**Six coverage keys are read here and written back at Phase 10 (coverage rebuild, SPEC §3.5).** They are documented field-by-field, with producer and consumer, in `references/spec/data-contracts.md` § State — read that file at Phase 0 as well; it is short and it is the contract. Do not read an absent key as a policy value:

| Key | Read at | Used by | Written at |
|---|---|---|---|
| `research_cut_at` | 0a-window | the window's opening bound | Phase 10 (measured instant, overwrite) |
| `open_loops[]` | 0a-loops | mandatory resolutions in the researcher brief | Phase 10 (resolve / drop / append) |
| `cover_lead_ledger[]` | 0a-ledger | the planner's lead choice — `cover_leads_on` + `cover_lead_topic_family` + `lead_rationale` | Phase 10 (prepend, keep last 12; family copied from the plan) |
| `sports_calendar[]` | 0a-calendar | results-ledger rows, On the Radar, planner briefing | Phase 10 (prune ended, append confirmed) |
| `interest_depth` | 0a-calendar | how deep each sport is covered | not written by the pipeline (owner-set) |
| `used_image_urls` | Phase 7.6 / 9 | the cross-issue lead-image budget (SPEC §3.8) | Phase 10 step 1a (`mirror-images.py`) |

### 0a-window. Compute the coverage window (mechanical, no web search)

**The window is `(previous research_cut_at, now]` — a knowability window, not a calendar range.** This is the fix for the largest coverage defect in the archive: issue #17 (window 13–19 Jul) carried the World Cup final twelve times as an *upcoming* fact, correctly, because research ran before kick-off; issue #18's window began 20 Jul, so the final's **result appears zero times in either issue** — the largest football tournament ever played concluded and the magazine never said who won. The Open, the same. The mechanism was never editorial: coverage was tracked by **date range**, knowability by **run date**, and nothing reconciled the two. The proof it was structural is issue #16, which published on a *Monday* and is the only issue that ever successfully reported a Sunday result (Wimbledon, 12 Jul) — it got there by accident of scheduling, not by design.

```bash
mkdir -p /tmp/signal-build
python3 - <<'PY' > /tmp/signal-build/window.json
import json, datetime
st = json.load(open('/tmp/the-signal/state/signal-state.json'))
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump({"from": st["research_cut_at"], "to": now, "research_cut_at": now}, __import__('sys').stdout)
PY
cat /tmp/signal-build/window.json
```

- `window.from` = the value **read from state** — the instant the *previous* issue's research stopped. Nothing may fall between two issues, so this bound is copied, never recomputed.
- `window.to` = `research_cut_at` = **this run's measured instant**. It is stamped here and may be **advanced once**, at Phase 3a-verify, to the instant the bundle actually froze (research genuinely stops when the last URL is verified). It never moves backwards, and there is exactly one value: `/tmp/signal-build/window.json` is the single source that Phase 4 copies into the plan and Phase 10 writes to state.
- If `research_cut_at` is missing from state (first run after the rebuild), fall back to `last_issue_date` at `00:00:00Z` and say so in the closing summary. Do not invent a plausible instant.

**Everything downstream is briefed with these two instants**, not with a date range: the researcher (Phase 3a) gathers what became knowable inside the window, the planner writes them into `issue_meta.research_cut_at` / `issue_meta.window` (Phase 4), and the stitcher derives the cover dateline from them (Phase 6).

**The intended visible consequence — read this before "fixing" it.** Because the window closes when research stops, an event concluding on Sunday evening lands in the **next** issue's window *by construction*. That is the point: the alternative is the status quo, where the event is inside the dateline and absent from the prose. It is only safe because §3.7 makes the carry-forward an obligation rather than a hope — the `[CARRIED FORWARD…]` caption in issue #18 ("CARRIED FORWARD TO №019 · THE RACE STILL TO RUN") was decorative, a promise the system had no mechanism to keep. Now the promise is a row in state. Do **not** widen the window to reach forward past the cut to make a dateline tidier; that reintroduces the defect exactly.

### 0a-loops. Read open loops → mandatory resolutions (mechanical)

Read `state.open_loops[]`. A loop is **matured** when `status == "open"` **and** `expected_resolution_date <= today` (SPEC §3.7; `resolved` and `dropped` are terminal — a dropped loop does not mature). Build the matured list and carry it forward as **mandatory resolutions**, not suggestions:

- Every matured loop **must** come back from Phase 3a as a `facts[]` entry carrying `resolves_loop: "<loop id>"` (the join key — see `references/spec/data-contracts.md` § `facts[]`). `validate-research-bundle.py --state` hard-fails the bundle otherwise (Phase 3b), and `validate-issue.py` independently hard-fails a rendered issue with no `data-resolves-loop="<id>"` for a matured loop (Phase 7.6). Both layers, because the bundle can carry a fact the writer then drops.
- Every matured loop's `band` names the chapter that **owes** the resolution. Pass it to the planner so the band is briefed with the debt, and to that band's writer in Phase 5.
- If a loop genuinely cannot be resolved (the event was postponed, abandoned, or the result is not reportable), the run says so explicitly and Phase 10 records it — `status: "dropped"` with a `resolution` naming the reason. A dropped loop is an honest miss on the record; a silently deleted loop is the original defect.

This is the whole counterpart obligation the pipeline lacked. The five verification layers that stop the writer asserting an unknown result are unchanged — and they were never the problem. The problem was that the more carefully the pipeline refused to guess a Sunday result, the more reliably that result vanished.

### 0a-ledger. Compute the cover-lead ledger (mechanical — a planner INPUT, not a gate)

Read `state.cover_lead_ledger[]` (last 12, newest first) and compute, for the **last 4** entries, the count of each `topic_family` appearing with `led_on: "news"`. Pass **the whole ledger plus that tally** to the planner in Phase 4. If any family reaches **≥3 of the last 4**, flag it in the planner brief as *rutted*, and name the consequence: leading `news` on that family again requires `issue_meta.lead_override_reason` (≥80 chars) or `validate-chapter-plan.py` rejects the plan (SPEC §3.6).

**This is not a restored topic-lock, and it must not become one.** `check-topic-lock.py` was deleted in v8.37 (W-3) and stays deleted; SPEC §1 non-goals forbid reintroducing it or any suppression gate. The difference is exact and load-bearing:

- **Topic-lock (retired) was suppression:** a sliding window that *forbade* a subject from leading, so the pipeline made the editorial decision by refusal.
- **The rut rule (this) is an input plus a forced written justification:** the planner can always lead with the same family again — it just has to say, in prose, why this week's development earns the cover over everything else that was available. Nothing is suppressed. Nothing is demoted automatically.

What actually changed is the planner's *field of view*. v8.37 left `lead_history` written-but-read-by-nothing, and the only lead history the planner could see was `last_cover_lead` — **one week**. So it could not see that UK politics had led 6 of the last 9 covers, and a holding-pattern story kept the lead by default (defect C). The ledger is nine-plus weeks of rendered-cover history; `lead_history` on `ongoing_stories[]` remains a *story-thread* record and is **not** interchangeable with it (see § State Tracking).

### 0a-calendar. Read + verify the sports calendar (light web search — verification, not discovery)

Read `state.sports_calendar[]`. **Every seeded entry carries `needs_verification: true`, and the seed is a prompt to check, never a fact of record (SPEC §3.12).** Before the planner relies on an entry, confirm its dates against a source with a targeted search or WebFetch. Verify only the entries this run will actually rely on — those whose `start`/`end` touch the window or the coming week — so the cost stays bounded as the calendar grows. An entry that cannot be confirmed is **not passed to the planner as fact**; say so and move on. Never rewrite an entry's dates from memory: re-verify or delete.

Then classify each confirmed entry against the 0a-window instants and hand the three buckets to the researcher (3a) and planner (4):

| Bucket | Test | Obligation |
|---|---|---|
| **Concluded in-window** | `end` falls inside `(window.from, window.to]` | **Mandatory results-ledger row** in the Touchline, `data-sport` on the row (SPEC §3.4/§3.11). A result that concluded in-window and is missing from the ledger is the defect this whole rebuild is about. |
| **Running now** | `start <= window.to` and `end > window.to` | Covered as in-progress — standings/leaderboard via the polymorphic `.mx-scorecard` `data-table-kind`, and it opens a loop if the conclusion is reportable (Phase 10). |
| **Opens next week** | `start` falls in the seven days after `window.to` | **On the Radar** in The Close. Forward fixtures live there now, not in the Touchline ledger (SPEC §3.11). |

**`multi_sport` classifies an event, never a result (SPEC §3.11, amended 2026-07-26).** `sports_calendar[].sport` may be `multi_sport` — the Commonwealth Games is a games, not a sport — but a **result belongs to a sport**, so a `multi_sport` entry must be briefed as *several* results: the researcher gathers per-discipline results and the ledger renders one row per event with a **specific** `data-sport` (`athletics`, `swimming`, `cycling`, …). `data-sport="multi_sport"` is forbidden and WP-4's validator rejects it — otherwise ten sports collapse into one token and a two-row ledger passes the ≥2-distinct-sports invariant while telling the reader nothing about breadth. The daily's domain names (`functions/daily/profile.js`) are a third, separately-mapped namespace; do not force the three to match. The canonical token list lives in `references/spec/data-contracts.md`.

**Dates vs instants — the one edge case worth care.** `sports_calendar` entries carry `start`/`end` as **dates** (`YYYY-MM-DD`) while the window is bounded by **instants**. Where an event's finish time is known (a 15:00 ET final), compare that; where only a date is known, treat it as concluding at the end of that day and — if the conclusion falls within a few hours of `window.to` — **verify against a source** rather than guess which side of the cut it landed on. Guessing here is exactly how a result gets counted as covered while its band says nothing.

**Depth is set by `interest_depth`, and an absent key is `unset` — never `off`.** The value set is `full` · `majors_only` · `results_only` · `off`. Only the three sports the owner has explicitly weighted are seeded (`football: full`, `golf: majors_only`, `motorsport: results_only`). The sports whose feeds arrived with the daily-inputs work — cricket, cycling, athletics — have **no key at all**, and a sport with no key is covered **on news value**: brief it, and add a key only when the owner states a depth. Reading an absent key as `off` would recreate the invisible-sport defect in a new place, which is precisely how football and golf came to be the only two sports the system could see. `results_only` (motorsport) is what stops one race saturating the Touchline with five furniture objects: big results are in scope, session-by-session and paddock process are out.

### 0b. P1 calendar check (mechanical, no web search)
P1 triggers are calendar-fixed. They always win. Compute against today's date and the state file:

- **Field Guide:** today is the Sunday closest to (`upcoming_trips[0].start` minus 6 weeks). Window: ±3 days.
- **Countdown:** today is the Sunday closest to (`upcoming_trips[0].start` minus 2-3 weeks). Window: ±3 days. If both Field Guide and Countdown could fire on the same Sunday, Field Guide wins (earlier in the trip arc).
- **Half-year Rewind:** today is the last Sunday of June. **Defer rule:** if `upcoming_trips[0]` overlaps that Sunday or the following week, defer to the first Sunday at least 5 days after the trip ends.
- **Year-end Rewind:** today is the last Sunday of December.
- **Season Review:** Serie A or PL closing weekend has just concluded (the league has played its final matchday in the last 7 days) AND no Season Review fired for that league this season.
- **Deep Dive — NOT a P1 (retired the standalone schedule, v8.39, S5).** The `deep_dive_schedule` quarterly timer is gone. Deep Dive was the only format carrying its own cadence state-machine *on top of* the P1/P2/P3 stack, and the extra machinery (a `next_due` date, a `cadence_weeks` band, defer-without-advancing bookkeeping) never earned its keep — Deep Dive already appears in **P2** (a major product launch in a core interest) and **P3** (the dry-spell editorial-picks pool). It now fires **only** through that existing stack, or on manual request. When P3 fires and the pool offers a Deep Dive, the editor still draws the topic from `deep_dive_backlog` (skipping `needs_sharpening` entries) — the backlog is kept; only the separate *timer* is retired.

If ANY P1 fires, commit to that format immediately. **Skip 0c, 0d, 0e.** Continue at Phase 3.

If multiple P1s fire on the same Sunday (rare): Field Guide > Countdown > Season Review > Rewind.

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

This scout is optional — the researcher subagent in Phase 3 will do its own news pass. The 0f scout exists so the main loop knows whether the issue is shaping up around a landscape-shift story (which influences cover headline framing and rotating-section selection). Scout **against the 0a-window instants**, not against "the last seven days", and treat the 0a-loops matured list and the 0a-calendar concluded-in-window bucket as already-committed coverage — they are obligations the issue carries before any new lead competes for space.

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

**MANDATORY (coverage rebuild, SPEC §3.5/§3.7/§3.12) — the researcher brief carries the window, the loops and the calendar.** Pass all four Phase-0 products inline, and state them as obligations, not context:

1. **The coverage window as two instants** (`/tmp/signal-build/window.json`). Gather what became *knowable* inside `(window.from, window.to]`. Do not reason in calendar weeks — "Sunday is in the week" is exactly the assumption that lost the World Cup final.
2. **The matured open loops (0a-loops) as mandatory resolutions.** For each, the researcher MUST return a `facts[]` entry whose `resolves_loop` equals the loop `id`, carrying the actual result with `status: "happened"` and a source URL. A loop it cannot resolve must be reported back explicitly with the reason (postponed / abandoned / not reportable) — never left silently unaddressed. This is the *only* mechanism by which a result that concluded after last week's cut reaches the reader.
3. **The sports calendar buckets (0a-calendar).** Every **concluded in-window** event needs the facts for a results-ledger row (winner, margin/score, venue, date) with a source — one row per event, a **specific** `data-sport` per row (a `multi_sport` calendar entry yields one row per discipline, never a `multi_sport` row). Every **running** event needs the current state of the table/leaderboard. Every event **opening next week** needs a dated line for On the Radar. Depth per `interest_depth`; a sport with **no** `interest_depth` key is researched on news value, not skipped.
4. **`status:"upcoming"` facts must be resolvable later.** A fact tagged `upcoming` becomes an open loop at publish, keyed on its own `date` — so the `date` on an upcoming fact is the **expected resolution date**, not a vague "soon". If the researcher cannot date the conclusion, it cannot open a loop, and a Sunday result will go missing again: date it or drop it.

Nothing here adds a bundle field beyond the ones already contracted (`resolves_loop` on `facts[]`; `shows` / `capture_year` / `licence` on `image_candidates[]`). The loop's `expected_resolution_date` is derived from the fact's `date` at publish, and its `band` from the chapter the planner routed the fact to.

**MANDATORY (v8.13.7) — Researcher MUST verify every image URL with WebFetch.** For each candidate, run WebFetch on the URL. Accept it ONLY if the response is 2xx and `Content-Type` starts with `image/`. Record the result inline on the candidate as:
```json
"verified": { "head_status": 200, "content_type": "image/jpeg", "verified_at": "<ISO timestamp>" }
```
If the URL is a brand-site PAGE (returns `text/html`), open it with WebFetch and find the real `<img src>` CDN URL in the markup — use THAT URL, not the page URL. If you cannot find a working URL for a subject, DROP the candidate from the bundle. Do not ship `"verify later"` notes. The bundle must surface at least 16 distinct verified URLs (per `thresholds.min_unique_candidates`) so writers don't recycle. **Per-pick image coverage (v8.32):** for recommendation formats (Starter Kit Essentials, Shortlist, Next), surface **at least one real image per recommended title** — actively search the official/press/show site, TMDB, and Wikimedia for *each named pick*, not just the ones that surface easily — so no pick ships imageless (the audio-drama Starter Kit floor: every pick had an image). In an egress-restricted run the URL is recorded `blocked` for CI to re-verify, but a real direct image URL must still be found for every pick.

**MANDATORY (SPEC §3.2/§3.8/§3.13/§3.14) — every candidate declares WHAT IT SHOWS, and the bundle carries ≥3 distinct shapes.** Each `image_candidates[]` entry carries `shows` (the 11-value enum), `capture_year` (the year the photo/render was made — `null` only for a synthetic `diagram`/`chart`) and a `licence` object (`holder`, `code`, `url`, `allows_derivatives`). Brief the researcher on the **floor, not a ceiling**: at least three distinct `shows` values, and actively hunt the shapes that carry information — the paper's own figures for a science piece (`media.springernature.com` and generic DOI/open-access hosts are in the domain map), a real gameplay screenshot for a game (Steam's `appdetails` API returns a `screenshots[]` array; the Steam CDNs are already whitelisted), a map or chart where the prose cannot show the thing. **Rank 5 of 5 — last resort — is `key_art`, `product_shot` and `portrait`** (`shows.last_resort_shapes`). **`key_art` and `portrait` may never be a lead figure, issue-wide, in any band** (SPEC §3.8, resolved 2026-07-26): both are substitutes for showing the thing itself — key art is the logo, a posed portrait is the person *not* doing the thing. `product_shot` may lead **only where the band's subject is the product itself** — a hardware launch or review, where the device genuinely is the most informative image — and never a game, software or service band, where it is a box standing in for something that moves. A candid at an event is `event_photo`, not `portrait`. There is **no Wikimedia quota in either direction** — Commons is a fine source when it holds the right *shape*, and the retired ≤30%/≤4 ceilings must not be reintroduced as a target (see Phase 3b).

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
6. **Stamp the research cut (coverage rebuild).** Research has now genuinely stopped, so advance `research_cut_at` / `window.to` in `/tmp/signal-build/window.json` to `date -u +%Y-%m-%dT%H:%M:%SZ` — the honest instant the bundle froze. It only ever moves **forward** from the 0a-window stamp, and this is the last time it moves: Phase 4 copies it into the plan, Phase 10 writes it to state, and next week's Phase 0 reads it back as `window.from`.

This is the only enforcement layer the researcher cannot fake. The CI workflow (`.github/workflows/issue-validation.yml`) re-checks every URL with full network access — fabricated `verified` blocks that pass orchestrator verification but fail CI will surface as a red ✗ on the publish commit (and an auto-filed GitHub issue).

If WebFetch fails for the orchestrator in a given environment (egress restricted on the URL's host), record `verified.head_status: "blocked"` and `verified.content_type: "blocked"` on the candidate, and rely on the CI workflow as the authoritative gate. The candidate is NOT dropped — it's flagged for CI to resolve.

### Phase 3b — Research-bundle validator (mandatory before planner spawns)
Run `python3 scripts/validate-research-bundle.py /tmp/signal-build/research-bundle.json --run-date <today> --state /tmp/the-signal/state/signal-state.json` (pass today's date — the date the pipeline is actually running — so the facts temporal gate anchors correctly). The script enforces the `image_candidates` rules from `references/spec/global.md` image-integrity:

- Every `url_or_keyword` must be an `http(s)://` URL (keywords are rejected — they force writers to invent URLs, the RT-16 trap).
- ≥3 of the 5 source types represented (press_kit / government / archive / news_cdn / wikimedia — see `references/image-source-types.json`).
- Any single domain >50% is RT-5 hard fail (`thresholds.single_domain_max_pct` — **not** retired).
- **≥3 distinct `shows` values across `image_candidates[]`** (`thresholds.min_distinct_shapes`, SPEC §3.8/§3.14). The axis is the 11-value `shows` enum — `event_photo` · `gameplay` · `in_engine` · `key_art` · `product_shot` · `portrait` · `diagram` · `map` · `chart` · `artefact` · `document` — canonicalised in `references/image-source-types.json` and mirrored in `references/spec/data-contracts.md`. A value outside the enum is a hard fail: an unlabelled or typo'd shape cannot be counted.
- **The Wikimedia caps are RETIRED (SPEC §3.14, 2026-07-26) — do not reinstate them and do not brief a researcher as though they existed.** `wikimedia_max_pct: 30` and `wikimedia_max_count: 4` are gone from `thresholds` (recorded in `retired_thresholds` so the retirement is auditable) and no script reads them. The reason is the whole of defect E: **a ceiling with no matching floor reads as a target.** Commons became the thing to fill *up to* — "four Wikimedia images allowed" — while nothing required an image that showed the mechanism working. `min_distinct_shapes` is the floor the ceiling was standing in for and failing to be. A bundle of eleven Commons images with three distinct shapes is better research than four Commons images that are all key art.
- **Shape quality is judged by information gained, not by provenance** (`references/compliance-checklist.md` § Image specificity check, rewritten by SPEC §3.13): (1) a photo/still of the actual thing happening (`event_photo`, `gameplay`), (2) a diagram/map/chart carrying information the prose cannot, (3) the artefact or primary document itself, (4) in-engine or in-context still, (5) **key art / product shot / posed portrait — last resort.** Of that rung, **`key_art` and `portrait` may never lead any band, issue-wide**, and `product_shot` may lead **only** where the band's subject is the product itself (hardware — never a game, software or service). Issue #18's Pixel & Byte lead was Halo key art with the logo composited in; the old spec ranked press-kit art at 2 and instructed "find official art for that game", so the researcher obeyed the spec. Do not hand writers a bundle whose only shapes are rank 5.
- Ambiguous domains like `live.staticflickr.com` require an explicit `source_type` field on the candidate.

It **also** enforces the `facts` provenance rules (v8.29 — see Phase 3a and `references/spec/global.md` § fact-provenance): each fact carries `claim`/`status`/`date`/`source_url`; a `status:"happened"` fact dated after `--run-date` is rejected (it can't have happened yet); a `type:"opinion"` fact must carry a real `speaker` + `quote`. An absent/empty `facts` array warns (acceptable for a fact-thin issue) but a malformed entry hard-fails.

**And (coverage rebuild, SPEC §3.7) it enforces the open-loop obligation.** `--state` is what makes that possible: with the state file passed, the validator computes the matured loops (`status == "open"` and `expected_resolution_date <= --run-date`) and **hard-fails when a matured loop has no `facts[]` entry with a matching `resolves_loop`**. Pass the *cloned repo's* state path so the loops it reads are the ones Phase 0a-loops read. This is not a new gate — it is a new check inside the existing upstream production aid, per SPEC §1's non-goals; the rendered counterpart is checked at Phase 7.6 by `validate-issue.py`, and no fourth ship gate exists.

**Non-zero exit code = research is not shippable to writers.** Re-spawn the researcher with the failure report inlined into the prompt. The researcher uses WebSearch / WebFetch to find verified URLs from the under-represented source types and rewrites `image_candidates`. Re-validate. Max 2 retries before escalating to the reader. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

This gate exists because the 17 May test issue shipped with 14 fabricated image URLs (writers constructed URLs because the bundle gave them keywords like "Wikimedia Commons: Keir Starmer"). Catching the broken bundle upstream costs one extra script run; catching the fabrications downstream costs a full writer re-run plus image substitution work.

### Phase 4 — Planner subagent + validator gate
Spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). Pass the path to `research-bundle.json`. In the prompt, tell it to read `references/chapter-plan-schema.md`, `references/pre-flight.md`, and the planner's spec slice: `references/spec/global.md` sections `identity`, `key-rules`, `markup-contracts`, `accent-lockdown`, `stat-budget`; plus the format's H2 anchor in `references/spec/formats.md`; plus `references/spec/specials.md` section `overview` if special edition. The subagent writes `/tmp/signal-build/chapter-plan.json`. **For weeklies (v8.30): the plan MUST include a `release_radar` chapter** (rendered after `screen_sound`) with a `radar_items` array of 15-20 entries across ≥4 categories — `validate-chapter-plan.py` hard-fails a weekly that omits it. The planner pulls these from the bundle's `release_radar` items; the writer (Phase 5) renders the chapter using the `.radar-cat` category-dot markup.

**Weekly word budget + image routing (2026-07-13 handoff A5/A6).** For weeklies the planner MUST also: (a) **allocate the word budget per band** — decompose the 6–9k issue target into per-band `target_word_count` shares drawn from each band's `target_words` range in `references/format-skeletons/weekly.json`, summing **≥ 6,000 (aim 6,800–7,500 — mid-band, so a light news week still clears 6,000)**, declaring the arithmetic in `issue_meta.word_budget`; and (b) **assign ≥ 1 `image_candidate` from the research bundle to the Long Read and each feature band; populate `images_needed` accordingly** — each entry's `role`/`source_constraint` copied from the chosen bundle candidate, `alt_required: true` on the Long Read's. `validate-chapter-plan.py` hard-fails a weekly plan whose allocations sum under 6,000 or whose `long_read` carries an empty `images_needed`, and warns on any round band allocated > 350 words with none. **(c) Set `issue_meta.design_system: "mx"` (the furniture layer is the weekly default, v8.43) and allocate the furniture objects to bands per `references/format-skeletons/weekly.json` § `furniture_layer.band_slots`** — the Touchline gets the fixtures ledger + standings scorecard + dial signature + a quote-object, The Week in Numbers gets the chart card, Do This Week gets the ticket, and quote-objects distribute to reach the Law-9 ≥4-named-voice floor. Omit `design_system` only for a deliberate legacy back-compat build (not new issues).

**Coverage window, cover lead and vintage (coverage rebuild, SPEC §3.1/§3.5/§3.6).** For weeklies the planner MUST also emit, in `issue_meta`:

- **`research_cut_at`** and **`window` `{from, to}`** — copied verbatim from `/tmp/signal-build/window.json`. `window.to` **equals** `research_cut_at` (this run's measured cut); `window.from` is the previous issue's cut, read from state at 0a-window. The planner does not compute or round these.
- **`cover_leads_on`** — `"news"` | `"long_read"`. The cover's lead transmission is now a declared choice, not an emergent one.
- **`cover_lead_topic_family`** — the `topic_family` of the story the cover leads on, from the closed enumeration in `references/chapter-plan-schema.md` § Topic Family Enumeration (which now includes `cyber_privacy`). **This is the field the rut rule matches against `state.cover_lead_ledger`**, and Phase 10 copies it verbatim into the new ledger entry, so it must be *stated* rather than left to be inferred from the piece pool. `validate-chapter-plan.py` treats it as **weekly-required and enum-checked**: an omitted or out-of-enum family hard-fails the plan (an out-of-enum value could never intersect the ledger, so the rule would pass while checking nothing). The validator's resolution chain — explicit field, else the families of the plan's `role: "lead"` pieces — survives only as the **compatibility path for plans written before the field existed**, so such a plan still gets a meaningful rut verdict instead of a crash. A new plan states the field.
- **`lead_rationale`** — ≥120 chars, and it must **name what was considered and rejected**. Not a summary of the chosen story: an account of the choice. This field exists because defect C was a planner that never had to argue for the lead.
- **`lead_override_reason`** — ≥80 chars, **only** when the rut rule trips (0a-ledger flagged the family as rutted and this plan still leads `news` on it). Omit it entirely otherwise.

And on the chapter briefs: **`long_read.vintage`** (`news` | `evergreen`, plus `material_span` + `latest_development` when evergreen — SPEC §3.1), and **`week_in_numbers.rows[]`** with a `source_band` per row (a `chapter_id` present in this plan, or the literal `"state"` for the personal rows). Every one of these fields is specified in `references/chapter-plan-schema.md` and enforced by `validate-chapter-plan.py`; nothing here is a new gate.

**Pass the planner all four Phase-0 products inline:** the window instants, the matured loops **with the `band` that owes each resolution** (so the owing band's brief carries the debt and its word allocation accounts for it), the concluded-in-window / running / opens-next-week calendar buckets (→ mandatory results-ledger rows, standings, On the Radar lines), and the full `cover_lead_ledger` with the last-4 tally. **On the ledger, the planner's obligation is prose, not avoidance** — it may lead on a rutted family every week if the news warrants it, provided it writes the override reason. Do not brief it as a prohibition, and do not re-add topic-lock: the retired script stayed retired precisely so that this decision lives with the planner rather than with a suppression window.

Run `python scripts/validate-chapter-plan.py`. **If invalid:** re-spawn planner with the validator's error report (max 2 retries). After 2 retries, advance the planner fallback chain (Opus → Sonnet) and try once at the next tier.

**Cost log:** after each planner attempt, run `bash scripts/log-call.sh planner <model> <issue_id> - <retry_count> <outcome>`. Outcome is `validator_fail` if validator rejected and another retry is coming, `ok` if the plan passed, `escalated` if the fallback chain ran out. See § Cost Logging.

### Phase 5 — Writer subagents (format-aware)
Read `chapter-plan.json`. For each chapter, spawn an `Agent` with `subagent_type: "general-purpose"` and `model: "opus"` (fallback `"sonnet"`). In the prompt, pass: the pre-flight.md path, the chapter brief (one chapter object from the plan), the research-bundle.json path, plus the H2 anchor reference for the issue's format inside `references/spec/formats.md`. Writers also read `references/spec/global.md` sections `markup-contracts`, `ground-discipline`, `accent-lockdown`.

**WEEKLY FORMAT (`weekly`) — Transmission band-content (v8.42):** the weekly is now assembled by **`scripts/stitch_weekly.py`**, which generates all chrome from `references/format-skeletons/weekly.json`. **A weekly writer is assigned ONE band and produces only that band's inner content** — no `<section>` wrapper, no band-head, no movement divider, no cover — written to `/tmp/signal-build/chapters/<band_id>.html`. Writers MUST read `references/component-contracts.md` § "Standard Weekly (Transmission)" and use the Transmission component vocabulary (`.letter`, `.figures`, `.digest`, `.lr-title`/`.lr-body`/`.pullquote`/`.plate-img`/`.aside-note`, `.lead`/`.scores`/`.items`, `.with-rail`/`.rail`, `.picks`, `.desk`/`.deskcol`/`.pin`, `.threads`, `.rabbit`, `.radar`, `.closepin`, `.endnumbers`). The canonical worked example of every band is now the **mx golden fixture at `references/golden/weekly-mx/chapters/`** (the densified default; the legacy `references/golden/weekly/chapters/` is retained only for back-compat). Mandatory structural hooks: `data-role="release-radar"` on the Screen & Sound rail (Release Radar is a rail INSIDE Screen & Sound, never its own band); `data-desk-column` on each Desk column (The Desk is ONE department, 1–2 columns, never 3+). The special-edition `.sp-*` vocabulary is **forbidden in weekly issues** — `stitch_weekly.py`'s gate AND `validate-issue.py`'s visual-consistency check both reject it (those classes render unstyled on the light weekly bundle). The cover, tuner "station list", movement dividers, band-heads, colophon and sign-off are NOT written by writers — the stitcher generates them from the plan's `cover` block and per-chapter `nav_coverline`/`nav_freq`/`nav_on` fields. **Images are placed, not optional (2026-07-13 handoff A6):** a band whose chapter brief carries a non-empty `images_needed` MUST emit a **real `<img>`** whose URL comes from the research bundle's `image_candidates`, wrapped in the real-image `.plate-img` form with a caption **and credit** (`.plate-cap` with `.fig`/`.txt`/`.credit`) — the empty `.plate-box` glyph placeholder does not satisfy the brief; **the Long Read must place ≥ 1**. The writer also treats its `target_word_count` as its allocated share of the issue budget: write to it, and if the material genuinely cannot cover the share, flag the planner for more research rather than silently shipping short.

**RESOLUTIONS + RESULTS-OF-RECORD (coverage rebuild, SPEC §3.4/§3.7/§3.11).** A writer whose band owes a matured loop is told so in its brief, and it MUST render the result on an element carrying **`data-resolves-loop="<loop id>"`** — the id verbatim from `state.open_loops[]`, because that attribute is the join key `validate-issue.py` checks at Phase 7.6. The Touchline's `.mx-ledger` is **results-of-record** (`data-role="results-ledger"`), one row per event concluded in-window with **`data-sport` on every row**, and that value is always a **specific sport** — `data-sport="multi_sport"` is forbidden, so a games contributes one row per discipline (SPEC §3.11); forward fixtures belong to On the Radar, not the ledger. Where the band brief carries an unresolved `upcoming` fact, write it as forthcoming (unchanged from v8.29) — but the carry-forward line is now a real promise: it becomes an open loop at publish and the next issue is obliged to resolve it. Do not write a "carried forward" caption for anything the plan has not actually dated; issue #18's "CARRIED FORWARD TO №019 · THE RACE STILL TO RUN" was decoration over a mechanism that did not exist.

**FURNITURE LAYER — ON BY DEFAULT (v8.43, WP-8/8.1).** Every weekly now ships the core furniture layer: the plan sets `issue_meta.design_system: "mx"` (the planner does this by default for weeklies — see `references/format-skeletons/weekly.json` § `furniture_layer`), and writers distribute the five furniture objects + the dial signature across the bands named in `furniture_layer.band_slots`, filling their interiors with `data-mx-event` markers per `references/core-components.md`. The objects: `.mx-ledger` fixtures/results ledger + `.mx-scorecard` standings + `.mx-dial` needle-sweep in The Touchline; `.mx-card--chart` sparkline in The Week in Numbers; `.mx-quote` named-voice objects distributed across Touchline/Screen & Sound/Long Read (Law-9 floor ≥4 distinct named voices); `.mx-ticket` in Do This Week. This is what carries the weekly to its Law-2 density budget (0.8–1.0 ev/screen @1440, no 3+ dead-screen run) — a weekly whose density doesn't change is a FAIL of the upgrade, not a success. Identity is untouchable: no scene-grounds, no display fonts (the three Transmission faces only), no `.sp-*`/event-skin loud components; motion is calm tier1 (furniture only, never running text, reduced-motion honored). LAYOUT RULE (WP-8.1): never strand a short furniture object in a rigid column beside tall body text — The Desk's two departments (Session · Ledger) must both fill, or a short service card floats so text reclaims the measure; verify no blank column at 1440/1024/820/390. The publish gate runs `tools/measure-issue.mjs` on the rendered weekly and hard-fails the density/craft/motion laws (`scripts/check-rendered-metrics.py`). To deliberately produce a legacy (non-furniture) weekly, omit `design_system` — but that is back-compat only, not for new issues.

**NON-HOLIDAY SPECIAL FORMATS (`deep_dive`, `versus`, `rewind`, `season_review`, `starter_kit`, `shortlist`, `next`, `lookahead`):** writers MUST read `references/spec/specials.md` § `cover` → "Component list" for the v8.21 editorial system: persistent `.mast` chrome, `.cover` / `.chapter` / `.chapter-body` structure, baseline flair (`.pullquote`, `.marginalia`, `.bignum`, `.sp-ornament`, `.sp-eyebrow`, `.has-dropcap`), figures (`.fig`, `.image-quote`), per-format flair components for the visual formats (`.vs-tape` / `.vs-pair` / `.vs-verdict`, `.year-band` / `.rewind-cards`, `.rating` / `.scoreboard` / `.milestones`, `.tier-band` / `.pick`). The old `sp-*` vocabulary (`.sp-chapter-gate`, `.sp-spread`, `.sp-pull-break`, `.sp-manifesto`, `.sp-bignum`, `.sp-gallery`, `.sp-diptych`, `.sp-marquee`, `.sp-parallax`, `.sp-wipe`, `.sp-stagger`, `.sp-splash`, `.mast-ticker`, `.sp-format-badge`, signature-moments `.sp-sig-*`, hype `.is-hype`) was retired in v8.21 — those classes are no longer in the CSS bundle and will render unstyled. **HOLIDAY FORMATS ONLY (`countdown`, `field_guide`):** writers read `references/spec/specials.md` § `holiday-identity` for the `.hol-*` component map. Holiday formats retain their motion/identity layer in CSS files `33-` and `36-` through `44-`. Each writer outputs `/tmp/signal-build/chapters/<chapter_id>.html` (chapter-only, no scaffold).

**Cover, navigator, foreword, colophon, footer chapters are FULL writer-agent chapters — not orchestrator-written.** Every chapter in the plan, including the front-matter and back-matter, gets a spawned writer Agent with pre-flight + brief + research bundle. The orchestrator does NOT write chapter content inline by hand. If a chapter is templated (scaffold-derived) it goes in `scaffold_parts_used` and the stitcher concatenates it directly; if it's authored content it goes through Phase 5. Don't mix. The 24 May 2026 weekly shipped with orchestrator-written cover/navigator/foreword/colophon/footer because the planner initially listed them as scaffold parts and the orchestrator then wrote them directly — neither path applied pre-flight or compliance gates. Either fully scaffold (template-only with no per-issue prose) or fully writer-agent (with the full Phase 5 → Phase 7 chain).

- **Parallel mode** (Countdown, Field Guide, Shortlist, Starter Kit, Lookahead, weekly): spawn all writers in one batch — issue every `Agent` call in a single message.
- **Sequential mode** (Deep Dive, Versus, Rewind, Season Review, Next): spawn writers one at a time. After each chapter completes, the next writer reads its predecessor's output to maintain throughline.

**Cost log:** after each writer returns, run `bash scripts/log-call.sh writer <model> <issue_id> <chapter_id> 0 ok`. One call per chapter. See § Cost Logging.

### Phase 6 — Stitch
Run `bash scripts/stitch-issue.sh --plan /tmp/signal-build/chapter-plan.json --out signal_<format>_<date>.html --issue-number <N>`. **For `weekly` (v8.42) the stitcher dispatches to `scripts/stitch_weekly.py`** — the deterministic, skeleton-driven path: it generates all chrome from `references/format-skeletons/weekly.json`, wraps each writer band-content file, injects the weekly-only bundle (`assets/css/weekly/*.css` + `assets/script-weekly.js`), and runs the weekly `.sp-*` gate. Specials keep the concatenation path below. Stitcher concatenates chapters, wraps in scaffold, injects CSS (alphabetical cascade) and JS deterministically. The `--issue-number` arg is required for standard weeklies (it's substituted into the footer `Issue #[N]` placeholder) and should be the value `last_issue_number + 1` from state. For specials, pass `--issue-number ""` (empty) or omit — specials don't carry issue numbers and the footer uses the format/topic header instead. **v8.18.1:** the stitcher now also substitutes `[DATE RANGE]` (computed as a one-week range ending on the issue date for weeklies, or the single date for specials) and `[Date]` (pretty-formatted issue date) placeholders from the head-open and footer templates. Writers don't touch these; the stitcher owns them. **v8.13.3:** for `countdown` and `field_guide` formats, stitch-issue.sh auto-rewrites the `<body>` tag to `<body class="is-special" data-special="<format>">` (the activation that switches on tier 11/12/13/14 CSS + JS), runs a banned-vocabulary grep gate (`sp-chapter-gate`/`sp-spread`/`sp-pull-break`/`sp-marginalia`/`sp-brief`/`sp-dash`/`sp-chapter-chrome`/`unmissables`/`unmissable`) and exits non-zero if any are found, and runs a positive-structure check that fails the stitch if no `.hol-half` is present. Writers cannot accidentally ship a holiday issue without the Holiday Identity activation.

**v8.13.4 fix:** the body-rewrite regex is now anchored to `</head>` (not the first `<body>` in the document). The scaffold `00-head-open.html` contains a documentation comment with an example body tag (`<body class="is-special" data-special="countdown"> (or field-guide).`), and a naive `count=1` regex matches that example FIRST and silently leaves the real `<body>` bare. Anchoring to `</head>` guarantees we rewrite the real DOM tag. If you edit stitch-issue.sh, preserve this anchoring.

**v8.22.5 weekly gate.** Symmetric to the holiday gate: for `weekly` format issues, the stitcher scans chapter bodies for special-edition `.sp-*` vocabulary tokens (`sp-spread`, `sp-marginalia`, `sp-rail`, `sp-margin`, `sp-pullquote-huge`, `sp-brief`, `sp-brief-kicker`, `sp-dash`, `sp-chapter-gate`, `sp-manifesto`, `sp-bignum`, `sp-gallery`, `sp-diptych`) and exits non-zero if any are found. Those classes are scoped to `body.is-special` selectors and render unstyled on a standard weekly. The 24 May 2026 weekly shipped with all of these in its chapter bodies — this gate stops the next one. Action on fail: re-run Phase 5 writers with the weekly-vocabulary brief.

**The cover dateline derives from the window (coverage rebuild, SPEC §3.5).** `[DATE RANGE]` is no longer "a one-week range ending on the issue date" — it is `issue_meta.window` rendered for the reader, so the dateline and the coverage claim are the same object. The consequence is intended and is stated at 0a-window: a Sunday-evening conclusion sits in the *next* dateline, and reaches the reader through the open-loop resolution rather than through a dateline that silently overstates what was knowable. If the stitched dateline and `issue_meta.window` ever disagree, the window wins and the stitcher is the bug.

**v8.22.5 `[YEAR]` substitution.** The stitcher now substitutes `[YEAR]` (in addition to `[Date]`, `[DATE RANGE]`, `[N]`) from the issue's pretty date. `01-masthead.html` uses `[YEAR]` in its right-meta tag; previously the literal shipped and got sed-fixed in Phase 9. Now handled in stitch.

**Plan-level multi-venue flag.** If `issue_meta.multi_venue` is `true` in chapter-plan.json, the stitcher additionally stamps `data-multi-venue="true"` on the rewritten body. This activates tier-9 per-venue scoping for Countdown (and is harmless on Field Guide, which uses the `.hol-half--one`/`--two` structure instead). The planner sets this flag for issues with two named venues; do not set it manually.

### Phase 7 — Per-chapter Gate 1 (during pipeline)
Each chapter has already self-audited via pre-flight.md. Now grep-scan every chapter HTML for the Gate 1 hard-fail patterns from `references/compliance-checklist.md` (1A reader-profile leaks, 1B fabrication markers, 1C staleness, 1E markup contracts, 1F image-caption integrity). Any failure → enter repair flow.

**Topic-lock and theme-clustering — RETIRED (v8.37, W-3).** `check-topic-lock.py` and `check-theme-clustering.py` are **deleted** and no longer run at any phase. Topic-lock's suppression is dropped in favour of **The Threads** (`ongoing_stories` now feeds only the reader-facing continuity recap, not a suppression gate), and theme-clustering's structural cause is removed by the four-movement spine (one Long Read + brisk rounds). "Don't re-run last week's Long Read subject on a holding pattern; no single theme owns the issue" is now **editorial judgement**, not a script. Do not reintroduce either script or its Gate-1 grep. (At Phase 0 the planner no longer needs to recompute `recent_leads`; `lead_history` is not read by any gate.)

**Plain-English spot check — Deep Dive + literary specials (v8.37 narrowed v8.30; folded v8.38, W-4).** The **standalone plain-English random-sample reading pass no longer runs as a weekly gate** — its per-weekly 3-random-paragraph sampling is retired and **folded into the single holistic editorial-quality read (Phase 9.5, gate 3 of the §5 ledger)**. The read below **still runs for the Deep Dive and literary special editions**, where performed prose is the characteristic failure; the trope lists stay as its calibration. For weeklies, hollow connective sentences and hedged answers are judged in the holistic read, not by random sample.

For the Deep Dive / literary-special reading pass, after the Gate 1 grep the orchestrator picks **3 random body paragraphs** from substantive body chapters (skip front/back-matter — cover, navigator, foreword, colophon, footer — and pure-list sections; on a Deep Dive also skip Argument / Keep-Digging) and asks itself, honestly, one question:

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
6. **(coverage rebuild, SPEC §3.7) For every matured open loop from 0a-loops:** confirm the issue actually states the result, and that the element carrying it has `data-resolves-loop="<loop id>"`. This step is the human-judgement counterpart to the two mechanical layers (Phase 3b on the bundle, Phase 7.6 on the HTML) — three chances to notice that last week's Sunday final still has no winner named. **The run date remains the knowability anchor** for every check in this phase; the window's closing instant (`window.to`) is the finer-grained version of the same idea, and where they differ the cut is authoritative.

Fix every FAIL before proceeding to Phase 8. The release-date class of error is the single most-cited fabrication category in reader feedback (Andor S2 framed as current; Tales of the Underworld framed as upcoming when it aired in 2025; Andor S2 end-date wrong by months). This phase is non-skippable.

### Phase 7.6 — Structural + asset validator (mandatory before publish)

Run `python3 scripts/validate-issue.py <stitched-html-path> --format <format>` and, when applicable, add `--multi-venue` for issues with two or more named venues.

**For `weekly` (v8.42)** this gate additionally hard-checks: the four-movement structure via the Transmission `data-*` hooks (all four `data-movement` bands; exactly one `data-role="long-read"`; The Desk = one `data-role="desk"` with 1–2 `data-desk-column`s and no exploded columns; Release Radar as a `data-role="release-radar"` rail inside Screen & Sound, never its own band; ≤13 `data-station` nav entries; Caught Up ≤8 lines); **visual-consistency** (`check_weekly_visual_consistency` — no special/holiday CSS markers or fonts in the injected assets, no `.sp-*` body components, the Transmission `.masthead`/`.issue` not the special dark hero); and a **scaffold-leak** check (`check_scaffold_leak` — no unfilled `[Title …]`/"Pick title" template tokens rendered as body text, handoff §8b).

**Open-loop resolution + coverage checks (coverage rebuild, SPEC §3.7/§3.8/§3.9/§3.11).** These land **inside this existing gate** — gate 2 of the three-gate ledger — not in a new one. Pass the state file and the run date so the validator can compute the matured loops itself:

```bash
python3 scripts/validate-issue.py <stitched-html-path> --format weekly \
  --state /tmp/the-signal/state/signal-state.json --run-date <today>
```

It then hard-fails: a **matured loop** (`status == "open"`, `expected_resolution_date <= run_date`) whose id has no `data-resolves-loop` anywhere in the rendered HTML; a **results ledger** carrying one `data-sport` when ≥2 tracked sports concluded in-window; a **caption whose visible sentence** omits the figure's `data-capture-year` while the surrounding band claims a later year; and the **image shape budgets** (≥3 distinct `data-shows`; at most one `key_art` in Pixel & Byte; **no `key_art` or `portrait` as any band's lead figure, issue-wide**, and `product_shot` as a lead only where the band's subject is the product; ≥1 `diagram|map|chart|artefact` in the Long Read; a Touchline figure captioned as a concluded result must be `event_photo`; no re-use of the previous issue's lead image via `used_image_urls`). The `--state` / `--run-date` naming mirrors the contracted invocation of `validate-research-bundle.py` in SPEC §3.7; the **check** is what the SPEC fixes, so if WP-4's validator exposes different flag names, this line is the bug and not the gate.

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

- No single domain >50% of images (RT-5 hard fail — `single_domain_max_pct`, not retired)
- ≥3 distinct source types from the 5-type menu (`min_distinct_source_types`)
- **≥3 distinct `data-shows` values across the issue** (`min_distinct_shapes`, SPEC §3.8/§3.14), read off the `data-shows` attribute the stitcher emits on every `.plate-img`. An issue with **no** `data-shows` at all fails — unlabelled figures cannot be counted — and a value outside the canonical `shows` enum is a hard fail (a typo'd shape is drift, not a new shape).
- **The Wikimedia caps are RETIRED here too (SPEC §3.14)** — `wikimedia_max_pct` / `wikimedia_max_count` are gone from the lookup file and this script no longer reads them. Domain diversity was never the problem: issue #18 cleared `min_distinct_source_types: 3` comfortably while leading Pixel & Byte on key art. Diversity of *domains* does not fix a boring issue; only different *kinds of picture* do.

Unknown domains (not in the lookup) trigger an advisory rather than a hard fail — extend `references/image-source-types.json` when a new recurring source appears.

**Non-zero exit code = the issue is not shippable.** Identify the over-represented domain, swap entries to under-represented source types (typically by extending research to press kits / government Flickr / archive hosts), update `research-bundle.json`, re-run the affected writer(s), re-stitch. **The orchestrator runs this script directly and reads the exit code** — gate-discipline rule applies.

This gate exists as a downstream catch for what Phase 3b missed — writers omitting some bundle images and skewing the final ratio, or new domains slipping in via writer prose that weren't in the bundle. The upstream validator (Phase 3b) is the primary defence; this is defence in depth.

### Phase 7.75 & 7.8 — REMOVED (v8.38, W-4 — folded into the three-gate ledger)

The standalone **prose-rhythm** gate (`check-prose-rhythm.py`) and the **DOM visual-smoke-test** gate (`visual-smoke-test.py`) are **deleted** and no longer run at any phase. Their intent survives, folded per the §5 gate ledger:

- **Prose-rhythm → the holistic editorial-quality read (Phase 9.5).** "Paragraph walls / no visual break every 2–4 paragraphs" was a proxy for *does this read well on the page?* — a judgement the holistic read makes directly. The read is told to flag any chapter that reads as a wall of text and to add visual breaks in repair. No script.
- **Visual-smoke-test → the markup-contracts gate (`validate-issue.py`).** The image-safety detectors already live in the image-URL chain: **D3** (page-URL-as-image, no image extension) is `validate-issue.py`'s `static_image_url_check`; **D6** (duplicate image URLs) and **D7** (unbundled URLs) are repaired programmatically by `auto-repair-images.py` (Phase 9 round 0) and enforced upstream by `validate-research-bundle.py` + Phase 3a-verify (the bundle is the only authority). The **holiday-chrome DOM checks** (D1 duplicate chrome, D2 un-wrapped venue chapters, D4 orphan holiday elements, D5 empty hero bands) fold into the markup gate: `validate-issue.py`'s holiday-activation + holiday-component checks plus the Gate-1E markup greps in `references/compliance-checklist.md` cover the class, and the stitcher's holiday scaffold override + half-wrap reorganisation prevent D1/D2 at source. Nothing that mattered is lost; one fewer script to run.

### Phase 8 — Stitched-issue Gate (Gate 3)
Cross-chapter checks: no two consecutive sections same component pattern, accent lockdown across chapters, link health, ongoing-story consistency. Plus Gate 2 editorial/visual quality. (Image-source diversity is enforced by Phase 7.7.) Fix any failures.

### Phase 9 — Self-healing repair (v8.13.8 — autonomous, max 3 rounds)

The reader is the **audience**, not a triage layer. Phase 9 must resolve gate failures itself; if it cannot, Phase 10 ships the best-effort issue anyway. Last week's issue stays accessible via `index.html` — a less-than-perfect new issue is preferable to no new issue.

**Round 0 — image defects auto-repair first (programmatic, no subagent).**
Run `python3 scripts/auto-repair-images.py <stitched-html> /tmp/signal-build/research-bundle.json`. This script rotates unused bundle URLs through every defective image slot in the rendered DOM — **duplicate URLs, unbundled URLs, and page-URLs-used-as-image** (it detects these itself; it is self-contained and does not depend on the deleted visual-smoke-test). It is pure Python — no subagent dependency. Exits 0 if all defects fixed, 1 if some are unfixable (bundle exhausted). This is the surviving home of the old D3/D6/D7 image-safety intent (part of the image-URL verification chain gate, §5).

Why this runs first: image defects are mechanically fixable from the existing bundle, and the bundle is the only authority writers may use anyway. Running this BEFORE spawning expensive repair agents avoids wasting writer-round budget on what's really an asset-substitution problem.

After auto-repair runs, re-stitch is **not** needed (the script edits the stitched HTML in place); just re-run Phase 7.5/7.6/7.7 gates.

**Rounds 1–3 — targeted subagent repair for content defects.**
If gates STILL fail after auto-repair (or fail in non-image ways — release-date errors, ground discipline, accent leaks, banned phrases), spawn ONE repair `Agent` (`subagent_type: "general-purpose"`, `model: "opus"`, fallback `"sonnet"`) per round. Pass the chapter HTML + the specific failure report + the bundle. Repair re-writes the chapter; re-stitch; re-run auto-repair-images.py; re-run gates. Cost log: `bash scripts/log-call.sh repair <model> <issue_id> <chapter_id> <round> <outcome>` (record the model actually used — `opus`, or `sonnet` if the fallback fired).

**After 3 rounds — PROCEED to Phase 10 regardless of remaining gate failures.** Do NOT escalate to the reader. The pipeline publishes the best-effort issue. The orchestrator records the remaining defects in the closing summary; the CI workflow files a tracking GitHub issue for visibility (informational, not blocking).

**Bundle-exhaustion case.** If `auto-repair-images.py` reports "bundle exhausted" (cannot substitute all defects), one of the round 1–3 repairs should re-spawn the **researcher** with an inline "find N more verified image URLs for venue X" brief, append the new candidates to the bundle, then re-run auto-repair. Only fall back to "ship with duplicates" after this researcher-extension also failed within the 3-round budget.

**Cost log:** after each repair attempt, run `bash scripts/log-call.sh repair <model> <issue_id> <chapter_id> <round_number> <outcome>`. Outcome is `gate_fail` if the gate still fails and another round is coming, `ok` if the chapter now passes, `escalated` if all 3 rounds exhausted. See § Cost Logging.

### Phase 9.5 — The holistic editorial-quality read (the THIRD ship-quality gate, before publish)

This is **gate 3 of 3** in the ledger (§5 of `docs/signal-final-recommendations-2026-07.md`) and the pipeline's one **quality** judgement. Every gate before it (Phases 3b, 7–8) measures *compliance* — did the issue break a rule? This one asks the only question that matters, the north-star of the whole magazine:

> **Did this issue tell him what the week added up to, and give him one thing to do?**

It **replaces the ~8 retired compliance scripts** and absorbs their intent into a single read: the old prose-rhythm (does it read as a wall of text?), theme-clustering (does one topic own the issue?), topic-lock (is this just last week's story again?), plain-English (is the prose performed rather than direct?), and the observational scorer's craft dimensions all become facets of this one judgement — not separate scripts. It reads the **post-repair artifact** — the exact HTML about to ship.

**Spawn a dedicated reader `Agent`** (`subagent_type: "general-purpose"`, `model: "opus"`, fallback `"sonnet"`). It is NOT the orchestrator and NOT any writer that worked on this issue — a producer grading its own work drifts generous. In the prompt, pass the path to the final stitched HTML and tell it to read `references/quality-rubric.md` (the full rubric, with its archive-anchored examples) and nothing else. It makes the one holistic judgement above, and to make it concrete it also scores the eight craft dimensions (voice, information density, length adequacy, structure, opening, throughline, novelty, visual richness — keys `voice, density, length, structure, opening, throughline, novelty, visual`; `throughline` is `null` for parallel formats; `length` checks the format's word band and per-band `target_words` shares, `visual` checks cover + image count vs the ~2/1,000-words norm + captions/credits + visual rhythm) plus, explicitly, **the two north-star sub-questions**: *did the issue tell him what the week added up to (a clear throughline / synthesis, not a re-list)?* and *did it give him one thing to do (a real, named, do-it-this-week action landing in Do This Week / a Desk pin)?* It also asks, as an added guiding question, **the structural integrity check**: *are all four movement bands present (THE OPEN / THE LONG READ / THE ROUNDS / THE CLOSE), and is The Desk a single nested department running 1–2 columns (not exploded into standalone sections)?* (The markup gate now hard-checks these, but the holistic read judges intent, not just markup.) It returns ONE JSON object exactly as specified in the rubric's "The JSON the scorer emits" section, including the mandatory `weakest` dimension and one-sentence `note`. If either north-star sub-question is a clear NO, the read flags it as a repair target.

The orchestrator then runs:
```bash
bash scripts/log-quality.sh '<reader-json>'
```
which injects `ts`, computes `overall`, appends one line to `state/quality-log.jsonl`, and regenerates the public `quality.html` page. Set `writer_model` to the model the writers actually ran on this issue and `scorer_model` to the reader's model id.

**Blocking-ish, not blocking (the "made to matter" policy — agreed verbatim with `references/quality-rubric.md`).** The holistic read can trigger ONE targeted repair round when any dimension scores below its repair threshold (a 1 or 2) or either north-star sub-question is a clear NO, provided budget remains in the Phase 9 3-round window — but it never blocks or reverts a publish outright: once the repair budget is spent, Phase 10's cardinal rule (always publish) wins, and the residual is recorded in the quality log. The reader gets a new issue every Sunday. The read exists to make quality **act**, not just observe: over a dozen issues the log still answers which dimension is chronically weakest (i.e. where the *spec* should change, not the model). Review with `bash scripts/quality-summary.sh`. See § Editorial Quality below.

### Phase 10 — Deliver + publish (always publishes; CI is post-hoc)

**Cardinal rule (v8.13.8):** Phase 10 ALWAYS publishes. Phase 9 has already done up to 3 rounds of self-healing repair; whatever survived is what ships. The reader gets a new issue every Sunday — degraded if necessary, broken-imperfect rather than missing. Last week's issue remains accessible at `/issues/<previous-filename>.html` via `index.html`, so the live site never lacks content even if this week's has minor defects.

**Mechanical publish receipt (v8.42 — reliability design Pillar F).** Before committing the issue, run the publish gate — it is a *script*, not a prompt rule, so it cannot be bypassed the way the Rewind was (shipped despite a failing image gate, handoff §8c):

```bash
bash scripts/publish-gate.sh <stitched-html> --format <fmt> [--issue-id <id>]
```

It re-runs the ship gates on the final artifact, writes `build-receipt.json` (each gate + exit code + verdict), and exits non-zero unless every hard gate is green. **Publish policy (reconciles the cardinal rule with "quality is paramount", per `docs/weekly-reliability-rebuild-design-2026-07.md` §6):** a **green** receipt → publish. A **red** receipt after the Phase 9 repair budget is spent → if the failures are *hard-safety* (broken markup/structure, failed visual-consistency, leaked scaffold, broken images) **HOLD and notify the owner** (better silent than broken); if only a *soft* residual remains (all hard gates green, a minor quality-read note) **publish on time** and record the residual in the build log only. Never make the reader the editor. For the weekly, `scripts/verify-weekly-golden.sh` is the pre-Sunday regression: run it after ANY change to `stitch_weekly.py`, `weekly.json`, the weekly CSS, or the weekly gates.

**Stage the final HTML** to scratch first. Filename: `signal_weekly_YYYY-MM-DD.html` for standard weeklies, `signal_<format>_YYYY-MM-DD.html` for specials (e.g. `signal_countdown_2026-06-07.html`). The scratch copy is `/tmp/signal-build/<filename>`; the durable copy lives in the repo (step 2 below).

**Update state file at `/tmp/the-signal/state/signal-state.json`** per the State Tracking section: increment `last_issue_number` (standard weekly only), update `last_issue_date`, `last_issue_format`, `section_topics_recently`, rotating `last_appeared` fields, ongoing-stories status, training-phase if a block boundary crossed, `recent_facts`, `recent_next_week_themes`. For specials: also update `last_special_date`, `last_special_format`, `consecutive_specials_count`, and append to `recent_special_formats` (then trim to last 6).

**Coverage continuity writes — MANDATORY, and the reason the whole mechanism works (coverage rebuild, SPEC §3.5).** Phase 0 can only open a window where the last one closed if this step actually happens. Write all of these before staging:

1. **`research_cut_at` ← the measured instant** from `/tmp/signal-build/window.json` (`window.to`), **overwriting** whatever is there. Not "now at publish time", not a rounded value, not the seeded literal — the instant research stopped, stamped at Phase 3a-verify. **Until this write happens the coverage fix is inert**: the window cannot open where the last one closed, and a day can again be inside a covered range while its results were unknowable. The seeded value (`2026-07-26T02:10:00Z`) is the SPEC literal, which the repo could bound but not confirm; the first real run replaces it.
2. **`open_loops[]` — three operations, in this order.**
   - **Resolve:** every matured loop the issue reported → `status: "resolved"`, `resolution` = a one-line statement of the result **plus its `source_url`**.
   - **Drop:** every matured loop the issue did **not** report → `status: "dropped"`, `resolution` naming why (postponed / abandoned / not reportable / missed). A dropped loop is the honest record of a miss and no longer matures; deleting it quietly is the defect. Loops whose `expected_resolution_date` is still in the future stay `open`, untouched.
   - **Append:** one new loop per `status:"upcoming"` fact the issue carried — `id` = `loop_<expected_resolution_date>_<slug>`, `claim` = the fact's claim, `expected_resolution_date` = the fact's `date`, `band` = the `chapter_id` that carried it, `issue_opened` = this issue number, `status: "open"`, `resolution: null`. Keep an `id` stable once written: it is the foreign key joining state ↔ `facts[].resolves_loop` ↔ `data-resolves-loop`, not a label.
3. **`cover_lead_ledger[]` ← prepend one entry, then truncate to 12** (newest first). Standard weeklies only — specials do not lead a weekly cover and are not numbered. `{issue, date, topic_family, one_line, led_on}`, where **`topic_family` is COPIED VERBATIM from `issue_meta.cover_lead_topic_family`** and `led_on` is `issue_meta.cover_leads_on` verbatim.

   **Copied — not re-derived from the rendered cover, and not inferred from the lead piece.** This is the one place in the coverage wiring where a plausible-looking shortcut produces a *green no-op*, so it is worth stating the mechanism. The rut rule (SPEC §3.6) **intersects** the plan's cover-lead family against the families in `state.cover_lead_ledger`. If the two sides are produced by different routes — the validator resolving one from the plan, the orchestrator naming the other by reading the cover at publish — they can disagree on any week where a story has two defensible families (`uk_politics` vs `economy_markets`; `olympics` vs `football`). When they disagree the intersection is empty, so the rule finds no rut, **passes, and has checked nothing**. That is worse than an absent check, because a green result reads as coverage. Copying the value makes both sides carry the same family *by construction* rather than by coincidence, which is why WP-1 added the field: before it existed, no plan field carried the family at all (`cover_leads_on` says news-vs-long_read only), and `validate-chapter-plan.py` had to resolve it — explicit field first, else the families of the plan's `role: "lead"` pieces, else it can only warn and skip. The field is now **weekly-required and enum-checked** (an omitted or out-of-enum family hard-fails the plan), and that resolution chain survives only as the compatibility path for plans written before it existed.

   The vocabulary is the **closed enumeration in `references/chapter-plan-schema.md` § Topic Family Enumeration** (one vocabulary in the system — the plan, the ledger and the validator all read that list; never a parallel set). Because the value is copied, the enumeration check `validate-chapter-plan.py` already ran at Phase 4 is also the ledger's guarantee: an unrecognised family cannot reach state without failing the plan first. If a cover lead genuinely has no family in the enumeration, **do not mis-file it** — say so in the closing summary and treat the gap as a spec amendment (this is how issue #8's Instructure/Canvas breach fell out of the ledger before `cyber_privacy` was added), because a mis-filed row silently narrows the rut rule's input just as surely as a mismatched one empties its intersection.
4. **`sports_calendar[]` — prune and extend, never rewrite from memory.** Drop entries whose `end` is now in the past. Append events that 0a-calendar **confirmed against a source this run** (`needs_verification: false`, since confirmation happened at the moment of adding); anything unconfirmed is not appended. Entries still marked `needs_verification: true` keep that flag until a run verifies them.
5. **`used_image_urls`** is **not** written here — it is written at step 1a below by `mirror-images.py`, which owns the url→hash mapping and the asset manifest. Because that runs *after* this state write, re-read `state/signal-state.json` from disk when building the push list at step 4, or the mirror's update is clobbered.

`interest_depth` is **owner-set and never written by the pipeline.** If a run wants a depth for a sport with no key, it says so in the closing summary and leaves the key absent — an absent key means *cover on news value* (see 0a-calendar), so inventing one to "tidy up" can silently switch a sport off.

**Publish to GitHub Pages.** Repository: `stevenmcdowell89-hash/the-signal`. Live site: https://stevenmcdowell89-hash.github.io/the-signal/. The repo was already cloned in Phase 0a; do not re-clone.

1. Copy the issue HTML into `/tmp/the-signal/issues/<filename>.html`.
1a. **Mirror images + generate cover** (offline-PWA + archive thumbnail). Run `bash scripts/post-publish.sh issues/<filename>.html` from the repo root. The script (a) downloads every external image referenced by the new issue into `/assets/cached/<hash>.<ext>` and rewrites the issue HTML to reference the local copies, and (b) extracts a cover thumbnail at `/assets/covers/<slug>.jpg` for the archive page. Idempotent. Failed image downloads leave the original URL intact so the issue still works online. Add any new files under `/assets/cached/` and `/assets/covers/` to the publish push list. **This step also owns two provenance records (coverage rebuild, SPEC §3.9/§3.10):** `mirror-images.py` writes `assets/cached/manifest.json` (url + licence + `shows` + `capture_year` per hash — provenance that used to be discarded, so a caption's claim could not be audited after publish) and updates **`state.used_image_urls`** (`{issues[], led[]}` per hash, the key that lets Phase 7.6 refuse to lead twice on the same image); `extract-covers.py` **refuses** to crop a source whose `licence.allows_derivatives` is `false` and exits non-zero naming the file and licence. Both `assets/cached/manifest.json` and the re-read `state/signal-state.json` go in the push list. The PWA snippet and reading-progress tracker are already baked into `template-parts/` so no per-issue injection is needed.
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
   - Call `mcp__github__push_files` with `owner: "stevenmcdowell89-hash"`, `repo: "the-signal"`, `branch: "main"`, the commit `message` (see below), and `files` listing every changed path with its contents read from disk. Standard-run files: `issues/<filename>.html`, `index.html`, `state/signal-state.json` (**re-read from disk after step 1a**, so the mirror's `used_image_urls` update is not clobbered by the in-memory copy from the earlier state write), `quality.html`, `state/quality-log.jsonl`, `assets/cached/manifest.json`. Plus the cost log if it lives in the repo (`state/cost-log.jsonl`).
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

**How it works.** At Phase 9.5 a dedicated scorer agent (never the orchestrator, never a writer on this issue) scores the post-repair artifact against `references/quality-rubric.md` — eight 1–5 dimensions (voice, density, length, structure, opening, throughline, novelty, visual) anchored to real archive examples, plus a mandatory `weakest` dimension and one-line `note`. The orchestrator pipes the scorer's JSON to `bash scripts/log-quality.sh`, which computes `overall`, appends to `state/quality-log.jsonl`, and regenerates `quality.html`.

**Where it lives + is visible.**
- `state/quality-log.jsonl` — append-only log, committed to the repo alongside `cost-log.jsonl`. Override path via `SIGNAL_QUALITY_LOG`.
- `quality.html` — a static, baked page at the repo root, served on the live site and linked from `index.html` ("Editorial quality →"). It can't read `state/` at runtime (`.assetsignore` excludes it), so the page is regenerated from the log at publish time, same pattern as `index.html`. This is the reader-facing view — a readable table of every scored issue.
- `bash scripts/quality-summary.sh [--since YYYY-MM-DD]` — terminal view.

**Why `writer_model` is stamped on every row.** This is the payoff. The model-selection policy (see § Model Selection) was rewritten on the principle that we can't *prove* a cheaper writer hurts quality because nothing measured it. This log is that missing instrument: once issues written by different models are scored, `quality-summary.sh` shows average overall *by writer model* — turning the model-tier question from a judgment call into an evidence-based one. Re-run that comparison when the next model ships rather than re-arguing it.

**The honest caveats (don't oversell this).** A sibling-model scorer removes the producer's bias, not all bias; the scorer model is itself part of the instrument (a score shift can be the magazine changing or the grader changing — hence `scorer_model` on every row); and the only thing that keeps it honest long-term is a ~monthly **human anchor** score (`scorer_model: "human"`) to detect drift. It is a trend instrument, not a verdict on any one issue. Scoring can trigger one targeted repair round within the Phase 9 budget (see Phase 9.5) — but it never blocks or reverts a publish outright.

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
  "recent_special_formats": [],

  "research_cut_at": "2026-07-26T02:10:00Z",
  "open_loops": [
    { "id": "loop_2026-07-19_wc-final", "claim": "World Cup final, Spain v Argentina, MetLife",
      "expected_resolution_date": "2026-07-19", "band": "touchline", "issue_opened": 17,
      "status": "open", "resolution": null }
  ],
  "cover_lead_ledger": [
    { "issue": 18, "date": "2026-07-26", "topic_family": "uk_politics",
      "one_line": "Burnham's first ordinary week", "led_on": "news" }
  ],
  "sports_calendar": [
    { "event": "The Open Championship", "sport": "golf", "start": "2026-07-16", "end": "2026-07-19",
      "importance": 1, "reader_relevant": true, "needs_verification": true }
  ],
  "used_image_urls": { "<sha256(url)[:12]>": { "issues": [17, 18], "led": [18] } },
  "interest_depth": { "motorsport": "results_only", "football": "full", "golf": "majors_only" }
}
```

### Coverage continuity (the six keys the coverage rebuild added)

`references/spec/data-contracts.md` § State is the field-by-field contract — producer, consumer and semantics for each. What matters at *this* level is which phase touches which key, so the whole loop is auditable in one table:

| Key | Read by | Written by | Failure mode if the write is skipped |
|---|---|---|---|
| `research_cut_at` | 0a-window (as `window.from`) | Phase 10, step "Coverage continuity" — the instant stamped at 3a-verify | The window cannot open where the last one closed. A day is "covered" while its results were unknowable. **This is the write that makes the fix real.** |
| `open_loops[]` | 0a-loops; Phase 3b (`--state`); Phase 7.6 | Phase 10 — resolve / drop / append | `upcoming` facts are gate-checked and abandoned. The more carefully the pipeline refuses to guess a Sunday result, the more reliably it vanishes. |
| `cover_lead_ledger[]` | 0a-ledger → planner; `validate-chapter-plan.py` | Phase 10 — prepend, keep 12 | The planner sees one week of lead history and cannot see a rut. |
| `sports_calendar[]` | 0a-calendar (verify, then bucket) | Phase 10 — prune ended, append confirmed | A Sunday-concluding major is on nobody's list before the bundle happens to mention it. |
| `used_image_urls` | Phase 7.6 cross-issue budget | Phase 10 step 1a (`mirror-images.py`) | The same image can lead two issues running. |
| `interest_depth` | 0a-calendar, the researcher/planner brief, the daily's feed weighting | **nobody — owner-set** | An absent key read as `off` re-creates the invisible-sport defect. |

**`cover_lead_ledger` is not `lead_history`, and neither is a suppression gate.** The distinction is the one thing to get right here:

- **`ongoing_stories[].lead_history`** is a *story-thread* record. Since v8.37 it is read by no gate, it does not reconcile with the rendered covers (Burnham's `2026-05-31` matches no weekly at all), and it stays exactly as it is — kept for reference, appended optionally.
- **`cover_lead_ledger`** is a *cover-lead-of-record* record — one row per rendered weekly cover, but each row's `topic_family` **copied from that issue's `issue_meta.cover_lead_topic_family`**, never re-read off the cover at publish (Phase 10 item 3 explains why: two routes to the same value can disagree, and a disagreement makes the rut rule pass while checking nothing). The seeded rows #18→#9 were necessarily read off the rendered covers because those issues shipped before the field existed; every row from #19 on is copied. Read at 0a-ledger and by `validate-chapter-plan.py`. It gives the planner nine-plus weeks of view where `last_cover_lead` gave one, which is how UK politics led 6 of 9 covers unnoticed (defect C).
- **Neither restores topic-lock.** `check-topic-lock.py` is deleted, stays deleted, and SPEC §1 forbids reintroducing it or any suppression gate. The rut rule cannot stop a lead; its entire power is to require **≥80 characters of written justification** when a family has led `news` in ≥3 of the last 4 covers. If a future reader finds themselves adding a rule that *prevents* a lead, that is the retired gate coming back under a new name.

**`recent_facts`** — array of short tags (max 12) for the closing colophon "A Fact". Before writing each issue, read this list and pick a fact whose topic, era, and angle don't overlap with any of the last 12. After writing, append the new tag and trim to last 12. Example tags: `"Anglo-Zanzibar war"`, `"shortest filibuster"`, `"Roman calendar reform"`.

**`recent_next_week_themes`** — array of short tags (max 4) for the closing "Next Week" line. Before writing, read this list and avoid repeating phrasing patterns. After writing, append and trim to last 4.

**`recent_special_formats`** — array of recent specials (max 6 entries) tracking which P3 rotation formats have been used. Each entry: `{ "date": "YYYY-MM-DD", "format": "versus", "topic": "Sanguli vs Clodia" }`. Used by Phase 0e to pick the next P3 format — prefer formats not in the last 6. Append after every special edition (P1, P2, or P3 trigger), then trim to last 6. P1 specials (Field Guide, Countdown, Rewind, Season Review) are recorded but don't influence P3 rotation — they're calendar-driven, not rotation-driven; P3 picks among the rotation-eligible formats (Guide — beginner or category mode, Versus, Deep Dive; the folded Shortlist/Starter Kit and the retired Blueprint are no longer separate picks, v8.39, S4).

**`deep_dive_backlog`** (Deep Dive topic queue — no separate schedule as of v8.39, S5). `deep_dive_schedule` is **retired**: Deep Dive no longer runs on its own quarterly timer. It fires through the ordinary P2/P3 stack (a detected major launch, or a dry-spell editorial pick) or on manual request — the same path every other special uses. The **backlog is kept** as the topic queue; only the timer is gone.

- `deep_dive_backlog`: array of topic entries. Each entry: `{ topic, scope, added, priority, expanded_scope?, expanded_scope_rationale?, needs_sharpening? }`. `topic` is short ("The rise and fall of Napoleon"). `scope` is a 2-4 sentence brief describing what the Deep Dive should cover, what interpretive frames to surface, and what visual taxonomy is mandatory for this subject. `expanded_scope: true` raises the word ceiling per the spec's flex rule. `needs_sharpening: true` marks entries that are too vague to commission and must be resolved before an editor picks them — skip those and try the next.
- **When a P3 (or P2) slot lands on Deep Dive**, draw the topic from the top non-`needs_sharpening` backlog entry, honouring `priority`. If every entry is `needs_sharpening`, pick a different P3 format instead of forcing a vague Deep Dive.
- `deep_dive_schedule` (RETIRED): any residual `{ cadence_weeks, next_due, last_fired, ... }` object left in a state file is now inert — nothing reads it. It can be deleted on the next state write.

Manual Deep Dives ("Run a Deep Dive on [topic]") are always available.

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
   - `ongoing_stories` — update each tracked story's situation and add/drop stories as needed; **this is now The Threads' data source** (the reader-facing continuity recap, § The Threads) and the Colophon "Next Week" note. Keep each entry's short "where it stands now" recap current so The Threads reads well. **v8.37 (W-3):** the topic-lock suppression role is retired — `lead_history` / `recent_leads` / `weeks_since_last_lead` / `last_development` are **no longer read by any gate** (`check-topic-lock.py` is deleted). You may keep `lead_history` for reference, but appending it is no longer mandatory and nothing enforces it. Deciding this week's Long Read subject (don't re-run last week's on a holding pattern) is editorial judgement now, informed by The Threads, not a cap. **The cover-lead decision is a separate record** — `cover_lead_ledger`, below — and it is a planner input plus a written justification, not a revival of the suppression role (see § Coverage continuity).
   - `training_phase` — update if the current date has crossed a block boundary (Block 1 ends May 3, Block 2 ends June 30, post-holiday starts July)
   - **`research_cut_at`** (always, weekly and special) — overwrite with the measured instant from `/tmp/signal-build/window.json`. Skipping this is the one omission that silently disables the coverage window.
   - **`open_loops`** (always) — resolve the matured loops the issue reported, drop the ones it didn't (with a reason), append one per `status:"upcoming"` fact carried.
   - **`cover_lead_ledger`** (standard weekly only) — prepend `{issue, date, topic_family, one_line, led_on}`, trim to last 12. `topic_family` is **copied from `issue_meta.cover_lead_topic_family`** and `led_on` from `issue_meta.cover_leads_on`; re-deriving either from the rendered cover is what empties the rut rule's intersection.
   - **`sports_calendar`** (always) — prune entries whose `end` has passed; append only events confirmed against a source this run.
   - **`used_image_urls`** — written by `mirror-images.py` at Phase 10 step 1a, not by this list. Re-read state from disk before pushing.
   - **`interest_depth`** — never written by the pipeline. Owner-set; an absent key means *unset*, not `off`.

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
| `15a-service-continuity.css` | **v8.36 (W-2)** — The Desk `.do-this-week` pin (section-accent, closes every Desk column), `.the-threads`/`.thread` continuity list, `.week-in-numbers` personal strip. JS-off renderable. |
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
| `13a-the-desk.html` | **v8.36** — The Desk service department: the four service columns (The Session / The Ledger / The Itinerary / The Toolkit), each closing on a `.do-this-week` pin. Render 1–2 per issue |
| `14-session.html` | the session (also a Desk column — see `13a-the-desk.html`) |
| `15-history.html` | this week in history |
| `15a-the-threads.html` | **v8.36** — The Threads continuity engine (`ongoing_stories` "previously on…" + life-threads). Placed before On the Radar |
| `15b-week-in-numbers.html` | **v8.36** — The Week in Numbers personal stat strip. Placed near the top (after The Letter) |
| `16-on-the-radar.html` | on the radar |
| `17-colophon.html` | end-of-issue colophon |
| `18-footer.html` | footer |
| `19-closing.html` | `.mag` close, back-to-top, `<!-- INJECT:JS -->`, `</body></html>` |

**Pipeline scripts and references** (v8.11.0+):

| Path | Purpose |
|---|---|
| `references/pre-flight.md` | Every writer subagent reads this before drafting. 12 regression triggers + canonical markup snippets + self-audit checklist. The primary defence — most failures are caught upstream here. |
| `references/chapter-plan-schema.md` | JSON Schema for the planner's output. Closed vocabulary for format and chapter_type. Documents the contract between planner and writers. |
| `references/spec/data-contracts.md` | **The machine records that cross phase boundaries** (coverage rebuild): the research bundle's `shows` / `capture_year` / `licence` / `resolves_loop` additions, the `shows` enum with the definitions the checks depend on, and all six state additions with producer + consumer per field. Read at Phase 0 alongside state; it is the contract behind § Coverage continuity. |
| `references/spec/` | Sliced editorial-spec.md for tight per-role context. Five flat files: `global.md`, `weekly.md`, `specials.md`, `formats.md`, `triggers.md`. Each former subdir-file is now an H2 (`## <anchor>`) inside the consolidated file. `README.md` documents reading order per role and the H2 anchor index. |
| `scripts/slice-spec.sh` | Deterministic slicer. Re-runs idempotently after editorial-spec.md edits to refresh the sliced spec. |
| `scripts/validate-chapter-plan.py` | Mandatory gate between Phase 4 and Phase 5. Catches malformed plans, missing fields, broken cross-refs. |
| `scripts/stitch-issue.sh` | Deterministic chapter concatenation + scaffold wrap + CSS/JS inject. Replaces inject-assets.sh in the pipeline. |
| `scripts/inject-assets.sh` | Legacy single-file CSS/JS injector. Kept for ad-hoc edits outside the pipeline. |
| `scripts/check-release-dates.sh` | Phase 7.5 release-date sanity check. Surfaces every claim of a date/relative-time near a media name in the stitched HTML, plus any locked-register entry. Output written to `/tmp/signal-date-claims.txt`. The agent walks the report and verifies each claim against the locked register or a web search before publish. |
| `scripts/validate-issue.py` | **Phase 7.6 mandatory post-stitch gate — carries TWO of the three ship-quality gates: the image-URL verification chain and the markup contracts.** Verifies structural well-formedness, banned-placeholder absence, the "Return to The Signal" back-link, holiday activation (body class + `data-special` + `.hol-masthead`/`.hol-cover`/`.hol-half` presence), **non-holiday special component variety** (per-format floor of distinct presentational components — stops a plain-page special), the **Issue-in-Numbers stats assertion** (v8.38 — stats aren't all identical / aren't just the issue number; the 13/13/13/13 defect), the static image-URL extension check, and image-URL reachability (HEAD requests in parallel). Exits non-zero on any failure. The orchestrator runs this directly and reads the exit code — subagent self-reports of "passed" are not acceptable. See Phase 7.6 in the workflow above. |
| `scripts/validate-research-bundle.py` | **Phase 3b mandatory upstream gate.** Reads `research-bundle.json` and enforces image_candidates rules: real URLs not keywords, ≥3 source types represented, RT-5 single-domain ≤50%, **≥3 distinct `shows` values (`min_distinct_shapes`)**, ambiguous-domain `source_type` annotation, plus the `shows`/`capture_year`/`licence` records and the open-loop resolution check (`--state`). **The Wikimedia ceilings are retired (SPEC §3.14) and this script no longer reads them** — the floor on distinct shapes replaced them. Blocks the planner from spawning until research is corrected — the strongest prevention against the URL-fabrication / mono-sourcing chain. Uses `references/image-source-types.json`. |
| `scripts/check-image-diversity.sh` | **Phase 7.7 mandatory post-stitch gate.** Classifies every image domain in the stitched HTML via the lookup table and enforces the same diversity rules as Phase 3b. Defence in depth — catches writers omitting bundle images and skewing the final ratio, or new domains slipping in. Sandbox-aware: unknown domains warn rather than fail. |
| `references/image-source-types.json` | Lookup table mapping domain → source type (press_kit / government / archive / news_cdn / wikimedia), **the canonical `shows` enum** (11 values — what an image *depicts*, orthogonal to its domain), and the live `thresholds`: `single_domain_max_pct: 50`, `min_distinct_source_types: 3`, `min_distinct_shapes: 3`, `min_unique_candidates: 16`, `max_uses_per_url: 1`. Edit when a new recurring source appears in research. Phase 3b, 7.6 and 7.7 all read this file, and it is the **one** home of the `shows` enum — a shape value living in a script but not in this file is the taxonomy drifting again. `retired_thresholds` records the withdrawn `wikimedia_max_pct` / `wikimedia_max_count` with the reason; it is history, not a live read. |
| `scripts/log-call.sh` | Fire-and-forget logger — main loop calls this after each subagent returns. Appends one JSON line to the cost log (default `/tmp/the-signal/state/cost-log.jsonl`, override via `SIGNAL_COST_LOG`). Errors are silent so logging never blocks the pipeline. |
| `scripts/auto-repair-images.py` | **Phase 9 round-0 programmatic repair.** Takes stitched HTML + research-bundle.json, identifies image defects (duplicates D6, unbundled D7, page-URL-as-image D3) and substitutes unused bundle URLs in-place. Pure Python — no subagent dependency. Exits 0 on clean / fully-repaired, 1 on partial (bundle exhausted). The orchestrator's Phase 9 loop absorbs partial failures via the 3-round budget; after 3, Phase 10 ships anyway. |
| `scripts/cost-summary.sh` | Reads the cost log and prints a per-issue and aggregate breakdown (calls per role, model usage, retry rate, validator/gate failures, escalations). Run after a few issues to validate the model fallback chains. |
| `references/quality-rubric.md` | The editorial-quality rubric scored at Phase 9.5: eight 1–5 dimensions (voice, density, length, structure, opening, throughline, novelty, visual) anchored to real archive examples, plus the scorer's JSON contract and the honest caveats. The pipeline's only quality signal — everything else is compliance. |
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
