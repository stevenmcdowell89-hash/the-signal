# WP-7 — Daily inputs (SPEC §3.15)

**Date:** 2026-07-26
**Branch:** `claude/signal-antikythera-article-lzzlup`
**Files touched (exclusive, nothing else):**
- `functions/daily/feeds.js`
- `functions/daily/profile.js`

---

## 1. The problem, restated from evidence

`feeds.js` carried 10 football feeds + 5 golf feeds and **nothing else for sport**; `profile.js` had
exactly two sport domains. Because the weekly can only cover what the daily surfaces, every other
sport was structurally invisible: cricket appeared **0** times across 16 published issues, the
Commonwealth Games once, the Tour de France once — while F1, which had **no feed and no reader-profile
domain**, came to dominate the Touchline via ad-hoc research fetches.

---

## 2. What changed

### 2.1 `feeds.js` — 9 new RSS feeds (inserted after the Golf block; nothing removed or reordered)

| id | domain | weight | url | stable |
|----|--------|--------|-----|--------|
| `bbc-sport` | `sport` | 0.45 | `https://feeds.bbci.co.uk/sport/rss.xml` | true |
| `bbc-cricket` | `cricket` | 0.45 | `https://feeds.bbci.co.uk/sport/cricket/rss.xml` | true |
| `espn-cricinfo` | `cricket` | 0.45 | `https://www.espncricinfo.com/rss/content/story/feeds/0.xml` | true |
| `bbc-cycling` | `cycling` | 0.4 | `https://feeds.bbci.co.uk/sport/cycling/rss.xml` | true |
| `cyclingnews` | `cycling` | 0.4 | `https://www.cyclingnews.com/feeds.xml` | true |
| `bbc-athletics` | `athletics` | 0.4 | `https://feeds.bbci.co.uk/sport/athletics/rss.xml` | true |
| `athletics-weekly` | `athletics` | 0.4 | `https://athleticsweekly.com/feed/` | true |
| `bbc-motorsport` | `motorsport` | 0.3 | `https://feeds.bbci.co.uk/sport/motorsport/rss.xml` | true |
| `bbc-formula1` | `motorsport` | 0.3 | `https://feeds.bbci.co.uk/sport/formula1/rss.xml` | true |

All follow the existing `{ id, type, domain, weight, url, stable, name }` shape and the
`feeds.bbci.co.uk/sport/<section>/rss.xml` pattern already used by `bbc-football` / `bbc-golf`.
`stable: true` on all nine is earned, not assumed — every one was fetched live, parsed, and confirmed
to contain dated `<item>` elements (§3 below).

BBC has **two** distinct motorsport sections and both are real, non-overlapping feeds (verified by
content: `/motorsport/` led with WRC, `/formula1/` with an F1 qualifying report), so both are included
under the single `motorsport` domain.

### 2.2 `feeds.js` — 3 new Reddit subs (`tier: "small"`, per the file's "add sparingly" note)

`RS("Cricket", "cricket", 0.45, "small")`, `RS("peloton", "cycling", 0.4, "small")`,
`RS("trackandfield", "athletics", 0.4, "small")`.

**No motorsport subreddit on purpose**: r/formula1 is a session-by-session firehose and would undo the
low motorsport weight this WP exists to set.

### 2.3 `profile.js` — 5 new domains, all `edition: "sport"`

| domain | weight | label | today_tonight |
|--------|--------|-------|---------------|
| `sport` | 0.45 | More Sport | yes |
| `cricket` | 0.45 | Cricket | yes |
| `cycling` | 0.4 | Cycling | yes |
| `athletics` | 0.4 | Athletics | yes |
| `motorsport` | 0.3 | Motorsport | **no** |

Added to both `topic_weights` (weight + keywords, inserted after `golf`) and `DOMAIN_META`
(label + edition + `today_tonight`), matching the existing `football`/`golf` entries' shape.
`config.js` already defines the `sport` edition (`{ id: "sport", label: "Sport" }`), so no change was
needed there.

`profile_version` bumped **7 → 8**. This is required, not cosmetic: `mergeConfig` union-merges new
`sources` into a saved KV config automatically, but `topic_weights` is only re-seeded when the version
advances. Without the bump the nine new feeds would ship to a live install with no topic weights for
their domains — they would score ~0 and the whole WP would be inert. The documented cost of the bump
(config.js:304-314) is that in-app profile edits are replaced by these defaults on the next load.

### 2.4 Keyword sets are deliberately disjoint

`score.js:80-103` re-homes an item only when a **foreign** domain gets **≥2 keyword hits** *and* beats
the feed's own domain by **>1.25×**. Two consequences drove the design:

- Generic cross-sport words ("final", "champion", "medal", "world championships") are **excluded** from
  the `sport` catch-all, because at 0.45 it would otherwise steal cricket/cycling/athletics items.
  Each domain carries its own vocabulary instead, so a cricket or cycling story arriving on the generic
  BBC Sport feed re-homes to its own domain (verified: 4 of 81 `bbc-sport` items routed to `cricket`).
- Bare "running"/"marathon" are **excluded** from `athletics` — they belong to `fitness` (training
  content) and would drag coaching articles into a results domain. Verified: two marathon items on
  `bbc-athletics` correctly routed to `fitness`.

Multi-sport meets (Olympics, Commonwealth Games) intentionally collect in the `sport` catch-all rather
than the individual sport domains. This matches WP-1's `sports_calendar` using `multi_sport` as its
sport token for exactly those events.

---

## 3. Verification (real commands, real output)

### 3.1 Syntax

```
$ node --check functions/daily/feeds.js
(no output, exit 0)
$ node --check functions/daily/profile.js
(no output, exit 0)
```

### 3.2 Every new URL, network-verified

Egress **was** available from this environment for RSS hosts. Codes are from
`curl -sS -o /dev/null -w '%{http_code}' --max-time 25 <url>` (no `-L`, so these are direct, not
post-redirect):

```
200  https://feeds.bbci.co.uk/sport/rss.xml
200  https://feeds.bbci.co.uk/sport/cricket/rss.xml
200  https://www.espncricinfo.com/rss/content/story/feeds/0.xml
200  https://feeds.bbci.co.uk/sport/cycling/rss.xml
200  https://www.cyclingnews.com/feeds.xml
200  https://feeds.bbci.co.uk/sport/athletics/rss.xml
200  https://athleticsweekly.com/feed/
200  https://feeds.bbci.co.uk/sport/motorsport/rss.xml
200  https://feeds.bbci.co.uk/sport/formula1/rss.xml
```

Item counts and freshest `pubDate` per feed (fetched live, 2026-07-26): bbc-sport 79-81 items;
bbc-cricket 48; espn-cricinfo 100 (`Sun, 26 Jul 2026 10:57:55 GMT`); bbc-cycling 19; cyclingnews 50
(`Sun, 26 Jul 2026 10:42:27 +0000`); bbc-athletics 40; athletics-weekly 8
(`Sat, 25 Jul 2026 11:52:28 +0000`); bbc-motorsport 19; bbc-formula1 68.

**One URL correction found by this check.** `https://www.cyclingnews.com/rss/` — the pattern used by
the sibling Future plc feed already in the file (`pcgamer.com/rss/`, which is a clean 200) — returns
**301** at Cyclingnews and chains `/rss/` → `/feeds.xml/` → `/feeds.xml`. The canonical 200 URL
`https://www.cyclingnews.com/feeds.xml` is what shipped, so ingest does not depend on redirect
following.

**Reddit could NOT be verified.** All `reddit.com/r/<sub>/.rss` requests return **403** from this
environment, including the control case `r/soccer`, which is already in the shipping list — so this is
Reddit blocking datacentre egress, not a bad sub name:

```
403 r/Cricket
403 r/peloton
403 r/trackandfield
403 r/soccer (existing, control)
```

The three new subs are long-standing public subreddits, and `ingest.js` validates and drops dead
sources gracefully, but I am **not** claiming a live verification I did not get.

### 3.3 Functional check — feeds parse, domains route (acceptance criterion #11)

Script imported the real `STARTER_FEEDS`, `PROFILE` and `scoreProfile`, fetched each new feed, and ran
the live headlines through the actual scorer:

```
1) feed domains with no topic_weight: none
   football    weight=0.85 edition=sport label="Football"    today_tonight=true
   golf        weight=0.45 edition=sport label="Golf"        today_tonight=false
   sport       weight=0.45 edition=sport label="More Sport"  today_tonight=true
   cricket     weight=0.45 edition=sport label="Cricket"     today_tonight=true
   cycling     weight=0.4  edition=sport label="Cycling"     today_tonight=true
   athletics   weight=0.4  edition=sport label="Athletics"   today_tonight=true
   motorsport  weight=0.3  edition=sport label="Motorsport"  today_tonight=false
3) motorsport(0.3) < football(0.85) && <= golf(0.45) -> true
   existing football/golf weights unchanged -> true
4) duplicate feed ids: none

ALL CHECKS PASSED
```

**Headline hit rate** (fraction of a feed's live headlines that score > 0, i.e. can rise above the
fold), calibrated against the existing football/golf feeds as the baseline:

```
bbc-football       football     34/77  =  44%   <- existing baseline
bbc-golf           golf         12/30  =  40%   <- existing baseline
bbc-cricket        cricket      21/48  =  44%
espn-cricinfo      cricket      15/100 =  15%
bbc-cycling        cycling      10/19  =  53%
cyclingnews        cyclingnews  45/50  =  90%
bbc-athletics      athletics    23/40  =  58%
athletics-weekly   athletics     3/8   =  38%
bbc-motorsport     motorsport    7/19  =  37%
bbc-formula1       motorsport   34/68  =  50%
bbc-sport          sport        16/81  =  20%
```

The first pass of keyword sets put `athletics` at 30% and `sport` at 13% — under the baseline, i.e.
real results ("Lyles wins 100m in world-leading 9.79 seconds") were scoring **0** and would have sat
below the fold forever. The sets were then tuned against live headlines (bare event distances added to
athletics; boxing weight classes, `paralympian`, `commonwealth`/`commonwealths` and multi-word medal
phrases added to sport; cricket match vocabulary — `century`, `knock`, `not out`, `lbw`, `powerplay`,
`toss`, `boundary` — added). `bbc-sport` reads low only because it is a routing feed: most of its 81
items are football and F1 stories that correctly stay out of the catch-all.

Sample of what now surfaces that previously could not (real scored output):

```
sport      0.29  What's on for Team NI on day three of Commonwealth Games?
sport      0.18  Scotland upset Wales for first win of Commonwealths
sport      0.29  Is 2026 the Commonwealth Games' last dance or a future-proofing revamp?
sport      0.29  How Eala's Wimbledon run made Filipinos fall in love with tennis
cricket    0.35  'A brutal innings' - Seifert's best strikes of his half-century
cricket    0.29  'That is some brutal hitting' - Marsh hits six sixes in huge innings
athletics  0.26  'Following in the footsteps of legends' - Kerr smashes mile world record
athletics  0.26  Ehammer breaks men's heptathlon world record
cycling    (90% of Cyclingnews' front page, incl. Tour de France stage results)
```

### 3.4 Regression — no existing item was stolen

Scored the live headlines of **every** existing (non-new) RSS feed with the committed profile and the
new profile, comparing assigned domain and score:

```
existing feeds scored: 59 live / 92 (unreachable or empty in this sandbox: 33)
titles compared: 3286
items whose domain OR score changed: 7
  bbc-world  [world]   world(0.00) -> sport(0.29)  Smash hit: How Alex Eala's Wimbledon run made everyday Filipinos fall in love with tennis
  bbc-ni     [local]   local(0.00) -> sport(0.29)  What's on for Team NI on day three of Commonwealth Games?
  news-letter[local]   local(0.20) -> sport(0.29)  Northern Ireland secure first Commonwealth Games medal as Bethany Firth earns bronze
  rte-news   [local]   local(0.00) -> sport(0.29)  All-Ireland Camogie semi-finals recap
  thejournal [local]   local(0.00) -> sport(0.29)  Cork see off Tipperary to set up All-Ireland camogie final rematch with Galway
  thejournal [local]   local(0.00) -> sport(0.29)  Champions Galway beat Kilkenny to return to All-Ireland senior camogie final
  marathon-handbook [fitness] fitness(0.00) -> sport(0.29)  Your Track-Only Schedule For The Glasgow 2026 Commonwealth Games
```

7 changes in 3286 titles, and **all seven are the defect being fixed**: sport stories that previously
scored 0.00 (invisible) now route into the Sport edition. Six of the seven were previously unscoreable;
the seventh (`news-letter`, a Commonwealth Games medal for NI) moves from `local` 0.20 to `sport` 0.29.
**Zero** false steals — nothing was pulled out of gaming, books, tech, film, finance, history or
football. (The 33 unreachable feeds are sandbox egress limits on those hosts, not a change from this
WP.)

### 3.5 Scope

```
$ git diff --stat -- functions/daily/feeds.js functions/daily/profile.js
 functions/daily/feeds.js   |  38 +++++++++++
 functions/daily/profile.js | 120 ++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 157 insertions(+), 1 deletion(-)
```

`git diff --name-only` also lists `scripts/extract-covers.py` and `scripts/mirror-images.py` — those
are **WP-8 running concurrently in the same tree**, not this WP. WP-7 touched only its two files.

---

## 4. Per-feed / per-domain weight justifications

| domain | weight | one-line justification |
|--------|--------|------------------------|
| `sport` (generic) | **0.45** | The catch-all for every sport with no domain of its own — rugby, tennis, boxing, snooker, darts, GAA, swimming, horse racing, and the multi-sport meets. Set level with golf/cricket so a Commonwealth Games day cannot be structurally invisible again, and far enough below football (0.85) that it can never crowd the brief. |
| `cricket` | **0.45** | Exact parity with golf: the flagship absence (0 mentions in 16 issues), and a summer results-and-majors sport of the same shape as golf — so an Ashes or Test result competes with a golf major on equal terms, no better and no worse. |
| `cycling` | **0.4** | The grand tours are the interest (the Tour de France appeared once in 16 issues); the daily peloton churn is not. 0.4 is the file's world/fitness tier: a stage win or GC swing surfaces, a team press release does not. |
| `athletics` | **0.4** | Same championship shape as cycling — the Worlds, the Olympic and Commonwealth track programme, Diamond League finals — a results interest rather than a weekly following, so it sits at the same tier and not at golf's. |
| `motorsport` | **0.3** | The owner's stated position: *"F1 is at best a passing interest, nice to know big results, I don't need a minute by minute"* → `interest_depth: "results_only"` (seeded by WP-1, key `motorsport`, confirmed in `state/signal-state.json`). 0.3 is the file's floor tier (music/podcasts): **materially below football (0.85) and below golf (0.45)** as the SPEC requires. A race win, a title decider or a corroborated confirmed/official story still clears the bar; a Friday-practice item does not. |

Two further motorsport-specific restraints, both deliberate:
- **No specialist motorsport feed.** `https://www.autosport.com/rss/feed/all` verifies fine (HTTP 200,
  ~50 items) and would have been the obvious pick, but a session-by-session firehose is precisely what
  made F1 saturate the Touchline. BBC's two sub-feeds alone are the results-level coverage asked for.
- **No `today_tonight`.** The dated-events strip (`render.js` `todayAndTonight`, gated on
  `topic_weights[d].today_tonight`) admits items with a real time signal in the title. On a race
  weekend those are mostly practice and qualifying session times — the minute-by-minute the owner
  explicitly does not want. `sport`, `cricket` (a day's play starting), `cycling` (today's stage) and
  `athletics` (tonight's final) do opt in, because their dated items are the events themselves.

Feed weights mirror their domain weight exactly, as every other block in the file does.

**Consistent with WP-1's mid-build SPEC correction** (§3.5, 2026-07-26): cricket, cycling and athletics
have **no** `interest_depth` key, and an absent key means *unset — cover on news value*, never `off`.
Their weights here are real, above-floor weights (0.45 / 0.4 / 0.4) precisely so that reading them as
"off" is impossible; only `motorsport`, which does carry an explicit `results_only`, is pushed to the
file's floor tier. §3.15 itself was not amended by that correction — this WP implements it as written.

---

## 5. Hardcoded sport assumptions found elsewhere (checked, not edited)

I do not own these files. All four are recorded as handoffs, not changed.

1. **`functions/daily/render.js:386` — `NEWS_SPORT`.** `new Set(["world","local","finance","football","golf"])`
   gates Headlines eligibility. The five new domains are absent, so a cricket / cycling / athletics /
   general-sport story can only reach Headlines by another route (corroborated across ≥2 feeds,
   `signal_high`, entity floor, or confidence ≥ `headline_strong_conf` = 0.75). It is a *broadening*
   clause, not a filter, so nothing is dropped on the floor — but a Test-match result is
   systematically less likely to lead than a golf result of equal weight. **Recommended:** add
   `"sport"`, `"cricket"`, `"cycling"`, `"athletics"`; deliberately **not** `"motorsport"` — a big F1
   result still qualifies via corroboration or a confirmed/official title, which is exactly
   `results_only`.
2. **`functions/daily/render.js:8-25` — `DOMAIN_LABELS`.** Cosmetic only; it is now a documented
   fallback and labels resolve from `topic_weights[d].label` first (confirmed in `buildState`), so the
   new domains render correctly ("More Sport", "Cricket", …). Adding the five keys would keep the
   fallback honest.
3. **`functions/daily/dedup.js:54` — `RELAXED_DOMAINS = new Set(["football"])`.** BBC Sport publishes
   3-4 near-variants of the same cricket match report (observed live: *"Ravindra stars with 98 as Fire
   beat MI London"*, *"Ravindra stars as Welsh Fire beat MI London to continue winning start"*,
   *"Seven sixes - Ravindra smashes 98 from 44 balls"*). That is the same churn the relaxed
   entity-merge was built for. **Recommended:** add `"cricket"` (and consider `"cycling"`, where stage
   reports duplicate similarly).
4. **WP-1 sport vocabulary.** `state/signal-state.json` `interest_depth` uses the key `motorsport`,
   which matches this WP's domain key exactly. But `sports_calendar[].sport` uses `multi_sport` for
   multi-sport meets, where the daily's catch-all domain is `sport`. The SPEC does not fix a shared
   sport vocabulary, so this is not a contract breach — but the rendered `data-sport` attribute
   (§3.4) and the results-ledger multi-sport invariant (§3.11) will be easier to check if they use the
   daily's domain tokens (`football | golf | sport | cricket | cycling | athletics | motorsport`), with
   `multi_sport` treated as `sport`. Flagging for WP-1/WP-3/WP-4.

Everything else in the daily is domain-agnostic and needed no change: `score.js` iterates
`Object.entries(topic_weights)`, `config.js` `mergeConfig` union-merges new `sources` by id (so the
nine feeds reach a live install without a migration), the `sport` edition already exists in
`config.js:173`, and `render.js` resolves labels, editions, sections, Also-domains and below-fold
fairness generically per domain.

---

## 6. What's left / not done

- **Reddit URLs unverified** (403 for every subreddit from this environment, including the existing
  `r/soccer` control). The three new subs are conventional names and `ingest.js` drops dead sources
  gracefully, but they have not been proven live.
- **`espn-cricinfo` keyword hit rate is 15%**, well under the 40-44% baseline. Its copy is
  player-name-shaped (*"Shafique, Shakeel added to Pakistan squad"*), which keyword scoring cannot
  reach without adding player or country names — and country names would let `cricket` (0.45) steal
  from `world` (0.4), which is a worse failure. `bbc-cricket` (44%) is the load-bearing cricket feed;
  ESPNcricinfo is depth and corroboration (`source_count` ≥ 2 lifts items into Headlines). If cricket
  still under-surfaces in practice, the better lever is the `guardian-football`-style
  `https://www.theguardian.com/sport/cricket/rss` (verified 200, 20 items, UK-editorial) as an
  alternative or addition — I chose the true specialist per the SPEC's wording.
- **`athletics-weekly` carries only 8 items** and updates a few times a week. It is a genuine
  specialist, not a firehose; `bbc-athletics` (58%, 40 items) is the primary.
- **No specialist feed for motorsport** — a deliberate omission, justified in §4, not an oversight.
- **`worldathletics.org/rss` was rejected.** It returns 200 and parses, but its head item was a 2025
  championship-host announcement, so the ordering looks non-chronological or stale. Not shipped.
- **Not verified end-to-end through a live daily run** — that needs the Worker, KV and D1. What is
  verified is every layer below that: feeds fetch and parse, `scoreProfile` assigns the intended
  domain, weights and editions resolve, and no existing domain regressed.
- **`profile_version: 8` will overwrite an existing saved profile's `topic_weights`** in KV on next
  load, discarding in-app profile edits. This is the documented mechanism (config.js:304-314) and is
  unavoidable if the new domains are to reach a live install, but the owner should know.
