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

## Push notifications (one-time Cloudflare Pages setup)

The PWA auto-subscribes any installed device to web push and the publish
pipeline POSTs to `/api/notify` after each Sunday run. The push handler
in `sw.js` pre-caches the new issue (HTML + cover + every inline image)
*before* showing the notification — so a tablet that receives the push
overnight has the issue fully offline by the morning.

### 1. Generate keys

**Web (Android / any browser):** open `https://<your-pages-host>/setup.html`. Tap **Generate keys**. It runs in your browser, never sends keys anywhere. Each value has a Copy button next to it.

**CLI (alternative):**

```
python3 -m pip install cryptography
python3 scripts/generate-vapid.py
```

Either way, you end up with three values: `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, and `NOTIFY_AUTH_TOKEN`. Don't commit any of them.

### 2. Configure the Cloudflare Pages project

Pages dashboard → the project → **Settings → Functions**:

**Variables and Secrets (Production)** — encrypt all three. Workers Builds
wipes plaintext variables that aren't declared in `wrangler.jsonc` on every
deploy; encrypted secrets survive.

- `VAPID_PUBLIC_KEY` — encrypted, the base64url public key.
- `VAPID_PRIVATE_KEY` — encrypted, the JWK JSON string.
- `NOTIFY_AUTH_TOKEN` — encrypted, the random URL-safe token.
- `VAPID_SUBJECT` *(optional)* — `mailto:you@example.com`; defaults to a
  placeholder if unset.

**KV namespace binding**
- Variable name: `SUBSCRIPTIONS`
- KV namespace: create one (e.g. `signal-push-subs`) and select it.

Redeploy the Pages project (any push or "Retry deployment") so the new
bindings take effect.

### 3. Wire the GitHub Action

Notifications fire from `.github/workflows/notify-on-publish.yml` on any
push to `main` that adds a new `issues/*.html` — scheduled or manual,
the workflow doesn't care how the issue got there. It reads two repo
secrets:

GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

- `NOTIFY_AUTH_TOKEN` — same value as the CF env var.
- `SIGNAL_NOTIFY_HOST` — your Pages host, no `https://` (e.g.
  `the-signal.pages.dev` or your custom domain).

If either is missing the workflow logs a warning and skips, so partial
setup doesn't break publishes.

### 4. Verify

1. Open the live site, install as PWA, accept the OS prompt.
2. Open the project's Pages Function logs (or visit `/sw-status`) — you
   should see a subscription stored.
3. Manually fire a test push:
   ```
   curl -X POST "https://<host>/api/notify" \
     -H "Authorization: Bearer <NOTIFY_AUTH_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","body":"hello","url":"/"}'
   ```
   Notification should arrive within a few seconds.

### Failure modes

- `/api/vapid-public-key` returns 503 → `VAPID_PUBLIC_KEY` env var missing.
- `/api/subscribe` returns 503 → `SUBSCRIPTIONS` KV binding missing.
- `/api/notify` returns 401 → wrong or unset `NOTIFY_AUTH_TOKEN`.
- Subscriptions returning 410/404 from the push service are auto-pruned
  on the next `/api/notify` call.

---

## The Brief (the daily) — Worker-native pipeline

The daily is a Cloudflare **Cron Trigger** that fires the Worker every 3h
(`triggers.crons` in `wrangler.jsonc`). Each run polls the tagged sources, runs
the triage engine (per-source baselines, velocity, profile ranking, dedup, the
fold, optional Haiku hook-lines), and writes the rendered state to KV. The home
(`index.html`) fetches `/api/daily` and renders it; `settings.html` edits the
live config. There is **no AI dependency at runtime** except the optional Tier-2
enrichment call. Requires the **Workers Paid plan** (already held).

### One-time provisioning (human; ~5 minutes)

Wrangler must be authed to Cloudflare (`npx wrangler login`). Then:

```sh
# 1. Two KV namespaces (live config + rendered state / spend ledger)
npx wrangler kv namespace create DAILY_CONFIG
npx wrangler kv namespace create DAILY_STATE

# 2. One D1 database (baselines, story-movement log, item set, run log)
npx wrangler d1 create the-signal-daily
```

Paste the three returned ids over the `REPLACE_ME_*` placeholders in
`wrangler.jsonc` (`kv_namespaces[].id` ×2 and `d1_databases[].database_id`).
The D1 **schema is created automatically** by the Worker on first run — there
are no migrations to apply.

Then set the two secrets:

```sh
# Token that gates settings writes (any long random string). Paste this same
# value once per device on first save in Settings.
npx wrangler secret put SETTINGS_TOKEN

# Anthropic key for Tier-2 enrichment (likely already set from the weekly;
# the daily reads the same ANTHROPIC_API_KEY).
npx wrangler secret put ANTHROPIC_API_KEY
```

Deploy (`git push` to `main` triggers Workers Builds, or `npx wrangler deploy`).
On the first cron fire — or a manual **Run now** in Settings — the brief
populates. To fire it by hand without waiting:

```sh
curl -X POST https://<host>/api/daily/run -H "X-Signal-Token: <SETTINGS_TOKEN>"
```

### Tuning (in-app, never a deploy)

Everything tunable lives in KV and is edited at `/settings.html`:
**sources** (add/remove feeds + per-source weight), **Bluesky handles**,
**interest profile** (named-entity floor, topic weights, special handling,
mutes — edit the JSON; err broad), **fold threshold**, **enrichment toggle /
model / shortlist size / monthly spend cap**, **cadence**, **push badge**.
The reader is expected to review the generated profile + feed list and prune.

Changing the *cron cadence itself* is the one thing that needs a deploy — edit
`triggers.crons` in `wrangler.jsonc` (the in-app `cadence_hours` is advisory).

### Cost ceiling

Tier-1 (the mechanical engine) runs free forever — no AI. Tier-2 enrichment
uses `claude-haiku-4-5` ($1/$5 per M tokens) on only the ~36-item shortlist,
with the profile prompt-cached. A **monthly spend cap** (config, default $5) is
enforced: on hit the daily auto-falls back to Tier-1 (headlines + links, no
hooks) and records it in the footer. The daily can never run an unbounded bill.

### Failure modes

- `/api/daily` returns an empty state → no run has completed yet; hit **Run now**.
- `/api/daily/run` or saving in Settings returns 401 → wrong/unset
  `SETTINGS_TOKEN`, or the device's pasted token is stale (use **Forget token**
  and re-enter).
- Footer says "headlines only" → enrichment is off, the key is missing, or the
  spend cap is hit (the reason is shown). Tier-1 still ships.
- A feed that errors or returns nothing is dropped gracefully for that run and
  reported in the run log (`runs` table, `notes: dead:N`); prune dead feeds in
  Settings.
- Run logs and per-story movement evidence live in D1 (`runs`, `story_log`) —
  the latter is what the weekly reads to tell "moved" from "still exists".

### Reddit — public `.rss` only (no API)

The Reddit **Data API / OAuth is not available and is not a planned option** —
treat it as permanently off the table. Reddit is served **only** via the public
per-subreddit `.rss` endpoints, with the size-tiered rotation (big/medium/small
pools in `functions/daily/config.js`) that keeps total polls under Reddit's
per-IP rate limit. That rotation is a **permanent** part of the design, not a
temporary workaround awaiting API approval. Add subreddits sparingly and as
`tier:small`. There is no `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET` path to
enable — do not reintroduce one.
