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

The pipeline: Phase 0 (decide format) → Phase 3 (researcher subagent) → Phase 4 (planner subagent + validator) → Phase 5 (writer subagents, parallel or sequential) → Phase 6 (stitch) → Phase 7 (per-chapter Gate 1) → Phase 7.5 (release-date check) → Phase 8 (stitched-issue Gate) → Phase 9 (repair if needed) → Phase 10 (deliver + publish).

There is NO separate "lightweight" path. Standard weeklies run the full pipeline same as specials. Build dir is `/tmp/signal-build/`, cleared at the start of every run.

> **Environment note.** Claude Code on the web runs in an ephemeral container that is reclaimed when the session ends. The repository at `stevenmcdowell89-hash/the-signal` is the only durable store — state, issues, and the cost log all live there. Per-session paths like `/tmp/signal-build/` are scratch only.

---

STUB - actual content is in /tmp/the-signal/.claude/skills/the-signal/SKILL.md - need direct file streaming.
