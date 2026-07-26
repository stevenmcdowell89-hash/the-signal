# WP-6 — Image taxonomy + specificity doctrine (defect E)

**Date:** 2026-07-26 · **Branch:** `claude/signal-antikythera-article-lzzlup` · **SPEC:** §3.3, §3.4, §3.8, §3.13, §3.14, AC #12

---

## 1. What the defect actually was

The bottleneck was never the source list. Three things, all inside WP-6's files:

1. **The taxonomy typed images by source domain, never by what they show.** A press kit is good provenance, so the safest, most-available press-kit asset — key art with the logo composited in — scored full marks. Issue #18 passed `min_distinct_source_types: 3` comfortably.
2. **The checklist actively prescribed the boring shape.** `compliance-checklist.md:424` ranked *"official art/press kit for the specific subject"* at 2, *"infographic or map that adds information"* at 3, and instructed verbatim *"find official art for that game"*. The researcher fetched Halo key art **because the spec told it to.**
3. **The Wikimedia cap made Commons the default** — a ceiling with no matching floor reads as a target.

Proved below: a four-image issue in which **every single picture is key art** and every domain was already whitelisted **PASSES the pre-WP-6 check** (§4.2).

## 2. Files touched (all four are WP-6's, no others)

| File | Change |
|---|---|
| `.claude/skills/the-signal/references/image-source-types.json` | v1 → **v2**. Canonical `shows` enum block; new `open_access_journal` type; 25 domains added, 1 reclassified, 0 removed; 3 `ambiguous_domains`; `min_distinct_shapes: 3`; Wikimedia thresholds retired into a `retired_thresholds` record. |
| `.claude/skills/the-signal/references/compliance-checklist.md` | Specificity hierarchy rewritten to §3.13 information-gained order; Pope example kept, Halo + Antikythera examples added; the mechanical/judgement split spelled out; new mechanized Gate-3 shape-diversity item; gate-ledger line for `check-image-diversity.sh` updated to name both axes. |
| `.claude/skills/the-signal/references/component-contracts.md` | `.plate-img` provenance record (4 attributes, table of why); results ledger; polymorphic scorecard; demoted-lead ledger; `data-resolves-loop`; `.fig-foot` wired to `open_loops`. Markup copied verbatim from SPEC §3.4. |
| `.claude/skills/the-signal/scripts/check-image-diversity.sh` | Wikimedia rules deleted; `min_distinct_shapes` + enum validity enforced; shape rules now run even when all assets are mirrored locally (the old script exited 0 in that case). |

> **Note on git state.** The orchestrator took WIP snapshot `9d354c9` (2026-07-26 11:22:30) mid-flight, which swept up `image-source-types.json` and `check-image-diversity.sh` while WP-6 was still running. Those two files therefore appear *committed*, and `image-source-types.json` was amended once after the snapshot (the Steam-CDN finding, §5.1). No files outside WP-6's four were touched.

## 3. The `shows` enum, canonicalised (SPEC §3.3)

Eleven values, closed set, now a first-class `shows` block in `image-source-types.json` alongside `types`:

`event_photo` · `gameplay` · `in_engine` · `key_art` · `product_shot` · `portrait` · `diagram` · `map` · `chart` · `artefact` · `document`

Each value carries `means` + `checks` (which downstream budget cares and why). The block also carries `specificity_hierarchy` (machine-readable §3.13 ranking), `information_figure_shapes` = `[diagram, map, chart, artefact]`, `last_resort_shapes` = `[key_art, product_shot, portrait]`, `never_lead_shapes` = `[key_art, product_shot]`. The script reads the enum from the file and never hardcodes it, so the two cannot drift.

Verified identical in meaning to `references/spec/data-contracts.md` § The `shows` enum (WP-1's mirror) and to SPEC §3.3 — same eleven values, same definitions for the five that the SPEC calls out.

```
$ python3 -c "import json; json.load(open('.claude/skills/the-signal/references/image-source-types.json'))"
(no output — valid)

$ python3 - <<'EOF'   # enum + domain-type integrity
...
JSON OK, version 2
domains: 172 | invalid type values: []
shows enum: 11 ['event_photo', 'gameplay', 'in_engine', 'key_art', 'product_shot', 'portrait', 'diagram', 'map', 'chart', 'artefact', 'document']
matches SPEC 3.3 exactly: True
hierarchy covers enum once each: True
thresholds: {'single_domain_max_pct': 50, 'min_distinct_source_types': 3, 'min_distinct_shapes': 3, 'min_unique_candidates': 16, 'max_uses_per_url': 1}
retired keys present in thresholds: []
```
(Re-run after the Steam-CDN addition: `json OK` / `domains: 173 invalid: []`.)

## 4. Acceptance criterion #12 — real output

`bash -n` clean:
```
$ bash -n .claude/skills/the-signal/scripts/check-image-diversity.sh
bash -n OK
```

Fixtures live in the scratchpad, **not** the repo:
`/tmp/claude-0/-home-user-the-signal/81541fa2-7765-5cd6-810f-5027bff091c8/scratchpad/wp6-fixtures/`

### 4.1 (a) fails `min_distinct_shapes`, (b) passes

The two fixtures are **identical in provenance** — same three domains, same three source types, no domain over 50%. Only the shapes differ. That isolation is the point: the new rule catches something no arrangement of domains can express.

```
$ bash .claude/skills/the-signal/scripts/check-image-diversity.sh .../fail-min-distinct-shapes.html
=== Phase 7.7: check-image-diversity.sh ===
Total images: 3
Distinct domains: 3
Labelled figures (data-shows): 3
Distinct shapes: 1 (floor 3)

By domain:
   1/3  (33.3%)  shared.fastly.steamstatic.com                  → press_kit
   1/3  (33.3%)  images.nasa.gov                                → government
   1/3  (33.3%)  gallica.bnf.fr                                 → archive

By source type: {'press_kit': 1, 'government': 1, 'archive': 1}

By shape (what the pictures SHOW): {'key_art': 3}

FAIL — rule violations:
  Shape diversity: 1 distinct shape(s) (['key_art']) < minimum of 3. This is the defect-E floor: an
  issue where every picture is the same safe shape (all key art, all portraits, all Commons artefacts)
  tells the reader nothing the headlines didn't. Reach up the hierarchy — information figures
  ['diagram', 'map', 'chart', 'artefact'] and photographs of the actual thing happening are the fix;
  ['key_art', 'product_shot', 'portrait'] are the last resort and never a lead.
[…remediation block…]
EXIT=1
```

```
$ bash .claude/skills/the-signal/scripts/check-image-diversity.sh .../pass-min-distinct-shapes.html
=== Phase 7.7: check-image-diversity.sh ===
Total images: 3
Distinct domains: 3
Labelled figures (data-shows): 3
Distinct shapes: 3 (floor 3)

By domain:
   1/3  (33.3%)  shared.fastly.steamstatic.com                  → press_kit
   1/3  (33.3%)  images.nasa.gov                                → government
   1/3  (33.3%)  gallica.bnf.fr                                 → archive

By source type: {'press_kit': 1, 'government': 1, 'archive': 1}

By shape (what the pictures SHOW): {'gameplay': 1, 'diagram': 1, 'event_photo': 1}

PASS — image diversity within thresholds on both axes (provenance + shape).
EXIT=0
```

### 4.2 The regression the old check could not see

`issue18-shaped-all-key-art.html` — 2 `press_kit` + 1 `government` + 1 `wikimedia`, four distinct already-whitelisted domains, Wikimedia at 1/4 = 25% (inside the retired 30% / 4-entry caps). **Every image is `key_art`.**

```
$ bash <pre-WP-6 script, git a73ac68, with the pre-WP-6 lookup> .../issue18-shaped-all-key-art.html
By source type: {'press_kit': 2, 'government': 1, 'wikimedia': 1}
PASS — image source diversity within thresholds.
EXIT=0

$ bash .claude/skills/the-signal/scripts/check-image-diversity.sh .../issue18-shaped-all-key-art.html
Distinct shapes: 1 (floor 3)
By shape (what the pictures SHOW): {'key_art': 4}
FAIL — rule violations:
  Shape diversity: 1 distinct shape(s) (['key_art']) < minimum of 3. […]
EXIT=1
```

A related finding while building that fixture: under the retired rules, **one** Commons image out of three breached `wikimedia_max_pct` (33.3% > 30%) while three key arts were fine. The ceiling was actively pricing the supplement and ignoring the shape.

### 4.3 Enum validity is a hard fail

`fail-bad-enum-value.html` — three distinct shapes, one of them the plausible typo `screenshot`:
```
By shape (what the pictures SHOW): {'gameplay': 1, 'screenshot': 1, 'event_photo': 1}
FAIL — rule violations:
  data-shows value(s) not in the canonical enum: ['screenshot']. The closed set is ['artefact', 'chart',
  'diagram', 'document', 'event_photo', 'gameplay', 'in_engine', 'key_art', 'map', 'portrait',
  'product_shot'] — see the `shows` block in references/image-source-types.json. A typo'd shape is
  invisible to every per-band budget in validate-issue.py, so this is a hard fail, not an advisory.
  Shape diversity: 2 distinct shape(s) (['event_photo', 'gameplay']) < minimum of 3. […]
EXIT=1
```

### 4.4 Issue #18 (frozen — recorded, not repaired)

```
$ bash .claude/skills/the-signal/scripts/check-image-diversity.sh issues/signal_weekly_2026-07-26.html
Labelled figures (data-shows): 0
Distinct shapes: 0 (floor 3)
Warnings:
  No external image URLs found — the provenance rules (single-domain cap, source-type diversity) are
  skipped for this file. The shape rules above still apply.
FAIL — rule violations:
  No data-shows attributes found — this issue is UNLABELLED […] If this is a pre-2026-07 issue, the
  failure is expected and correct — the taxonomy did not exist when it shipped.
EXIT=1
```
**The pre-WP-6 script on the same file:** `No external image URLs found — skipping diversity check.` `EXIT=0`. All of #18's assets are mirrored to `/assets/cached/`, so Phase 7.7 was a **complete no-op on the actual shipped issue** — it only ever checked issues that hotlinked. Fixed here by making the shape rules independent of the external-URL early exit. Add this to the expected-failure ledger alongside AC #3 and #8.

## 5. Domains added, with confidence

25 added, **0 removed**, 1 reclassified. Full provenance is recorded in the file itself under `_domains_added_2026_07_26`, split into three honesty buckets.

### 5.1 Verified — an asset was fetched and returned an image content-type
| Domain | Type | Evidence |
|---|---|---|
| `gallica.bnf.fr` | `archive` | `200 image/jpeg` — `/iiif/ark:/12148/btv1b8449691v/f1/full/full/0/native.jpg` |
| `images.nypl.org` | `archive` | `200 image/jpeg` — `/index.php?id=809053&t=w` |
| `journals.plos.org` | `open_access_journal` | `200 image/png` — `/plosone/article/figure/image?...pone.0000217.g001` |
| `iiif.elifesciences.org` | `open_access_journal` | `200 image/jpeg` — `/lax/09560%2Felife-09560-fig1-v1.tif/full/full/0/default.jpg` |
| `media.springernature.com` | **reclassified** `news_cdn` → `open_access_journal` | `200 image/png` on `art%3A10.1038%2Fs41598-021-84310-w/…Fig1_HTML.png` — **that DOI is the Freeth 2021 *Scientific Reports* Antikythera paper.** The correct Long Read figure was one HTTP request away on an already-whitelisted host. |
| `shared.akamai.steamstatic.com` | `press_kit` | `200 image/jpeg`. **A real gap found while writing the Halo example.** `appdetails?appids=976730` returns 15 `screenshots[]`, and the `path_full` host it hands back is `shared.**akamai**.steamstatic.com` — only the `fastly` twin was mapped. Both serve the identical path. Unmapped, every Steam gameplay screenshot would have classified as `unknown` and been *excluded from diversity counting* — the taxonomy would have penalised the correct image. |

### 5.2 Live host, no asset fetched — confident classification
`ids.si.edu` (Smithsonian Open Access IDS delivery; host 200, fabricated id 404'd as expected) · `pmc.ncbi.nlm.nih.gov` · `cdn.ncbi.nlm.nih.gov` · `www.davidrumsey.com` + `davidrumsey.com` · `www.getty.edu` + `getty.edu` · `www.europeana.eu` + `api.europeana.eu` · `www.frontiersin.org` + `frontiersin.org` · `www.mdpi.com` + `mdpi.com` (root 403 to HEAD = bot protection, not evidence either way) · `www.si.edu` + `si.edu`.

Caveats written into the file: **PMC free-to-read is not reuse-licensed** — read the article's licence line, record `UNKNOWN` rather than guess. **Europeana is an aggregator** — the asset usually lives on the contributing institution's host; credit the holding institution, never "Europeana".

### 5.3 Unverified in the wild — mapped on knowledge, flagged as such
- `media.getty.edu` (Getty's IIIF server; answered 503/404 to probes).
- `www.rijksmuseum.nl` + `rijksmuseum.nl` — **lowest confidence in the set.** Rijksmuseum API responses have historically pointed at third-party hosts; those are deliberately *not* mapped.
- `digitalcollections.nypl.gov` — unreachable from this sandbox; item pages are not image `src`s anyway, follow through to `images.nypl.org`.
- `www.flickr.com/photos/britishlibrary` — path-qualified exactly like the existing government Flickr accounts. The bytes come from `*.staticflickr.com`, so `source_type` must still be set explicitly (see `ambiguous_domains`).

### 5.4 Deliberately NOT mapped
- `doi.org` / `dx.doi.org` → `ambiguous_domains`: a DOI is a **resolver, never an image**. Resolve it, take the figure from the publisher's figure CDN, record *that* host. This is the generic DOI/open-access handling §3.14 asked for; the `open_access_journal` type is the other half.
- `lh3.googleusercontent.com` → `ambiguous_domains`: shared Google host, serves museum collections and arbitrary user content alike, carries **no provenance signal**.
- `royalsocietypublishing.org`, `ars.els-cdn.com`, `arxiv.org`, `cdn.akamai.steamstatic.com` (404 on the verified path shape) — omitted rather than guessed. A wrong host mapping is worse than a missing one: a missing host draws an advisory, a wrong one silently launders provenance.
- **Wellcome and `loc.gov` / `archive.org` / `images.metmuseum.org` / the Flickr farms were already present.** §3.14's point exactly.

## 6. Thresholds

**Retired** (moved out of `thresholds` into a `retired_thresholds` record so the retirement is auditable, with the rationale and the consumer handoff): `wikimedia_max_pct: 30`, `wikimedia_max_count: 4`.

**Added:** `min_distinct_shapes: 3`. **Unchanged:** `single_domain_max_pct: 50`, `min_distinct_source_types: 3`, `min_unique_candidates: 16`, `max_uses_per_url: 1`.

**New source type:** `open_access_journal` — "the paper's own figures", with the licence-is-per-article warning attached.

## 7. Dangling references to the retired thresholds — every hit

Final sweep, every hit in the repo:
```
$ grep -rn "wikimedia_max_pct\|wikimedia_max_count" . --exclude-dir=.git
docs/editorial-coverage-rebuild-SPEC-2026-07-26.md:403             the SPEC's own retirement instruction — prose
docs/editorial-coverage-rebuild-EVIDENCE/WP-2.md:190,245,273       WP-2's evidence: names them only as retired — prose
docs/editorial-coverage-rebuild-EVIDENCE/WP-6.md:…                 this file
.claude/skills/the-signal/references/spec/data-contracts.md:138    WP-1's prose: "replaces the retired …" — correct as written
.claude/skills/the-signal/references/editorial-spec.md:512         WP-2's prose: "the Wikimedia cap is retired … min_distinct_shapes: 3" — correct, and independently consistent with this WP
.claude/skills/the-signal/references/compliance-checklist.md:433   WP-6 prose: the de-villainising note
.claude/skills/the-signal/scripts/check-image-diversity.sh:24-25   WP-6 prose: the header's do-not-reinstate comment
.claude/skills/the-signal/references/image-source-types.json:291-293  WP-6: the retired_thresholds history record, OUTSIDE `thresholds`
.claude/skills/the-signal/scripts/validate-research-bundle.py:458,460,463,465   ← LIVE CODE READ. WP-5's file.
```

Only one **executable** consumer is left dangling, and it is not WP-6's file.

### 7.1 HANDOFF → WP-5 (blocking, reproduced)

`validate-research-bundle.py` reads `thresholds["wikimedia_max_count"]` and `["wikimedia_max_pct"]` **unguarded** at its Rule 2 (~lines 456–466). With the keys retired, the bundle gate raises `KeyError`. Reproduced against a minimal two-candidate bundle:

```
$ python3 .claude/skills/the-signal/scripts/validate-research-bundle.py .../minimal-bundle.json --run-date 2026-07-26
Traceback (most recent call last):
  File ".../validate-research-bundle.py", line 524, in <module>
    main()
  File ".../validate-research-bundle.py", line 458, in main
    if wm > thresholds["wikimedia_max_count"]:
            ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'wikimedia_max_count'
```

**WP-5 must delete both reads and replace them with a `min_distinct_shapes` check over `image_candidates[].shows`** (the bundle-side twin of §4.1). WP-5 runs *after* WP-6 in the SPEC dependency order, which is why the retirement lands first — but until WP-5 does it, Phase 3b crashes. The same note is recorded inside the JSON at `retired_thresholds.consumer_handoff`, so it survives even if this evidence file is not read.

*(Not edited by WP-6: §2 ownership is exclusive, and a one-line fix in another WP's file is still a fix in another WP's file.)*

## 8. The specificity hierarchy, as rewritten (§3.13)

`compliance-checklist.md` § Image specificity check now ranks by **information gained**:

1. a photograph or still of the actual thing happening (`event_photo`, `gameplay`)
2. a diagram / map / chart carrying information the prose cannot (`diagram`, `map`, `chart`) — *a promotion; it used to sit below press-kit art, which is exactly backwards*
3. the artefact or the primary document itself (`artefact`, `document`)
4. an in-engine or in-context still (`in_engine`)
5. key art / product shot / posed portrait — **last resort, never a lead**

- **Pope example kept** (still correct), now annotated with the shape values and the reason the map outranks the wire photo.
- **Halo example added:** the old wording is quoted as the cause — the researcher obeyed the spec — and the fix names the `appdetails` API, the verified 15-screenshot response for app id 976730, `path_full`, and the already-mapped Steam CDN hosts. The Antikythera case is folded in: both times the source list was fine and the taxonomy was the bottleneck.
- **Commons de-villainised:** the caps are gone; Commons is right when it holds the most *informative* image and wrong when it holds the most *convenient* one. A floor on shapes, not a cap on a domain, is what enforces that.
- **The mechanical/judgement split is now written down**, because "image intent → gate 1" was recorded in v8.38 while gate 1 only checked HTTP 200:
  - *Mechanical, read the exit codes:* `check-image-diversity.sh` (issue-wide distinct-shape floor + enum validity); `validate-issue.py` (per-band §3.8 budgets + §3.9 caption vintage).
  - *Judgement, stays this checkbox:* whether **this** picture is the most specific available picture of **this** thing.
  - Plus the anti-drift rule: the enum lives in exactly one place; a shape value in a script but not in the file is the drift starting again.
- New **mechanized Gate-3 item** for shape diversity, with the `grep -oE 'data-shows="[a-z_]+"' | sort | uniq -c` eyeball backstop.
- The gate-ledger line for `check-image-diversity.sh` now names both axes.

## 9. Component contracts added (markup verbatim from SPEC §3.4)

Nothing invented — WP-3 emits and WP-4 checks these in parallel, so every snippet was copied from §3.4.

- **`.plate-img` provenance record.** `data-mx-event="figure" class="plate-img" data-shows=… data-capture-year=… data-licence=… data-allows-derivatives=…` on the plate contract *and* on the Long Read's inline example, plus a table of what each attribute is for (including why `data-allows-derivatives` exists: #18's cover source is CC BY-**ND** and was smart-cropped) and the §3.8 budgets a writer must plan around.
- **`.mx-ledger[data-role="results-ledger"]`** with per-row `data-sport` — results of record, not fixtures; the `results_ledger_multi_sport` ≥2-sport invariant; the density argument (six rows of one race vs six rows across four sports).
- **`.mx-scorecard[data-table-kind]`** ∈ `league`·`medal`·`gc`·`leaderboard`·`championship`, mandatory, no sixth value.
- **`.mx-ledger[data-role="demoted-lead"]`** in the Close — with *why* it exists (there was no shape for demotion, so a holding-pattern story kept the cover) and the warning never to emit a bare `.mx-ledger` beside a roled one.
- **`data-resolves-loop`** as a cross-band contract: join key into `state.open_loops[].id`, goes on the element reporting the result, checked at both layers.
- **`.fig-foot` wired to `open_loops`** (§3.10 note). The decorative `[CARRIED FORWARD…]` placeholder — the only hint of continuity in the format, with no data behind it — now fills from an `open_loops` entry whose `status` is `open`, prefers the soonest-maturing loop, falls back to a totals line rather than inventing a cliffhanger, and pairs with `data-resolves-loop` when the panel reports a resolution ("the `.fig-foot` announces the debt; `data-resolves-loop` is how it gets paid"). `week_in_numbers.rows[].source_band` noted as the plan-side traceability field.

## 10. Repo state

```
$ git status --short      # at the close of WP-6
 M .claude/skills/the-signal/assets/css/weekly-mx/11-mx-coverage-rebuild.css   (WP-3, in flight)
 M .claude/skills/the-signal/assets/css/weekly/01-coverage-rebuild.css         (WP-3, in flight)
 M .claude/skills/the-signal/references/compliance-checklist.md    ← WP-6
 M .claude/skills/the-signal/references/format-skeletons/weekly.json           (WP-3, in flight)
 M .claude/skills/the-signal/references/image-source-types.json    ← WP-6
 M .claude/skills/the-signal/references/sections.md                            (WP-2, in flight)
?? docs/editorial-coverage-rebuild-EVIDENCE/WP-11.md                           (WP-11)
?? docs/editorial-coverage-rebuild-EVIDENCE/WP-2.md                            (WP-2)
?? docs/editorial-coverage-rebuild-EVIDENCE/WP-6.md               ← WP-6
```
**Every WP-6 entry in that list is one of WP-6's four files; every other entry belongs to another WP that is still running.** `check-image-diversity.sh` and `component-contracts.md` show *clean* only because the orchestrator took WIP snapshots mid-flight (`9d354c9` at 11:22:30 and a later one) that swept up WP-6's completed files. `image-source-types.json` shows modified because it was amended once after the first snapshot (§5.1, the Steam CDN finding). Nothing outside WP-6's four files was edited, and `docs/editorial-coverage-rebuild-PROGRESS.md` was not touched. Not committed — the orchestrator commits.

## 11. What's left / notes for the orchestrator

1. **WP-5 handoff is blocking** — §7.1. `validate-research-bundle.py` `KeyError`s until its Rule 2 is replaced with a `min_distinct_shapes` check over `image_candidates[].shows`.
2. **Expected-failure ledger addition.** Issue #18 now fails Phase 7.7 (unlabelled → cannot meet `min_distinct_shapes`). Recorded, not repaired. Also worth recording as its own finding: the pre-WP-6 Phase 7.7 check was a **no-op on every issue whose assets were mirrored locally**, which is every recent issue.
3. **WP-4 depends on the enum block** — `lookup["shows"]["values"]` keys are the closed set; `information_figure_shapes` / `never_lead_shapes` are provided machine-readable so §3.8's budgets need no second copy of the list.
4. **WP-10 fixtures.** The three scratchpad fixtures are deliberately outside the repo. If the harness wants permanent versions they belong under `references/fixtures/coverage-rebuild/` (WP-10's tree): `fail-min-distinct-shapes.html`, `pass-min-distinct-shapes.html` (provenance-identical, shapes differ), `fail-bad-enum-value.html`, `issue18-shaped-all-key-art.html` (the regression the old check passed).
5. **Not done, deliberately:** `min_distinct_shapes` is not enforced against the *research bundle* — that is WP-5's Rule 2 replacement, and duplicating it here would put the same rule in two owners' files. Per-band shape budgets are WP-4's; this script stays issue-wide.
6. **Watch item.** `min_distinct_shapes: 3` is a floor that a lazy issue can satisfy with `key_art` + `portrait` + `product_shot` — three shapes, all rank 5. Only WP-4's per-band budgets (no `key_art` lead, Long Read information figure) close that. If those land weakened, this floor is weaker than it looks; consider a rank-weighted floor next iteration.
7. **`www.rijksmuseum.nl` is the weakest entry in the file** and the first candidate for deletion if it ever misclassifies. Flagged in `_domains_added_2026_07_26.unverified_in_the_wild`.

---

# WP-6 follow-up (2026-07-26) — machine/prose list reconciliation

**Raised by:** WP-9, via the coordinator. **Baseline for diffs:** commit `d907035`. **Files touched:** all four are WP-6's; nothing else.

## F1. The bug

`image-source-types.json` → `shows.never_lead_shapes` was `["key_art", "product_shot"]`, while the rank-5 prose in `compliance-checklist.md` read *"key art / product shot / **posed portrait** — last resort, and never a lead figure."* WP-4 implements the never-lead check **against the machine list**, so as it stood a posed portrait could legitimately have led an issue while the written doctrine forbade it — and that is exactly the shape the "random Pope photo" rule exists to reject: a profile portrait standing in for a story about what someone actually did.

**Fixed:** `never_lead_shapes` = `["key_art", "product_shot", "portrait"]`.

**Rationale, now recorded in the file:** a *posed* portrait is `portrait`; a photograph of a person actually *doing* the thing is `event_photo`, which may lead freely. The restriction therefore costs nothing legitimate — including for a profile or an obituary, where a picture of the subject in action is both available and better.

## F2. Full reconciliation of every derived list, both directions

The prose ranks were parsed **out of `compliance-checklist.md` itself** (not retyped from memory) and compared to the JSON, so the reconciliation is a measurement rather than an assertion:

```
PROSE ranks parsed from compliance-checklist.md:      MACHINE specificity_hierarchy:
  rank 1 ['event_photo', 'gameplay']                    rank 1 ['event_photo', 'gameplay']
  rank 2 ['diagram', 'map', 'chart']                    rank 2 ['diagram', 'map', 'chart']
  rank 3 ['artefact', 'document']                       rank 3 ['artefact', 'document']
  rank 4 ['in_engine']                                  rank 4 ['in_engine']
  rank 5 ['key_art', 'product_shot', 'portrait']        rank 5 ['key_art', 'product_shot', 'portrait']

RECONCILIATION
  ranks identical both directions: True
  hierarchy partitions the enum exactly (each value once): True | count 11 of 11
  last_resort_shapes == rank 5: True ['key_art', 'product_shot', 'portrait']
  never_lead_shapes  == rank 5: True ['key_art', 'product_shot', 'portrait']
  information_figure_shapes: ['diagram', 'map', 'chart', 'artefact']
  compliance-checklist.md: info-figure set stated as diagram/map/chart/artefact x2
  component-contracts.md:  info-figure set stated as diagram/map/chart/artefact x2
  'document' in information_figure_shapes: False (SPEC §3.8 names four; asymmetry documented)
```

**Final membership, audited:**

| List | Members | Authority |
|---|---|---|
| `specificity_hierarchy` | 1 `event_photo`,`gameplay` · 2 `diagram`,`map`,`chart` · 3 `artefact`,`document` · 4 `in_engine` · 5 `key_art`,`product_shot`,`portrait` | SPEC §3.13. Partitions the 11-value enum exactly once — no value missing, none duplicated. |
| `information_figure_shapes` | `diagram`, `map`, `chart`, `artefact` | SPEC §3.8 (Long Read requirement). |
| `last_resort_shapes` | `key_art`, `product_shot`, `portrait` | = rank 5. |
| `never_lead_shapes` | `key_art`, `product_shot`, `portrait` | = rank 5, because in the prose "last resort" and "never the lead figure" are **one** rule. |

## F3. The other drift found — the `artefact` / `document` asymmetry

`document` shares rank 3 with `artefact` in the hierarchy but is **not** in `information_figure_shapes`. That is correct — SPEC §3.8 names four shapes for the Long Read requirement and `document` is not among them (a store listing is a primary source, not a figure that explains a mechanism) — but nothing said so, and a reader comparing the two lists would reasonably have read it as the same class of bug as F1. **Now stated explicitly in both places**: as `_derived_lists_doc.information_figure_shapes` in the JSON ("DELIBERATE ASYMMETRY, not drift") and as an italic note on rank 3 in the checklist prose. No membership changed.

No other machine/prose divergence found. The two `_doc` strings and the three files' info-figure statements all agree.

## F4. Consequential edits

- **`image-source-types.json`** — `portrait` added to `never_lead_shapes`; new `shows._derived_lists_doc` block recording, per list, what it means, which document is its authority, and the instruction to change prose and list in the same commit. It also names F1 as the drift that already happened, so the next reader knows the failure mode is real.
- **`compliance-checklist.md`** — rank 5 now carries the posed-portrait-vs-`event_photo` rationale and points at `shows.never_lead_shapes` ("the prose and the machine list are the same rule written twice"); rank 3 carries the asymmetry note.
- **`component-contracts.md`** — the plate contract said only "Key art is rank 5 of 5", which was true but narrower than the doctrine. It now reads: `key_art`, `product_shot` and `portrait` are all rank 5, last resort, and **never a `.plate-img.lead` in any band**, with §3.8's narrower mechanical minimum called out so a writer is not misled about what the validator currently enforces.
- **`check-image-diversity.sh`** — the remediation message asserted "…are the last resort and never a lead" while printing only `last_resort_shapes`. It now reads `never_lead_shapes` too and prints one clause when the lists coincide, two when they diverge. The message can no longer claim a rule the lookup does not hold.

## F5. Criterion #12 re-run — nothing regressed

```
$ bash -n .claude/skills/the-signal/scripts/check-image-diversity.sh
bash -n OK
$ python3 -c "import json; json.load(open('.claude/skills/the-signal/references/image-source-types.json'))"
json OK

$ bash …/check-image-diversity.sh …/fail-min-distinct-shapes.html
Labelled figures (data-shows): 3
Distinct shapes: 1 (floor 3)
By shape (what the pictures SHOW): {'key_art': 3}
FAIL — rule violations:
  Shape diversity: 1 distinct shape(s) (['key_art']) < minimum of 3. […] Reach up the hierarchy —
  information figures ['diagram', 'map', 'chart', 'artefact'] and photographs of the actual thing
  happening are the fix. ['key_art', 'product_shot', 'portrait'] are the last resort and may never
  be a lead figure.
EXIT=1

$ bash …/check-image-diversity.sh …/pass-min-distinct-shapes.html
Distinct shapes: 3 (floor 3)
By shape (what the pictures SHOW): {'gameplay': 1, 'diagram': 1, 'event_photo': 1}
PASS — image diversity within thresholds on both axes (provenance + shape).
EXIT=0
```
The failure text now names all three rank-5 shapes, which is the fix showing up in the operator-facing output. Other fixtures unchanged: `fail-bad-enum-value.html` exit 1, `issue18-shaped-all-key-art.html` exit 1, `issues/signal_weekly_2026-07-26.html` exit 1.

```
$ git diff --stat d907035 -- <WP-6's four files>
 .claude/skills/the-signal/references/compliance-checklist.md | 4 ++--
 .claude/skills/the-signal/references/component-contracts.md  | 2 +-
 .claude/skills/the-signal/references/image-source-types.json | 9 ++++++++-
 .claude/skills/the-signal/scripts/check-image-diversity.sh   | 5 +++--
 4 files changed, 14 insertions(+), 6 deletions(-)
```

## F6. Handoffs

1. **→ WP-9 (stale citation, one clause).** `SKILL.md:274` currently works *around* the bug: *"`key_art` and `product_shot` may never lead a band (`shows.never_lead_shapes` in the lookup file; the checklist prose puts `portrait` in the same rung, so do not lead on one either)."* The parenthetical is now obsolete — the lookup and the prose agree, and all three shapes are in the list. It should read: *"`key_art`, `product_shot` and `portrait` may never lead a band (`shows.never_lead_shapes`)."* Not edited: `SKILL.md` is WP-9's. `SKILL.md:311` quotes the rank-5 prose correctly and needs no change.
2. **→ WP-4 (scope, needs a conscious choice).** `never_lead_shapes` is doctrine-derived and **broader** than SPEC §3.8's mechanical minimum, which names only `key_art` and only in Pixel & Byte. Implementing the whole list is the intent and is now recorded in the file; implementing only §3.8's letter is defensible; silently implementing something in between is the outcome to avoid. Flagged inside the JSON as well as here.
3. Unchanged from the main report: the **blocking** `validate-research-bundle.py` `KeyError` handoff to WP-5 (§7.1).

---

# WP-6 follow-up 2 (2026-07-26) — `data-table-kind` gains a sixth value

**Raised by:** WP-3b (complete), via the coordinator. **Baseline for diffs:** commit `d10d34c`. **Files touched:** `component-contracts.md` only (one of WP-6's four). `weekly.json`, the CSS and `validate-issue.py` were read as sources of truth, not edited.

## G1. The stale line

`component-contracts.md:230` read *"**Mandatory; no sixth value.**"* There now is one. SPEC §3.11 added **`finance`** because the original five (`league`, `medal`, `gc`, `leaderboard`, `championship`) were **all sport**, while The Desk already used `.mx-scorecard` for a financial card — the mx golden's *"The Rate War · As of 19 Jul"*. The enum could not describe an existing, legitimate use of the component it governed.

Worth stating plainly, because it is the same category error twice: a *polymorphic* table whose vocabulary admits only sport reproduces, one level down, the single-shape mistake polymorphism was introduced to fix.

## G2. The contract, updated

`data-table-kind` ∈ `league` · `medal` · `gc` · `leaderboard` · `championship` · **`finance`** — six values. The absolute is reworded rather than deleted: *"Mandatory, and the list is closed at these six — but treat 'closed' as of this document's date, not as a law: the enum grew from five to six precisely because a closed list outlived its scope."*

The `finance` entry documents the design intent WP-3b implemented, since this file is what writers copy from — with the golden's Rate War card as the worked markup:
- **Label · figure. No `.mx-scorecard__pos` column** (nothing in the card is in first place) **and no podium rule-off** (the `championship` kind's rule under the top three is meaningless here).
- Label column **wraps**; the figure column is **atomic and mixed-unit** (`3.75%`, `×4`, `−0.16pp`, `30 JUL`), shrink-wrapped so a value never splits.
- `tr.is-lead` is **the reference figure the others are read against**, rendered in **signal blue, not vermilion** — vermilion belongs to what leads or wins, the same doctrine as `data-role="demoted-lead"`. Carrying sport's visual grammar into a rate card would be the sport-only enum's error again, one level down.
- Title convention `<thing> · As of <DD MON>` — a rate card without an as-of date is undated data pretending to be current.
- Lives in **The Desk** (`.deskcol__card` inside a `[data-desk-column]`), not the Touchline.

## G3. How `finance`'s availability is worded — the judgement call

I took the option of **wording it as not-yet-usable**, in a blockquote directly under the contract:

> **`finance` is not stampable yet — declared and styled, not yet legal (as of 2026-07-26).** `validate-issue.py` hardcodes the original five (`TABLE_KINDS` at ~line 1764) and hard-fails any value outside them, so stamping `data-table-kind="finance"` on a real card today fails gate 2, while leaving it off only WARNs. That is why the golden's Rate War card still carries a bare `.mx-scorecard`. **Until WP-4 extends `TABLE_KINDS`, write the finance card without `data-table-kind` and accept the warning.**

Reasoning: this file is copied from, so a contract that reads as available would hand a writer a gate-2 failure. Verified against source, not assumed — `validate-issue.py:1764` is `TABLE_KINDS = ("league", "medal", "gc", "leaderboard", "championship")` and `check_table_kind` fails on an unlisted value while only warning on a missing one; the golden's Desk card at `references/golden/weekly-mx/chapters/the_desk.html:18` is indeed a bare `.mx-scorecard`. The note also says the CSS and `weekly.json` already carry the sixth kind, so the stamp becomes correct the moment the validator does and nothing else needs to change.

## G4. Sweep for the same class of stale absolute

Every count, closed list and "no other value" claim in `component-contracts.md`, checked against the current source of truth rather than against memory:

| Claim in the file | Source of truth | Verdict |
|---|---|---|
| `data-table-kind` — "no sixth value" | SPEC §3.11, `weekly.json`, CSS | **STALE — fixed above.** |
| Caught Up — "HARD cap 8 `<li>`" | `weekly.json` → `invariants.caught_up_cap` ("at most 8 `<li>`") | Current ✓ |
| The Desk — "1–2 `.deskcol` total, never 3+" | `invariants.desk_is_one_nested_department` ("fail on 0 or 3+ columns") | Current ✓ |
| Long Read — "exactly one per issue" | `invariants.exactly_one_long_read` | Current ✓ |
| Long Read — "MUST carry ≥1 real image plate"; weekly floor 8 `<img>` | `invariants.long_read_has_image`, `image-floor` | Current ✓ |
| Results ledger — "≥2 distinct `data-sport`" | `invariants.results_ledger_multi_sport` | Current ✓ |
| `shows` / `data-shows` — 11 values, closed | `image-source-types.json` (canonical) | Current ✓ (reconciled in follow-up 1) |
| Season Review `.scorecard` — "`data-tier` accepts `hot \| warm \| cold`" | CSS: `body.is-special[data-special="season-review"] .scorecard[data-tier=…]` | Current ✓. **Near-miss worth recording:** the stylesheet also defines `data-tier` = `top`/`strong`/`wildcard`/`wait`/`skip`, but those belong to *other* components (Shortlist verdict pills, Next tier rows), not `.scorecard`. Checked the selectors rather than grepping the value list — the value-list grep alone would have produced a false positive. |
| `.mx-ledger` `data-role` — results-ledger / demoted-lead | grep of `weekly.json` + stitcher + CSS returns exactly those two; `validate-issue.py` also knows `long-read`, `desk`, `release-radar` (all documented elsewhere in this file) | Current ✓ — the file makes no closed-list claim about `data-role`, which is why it did not go stale. |
| Colophon "exactly 4 `.cell`", Week in Numbers "4–6 `.fig-row`" | Not mechanically enforced anywhere; editorial shape only | Current ✓ (nothing to drift from) |

**One gap of the same class found and fixed** (an omission rather than a wrong absolute): the Long Read contract showed `.lr-title` as pure writer markup and said nothing about the vintage stamp. `stitch_weekly.py` **stamps `.lr-vintage` into the writer's `.lr-title`** when the plan says `evergreen`, **and strips the issue date out of the writer's `.byline`** (idempotently — it removes any existing `.lr-vintage` first). A writer copying this contract could have hand-written a vintage line, or fought the stitcher over the byline. Added as a blockquote note: vintage is a *plan* decision, not a writing decision.

## G5. Verification

```
$ grep -n "no sixth value" …/component-contracts.md
  stale claim removed ✓
$ grep -n 'data-table-kind` ∈' …/component-contracts.md
232: … `league` · `medal` · `gc` · `leaderboard` · `championship` · `finance` (SPEC §3.4, extended by the §3.11 amendment) …
$ grep -c '^```' …/component-contracts.md
80        (even — code fences balanced)

$ git diff --stat d10d34c -- <WP-6's four files>
 .../the-signal/references/component-contracts.md   | 26 +++++++++++++++++++++-
 1 file changed, 25 insertions(+), 1 deletion(-)
$ git diff --name-only d10d34c
 .claude/skills/the-signal/references/component-contracts.md      (only file changed since the baseline)
```

Unchanged-file regression check (the other three files were not touched this round, confirmed above):
```
$ python3 -c "import json; json.load(open('…/image-source-types.json'))"   → json OK
$ bash -n …/check-image-diversity.sh                                       → bash -n OK
$ …/check-image-diversity.sh …/fail-min-distinct-shapes.html               → exit 1
$ …/check-image-diversity.sh …/pass-min-distinct-shapes.html               → exit 0
```

## G6. Handoffs

1. **→ WP-4 (already routed, restated with the exact site).** `validate-issue.py:1764` `TABLE_KINDS` needs `"finance"` appended, and the failure message at ~2197 says *"outside the five legal shapes"* — that count needs to move to six too, or the message will misreport the rule it enforces. Until then `finance` is styled and declared but not stampable, and `component-contracts.md` says so explicitly (§G3).
2. Carried forward from follow-up 1: `SKILL.md:274`'s obsolete `never_lead_shapes` parenthetical (→ WP-9), and the blocking `validate-research-bundle.py` `KeyError` (→ WP-5, §7.1).
