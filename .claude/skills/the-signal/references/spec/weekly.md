# Spec slice — weekly

_This file consolidates the weekly/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Standard Weekly (default)
The full Sunday edition. **6,000-8,000 words, 20-30 pages.** Section order as listed above.



---

## sections

## Section Structure (Standard Weekly)

Sections are divided into **fixed** (appear every issue) and **rotating** (appear on a cadence, selected per issue). Each issue includes all fixed sections plus 3-4 rotating sections. The Navigator adapts to show only the sections present in that issue. The issue ends with a Colophon (sign-off block) before the Footer — see § End-of-Issue Colophon.

> **Why 3-4 rotating slots (v8.16).** The roster grew from 9 rotating sections to 14 in v8.16. With per-section cadence targets ranging from every 2-3 weeks (Shelf, History) to every 6 weeks (Saga, Channel), each issue needs 3-4 slots to keep every section near its target cadence.

### Fixed vs Rotating

**Fixed (every issue):** Cover, Navigator, Foreword, The Long Shelf, The World This Week, Pixel & Byte, The Touchline, Screen & Sound (with Release Radar), The Session (omit if nothing found), On the Radar, Footer.

**Rotating (cadence-based):** The Shelf, The Listen, This Week in History, The Workshop, The Toolkit, The Ledger, The Long Game, The Wallet, The Itinerary, The Local, The Brickyard, The Saga, The Lab, The Channel.

See **Rotation Mechanics** below for scheduling rules.


For individual section content rules, voice notes, and research guidance, see `references/sections.md`. Only read sections appearing in this issue.




---

## rotating

## Rotation Mechanics

Each issue includes **all fixed sections** plus **3-4 rotating sections** selected based on cadence and editorial judgement.

### Cadence Table

| Section | Target Cadence | Research Window | Notes |
|---|---|---|---|
| The Shelf | Every 2-3 weeks | Since last appearance | Catch-up rule: covers full gap |
| This Week in History | Every 2-3 weeks | Current week | History is date-bound |
| The Listen | Every 3-4 weeks | Since last appearance | Podcasts + audio drama; episodic + retrospective |
| The Workshop | Every 3-4 weeks | Since last appearance | Home gym, gear, recovery tools |
| The Toolkit | Every 3-4 weeks | Since last appearance | Apps, productivity, workflows |
| The Ledger | Every 3-4 weeks | Since last appearance | Side hustle, Etsy, templates |
| The Long Game | Monthly (~every 4 weeks) | Since last appearance | Personal finance, investing |
| The Wallet | Every 3-4 weeks | Since last appearance | Consumer fintech, banking apps |
| The Itinerary | Every 3-4 weeks (more near trips) | Since last appearance + forward 2-4 weeks for events | European travel + theme parks |
| The Local | Every 3-4 weeks | Since last appearance + forward 2-4 weeks for events | NI hidden gems + unusual family events |
| The Brickyard | Every 4-6 weeks | Since last appearance | LEGO sets, builds, MOCs, availability |
| The Saga | Every 6 weeks | Since last appearance | Star Wars + fantasy lore deep dives (no spoilers) |
| The Lab | Monthly (~every 4 weeks) | Since last appearance | Training-science deep dive, slower than The Session |
| The Channel | Every 6 weeks | Since last appearance | Music — synthwave, soundtracks, retro listening |

### Selection Rules

1. **Check the state file** (`signal-state.json`) for `rotating_sections` — each entry has `last_appeared` date.
2. **Pick the most overdue sections first.** If The Shelf last appeared 3 weeks ago and The Wallet 2 weeks ago, The Shelf has priority.
3. **Cap at 3-4 rotating sections per issue** to maintain pacing. Rotating sections should be substantive (300-600 words each, except The Shelf which can be longer). The 6,500+ word target is met primarily by the fixed sections' Lead + Companion structure; rotating sections add variety on top, not bulk.
4. **The Itinerary overrides normal cadence** when a trip is approaching — it appears every issue or every other issue in the lead-up. Check state file for `upcoming_trips`.
5. **Don't force it.** If research for a rotating section turns up nothing worthwhile, skip it even if it's overdue. The cadence is a guide, not a mandate.
6. **Ensure variety across a month.** Over any 4-issue stretch, aim for every rotating section to appear at least once (except The Long Game / The Lab, which are monthly, and The Itinerary, which is event-driven, and The Saga / The Channel, which run on a 6-week cadence).
7. **Hard cadence floor (planner-enforced).** A rotating section CANNOT be scheduled unless `weeks_since_last_appeared >= cadence_low` (the lower bound of its cadence band). The planner-side validator rejects any chapter plan that schedules a section inside its floor. Override: if no other rotating section is eligible (rare; only happens when most of the roster is too-soon AND the issue still needs slots), the planner picks the most-overdue section and the validator emits a warning instead of a hard fail.

8. **Deficit promotion (mandatory force-include).** A rotating section with `weeks_since_last_appeared >= 2 * cadence_high` is force-included in the next eligible issue, regardless of editorial preference. The planner must include it; the validator rejects any plan that leaves a deficit-eligible section out without an explicit reason field (`"deficit_override_reason"`). Prevents the Ledger / Wallet droughts seen in early v8.x.

9. **Default research window when `last_appeared` is null.** When a rotating section appears for the first time after a state file reset (or first-ever appearance), its research window defaults to "past 4 weeks" — NOT open-ended. Prevents the first appearance of a section from surfacing months-old news (e.g. the Revolut-from-March bug). Override via explicit `initial_research_window_weeks` field in state if the editor wants different.

### Placement: Interleave, Don't Stack

**Rotating sections must be woven between fixed sections, not dumped at the end.** They should feel like natural parts of the issue, not an appendix. Each rotating section has a preferred placement slot:

| Rotating Section | Preferred Slot | Reasoning |
|---|---|---|
| The Shelf | Between Screen & Sound and The Session (original position) | Natural flow from entertainment to books |
| The Listen | Between Screen & Sound and The Session | Pairs with entertainment, breaks before fitness |
| The Workshop | Between The Session and the next section | Gear/gym pairs naturally with fitness |
| The Toolkit | Between The World This Week and Pixel & Byte | Productivity/apps feel at home near the tech section |
| The Ledger | Between The Touchline and Screen & Sound | Change of pace between sport and entertainment |
| The Long Game | Between The Touchline and Screen & Sound | Finance as a breather between dense sections |
| The Wallet | Between Pixel & Byte and The Touchline | Fintech pairs with the tech section |
| The Itinerary | Between The Session and On the Radar | Travel/events naturally leads into the calendar |
| The Local | Between The Session and On the Radar | NI events lead naturally into the calendar |
| The Brickyard | Between Pixel & Byte and Screen & Sound | Sits in the "play" cluster |
| The Saga | Between Screen & Sound and The Shelf | Sits in the "story" cluster |
| The Lab | Between The Session and the next section | Pairs with fitness; deeper than the weekly Session |
| The Channel | Between Screen & Sound and The Shelf | Sits in the "listen" cluster (or before The Listen if both present) |
| This Week in History | Between The Session and On the Radar (original position) | Reflective close before the forward-looking calendar |

**When 3-4 rotating sections appear in the same issue:**
- Spread them across different slots — never place two rotating sections back-to-back.
- If two sections share a preferred slot, move one to its alternate position.
- The read-next connectors chain naturally through whatever sections are present.

**Each rotating section uses the full visual toolkit.** They are not second-class citizens:
- Every rotating section gets a `.sec-watermark`, section divider (`hr.divider.dv-[name]`), section-label, and a navigator card.
- Each uses at least 2-3 different component types (see component palette below).
- Background colours and accent colours are defined in CSS (`--[name]-bg`, `--[name]-accent`).
- Use `.reveal` animations on key elements.


### Research Scoping

Only research topics for the rotating sections selected for this issue. This saves time and keeps research focused. Fixed sections always get researched. The search checklist below marks which groups are always-run vs conditional.

---



---

## anchor-piece

## Anchor-Piece Rotation (deprecated v8.15)

Removed. Replaced by the Lead + Companion structure (see § Article Structure). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

---



---

## search-checklist

## Search Checklist

Run the **core groups** every issue. Run **rotating groups** only when that section is selected for the issue.

### Core Groups (every issue)

**Group 1 — News & Geopolitics:** dominant running story, world news, UK / national politics, NI news briefly. Within this group, the scout phase MUST explicitly check for: (a) any UK / Irish / Scottish / Welsh / European elections held in the past 7 days (general, devolved, council aggregate); (b) live PM or opposition-leader leadership challenges (MPs calling for resignation, named challengers emerging, union pressure); (c) Cabinet-level resignations or sackings; (d) major government policy events (Budget, headline legal rulings, immigration policy changes). If any of (a)-(d) fired in the last 7 days, that story is automatically a candidate for Lead 1 unless an even bigger world story crowds it out. See the UK / national politics rule in this spec for the full Lead-grade vs parish-pump test.

**Group 2 — Tech & Gaming:** Nintendo Switch 2, Steam Deck, GeForce Now, consumer AI tools, Pixel/Xiaomi/e-readers, LEGO news and releases, gaming news and releases

**Group 3 — Football & Sport:** First, check: are World Cup qualifiers, Euro qualifiers, World Cup finals, Euros, CL/EL knockout stages, or other major tournaments active this week? If yes, search for those first — they lead the section. Then search domestic (Juventus + Serie A, Premier League) only for significant news. If no tournament is active, search Serie A + Juventus, Premier League, CL/EL (in season), golf majors/Ryder Cup (when in season).

**Group 4 — Culture & Entertainment:** new movies and TV releases, Star Wars news, synthwave/retrowave/electronic music

**Group 5 — Fitness (for The Session):** running articles (race prep, 10k training, zone 2), gym/strength training (concurrent training, body recomposition, structured programming), kettlebell/StrongFirst/Dan John, mobility and recovery science, wearable/Garmin training data interpretation, nutrition for cutting while training

**Group 6 — Features & Evergreen (rotate):** gaming retrospectives, Reddit notable threads (r/NintendoSwitch, r/Juve, r/fantasybooks, r/kettlebell, r/running, r/fitness, r/StarWars, r/lego, r/Garmin), great long-reads from any era

**Images:** source via image search for every major section.

### Rotating Groups

Search groups for rotating sections are in `references/sections.md`. Only search the groups for sections appearing in this issue.

---



---

## image-budget

## Component Quick Reference

Use 10-14 different types per standard issue. No two consecutive sections should use the same layout pattern.

| Component | Class(es) | When to use |
|---|---|---|
| The Angle box | `.angle` | Significant stories only — geopolitics, major tech shifts |
| Pull quote | `.pull-quote` (+`.centered`, +`.wide`) | 3-4 per issue to break prose. Rotate variants. |
| Stats row | `.stat-bar` > `.stat` > `.stat-num.count-up` | Key numbers for a story |
| Did You Know | `.dyk` | 3-5 scattered, section-aware colours |
| Sidebar | `.sidebar` | Curated lists: "Family Picks", context boxes |
| Split layout | `.split-60-40`, `.split-40-60` | Text beside image or sidebar |
| Quick takes | `.dual-col` > `.col-card` | Two mini-articles side by side |
| Compact takes | `.compact-take`, `.compact-grid` | Secondary stories, card format |
| Margin note | `.margin-note` | Tufte-style aside, floats right on desktop |
| Big number | `.big-number`, `.big-number-row` | Dramatic stat pulled mid-article |
| Display stat | `.display-stat` | Inline accent-coloured number |
| Mini data viz | `.sparkline`, `.pos-change`, `.mini-bar-track`/`.mini-bar-fill` | League tables, form charts |
| Rating dots | `.rating` > `.dot.filled`/`.dot` | Reviews in Screen & Sound, Shelf |
| Card stack | `.card-stack` > `.stack-card` | Horizontal scrollable review cards |
| Timeline | `.timeline` > `.timeline-node` | History items, event chronologies |
| Collapsible | `<details class="collapsible">` | Optional-depth content, spoilers |
| Image montage | `.img-montage.layout-1-2` | Grid of 2-4 images |
| Offset image | `.img-offset` | 60% width, text wraps around |
| Hero bleed | `.hero-bleed` | Full-width section-opening image |
| Float image | `.img-float-left` | Book covers, album art |
| Also list | `.also-list` | Simple bold+description list |
| Also cards | `.also-cards` > `.also-card` | 2-col card grid for 4+ items |
| Read-next | `.read-next` | Section-to-section teaser link |
| Watermark | `.sec-watermark` | Oversized label behind section content |
| Section opener | `.sec-opener` | Dramatic section start with gradient band |
| Reveal animation | `.reveal` | Fade+slide on scroll — apply ONLY to small leaf elements: individual images, angles, pull-quotes, individual cards. **NEVER on `<section>`, `split-60-40`, `split-40-60`, `dual-col`, `also-cards`, or any container that wraps a full section or multiple items.** |
| Count-up | `.count-up` (+ `data-target`) | Stat numbers animate from 0 on scroll |
| Book cards | `.book-card`, `.book-grid` | Book recommendations with rating dots |
| Workout card | `.workout-card` | Rep scheme/protocol tables |
| Year badge | `.year-badge` | Monospace date badges for history |
| Category dot | `.radar-cat` (+`.film`,`.game`,`.tv`,`.lego`,`.tech`,`.book`,`.music`) | Release Radar and On the Radar |
| Results strip | `.results-strip` > `.result-card` | Match results with large scores |
| Platform badge | `.platform-badge` | Streaming/platform labels |
| Inset divider | `.divider.inset` | Centred divider with breathing room |
| Entry: stat-first | `.entry-stat` + `.entry-stat-context` | Open article with a dramatic number. Section-aware colours. |
| Entry: quote-first | `.entry-quote` | Open article with a punchy quote. Left-bordered, section-aware. |
| Entry: bullets-first | `.entry-bullets` | Open article with 3 key facts. Left-bordered, section-aware. |
| Entry: question-first | `.entry-question` | Open article with a provocative question. Italic serif. |
| Breather band | `.breather` (+ `.dark`) | Breathing room between dense sections. Contains `.breather-stat`, `.breather-context`, `.breather-teaser`. Use `.dark` variant between dark sections. |
| Also-list tiers | `.tier-hot`, `.tier-warm`, `.tier-note` on `<li>` | Visual weight hierarchy in Also lists. Hot = left accent border + tinted background, warm = subtle border, note = faded. Section-aware. |
| Compare panel | `.compare-panel` > `.compare-side.left` / `.compare-side.right` | Side-by-side comparisons: tech specs, football stats, book recs. Stacks on mobile. Section-aware borders. |
| Floated sidebar | `.sidebar-float` | Text wraps around naturally. More editorial than `.split-60-40`. Section-aware background/borders. Collapses to full-width on mobile. |
| Grain overlay | `.grain-overlay` | SVG film-grain pinned to viewport. Opt-in — placed once, outside `.mag`. Omit for cleaner issues. (Enhancement 22A) |
| Chapter chrome | `.chapter-chrome` > `.eyebrow`/`.hair`/`.roman` | Editorial head inside any section — eyebrow label, hair-rule, roman numeral. Auto-inherits section accent. (Enhancement 22B) |
| Folio watermark | `.folio-watermark` | Giant italic numeral bleeding off bottom-right of a section. Coexists with `.sec-watermark` (top-left). Hidden below 820px. (Enhancement 22C) |
| Pull-break | `.pull-break` > `.pull`/`.attrib` | Dark full-bleed quote band with book-end quotation marks. **World-only flourish, max one per issue.** (Enhancement 22D) |
| Marginalia | `.marginalia` > `.quote`/`.attrib`/`.datum`/`ul` | Floated sidebar card with italic quote, datum blocks, list. Auto-inherits section accent; auto-inverts to paper-on-dark on dark sections. (Enhancement 22E) |
| TOC-style navigator | `.nav-section.toc-style` + `.toc-row.<section>` | Opt-in alternate navigator. Drop in `04-navigator-toc.html` instead of `04-navigator.html`. All TOC selectors scoped — cannot leak into other tables/lists. (Enhancement 22F) |
| Ember period | `.mast-period` / `.brand-period` | Ember-coloured period on "The Signal." wordmark in masthead and cover. (Enhancement 22G) |

**Entry pattern rotation rule:** no two adjacent articles should open the same way. Rotate between `.entry-stat`, `.entry-quote`, `.entry-bullets`, `.entry-question`, and plain prose openings. This applies across articles within a section and across section leads.

**Breather band usage:** place 1-2 breather bands per issue between particularly dense sections. Use light variant between light/warm backgrounds, dark variant between dark backgrounds (Touchline, Screen & Sound, Shelf). Don't overuse — they're breathing room, not filler.

**Rotation rule:** no 3+ screen-heights of unbroken prose anywhere. Vary which sections use split layouts, where pull quotes appear, whether history uses timeline or bullets, which also-lists use card variant. Use entry patterns to vary article openings. Use sidebar-float as an alternative to split layouts. Use compare panels where a natural comparison exists.

---


