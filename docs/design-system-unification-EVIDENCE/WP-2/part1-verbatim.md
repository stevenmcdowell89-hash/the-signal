# PART 1 — DESIGN LAWS (the north star; every visual gate scores against these)

The bar is `issues/signal_countdown_2026-06-14.html` and `issues/signal_field-guide_2026-05-17.html`, rendered — not their theme, their QUALITIES. The reference mockup `docs/mockups/unification-furniture-kit-mockup.html` shows the qualities de-themed. These twelve laws are binding. Each is written to be scoreable PASS/FAIL by a verifier looking at rendered screenshots.

**LAW 1 — SCENOGRAPHY: objects on a surface, never boxes on a page.**
Every ephemera object carries ≥2 of: rotation (1–3°), fastener (tape/pin/stamp/photo-corner), shadow or paper texture, scene-ground behind it, overlap with a neighboring element. Every act has a SCENE ground (gradient sky, starfield, pattern field, visible grain) — a flat single-color background behind an entire act is a FAIL. At least one object per chapter breaks the column grid (tilted, bleeding off-edge, or overlapping a boundary). Verifier's verbatim question at every gate: **"Objects on a surface, or boxes on a page?"** — "boxes" fails. Reference: the countdown at 390px puts a starfield with sparkle glyphs behind PLAIN BODY TEXT; that is the minimum ambient standard for event-skin acts.

**LAW 2 — DENSITY WITH DISTRIBUTION.**
Designed visual events per screen (event = one of: captioned figure/`<img>`; ephemera object; ledger/table block; stat band; quote-object with named source; numbered plate/act opener; self-made chart/diagram/map; marquee/act-divider; cheat-sheet. NOT: drop caps, hairlines, subheads, bold runs):
| Format | floor–target | Words/screen max |
|---|---|---|
| Weekly | 0.8–1.0 | 210 |
| Deep Dive | 0.7–0.9 | 220 |
| Rewind / Season Review | 0.9–1.1 | 210 |
| Versus / Guide / Next | 0.8–1.0 | 210 |
| Trip specials | 1.0–1.3 | 210 |
Distribution: **no run of 3+ consecutive screens with zero events** (measured on the rendered page at 1440×900 and 390×844; screens = pageHeight/viewportHeight). Max 4–5 consecutive paragraphs without an event. Averages alone never pass — distribution must pass too.

**LAW 3 — LENGTH: density by shortness is a FAIL.**
Body-copy word floors (excluding chrome/captions): Weekly 6,000 · Deep Dive 8,000 · Season Review 6,500 · Rewind 7,000 · Versus 4,500 · Guide 3,500 · Next 3,000 · Countdown 4,500 · Field Guide 6,000. Cautionary precedent: attempt #2's 542-word stub "passed" density. An issue below floor fails regardless of any other metric.

**LAW 4 — ARC: the scroll travels.**
1–3 palette acts per issue, each with its own ground; the act transition is a designed moment (transit band, gold seam, crossfade), not a background-color swap. Reference: countdown's indigo-night → cream-savannah shift. Editorial specials express this in ink terms (paper-white → parchment/sepia tints); the weekly may use its existing band rhythm.

**LAW 5 — MOTION: tiered, furniture-attached, verified.**
Tier per format: tier0 print-still (Deep Dive): hairline draw-ins + ghost-numeral parallax only. tier1 calm (Weekly, Rewind, Next, Guide): rise-on-scroll + object settles (cards "tape down" with ~1° settle, ledger rows tick in sequentially, sparklines draw). tier2 event (trip specials, Season Review, Versus): stamp-slam, marquee, flips, act crossfade. One signature moment per format: Versus = verdict stamp slams per round; Season Review = leaderboard rows climb into place; Rewind = Memory Test columns reveal in sequence; Weekly = dial-needle sweep on band entry; Countdown = flips. Hard rules: motion attaches to furniture, never running text; `prefers-reduced-motion` honored by every animation; JS-off renders 100% of content; no scroll-jacking. **A tier1+ issue where nothing visibly moves during a real scroll capture is a FAIL** (attempt #2 shipped zero perceptible motion).

**LAW 6 — OBJECT FICTION: every fact-block wears its kit.**
Each issue declares ONE kit (Part 2 §2.4), uses 2–3 object types from it plus the universal fasteners. Facts, quotes, and data ship as kit objects — a quote is a postcard/strip with a named source, a result is a ticket stub or scorecard, a comparison is a chalkboard/programme spread — never as a generic bordered `<div>`. Generic bordered boxes carrying content that a kit object exists for = FAIL.

**LAW 7 — COVERS: poster-grade, owned per format.**
Each format has one owned cover gesture (Field Guide owns its giant "44"; Deep Dive: oversized ghosted numeral or map fragment; Rewind: the year-band; Next: route-card timeline; Season Review: bracket/trophy motif). Event-skin covers are posters (multi-voice type, illustration/plate, arc text); no two formats may render visually interchangeable covers; cover reads `var(--mx-accent)`, never a hard-coded accent. The three-identical-dark-covers pattern of the old editorial system is the named anti-goal.

**LAW 8 — TYPE: six voices, disciplined.**
The six type roles all appear across an issue; the cover uses ≥3 distinct voices; mono micro-labels ≥0.72rem; body measure ≤68ch (attempt-observed violations: 0.66rem labels, 1,270px measures). Playfulness lives in display/furniture; body text stays disciplined.

**LAW 9 — TRUST: the magazine has arguments, not experiences.**
Three lanes: EXPERIENCED (taste/feel/being-there) — never first-person, only named verbatim quotes, no invented consensus; ANALYZED — own opinions allowed with working shown; CURATED — selection/reader-fit fully allowed. Minimum named external voices per issue: Weekly ≥4 · Deep Dive ≥5 (historians/primary sources count) · Season Review ≥5 · Rewind ≥3 · trip specials ≥6 · Versus/Guide/Next ≥3. Every voice renders as a quote-object at least once. Self-quotes ("— THE SIGNAL") do not count and are capped at 1 per issue. Each quote max 2 renderings; each fact max 2 tellings. (Attempt #2 shipped ZERO external voices and two self-quotes.)

**LAW 10 — CRAFT FLOOR.**
At 390×844: no document-level horizontal scroll; fixed chrome (back pill, masthead, progress) never overlaps content at any scroll depth — reserve space or hide-on-scroll; tables never truncate mid-word at rest (stack or scroll-wrap with visible affordance); ephemera images are real `<img>` (object-fit) or `role="img"`+`aria-label`; token-level dark mode; minimal print sheet; WCAG AA contrast per act. (Attempt #2 failures: pill overlapped content at every depth; table columns cut mid-word.)

**LAW 11 — IDENTITY: three skins, each itself.**
Transmission (weekly): identity permanently protected — palette, type stack, 800px printed-object chassis, radio conceit — but the weekly IS upgraded: it reaches its Law-2 budget via core furniture through an alias block (mockup spread 2 is the reference; a weekly whose density doesn't change is a FAIL of the engagement, not a success). Editorial skin (Deep Dive/Rewind/Versus/Guide/Next): bookish gravitas kept; motif surface capped at palette-arc + one pattern + one cover gesture; scenography expressed in paper-and-ink (archival objects, not theme park). Event skin (trip specials, Season Review): full holiday-descended treatment.

**LAW 12 — HONESTY: evidence or it didn't happen.**
No gate claim without committed artifacts (Part 6). A discovered false PASS voids the phase and triggers re-verification of all prior gates by fresh subagents. (Attempt #2 recorded "GREEN" evidence that was false on first human look.)

---

# PART 2 — ARCHITECTURE (target state)
