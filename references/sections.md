# The Signal — Section Reference

Detailed content rules, voice notes, and research guidance for each section.
Only read the sections appearing in this issue.

---

### Cover
Masthead, date, issue number, editorial hook headline, 6-10 topic tags. Ambient animation via CSS.

### Navigator
Visual card grid linking to each section. Top 1-2 cards use `.nav-card.lead` (two-column span with thumbnail). Section icons on each card. 8-14 cards total.

### Foreword
50-80 words. One thread, one hook. No "meanwhile" or "elsewhere". Drop-cap renders automatically.

### The Long Shelf — Worth Your Time
6-8 recommended reads/listens/watches with linked titles, source, and one-sentence hook. Two-column grid. 2 of 8 items should be genuine wildcards outside the magazine's usual coverage areas. Each item's one-sentence hook should sell the content on its own merit — not explain why it was selected for this reader.

### The World This Week
Lead story + supporting stories. Hero image. White background, rose accent.
- Opinions mandatory — give editorial takes
- The Angle box only for genuinely significant stories
- 6-10 Also This Week one-liners

**Ongoing Story Tracker**
When a single topic has led The World This Week for 2 consecutive weeks, it graduates from headline coverage to a dedicated **"Ongoing"** subsection within World This Week. Rules:
- **Position:** after the new lead story, before Also This Week. Visually distinct — use a `.sidebar` or bordered box with the story label (e.g. "Iran War — Week 7", "Ukraine — Month 26").
- **Content:** factual updates only. What happened this week, key numbers, status changes. No new editorial angles on why it matters — that was established when it first led. Think situation report, not op-ed.
- **Space:** give it as much space as the story needs to cover the week's developments thoroughly. A quiet week might be 200 words; a week with military, diplomatic, and economic threads running simultaneously might be 800. Use paragraphs, stat bars, big-numbers, and links to primary sources. The constraint isn't word count — it's that the tracker doesn't set the tone for the section. It sits in its box, covers everything factually, and the new lead story above it sets the editorial direction for the week.
- **The issue can grow to accommodate it.** An ongoing tracker doesn't steal space from the new lead or other stories — the issue expands slightly.
- **Promote back to headline** when there's genuine big news — a ceasefire, a major escalation, a paradigm shift. The bar for re-promotion is high: it must be the kind of development that would lead any newspaper, not just the latest incremental update.
- **Demote to Also This Week** when the story becomes a low-level stalemate, shrinks in significance, or stops producing meaningful weekly developments. It can graduate back to Ongoing or Headline if things change.
- **Drop entirely** when the story is resolved or no longer has weekly developments worth reporting.
- **Multiple ongoing stories can coexist.** If two or three running stories are all in tracker mode, they each get their own labelled box. They stack after the lead.
- **This pattern applies to any running story** — wars, political crises, drawn-out negotiations, pandemics, ongoing tech antitrust cases, anything. Not just world news — if a tech story (e.g. a major antitrust trial) or sports story (e.g. a drawn-out transfer saga) has been leading its section for 2+ weeks, the same pattern applies within that section.

**Track in state file:** add `ongoing_stories` array. Each entry: `{ "topic": "Iran War", "section": "world", "weeks_as_lead": 4, "weeks_as_ongoing": 2, "last_status": "ongoing" }`. Update weekly.

### Pixel & Byte
Gaming, consumer tech, AI tools, LEGO, Steam Deck, e-readers. Warm background, ember accent.
- LEGO goes here (not Screen & Sound)
- Use "Family Picks" or "For the Kids" sidebars — don't sprinkle "your son will love" through prose
- 4+ Also in Tech & Gaming items

### The Touchline
**Data first, then narrative.** Dark background, green accents.

**The Touchline is a flexible sports section, not a fixed football roster.** Its content should adapt to whatever is most compelling in sport that week. Nothing has a guaranteed slot — everything earns its space.

**Team allegiance:** The reader supports Juventus. Do not assume support for Northern Ireland, any Premier League club, or any other team. Coverage of other teams (including NI) is fine when they are the biggest story of the round, but never frame it as "our" team or assume the reader has a rooting interest.

**Priority hierarchy (what leads the section):**
1. **Major tournament in progress** (World Cup finals, Euros, Copa América) — dominates the section. Domestic leagues drop to one-liners or are omitted.
2. **Major non-football event** (Ryder Cup, golf major, Olympics, rugby World Cup, F1 title decider) — can take the lead and push football into a secondary role. Give it the space it deserves.
3. **Active qualifying campaign** (WC qualifiers, Euro qualifiers) — leads over domestic leagues. Domestic only if genuinely significant (sacking, title decided, record).
4. **CL/EL knockout stages** (QF onward) — lead over domestic. Group stages share space.
5. **Normal domestic weeks** — Serie A and PL share the section.

**European football beyond Serie A/PL** (La Liga, Bundesliga, Ligue 1, etc.) — not included by default. Surface only when something is genuinely compelling: a thrilling title race, a historic result, a major sacking, a story with wider significance. Routine matchday results from other leagues don't make the cut.

**Flexible space within the section:** Sub-topics expand and contract based on what happened. A Ryder Cup Sunday can take 70% of the section with football condensed to quick results. A quiet international break can mean a shorter Touchline overall. The section should never exceed ~30% of the total issue length, but content moves freely within it.

- Sparklines for form, position-change indicators
- **Serie A ≥ PL** in coverage depth during normal domestic weeks. Cover the whole league — title race, relegation, stories — not just Juve. **Serie A table must show the full table or at minimum top 10 + relegation zone, not just the top 5.** PL table same standard.
- Golf majors and other major sporting events get proper coverage when in season — they can lead the section
- Football reads like editorial, not match reports — the reader already knows the scores
- Image montage for match photos

### Screen & Sound
Film, TV, streaming, Star Wars (always search). Dark purple background, neon accent.
- **Write as a culture critic.** Review films, shows, and music the way any entertainment column would. The reader profile drives topic selection, not prose.
- Opinions are mandatory — not press-release summaries
- Rating dots for reviews
- Card stack for Quick Reviews
- Collapsible sections for spoiler content
- **The Release Radar:** 15-20+ items across ALL categories (film, TV, games, LEGO, tech, books, music). Sub-sections: Now Showing, Coming Soon, Leaving Soon, Also Streaming. Category dots for visual scanning. **Items within each sub-section must be in chronological date order** (earliest first for Coming Soon, most recent first for Now Showing/Also Streaming).
- "For the Kids" sidebar when relevant
- **No overlap with On the Radar** — Release Radar covers product/media releases only

### The Shelf *(rotating — every 2-3 weeks)*
Books, music, podcasts. Dark brown background, gold accent.
- **Catch-up rule:** when The Shelf appears, research covers the entire period since it last appeared (not just the past 7 days). Check state file for `last_shelf_date`. No good book news, podcast episode, or music release should fall through the cracks.
- **Write as a general editorial reviewer.** The reader profile tells you what genres and topics to research and select from — it does NOT belong in the prose. Review books the way any book column would: premise, tone, what makes it worth reading. Never open with "since you're into Malazan" or "as a Cosmere fan." The selection already signals relevance.
- Books: features, recommendations, book cards with rating dots. Both epic series AND short fiction. Occasional narrative history (Dan Jones, Tom Holland, Mary Beard).
- **CRITICAL: No spoilers.** Never reveal plot twists, character deaths, endings for any book. This rule is absolute but invisible — never announce compliance with it.
- Music: synthwave/retrowave — NOT a fixed section, cover only when relevant.
- Podcasts: flag specific new episodes with episode titles, dates, and what makes them worth listening to. **Only describe episode content you can verify via search.** If you cannot confirm what a specific episode discussed, link to it without a content summary — do not invent one. The value is surfacing specific episodes since the last Shelf appearance and why they stood out. Cross-reference with audio drama recs.

### The Session
Sourced fitness feature. Light green background, orange accent.
- **Write as a fitness journalist, not a personal trainer.** The reader profile tells you which training modalities to cover — it does NOT belong in the prose. Don't write "for someone following the Ibex programme" or "as a runner training for a 10k." Write about the topic in a way any fitness-interested reader would find useful.
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

### This Week in History *(rotating — every 2-3 weeks)*
Warm parchment background, gold accent.
- One featured event (150-300 words) + 3-4 "Also This Week" one-liners using timeline component.
- **Strong preference for pre-WW2 history.** Ancient, medieval, Roman, classical, or early modern. WW1/WW2 only for truly major anniversaries. Post-WW2 is the last resort.
- Connect to current events when resonant.
- **Links are essential here.** The featured event must link to its Wikipedia article — Wikipedia is the preferred starting point for history rabbit holes. Additional links (long-form pieces, podcast episodes, documentaries) are welcome but Wikipedia comes first. "Also This Week" one-liners should each link to their Wikipedia article too. History is the section most likely to make the reader think "I want to know more" — give them somewhere to go.

### The Pantry *(rotating — every 2-3 weeks)*
One practical meal prep idea or recipe per appearance. Light warm background, terracotta accent.
- **Purpose:** inspiration for the reader's meal rotation, not a meal plan. One solid idea they can decide whether to adopt.
- **Nutrition context (invisible in prose):** Reader targets ~2,200-2,300 kcal/day with 180g+ protein during the cut (through June 30). Recipes that hit 40-50g protein per serving in the 400-550 kcal range are ideal. Post-holiday this shifts to maintenance/surplus. Prioritise: batch-cookable, scales to 5+ portions, family-friendly (10-year-old son), uses common ingredients. The reader meal preps — practical storage and reheating notes are high value.
- High-protein, batch-friendly, compatible with a cutting diet (~0.75kg/week loss while training).
- Should be genuinely appetising and practical — not bland "chicken and rice" bodybuilder food.
- Good sources: Mob Kitchen, Pinch of Nom, BBC Good Food, Reddit r/MealPrepSunday, Serious Eats, Budget Bytes. NOT generic Men's Health meal plans.
- Include: ingredients, rough macros (protein per serving), prep time, batch size, storage notes.
- Use recipe card component (adapt workout card pattern). Include one hero image.
- Research window: since last Pantry appearance (check state file).

### The Workshop *(rotating — every 3-4 weeks)*
Home gym gear, equipment reviews, recovery tools. Light grey background, steel accent.
- Reader is building a home gym. Current kit: competition kettlebells, dip bars, slant board, resistance bands. Interested in expanding.
- Cover: equipment reviews, setup ideas, recovery tool reviews (massage guns, foam rollers, mobility tools), running gear (shoes, watches, vests), wearable tech.
- Only stuff relevant to the reader's actual training (structured gym via Ibex, recreational running, kettlebells at home, Pliability mobility).
- Good sources: Garage Gym Reviews, r/homegym, Stronger by Science gear reviews, Running Warehouse, DC Rainmaker (wearables).
- Not generic "best home gym 2026" listicles. Specific, opinionated recommendations.
- Research window: since last Workshop appearance.

### The Toolkit *(rotating — every 3-4 weeks)*
Apps, tablet productivity, digital workflow discoveries. Light blue-grey background, cyan accent.
- Reader uses: Xiaomi Pad (Android), Todoist, Perplexity, multi-screen setups, split-screen productivity. Does NOT use Notion (but builds Notion templates to sell — that's The Ledger's territory).
- Cover: new Android apps worth trying, Todoist tips and workflows, productivity tools, tablet accessories, interesting AI tools (consumer, not enterprise), digital organisation.
- Should feel like discoveries — "here's something you might not have found" — not app store roundups.
- Good sources: r/Android, r/Todoist, Product Hunt, 9to5Google, The Verge (apps/tools coverage), XDA Developers.
- Research window: since last Toolkit appearance.

### The Ledger *(rotating — every 3-4 weeks)*
Passive income, side hustle strategy, digital product sales. Warm cream background, amber accent.
- Reader explores selling digital templates on Etsy (Notion templates, Kindle Scribe templates) as a side income stream. Note: the reader doesn't use Notion personally — he builds templates for others to use.
- Cover: Etsy seller trends, template ideas, digital product strategies, marketplace news, passive income tactics, print-on-demand, content monetisation.
- This is the reader's entrepreneurial hobby, not "work content." Frame as creative/business-building, not corporate.
- Good sources: r/Etsy, r/passive_income, Etsy seller forums, indie maker communities, Starter Story.
- No MLM, no crypto schemes, no get-rich-quick. Practical, grounded strategies.
- Research window: since last Ledger appearance.

### The Long Game *(rotating — monthly)*
Personal finance and investing, framed editorially. Cool grey background, navy accent.
- Editorial takes on saving, investing, financial trends. Not financial advice — interesting reads and perspectives.
- Cover: market trends explained simply, savings strategies, ISA/pension news, interesting finance reads, investment ideas framed as editorial.
- UK-relevant (ISAs, pensions, UK platforms like Vanguard, Trading 212, etc.).
- Good sources: Monevator, r/UKPersonalFinance, Money Saving Expert, FT (free articles), This Is Money.
- Not day-trading, not crypto speculation. Long-term, sensible perspective.
- Research window: since last Long Game appearance.

### The Wallet *(rotating — every 3-4 weeks)*
Consumer fintech news, features, and deals. Clean white background, teal accent.
- The reader cares about: Monzo, Revolut, Starling, cashback cards, new account features, switching deals, fintech product launches.
- Cover: new features in banking apps (Monzo Pots updates, Revolut credit cards, Starling Spaces), cashback deals, new cards worth considering, interesting fintech product launches, comparison insights.
- Practical and consumer-focused. "Revolut just launched X and here's whether it's worth it" — not fintech industry analysis.
- Good sources: r/UKPersonalFinance, MSE forum, Head for Points (cards/rewards), Monzo/Revolut/Starling blogs and changelogs.
- Research window: since last Wallet appearance.

### The Itinerary *(rotating — event-driven, increases near trips)*
Travel, theme parks, and local NI hidden gems. Warm sand background, coral accent.
- **Owns all travel and parks content.** When The Itinerary appears, Disney Parks, Efteling, Beekse Bergen, and all travel content consolidates here. When absent, parks news drops to one-liners in On the Radar.
- **Three content streams:**
  1. **Travel abroad:** destination profiles, flight deals, European trips with a kid, logistics tips.
  2. **Theme parks:** Disney Parks news, Efteling updates, Beekse Bergen, other parks worth knowing about. New rides, events, ticket deals, tips.
  3. **NI local finds:** hidden gems, unusual family events, places the reader may not have heard of or tried. NOT the zoo, the leisure centre, or obvious tourist spots. Rare finds, quirky events, seasonal things worth knowing about. Must pass the test: would a local find this genuinely surprising or useful?
- **Frequency:** appears every 3-4 weeks normally. Increases to every issue (or every other) when a trip is approaching. Check state file for upcoming trips.
- Research window: since last Itinerary appearance. For NI local, also search forward for upcoming events in the next 2-4 weeks.

### On the Radar — Coming Up
8-10 upcoming items: fixtures, sporting events, local NI events, parkruns, dates to know, personal milestones, deadlines, cultural events. Compact grid with date + event + detail. Category dots.
- **No overlap with Release Radar.** Product/media releases go in Release Radar. This is for everything else.
- When The Itinerary is absent, parks and travel news can appear here as one-liners.

### Footer
Masthead echo, issue info line.

---

---

## Component Palettes for Rotating Sections

### Component Palettes for Rotating Sections

| Section | Primary Components | Why |
|---|---|---|
| **The Pantry** | `.workout-card` (adapted as recipe card), `.big-number` (protein/cals), `.split-60-40` (image + ingredients), `.sidebar` (storage notes) | Recipe card is the centrepiece; stats make macros scannable |
| **The Workshop** | `.compare-panel` (product A vs B), `.also-cards` (gear picks), `.big-number` (price/specs), `.img-offset` (product photos) | Compare panels are natural for gear reviews |
| **The Toolkit** | `.also-cards` (app picks), `.compact-grid` (2 app reviews side by side), `.sidebar-float` ("What it replaces"), `.entry-stat` ("3M downloads") | Card-based layout suits app discovery |
| **The Ledger** | `.stat-bar` (revenue/trend numbers), `.entry-stat` or `.entry-bullets`, `.pull-quote` (seller insight), `.also-list` with tiers | Data-forward; stat bars make trends scannable |
| **The Long Game** | `.big-number-row` (ISA allowance, rate), `.pull-quote` (editorial take), `.sidebar` ("One Thing to Do This Month"), `.entry-question` | Editoral framing; big numbers for rates/returns |
| **The Wallet** | `.compare-panel` (card A vs card B), `.also-cards` (feature roundup), `.entry-bullets` (key changes), `.stat-bar` (rates/cashback %) | Compare panels natural for card/account comparisons |
| **The Itinerary** | `.timeline` (trip countdown or event dates), `.split-60-40` (destination + image), `.dyk` ("Did you know Efteling..."), `.img-montage` (destination photos), `.sidebar` (logistics) | Timeline for trip countdowns; images sell destinations |
| **The Shelf** | `.book-card` / `.book-grid`, `.card-stack`, `.rating`, `.pull-quote`, `.collapsible` | Already well-defined from weekly version |
| **This Week in History** | `.timeline`, `.year-badge`, `.img-offset`, `.sec-opener` | Already well-defined from weekly version |


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

**Group R1 — The Shelf:** fantasy/sci-fi book news + r/Fantasy, podcasts (Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions), audio drama recommendations, synthwave/retrowave music releases. Research window: since last Shelf appearance.

**Group R2 — This Week in History:** history this week (ancient/medieval preferred). Research window: current week.

**Group R3 — The Pantry:** high-protein meal prep recipes, batch cooking ideas, r/MealPrepSunday, Mob Kitchen, BBC Good Food. Research window: since last Pantry appearance.

**Group R4 — The Workshop:** home gym equipment reviews, recovery tools, running gear, kettlebell gear, r/homegym, Garage Gym Reviews, DC Rainmaker. Research window: since last Workshop appearance.

**Group R5 — The Toolkit:** new Android apps, Todoist tips/workflows, productivity tools, tablet accessories, AI tools (consumer), r/Android, r/Todoist, Product Hunt. Research window: since last Toolkit appearance.

**Group R6 — The Ledger:** Etsy seller trends, digital product strategies, Notion template market (seller perspective — what sells, pricing, niches), Kindle Scribe template market, passive income ideas, r/Etsy, r/passive_income. Research window: since last Ledger appearance.

**Group R7 — The Long Game:** UK personal finance news, ISA/pension updates, investment reads, Monevator, r/UKPersonalFinance. Research window: since last Long Game appearance.

**Group R8 — The Wallet:** Monzo/Revolut/Starling updates, new fintech features, cashback cards, switching deals, MSE forum, Head for Points. Research window: since last Wallet appearance.

**Group R9 — The Itinerary:** Disney Parks news, Efteling updates, Beekse Bergen, European travel deals, NI hidden gems and unusual family events (search forward 2-4 weeks for upcoming events). Research window: since last Itinerary appearance.
