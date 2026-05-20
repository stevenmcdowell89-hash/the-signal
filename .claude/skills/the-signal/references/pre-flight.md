# Pre-Flight — Writer Subagent Checklist

**Every writer subagent MUST read this file before drafting. Researcher and planner read it too.**

---

## 1. Purpose

This file catches the ~12 regression patterns that have appeared in past issues. Read it once, check your chapter against it, and your chapter passes Gate 1 without rework. It is not a summary of the full editorial spec — it is a targeted hit list of the most common failures.

**If you need more detail:** editorial-spec.md (full spec) → compliance-checklist.md (gate greps) → references/spec/global/ (sliced rules by topic).

---

## 2. Twelve Regression Triggers

Each trigger: what it looks like, why it's banned, what to do instead.

---

### RT-1: Reader-Profile Leaks

**What it looks like:**
- "your son will love this"
- "perfect for your 10-year-old"
- "you and your partner"
- "your tablet", "your watch"
- "you'll appreciate this because you follow Malazan"
- "since you're into Juventus"
- "as a kettlebell fan"
- "spoiler-free" / "no spoilers in sight" (announces a rule that must be invisible)
- "It's not bland meal prep food" (defensive justification pattern)

**Why banned:** The reader profile drives research and selection — it must be invisible in the prose. The Signal has 100,000 imaginary readers. If a sentence would only make sense written for one person, it fails.

**Instead:** State facts as venue character or general editorial voice:
- "family-friendly" not "great for your son"
- "adult-oriented evening spot" not "you and your partner will love"
- "For anyone watching the Serie A title race" not "since you follow Serie A"
- Simply cover the topic — never justify why you selected it.

---

### RT-2: No-Taste Rule (Invented Sensory Prose)

**What it looks like:**
- "the first bite reveals…"
- "it smells of cinnamon and…"
- "warm and buttery", "crisp at the edges"
- "melt-in-the-mouth", "moreish", "divine"
- "the room feels intimate"
- "cooks in striped aprons" (invented atmosphere)
- "rich and comforting"

**Why banned:** The agent has not tasted, smelled, or visited anything. Invented sensory prose is fabrication. It reads as marketing copy, not editorial.

**Instead:** If a sensory detail is needed, quote a credited source. The photo carries the visual sensory load. Describe factually: "A harissa-style chicken dish with chickpeas and rice" — not "a warming, aromatic bowl that fills the kitchen with scent."

---

### RT-3: Coral Accent Lockdown Violation

**What it looks like:**
- A pull-quote with coral text or border
- A brief sidebar with coral kicker
- A dashboard (`sp-dash`) with coral `strong` elements
- An eyebrow label in coral
- A spread `h2` with coral marker
- Any use of `color: var(--sp-accent-primary)` or `color: #E8384F` outside the allowed list

**Why banned (v8.4 hard rule):** Coral is reserved for three things ONLY: (1) the Roman numeral inside `.sp-chapter-gate`, (2) the Countdown D-day badge, (3) the page progress bar. When coral appears elsewhere, it loses all meaning as a chapter-break signal.

**Allowed exceptions (hype chapters only):** `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, `.why-its-here` — but ONLY on `[data-sp-chapter].is-hype` chapters, and NEVER on literary formats (Deep Dive, Versus, Rewind, Season Review).

**Instead:** Everywhere coral was previously used, the CSS automatically uses `--sp-accent-secondary` (muted slate on paper, bone on ink). You don't need to set it — just don't override with coral.

---

### RT-4: No-Price-Research Rule (Versus Holiday Subtype)

**What it looks like:**
- Invented price comparisons: "Venue A costs €X per night vs Venue B at €Y"
- Round verdicts on value based on estimated or assumed prices
- "roughly" / "approximately" pricing without citation

**Why banned:** The Versus holiday/destination subtype requires a like-for-like value round with sourced prices. Invented prices produce a false verdict. If exact prices are unavailable, say so explicitly and give proportional gap with citations.

**Instead:** Source real prices for identical parameters (same dates, party size, accommodation tier). Where exact prices are unavailable: "Venue A runs significantly higher for equivalent stays — forum reports from March 2026 suggest a gap of 30–40% for comparable park-access packages (r/Efteling)."

---

### RT-5: Image Source Diversity Violation

**What it looks like:**
- 9 of 14 images sourced from `commons.wikimedia.org` (the 17 May 2026 test issue, pre-rebalance)
- 8 of 10 images sourced from `upload.wikimedia.org`
- All hotel images from the official hotel website
- All park images from one press kit domain

**Why banned (every format):** Over-reliance on a single domain signals shallow research. A magazine where most images come from one easy host couldn't be bothered to look further. Gate 3 hard-fails any issue where a single domain exceeds 50% of attributed images. Wikimedia is specifically capped at 4 entries or 30% of images, whichever is smaller — it is the *last-resort supplement*, not the default (see `references/spec/global.md` image-integrity).

**Instead:** Pull from the five source-type menu in `references/spec/global.md` image-integrity — press kits / brand CDNs, government Flickr + media libraries, museum/archive direct hosts, news-agency CDNs (when editorial-use cleared), and Wikimedia. Every issue must draw from at least three of those five. For any venue or topic, confirm you can name at least 3 independent image domains across the issue before publish.

---

### RT-6: Fabricated Stats / Podcast / Article Content

**What it looks like:**
- "Drew 7-0" — a scoreline you didn't verify
- "In episode 412 of Football Weekly, they discussed…" — invented episode content
- "A 2024 study found that…" — a study you can't link to
- "According to [article title]…" — article you invented

**Why banned:** Fabrication is a hard fail. It's indistinguishable from real facts to the reader and permanently damages trust.

**Instead:** If you can't verify it, don't include it. For podcasts: link without a summary, or omit. For stats: if unconfirmed, say "unconfirmed reports" or omit. Every scoreline must be verified. Every linked article must exist.

---

### RT-7: Banned Alternate Markup

**What it looks like (all are banned):**

```html
<!-- BANNED pullquote -->
<div class="sp-pullquote-huge">...</div>
<p class="sp-pq-quote">...</p>
<p class="sp-pq-attrib">...</p>

<!-- BANNED marginalia -->
<div class="sp-marginalia">...</div>
<p class="sp-marg-kicker">...</p>
<p class="sp-marg-label">...</p>

<!-- BANNED pull-break -->
<blockquote class="sp-pull-break">...</blockquote>
<h2 class="sp-pull">...</h2>

<!-- BANNED brief sidebar -->
<aside class="sp-brief">...</aside>
<h3 class="sp-brief-h">...</h3>

<!-- BANNED hero quote -->
<blockquote class="sp-hero-quote">...</blockquote>

<!-- BANNED chapter chrome -->
<header class="sp-chapter-chrome">...</header>
<!-- (also: missing .sp-hair inside chapter chrome) -->
```

**Why banned:** The CSS targets specific tag + class combinations. Wrong tags bypass the readability locks and produce contrast bugs — bone-on-cream cards, ink-on-dark bands. This has been the single largest source of v8.x regressions.

**Instead:** Use only the canonical markup in § 3 below.

---

### RT-8: Missing Chapter-Gate Data Attributes

**What it looks like:**
```html
<!-- MISSING required attributes -->
<aside class="sp-chapter-gate">...</aside>
<section data-sp-chapter>...</section>
```

**Why banned:** The chapter gate JS driver reads `data-chapter-num`, `data-chapter-title`, and `data-chapter-arc` to build the sticky scroll panel. Missing any of them produces a blank black viewport on scroll.

**Instead:** Every chapter gate and chapter wrapper must carry the full attribute set:
```html
<aside class="sp-chapter-gate" data-chapter-num="II"
      data-chapter-title="Top Attractions"
      data-chapter-arc="The rides worth your day">
  <div class="scg-arc">Visual Highlights</div>
  <div class="scg-numeral">II</div>
  <div class="scg-title">Top Attractions</div>
  <div class="scg-deck">The rides worth your day</div>
</aside>
<section data-sp-chapter data-chapter-num="2"
         data-chapter-title="Top Attractions"
         data-chapter-arc="The rides worth your day"
         class="sp-ground-paper">
```

---

### RT-9: Drop-Cap on Hype Picks (Forbidden)

**What it looks like:**
- A drop-cap (large first letter) on the first paragraph of a pick inside `.unmissables`
- `::first-letter` styling on any `.unmissable` prose block

**Why banned:** Drop-caps are for literary spreads only — the first letter of body text inside `.sp-spread-body > p:first-of-type`. They are CSS-automated there. On hype picks they look like a formatting bug and break the visual rhythm.

**Instead:** Hype pick prose opens normally. Let the hero image + `.why-its-here` kicker do the visual work.

---

### RT-10: Broken Pull-Break Wrap

**What it looks like:**
```html
<!-- BROKEN: pull-break outside its wrapper -->
<section data-sp-chapter ...>
  <div class="sp-spread">...</div>
  <div class="sp-pull-break">...</div>  <!-- WRONG -->
</section>
```

**Why banned:** `.sp-pull-break` must be nested inside `.sp-pull-break-wrap`. The wrapper is what provides the full-bleed dark background. A bare `.sp-pull-break` renders without the backdrop, producing floating text on the chapter ground.

**Instead:**
```html
<div class="sp-pull-break-wrap sp-ground-deep">
  <div class="sp-pull-break">
    <p class="sp-pull">The quote text here</p>
    <p class="sp-pull-attrib">— Attribution</p>
  </div>
</div>
```

---

### RT-11: Marginalia Outside `.sp-spread`

**What it looks like:**
```html
<!-- WRONG: marginalia outside the spread -->
<section data-sp-chapter ...>
  <aside class="sp-marginalia">...</aside>
  <p>Prose continues...</p>
</section>
```

**Why banned:** Marginalia (`<aside class="sp-marginalia">`) is only legal inside the three-column spread (`.sp-spread`). The CSS uses a descendant selector that only fires within the spread context. Outside it, the component has no layout anchor and collapses unpredictably.

**Instead:** Either place the marginalia inside a `.sp-spread > .sp-margin` element, or use a `.sp-brief` sidebar instead.

---

### RT-12: Hype Modifiers on Literary Formats

**What it looks like:**
- `class="sp-chapter-gate is-hype"` on a Deep Dive chapter
- `[data-sp-chapter].is-hype` on a Versus chapter
- `.sp-ground-gallery` used in a Rewind or Season Review

**Why banned:** Hype modifiers (`.is-hype`, `.sp-ground-gallery`, `.unmissables`) exist specifically for Countdown and Field Guide. Literary formats (Deep Dive, Versus, Rewind, Season Review) rely on the full default chrome — the extended chapter gate, the full coral lockdown, the paper/ink rhythm — for their voice. Hype chrome on a literary chapter breaks the tonal contract.

**Instead:** Reserve all hype modifiers strictly for:
- Countdown: Top Attractions, Accommodation, Mood Board, Five Moments, By the Numbers (image-led)
- Field Guide: The Opening, The Unmissables

---

### RT-13: Holiday Identity — wrong markup vocabulary (v8.12)

**Applies only to:** `data-special="countdown"` and `data-special="field-guide"` issues. On every other format, ignore this trigger entirely.

**What it looks like:**
- A Countdown or Field Guide issue using `.sp-chapter-gate`, `.sp-spread`, `.sp-pull-break`, `.sp-marginalia`, `.sp-brief`, `.sp-dash`, or `.sp-chapter-chrome`
- A Countdown or Field Guide issue without any `.hol-*` components
- A Countdown or Field Guide issue with `.unmissables` / `.unmissable` (default chrome) instead of `.hol-unmissable`
- A Countdown or Field Guide issue using paper/ink grounds (`.sp-ground-paper`, `.sp-ground-ink`) on the body or on chapter wrappers

**Why banned:** v8.12 introduced a separate visual identity for Countdown and Field Guide (tier 36, `36-holiday-identity.css`). The two formats no longer use the default chapter-gate / spread / paper-ink-ground / coral-lockdown system. Instead they use the holiday vocabulary: `.hol-cover`, `.hol-half`, `.hol-transit`, `.hol-anchor`, `.hol-unmissable`, `.hol-polaroid`, `.hol-postcard`, `.hol-stamp`, `.hol-marquee`, `.hol-dont-miss`, `.hol-chalkboard`, `.hol-meanwhile`, `.hol-subscribe`. Default chrome markup is **hidden** on these issues by tier 36 — a chapter built with default markup would render as a blank stretch.

**Instead:** Use the holiday vocabulary throughout. See `references/spec/specials.md` § holiday-identity for the full component map and `§ 3. Canonical Markup Snippets` below for the snippets. Key swaps:

| If you'd reach for… | Use instead (holiday issue) |
|---|---|
| `.sp-chapter-gate` | nothing — holiday issues have no chapter gates |
| `.sp-spread` body | `.hol-half__inner` plus content components |
| `.sp-pull-break` | `.hol-marquee` or `.hol-dont-miss` |
| `.sp-marginalia` | `.hol-stamp` or `.hol-polaroid` |
| `.sp-brief` | `.hol-anchor` (for a feature) or `.hol-postcard` (for a small aside) |
| `.sp-dash` | `.hol-countdown` (live grid) or inline big numbers within `.hol-anchor__meta` |
| `.unmissables` / `.unmissable` | `.hol-unmissable` (alternating left/right rotated photo + parchment card) |
| `.sp-ground-paper` | nothing on the wrapper; cream grounds happen inside specific components |
| `.sp-ground-ink` | nothing on the wrapper; indigo is Half I's default ground |
| `.sp-ground-gallery` | not legal on holiday issues |

**Halves and the transit:** every multi-venue holiday issue uses exactly TWO halves (`.hol-half--one`, `.hol-half--two`) separated by exactly ONE `.hol-transit`. Single-venue issues use ONE `.hol-half--one` with one or two `.hol-marquee` interior breaks. Adding extra transits, omitting the transit on a multi-venue issue, or stacking halves of the same type is a hard fail.

### RT-14: Flat-fill ground on Half II (v8.13)

**Applies only to:** `data-special="countdown"` and `data-special="field-guide"` issues with a `.hol-half--two`. On every other format, ignore.

**What it looks like:**
- A `.hol-half--two` whose inner content sets `background: var(--hol-terracotta)` (or any flat orange / terracotta) on the wrapper or on a chapter inside it.
- A `.hol-half--two` with no savannah ambient layer — the section reads as a flat solid block rather than a savannah landscape.
- Decorative dots, circles, or random lines used as the only ambient layer on a Beekse Bergen / Half II chapter (the giraffe + acacia + elephant SVG band is the canonical recipe; abstract dot grids are not).

**Why banned:** v8.13 replaced the original flat-terracotta-with-mustard-dots Half II ground with a layered savannah recipe (gradient sand-to-khaki sky, conic sun rays from the upper-right, SVG silhouettes of giraffes, acacia trees and an elephant along the bottom). Flat orange fills, abstract dot grids, and random-line ambient layers don't evoke safari — they evoke a generic warning panel. The Half II identity is **savannah cartography**, not coloured rectangle.

**Instead:**
- Let `.hol-half--two` paint its own ground. Do NOT set `background:` on the wrapper or on inner sections.
- For one or two chapters add an optional theme class on TOP of the half ground: `.theme-tracks` (paw-print watermark), `.theme-heat-haze` (subtle shimmer ribbon — use ONCE per issue maximum). Both stack cleanly above the existing sun-rays + silhouette layers.
- For Wonder Hotel and accommodation chapters in Half I, use `.theme-airships` to layer line-drawn hot-air balloons over the indigo ground.
- For storybook feature chapters in Half I, use `.theme-celestial` (richer star-and-constellation field) and/or `.theme-fairytale` (Anton-Pieck tree silhouettes along the bottom).

**Grep recipe:**
```bash
# RT-14: No flat terracotta or orange background-color inline
grep -oE 'background[^;]*(:|=)[^;]*(c25a2e|terracotta|orange|d97706|f97316)' chapter.html
# expect: empty inside .hol-half--two
```

### RT-15: Venue / half mismatch (v8.13)

**Applies only to:** multi-venue Countdown and Field Guide issues. On single-venue issues, ignore.

**What it looks like:**
- A chapter sitting inside `.hol-half--one` whose subject is Beekse Bergen (safari resort, Tamani, the safari bus, the lakes, Karibu Town, etc.).
- A chapter sitting inside `.hol-half--two` whose subject is Efteling (Polles Keuken, Wonder Hotel, Symbolica, Aquanura, Het Witte Paard, etc.).
- A chapter inside Half II using indigo/cream Efteling palette colour overrides, or vice versa.

**Why banned:** the half is the venue. Half I IS Efteling — indigo storybook night sky. Half II IS Beekse Bergen — savannah cartography on cream sand. A chapter on the wrong side of the transit reads to the reader as either a misnamed chapter or a broken issue. The transit intermission is the named structural commitment to the venue change; subverting it confuses the entire navigation logic.

**Instead:** every chapter sits inside the half whose venue it covers. If a chapter is genuinely cross-venue (e.g. a Quick Orientation map showing both venues, or a transit / between-the-parks logistics chapter), it lives OUTSIDE both halves — either after the cover and before Half I, or as the body of the transit intermission card. Never inside the wrong half.

**Grep recipe:**
```bash
# RT-15: Beekse Bergen names in Half I, or Efteling names in Half II
# Run after a stitched build. The script extracts each .hol-half block
# and checks for venue-name leakage.
# Quick manual check:
awk '/class="hol-half hol-half--one/,/<\/section>/' issue.html | grep -iE 'beekse|safari resort|karibu|tamani|safari bus'
# expect: empty
awk '/class="hol-half hol-half--two/,/<\/section>/' issue.html | grep -iE 'efteling|kaatsheuvel|polles|wonder hotel|symbolica|aquanura|witte paard'
# expect: empty
```

---

### RT-16: Fabricated image URL (v8.13.4)

**The trap.** Writer subagents construct plausible-looking `src=` URLs by pattern-matching against domains seen in research (`upload.wikimedia.org/wikipedia/commons/X/XY/Name.jpg`, `press.bethesda.net/game/...`, `lumiere-a.akamaihd.net/v1/images/...`). The Wikimedia path requires the actual MD5 hash prefix of the filename; the press-kit URLs are pages not assets; the Lumiere file slugs differ per asset. Guessing produces a 404 that the pipeline does not currently detect — the issue ships with broken-image icons.

**Confirmed prior fabrications (the 17 May 2026 test issue):**
- `upload.wikimedia.org/.../0/08/Pálinkás_Ferenc_Stadion_2.jpg` — "Pálinkás" is Hungarian fruit brandy; the stadium is Puskás
- `press.bethesda.net/game/indiana-jones-and-the-great-circle` — page slug, not image asset
- `www.starwars.com/press-assets/the-mandalorian-and-grogu/key-art` — invented URL pattern
- `photojournal.jpl.nasa.gov/jpeg/PIA26178.jpg` — guessed PIA number
- `upload.wikimedia.org/.../9/94/Cloudflare_Logo.png` — guessed hash prefix
- 9 more in the same issue

**The rule.**

1. **Writers MUST NOT construct image URLs.** Every `src=` value must come verbatim from `research-bundle.json` → `image_candidates[i].url_or_keyword`. If that field is a keyword rather than a URL (legacy bundles), OMIT the `<img>` tag entirely and let the caption stand alone — never guess.

2. **Researchers MUST provide URLs from at least 3 of the 5 source types in `references/spec/global.md` image-integrity.** Pull from press kits / brand CDNs, government Flickr + media libraries, museum / archive direct hosts, news-agency CDNs, and Wikimedia. Cap Wikimedia at 4 entries or 30% of the issue's image budget (whichever is smaller) — it is the supplement of last resort, not the default. RT-5 hard-fails any issue where one domain exceeds 50%.

3. **When using Wikimedia as a supplement**, format every URL as `https://commons.wikimedia.org/wiki/Special:FilePath/Exact_File_Name.jpg?width=N` — the redirect resolves any verified file by canonical name. Never construct an `upload.wikimedia.org/wikipedia/commons/X/XY/...` URL manually; the hash prefix is computed from the filename and guessing it gets it wrong.

4. **Phase 3b (`validate-research-bundle.py`) blocks the planner if the bundle contains keywords-not-URLs, fails diversity, or breaches the Wikimedia cap.** Phase 7.6 (`validate-issue.py`) probes every `<img src>` for HTTP reachability post-stitch. Phase 7.7 (`check-image-diversity.sh`) re-checks domain ratios post-stitch as defence in depth. All three are non-skippable gates under the orchestrator's gate-discipline rule (see SKILL.md). The JS onerror fallback in `script.js` is the runtime safety net for the rare case where a verified URL goes offline between publish and viewing.

**Self-audit grep:**
```bash
# Reject any src= that doesn't appear in research-bundle.json
python3 -c "
import json, re
bundle = json.load(open('/tmp/signal-build/research-bundle.json'))
allowed = set()
for c in bundle.get('image_candidates', []):
    u = c.get('url_or_keyword', '')
    if u.startswith('http'):
        allowed.add(u)
html = open('chapters/MY-CHAPTER.html').read()
for src in re.findall(r'<img[^>]+src=\"([^\"]+)\"', html):
    if src not in allowed:
        print(f'FABRICATED: {src}')
"
# expect: empty
```

---

### RT-17: Holiday-issue visual regressions (v8.14)

Three failure modes that emerged during the May 2026 multi-venue Field Guide rebuild. All apply equally to Countdown — both formats render under the Holiday Identity layer.

**The traps.**

1. **Stock-photo dominance.** Brand press kits (especially hotel/resort CDNs) over-index on "smiling family at table", "barman pouring for a delighted guest", "child eating cake", "couple toasting on a terrace". These shots are designed to sell an accommodation product, not to document the food, the room, or the venue's character. When the researcher uncritically harvests every press-kit URL, the issue reads as a sponsored deck.

2. **Sub-50% domain compliance + same-context duplication.** A bundle can satisfy RT-5 (no single domain >50%) and still ship with the SAME image used as the hero of an Unmissable AND as the header of the matching meal-slot. The validator allows this; the reader notices.

3. **Front-loaded visual moments.** Decorative anchors — Trip-in-Numbers, T-MINUS banners, hype marquees, big pull-quotes, drop-caps — all sprinkled into the first chapter and forgotten thereafter. The opening reads strong; the back of the issue reads as a wall of paragraphs.

**Confirmed regressions in the 17 May 2026 rebuild:**
- BB Unmissables initially shipped with `gezin-bowlen-pamoja-lounge` (family-bowling press shot) as the Pamoja hero, `barman-cocktails-vrouw-hogon-house` (barman + customer) as the Hogon hero, and `saladebar-diner-amma` (diners at the salad bar) as the Amma atmospheric. Reader rejected all three as stock-coded.
- Same rebuild then shipped Trip-in-Numbers + T-MINUS banner + pulsing countdown all in the first third; the middle and back of the issue had no decorative anchors. Reader caught the clustering on inspection.
- Brasserie 7 (Efteling Grand Hotel) was used as cover-collage polaroid AND breakfast-slot header AND dinner-slot header — three uses of two near-identical images, each visually prominent.

**The rules.**

1. **Subject hierarchy for image candidates (researcher + writer).** Preferred subject order, in priority:
   - Food close-up (dish on plate, drink in cup, ingredient detail) — strongest.
   - Architecture / theming / interior / exterior — second.
   - Chef-at-work / kitchen action (people-as-craft) — third.
   - Patrons-as-subject (diners, family-at-table) — last resort, often skip.
   When a press kit offers (a) a dish close-up and (b) "happy family eating that dish", select (a). Surface (b) only if it's the only image available for that venue AND the framing makes the people incidental.

2. **Per-pick image floor: 2 minimum.** Every Unmissable / Top Attraction / Accommodation pick gets a hero AND at least one inline secondary image (food close-up, detail shot, architecture, theming). A pick that ships with one hero + four paragraphs of prose is under-illustrated.

3. **Per-slot header floor: 1 minimum.** Every meal-slot section in a meal-slots chapter (Field Guide) or equivalent ranked-list section in a Countdown gets a wide header band image under the slot title and intro paragraph. Five slots = five headers.

4. **Same-image-different-context cap: max 2 issue-wide, max 1 per chapter.** A URL may appear at most twice across the entire issue, and at most once per chapter (the `visual-smoke-test.py` D6 gate enforces this; the `--max-uses-per-url 2` flag is the upper limit for deliberate cross-context use like a cover collage + later full-size hero). Same-context duplicates (pick hero + same-venue slot header in the same chapter) are a regression — swap to the venue's secondary image or to a different venue's bundle entry.

5. **Visual scatter across the issue.** Every chapter carries at least one decorative anchor (drop-cap, fleuron divider, pull-quote, ribbon tab, T-MINUS banner, Trip-in-Numbers, hype marquee). For multi-venue issues, decorative anchors at each half's close are mandatory — the half boundaries are the strongest hype-punch positions in the layout.

**Self-audit grep:**
```bash
# 1. Stock-photo dominance check (subject heuristic — manual review of captions
#    in research-bundle.json is the surest test, but a regex flags obvious cases)
python3 -c "
import json
bundle = json.load(open('/tmp/signal-build/research-bundle.json'))
stock_signals = ['gezin', 'family', 'kinderen-aan-tafel', 'vrouw-met', 'barman-met',
                 'koppel', 'couple', 'smiling', 'child-eating']
candidates = bundle.get('image_candidates', [])
flags = [c for c in candidates if any(s in (c.get('url_or_keyword','') + c.get('subject','')).lower() for s in stock_signals)]
print(f'{len(flags)} candidates match staged-people signals (of {len(candidates)} total)')
for c in flags[:5]:
    print(f'  - {c.get(\"url_or_keyword\",\"\")[:80]}')
"

# 2. Same-image-different-context check (per-chapter, post-stitch)
python3 -c "
import re
from collections import Counter
html = open('/tmp/signal-build/signal_*.html').read()
imgs = re.findall(r'https?://[^\s\"<>]+\.(?:jpg|jpeg|png|JPG)', html)
dupes = {u: n for u, n in Counter(imgs).items() if n > 2}
print(f'{len(dupes)} URLs appear >2x:')
for u, n in dupes.items():
    print(f'  {n}x {u.split(\"/\")[-1][:60]}')
"

# 3. Visual-scatter check (count decorative anchors per chapter file)
for f in /tmp/signal-build/chapters/*.html; do
  echo -n "$(basename $f): "
  grep -cE 'hol-dropcap|hol-fleuron|hol-pull|hol-tminus|hol-trip-numbers|hol-ribbon-tab|hol-hype-marquee' "$f"
done
# expect: every chapter ≥1 (except transit/footer where typographic-only bands suffice)
```

---

### RT-18: Lead + Companion topic discipline (v8.15)

When you write a fixed-section chapter, you write BOTH the Lead AND the Companion (or you receive them as two pieces from the planner — confirm both are present). Self-check before submission:

1. Is there a Lead piece (300-700 words) AND a Companion piece (200-450 words)?
2. Are they on visibly different topics, not two framings of the same story?
3. Does each have a substantive body, not a stub?
4. Does each link to at least one canonical source?
5. If your section is World This Week and the Lead is about an ongoing tracked story (Iran, Ukraine), the Companion MUST be on a topic family from a different cluster (not just a different war).
6. If your section is Touchline and the Lead is football, the Companion MUST be a non-football sport.
7. If your section is Screen & Sound and the Lead is Star Wars (or any single franchise), the Companion MUST be from a different franchise.

If any of the above is false, do NOT submit — escalate back to the planner.

### RT-19: Section link discipline (v8.15)

Before submission, count outbound `<a href="http...">` links in your chapter. For sections in {World This Week, Pixel & Byte, Touchline, Screen & Sound, On the Radar}: every substantial item — every Lead, every Companion, every Also item, every Quick Review, every On the Radar entry — must link to its specific canonical source. Category pages and homepages do not count. If you can't find a link for an item, find a different item.

### RT-20: Director's Cut mode discipline (v8.17)

If your Screen & Sound chapter plan has `sub_format: "directors_cut"`:
1. Lead must be 550-750 words and read as an essay on a show / film / director / arc — NOT a current-week news beat.
2. Companion remains mandatory: 250-450 words, on a different topic family. The Companion can carry the current-week news beat that the Director's Cut displaced.
3. Voice for the Lead: culture critic essayist. Not "what dropped this week".
4. Cite where appropriate (link to the show / film, link to interviews if quoted, link to other essays you're responding to).
5. After publish, update state file `last_directors_cut_date`.
6. Optionally mark the section header visually with `<span class="sub-format-tag">Director's Cut</span>` inside the `.section-label`.

### RT-21: A Closer Look mode discipline (v8.17)

If your This Week in History chapter plan has `sub_format: "closer_look"`:
1. Write ONE 600-800 word narrative deep dive on one event or figure. No also-this-weeks timeline. No multiple items.
2. Wikipedia link mandatory for the subject; additional well-sourced links (podcasts, long-form articles, primary sources) welcome.
3. Strong pre-WW2 preference — this format is ideal for ancient/medieval/early modern.
4. Voice: narrative historian — tell the story, ground it in specifics, surface what's surprising. Not encyclopedic.
5. After publish, update state file `last_closer_look_date`.
6. Optionally mark the section header visually with `<span class="sub-format-tag">A Closer Look</span>` inside the `.section-label`.

### RT-22: Bundle-only facts (v8.18.1) — hard rule

**Every named factual claim in your chapter MUST trace back to the research bundle.** This is the same discipline as RT-2 (No-Taste Rule) extended from sensory prose to ALL specifics. The bundle is the ground truth; the writer's job is to *interpret* it editorially, not to invent additions.

**Banned:**
- Inventing media titles, show names, album names, podcast episodes, books, articles, or events that are not in the research bundle. (This is the failure mode observed in the v8.18 test run: writers under-supplied with bundle content invented "Apple Mythic Quest-replacement", "BBC adaptation of Adam Mars-Jones' Box Hill", "Carpenter Brut Knife Twin single" — none real, none in the bundle.)
- Inventing dates, prices, statistics, quotes, or attribution.
- Inventing source names ("according to The Guardian…" when no Guardian article is in the bundle).
- Inventing relationships between things ("X collaborated with Y" without a bundle source confirming).
- "Plausible-sounding" placeholder facts to round out a paragraph.

**Required:**
- Every named title, date, price, stat, or quoted line must be present in `research-bundle.json` (the `sources`, `key_facts`, `image_candidates`, or topic-specific arrays). Trace before you write.
- If the bundle doesn't carry enough material for a piece, do NOT invent — instead: (a) shorten the piece toward the floor (200-word minimum for Companion, 300 for Lead), (b) escalate via the planner for additional research, or (c) suggest a different topic entirely. **Compressed-but-true beats expanded-but-fabricated.** Always.
- Quotes must carry attribution AND a link to the source.
- When in doubt about whether a fact is supported, omit it.

**Self-audit before submission.** Walk every paragraph. For each specific name, date, number, quote: open `/tmp/signal-build/research-bundle.json` and find the supporting entry. If you can't find it, cut the claim.

The whole magazine is undermined by a single fabrication the reader catches. This rule is non-negotiable across every section and every writer subagent.

### RT-23: Lens-not-Filter (v8.19) — discovery vs reinforcement

The reader profile is a lens, not a filter. Two checks every recommendation-section writer makes before submission:

**1. Discovery vs. Reinforcement balance (~50/50 target).** For your section's picks, count how many reinforce something the reader already engages with (Todoist, Cosmere, synthwave, Switch 2, etc.) vs. how many are genuinely new (a different app, an unfamiliar writer, a label they haven't heard of, an adjacent training method). Aim for parity. A section that's 90% reinforcement is a failure mode — it makes the magazine feel like a feed. A section that's 100% discovery is also wrong — it stops feeling curated.

**2. The anti-drift check.** If you can name the dominant brand/app/series your section featured last appearance (look at the state file: `last_toolkit_app`, `last_session_topic`, or the last appearance in `issues/`), this appearance MUST NOT default to the same. Different app, different artist, different angle. The whole point of rotating sections is that they don't become single-topic columns.

If your section is one of the recommendation sections (Shelf, Listen, Workshop, Toolkit, Ledger, Long Game, Wallet, Brickyard, Saga, Lab, Channel, Long Shelf, Companion pieces in fixed sections): apply both checks before submitting.

If your section is World This Week or any news section: **a major world story that landed this week is covered even when it falls outside the declared interest profile.** A vacuum on a story everyone else is reading is a failure mode. Cover at the appropriate weight — Lead, Companion, or substantive Also item — based on the story's actual significance.

For the issue-level Discovery Quota (>= 3 picks per weekly issue): the planner identifies and tags discovery picks in the chapter plan's `discovery_picks` array. Validator rejects plans with < 3. Writers don't need to coordinate across sections — the planner has set the targets.

---

## 3. Canonical Markup Snippets

Copy-paste these directly. Do not invent alternates.

### Pullquote (`.sp-pullquote-huge`)
```html
<blockquote class="sp-pullquote-huge">
  <p>The quote text goes here — pull the most resonant line from the chapter.</p>
  <cite>— Source attribution or chapter context</cite>
</blockquote>
```

### Marginalia (inside `.sp-spread` only)
```html
<aside class="sp-marginalia" data-side="right">
  <span class="sp-marginalia-label">Context Note</span>
  <p>The marginalia body text. A datum, a brief aside, or a quoted fragment.</p>
</aside>
```

### Pull-Break
```html
<div class="sp-pull-break-wrap sp-ground-deep">
  <div class="sp-pull-break">
    <p class="sp-pull">The key sentence from this chapter — the line worth repeating.</p>
    <p class="sp-pull-attrib">— Attribution or context</p>
  </div>
</div>
```

### Chapter Gate + Section (full attribute set)
```html
<!-- Gate must PRECEDE the section -->
<aside class="sp-chapter-gate" data-chapter-num="III"
      data-chapter-title="Five Moments Worth the Trip"
      data-chapter-arc="The memories you'll carry home">
  <div class="scg-arc">Signature Moments</div>
  <div class="scg-numeral">III</div>
  <div class="scg-title">Five Moments Worth the Trip</div>
  <div class="scg-deck">The memories you'll carry home</div>
</aside>

<section data-sp-chapter data-chapter-num="3"
         data-chapter-title="Five Moments Worth the Trip"
         data-chapter-arc="The memories you'll carry home"
         class="sp-ground-ink">
  <!-- chapter content -->
</section>
```

**Hype variant** (Countdown / Field Guide only — never literary):
```html
<aside class="sp-chapter-gate is-hype" data-chapter-num="II" ...>...</aside>
<section data-sp-chapter class="sp-ground-paper is-hype" ...>...</section>
```

### Unmissables (Field Guide — 6–10 picks)
```html
<div class="unmissables">
  <div class="unmissable">
    <figure>
      <img src="https://..." alt="Descriptive alt text">
      <figcaption>What it shows. Credit: Source / License.</figcaption>
    </figure>
    <p>Sensory prose (sourced or factual — no invented flavours). Two to four sentences covering the character of this pick.</p>
    <p class="why-its-here">Why It's Here — one sentence with the sourced reason this pick made the list (frequency / hidden gem / cultural significance / structural uniqueness / theming).</p>
    <dl>
      <dt>Price</dt><dd>€X per person / included with entry</dd>
      <dt>Booking</dt><dd>Walk-in or advance required</dd>
      <dt>Timing</dt><dd>Best time to visit</dd>
      <dt>Walk</dt><dd>Distance from nearest gate / station</dd>
    </dl>
  </div>
  <!-- repeat for each pick -->
</div>
```

### Brief Sidebar
```html
<div class="sp-brief">
  <p class="sp-brief-kicker">Sidebar label — CONTEXT / ASIDE / NOTE</p>
  <h4 class="sp-brief-h">Brief sidebar heading</h4>
  <p>The sidebar body. Factual, concise, 40-80 words.</p>
  <p class="sp-brief-byline">Source or attribution if needed</p>
</div>
```

### Stat Dashboard (`sp-dash`)
```html
<div class="sp-dash">
  <div class="sp-dash-cell">
    <span class="sp-dash-label">Label</span>
    <span class="sp-number" data-to="42">42</span>
    <span class="sp-dash-unit">unit</span>
  </div>
  <!-- max 6 cells; max 1 sp-dash per issue -->
</div>
```

### Three-Column Spread (`.sp-spread`)
```html
<div class="sp-spread">
  <div class="sp-rail" aria-hidden="true"></div>
  <aside class="sp-margin">
    <!-- Marginalia, datum blocks, or small aside content -->
    <aside class="sp-marginalia" data-side="right">
      <span class="sp-marginalia-label">Aside</span>
      <p>Marginalia content.</p>
    </aside>
  </aside>
  <div class="sp-spread-body">
    <!-- Drop-cap auto-applied to p:first-of-type — do NOT wrap manually -->
    <p>Opening paragraph of the chapter's literary body...</p>
    <p>Subsequent paragraphs continue here.</p>
  </div>
</div>
```

---

### Holiday issue scaffold (Countdown + Field Guide only — v8.12)

**Body activation:**
```html
<body class="is-special" data-special="countdown"><!-- or data-special="field-guide" -->
```

**Masthead:**
```html
<header class="hol-masthead">
  <div class="hol-masthead__title">The Signal<span class="stop">.</span></div>
  <div class="hol-masthead__badge">Special Edition · Countdown</div>
  <div class="hol-masthead__meta">No. 02 · 16 May 2026 · T-minus 45 days</div>
</header>
```

**Cover (with live countdown):**
```html
<section class="hol-cover">
  <svg class="hol-cover__cloud hol-cover__cloud--1" viewBox="0 0 320 90" aria-hidden="true">...</svg>
  <svg class="hol-cover__cloud hol-cover__cloud--2" viewBox="0 0 320 90" aria-hidden="true">...</svg>
  <svg class="hol-cover__cloud hol-cover__cloud--3" viewBox="0 0 320 90" aria-hidden="true">...</svg>
  <div class="hol-cover__back-num">45</div>
  <div class="hol-cover__back-script">days</div>
  <div class="hol-cover__inner">
    <div class="hol-cover__sig"><span>The Signal · Holiday Specials · No. 02</span><span>Saturday · 16 May 2026</span></div>
    <div class="hol-cover__overline">The countdown begins.</div>
    <h1 class="hol-cover__title">Forty-five<br>days to <span class="ruby">Efteling</span><br><span class="amp">&amp;</span> <span class="outline">Beekse Bergen</span>.</h1>
    <p class="hol-cover__dek">Cover dek text — a single paragraph framing the issue.</p>
    <div class="hol-cover__layout">
      <div class="hol-countdown" data-target="2026-06-30T09:00:00+02:00">
        <div class="hol-countdown__grid">
          <div class="hol-countdown__cell"><div class="hol-countdown__num" data-cd="days">45</div><div class="hol-countdown__unit">days</div></div>
          <div class="hol-countdown__cell"><div class="hol-countdown__num" data-cd="hours">06</div><div class="hol-countdown__unit">hours</div></div>
          <div class="hol-countdown__cell"><div class="hol-countdown__num" data-cd="mins">42</div><div class="hol-countdown__unit">minutes</div></div>
          <div class="hol-countdown__cell"><div class="hol-countdown__num" data-cd="secs">18</div><div class="hol-countdown__unit">seconds</div></div>
        </div>
        <div class="hol-countdown__target">target · tuesday 30 jun 2026 · 09:00 cest · kaatsheuvel</div>
      </div>
      <div class="hol-cover__collage" aria-hidden="true">
        <figure class="hol-polaroid" style="top: 0; left: 10%;">
          <div class="hol-polaroid__tape"></div>
          <div class="hol-polaroid__photo" style="background-image:url('...');"></div>
          <figcaption class="hol-polaroid__caption">the floating castle.</figcaption>
        </figure>
        <div class="hol-stamp hol-stamp--brass" style="top: 30px; right: 0;"><span>BOOKED<b>JUN 30</b>★ ★ ★</span></div>
      </div>
    </div>
  </div>
</section>
```

**Half opener (use at the top of `.hol-half`):**
```html
<div class="hol-half__opener">
  <div class="hol-half__opener-tag">Part One:</div>
  <h2 class="hol-half__opener-title">Efteling</h2>
  <div class="hol-half__opener-subtitle"><span>The Floating Castle</span></div>
  <div class="hol-half__opener-pills">
    <span>Wondrous Tales</span><span class="dot">•</span>
    <span>Culinary Magic</span><span class="dot">•</span>
    <span>Kaatsheuvel</span>
  </div>
</div>
```

**Half wrapper (each half is one section):**
```html
<section class="hol-half hol-half--one"><!-- or hol-half--two -->
  <div class="hol-half__inner">
    <!-- hol-half__opener, then content components -->
  </div>
</section>
```

**Transit intermission (between Half I and Half II, multi-venue only):**
```html
<section class="hol-transit">
  <div class="hol-transit__side hol-transit__side--left">
    <div class="hol-transit__mega-bg">EFTELING</div>
    <div class="hol-transit__label">
      <span class="hol-transit__hand">Leaving the Castle…</span>
      <span class="hol-transit__name">PART ONE</span>
    </div>
  </div>
  <div class="hol-transit__center">
    <div class="hol-transit__center-card">Transit Intermission</div>
  </div>
  <div class="hol-transit__side hol-transit__side--right">
    <div class="hol-transit__mega-bg">SAFARI</div>
    <div class="hol-transit__label">
      <span class="hol-transit__hand">Entering the Wild…</span>
      <span class="hol-transit__name">PART TWO</span>
    </div>
  </div>
</section>
```

**Holiday unmissable row (alternates left/right — add `hol-unmissable--reverse` to every second row):**
```html
<div class="hol-unmissable">
  <div class="hol-unmissable__photo-wrap">
    <div class="hol-unmissable__photo" style="background-image:url('...');"></div>
  </div>
  <div class="hol-unmissable__card">
    <div class="hol-unmissable__num-row">
      <span class="hol-unmissable__num">01</span>
      <h3 class="hol-unmissable__title">Polles Keuken</h3>
    </div>
    <p class="hol-unmissable__quote">"Source-attributed quote here." — source citation.</p>
    <div class="hol-unmissable__why">Why it's here · source signal type</div>
    <dl class="hol-unmissable__facts">
      <div class="row"><dt>Where</dt><dd>…</dd></div>
      <div class="row"><dt>Order</dt><dd>…</dd></div>
      <div class="row"><dt>Timing</dt><dd>…</dd></div>
      <div class="row"><dt>Walk</dt><dd>…</dd></div>
    </dl>
  </div>
</div>
```

**Anchor feature (use once or twice per half for the headline beat):**
```html
<div class="hol-anchor">
  <div class="hol-anchor__photo" style="background-image:url('...');"></div>
  <div>
    <h3 class="hol-anchor__title">RESTAURANT SAGA</h3>
    <p class="hol-anchor__dek">Italic serif dek text — the case for this feature.</p>
    <div class="hol-anchor__meta">
      <div>⏱ TIME<br><b>45 MIN</b></div>
      <div>★ TIER<br><b>HOT</b></div>
    </div>
  </div>
  <div class="hol-anchor__badge">Seasonal<br>Special</div>
  <div class="hol-anchor__note">* magic in the air *</div>
</div>
```

**Don't Miss block:**
```html
<div class="hol-dont-miss">
  <div class="hol-dont-miss__kicker">don't miss</div>
  <h3 class="hol-dont-miss__title">Three Efteling bites worth a detour</h3>
  <ul class="hol-dont-miss__list">
    <li><b>Stroopwafel cart.</b> Description here.</li>
    <li><b>Second item.</b> Description.</li>
    <li><b>Third item.</b> Description.</li>
  </ul>
</div>
```

**Marquee (kinetic section transition):**
```html
<div class="hol-marquee" aria-hidden="true">
  <div class="hol-marquee__track">
    <span>One repeating phrase</span>
    <span>Another</span>
    <span>Third</span>
    <span>One repeating phrase</span>
    <span>Another</span>
    <span>Third</span>
  </div>
</div>
```
Double the phrase list so the loop is seamless.

**Meanwhile + sign-off (closes the issue):**
```html
<section class="hol-meanwhile">
  <div class="hol-meanwhile__giant-bg">SIGNAL</div>
  <div class="hol-meanwhile__inner">
    <div>
      <h2 class="hol-meanwhile__title">Meanwhile…</h2>
      <p class="hol-meanwhile__body">Closing serif italic paragraph.</p>
    </div>
    <div class="hol-subscribe">
      <div class="hol-subscribe__inner">
        <h3 class="hol-subscribe__title">Don't miss the next chapter.</h3>
        <p class="hol-subscribe__hand">Hand-script tagline.</p>
      </div>
    </div>
  </div>
  <div class="hol-footer-row">
    <div class="hol-footer-row__brand">The Signal<span class="stop">.</span></div>
    <div class="hol-footer-row__links"><span>Holiday Specials</span><span>Archive</span></div>
    <div class="hol-footer-row__tagline">"Eat well, travel often."</div>
  </div>
</section>
```

---

## 4. Self-Audit Checklist

Run these greps against your chapter HTML before submitting. Every command should return the expected value.

```bash
# RT-7a: No banned pullquote div
grep -c '<div class="sp-pullquote-huge"' chapter.html           # expect: 0

# RT-7b: No banned pullquote child classes
grep -c 'class="sp-pq-quote"' chapter.html                      # expect: 0
grep -c 'class="sp-pq-attrib"' chapter.html                     # expect: 0

# RT-7c: No banned marginalia div
grep -c '<div class="sp-marginalia"' chapter.html               # expect: 0

# RT-7d: No banned marginalia label classes
grep -c 'class="sp-marg-kicker"' chapter.html                   # expect: 0
grep -c 'class="sp-marg-label"' chapter.html                    # expect: 0

# RT-7e: No banned pull-break blockquote
grep -c '<blockquote class="sp-pull-break"' chapter.html        # expect: 0

# RT-7f: No banned brief sidebar aside
grep -c '<aside class="sp-brief"' chapter.html                  # expect: 0

# RT-7g: No banned brief heading level
grep -cE '<h[123][^>]*class="sp-brief-h"' chapter.html          # expect: 0

# RT-7h: No banned hero quote blockquote
grep -c '<blockquote class="sp-hero-quote"' chapter.html        # expect: 0

# RT-1: No reader-profile leak phrases
grep -iE 'your (son|kids|10.year.old|partner|tablet|watch)|you.ll love|perfect for (your|you)|since you|as a.*fan|spoiler.free' chapter.html
# expect: no output

# RT-8: Chapter gate has all required attributes
grep 'sp-chapter-gate' chapter.html | grep -v 'data-chapter-num'
# expect: no output (every gate must have data-chapter-num)

# RT-3: No coral outside allowed elements
grep -E 'color.*E8384F|color.*sp-accent-primary' chapter.html
# expect: no output (CSS handles accent; never set coral inline)

# RT-13 (holiday only — Countdown / Field Guide):
# No default-chrome markup. Run only when data-special="countdown" or "field-guide".
grep -cE 'class="sp-chapter-gate|class="sp-spread|class="sp-pull-break|class="sp-marginalia|class="sp-brief|class="sp-dash|class="sp-chapter-chrome|class="unmissables|class="unmissable[ "]' chapter.html
# expect: 0 on holiday issues. Non-zero is a hard fail — use .hol-* vocabulary.

# RT-13b: Every holiday issue uses at least one .hol-half
grep -c 'class="hol-half ' chapter.html
# expect: ≥1 on holiday issues. 0 means the issue is missing the structural unit.

# RT-13c: Multi-venue holiday issues have exactly one .hol-transit
grep -c 'class="hol-transit"' chapter.html
# expect: 1 on multi-venue holiday issues, 0 on single-venue. Never 2+.

# RT-6: No fabricated URL patterns (bare domains without path)
grep -oE 'href="https?://[^/"]+/"' chapter.html
# expect: empty or only known category pages — check each result

# RT-10: Pull-break has wrapper
grep -n 'sp-pull-break' chapter.html
# expect: every sp-pull-break line has a sp-pull-break-wrap in context
```

---

## 5. Lookup Chain

If you need detail beyond what's in this file:

1. **`references/editorial-spec.md`** — full spec (980 lines)
2. **`references/compliance-checklist.md`** — Gate 1 + Gate 2 + Gate 3 mechanical checks
3. **`references/spec/global/04-markup-contracts.md`** — full markup contract table (all banned alternates)
4. **`references/spec/global/07-accent-lockdown.md`** — full accent lockdown rules
5. **`references/spec/formats/<format>.md`** — format-specific requirements for this issue
6. **`references/spec/specials/`** — chapter gate, imagery budget, ground discipline in detail
