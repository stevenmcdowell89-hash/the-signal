# The Signal — Section Reference

Detailed content rules, voice notes, and research guidance for each section.
Only read the sections appearing in this issue.

---

## Cross-cutting principle: Lens, not Filter (v8.19)

Applies to every recommendation section below (Shelf, Listening, The Ledger, The Itinerary, The Toolkit, Saga, plus Long Shelf and any Companion / Catch-Up picks in fixed sections):

- **50/50 Discovery vs. Reinforcement target.** Roughly half the picks reinforce something the reader already engages with; the other half surface something genuinely new. "New" = an app the reader doesn't use, a writer they haven't read, a label/artist they haven't heard of, a training method adjacent to but distinct from their current programme, a corner of personal finance they don't already follow, a podcast they don't subscribe to. Track in the chapter plan; writer self-audits via RT-23.
- **No drift-to-defaults.** If the last appearance of this section featured a specific brand/app/series (e.g. Todoist, Efteling, Cosmere), the next appearance should NOT default to the same. Anti-repetition rules in state file (`last_toolkit_app` etc.) catch the obvious cases; editorial judgement catches the rest.
- **The Long Shelf wildcard rule (2-of-8) is the floor, not the ceiling.** Other recommendation sections aim for similar discovery weight.

For news sections (World This Week especially): **major world stories are covered regardless of profile fit.** A war, election upset, regulatory change with broad consumer impact, or major scientific breakthrough lands in the issue whether or not it maps to a declared interest. See § Lens, Not Filter in editorial-spec.md.

## Cross-cutting principle: Borrowed angles, our voice (v8.28)

Applies to **every** section (replaces the old per-section "opinions mandatory / culture critic / write as a reviewer" lines — full rule in editorial-spec.md § Borrowed angles, our voice):

- **Confident voice, borrowed opinion — never invented.** Voice a take real commentators hold (found in research) as if it were ours; no citation duty, no robotic "X said Y"; a take you made up is cut. **Not everything needs an angle** — gaming releases, results roundups, evidence explainers are often better as plain facts ("study X found A, Y found B, it leans toward W"); answer any question you pose from the sources.
- **Length follows the material; facts come from the bundle.** As many words as the substance earns (no padding); state only what research found, and a stated result must have happened by the issue date.
- **Reader-profile invisibility holds:** the profile drives *selection*, never the prose (no "since you're into Malazan", "as a runner").

---

### Cover
Masthead, date, issue number, editorial hook headline, 6-10 topic tags. Ambient animation via CSS.

### Navigator
Visual card grid linking to each section. Top 1-2 cards use `.nav-card.lead` (two-column span with thumbnail). Section icons on each card. 8-14 cards total.

### The Letter (replaces the author-less Foreword, v8.35)
The signed editor's letter that opens the issue. A **named Editor speaking in the first person** ("I") states **the week's thesis** and **connects the dots across domains** — what the week added up to, the threads that rhyme. ~120–200 words, signed "— The Editor". First-person Editor voice is explicitly allowed (the reader stays invisible — never "you"/"your son"/profile callbacks; see Gate 1A's split). It is the opening *movement*, not an essay: say the thesis, draw two or three threads together, hand off to the issue. Keep the `.foreword` markup and its automatic drop-cap; the navigator card reads "The Letter". No "meanwhile" / "elsewhere" filler.

### The Week in Numbers *(fixed — the personal stat strip, v8.36)*
A small, compact **personal** stat strip near the top of the issue (after The Letter). A handful of numbers about *the reader's* week — not the news. Uses the existing `.stat-bar` / `.stat` component vocabulary (compact, not a full section; wrap in `.week-in-numbers`).
- **Garmin miles + current training block** (from state `training_phase`) — e.g. "31.2 mi · Base block, wk 6".
- **FPL rank** — the reader's Fantasy Premier League overall rank (and movement if known).
- **The Juventus result** — the week's Juve scoreline.
- **One money number** — a single figure from The Ledger's world (a savings rate, an Etsy month, an ISA milestone).
- 4–5 stats, quietly personal. If a number genuinely isn't available this week, drop that stat rather than inventing it.
- **Distinct from the Colophon's "Issue in Numbers"** (§ End-of-Issue Colophon in the spec): that block counts *the issue* (words, sections, links, images); this one counts *the reader's week*. Both ship every issue; never merge them.

### The Long Shelf — Worth Your Time
6-8 recommended reads/listens/watches with linked titles, source, and one-sentence hook. Two-column grid. 2 of 8 items should be genuine wildcards outside the magazine's usual coverage areas. Each item's one-sentence hook should sell the content on its own merit — not explain why it was selected for this reader.

**Wildcard discipline:** 2 of 8 items MUST be wildcards (outside the magazine's usual coverage areas). Mark them with `wildcard: true` in the chapter plan.

### The World This Week
Hero image. White background, rose accent.
- **One or two lead stories depending on the week.** If one story is genuinely massive (war breaks out, leader assassinated, major treaty), it gets the section to itself as a single lead. Most weeks, run two properly developed stories (300-500 words each) -- the world rarely has just one thing worth knowing about. The reader should come away knowing 3-4 things that happened, not just one.
- The Angle box only for genuinely significant stories
- **Also This Week: 4-6 items, not throwaway one-liners.** Each Also item gets 2-3 sentences minimum: what happened, why it matters, and a link. A one-liner that nobody remembers five minutes later isn't worth including. Cut the count and increase the quality.

**Considered-piece backbone (v8.27, inverted v8.34):** World This Week runs one considered piece (400–700 words) that passes the two-factor test (did it move this week + does it add the layer the daily couldn't — the week's arc tied together, or the combined picture across piecemeal items) — synthesis, a roundup with a named layer, an angle, or a feature. The Catch-Up roundup is **optional grounding**, not exhaustive coverage — the *other* interesting world news worth a line (every item what/why/link), with one-line safety-net headlines for the week's majors so nothing big is dropped. An optional Companion (250–450 words, distinct topic family — if the Lead is Iran, the Companion can't be Iran) only when there's a genuine second deep story. Ongoing-story tracker boxes are *in addition*. The Starmer ×3 failure was a holding-pattern story leading on recap — don't repeat it.

**Ongoing Story Tracker**
When a single topic has led The World This Week for 2 consecutive weeks, it graduates from headline coverage to a dedicated **"Ongoing"** subsection within World This Week. Rules:
- **Position:** after the new lead story, before Also This Week. Visually distinct — use a `.sidebar` or bordered box with the story label (e.g. "Iran War — Week 7", "Ukraine — Month 26").
- **Content:** factual updates only. What happened this week, key numbers, status changes. No new editorial angles on why it matters — that was established when it first led. Think situation report, not op-ed.
- **Space:** give it as much space as the story needs to cover the week's developments thoroughly. A quiet week might be 200 words; a week with military, diplomatic, and economic threads running simultaneously might be 800. Use paragraphs, stat bars, big-numbers, and links to primary sources. The constraint isn't word count — it's that the tracker doesn't set the tone for the section. It sits in its box, covers everything factually, and the new lead story above it sets the editorial direction for the week.
- **The issue can grow to accommodate it.** An ongoing tracker doesn't steal space from the new lead or other stories — the issue expands slightly.
- **Promote back to headline** when there's genuine big news. When promoted, the tracker merges into the headline coverage for that week -- no tracker box alongside a headline piece. The following week it returns to the tracker unless something even bigger happens.
- **The bar for re-promotion rises exponentially.** Each consecutive week a story leads makes the next promotion harder to justify. Week 1-2 as lead: normal editorial judgment. Returning to lead after time in tracker: must be the kind of development that would lead any newspaper. Returning to lead two weeks running: needs a genuine paradigm shift (ceasefire signed, capital falls, intervention by a new country). Three in a row: the story must have fundamentally changed in nature. Four or five consecutive headlines: the world had better have ended the preceding week. If in doubt, it goes in the tracker. There is always other news.
- **Demote to Also This Week** when the story becomes a low-level stalemate, shrinks in significance, or stops producing meaningful weekly developments. It can graduate back to Ongoing or Headline if things change.
- **Drop entirely** when the story is resolved or no longer has weekly developments worth reporting.
- **Multiple ongoing stories can coexist.** If two or three running stories are all in tracker mode, they each get their own labelled box. They stack after the lead.
- **This pattern applies to any running story** — wars, political crises, drawn-out negotiations, pandemics, ongoing tech antitrust cases, anything. Not just world news — if a tech story (e.g. a major antitrust trial) or sports story (e.g. a drawn-out transfer saga) has been leading its section for 2+ weeks, the same pattern applies within that section.

**Track in state file:** add `ongoing_stories` array. Each entry: `{ "topic": "Iran War", "section": "world", "weeks_as_lead": 4, "weeks_as_ongoing": 2, "last_status": "ongoing" }`. Update weekly.

### Pixel & Byte *(fixed — the dedicated gaming section, v8.27)*
Gaming + LEGO. Warm background, ember accent. **Consumer tech / AI / apps moved to The Toolkit** — Pixel & Byte is now gaming's own home.
- **Scope:** Nintendo Switch 2, Steam Deck / Steam Machine, GeForce Now, high-quality tablet games, **plus generalist** — the biggest game of the year gets covered even if it's not on Switch.
- **Floor (the section minimum, write it every week):** *what came out this week, plus highlights of the next month* — with **real explainers, never namedrops.** "Namedropped three game releases and moved on" is the exact failure this section exists to prevent: tell the reader what each one is, why it matters, and link it.
- **Upside on top of the floor (the Lead):** a *new* rumour-with-analysis, or a release genuinely worth playing — the angled Lead that passes the two-factor test. Months-old rumours the reader already knows (the CIRQA-leak failure) don't qualify.
- **LEGO folds in here** as an occasional "play"-cluster beat (new set announcements, build reviews, retiring sets). Use "Family Picks" sidebars — don't sprinkle "your son will love" through prose.
- **Catch-Up roundup:** 4+ gaming items, each with what/why/link.

**Considered-piece backbone (inverted v8.34):** the considered piece is either an angled gaming Lead (300–500 words) **or** the curated releases-this-week-plus-next-month roundup written with real explainers — a roundup with a named layer (the gaming floor above), authored *as the Lead*, not as bare catch-up. The Catch-Up roundup (new rumours, smaller items) is optional grounding on top. A Companion is optional — only if a second distinct gaming topic genuinely earns a full piece.

### The Desk *(the service department — umbrella for four service columns, v8.36)*

The Desk is the restored **service department**: the part of the issue whose job is to help the reader *do* something this week, not just know about it. It groups **four service columns** — **The Session** (fitness), **The Ledger** (money/finance/fintech/side-hustle), **The Itinerary** (travel/parks/NI-local), **The Toolkit** (tech/Android/e-ink) — and **1–2 run per issue**, chosen by which domain is most overdue *and* has genuine, actionable service news this week. A domain with nothing to act on yields rather than padding to appear.

- **Each column keeps its own brief and content rules** (the four briefs follow / precede this one: The Session, The Ledger, The Itinerary, The Toolkit). The Desk is the umbrella, not a replacement for those rules.
- **The mandatory "Do This Week" pin.** Every Desk column that runs **ends on exactly one "Do This Week" pin** — one concrete, do-it-this-week action, with the *why* attached and the **selection criteria stated, not vibes**. Name the specific thing and say why *that* one.
  - **Good:** *"Move your emergency fund to Chase Saver at 4.75% AER — it's the top easy-access rate right now with no intro-bonus cliff."*
  - **Bad:** *"Consider a high-interest savings account."* (no named product, no criterion, not do-it-this-week).
  - The Session's pin might be a specific session/protocol to run this week; The Itinerary's a specific booking/window to act on; The Toolkit's a specific app/setting to install or change. One pin per column, always the last element.
- **Markup:** a `.do-this-week` block (see `references/component-contracts.md`). The pin is service, not an aphorism — exempt from the one-aphorism-per-issue cap, and it is *not* the column's Lead.
- **Placement:** the running columns sit together as the service department, in the "act on it" cluster before The Threads and the close (see § Rotation Mechanics → Placement in the spec).

### The Toolkit *(Desk service column — tech; yields strictly, v8.36)*
Tech & tools: consumer tech, consumer AI, apps, tablet productivity, digital workflows. Light blue-grey background, cyan accent. **A Desk service column (v8.36) — was a fixed-but-yields section; content unchanged. Absorbs the consumer-tech + AI that used to live in Pixel & Byte, alongside its existing apps/productivity beat.** Closes on a **"Do This Week" pin** (see § The Desk).
- **Runs only when it has real service news.** It is **expected to disappear regularly** — yield entirely when the week is thin (roughly appears every other issue). Do NOT pad it to appear.
- **Catch-up rule on return:** cover the entire gap since its last appearance (track `last_appeared`), not just the past 7 days — so yielding batches a fortnight of tech news into one good roundup rather than dropping it.
- **The Lead stays a discovery** — "a tool/app/feature worth finding", not an app-store roundup. The **Catch-Up roundup carries the consumer-tech news** (hardware, AI products, app updates), each item what/why/link.
- **Consumer-only test for AI items.** This is a CONSUMER section, not work/dev/enterprise. Every AI item must pass: "would a non-developer reader actually encounter or use this?"
  - **In:** consumer-facing AI (ChatGPT / Claude / Gemini features, image/video generation, AI in tablets/phones, AI in everyday apps like Spotify / WhatsApp / Google Maps, AI search (Perplexity, SGE), on-device AI in Pixel / Xiaomi / iPhone, consumer AI hardware, AI in games or streaming).
  - **Out:** developer tooling (Copilot / Cursor / IDE integrations, code review, DevOps), enterprise AI (business workflow automation, AI ops/governance, CRM/ERP/BI AI, customer-service AI, compliance/legal/HR AI), pure-research announcements (benchmarks, paper releases) unless they ship as a consumer product the same week. Rule of thumb: if it would feel at home in an Engineering Digest, it doesn't belong.
- **Consumer tech & wearables hardware:** Pixel/Xiaomi/e-readers; wearable *hardware/firmware/app* news (Whoop, Garmin, Oura) belongs here as consumer tech. Fitness *training* angles off that data belong in The Session.
- Reader uses: Xiaomi Pad (Android), Todoist, Perplexity, split-screen productivity. Builds (but doesn't personally use) Notion templates — that's The Ledger's territory.
- **Anti-repetition:** same app/tool cannot anchor two consecutive Toolkit appearances. Track `last_toolkit_app` in state.
- Good sources: r/Android, r/Todoist, Product Hunt, 9to5Google, The Verge, XDA, DC Rainmaker (wearables).

**Considered-piece backbone (inverted v8.34):** the discovery Lead (300–500 words) is the considered piece, with the period's consumer-tech/AI news as optional Catch-Up grounding. Companion optional. If a return week has only undifferentiated catch-up and no real discovery to make, the section **yields** (its strict-yield rule already expects this) rather than running a roundup to fill the slot.

### The Touchline
**Data first, then narrative.** Dark background, green accents.

**The Touchline is a flexible sports section, not a fixed football roster.** Its content should adapt to whatever is most compelling in sport that week. Nothing has a guaranteed slot — everything earns its space.

**Team allegiance:** The reader supports Juventus. Do not assume support for Northern Ireland, any Premier League club, or any other team. Coverage of other teams (including NI) is fine when they are the biggest story of the round, but never frame it as "our" team or assume the reader has a rooting interest.

**Priority hierarchy (what leads the section):**
1. **Major tournament in progress** (World Cup finals, Euros, Copa América) — dominates the section. Domestic leagues drop to one-liners or are omitted.
2. **Major non-football event** (Ryder Cup, golf major, Olympics, rugby World Cup, F1 title decider) — can take the lead and push football into a secondary role. Give it the space it deserves.
3. **Structural / governance / business stories in any sport** — LIV folding or merging, Super League rumblings, Saudi PIF moves in sport, F1 ownership changes, Premier League PSR rulings, doping scandals, league finance crises, major sanctions, Olympic host decisions. These can lead the section when the story is genuinely big, even with no on-field action attached. Treat them as Touchline material first — they are sport stories, not business stories.
4. **Active qualifying campaign** (WC qualifiers, Euro qualifiers) — leads over domestic leagues. Domestic only if genuinely significant (sacking, title decided, record).
5. **CL/EL knockout stages** (QF onward) — lead over domestic. Group stages share space.
6. **Normal domestic weeks** — Serie A and PL share the section.

**Football is the floor, not the default.** Domestic football fills the section when nothing higher up the hierarchy has earned the lead. A quiet domestic week reads as "this is what happened" — results, table, one or two notes — and that is fine. Do not inflate routine football into the headline if a tournament, major non-football event, or structural sport story exists.

**Demotion principle.** When a story from priorities 1–3 takes the lead, football compresses cleanly: condensed results, the table, a one-line note on anything genuinely significant (sacking, title decided, record). Don't try to give football equal weight on those weeks — the section is finite and the lead has earned its space.

**Search must reach beyond football every week.** Even on weeks where the priority hierarchy looks football-shaped, run a quick scan for: golf (PGA / DP World / LIV / majors / Ryder Cup), F1, Olympics buildup or news, rugby (Six Nations / World Cup / URC), tennis (Slams / Masters), and structural/governance stories across all sports. If something there has earned headline space under priorities 2 or 3, it leads.

**European football beyond Serie A/PL** (La Liga, Bundesliga, Ligue 1, etc.) — not included by default. Surface only when something is genuinely compelling: a thrilling title race, a historic result, a major sacking, a story with wider significance. Routine matchday results from other leagues don't make the cut.

**Flexible space within the section:** Sub-topics expand and contract based on what happened. A Ryder Cup Sunday can take 70% of the section with football condensed to quick results. A LIV-folds week, an Olympic host vote, or an F1 ownership shake-up can do the same. A quiet international break can mean a shorter Touchline overall. The section should never exceed ~30% of the total issue length, but content moves freely within it.

- Sparklines for form, position-change indicators
- **Serie A ≥ PL** in coverage depth during normal domestic weeks. Cover the whole league — title race, relegation, stories — not just Juve. **Serie A table must show the full table or at minimum top 10 + relegation zone, not just the top 5.** PL table same standard.
- Golf majors and other major sporting events get proper coverage when in season — they can lead the section
- Football reads like editorial, not match reports — the reader already knows the scores
- Image montage for match photos

**Considered-piece backbone (v8.27, inverted v8.34):** one considered piece (the most compelling sport story that passes the two-factor test — lead with the angle, never a play-by-play recap of a match the reader watched). The Catch-Up roundup is optional grounding, but **when it runs it must carry the football the reader actually wants** — transfer rumours and confirmations, squad/World-Cup announcements, what's coming up — plus one-line safety-net results for the week's majors. The old failure was spending the whole section on "Arsenal won" and dropping the transfer catch-up entirely. An optional Companion: when the Lead is football, a Companion must be a non-football sport (golf, F1, rugby, tennis, snooker, governance/structural); when the Lead is a Priority-2/3 non-football story, a Companion may be football.

### Screen & Sound
Film, TV, streaming, Star Wars (always search). Dark purple background, neon accent.
- **Culture-desk voice, borrowed takes** (cross-cutting rule): synthesise the views critics actually hold; never invent a verdict.
- Opinions are mandatory — not press-release summaries
- Rating dots for reviews
- Card stack for Quick Reviews
- Collapsible sections for spoiler content
- **The Release Radar (mandatory + enforced, v8.30):** 15-20+ items across ALL categories (film, TV, games, LEGO, tech, books, music; **≥4 categories must appear**). Sub-sections: Now Showing, Coming Soon, Leaving Soon, Also Streaming. Category dots for visual scanning. **Items within each sub-section must be in chronological date order** (earliest first for Coming Soon, most recent first for Now Showing/Also Streaming). Each item carries a date and a `status` (`happened`/`upcoming`, reusing the v8.29 tag). It is its own `release_radar` chapter rendered right after Screen & Sound; `validate-chapter-plan.py` hard-fails a weekly that omits it or ships fewer than 15 items / 4 categories. (It used to be unenforced "tail content" and silently dropped — that gap is now closed.)
- "For the Kids" sidebar when relevant
- **No overlap with On the Radar** — Release Radar covers product/media releases only

**Considered-piece backbone (v8.27, inverted v8.34):** one considered piece (a review or culture-critic take that passes the two-factor test) with an **optional** Catch-Up roundup of the week's releases/news (what/why/link) grounding it. The Release Radar is in addition. An optional Companion is forbidden from sharing the Lead's franchise.

**Sub-format: Director's Cut (monthly).** Every 4th standard weekly, the Screen & Sound Lead runs in Director's Cut mode — a 550-750 word essay on a show, film, director, or arc rather than the week's news beat. Voice: culture critic, not news reviewer. Examples: "What Andor Season 2 understood that the prequels didn't" / "Why Severance's pacing is the show's secret weapon" / "The Coen Brothers' grammar of disappointment". Companion remains standard (250-450 words, distinct topic family, may carry the week's main beat the Director's Cut displaced). State file tracks `last_directors_cut_date`; planner-side hard rule `weeks_since_last_directors_cut >= 4`. Tagged in chapter plan as `sub_format: "directors_cut"`. Optionally marked in the rendered section header with `<span class="sub-format-tag">Director's Cut</span>` inside `.section-label`.

### The Shelf *(rotating — every 2-3 weeks)*
Books and music. Dark brown background, gold accent.
- **Owns books (primary).** Podcasts, audio drama, and music live in **Listening**; The Shelf may mention a notable music release in passing when Listening isn't running, but the dedicated music read is Listening's.
- **Catch-up rule:** when The Shelf appears, research covers the entire period since it last appeared (not just the past 7 days). Check state file for `last_shelf_date`. No good book news or music release should fall through the cracks.
- **Review like a book column, borrowed takes:** premise, tone, what makes it worth reading — synthesised from real reviews, not invented. **Real, named titles or the section yields (v8.28)** — never write about empty categories or invent book names; if research found no real books, The Shelf doesn't run this week.
- Books: features, recommendations, book cards with rating dots. Both epic series AND short fiction. Occasional narrative history (Dan Jones, Tom Holland, Mary Beard).
- **CRITICAL: No spoilers.** Never reveal plot twists, character deaths, endings for any book. This rule is absolute but invisible — never announce compliance with it.
- Music: light-touch when Listening isn't running. Synthwave/retrowave or a notable release noted in passing — the deep music read lives in Listening.

### Listening *(rotating — every 3-4 weeks; absorbs the old Listen + Channel, v8.27)*
Podcasts + audio drama + music. Warm slate background, brass accent.
- **Owns podcasts, audio drama, and music.** Merges the old The Listen (podcasts/audio drama) and The Channel (synthwave/soundtracks/retro). On a given week it leans whichever way the news pushes — a podcast-and-audio-drama issue, or a music issue — but the section is one home for "things to listen to".
- **Podcasts/audio drama:** episode-of-the-week picks, audio drama recommendations, podcast deep-cuts (forgotten gems, niche shows), one-offs from the reader's known feed (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions).
- **Episode specificity.** Flag specific new episodes by title and date — never the show in the abstract. "What Went Wrong: 'The Day the Music Industry Sued Its Customers' (released 14 May)" not "What Went Wrong covers tech disasters".
- **Music:** new synthwave/retrowave releases (album of the period; label news from FiXT / Lakeshore / Aphasia / Lazerdiscs), soundtrack picks (film/game, recent or evergreen), retro-listening (a 70s/80s album having a moment, a reissue worth knowing). **Embed the music itself** — Bandcamp/Spotify/YouTube links, not the article about the music.
- **Only describe content you can verify.** Don't invent episode content. If you can't confirm what an episode discussed, link it without a content summary.
- **Audio drama recs cross-reference with The Shelf.** When an audio drama adapts a book also reviewed in The Shelf, cross-link.
- **Catch-up rule:** research window is since Listening last appeared. Track in state file `the_listening.last_appeared`.
- Good sources: Apple Podcasts Charts (UK/IE), Pocket Casts Discover, Audible originals, BBC Sounds; Bandcamp Daily synthwave tag, RetroSynth, /r/outrun, /r/synthwave, /r/SoundtrackCollection.

### The Session *(Desk service column — fitness; the single home for all fitness, v8.36)*
Sourced fitness feature. Light green background, orange accent. **A Desk service column (v8.36) — was a fixed fitness section; content unchanged. Absorbs the old Workshop (home-gym gear, equipment & recovery-tool reviews) and The Lab (training-science deep dives) as rotating *angles within* Session** — fitness now has one home, not four (Session / Workshop / Lab / a Pixel & Byte wearable lead). On a given week the Session can be a training feature, a gear review, or a science deep-dive — rotate the angle (track `last_session_topic`). Closes on a **"Do This Week" pin** (see § The Desk) — e.g. a specific session, protocol, or deload to run *this* week, with the why and the criterion stated.
- **Fitness-desk voice, evidence-led:** state what the studies actually found ("X found A, Y found B, it leans toward W") — often better as plain findings than a baked-in angle; answer the question you pose. No invented conclusions; sources are Stronger by Science / Barbell Medicine / Examine / Galpin tier.
- **Check state file `training_phase`** to know what's currently relevant. Research topics that align with the current phase — this sharpens research without leaking into prose.
- **Rotate across these topics, prioritising what's relevant to current phase:**
  - Hypertrophy-focused programming in a deficit (double progression, RPE management, volume landmarks, when to deload)
  - Concurrent training science (combining lifting and running without interference)
  - Gymnastics rings training (progressions, stabilisation benefits, programming ring work alongside barbell)
  - Kettlebell conditioning (complexes, EMOM, Dan John, GS-style work, finisher design)
  - Running science (zone training, lactate threshold, 10k race prep, easy running benefits)
  - Recovery and mobility (Pliability-style routines, foam rolling science, sleep as recovery tool)
  - Wearable data (Garmin HRV, Body Battery, Training Readiness, resting heart rate trends, recovery optimisation)
  - Nutrition for recomposition (protein timing, deficit management, calorie cycling, muscle retention during cuts, high-protein meal strategies at 180g+ daily)
  - Landmine training (an underrated tool — Meadows rows, Viking press, lateral raises)
  - Home gym programming (making the most of barbell + rack + KBs + rings, no dumbbells)
- **Research context (invisible in prose):** Reader trains 6-7 days/week. Hypertrophy rep ranges (6-10 compounds, 10-15 accessories). Double progression model. Home gym: barbell up to 100kg, squat rack, landmine, competition KBs 12-32kg, gymnastics rings, slant board, no dumbbells. Currently in a ~500 kcal deficit cutting from ~110kg to 100kg target. 10k race May 3, then shifts to higher-volume fat loss through June 30. Post-holiday: hypertrophy at maintenance/surplus.
- Only include when there's genuinely useful sourced content — omit entirely if nothing found.
- **Good sources:** Stronger by Science (top tier — Greg Nuckols, Eric Trexler, Eric Helms), StrongFirst, Dan John, Outside Online, Runner's World, T-Nation (training only), Alex Viada, Barbell Medicine, Andy Galpin, Examine.com (nutrition), Jeff Nippard (training science), Layne Norton. NOT Men's Health, NOT bodybuilding, NOT Renaissance Periodization (RP), NOT Mike Israetel.
- No generic advice ("stay hydrated", "warm up properly").
- **Good Session topics:** concurrent training (lifting + running without interference), rate of loss and muscle retention during a cut, how to interpret Garmin training readiness and HRV trends, mobility routines for runners, protein timing and distribution, the science of deload weeks, progressive overload with kettlebells at home, running economy and zone 2 benefits, managing fatigue across multiple training modalities, fitness gear and tech (running shoes, kettlebells, home gym equipment, wearables, recovery tools — only stuff relevant to the reader's actual training), home gym setup and equipment reviews (reader is building out a home gym — currently has competition KBs, dip bars, slant board, resistance band; interested in expanding).

**Considered-piece backbone / deep note (v8.27, inverted v8.34):** the considered piece is the Session Lead (400–500 words) + a Companion "Also worth reading" deep note (200–250 words) on a different training-topic cluster (Session is the one section where a Companion is still strongly encouraged, since it now carries the absorbed Workshop gear angle and Lab science angle). A light Catch-Up of fitness-gear/wearable-data notes is optional grounding and can stand in for the deep note on a thin week. **Same cluster cannot anchor two consecutive Session Leads** — track in state-file `last_session_topic`.

### This Week in History *(rotating — every 2-3 weeks)*
Warm parchment background, gold accent.
- One featured event (150-300 words) + 3-4 "Also This Week" one-liners using timeline component.
- **Strong preference for pre-WW2 history.** Ancient, medieval, Roman, classical, or early modern. WW1/WW2 only for truly major anniversaries. Post-WW2 is the last resort.
- Connect to current events when resonant.
- **Links are essential here.** The featured event must link to its Wikipedia article — Wikipedia is the preferred starting point for history rabbit holes. Additional links (long-form pieces, podcast episodes, documentaries) are welcome but Wikipedia comes first. "Also This Week" one-liners should each link to their Wikipedia article too. History is the section most likely to make the reader think "I want to know more" — give them somewhere to go.

**Sub-format: A Closer Look (every 6 weeks).** Every 6 weeks (when History is scheduled AND `weeks_since_last_closer_look >= 6`), the section runs as A Closer Look — a single 600-800 word narrative deep dive on one event or figure, replacing the standard "one featured event + 3-4 also-this-weeks" pattern. Pre-WW2 strongly preferred — this format is ideal for ancient/medieval/early modern. Wikipedia link mandatory; additional sources welcome (long-form articles, podcast episodes, primary sources). Voice: narrative historian — tell the story, ground it in specifics, surface what's surprising. Not encyclopedic. Examples: "The Anglo-Zanzibar War: How a 38-Minute Conflict Set the Edges of Empire" / "Hatshepsut and the Erasure: What Happened to Egypt's Lost Pharaoh" / "The Year Without a Summer: 1816 and the Origin of Frankenstein". State file tracks `last_closer_look_date`. Tagged in chapter plan as `sub_format: "closer_look"`. Validator enforces single-item structure (no `also_items`) and 600-word floor.

### The Ledger *(Desk service column — money; every 3-4 weeks, v8.36; was "Money")*
The money domain — personal finance, consumer fintech, and the side-hustle. **A Desk service column (v8.36) — the rebrand of the former "Money" rotating section; streams and content identical, new name (the CSS `.ledger-section` / `--ledger-*` tokens already exist).** Warm cream / amber accent. Three streams that lean whichever way the week pushes:
1. **Personal finance & investing** (the old Long Game): editorial takes on saving, investing, ISA/pension news, market trends explained simply, interesting finance reads. UK-relevant (ISAs, pensions, Vanguard, Trading 212). Not financial advice; not day-trading or crypto speculation — long-term, sensible perspective. Sources: Monevator, r/UKPersonalFinance, Money Saving Expert, FT (free), This Is Money.
2. **Consumer fintech** (the old Wallet): Monzo / Revolut / Starling features, cashback cards, switching deals, fintech launches. Practical — "Revolut launched X, here's whether it's worth it" — not industry analysis. Sources: r/UKPersonalFinance, MSE forum, Head for Points, the banks' own changelogs.
3. **Side-hustle / digital products** (the old side-hustle beat): Etsy seller trends, Notion/Kindle Scribe template ideas and strategy, passive income, print-on-demand. The reader builds templates to sell (he doesn't use Notion himself). Frame as creative/business-building, not corporate or "work content". No MLM, no crypto schemes, no get-rich-quick. Sources: r/Etsy, r/passive_income, indie-maker communities, Starter Story.
- **It's all one domain** — don't run all three streams every time; pick what actually has news. Research window: since The Ledger last appeared (catch-up rule). Renders as `.ledger-section` (CSS `--ledger-*` tokens already exist); the state-file key stays `the_money.last_appeared` for continuity — the rebrand is reader-facing.
- **Closes on a "Do This Week" pin** (see § The Desk) — a single named, criteria-stated money action (a specific account/rate to switch to, a specific ISA move to make this week), not "consider high-interest savings".

### The Itinerary *(Desk service column — travel; every 3-4 weeks, more near trips, v8.36; was "Places")*
Travel, theme parks, and Northern Ireland local. **A Desk service column (v8.36) — the rebrand of the former "Places" rotating section; content identical, new name (the CSS `.itinerary-section` / `--itinerary-*` tokens already exist).** Warm sand background, coral accent. Owns all travel/parks/NI content when present; one-liners in On the Radar when absent.
- **Three streams, weighted by what's available:**
  1. **Travel abroad:** destination profiles, flight deals, European family trips, logistics.
  2. **Theme parks:** Disney Parks, Efteling, Beekse Bergen, other parks worth knowing about.
  3. **NI local (the old Local):** hidden gems (a forgotten walk, an underrated café, a quirky museum, a coastal find), unusual family events (search forward 2-4 weeks), light NI context (an NI-set book, artist, or history piece). **Test:** would a NI local find this genuinely surprising or useful? Excludes the zoo, leisure centres, anything on page one of "things to do in Belfast".
- **Frequency:** every 3-4 weeks normally; increases to every issue (or every other) when a trip is approaching — check state file `upcoming_trips`.
- **Research:** since The Itinerary last appeared, plus 2-4 weeks forward for events. State-file key stays `the_places.last_appeared` for continuity (rebrand is reader-facing). Sources: Disney/Efteling/Beekse Bergen official, European travel deals; Visit Belfast, Discover Northern Ireland, r/northernireland, Belfast Live / Irish News for events, local food blogs.
- **Closes on a "Do This Week" pin** (see § The Desk) — a specific, criteria-stated travel action (a booking window opening, a park date to reserve, a specific NI event to go to this week).

### The Saga *(trigger-driven — NO cadence timer, v8.27)*
Lore deep dives — Star Wars universe, fantasy book worlds, show analysis. Deep purple background, antique gold accent. The long-form universe-writing read that keeps Screen & Sound current-week and The Shelf focused on what to read next.
- **Runs on a peg, not a clock.** It is NOT scheduled by cadence and is NOT deficit-promoted. It appears only when there is a *reason*:
  - **Public peg** the researcher finds: a finale aired, a new book/season in a series the reader follows released, an author AMA.
  - **Private peg** the reader supplies: a `currently_reading` / `currently_watching` note in state (the researcher reads it as a peg source), or a manual trigger ("run a Saga on the Cosmere"). The pipeline cannot know what the reader is personally reading/watching — the same boundary that makes Next and Lookahead manual-only.
  - If neither peg is live, The Saga simply doesn't run that week.
- **Three content modes:**
  1. Star Wars universe deep dives (Maul's arc across Clone Wars / Rebels / Mandalorian; lore connecting recent shows to older canon).
  2. Fantasy book-universe lore (Cosmere magic systems, Malazan worldbuilding — **never plot, never characters' fates, never endings**).
  3. Show analysis with optional spoilers (an essay on a finished arc; spoilers behind a `<details>` collapsible labelled "Spoilers below").
- **Spoiler rule is absolute.** Plot, deaths, endings, betrayals, twists — forbidden in book content, behind `<details>` in show content. Violation = Gate 1 hard fail.
- **Tone is essayistic, not breathless** — a Sunday-magazine essay, not a fan-blog hot take. Cite lore sources (canonical databanks, author interviews, episode references).
- Good sources: Wookieepedia, official Star Wars databank, author Q&As (Brandon Sanderson AMAs, Steven Erikson interviews), Tor.com, /r/cosmere, /r/Malazan, /r/StarWars.
- Track in state file `the_saga.last_appeared` (for "when did it last run", not for cadence scheduling).

### The Threads *(fixed — the continuity engine, v8.36)*
The reader-facing continuity section: the magazine's "previously on…". Built off the state file's `ongoing_stories`, **extended beyond World** to named sagas across all domains, plus the reader's own life-threads. Part of the closing movement, placed just before On the Radar. Warm neutral ground; uses the `.the-threads` > `.thread` markup.
- **Two kinds of thread:**
  1. **Named sagas** (`.thread-saga`, from `ongoing_stories`, any domain): an Iran-endgame thread, a Serie A / Antonelli title-run thread, a long-running show arc, a Switch-2-ecosystem thread. Each is a few lines — a "previously on / where it stands now" recap — plus a link.
  2. **Life-threads** (`.thread-life`): the reader's own ongoing arcs — the marathon build from state `training_phase` ("Week 6 of the block; long run up to 18 miles"), the upcoming trip from state `upcoming_trips` (the Efteling trip). Recapped the same way.
- **`ongoing_stories` is now DUAL-USE (v8.36).** Historically it fed *only* the Topic-Lock suppression backstop (keeping a heavily-rotated story out of the Lead). **That suppression use is fully intact and unchanged.** The Threads additionally reads the same records and surfaces them as a reader-facing asset. Same data, two jobs: (a) topic-lock suppression backstop, (b) The Threads' data source. `training_phase` + `upcoming_trips` additionally feed the life-threads. Suppressing a topic from the Lead does **not** remove it from The Threads — a cooling-off story is exactly what the reader wants recapped.
- **Voice:** situation-report + "previously on" recap — factual, compact, each thread a few lines and a link. No invented angle or new opinion; it is a recap, not a Lead, and carries **no "Do This Week" pin** (that is the Desk's job).
- **Typically 3–6 threads.** Pick the live ones; don't pad. A thread with no genuine development since last issue can be held.

### On the Radar — Coming Up
8-10 upcoming items: fixtures, sporting events, local NI events, parkruns, dates to know, personal milestones, deadlines, cultural events. Compact grid with date + event + detail. Category dots.
- **No overlap with Release Radar.** Product/media releases go in Release Radar. This is for everything else.
- When The Itinerary is absent, parks and travel news can appear here as one-liners.

**Mandatory links + "Why it matters" lines:** Every item links to its canonical source. The 2-3 most important items per issue get a 10–15 word "Why it matters" line below the date+event line.

### Footer
Masthead echo, issue info line.

### Topic Families & Recent Leads

**Topic families** are closed-vocabulary tags on every Lead (and any optional Companion) piece in the chapter plan. Used by the planner-side validator to enforce Lead ≠ Companion topic family within a section *when a companion is present*. Used by the Gate 1 grep to enforce the recent-leads bar on repeat-promoted ongoing stories.

The full enumeration lives in `references/chapter-plan-schema.md`. Adding a new family requires spec amendment.

**Recent leads (sliding-window cap, v8.18).** Every time a topic family anchors any fixed section's Lead, the date is appended to that topic's `lead_history` array in state. `recent_leads` = count of entries within the last **26 weeks** of the current issue date. A topic with `recent_leads >= 3` requires `weeks_since_last_lead >= recent_leads × 2` before it can lead again. Older entries age out of the window automatically, so a topic that goes quiet for 6 months becomes promotable again without manual override.

**The Ledger ↔ The Session boundary** is enforced: The Ledger's finance content is finance only; fitness deep-dives go to The Session. Both are Desk columns (v8.36), but the domain boundary holds. Cross-classification fails Gate 2.

---

---

## Component Palettes for Rotating Sections

### Component Palettes for Rotating Sections

| Section | Primary Components | Why |
|---|---|---|
| **The Toolkit** *(Desk column — tech)* | `.also-cards` (app/tech picks), `.compact-grid` (2 reviews side by side), `.compare-panel` (product A vs B), `.sidebar-float` ("What it replaces"), `.entry-stat` ("3M downloads"), **`.do-this-week` (closing pin)** | Card-based layout suits app/tech discovery; compare panels for hardware. Every Desk column closes on a `.do-this-week` pin |
| **The Shelf** | `.book-card` / `.book-grid`, `.card-stack`, `.rating`, `.pull-quote`, `.collapsible` | Already well-defined from weekly version |
| **This Week in History** | `.timeline`, `.year-badge`, `.img-offset`, `.sec-opener` | Already well-defined from weekly version |
| **Listening** *(podcasts + audio drama + music)* | `.also-cards` (episodes/albums), `.entry-bullets` (show notes / label news), `.rating` (episode/album quality), `.pull-quote` (memorable line) | Cards suit episodic + album recs |
| **The Ledger** *(Desk column — finance + fintech + side-hustle; was Money)* | `.big-number-row` (ISA allowance, rate, revenue), `.compare-panel` (card/account A vs B), `.stat-bar` (rates/cashback %), `.pull-quote` (editorial take), **`.do-this-week` (closing pin)** | Data-forward; big numbers and compare panels make money scannable. Closes on the `.do-this-week` pin |
| **The Itinerary** *(Desk column — travel + parks + NI local; was Places)* | `.timeline` (trip/event dates), `.split-60-40` (destination/find + image), `.img-montage` (destination photos), `.dyk` ("Did you know Efteling…"), **`.do-this-week` (closing pin)** | Timeline for trips; images sell destinations. Closes on the `.do-this-week` pin |
| **The Session** *(Desk column — fitness)* | `.workout-card` (protocol table), `.big-number` (a training stat), `.pull-quote` (a coaching line), `.do-this-week` (closing pin) | Protocol tables + one closing action; closes on the `.do-this-week` pin |
| **The Saga** *(trigger-driven)* | `.dual-col` (essay layout), `.pull-quote` (memorable lore line), `.collapsible` (spoilers), `.timeline` (multi-show arc) | Essay-shaped; collapsibles isolate spoiler content |
| **The Threads** *(fixed — continuity)* | `.the-threads` > `.thread` (`.thread-saga` / `.thread-life`), each a recap line + link | "Previously on…" list; no pin (recap, not service) |
| **The Week in Numbers** *(fixed — personal strip)* | `.week-in-numbers` wrapping `.stat-bar` > `.stat` | Compact personal read-out; reuses the stat vocabulary |


### Down the Rabbit Hole (recurring sidebar)

A light sidebar that appears every 3-4 weeks, embedded within any section where it fits naturally. Not a standalone section — it's a boxed nudge (use `.sidebar-float` or `.sidebar`) placed inside a fixed or rotating section.

- **Purpose:** "This is something you might be interested in exploring based on your tastes." An adjacent-interest nudge — the kind of thing a good editor would slip in because they know the reader.
- **Tone:** Curious, not prescriptive. "You like X, so you might find Y interesting" — then a brief intro (50-100 words) with 2-3 links to get started.
- **Examples:** "You're into Malazan — have you tried Lois McMaster Bujold's Vorkosigan Saga?" / "Given your interest in kettlebells and Dan John, the Highland Games community might be worth a look." / "Synthwave fan? The demoscene has similar vibes and a 40-year history."
- **Not a full section.** No navigator card, no watermark, no dedicated background. It's a sidebar box with a "Down the Rabbit Hole" label, styled to match whichever section hosts it.
- **Research:** When it's due to appear, one quick search based on the reader's existing interests to find a genuine adjacent rabbit hole. No research needed if nothing surfaces — skip it.
- **Cadence:** Every 3-4 weeks. Track in state file as `down_the_rabbit_hole` with `last_appeared`.

### Research Scoping

Only research topics for the rotating sections selected for this issue. This saves time and keeps research focused. Fixed sections always get researched. The search checklist below marks which groups are always-run vs conditional.

---

---

## Search Groups for Rotating Sections

Only search the groups for sections appearing in this issue.

**Group R1 — The Shelf:** fantasy/sci-fi book news + r/Fantasy, narrative history (Dan Jones / Tom Holland / Mary Beard), occasional music context when Listening isn't running. Research window: since last Shelf appearance.

**Group R2 — This Week in History:** history this week (ancient/medieval preferred). Research window: current week.

**Group R3 — Listening** *(podcasts + audio drama + music)*: podcast episodes (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions, plus discover), audio drama releases, niche podcast finds; synthwave/retrowave releases (Bandcamp Daily, RetroSynth, FiXT, Lakeshore, Aphasia, Lazerdiscs), soundtrack picks, retro-listening reissues, /r/outrun, /r/synthwave, /r/SoundtrackCollection. Research window: since last Listening appearance.

**Group R4 — The Ledger** *(Desk column — finance + fintech + side-hustle; was Money)*: UK personal finance / ISA / pension / investment reads (Monevator, r/UKPersonalFinance, MSE, This Is Money); consumer fintech — Monzo/Revolut/Starling updates, cashback cards, switching deals (MSE forum, Head for Points); side-hustle — Etsy seller trends, Notion/Kindle Scribe template market, passive income (r/Etsy, r/passive_income). **Also surface a named, criteria-stated "Do This Week" money action** (the specific rate/account/move worth acting on). Research window: since last Ledger appearance.

**Group R5 — The Itinerary** *(Desk column — travel + parks + NI local; was Places)*: Disney Parks / Efteling / Beekse Bergen news, European travel deals; NI hidden gems, unusual family events, NI cultural happenings (Visit Belfast, Discover NI, r/northernireland, Belfast Live / Irish News). Search forward 2-4 weeks for events. **Also surface a "Do This Week" travel action** (a booking window, a date to reserve, an event to attend). Research window: since last Itinerary appearance.

**Group R-Toolkit — The Toolkit** *(fixed-but-yields; search every issue it's due)*: consumer tech (Pixel/Xiaomi/e-readers, wearable hardware/firmware — Whoop/Garmin/Oura), consumer AI tools, new Android apps, Todoist tips/workflows, productivity tools, tablet accessories. Sources: r/Android, r/Todoist, Product Hunt, 9to5Google, The Verge, XDA, DC Rainmaker. Research window: since last Toolkit appearance (catch-up rule — cover the full gap).

**Group R-Saga — The Saga** *(trigger-driven only — search ONLY when a public or private peg has fired it)*: Star Wars lore deep-dives (Wookieepedia, official databank, /r/StarWars), fantasy book-universe lore (Cosmere — /r/cosmere, Brandon Sanderson AMAs; Malazan — /r/Malazan, Steven Erikson interviews), Tor.com long-reads, show-arc essays. Spoiler-policed. Peg sources also include the reader's `currently_reading` / `currently_watching` state. Research window: scoped to the peg.

> Gaming and tech&tools are no longer rotating search groups — Gaming is core Group 2a (Pixel & Byte, every issue); Tech & tools is the Toolkit group above. LEGO is searched within Group 2a. Fitness gear/science is searched within core Group 5 (The Session, which absorbed Workshop + Lab).
