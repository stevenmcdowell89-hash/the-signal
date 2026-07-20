# PARITY SCORECARD — VERIFIER 2 (independent)

Candidate: event-skin Season Review, tier2 motion — `WP-7/parity-candidate-sr/` (renders of `signal_season-review_2026-07-20.html`, metrics generated 2026-07-20T07:36Z)
References: frozen packs `references/{countdown,field-guide,mockup}/render/`
Laws: `WP-2/part1-verbatim.md` (verbatim)
Protocol: screenshots + metrics only. No source HTML/CSS/JS read, no git history, no other verifier's scorecard.

Evidence volume: 22 candidate shots viewed — 1440: `cover.png`, `depth-0.png`–`depth-7.png`; 390: `cover.png`, `depth-1.png`, `depth-3.png`, `depth-5.png`, `depth-7.png`; `dark-1440.png`; burst/1440: `burst-0/1/2/5.png`; burst/390: `burst-0/2/5.png`. 7 reference shots — countdown `1440/cover.png`, `1440/depth-2.png`, `1440/depth-5.png`, `390/depth-1.png`, `390/depth-3.png`; field-guide `1440/cover.png`; mockup `1440/depth-2.png`.

---

## 1. The three verbatim questions (screenshots alone)

**"Objects on a surface, or boxes on a page?"** — Objects on a surface: every fact-block sits as rotated, taped/pinned, drop-shadowed paper on a live ground (`1440/depth-1.png` taped chart polaroid tilted over the starfield; `390/depth-3.png` tilted podium ledger; `390/depth-5.png` two rotated rubber stamps on the terrace check).

**"Does the scroll travel, or is it one flat ground?"** — It travels: a floodlit indigo starfield night (`1440/depth-1.png`, `depth-3.png`) gives way to a cream terrace-check ledger room (`1440/depth-4.png`–`depth-6.png`) and closes on a punched full-time ticket (`390/depth-7.png`).

**"Would a reader who loved the trip countdown recognize this as the same magazine's craft?"** — Yes: the same masthead chrome, the same starfield-behind-plain-body-text ambient, the same taped-polaroid chart language, and a ghost-numeral poster cover in the same register as the countdown's "GREETINGS FROM" poster — themed football, not themed differently in kind.

---

## 2. True side-by-sides (same width, same message)

**LAW 1 — candidate `1440/depth-1.png` vs reference countdown `1440/depth-2.png`.** Both: chart-on-paper ephemera (tape/gold rail, rotation, shadow, handwritten caption) floating over a starfield scene ground with plain running body text set directly on the star ground. The candidate matches the countdown's stated minimum ambient standard (countdown `390/depth-1.png` — starfield + sparkle glyphs behind body text — confirmed in the reference pack). Parity: met.

**LAW 2 — candidate `1440/depth-2.png` vs reference mockup `1440/depth-2.png`.** One screen each, same message ("dense furniture screen"). Candidate: four numbered zig scorecard entries (02/03 plates, two mono match-card stubs), all rotated with shadows. Mockup: two taped ephemera cards + quote-object + statband on one screen. Candidate density per screen meets or exceeds the reference screen. Parity: met.

**LAW 4 — candidate `1440/depth-3.png` → `1440/depth-4.png` vs reference countdown `1440/depth-2.png` → `1440/depth-5.png`.** Both pairs make the same move at the same width: indigo-night starfield act → cream daytime act (candidate: terrace check "The Ledger"; countdown: savannah). Parity: met.

**LAW 7 — candidate `1440/cover.png` vs countdown `1440/cover.png` vs field-guide `1440/cover.png`.** All three are posters; none interchangeable. Candidate: script strap "the biggest world cup ever played" + slab "ONE HUNDRED" + outline "FOUR" + ghost "26" numeral + trophy roundel. Countdown: arc "GREETINGS FROM", illustrated castle/sun-face, flip-clock. Field-guide: giant ghost "44", pink display "Efteling", outline "Beekse Bergen." Family DNA shared (ghost numeral, mixed voices, indigo ground), gestures owned per format. Parity: met.

---

## 3. The twelve laws

**LAW 1 — SCENOGRAPHY: PASS.**
Both acts carry scene grounds with visible grain: starfield + gold dust (`1440/depth-1.png`, `depth-3.png`), terrace check pattern (`1440/depth-4.png`, `390/depth-5.png`); no flat single-color act ground anywhere in 22 shots. Objects carry ≥2 treatments: taped + rotated + shadowed chart polaroid (`1440/depth-1.png`), taped ruled card (`1440/depth-6.png`), pinned fixture card + tilted coaster (`1440/depth-3.png`). Grid breaks per chapter: the "bronze, loudly" coaster overlaps the "THE TEN-GOAL GOODBYE" display headline (`1440/depth-3.png`); award stamps overlap each other (`1440/depth-4.png` metrics y=22431–22473 cluster); ticket tilts across the footer boundary (`390/depth-7.png`). Verbatim question answered "objects" above.

**LAW 2 — DENSITY WITH DISTRIBUTION: PASS.**
metrics.json: events mode `data-mx-event`, count 71. 1440×900: 1.95/screen, words 204.9/screen (≤210). 390×844: 1.45/screen, words 152.9/screen (≤210). Floor for Season Review 0.9–1.1: cleared at both widths (above target, which is the anti-sparsity direction; no fail condition attaches). Distribution: `longestZeroEventRun: 1`, `emptyScreens: [0]` (the cover screen itself), `law2DistributionFail: false` at both widths. Side-by-side in §2 confirms the numbers are real on screen.

**LAW 3 — LENGTH: PASS.**
`words.bodyCopy: 7472` at both viewports vs Season Review floor 6,500. Screenshots corroborate sustained body copy (`1440/depth-3.png`, `390/depth-7.png` closing chapters are full paragraphs, not stubs).

**LAW 4 — ARC: PASS.**
Two palette acts (within 1–3): Act I "The Tournament" (indigo starfield, metrics plate y=1473) → Act II "The Ledger" (cream terrace check, metrics plate y=15637). Transition is a designed moment, not a background swap: metrics records a `marquee` event `div.mx-transit` — "FLOODLIGHT leaving The Tournament Full Time TERRACE entering The Ledger" (y=15337, h=300) — plus `mx-seam--out`/`mx-seam--in` opacity transitions on both act sections (motion.sampled). The transit band itself falls between depth-3 (ends ~14,580) and depth-4 (starts 18,240) captures, so it is evidenced by metrics rather than a shot; the ground change it mediates is fully visible (`1440/depth-3.png` → `1440/depth-4.png`). Reference parity in §2.

**LAW 5 — MOTION (tier2, per gate operationalization): PASS.**
Burst frames show visible mid-reveal → settled at BOTH widths. 1440: `burst-0.png` — quote-object absent and Norway scorecard grade rows absent; `burst-1.png` — quote landed, rows still absent; `burst-2.png` — rows ticked in ("Grade A", "QF", "D3 + AET" rows now present); `burst-5.png` — settled, crisp, layout-stable. 390: `burst-0.png` (rows + quote absent) → `burst-2.png` (present, mid-settle) → `burst-5.png` (settled). Reduced motion: `reducedMotion.1440x900.animatedElements: 0` and `reducedMotion.390x844.animatedElements: 0`. No motion on running text: all 140 sampled animated selectors are furniture — `mx-rise-in` on headers/quotes/anchors, `mx-row-tick` on ledger/statband rows, `mx-settle-in` on cards/tickets/coasters, `mx-slam-in` on stamps, seam opacity — no paragraph/running-text selectors. Signature moment present: `#the-scorecards.mx-sig-rows-climb` with `mx-row-climb` on scorecard table rows (Season Review's "leaderboard rows climb into place").

**LAW 6 — OBJECT FICTION: PASS.**
One coherent match-day kit: perforated full-time ticket with punched holes and "FULL TIME 104/104" stamp (`390/depth-7.png`), circular rubber stamps for awards (`390/depth-5.png`, `1440/depth-4.png`), scorecards/ledgers on ruled paper (`390/depth-3.png`, burst frames), coasters (`1440/depth-3.png`), taped chart polaroids (`1440/depth-1.png`), plus universal fasteners (tape, pins). Quotes ship as bar-quote objects with mono named sources; results as scorecards/tickets; the comparison table is a tilted paper ledger. Zero generic bordered boxes observed across 22 shots. Zero photographs — CORRECT for furniture-first football; the scorecards, ledgers, charts and stamps carry the visual load.

**LAW 7 — COVERS: PASS.**
Poster-grade, owned gesture (giant trophy roundel + ghost "26" + tally headline "ONE HUNDRED & FOUR"), ≥3 voices on the cover (script, slab, outline, mono strap — four). Not interchangeable with countdown or field-guide covers (side-by-side §2). Token accent: `dark-1440.png` shows the chrome re-skinned by tokens (masthead flips to near-black, format badge re-colors) — accent behavior is token-driven, not visibly hard-coded; no code inspection performed per protocol.

**LAW 8 — TYPE: PASS.**
Six voices across the issue: Didone masthead/body serif (`390/depth-7.png` paragraphs), slab display ("ONE HUNDRED"), outline display ("FOUR"), script annotation ("the biggest world cup ever played", chart caption "eight games, one goal conceded", "bronze, loudly"), mono micro-labels ("THE PODIUM BENEATH THE CHAMPION", "FIXTURE:/DATE:/SCORE:"), sans verdict text in scorecards, plus gold condensed display ("THE TEN-GOAL GOODBYE"). Cover: 4 distinct voices. Mono labels at 390 are comfortably legible (no sub-0.72rem-looking micro-type observed). Body measure at 1440 ~68ch column (`1440/depth-3.png`), nowhere near the 1,270px anti-pattern.

**LAW 9 — TRUST: PASS.**
metrics byType `quote: 11` ≥ Season Review floor 5. Named attributions verified on-screen: Pedro 'Bubista' Brito (`1440/depth-4.png`, `1440/depth-7.png` — two different quotes, each rendered once), Thomas Tuchel (`390/depth-3.png`), Lionel Scaloni (`1440/depth-5.png`), Kenan Yildiz (`1440/depth-6.png`); metrics labels add Erling Haaland and Mauricio Pochettino — ≥6 distinct named external voices, each as a quote-object. No "— THE SIGNAL" self-quote appears among the 11 quote labels. Analysis chapters show working (ESPN sixty-year dataset, FIFA figures cited in chart caption `1440/depth-1.png`).

**LAW 10 — CRAFT FLOOR: PASS.**
390×844 metrics: `horizontalScroll.flag: false`, `scrollLeftAfterAttempt: 0` (no document-level horizontal scroll; `maxContentRightPx: 402` is clipped decorative bleed, non-scrolling); `chromeOverlap.totalIntersections: 0` across 10 sampled depths (back pill clear in every 390 shot); `tableTruncation.fails: false` — the podium ledger and scorecard rows wrap whole words (`390/depth-3.png`, `burst/390/burst-5.png`). Token-level dark mode evidenced by `dark-1440.png` (chrome and badge re-themed). Ephemera are CSS-drawn objects, no raster photos to mis-fit. Contrast: cream-on-indigo body and near-black-on-cream ledger both read comfortably AA at both widths.

**LAW 11 — IDENTITY (event skin): PASS.**
Full holiday-descended scenography as required for the event skin: poster cover, two grained scene grounds, transit marquee between acts, stamp-slams, tickets, coasters, script annotations — the same treatment family as the countdown (§1 Q3, §2 comparisons), themed to football rather than to a park. It does not read as an editorial-skin issue wearing a costume, and it does not counterfeit the countdown's park theme.

**LAW 12 — HONESTY: PASS.**
The evidence pack is complete and internally consistent: render-manifest files match what is on disk (18 depth/cover shots, dark, 12 burst frames); metrics event y-positions line up with what the depth shots show (e.g. the Brito quote at y≈18,596 sits inside the burst-depth crop at y=18,240 exactly where the frames show it landing); burst frames genuinely differ frame-to-frame (elements absent → present → settled), i.e. the motion evidence could not have been faked by re-shooting a settled page. No claim above rests on an artifact I could not open.

---

## 4. Verdict

All twelve laws PASS on quoted, filename-level evidence at both widths, in dark mode, and across the motion burst.

Noted for the record (non-blocking): the act-transition marquee band itself sits between depth captures at both widths and is evidenced via metrics (`div.mx-transit` event + seam transitions) plus the visible ground change; a future render pack should drop a depth on the transit for direct visual proof. Event density (1.95/screen at 1440) runs above the 1.1 target — above-target is not a defined fail and distribution is clean, but it is worth an editor's eye.

VERIFIER 2: PASS
