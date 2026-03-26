---
name: the-signal
description: >-
  Generate issues of The Signal, a weekly personal magazine designed to be read
  on a Sunday morning with coffee. Use when asked to run, generate, create, or
  schedule The Signal, or when the user mentions "the signal", "signal magazine",
  "sunday magazine", "personal magazine", "run the signal", "deep dive",
  "long read", "countdown", "season review", or "shelf special" in the context
  of their personal weekly reading. Supports multiple issue formats: standard
  weekly, deep dive, long read, countdown, season review, and shelf special.
  Includes HTML template, editorial spec, and a compliance checklist.
metadata:
  author: steven-mcdowell
  version: '2.1'
---

# The Signal

Generate issues of The Signal — a weekly personal magazine for Sunday morning reading.

## When to Use This Skill

Use when the user asks to:

- Run, generate, or create a Signal issue (e.g., "Run The Signal")
- Schedule The Signal to run on a recurring basis
- Create a special edition (Deep Dive, Long Read, Countdown, Season Review, Shelf Special)
- Anything referencing "the signal", "signal magazine", or "sunday magazine"

The user may optionally steer the issue:

- "Run The Signal, but the Nintendo Direct happened this week so give that more space"
- "Run The Signal — Juve had a massive midweek result, make sure that gets proper coverage"
- "Run a Deep Dive on [topic]"
- "Run a Countdown for [event/trip]"
- "Run a Shelf Special — I just finished Malazan, what's next?"

## Quick Reference

| Format | Trigger | Template | Target length |
|---|---|---|---|
| Standard Weekly | Default / "Run The Signal" | `assets/weekly-template.html` | 6,000–8,000+ words, 20–30 pages |
| Deep Dive | "Run a Deep Dive on [topic]" | Adapted from weekly | No hard limit |
| The Long Read | "Run a Long Read on [theme]" | Adapted from weekly | 2,000–3,000 word essay |
| The Countdown | "Run a Countdown for [event]" | Adapted from weekly | Comprehensive event prep |
| The Season Review | "Run a Season Review for [subject]" | Adapted from weekly | Full retrospective |
| The Shelf Special | "Run a Shelf Special — [context]" | Adapted from weekly | 8–15 curated picks |

## Workflow

### Step 1: Read the editorial spec

Before generating any issue, read `references/editorial-spec.md` in its entirety. This is the single source of truth for all editorial rules, topic priorities, section structures, voice/tone, design system, and content standards. Never deviate from it unless the user explicitly instructs you to.

### Step 2: Determine the format

Unless the user specifies a format, use **Standard Weekly**. Special editions are always manual triggers:

- **Standard Weekly** — default. The full Sunday edition.
- **Deep Dive** — user says "Run a Deep Dive on [topic]."
- **The Long Read** — user says "Run a Long Read on [theme]."
- **The Countdown** — user says "Run a Countdown for [event/trip]."
- **The Season Review** — user says "Run a Season Review for [subject]."
- **The Shelf Special** — user says "Run a Shelf Special — [context]."

### Step 3: Research

Search the web for each topic area individually. Cover the previous 7 days ending today (or the date range the user specifies). Never rely on training data for current news.

**Mandatory searches for Standard Weekly** (at minimum):
1. World news and geopolitics (dominant running story)
2. Gaming news (Nintendo, Switch 2, indie, major releases)
3. Consumer tech, AI tools, Pixel/Xiaomi/e-readers
4. Steam Deck / GeForce Now news
5. LEGO news and releases
6. Juventus results, Serie A standings and wider league stories
7. Premier League results, standings, storylines
8. Champions League (when in season)
9. Film and TV — releases, streaming, reviews
10. Star Wars news (always — Lucasfilm always has something)
11. Synthwave / retrowave / electronic music (when relevant)
12. Books — fantasy, sci-fi, short fiction, community discussion
13. Kettlebell / fitness / running articles (StrongFirst, Dan John, etc.)
14. Podcasts — Football Weekly, The Bunker, What Went Wrong, History of Rome/Revolutions
15. Disney Parks / Efteling (when trip upcoming)
16. Northern Ireland local news (briefly)
17. Upcoming release dates (games, films, TV, books, LEGO, tech)
18. Reddit discussions in relevant subreddits
19. Audio drama recommendations (rotating)

For **image sourcing**: search for specific subjects (e.g., "Nintendo Switch 2 console", "Champions League match action", "Malazan book cover"). Include images via URLs with alt text and credit captions. Every major section needs at least one image.

For special editions, focus research on the specific topic while maintaining the editorial voice and visual design.

### Step 4: Read the HTML template

Read `assets/weekly-template.html`. Match the CSS, HTML structure, class names, colours, fonts, and component styles exactly. The template is the design reference — do not alter the visual design.

For special editions, adapt the template structure to suit the format (see editorial spec for each format's section list) while maintaining the same visual design system.

### Step 5: Generate the issue

Write the full HTML issue following:
- The section order and structure from the editorial spec
- The design and CSS from the template
- All content rules (sources, opinions, tone shifts, coverage requirements)
- Layout component rotation (don't use the same set every issue)
- Image sourcing (mandatory — every major section needs at least one)

**Key reminders:**
- The Touchline always leads with data (tables, results) before narrative
- The Release Radar must be comprehensive (15–20+ items across ALL categories: film, TV, games, LEGO, tech, books, music)
- Every substantial story should have an Angle box
- This Week in History appears every week (prefer ancient/medieval/classical)
- Opinions are mandatory — the reader wants a take, not neutrality
- Source every factual claim with linked references
- 3–5 Did You Know boxes scattered throughout — section-aware (adapt to dark sections)
- No "Other Signals" section — distribute to relevant "Also" lists
- Write like a magazine, not a personal assistant — personalisation is in the selection, not the prose
- Every issue must include 2–3 wildcard items the reader didn't ask for
- Serie A coverage extends beyond Juve — cover the whole league
- Music is NOT a fixed section — cover when relevant, skip when not
- Use dedicated sidebars ("Family Picks", "For the Kids") instead of sprinkling son-related notes through prose
- Include the JavaScript block from the template for progress bar and back-to-top functionality
- Navigator cards must anchor-link to sections (`href="#sectionId"` with matching `id` on each `.sec`)
- Top 1–2 nav cards use `.nav-card.lead` (two-column span with optional thumbnail)
- Use pull quotes, sidebar boxes, workout cards, year badges, and category dots as documented in the editorial spec
- Use `.hero-bleed` for at least one full-bleed hero image per issue, `.img-float-left` for book covers/album art
- Rotate layout components issue to issue — don't repeat the same set every week

### Step 6: Run the compliance checklist

Before delivering, read `references/compliance-checklist.md` and verify every item. Fix any failures before sharing. Common failures:
- Issue is too short (under 5,000 words)
- Missing images
- Coverage gaps (synthwave, Star Wars, books, kettlebells)
- Release Radar too thin
- Touchline doesn't lead with data
- Sections blend visually

### Step 7: Deliver

Share the HTML file with the user. Name it using the pattern `signal_weekly_YYYY-MM-DD.html` for standard issues, or `signal_[format]_YYYY-MM-DD.html` for special editions.

## State Tracking

When running multiple issues over time (especially via a scheduled cron), maintain a state file at `/home/user/workspace/signal-state.json` tracking:

```json
{
  "last_issue_number": 1,
  "last_issue_date": "2026-03-29",
  "last_issue_format": "weekly",
  "last_cover_lead": "World news topic",
  "topics_covered_recently": ["list of recent lead topics"]
}
```

This ensures:
- Issue numbering is continuous
- Lead topics vary week to week
- Coverage breadth is maintained over time

## Scheduling

When setting up a recurring schedule:
- Run every Sunday morning (the reader reads with coffee)
- Each run: read editorial spec → research → select format → read template → generate → run compliance checklist → deliver
- State file must be read at start and updated at end of each run
- Over a month, every interest cluster should get meaningful coverage at least twice

## Important Rules (always enforced)

- **No work/enterprise content** — unless it passes the "would they message a colleague on Monday?" test
- **No celebrity culture, Westminster politics, or royal family** — unless genuinely significant
- **No generic fitness advice** — only sourced content from real articles
- **No AI-generated images** — source real images via web search
- **No fabricated links** — every URL must be real and working
- **No "Other Signals" section** — distribute items into relevant section "Also" lists
- **No "what this means for you" framing** — write like a magazine, not a personal assistant
- **Always search the web** — never generate an issue from training data alone
- **Always include images** — this is a magazine, not a memo
- **Always include 2–3 wildcard items** — if the whole issue is predictable, it's too narrow
- **Data before narrative** in The Touchline — league tables and results first
- **Opinions are mandatory** — the reader wants editorial voice, not neutrality
- **Match the HTML template exactly** — never alter the visual design system
