# WP-2 PARITY SCORECARD — Deep Dive candidate (editorial skin, tier0)

Verifier inputs: `parity-candidate-dd/render/` (16 screenshots viewed: 1440 cover + depth-0..7, 390 cover + depth-0..7, dark-1440), `parity-candidate-dd/metrics.json`, frozen references (8 screenshots viewed: countdown 1440 cover/depth-2/depth-5, countdown 390 depth-2, mockup 1440 cover/depth-1/depth-3, mockup 390 depth-2), and Part-1 verbatim laws. No build context consulted.

## The three questions (from screenshots alone)

1. **"Objects on a surface, or boxes on a page?"** — Objects on a surface: taped index cards with visible shadow and tilt, ring-stamps with handwritten annotations beside them, a pinned and tilted archival map bleeding off the left edge, and a pin-headed tilted chart, all sitting on a continuously textured parchment/ash lattice ground — nothing reads as a bordered box.
2. **"Does the scroll travel, or is it one flat ground?"** — It travels: dark 1453-poster cover → cream parchment Act I → tan-gold Act II → dark-ash Act III → cream coda → dark colophon, the same lattice grain re-inked at each stop.
3. **"Would a reader who loved the trip countdown recognize this as the same magazine's craft?"** — Yes: the same masthead chrome and back pill, the same mono micro-label voice, the same stamp/taped-card/ledger furniture and ghost-display-type gestures, expressed in ink and parchment instead of starfield and moonlight.

## The Twelve Laws

### LAW 1 — SCENOGRAPHY: **PASS**
Side-by-side performed: candidate `1440/depth-2.png` + reference `countdown/1440/depth-2.png` + `mockup/1440/depth-1.png` in one message; also candidate `390/depth-2.png` + `countdown/390/depth-2.png` + `mockup/390/depth-2.png`.
- Candidate `1440/depth-2.png`: taped index card (tape shadow, slight tilt, ruled paper texture) reading "margin note · File VI / INDEX CARD · THE SIGNAL ARCHIVE"; oxblood ring-stamp "THE GREAT SIEGE 717–718 BROKEN AT THE WALLS" with handwritten annotation beside it; entire act ground is a visible diamond-lattice parchment grain, not flat color.
- Candidate `1440/depth-3.png`: archival map pinned on a rod, tilted, bleeding off the left edge; population chart card with a visible pin ball, tilted; ghost "V" numeral in `1440/depth-1.png` breaks the column and bleeds toward the right margin. Every act screen sampled (cream, tan, dark-ash) carries the lattice grain — no flat single-color act ground observed at either width.
- Visible difference vs countdown: countdown's ground is an indigo starfield with sparkle glyphs and constellation lines behind plain body text (`countdown/1440/depth-2.png`); the candidate substitutes a quieter paper lattice — the correct editorial-skin translation of the same ambient standard, and equal to the mockup's dossier-spread treatment (taped index cards on plum ground, `mockup/390/depth-2.png`).
- Ephemera carry ≥2 qualifiers each (tape+tilt+shadow on cards; pin+tilt on map/chart; rotation+ink distress on stamps). Objects, not boxes.

### LAW 2 — DENSITY WITH DISTRIBUTION: **PASS**
Side-by-side performed (same messages as Law 1; candidate `390/depth-2.png` vs `countdown/390/depth-2.png` and `mockup/390/depth-2.png` — candidate screen carries card + stamp + kicker rule; mockup screen carries two taped cards + quote-object; comparable event cadence).
metrics.json: 1440×900 — 84 events, 0.98/screen (floor 0.7 met; slightly above the 0.9 target, i.e. rich, not sparse), words/screen 215.13 ≤ 220 max, `longestZeroEventRun: 1`, `law2DistributionFail: false`. 390×844 — 84 events, 0.73/screen (within 0.7–0.9), words/screen 159.57, `longestZeroEventRun: 2` (< 3), `law2DistributionFail: false`. Event mix is varied (17 plates, 23 ephemera, 18 figures, 8 quotes, 6 ledgers, 6 statbands, 3 charts, 3 marquees). Averages AND distribution both pass at both widths.

### LAW 3 — LENGTH: **PASS**
metrics.json `words.bodyCopy: 18,429` at both widths vs Deep Dive floor 8,000 — more than double the floor. Not density-by-shortness: 85.67 screens at 1440.

### LAW 4 — ARC: **PASS**
Side-by-side performed: candidate `1440/depth-3.png` (Act II tan-gold ground) + candidate `1440/depth-5.png` (Act III dark-ash ground, gold ghost "XII") + reference `countdown/1440/depth-5.png` (cream-savannah act with taped polaroids and quote-object, post indigo-night shift) + `mockup/1440/depth-3.png` (plum act closing into gold-seam transit band "SAME KIT · MOTIF: TRANSMISSION" then cream act).
- Candidate has 3 palette acts + coda, each with its own inked ground: parchment cream (`1440/depth-1`, `depth-2`), tan-gold (`1440/depth-3`, `depth-4`), dark ash (`1440/depth-5`, `390/depth-5`), cream coda (`390/depth-6`), dark colophon (`1440/depth-7`).
- Transitions are designed moments, not background swaps: metrics lists three `div.mx-transit` marquee bands ("STONE leaving … Turn the Page … GOLD arriving", y=23514; GOLD→ASH y=48438; ASH→LIGHT y=62751) — the same transit-band furniture visible in the mockup reference.
- Difference vs countdown: countdown's arc is scenic (indigo night → cream savanna); the candidate expresses the arc in ink terms (paper-white → parchment/sepia → ash) exactly as Law 4 prescribes for editorial specials.

### LAW 5 — MOTION (tier0 print-still): **PASS**
Deep Dive is tier0: motion census 0 is correct. metrics.json `motion.animatedElements: 0` at both widths (nothing fires during scroll pass), and `reducedMotion` census is 0/0 — reduced-motion is clean. No scroll-jacking indicators; static captures at all depths render complete content.

### LAW 6 — OBJECT FICTION: **PASS**
One kit — the archive/dossier — used consistently: taped INDEX CARD objects ("INDEX CARD · THE SIGNAL ARCHIVE", `1440/depth-2.png`, `1440/depth-4.png`, `390/depth-2.png`), oxblood ring-stamps for dated facts ("THE GREAT SIEGE 717–718", "MEDIEVAL APEX 1025", "TO THE SLAVS 863"), ledgers/scorecards for data ("The Argument · the magazine's take", "Ledger · The Whole Arc, 330–1461" per metrics), pinned exhibits for figures. Quotes ship as quote-objects with named sources (metrics: Justinian I, St Basil of Caesarea, Loukas Notaras, Edward Gibbon, Judith Herrin). Even the back-matter "Meanwhile…" items (`1440/depth-7.png`) wear numbered plates + "NOTED" chips on ruled cards, not generic bordered divs. No generic box observed carrying content a kit object exists for.

### LAW 7 — COVERS: **PASS**
Side-by-side performed: candidate `1440/cover.png` + `countdown/1440/cover.png` + `mockup/1440/cover.png` in one message.
- Candidate cover owns the Deep Dive gesture: a giant ghosted "1453" numeral fills the ground behind the title stack. Poster-grade multi-voice type: gold script ("the Byzantine Empire · 330–1453"), heavy cream slab ("THE EMPIRE THAT"), outline display ("OUTLIVED"), mono caps kicker row — 4 distinct voices.
- Visible differences vs references: countdown cover is an illustrated night poster (smiling moon, castle silhouette, arc text "GREETINGS FROM", flip counter) — completely different gesture; mockup cover is a dark type-only sketch page. The three are in no way interchangeable; the three-identical-dark-covers anti-goal is not present.
- Accent reads as the issue's gold/oxblood family; `dark-1440.png` shows chrome re-theming under dark scheme, consistent with token-driven color rather than hard-coding (source inspection out of scope).

### LAW 8 — TYPE: **PASS**
Cover uses ≥3 voices (script, slab, outline, mono — see Law 7). Across the issue all six roles appear: serif body (`1440/depth-1.png`), italic serif deck ("Thirty-eight years of reach…"), display serif heads ("Justinian's Reach"), mono micro-labels ("THE WALLS, THE FLEET, AND THE FIRE"; "INDEX CARD · THE SIGNAL ARCHIVE"), handwritten annotation voice ("the siege that stopped an Arab conquest…"), typewriter card voice on index cards. Mono labels render comfortably legible at 390 (`390/depth-2.png`) — no sub-0.72rem squint labels observed. Body measure at 1440 is a ~630px column (~60–65ch), well under 68ch; no 1,270px measures.

### LAW 9 — TRUST: **PASS**
Deep Dive needs ≥5 named external voices rendered as quote-objects. metrics.json lists 8 quote-objects; named sources visible in labels: Justinian I ("Solomon, I have outdone thee"), St Basil of Caesarea, Loukas Notaras ("Better the Sultan's turban…"), Edward Gibbon ("The triumph of barbarism and religion"), Judith Herrin (×2) — ≥5 named voices, historians and primary sources counting per the law. Analysis lane shows its working ("The Argument · the magazine's take" ledger; "Two verdicts on Byzantium" scorecard opposing Gibbon vs revisionist). No "— THE SIGNAL" self-quote observed in any screenshot or metrics label; no first-person experience claims observed.

### LAW 10 — CRAFT FLOOR: **PASS**
metrics.json at 390×844: `horizontalScroll.flag: false` (docScrollWidth 390 = clientWidth, scrollLeftAfterAttempt 0; bleeding objects suppressed via overflow-x, the sanctioned technique); `chromeOverlap.fails: false` (1 fixed/sticky element, 10 depths sampled, 0 intersections — same at 1440); `tableTruncation.flags: []`. Screenshots at 390 show no mid-word truncation in ledgers/cards; figures (San Vitale mosaic, Virgin Eleousa icon at `390/depth-6.png`) are real photographic images in card frames. `dark-1440.png` renders the page under dark scheme with chrome re-themed and contrast intact — token-level dark mode responds. Contrast at rest reads AA-comfortable in every sampled act (dark ink on parchment; cream on ash).

### LAW 11 — IDENTITY: **PASS**
Editorial skin kept to paper-and-ink restraint: palette-arc in ink/parchment/sepia/ash tints (Law 4 evidence), exactly one pattern (the diamond lattice grain, re-inked per act), one cover gesture (ghost numeral), archival objects only (index cards, stamps, pinned maps, ledgers) — no theme-park scenography, no starfields, no illustration characters. Bookish gravitas intact (`1440/depth-1.png` reads like a set fine-press page). And it is emphatically not flat boxes on a page (Law 1 evidence). The skin is itself.

### LAW 12 — HONESTY: **PASS**
The gate claim ships with committed artifacts: full two-width screenshot set + dark render + render-manifest + machine metrics (`metrics.json`, generated 2026-07-19 from `tools/measure-issue.mjs`). Metrics cross-check against screenshots at every point sampled (stamp positions, card labels, act grounds, event counts) — no discrepancy between recorded evidence and what the renders actually show.

## Verdict

Twelve of twelve laws PASS.

**WP-2 PARITY: PASS**
