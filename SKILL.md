---
name: the-signal
description: >-
  Generate issues of The Signal, a weekly personal magazine designed to be read
  on a Sunday morning with coffee. Use when asked to run, generate, create, or
  schedule The Signal, or when the user mentions "the signal", "signal magazine",
  "sunday magazine", "personal magazine", "run the signal", "deep dive",
  "countdown", "season review", "versus", "rewind", "starter kit",
  "blueprint", or "field guide" in the context of their personal weekly
  reading. Supports multiple issue formats: standard weekly, deep dive,
  countdown, season review, versus, rewind, starter kit, blueprint, and
  field guide. Includes HTML template, editorial
  spec, and a compliance checklist.
metadata:
  author: steven-mcdowell
  version: '7.3'
---

# The Signal

Generate issues of The Signal — a weekly personal magazine for Sunday morning reading.

## Model Selection

The Signal uses two model tiers depending on issue format:

| Format | Tier | Why |
|---|---|---|
| **Standard weekly** | Default (cost-effective) | Sonnet-tier models handle the rotating-section weekly reliably at a fraction of the cost |
| **Special editions** (Deep Dive, Countdown, Season Review, Versus, Rewind, Starter Kit, Blueprint, Field Guide) | **Highest-quality** | Lower-frequency, higher-stakes issues where depth, long-horizon coherence, opinionated voice, and strict instruction-following matter |

**How to apply the premium tier:** Once the format is committed in Step 2 and it is a special edition, load the `model-catalog` skill and read `text-models.md` to identify the current highest-quality text/agent model (the one recommended for "complex tasks", "asset creation", "website building"). Delegate the research + generation phase (Steps 3–5) to a `general_purpose` subagent using that model's identifier in the `model` parameter. Preload the `the-signal` skill into the subagent. Pass the committed format, the state-file snapshot, and any trigger context in the objective. The main loop still handles Steps 1–2 (scout/commit), Step 6 (inject), Steps 7–8 (gates), and Step 9 (deliver + state update).

This indirection means when Anthropic (or any provider) ships a better flagship, The Signal automatically picks it up without a skill edit — the catalog is the source of truth for "what's currently best".

If the user explicitly overrides (e.g. "run the weekly on the top model" or "keep this special on the default to save credits"), honour the override.

## Workflow

### 0. Pre-flight — verify skill files are intact
Before any other step, verify the skill has not been partially restored from an older snapshot. Run:

```bash
for f in references/editorial-spec.md references/sections.md references/compliance-checklist.md references/component-contracts.md references/visual-language.md assets/styles.css assets/weekly-template.html assets/script.js; do
  [ -f "/home/user/workspace/skills/user/the-signal/$f" ] || echo "MISSING: $f"
done
```

If any file prints MISSING, pull it from the canonical GitHub repo `stevenmcdowell89-hash/the-signal` before continuing:

```bash
gh api repos/stevenmcdowell89-hash/the-signal/contents/<path>?ref=main -H 'Accept: application/vnd.github.raw' > /home/user/workspace/skills/user/the-signal/<path>
```

Also spot-check: `grep -c Fraunces /home/user/workspace/skills/user/the-signal/assets/styles.css` — expect ≥ 3. If 0, the font swap has been reverted and must be re-applied before generation (see §6).

### 1. Read core spec + state file
Read `references/editorial-spec.md` (the core spec — editorial rules, reader profile, key rules, issue formats, auto-triggers, search checklist, component reference, visual design). Also read the state file at `/home/user/workspace/signal-state.json`.

**Do NOT read yet:** `references/sections.md` (section details — read later for selected sections only), `references/compliance-checklist.md` (read at compliance step), `assets/styles.css` and `assets/script.js` (injected by build script, never read into context), `assets/weekly-template.html` (read at generation step).

### 2. Scout for triggers (before any full research)
A quick, cheap check to decide the issue format before committing to a full research pass.

If the reader has manually requested a specific format, use that and skip to step 4.

Otherwise, run **only these targeted checks** (2-4 quick searches total):
1. **Priority 1 — Calendar-fixed:** Check dates against state file. Last Sunday of June/December? Trip in `upcoming_trips` ~6 weeks away (Field Guide) or 2-3 weeks away (Countdown)?
2. **Priority 2 — Event-driven:** 2-3 quick searches for season endings, tournament conclusions, major launches.
3. **Priority 3 — Safety net:** Only if `last_special_date` is 5+ weeks ago and no P1/P2 fired.

Evaluate guardrails. **Commit to a format now.**

### 3. Select rotating sections + read section reference
For standard weekly: identify which rotating sections are most overdue from state file. Select 2-3. Check if Down the Rabbit Hole sidebar is due.

Now read `references/sections.md` in full. It contains all section descriptions, content rules, and rotating search groups. It's small enough to read entirely — don't try to read selectively.

For special editions: still read sections.md — you'll need the fixed section descriptions for the Meanwhile section.

### 4. Research
**For standard weekly:** Search for each **core group** from the Search Checklist in the core spec. Then search the **rotating groups** from sections.md only for selected sections. For catch-up sections (Shelf, etc.), research covers the full gap since last appearance.

**For special editions:** Research the topic in depth. Lighter pass across core news groups for the "Meanwhile..." section.

Never rely on training data. Source images for every major section.

### 5. Read template + visual language + generate
Read, in this order:
1. `assets/weekly-template.html` — HTML structure and available component patterns.
2. **`references/visual-language.md` — the aesthetic layer. Read in full.** This describes type, palette, chrome, motion, and component vocabulary. Apply it to every section. Sections mentioned in §9 of the visual language doc have default component mappings — use them unless content calls for an override.

**⛔ Hard rule on CSS and JS:** Do NOT read styles.css or script.js. Do NOT write any `<style>` tag or any `@font-face`, `:root {}`, or inline CSS declarations in the HTML yourself. Do NOT include a `<link>` to Google Fonts — the injected CSS already imports the correct fonts. The only markers you place are:
- `<!-- INJECT:CSS -->` on its own line inside `<head>` (nothing else between `<head>` and this marker except `<meta>` + `<title>`)
- `<!-- INJECT:JS -->` on its own line immediately before `</body>`

**Why:** any `<style>` tag you write will paint a conflicting cascade on top of the injected canonical styles. Every font family, every accent colour, every background token must come from `assets/styles.css` — not from your memory. If a section needs a style that styles.css doesn't have, STOP and tell the user — do not invent one.

Write the full HTML issue. Key reminders:
- **Apply the visual language.** Two fonts only (Fraunces + Geist). Ember accent default. Inline italic accent via `<em>` — no `.hl` bars. Per-section accent shifts via `data-accent` where content warrants. ≥ 4 distinct component treatments from visual-language §4. No component appears more than twice in the issue. Alternate dark and paper grounds across consecutive sections. ≥ 2 continuous scroll-linked motion moves from visual-language §5.1. Accent ≤ 8% of any on-screen area. Zero roman numerals as section markers, zero “Dispatch” / “Chapter” vocabulary.
- Rotate layout components — no two consecutive sections use the same pattern
- Use 8–12 different component types
- Every major section needs at least one image
- Opinions mandatory
- **The reader profile must be invisible in the prose.** Write as a general-interest magazine journalist.
- Only include selected rotating sections — Navigator adapts accordingly

### 6. Inject CSS/JS
Run `bash /home/user/workspace/skills/user/the-signal/scripts/inject-assets.sh <html-file>` to replace the placeholder comments with the full CSS and JS from the assets directory.

**Post-inject verification** — run these four greps on the output file. Every one must hit its target:

```bash
F=<html-file>
grep -c "Fraunces" "$F"                      # expect ≥ 3
grep -c "Geist" "$F"                         # expect ≥ 10
grep -c -E "Cormorant|DM Sans|JetBrains Mono|Instrument Serif" "$F"   # expect 0
grep -c "d2411e" "$F"                        # expect ≥ 1 (ember hex)
grep -c "<style>" "$F"                       # expect exactly 1
```

If `<style>` count is > 1, the agent wrote its own style block in violation of §5 — go back and strip it. If old-font count > 0, styles.css has drifted or an inline block slipped in — fix before proceeding.

### 7. GATE 1 — Hard fail scan
Read `references/compliance-checklist.md`. Run **Gate 1** — a mechanical text scan of the output. Check 1A (reader-profile leaks), 1B (fabrication), 1C (staleness), 1D (links). **Fix every failure before proceeding.** This is the most important step.

### 8. GATE 2 — Editorial & visual quality
Run through every Gate 2 item in the compliance checklist. Fix any failures.

### 9. Deliver
Save as `signal_weekly_YYYY-MM-DD.html` (or `signal_[format]_YYYY-MM-DD.html`). Push to GitHub Pages repository if set up.

## State Tracking

For recurring runs, maintain `/home/user/workspace/signal-state.json`:

```json
{
  "last_issue_number": 1,
  "last_issue_date": "2026-03-29",
  "last_issue_format": "weekly",
  "last_cover_lead": "World news topic",
  "topics_covered_recently": [],
  "rotating_sections": {
    "the_shelf": { "last_appeared": null, "cadence_weeks": [2, 3] },
    "this_week_in_history": { "last_appeared": null, "cadence_weeks": [2, 3] },
    "the_pantry": { "last_appeared": null, "cadence_weeks": [2, 3] },
    "the_workshop": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_toolkit": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_ledger": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_long_game": { "last_appeared": null, "cadence_weeks": [4, 4] },
    "the_wallet": { "last_appeared": null, "cadence_weeks": [3, 4] },
    "the_itinerary": { "last_appeared": null, "cadence_weeks": [3, 4] }
  },
  "down_the_rabbit_hole": { "last_appeared": null, "cadence_weeks": [3, 4] },
  "training_phase": {
    "current_block": "Block 1: Race Prep + Fat Loss",
    "block_dates": "April 4 - May 3",
    "next_block": "Block 2: Fat Loss + Hypertrophy (May 4 - June 30)",
    "key_event": "10k race May 3",
    "focus": "concurrent training (4 lifts + 3 runs/week), hypertrophy in deficit, race prep",
    "post_june30": "hypertrophy at maintenance/surplus"
  },
  "ongoing_stories": [
    { "topic": "Iran War", "section": "world", "weeks_as_lead": 4, "weeks_as_ongoing": 0, "last_status": "lead" }
  ],
  "upcoming_trips": [
    {
      "destination": "Efteling + Beekse Bergen, Netherlands",
      "start": "2026-06-30",
      "end": "2026-07-07",
      "legs": [
        { "place": "Efteling", "start": "2026-06-30", "end": "2026-07-02", "nights": 2 },
        { "place": "Beekse Bergen Safari Resort", "start": "2026-07-02", "end": "2026-07-07", "nights": 5 }
      ],
      "field_guide_due": true,
      "countdown_due": true
    }
  ],
  "last_special_date": null,
  "last_special_format": null,
  "consecutive_specials_count": 0,
  "editorial_picks_used": []
}
```

When generating an issue:
1. Read state file at start
2. Evaluate auto-trigger logic (Priority 1 → 2 → 3) and guardrails
3. If standard weekly: select 2-3 rotating sections based on cadence priority (most overdue first)
4. Research accordingly (full groups for weekly, topic + light news pass for specials)
5. After generation, update:
   - `last_issue_date`, `last_issue_number`, `last_issue_format`
   - `last_appeared` for each rotating section that appeared (standard weekly only)
   - `down_the_rabbit_hole.last_appeared` (if it appeared as a sidebar)
   - `last_special_date` and `last_special_format` (if special edition)
   - `consecutive_specials_count` (increment if special, reset to 0 if weekly)
   - `editorial_picks_used` (append topic if Priority 3 was used)
   - `ongoing_stories` — update weeks_as_lead/weeks_as_ongoing counts, promote/demote/drop stories as needed, add new entries if a topic has now led for 2 consecutive weeks
   - `training_phase` — update if the current date has crossed a block boundary (Block 1 ends May 3, Block 2 ends June 30, post-holiday starts July)

## Scheduling

Run every Sunday morning. Each run follows the full workflow above. State file read at start, updated at end. Over a month, every interest cluster gets meaningful coverage at least twice.
