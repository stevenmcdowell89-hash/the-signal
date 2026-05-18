# Operations

How to run and schedule The Signal.

## Scheduled weekly generation (Claude Code on the Web)

The Sunday issue can be generated automatically by a Claude Code on the Web
trigger. Once configured in the dashboard, every Sunday at the chosen time
a fresh session fires, runs the pipeline, and publishes to GitHub
(which Cloudflare auto-deploys).

### One-time setup

1. **Verify the SessionStart hook is on `main`.** This repo has
   `.claude/hooks/session-start.sh` registered in `.claude/settings.json`.
   It installs the Python packages the pipeline needs (Pillow, requests).
   No action needed beyond keeping these files in the repo.

2. **In the Claude Code web dashboard:**
   - Source: this repo (`stevenmcdowell89-hash/the-signal`), branch `main`
   - Schedule: a Sunday morning cron — e.g. `0 6 * * 0` for 6am UTC
   - Network policy: same as your manual sessions (needs egress for
     research + Cloudflare assets)
   - Prompt: paste the [canonical prompt below](#canonical-trigger-prompt) verbatim

3. **Run it manually once from the trigger dashboard before relying on
   the schedule.** Confirms the unattended flow works end-to-end.

### Canonical trigger prompt

```
Run the weekly Signal pipeline now.

Use existing state in state/signal-state.json to decide format. The skill's
Phase 0 logic will pick a special edition automatically if a calendar
condition is met (Field Guide ~6 weeks before a trip, Countdown 2-3 weeks
before, Season Review when a league ends, Rewind half-year / year-end);
otherwise produce a standard weekly.

Run unattended. Do NOT ask clarifying questions. Apply judgement on
ambiguous decisions and proceed. Phase 9 self-healing handles repair
internally; Phase 10 always publishes the best-effort issue even if
gates remain red — that's by design.

On completion, push the new issue + updated state to main via the
GitHub MCP server. Cloudflare will auto-deploy. Report the published
URL plus any unresolved gate failures in your closing summary.
```

### What happens when the trigger fires

1. Container spins up; SessionStart hook installs deps (~20s on cold
   start, faster on warm reuse).
2. Claude session starts with the prompt above as the first message.
3. The `/signal` skill is invoked. Pipeline runs through Phases 0–10.
4. State updated, new HTML + cached images + cover committed; pushed
   via GitHub MCP.
5. Cloudflare auto-deploys.
6. Session reports the URL.

### Failure handling

The pipeline is designed for unattended operation:

- **Phase 9** runs up to 3 rounds of self-healing repair on validator failures.
- **Phase 10** always publishes the best-effort issue, even on remaining
  red gates. A broken-imperfect issue is preferable to no issue.
- The previous week's issue stays accessible via `index.html`, so the
  live site never lacks content.
- The CI workflow (`.github/workflows/issue-validation.yml`) runs
  post-publish and opens a tracking GitHub Issue on any defects it finds.

**Worth watching:** the GitHub Issues tab. Treat it as a Sunday-evening
inbox check. If the same gate keeps tripping week after week, that's a
real signal to investigate.

## Manual generation

Same as before — start a Claude Code session in this repo and invoke the
skill: `/signal` or `Run The Signal`. The trigger and the manual paths use
the exact same pipeline.

## Local development

The SessionStart hook only runs when `CLAUDE_CODE_REMOTE=true`. On a
local machine the hook exits immediately, so it doesn't disturb local
dev setups. Install Python deps locally as needed:

```
python3 -m pip install Pillow requests
```
