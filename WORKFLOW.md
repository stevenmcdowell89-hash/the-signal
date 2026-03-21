# The Signal — Production Workflow

This document defines the end-to-end workflow for producing an issue of The Signal. Each phase is a discrete step with clear inputs, outputs, and handoff points.

**Source of truth:** `The_Signal_Editorial_Brief_prompt.md` is the sole authority for all editorial, design, and structural decisions. No other template or reference file should override it.

**The AI is the editor. The reader never reviews content or tone.** The reader triggers a run ("run an episode of The Signal") and receives a finished, published issue. All editorial judgment — tone, depth, wildcards, cross-cluster connections, opinion — is the AI's responsibility, enforced through subagent prompts and the preflight validation script. If the script passes and the screenshots look right, the issue ships.

---

## Phase Overview

| Phase | Name | Type | Output |
|-------|------|------|--------|
| 0 | Setup | Orchestrator | Date range, issue number, workspace structure |
| 1 | Research (parallel) | 6–7 subagents | Markdown notes per topic cluster |
| 2 | Image Research | 1 subagent | `images.json` — URLs mapped to sections |
| 3 | Build HTML | 1 subagent (extended context) | `issue-N.html` |
| 4 | Preflight Validation | Script | Pass/fail report |
| 5 | Fix Failures | Subagent (if needed) | Updated `issue-N.html` |
| 6 | Visual QA | Screenshots | AI-verified renders |
| 7 | Generate PDF | Playwright | `issue-N.pdf` |
| 8 | Publish | Git + GitHub Pages | Live URL |

---

## Phase 0: Setup

**Actor:** Orchestrator (main agent)

1. Determine the date range (previous 7 days ending today)
2. Determine the issue number (check existing issues in repo)
3. Create workspace directory: `/home/user/workspace/the-signal/`
4. Create research output directory: `/home/user/workspace/research/`
5. Read the editorial brief to confirm current reader profile, search checklist, and any flagged trips/events

**Output:** Date range string, issue number, clean workspace

---

## Phase 1: Research (Parallel)

**Actor:** 6–7 parallel research subagents, each with `research-assistant` skill loaded

Each subagent covers one topic cluster. They search the web, gather facts, and write structured markdown notes. Each subagent saves its output to a dedicated file.

### Subagent 1: World News & NI
- File: `/home/user/workspace/research/world-news.md`
- Searches: World news this week, Iran/dominant story, Northern Ireland news, central bank decisions, geopolitics, conflicts, economic shifts
- Output: Stories with sources, key stats, "Also This Week" one-liners

### Subagent 2: Gaming, Tech, AI, LEGO, Android
- File: `/home/user/workspace/research/tech-gaming.md`
- Searches: Switch 2 news, Steam Deck news, GeForce Now, consumer AI (ChatGPT/Claude/Gemini), Android/Pixel, Xiaomi, LEGO news/retirements, notable app releases
- Output: Stories with sources, product details, "Also in Tech & Gaming" one-liners

### Subagent 3: Football
- File: `/home/user/workspace/research/football.md`
- Searches: Juventus results/news, Serie A results + standings (full table), Premier League results + standings (full table), Champions League results/fixtures, transfer rumours, Golf majors (if relevant)
- Output: Tables (Serie A top 6+, PL top 6+), match results, narrative storylines, "Also on the Pitch" one-liners
- **Critical:** Must include actual league table data with Pos/Team/P/W/D/L/Pts columns

### Subagent 4: Film, TV, Star Wars, Disney Parks
- File: `/home/user/workspace/research/screen-sound.md`
- Searches: New movies this week, new TV shows, Star Wars news, Disney Parks news, Efteling news (when trip flagged), Peaky Blinders/major franchise updates, streaming catalogue changes
- Output: Feature stories, Release Radar items across ALL categories (film, TV, games, LEGO, tech, books, music — target 20+ items), "Also in Film & TV" one-liners
- **Release Radar must have 4 sub-sections:** Now Showing/Just Dropped, Coming Soon, Leaving Soon, Also Streaming This Month

### Subagent 5: Books, Music, Podcasts
- File: `/home/user/workspace/research/shelf.md`
- Searches: Fantasy/sci-fi book releases, Malazan/Cosmere/Sanderson news, Nebula/Hugo nominations, synthwave releases (Carpenter Brut, Kavinsky, Gunship, etc.), notable album releases in other genres, Football Weekly latest, The Bunker latest, What Went Wrong latest, Reddit r/fantasybooks, r/StarWars, r/lego
- Output: Book recommendations (including "if you liked X, try Y"), music features, podcast cross-references, "Also on The Shelf" one-liners
- **Must include at least one Reddit thread/source**

### Subagent 6: Fitness, Running, History
- File: `/home/user/workspace/research/fitness-history.md`
- Searches: Kettlebell programming articles (Dan John, StrongFirst, Pat Flynn), running training methodology, hybrid training, Zone 2, nutrition research, parkrun NI, "this week in history" (March 15-21 across centuries, preference for pre-WW2/ancient)
- Output: Feature article (sourced, not generic advice), "Did You Know" facts, History main feature (150-300 words) + 3-4 "Also This Week in History" one-liners
- **History feature must be a specific event from this calendar week**

### Subagent 7 (optional): Wildcards & Gap-Filling
- File: `/home/user/workspace/research/wildcards.md`
- Searches: Scientific breakthroughs, extraordinary journalism, cultural phenomena outside reader's usual interests, "did you know" facts, architectural/design angles on existing stories
- Output: 3-5 wildcard items suitable for Long Shelf, Did You Know boxes, or one-liners
- **Wildcard rule: at least 2-3 items the reader would not have found themselves**

---

## Phase 2: Image Research

**Actor:** 1 dedicated subagent

**This phase is mandatory. Issues without images fail preflight validation.**

The image subagent reads all research files, identifies the major stories per section, and searches for appropriate images.

### Process:
1. Read all research markdown files from Phase 1
2. For each major section, identify 1-3 stories that need images
3. Use image search to find: game screenshots/key art, match photos, film stills, product shots, book covers, album art, historical images
4. Save results to `/home/user/workspace/research/images.json`

### Output format (`images.json`):
```json
{
  "world": [
    {
      "story": "Iran War - Kharg Island",
      "url": "https://example.com/image.jpg",
      "alt": "Satellite image of Kharg Island oil terminal",
      "caption": "Kharg Island, responsible for 90% of Iran's crude exports. Reuters",
      "width": "full"
    }
  ],
  "pixel-byte": [...],
  "touchline": [...],
  "screen-sound": [...],
  "shelf": [...],
  "session": [...],
  "history": [...]
}
```

### Rules:
- Minimum 1 image per major section (world, pixel-byte, touchline, screen-sound, shelf)
- Target 8-12 images total
- Prefer: official press images, screenshots, match photos, book covers, album art
- Never use: AI-generated images, generic stock photography
- Every image must have: `url`, `alt` text, `caption` with source credit, `width` ("full" or "inline")
- Book covers and album art: use `width: "inline"` (200-250px)
- Section hero images: use `width: "full"`

---

## Phase 3: Build HTML

**Actor:** 1 subagent with `website-building` skill, extended context enabled

### Inputs:
- All research files from `/home/user/workspace/research/`
- Image manifest from `/home/user/workspace/research/images.json`
- Editorial brief from `/home/user/workspace/The_Signal_Editorial_Brief_prompt.md`

### Critical instructions for the builder:

**Typography (from the brief):**
- Headlines: `Playfair Display` (serif, 900 weight for titles, 700 for section heads)
- Body: `Source Serif 4` (serif)
- UI elements, tags, labels, navigator: `Source Sans 3` (sans-serif)
- Google Fonts link: `https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap`

**Colour palette (from the brief):**
- Primary dark: `#1A1A2E`
- Mid dark: `#16213E`
- Warm accent (rose): `#E94560`
- Secondary accent (amber): `#FF6B35`
- Cool accent (blue): `#0F3460`
- White: `#FFFFFF`
- Off-white: `#F7F7F8`
- Surface: `#F0F0F3`
- Body text: `#2D2D3A`
- Muted text: `#7F8C9B`
- Border: `#E2E2E8`
- Success: `#00B894`
- Alert: `#E74C3C`

**Layout:**
- Magazine container: `max-width: 880px`, centred, white background, subtle shadow
- Responsive breakpoint at ≤700px
- Section padding: ≥40px vertical
- 8px gradient divider bars between every section

**Foreword:** 50-80 words. One editorial thread. No "meanwhile", "elsewhere", "also this week". Not a summary of the cover.

**Images:** Embed all images from `images.json` at appropriate points. Full-width images get `width: 100%` with `aspect-ratio: 16/7` and `object-fit: cover`. Inline images get `max-width: 250px`. All images must have `alt` text and a caption.

**Output:** Single complete HTML file at `/home/user/workspace/the-signal/issues/issue-N.html`

---

## Phase 4: Preflight Validation

**Actor:** Orchestrator runs the validation script

```bash
python /home/user/workspace/the-signal/validate-issue.py /home/user/workspace/the-signal/issues/issue-N.html
```

### If all checks pass:
→ Proceed to Phase 6 (Visual QA)

### If any checks fail:
→ Proceed to Phase 5 (Fix Failures)

---

## Phase 5: Fix Failures (Conditional)

**Actor:** 1 subagent (or the orchestrator for simple fixes)

Read the validation report. Fix each failure:
- **Missing images:** Add `<img>` tags using URLs from `images.json`
- **Wrong fonts:** Replace font-family declarations
- **Wrong colours:** Replace hex values
- **Wrong max-width:** Change to 880px
- **Over-length foreword:** Trim to 80 words
- **Missing sections:** Add missing content

After fixing, re-run Phase 4. Repeat until all MUST-PASS checks pass.

**Maximum iterations:** 3. If still failing after 3 rounds, flag to user.

---

## Phase 6: Visual QA

**Actor:** Orchestrator using Playwright screenshots

1. Start a local HTTP server serving the issue directory
2. Take full-page screenshots at 880px width
3. Take section-specific screenshots (cover, touchline, screen & sound, shelf)
4. Visually verify:
   - Fonts render correctly (serif headlines, serif body, sans-serif UI)
   - Colour sections are distinct and identifiable
   - Images display properly
   - Tables are readable
   - No text overflow, truncation, or wrapping issues
   - Section dividers are visible
   - Mobile responsiveness (optional: screenshot at 375px width)

---

## Phase 7: Generate PDF

**Actor:** Orchestrator using Playwright

```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file:///path/to/issue-N.html', { waitUntil: 'networkidle' });
await page.waitForTimeout(3000); // wait for fonts
await page.pdf({
  path: '/path/to/issue-N.pdf',
  format: 'A4',
  printBackground: true,
  margin: { top: '0', right: '0', bottom: '0', left: '0' }
});
await browser.close();
```

The PDF is a supplementary download — the HTML is the canonical format.

---

## Phase 8: Publish

**Actor:** Orchestrator using GitHub CLI

1. Clone or pull the `the-signal` repo
2. Copy `issue-N.html` and `issue-N.pdf` to `issues/`
3. Update `index.html` archive page with new issue card
4. Commit and push
5. Wait for GitHub Pages build to complete
6. Verify live URLs:
   - Archive: `https://stevenmcdowell89-hash.github.io/the-signal/`
   - Issue: `https://stevenmcdowell89-hash.github.io/the-signal/issues/issue-N.html`
   - PDF: `https://stevenmcdowell89-hash.github.io/the-signal/issues/issue-N.pdf`

---

## File Structure

```
/home/user/workspace/
├── The_Signal_Editorial_Brief_prompt.md    ← sole source of truth
├── research/
│   ├── world-news.md
│   ├── tech-gaming.md
│   ├── football.md
│   ├── screen-sound.md
│   ├── shelf.md
│   ├── fitness-history.md
│   ├── wildcards.md                        ← optional
│   └── images.json                         ← image manifest
└── the-signal/
    ├── WORKFLOW.md                          ← this file
    ├── preflight-checklist.md              ← human-readable checklist
    ├── validate-issue.py                   ← machine validation script
    ├── index.html                          ← archive page
    └── issues/
        ├── issue-1.html
        ├── issue-1.pdf
        ├── issue-2.html
        └── issue-2.pdf
```

---

## Quick Reference: Common Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| No images | Image research phase skipped or builder didn't use images.json | Run Phase 2, re-run Phase 3 |
| Wrong fonts | Builder used template fonts instead of brief fonts | Replace CSS font-family declarations |
| Wrong colours | Builder used template colours instead of brief hex values | Replace CSS colour values |
| Foreword too long | Builder wrote a summary instead of a hook | Rewrite: one thread, 50-80 words |
| Missing Release Radar sub-sections | Screen & Sound research didn't categorise releases | Re-research: split into Now/Coming/Leaving/Streaming |
| No Reddit sources | Shelf research didn't check subreddits | Re-search r/fantasybooks, r/kettlebell, etc. |
| Missing league tables | Football research didn't include structured table data | Re-research with explicit table request |
| No "Also" lists | Builder focused on features and forgot one-liners | Add 5-8 one-liners per section from research |
