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
  version: '3.0'
---

# The Signal

Generate issues of The Signal — a weekly personal magazine for Sunday morning reading.

## Workflow

### 1. Read the editorial spec
Read `references/editorial-spec.md` in full. It is the single source of truth for editorial rules, reader profile, section structures, voice, design system, content standards, and search requirements.

### 2. Determine the format
Default is **Standard Weekly**. Special editions are always manual triggers — see the editorial spec for all six formats and their section lists.

### 3. Research
Search the web for each topic group from the **Search Checklist** in the editorial spec. Cover the previous 7 days. Never rely on training data. Source images for every major section.

### 4. Read the template files
- Read `assets/weekly-template.html` for the HTML structure and available components.
- Read `assets/styles.css` for the full CSS. Paste it into a `<style>` tag in the generated issue.
- Read `assets/script.js` for the JS. Paste it into a `<script>` tag before `</body>`.

Match class names, colours, fonts, and component patterns exactly. For special editions, adapt the section structure while keeping the same design system.

### 5. Generate the issue
Write the full HTML issue following the editorial spec for content and the template for structure. Key reminders:
- Rotate layout components — no two consecutive sections should use the same pattern
- Use 8–12 different component types per standard issue
- Every major section needs at least one image
- Opinions are mandatory — the reader wants a take, not neutrality

### 6. Run the compliance checklist
Read `references/compliance-checklist.md` and verify every item. Fix any failures before sharing.

### 7. Deliver
Share the HTML file. Name: `signal_weekly_YYYY-MM-DD.html` (or `signal_[format]_YYYY-MM-DD.html` for special editions). If the user has a GitHub Pages setup, also push to the repository.

## State Tracking

For recurring runs, maintain `/home/user/workspace/signal-state.json`:

```json
{
  "last_issue_number": 1,
  "last_issue_date": "2026-03-29",
  "last_issue_format": "weekly",
  "last_cover_lead": "World news topic",
  "topics_covered_recently": []
}
```

## Scheduling

Run every Sunday morning. Each run follows the full workflow above. State file read at start, updated at end. Over a month, every interest cluster gets meaningful coverage at least twice.
