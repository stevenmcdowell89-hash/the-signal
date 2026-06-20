# Reddit Data API — application text (Gate zero)

**Status: human action required.** Per §11 of the build, this is yours to submit.
The daily ships and works fully on RSS + HN + Bluesky without it; Reddit is a
Phase-2 source addition that drops in with no rework once approved (~2–4 weeks).

## What to do

1. Register a Reddit OAuth app: https://www.reddit.com/prefs/apps
   → "create another app…" → type **script** (personal use).
   - name: `The Signal (personal reading aggregator)`
   - redirect uri: `http://localhost:8080` (unused for script-type, but required)
   - note the **client id** (under the app name) and **client secret**.
2. Submit the Data API access request (all API access now needs pre-approval):
   https://support.reddithelp.com/hc/en-us/requests/new?ticket_form_id=14868593862164
   — paste the application text below.
3. When approved, add the client id/secret as Worker secrets and add the
   subreddits as tagged sources in Settings (Phase 2). No deploy/rework needed.

## Application text (copy-paste, edit the bracketed bits)

> **Organisation / individual:** Individual, non-commercial personal use.
>
> **Contact email:** [your email]
>
> **What are you building?**
> A personal reading aggregator for my own use. It collects headlines from
> public RSS feeds, Hacker News, and (with this access) a handful of subreddits I
> follow, ranks them against my own interest profile, and presents the few that
> matter as a short daily brief I read on my own devices. It replaces me manually
> checking these sources every day.
>
> **How will you use the Reddit Data API?**
> Read-only. Roughly every 3 hours my aggregator polls the `hot`/`top` listings
> and comment counts of a small fixed set of subreddits (well under 100 queries
> per minute — typically a few dozen requests per poll). I use the data to detect
> which threads are rising and to link back to the original Reddit discussion. I
> do not post, vote, message, or write anything to Reddit.
>
> **Will you summarise content with an LLM?**
> Yes — at inference time only, for my own reading. When I open the brief, a
> single short "why this matters" line may be generated for a thread by a hosted
> LLM. This is transient summarisation for my personal consumption. I do **not**
> use any Reddit content for model training, and I do **not** redistribute,
> publish, or share Reddit content or derived data with anyone else.
>
> **Data storage / retention:**
> I store only the thread title, score, comment count, timestamp, and the
> permalink, for up to ~14 days, purely to rank and de-duplicate items. No user
> data, no comment bodies are retained.
>
> **Commercial use:** None. This is a single-user personal tool.
>
> I'm happy to provide any further detail. Thank you for considering the request.

## Phase-2 subreddits (the tagged set, by domain)

These are the §8 P2 subreddits — add them in Settings once approved:

- **Gaming:** r/NintendoSwitch, r/Games, r/SteamDeck, r/MonsterHunter, r/paradoxplaza, r/BaldursGate3
- **Football:** r/Juve, r/seriea, r/soccer, r/FantasyPL
- **Tech & Devices:** r/Android, r/Xiaomi, r/eink
- **Golf:** r/golf · **LEGO:** r/lego
- **Books:** r/Cosmere, r/Fantasy, r/Malazan
- **Film/TV:** r/StarWars, r/television
- **Music:** r/outrun, r/synthwave
- **Fitness:** r/running, r/AdvancedRunning, r/weightroom
- **Finance:** r/UKPersonalFinance, r/Monzo, r/fintech
- **Travel:** r/themeparks, r/wdw
- **Home/Self-hosting:** r/selfhosted, r/homeassistant

## What Phase 2 adds (engine, when approved)

- Reddit as a tagged `source_type` with OAuth (client id/secret as Worker secrets).
- Reddit ranking: trajectory + per-sub baselines + comment-velocity (the engine
  already has the per-source baseline + velocity machinery; Reddit slots in).
- Links target the **comments permalink** (the discussion), per §5.

This is pure config/source addition — no rework to the engine, home, or config
surface.
