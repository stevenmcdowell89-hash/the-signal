# The Signal — Preflight Checklist

Run this checklist against the finished HTML before publishing. Failures in the **MUST PASS** section block publication. Failures in the **EDITORIAL REVIEW** section are warnings that require human judgment.

---

## MUST PASS — Machine-Verifiable Rules

These are checked automatically by `validate-issue.py`. All must pass or the issue is not published.

### Structure & Section Order

- [ ] Section order is: Cover → Navigator → Foreword → Long Shelf → The World This Week → Pixel & Byte → The Touchline → Screen & Sound → The Shelf → The Session (if present) → This Week in History → On the Radar → Footer
- [ ] Cover contains: masthead ("The Signal"), date range, issue number, headline hook, topic tags
- [ ] Navigator contains stories grouped by section with colour-coded cards
- [ ] Navigator card count matches actual story count in the issue (±2 tolerance for one-liners)
- [ ] Every section has a full-width coloured gradient divider bar (8px) above it
- [ ] Footer is present with masthead and issue metadata

### Word Counts & Volume

- [ ] Total word count is 6,000–10,000 (target 6,000–8,000+, hard floor 5,000)
- [ ] Foreword is 50–80 words (hard limit — fail if over 80 or under 50)
- [ ] This Week in History main feature is 150–300 words
- [ ] The Long Shelf has 6–8 items (each with: linked title, source, one-sentence rationale)
- [ ] Release Radar has 15+ items across all categories
- [ ] Release Radar has all four sub-sections: Now Showing, Coming Soon, Leaving Soon, Also Streaming

### Images

- [ ] Total `<img>` tag count is ≥ 6 (minimum one per major section)
- [ ] The World This Week has ≥ 1 image
- [ ] Pixel & Byte has ≥ 1 image
- [ ] The Touchline has ≥ 1 image
- [ ] Screen & Sound has ≥ 1 image
- [ ] The Shelf has ≥ 1 image (book cover or album art)
- [ ] No `<img>` tags have empty or missing `alt` attributes
- [ ] No `<img>` tags reference AI-generated images or generic stock photos

### Typography

- [ ] Google Fonts link loads: Playfair Display (400, 700, 900), Source Serif 4 (400, 600, 700, 400italic), Source Sans 3 (400, 600, 700)
- [ ] Headlines use `font-family: 'Playfair Display', serif`
- [ ] Body text uses `font-family: 'Source Serif 4', serif`
- [ ] UI elements (tags, labels, nav, captions) use `font-family: 'Source Sans 3', sans-serif`
- [ ] No other font families appear in the CSS (except generic fallbacks)

### Colour Palette

- [ ] Primary dark: `#1A1A2E`
- [ ] Mid dark: `#16213E`
- [ ] Warm accent (rose): `#E94560`
- [ ] Secondary accent (amber): `#FF6B35`
- [ ] Cool accent (blue): `#0F3460`
- [ ] Off-white bg: `#F7F7F8`
- [ ] Surface bg: `#F0F0F3`
- [ ] Body text: `#2D2D3A`
- [ ] Muted text: `#7F8C9B`
- [ ] Border: `#E2E2E8`

### Layout

- [ ] Magazine container uses `max-width: 880px`
- [ ] Responsive breakpoint exists for ≤700px
- [ ] Sections have ≥40px vertical padding
- [ ] Two-column layouts stack to single column on mobile

### Section Content Minimums

- [ ] The World This Week: ≥ 2 stories with depth + "Also This Week" list of ≥ 5 one-liners
- [ ] Pixel & Byte: ≥ 2 stories + "Also in Tech & Gaming" one-liners
- [ ] The Touchline: league tables present for Serie A (top 6+) and Premier League (top 6+)
- [ ] The Touchline: key results from the week listed
- [ ] The Touchline: Champions League results/fixtures present (when CL games were played)
- [ ] The Touchline: ≥ 1 narrative piece (Juve or PL or CL)
- [ ] The Touchline: "Also on the Pitch" one-liners present
- [ ] Screen & Sound: ≥ 1 feature piece + Release Radar
- [ ] The Shelf: books sub-section present with ≥ 2 items
- [ ] The Shelf: podcasts sub-section present with ≥ 1 cross-reference to reader's podcasts
- [ ] This Week in History: main feature present + ≥ 3 "Also This Week in History" one-liners
- [ ] On the Radar: ≥ 5 forward-looking items

### Source Attribution

- [ ] Every story beyond one-liners has source links
- [ ] Sources are linked (not just named)
- [ ] At least one Reddit source appears somewhere in the issue (r/fantasybooks, r/kettlebell, r/NintendoSwitch, r/Juve, r/StarWars, r/lego, etc.)

### Mandatory Search Coverage

These topics must have been searched during research. The validation script checks for evidence of coverage (keyword presence) in the final HTML:

- [ ] "Iran" or current dominant running story mentioned
- [ ] "Northern Ireland" or "NI" mentioned (even if just a one-liner)
- [ ] "Switch 2" or "Nintendo" mentioned
- [ ] "AI" mentioned (consumer AI context)
- [ ] "Star Wars" mentioned
- [ ] "LEGO" or "Lego" mentioned
- [ ] "Juventus" or "Juve" mentioned
- [ ] "Serie A" mentioned
- [ ] "Premier League" mentioned
- [ ] "Champions League" or "CL" mentioned (when in season)
- [ ] "synthwave" or a tracked artist name mentioned (Carpenter Brut, Kavinsky, Gunship, Perturbator, FM-84, The Midnight, Madeon, AWOLNATION)
- [ ] "kettlebell" or "Dan John" or "StrongFirst" mentioned
- [ ] "Disney" mentioned (parks or entertainment context)

---

## EDITORIAL REVIEW — Human Judgment Required

These cannot be checked mechanically. Review after the machine checks pass.

### Tone & Voice

- [ ] Foreword finds one editorial thread — not a summary of the issue
- [ ] Foreword does NOT use "meanwhile", "elsewhere", or "also this week"
- [ ] Foreword does NOT restate the cover contents in prose form
- [ ] Tone flexes by section (sharper for world news, enthusiastic for gaming, personality for football, practical for fitness)
- [ ] Reads like a magazine, not a news digest or AI summary
- [ ] Has opinions — at least one take the reader can agree or disagree with
- [ ] Screen & Sound has editorial opinion, not just press-release summaries

### Content Quality

- [ ] Stories framed through "what does this mean" / "the angle you didn't get from the headline"
- [ ] No generic fitness advice written from training knowledge (must be sourced)
- [ ] Football reads as narrative, not match reports
- [ ] Tech reads as consumer impact, not press releases
- [ ] Depth calibrated to significance (big stories get full treatment, minor stories get one-liners)
- [ ] No work/enterprise content unless it clears the Monday-morning threshold
- [ ] No UK party politics, celebrity gossip, crypto/Web3

### Wildcard Rule

- [ ] ≥ 2 items the reader did not ask for and would not have found themselves
- [ ] At least 2 Long Shelf items are genuine surprises outside the reader's usual interests
- [ ] The entire issue could NOT have been predicted from the reader's interest list alone

### Cross-Cluster Synthesis

- [ ] At least one explicit connection made between stories in different sections
- [ ] Local NI stories connected to wider context when relevant

### The Reader's Son

- [ ] At least one mention of family-friendly/co-op content when relevant games or shows are covered

### Book Recommendations

- [ ] At least one "If you liked X, try Y" recommendation (rotate across issues — not required every single week, but should appear most weeks)

---

## Post-Publish

- [ ] HTML renders correctly at 880px width
- [ ] All links work (spot-check 5 random links)
- [ ] PDF generated and attached
- [ ] GitHub Pages updated and live
- [ ] Archive index page updated with new issue
