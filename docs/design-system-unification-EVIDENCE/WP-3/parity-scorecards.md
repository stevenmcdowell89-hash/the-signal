# WP-3 Design-Parity Scorecards

Verifier: independent design-parity pass, 2026-07-19. Inputs: the two candidate packs (`render/` + `metrics.json`), the frozen reference packs (`references/{countdown,field-guide,mockup}/render/`), and Part 1 verbatim (`WP-2/part1-verbatim.md`). No source HTML/CSS, git history, or progress docs were consulted. Screenshots opened: 13 candidate-1, 11 candidate-2, 9 reference (both widths + dark for each candidate; minimums met).

---

## CANDIDATE 1 — editorial-skin Deep Dive (`parity-candidate-dd-editorial/`, source `dd-2026-06-30-editorial.html`)

### Step 1 — the three questions (screenshots alone)

- **"Objects on a surface, or boxes on a page?"** Objects on a surface: taped ruled cards, a push-pinned hand-drawn chart, rotated postal date-stamps and an index card all sit at 1–3° with shadows on a visibly cross-hatched paper ground (1440/depth-2.png, depth-3.png; 390/depth-2.png).
- **"Does the scroll travel, or is it one flat ground?"** It travels: dark-ink cover → cream paper Act I → parchment-gold Act II → ash-brown Act III → back to cream coda, with marquee transit bands ("STONE leaving … GOLD arriving") between acts (cover.png, 1440/depth-1.png, depth-3.png, depth-5.png, depth-7.png; metrics `mx-transit` ×3).
- **"Would a reader who loved the trip countdown recognize this as the same magazine's craft?"** Yes — the same tape/pin/stamp fastener language, handwritten annotations, ghost numerals and mono micro-labels, spoken in archival ink instead of holiday scenography.

### Step 2 — side-by-sides (Laws 1, 2, 4, 7)

References used: `references/mockup/` (the de-themed kit, incl. the Dossier/Deep Dive spread) and `references/field-guide/` (the event-skin bar), viewed at the same widths as the candidate (1440 covers and spreads; 390 pair: candidate `390/depth-2.png` vs field-guide `390/depth-2.png` opened in the same message).

- **Law 1 (scene):** Mockup depth-2 shows the kit standard — taped index card + CSS solidus card at ~2° with shadows on a plum ground. Candidate matches it like-for-like in paper terms: taped/ruled cards, pinned chart with a rendered pushpin, rotated ink stamps, on a cross-hatch ground that is never flat. Difference: candidate's ground is quieter (editorial restraint per Law 11) — pattern instead of starfield; that is the correct skin expression, not a gap.
- **Law 2 (density):** At 390, candidate depth-2 shows index card + crosshead + stamp inside one screen; field-guide 390/depth-2 shows one taped photo card. Candidate's on-screen event cadence visibly matches or exceeds the reference's. (Quantitative result below — one metric breaches.)
- **Law 4 (arc):** Field-guide holds one indigo ground for long stretches; candidate visibly changes ground per act (cream → parchment gold → dark ash) with designed transit bands, expressed in ink/paper tints exactly as Law 4 prescribes for editorial specials. Candidate's arc is *stronger* than the field-guide reference's at the depths sampled.
- **Law 7 (cover):** Candidate cover (1440/cover.png) vs field-guide cover (1440/cover.png): both poster-grade; field-guide's gesture is the giant "44" + pink solid/outline sans; candidate's is the owned Deep Dive gesture — oversized ghosted "1453" numeral + ghost script "Rhomaioi", script kicker, serif display with outlined "Outlived", act pills. Not interchangeable. Difference: candidate is darker/quieter (correct for editorial skin); field-guide reference's own masthead is overlapped by the back pill ("…gnal"), a flaw the candidate does not share.

### Step 3 — the Twelve Laws

| Law | Verdict | Evidence |
|---|---|---|
| 1 Scenography | **PASS** | 1440/depth-2.png: rotated postal stamp + handwritten sidenote + taped ruled card on cross-hatch ground; 1440/depth-3.png: pinned tilted map card, pinned self-made bar chart with pushpin + handwritten caption; 1440/depth-5.png: ghost "XII" numeral bleeding off right edge. No flat single-color act ground anywhere in 13 shots. Objects, not boxes. |
| 2 Density w/ distribution | **FAIL (marginal)** | metrics.json 1440×900: words/screen **222.7 > 220 max** for Deep Dive — an explicit cap breach. Everything else passes: 390 words/screen 162.3; events/screen 1.02 (1440) and 0.74 (390, in band); distribution `longestZeroEventRun: 1` at both widths, `law2DistributionFail: false`. The breach is +1.2% at one viewport; remediable by ~230 fewer body words or ~2 screens more air at 1440. Honest reading of a stated max: over is over. |
| 3 Length | **PASS** | metrics.json: bodyCopy **18,429** ≥ 8,000 Deep Dive floor (2.3×). Not density-by-shortness. |
| 4 Arc | **PASS** | Grounds per act visibly distinct (1440 depth-1 cream, depth-3 parchment-gold, depth-5 ash-brown, depth-7 cream coda); metrics: 3 `mx-transit` marquee bands ("STONE leaving The Founding Centuries… GOLD arriving", "GOLD leaving… ASH arriving", "ASH leaving… LIGHT arriving") — designed moments, not background swaps; ink-terms expression per Law 4's editorial clause. |
| 5 Motion | **PASS** | Tier0 print-still per Law 11/engagement brief: metrics motion census **0 animated elements** at both widths (correct for tier0), reduced-motion census 0, JS-independence not contradicted by any shot; nothing attached to running text. |
| 6 Object fiction | **PASS** | One kit (dossier/archive) with 2–3 object types + universal fasteners: facts as ruled/taped index cards ("THE NAME:", "A STATE SECRET, STILL KEPT:" — 1440/depth-2.png), dates as circular postal stamps (depth-2, depth-3), data as pinned hand-chart (depth-3) and mono ledgers/scorecards (metrics: ledger ×6, statband ×6). No generic bordered div carrying kit-eligible content observed; the plainest furniture (depth-7 "Meanwhile" ranked entries) still wears number plates + "NOTED" stamp chips. |
| 7 Covers | **PASS** | cover.png: ghosted-numeral gesture owned by Deep Dive ("1453" + "Rhomaioi"), ≥3 voices, poster-grade; distinct from countdown and field-guide covers. dark-1440.png shows chrome accent re-toned in dark (plum → blue), evidence the accent is token-driven, not hard-coded. |
| 8 Type | **PASS** | Six voices across issue: serif display (titles), outlined display ("Outlived"), script/hand (annotations "the Danube frontier, regained"), mono micro-labels ("CREDIT", "INDEX CARD · THE SIGNAL ARCHIVE" — legible ≥0.72rem at 390/depth-2.png), italic serif decks, sans body on cover. Body measure ~630px ≈ 60–65ch at 1440 (1440/depth-1.png). Cover uses ≥3 voices. |
| 9 Trust | **PASS** | ≥5 named external voices, each as a quote-object (metrics `mx-quote` figures): Justinian I ("Solomon, I have outdone thee"), St Basil of Caesarea, Loukas Notaras ("Better the Sultan's turban…"), Judith Herrin, Edward Gibbon ("The triumph of barbarism and religion") — historians/primary sources count per Law 9. No "— THE SIGNAL" self-quote observed; no quote rendered >2×. |
| 10 Craft floor | **PASS** | metrics 390: no document h-scroll (`flag:false`), chrome overlap 0 intersections at 10 depths, tableTruncation none; 390 shots show no mid-word cuts and chrome reserving space (390/cover.png stacks the masthead). Real `<img>` photography visible (mosaics, maps). dark-1440.png renders (cover-only capture; body dark-mode not observable in pack — noted, not contradicted). Contrast in all shots comfortably AA. |
| 11 Identity | **PASS** | Editorial skin kept bookish: paper-and-ink scenography (archival cards/stamps, no theme-park props), motif surface capped at palette arc + one pattern (cross-hatch) + one cover gesture (ghost numeral). |
| 12 Honesty | **PASS** | Full evidence pack present (render-manifest.json, both widths + dark, metrics.json); every metrics claim spot-checked against pixels matched (e.g., motion 0 ↔ nothing mid-animation in shots; event list y-positions match screenshots). |

### Verdict

Eleven of twelve laws pass, several above the bar. Law 2 fails on a single quantitative cap: 222.7 words/screen at 1440×900 against a stated max of 220. Per protocol (all twelve or nothing), and because a false PASS voids everything downstream:

**CANDIDATE 1 PARITY: FAIL**

*(Remediation is small and mechanical: trim ~230 body-copy words or add ~2 screens of breathing room at desktop, re-measure, re-submit. No design rework indicated.)*

---

## CANDIDATE 2 — event-skin Countdown re-dress (`parity-candidate-countdown-event/`, source `countdown-2026-06-14-event.html`)

### Step 1 — the three questions (screenshots alone)

- **"Objects on a surface, or boxes on a page?"** Objects on a surface: taped, rotated polaroids that overlap; brass circular stamps; a tilted full-bleed caution-tape marquee; airmail-bordered postcards with handwritten quotes — on starfield and savannah-grain grounds (1440/depth-1.png, depth-2.png, depth-4.png, depth-7.png).
- **"Does the scroll travel, or is it one flat ground?"** It travels: indigo-night starfield (Efteling) → cream savannah grain (Beekse Bergen) with a designed transit marquee ("EFTELING… fairytale → savannah") at the seam — the exact indigo-night → cream-savannah shift Law 4 cites (1440/depth-3.png bottom, depth-4.png).
- **"Would a reader who loved the trip countdown recognize this as the same magazine's craft?"** Yes — it is recognizably the same issue, and at rest it is now *cleaner* than the original: same postcard fiction, same countdown, same voices, better-set objects.

### Step 2 — side-by-side vs the ORIGINAL frozen countdown (same widths; pair `1440/depth-5.png` vs reference `1440/depth-5.png` opened in the same message)

- **Law 1:** Both put objects on a scene ground. Re-dress **better**: taped polaroids sit in balanced overlapping shelves with handwritten captions and mono credits (candidate depth-5) where the original hugs the left margin leaving a dead right half (reference depth-5); candidate's savannah ground carries a continuous cross-hatch grain, the original's is near-flat cream with sparse paw-print glyphs. At 390 the candidate keeps the reference's own minimum standard — sparkle glyphs behind plain body text (candidate 390/depth-1.png vs reference 390/depth-2.png).
- **Law 2:** Re-dress **denser and better distributed**: 115 events vs the original's 95; 2.19/screen vs 1.75 (1440) and 1.46 vs 1.15 (390); zero-event run of 1 both widths. Nothing was thinned in the re-dress.
- **Law 4:** Same two-act arc in both. Re-dress **at parity**: the night → savannah shift survives intact and the seam is a designed transit marquee. The original's per-act ambience (constellation lines, drifting glyphs) was busier; the re-dress's grounds are steadier — acceptable, not a regression at rest.
- **Law 7:** Original cover: arc-text "GREETINGS FROM", drop-shadow display, castle + smiling sun; but its chrome overlaps the masthead wordmark ("…gnal" behind the back pill) and at 390 the subtitle/badges collide with the castle art (reference 390/cover.png). Re-dress cover: same poster voice (script "greetings from" + chunky EFTELING + outline BEEKSE BERGEN + naive sun/castle illustration) contained in a postcard rule-frame; no overlap at either width, live-countdown statband kept. Re-dress **better** on craft, **equal** on gesture; one visible change: the accent pill/hairline reads steel-blue where the original was gold — token choice, still `--mx-accent`-driven (identical in dark-1440.png).
- **Where the re-dress is worse / pending:** motion. The original fired **185–187** animated elements during the scroll pass (flips, drifts); the re-dress fires **2** (marquee drift). Scroll-driven tier2 signature moments — stamp-slams, countdown flips, act crossfade — are **pending** (later phase per the engagement brief) and are the one axis where the original still outclasses the re-dress. Also −236 body words vs original (6,380 vs 6,616; still well above floor).

### Step 3 — the Twelve Laws

| Law | Verdict | Evidence |
|---|---|---|
| 1 Scenography | **PASS** | 1440/depth-1.png: taped polaroid ~2° + brass stamp + caution-tape marquee tilted and bleeding both edges + ghost "2" numeral, all on dotted starfield; 390/depth-1.png: sparkle glyphs behind plain body text (the Law-1 reference standard, kept); 1440/depth-4.png: overlapping taped polaroids + "FOUR PARTS ONE PASS" stamp on savannah grain. Every ephemera object carries ≥2 of rotation/fastener/shadow; no flat act ground. |
| 2 Density w/ distribution | **PASS** | metrics.json: events/screen **2.19** (1440) and **1.46** (390) vs 1.0 floor — above the 1.3 target, as the frozen bar itself is (reference 1.75/1.15), so above-target matches the bar; words/screen 121.7 and 81.0, both ≤ 210 max; `longestZeroEventRun: 1` at both widths. |
| 3 Length | **PASS** | metrics.json: bodyCopy **6,380** ≥ 4,500 Countdown floor (−236 vs original 6,616, noted, still 1.4× floor). |
| 4 Arc | **PASS** | Starfield act → grain act with `mx-transit` marquee at the seam (1440/depth-3.png bottom, metrics marquee ×3 incl. "EFTELING the floating castle … fairytale → savannah"); matches Law 4's cited countdown shift. |
| 5 Motion (scoped per engagement: tier2 signature moments deferred) | **PASS (with pending note)** | (i) motion fires during real scroll: metrics `animatedElements: 2` — `mx-marquee__track / CSSAnimation:mx-marquee-drift` at both widths; (ii) reduced-motion census **0** at both widths; (iii) both animated nodes are furniture (marquee tracks), no motion on running text in any shot. **Pending:** fuller tier2 moments — stamp-slam, countdown flips, act crossfade — are absent (original fired 185+ elements); they must land in the later phase for full tier2 parity. |
| 6 Object fiction | **PASS** | Postcard/travel kit throughout: airmail mail-cards with handwritten reader quotes ("Greetings from…", 1440/depth-7.png), taped polaroids, brass circular stamps, ticket-style ranked zig entries with number plates + WHERE/WHY ledger rows (1440/depth-2.png), caution-tape marquee, cheat-sheet ("good to know", metrics), Karibu Town ledger. No generic bordered divs carrying kit-eligible content observed. |
| 7 Covers | **PASS** | cover.png: poster with ≥3 voices (script, chunky solid, outline) + illustration + live countdown statband, framed as a postcard; distinct from field-guide's "44" cover and from the Deep Dive candidate; accent identical in dark-1440.png (token-driven). Re-dress fixes the original's masthead overlap and 390 title collisions. |
| 8 Type | **PASS** | Script kicker, chunky display, outline display, serif italic quote voice, mono micro-labels ("PHOTO · EFTELING PRESS / OFFICIAL SITE" — legible ≥0.72rem, 1440/depth-2.png), sans body. Cover ≥3 voices; body measure ~630px ≈ 65ch (1440/depth-3.png). |
| 9 Trust | **PASS** | ≥6 named external voices, pixel-confirmed four as rendered quote/kit objects: Benjiramon, *Along for the Ride* (zig quotes, 1440/depth-2.png), Lisa, *FlipFlop Globetrotters* (390/depth-4.png), keeper Mariska Vermij-Van Dijk via Omroep Brabant (serif quote-object, 1440/depth-5.png), The Bayliss family, *Little Clogs Holidays* (airmail postcard, 1440/depth-7.png); metrics shows 9 `mx-quote` figures + 8 quote-bearing mail-cards including the Chloe Gallagher "Unlike busy, overstimulating theme parks…" and second-keeper cheetah-EEP quotes carried verbatim from the frozen issue (attributions confirmed in the reference twin, reference 1440/depth-4.png). No self-quote beyond the footer strapline. |
| 10 Craft floor | **PASS** | metrics 390: no document h-scroll, chrome overlap 0/10 depths, no table truncation; 390 shots clean (390/cover.png, depth-1, depth-4); real `<img>` photography throughout; dark-1440.png renders (cover-only capture, noted). Cream-on-indigo and ink-on-cream text comfortably AA. Materially better than the frozen original, whose back pill overlaps content and whose 390 cover self-collides. |
| 11 Identity | **PASS** | Event skin at full scenography: starfield, illustration, caution tape, postcards, stamps — holiday-descended treatment preserved through the re-dress. |
| 12 Honesty | **PASS** | Full pack (manifest, both widths + dark, metrics); metrics spot-checks match pixels (marquee present where census says motion fired; event y-positions match shots; countdown statband present at cover and coda as listed). |

### Verdict

All twelve laws pass under the stated scope (tier2 signature moments explicitly deferred to a later phase — flagged under Law 5 and Step 2 as the one axis where the frozen original still leads).

**CANDIDATE 2 PARITY: PASS**
