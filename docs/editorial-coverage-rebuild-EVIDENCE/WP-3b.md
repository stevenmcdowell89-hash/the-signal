# WP-3b — `data-table-kind: finance`, and the golden's unknown capture years

**Status: Task 1 DONE. Task 2 done further than scoped, with four honest `""` remaining.**
**Golden: `verify-weekly-golden.sh` exit 0 before and after — 73 PASS / 0 FAIL / 3 WARN.**
Picked up cold from WP-3 (its context was gone). Baseline for every diff below is the named commit
**`fa8c80c`** ("WP-3: golden gate green again"), never `git stash`.

---

## Files touched

| File | Owner | Basis |
|---|---|---|
| `.claude/skills/the-signal/references/format-skeletons/weekly.json` | WP-3 (inherited) | mine |
| `.claude/skills/the-signal/assets/css/weekly-mx/11-mx-coverage-rebuild.css` | WP-3 (inherited) | mine |
| `.claude/skills/the-signal/references/golden/weekly/chapters/{the_letter,this_week_in_history,touchline}.html` | WP-3 (inherited) | mine |
| `.claude/skills/the-signal/references/golden/weekly-mx/chapters/{long_read,the_letter,the_threads,touchline}.html` | WP-3 (inherited) | mine |
| `.claude/skills/the-signal/references/golden/weekly-mx/expected.html` | WP-3 (inherited) | mine — regenerated, never hand-edited |
| `assets/cached/manifest.json` | **WP-8** | **written under explicit coordinator grant — see § Ownership** |

**Not touched:** `validate-issue.py` (WP-4, complete — the `finance` handoff below is for the
coordinator to route), `docs/editorial-coverage-rebuild-PROGRESS.md`, the legacy golden's
`chapter-plan.json` (WP-10's, per instruction), `stitch_weekly.py` (needed no change), the SPEC (its
only working-tree diff is the coordinator's own §3.11 `finance` amendment, untouched by me).

```
$ git diff --stat fa8c80c
 .../css/weekly-mx/11-mx-coverage-rebuild.css       |  24 +++-
 .../references/format-skeletons/weekly.json        |   6 +-
 .../golden/weekly-mx/chapters/long_read.html       |   4 +-
 .../golden/weekly-mx/chapters/the_letter.html      |   8 +-
 .../golden/weekly-mx/chapters/the_threads.html     |   4 +-
 .../golden/weekly-mx/chapters/touchline.html       |   4 +-
 .../references/golden/weekly-mx/expected.html      |  44 +++++--
 .../golden/weekly/chapters/the_letter.html         |   4 +-
 .../weekly/chapters/this_week_in_history.html      |   2 +-
 .../golden/weekly/chapters/touchline.html          |   4 +-
 assets/cached/manifest.json                        | 128 ++++++++++-----------
 docs/editorial-coverage-rebuild-SPEC-2026-07-26.md |   8 +-     ← coordinator's amendment, not mine
 12 files changed, 143 insertions(+), 97 deletions(-)
```

The SPEC row is the coordinator's own §3.11 amendment, which landed as `5b682ea` ("SPEC:
data-table-kind gains `finance`") while this work was in flight. Against that commit my diff is the
other 11 files only:

```
$ git diff --stat HEAD | tail -1
 11 files changed, 136 insertions(+), 96 deletions(-)

$ git diff --stat fa8c80c -- .claude/skills/the-signal/scripts/
(empty — the stitcher needed no change)
```

---

## Baseline — the gate was green before I started

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh ; echo "EXIT=$?"
  …
  [PASS] table-kind: 1 data-table-kind value(s), all legal: ['championship']
  [WARN] figure-provenance/licence-unknown: 8 figure(s) render data-licence="UNKNOWN": …
  [WARN] image-urls: skipped per --skip-image-urls
  2 warning(s). PASS.
=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ===
EXIT=0
```

---

# TASK 1 · `data-table-kind` gains `finance`

## What changed

**`weekly.json`** — the enum is declared in three places and all three now read
`league|medal|gc|leaderboard|championship|finance`:

1. `structural_hooks.table_kind` — the contract statement, plus why the sixth value exists.
2. `furniture_layer.components.standings_card` — the component doctrine, plus the finance shape's
   rendering (`label · figure`, wrapping label column, atomic mixed-unit figure column, `tr.is-lead`
   as a **reference** figure).
3. `furniture_layer.note`'s CSS budget line — 55.5 KB → **56.5 KB**, and "the five
   `data-table-kind` variants" → the variants plus "WP-3b a further 1.0 KB for the sixth variant".

The `standings_card` component's home also changed from "Lives in The Touchline" to "Lives in The
Touchline, and (as a finance card) The Desk" — the enum was only half the omission; the component's
own documentation said sport too.

**CSS** (`weekly-mx/11-mx-coverage-rebuild.css`, +989 bytes: 5,619 → 6,608). `.mx-scorecard` is
mx-only, so this is the one stylesheet that needed it. Four rules, all through the Transmission alias
— **no new font, colour or token, and no `.sp-*` / `.hol-*`** (both are gate-forbidden in weeklies;
verified absent below):

```css
/* finance — a REFERENCE card, not a ranking: label · figure, "as of" a date. No
   position column, no podium rule-off — nothing in it is winning. The label
   column wraps; the figure column is atomic and mixed-unit ("3.75%", "−0.16pp",
   "30 JUL"), so it shrink-wraps and never splits a value. */
.mx-scorecard[data-table-kind="finance"] .mx-scorecard__gap,
.mx-scorecard[data-table-kind="finance"] td:last-child {
  width: 1%; text-align: right; white-space: nowrap; letter-spacing: 0.04em;
}
/* The highlighted row is the reference figure the others are read against, not a
   leader: vermilion belongs to what leads or wins (same doctrine as
   data-role="demoted-lead"), so the anchor takes signal blue. */
.mx-scorecard[data-table-kind="finance"] tr.is-lead .mx-scorecard__gap,
.mx-scorecard[data-table-kind="finance"] tr.is-lead td:last-child {
  color: var(--mx-support-1);
}
```

**The design decision worth recording.** The base component already paints `tr.is-lead
.mx-scorecard__gap` vermilion (`--mx-accent`), because in the five sport kinds the highlighted row is
the *winner*. In a rate card it is the **reference rate the other rows are read against** — the BoE
base rate, against which lender cuts are the story. So `finance` withdraws the accent to signal blue,
the same gesture and the same reasoning WP-3 used for `data-role="demoted-lead"`: vermilion belongs to
what leads or wins. That is the substantive difference between "a sixth CSS block" and a sixth *kind*.
`finance` also deliberately has **no podium rule-off** and **no position column** — the two things
every sport kind has, and the two things a reference table must not imply.

Shape taken from the live use it exists to describe — the mx golden's Desk card, `The Rate War · As of
19 Jul`: `tr.is-lead` BoE base rate `3.75%`, then `×4`, `−0.16pp`, `30 JUL`. Mixed units in one column
is exactly why the figure column must shrink-wrap and never break.

## The `finance` value is NOT stamped into the golden — and that is the point

**`validate-issue.py` HARDCODES the five values. It does not read `weekly.json`.**

```
$ grep -n TABLE_KINDS .claude/skills/the-signal/scripts/validate-issue.py
1764:TABLE_KINDS = ("league", "medal", "gc", "leaderboard", "championship")
2192:    bad = sorted({v for v in values if v not in TABLE_KINDS})
2198:                    f"Legal: {list(TABLE_KINDS)} (SPEC §3.4). A sixth value renders as the "
2207:                    f"renders as the unstyled base shape. Declare one of {list(TABLE_KINDS)} "
```

`check_table_kind` treats an unlisted value as a **hard FAIL**, not a warning. Proved on a scratchpad
copy of the mx golden with the sixth value stamped on the Desk's rate card — the file the enum was
extended *for*:

```
$ python3 …/validate-issue.py <scratchpad>/mx-finance-probe.html --format weekly --skip-image-urls
[FAIL] table-kind: data-table-kind value(s) outside the five legal shapes: ['finance'].
       Legal: ['league', 'medal', 'gc', 'leaderboard', 'championship'] (SPEC §3.4).
       A sixth value renders as the unstyled base card — CSS exists for exactly these five.
1 failure(s) — issue NOT shippable.
```

So stamping `data-table-kind="finance"` on the Desk card would take the golden to exit 1. I did not
stamp it, and I did not edit WP-4's file. **→ HANDOFF 1 (coordinator).** The enum extension is
therefore *live in the structure of record and in the CSS, and inert in the rendered fixture* until
WP-4's `TABLE_KINDS` gains `finance`. The Desk card stays undeclared exactly as WP-3 left it; the gate
is green either way.

The finance CSS *is* shipped and reachable — verified inside the mx golden's injected `<style>`:

```
  injected CSS contains '.mx-scorecard[data-table-kind="finance"] .mx-scorecard__gap': True
  injected CSS contains '.mx-scorecard[data-table-kind="finance"] tr.is-lead .mx-scorecard__gap': True
  injected <style> size: 56.4 KB
```

**Two smaller findings from reading `check_table_kind`:**

- **→ HANDOFF 2 (coordinator / WP-4).** WP-3's note 9 said the undeclared Desk card produces a WARN.
  It does not. The check is `if bad: … elif values: ok(…) elif n_cards: warn(…)` — the "no
  `data-table-kind`" warning is only reachable when **no** card in the issue declares one. The mx
  golden declares `championship` on the Touchline card, so the Desk card's omission is currently
  **silent**. That is a per-issue check where a per-card one was intended.
- **→ HANDOFF 3 (WP-6, `component-contracts.md:230`).** That file states the enum and adds
  "**Mandatory; no sixth value.**" It is now wrong on both counts. `references/sections.md:148`
  (WP-2) also lists the five. Neither is mine; both need the amendment.

---

# TASK 2 · the golden's `data-capture-year=""`

## Outcome: 9 → 5 empty, and only 4 of those are unknowns

| | baseline `fa8c80c` | now |
|---|---|---|
| `data-capture-year=""` across both goldens | **9** of 21 | **5** of 21 |
| — of which contract-correct (`shows: chart`, §3.2) | 0 counted | 1 |
| — genuinely unknown | 9 | **4** |
| `data-licence="UNKNOWN"` | **8** | **4** |
| figure attributes stamped from the manifest | 0 | **5** |

## Method: I did not install new images. I recovered the ones already there.

WP-3's handoff 11 proposed fixing this by installing two verified Steam `in_engine` screenshots.
**I checked that first and it would not have moved the number at all**: the two figures those
screenshots would replace (Palworld `63a71c18c1e3`, Halo `8ff67aa0126f`) already carry a grounded
`data-capture-year="2026"`. Handoff 11 conflated two separate gaps — the *shape* gap (key art where
gameplay belongs, §3.13) and the *vintage* gap (`""`). The nine `""` figures are photographs, a map
and a portrait; not one is a game asset. Egress works (Steam `appdetails` returned HTTP 200 / 35,259
bytes for appid 1623730 on the first try), so this was a judgement, not a blocker — see § Steam.

The real lever was WP-3's stated premise: *"None of the 27 golden asset hashes has a recoverable
source URL."* That premise is **false**, and the manifest's own key rule is what disproves it. Files
are named `sha256(url)[:12]`, which is one-way — but it is *checkable* in the forward direction. So:
find candidate URLs by other means, hash them, and a match is proof rather than inference.

Two search paths, both zero-guess:

1. **Exact content match.** Commons' API indexes file SHA-1: `list=allimages&aisha1=<sha1 of the
   cached bytes>` returns the file if the cache holds the original. **4 of 6 hits.**
2. **Thumbnail reconstruction.** Two cached files are 1920 px wide — Wikimedia thumbnails, so their
   bytes are not the original's and path 1 misses. Found those by the author named in the fixture's
   own `.credit` line, then confirmed **twice**: the regenerated 1920 px thumbnail is byte-identical
   to the cached file, *and* `sha256(thumburl)[:12]` equals the filename.

Every recovery below is confirmed by `sha256(url)[:12] == <cached filename>`. Nothing is inferred from
a credit line; the credit line was only ever a search hint.

```
OK   a7143c11f458  https://upload.wikimedia.org/wikipedia/commons/0/03/Spencer_Gore_portrait.jpg
OK   65aa827ae471  …/6/6b/Official_portrait_of_Andy_Burnham_MP_2026_%28cropped_3x4%29.jpg
OK   2a9d4f29c684  …/c/ca/Andy_Burnham_on_13_August_2024_%28cropped_2%29.jpg
OK   e5e95fd4612f  …/a/ae/Strait_of_hormuz_full.jpg
OK   ac225d893976  …/thumb/d/dc/Centre_Court_Wimbledon_2009.JPG/1920px-Centre_Court_Wimbledon_2009.JPG
OK   161e21e690fa  …/thumb/5/50/Horn_antenna-Pleumeur-bodou.jpg/1920px-Horn_antenna-Pleumeur-bodou.jpg
OK   c0fbc060b733  …/f/fc/MetLife_Stadium_Exterior%2C_2026_FIFA_World_Cup_%28June_20%2C_2026%29_%28cropped%29.jpg
OK   f37adaa87280  …/c/cf/Sinner_Zverev_Princess_of_Wales_Wimbledon_2026_%28cropped%29.jpg
```

## The eight recovered assets, and the basis for every year

| hash | source | licence (was) | `capture_year` | grounding — the exact field it came from |
|---|---|---|---|---|
| `161e21e690fa` | `File:Horn antenna-Pleumeur-bodou.jpg` (1920px thumb) | CC-BY-SA-3.0 (unchanged) | **2012** | file's own EXIF `DateTimeOriginal 2012-09-13 13:58:49`, Canon EOS 40D. Not the 1962 event it depicts |
| `a7143c11f458` | `File:Spencer Gore portrait.jpg` | PUBLIC-DOMAIN (unchanged) | **`null` → `""`** | Commons dates it only *"Before 19 April 1906"* — an upper bound (Gore's death), not a year. **Left empty on purpose** |
| `ac225d893976` | `File:Centre Court Wimbledon 2009.JPG` (1920px thumb) | CC-BY-SA-3.0 (unchanged) | **2009** | own-work description *"The Centre Court at Wimbledon 2009: the new roof"* + `Category:2009 Wimbledon Championships` |
| `65aa827ae471` | `File:Official portrait of Andy Burnham MP 2026 (cropped 3x4).jpg` | **UNKNOWN → CC-BY-3.0**, House of Commons | **2026** | `DateTimeOriginal 2026-07-13 17:09:24` |
| `2a9d4f29c684` | `File:Andy Burnham on 13 August 2024 (cropped 2).jpg` | **CC-BY-SA-3.0 → CC-BY-2.0**, Scottish Government | **2024** | `DateTimeOriginal 2024-08-13 17:06:21`, corroborated by filename and description |
| `e5e95fd4612f` | `File:Strait of hormuz full.jpg` | **UNKNOWN → PUBLIC-DOMAIN** (PD-USGov) | **2004** | see the reasoning below |
| `c0fbc060b733` | `File:MetLife Stadium Exterior, 2026 FIFA World Cup…(cropped).jpg` | **UNKNOWN → CC-BY-4.0**, MiracleMiles | **2026** | `DateTimeOriginal 2026-06-20 10:41:20` (already claimed 2026; now sourced) |
| `f37adaa87280` | `File:Sinner Zverev Princess of Wales Wimbledon 2026 (cropped).jpg` | **UNKNOWN → CC-BY-SA-4.0**, Daniel Cooper / crop by Kacir | **2026** | file's `Date` field `2026-07-12` (already claimed 2026; now sourced) |

**Two licence records were not merely missing but wrong, and both mattered:**

- **`2a9d4f29c684` asserted `CC-BY-SA-3.0`.** It is **CC BY 2.0** — no ShareAlike, and a different
  rightsholder (Scottish Government, from Flickr) than the credit's bare "Wikimedia Commons".
  The fixture was making a false licence claim, and it was the *canonical example* writers copy.
- **`c0fbc060b733` — the mx golden's COVER — rendered `data-licence="UNKNOWN"` with
  `data-allows-derivatives="false"`.** It is CC BY 4.0 own work: derivatives **are** permitted. Under
  the honest record WP-8's `extract-covers.py` would have refused a crop that is actually allowed.
  Worth naming because §3.10's live violation is the *opposite* error (an ND source that *was*
  cropped): a false `false` is not the safe direction, it is just a different wrong answer, and it
  teaches people to route around the gate.

**Why `e5e95fd4612f` is 2004 and not a guess.** The file page lists two sources — an *"Iran Country
Profile"* map (`iran_country_profile_2009.jpg`) and a detail map (`iran_strait_of_hormuz_2004.jpg`) —
and carries `{{PCL|Strait of Hormuz (2004)}}`. Ambiguous on its face. The original upload log settles
it: **2007-12-20**, two years before the 2009 country profile existed. Only the 2004 chart is
possible. Licence `{{PD-USGov}}`.

**Nothing in `assets/cached/` was added, replaced or deleted** (`git status --short assets/cached`
lists only `manifest.json`). The bytes on disk were always right; only the record of them was missing.

## The four figures still `""`, and why each stays that way

| figure | why |
|---|---|
| `a7143c11f458` (legacy, Spencer Gore, PD) | URL and licence recovered; **year deliberately not**. Commons gives *"Before 19 April 1906"*. The band claims 1877 and cartes de visite span the 1860s–80s. Any of those is a fabrication, and this rebuild exists because an image's vintage was mis-stated |
| `ebecfdf2c5a9` (AP Photo · via CBS News) | wire photo, not on Commons — sha1 lookup returns `NO COMMONS MATCH`. No recoverable URL, no licence, no date |
| `61aac2156d95` (Reuters · via PBS) | as above |
| `0d3de2610c28` (Reuters · via PBS NewsHour) | as above |

Plus the mx Long Read's self-made `chart` (a `data:` URI SVG), whose `""` is **contract-correct** —
§3.2 permits a null capture year for a synthetic chart. It is in the count of 5 but is not a gap.

I re-ran the SHA-1 lookup on all four wire photos plus `d2f4e531313a` to be sure the "unrecoverable"
claim is tested rather than assumed:

```
ebecfdf2c5a9 NO COMMONS MATCH      c0fbc060b733 ['File:MetLife Stadium Exterior, 2026 FIFA World Cup…']
61aac2156d95 NO COMMONS MATCH      f37adaa87280 ['File:Sinner Zverev Princess of Wales Wimbledon 2026…']
0d3de2610c28 NO COMMONS MATCH      d2f4e531313a NO COMMONS MATCH
```

## How the values reach the rendered figure — the manifest join, demonstrated

For all eight recovered assets I **removed the writer-authored provenance attributes from the golden
chapters** and let `stitch_weekly.py` fill them from `assets/cached/manifest.json`:

```
- <div data-mx-event="figure" class="plate-img" data-shows="portrait" data-capture-year=""
       data-licence="UNKNOWN" data-allows-derivatives="false">
+ <div data-mx-event="figure" class="plate-img">
```

This is deliberate and is the more valuable half of the change. §3.4a note 6 recorded figure
provenance as *"0-of-14 today, by construction"* — every attribute had to be hand-typed by the writer
because all 438 manifest entries were `UNKNOWN` back-fills. With eight real entries the join has real
inputs, so the golden now **demonstrates the §3.10 path** instead of demonstrating hand-copied licence
codes:

```
  Fig provenance: 14/14 complete (5 stamped from the manifest: 438 asset[s])
```

(Five, not eight: three of the eight live in the legacy golden, stitched separately.)

## Caption corrections — §3.9 is now demonstrable in the fixture writers copy

Giving a figure a real year *activates* §3.9 on it. One activation failed immediately, which is the
check earning its keep on the canonical example:

```
[FAIL] caption-vintage: 1 of 10 dated figure(s) illustrate a later claim without saying so (SPEC §3.9):
    • FIG. [the_threads, /assets/cached/e5e95fd4612f.jpg]
        capture year 2004 is OLDER than the band's latest claim 2007, and "2004" does not appear
        in the caption's visible sentence.
        .plate-cap .txt (credit excluded) reads: 'The Strait of Hormuz — the choke-point the strikes
        are meant to keep open, where the marked shipping lanes run within a few miles of the
        Iranian coast.'
```

Fixed the way §3.9's own worked example prescribes — the year goes in the sentence the reader sees:

| figure | caption change | why |
|---|---|---|
| `e5e95fd4612f` | → "The Strait of Hormuz **on a 2004 US government chart** — …" | **required**: the §3.9 failure above |
| `161e21e690fa` | → "The horn antenna at Pleumeur-Bodou, Brittany, **photographed in 2012** — …" | not required by the gate; see the blind spot below |
| `ac225d893976` | → "Centre Court, SW19, **under the roof that was new in 2009** — …" | as above |
| `2a9d4f29c684` | → "Andy Burnham, **pictured in 2024** — sworn in as prime minister on Monday…" | as above |
| `65aa827ae471` | → "in his official parliamentary portrait, **taken this month** — …" | grounded: `DateTimeOriginal 2026-07-13`, and the issue is dated 2026-07-19 |

Four `.credit` spans were also corrected, because a bare "Wikimedia Commons" is not an attribution
and one of them was a false licence claim: → `Scottish Government · CC BY 2.0 · via Wikimedia
Commons`, `House of Commons · CC BY 3.0 · via …`, `MiracleMiles · CC BY 4.0 · via …`,
`Daniel Cooper · CC BY-SA 4.0 · via …`, and `US Government · public domain · via …`.

**→ HANDOFF 4 (WP-4 / WP-10): §3.9 has a blind spot, and the golden was sitting in it.** Three of the
five captions above **passed** §3.9 while being wrong, because `claim_max` is the largest *4-digit*
year in the band's prose and these bands spell their years out. The Touchline says "one hundred and
forty-nine years after the first Championships"; The Letter says "sixty-four years ago this week". The
check reported *"capture 2009, band makes no dated claim"* for a 2009 photograph captioned as **this
week's** Wimbledon final — a live defect-B instance, invisible to the gate. I corrected the captions
editorially rather than widen the check (not my file, and word-number parsing is a real decision, not
a tweak). The blind spot itself remains.

---

## Ownership — a write to a WP-8 file, under explicit grant

`assets/cached/manifest.json` is **WP-8's** under SPEC §2. I wrote to it under the coordinator's
explicit grant in the WP-3b brief. Recorded here so the ownership log stays truthful. Discipline
applied:

- Entries built by **importing WP-8's own `merge_entry()` and `write_manifest()`** from
  `scripts/mirror-images.py` rather than hand-writing JSON, so field set, `licence` sub-shape, key
  order and formatting are WP-8's, not mine. `mirror-images.py` itself is untouched.
- Merge-on-write semantics respected: gaps filled, **nothing overwritten** — the eight entries kept
  their existing `issues` / `led` / `issue_slugs` / `led_slugs` history untouched.
- **One deliberate exception, flagged:** `notes` was **appended to**, not replaced. WP-8's
  `_merge_scalar` fills a non-empty `notes` never — but each placeholder note asserts *"Source URL is
  unrecoverable"*, which is now false for these eight. Leaving it would have made the record
  self-contradictory. Each note now reads `<original> — SUPERSEDED IN PART: WP-3b (2026-07-26): …`
  with the recovery method and the exact field each value came from. The original sentence is
  preserved, not deleted.
- `fetched_at` stays `UNKNOWN` on all eight. The URL was **recovered** today; the asset was not
  re-fetched, and claiming a fetch time we do not have is the same class of error as guessing a year.

### Key-set diff — nothing pruned

```
$ python3 - (before = copy taken pre-edit; after = working tree)
weekly.json json.load OK — keys: 12
manifest.json json.load OK — entries: 438
key set identical: True | added: none | REMOVED: none
changed entries (8): ['161e21e690fa', '2a9d4f29c684', '65aa827ae471', 'a7143c11f458',
                      'ac225d893976', 'c0fbc060b733', 'e5e95fd4612f', 'f37adaa87280']
untouched entries: 430

$ git diff --numstat fa8c80c -- assets/cached/manifest.json
64      64      assets/cached/manifest.json
```

438 before, 438 after; 430 of 438 entries byte-identical; the 8 changed are exactly the 8 recovered.

---

## Steam: egress worked, and I still did not install the screenshots

Recorded because the grant was given and deliberately not spent.

```
$ curl -sS -m 25 "https://store.steampowered.com/api/appdetails?appids=1623730&l=english"
HTTP=200 bytes=35259
```

Egress is fine; WP-3's `in_engine` path is live. I skipped the install for three reasons, in order of
weight:

1. **It does not serve the task.** Both figures it would replace already carry a grounded
   `capture_year` of 2026. The `""` count would have gone 9 → 9.
2. **The grant is scoped to "only images the golden actually needs."** After the recovery above the
   golden needs none: every asset it already has now has a real URL, a real licence, and a year
   wherever one can be grounded.
3. **Cost/risk.** Installing means new `alt` text and new caption prose for images I would have to
   view and describe, on a fixture whose byte-identity is the regression — against zero movement on
   the stated goal.

**→ HANDOFF 5 (coordinator).** The *shape* gap WP-3 identified is real and is **still open**: neither
golden contains a single `gameplay` or `in_engine` figure, so the canonical worked example still
teaches `key_art` for game coverage — §3.13's rank 5 illustrating rank-1 subject matter. That is a
separate, genuinely worthwhile job (fetch, view, describe, re-caption, install, manifest), and it
should be scoped as one rather than smuggled in as a side effect of a provenance fix. WP-3's two
verified candidates (Palworld sky-island traversal; Halo Warthog ice cavern) are re-fetchable from
`appdetails` in one call.

---

## Verification — real output, all commands run

```
$ python3 -c "import json; json.load(open('.claude/skills/the-signal/references/format-skeletons/weekly.json'))"
weekly.json json.load OK — keys: 12

$ python3 -c "import json; json.load(open('assets/cached/manifest.json'))"
manifest.json json.load OK — entries: 438

$ python3 -m py_compile .claude/skills/the-signal/scripts/stitch_weekly.py
py_compile stitch_weekly.py OK

$ python3 (CSS structural check on 11-mx-coverage-rebuild.css)
braces balanced: True 25 25
forbidden .sp-/.hol- selectors: []
kinds present: ['championship', 'finance', 'gc', 'leaderboard', 'league', 'medal']
```

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh ; echo "EXIT=$?"
### FINAL — REAL OUTPUT ###
  PASS: 73   FAIL: 0   WARN: 3
=== weekly golden regression ===
  Size:   90,637 chars / 91,020 bytes
  [PASS] caption-vintage: 6 figure(s) with a dated capture year, all consistent with their band's
         claims: COVER [the_letter/lead, /assets/cached/161e21e690fa.jpg] — capture 2012, band makes
         no dated claim; FIG. 01 …
  [PASS] figure-provenance: all 7 .plate-img figure(s) carry the four-attribute provenance record
  [PASS] image-shapes/distinct: 4 distinct data-shows value(s) (floor 3): ['artefact', 'event_photo',
         'key_art', 'portrait']
  1 warning(s). PASS.

  FAIL — 7 error(s) found in '…/golden/weekly/chapter-plan.json':
  PRODUCTION HALT, not a ship failure. This is an upstream production aid (SPEC §1),
    (validate-chapter-plan weekly branch not present or plan-arg differs — skipping plan check)
      ↑ PRE-EXISTING, UNTOUCHED. WP-3's handoff 10; routed to WP-10. The harness swallows it.

=== mx-weekly golden regression (WP-8) ===
--- byte-identity vs committed expected.html ---
  byte-identical ✓
  Size:   162,039 chars / 162,679 bytes
  [PASS] caption-vintage: 10 figure(s) with a dated capture year, all consistent with their band's
         claims: COVER [the_letter/lead, /assets/cached/c0fbc060b733.jpg] — capture 2026, band makes
         no dated claim; FIG. 01 …
  [PASS] figure-provenance: all 14 .plate-img figure(s) carry the four-attribute provenance record
  [PASS] image-shapes/distinct: 7 distinct data-shows value(s) (floor 3): ['chart', 'diagram',
         'document', 'event_photo', 'key_art', 'map', 'portrait']
  [PASS] table-kind: 1 data-table-kind value(s), all legal: ['championship']
  [WARN] figure-provenance/licence-unknown: 4 figure(s) render data-licence="UNKNOWN":
         FIG. 02 [long_read, …/ebecfdf2c5a9.jpg]; FIG. [the_threads, …/d2f4e531313a.jpg];
         FIG. [the_threads, …/61aac2156d95.jpg]; FIG. [the_threads, …/0d3de2610c28.jpg].
  [WARN] image-urls: skipped per --skip-image-urls
  2 warning(s). PASS.

=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ===
EXIT=0
```

`expected.html` was **regenerated by the stitcher**, never hand-edited — the CSS change alone breaks
byte-identity, so it had to be. Its only drift from `fa8c80c` was verified, before regenerating, to be
exactly the new injected CSS plus the eight figures' attribute source and the caption/credit edits.

Nothing was rendered in a browser: the finance CSS is verified as present, brace-balanced,
alias-only and selector-correct, and it is **not exercised by any markup yet** — no fixture may
declare `finance` until WP-4's `TABLE_KINDS` accepts it (handoff 1). Someone should look at a finance
card once it can be stamped.

---

## Handoff summary

1. **→ coordinator / WP-4:** `validate-issue.py:1764` hardcodes the five values and **hard-fails** a
   sixth. Add `finance` to `TABLE_KINDS`; then stamp `data-table-kind="finance"` on the mx golden's
   Desk rate card (a one-line fixture change, mine, ready to make on your word). Better still, have
   the check read `weekly.json § structural_hooks.table_kind` so this cannot drift a third time.
2. **→ coordinator / WP-4:** the "`.mx-scorecard` with no `data-table-kind`" warning is per-**issue**,
   not per-**card** — one declared card silences it for every undeclared one. WP-3's note 9 assumed
   otherwise, and the Desk card's omission is currently silent.
3. **→ WP-6 / WP-2:** `component-contracts.md:230` says the enum is "Mandatory; **no sixth value**",
   and `sections.md:148` lists the five. Both need the §3.11 amendment.
4. **→ WP-4 / WP-10:** §3.9's `claim_max` only sees 4-digit years, so a band that spells its years out
   ("one hundred and forty-nine years after…") reports *"band makes no dated claim"* and the check
   cannot fire. A 2009 photograph captioned as this week's Wimbledon final passed. Corrected
   editorially here; the gap in the check is unfixed and is WP-4's call.
5. **→ coordinator:** the shape gap is still open — no `gameplay` or `in_engine` figure exists in
   either golden, so the canonical example still teaches key art for games. Scope it as its own job.
6. **→ WP-8:** eight `manifest.json` entries now carry real `url` / `licence` / `shows` /
   `capture_year`, written through your own `merge_entry()`. **`mirror-images.py` cannot reproduce
   this**: the recovery is a Commons SHA-1 lookup (plus thumbnail reconstruction for 1920px caches),
   confirmed by `sha256(url)[:12] == filename`. It is worth adding as a back-fill mode — the same
   method should recover a large share of the remaining 425 `UNKNOWN` entries, which is the durable
   fix for both `data-licence="UNKNOWN"` and `data-capture-year=""` across the whole archive, not just
   the goldens. Also note the *false* `allows_derivatives: false` on the mx cover (`c0fbc060b733`),
   corrected here: an over-restrictive licence record is not the safe direction for
   `extract-covers.py`, it just teaches people to route around the gate.
