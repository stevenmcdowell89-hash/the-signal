# Negative Fixtures — WP-0 gate calibration

These are **deliberately bad** artifacts. Their sole job is to make the
mechanical gate suite prove it can FAIL. A gate that has never failed anything
is unproven and its PASSes do not count (SPEC Part 6 §4, F-19).

Each fixture renders **offline** (inline minimal CSS, no external fonts/deps).
The one deliberate exception is `flat-redress-deepdive.html`, which carries a
single dead external hotlink (`https://example.invalid/dead.jpg`) so the F-16
external-src image check has something to fail on.

Every fixture is `data-mx` (carries `data-skin` + `--mx-*`), so the Law-3 word
floor and Law-9 voice minimum apply — exactly the surface attempt #2 gamed.

## Fixture → gate(s) it MUST fail → expected verdict

| Fixture | Format | Targeted gate(s) it must FAIL | Tool | Expected verdict |
|---|---|---|---|---|
| `stub-season-review.html` | season-review (~528 words) | Law-3 word floor (6500); Law-9 voices=0; TRUE low density | `validate-issue.py` + `measure-issue.mjs` | `length-floor` FAIL · `voice-minimums` FAIL · **0 ev/screen** (not a gamed high number) |
| `flat-boxes-season-review.html` | season-review (~6931 words) | Density (flat divs are not Law-2 events); Law-9 voices=0 | `measure-issue.mjs` + `validate-issue.py` | **0 ev/screen**, zero-event run 19 (desktop)/33 (mobile) screens · `voice-minimums` FAIL · **`length-floor` PASSES** (failure isolated to flatness/density/voices) |
| `rewind-scaffold-tokens.html` | rewind | Scaffold/strategy grep (F-14) | `validate-issue.py` | `scaffold-tokens` FAIL on `#[N]`, `[N]`, `ch2-1`, `viz_3`, "research bundle", "furniture-first" |
| `flat-redress-deepdive.html` | deep-dive | Density (flat upright boxes); F-16 dead external hotlink | `measure-issue.mjs` + `validate-issue.py` | **0.28/0.16 ev/screen** · `image-urls` FAIL on `https://example.invalid/dead.jpg` |

**On "isolated" (flat-boxes):** this means only that the flat-boxes fixture
**clears the 6500-word floor** (unlike the stub), so its density/voices failure
is demonstrated *independently of* the length gate. It is NOT the only check it
fails: being an offline stub with zero components, every fixture also (correctly)
trips `back-link` (no injected archive marker) and `special-variety` (0 component
types). Those are additional TRUE failures, not false positives — they do not
weaken the targeted gate's fail-provenance. The independent WP-0 gate verifier
confirmed each targeted gate above fires as its own distinct FAIL.

## The rule

**If any fixture ever PASSES its targeted gate, the gate has regressed** (SPEC
Part 6 §4). Stop: all PASSes since that gate's last calibration are void, and
the gate must be repaired before any further gate claim is trusted.

## Measured baseline (for contrast)

The known-good reference `issues/signal_countdown_2026-06-14.html` measures
**2.11 ev/screen** desktop (see `../wp-0/calibration/countdown.metrics.json`).
The flat/stub fixtures read **0–0.28 ev/screen** — the tool sees the difference.

## Re-run commands

```
# mechanical validator (per fixture)
python3 .claude/skills/the-signal/scripts/validate-issue.py \
    docs/design-system-unification-EVIDENCE/negative-fixtures/<fixture>.html --skip-image-urls

# F-16 needs the network path (drop --skip-image-urls):
python3 .claude/skills/the-signal/scripts/validate-issue.py \
    docs/design-system-unification-EVIDENCE/negative-fixtures/flat-redress-deepdive.html

# density / distribution / motion census
node tools/measure-issue.mjs . \
    /docs/design-system-unification-EVIDENCE/negative-fixtures/<fixture>.html /tmp/out.json
```
