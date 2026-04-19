# The Signal — Compliance Checklist

Two gates. Gate 1 is a mechanical text scan — run it BEFORE reading Gate 2. If Gate 1 fails, fix before proceeding. Gate 2 is editorial and visual quality.

---

## GATE 1 — Hard Fails (scan the output text)

These are the most common and most damaging errors. Each one requires a literal scan of the generated HTML text. Do not skip this gate. Do not skim it. Run each check deliberately.

### 1A. Reader-Profile Leaks

Search the full text for ANY phrase that reveals the magazine knows who the reader is. The reader profile exists to guide research and selection — it must be invisible in the prose.

**Search for these patterns and remove/rewrite every match:**
- The reader's specific devices by name: "Xiaomi", "Garmin", "Todoist" (unless in a general product review context where any magazine would name them)
- Direct reader address: "your tablet", "your watch", "your son", "this matters to you", "you'll appreciate", "worth it for you"
- Profile callbacks: "as a [interest] fan", "for someone who [trait]", "since you're into [topic]"
- Selection justifications: "You're deep into Malazan", "Given your interest in", "Since you follow Serie A" — the selection already did this work
- Invisible-rule announcements: "no spoilers in sight", "spoiler-free" (the no-spoilers rule is absolute but never mentioned)
- "It's not X, it's Y" defensive pattern: "It's not bland meal prep food", "This isn't just another listicle"

**The test:** would this sentence make sense in a magazine with 100,000 readers? If it would only make sense written for one person, rewrite it.

**Good examples to aim for:** "If you find high fantasy world-building exhausting and want something with tighter scope" / "For anyone watching the Serie A title race" / "If you're gaming via cloud streaming on a tablet"

### 1B. Fabrication

- [ ] **No fabricated results.** "Drew 7-0" is not a thing. Every scoreline must be verified. If unconfirmed, don't include it.
- [ ] **No fabricated podcast/article/video content.** Do not invent what a specific episode discussed. If you can't verify it, link without a summary or omit.
- [ ] **No fabricated URLs.** Every link must be real.
- [ ] **No fabricated media.** Every TV show, film, game, book, podcast must be confirmed as real and current. No implying new episodes for ended shows. No miscategorising (game listed as a Netflix show).

### 1C. Staleness

- [ ] **Every news item is from the current week (7 days).** A Champions League exit from 5 weeks ago is not this week's story. A Carabao Cup final from a fortnight ago is not this week's story.
- [ ] **No forced favourite-team content.** If Juventus haven't played this week, they appear in the league table and that's it. Don't dredge up old results to fill space. Same for any team or topic from the reader profile.
- [ ] **Fixture dates verified.** Serie A has Sunday and Monday fixtures. Check every match date. If a match hasn't been played yet, say so — don't report a result that doesn't exist.
- [ ] **Ongoing stories in tracker, not headline.** Check `ongoing_stories` in state file. Any story that has led for 2+ consecutive weeks must be in an Ongoing tracker box, not leading the section again with a new angle.

### 1D. Links

- [ ] **Every substantial item has at least one outbound link.** No dead ends.
- [ ] **Links go to the specific item**, not a category page. The recipe, not "all chicken recipes." The episode, not the show page.
- [ ] **History items link to Wikipedia** (preferred) for every featured event and every "Also" one-liner.

---

## GATE 2 — Editorial & Visual Quality

Only proceed here after Gate 1 passes clean.

### Coverage
- [ ] Word count meets format target (see editorial spec Issue Formats)
- [ ] Every major section has at least one relevant image
- [ ] Touchline: lead story is most compelling sport of the week. Serie A ≥ PL depth on normal domestic weeks. Full table (top 10 + relegation zone). Coverage beyond Juve. Doesn't exceed ~30% of issue.
- [ ] Release Radar: 15-20+ items across ALL categories, chronological within sub-sections
- [ ] Star Wars mentioned somewhere
- [ ] No coverage gaps in fixed sections
- [ ] Issue has news AND features/evergreen — not purely news
- [ ] On the Radar: 8-10 items, no overlap with Release Radar, specific and non-patronising

### Rotating Sections
- [ ] 2-3 rotating sections selected from state file cadence priority
- [ ] Only selected sections researched — no wasted research
- [ ] Catch-up rule respected (Shelf, etc. — full gap since last appearance)
- [ ] Navigator only shows sections present in this issue
- [ ] Down the Rabbit Hole included as sidebar if due (3-4 weeks)

### Ongoing Stories
- [ ] Ongoing trackers are factual, not editorial — situation report tone
- [ ] Ongoing trackers have proper space — scaled to the week's developments
- [ ] New lead story is genuinely new — not a rehashed angle on the ongoing story
- [ ] State file updated with ongoing_stories changes

### Structure
- [ ] Touchline leads with data (tables, scores) before narrative
- [ ] Foreword: 50-80 words, one thread
- [ ] LEGO in Pixel & Byte, not Screen & Sound
- [ ] History prefers pre-WW2; images match the historical event (no reusing images from other sections)
- [ ] Music only when relevant within The Shelf's rotation; music releases still in Release Radar when Shelf absent
- [ ] Session: only sourced content, or omitted entirely
- [ ] Podcast recs are episode-specific: title, date, reason — verified content only
- [ ] The Itinerary owns all travel/parks/NI content when present; On the Radar one-liners when absent

### Voice
- [ ] Opinions present throughout — not neutral press releases
- [ ] Football reads as editorial, not match reports
- [ ] No spoilers — ever
- [ ] Writes like a magazine journalist, not a personal assistant
- [ ] Each taste-based section (Shelf, Session, Screen & Sound) writes as a general reviewer — profile drives selection, not prose

### Visual Variety
- [ ] 10+ different component types
- [ ] No two consecutive sections use the same layout pattern
- [ ] No 3+ screen-heights of unbroken prose
- [ ] At least 3 pull quotes, 2 big-number callouts, 3-5 DYK boxes
- [ ] Entry pattern rotation (`.entry-stat`, `.entry-quote`, `.entry-bullets`, `.entry-question`, prose)
- [ ] 1-2 breather bands between dense sections
- [ ] At least 1 compare panel or sidebar-float
- [ ] Read-next connectors between at least 3 major sections
- [ ] Maps included when relevant (history, world news, travel) — sourced from real sources, not AI-generated

### Visual Language (from `references/visual-language.md`)
These are the self-check items from visual-language §10. Every “no” is a fix-before-ship.
- [ ] **Two fonts only** — Fraunces (display/serif) and Geist (sans). Zero Cormorant, DM Sans, JetBrains Mono, Inter, Instrument Serif in the output. `grep -c -E "Cormorant|DM Sans|JetBrains|Instrument Serif" <file>` returns 0.
- [ ] **Ember accent** (`#d2411e`) is the primary accent. No `--rose` leaks on a weekly. `grep -c "var(--rose)" <file>` ≤ 2 (allowed only as deliberate override, not default).
- [ ] ≥ 4 distinct component treatments from visual-language §4 appear in the issue
- [ ] No single component appears more than twice (guards against bridger-sameness)
- [ ] Dark and paper grounds alternate across consecutive sections — never two consecutive on the same ground
- [ ] Every section meets its minimum density from visual-language §6.1
- [ ] Every list-item carries ≥ 1 sentence of editorial verdict
- [ ] ≥ 2 continuous scroll-linked motion moves from visual-language §5.1 are present (parallax on hero, section colour flood, sticky image with scrolling captions, count-up numerals, colour-adaptive nav, footer-rising-card, image progressive reveal, cover photo scale-down)
- [ ] Accent occupies ≤ ~8% of any on-screen position (no decorative accent borders on sidebars, rails, rules)
- [ ] Inline italic accent via `<em>` in body — no `.hl` highlight bars. `grep -c "class=\"hl\"" <file>` returns 0.
- [ ] Zero roman numerals as section markers. Zero “Dispatch” / “Chapter” vocabulary. Zero preloader pun text.
- [ ] Dispatch seal appears only on cover + colophon (not every section)
- [ ] Masthead has Sunday timestamp (`06:40`), issue number, date in MMXXVI form
- [ ] Feels right at both 1194×834 (tablet landscape) and 834×1194 (tablet portrait)

### Wildcards & Synthesis
- [ ] 2-3 items the reader didn't ask for
- [ ] 2 of 8 Long Shelf items are wildcards
- [ ] Cross-cluster connections present where natural

### Special Editions (when applicable)
- [ ] "Meanwhile..." section present before Footer, 12-18 linked items
- [ ] Guardrails respected: no 3+ consecutive specials, manual triggers override
- [ ] Trip-aware rules: Rewinds deferred near trips, Field Guide before Countdown, Season Reviews patient
- [ ] State file updated: `last_special_date`, `last_special_format`, `consecutive_specials_count`

### Field Guide (when applicable)
- [ ] Reference-first, scannable on a phone
- [ ] Every meal slot covered with 3-5+ options
- [ ] Full spectrum: fine dining → comfort food fallbacks
- [ ] Theming/experience noted, kid-friendly callouts, booking notes
- [ ] Multi-venue: primary gets full treatment, secondary gets practical section
- [ ] Research depth: official menus, TripAdvisor, blogs, Reddit, YouTube all consulted

### Technical
- [ ] **CSS/JS injected:** verify the output contains `<style>` and `<script>` tags (not `<!-- INJECT:CSS -->` placeholders). If placeholders remain, run `scripts/inject-assets.sh` again.
- [ ] **No `.reveal` on sections or containers.** Search for `<section.*reveal` and for `reveal` on `split-60-40`, `split-40-60`, `dual-col`, `also-cards`. `.reveal` may only appear on small leaf elements (individual images, angles, pull-quotes, cards). Sections and layout containers must always be visible — `reveal` with `opacity:0` on large elements causes blank pages on mobile.
- [ ] Navigator cards anchor-link to sections with matching `id` attributes
- [ ] Progress bar and back-to-top button functional
- [ ] No rendering artefacts: no stray numbers, no garbled sections, no broken layouts
