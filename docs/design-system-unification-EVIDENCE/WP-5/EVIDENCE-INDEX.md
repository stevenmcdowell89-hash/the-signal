# WP-5 MOTION — evidence pack (builder-produced; orchestrator to move into
# docs/design-system-unification-EVIDENCE/WP-5/ and independently verify)

Generated 2026-07-19 on branch claude/design-system-unification-orchestrate-fauubj.
All numbers below come from tools/measure-issue.mjs (census logic untouched).

## Motion census (animatedElements; chrome excluded)

| fixture | tier | 1440 JS-on | 390 JS-on | reduced (both) | words 1440/390 |
|---|---|---|---|---|---|
| skinned/countdown-2026-06-14-event.html | tier2 | 144 | 144 | 0 / 0 | 6380 / 6380 |
| skinned/dd-2026-06-30-editorial.html | tier0 | 46 | 46 | 0 / 0 | 18429 / 18429 |
| tier1 probe (countdown flipped to tier1, temp copy) | tier1 | 134 | 134 | 0 / 0 | 6380 / 6380 |
| negative/attempt2-flat-redress-deep-dive.html | — | 132 | 139 | 0 / 0 | 18243 / 18335 |

Animation kinds fired (1440):
- DD tier0: mx-draw-in ×33 + transform transitions ×13 (ghost parallax) — ONLY
  the two tier0-permitted moves.
- Countdown tier2: mx-rise-in ×48, mx-settle-in ×46, mx-row-tick ×34,
  mx-flip-in ×8, mx-slam-in ×4, mx-marquee-drift ×2, seam opacity ×2.
- tier1 probe: mx-rise-in ×48, mx-settle-in ×50 (stamps settle, no slam),
  mx-row-tick ×34, slow marquee ×2 — no flips, no slams, no seams.
- Flat negative: ZERO mx-* animations (only its own legacy sp-rise
  transitions + coverDrift, identical in character and magnitude to its
  committed WP-0 baseline of 137/139 — WP-5 gave it nothing). NOTE: the WP-5
  brief assumed this fixture measured 0; the committed WP-0 baseline shows it
  never did (its embedded legacy script fires micro-transitions). The
  distinguishing gate signal is unchanged: no mx motion attaches without mx
  hooks + controller.

## Files

- measure-countdown-event/metrics.json — tier2 fixture, full metrics
- measure-dd-editorial/metrics.json — tier0 fixture, full metrics
- measure-tier1-probe/metrics.json — tier1 probe copy
- measure-negative-flat/metrics.json — flat negative fixture
- jsoff-countdown.json / jsoff-dd.json — JS-on vs JS-off word-count equality
  (same exclusions as measure-issue): 6380=6380 and 18429=18429 at both
  widths; data-mx-motion-ready absent JS-off; zero elements left at opacity 0
  after the scroll pass JS-on. Produced by jsoff-wordcheck.mjs (scratchpad
  tool, uses tools/lib/mx-harness.mjs).
- render-countdown-nojs/, render-dd-nojs/ — full JS-disabled render packs
  (tools/render.mjs --no-js): every depth content-complete, no blank regions.
- render-countdown-burst/burst/ — frame-sequence evidence (tools/render.mjs
  --burst 4): 6 frames across ~2.1s after a fresh-page teleport to depth 4.
  burst-0 = polaroid mid-settle at partial opacity, neighbors still in
  stagger delay; burst-1 = cards taped down + "FOUR PARTS ONE PASS" stamp
  slammed; burst-0/1/2 md5-distinct, burst-2..5 identical (settled). Two
  differing frames = motion visibly firing (Law 5 / WP-5 gate).
- stitch-test/ — mx-path stitch smoke: minimal deep-dive mx plan stitched via
  scripts/stitch-issue.sh; output carries mx-motion.js (8,196 bytes, "JS
  injected: 8,196 bytes"), zero legacy script.js markers; live-render check
  confirmed data-mx-motion-ready stamped + mx-draw-in fired.
