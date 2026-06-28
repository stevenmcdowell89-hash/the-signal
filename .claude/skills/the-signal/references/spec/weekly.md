# Spec slice — weekly

_This file consolidates the weekly/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview

### Standard Weekly (default)
The full Sunday edition. **No hard word target — a healthy Sunday read sized to the week's news, typically ~20-30 pages.** Held by per-section shape (a considered piece per section; Catch-Up optional), not a word quota; flex to the news and yield thin sections rather than padding to a number (v8.27). Section order as listed above.



---

## sections

## Section Structure (Standard Weekly)

Sections are divided into **fixed** (appear every issue, except where noted) and **rotating** (appear on a cadence, selected per issue). Each issue includes the fixed sections plus **2-3 rotating sections**. The Navigator adapts to show only the sections present in that issue. The issue ends with a Colophon (sign-off block) before the Footer — see § End-of-Issue Colophon.

> **Why 2-3 rotating slots (v8.27, was 3-4 in v8.16).** The v8.16 roster grew to 14 rotating sections by *splitting* (The Listen out of The Shelf, The Local out of The Itinerary, plus Brickyard / Saga / Lab / Channel), which made several sections compete for the same content and let one interest flood an issue. v8.27 redesigns the roster around the reader's actual interest-domains — one home per domain — collapsing to **5 rotating sections plus one trigger-driven section**. Fewer sections + fewer slots = less slot-filling pressure and a shorter, less-padded issue, back toward the "good era" size.

### Fixed vs Rotating

**Fixed (every issue):** Cover, Navigator, Foreword, The Long Shelf, The World This Week, Pixel & Byte (gaming + LEGO), The Toolkit (tech & tools — *fixed slot but routinely yields*; see its brief), The Touchline, Screen & Sound (with Release Radar), The Session (omit if nothing found), On the Radar, Footer.

> **Yield rather than fill (v8.34).** The Toolkit's "yield when the week is thin, don't pad it to appear" principle now applies to **every** fixed section: a fixed section whose week offers only catch-up — the recap the daily already delivered — **yields** that week rather than running a roundup to fill the slot. The mandatory element is the considered piece (§ Article Structure), not the section's mere presence.

> **The Toolkit is a fixed slot that is expected to disappear regularly.** It is "fixed" only in the sense that it is always *considered* every week — but it carries consumer-tech / AI / apps news, which is not weekly. When the week is thin it **yields entirely** (don't pad it to appear). When it returns it must cover the **entire gap since its last appearance** (the catch-up rule, as The Shelf has), so yielding never drops a fortnight of tech news — it batches it into one good roundup. In practice it appears roughly every other week.

**Rotating (cadence-based, pick 2-3 per issue):** The Shelf (books), This Week in History, Listening (podcasts + audio drama + music), Money (personal finance + fintech + side-hustle), Places (European travel + theme parks + NI local).

**Trigger-driven (no cadence timer):** The Saga (lore deep-dive). It does NOT rotate on a clock — it runs only on a *reason*: a live public peg the researcher finds (a finale aired, a new book/season in a series the reader follows released, an author AMA), or a private peg the reader supplies (`currently_reading` / `currently_watching` in state, or a manual "run a Saga on …" trigger). See its brief in `references/sections.md` and the trigger note under § Auto-Triggered Specials.

See **Rotation Mechanics** below for scheduling rules.


For individual section content rules, voice notes, and research guidance, see `references/sections.md`. Only read sections appearing in this issue.




---

## rotating

## Rotation Mechanics

Each issue includes the **fixed sections** plus **2-3 rotating sections** selected based on cadence and editorial judgement.

### Cadence Table (v8.27 — redesigned roster, one home per domain)

| Section | Target Cadence | Research Window | Notes |
|---|---|---|---|
| The Shelf | Every 2-3 weeks | Since last appearance | Books (primary), narrative history. Catch-up rule: covers full gap |
| This Week in History | Every 2-3 weeks | Current week | History is date-bound |
| Listening | Every 3-4 weeks | Since last appearance | Podcasts + audio drama + music (absorbs the old Listen + Channel) |
| Money | Every 3-4 weeks | Since last appearance | Personal finance + consumer fintech + side-hustle/Etsy (absorbs Long Game + Wallet + Ledger) |
| Places | Every 3-4 weeks (more near trips) | Since last appearance + forward 2-4 weeks for events | European travel + theme parks + NI local (absorbs Itinerary + Local) |

**Trigger-driven (NOT on this table):** **The Saga** (lore deep-dive) has no cadence timer — it runs on a live peg, not a clock. See § Auto-Triggered Specials → "The Saga (trigger-driven)" and its brief in `references/sections.md`. The planner does not deficit-promote it.

**Folded away in v8.27 (do not schedule — they no longer exist as standalone sections):** The Workshop and The Lab fold into **The Session** (training science + gear are now rotating angles within it); LEGO folds into **Pixel & Byte**; The Listen + The Channel → **Listening**; The Long Game + The Wallet + The Ledger → **Money**; The Itinerary + The Local → **Places**. The Toolkit is no longer rotating — it is a fixed-but-yields section (see § Section Structure).

### Selection Rules

1. **Check the state file** (`signal-state.json`) for `rotating_sections` — each entry has `last_appeared` date.
2. **Pick the most overdue sections first.** If The Shelf last appeared 3 weeks ago and Money 2 weeks ago, The Shelf has priority.
3. **Cap at 2-3 rotating sections per issue** to maintain pacing. Rotating sections should be substantive (300-600 words each, except The Shelf which can be longer). The issue's bulk comes from the fixed sections' considered pieces; rotating sections add variety on top, not bulk. Fewer slots is deliberate (v8.27) — it keeps the issue from padding.
4. **Places overrides normal cadence** when a trip is approaching — it appears every issue or every other issue in the lead-up. Check state file for `upcoming_trips`.
5. **Don't force it.** If research for a rotating section turns up nothing worthwhile, skip it even if it's overdue. The cadence is a guide, not a mandate.
6. **Ensure variety across a month.** Over any 4-issue stretch, aim for each of the 5 rotating sections (The Shelf, This Week in History, Listening, Money, Places) to appear at least once. The Saga is excluded — it is trigger-driven, not on a cadence (see Cadence Table).
7. **Hard cadence floor (planner-enforced).** A rotating section CANNOT be scheduled unless `weeks_since_last_appeared >= cadence_low` (the lower bound of its cadence band). The planner-side validator rejects any chapter plan that schedules a section inside its floor. Override: if no other rotating section is eligible (rare; only happens when most of the roster is too-soon AND the issue still needs slots), the planner picks the most-overdue section and the validator emits a warning instead of a hard fail.

8. **Deficit promotion (mandatory force-include).** A rotating section with `weeks_since_last_appeared >= 2 * cadence_high` is force-included in the next eligible issue, regardless of editorial preference. The planner must include it; the validator rejects any plan that leaves a deficit-eligible section out without an explicit reason field (`"deficit_override_reason"`). Prevents the Ledger / Wallet droughts seen in early v8.x.

9. **Default research window when `last_appeared` is null.** When a rotating section appears for the first time after a state file reset (or first-ever appearance), its research window defaults to "past 4 weeks" — NOT open-ended. Prevents the first appearance of a section from surfacing months-old news (e.g. the Revolut-from-March bug). Override via explicit `initial_research_window_weeks` field in state if the editor wants different.

### Placement: Interleave, Don't Stack

**Rotating sections must be woven between fixed sections, not dumped at the end.** They should feel like natural parts of the issue, not an appendix. Each rotating section has a preferred placement slot:

| Rotating Section | Preferred Slot | Reasoning |
|---|---|---|
| The Shelf | Between Screen & Sound and The Session (original position) | Natural flow from entertainment to books |
| Listening | Between Screen & Sound and The Session | Pairs with entertainment, breaks before fitness |
| Money | Between The Touchline and Screen & Sound | A breather between dense sections |
| Places | Between The Session and On the Radar | Travel/events naturally leads into the calendar |
| This Week in History | Between The Session and On the Radar (original position) | Reflective close before the forward-looking calendar |
| The Saga *(trigger-driven)* | Between Screen & Sound and The Shelf | Sits in the "story" cluster when a peg fires it |

The Toolkit, when it appears (fixed-but-yields), sits between The World This Week and Pixel & Byte — productivity/tech feels at home near the gaming section.

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

Removed. Replaced by the Lead + Companion structure (see § Article Structure). The anchor-piece rotation was unenforced across 8 weekly issues; the new two-anchor structure subsumes its purpose of giving every issue a second centre of gravity.

---



---

## search-checklist

## Search Checklist

Run the **core groups** every issue. Run **rotating groups** only when that section is selected for the issue.

### Core Groups (every issue)

**Group 1 — News & Geopolitics:** dominant running story, world news. **UK / national politics is out by default** (see the UK / national politics rule in § Key Rules) — scan for it only to catch the rare genuine landscape shift (an election *result* that changes the picture, a government actually falling) and to surface a one-line safety-net mention of any big Westminster story in the Catch-Up roundup. **No story is auto-promoted to the Lead.** A UK-politics development — even a leadership challenge or a cabinet resignation — is *not* automatically a Lead-1 candidate (the v8.x auto-promote mandate was the direct engine of the Starmer ×3 run). It is covered like anything else, and it leads only if it passes the two-factor Lead test (§ Article Structure: did it move this week AND can we add the layer the daily couldn't). The news-breadth floor (Lens-not-Filter) still holds: a genuinely big world story always gets *covered*, in the Lead if it clears the test, otherwise as a Catch-Up line.

**Group 2a — Gaming (for Pixel & Byte, every issue):** Nintendo Switch 2, Steam Deck / Steam Machine, GeForce Now, high-quality tablet games, plus generalist gaming (the biggest game of the year gets covered even if it's not on Switch) — what came out this week + highlights of the next month + *new* rumours-with-analysis. LEGO news and releases (LEGO now lives in Pixel & Byte as an occasional "play" beat).

**Group 2b — Tech & tools (for The Toolkit, when it runs):** consumer tech (Pixel/Xiaomi/e-readers, wearables hardware as consumer news), consumer AI tools, Android apps / tablet productivity / workflows. The Toolkit yields when thin; when it runs, cover the full gap since its last appearance.

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
| Ember period | `.mast-period` / `.brand-period` | Ember-coloured period on "The Signal." wordmark in masthead and cover. (Enhancement 22G) |

**Entry pattern rotation rule:** no two adjacent articles should open the same way. Rotate between `.entry-stat`, `.entry-quote`, `.entry-bullets`, `.entry-question`, and plain prose openings. This applies across articles within a section and across section leads.

**Breather band usage:** place 1-2 breather bands per issue between particularly dense sections. Use light variant between light/warm backgrounds, dark variant between dark backgrounds (Touchline, Screen & Sound, Shelf). Don't overuse — they're breathing room, not filler.

**Rotation rule:** no 3+ screen-heights of unbroken prose anywhere. Vary which sections use split layouts, where pull quotes appear, whether history uses timeline or bullets, which also-lists use card variant. Use entry patterns to vary article openings. Use sidebar-float as an alternative to split layouts. Use compare panels where a natural comparison exists.

---


