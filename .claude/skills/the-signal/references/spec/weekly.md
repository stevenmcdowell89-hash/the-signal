# Spec slice — weekly

_This file consolidates the weekly/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

## Issue Formats

### Standard Weekly (default)
The full Sunday edition. **6,500+ words with no hard ceiling, 20-30+ pages.** Section order as listed above. Per-section depth floors hold (no fixed-section piece below 200 words); every fixed section runs a Lead + Companion of 200–700 words each. See editorial-spec.md § Article Structure: Lead + Companion for the full structural contract.



---

## sections

## Section Structure (Standard Weekly)

Sections are divided into **fixed** (appear every issue) and **rotating** (appear on a cadence, selected per issue). Each issue includes all fixed sections plus 2-3 rotating sections. The Navigator adapts to show only the sections present in that issue. The issue ends with a Colophon (sign-off block) before the Footer — see § End-of-Issue Colophon.

### Fixed vs Rotating

**Fixed (every issue):** Cover, Navigator, Foreword, The Long Shelf, The World This Week, Pixel & Byte, The Touchline, Screen & Sound (with Release Radar), The Session (omit if nothing found), On the Radar, Footer.

**Rotating (cadence-based):** The Shelf, This Week in History, The Pantry, The Workshop, The Toolkit, The Ledger, The Long Game, The Wallet, The Itinerary.

See **Rotation Mechanics** below for scheduling rules.


For individual section content rules, voice notes, and research guidance, see `references/sections.md`. Only read sections appearing in this issue.


## Anchor-Piece Rotation (deprecated v8.15)

Removed. Replaced by the Lead + Companion structure (see § Article Structure). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

---

## End-of-Issue Colophon

Every issue ends with a **Colophon** — a sign-off block between On the Radar and the Footer. It's a single full-width `<section class="colophon">` on paper background, visually distinct from both the editorial sections and the footer. Three blocks in a grid:

### Block 1 — Issue in Numbers

A small stat grid summarising the issue itself: word count, number of sections, number of links, articles read, images. If an anchor piece ran, include "Anchor: [section name]". 4-6 stats, quietly pleasing rather than boastful.

### Block 2 — Next Week

One or two sentences teasing what's coming: a tracked ongoing story, a rotating section due, an event on the horizon. Written by the editor, not generated from the state file alone — should feel like a human note, not a changelog. Keep it short; don't promise specifics that might not hold.

### Block 3 — A Fact

The standing feature. **One curious fact, unrelated to any story in this issue.** 20-40 words. The tone is Snapple-cap-meets-QI: surprising, verifiable, and genuinely interesting to a curious generalist. Rotate weekly — never repeat a fact within a 12-issue window. Source from Wikipedia curiosities, reference books, or a fact you came across during research and couldn't fit anywhere.

The Colophon closes with a small sign-off line (`.colophon-sign`) — issue number, date, and the standing tagline.

---

## Article Structure: Lead + Companion

Every fixed section in a standard weekly runs a **Lead piece** AND a **Companion piece**, both substantial, on **distinct topic families**. The Lead is the section's centrepiece; the Companion is not a footnote — it's a second proper article. Tail content (also-lists, quick reviews, tables, sub-sections like the AI block in Pixel & Byte or Release Radar in Screen & Sound) is in addition to Lead + Companion, not instead of it.

### Word count band

| Piece | Floor | Typical | Ceiling |
|---|---|---|---|
| Lead | 300 words | 400–700 words | 1,000+ on a genuinely massive week |
| Companion | 200 words | 250–450 words | 600 words |

The Companion never compresses below 200 words. If research can't support a 200-word companion, the planner must broaden the section's scope — not shrink the piece into a one-liner.

### Topic-family discipline

The Lead and the Companion in the same section MUST be on different `topic_family` values. The closed enumeration of topic families lives in `references/chapter-plan-schema.md`. A planner-side validator rejects any chapter plan where Lead.topic_family == Companion.topic_family within a section.

Tail items (also-lists, quick reviews) are not subject to this rule — they can repeat the lead's topic family. But the Lead and Companion always anchor different ground.

### Sections exempted from Lead + Companion

- **Cover, Navigator, Foreword, Footer, Colophon** — chrome / framing, single-piece by design.
- **The Long Shelf** — already structurally varied (6–8 items with 2 wildcards). Keep its existing shape.
- **On the Radar** — compact date-grid format. Keep its existing shape (but see § On the Radar update below for the "why it matters" half-line addition).

### Sections covered by Lead + Companion (mandatory)

- **The World This Week** — Lead + Companion on distinct topic families. Ongoing-story tracker boxes are in addition.
- **Pixel & Byte** — Lead + Companion. If Lead is gaming, Companion is non-gaming consumer tech (or vice versa).
- **The Touchline** — Lead + Companion. **The Companion must be a non-football sport** when the Lead is football. If the Lead is a Priority-2/3 non-football story (per existing Touchline hierarchy), the Companion may be football.
- **Screen & Sound** — Lead + Companion. **Companion cannot be the same franchise as the Lead** (so a Star Wars Lead requires a non-Star-Wars Companion; an MCU Lead requires non-MCU; etc.).
- **The Session** — Lead piece + a "Companion deep note" of 200–250 words on a different training-topic cluster (see clusters list in sections.md). The Companion can be lighter than other sections' companions but must still be substantive.

Rotating sections use their existing single-feature shape — they don't need Lead + Companion because they already provide variety by rotating in and out across issues.

---

## Topic Lock: Lifetime Leads & Escalating Bar

The spec's "bar rises exponentially" rule for re-promoting ongoing stories needs mechanical enforcement. Two new state-file fields on each entry in `ongoing_stories`:

- `lifetime_leads` (int) — incremented every time this topic anchors any fixed section Lead (not just World). Counts across the topic's entire lifetime.
- `weeks_since_last_lead` (int) — ticks +1 each weekly the topic is NOT the lead; resets to 0 when it is.

### Planner enforcement

A topic with `lifetime_leads >= 3` cannot anchor the Lead unless `weeks_since_last_lead >= lifetime_leads * 2`.

Worked example: Iran has had 5 lifetime leads. Re-promoting Iran to Lead requires 10 weeks of not-leading first. Until then, Iran lives in the tracker box.

### Topics this rule applies to

`ongoing_stories` is not limited to World This Week — it's a tracking concept for any topic that has anchored any section's Lead. Track:

- World This Week: Iran War, Ukraine, US-China trade, etc.
- Pixel & Byte: Switch 2 ecosystem, Steam Deck, consumer AI launches
- Touchline: Serie A title race, Champions League knockout, WC qualifying campaign
- Screen & Sound: long-running show arcs (Star Wars: Maul, Daredevil, House of the Dragon, etc.)
- Session: running-race build-up, hypertrophy block, etc.

### Gate 1 grep check

After generation, scan each fixed section's Lead H2 + first paragraph for the topic's named entities. If `lifetime_leads >= 3` for any tracked topic AND that topic's named entities appear in the Lead (≥3 mentions or in H2), Gate 1 fails with reason "topic-lock: <topic> exceeds lifetime-leads bar". Re-plan the Lead.

---

## Per-section discipline rules

- **The Toolkit (rotating)** — Same app cannot anchor two consecutive Toolkit appearances. Track `last_toolkit_app` in state file (slug like `todoist`, `obsidian`, `perplexity`).
- **The Session** — State-file `last_session_topic` tracks the cluster (running_science / concurrent_training / hypertrophy / kettlebells / gymnastics_rings / recovery_mobility / wearable_data / nutrition_recomp / landmine_training / home_gym_programming). Same cluster cannot anchor two consecutive Session Leads.
- **The Long Game ↔ The Session boundary** — The Long Game is **finance only** (ISAs, pensions, savings, investing, market trends, UK personal-finance reads). Fitness deep-dives belong in The Session. Misclassification = Gate 2 hard fail (compliance-checklist).

---

## rotating

## Rotation Mechanics

Each issue includes **all fixed sections** plus **2-3 rotating sections** selected based on cadence and editorial judgement.

### Cadence Table

| Section | Target Cadence | Research Window | Notes |
|---|---|---|---|
| The Shelf | Every 2-3 weeks | Since last appearance | Catch-up rule: covers full gap |
| This Week in History | Every 2-3 weeks | Current week | History is date-bound |
| The Pantry | Every 2-3 weeks | Since last appearance | One recipe per appearance |
| The Workshop | Every 3-4 weeks | Since last appearance | Home gym, gear, recovery tools |
| The Toolkit | Every 3-4 weeks | Since last appearance | Apps, productivity, workflows |
| The Ledger | Every 3-4 weeks | Since last appearance | Side hustle, Etsy, templates |
| The Long Game | Monthly (~every 4 weeks) | Since last appearance | Personal finance, investing |
| The Wallet | Every 3-4 weeks | Since last appearance | Consumer fintech, banking apps |
| The Itinerary | Every 3-4 weeks (more near trips) | Since last appearance + forward 2-4 weeks for events | Travel, parks, NI hidden gems |

### Selection Rules

1. **Check the state file** (`signal-state.json`) for `rotating_sections` — each entry has `last_appeared` date.
2. **Pick the most overdue sections first.** If The Shelf last appeared 3 weeks ago and The Wallet 2 weeks ago, The Shelf has priority.
3. **Cap at 2-3 rotating sections per issue** to maintain pacing. Rotating sections should be substantive (300-600 words each, except The Shelf which can be longer). The 6,500+ word target is met primarily by the fixed sections' Lead + Companion structure; rotating sections add variety on top, not bulk.
4. **The Itinerary overrides normal cadence** when a trip is approaching — it appears every issue or every other issue in the lead-up. Check state file for `upcoming_trips`.
5. **Don't force it.** If research for a rotating section turns up nothing worthwhile, skip it even if it's overdue. The cadence is a guide, not a mandate.
6. **Ensure variety across a month.** Over any 4-issue stretch, aim for every rotating section to appear at least once (except The Long Game, which is monthly, and The Itinerary, which is event-driven).

### Placement: Interleave, Don't Stack

**Rotating sections must be woven between fixed sections, not dumped at the end.** They should feel like natural parts of the issue, not an appendix. Each rotating section has a preferred placement slot:

| Rotating Section | Preferred Slot | Reasoning |
|---|---|---|
| The Pantry | Between Pixel & Byte and The Touchline | Palate cleanser between tech and sport; warm tone bridges the gap |
| The Shelf | Between Screen & Sound and The Session (original position) | Natural flow from entertainment to books/podcasts |
| The Workshop | Between The Session and the next section | Gear/gym pairs naturally with fitness |
| The Toolkit | Between The World This Week and Pixel & Byte | Productivity/apps feel at home near the tech section |
| The Ledger | Between The Touchline and Screen & Sound | Change of pace between sport and entertainment |
| The Long Game | Between The Touchline and Screen & Sound | Finance as a breather between dense sections |
| The Wallet | Between Pixel & Byte and The Touchline | Fintech pairs with the tech section |
| The Itinerary | Between The Session and On the Radar | Travel/events naturally leads into the calendar |
| This Week in History | Between The Session and On the Radar (original position) | Reflective close before the forward-looking calendar |

**When 2-3 rotating sections appear in the same issue:**
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

Removed. Replaced by the Lead + Companion structure (see § Article Structure: Lead + Companion above). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

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

