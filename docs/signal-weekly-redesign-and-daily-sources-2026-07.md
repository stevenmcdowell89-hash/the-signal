# The Signal — Weekly Ground-Up Redesign + Daily Enhancement & Source Expansion

_July 2026. Companion to `signal-recommendations-2026-07.md`. Three fresh research tracks: (A) a clean-slate redesign of the weekly from first principles; (B) content enhancements for the daily Brief; (C) a large set of new daily sources ready to paste into Settings. Research/recommendations only — no product code changed._

---

# PART A — The Weekly, Rebuilt From the Ground Up

_Grounded in issues `2026-07-05`, `2026-06-28`, the good-era `2026-04-19`, the v8.27 spec, and `signal-state.json`. Best-practice devices attributed; the rest is design judgment._

## A1. First-principles thesis

The daily now owns "what happened," so the weekly's only defensible job is **composition**: turning a scattered week — the news _and_ the reader's own life (what he read, watched, trained, spent, planned) — into a single narrative he can hold, told by a person he recognises. Nothing else in his stack does this: the daily fragments, the feeds silo his twelve interests, and no algorithm remembers what it told him three weeks ago. **The one job the weekly must do that nothing else can is synthesis-with-memory: connect the dots across domains and across time, in a human editorial voice, and hand him one concrete thing to act on.** If an issue only tells him what happened, it has failed; if it tells him what the week _added up to for him_ and what to do about it, it has earned the Sunday slot.

## A2. The clean-slate weekly

### Identity & voice — put a person in the personal magazine

The single biggest change: The Signal gets a named editorial voice, **"the Editor,"** who speaks in first person and opens every issue with a letter. Today's Gate 1A bans "I/we" everywhere — a reasonable rule for keeping the _reader's_ family out of specials, but it has over-corrected into a magazine with no author at all. **Split the rule: the reader stays invisible; the Editor becomes visible.** (Morning Brew's fixed first-person hello, sourced.)

House-voice rewrite:
- **Kill the mandatory per-section aphorism.** The tic the scorer has flagged five issues running (weakest=voice) is _structural_: the pipeline requires every section to land a closing line, so twelve sections manufacture twelve fortune-cookie endings. Replace "every section ends on a line" with **"earn your closer or don't have one," capped at one per issue.**
- **Kill the Angle-box-reprinted-as-pull-quote.** One thought, stated once.
- **Keep** the borrowed-opinion rule (voice real takes, invent nothing) — the reason the prose floor is high.
- **Add Semafor's labeled honesty** (sourced): where a section has a real argument, carry a visible **"The case against"** line (Room for Disagreement) — the cheapest trust-builder there is, and it kills the smug single-take habit.

### Issue architecture — four movements, not thirteen sections

Design the issue as a reading arc with four movements and clear act-breaks. Mood → depth → breadth → action.

- **Movement I — THE OPEN.** `The Letter` (Editor's thesis, dots connected across domains) → `The Week, Composed` (world synthesis — the section that already works) → **`Caught Up`**, a _hard-capped 8-line digest_ (the Economist "World This Week" contract, sourced): fixed-length, non-expandable, one line per item — _"you are now caught up"_ — so the deep pieces never pretend to be comprehensive, and the daily-breadth safety-net stops bloating every section.
- **Movement II — THE LONG READ.** Exactly **one** anchor feature per issue, rotating subject across his whole world (world deep-synthesis, a Juventus/Serie-A tactical essay, history at AskHistorians depth, a Cosmere/Malazan or Star Wars essay, a strength-science note, an AI/tech essay). Tortoise's scarcity rule made structural (sourced) — replaces today's failed "two deep anchors in every section." Absorbs the Saga, Deep-Dive-lite, and evergreen-feature impulses into one ownable centrepiece.
- **Movement III — THE ROUNDS.** Branded domain sections doing **synthesis or service, not catch-up**: `The Touchline` (football), `Pixel & Byte` (gaming + LEGO), `Screen & Sound` (film/TV/music + a "Bookmark" books rail), plus **`The Desk`** (the restored service department). 2–3 appear per issue on the news.
- **Movement IV — THE CLOSE.** `The Threads` (running-saga callbacks) → `Down the Rabbit Hole` (signature curiosity) → `On the Radar` (week ahead) → **`Do This Week`** (the single service action) → `The Colophon` (sign-off). The issue ends on a **verb**, then a human beat.

### The section/content model

| Department | Job | Cadence |
|---|---|---|
| **The Letter** | Editor's voice; week's thesis; cross-domain dot-connecting | every issue |
| **The Week, Composed** | World synthesis | every issue |
| **Caught Up** | 8-line hard-capped digest; the "you're caught up" contract | every issue |
| **The Long Read** | Single deep anchor, rotating subject | every issue (1) |
| **The Touchline** | Football synthesis + season-as-saga (Juve/Serie A, PL, CL, tournaments, FPL, golf majors) | most weeks |
| **Pixel & Byte** | Gaming + LEGO — what it _means_ (Switch 2, Steam Deck, Monster Hunter, BG3, Paradox) | most weeks |
| **Screen & Sound** | Culture-critic voice + Bookmark rail (film/TV, Star Wars, synthwave, SFF books) | most weeks |
| **The Desk** | THE service layer — rotating columns each ending in an action: **The Session** (fitness), **The Ledger** (money/fintech/Etsy), **The Itinerary** (travel/parks/NI), **The Toolkit** (tech/Android/e-ink) | 1–2/week |
| **The Threads** | Continuity engine — named sagas + "previously on…" callbacks across ALL domains | every issue |
| **Down the Rabbit Hole** | Signature curiosity ritual (etymology/history curio) | every issue |
| **On the Radar** | Week ahead | every issue |

**The service layer is the most important fix after voice.** The v8.27 collapse of The Ledger/The Itinerary/The Long Game into generic Money/Places lost the _verb_. The good-era issue closed on **"One Thing to Do This Month"** ("set up a standing order into an index tracker… even £50/month compounds"). Rebuild it as **The Desk**, whose rotating columns always end on a **"Do This Week"** pin, stating idiosyncratic criteria not vibes (Monocle, sourced) — "Buy this ISA because X, before this date, here's the standing order" beats "the market did things."

### Continuity & ritual mechanics (the solo moat)

- **The Threads — the Matt Levine engine (sourced):** give recurring situations **proper names, reused verbatim**, with **"previously on…"** one-liners. Extend beyond World. Today `ongoing_stories` exists only to _gate_ topic-lock — a suppression mechanism; flip it into a reader-facing asset: the Iran endgame, the UK-Labour race, **Antonelli's title run**, and _his own life-threads_ (marathon build in `training_phase`, the just-finished Efteling trip). "Three weeks ago we said the ceasefire was turning into paperwork; here's what the funeral changed" is the sentence no feed can write.
- **Keep Down the Rabbit Hole** as _the_ ownable ritual (already beloved: the "deadline"/Andersonville item), fixed slot near the close.
- **The Week in Numbers** — a small personal strip nobody else can produce: Garmin miles + training-block status, FPL rank, the Juventus result, one money number.
- **One Big Thing** = the Long Read. **One Action** = Do This Week. Exactly one of each per issue — scarcity as a feature.

### Personalization & the daily bridge

- Promote the World lead's existing move ("_The daily brief carried the fireworks. What the week actually added up to is…_") to a **standard opening gesture** for any section touching live news.
- Mine reader state already present: `currently_reading`/`currently_watching` → Long Read pegs + Bookmark; `upcoming_trips` → Itinerary + a Threads countdown; `training_phase` → The Session's angle + the numbers strip; `wearables` → training-science hooks. Rich state, currently used for gating not intimacy.
- **Add one new input: a "Saved This Week" queue** — a lightweight state field where the reader drops links/notes to thread in. The Letter and The Threads pull from it. This is the true daily→weekly bridge: the daily surfaces, he saves, the weekly composes.
- **Synthesis-by-juxtaposition (The Week, sourced):** for World and the Long Read, present 2–4 **attributed** conflicting excerpts in sequence and let the arrangement carry meaning — attribution _is_ the credibility. A concrete upgrade over the single-Angle-box habit.

### Visual / reading concept for tablet

- Xiaomi Pad, portrait, Sunday morning, ~30–45 min of _selective_ reading — design for skim-with-depth-on-demand.
- **Length: cut hard.** Today's ~630KB two-anchors-per-section issues are a compliance artefact. Target **~6,000–9,000 words** (~40% cut), weight moved into the one Long Read.
- **Pacing:** the four movements get real act-breaks (full-bleed divider/breather between movements, not between every section). Keep "no 3+ screens of unbroken prose."
- **Component kit:** cut the ~50-component palette to a **tight ~12** (cover, letter, section opener, synthesis body, capped digest, results/stats strip, "case against" callout, one pull-break/issue, Threads "previously" card, Do-This-Week pin, radar cards, colophon).
- Keep the serif body, mono labels, per-section reading-time badges, and an editorial cover: one defining image + the Letter's thesis line as coverline.

## A3. Keep / Change / Kill

| | Current | Redesign move |
|---|---|---|
| **KEEP** | World This Week synthesis | Template for the whole product |
| **KEEP** | Prose floor, fact density, sourcing, image-integrity chain | Preserve wholesale |
| **KEEP** | Touchline / Pixel & Byte / Screen & Sound brands | Sharpen to synthesis+service |
| **KEEP** | Down the Rabbit Hole; reading-time badges; editorial cover; serif type | Elevate Rabbit Hole to _the_ signature ritual |
| **KEEP** | On the Radar / Release Radar | Forward-look + reference |
| **CHANGE** | Foreword (author-less) | → **The Letter** (Editor's first-person voice) |
| **CHANGE** | Two deep anchors per section | → **one Long Read** + lighter synthesis elsewhere |
| **CHANGE** | Breadth safety-net bloating every section | → **Caught Up**, one hard-capped 8-line digest |
| **CHANGE** | Generic Money/Places (v8.27) | → **The Desk** (Ledger/Itinerary/Session/Toolkit), each ends in **Do This Week** |
| **CHANGE** | `ongoing_stories` only gates topic-lock | → powers **The Threads** reader-facing callbacks |
| **CHANGE** | Single Angle box, one take | → add **"The case against"** where an argument exists |
| **CHANGE** | ~50-component palette, ~630KB | → ~12-component kit, ~6–9k words |
| **KILL** | Mandatory per-section aphorism | Cap 1/issue (root cause of weakest=voice ×5) |
| **KILL** | Angle reprinted as pull-quote | Self-plagiarising tic |
| **KILL** | Catch-up-only sections | They yield |
| **KILL** | Rule/gate accretion optimising compliance | Retire most gates (see migration) |
| **KILL** | "No author anywhere" reading of Gate 1A | Reader invisible; Editor visible |

## A4. Migration path (sequence it — a hard reset is risky)

- **Phase 1 — Voice & the person (next 1–2 issues, near-zero structural risk).** Replace the Foreword with **The Letter**; kill the mandatory aphorism + Angle-as-pull-quote (cap one aphorism/issue); make the "daily carried the facts, here's the layer" gesture the standard section opener. _Retire:_ the per-section closer/aphorism check and entry-pattern-rotation enforcement. Should move the scorer off weakest=voice for the least work.
- **Phase 2 — Service & continuity (issues 3–5).** Stand up **The Desk** with **Do This Week** pins (rebrand Money→Ledger, Places→Itinerary). Launch **The Threads** off `ongoing_stories`, extended beyond World. Add **The Week in Numbers**. _Retire:_ the deficit-promotion and hard-cadence-floor validators — the roster is now small enough for a simple "each domain at least monthly" checklist.
- **Phase 3 — The spine & the Long Read (issues 6–8).** Adopt the four-movement architecture; introduce **The Long Read** as the single anchor (absorbing Saga + Deep-Dive-lite + evergreen); stop forcing two anchors per section. Add **Caught Up**; retire the breadth-safety-net-in-every-section rule. Cut length ~40%; trim the component palette. _Retire:_ the topic-lock sliding-window machinery and its Gate-1 grep — The Threads now _owns_ continuity as a feature, so suppression-by-gate is redundant.
- **Phase 4 — Personalization loop & consolidation (ongoing).** Add the **"Saved This Week"** input feeding The Letter and The Threads. Collapse the v8.13→v8.34 patch-stack into **one clean editorial charter**. **Keep exactly three gates:** image-URL verification (safety), markup contracts (rendering safety), and **one holistic editorial-quality read** replacing the ~8 compliance scripts. Optimise for one question — _did this issue tell him what the week added up to, and give him one thing to do?_

## A5. The north star

A year from now, Sunday morning, the Pad wakes to a cover that is one photograph and one sentence — the week, named. The Editor's letter reads like a friend who's been paying attention all week and has thought about how it all fits, so that by the second paragraph football, the Middle East, and the reader's own just-finished trip are somehow the same story. He's already caught up — the daily did that, and Caught Up confirms it in eight lines — so he never re-reads the news; he reads what it meant. He sinks into the one Long Read the way he'd sink into a good longform piece with a second coffee, then moves through his worlds in sharp, opinionated rounds that occasionally admit the case against themselves. The Threads remember what he was following — Antonelli chasing history, the marathon block he just restarted. Down the Rabbit Hole hands him one delightful, useless, true thing to know. And he closes not on a fortune-cookie aphorism but on a single verb — do this, this week, here's why — and a last human line. It's shorter than it used to be, and it feels like more, because for the first time it feels like it was written by someone, to him.

---

# PART B — Daily Brief: Content Enhancements

_These are content-layer enhancements (the plumbing bugs — dead push, cadence, read-state, save-for-later, the daily→weekly bridge — are in the companion doc and are assumed logged)._

## B1. Current content verdict

Strong: content-led ranking is real (`score.js` lifts confirmed/official, buries rumour; football override means "here we go/done deal" beat "linked with"); one-line-per-card discipline (`why` → `hook` → `summary`); per-interest completeness on quiet days; a partial human layer (discussion chips, Communities, a `register` taxonomy that actually weights ranking). Thin/flat: the best trust cue in the data is invisible; there's no daily lead; "Start here" is an unlinked table of contents; "Developing" is a hollow badge; no skim-vs-understand depth; communities are raw dumps; football is weighted like the core but read like everything else; voice is uniformly neutral even where a light curatorial voice would earn its keep.

## B2. Recommendations, tiered

**Tier 1 — do first (cheap; mostly reuse of existing data/AI)**
- **B-T1a. Render "covered by N sources."** `source_count` is already computed, already drives ranking (`render.js` `importance()`), already shipped in `publicItem` — but **never rendered**. Add a chip in `catchEl` when `source_count ≥ 2` (e.g. `◆ 6 sources`). Zero pipeline cost; a trust + importance cue in one glyph that explains _why_ an item leads. Highest value-per-effort in the whole list. _Lands: `index.html`._
- **B-T1b. A genuine "One Big Thing" lead.** Promote `headlines[0]` into a distinct lead block above Headlines — bigger type, its `why` always shown, source-count + Developing inline (`editPicks` already writes its `why`). Turns "a ranked list" into "an edition with a front page." _Lands: `render.js` + `index.html`._
- **B-T1c. Give "Developing" substance — "what changed since yesterday."** The daily-ness move. Persist last-surfaced headline/signal-tier per cluster (extend `story_log` in `score.js`) and render the delta ("was _linked with_ → now _here we go_") — no AI needed for v1. Converts a static leaderboard into a story you're following. _Lands: `db.js`/`score.js` (+ optional `editorial.js`, `index.html`)._
- **B-T1d. Upgrade "Start here" to voiced, linked one-liners.** Replace three bare titles with the three lead `why`-lines already computed, made tappable (change `start_here` to carry `{title, why, link}`). Reuses existing AI output; makes the most-prominent slot the most-edited. _Lands: `render.js` + `index.html`._

**Tier 2 — investment**
- **B-T2e. Skim vs understand.** Keep _both_ the `hook` (what's new) and `why` (why it matters) on the card, expandable from the one-liner. Both already exist; today one is discarded. Optionally add a purpose-built `why`/`number` field to the enrich schema. _Lands: `enrich.js` + `index.html`._
- **B-T2f. Synthesise the community layer.** Add a communities digest mirroring `digestRollups`: 1–2 sentences of "what Reddit/HN/Bluesky are actually arguing about today" atop the Communities tab. Turns a raw dump into the human-texture read it's meant to be. _Lands: `editorial.js` + `index.html`._
- **B-T2g. Football saga tracker + fixtures/results rail.** Football is the most-weighted live interest but has no continuity structure. (1) Group a transfer story's clusters across days via `story_log` — "Vlahovic to Juve — day 6: was _talks_, now _medical booked_"; (2) a compact Juventus/Serie A + PL fixtures-and-results strip in the Sport edition. _Lands: `render.js` (+ optional `editorial.js`)._
- **B-T2h. Morning vs evening framing.** Use `generated_at` hour: a morning lead ("Here's your day") vs an evening recap ("What moved since this morning," built from the new-since set). _Lands: `render.js` + `editorial.js` + `index.html`._

**Tier 3 — polish**
- Per-domain "one thing to know" header line (extend `edition_briefs` to per-section). · "By the numbers" chip when a headline carries a figure. · Tap the source-count chip to list the source names behind it. · A slightly warmer hook register for `colour`/`discovery` items only. · Bridge daily developing-clusters → refresh the weekly `ongoing_stories.last_development` so both products share one continuity spine.

## B3. The one content move

**Give story-threads real continuity — the "what changed since yesterday" line on developing items (B-T1c), promoted into a small recurring "Still developing" thread near the top.** Everything else makes a good _digest_ better; this makes it a _daily_. The engine already has the raw material (`story_log` time-series, `developing`/`days_active`, the signal-tier transitions). It's largely mechanical, serves the two most-weighted live interests (football sagas, world stories), and is the difference between "today's top items" and "here's how your world moved since yesterday." Cheapest-first honourable mention: ship **B-T1a (render `source_count`)** alongside — it's nearly free.

_Sourced best-practice: Axios (why-it-matters, 1-big-thing, AM/PM); Semafor (labeled layers, Notable); Techmeme (coverage counts); Particle (what's-new-since, clustering); Ground News (coverage context); The Browser (one-line curation). Football rail / saga persistence / daily→weekly bridge are judgment fitted to this engine._

---

# PART C — Daily Source Expansion

_All URLs checked live where the host allowed (11 Jul 2026). **verified?**: `YES` = valid RSS/Atom with fresh items; `conv` = real canonical path but host blocked the check — validate on ingest; `HTML→conv` = use the noted feed path. Source list lives in `functions/daily/feeds.js` (defaults) and is edited live in Settings (`DAILY_CONFIG` KV)._

## C1. Gap analysis

| Domain | Current | Priority |
|---|---|---|
| world | 3 RSS (UK-centric, no wire/geopolitics) | **HIGH** |
| local (NI) | 1 RSS + 1 reddit (BBC NI only) | **HIGH** |
| football | 3 RSS + 4 reddit (no Juve/Serie-A-English, no transfers, no tactics) | **HIGH (core)** |
| gaming | 4 RSS + 6 reddit (weak on Nintendo-news + majors + official blogs) | **MED-HIGH** |
| books | 1 RSS + 3 reddit (Reactor only; no Cosmere/Malazan/Locus) | **HIGH (core)** |
| fitness | 1 RSS + 3 reddit (Runner's World only; no strength/wearables/trail) | **HIGH** |
| ai_engineering | 3 (infra-heavy; no consumer-AI voices) | **HIGH** |
| finance | 1 RSS + 4 reddit (Monevator only) | MED-HIGH |
| tech_devices | 3 RSS + 2 reddit (thin e-ink/wearables) | MED |
| history | 1 RSS + 2 reddit (no podcasts/History Today) | MED |
| film_tv | 2 RSS + 2 reddit (no trailers/majors) | MED |
| golf / lego / travel / music / podcasts | 1–2 each | LOW-MED |
| **Bluesky (all)** | **0 — biggest single opportunity** | **HIGH** |

## C2. New candidates by domain

### World (0.4)
- Al Jazeera – All · rss · `https://www.aljazeera.com/xml/rss/all.xml` · non-Western geopolitics · **YES**
- France24 English · rss · `https://www.france24.com/en/rss` · European lens · **YES**
- AP Top News · rss · `https://feeds.apnews.com/rss/apf-topnews` · neutral wire · conv
- Reuters World · rss · `https://www.reutersagency.com/feed/?best-topics=world&post_type=best` · wire · conv
- DW English – All · rss · `https://rss.dw.com/rdf/rss-en-all` · European public broadcaster · conv
- Economist – International · rss · `https://www.economist.com/international/rss.xml` · analysis (headline-only, paywall) · conv

### Local — Northern Ireland (0.5)
- Belfast Telegraph – NI · rss · `https://www.belfasttelegraph.co.uk/news/northern-ireland/rss/` · biggest NI daily · conv
- Irish News · rss · `https://www.irishnews.com/rss/` · nationalist-leaning NI daily · conv
- News Letter · rss · `https://www.newsletter.co.uk/rss` · unionist-leaning NI daily · conv
- RTÉ News · rss · `https://www.rte.ie/feeds/rss/?index=/news/` · all-Ireland public broadcaster · **YES**
- TheJournal.ie · rss · `https://www.thejournal.ie/feed/` · fast Ireland news · **YES**
- r/belfast · reddit (small) · city-level chatter · conv

### Football (0.85) — core; prioritise Juventus/Serie A
- **Juvefc.com** · rss · `https://www.juvefc.com/feed/` · dedicated English Juventus + transfers · **YES**
- Get Italian Football News · rss · `https://www.getfootballnewsitaly.com/feed/` · deepest English Serie A · conv
- Black & White & Read All Over · rss · `https://www.blackwhitereadallover.com/rss/index.xml` · SB Nation Juventus blog · conv
- Forza Italian Football · rss · `https://forzaitalianfootball.com/feed/` · English Serie A features/pods · conv
- SempreMilan · rss · `https://sempremilan.com/feed` · Serie A rival coverage · **YES**
- **Fabrizio Romano** · bluesky · `fabriziorom.bsky.social` · THE transfer source · **YES**
- Guardian Football Weekly (pod) · rss · `https://www.theguardian.com/football/series/footballweekly/podcast.xml` · flagship pod · conv

### Gaming (0.9)
- **Nintendo Everything** · rss · `https://nintendoeverything.com/feed/` · high-volume Nintendo · **YES**
- GoNintendo · rss · `https://gonintendo.com/feeds/all.xml` · Nintendo aggregator · **YES**
- Nintendo Wire · rss · `https://nintendowire.com/feed/` · Nintendo features/reviews · **YES**
- IGN Games · rss · `https://feeds.feedburner.com/ign/games-all` · majors volume · **YES**
- PC Gamer · rss · `https://www.pcgamer.com/rss/` · PC/strategy · **YES**
- Kotaku · rss · `https://kotaku.com/rss` · culture/news · **YES**
- GameSpot News · rss · `https://www.gamespot.com/feeds/game-news/` · majors · conv
- Polygon · rss · `https://www.polygon.com/rss/index.xml` · features/reviews · conv
- PlayStation.Blog · rss · `https://blog.playstation.com/feed/` · official PS/State of Play · **YES**
- r/pcgaming (medium), r/patientgamers (small) · strategy/backlog fit · conv

### Books / SFF (0.5, NO SPOILERS) — core
- Reactor on Bluesky · bluesky · `reactorsff.bsky.social` · Tor/Reactor SFF · **YES**
- 17th Shard (Cosmere) · rss · `https://www.17thshard.com/forum/discover/6.xml/` · THE Sanderson/Cosmere community · conv
- Locus Magazine · rss · `https://locusmag.com/feed/` · SFF deals/releases/awards · conv
- Grimdark Magazine · rss · `https://www.grimdarkmagazine.com/feed/` · Malazan-adjacent · conv
- r/Stormlight_Archive (small), r/printSF (small) · conv
- _Note: Brandon Sanderson has left Bluesky — no Sanderson handle; the Cosmere floor + 17th Shard cover him._

### Fitness (0.4, news/gear/method)
- DC Rainmaker · rss · `https://www.dcrainmaker.com/feed` · definitive Garmin/wearables · **YES**
- Marathon Handbook · rss · `https://marathonhandbook.com/feed/` · active running · **YES**
- Stronger by Science · rss · `https://www.strongerbyscience.com/feed/` · evidence-based strength · conv
- iRunFar · rss · `https://www.irunfar.com/feed` · trail/ultra + gear · conv
- r/trailrunning (small), r/kettlebell (small) · conv

### Tech & devices (0.75)
- Android Police · rss · `https://www.androidpolice.com/feed/` · deep Android/Pixel · **YES**
- Good e-Reader · rss · `https://goodereader.com/blog/feed` · THE e-ink source (Boox/Kobo/Kindle) · **YES**
- r/kobo (small) · e-reader chatter · conv

### AI / engineering (0.7)
- **Simon Willison's Weblog** · rss · `https://simonwillison.net/atom/everything/` · best practical LLM-tools blog · **YES**
- Import AI (Jack Clark) · rss · `https://jack-clark.net/feed/` · weekly AI research digest · **YES**
- OpenAI News · rss · `https://openai.com/blog/rss.xml` · official launches · **YES**
- Anthropic News · rss · `https://www.anthropic.com/rss.xml` · official Claude · conv
- Ars Technica · rss · `https://arstechnica.com/feed/` · deep tech/AI reporting · conv
- The Batch (DeepLearning.AI) · rss · `https://www.deeplearning.ai/the-batch/feed/` · Ng weekly AI news · conv

### Finance (0.5)
- Sifted · rss · `https://sifted.eu/feed` · European startup/fintech (FT-backed) · **YES**
- Finextra Headlines · rss · `https://www.finextra.com/rss/headlines.aspx` · fintech/banking · **YES**
- MoneySavingExpert News · rss · `https://www.moneysavingexpert.com/news/feed/` · UK consumer money (⚠ CF-flaky) · conv
- Be Clever With Your Cash · rss · `https://becleverwithyourcash.com/feed/` · UK personal finance · conv
- PensionCraft · rss · `https://pensioncraft.com/feed/` · UK investing/pensions · conv
- r/UKInvesting (small) · conv

### History (0.35)
- The Rest Is History (pod) · rss · `https://feeds.megaphone.fm/GLT4787413333` · perfect topical fit · **YES**
- History Today · rss · `https://www.historytoday.com/feed/rss.xml` · history magazine · conv
- Fall of Civilizations (pod) · rss · `https://feeds.buzzsprout.com/975519.rss` · landmark long-form · conv

### Film & TV / Star Wars (0.4, NO SPOILERS)
- /Film · rss · `https://www.slashfilm.com/feed/` · movie/TV news + trailers · **YES**
- ScreenRant · rss · `https://screenrant.com/feed/` · high-volume film/TV/SW · **YES**
- Collider · rss · `https://collider.com/feed/` · news + interviews · **YES**
- StarWars.com (official) · rss · `https://www.starwars.com/news/feed` · official (⚠ may be dead — validate) · conv
- r/StarWarsLeaks (small) · ⚠ leak/spoiler risk — suppress rules apply · conv

### Golf (0.45)
- Golf.com · rss · `https://golf.com/feed/` · tour/equipment/instruction · **YES**
- No Laying Up · rss · `https://nolayingup.com/blog?format=rss` · beloved golf media · HTML→conv
- bunkered · rss · `https://www.bunkered.co.uk/feed` · Scottish golf · conv
- Golf Digest · rss · `https://www.golfdigest.com/feed/rss` · majors/equipment · conv

### LEGO (0.45)
- Jay's Brick Blog · rss · `https://jaysbrickblog.com/feed/` · reviews/news/deals · **YES**
- New Elementary · rss · `https://www.newelementary.com/feeds/posts/default?alt=rss` · parts/technique · conv
- The Brick Fan · rss · `https://www.thebrickfan.com/feed/` · set news + deals · conv

### Travel / theme parks (0.4)
- Theme Park Insider · rss · `https://www.themeparkinsider.com/rss.cfm` · industry incl. European · conv
- Looopings (NL) · rss · `https://www.looopings.nl/feed/` · Dutch/European parks + Efteling · HTML→conv
- Coaster101 · rss · `https://www.coaster101.com/feed/` · coaster/park news · conv
- r/Efteling (small) · Efteling is a named-entity floor item · conv

### Music / synthwave (0.3)
- FiXT Neon (label) · rss · `https://www.fixtstore.com/blogs/news.atom` · darksynth releases · conv
- Iron Skullet · rss · `https://www.ironskullet.com/feeds/posts/default?alt=rss` · synthwave curation · conv

## C3. Top 20 highest-value additions

1. Juvefc.com · rss · `https://www.juvefc.com/feed/` · 0.85
2. Fabrizio Romano · bluesky · `fabriziorom.bsky.social` · 0.85
3. Get Italian Football News · rss · `https://www.getfootballnewsitaly.com/feed/` · 0.85
4. Nintendo Everything · rss · `https://nintendoeverything.com/feed/` · 0.9
5. GoNintendo · rss · `https://gonintendo.com/feeds/all.xml` · 0.9
6. 17th Shard · rss · `https://www.17thshard.com/forum/discover/6.xml/` · 0.55
7. Locus Magazine · rss · `https://locusmag.com/feed/` · 0.5
8. DC Rainmaker · rss · `https://www.dcrainmaker.com/feed` · 0.4
9. Marathon Handbook · rss · `https://marathonhandbook.com/feed/` · 0.4
10. Simon Willison's Weblog · rss · `https://simonwillison.net/atom/everything/` · 0.7
11. Al Jazeera All · rss · `https://www.aljazeera.com/xml/rss/all.xml` · 0.4
12. RTÉ News · rss · `https://www.rte.ie/feeds/rss/?index=/news/` · 0.5
13. Belfast Telegraph NI · rss · `https://www.belfasttelegraph.co.uk/news/northern-ireland/rss/` · 0.5
14. IGN Games · rss · `https://feeds.feedburner.com/ign/games-all` · 0.9
15. PlayStation.Blog · rss · `https://blog.playstation.com/feed/` · 0.9
16. Good e-Reader · rss · `https://goodereader.com/blog/feed` · 0.72
17. Android Police · rss · `https://www.androidpolice.com/feed/` · 0.75
18. Golf.com · rss · `https://golf.com/feed/` · 0.45
19. The Rest Is History · rss · `https://feeds.megaphone.fm/GLT4787413333` · 0.35
20. /Film · rss · `https://www.slashfilm.com/feed/` · 0.4

## C4. Bluesky starter set (zero → curated)

Handles are stable identifiers; add and let ingest validate. ✓ = verified handle.
- Football: `fabriziorom.bsky.social` ✓ (0.85); GIFN + an Italian football journalist (validate handles on add).
- Gaming: `wario64.bsky.social` ✓ deals/release news (0.9); Nintendo Life / a Nintendo insider (validate).
- Books: `reactorsff.bsky.social` ✓ (0.5); 17th Shard (validate).
- Fitness: DC Rainmaker / Stronger by Science (validate).
- AI/tech: `simonwillison.net` (custom-domain handle, validate); official Anthropic/OpenAI (validate).
- History: The Rest Is History (validate).

Seed the four ✓ handles first (Romano, Wario64, Reactor, + one AI voice), then expand — each is cheap to prune in Settings.

## C5. Notes — dead / risky / paywalled / rate-limit

- **Dead (do not re-add):** `brandonsanderson.com/feed/` (404, already disabled), Monzo blog RSS (404). `starwars.com/news/feed` may still 404 — validate; Star Wars News Net remains the working replacement.
- **Anti-bot 403s (feeds are real, block WebFetch's UA; usually fine server-side — validate on ingest):** 17th Shard, Locus, Grimdark, iRunFar, Stronger by Science, GameSpot, History Today, Theme Park Insider, bunkered, Black & White & Read All Over.
- **MoneySavingExpert:** RSS has a history of Cloudflare misconfig breaking it intermittently — expect occasional dead runs; Monevator + r/UKPersonalFinance anchor the domain.
- **Paywalled = headline/summary only:** The Economist, Sifted (metered). The Athletic has **no public RSS** — use Fabrizio Romano + Guardian for that layer.
- **Egress-blocked from the test environment (canonical, safe with validate-on-ingest):** Reuters, AP, Economist, Polygon, Ars Technica, Belfast Telegraph.
- **Reddit rate-limit (public `.rss` only — no API):** the Reddit Data API / OAuth is **not available and not an option**; Reddit is served solely via public `.rss`. Config already moved to per-subreddit tiers after 36 polls tripped Reddit's limit (`config.js` migrations); that tiering is permanent. Add new subreddits sparingly and as **tier:small** so they compete in the small pool rather than adding a dedicated poll each.
- **Feed-path quirks:** No Laying Up needs `?format=rss`; New Elementary + Iron Skullet are Blogger (`/feeds/posts/default?alt=rss`); Looopings `/feed/` served an HTML shell in-test — validate (r/Efteling covers the floor entity if dead).
- **No new domain key needed** — every candidate maps onto an existing `topic_weights` domain. Dedicated-Juventus, consumer-AI, and e-ink interests are served by _sources_ within `football`, `ai_engineering`, and `tech_devices`.
