# The Signal — Compliance Checklist

> Run this after generation (Step 7) and after editorial review (Step 8) in the workflow.
> Gate 1 is mechanical — zero tolerance, fix before proceeding. Gate 2 is editorial — fix failures before delivery.
> Source of truth for allowed components: `assets/styles.css` and `assets/weekly-template.html`.

---

## GATE 1 — Hard Fails

Gate 1 is a mechanical text scan. Every item below is binary: pass or fail. No partial credit. **Fix every failure before proceeding to Gate 2.**

---

### 1A — Reader-Profile Leaks

The reader profile drives topic selection. It must be invisible in the prose. Scan the entire HTML output for every instance of the following patterns (case-insensitive). Any match is a hard fail.

**Forbidden direct-address patterns:**
- "as a banking"
- "your role in fintech"
- "since you're tracking a 10k"
- "since you're training"
- "fellow Malazan fan"
- "fellow Cosmere fan"
- "fellow [X] fan" (any fandom substituted)
- "as a [job title]" (any job title substituted)
- "as an engineering manager"
- "your work in banking"
- "in your line of work"
- "your Garmin"
- "your Ibex programme"
- "your 10k"
- "your run"
- "your home gym"
- "your house in Northern Ireland"
- "your dog"
- "your Pixel"
- "your Monzo"
- "for someone like you"
- "if you're a fan of [X]" where X is any tracked interest
- "you'll love this if you play Nintendo"
- "as a parent"
- "if you're considering children"
- Second-person "you" used to make a claim about the reader's job, family, location, fitness level, or interests

**The cardinal rule verbatim (must be embedded in your reasoning, not your output):** The reader profile is invisible in the prose. Write as a general-interest Sunday magazine journalist for any educated adult. The reader profile drives TOPIC SELECTION — it never shows in voice, framing, or second-person address. No "as a banking engineering manager", no "your role in fintech", no "since you're tracking a 10k", no "fellow Malazan fan".

**Fix:** Rewrite the sentence as though writing for any educated adult Sunday magazine reader. Remove the direct address entirely.

---

### 1B — Fabrication

Scan for unsourced numeric claims and attributed quotes.

**Statistics:**
- Every percentage, metric, price, count, or rate in the issue must have a source attributed.
- Inline attribution ("according to the ONS", "per the Bank of England") is sufficient for prose.
- Any stat that appears in a `.dash__cell`, `.datum-card`, `.plate__stat`, or `.chart-card__foot` must have a source in the Colophon sources block.
- Fail if: a stat is stated as fact with no attribution and no colophon source.

**Quotes:**
- Every attributed quote (in `.pull-break__quote`, `.pull-quote-card`, `.marginalia__pull`, `blockquote`) must be traceable to a real person who said it in a real context.
- Fail if: a quote is attributed to a named individual but cannot be verified as real. When in doubt, use "— paraphrased" or rephrase as reported speech.
- Fail if: a fictional quote (invented for atmosphere) is presented as a real attributed quote.

**Book/product details:**
- Author names, publisher names, game titles, app version numbers must be accurate.
- Fail if: a title is attributed to the wrong author.

---

### 1C — Staleness

**Date in masthead:**
- The masthead `<header class="mast">` must display the current issue date in the `line1` div: `SUNDAY 06:40 · NO. [N] · [DD MONTH]`.
- The `.cover__meta-top` and the Colophon footer must also carry the correct date.
- Fail if: the date is blank, templated (`[DD MONTH]`), or more than 6 days behind the generation date.

**"Last week" references:**
- Fail if: any reference to "last week" in The Week section describes an event that predates the current issue by more than 12 days.
- Fail if: any ongoing story counter (e.g. "Week 7 of the conflict") is not updated from the state file.

**Issue number:**
- Fail if: the issue number in the masthead, cover, Contents, and Colophon do not all match.

---

### 1D — Links

**Outbound links:**
- All `href` values in the issue must be either `#` (internal anchor) or begin with `https://` or `http://`.
- Fail if: any href is a relative path, a placeholder (`[URL]`), an empty string, or a `javascript:` URI.
- Outbound links in the Colophon sources block must open in a new tab (`target="_blank" rel="noopener"`).

**Colophon sources:**
- The Colophon must have ≥ 6 source entries in `.colophon__sources`.
- Each source must have a non-empty `href` that is a real URL.
- Fail if: any source URL is a placeholder.

---

### 1E — Forbidden Fonts, Hexes, and Classes

Scan the HTML and any inline styles for the following. **Any match is a hard fail.**

**Forbidden fonts (must not appear in any `font-family`, `@font-face`, or Google Fonts URL):**
- `Cormorant`
- `DM Sans`
- `JetBrains Mono`
- `Instrument Serif`
- `Inter`
- `Newsreader`
- `IBM Plex Mono`

The only permitted fonts are **Fraunces** and **Geist**, loaded from the Google Fonts URL in `<head>`.

**Forbidden hex values (must not appear in any `style=""`, `fill`, `stroke`, or colour property):**
- `#1B1B2F`
- `#E8384F`
- `#D2FF00`
- `#FF8700` (McLaren orange)
- Any hex that is not from the ember, dossier, blueprint, or midnight palette definitions in `styles.css`.

Never use `rgb()` or `rgba()` inline for colour values if the colour is not defined as a CSS variable.

**Forbidden CSS classes (must not appear anywhere in the HTML):**

| Forbidden | Use instead |
|-----------|-------------|
| `.book-card` | `.fan-spread__card` |
| `.big-number` | `.dash__num` or `.datum-card__value` |
| `.big-number-row` | `.dash` |
| `.cover-brand` | `.mast` |
| `.section-label` | `.section-eyebrow` or `.spine-label` |
| `.cover-tags` | `.cover__tags` |
| `.cover-headline` | `.cover__headline` |
| `.cover-issue` | `.cover__meta-top` |
| `.cover-noise` | `.grain` |
| `.cover-grain` | `.grain` |
| `.dyk` | *(no equivalent — remove the "Did you know" pattern entirely)* |
| `.angle` | *(no equivalent — remove)* |
| `.also-cards` | `.brief-grid` |
| `.also-list` | `.colophon__list` |
| `.compare-panel` | *(no equivalent — use `.chart-card` or `.dash`)* |
| `.stat-bar` | `.dash__cell` or `.plate__stat` |
| `.workout-card` | `.fan-spread__card` |
| `.card-stack` | `.fan-spread__deck` |
| `.sidebar` | `.marginalia` |
| `.sidebar-float` | `.marginalia` |
| `.margin-note` | `.marginalia__note` |
| `.entry-stat` | `.datum-card` |
| `.entry-quote` | `.pull-quote-card` or `.marginalia__pull` |
| `.entry-question` | *(remove)* |
| `.tier-hot` | *(remove tier patterns entirely)* |
| `.tier-warm` | *(remove)* |
| `.tier-note` | *(remove)* |
| `.nav-section` | `.mast` |
| `.nav-grid` | *(remove)* |
| `.nav-card` | *(remove)* |
| `.radar-grid` | *(remove)* |
| `.league-table` | `.contents-ledger` |
| `.results-strip` | `.index-strip` |
| `.split-60-40` | *(use CSS grid inline or layout within feature-band)* |
| `.img-offset` | `.feature-band__hero` |
| `.breather` | `.ribbon` or `.pull-break` |
| `.rating` | *(no equivalent — express opinion in prose)* |
| `.collapsible` | *(remove)* |
| `.mag` | *(remove)* |
| `.pull-quote` wrapper | `.pull-quote-card` |

**Forbidden section names and vocabulary:**
- "Dispatch" (the word — the seal component `dispatch-seal` is fine, but do not call the issue a "Dispatch")
- "Chapter" as a section label
- "Foreword" (use "Editor's Note")
- "Navigator" (use `.mast`)
- Roman numerals as section markers (I, II, III — use arabic: 01, 02, 03)
- "The Long Shelf" (it is "The Shelf")
- "The World This Week" (it is "The Week")
- "Pixel & Byte" (no longer exists)
- "The Touchline" (no longer exists)
- "Screen & Sound" (no longer exists)
- "The Session" (no longer exists)
- "The Wallet" (no longer exists)
- "On the Radar" (no longer exists)
- "Footer" (it is "Colophon")

---

### 1F — Template Placeholders

During generation (Step 5), the template markers `<!-- INJECT:CSS -->` and `<!-- INJECT:JS -->` must be present in the output:
- `<!-- INJECT:CSS -->` inside `<head>`, after the Google Fonts link.
- `<!-- INJECT:JS -->` just before `</body>`.

**Before inject (Steps 1–5):** both markers must be present.
**After inject (Step 6 — `bash scripts/inject-assets.sh <file>`):** both markers are replaced by the full CSS and JS. Verify neither marker remains in the injected file.

Fail if: markers are absent before inject, or still present after inject.

---

## GATE 2 — Editorial & Visual Quality

Gate 2 items may require editorial judgement. Fix all failures before delivery.

---

### 2A — Coverage

**Core groups:** Confirm that every core group from the Search Checklist was researched and is represented in the issue:
- World news
- UK news
- Sport (PL, CL, Serie A/Juventus, golf if in season)
- Tech and Gaming
- Entertainment
- Training and Running
- UK Personal Finance
- Books

Not every group needs a full section — some will appear as items in The Week. But none should be silently missing.

**Rotating sections:** Confirm that each selected rotating section was fully researched using its specific search groups from `sections.md`.

---

### 2B — Rotating Sections

- Confirm 2–3 rotating sections were selected (not fewer, not more).
- Confirm selection was by cadence priority (most overdue first).
- Confirm Down the Rabbit Hole was evaluated against its cadence and included or excluded accordingly.
- Confirm no two consecutive rotating sections share the same primary component without a ribbon or pull-break interlude between them.

---

### 2C — Ongoing Stories

Check the `ongoing_stories` array in the state file. For each active story:
- Confirm the story is either updated as a lead item, a Week item, or carries a running counter ("Week N of the conflict").
- If a story has been ongoing for ≥ 3 weeks, it should be mentioned somewhere even if not as the lead.
- Fail if: an active ongoing story is not referenced anywhere in the issue.

---

### 2D — Structure

- Confirm exactly 13 structural positions in the correct order (Cover → Contents → Lead → Lead Pull-Break → The Week → [rotating A] → [rotating B] → [rotating C if selected] → Rabbit Hole → Rabbit Hole Pull-Break → Editor's Note → Colophon).
- Confirm grounds alternate (dark/paper) across consecutive sections. No two adjacent sections share the same ground.
- Confirm Lead is paper by default (or dark with justification noted in a comment).
- Confirm Rabbit Hole ground contrasts the section immediately preceding it.
- Confirm Colophon is dark.
- Confirm Cover is dark.

---

### 2E — Voice

- Every list item (in `.index-strip`, `.colophon__list`, `.brief-card`, fan-spread card body, plate caption, timeline-row body) carries ≥ 1 opinion sentence — not just a factual description.
- British English throughout: colour, favour, programme, defence, analyse, realise.
- No spoilers for Malazan, Cosmere (any Sanderson), Star Wars (any era), or The Running Man.
- No hedging filler ("quite possibly", "somewhat arguably").

---

### 2F — Visual Variety

- ≥ 4 distinct component types used across the issue.
- No single component used more than twice consecutively without a visual break.
- ≥ 1 image per major section (Lead, each rotating section, Rabbit Hole). Images must have descriptive `alt` text — not empty, not "[ALT]".
- ≥ 2 pull quotes total (one per pull-break, ≥ 1 more in marginalia or pull-quote-card).
- ≥ 1 `.count-up` stat with a real `data-target` numeric value.
- ≥ 1 `.fan-spread` or `.plate-strip` in the rotating sections.

---

### 2G — Motion

- Cover hero image has `.parallax` class on the container div (required).
- Feature-band hero images have `.parallax` (recommended — warn if absent).
- All major content blocks have `.reveal` class.
- All numeric stat displays (`.dash__num`, `.plate__stat-num`, `.datum-card__value`) contain a `.count-up` span with a real `data-target`.
- At least one `.ribbon` is present (with `.ribbon__track` and ≥ 3 `.ribbon__item` elements).
- No motion class is applied to an element that does not exist in the CSS (run Gate 1E first).

---

### 2H — Responsive Layouts

- The issue should read cleanly at 1194×834 (landscape tablet) and 834×1194 (portrait tablet).
- Fan-spread decks must not overflow their container on portrait.
- Plate-strips use horizontal scroll-snap — confirm `overflow-x: auto` is not overridden.
- No fixed-width values that would clip content below 768px wide.

---

### 2I — Technical

- Valid HTML: every opened tag is closed; no unclosed `<section>`, `<div>`, `<article>`.
- All `<img>` have `alt` text that is descriptive (not empty, not a placeholder).
- All `href` values in the Colophon sources are real URLs beginning with `https://`.
- Outbound links in the sources block have `target="_blank" rel="noopener"`.
- The `.dispatch-seal` has `data-num`, `data-month`, and `data-year` attributes set with real values, not placeholders.
- No inline `style="font-family: ..."` anywhere. CSS owns all fonts.
- No inline `style="color: #..."` unless overriding `--accent` for a dossier scheme section (`style="--accent:#b8902a;"`).
- The `<body>` has `data-scheme="ember"` and `data-ground="dark"` attributes.
- `<html lang="en">` is present.
- `<meta charset="UTF-8">` and `<meta name="viewport" ...>` are present.

---

## Quick Checklist Summary

Copy-paste for fast pre-delivery review:

**Gate 1 (zero-tolerance):**
- [ ] 1A: No reader-profile leaks in prose
- [ ] 1B: All stats sourced, all quotes attributable
- [ ] 1C: Date correct in masthead, cover, and colophon; issue number consistent
- [ ] 1D: All links `https://` or internal anchors; colophon has ≥ 6 real URLs
- [ ] 1E: No forbidden fonts, hexes, or class names
- [ ] 1F: INJECT markers present before injection; absent after injection

**Gate 2 (editorial quality):**
- [ ] 2A: All 8 core groups covered
- [ ] 2B: 2–3 rotating sections selected by cadence priority; DtRH evaluated
- [ ] 2C: Ongoing stories referenced and counters updated
- [ ] 2D: 13 sections in order; grounds alternate; Lead=paper; Rabbit Hole contrasts preceding section
- [ ] 2E: Opinion per list item; British English; no spoilers
- [ ] 2F: ≥ 4 distinct components; ≥ 1 image per major section; ≥ 2 pull quotes; ≥ 1 count-up stat; ≥ 1 fan-spread or plate-strip
- [ ] 2G: Parallax on cover hero; reveal on all blocks; count-up on stats; ≥ 1 ribbon
- [ ] 2H: Readable at 1194×834 and 834×1194
- [ ] 2I: Valid HTML; all img have alt; outbound links open new tab; dispatch-seal has real data attributes; no inline font-family
