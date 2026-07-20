# WP-8 — DESIGN-PARITY SCORECARD · The Signal WEEKLY (Transmission) densification

Verifier: WP-8 Design-Parity gate. No build context read; scored purely from the committed renders + metrics.
Scope: Transmission (weekly) identity is PERMANENTLY PROTECTED (Law 11). Law 1 judged as "objects not boxes" WITHIN Transmission restraint (no scene-grounds, no display fonts). Law 4 = band rhythm is the sanctioned arc. Law 7 = masthead cover is the owned gesture, compared to the shipped baseline cover. Law 5 = tier1.

Inputs:
- CANDIDATE (dense, tier1): `WP-8/parity-candidate-weekly-render/` + `WP-8/parity-candidate-weekly-metrics.json`
- IDENTITY BASELINE (shipped weekly today, the sparse "before"): `WP-8/shipped-weekly-identity-render/` + `WP-8/baseline-shipped-weekly-metrics.json`
- FROZEN REFERENCES (craft bar / distinctness): `references/{countdown,field-guide,mockup}/render/`
- Laws verbatim: `WP-2/part1-verbatim.md`

Evidence viewed — candidate (14): `1440/cover,depth-0,depth-1,depth-2,depth-3,depth-4,depth-5`, `dark-1440`, `dark-1440-touchline`, `dark-1440-ledger`, `390/depth-3,depth-5`, `burst/1440/burst-0,burst-3`. Baseline (5): `1440/cover,depth-1,depth-3,depth-5`, `390/depth-4`. References (3): `countdown/1440/cover`, `field-guide/1440/cover`, `mockup/1440/cover`. Minimums met (≥8 candidate / ≥4 baseline / ≥3 reference).

---

## 1) THE THREE VERBATIM QUESTIONS (from screenshots)

**"Objects on a surface, or boxes on a page?"**
OBJECTS — within Transmission restraint. `dark-1440-ledger.png` and `1440/depth-3.png` show a radio dial/tuner ("TUNED · 98.4 · SW19 & METLIFE"), quote-objects with a red left-rule on a tinted paper panel with a settle shadow (Zverev, Tuchel, Owen Myers), a fixtures/results ledger with hairline rules and mono day-stamps, and a ticket stub whose perforation notch is visible at `390/depth-3.png` ("ALL ENGLAND CLUB"). These are printed objects in the weekly's own cream paper and blue/red ink — not the plain bordered `<div>` the baseline shipped (`shipped .../1440/depth-3.png` renders "A final still to be played" as a flat box).

**"Does the scroll travel (band rhythm + density)?"**
YES. Red waveform seams divide bands (`1440/depth-1.png`, `dark-1440-touchline.png`: BAND 05 → BAND 06 across a red waveform), Roman band numerals (II The Long Read, III The Rounds), and events land steadily — 32 designed events, longest zero-event run of 1 screen @1440. Not one flat undesigned column.

**"Is this unmistakably the same Transmission weekly, only denser?"**
YES. Cream paper, "The Signal" serif masthead with the red italic, waveform/radio conceit (now furniture: the tuning dial), ~800px printed-object chassis, blue/red ink, mono FM labels — all intact and identical to the shipped cover. The added furniture raised density from 0.35 → 0.86 ev/screen without importing any foreign skin.

---

## 2) SIDE-BY-SIDE — candidate vs SHIPPED BASELINE (same width, same message)

| Aspect | SHIPPED baseline (before) | CANDIDATE (after) | Visible difference |
|---|---|---|---|
| Cover (`1440/cover.png`) | The Signal serif + red italic, waveform, station list, cream | **Pixel-identical** | Same identity — Law 7/11 hold |
| Events @1440 | 11 (all `figure`) · 0.35/screen | 32 (figure/ledger/quote/chart/statband/ephemera) · 0.86/screen | +21 designed objects; density target reached |
| Distribution @1440 | longest zero-event run **8** · `law2DistributionFail: true` | longest run **1** · `false` | Empty stretches eliminated |
| Interior (`depth-3`) | "A final still to be played" = flat bordered box; body-only screens | Same content + dial, quote-objects, fixtures ledger, Release Radar rail | Boxes → furniture; column → scored spread |
| Body words | 7,300 | 7,763 | Denser AND slightly longer — not density-by-shortening |
| Craft @390 | chromeOverlap `fails: true` (back pill over content, 6 pairs) | chromeOverlap `fails: false` | Candidate FIXED the shipped overlap defect |

Baseline is unmistakably the sparse "before"; candidate is the dense "after" — same paper, masthead, type, chassis, ink.

---

## 3) THE TWELVE LAWS — PASS/FAIL

**LAW 1 — Scenography (objects, Transmission restraint) · PASS.** Dial/tuner, quote-objects (red rule + tinted panel + settle), fixtures ledger, ticket stub w/ perforation (`390/depth-3.png`), scorecard, chart card, Release Radar rail — printed objects in the weekly's own paper/ink. Critically NO event-skin grounds (no starfield/gradient/pattern), so no Law-11 breach. Contrast baseline's flat box (`shipped/1440/depth-3.png`).

**LAW 2 — Density with distribution · PASS.** Candidate @1440: 0.86 ev/screen (within 0.8–1.0), 32 events, `law2DistributionFail: false`, longest zero run 1. @390: distribution passes (longest run 2); per-screen 0.54 is the expected dilution across ~60 tall screens, not a hole. Baseline was 0.35 @1440 with an 8-screen dead run (fail). Budget met, distribution clean both widths.

**LAW 3 — Length floor (weekly 6,000) · PASS.** Candidate body copy 7,763 words — comfortably above floor. Density is not bought by shortening.

**LAW 4 — Arc (weekly = band rhythm) · PASS.** Bands 01/05/06/09/10 with designed red-waveform seams between them (`depth-1`, `dark-touchline`) — the sanctioned weekly arc, not a background-color swap. No palette acts demanded of the weekly.

**LAW 5 — Motion tier1, verified · PASS.** Metrics: 20 animated elements firing during scroll (`mx-dial-sweep`, `mx-row-tick`, `mx-chart-draw`, `mx-rise-in`, `mx-settle-in`); `reducedMotion` = 0 at both widths. Burst frames show it visibly: the Tuchel quote-object is greyed/mid-rise in `burst-0.png` and settled to full ink by `burst-3.png`. Signature = dial-needle sweep on band entry, present. Not the zero-motion failure of prior attempts.

**LAW 6 — Object fiction · PASS.** Quotes ship as quote-objects with named sources; results as fixtures ledger / scorecard / ticket; data as chart card and stat bands ("DATUMS OF THE WEEK", "ISSUE IN NUMBERS"). Facts wear the kit, not generic boxes.

**LAW 7 — Cover (owned, same identity) · PASS.** Candidate cover is identical to the shipped baseline cover — same serif+red-italic masthead, waveform, station list, cream. Accent reads as the weekly's red ink. Not interchangeable with countdown or field-guide covers.

**LAW 8 — Type, six voices · PASS.** Serif display headline, red Newsreader italic, blue standfirst, disciplined single-column serif body (≤68ch inside the 800px chassis), mono micro-labels at readable size (STATION LIST, BAND 05, FM freqs). Type stack held to Instrument Serif / Newsreader / JetBrains Mono — no display fonts.

**LAW 9 — Trust, ≥4 named external voices · PASS.** Alexander Zverev, Thomas Tuchel, Owen Myers (The Guardian), Jannik Sinner, plus a named Heartstopper critic — each rendered as a quote-object (metrics list 5 quote events). No first-person experiential claims; no self-quote padding.

**LAW 10 — Craft floor · PASS.** Metrics both widths: horizontal-scroll flag false; `chromeOverlap.fails: false`; `tableTruncation.fails: false`; real `<img>` figures; token-level dark mode confirmed (`dark-1440.png` renders full identity on near-black paper); cream/ink AA per band. Candidate repairs the baseline's 390 pill-overlap defect.

**LAW 11 — Identity (three skins, each itself) · PASS — headline law.** Unmistakably Transmission: cream paper, serif masthead + red italic, waveform/radio conceit as dial furniture, ~800px chassis, blue/red ink, mono FM labels. NO scene-grounds, NO display fonts, NO loud grounds anywhere in the 14 shots. Cannot be confused with the countdown (navy starfield + sun illustration + giant sans) or the field-guide (navy dot-field + giant sans + ghosted "44"). Densified via core furniture through the alias block, exactly as Law 11 requires of the upgraded weekly.

**LAW 12 — Honesty · PASS.** Every claim above is anchored to committed render files and the two metrics JSONs; no unbacked assertions.

**Score: 12 / 12 PASS.**

---

## HEADLINE ANSWER

**Yes — this is unmistakably the same Transmission weekly (same cream paper, "The Signal" serif + red-italic masthead, waveform/radio conceit, ~800px printed-object chassis, blue/red ink), only denser: designed events rose from 0.35 to 0.86 per screen and the 8-screen dead run is gone, with no scene-grounds, display fonts, or foreign skin anywhere.**

**WP-8 PARITY: PASS**
