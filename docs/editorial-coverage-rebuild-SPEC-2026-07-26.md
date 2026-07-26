# Editorial Coverage Rebuild — SPEC

**Date:** 2026-07-26
**Branch:** `claude/signal-antikythera-article-lzzlup`
**Status:** authoritative build plan. Implementation is tracked in `docs/editorial-coverage-rebuild-PROGRESS.md`.
**Trigger:** owner review of Issue #18 (2026-07-26). Issue #18 itself is **NOT to be modified** — it is the evidence exhibit and the regression fixture.

---

## 0. Why

Five defects were diagnosed against Issue #18 and the archive. Each has a structural cause in the
pipeline, not a writing cause. This spec fixes the structures.

| ID | Defect | Structural cause |
|----|--------|------------------|
| **A** | An evergreen Long Read reads as breaking news ("wow, they've just discovered this") | The plan has no field for a piece's vintage, so the stitcher stamps the issue date on every anchor and the validator cannot tell news from feature |
| **B** | A 2007 reconstruction photo illustrates a 2021 breakthrough | No image candidate carries a capture year; no check compares an image's vintage to the dated claims around it |
| **C** | UK politics led the cover 6 of 9 issues; a holding-pattern story keeps the lead | v8.37 retired `check-topic-lock.py` and left `lead_history` written-but-unread. The planner sees one week of history (`last_cover_lead`) and cannot see a rut. No demotion shape exists for the cover |
| **D** | Sunday-concluding events vanish (World Cup final, The Open); F1 saturates the Touchline (5 bands, one race) | (i) the coverage window is a **calendar range**, so a day can be "covered" while its results were unknowable at research time; (ii) `status:"upcoming"` facts are gate-checked then abandoned — nothing carries them forward; (iii) the Touchline carries 5 of 6 furniture objects in ≤600 words and every object is single-competition-shaped, so only a weekly-table sport can fill them; (iv) no sporting calendar exists; (v) the daily has 2 sport domains (football, golf) and no other sport is visible to the system |
| **E** | Images are safe and boring — game coverage is key art, the Long Read was Wikimedia-only | The taxonomy classifies images by **source domain**, never by **what the image shows**; and `compliance-checklist.md:424` actively ranks "official art/press kit" above "infographic that adds information", i.e. the spec prescribes key art. The specificity intent was dropped when `visual-smoke-test.py` was deleted (ledger says "image intent → gate 1", but gate 1 only checks HTTP 200) |

**Non-goals.** Do not reintroduce `check-topic-lock.py` or any suppression gate. Do not add a fourth
ship gate — new mechanical checks land **inside** the existing three (gate 1 = `validate-issue.py`
image checks, gate 2 = `validate-issue.py` markup contracts, gate 3 = the holistic read) or in the
**upstream production aids** (`validate-research-bundle.py`, `validate-chapter-plan.py`).

---

## 1. Build rules (read before touching anything)

1. **This file is the interface.** Work packages run in parallel and must not negotiate with each
   other. Every cross-WP contract — field name, attribute name, enum value, exact markup — is fixed
   in §3 below. If a contract here is wrong or impossible, **stop and report**; do not improvise a
   different one, because another WP is implementing against the written version.
2. **File ownership is exclusive.** §2 assigns every file to exactly one WP. Do not edit a file
   owned by another WP, even a one-line change. If you need a change in someone else's file, report
   it as a handoff note.
3. **Issue #18 is frozen.** `issues/signal_weekly_2026-07-26.html`, its assets, and
   `state/quality-log.jsonl` are read-only. New checks are *expected* to fail against #18 — that is
   the proof they work, and it is recorded, not fixed.
4. **No silent scope reduction.** If part of a WP can't be done, finish the rest and say exactly
   what you left and why.
5. **Every WP writes its own evidence file.** Write
   `docs/editorial-coverage-rebuild-EVIDENCE/WP-<N>.md`: what changed, files touched, the exact
   verification commands and their output, what's left, and any handoff notes. **Do not edit
   `docs/editorial-coverage-rebuild-PROGRESS.md`** — WPs run concurrently and a shared file loses
   writes. The orchestrator merges the evidence files into the PROGRESS ledger.
   *(Exception: WP-1 ran alone before this rule and wrote to PROGRESS directly.)*
6. **Verification is evidence, not assertion.** "I added the check" is not done. Done is: the check
   fires on a known-bad input and passes on a known-good one, with the command and its output
   recorded in PROGRESS.

---

## 2. File ownership map

No file appears twice. Anything not listed is unowned — report before touching.

| WP | Title | Exclusive files |
|----|-------|-----------------|
| **WP-1** | Data contracts (foundation) | `.claude/skills/the-signal/references/chapter-plan-schema.md`, `.claude/skills/the-signal/references/spec/data-contracts.md` *(new)*, `state/signal-state.json` |
| **WP-2** | Editorial prose spec | `.claude/skills/the-signal/references/editorial-spec.md`, `.claude/skills/the-signal/references/sections.md` |
| **WP-3** | Structure of record + stitcher + CSS | `.claude/skills/the-signal/references/format-skeletons/weekly.json`, `.claude/skills/the-signal/scripts/stitch_weekly.py`, `.claude/skills/the-signal/assets/css/**` |
| **WP-4** | Rendered-issue checks | `.claude/skills/the-signal/scripts/validate-issue.py` |
| **WP-5** | Upstream production aids | `.claude/skills/the-signal/scripts/validate-research-bundle.py`, `.claude/skills/the-signal/scripts/validate-chapter-plan.py` |
| **WP-6** | Image taxonomy + specificity doctrine | `.claude/skills/the-signal/references/image-source-types.json`, `.claude/skills/the-signal/references/compliance-checklist.md`, `.claude/skills/the-signal/references/component-contracts.md`, `.claude/skills/the-signal/scripts/check-image-diversity.sh` |
| **WP-7** | Daily inputs | `functions/daily/feeds.js`, `functions/daily/profile.js` |
| **WP-8** | Asset provenance + licence safety | `scripts/mirror-images.py`, `scripts/extract-covers.py` |
| **WP-9** | Pipeline phase wiring | `.claude/skills/the-signal/SKILL.md` |
| **WP-10** | Verification harness | `.claude/skills/the-signal/scripts/test-coverage-gates.sh` *(new)*, `.claude/skills/the-signal/references/fixtures/coverage-rebuild/**` *(new)* |
| **WP-11** | Daily routing (added 2026-07-26) | `functions/daily/render.js`, `functions/daily/dedup.js` |
| **WP-12** | Skill version + changelog (added 2026-07-26) | `.claude/skills/the-signal/CHANGELOG.md`, and the skill-version marker wherever it lives |

**Ownership correction (2026-07-26): `references/golden/weekly-mx/**` belongs to WP-3.** The map's third
gap. WP-3's brief told it to handle golden parity deliberately, but the golden fixture itself was left
unowned — so a file the build was always going to have to regenerate had no owner. It is WP-3's,
because WP-3 owns the stitcher that produces it. WP-10 (verification harness) must therefore treat the
regenerated golden as an **input it checks**, never a file it edits: a harness that can rewrite its own
expected output proves nothing.

**WP-12 exists because the map had a second gap.** WP-9 reported it: the skill keeps a `CHANGELOG.md`
and a version convention (`v8.43` at time of writing), and no WP owned either — so a rebuild touching
the plan schema, the structure of record, the stitcher, both validators and the phase wiring would
have shipped with no version bump and no changelog entry. WP-12 runs **last**, after WP-10, so it can
describe what actually landed rather than what was planned.

**WP-11 exists because the original map had a gap.** WP-7 added sport feeds and domains but the code
that *routes* them was unowned, so its work is partially inert: `render.js:386`'s `NEWS_SPORT` set
gates headline eligibility and lists only `world, local, finance, football, golf`, so a cricket or
athletics story cannot lead Headlines however big it is; `render.js`'s `DOMAIN_LABELS` has no label
for the new domains; and `dedup.js:54`'s `RELAXED_DOMAINS` contains only `football`, while the BBC
publishes 3–4 variants of every cricket match report.

**Dependency order:** WP-1 first, alone. Then WP-2, WP-3, WP-6, WP-7, WP-8, WP-9 in parallel. Then
WP-4, WP-5 (they check what WP-3 renders). Then WP-10.

---

## 3. Contracts

These are normative. Field names, attribute names and enum values are exact.

### 3.1 Chapter-plan additions (WP-1 defines; WP-5 enforces)

```jsonc
"issue_meta": {
  // CORRECTED 2026-07-26 (WP-9 finding). The original comment here read "the window's opening
  // bound", which contradicted this very example. To be unambiguous:
  //   research_cut_at  = THIS issue's cut  == window.to   (the newly measured instant)
  //   window.from      = the PREVIOUS issue's research_cut_at, read from state
  // So the window is (previous cut, this cut]. The same wrong phrasing was mirrored into
  // chapter-plan-schema.md and is corrected there too.
  "research_cut_at": "2026-07-26T02:10:00Z",   // ISO8601; == window.to
  "window": { "from": "2026-07-19T02:14:00Z", "to": "2026-07-26T02:10:00Z" },
  "cover_leads_on": "news" | "long_read",       // REQUIRED
  "lead_rationale": "…",                        // REQUIRED, ≥120 chars, names what was considered and rejected
  "lead_override_reason": "…"                   // REQUIRED only when the rut rule (§3.6) trips
}
```

```jsonc
// on the long_read chapter brief
"long_read": {
  "vintage": "news" | "evergreen",              // REQUIRED
  "material_span": "1901–2021",                 // REQUIRED when evergreen; en-dash
  "latest_development": "2021-03"               // REQUIRED when evergreen; YYYY-MM
}
```

```jsonc
// on the week_in_numbers chapter brief — each row declares where its datum came from
"week_in_numbers": {
  "rows": [ { "key": "Pole Margin", "source_band": "touchline" },
            { "key": "Training Volume", "source_band": "state" } ]   // source_band REQUIRED
}
// source_band value set (WP-1 correction, 2026-07-26): the `chapter_id` of a chapter present in
// this plan, OR the literal "state". The Week in Numbers is partly a PERSONAL stat strip rendered
// from state/signal-state.json, so those rows have no originating band. WP-5 MUST accept "state"
// or the contract is unsatisfiable for the section as specified in chapter-plan-schema.md (v8.36).
```

### 3.2 Research-bundle additions (WP-1 defines; WP-5 enforces)

```jsonc
"image_candidates": [{
  // …existing bundle fields unchanged. NOTE (WP-1 correction, 2026-07-26): the bundle's URL key is
  // `url_or_keyword`, NOT `url`. The real existing keys are `url_or_keyword`, `verified`,
  // `source_type`, `context`, optional `direct_cdn`. `role` and `source_constraint` belong to the
  // CHAPTER PLAN's `images_needed[]`, not the bundle. WP-5/WP-8 must read `url_or_keyword`.
  "shows": "event_photo",        // REQUIRED, enum §3.3
  // SIMPLIFIED 2026-07-26 (WP-5 finding). This originally read "null ONLY when shows ∈ {diagram,
  // chart} AND the asset is synthetic" — but nothing recorded synthetic-ness, so half the condition
  // was unverifiable and WP-5 had to hard-fail the enum half and merely warn on the rest. Resolved by
  // DELETING the synthetic clause rather than adding a field for it: a diagram or a chart is
  // synthetic by nature, so the enum was already doing all the work. null is legal iff
  // shows ∈ {diagram, chart}. No `synthetic` field exists or should be added.
  "capture_year": 2007,          // REQUIRED; null legal iff shows ∈ {diagram, chart}
  "licence": {                   // REQUIRED, replaces the free-text credit as the machine record
    "holder": "Mogi Vicentini",
    "code": "CC-BY-2.5",         // SPDX-ish token, or "PRESS-KIT-EDITORIAL" | "PUBLIC-DOMAIN" | "CC0" | "UNKNOWN"
    "url": "https://creativecommons.org/licenses/by/2.5/",
    "allows_derivatives": true   // REQUIRED; false for any ND licence
  }
}]
```

```jsonc
"facts": [{
  // …existing fields (claim, status, date, source_url) unchanged…
  "resolves_loop": "loop_2026-07-19_wc-final"   // OPTIONAL; set when this fact closes an open loop
}]
```

### 3.3 The `shows` enum — what an image depicts (WP-6 canonicalises in `image-source-types.json`)

Orthogonal to `source_type`. A press kit can supply `key_art` or `gameplay`; the domain does not tell
you which.

`event_photo` · `gameplay` · `in_engine` · `key_art` · `product_shot` · `portrait` · `diagram` ·
`map` · `chart` · `artefact` · `document`

Definitions that matter for the checks:
- `gameplay` — player's view, in-game HUD present.
- `in_engine` — cutscene/render, no HUD. Better than key art, not gameplay.
- `key_art` — marketing art, usually with the logo composited in.
- `artefact` — the physical object itself (museum/archive).
- `document` — a page, screen, listing or record (e.g. a store listing).

### 3.4 Rendered markup contracts (WP-3 emits; WP-4 checks)

**Long Read vintage.**
```html
<section class="longread" data-role="long-read" data-vintage="evergreen">
  <div class="lr-title">
    <div class="mono" style="color:var(--signal);">TWO THOUSAND YEARS, ONE CRANK</div>
    <div class="mono lr-vintage">NOT THIS WEEK · A STANDING STORY · 1901–2021 · LATEST DEVELOPMENT MAR 2021</div>
    <h2>…</h2>
    <p class="stand">…</p>
    <p class="mono byline">BY THE EDITOR · THE LONG READ · A STANDING STORY</p>
  </div>
```
- `data-vintage` is **always** present, `news` or `evergreen`.
- When `evergreen`: `.lr-vintage` is present; the `.byline` **must not** contain the issue date.
- When `news`: `.lr-vintage` is absent; the `.byline` keeps `· DD MON YYYY` as today.

**Figure provenance.** Every `.plate-img` carries the machine record:
```html
<div data-mx-event="figure" class="plate-img" data-shows="in_engine" data-capture-year="2007"
     data-licence="CC-BY-2.5" data-allows-derivatives="true">
```

**Letter framing when the anchor is evergreen.** The paragraph in The Letter that introduces the
Long Read carries `data-lr-framing="feature"`. Presence is what is checked; the wording stays
editorial.

**Results ledger.** The Touchline's ledger is results-of-record, and every row declares its sport:
```html
<div class="mx-ledger" data-mx-event="ledger" data-role="results-ledger">
  <div class="mx-ledger__row" data-sport="football">…</div>
  <div class="mx-ledger__row" data-sport="golf">…</div>
```

**Polymorphic table.** `.mx-scorecard` gains `data-table-kind` ∈
`league` · `medal` · `gc` · `leaderboard` · `championship`.

**Resolved loop.** Any element reporting a carried-forward result carries
`data-resolves-loop="<loop id>"`.

**Demoted lead.** The Close's policy ledger:
```html
<div class="mx-ledger" data-mx-event="ledger" data-role="demoted-lead">
```

### 3.4a As-built reconciliation (WP-3 complete, 2026-07-26) — **WP-4 implements against THIS**

WP-3 has shipped. Where the as-built differs from §3.4 above, the as-built wins; §3.4's *values* are
all unchanged.

1. **Two attributes beyond §3.4's list.** `data-cover-leads-on="news|long_read"` on
   `<header class="cover">`, and `data-nav-band="<band_id>"` on every `[data-station]`. Documented in
   `weekly.json` § `structural_hooks.cover_leads_on`.
2. **Never name a new attribute `data-station*`.** `validate-issue.py`'s navigator tally is
   `re.findall(r'\bdata-station\b')`, which double-counted WP-3's first attempt (`data-station-band`)
   and failed the nav-count invariant. Renamed to `data-nav-band`.
3. **`data-capture-year=""` is the legal null rendering** — empty string, not `"UNKNOWN"`, not absent.
   §3.9's caption-vintage rule applies **only to a non-empty 4-digit value**; treat `""` as "no year to
   compare". A value that is neither empty nor 4 digits must fail: the stitcher never emits one, so it
   came from a writer.
4. **`.lr-title` is writer-authored, not stitcher-generated.** §3.4 assumed otherwise. The stitcher
   *normalises* the block instead. No contract value changed. Moving generation into the stitcher is
   the cleaner end-state but needs both goldens' `chapters/long_read.html` and a decision about whether
   writers keep the headline and standfirst — deliberately out of scope.
5. **`fixtures_ledger` is renamed.** The Touchline object is now `results_ledger` (concluded results)
   plus a separate `fixtures_lookahead` (forward fixtures, moved to On the Radar). §3.11's prose still
   says `fixtures_ledger`; the live skeleton is authoritative.
6. **Figure provenance is 0-of-14 today, by construction.** WP-3 stamps figure attributes only from
   `assets/cached/manifest.json`, and all 438 of WP-8's entries are `UNKNOWN`/`null` back-fills — so
   **every `.plate-img` attribute must currently come from the writer**, and only WP-4 can fail its
   absence. WP-3 hard-fails via `--strict-figure-provenance`, off by default because it would fail
   every current fixture.
   *Cross-WP bug caught here and worth remembering:* WP-3 initially stamped those placeholders
   literally, rendering `data-shows="UNKNOWN"` and `data-allows-derivatives="false"` — which would have
   made the entire legacy archive look ND-restricted and poisoned WP-8's licence gate. Placeholders are
   now never stamped: the attribute stays absent and is reported as a gap.
7. **`results_ledger_multi_sport` needs two inputs the HTML does not contain** — state's
   `interest_depth` and `sports_calendar` — to know whether ≥2 tracked sports concluded in-window. WP-4
   therefore needs `--state`.

### 3.5 State additions (WP-1 owns the file; WP-9 wires the reads/writes)

```jsonc
"research_cut_at": "2026-07-26T02:10:00Z",     // written at publish; opens the next window
"open_loops": [{
  "id": "loop_2026-07-19_wc-final",
  "claim": "World Cup final, Spain v Argentina, MetLife",
  "expected_resolution_date": "2026-07-19",
  "band": "touchline",
  "issue_opened": 17,
  "status": "open" | "resolved" | "dropped",
  "resolution": null                            // filled when resolved; free text + source_url
}],
"cover_lead_ledger": [{                         // last 12, newest first
  "issue": 18, "date": "2026-07-26",
  "topic_family": "uk_politics",
  "one_line": "Burnham's first ordinary week",
  "led_on": "news"
}],
"sports_calendar": [{
  "event": "The Open Championship", "sport": "golf",
  "start": "2026-07-16", "end": "2026-07-19",
  "importance": 1,                               // 1 = must appear, 2 = should, 3 = if room
  "reader_relevant": true,
  "needs_verification": true                     // Phase 0 confirms dates against sources before use
}],
"used_image_urls": { "<sha256[:12]>": { "issues": [17, 18], "led": [17, 18] } },
"interest_depth": { "motorsport": "results_only", "football": "full", "golf": "majors_only" }
```

`interest_depth` values: `full` · `majors_only` · `results_only` · `off`.

**An absent key is `unset`, never `off` (WP-1 correction, 2026-07-26).** Only the sports the owner has
explicitly weighted are seeded (motorsport, football, golf). The sports WP-7 adds feeds for — cricket,
cycling, athletics — have no key. An absent key means *cover on news value*; reading it as `off` would
recreate defect D's invisible-sport problem in a new place. WP-9 must implement it that way.

**`research_cut_at` must be a measured write (WP-1 correction, 2026-07-26).** The seeded value is the
§3.5 literal, which the repo can bound but not confirm. WP-9 must overwrite it with a real instant at
publish, and Phase 0 must copy the *previous* value into `issue_meta.window.from`. Until that write
exists, D1 is inert — the window still cannot open where the last one closed.

**Topic-family enumeration gap (WP-1 finding, authorised 2026-07-26).** The closed enumeration in
`chapter-plan-schema.md` § Topic Family Enumeration has no family for cybersecurity / data-breach
news, so issue #8's cover lead (the Instructure/Canvas breach) could not be classified and was left
out of `cover_lead_ledger` — which silently narrows the rut rule's input. **Add family `cyber_privacy`**
and backfill issue #8 into the ledger. This is a `chapter-plan-schema.md` + `state` change, so it
stays with WP-1 (resumed), preserving the ownership map. Flagged for the owner as a judgement call:
it is a new editorial category, chosen because the reader profile carries world news, consumer tech
and AI, and a 275M-record breach has no other home.

### 3.6 The rut rule (WP-5)

Not suppression — a forced conscious choice. `validate-chapter-plan.py` **fails** a weekly plan when
all of:
- the same `topic_family` appears as `led_on: "news"` in **≥3 of the last 4** `cover_lead_ledger` entries, **and**
- this plan sets `cover_leads_on: "news"` with that same `topic_family`, **and**
- `issue_meta.lead_override_reason` is absent or under 80 chars.

The planner can always lead with it again — it just has to say why in writing.

**Missing field, added 2026-07-26 (WP-5 finding).** The rule above compares "this plan's
`topic_family`" against the ledger — but **no contract field carried it**. §3.1 defined
`cover_leads_on` and `lead_rationale` and never the family itself, so the rule had nothing to compare.
WP-5 shipped a fallback chain (explicit if supplied → `pieces[role=lead]` → warn) to avoid guessing.
**Add `issue_meta.cover_lead_topic_family`** (required for weeklies, drawn from the closed Topic Family
Enumeration in `chapter-plan-schema.md`, which now includes `cyber_privacy`). WP-1 owns the schema;
WP-5's fallback stays as a compatibility path for plans written before the field existed.

### 3.7 Open-loop resolution rule (WP-5 upstream, WP-4 rendered)

A loop is **matured** when `status == "open"` and `expected_resolution_date <= run_date`.

- `validate-research-bundle.py --run-date <today> --state state/signal-state.json`: **fail** if a
  matured loop has no `facts[]` entry with a matching `resolves_loop`.
- `validate-issue.py`: **fail** if a matured loop's id has no `data-resolves-loop` in the rendered
  HTML. (Both layers, because the bundle can carry a fact the writer then drops.)

### 3.8 Image shape budgets (WP-4)

Per rendered issue:
- **≥3 distinct** `data-shows` values across the issue.
- **Pixel & Byte:** at most **one** `key_art` in the band, and `key_art` **may not** be the band's
  lead figure (`.plate-img.lead`).
- **Never-lead, resolved 2026-07-26 (WP-6 finding).** WP-6's reconciliation made
  `never_lead_shapes = {key_art, product_shot, portrait}` (all of rank 5), which is **broader than
  this section's original letter** (Pixel & Byte + `key_art` only), and it correctly asked for a
  conscious choice rather than guessing. The resolution, which WP-4 implements:
  - **`key_art` and `portrait`: never a lead, issue-wide, any band.** Both are substitutes for showing
    the thing itself — key art is the logo, a posed portrait is the person not doing the thing. This is
    exactly the "random Pope photo" failure, and it is the defect the owner named ("every time we talk
    about a game we just get cover art").
  - **`product_shot`: may lead only when the band's subject IS the product** — a hardware launch or
    review, where the device genuinely is the most informative image. It may **not** lead a software,
    game or service band, where it is a box standing in for a thing that moves.
  A blanket issue-wide ban on all three would have been simpler and wrong: it would break legitimate
  hardware coverage, which this reader gets (Garmin, Whoop, Pixel, Xiaomi, e-readers).
- **Long Read:** **≥1** figure with `data-shows` ∈ {`diagram`, `map`, `chart`, `artefact`}.
- **Touchline:** any figure captioned as a concluded result must be `event_photo`.
- **Cross-issue:** a `src` that `led` the previous issue may not lead this one (reads
  `used_image_urls` via the asset manifest, §3.9).

### 3.9 Caption vintage rule (WP-4) — fixes defect B mechanically

For each `.plate-img` with a non-null `data-capture-year`:
let `claim_max` = the largest 4-digit year in 1500–2100 appearing in the **prose** of the enclosing
band (excluding figure captions). If `data-capture-year < claim_max`, then the caption's **visible
sentence** — `.plate-cap .txt`, *excluding* the `.credit` span — **must contain the capture year as a
4-digit string**. Otherwise: fail.

*Worked example (why this is right):* Issue #18 FIG 03 has `capture_year` 2007, its band claims 2021,
and its `.txt` reads "A working modern reconstruction of the front dial…" with the year only in
`.credit`. → **fails**, correctly. Rewriting `.txt` to "a 2007 working reconstruction, built on the
pre-2021 understanding" → passes.

### 3.10 Asset manifest (WP-8) — provenance must survive publish

`mirror-images.py` currently names files `sha256(url)[:12]` and **discards the URL**, so a caption's
provenance claim cannot be audited after publish (verified: ~400 Commons candidates reverse-hashed,
no match). Add `assets/cached/manifest.json`:

```jsonc
{ "<sha256[:12]>": {
    "url": "https://…", "fetched_at": "…",
    "licence": { "holder": "…", "code": "…", "url": "…", "allows_derivatives": true },
    "shows": "in_engine", "capture_year": 2007,
    "issues": [18], "led": [18] } }
```

`extract-covers.py` **must refuse** to crop/resize a source whose `licence.allows_derivatives` is
`false`, and exit non-zero with a clear message naming the file and licence. Issue #18's cover source
is CC BY-**ND** and is currently smart-cropped into `assets/covers/` — a real, live violation. The
fix is forward-looking: **do not re-crop or delete #18's existing cover**; the check applies to new
issues.

### 3.11 Touchline restructure (WP-3 structure, WP-2 doctrine, WP-4 checks)

In `weekly.json`:
- `touchline.target_words` → `{ "min": 500, "max": 800 }` (was 350–600). Five furniture objects in
  ≤600 words is what forces single-competition coverage. **This raises prose, it does not cut
  furniture** — density is events-per-screen, and a 6-row ledger across 4 sports is the same density
  as 6 rows of one race.
- `furniture_layer.components.fixtures_ledger` → **results ledger**: concluded results since the
  research cut, one row per event, `data-sport` on every row. Forward fixtures move to On the Radar.
- `furniture_layer.components.standings_card` → polymorphic per §3.4 `data-table-kind`.
- `furniture_layer.components.dial_signature` → **optional** (drop "recommended"); retargetable to
  whatever leads.
- New invariant `results_ledger_multi_sport`: the results ledger must carry **≥2 distinct
  `data-sport` values** whenever ≥2 tracked sports had an event conclude in-window.

**Sport tokens — one vocabulary, and `multi_sport` is not a result (added 2026-07-26).** WP-7 reported
that `state.sports_calendar[].sport` uses `multi_sport` for the Commonwealth Games while the daily's
new catch-all domain is `sport`. Left alone this opens a hole in the invariant above: a games whose
rows all carry `data-sport="multi_sport"` would collapse ten sports into one token, and a ledger of
`[motorsport, multi_sport]` would pass "≥2 distinct" while telling the reader nothing about breadth.

Resolution — three namespaces, explicitly related, canonicalised by **WP-1** in
`references/spec/data-contracts.md`:
- **Sport token** (canonical): a specific sport — `football`, `golf`, `cricket`, `cycling`,
  `athletics`, `motorsport`, `swimming`, `boxing`, `rugby`, `tennis`, … This is what `data-sport`
  carries.
- **`sports_calendar[].sport`**: may additionally take `multi_sport`, because it classifies an *event*
  (a games), not a result.
- **Daily domain** (`functions/daily/profile.js`): a separate routing namespace that may differ
  (`sport` as a catch-all); document the mapping, do not force the names to match.

**`data-sport="multi_sport"` is forbidden — WP-4 must reject it.** A result belongs to a sport; rows
derived from a multi-sport games carry the specific sport (`athletics`, `swimming`, …).

**Hard-fail vs warn (WP-1 round 3, 2026-07-26).** WP-1 canonicalised **22** sport tokens in
`data-contracts.md` § Sport tokens. WP-4 must **hard-fail** `data-sport="multi_sport"` but only **warn**
on a token outside the 22 — a closed list that hard-fails would block a ship on the multi-sport-games
long tail (lawn bowls, para events), and a breadth check that blocks breadth is self-defeating. WP-1
extends the list by appending. `multi_sport` is also barred as an `interest_depth` key. **WP-3:** every
`.mx-ledger__row` carries a specific token, *including* rows derived from a games.

### 3.12 Sports calendar seeding (WP-1)

Seed `sports_calendar` for the remainder of 2026 with recurring/announced majors only. **Every seeded
entry gets `needs_verification: true`** and Phase 0 confirms its dates against a source before the
planner relies on it — the seed is a prompt to check, never a fact of record. Do not invent results,
venues or fixtures.

### 3.13 Specificity hierarchy rewrite (WP-6)

`compliance-checklist.md:424` currently ranks *"official art/press kit for the specific subject"* at
2 and *"infographic or map that adds information"* at 3, and instructs "find official art for that
game". Replace the ranking with information-gained order:

1. photograph or still of the actual thing happening (`event_photo`, `gameplay`)
2. diagram / map / chart carrying information the prose cannot
3. the artefact or primary document itself
4. in-engine or in-context still
5. key art / product shot / posed portrait — **last resort, never a lead**

Keep the "random Pope photo" worked example; it is still correct. Add the Halo worked example: key
art with the logo composited in tells the reader nothing the headline didn't — Steam's `appdetails`
API returns a `screenshots[]` array per game and `shared.fastly.steamstatic.com` is **already** in
the domain map.

### 3.14 Source ladder (WP-6)

Retire `wikimedia_max_pct` and `wikimedia_max_count`. A ceiling reads as a target: Commons became the
default to fill up to, while nothing set a floor for the interesting shapes. Replace with
`min_distinct_shapes: 3` (§3.8) and add a new source type `open_access_journal`.

Add to `domains` (note: `media.springernature.com`, `images.metmuseum.org`,
`shared.fastly.steamstatic.com`, `loc.gov`, `archive.org` and the Flickr farms are **already
present** — the gap was never the source list): Getty **Open Content** (the museum, not the agency),
Rijksmuseum, Smithsonian Open Access, Europeana, Gallica/BnF, NYPL Digital Collections, Wellcome
Collection, British Library on Flickr, David Rumsey (maps), plus generic DOI/open-access-journal
handling so "the paper's own figures" becomes the reflex for any science piece.

*Worked example of the cost:* the Antikythera Long Read needed the 2021 Freeth *Scientific Reports*
figures — CC BY, on an already-whitelisted domain — and went to Commons for a 2007 perspex model
instead.

### 3.15 Daily inputs (WP-7)

`functions/daily/feeds.js` carries 10 football + 5 golf feeds and nothing else; `profile.js` has
exactly two sport domains. Every other sport is invisible to the whole system.

- Add feeds: generic BBC Sport, cricket, cycling, motorsport, athletics (BBC Sport sub-feeds plus one
  reputable specialist each where a stable RSS URL exists).
- Add matching `profile.js` domains with `edition: "sport"`.
- Weight motorsport **low**, consistent with `interest_depth: results_only` — big results in scope,
  session-by-session out.
- Do not change existing football/golf weights.

---

## 4. Acceptance criteria

A WP is done when its checks demonstrably fire. WP-10 builds the harness and records evidence.

| # | Assertion | Verified by |
|---|-----------|-------------|
| 1 | A weekly plan whose `long_read` omits `vintage` is rejected | WP-5 |
| 2 | An evergreen anchor renders `.lr-vintage` and a date-free byline; a news anchor renders neither | WP-3 + WP-4 |
| 3 | Issue #18 **fails** the caption-vintage check at FIG 03, and a corrected fixture passes | WP-4 + WP-10 |
| 4 | A plan leading `news` on a topic_family that led 3 of the last 4, with no override reason, is rejected | WP-5 |
| 5 | A matured open loop with no resolving fact fails the bundle gate | WP-5 |
| 6 | A matured open loop absent from the rendered HTML fails `validate-issue.py` | WP-4 |
| 7 | A results ledger with one `data-sport` fails when ≥2 tracked sports concluded in-window | WP-4 |
| 8 | Issue #18 **fails** the shape-budget check (Pixel & Byte leads on `key_art`; Long Read has no diagram/map/chart/artefact) | WP-4 + WP-10 |
| 9 | `extract-covers.py` exits non-zero on an `allows_derivatives: false` source | WP-8 |
| 10 | `mirror-images.py` writes `assets/cached/manifest.json` with url + licence per hash | WP-8 |
| 11 | The daily surfaces a cricket/cycling/athletics item (feed parses, domain routes) | WP-7 |
| 12 | `check-image-diversity.sh` no longer reads the retired Wikimedia thresholds and enforces `min_distinct_shapes` | WP-6 |

**Expected-failure ledger.** Issue #18 must fail #3 and #8 after this work. Those failures get
recorded in PROGRESS as evidence. **#18 is not to be repaired.**

**Fixtures for #5 and #6 (WP-1 correction, 2026-07-26).** The two `open_loops` seeded in state are
`status: "dropped"` — honest history, since neither the World Cup final nor The Open was ever reported
and #18 is frozen. **A dropped loop does not mature**, so those seeds will not by themselves make the
§3.7 gates fire. WP-10 must build a fixture carrying `status: "open"` with a past
`expected_resolution_date` to demonstrate #5 and #6, and must show both the firing case and the
passing case (loop resolved by a fact / by `data-resolves-loop` in the HTML).

---

## 5. Out of scope

- Regenerating or amending any published issue.
- The holistic-read rubric (`quality-rubric.md`) — the new mechanical checks deliberately sit
  upstream of it, and gate 3 stays a judgement.
- A fourth ship gate.
- Making the archive private / `robots.txt` / access-gating. Discussed, deferred — it changes the
  licensing posture and is the owner's call, not a build task.
- Backfilling `sports_calendar` beyond 2026, or asserting any 2026 result.
