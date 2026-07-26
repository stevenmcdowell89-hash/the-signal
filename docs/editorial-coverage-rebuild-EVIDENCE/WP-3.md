# WP-3 — Structure of record + stitcher + CSS

**Status: DONE.** Defects A, C, D structurally addressed; B/E partially (see § What WP-4 must catch).
SPEC §3.4 markup emitted exactly as written. `verify-weekly-golden.sh` **passes, exit 0**, after a
deliberate regeneration of the mx golden snapshot (§ Golden parity).

---

## Files touched

| File | Owner | Change |
|---|---|---|
| `.claude/skills/the-signal/scripts/stitch_weekly.py` | WP-3 | +397/−~10 — vintage, cover lead, figure provenance |
| `.claude/skills/the-signal/references/format-skeletons/weekly.json` | WP-3 | +42/−12 — Touchline restructure, hooks, invariant |
| `.claude/skills/the-signal/assets/css/weekly/01-coverage-rebuild.css` | WP-3 | **new**, 50 lines / 2.3 KB |
| `.claude/skills/the-signal/assets/css/weekly-mx/11-mx-coverage-rebuild.css` | WP-3 | **new**, 119 lines / 5.5 KB |
| `.claude/skills/the-signal/references/golden/weekly-mx/expected.html` | **unowned** | regenerated — see § Golden parity |

```
$ git diff --stat 6325658 -- .../scripts/stitch_weekly.py .../format-skeletons/weekly.json .../assets/css .../references/golden
 .../css/weekly-mx/11-mx-coverage-rebuild.css       | 119 ++++++
 .../assets/css/weekly/01-coverage-rebuild.css      |  50 +++
 .../references/format-skeletons/weekly.json        |  42 ++-
 .../references/golden/weekly-mx/expected.html      | 193 +++++++++-
 .claude/skills/the-signal/scripts/stitch_weekly.py | 397 ++++++++++++++++++++-
 5 files changed, 773 insertions(+), 28 deletions(-)
```

Nothing else. `issues/signal_weekly_2026-07-26.html` (#18) untouched, per SPEC §1.3.

---

## 1 · Long Read vintage (defect A) — SPEC §3.4

`stitch_weekly.py` emits `data-vintage="news"|"evergreen"` on the long-read `<section>` from the
plan's `long_read.vintage`, **always present**.

**The SPEC's premise about the `.lr-title` block is wrong for this repo, and it matters.** The brief
says "writers never emit band-heads or the `.lr-title` block". Writers *do* emit `.lr-title` — see
`references/golden/weekly/chapters/long_read.html:1-6` and `weekly-mx/chapters/long_read.html:1-6`,
both of which open with `<div class="lr-title">` including the `.byline`. The stitcher owns the
`<section>` wrapper, the band-head and the movement dividers around it, not the title block.

Rather than move `.lr-title` generation into the stitcher (which would have required editing both
goldens' writer content — unowned files — and would have thrown away writer control of the headline
and standfirst), the stitcher **normalises** the block: `apply_long_read_vintage()` inserts the
`.lr-vintage` line before the `<h2>` and rewrites the `.byline`. The rendered result is identical to
the contract, and the vintage decisions stay un-contradictable by the writer. Recorded here as a SPEC
prose correction, not a contract change — **no attribute, class or value differs from §3.4.**

### Rendered output — evergreen (byte-for-byte §3.4)

```html
<section class="longread" data-role="long-read" data-vintage="evergreen">
    <div class="lr-title">
      <div class="mono" style="color:var(--signal);">SEVEN LEADERS, NO ELECTION</div>
      <div class="mono lr-vintage">NOT THIS WEEK · A STANDING STORY · 1901–2021 · LATEST DEVELOPMENT MAR 2021</div>
      <h2>How Britain hands over <em>power</em></h2>
      <p class="stand">On Monday, Andy Burnham is expected to walk into Downing Street…</p>
      <p class="mono byline">BY THE EDITOR · THE LONG READ · A STANDING STORY</p>
    </div>
```

### Rendered output — news (no `.lr-vintage`, byline keeps the date)

```html
<section class="longread" data-role="long-read" data-vintage="news">
    <div class="lr-title">
      <div class="mono" style="color:var(--signal);">SEVEN LEADERS, NO ELECTION</div>
      <h2>How Britain hands over <em>power</em></h2>
      <p class="stand">On Monday, Andy Burnham is expected to walk into Downing Street…</p>
      <p class="mono byline">BY THE EDITOR · THE LONG READ · 19 JUL 2026</p>
    </div>
```

### Byline normalisation — unit cases (real output)

```
$ python3 /tmp/bl.py
  evergreen date-stripped    -> BY THE EDITOR · THE LONG READ · A STANDING STORY
  evergreen long month       -> BY THE EDITOR · THE LONG READ · A STANDING STORY
  evergreen already framed   -> BY THE EDITOR · A STANDING STORY
  news date absent           -> BY THE EDITOR · THE LONG READ · 19 JUL 2026
  news WRONG date            -> BY THE EDITOR · THE LONG READ · 19 JUL 2026
  news correct date          -> BY THE EDITOR · THE LONG READ · 19 JUL 2026
  news unpadded day          -> BY THE EDITOR · THE LONG READ · 19 JUL 2026
  idempotent re-stamp: True | lr-vintage occurrences: 1
  evergreen->news drops .lr-vintage: True | byline: BY THE EDITOR · 19 JUL 2026
  month_year: [('2021-03', 'MAR 2021'), ('2021-12', 'DEC 2021'), ('2021-13', None), ('2021-3', None), ('', None)]
```

Normalisation is **total in both directions**: an evergreen byline can never carry a date, and a news
byline can never carry `A STANDING STORY`. Date matching tolerates zero-padding and month-name length
(`5 July 2026` == `05 JUL 2026`), so a correct writer date is left byte-identical — which is why both
goldens' bylines are unchanged.

### Fail-fast cases (real output)

```
$ … --plan plan-badvintage.json     # long_read.vintage = "ancient"
  exit=1 :: long_read.vintage='ancient' is not one of ['news', 'evergreen'] (SPEC §3.1).
$ … --plan plan-badleads.json       # issue_meta.cover_leads_on = "sport"
  exit=1 :: issue_meta.cover_leads_on='sport' is not one of ['news', 'long_read'] (SPEC §3.1).
$ … --plan plan-badeg.json          # evergreen, material_span/latest_development removed
  exit=1 :: The long_read chapter declares vintage='evergreen' but the plan is missing a usable
            material_span / latest_development …
```

**A missing `vintage` defaults to `news` with a loud warning, it does not die.** Deliberate: `news` is
the status-quo rendering (dated byline, no vintage line), so the default is a no-op rather than a
fabrication; acceptance criterion #1 assigns rejection-on-absence to **WP-5's plan validator**; and
dying would make the stitcher unable to render either golden fixture. Same reasoning for
`cover_leads_on`. Both warn on stdout every run:

```
  ! long_read.vintage absent — defaulting to "news" (the status-quo rendering: dated byline, no
    .lr-vintage). SPEC §3.1 requires it; validate-chapter-plan.py (WP-5) is the gate.
```

### CSS — `.lr-vintage`

`assets/css/weekly/01-coverage-rebuild.css` (weekly **core**, so it styles with or without the mx
layer). Per `references/spec/weekly.md` § The Transmission identity: mono is the shared `.mono` rule
(JetBrains Mono, uppercase, .16em) and the new rule only adds colour, tracking and spacing. Set as a
**ruled mono band** — the same "stamped on the paper" gesture as `.bandhead`, so it reads as furniture
rather than as a sentence the Editor wrote. **Signal-blue, not vermilion**, because vermilion is the
one accent and the kicker immediately above already spends it (§ Accent lockdown).

Audit of both new stylesheets:

```
01-coverage-rebuild.css: braces 8/8 balanced=True
   hex/rgb literals: none
   font-family decls: 0
   tokens used: ['--blue', '--hair']
   sp-/hol- classes: none
11-mx-coverage-rebuild.css: braces 26/26 balanced=True
   hex/rgb literals: none
   font-family decls: 0
   tokens used: ['--mx-accent', '--mx-accent-2', '--mx-card-ink', '--mx-hair', '--mx-ink', '--mx-ink-soft', '--mx-support-1']
   sp-/hol- classes: none
```

No new font, no new colour, no new token — so the warm-night dark variant at the foot of
`00-transmission.css` keeps working with nothing restated.

---

## 2 · Figure provenance (defects B, E) — SPEC §3.4

### Where this can actually be enforced

`.plate-img` markup is authored by the **writer**, inside band content. The stitcher never generates
it. So the four attributes cannot simply be "emitted". But they are a machine record of the **asset**,
not of the prose — and WP-8 now writes exactly that record to `assets/cached/manifest.json` (SPEC
§3.10), keyed by the `sha256(url)[:12]` that `mirror-images.py` already uses as the cached filename.
The writer's `<img src="/assets/cached/<hash>.jpg">` therefore **joins straight onto it**.

So the stitcher does real work, not just validation: `stamp_figure_provenance()` looks the hash up and
stamps `data-shows` / `data-capture-year` / `data-licence` / `data-allows-derivatives` onto the
`.plate-img`. Writers never hand-copy licence codes into markup.

- **Writer-authored attributes always win** — an explicit authorial claim is never overwritten.
- The `shows` enum is loaded from `references/image-source-types.json` § `shows` (WP-6's canonical
  home; 11 values confirmed loaded), with the SPEC §3.3 literal as fallback so there is no hard
  dependency on another WP's file.

### Rendered output (fixture manifest carrying real values)

```html
<div data-mx-event="figure" class="plate-img lead" style="margin-top:18px;" data-shows="diagram" data-capture-year="" data-licence="CC0" data-allows-derivatives="true">
<div data-mx-event="figure" class="plate-img" data-shows="artefact" data-capture-year="2024" data-licence="CC-BY-3.0" data-allows-derivatives="true">
<div data-mx-event="figure" class="plate-img lead" data-shows="event_photo" data-capture-year="2026" data-licence="CC-BY-ND-4.0" data-allows-derivatives="false">
```

Matches §3.4's shape and attribute order. Note row 2: the manifest said `shows: "portrait"`, the
writer had hand-written `data-shows="artefact"`, and the writer's value survived. Note row 1:
`capture_year: null` renders `data-capture-year=""` (the legal synthetic-diagram/chart rendering, and
what §3.9 reads as "no year to compare").

### A placeholder is not a record — a bug caught during verification

The live manifest has **438 entries and every one is an honest back-fill**: WP-8 could not recover the
source URLs of already-published assets (sha256 is one-way), so it wrote
`shows: "UNKNOWN"`, `capture_year: "UNKNOWN"`, `licence.code: "UNKNOWN"`, `allows_derivatives: null`.

My first implementation stamped those straight through, producing
`data-shows="UNKNOWN" data-capture-year="UNKNOWN" data-licence="UNKNOWN" data-allows-derivatives="false"`
on 14 of 14 figures. That is three lies and one fabrication: `UNKNOWN` is not in the `shows` enum,
`data-capture-year="UNKNOWN"` is not a year that §3.9 can compare, and
`data-allows-derivatives="false"` asserts a licence finding derived from a JSON `null`.

Fixed: each field is stamped **only when the manifest holds a real value** — `shows` must be in the
11-value enum; `capture_year` must be an integer year in 1500–2100 or an explicit JSON `null`;
`licence.code` must be non-empty and not `UNKNOWN`; `allows_derivatives` must be an actual boolean.
Otherwise the attribute stays **absent** and the figure is reported as a gap, which is what lets WP-4
fail it. Verified both ways:

```
### A. fixture manifest with REAL values ###
  Fig provenance: 3/14 complete (3 stamped from the manifest: 3 asset[s])
### B. the REAL repo manifest (438 UNKNOWN back-fills) — must stamp NOTHING ###
  Fig provenance: 0/14 complete (0 stamped from the manifest: 438 asset[s])
UNKNOWN stamped into HTML? -> 0 occurrence(s)
data-allows-derivatives asserted? -> 0 occurrence(s)
```

### Honest reporting + an opt-in hard gate

Every run prints a per-figure gap report naming the `src` and the missing keys, and a summary line
(`Fig provenance: N/M complete`). `--strict-figure-provenance` turns it fatal:

```
$ … --strict-figure-provenance ; echo exit=$?
  exit=1
═══ WEEKLY STITCH FAILED ═══
14 of 14 .plate-img figure[s] are short of the SPEC §3.4 provenance record …
```

Default is report-and-continue, because `validate-issue.py` is the ship gate (SPEC §0: no fourth
gate) and both goldens would otherwise be unbuildable.

---

## 3 · Touchline restructure (defect D) — SPEC §3.11

In `weekly.json`:

- **`touchline.target_words` 350–600 → `{min: 500, max: 800}`**, with a `note` recording *why*, in the
  SPEC's own terms: five furniture objects in ≤600 words is what forced single-competition coverage;
  **this raises prose, it does not cut furniture**; density is events-per-screen. `band_slots.touchline`
  still lists all five objects — nothing was removed to compensate.
- **`fixtures_ledger` → `results_ledger`** (key renamed; verified no script, shell or JSON outside
  `weekly.json` keyed on the old name). Now results-of-record: events that **concluded** since
  `issue_meta.window.from`, one row per event, `data-role="results-ledger"`, `data-sport` on every row.
- **`fixtures_lookahead`** added as the other half of the split, slotted into `on_the_radar`. Documented
  as *not* the results ledger and explicitly barred from carrying `data-role="results-ledger"` — I did
  **not** invent a new `data-role` value, since §3.4 does not define one.
- **`standings_card` → polymorphic**, `data-table-kind` ∈ `league` · `medal` · `gc` · `leaderboard` ·
  `championship`, each with CSS (below).
- **`dial_signature` → optional**: "Optional but recommended in The Touchline" replaced with
  "OPTIONAL, and RETARGETABLE to whatever leads the band", with the reason — a standing recommendation
  on a single-competition dial is part of what let one sport saturate the band.
- **New invariant `results_ledger_multi_sport`** in `invariants`, with the "tracked sport" definition
  spelled out *including* WP-1's absent-key correction (an absent `interest_depth` key is **unset**,
  never `off`).

### CSS for the five table kinds

`assets/css/weekly-mx/11-mx-coverage-rebuild.css` (mx layer, because `.mx-scorecard`'s base is there
and reads the `--mx-*` alias). Shared: `font-variant-numeric: tabular-nums` on every kind, plus a
`th` head-row style — a medal table needs G/S/B heads, a league table does not.

| kind | shape | treatment |
|---|---|---|
| `league` | position · club · points | last cell right-aligned, bold, no-wrap |
| `championship` | rank · driver · points | same, **plus a rule after third** — a season table's story is the podium |
| `medal` | rank · nation · G · S · B (· total) | every cell from the 3rd is a 30px right-aligned count; gold takes the accent, silver/bronze go quiet |
| `gc` | rank · rider · time gap | mono tracking, never wraps mid-time, leader in accent |
| `leaderboard` | position · player · score to par | as `gc`, plus `tr.is-cut` for a cut line |

The single-gap-column card was the *reason* only a weekly-table sport could fill the Touchline: a
medal table, a general classification and a golf board were literally unrenderable.

### Sport tokens (coordinator amendment, folded in mid-task)

The SPEC gained *"Sport tokens — one vocabulary, and `multi_sport` is not a result"* while this WP was
in flight. Handled by correcting three places in `weekly.json` — `structural_hooks.results_ledger`,
`furniture_layer.components.results_ledger`, and `invariants.results_ledger_multi_sport` — so all
three now state:

- `data-sport` takes a **specific sport token** from the canonical 22 in
  `references/spec/data-contracts.md` § Sport tokens (lowercase snake_case, the **sport** not the
  competition);
- `data-sport="multi_sport"` is **forbidden** in rendered HTML and hard-failed by WP-4, legal only in
  `state.sports_calendar[].sport` where it classifies an *event*;
- a multi-sport games contributes **one row per sport** (a Games swimming final is
  `data-sport="swimming"`, a Games 10,000m is `data-sport="athletics"`), never one row for the games;
- a token outside the 22 **warns**, it does not fail — the Games long tail must not block a ship.

The invariant text now says distinctness is counted **over specific tokens only**, and gives the
one-line reason: `[motorsport, multi_sport]` would satisfy "≥2 distinct" while delivering none of the
breadth the invariant exists to force. **No fixture or worked example anywhere in my files emits
`multi_sport`** — verified on the rendered issue: `distinct data-sport tokens: ['football', 'tennis']
· multi_sport present: False`. The CSS selector is `[data-sport]`, value-agnostic, so it needed no
change.

---

## 4 · Cover leads on the Long Read (defect C) — SPEC §3.1

How the cover is built today: `render_cover()` takes copy from `plan["cover"]`
(`eyebrow`, `lead_head`/`lead_head_html`, `standfirst`, `tagline`), and the tuner station list is
assembled from the per-chapter `nav_coverline`/`nav_coverline_html`, `nav_freq`, `nav_on` fields of
every `nav: true` band present, **in skeleton order**.

`issue_meta.cover_leads_on` now drives three things:

1. `data-cover-leads-on="news|long_read"` on `<header class="cover">`.
2. On `long_read`, the long_read station is **hoisted to the top of the tuner and forced `on`**, so
   the station list leads with the Long Read instead of following skeleton order.
3. The `.lead__eyebrow` **default** becomes `BAND 01 — THE LEAD TRANSMISSION · THE LONG READ`.

The cover **copy stays the planner's** — an explicit `cover.eyebrow` always wins and the stitcher
never touches `lead_head`/`standfirst`. Writing editorial wording is not the stitcher's job.

If `cover_leads_on == "long_read"` but the plan gives the long_read chapter no coverline, the stitch
**dies** — the cover cannot lead on a station that does not exist.

### Rendered output (fixture where The Letter also carries a coverline, so the hoist is visible)

```
===== hoist-control (cover_leads_on: news) =====
<header class="cover" data-cover-leads-on="news">
<div class="mono lead__eyebrow">BAND 01 — THE LEAD TRANSMISSION</div>
station order: [(' on','the_letter'), (' on','long_read'), ('','touchline'), (' on','pixel_byte')]

===== hoist-demo (cover_leads_on: long_read) =====
<header class="cover" data-cover-leads-on="long_read">
<div class="mono lead__eyebrow">BAND 01 — THE LEAD TRANSMISSION · THE LONG READ</div>
station order: [(' on','long_read'), (' on','the_letter'), ('','touchline'), (' on','pixel_byte')]
```

### A live check I broke and fixed: `data-nav-band`, not `data-station-band`

Each station also carries the band id so the ordering is auditable. My first name was
`data-station-band` — which **broke `validate-issue.py`**. Its navigator tally is
`re.findall(r'\bdata-station\b', clean)`, and `-` is a regex word boundary, so `data-station-band`
matches it too: every station counted twice and a 7-station issue failed
`[FAIL] weekly-structure/nav-count: 14 navigator stations; target <=13`.

Renamed to **`data-nav-band`**. Verified fixed (`[PASS] weekly-structure/nav-count: 7 navigator
stations (4-13)`), the reason recorded in a code comment and in
`weekly.json § structural_hooks.cover_leads_on` so it is not re-introduced. Audited for any other
collision: the only two `\b`-delimited attribute tallies in `validate-issue.py` are
`\bdata-desk-column\b` and `\bdata-station\b`, and nothing I emit is a prefix of either.

**Worth flagging as a process note:** I initially mis-diagnosed this as pre-existing, because I tried
to establish a baseline with `git stash` — and the orchestrator had already snapshot-committed my
stitcher, so the stash was empty and the "baseline" run still contained my bug. Mid-flight WIP commits
make `git stash` an unreliable way to get a pre-WP baseline.

`data-cover-leads-on` and `data-nav-band` are **WP-3 additions beyond §3.4's list**, added so the
cover-lead decision is auditable in the rendered object. Both are additive and inert to any check that
ignores them; both are documented in `weekly.json § structural_hooks`.

---

## 5 · Demoted-lead ledger + resolved loops — SPEC §3.4

**Structure.** New component `demoted_lead_ledger` (`.mx-ledger[data-role="demoted-lead"]`), wired
into `band_slots.the_threads` — The Threads is the continuity band inside THE CLOSE. `data-resolves-loop`
is an attribute, not a component, so it is documented under `structural_hooks.resolves_loop`.

**CSS.** `data-role="demoted-lead"`: the demotion has to be *visible*, and the way this identity says
"no longer the loudest thing here" is to **withdraw the accent** — light top rule, pencil-grey caption
and date, signal-blue result column instead of vermilion. Vermilion belongs to what leads.

`data-resolves-loop`: a blue spine (`box-shadow: inset 2px 0 0`) marking a carried-forward result being
**closed**. Implemented in *both* layers with the same gesture — core weekly for `.items > li`,
`.digest > li`, `.threads`, `.score`, and mx for `.mx-ledger__row` — so a closure reads identically
wherever it lands.

### Rendered output

```html
<div class="mx-ledger" data-mx-event="ledger" data-role="results-ledger">
      <div class="mx-ledger__caption">Results of Record · Since the Cut</div>
      <div class="mx-ledger__row" data-sport="football" data-resolves-loop="loop_2026-07-18_wc-third-place">…</div>
      <div class="mx-ledger__row" data-sport="tennis">…</div>
      <div class="mx-ledger__row" data-sport="tennis">…</div>
    </div>

<div class="mx-scorecard" data-mx-event="ledger" data-table-kind="championship">

<div class="mx-ledger" data-mx-event="ledger" data-role="demoted-lead">
      <div class="mx-ledger__caption">Off the Cover &middot; Still Running</div>
      <div class="mx-ledger__row">…<span class="mx-ledger__result">HOLDING</span>…</div>
    </div>
```

The ledger rows reuse the mx golden's **own real results** with only the contract attributes added —
no result, score or fixture was invented for a fixture.

---

## The new CSS is injected into a rendered issue

Not merely present on disk. Extracted from the `<style>` block of a stitched issue:

```
injected <style> = 55.5 KB
  OK   .lr-title .lr-vintage{
  OK   .lr-title .lr-vintage + h2{
  OK   .items > li[data-resolves-loop]
  OK   .score[data-resolves-loop]
  OK   .mx-ledger[data-role="results-ledger"] .mx-ledger__row[data-sport]
  OK   .mx-ledger[data-role="demoted-lead"] {
  OK   .mx-ledger__row[data-resolves-loop] {
  OK   .mx-scorecard[data-table-kind] td,
  OK   .mx-scorecard[data-table-kind="league"] td:last-child
  OK   .mx-scorecard[data-table-kind="medal"] td:nth-child(n + 3),
  OK   .mx-scorecard[data-table-kind="gc"] .mx-scorecard__gap,
  OK   .mx-scorecard[data-table-kind="leaderboard"] tr.is-cut td
  OK   .mx-scorecard[data-table-kind="championship"] td:last-child
```

And the stitcher's own accounting confirms both files are in the bundle:
`CSS: 55.5 KB (5 file[s])` = `weekly/00-transmission` 25.3 + `weekly/01-coverage-rebuild` 2.3 +
`skins/skin-transmission` 2.2 + `weekly-mx/10-mx-weekly` 20.2 + `weekly-mx/11-mx-coverage-rebuild` 5.5.

```
pre-WP-3 mx bundle: 47.7 KB   post-WP-3: 55.5 KB   (+7.8 KB)
```

**Budget note.** My first draft of the two stylesheets was 12.0 KB, most of it comment prose. The
bundle is *inlined into every issue*, so comments are delivered bytes on a target already overrun
(`css_target_kb: 40`). I cut it to 7.8 KB by moving the long rationale into `weekly.json` (which is
never shipped) and into this file, keeping short pointed comments in the CSS.
`furniture_layer.budget.note` is updated with the real measured per-file breakdown.

**Not verified:** nothing was rendered in a browser. Injection, selector presence, brace balance,
token-only colours and zero `font-family` declarations are all machine-checked above; visual
correctness of the five table variants is not.

---

## Golden parity — decision and justification

**Decision: `references/golden/weekly-mx/expected.html` regenerated. `verify-weekly-golden.sh` passes,
exit 0.**

Byte drift was unavoidable — the CSS bundle is inlined into the output, so *any* stylesheet change
breaks the snapshot. So the question was only whether the drift is exactly what I intended. Diffed
with the `<style>` block masked, before regenerating:

```
CSS: expected 48805B -> new 56738B (+7933)
non-CSS changed lines: 22
-  <header class="cover">
+  <header class="cover" data-cover-leads-on="news">
-        <div class="station on" data-station>
+        <div class="station on" data-station data-nav-band="long_read">
   … ×9 stations …
-  <section class="longread" data-role="long-read">
+  <section class="longread" data-role="long-read" data-vintage="news">
```

Exactly three intended changes and nothing else: the cover declaration, the nine station band ids, the
long-read vintage. **No prose changed, no figure attribute appeared** (correctly — the golden's assets
are all `UNKNOWN` in the manifest), and **the byline is untouched**, which independently proves the
news-path date normalisation is a no-op on a correct writer byline.

`expected.html` is a **generated snapshot** whose only job is to detect unintended drift; the fixture
proper is `chapter-plan.json` + `chapters/*.html`, which I did not touch. Regenerating it after a
deliberate, enumerated generator change is the intended maintenance action. It is nonetheless an
**unowned file** under SPEC §2, so it is declared here explicitly; the brief pre-authorised the call.
Pre-regeneration copy kept at `scratchpad/expected.html.before`.

**Confirmed the regenerated golden still represents a valid issue** — not just byte-identical:

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh ; echo "REAL EXIT=$?"
…
--- validate (all gates …) ---            # legacy golden
[PASS] weekly-structure/nav-count: 7 navigator stations (4-13)
… 23 PASS …
1 warning(s). PASS.
--- validate the golden plan against the skeleton ---
PASS — '…/golden/weekly/chapter-plan.json' is valid.
=== mx-weekly golden regression (WP-8) ===
--- byte-identity vs committed expected.html ---
  byte-identical ✓
[PASS] law3-word-floor: 8,173 words clears the Law-3 weekly floor of 6,000
[PASS] law9-voices: counted 4 distinct named external voice(s) … clears the Law-9 weekly floor of 4
[PASS] f16-external-img-src: all 17 <img> src(s) local or data:
… 25 PASS …
1 warning(s). PASS.
=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ===
REAL EXIT=0
```

(The single warning in each is `image-urls: skipped per --skip-image-urls` — the offline sandbox
cannot run network HEAD checks. Pre-existing behaviour of the harness.)

**A trap in this script, for whoever runs it next:** it pipes `diff … | head -12` under
`set -euo pipefail`, so on drift it exits **141** (SIGPIPE), not 1. And `bash verify… | tail -40`
reports `tail`'s exit code, i.e. 0, hiding a failure completely. Capture to a file and check `$?`.

---

## Verification commands (all run, real output above)

```
$ python3 -m py_compile .claude/skills/the-signal/scripts/stitch_weekly.py
py_compile stitch_weekly.py: OK
$ python3 -c "import json; json.load(open('.../format-skeletons/weekly.json'))"
json.load weekly.json: OK
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh ; echo $?
=== GOLDEN REGRESSION PASS … ===   REAL EXIT=0
$ git status --short
 M .claude/skills/the-signal/scripts/stitch_weekly.py
   (everything else already snapshot-committed by the orchestrator mid-task; full
    WP-3 footprint confirmed with `git diff --stat 6325658 -- <my paths>` above)
```

Four fixture plans exercising both `vintage` × both `cover_leads_on` values:

```
  [news-news]            Cover leads on: news        Long Read: vintage=news
  [evergreen-news]       Cover leads on: news        Long Read: vintage=evergreen · 1901–2021 · latest 2021-03
  [news-longread]        Cover leads on: long_read   Long Read: vintage=news
  [evergreen-longread]   Cover leads on: long_read   Long Read: vintage=evergreen · 1901–2021 · latest 2021-03
```

Fixtures live in the scratchpad, **not** the repo:
`plan-{news,evergreen}-{news,longread}.json`, `plan-hoist-{demo,control}.json`,
`plan-bad{vintage,leads,eg}.json`, `manifest-fixture.json`, `cbuild/chapters/{touchline,the_threads,long_read}.html`.
See § Handoff notes for WP-10.

---

## What WP-4 must catch — the coverage I do **not** have

Stated precisely, because pretending otherwise is worse than a gap.

1. **Figure provenance on any asset the manifest does not know.** I stamp only from
   `assets/cached/manifest.json`. Today that is **0 of 14** figures on a real fixture, because all 438
   entries are `UNKNOWN` back-fills. Until WP-8's manifest carries real records (issue #19 onward),
   **every `.plate-img` attribute must come from the writer**, and only `validate-issue.py` can fail
   its absence. The stitcher reports the gap per-figure and can hard-fail with
   `--strict-figure-provenance`, but that is off by default and no caller passes it.
2. **`data-lr-framing="feature"` in The Letter.** It marks a *prose paragraph* the writer authors; the
   stitcher cannot know which one. It warns when the anchor is evergreen and the attribute is absent
   anywhere in the letter band, and that is the ceiling of what it can do.
3. **`data-sport` values.** The stitcher passes writer markup through verbatim: it does not add,
   validate or normalise `data-sport`, so hard-failing `multi_sport`, warning on a token outside the
   22, and enforcing `results_ledger_multi_sport` are all WP-4's. Note the invariant needs *two*
   inputs the rendered HTML does not contain — state's `interest_depth` and `sports_calendar` — to
   decide whether ≥2 tracked sports concluded in-window.
4. **`data-resolves-loop` presence per matured loop** (SPEC §3.7). The stitcher neither reads
   `state.open_loops` nor injects the attribute.
5. **`data-table-kind` value validity.** CSS exists for all five; nothing stops a writer emitting a
   sixth, which would render as the unstyled base card.
6. **`data-vintage` vs the plan.** The stitcher is the only writer of this attribute, so it cannot
   disagree with the plan — but WP-4 should still assert presence, the enum, and the
   `evergreen ⇒ .lr-vintage present ∧ no date in .byline` pair, since that is acceptance criterion #2.

---

## Left undone / deliberate scope calls

- **`.lr-title` is still writer-authored.** Moving its generation into the stitcher is the cleaner
  end-state and would let the stitcher own the block outright as §3.4 assumes — but it requires
  editing both goldens' `chapters/long_read.html` (unowned) and a decision about whether writers keep
  control of the headline and standfirst. Out of scope here; flagged below.
- **No browser render.** See § injection note.
- **Issue #18 not regenerated** (SPEC §1.3). Its long-read section still has no `data-vintage`, which
  is the recorded expected failure in the PROGRESS expected-failure ledger.
- **`navigator_ceiling` left at 4–13.** The legacy golden briefly failed it at 14; that turned out to
  be my `data-station-band` bug, not a real ceiling problem. The invariant is unchanged.

---

## Handoff notes

1. **→ WP-4: two attributes beyond §3.4's list.** `data-cover-leads-on="news|long_read"` on
   `<header class="cover">`, and `data-nav-band="<band_id>"` on every `[data-station]`. Both are
   documented in `weekly.json § structural_hooks.cover_leads_on`. **Do not** name any future attribute
   `data-station*` — your navigator tally `re.findall(r'\bdata-station\b')` double-counts it.
2. **→ WP-4: `data-capture-year=""` is the legal null rendering.** Empty string, not `"UNKNOWN"` and
   not absent-when-null. §3.9's rule applies only to a **non-empty** value; treat `""` as "no year to
   compare". A `data-capture-year` that is not 4 digits or empty should be a failure — the stitcher
   guarantees it never emits one, so any such value came from a writer.
3. **→ WP-4/WP-10: `--strict-figure-provenance` exists and is off by default.** Once the manifest
   carries real records for a whole issue, turning it on in `stitch-issue.sh` (WP-9's file) would move
   the check upstream of the ship gate. Not done here — it would fail every current fixture.
4. **→ WP-8: the manifest join key works and the shape is right.** `assets/cached/manifest.json` is
   read by hash and consumed as documented. Two requests: keep `capture_year` a JSON **integer or
   `null`** (never the string `"UNKNOWN"` — write the key absent instead), and keep
   `licence.allows_derivatives` a real boolean or absent, never `null`. The stitcher already refuses
   placeholders, so a placeholder is silently equivalent to no record.
5. **→ orchestrator/owner: SPEC §3.4's premise about `.lr-title` is wrong for this repo.** Writers
   emit the block, including the `.byline`. Nothing in the contract changed; the stitcher normalises
   instead of generating. If you want it genuinely stitcher-owned, that is a follow-up touching both
   goldens' writer content and needs an owner.
6. **→ WP-10: the fixtures are in the scratchpad, and you should own them if you want them.** The
   four `vintage × cover_leads_on` plans, the hoist demo/control pair, the three fail-fast plans, the
   real-valued `manifest-fixture.json`, and the `cbuild/` band content carrying the full §3.4 contract
   markup (results ledger with per-sport rows, `data-resolves-loop`, `data-table-kind`,
   `demoted-lead`) are all reusable for `test-coverage-gates.sh`. They are deliberately **not** in the
   repo — `references/fixtures/coverage-rebuild/**` is yours.
7. **→ WP-10: `verify-weekly-golden.sh` exits 141 on mx drift, and `| tail` masks failures.** See the
   trap note in § Golden parity. Worth wrapping in the harness.
8. **→ orchestrator: mid-task WIP commits made `git stash` an unreliable baseline** and cost me a
   mis-diagnosis (§4). If a WP is asked to prove "pre-existing vs mine", it needs a stable
   pre-WP ref to diff against.

---

# WP-3 — REOPENED: golden fixtures given real §3.4 figure provenance

**Trigger:** WP-4 landed and `verify-weekly-golden.sh` went to **exit 1** — both goldens failed three
image checks because their writer chapters predate SPEC §3.4.
**Outcome: exit 0, 73 PASS / 0 FAIL / 3 WARN.** No check was weakened; `validate-issue.py` untouched.
Baseline for every diff below is **`68230f2`** ("WP-4 DONE"), not `git stash`.

## Files touched — golden fixtures only

```
$ git diff --stat 68230f2 -- <WP-3's four owned paths + references/golden>
 .../golden/weekly-mx/chapters/{long_read,pixel_byte,screen_sound,the_letter,
                                the_threads,this_week_in_history,touchline}.html
 .../golden/weekly-mx/expected.html
 .../golden/weekly/chapters/{long_read,pixel_byte,screen_sound,the_letter,
                             this_week_in_history,touchline}.html
 14 files changed, 61 insertions(+), 61 deletions(-)

$ git diff --name-only 68230f2 | grep -v <WP-3 ownership>
(empty — nothing outside WP-3's files)
$ git status --short assets/cached
(empty — no new asset written)
```

`stitch_weekly.py`, `weekly.json` and both stylesheets are **unchanged** since `68230f2`: this was
purely a stale-fixture fix.

## What the three failures actually were

```
[FAIL] figure-provenance: 7 of 7 .plate-img figure(s) are short of the SPEC §3.4 provenance record
[FAIL] image-shapes/distinct: 0 distinct data-shows value(s) across 7 figure(s) ([]); the floor is 3
[FAIL] image-shapes/long-read-information: the Long Read's 2 figure(s) include none of
       ['diagram','map','chart','artefact']
```

**WP-4's handoff called this a minimal fixture fix. It is not, and the reason matters.** Declaring
`data-shows` *honestly* wakes two checks that were silent while the attribute was absent (by design —
"(2), (3) and (5) can only speak about a declared value"). Adding attributes alone would have traded
three failures for two new ones:

- `image-shapes/never-lead` — **three** band lead figures across the two goldens are genuinely
  `key_art`: Palworld's Steam header capsule (legacy Pixel & Byte), the Project Hail Mary poster
  (legacy Screen & Sound), the Halo: Campaign Evolved key art (mx Pixel & Byte).
- `image-shapes/pixel-byte-key-art` — mx Pixel & Byte carried **two** `key_art` (cap is 1).
- `image-shapes/long-read-information` — the mx Long Read had only a `portrait` and an `event_photo`.

The goldens were, in other words, carrying live instances of **defect E** — the thing this rebuild
exists to fix. WP-4's checks are right; the fixtures were stale.

## §2b · The honesty basis for every `data-shows` value

**I looked at each image**, not just its alt text. Six were visually inspected because their shape was
genuinely ambiguous; the rest are unambiguous photographs whose alt text describes them accurately.

| Asset | Value | Basis |
|---|---|---|
| `e1d80d7ae3a7` | `artefact` | **Viewed:** object shot of the Telstar 1 sphere on black — the physical object, not an event |
| `161e21e690fa` | `artefact` | **Viewed:** the preserved Pleumeur-Bodou horn antenna indoors — a museum installation |
| `407d2c022a03` | `document` | **Viewed:** the first Mars image reproduced twice, annotated "Edge of Mars"/"Clouds Over Mars" — the primary *record*, not a museum object |
| `7652b526eda5` | `diagram` | **Viewed:** graticule, labelled LIMB/TERMINATOR, 22 numbered frame footprints overlaid — an explanatory overlay on a map base; its payload is the coverage footprint |
| `42906603647c` | `event_photo` | **Viewed:** production still, no logo or title treatment. WP-6's canonical wording settles it: `event_photo` = "A photograph **or still** of the actual thing happening" |
| `c0fbc060b733` | `event_photo` | **Viewed:** MetLife Stadium in its actual FIFA World Cup 26 dressing (tournament banners, "WE ARE NEW YORK NEW JERSEY") — a documentary photograph of the real subject |
| `63a71c18c1e3` · `8ff67aa0126f` · `de0cff9fdf9c` | `key_art` | **Viewed:** all three have the logo composited in (the first is a 460×215 Steam header capsule). Textbook §3.13 rank-5 |
| `5c81e72a0f95` | `key_art` | **Viewed:** film poster with title treatment |
| `df664fac69a2` · `ac225d893976` · `f37adaa87280` · `ebecfdf2c5a9` · `d2f4e531313a` · `61aac2156d95` · `0d3de2610c28` | `event_photo` | photographs of the thing happening (satellite deployment, Centre Court in play, chamber speech, a candid outside a doorway, a tanker under way, a resident in rubble) |
| `a7143c11f458` · `2a9d4f29c684` · `65aa827ae471` | `portrait` | posed studio/official portraits — per WP-6, "a candid at an event is event_photo, not portrait", and these are not candids |
| `e5e95fd4612f` | `map` | a labelled geographic figure of the Strait of Hormuz |

**Nothing was chosen to satisfy a floor.** The distinct-shape counts (4 legacy, 7 mx) are a
*consequence* of the honest values, not an input to them. The Long Read information figure the legacy
golden needed was already there — Telstar 1 is honestly `artefact`, so no swap was required.

### `data-capture-year` — where the honest answer is "unknown"

**None of the 27 golden asset hashes has a recoverable source URL.** Verified:

```
manifest entries with a real url: 13   (all Efteling/Beekse Bergen restaurant photos)
golden asset hashes: 27
golden hashes WITH a real url in the manifest: NONE
```

So a capture year can only be honest where the asset's own content or the fixture's own caption dates
it. I set a year in exactly those 11 cases — 1962 (Telstar 1 existed only in 1962 and was never
recovered; caption says "the 1962 sphere"), 1984 (caption and alt name the Discovery deployment), 1965
(Mariner 4 flyby, the band's own "This week in 1965"), 2026 (World Cup 26 banners visible on the
stadium; "the 2026 film"; "the 2026 Wimbledon final"; games released 2026 per the prose) — and left the
other 9 as `data-capture-year=""`.

`""` is the legal null rendering and WP-4 skips §3.9 on it. **I am flagging that as a real limitation,
not presenting it as a fix:** §3.9 cannot bite on those 9 figures, so for them defect B remains
undetectable. The alternative was to guess 9 years, which is the fabrication I was told not to commit.
The durable fix is re-sourcing the fixture's assets so their URLs and dates are known — see handoff 11.

### `data-licence` / `data-allows-derivatives`

Taken from each figure's own `.credit` line — the fixture's existing provenance claim. Where the credit
names a licence it is used (`CC-BY-SA-3.0`, `PUBLIC-DOMAIN`); where it names only a wire or publisher
("AP Photo · via CBS News", "Reuters · via PBS", "Wikimedia Commons" with no licence) the honest token
is `UNKNOWN` with `allows-derivatives="false"` — legal, and WP-4 reports it as a **warning**, which is
the correct visible state:

```
[WARN] figure-provenance/licence-unknown: 8 figure(s) render data-licence="UNKNOWN" …
```

Press-kit material (game key art, the poster, the Netflix still) is `PRESS-KIT-EDITORIAL` /
`allows-derivatives="false"`.

## §2c · The three key-art leads: no image was swapped, and why

**I tried to swap them.** SPEC §3.13 names the path explicitly, and it works: Steam's `appdetails`
returned real screenshots for both games, and I downloaded and inspected candidates —
Palworld players flying mounted Pals over the Paldium sky islands (exactly the 1.0 features the prose
names) and a Warthog firing in an ice cavern for Halo. Both are **`in_engine`** (no HUD), which the
enum explicitly permits as a lead.

**Writing them to `assets/cached/` was blocked by the sandbox**, and on reflection that is the right
outcome: `assets/cached/**` is not a WP-3 file, and adding assets also implies writing WP-8's
`manifest.json`. I did not work around it.

So the three key_art figures were fixed the other honest way — **the doctrine's own remedy**: key art
is last resort and may never establish a band, so the band no longer opens on it. Each figure was
**genuinely relocated** into the item it illustrates, so the reader now meets prose first:

```
  weekly     item «Palworld hits 1.0»              hosts figure «Palworld leaves early access at 1.0…»
  weekly     item «Project Hail Mary lands on Prime» hosts figure «Project Hail Mary reaches Prime Video…»
  weekly-mx  item «Halo comes to PlayStation»      hosts figure «Halo: Campaign Evolved — the remade…»
  band-lead figures remaining in all three bands: 0
```

This is a real structural change with a reader-visible effect, not a class rename — I specifically
rejected "drop `.lead` but leave the image opening the band", which would have been gaming the check.
Div/`<li>` balance verified in every edited file ("all balanced").

**mx Pixel & Byte's two-`key_art` cap** was resolved by removing the duplicate marketing image (the
Black Flag key art), keeping its prose. That is the budget doing its job rather than a workaround: per
§3.13 a logo "tells the reader nothing the headline didn't", and a band with marketing art for both
games should show one piece of it, not two.

## §2d · The mx Long Read's information figure — a self-made chart

The mx Long Read had only a `portrait` and an `event_photo`, and no photographic information figure
exists for a piece about the mechanics of prime-ministerial succession. Rather than mislabel one, I
added a **self-made `chart`** — SPEC §3.13 rank 2 / §3.14 "the paper's own figures", and the shape
`weekly.json`'s own `chart_card` component already prescribes. It is an inline `data:` URI SVG, so **no
new asset file was needed**.

Every name, count and date in it is stated **verbatim in that fixture's own prose** (grep-verified
before drawing): the seven-name sequence and "a decade that ought to hold two or three"; "By CNN's
count, four of the most recent handovers happened with no general election at all"; "Labour won the
last general election, in 2024". Election-vs-handover status is deliberately **not** assigned per name,
because the prose does not — the count is a standalone annotation instead of a bracket over specific
segments. `data-capture-year=""` is correct here on the contract's own terms (§3.2 allows a null
capture year for a synthetic chart).

```
well-formed XML: True | viewBox: 0 0 760 214
out-of-bounds elements: none
colours used: ['#16151A', '#243F5C', '#8A8578', '#EFE8D9', '#F5F0E6', '#FF3B2F']   ← the six Transmission palette hexes, nothing else
```

**Not verified:** no rasteriser (`rsvg-convert`/`convert`/`inkscape`) is available in this sandbox, so
the chart was validated structurally and never *rendered*. Someone should look at it once.

## Stylesheet injection — the coordinator's explicit question

Both stylesheets are in the injected `<style>` of the rendered goldens, and the layering is correct:
the legacy (non-mx) golden gets the core file only; the mx golden gets both.

```
=== LEGACY golden (design_system absent) ===
  injected <style>: 28.7 KB  (file 88.8 KB)
  weekly/01-coverage-rebuild.css header present: True
  weekly-mx/11-mx-coverage-rebuild.css header present: False  (expected: False)
  all 4 core selectors in the injected CSS: True
  all 9 mx selectors in the injected CSS: False  (expected: False)
  markup in THIS document: data-vintage=True data-cover-leads-on=True data-table-kind=False data-shows×7

=== MX golden expected.html ===
  injected <style>: 56.6 KB  (file 157.7 KB)
  weekly/01-coverage-rebuild.css header present: True
  weekly-mx/11-mx-coverage-rebuild.css header present: True  (expected: True)
  all 4 core selectors in the injected CSS: True
  all 9 mx selectors in the injected CSS: True  (expected: True)
  markup in THIS document: data-vintage=True data-cover-leads-on=True data-table-kind=True data-shows×14
```

Selectors probed by literal text include `.lr-title .lr-vintage{`, `.items > li[data-resolves-loop]`,
`.mx-ledger[data-role="results-ledger"] .mx-ledger__row[data-sport]`,
`.mx-ledger[data-role="demoted-lead"] {`, and all five `data-table-kind` variants. Each document also
contains markup those rules bind to.

## Verification — real output

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh ; echo $?
### verify-weekly-golden.sh REAL EXIT=0 ###
  PASS: 73   FAIL: 0   WARN: 3
=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ===
```

Legacy golden (was 3 FAIL, now 0):
```
[PASS] figure-provenance: all 7 .plate-img figure(s) carry the four-attribute provenance record
[PASS] image-shapes/distinct: 4 distinct data-shows value(s) (floor 3): ['artefact','event_photo','key_art','portrait']
[PASS] image-shapes/never-lead: none of the 2 declared lead figure(s) use a never-lead shape
[PASS] image-shapes/pixel-byte-key-art: 1 key_art figure(s), none leading
[PASS] image-shapes/long-read-information: the Long Read carries 1 information figure(s): FIG. 01=artefact
[PASS] caption-vintage: 4 figure(s) with a dated capture year, all consistent … capture 1962 < claim 1965, and the visible caption says so
1 warning(s). PASS.
```

mx golden:
```
  byte-identical ✓
[PASS] figure-provenance: all 14 .plate-img figure(s) carry the four-attribute provenance record
[PASS] image-shapes/distinct: 7 distinct data-shows value(s): ['chart','diagram','document','event_photo','key_art','map','portrait']
[PASS] image-shapes/long-read-information: the Long Read carries 1 information figure(s): FIG.=chart
[PASS] image-shapes/touchline-result: 1 Touchline result figure(s), none mis-shaped FIG.=event_photo
[PASS] table-kind: 1 data-table-kind value(s), all legal: ['championship']
2 warning(s). PASS.
```

**No new failures on either golden.** The 3 warnings are: `image-urls` skipped (offline, ×2) and
`figure-provenance/licence-unknown` (×8, the honest state of those credits).

I also added `data-table-kind="championship"` to the mx Touchline `.mx-scorecard` (the World Cup's
final placings — a championship standing; my CSS rules off after the podium, which is apt here),
clearing a `table-kind` warning.

## Handoff notes (continued)

9. **→ coordinator: `data-table-kind`'s enum has no non-sport value, and `.mx-scorecard` is used for
   non-sport cards.** The mx golden's Desk carries `.mx-scorecard` "The Rate War · As of 19 Jul" (BoE
   base rate, lender cuts, MPC date) — a **financial reference card**. None of §3.4's five values
   (league/medal/gc/leaderboard/championship) honestly describes it, so I left it undeclared and WP-4
   warns. §3.4's enum is a fixed cross-WP contract, so I did not add a sixth value unilaterally. Either
   add a non-sport value, or scope WP-4's warning to Touchline scorecards, or stop using
   `.mx-scorecard` outside sport. **Currently a WARN, so nothing is blocked.**
10. **→ coordinator / WP-5 / WP-10: the LEGACY golden's `chapter-plan.json` now FAILS
    `validate-chapter-plan.py` with 7 errors** (missing `research_cut_at`, `window`, `cover_leads_on`,
    `cover_lead_topic_family`, `lead_rationale`, `long_read.vintage`, `week_in_numbers.rows`).
    `verify-weekly-golden.sh` **swallows** it (`|| echo "… skipping plan check"`), so the gate is green
    — but it is a real staleness of the same class I just fixed, and it will bite WP-10. I deliberately
    did **not** fix it: it needs `lead_rationale` prose authored into the fixture (≥120 chars) and a
    `latest_development` month I **cannot ground** — the Telstar piece is plainly `evergreen` with
    material spanning 1945–1984, but nothing in the fixture dates the 1984 deployment to a month, and
    guessing one is exactly the fabrication I refused elsewhere. Needs a decision on what the fixture
    should assert. (Note the harness swallowing this failure is itself worth fixing.)
11. **→ WP-8 + coordinator: the real fix for the goldens' provenance is re-sourcing, and I have the
    replacement images ready.** 9 of 21 golden figures carry `data-capture-year=""` and 8 carry
    `data-licence="UNKNOWN"` because their source URLs are unrecoverable. Two verified `in_engine`
    Steam screenshots (Palworld sky-islands traversal; Halo Warthog ice cavern) are downloaded and
    inspected in the scratchpad and would upgrade both Pixel & Byte bands from relocated key art to
    rank-4 leads with known URL, licence and year. Blocked only on write access to `assets/cached/**`
    plus WP-8 recording them in `manifest.json`. Say the word and it is a small change.
12. **→ WP-4: nothing needs changing, and two of your checks earned their keep.** `never-lead` and
    `pixel-byte-key-art` caught genuine defect-E instances in the fixtures the moment shapes were
    declared — that is the checks working, not fixture noise. One correction for your handoff 1: adding
    the four attributes is *not* sufficient on its own; honest values also require the fixture's
    key-art leads and the mx Long Read's missing information figure to be dealt with.
