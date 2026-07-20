# PARITY SCORECARD — VERIFIER 1
Candidate: Season Review, "The 2026 World Cup" (event skin, tier2 motion)
Pack: `docs/design-system-unification-EVIDENCE/WP-7/parity-candidate-sr/`
References: frozen renders of countdown, field-guide, unification mockup
Laws: WP-2/part1-verbatim.md, scored verbatim. Date: 2026-07-20.

Shots examined: candidate 23 (1440: cover + depth-0..7; 390: cover + depth-0,2,3,4,6,7; dark-1440; burst/1440 frames 0,1,2,5; burst/390 frames 0,1,5) · references 6 (countdown 1440 cover + depth-2, countdown 390 depth-3, field-guide 1440 cover, mockup 1440 depth-1 + depth-2). Metrics: `parity-candidate-sr/metrics.json`.

---

## 1 — The three verbatim questions (screenshots alone)

**"Objects on a surface, or boxes on a page?"** — Objects on a surface: in `1440/depth-1.png` a rotated, tape-fastened, drop-shadowed chart card sits on an indigo dot-sparkle night ground, and in `1440/depth-4.png` tilted scorecards with shadows sit on a parchment checkerboard field — nothing reads as a box on white.

**"Does the scroll travel, or is it one flat ground?"** — It travels: `1440/depth-0..3` are a floodlit indigo-night starfield act and `1440/depth-4..7` are a parchment-checkerboard ledger act, with metrics recording a marquee transit band ("FLOODLIGHT leaving The Tournament … TERRACE entering The Ledger", y=15337) and paired `mx-seam` opacity crossfades between them.

**"Would a reader who loved the trip countdown recognize this as the same magazine's craft?"** — Yes: the same craft signature — script-over-slab poster cover with a giant ghosted numeral, body copy set directly on a decorated night ground, taped paper ephemera, mono micro-labels, named quote-objects — carried into a new football-dossier conceit.

---

## 2 — Side-by-sides (same width, stated differences)

**Law 1 (1440): candidate `1440/depth-1.png` vs countdown `references/countdown/render/1440/depth-2.png`.** Both put running body text directly on an indigo night scene-ground. Candidate's chart is a rotated paper object with tape fastener, hand-script caption and mono credit line, breaking the column leftward; countdown's chart is an upright cream card with a gold spine on a constellation field. Difference: candidate's ambient field is a subtler gold dot-grid vs countdown's star glyphs and constellation lines; candidate compensates with stronger object treatment (rotation + tape + shadow on the figure, which the countdown chart card lacks). Candidate meets and locally exceeds the reference's ambient minimum.

**Law 2 (1440): candidate `1440/depth-2.png` vs mockup `references/mockup/render/1440/depth-2.png`.** One candidate screen carries four designed events (numbered plates 02 and 03 with kicker + pull-line, two rotated fixture-ledger cards with mono scorelines); the mockup screen carries four (taped index card, taped photo-corner solidus card, named quote-object, stat-band opening). Same event cadence; difference is candidate runs a two-column zig with alternating tilt where the mockup pairs objects side-by-side. No sparse stretch in either.

**Law 4 (390): candidate `390/depth-3.png` vs countdown `references/countdown/render/390/depth-3.png`.** Countdown's act shift is indigo-night → cream savannah; candidate's is indigo floodlight → parchment ledger, evidenced across `390/depth-3` (still starfield, podium scorecard + Tuchel quote) into `390/depth-4/6/7` (checkerboard parchment ground). Difference: candidate's transition is a marquee transit band + gold seam crossfade (metrics `div.mx-transit` marquee event; `mx-seam--out`/`mx-seam--in` opacity transitions) where countdown cuts at an act plate — candidate's transition is the more designed moment.

**Law 7 (1440): candidate `1440/cover.png` vs field-guide `references/field-guide/render/1440/cover.png`.** Both are poster covers on indigo with a ghosted background numeral ("26" vs the field-guide's owned "44"). Differences that keep them non-interchangeable: candidate is a centred slab stack ("ONE HUNDRED / & FOUR" with an outline voice) crowned by a yellow script arc line and anchored by a circular trophy roundel — the Season Review's owned bracket/trophy motif; field-guide is a left-set mixed-weight sentence ("The Field Guide to Efteling & Beekse Bergen.") with a pink display voice and no roundel. Nobody would shelve these as the same cover.

---

## 3 — The Twelve Laws

**LAW 1 — SCENOGRAPHY: PASS.** Every sampled ephemera object carries ≥2 qualifiers: `1440/depth-1.png` chart = rotation + tape + shadow + scene-ground; `1440/depth-2.png` fixture cards = rotation + shadow + numbered chip; `390/depth-7.png` closing ticket = rotation + perforation stub + shadow. Act grounds are never flat: gold dot-sparkle starfield (Act I, `1440/depth-0..3`), parchment checkerboard with grain (Act II, `1440/depth-4..7`). Grid-breakers per chapter sampled: tilted taped chart (File 02), zig tilt cards (File 03), "bronze, loudly" circular coaster overlapping the headline and bleeding into the margin (`1440/depth-3.png`), rotated scorecards (File 05), taped ruled Sunday card (`390/depth-6.png`), tilted ticket (File 10). Verbatim question answered "objects."

**LAW 2 — DENSITY WITH DISTRIBUTION: PASS.** metrics.json: events counted by `data-mx-event` = 71; 1.95/screen at 1440, 1.45/screen at 390 — above the Season Review floor of 0.9 at both widths (above the 1.1 target band, i.e. rich, not sparse — the fail direction is sparseness; screenshots show generous whitespace, no crowding). Words/screen 204.9 (1440) and 152.9 (390), both ≤210. Distribution: `longestZeroEventRun: 1` at both widths (only the cover screen), `law2DistributionFail: false`. Side-by-side vs mockup confirms cadence visually.

**LAW 3 — LENGTH: PASS.** metrics.json `words.bodyCopy: 7472` ≥ Season Review floor 6,500. Not density-by-shortness: 36.5 screens at 1440.

**LAW 4 — ARC: PASS.** Two palette acts, each with its own ground (starfield indigo; parchment checkerboard — `1440/depth-1.png` vs `1440/depth-5.png`). Transition is a designed moment: marquee transit band (metrics event type `marquee`, "FLOODLIGHT leaving … TERRACE entering …") plus `mx-seam--out`/`mx-seam--in` opacity crossfade, not a background swap. Matches countdown's indigo→cream precedent (side-by-side above).

**LAW 5 — MOTION (tier2): PASS.** Burst frames show objects visibly mid-reveal → settled at BOTH widths: `burst/1440/burst-0.png` has the Cape Verde scorecard with its grade rows not yet ticked in and the Brito quote-object entirely absent; `burst-1.png` the quote has risen but Norway's rows are still missing; `burst-2.png` rows mid-tick; `burst-5.png` fully settled. Same sequence at 390: `burst/390/burst-0.png` (rows + quote absent) → `burst-1.png` (quote in, rows absent) → `burst-5.png` (settled, "Grade A+ / D3 + AET" rows present). Reduced-motion census: metrics `reducedMotion` = `{"1440x900": 0, "390x844": 0}` — exactly 0 as required. Motion is furniture-attached only: all 140 sampled animated selectors are plates, quote figures, ledger/table rows, stamps, cards, zig entries, seams — no running-text element animates. Signature moment present: `article#the-scorecards.mx-sig-rows-climb` with `mx-row-climb` on scorecard table rows = leaderboard rows climb into place. No scroll-jacking observed across depth captures.

**LAW 6 — OBJECT FICTION: PASS.** One kit — the tournament file/dossier — used consistently: results as fixture-ledger cards and a perforated ticket stub (`1440/depth-2.png`, `390/depth-7.png` "2026 FIFA WORLD CUP — CLOSED / FULL TIME 104/104"), team verdicts as graded scorecards (`390/depth-4.png`), awards as ink stamps (`1440/depth-5.png` "PERFORMANCE IN DEFEAT", "MATCH OF…" roundels), quotes as rule-and-panel quote-objects with mono attributions, notes as taped ruled index cards ("YOUR SUNDAYS, AS FILED", `390/depth-6.png`). Zero photographs — correct for this furniture-first football issue; the fixture ledgers, scorecards and two self-made charts carry the visual load, and none of it is a generic bordered div.

**LAW 7 — COVERS: PASS.** Poster-grade owned cover: trophy roundel + centred slab stack + yellow script arc "the biggest world cup ever played" + ghosted "26" (`1440/cover.png`). ≥3 distinct voices on the cover (script, solid slab, outline slab, mono kicker, serif masthead). Side-by-side with field-guide's "44" cover shows shared family DNA but clearly non-interchangeable compositions; equally distinct from countdown's illustrated "GREETINGS FROM" postcard cover. Dark render (`dark-1440.png`) flips chrome at token level while the accent survives — behaviour consistent with `var(--mx-accent)` theming, not a hard-coded one-off.

**LAW 8 — TYPE: PASS.** Six voices all appear: serif display (zig headlines), slab display (cover), script/marker (cover arc, chart captions "eight games, one goal conceded…"), mono smallcaps (kickers, ledger labels, quote attributions), body serif (running text), sans (card body text) — the colophon itself reads "set in six voices" (`1440/depth-7.png`). Cover uses ≥3. Mono micro-labels are comfortably legible at both widths (e.g. "CHART · THE SIGNAL, FROM FIFA MATCH RECORDS" at 1440; attribution lines at 390). Body measure is a ~600px column at 1440 (`1440/depth-3.png`), roughly 65ch — nothing near the 1,270px anti-pattern. Playfulness confined to display/furniture; body stays disciplined.

**LAW 9 — TRUST: PASS.** Named external voices rendered as quote-objects, counted in screenshots: Thomas Tuchel (`390/depth-3.png`), Pedro 'Bubista' Brito (`1440/depth-4.png` and a second, different quote at `1440/depth-7.png`), Lionel Scaloni (`1440/depth-5.png`), Kenan Yildiz (`1440/depth-6.png`) — 4 seen directly in the depth sampling; metrics `byType.quote: 11` cross-check adds Erling Haaland (y=10915) and Mauricio Pochettino (y=20960) as named quote-objects falling between capture depths. Distinct named voices ≥6 ≥ the Season Review floor of 5. No "— THE SIGNAL" self-quote appears in any screenshot or any of the 11 quote labels. No voice exceeds 2 renderings (Brito appears twice with two different quotes). Lanes respected: verdicts are argued with working shown (ESPN/FIFA/Sky/Al Jazeera citations visible in card copy); no first-person being-there claims.

**LAW 10 — CRAFT FLOOR: PASS.** metrics.json at 390×844: `horizontalScroll.flag: false` (docScrollWidth 390 = clientWidth); `chromeOverlap`: 1 fixed element, 10 depths sampled, 0 intersections; `tableTruncation.flags: []` — and visually the scorecard tables at 390 wrap cleanly with no mid-word cuts (`390/depth-4.png`). Fixed chrome is absent from all mid-scroll 390 captures (hide-on-scroll behaviour). Token-level dark mode evidenced by `dark-1440.png` (chrome and masthead flip, grounds hold). Contrast per act reads high (cream-on-indigo, near-black-on-parchment).

**LAW 11 — IDENTITY: PASS.** Full event-skin scenography as required for Season Review: scene grounds both acts, stamps, tickets, tape, marquee transit, slam/climb/settle motion — holiday-descended treatment, yet themed as its own football filing-cabinet ("FILE 01…FILE 10", "committed in ink", "Put the file away") rather than a countdown re-skin. It is itself while unmistakably the same magazine.

**LAW 12 — HONESTY: PASS.** Every claim above is anchored to a committed artifact in the pack (render-manifest + metrics generated 2026-07-20 from the same source file; burst notes state methodology). Spot-checks found no metric contradicted by the pixels: event cadence, motion, act grounds, quote objects and word volume all corroborate. No unverifiable "GREEN" claims relied upon.

---

## Verdict

Twelve of twelve laws PASS on filename-quoted visual evidence and metrics.

Caveats recorded for the ledger (non-blocking, outside this pack's scoreable scope): JS-off render and print sheet are not part of this evidence pack and were not scored; event density runs above the target band (1.95/screen at 1440), which is the safe side of Law 2.

**VERIFIER 1: PASS**
