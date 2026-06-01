# The Signal — Compliance Checklist

Two gates. Gate 1 is a mechanical text scan — run it BEFORE reading Gate 2. If Gate 1 fails, fix before proceeding. Gate 2 is editorial and visual quality.

**v8.11.0 update:** Gate 1 now runs **per chapter during the pipeline** (Phase 7), not just at end of run. Each writer self-audits via `references/pre-flight.md` before submission. The main loop then grep-scans every chapter against this gate before stitching. Most regressions are caught upstream by pre-flight; this file catches what slipped through.

**v8.13.4 update — what is now MECHANIZED vs what remains MANUAL.**
- **Mechanized** (run by the orchestrator as scripts, exit-code gated):
  - `scripts/validate-chapter-plan.py` — Phase 4 plan validity.
  - `scripts/stitch-issue.sh` — Phase 6 holiday-activation rewrite + banned-vocabulary scan (`sp-*` tokens on holiday formats) + positive `.hol-half` presence.
  - `scripts/check-release-dates.sh` — Phase 7.5 date/release-fact surface.
  - `scripts/validate-issue.py` — Phase 7.6 structural well-formedness, banned literal placeholders in DOM, holiday-identity body activation (real `<body>` after `</head>`, not example in comment), required holiday components (`.hol-masthead` / `.hol-cover` / `.hol-half`), multi-venue body flag + two distinct `data-venue` values, and image-URL HEAD-checks.
- **Manual** (still requires a reading pass — no script can judge prose):
  - **1A Reader-profile leaks** below.
  - **1B Fabrication** of facts, dates, quotes, attribution (date register is partially mechanized via `check-release-dates.sh`; the agent still walks the surface).
  - **1C Staleness** (rotating-section topics not in spec, ongoing-stories continuity).
  - **1D Link health** (only structural URL reachability is mechanized; relevance is not).
  - **1E Markup contract** (partially mechanized via the stitch-time grep gate; spot-check anything novel).
  - **1F Image-caption integrity** (whether the caption matches the image is still a human/agent judgement).

If a check in this file is duplicated by a mechanized gate, the mechanized gate is authoritative and the prose here is a reading aid only.

Gate 1 has six sections: 1A reader-profile leaks, 1B fabrication, 1C staleness, 1D links, **1E markup contract compliance** (special editions only), **1F image-caption integrity**. Sections 1E and 1F are bash grep recipes — run them, every command must return the expected value before proceeding.

---

## GATE 1 — Hard Fails (scan the output text)

These are the most common and most damaging errors. Each one requires a literal scan of the generated HTML text. Do not skip this gate. Do not skim it. Run each check deliberately.

### 1A. Reader-Profile Leaks

Search the full text for ANY phrase that reveals the magazine knows who the reader is. The reader profile exists to guide research and selection — it must be invisible in the prose.

**Search for these patterns and remove/rewrite every match:**
- The reader's specific devices by name: "Xiaomi", "Garmin", "Todoist" (unless in a general product review context where any magazine would name them)
- Direct reader address: "your tablet", "your watch", "your son", "your partner", "your 10-year-old", "this matters to you", "you'll appreciate", "worth it for you", "you'll love", "you and your partner"
- Profile callbacks: "as a [interest] fan", "for someone who [trait]", "since you're into [topic]", "as a Malazan reader", "as a Juventus fan", "as someone travelling by train"
- Selection justifications: "You're deep into Malazan", "Given your interest in", "Since you follow Serie A" — the selection already did this work
- Trip-specials specific leaks (Field Guide / Countdown): "perfect for your 10-year-old", "your son will love", "take the kids", "one for each of you", "you and your partner will…". Audience-fit information must be stated as **venue character** ("family-friendly", "adult-oriented evening spot", "walk-in welcome") — never as reader instruction. The reader applies it to their own party.
- Invisible-rule announcements: "no spoilers in sight", "spoiler-free" (the no-spoilers rule is absolute but never mentioned)
- "It's not X, it's Y" defensive pattern: "It's not bland meal prep food", "This isn't just another listicle"

**The test:** would this sentence make sense in a magazine with 100,000 readers? If it would only make sense written for one person, rewrite it.

**Good examples to aim for:** "If you find high fantasy world-building exhausting and want something with tighter scope" / "For anyone watching the Serie A title race" / "If you're gaming via cloud streaming on a tablet"

### 1B. Fabrication

- [ ] **No fabricated results.** "Drew 7-0" is not a thing. Every scoreline must be verified. If unconfirmed, don't include it.
- [ ] **League tables are internally consistent.** If you update a team's points from a weekend result, re-sort the entire table by points. A team with more points than the team above them is wrong. Do not patch individual results onto a stale table -- either use the fully updated table from a single authoritative source, or rebuild the standings from scratch after applying all results.
- [ ] **No fabricated podcast/article/video content.** Do not invent what a specific episode discussed. If you can't verify it, link without a summary or omit.
- [ ] **No fabricated URLs.** Every link must be real.
- [ ] **No fabricated media.** Every TV show, film, game, book, podcast must be confirmed as real and current. No implying new episodes for ended shows. No miscategorising (game listed as a Netflix show).
- [ ] **HARD CHECK -- Verify the year on every media premiere.** When a feature claims a show "premiered this week" or "dropped on [date]", search the web for the actual premiere year. The trap: dates without years feel current. Always confirm the FULL date (day, month, year) for any premiere, launch, release, or anniversary before featuring it.
- [ ] **HARD CHECK -- No result/fixture that hasn't happened yet (v8.28, run-date-anchored v8.29).** Any stated sports result, score, qualifying outcome, or league standing must have ACTUALLY OCCURRED by the **run date** (when facts were knowable — not merely by the issue's cover date; an event in the gap between run and cover date is still in the future at research time) and trace to a source reporting it as happened — not a preview, not a prior-year result pulled forward. The Monaco "Norris on pole" failure (qualifying a week away, asserted as fact) and the State-of-Play showcase written as "delivered" before it aired are this class. Every load-bearing fact carries a `status` tag the researcher set in the bundle: a `status:"upcoming"` fact is written as forthcoming, never as a result. And every load-bearing fact must trace to the research bundle (RT-22) — the prose adds no facts the research didn't supply.
- [ ] **HARD CHECK -- Named commentator carries a real quote (v8.29).** Voicing a borrowed angle as our own needs no attribution, but the moment a person is *named* (or the take is hung on them), the bundle must carry them as a `type:"opinion"` fact with a real `quote`. A name with no backing quote in the bundle is fabricated attribution — cut the name or voice the angle unattributed.
- [ ] **Locked Star Wars / Disney+ dates (tripwire register).** The agent has repeatedly fabricated "upcoming" Star Wars releases that already aired. The following are CONFIRMED and LOCKED — any mention must use these dates or no date, never relative phrasing like "last May" / "this summer" / "coming next month":
  - **Andor S1:** premiered 21 September 2022, ended 23 November 2022.
  - **Andor S2:** premiered 22 April 2025, ended 13 May 2025 (12 episodes in four three-episode weekly arcs). Series COMPLETE — no Season 3.
  - **Tales of the Jedi:** released 26 October 2022 (six shorts).
  - **Tales of the Empire:** released 4 May 2024 (six shorts).
  - **Tales of the Underworld:** released 4 May 2025 (six shorts, all on day one). Already aired — do NOT frame as upcoming.
  - **Skeleton Crew:** premiered 3 December 2024, ended 14 January 2025. Series COMPLETE.
  - **The Acolyte:** premiered 4 June 2024, cancelled August 2024.
  - **The Mandalorian and Grogu (film):** in cinemas 22 May 2026 (this IS upcoming as of mid-2026).
  - **Maul: Shadow Lord:** ten-episode run February–May 2026; finale 4 May 2026.
  Confirmed prior fabrications: issue #6 framed Andor S2 as current; issue #8 said Andor S2 ended "last September" and framed Tales of the Underworld as a "4 June" upcoming release. Star Wars / Disney+ release framing is a known fabrication trap.
- [ ] **Date-without-year ban (general rule).** Any sentence that uses a relative date for a media release — "lands on Disney+ on 4 June", "comes out next month", "hits cinemas 22 May", "this summer" — must include the YEAR explicitly OR be verified against current-year reality before publication. The trap pattern: the agent reads about a release dated "4 June" in a 2025 article and copies it forward as if it were 2026. Always answer two questions for any media-release date: (1) what year is the source from, and (2) what year is the release? If the answer to (2) is in the past, the item is either historical context (treat as such) or wrong (cut it).

### 1C. Staleness

- [ ] **Every news item is from the current week (7 days).** A Champions League exit from 5 weeks ago is not this week's story. A Carabao Cup final from a fortnight ago is not this week's story.
- [ ] **No forced favourite-team content.** If Juventus haven't played this week, they appear in the league table and that's it. Don't dredge up old results to fill space. Same for any team or topic from the reader profile.
- [ ] **No repeat topics in successive issues.** Check `topics_covered_recently` in the state file. If a Session topic or feature angle has been covered in the last 2-3 issues, pick a different angle this week. Variety matters: even a great topic gets stale at 3 weeks running. Specifically for The Session: do not run the same training topic (taper, recovery, periodisation, etc.) two weeks in a row -- rotate the angle.
- [ ] **Fixture dates verified.** Serie A has Sunday and Monday fixtures. Check every match date. If a match hasn't been played yet, say so — don't report a result that doesn't exist.
- [ ] **Ongoing stories in tracker, not headline.** Check `ongoing_stories` in state file. Any story that has led for 2+ consecutive weeks must be in an Ongoing tracker box, not leading the section again with a new angle.

### 1D. Links

- [ ] **Every substantial item has at least one outbound link.** No dead ends.
- [ ] **Links go to the specific item**, not a category page. The recipe, not "all chicken recipes." The episode, not the show page.
- [ ] **History items link to Wikipedia** (preferred) for every featured event and every "Also" one-liner.

### 1E. Markup contract compliance (special editions only)

The special-edition CSS targets specific tag + class combinations. Banned alternates bypass the readability locks and produce contrast bugs (bone-on-cream cards, ink-on-dark bands). Run every command below against the rendered HTML before delivery; **every command must return `0`**. Any non-zero result is a hard fail — fix the markup before proceeding to Gate 2.

Replace `FILE` with the issue's HTML path.

```bash
# Pullquote (huge) — must be <blockquote>, never <div>
grep -c '<div class="sp-pullquote-huge"' FILE     # expect 0
grep -c 'class="sp-pq-quote"' FILE                # expect 0  (use plain <p>)
grep -c 'class="sp-pq-attrib"' FILE               # expect 0  (use <cite>)

# Marginalia — label must be <span class="sp-marginalia-label">
grep -c 'class="sp-marg-kicker"' FILE             # expect 0
grep -c 'class="sp-marg-label"' FILE              # expect 0
grep -c '<div class="sp-marginalia"' FILE         # expect 0  (use <aside>)

# Pull-break — must be <div class="sp-pull-break">, wrapped in .sp-pull-break-wrap
grep -c '<blockquote class="sp-pull-break"' FILE  # expect 0
grep -c '<h[1-6][^>]*class="sp-pull"' FILE        # expect 0  (use <p class="sp-pull">)

# Brief sidebar — must use <h4>, not <h2>/<h3>
grep -cE '<h[123][^>]*class="sp-brief-h"' FILE    # expect 0
grep -c '<aside class="sp-brief"' FILE            # expect 0  (use <div>)

# Hero quote — attribution must be <p class="sp-hero-quote-at">
grep -c '<blockquote class="sp-hero-quote"' FILE  # expect 0

# Chapter chrome — every chrome must contain the .sp-hair separator
# (count of chromes minus count of hairs must be 0)
chrome=$(grep -c 'class="sp-chapter-chrome"' FILE)
hair=$(grep -c 'class="sp-hair"' FILE)
[ "$chrome" -eq "$hair" ] || echo "FAIL: $chrome chromes, $hair hairs"

# Holiday Identity (v8.12) — Countdown + Field Guide only
# These checks fire when data-special="countdown" or "field-guide".
# Determine format:
format=$(grep -oE 'data-special="[a-z-]+"' FILE | head -1 | sed 's/.*"\(.*\)"/\1/')

if [ "$format" = "countdown" ] || [ "$format" = "field-guide" ]; then
  # No default-chrome markup on holiday issues
  grep -cE 'class="sp-chapter-gate|class="sp-spread|class="sp-pull-break|class="sp-marginalia|class="sp-brief|class="sp-dash|class="sp-chapter-chrome|class="unmissables|class="unmissable[ "]' FILE
  # expect 0

  # At least one .hol-half present
  hol_half=$(grep -c 'class="hol-half ' FILE)
  [ "$hol_half" -ge 1 ] || echo "FAIL: holiday issue has no .hol-half"

  # Cover present
  grep -c 'class="hol-cover"' FILE   # expect ≥1

  # Closing meanwhile present
  grep -c 'class="hol-meanwhile"' FILE   # expect ≥1

  # Transit count rule — multi-venue (data-multi-venue="true") = 1 transit;
  # single-venue = 0. Either way, never 2+.
  transit=$(grep -c 'class="hol-transit"' FILE)
  multi=$(grep -c 'data-multi-venue="true"' FILE)
  if [ "$transit" -gt 1 ]; then echo "FAIL: >1 .hol-transit"; fi
  if [ "$multi" -ge 1 ] && [ "$transit" -ne 1 ]; then echo "FAIL: multi-venue issue must have exactly 1 .hol-transit"; fi
  if [ "$multi" -eq 0 ] && [ "$transit" -ne 0 ]; then echo "FAIL: single-venue issue must have 0 .hol-transit"; fi

  # No coral on holiday issues (whole-issue ban, not just inline-style ban)
  grep -cE 'E8384F|--sp-accent-primary' FILE  # expect 0
fi
```

For each row in the canonical markup table (editorial-spec.md §Markup contracts), the corresponding banned alternate column maps to one or more of the greps above. If you add a new editorial component, you must add its banned-alternates greps here in the same commit.

**Why this is Gate 1, not Gate 2:** banned markup is mechanically detectable from the text alone, and it is the single largest historical source of contrast bugs (one v8.10.x issue had eight marginalia, six pull-breaks, and five pullquotes — every one rendered with the wrong contrast because the markup was wrong). It belongs with fabrication and staleness in the hard-fail tier.

### 1F. Image-caption integrity (mechanical scan)

Three image bugs have shipped in past issues; each is mechanically scannable. **Every command must return the expected value below.** Any failure is a hard fail.

Replace `FILE` with the issue's HTML path.

```bash
# 1. No duplicate <img src="..."> URLs in one issue.
# Re-using the same image with two different captions = at least one caption is lying.
grep -oE '<img[^>]+src="[^"]+"' FILE | sed -E 's/.*src="([^"]+)".*/\1/' | sort | uniq -d
# expect: empty output

# 2. Every <img> has a caption nearby.
# Count <img> tags vs <figcaption> tags. The ratio must be roughly 1:1
# (exact counts vary by template, but every major image must be captioned).
imgs=$(grep -c '<img' FILE)
caps=$(grep -c '<figcaption' FILE)
echo "$imgs images, $caps captions"
# expect: caps >= imgs * 0.85   (allow up to 15% for pure decorative images)

# 3. YouTube thumbnail subjects — list them so a human can verify.
# The script can't watch the videos; the editor must, before shipping.
grep -oE 'i\.ytimg\.com/vi/[A-Za-z0-9_-]+' FILE | sort -u
# For each <id> listed, open https://youtube.com/watch?v=<id> and confirm the
# video title matches the captioned subject. If you cannot verify, REMOVE the image.

# 4. Wikimedia filename consistency — list filenames + nearby captions for human review.
grep -oE 'upload\.wikimedia\.org/[^"]+\.(jpg|JPG|jpeg|png|svg|webp|gif)' FILE | sort -u
# For each filename, confirm it depicts the captioned subject. The filename is
# usually a place + number (`Sirmione_007.JPG`); if the caption says a different
# place, it's fabrication. Cut or replace.

# 5. Every image must have a credit line in its caption.
# Captions without 'Photo:', 'Still:', 'Credit:', 'Image:', 'via', or 'CC' are uncredited.
awk '/<figcaption/,/<\/figcaption>/' FILE | grep -v -E 'Photo:|Still:|Credit:|Image:|via |CC[- ]BY|press kit|Wikimedia' | grep -c '<figcaption'
# expect: 0 (every figcaption matches one of the credit patterns)
```

**Why this is Gate 1, not Gate 2:** image-caption mismatch is fabrication of visual claims, parallel to fabrication of factual claims (1B). One v8.10.x issue had the same YouTube thumbnail captioned as two different venues in two different chapters — a confident lie the reader would only notice on close inspection. Mechanical detection prevents the class entirely.

### 1G. Lead + Catch-Up structural compliance (v8.27 — replaces the v8.15 two-anchor rule)

For every fixed section in the stitched HTML, confirm the **Lead + Catch-Up** shape: one angled Lead, plus a substantive Catch-Up roundup (or an optional Companion, or — for a section running short, especially The Toolkit — a visible yield). The old rule hard-failed any section without *two deep anchors*; that mandate is retired. The new failure modes are: (a) a bare Lead with no Catch-Up roundup and no companion; (b) a Catch-Up that is bare namedrops (items naming a thing with no "why it matters" and no link). The chapter-plan validator (`check_section_shape`) catches both at Phase 4; this is the stitched-HTML reading pass.

```bash
# Sketch:
# For each fixed section (world, pixel_byte, toolkit, touchline, screen_sound, session) that APPEARS:
#   - A Lead (substantial H2 + body, >= 300 words).
#   - PLUS a second element: a Catch-Up roundup (several items, each what/why/link),
#     OR a Companion article (>= 200 words, distinct topic), OR a visible short/yield note.
#   - Catch-Up items must NOT be bare namedrops: each names a thing, says why it matters, and links.
# A bare Lead alone, or a namedrop-only roundup, is a hard fail.
# The Toolkit may be ABSENT entirely (it yields on thin weeks) — absence is not a failure.
```

### 1H. Recent-leads sliding-window cap (v8.15, refined v8.18)

For each topic in state-file ongoing_stories, compute `recent_leads` = count of entries in `lead_history` with date within the last 26 weeks of the issue date. If `recent_leads >= 3`:
1. Read the topic's named-entity tag (e.g. "Iran War" -> ["iran", "tehran", "hormuz", "khamenei"])
2. Scan each fixed section's Lead H2 + first paragraph
3. If named entities appear in H2 OR appear 3+ times in first paragraph AND `recent_leads * 2 > weeks_since_last_lead`: hard fail with reason "topic-lock"

Leads older than 26 weeks age out of the window automatically — they don't count toward `recent_leads`. Topics that have gone quiet for 6 months become promotable again without override (v8.18 change from the v8.15 unbounded lifetime counter).

### 1I. Per-section mandatory links (promoted from Gate 1D v8.15)

For each section in {world, pixel_byte, touchline, screen_sound, on_the_radar}:
- Count `<a href="http...">` inside the section: must be >= 1 per substantial item
- For On the Radar specifically: every list item must contain an `<a href="http...">`
Hard fail if any item is link-free.

### 1J. Long Shelf wildcard count

For long_shelf section: count items with class="wildcard" (or data-wildcard="true"). Must be >= 2. Hard fail otherwise.

### 1K. Long Game ↔ Session boundary

For long_game section: scan body for fitness-cluster vocabulary (sets, reps, deload, taper, mileage, HRV, kettlebell, deadlift, squat, lifting, run pace). 3+ matches = misclassified fitness content in a finance section. Hard fail.

### 1L. Rotating cadence floor (planner enforcement)

For each rotating section in the issue, verify `weeks_since_last_appeared >= cadence_low` (per state file). If a section is scheduled inside its floor without a `deficit_override_reason`, hard fail with reason "cadence-floor".

### 1M. Deficit-eligible section omitted

For each rotating section with `weeks_since_last_appeared >= 2 * cadence_high`, verify it appears in the issue. If absent without a `deficit_override_reason`, hard fail with reason "cadence-deficit".

### 1F+. Image URL verification chain (v8.13.7+ — UNBREAKABLE)

Gate 1F handles per-issue scans the writer/orchestrator can run by eye. The verification chain below is **structurally enforced** by gate scripts the orchestrator MUST run. Each is non-skippable; together they make broken / fabricated / duplicate image URLs impossible to ship.

| Phase | Script | What it enforces |
|---|---|---|
| 3a | (researcher subagent) | Every `image_candidates[i]` carries a `verified` block with `head_status: 200`, `content_type: image/*`. Bundle floor ≥16 unique URLs. |
| **3a-verify** | (orchestrator WebFetch loop) | Orchestrator re-fetches every URL itself and OVERWRITES the researcher's `verified` block with the orchestrator's actual result. Closes the self-attestation hole. |
| 3b | `scripts/validate-research-bundle.py` | Rejects bundle if any candidate is unverified / non-2xx / non-image / no image extension / fewer than `min_unique_candidates` distinct URLs. |
| 7.8 D3 | `scripts/visual-smoke-test.py` | Any DOM image URL with no image extension fails. |
| 7.8 D6 | `scripts/visual-smoke-test.py` | Any URL used more than `max_uses_per_url` times in the DOM fails (default 1). |
| 7.8 D7 | `scripts/visual-smoke-test.py --bundle` | Every DOM image URL must appear verbatim in `image_candidates`. |
| CI | `.github/workflows/issue-validation.yml` | All gates re-run in unrestricted-egress environment on every push/PR. Auto-files `validation-failed` issue on failure. |

See `references/spec/global.md` § image-integrity → "Image URL verification chain" for the full layer-by-layer description and rationale.

---

## GATE 2 — Editorial & Visual Quality

### Closing Colophon
- [ ] **Closing fact "A Fact" must NOT repeat within 12 weeks.** Read `recent_facts` from state before writing. Never use a topic, era, or angle from the last 12 entries. After generating, append the new fact's short tag (e.g. "Anglo-Zanzibar war", "Roman calendar reform", "longest filibuster") to `recent_facts` and trim to last 12.
- [ ] **Closing "Next Week" line must NOT repeat phrasing patterns from the last 4 weeks.** Read `recent_next_week_themes` from state before writing. After generating, append a short tag and trim to last 4.
- [ ] Closing fact has a verifiable source link (Wikipedia is acceptable).

Only proceed here after Gate 1 passes clean.

### Coverage
- [ ] Issue is a healthy Sunday read sized to the week — no hard word target; don't pad to a number, don't pad a thin section (v8.27).
- [ ] Every major section has at least one relevant image
- [ ] **Lead + Catch-Up shape, Lead OPTIONAL (v8.28).** A section may run a Catch-Up only (pure facts, no Lead) — that's fine and often better (gaming, results). A bare Lead with no Catch-Up/companion/yield is a fail; an empty section is a fail.
- [ ] **If a Lead runs, two-factor test + borrowed angle:** it *moved this week* (not a holding pattern — "still in crisis / clings on / waiting on the vote") AND the something-extra is a *sourced* angle real commentators hold, voiced as ours — never invented (the Star Wars "nothing" essay and the Starmer ×3 run are the anchor failures).
- [ ] **The Catch-Up carries specific facts, not namedrops** — every item a real fact (name/number/date) + why it matters + a link; a beat-label with no fact is cut ("namedropped three game releases and moved on"). Plus one-line safety-net headlines for the week's majors.
- [ ] **UK politics is out by default** (v8.27). It appears only as a genuine landscape shift (an election *result* that changes the picture, a government actually falling) that also passes the two-factor Lead test; reshuffles / leadership will-he-won't-he / resignation-call counts / Stormont process / polling chatter are out (a one-line safety-net mention at most). It is never auto-promoted to the Lead.
- [ ] If a Companion runs, it's on a visibly different topic from the Lead (not a re-framing of the same story).
- [ ] No fixed section reads as 70%+ about one story when there's been substantial coverage of that story across recent issues.
- [ ] Touchline: lead story is most compelling sport of the week. Serie A ≥ PL depth on normal domestic weeks. Full table (top 10 + relegation zone). Coverage beyond Juve. Doesn't exceed ~30% of issue.
- [ ] **Touchline diversity rule.** Even in a Scudetto-clinching, title-decided, or otherwise once-a-season football week, Touchline must surface at least THREE distinct sport beats — not one big football story plus scraps. The bar: either (a) three different football competitions covered with real substance (e.g. Serie A + Champions League + an FA Cup or Coppa beat), OR (b) at least one beat clearly outside top-flight football (F1 race weekend, snooker/golf/tennis major, NBA / Euroleague playoffs, NFL draft, Six Nations rugby, world athletics, NW200, GAA championship). When a single story (a title clinch, a CL final, a Coppa final) genuinely dominates the week, the lead can take the lion's share — but the section still needs two other meaningfully-treated beats below it. The Also on the Pitch list does NOT count toward the three; it complements them. If the week is genuinely thin outside the headline, surface a non-football sport rather than padding the football coverage.
- [ ] Release Radar: 15-20+ items across ALL categories, chronological within sub-sections
- [ ] Star Wars mentioned somewhere
- [ ] No coverage gaps in fixed sections
- [ ] Issue has news AND features/evergreen — not purely news
- [ ] On the Radar: 8-10 items, no overlap with Release Radar, specific and non-patronising

### Rotating Sections
- [ ] 2-3 rotating sections selected from state file cadence priority (v8.27 — was 3-4). Roster: The Shelf, This Week in History, Listening, Money, Places.
- [ ] The Saga is trigger-driven, NOT scheduled by cadence — present only if a public peg (researcher-found) or private peg (`currently_reading`/`currently_watching` or manual trigger) fired it.
- [ ] The Toolkit (fixed-but-yields) appears only when there's tech news; on return it covers the full gap since last appearance, not just 7 days.
- [ ] Only selected sections researched — no wasted research
- [ ] Catch-up rule respected (Shelf, Toolkit, Listening, Money, Places — full gap since last appearance)
- [ ] Navigator only shows sections present in this issue
- [ ] Down the Rabbit Hole included as sidebar if due (3-4 weeks)

### Sub-formats (v8.17)
- [ ] If Screen & Sound's chapter plan was Director's Cut (`sub_format: "directors_cut"`), the rendered Lead reads as an essay (not a current-week news beat), is 550+ words, and the section still carries its Catch-Up roundup (a Companion may carry the displaced current-week beat, but the week's releases are covered either way). `last_directors_cut_date` is updated post-publish.
- [ ] If This Week in History was A Closer Look (`sub_format: "closer_look"`), the rendered section is a single 600-800 word narrative on one event/figure, no also-this-weeks timeline, Wikipedia link present. `last_closer_look_date` is updated post-publish.

### Ongoing Stories
- [ ] Ongoing trackers are factual, not editorial — situation report tone
- [ ] Ongoing trackers have proper space — scaled to the week's developments
- [ ] New lead story is genuinely new — not a rehashed angle on the ongoing story
- [ ] **Iran War re-promotion bar (active rule, current state).** Iran has been promoted back to lead 5 times. The bar for the NEXT Iran lead is now "paradigm-shift class": capital falls, regime change, ceasefire signed/collapsed, US ground action, nuclear escalation, Hormuz reopening permanently, Khamenei dies, or comparable. Cost-number updates, fresh tanker incidents, fresh sanctions, fresh Senate resolutions, oil-price spikes — NONE of these clear the bar by themselves any more. They go in the Also list or in an Ongoing-Story sidebar, not in a lead. When in doubt, demote.
- [ ] **Generalised exponential bar.** Any ongoing story that has led 4+ times applies the same rule — next promotion requires a paradigm-shift development, not an incremental update.
- [ ] State file updated with ongoing_stories changes

### Structure
- [ ] Touchline leads with data (tables, scores) before narrative
- [ ] Foreword: 50-80 words, one thread
- [ ] LEGO in Pixel & Byte, not Screen & Sound
- [ ] History prefers pre-WW2; images match the historical event (no reusing images from other sections)
- [ ] Music lives in Listening when it runs; light-touch in The Shelf otherwise; music releases still in Release Radar when neither present
- [ ] Session: only sourced content, or omitted entirely
- [ ] Podcast recs are episode-specific: title, date, reason — verified content only
- [ ] Places owns all travel/parks/NI content when present; On the Radar one-liners when absent

### Voice
- [ ] **Borrowed angles, our voice — no invented opinion (v8.28).** Every angle / opinion / conclusion / counterargument traces to a real commentator's view found in research, voiced confidently as ours (no quoting/attribution duty). A take the writer made up is a fail — the Star Wars "nothing" essay is the anchor. **Not every piece needs an angle:** facts-only is fine and often better (gaming releases, results roundups, the cut-piece "state the studies" form). A posed question is answered from the sources, never left hanging.
- [ ] **No invented analysis beyond the sources; no stated result that hasn't happened** (the Monaco "Norris on pole" failure). Facts trace to the research bundle (RT-22).
- [ ] **Length follows the material — no padding (v8.28).** A 30-second idea is not 600 words. This subsumes the old filler-phrase lists — they were all symptoms of frame-over-fact. Scan for and cut: "if you've been on the fence…" / "now's the time to…" openers; "it's worth noting / what's striking is" throat-clearing; "is suddenly very real / has arrived" closers; rule-of-three padding where the middle item just rephrases the first. **The general rule: a paragraph that's a fact wrapped in frame gets cut to the fact.**
- [ ] No spoilers — ever
- [ ] Football reads as editorial, not match reports; writes like a magazine journalist, not a personal assistant

### Visual Variety
- [ ] **Component variety.** Weeklies: 10+ different component types (manual count). **Non-holiday specials: MECHANIZED** — satisfied by a PASS on `validate-issue.py` → `special-variety` (hard floor 9 for deep-dive/rewind/starter-kit; 7 for versus/season-review/shortlist/lookahead/next). Read the gate's exit code; don't hand-count specials.
- [ ] No two consecutive sections use the same layout pattern
- [ ] No 3+ screen-heights of unbroken prose
- [ ] At least 3 pull quotes, 2 big-number callouts, 3-5 DYK boxes
- [ ] Entry pattern rotation (`.entry-stat`, `.entry-quote`, `.entry-bullets`, `.entry-question`, prose)
- [ ] 1-2 breather bands between dense sections
- [ ] At least 1 compare panel or sidebar-float
- [ ] Read-next connectors between at least 3 major sections
- [ ] Maps included when relevant (history, world news, travel) — sourced from real sources, not AI-generated

### Wildcards & Synthesis
- [ ] 2-3 items the reader didn't ask for
- [ ] 2 of 8 Long Shelf items are wildcards
- [ ] Cross-cluster connections present where natural

### Lens-not-Filter (v8.19)
- [ ] `plan.discovery_picks` carries >= 3 entries (weekly format). Each entry has chapter_id, headline_hint, discovery_rationale.
- [ ] Every discovery_pick item appears in the rendered HTML at the chapter it's tagged to. (Spot-check: open the named chapter, find the item.)
- [ ] Each recommendation section appearing this issue (Shelf, Listening, Money, Places, Toolkit, Saga) shows visible Discovery vs. Reinforcement balance — not 100% reinforcement of known brands/apps/series.
- [ ] No recommendation section repeats the dominant brand/app/series from its previous appearance (cross-reference state file `last_toolkit_app`, `last_session_topic`, and the latest issue of each section in `issues/`).
- [ ] World This Week (or another news section) carries any genuinely major world story that landed this week, regardless of whether it maps to a declared interest. Story missing = Gate 2 fail.

### Special Editions (when applicable)
- [ ] "Meanwhile..." section present before Footer, 12-18 linked items
- [ ] Guardrails respected: no 3+ consecutive specials, manual triggers override
- [ ] Trip-aware rules: Rewinds deferred near trips, Field Guide before Countdown, Season Reviews patient
- [ ] State file updated: `last_special_date`, `last_special_format`, `consecutive_specials_count`

### Countdown (when applicable)
- [ ] **Title uses the reader's name for the trip**, not a geographic locator. Marquee venue(s) on the cover ("Efteling & Beekse Bergen"), never the host town/city ("Kaatsheuvel"). Same name carries through masthead ticker, navigator, foreword, and footer.
- [ ] **Hype over homework.** No chapter reads as a checklist, how-to, or planning exercise. If a chapter answers "how do I do this?" rather than "why should I be excited about this?", it's in the wrong format. Reader should come away wanting to go, not wanting to plan.
- [ ] **Visuals-first (tiered).** Narrative chapters carry 3+ real, credited images. Mood Board carries 8–12. Stat-led and coda chapters (By the Numbers, Before You Go) carry 1+. Five Moments Worth the Trip carries one image per moment (5+). No chapter ships with only prose. All images real and credited — no AI, no uncredited stock.
- [ ] **Top Attractions (or venue-equivalent) chapter present** when any venue has headline draws. Ranked 5–7 items, each with one image, one opinionated take, one practical note. Shape fits the venue (theme park → rides; safari → animal encounters; resort → corners/zones).
- [ ] **Mood Board chapter present.** 8–12 images, captions only, no prose block. For multi-venue trips, split 50/50 or two separate boards.
- [ ] **By the Numbers chapter present as hype opener**, right after Foreword. All venues represented in the figures.
- [ ] **Five Moments Worth the Trip chapter present.** Third-person editorial voice — no "I" or "we". One image per moment. At least two moments from each venue on multi-venue trips.
- [ ] **Logistics compressed into "Before You Go" coda.** No standalone Logistics chapter. Total logistics content across the issue ≤ 400 words.
- [ ] **Multi-venue balance check (MECHANICAL).** Count words and images per venue across the whole issue. Both splits must sit within 60/40. If either exceeds, rebalance before delivery. The shape of each venue's coverage can differ (theme park vs safari), but the hype weight and visual presence must be equal. Never 8 chapters on venue A and a single paragraph on venue B.
- [ ] **No invented day-by-day itinerary.** A day-by-day plan only appears when the reader has explicitly supplied one. If they haven't, that chapter is omitted entirely — do not guess at fillers like "morning at the park, afternoon by the pool."
- [ ] **No padded chapters.** Word-count band is a target, not a floor. Cut any chapter that doesn't have genuine content; a tighter Countdown beats a padded one with obvious filler.
- [ ] **Accommodation chapter present** when the reader has named a hotel/lodge/resort. Each property gets rooms + dining + facilities + activities + "why pay the premium". Multiple properties get parallel treatment. Minimum 400–600 words and 4 images per property.
- [ ] **Accommodation chapter is actually about accommodation.** A chapter gated with a hotel/resort name must contain real coverage of that property, not a two-park contrast or pivot paragraph. If research was thin, the chapter was either bulked up or relabelled to what it actually covers.
- [ ] **Whole-estate research.** For every venue covered, the issue reflects the full estate, not just the marquee feature. Beekse Bergen: safari park + Speelland + Safari Resort hotel (restaurants, pools, bowling) + Lake Beekse Bergen. Center Parcs: lodges + pool complex + activities + restaurant village. Before delivery, confirm you can list every zone, every restaurant, every activity type for each venue. If the issue could be summarised as "you can drive round the animals" or equivalent one-liner, research was insufficient.
- [ ] **Travel imagery target met.** 25–40 images across the issue (hotels alone contribute 8–12). Every venue/room/restaurant/activity chapter has at least 2 images. Mix of establishing + detail shots. Every image captioned with what + where + credit. Sourced from official press kits, Wikimedia, credited Flickr — never AI-generated.

### Versus (when applicable)
- [ ] **Source diversity.** Both cases built from a wide pool: long-form reviews, blogs, Reddit, YouTube reviews/walk-throughs, forum trip reports, parent/practitioner communities, regional-language sources where relevant. At least 3 independent source types per round/chapter. Official sites are the spine, not the body. AI-generated and uncredited stock banned for both prose and imagery.
- [ ] **No-taste rule.** Round winners and the final verdict trace to convergence of source signal, not to synthesised verdicts. Strong claims surface as paraphrased consensus ("reviewers consistently rate…", "the consensus across blogs and Reddit is…") never as agent-voice judgements. Frequency of mention beats per-source ranking; hidden-gem clause still available.
- [ ] **Reader-profile invisibility (Gate 1A) holds.** Audience-fit stated as venue character ("A's slide tower is consistently named the strongest of the two in family-travel reviews"), never as reader instruction ("your son will love…").
- [ ] **The Verdict picks a winner under stated conditions.** No "both are great" cop-out. The conditions must be specific and acknowledge where each option actually wins.

### Versus — holiday/destination subtype (when applicable)
- [ ] **Round-by-round structure used, not Case-for-A/Case-for-B.** Each round is a chapter and ends with a round verdict (A, B, or draw, with sourced reasoning).
- [ ] **Orientation chapter present.** "What Each Place Is" sits between Tale of the Tape and the rounds. ~400-600 words. The reader knows what each place fundamentally *is* before the rounds begin.
- [ ] **Pools/slides round present and deep when both venues have a water complex.** Covers slide types and age fit, pool variety, thermal/spa, crowding patterns, included-vs-charged, restrictions, queue consensus. Treated with the depth a deciding-factor round deserves — 8-12 source quotes feeding this round is normal.
- [ ] **Value round present and standalone, never folded in.** Like-for-like comparison: same dates, party size, length of stay, comparable accommodation tier. Where exact prices unavailable, proportional gap with citations.
- [ ] **"What the price gap buys" surfaced concretely and sourced.** Not "A is more premium" — specific facilities, restaurants, inclusions, with sources. Reader can map specific spend onto specific value.
- [ ] **Verdict refuses a flat winner.** A flat "A wins" or "B wins" is a fail. The Verdict explicitly weighs the price gap, names which rounds went each way, and frames the winner conditionally on what the reader prioritises and how they'd otherwise spend the price difference.
- [ ] **Accessibility round only when the two venues genuinely differ on it.** Dropped when both sit in the same area or rely on the same transport. Trip `access_constraints` still applied across the issue regardless.
- [ ] **Source quote density.** Each round carries multiple attributed quotes from independent sources. A round resting on one source isn't a round, it's a hidden-gem call — surface it as such.

### Field Guide (when applicable)
- [ ] Reference-first, scannable on a phone
- [ ] Every meal slot covered with 3-5+ options
- [ ] Full spectrum: fine dining → comfort food fallbacks
- [ ] Theming/experience noted, audience-fit stated as venue character ("family-friendly", not "great for your son"), booking notes
- [ ] Multi-venue: primary gets full treatment, secondary gets practical section
- [ ] Research depth: official menus, TripAdvisor, blogs, Reddit, YouTube all consulted
- [ ] **No-taste rule — selection traces to sources, not to taste.** Every Unmissable is justified by ONE of: (a) frequency — multiple independent sources converge on it; (b) hidden-gem clause — a single credible source makes a substantive, specific case for it; (c) documented regional/cultural significance; (d) structural uniqueness in the venue; (e) notable theming/setting documented in real material. Never "sounds nice" or "would probably be good". Same applies to Countdown's Top Attractions and Five Moments.
- [ ] **No-taste rule — ranking/tiering reflects source signal, not taste.** Hot tier = high-frequency consensus OR exceptional hidden gem. Warm tier = recommended with caveats / narrower appeal / split opinions. Note tier = niche or situational. **Frequency-of-mention beats per-source-ranking inside any one source** — 5 blogs listing a place at their #5 spot outranks 1 blog listing a place at its #1 spot. If a pick's tier rests on the agent's guess at quality rather than what sources say, demote it or move it.
- [ ] **Quote density — with hidden-gem carve-out.** Frequency-driven picks carry at least 2 attributed sources woven into the prose. Hidden-gem picks (single-source) carry at least 1 well-developed attributed source plus a clear flag that this is a hidden-gem call ("one Dutch food blogger argues at length…", "a deep-dive on r/Efteling singles out…"). Picks with zero attributed sources are under-researched — cut or re-research.
- [ ] **Banned-phrase scan — no synthetic sensory prose.** Search the output for first-person/sensory phrases the agent can't have actually experienced, and cut every instance not inside an attributed quote: `the first bite`, `it smells of`, `the room feels`, `you'll taste`, `warm and buttery`, `crisp at the edges`, `melt-in-the-mouth`, `rich and`, `comforting`, `moreish`, `divine`, `cooks in striped aprons` (and any equivalent invented atmosphere). If a sensory detail is needed, quote the source. The photo carries the visual sensory load.
- [ ] **Opinions are reported, not held.** Strong claims ("skip this", "worth the wait", "tourist trap") appear only as paraphrases of source consensus, surfaced as such ("reviewers consistently warn…", "consensus across blogs and Reddit is…"). No naked agent-voice verdicts on quality.

### Technical
- [ ] **CSS/JS injected:** verify the output contains `<style>` and `<script>` tags (not `<!-- INJECT:CSS -->` placeholders). If placeholders remain, run `scripts/inject-assets.sh` again.
- [ ] **No `.reveal` on sections or containers.** Search for `<section.*reveal` and for `reveal` on `split-60-40`, `split-40-60`, `dual-col`, `also-cards`. `.reveal` may only appear on small leaf elements (individual images, angles, pull-quotes, cards). Sections and layout containers must always be visible — `reveal` with `opacity:0` on large elements causes blank pages on mobile.
- [ ] **Single masthead only.** The persistent masthead is the `<div class="mast" aria-hidden="true">` block sitting OUTSIDE `.mag` (right after `<body>`, before the progress bar). There must be exactly ONE masthead. Search for `class="masthead"` (note: `masthead` not `mast`) — if any `<nav class="masthead">` exists, delete it. The old static masthead has been replaced by the persistent `.mast` div; keeping both makes the duplicate render unstyled at the top of the page.
- [ ] **Image URLs are real and load.** Every `<img src="https://..."` must point to an image that returns HTTP 200. **Do NOT construct Wikimedia thumb URLs** like `/wikipedia/commons/thumb/X/YZ/Filename.jpg/640px-Filename.jpg` — the size-prefixed thumbnails frequently 404. Use one of these reliable patterns instead:
  1. **Original-resolution Wikimedia URL:** `https://upload.wikimedia.org/wikipedia/commons/X/YZ/Filename.jpg` (no `/thumb/`, no size suffix). The `X/YZ` hash MUST match the actual file location — verify by visiting the Wikimedia Commons page first.
  2. **Stable canonical redirect (preferred when uncertain):** `https://commons.wikimedia.org/wiki/Special:FilePath/Filename.jpg` — this redirects to the current image regardless of hash path. Always works as long as the filename is correct.
  Verify EVERY image URL with a HEAD request before committing. A broken hero image is a visible failure.
- [ ] **Image resolution check.** Before using a Wikimedia Commons image as a hero or feature image, confirm the source resolution is reasonable. A 15KB / 800x600 file will pixelate badly when stretched to a 960px hero slot. Visit the Commons file page and check the "Original file" dimensions -- aim for at least 1500px on the longest dimension for hero images. Avoid files under 100KB for any prominent visual.
- [ ] **Image specificity check (the "random Pope photo" rule).** A generic Wikimedia photo of a subject is almost never the right image. Before using ANY image, ask: does this picture show the SPECIFIC thing the section is about? A profile portrait of the Pope is wrong for a story about his Africa trip — find a wire photo of him in Equatorial Guinea, or better, a map of the trip route. A generic Switch 2 product shot is wrong for a story about a specific game launch — find official art for that game. A stock console shot is wrong for a feature on a specific franchise — find period-appropriate art for that franchise. The hierarchy of preference: (1) journalism/wire photo of the actual event, (2) official art/press kit for the specific subject, (3) infographic or map that adds information the prose doesn't carry, (4) period-appropriate context image. Generic Wikimedia portraits/product shots are the LAST resort, not the default. If you can't find a specific image, sometimes the right answer is no image at all rather than a generic one.
- [ ] **League tables MUST use the `.league-table` component class.** Never use inline `style=""` on table cells, never invent ad-hoc table styling, never use a generic `<table>` for league tables. The component class handles backgrounds, text colour, row striping, and qualifying/relegation tinting via the existing CSS in `09-section-touchline.css`. Inline white text on cream background = invisible table = visible failure. If a row needs special treatment (highlighted team, qualifying band, relegation band), use the existing modifier classes (`.is-highlighted`, `.qual-cl`, `.qual-el`, `.relegation`) — do not write inline styles. After generation, search the output for `<table` and verify every match either uses `.league-table` or has a documented reason not to.
- [ ] Navigator cards anchor-link to sections with matching `id` attributes
- [ ] Progress bar and back-to-top button functional
- [ ] No rendering artefacts: no stray numbers, no garbled sections, no broken layouts

---

## GATE 3 — Stitched-Issue Gate (cross-chapter, v8.11.0+)

Run after `scripts/stitch-issue.sh` completes. These are cross-chapter checks that per-chapter writers cannot self-audit.

- [ ] **Image-source diversity:** no single domain provides >50% of attributed images across the full issue. Check `grep -oE 'src="https://([^/"]+)' output.html | sort | uniq -c | sort -rn` — if the top domain count / total > 0.5, diversify.
- [ ] **No two consecutive sections share same primary component pattern.** Scan through the stitched HTML — no two adjacent `<section>` elements should open with the same component class (e.g. two consecutive `.entry-stat` openers, two consecutive `.hero-bleed` images).
- [ ] **Accent lockdown enforced across all chapters.** Search the stitched output: `grep -E 'color.*E8384F|color.*sp-accent-primary' output.html` must return 0 inline style matches. CSS-class-driven coral is handled by the cascade; only inline style overrides are a failure.
- [ ] **All internal cross-refs resolve.** For sequential formats only: any `chapter_id` referenced in a cross_refs field exists in the stitched output. Search for each `data-chapter-title` cited in the prose.
- [ ] **Ongoing-story claims consistent across chapters.** No chapter should contradict another on a running story's status (e.g. "ongoing" in chapter 3, "concluded" in chapter 7). Scan manually if multiple chapters cover the same story.
- [ ] **Link health (sample-check).** Pick 5 outbound `href` URLs at random. Verify each returns HTTP 200. `curl -sI <url> | head -1` — expect `200`. A 404 or redirect-to-homepage is a fail.
- [ ] **Scaffold integrity:**
  - CSS injected: `grep -c '<!-- INJECT:CSS -->' output.html` must return 0
  - JS injected: `grep -c '<!-- INJECT:JS -->' output.html` must return 0
  - `<style>` block populated: `grep -c '<style>' output.html` must return ≥1 and the block must not be empty
  - `<script>` block populated: `grep -c '<script>' output.html` must return ≥1 and the block must not be empty
