# Spec slice — specials

_This file consolidates the specials/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._


---

## overview


  **Lead-grade (cover this fully — often as a lead, never less than substantial Also coverage):**
  - General election campaigns and results
  - Council / Senedd / Holyrood / NI Assembly election RESULTS at the aggregate level when they shift the national picture (a Reform breakthrough; Labour losing 1,500 councillors; first head of devolved government to lose their seat in post; the two-party system fragmenting)
  - Live PM / opposition-leader leadership challenges (MPs publicly calling for resignation, union withdrawal of support, named challengers emerging, vote-of-confidence threats)
  - Major government policy with national impact (Budget, NHS structural reform, immigration policy with measurable change, major tariff/trade decisions, headline legal rulings against the government)
  - Party-leadership changes at the top of any major party (Labour, Conservative, Reform, Lib Dem, Green, SNP, Plaid)
  - Cabinet-level resignations or sackings
  - Constitutional and devolution shifts (e.g. credible second Scottish independence referendum, NI border-poll motion progressing)

  **Parish-pump (exclude or one-line in Also at most):**
  - Individual constituency by-elections (Bromley-tier)
  - Ward-by-ward council results, named candidates, individual mayoralty wins/losses unless they touch a Lead-grade story (e.g. "Camden Labour leader lost seat to Greens" matters because it's Starmer's own borough during a leadership crisis — covered as a beat inside the leadership story, not as its own item)
  - Individual MP scandals that aren't government-shaking
  - NI Assembly party-on-party arguments that don't change policy: DUP-vs-Alliance street-name disputes, parade-route arguments, language-act flag arguments, identity-politics theatre with no legislative outcome
  - Westminster process stories: committee reshuffles, whip rows, Speaker rulings, parliamentary procedure disputes
  - Polling-only stories without an event behind them ("Reform 5 points ahead" with no election trigger)

  **The test:** is this a moment where the political landscape shifts, or is this routine politics? The Bromley by-election is routine even when it's surprising. "Reform takes 1,453 council seats" is a landscape shift. "30 Labour MPs calling on the PM to resign" is a landscape shift. "DUP threatens to walk over street name" is theatre. When the landscape shifts, lead with it. The same logic applies to Irish, Scottish, Welsh and broader European national politics — the threshold is "does the shape of national politics actually change?"



---

## cover

---

## Visual Design

**The template parts in `assets/template-parts/` are the authoritative structure reference.** Each file holds one logical section (cover, navigator, world, touchline, etc.). Use their class names and component patterns exactly. Read only the parts this issue uses.

**CSS/JS injection:** Do NOT read or paste any file from `assets/css/` or `assets/script.js` into context. Instead, place `<!-- INJECT:CSS -->` in the `<head>` and `<!-- INJECT:JS -->` before `</body>`. After generation, run `scripts/inject-assets.sh` to inject the full CSS and JS automatically. This saves significant context for research.

**Fonts:** Cormorant Garamond (headlines, body), DM Sans (UI, tags, labels), JetBrains Mono (section labels, dates).

**Section backgrounds:** World = `--paper` (light), Pixel & Byte = `--warm`, Touchline = `--pitch` (near-black), Screen & Sound = `--screen-bg` (dark purple), Shelf = `--shelf-bg` (dark brown), Session = `--session-bg` (light green), History = `--hist-bg` (parchment). **Rotating section backgrounds:** Pantry = light warm/terracotta accent, Workshop = light grey/steel accent, Toolkit = light blue-grey/cyan accent, Ledger = warm cream/amber accent, Long Game = cool grey/navy accent, Wallet = clean white/teal accent, Itinerary = warm sand/coral accent. New rotating sections should use CSS custom properties following the same pattern as existing sections.

**Dark sections:** body text uses `rgba(255,255,255,.8)`. DYK boxes adapt to section palette.

**Output:** single HTML file, CSS and JS injected via build script, responsive (960px max-width, breakpoints at 820px and 600px). Reader's primary device is a Xiaomi Pad 8 tablet (~800px portrait), which sits BETWEEN the 820px and 600px breakpoints — always sanity-check tablet rendering, not just desktop and phone.

**Tablet column-width rule (special editions):** Centred display blocks that use `max-width: <N>ch` (manifesto, huge pull quotes, image-quote blockquotes, diptych body) must have a tablet override at `@media (min-width: 601px) and (max-width: 1024px)` that widens the measure with `min(<pct>%, <px>)` instead. At tablet, `clamp()` font sizes sit at their mid-scale (~5vw of 800px ≈ 40px) and a 20ch limit collapses to ~360px — a narrow column marooned in the middle of the viewport. Always widen to at least 90% of the viewport up to a sensible px cap. The same logic applies if you add any new centred component bound by `ch` measure: include the tablet override in the same patch.

**Cover height rule (all formats):** `.cover` must fill the full viewport on first load — no next-section chrome (chapter gate, first headline, ground colour) should peek up from below the fold. Implementation: `min-height: 100vh; min-height: 100dvh; box-sizing: border-box` on the base rule, and the same full-height on the mobile override at `@media (max-width: 720px)`. **Do not regress to `82vh` / `72vh`** — those were from an earlier pre-tablet version and leave the cover shorter than a modern phone or tablet viewport. `100dvh` ensures the cover stretches to the full window whether the mobile URL bar is shown or hidden. The scroll-cue inside the cover foot is the reader's sole cue to keep scrolling; nothing from the next section should compete with it. If you add a new component inside `.cover`, use `grid-row: auto` and let the existing `auto 1fr auto` track layout anchor it — don't set a fixed cover height that shorter than the viewport.

**Tablet ground-level gutter rule (special editions):** `.sp-ground-paper` and `.sp-ground-ink` chapter wrappers are full-bleed by design — the background tone reaches the viewport edge. Their CONTENT is given a horizontal gutter on tablet and mobile by `26-special-editorial.css` (28px tablet / 20px mobile, with `env(safe-area-inset-*)` floors). When you add a NEW component inside a chapter that should also be full-bleed (like `.sp-pull-break`, `.sp-folio`, `.sp-gallery`, `.sp-image-strip`, `.sp-scroll-image.is-fullbleed`), you MUST add it to the `:not(...)` exemption list in that media query — otherwise it'll inherit the gutter and look misaligned against the other full-bleed components.

**Navigator variants:** default grid (`04-navigator.html`) for most issues; TOC-style (`04-navigator-toc.html`) for longer, more literary issues — special editions, deep dives, field guides. The TOC variant reads like a bound-magazine contents page and is opt-in per issue.

---

## Special Editions — Maximalist Motion System

Special editions (Countdown, Rewind, Versus, Season Review, Deep Dive, Blueprint, Starter Kit, Shortlist, Field Guide) opt into an additive motion + chrome layer on top of the standard Signal identity. This layer is defined in `assets/css/23-special-chrome.css`, `assets/css/24-special-motion.css`, and the special-edition block at the bottom of `assets/script.js`. It activates only when `<body>` has `class="mag-body is-special"`.

### Content-first contract (non-negotiable)
Every motion component below obeys these rules. Never ship a special edition that violates any of them:
- **No scroll hijacking, ever.** Native scroll speed and direction are untouched.
- **No motion on body copy.** Only chrome, openers, and decorative layers animate. Prose is always static.
- **Stagger reveals cap at 400ms total.** Word-level reveals use 40ms delays and stop after ~10 words.


---

## meanwhile

  - **Opinions are reported, not held.** Strong claims like "skip this one", "worth the wait", "tourist trap" are allowed — but each one must be **a paraphrase of converging source signal**, not the agent's verdict. Surface it as such: "reviewers consistently warn it's a tourist trap", "the consensus across blogs and Reddit is it's worth the wait for the dragon-themed dessert". The voice has a spine because the sources do; if the sources disagree, say that too ("opinions split: Reddit rates it highly, TripAdvisor doesn't"). Never hedge invented opinion as fake-strong opinion.
  - **Insider moments delivered as gifts.** Timing tips ("reviewers suggest 11:30 to beat the rush"), off-menu asks, hidden seating, the second-floor nobody knows about — surface these inside the prose, not just in sidebars. Every one must trace to a real source; if it can't, cut it.
  - **Theming and atmosphere as equal citizens to food quality.** When sources note a mediocre meal in an incredible room, say that. When they note a great kitchen in a soulless space, say that too. Theming/atmosphere claims still need source backing — a blog photo, a quoted line, a Reddit comment.
  - **Energy in the prose, not the punctuation.** No exclamation-mark spam. No "you won't believe what's at #3" listicle voice. No "trust me, you'll love it". The excitement comes from sounding like an editor who has done the reading — not like someone who has been there themselves.
  - **Practical backbone stays intact.** Prices, booking notes, dietary flags, kid-friendly callouts, queue tactics — all still there. They're just delivered inside prose that sounds excited to share them, not a database dump.
  - Field Guide lands around 45/55 hype-to-practical, front-loaded with hype. The Countdown (2-3 weeks out) does the pure anticipation work with zero homework. These voice rules sharpen every section — both the Unmissables up front and the ranked practical chapters that follow.
- **Multiple options, always.** The reader is there for multiple days and wants choice. Every meal slot (breakfast, lunch, dinner, snacks, desserts, drinks/coffee) should have 3-5+ options ranked or categorised. Include: what to order, price range where findable, atmosphere/theming notes, whether it's table-service or grab-and-go, and any booking requirements. Practical detail lives **inside** the prose where possible, not only in sidebars — the reader is reading for pleasure, not scanning a database.
- **Cover the full spectrum.** Fine dining with amazing theming → solid family meals → quick bites when you're knackered → unique treats you can't get anywhere else → best coffee spots → "we just want a burger and chips" fallbacks. The reader wants to know about the dragon-shaped dessert AND the reliable burger joint.
- **Theming and experience matter.** If a restaurant has incredible theming worth seeing even if you don't eat there, say so. If a place has an atmosphere that makes a mediocre meal worthwhile, say so. If a café is the best stroopwafel in the park, say so.
- **Multi-venue trips:** If the trip covers multiple parks/resorts (e.g. Efteling + Beekse Bergen), the primary destination gets the full treatment. Secondary venues get a shorter but still practical section — key dining options, standouts, and practical notes.
- **Research depth matters.** This format lives or dies on completeness. Source from: official park/resort websites and menus (source-of-truth for what exists today, prices, opening hours), TripAdvisor and Google reviews, travel blogs (DFBguide, TravelMamas, park-specific forums, family-travel and solo-travel blogs), Reddit (r/Efteling, r/themeparks, r/foodtravel, destination-specific subs), YouTube food tours and vlogs, Instagram and TikTok location tags, food-blogger Substacks, and any Dutch/regional-language sources where relevant. Cross-reference at least three source types per major venue to catch seasonal menus, recently closed spots, new openings, and the gap between marketing copy and what diners actually report. **Imagery follows the same diversity rule:** traveller photos from blogs, Reddit photo threads, well-credited Flickr/Instagram posts, and food-tour video stills are all in scope alongside official press shots — quality and credit are the bar, not source pedigree. **The photo carries the sensory load that the prose does not** — see the Factual write-up rule. A specific, well-credited shot of the actual dish on the actual plate does work the writing must not attempt.
- **Audience callouts — stated as venue character, never as reader instruction.** A sidebar or icon system can flag places by their general character: "family-friendly", "adult-oriented evening spot", "buggy-friendly", "late-night", "walk-in welcome", "booking essential". These are facts about the venue, not directions to the reader. Banned: "perfect for your son", "your 10-year-old will love", "great for the kids" — the reader's family composition is invisible per Gate 1A. The reader can apply venue character to their own circumstances; the magazine never does it for them.
- **Tone is conversational, not instructional.** Phrases like "worth building an evening around", "the pick when you want something quiet after a loud day", "the kind of place that rewards a long lunch" frame venues by their general character without addressing the reader directly. Banned: "one for each of you", "you and your partner", "take the kids", "if you've been waiting for…" — these all violate Gate 1A. Write as if any reader of the magazine might be heading to this trip; the warmth comes from venue-level specificity, not from second-person address.
- **Images do heavy lifting.** Food photography isn't supporting content — it's the reason to turn the page. Every Unmissable gets a strong image. Major meal-slot sections get at least one. Lean toward bigger images, less whitespace, more visual momentum. The reader is scrolling on a tablet with coffee — make it a pleasure to look at.
- Use `.also-cards` for option grids, `.compare-panel` for head-to-head comparisons (e.g. two similar restaurants), `.stat-bar` for price ranges, `.sidebar` for tips ("book 2 weeks ahead" / "queue is shortest at 11:30"), `.big-number` for standout stats, `.dyk` for food trivia, `.tier-hot`/`.tier-warm`/`.tier-note` for ranking tiers.
- Use 10-14 component types. Images are critical — food photography sells the recommendations.
- Best for: theme park food guides, city eating guides, resort dining guides — any trip where finding the right places to eat is a meaningful part of the experience.

All special editions use the same design system and component library. Use sidebars, stat bars, DYK boxes, card stacks, collapsible sections generously — a special edition with no visual furniture is a wall of prose.

---

## Auto-Triggered Specials

The workflow's **scout step** (step 2 in SKILL.md) evaluates these triggers with 2-4 quick searches **before** committing to any full research pass. This prevents wasting research on a standard weekly that gets discarded. The reader never requests these — they appear as a surprise, like a magazine supplement. **All formats remain manually triggerable at any time** in addition to their auto-triggers.

### The "Meanwhile..." Section

When a special edition replaces the standard weekly, it must include a **"Meanwhile..."** section before the Footer. This ensures the reader never misses a week of news.

- 12-18 bullet points covering the week's biggest stories across all fixed-section areas: world news, tech/gaming, sport (results, tables, key stories), entertainment, and any breaking news.
- **Every item must include a linked source** so the reader can go deeper on anything that matters to them.
- Format: bold headline + one sentence + linked source. Compact, scannable.
- Use `.also-list` with `.tier-hot` / `.tier-warm` / `.tier-note` tiers to signal importance.
- This is a catch-up safety net, not a section to linger in. Keep it tight.

### Auto-Trigger Logic

Evaluate during the **scout step** (before full research). Priority order — highest wins. Only one special per week.

**Priority 1 — Calendar-Fixed Triggers (predictable, always fire)**

| Trigger | Format | When |
|---|---|---|
| Half-year mark | Rewind — "H1 in Review" | Last Sunday of June (defer if within 7 days of a trip — see trip-aware rules) |
| Year-end | Rewind — "The Year in Review" | Last Sunday of December |
| **Trip food guide (food-focused, always)** | **Field Guide** | ~6 weeks before an `upcoming_trips` entry with food-research value. **MANDATORY:** read § The Field Guide in full before any planning or writing — see the 14 headline rules at the top of that section. |
| Trip approaching | Countdown | 2-3 weeks before an `upcoming_trips` entry in state file |

**Priority 2 — Event-Driven Triggers (detected during research)**

| Trigger | Format | Detection |
|---|---|---|
| Serie A season concluded | Season Review — Serie A | Research finds final matchday results |
| Premier League season concluded | Season Review — Premier League | Research finds final matchday results |
| Major tournament concluded | Season Review — [Tournament] | Research finds final/closing ceremony |
| A major product launch this week | Deep Dive or Versus | Research finds a significant launch in a core interest (Switch 2, major game, new console, etc.) |
| Two competing products launched/announced close together | Versus | Research finds a natural head-to-head |

**Priority 3 — Editorial Picks (the safety net against dry spells)**

If no Priority 1 or 2 trigger has fired in the last 5 weeks, the editor picks a special from the pool below. These are evergreen — they don't depend on external events:

| Format | Example Topics |
|---|---|---|


---

## chapter-gate

- **`.sp-spine`** — decorative inline SVG hairline that draws itself in (`stroke-dashoffset` animation) when scrolled into view. Add 1-2 per long chapter inside the `.sp-margin` column or `.sp-rail` to add typographic depth without weight. Pattern: `<svg class="sp-spine" viewBox="0 0 2 200"><path d="M1 0 V200" /></svg>` (or a curve). Lives decoratively in the margins, never near body text.

**Reduced-motion:** All tier-5.5 motion is wrapped in a `@media (prefers-reduced-motion: reduce)` kill switch — animations collapse to instant, transforms reset, decorative drift disabled. Content-readable state always reachable without motion.

### Signature moments — ONE per format (mandatory)

Each special edition format has exactly one signature moment — a single visual element readers will remember and describe to someone else. They are not interchangeable. Including a Countdown's hourglass in a Versus issue would dilute both. Use the prescribed component for the format and no other.

| Format | Component | Where it lives | Required content hook |
|---|---|---|---|
| Countdown | `.sp-sand-clock` | Cover, below masthead | `data-total="<days>" data-remaining="<days>"` on the wrapper |
| Rewind | `.sp-memory-wall` | Fixed right gutter (desktop), strip above sections (mobile) | One `<div class="mw-cell" data-item-id="…" style="background-image:url(…)">` per item; each prose section gets `data-reveals="id1,id2"` |
| Versus | `.sp-fault-line` | Sticky vertical line spanning all comparison sections | `data-max-shift="90"` on the line; each paragraph in the comparison `<p data-lean="-2"…+2>`; verdict element `data-verdict="a"\|"b"` |
| Season Review | `.sp-form-tape` | Top of the issue + repeated at top of each chapter | Each chapter `<section data-results="W,W,D,L,W" data-result-from="0">…</section>`; tape pre-renders one `.ft-pill` per fixture |
| Deep Dive | `.sp-thread-pull` | Fixed left margin (desktops ≥ 1100px only) | Wrapper element `[data-tp-track]` defines the scroll range; markers `<g class="tp-marker" data-at="0.42">…</g>` inside the SVG carry concept-tag text |
| Blueprint | `.sp-build-meter` | Sticky top of viewport, below masthead | One `.bm-cell` per phase in the meter; each phase section `<section data-phase="0">…</section>` |
| Starter Kit | `.sp-cold-start` | Cover/opener, gates the prose | One word, split into `<span class="cs-letter">K</span>` per letter. Wrap the rest of the issue in `.sp-cs-after` |
| Shortlist | `.sp-deck-reveal` | Mid-issue picks block | A `.sp-deck` with one `.dk-card` per pick (#1 first / on top); scroll triggers `<div data-deck-step="1">…</div>` peel cards |
| Field Guide | `.sp-pinboard` | Cover/opener (sticky 100vh) | A `.sp-pinboard` with `.pb-stage` background image + `.pb-pin`/`.pb-label` pairs (`--x:38%; --y:52%`); prose sections referring to a pin add `data-pin-id="<id>"` to trigger pulse |

**Authoring rules:**
- Pick the right one for the format. One per issue. Don't mix.
- Always provide the data hook listed above; without it, the component renders inert (which is the safe fallback).
- All nine moments degrade gracefully under `prefers-reduced-motion` and on missing JS.
- **Mobile gating:** `sp-thread-pull` hides below 1100px; `sp-memory-wall` collapses to a horizontal strip below 900px; everything else adapts.
- **No content sacrificed.** If the moment doesn't fit the issue's content shape (e.g. a Versus issue with no clear A/B paragraphs), skip the moment rather than force the structure.

### Chapter transitions + ambient (format-agnostic)

These components compose with the existing `.sp-wipe`, `.sp-curtain`, ground alternation, and chrome — they are punctuation, not replacements. Available to every special edition format.

**Transitions (use sparingly — these create a deliberate reading pause):**

- **`.sp-stat-curtain`** — full-viewport overlay rises with one hero stat or epigraph, then retracts. Use at **most twice per issue** at moments where a hard pause is editorially earned (chapter break before the centrepiece, before the verdict). Markup: `<div class="sp-stat-curtain" id="sc-1"><p class="scu-stat">23,400</p><p class="scu-caption">Roller-coaster runs in 2025</p></div>` plus a trigger `<div data-curtain-for="sc-1"></div>` placed at the chapter end where it should fire.
- **`.sp-page-fold`** — bottom 40vh folds upward via 3D rotateX. Use **only at paper↔ink chapter handoffs** to dramatise the ground swap. Markup: wrap the boundary in `<div class="sp-page-fold-wrap"><div class="sp-page-fold" style="--sp-ground-prev: var(--sp-paper);"></div><div class="sp-page-fold-shadow"></div></div>`. Set `--sp-ground-prev` to the outgoing chapter's ground colour token. Maximum 2 per issue.

**Ambient (these run continuously and become part of the issue's atmosphere):**

- **`.sp-chapter-beads`** — fixed right-gutter bead strip, one per chapter, with within-chapter progress connector. **Universal: works on standard weekly AND every special edition.** Markup: a single `<aside class="sp-chapter-beads" aria-hidden="true"></aside>` near the end of `<body>` (already included in `template-parts/19-closing.html`). **Chapter discovery order:** (1) elements with `[data-sp-chapter]` — typical for specials; (2) fallback to `.mag > section.sec` — used by every standard-weekly section. **Title resolution:** `[data-sp-chapter-title]` → first `<h2>` text → section `id` (title-cased) → `Chapter N`. Accent colour auto-cascades: `--sp-accent` on specials, `--accent` on standards. **Mobile (≤ 820px):** collapses to a thin vertical line with no labels. Click a bead to scroll to that chapter.
- **`.sp-horizon`** — bottom-edge strip bleeds the next chapter's ground colour upward as within-chapter progress nears 100%. Markup: a single `<div class="sp-horizon" aria-hidden="true"></div>` near the end of `<body>`. Each chapter element must carry `data-sp-chapter` AND `data-sp-ground-color="#hex"` so the next chapter's colour is known.

**Authoring contract for ambient:**
- Both ambient components share the same per-chapter progress calculation (one rAF loop, zero duplicated work). Adding `.sp-horizon` for free if you've already added `.sp-chapter-beads`.
- Both require chapters to be marked with `data-sp-chapter` on the section root and `data-sp-chapter-title` for tooltips (specials). **Standard editions need no mark-up** — beads auto-discover from `<section class="sec">`. `data-sp-ground-color` is required only if you use `.sp-horizon` (special editions only).
- Reduced-motion: beads stay (active state only, no fill animation); horizon collapses to a static 2vh strip near chapter end.

### Chapter gate (MANDATORY for every chapter on every special edition — v8.5, sticky scroll model)

**The chapter gate is the single most important element in a special edition.** It is the digital equivalent of turning a page in a real magazine — a viewport-locking moment that unambiguously says *"a new chapter starts here"*. It is the permanent, unmissable signal the reader can spot at any scroll speed.

**Mandatory on:** every `[data-sp-chapter]` in every special edition. If a chapter does not open with `.sp-chapter-gate`, the issue fails Gate 2.

**Structure:**
```
<aside class="sp-chapter-gate"
       data-chapter-num="V"
       data-chapter-title="BEEKSE BERGEN"
       data-chapter-arc="Act III — the wild">
  <p class="scg-deck">Five days inside Europe's largest safari park, and a hotel where the lions wake you up.</p>
</aside>
```
Place the gate **immediately before** the chapter section's opening `<section data-sp-chapter="…">` tag. The controller auto-builds the black panel and drives the scroll-progress reveal.

**How it behaves (v8.5 sticky scroll model):**
- The gate is a 160vh scroll track containing a `position: sticky` full-bleed black panel (`#0A0E17`) that locks to the viewport for ~1 screen-height of scroll.


---

## imagery-budget

- **`prefers-reduced-motion` disables every decorative animation.** The controller short-circuits after the splash cleanup.
- **JS-off still renders a complete issue.** All motion is additive — the issue must be fully readable with scripts disabled.
- **Word counts and section depth are not reduced to make room for motion.** Motion sits around content, not in place of it.
- **Format-variable intensity.** Countdown / Versus / Rewind go loud. Deep Dive / Blueprint / Field Guide stay quiet (splash + ticker + manifesto only).

### Authoring a special edition
1. On `<body>`, add `is-special` and `data-special="<format>"` where format is one of: `countdown`, `rewind`, `versus`, `season-review`, `deep-dive`, `blueprint`, `starter-kit`, `shortlist`, `field-guide`.
2. **For Countdown only:** add `data-dday-start="N"` on `<body>` where N is the number of days between the issue date (today, when generating) and the event. The D-day badge displays this authored value statically — a magazine issue is a snapshot and the badge must agree with the prose, forever. Compute N at generation time as `(trip_date - today)` in days. The Countdown auto-trigger fires 2-3 weeks before a trip, so N is typically 14-21. If generating a prototype or back-dated issue, use the fictional issue-date reference. (Optional: also add `data-trip-date="YYYY-MM-DD"` for human reference, but it does NOT drive a live countdown at runtime.) The previous scroll-scrubbing pattern (`data-dday-start` + `data-dday-end` interpolated by scroll percentage) has been removed — a scroll-driven countdown is nonsensical.
3. Include the components from the component list below as appropriate for the format. Each component has a documented HTML contract in `component-contracts.md` (or inline in the CSS).
4. Inject assets with `scripts/inject-assets.sh` as normal.

### Component list
**Chrome (tier 1 — all special editions):**
- `.sp-splash` — full-bleed pre-roll wash with format glyph, self-dismisses after 2.2s
- `.mast-ticker` — horizontal marquee masthead replacing the static masthead
- `.sp-format-badge` — rotated ◆ format label, fixed top-right
- `.sp-footer-card` with arc notch + ◆ seal — closing card

**Scroll motion (tier 2 — loud formats):**


---

## editorial-body-kit


**In addition, across the whole issue:**
- At least **2 sections** use a multi-image component (gallery, diptych, or image-strip)
- At least **3 sections** use `.sp-scroll-image` or `.sp-inline-figure` for embedded imagery
- At least **2 sections** use `.sp-pullquote-huge` to break up prose
- Long prose sections (>500 words) include `.sp-kicker` on h3/h4 headings
- Long prose sections include at least one `.sp-marginalia` or inline `.sp-number` callout
- Section transitions alternate between `.sp-wipe` and `.sp-curtain` for rhythm variety — don't use the same transition twice in a row

These are minimums — more is fine. Research images for EVERY major section, not just the cover topic.

### Image-caption integrity (v8.10.3 — hard rule)

A wrong image with a confident caption is worse than no image at all. Three failure modes have been observed in past issues; all are forbidden, all are mechanically scannable in Gate 1F.

**1. No duplicate `src` URLs in one issue.**
Every `<img src="…">` in the rendered HTML must point to a unique URL. Re-using the same image with two different captions is a fabrication: at least one caption is lying. If the same image genuinely belongs in two places, redesign — find a second source for the second placement, or cut one of the placements. The most common variant of this bug is the same YouTube thumbnail used twice with contradictory subjects (e.g. `i.ytimg.com/vi/<id>/maxresdefault.jpg` captioned as Venue A's pools in chapter III and Venue B's harbour in chapter VII). Banned without exception.

**2. YouTube thumbnail subject must match the video.**


---

## signature-moments


The tier-4 imagery budget addresses *what's in* each chapter. The tier-5 editorial body kit addresses *how each chapter is structured*. Both apply.

**Per-chapter:**
- Every chapter wrapper carries `.sp-ground-paper` or `.sp-ground-ink`. Chapters alternate ground value — never two paper chapters in a row, never two ink chapters in a row. The shift IS the transition; this replaces the need for a `.sp-wipe` or `.sp-curtain` between alternating-ground chapters (use those between same-ground chapters or for rhythm variety only).
- Every chapter opens with a `.sp-chapter-chrome` strip carrying its roman numeral, name, and slug.
- Every chapter contains at least one `.sp-folio` watermark for typographic depth.
- Any chapter ≥800 words MUST use a `.sp-spread` layout (rail + body + margin). Shorter chapters may use a single-column body but still need at least one `.sp-brief`, `.sp-hero-quote`, or `.sp-dash` mid-prose.
- Every chapter ends with a `.sp-signoff` line.

**Across the issue:**
- At least 1 `.sp-pull-break` for a major rhythm break (typically between the second and third chapter)
- At least 1 `.sp-bridger` interlude inside a long chapter
- At least 1 `.sp-dash` instead of an italicised list of stats anywhere stats are presented
- Section headings inside `.sp-spread-body` use the `§` section mark automatically (built into the CSS)
- First paragraph of each `.sp-spread-body` gets a 110px italic accent drop cap automatically (built into the CSS) — do not manually wrap the first letter

### Editorial motion layer (tier 5.5) — MANDATORY for loud special editions

The tier-5 body kit gives the magazine its structure. The tier-5.5 motion layer (in `28-special-motion-editorial.css` + matching JS controllers in `assets/script.js`) gives it kinetic life. Inspired by adapted motion vocabulary from landonorris.com (wipe-band reveals, scroll drift, staggered entries) — translated into editorial idiom. **Most of it is automatic** — applied by the JS controllers on scroll. A few patterns require explicit class application.

**Automatic — no markup changes required:**
- `.sp-folio` watermarks drift ±60px on scroll (subtle parallax, via `--sp-folio-y`)


---

## chapter-transitions

- `.sp-chapter-chrome` opens with a sequenced wipe (numeral → hair → name → slug, staggered)
- `.sp-dash-cell`s stagger in 90ms apart
- `.sp-tl-row`s stagger in down the timeline
- `.sp-hero-quote` lifts in with the corner glyph drifting in opposite direction
- `.sp-brief` slides in with its accent rule scaling vertically from 0
- `.sp-pull-break` corner quote marks scale in from opposite corners
- `.sp-bridger` three columns enter staggered
- `.sp-spread` rail and margin slide in from opposite sides as body fades up
- `.sp-spread-body` first letter (drop cap) pops in with a slight scale
- `.sp-signoff` scale-in finale
- `.sp-caption-strip` hairline rule draws across
- All in-prose `<a>` links get an underline-draw on hover (background-size 0% → 100%)
- Native `scroll-behavior: smooth` on the document
- Ground-seam accent hairline appears between alternating-ground chapters
- Paper-bg components (`.sp-brief`, `.sp-hero-quote`, `.sp-bridger`, `.sp-margin`) automatically lock to ink text colour even when nested in `.sp-ground-ink` chapters (readability lock — no need to add `.sp-island` manually)

**Explicit class application — REQUIRED on loud specials:**
- **`.sp-band`** is THE signature move (the Lando wipe-band reveal). Every chapter chrome's `.sp-eyebrow` and `.sp-chapter-name` MUST carry `.sp-band`. Every `.sp-signoff` label MUST carry `.sp-band`. Every standalone `.sp-eyebrow` kicker above a major component title gets `.sp-band`. The JS auto-wraps the inner text into `.sp-band-t` on the first observation.
- **`.sp-band sp-band-thin`** — lighter underline-sweep variant. Apply to dashboard `.sp-dash-hint` kickers and caption-strip eyebrows where you want the sweep without hiding the text.


---

## multi-venue

### The Countdown
Pre-event build-up. **5,000-7,000 words, 18-25 pages.** Manual trigger: "Run a Countdown for [event/trip]." Best for: trips, launches, tournaments, any event worth building anticipation for.

**Canonical chapter order:** Cover → Foreword → By the Numbers → Event in Depth → Top Attractions (or equivalent venue-specific hype chapter) → Accommodation → Mood Board → What to Watch / Read / Play → Five Moments Worth the Trip → [Day-by-day plan — only if reader supplied one] → Before You Go (merged coda: surprising facts + essential logistics) → On the Radar → Footer.

**Hype over homework — the defining principle.** A Countdown exists to build anticipation, not to plan the trip. Logistics are compressed into a short coda near the end; the issue's weight sits in the chapters that make the reader *want to go*: the ranked attractions, the accommodation, the mood board, the moments worth the trip. If a chapter reads as a checklist or a how-to, it's in the wrong format — send that content to a Field Guide instead.

**Hype-chapter visuals — opt-in modifiers (v8.9.1).** The default special-edition chrome (full-viewport chapter gate, coral accent lockdown, paper/ink grounds) is tuned for literary formats like Deep Dive and Rewind. On hype chapters it dampens the exact pages that should amplify. Four opt-in modifiers exist in `32-hype-variants.css` to dial the chrome back where excitement is the job. Use on Countdown hype chapters (Top Attractions, Accommodation, Mood Board, Five Moments Worth the Trip, and By the Numbers when image-led) and on Field Guide's The Opening + The Unmissables. Never use on literary chapters — Deep Dive, Rewind, Season Review, Versus keep the full default chrome.

- **`.sp-chapter-gate.is-hype`** — compact gate variant. Same markup, same four text layers; track collapses to 60vh (was 110vh), sticky hold to 40vh (was 100vh), all layers fully revealed by progress 0.08 (was 0.20). The gate still announces the chapter; it no longer dwells.
- **`[data-sp-chapter].is-hype`** — attribute on the chapter wrapper that narrowly re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, and `.why-its-here`. Everything else (pull-quotes, briefs, dashboard strong, spread h2, eyebrow) stays demoted per the global accent lockdown. Coral stays rare — just not absent on the elements meant to shout.
- **`.sp-ground-gallery`** — third ground type alongside paper and ink. Neutral slate (#1A1E27), not pitch. Legal only on image-first chapters: Mood Board (primary use), Field Guide's The Opening when run image-led, optional for Five Moments Worth the Trip when the moment images are the point. Full-bleed image walls read as photography on a gallery wall instead of captioned content in a magazine spread.
- **`.unmissables` / `.unmissable`** — Field Guide Unmissables pattern. 6–10 picks, each a full-width editorial beat (NOT a card grid). Per pick: hero image with captioned credit rule, **factual write-up** (what it is, what's good about it, what to order — anchored in attributed quotes from reviewers/diners/bloggers, never invented sensory description), “Why It's Here” coral kicker line, practical footer strip (price / booking / timing / walk) as a mono `<dl>` under a muted rule. Practical detail lives INSIDE the pick — that's the 45/55 Field Guide rule made structural. Drop-cap forbidden on picks (reserved for chapter openings).

**When to apply them.** If a chapter's primary job is anticipation and it opens with imagery or a count-up stat, it's hype — add `.is-hype` to both the `sp-chapter-gate` and the chapter wrapper, and consider `.sp-ground-gallery` if the chapter is image-first. If the chapter's primary job is reflection or argument, it's literary — leave all four modifiers off. When in doubt, default to literary; the chrome is expensive-looking and holds up on its own. The modifiers are cheap to add and free to remove.

**Visuals-first or cut.** Every chapter in a Countdown must be able to carry its own imagery. Minimums by chapter type:
- **Narrative chapters** (Event in Depth, Top Attractions, Accommodation, Watch/Read/Play, Five Moments Worth the Trip): 3+ real, well-credited images — cut or reshape the chapter if it can't hit this.
- **Visual-led chapters** (Mood Board): 8–12 images, captions only.
- **Stat-led and coda chapters** (By the Numbers, Before You Go): 1+ image minimum — a stat dashboard doesn't need to be visually dense, but it still needs at least one establishing image to anchor it.
- **Five Moments Worth the Trip**: one strong image per moment (so five minimum). If a moment can't be illustrated, replace it with one that can.

All images must be real and credited (official venue media, Wikimedia, reputable travel press, the property's own site). No AI-generated imagery, no uncredited stock filler.

**Equal hype weight for multi-venue trips.** When a trip has two or more headline venues, every venue gets equal hype weight across the issue — but the *shape* of the hype can differ to match what each venue actually is. A theme park earns a "Top 5 Attractions" chapter; a safari resort earns "Top 5 Animal Encounters" or "The Safari, Ranked" — same job, different shape. The test is not "did I mirror the structure" but **"did I give both places equal hype weight and equal visual presence?"** Measured mechanically: total words per venue and total images per venue across the issue must sit within a 60/40 split. If one venue genuinely warrants a chapter the other doesn't (e.g. one has 70 years of history worth a chapter, the other doesn't), the other venue gets an extra chapter of equivalent weight elsewhere to rebalance. Never 8 chapters on venue A and a single history paragraph on venue B.

**Multi-venue destination theming (v8.10).** When a Countdown covers two or more headline venues, opt into per-venue theming so the reader's eye registers "a different place" the moment they hit a different chapter — without the issue fragmenting into two designs glued together. Activated by adding `data-multi-venue="true"` to `<body>` alongside the standard `data-special="countdown"`, then tagging each venue chapter section with `data-venue="efteling"` or `data-venue="beekse-bergen"` (use kebab-case venue identifiers). Defined in `33-countdown-destinations.css`. What the layer changes:
- **Per-venue ground.** `.sp-ground-paper` and `.sp-ground-ink` adopt the venue's paper/ink tokens (`--eft-paper` / `--eft-ink` / `--bee-paper` / `--bee-ink`). Cream + plum for Efteling; warm sand + dark earth for Beekse Bergen.
- **Per-venue accent.** Demoted secondary accents (kicker, brief-kicker, datum value, eyebrow, dashboard strong, pull-quote cite, spread h2 marker) repaint with the venue accent (`--eft-accent` antique gold, `--bee-accent` terracotta). Coral primary stays exclusive to gate numeral / D-day badge / progress bar; venue accents replace slate/bone, never primary.
- **Decorative venue glyph.** A faint mask-image watermark sits in the bottom-right of each venue chapter — a twisting vine + crown finial for Efteling, a giraffe silhouette (PhyloPic CC0) for Beekse Bergen. 0.06 opacity on paper, 0.08 on ink. `pointer-events: none`. No stacking-context changes — sticky pin, page-fold, chapter beads all unaffected.
- **Inline venue tag.** Authors can drop `<span class="sp-venue-tag">Efteling</span>` or `<span class="sp-venue-tag">Beekse Bergen</span>` inside a chapter (e.g. above the kicker on the chapter's first spread) for a tiny pill that labels the venue inline, painted in the venue accent.

The layer is purely additive: removing `data-multi-venue="true"` strips all theming and the issue renders identically to a single-venue Countdown. Wax seal stays giraffe-facing-right and standard rotation — one seal per issue, by design. Hype-variant chapters (`.is-hype`) keep their coral re-permission untouched; venue accent only fires on non-hype venue chapters where the global lockdown would otherwise apply. Galleries (`.sp-ground-gallery`) stay neutral slate and are explicitly preserved. Reduced-motion users get the same static glyph with no transitions. Cascade order matters: `33-countdown-destinations.css` must load AFTER `32-hype-variants.css` (alphabetical sort enforces this).

**Top Attractions (or equivalent) — mandatory when a venue has headline draws.** A ranked 5–7 item chapter with opinion. Each item: one strong image (ideally `.sp-scroll-image` or `.sp-image-quote`), a short take on *why* it's worth the queue / the early morning / the detour, and a one-line practical note (best time, height requirement, fast-pass eligibility, feeding times, whatever applies). Scales to multi-venue trips as parallel ranked chapters (one per venue), each with 5–7 items. For non-theme-park venues, reshape the chapter to fit: "Top 5 Animal Encounters," "The Safari, Ranked," "Five Corners of the Resort," "The Stages, Ranked" — whatever the venue is actually *about*. If the venue has no obvious ranking surface, skip this chapter for that venue and rebalance with an extra chapter elsewhere.

**Mood Board — mandatory.** A dense visual-only chapter: 8–12 images arranged in `.sp-image-strip`, `.sp-gallery`, or an image montage component. Captions only, no prose block. Pure atmosphere — what a week there actually *looks* like. For multi-venue trips, either split the board 50/50 between venues (labelled sub-sections within one chapter) or run two separate Mood Boards (one per venue). Never one board that skews to the more photogenic site.

**By the Numbers — a chapter, not just a stat block.** "The trip in eleven figures — before the prose starts." Uses `.sp-dash` plus one or two `.sp-number-huge` count-ups. Every venue represented in the numbers. Reads as hype because every stat is a brag: acres, coaster counts, animals, nights booked, miles from home, expected step count. Place early — right after Foreword — as the hype opener.

**Five Moments Worth the Trip — mandatory, third-person editorial voice.** A short chapter (~400–600 words) naming five specific *moments* (not attractions — moments) the reader should anticipate, with one image per moment. Written in the magazine's standard third-person voice, never first-person (no "I" or "we" — that breaks the reader-profile invisibility rule). Each moment is specific and opinionated: "The first sight of the Fairytale Forest at dusk, when the lanterns come on." "Breakfast on the safari resort terrace while the giraffes walk past the fence." For multi-venue trips, at least two moments from each venue. No all-one-venue lists.

**Title rule — use the reader's name for the trip.** The cover title and recurring chapter chrome must use the destination(s) the reader actually associates with the trip — the names they use when they talk about it — not the geographic locator that happens to host them. "Efteling & Beekse Bergen" not "Kaatsheuvel." "Walt Disney World" not "Lake Buena Vista." "Center Parcs Longleat" not "Warminster." If the reader has named the trip in their request ("the Efteling trip"), use that name verbatim. If they haven't, lead with the marquee venue(s) and only fall back to a city/region name when the trip has no anchor venue (e.g. a touring city break). The locator can appear once, lower down, as supporting context ("in the Brabant province of the Netherlands") — never on the cover or in the running chapter chrome. **The same name carries through the issue:** masthead ticker, navigator, foreword opening, and footer all use the reader's trip name. The locator is information; the trip name is identity.

**Itinerary rule — do not invent a day-by-day plan.** Only include a day-by-day / hour-by-hour itinerary when the reader has explicitly supplied one in their trigger or in conversation. If they haven't, drop the day-by-day chapter entirely and lean harder on the other chapters (event in depth, logistics, what to watch/read/play, surprising facts). A guessed itinerary reads as filler and undersells the trip — e.g. suggesting a half-day return to a venue the reader has already spent two nights at. When in doubt, omit. The Countdown is build-up, not a plan; planning is the reader's job.

**No filler chapters generally.** If a chapter doesn't have genuine content to fill it (real research, real opinions, real images, the reader's own plans), cut it. A tighter five-chapter Countdown that respects the reader's intelligence beats a padded seven-chapter one with invented schedules and obvious filler. The word-count band (5,000–7,000) is a target, not a floor.

**Logistics demoted to a coda.** The old standalone Logistics chapter is gone. Essential logistics (flights, parking, transfers, what-to-pack, currency, timezone, anything genuinely practical) are compressed into the "Before You Go" coda near the end of the issue, merged with Surprising Facts. Cap: ~400 words of logistics content total. Anything longer is either planning (belongs in a Field Guide) or filler (cut it). Logistics are homework; homework does not lead a Countdown.

**Accommodation chapter — mandatory when the reader has booked a hotel/lodge/resort.** A trip is judged at least as much by where you sleep as where you go during the day. If the reader has named the accommodation in their request or in conversation, the Countdown MUST include a dedicated accommodation chapter (positioned mid-issue, after Top Attractions and before Mood Board per the canonical order). Cover for each property: rooms (configurations, capacity, what makes them distinct), dining options on-site (every restaurant + bar + grab-and-go, with what to expect), facilities and activities included in the stay (pool, kids' club, animal encounters, water play, themed evening events), what's near it on-foot, and — critically — what makes it worth the premium over staying off-site. Multiple properties get parallel treatment: same structure for each, then a short "choosing between them" or "the order in which you'll see them" beat. **This chapter leans heavily visual** — hotels are some of the most photogenic content in the issue. Aim for 4–6 images per property: exterior/setting, room interior, signature dining space, signature facility/activity. Use `.sp-scroll-image`, `.sp-inline-figure`, and `.sp-gallery` aggressively here. Source from official property sites, the parent group's media library, well-credited Flickr/Wikimedia uploads, and reputable review blogs with image rights. Never AI-generated.

**A diptych or transition section is NOT an accommodation chapter.** A chapter labelled with a hotel/resort name in its gate (e.g. "WONDER HOTEL") must contain actual coverage of that property — rooms, dining, facilities, images — not a two-park contrast or a short pivot paragraph. If research on the named accommodation is thin, either (a) do more research before committing to the chapter, or (b) relabel the chapter to what it actually covers ("Two Temperaments", "Between the Parks") and move the accommodation coverage into a properly named chapter later. Never ship a chapter whose title writes a cheque the body can't cash — the gate is a promise to the reader. Mandatory minimum for an accommodation chapter: 400–600 words per property, at least 4 images per property, and at least one `.sp-gallery` or `.sp-image-strip`. If you can't hit the minimum, it isn't an accommodation chapter.

**Source diversity — beyond the official channels.** A Countdown's job is to make the reader feel the place. Official sites alone produce a sanitised, corporate-feeling issue. Research must draw from a mix: official venue/resort sites and menus for the source-of-truth facts; **plus** TripAdvisor/Google review threads, travel blogs (DFBguide, TravelMamas, themed-entertainment blogs, family-travel and solo-travel blogs alike), Reddit communities (r/Efteling, r/themeparks, r/solotravel, destination-specific subs), YouTube vlogs and food-tour videos, Instagram and TikTok location tags, and Dutch/regional-language sources where the trip warrants it. The reader's gut sense of "what's it actually like" comes from the unofficial layer; the official layer is just the spine. Cross-reference across at least three source types per major chapter. If everything in a chapter traces back to one website, the chapter is under-researched.

**Access constraints — read the trip entry.** Each `upcoming_trips` entry may carry an `access_constraints` block (e.g. `excluded_modes: ["car"]`, `allowed_modes: ["plane", "public_transport", "walking"]`, plus free-text notes). When present, **honour them strictly**: any attraction, restaurant, hotel, day-trip, or moment that effectively requires an excluded mode is removed from rankings and recommendations, not just flagged. Car-dependent options, where car is excluded, may appear *in passing* (one-line context — "there are also out-of-town outlets along the A65 that we'll skip") but never as picks. Conversely, walkability, station-distance, and bus/tram access become first-class facts in every Quick Stats sidebar, datum row, and Mood Board caption when public transport is the constraint. Field Guide picks and Countdown attractions/accommodation chapters all inherit this — the reader's mode of travel changes which chapters are worth writing.

**Research the whole estate, not the headline.** Many venues are larger than their marquee feature, and default searches will only surface the marquee. Beekse Bergen is a safari park *and* a Speelland adventure/water-play area (nearly the same size) *and* the Safari Resort hotel (with its own restaurants, pools, bowling, themed facilities) *and* Lake Beekse Bergen (beaches, water sports). Center Parcs is lodges *and* the Subtropical Swimming Paradise *and* the activity programme *and* the restaurant village. Disneyland Paris is two parks *and* Disney Village *and* the hotel estate. Before writing any chapter about a venue, map the full estate: read the official site's site-map / "what's on" / "things to do" pages in full, not just the first landing page. List every zone, every restaurant, every activity, every facility. Coverage must reflect what the venue actually *is*, not what its name suggests. A Beekse Bergen chapter that only covers "you can drive round the animals" is structurally wrong, regardless of word count. Rule of thumb: if you can summarise a venue's estate in one sentence, you haven't researched it yet.

**Imagery rule for travel Countdowns.** A reader preparing for a holiday wants to *see* the place, not just read its history. Travel Countdowns must show, not just tell. Apply on top of the standard tier-4 imagery budget:
- **Every chapter that describes a venue, room, ride, restaurant, animal experience, or pool** carries at least 2 images (hero + detail) and ideally a `.sp-gallery` or `.sp-image-strip` if more are available.
- **Across the whole issue, target 25–40 images** — most travel Countdowns will skew to the upper end. Hotels alone should contribute 8–12.
- **Caption every image** with a one-line `.sp-caption-strip` or `<figcaption>` saying what the reader is looking at, where it is, and the credit. “Exterior of the X hotel at dusk” beats no caption every time — the reader is orienting themselves.
- **Mix establishing shots with detail shots.** Don't show only wide exteriors; show the room, the breakfast spread, the kid feeding a giraffe from the window. Detail shots sell the place more than vistas do.
- **Sources, in order of preference, but cast a wide net.** Start with Wikimedia, official press kits, and credited Flickr — theme parks and resort groups (Efteling/Libema/Disney/Universal/Center Parcs/etc.) maintain extensive press image libraries that are free to use editorially with credit. **Then go beyond the official channels.** Well-shot traveller photography from travel blogs, Reddit photo threads (r/Efteling, r/themeparks, r/solotravel etc.), Flickr's wider pool, Instagram posts with clear credit, and forum trip reports are all in scope — they often capture detail (queue energy, food on a real plate, a room actually lived in) that press kits never will. The bar is quality and credit, not source pedigree: only use images that are sharp, well-composed, and large enough to render at the layout's native size; always credit the photographer/blog/handle + licence or permission basis. **Never AI-generated, never uncredited stock filler.**



---

## hype-chapter-visuals


> See `formats/countdown.md` for the full hype-chapter spec. This file is a cross-format summary.

**Hype-chapter visuals** are opt-in CSS modifiers (`32-hype-variants.css`) that dial back default special-edition chrome on chapters where excitement — not literary depth — is the job.

## When to use hype modifiers

Apply on:
- Countdown hype chapters: Top Attractions, Accommodation, Mood Board, Five Moments Worth the Trip, By the Numbers (when image-led)
- Field Guide: The Opening, The Unmissables

**Never apply on literary formats:** Deep Dive, Versus, Rewind, Season Review — these keep full default chrome.

## The four modifiers

1. **`.sp-chapter-gate.is-hype`** — compact gate: 60vh track (vs 110vh), 40vh hold (vs 100vh), layers solid by progress 0.08 (vs 0.20)
2. **`[data-sp-chapter].is-hype`** — re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, `.why-its-here`. All global lockdown elements unchanged.
3. **`.sp-ground-gallery`** — neutral slate ground (#1A1E27) for image-first chapters (Mood Board primary, optionally Field Guide Opening). NOT pitch black.
4. **`.unmissables` / `.unmissable`** — Field Guide Unmissables pattern: 6-10 full-width editorial beats, each = hero image + sensory prose + "Why It's Here" coral kicker + mono `<dl>` practical footer. Drop-cap forbidden on picks.

## Markup reminder

```html
<!-- Hype chapter gate -->
<div class="sp-chapter-gate is-hype" data-chapter-num="II" ...>...</div>

<!-- Hype chapter wrapper -->
<section data-sp-chapter data-chapter-num="2" data-chapter-title="Top Attractions"
         data-chapter-arc="The rides worth your day" class="is-hype">
```


---

## readability-locks


**CSS layer:** `34-readability-locks.css` (Tier 10, runs last in cascade).

Some self-painting components lose identity when nested inside `[data-sp-chapter]` because Tier 7's ground-discipline lockdown is over-aggressive. This layer re-locks each component to a fixed background+text pair regardless of the chapter ground above it.

| Component | Lock |
|---|---|
| `.sp-marginalia` | Always cream-bg + ink-text |
| `.sp-pull-break` | Always dark-bg + bone-text |
| `.sp-pullquote-huge` text | Set explicitly per chapter ground |

**Why this matters for writers:** if you use these components in the markup (which you should, per pre-flight.md), the CSS will handle contrast automatically. You do NOT need to add inline styles or ground overrides. Just use the canonical markup and the lock layer handles it.

**Markup contracts (Gate 1E):** the lockdown only works when markup matches the contract. See `global/04-markup-contracts.md` and `references/pre-flight.md` § Canonical markup snippets.


---

## portrait-spread


**CSS:** `26-special-editorial.css`. The three-column `.sp-spread` layout adapts at ≤980px.

## Portrait behaviour

At ≤ 980px, `.sp-spread` becomes `display: flow-root; position: relative`.

- **Rail** (`.sp-rail`): `position: absolute; top:0; bottom:0; left:0; width: 60/44px` — runs full spread height as decorative chapter-side chrome.
- **Margin aside** (`.sp-margin`): reparented via the portrait-spread-reparenter IIFE in `script.js` to be first child of `.sp-spread-body`; floats right (190/128px) with `shape-outside: margin-box`. Body is `flow-root` with left padding (78/58px) to clear the rail. Prose flows around the margin and reclaims full reading width once it ends.
- **Ink grounds**: the margin paints a solid paper-tinted background so ink-on-paper text stays legible.

## Markup contract

```html
<div class="sp-spread">
  <div class="sp-rail" aria-hidden="true"></div>
  <aside class="sp-margin">
    <!-- marginalia content -->
  </aside>
  <div class="sp-spread-body">
    <!-- prose, drop cap on first <p> -->
  </div>
</div>
```

**Never stack:** portrait is the canonical read. The three-column desktop layout is a bonus, not the target.


---

## holiday-identity

---

## Holiday Identity (v8.12 — Countdown and Field Guide only)

The Countdown and Field Guide formats use a **separate visual identity** from every other special edition. Where Deep Dive, Rewind, Versus, Season Review, Blueprint, Starter Kit, and Shortlist all share the default special-edition chrome (sticky chapter gate, paper/ink grounds, coral lockdown, restrained editorial register), Countdown and Field Guide do not. The default chrome reads as "serious magazine"; holiday issues need to read as "trip scrapbook, building excitement."

**CSS layer:** `36-holiday-identity.css` (Tier 11). Loads only when `body.is-special[data-special="countdown"]` or `body.is-special[data-special="field-guide"]` is set. On every other format the file is dormant.

**What the layer changes vs default chrome:**

1. **No sticky chapter gate.** The 110vh black chapter-gate scroll-track is hidden on holiday issues. Structural rhythm is instead carried by two **halves** and one **transit intermission** between them (`.hol-transit`). Multi-venue trips get the full two-half treatment; single-venue Field Guides run as one half with a softer interior break (a tilted `.hol-marquee` between sections, not a full transit).
2. **No coral accent lockdown.** The default chrome restricts coral to chapter-gate numeral, D-day badge, and progress bar. Holiday issues do not use coral at all. The issue's identity accent is **brass** (`--hol-brass` / `--hol-brass-light`); ruby, rose, emerald, mustard, terracotta all run freely throughout.
3. **No ground discipline.** The default chrome neutralises component-level grounds inside chapters. Holiday issues encourage per-block grounds — a rotated polaroid on a brass card on a celestial-themed section.
4. **Type personality swap.** Default chrome uses Space Grotesk for chapter titles. Holiday issues use six type stacks simultaneously: Bowlby One (display-chunk), Cinzel italic (serif-display), Yellowtail (script-ornate), Caveat (script-note), Anton (display-tall), Alfa Slab One (display-slab). DM Sans body and Space Mono kicker are shared with default chrome. Each face does a specific job — see Type roles below.
5. **Ambient layer swap.** Default chrome ambient: chapter beads, sticky pin, page-fold, horizon. Holiday ambient: drifting clouds in dark heroes, kinetic marquees as section transitions, savannah silhouettes along Half II's bottom edge, optional fairytale tree silhouettes on celestial halves, star field across Half I.

**Structural beats (in order):**

1. `.hol-masthead` — narrow brand strip with format badge and T-minus meta. Replaces default masthead for holiday issues.
2. `.hol-cover` — full-bleed indigo poster with star field, drifting clouds, mega-numeral watermark, chunky title with mixed type, optional `.hol-countdown` live grid on the left, optional scrapbook collage on the right.
3. `.hol-kicker-strip` — cream-paper promise of the issue with double rule, chunky title + script subtitle on the left, mono meta on the right.
4. `.hol-half--one` — Half I body (Efteling default register: indigo + celestial backdrop + brass/rose/cream accents). Contains: stacked opener, content blocks (anchor, unmissable rows, marquee, don't-miss, polaroids, postcards), and closes seamlessly into the transit.
5. `.hol-transit` — the **only** structural break in the issue. Full-bleed 280px black band with mega kinetic typography watermarking each side and the divider card pinned centre. Single-venue issues omit this and replace it with a softer in-half break (`.hol-marquee` between sections).
6. `.hol-half--two` — Half II body (Beekse Bergen default register: terracotta + savannah silhouettes + mustard/bone/burnt accents). Same content blocks, completely different palette.
7. `.hol-meanwhile` — closing dark block with mega "MEANWHILE" / "SIGNAL" / "T-MINUS" watermark, brass title in chunky display, italic serif body. Adjacent rotated `.hol-subscribe` card.
8. `.hol-footer-row` — brand mark + mono links + hand-script tagline. Closes the issue.

**Type roles:**

| Face | Role | Examples |
|---|---|---|
| Bowlby One (`--hol-t-chunk`) | Mega display titles, big numbers, marquee text | Cover title, half titles in Half II, marquee bars, mega watermarks |
| Cinzel italic (`--hol-t-serif`) | Half I serif titles, italic pull-quotes, dek text | Half I opener title, anchor titles, unmissable titles |
| Yellowtail (`--hol-t-script`) | "Part One:" / "Don't Miss" / overline tags, hand-arrow notes | Cover overline, opener tags, transit hand-script, don't-miss kicker |
| Caveat (`--hol-t-hand`) | Polaroid captions, postcard backs, tagline endings, sticker text | Every handwritten caption in the issue |
| Anton (`--hol-t-tall`) | Tall display, transit names, postcard place labels, chalkboard items | "EFTELING" / "SAFARI" mega-watermark in transit |
| Alfa Slab One (`--hol-t-slab`) | Stamp inner text, big slab numerals where chunky is too round | Inside `.hol-stamp` b text |
| DM Sans (`--hol-t-body`) | All body copy | Same as default |
| Space Mono (`--hol-t-mono`) | Kickers, meta, ALL CAPS labels, stamps outer ring text | Mast meta, kicker-strip meta, stamp text, unmissable facts dt |

**Component vocabulary (full list, all prefixed `.hol-`):**

| Class | Role |
|---|---|
| `.hol-masthead` (`__title`, `__badge`, `__meta`) | Page-top brand strip |
| `.hol-cover` (`__inner`, `__sig`, `__overline`, `__title`, `__dek`, `__layout`, `__collage`, `__cloud`, `__back-num`, `__back-script`) | Full-bleed cover poster |
| `.hol-countdown` (`__grid`, `__cell`, `__num`, `__unit`, `__target`) | Live countdown digit grid. JS controller binds to `[data-cd]` cells; wrapper carries `data-target` ISO string |
| `.hol-kicker-strip` (`__inner`, `__title`, `__sub`, `__meta`) | Promise strip between cover and Half I |
| `.hol-half` + `.hol-half--one` / `--two` (`__inner`, `__opener`, `__opener-tag`, `__opener-title`, `__opener-subtitle`, `__opener-pills`) | Half section wrapper + stacked opener |
| `.hol-half--fairytale` | Optional ambient variant — Anton-Pieck tree silhouettes along the bottom of Half I |
| `.hol-transit` (`__side`, `__side--left`, `__side--right`, `__mega-bg`, `__label`, `__hand`, `__name`, `__center`, `__center-card`) | The single structural break between halves |
| `.hol-polaroid` (`__photo`, `__caption`, `__tape`) + `--right` / `--flat` | Rotated photo card with washi tape |
| `.hol-postcard` (`__front`, `__back`, `__greeting`, `__place`) | Greeting front + handwritten lined back |
| `.hol-stamp` + `--brass` / `--emerald` / `--mustard` | Circular rubber-stamp seal |
| `.hol-anchor` (`__photo`, `__title`, `__dek`, `__meta`, `__badge`, `__note`) | Feature article block with tilted border, rotated badge, hand-script note |
| `.hol-unmissable` + `--reverse` (`__photo-wrap`, `__photo`, `__card`, `__num-row`, `__num`, `__title`, `__quote`, `__why`, `__facts`) | Alternating left/right photo + parchment row. Use 6–10 per Field Guide; 5–7 per Countdown Top Attractions |
| `.hol-dont-miss` (`__kicker`, `__title`, `__list`) | Rotated ruby block with tilted shadow numerals |
| `.hol-marquee` (`__track`) | Kinetic horizontal scroll banner. Reduced-motion safe |
| `.hol-chalkboard` (`__tag`, `__title`, `__items`, `__row`, `__item`, `__price`, `__note`) | Half II tilted chalkboard menu card |
| `.hol-meanwhile` (`__giant-bg`, `__inner`, `__title`, `__body`) | Closing dark block |
| `.hol-subscribe` (`__inner`, `__title`, `__form`, `__input`, `__btn`, `__hand`) | Rotated subscribe card |
| `.hol-footer-row` (`__brand`, `__links`, `__tagline`) | Page-bottom brand mark + links + tagline |

**Activation:**
```html
<!-- Countdown -->
<body class="is-special" data-special="countdown">

<!-- Field Guide -->
<body class="is-special" data-special="field-guide">
```

No additional class is needed on the body. The default chrome's `body.is-special` activation still fires; tier 36's selectors disable the parts of default chrome that conflict and install the holiday vocabulary on top.

**Single-venue vs multi-venue:**
- **Multi-venue trip:** use both `.hol-half--one` and `.hol-half--two`, separated by one `.hol-transit`. The transit is the entire chapter-rhythm system for the issue. Half I covers the first venue; Half II covers the second.
- **Single-venue trip:** use only `.hol-half--one`. Replace the transit with one or two interior `.hol-marquee` breaks placed between major content groups (e.g. after Top Attractions, after Mood Board). The marquee functions as the softer in-half rhythm beat.

**What does NOT change vs the existing Countdown / Field Guide editorial specs:**

The editorial rules for Countdown and Field Guide (canonical chapter order, no-taste rule, hype-over-homework, 45/55 hype-to-practical, reader-profile invisibility, source diversity, image source rules, multi-venue balance check, access constraints, locked release-date register) all remain in force exactly as written. This layer is purely visual identity — content rules are unchanged.

**Compatibility with multi-venue theming (Tier 9, `33-countdown-destinations.css`):**

Tier 9 multi-venue theming and tier 11 holiday identity are independent. If a Countdown uses both:
- Tier 9 provides per-venue palette tokens (Efteling cream + plum + antique gold; Beekse warm sand + dark earth + terracotta) and the decorative venue glyph in the bottom-right corner.
- Tier 11 provides the cover, transit, half opener, ephemera vocabulary, and the type system.

The two layers compose cleanly: tier 9's venue palette can be used for the half ground, tier 11's component vocabulary for everything inside it. If a conflict arises (e.g. tier 9 sets a paper ground but tier 11 wants the indigo half-one register), the holiday half-register wins because tier 11 loads later in the cascade.

**Reduced-motion safety:**

Every animation in tier 36 (drift, marquee, flip-pop, hover-unrotate) is gated behind a `prefers-reduced-motion: reduce` override at the bottom of the file. Reduced-motion users see the same layouts with no motion.

---

### v8.13 — visual richness upgrade (May 2026)

v8.13 replaces three weak spots in the original Holiday Identity layer with the proven recipes from `signal-holiday.css`. Every change is **additive** unless explicitly noted — the v8.12 vocabulary continues to work, and existing planners that emit the old class names still produce valid output. The new components are opt-in extensions plus one breaking change to `.hol-half--two`'s ambient layer.

**1. Half II is now savannah cartography, not flat orange (BREAKING for `.hol-half--two`).**

The original `.hol-half--two` painted a flat terracotta ground with a mustard radial-dot grid and a small SVG silhouette band at the bottom. v8.13 replaces all three:

- **Ground:** gradient from `--hol-sand` (#ede1c8) at the top through `--hol-bone` (#f5ecd6) to a khaki dust tone at the bottom. Body text colour becomes `--hol-savannah-ink` (#1c2613) for legibility on the now-lighter ground.
- **Sun layer (`::before`):** conic sun-rays from the upper-right (`92% 8%`) plus a radial brass-orange sun disc. Reads as the savannah morning sun.
- **Silhouette band (`::after`):** the proven SVG band from `signal-holiday.css` — three giraffes at varying heights, three acacia trees, an elephant in mid-section, two grass tufts, and small bird scribbles. Tiled across the bottom 240px.

All Half II component overrides (anchor, opener, etc.) are repainted to work on the new light ground: bone-on-terracotta becomes savannah-ink-on-cream-sand, with burnt as the primary accent and mustard as the secondary. Writers and planners should **never** set `background:` on the `.hol-half--two` wrapper or on a chapter inside it.

**2. Optional atmospheric theme layers.**

Five new utility classes, each a single CSS pseudo-element with a tiled SVG. Stack ON TOP of a half (or any positioned section) for extra atmosphere on selected chapters. Each is static and repeating — paint cost is amortised by the browser image cache; identical across one page or thirty of scroll.

| Class | When to use | What it adds |
|---|---|---|
| `.theme-celestial` | Feature Half I chapters (the Top Wonders chapter, the Anchor chapter) | Richer starfield with constellation lines connecting stars + four-point sparkle stars |
| `.theme-fairytale` | Half I storybook chapters | Anton-Pieck silhouette band of gnarled trees along the bottom 220px with brass lantern dots |
| `.theme-flourish` | Half I chapter openers | Anton-Pieck brass filigree corner brackets (top-left + mirrored top-right) |
| `.theme-airships` | Half I Wonder Hotel / accommodation chapters | Line-drawn hot-air balloons drifting across the section |
| `.theme-tracks` | Half II safari chapters | Low-opacity terracotta paw/hoof print watermark across the section |
| `.theme-heat-haze` | Half II — ONE chapter per issue maximum | Subtle blurred shimmer ribbon at 32% height, 4s ease-in-out infinite alternate. The single moment of animation in Half II. |

Legacy alias: `.hol-half--fairytale` continues to work and produces the same tree-silhouette band. New writers should prefer `.theme-fairytale` (more composable).

**3. `.hol-wonders` editorial pattern (NEW component).**

A chapter-level component for ranked editorial picks (Field Guide Unmissables, Countdown Top Attractions). Each row is a rotated hero image with thick white border paired beside a parchment card carrying a numbered chip, serif italic pull-quote lede, and a tight Where/Why meta strip. Rows alternate sides via `.hol-wonder--reverse`. The component is designed to sit ON TOP of the indigo + starfield + storybook ground of `.hol-half--one` — the dark backdrop reads through between rows, making the parchment cards feel like illustrated plates pasted onto the night sky. The hover-unrotate on the photo is the only motion.

This sits alongside `.hol-unmissable` rather than replacing it. The two patterns serve different shapes: `.hol-unmissable` is the magazine-feature row with a long card, full quote attribution, and a four-row practical footer; `.hol-wonders` is the tighter editorial-list row with the numbered chip and a two-row Where/Why meta. Use `.hol-wonders` when the chapter is **ranked culinary or attraction wonders**; use `.hol-unmissable` when the chapter is the full Field Guide Unmissables pattern.

```html
<section class="hol-half hol-half--one theme-celestial theme-fairytale">
  <div class="hol-half__inner">
    <div class="hol-wonders">
      <div class="hol-wonders__intro">
        <h2>Top Ten Culinary Wonders</h2>
        <p>The unmissable flavours of Efteling</p>
      </div>
      <div class="hol-wonder">
        <div class="hol-wonder__photo" style="background-image:url('...');"></div>
        <div class="hol-wonder__card">
          <div class="hol-wonder__head">
            <span class="hol-wonder__num">01</span>
            <h3 class="hol-wonder__title">Pancakes at Polles Keuken</h3>
          </div>
          <p class="hol-wonder__quote">"Twelve little ones, butter, sugar — worth the queue every time." — r/Efteling</p>
          <dl class="hol-wonder__meta">
            <dt>Where</dt><dd>Polles Keuken, Fairytale Forest</dd>
            <dt>Why</dt><dd>Source convergence across Reddit, blogs, and TripAdvisor on the pancakes specifically.</dd>
          </dl>
        </div>
      </div>
      <div class="hol-wonder hol-wonder--reverse">...</div>
      <!-- alternate sides for every subsequent row -->
    </div>
  </div>
</section>
```

**4. Cover poster variant (NEW component).**

A 70s travel-brochure cover for Countdown and Field Guide issues. Activate by adding `.hol-cover--poster` to the existing `.hol-cover` element. The base `.hol-cover` treatment (cloud-drift indigo poster with collage on the right) is preserved for issues that want the scrapbook-collage feel; the poster variant replaces it with a silkscreen-print SVG illustration plate plus a centred title stack.

The illustration plate is a static SVG: midnight sky gradient, sunburst rays from the upper-right, big moon-with-face character, scattered round stars, four-point sparkle stars, distant ridge silhouette, offset-overprint castle silhouette in rose ghost + cream front with brass lit windows, floating clouds, water reflection, and shoreline trees. The plate is identical across Countdown and Field Guide — it reads as the fairytale night sky on both.

On top of the plate sit, in order:
- `.hol-cover__sig` — the meta strip (brand + issue + kicker)
- `.hol-cover__arch` — SVG text-on-path arc (e.g. "★ GREETINGS FROM ★" for Countdown, "★ EAT YOUR WAY THROUGH ★" for Field Guide)
- `.hol-cover__title` with a `.hol-cover__title--print` inner span — chunky Bowlby One with a hard offset shadow in `--hol-ruby` that reads as misregistered screen-print
- `.hol-cover__sub` — Yellowtail subtitle, slightly tilted
- `.hol-cover__deck` — three-pill mono row with star dividers (date · gates · family-of-four, etc.)
- `.hol-countdown` — the existing live digit grid, pinned at the bottom of the stack

Template part: `assets/template-parts/03-cover-poster.html`. The full SVG plate plus the stack scaffold is embedded — writers paste it verbatim and fill the bracketed placeholders.

**5. Letterpress titles on Half II.**

The Half II opener title now uses `text-shadow: 6px 6px 0 var(--hol-burnt)` for a letterpress / poster-print feel instead of the original drop-shadow. This is a single-line change but it lands every chapter title in the savannah half as a hand-printed poster.

**Pre-flight regressions added in v8.13:**
- **RT-14:** Flat-fill ground on Half II is banned. Let `.hol-half--two` paint its own ground; don't set `background:` on the wrapper or on inner sections.
- **RT-15:** Venue/half mismatch is banned. Every Efteling chapter sits in `.hol-half--one`; every Beekse Bergen chapter sits in `.hol-half--two`. Cross-venue chapters live outside both halves (after the cover, or as the transit body).


