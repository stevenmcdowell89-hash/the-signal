# Data contracts — the machine records that cross phase boundaries

**Owner:** WP-1 of `docs/editorial-coverage-rebuild-SPEC-2026-07-26.md` (the SPEC).
**Status:** normative for field names, enum values and semantics. Where this file and the SPEC
disagree, the SPEC wins and this file is a bug — report it, do not improvise a third version.

The pipeline hands work between phases as **files**, not conversation: the researcher writes
`research-bundle.json`, the planner writes `chapter-plan.json`, the stitcher writes the issue HTML,
and `state/signal-state.json` carries continuity between issues. Every field below crosses one of
those boundaries, so more than one work package touches it. This file is the single place that says
what each field means, who writes it, and who reads it.

Where each contract is documented in full:

| Record | Canonical documentation | Enforced by |
|---|---|---|
| `chapter-plan.json` | `references/chapter-plan-schema.md` | `scripts/validate-chapter-plan.py` (WP-5) |
| `research-bundle.json` additions | **this file**, § Research bundle | `scripts/validate-research-bundle.py` (WP-5) |
| the `shows` enum | **this file**, § The `shows` enum — canonicalised in `references/image-source-types.json` (WP-6) | `validate-research-bundle.py` (WP-5), `validate-issue.py` (WP-4), `check-image-diversity.sh` (WP-6) |
| `state/signal-state.json` additions | **this file**, § State | written/read by `SKILL.md` phase wiring (WP-9); read by WP-4/WP-5 validators |
| rendered HTML attributes | SPEC §3.4 — emitted by `scripts/stitch_weekly.py` (WP-3) | `scripts/validate-issue.py` (WP-4) |
| `assets/cached/manifest.json` | SPEC §3.10 — written by `scripts/mirror-images.py` (WP-8) | `scripts/extract-covers.py` (WP-8) |

---

## Research bundle

Produced by the **researcher** (Phase 3a) and the **orchestrator's** re-verification pass
(Phase 3a-verify). Consumed by `validate-research-bundle.py` (WP-5), then by the **planner**
(which routes candidates into each chapter's `images_needed`) and the **writers**.

### `image_candidates[]` — three additions (SPEC §3.2)

```jsonc
"image_candidates": [{
  // ── existing fields, unchanged ──
  "url_or_keyword": "https://upload.wikimedia.org/…/NAMA_Machine_d'Anticythère_1.jpg",
  "verified": { "head_status": 200, "content_type": "image/jpeg", "verified_at": "2026-07-26T01:44:00Z" },
  "source_type": "wikimedia",        // domain-derived, from image-source-types.json
  "context": "Long Read — front dial",
  "direct_cdn": true,                // only when the URL has no image extension

  // ── WP-1 additions ──
  "shows": "artefact",               // REQUIRED, enum below (§ The `shows` enum)
  "capture_year": 2007,              // REQUIRED integer; null ONLY when
                                     //   shows ∈ {diagram, chart} AND the asset is synthetic
  "licence": {                       // REQUIRED object — the machine record that replaces
                                     //   free-text credit as the thing checks can read
    "holder": "Mogi Vicentini",      // REQUIRED — person/institution to credit
    "code": "CC-BY-2.5",             // REQUIRED — SPDX-ish token, or one of
                                     //   "PRESS-KIT-EDITORIAL" | "PUBLIC-DOMAIN" | "CC0" | "UNKNOWN"
    "url": "https://creativecommons.org/licenses/by/2.5/",   // REQUIRED — the licence deed
    "allows_derivatives": true       // REQUIRED boolean — false for ANY ND licence
  }
}]
```

**Why each exists.**

- `shows` — the taxonomy classified images by *source domain* only, so "a press kit supplied it" was
  treated as an answer to "what is in the picture" (defect E). It is not: a press kit can supply
  `key_art` or `gameplay`. `shows` is **orthogonal** to `source_type`; both are required.
- `capture_year` — an image has a vintage and the prose around it makes dated claims. Without a
  capture year nothing can compare the two, which is how a 2007 reconstruction photograph came to
  illustrate a 2021 breakthrough (defect B). The caption-vintage rule (SPEC §3.9, WP-4) is a pure
  function of this field plus the band's prose, so it must be present and honest. Guidance: use the
  year the *photograph/render was made*, not the year of the thing depicted (a 2019 photo of a
  1901 artefact is `2019`); for a scan of a historical document use the document's year.
- `licence` — the credit line is prose, so `extract-covers.py` could not know that issue #18's cover
  source was CC BY-**ND** before smart-cropping it (SPEC §3.10, a live violation). `allows_derivatives`
  is the field that makes a derivative-safety check possible. `UNKNOWN` is legal in the bundle and is
  a signal to the planner not to build on it; it is **not** a licence to crop.

**Rendered downstream as** `data-shows`, `data-capture-year`, `data-licence`,
`data-allows-derivatives` on every `.plate-img` (SPEC §3.4 — WP-3 emits, WP-4 checks), and persisted
per asset hash in `assets/cached/manifest.json` (SPEC §3.10 — WP-8).

> **SPEC deviation, recorded (WP-1).** SPEC §3.2's comment lists the existing fields as
> "`url`, `verified`, `source_constraint`, `role`". The keys actually present in the bundle — the
> ones `validate-research-bundle.py` reads today — are **`url_or_keyword`**, `verified`,
> `source_type`, `context` (+ optional `direct_cdn`). `role` and `source_constraint` are fields of
> the *chapter plan's* `images_needed[]`, not of the bundle. The three **new** field names in §3.2
> are unaffected; only the parenthetical is wrong. WP-5 and WP-8 must key off `url_or_keyword`.

### `facts[]` — one addition (SPEC §3.2)

```jsonc
"facts": [{
  // ── existing fields, unchanged: claim, status ("happened"|"upcoming"), date, source_url,
  //    plus type ("fact"|"opinion") and, when type=="opinion", speaker + quote ──
  "resolves_loop": "loop_2026-07-19_wc-final"   // OPTIONAL — set when this fact closes an open loop
}]
```

`resolves_loop` is the missing carry-forward. `status: "upcoming"` facts were gate-checked and then
abandoned, so a Sunday-concluding event ("World Cup final today, 15:00 ET") was reported as pending
and never resolved (defect D). The value MUST equal an `id` in state's `open_loops[]`.

**Consumed by:** `validate-research-bundle.py --run-date <today> --state state/signal-state.json`
(WP-5) — a **matured** loop (`status == "open"` and `expected_resolution_date <= run_date`) with no
matching `resolves_loop` fails the bundle gate (SPEC §3.7). Then by the writer, which renders
`data-resolves-loop="<id>"` on the element carrying the result (SPEC §3.4), which `validate-issue.py`
(WP-4) checks independently — both layers, because a bundle can carry a fact the writer drops.

---

## The `shows` enum — what an image depicts

**Canonical home: `references/image-source-types.json` (WP-6 owns that file and canonicalises the
enum there).** This section documents it so WP-4, WP-5 and WP-8 do not have to guess; if the two ever
diverge, `image-source-types.json` is the machine-readable source of truth for consumers and the
divergence is a bug to report.

The eleven values, exactly (SPEC §3.3):

`event_photo` · `gameplay` · `in_engine` · `key_art` · `product_shot` · `portrait` · `diagram` ·
`map` · `chart` · `artefact` · `document`

Definitions that the checks depend on:

| Value | Means | Why a check cares |
|---|---|---|
| `event_photo` | A photograph of the actual thing happening | Touchline: any figure captioned as a concluded result MUST be `event_photo` (SPEC §3.8) |
| `gameplay` | The player's view, **in-game HUD present** | Top of the specificity hierarchy for games (SPEC §3.13) |
| `in_engine` | Cutscene or engine render, **no HUD** — better than key art, not gameplay | Ranks 4th in the hierarchy |
| `key_art` | Marketing art, usually with the logo composited in | Pixel & Byte: **at most one** per band, and **never** the band's lead figure (`.plate-img.lead`) |
| `product_shot` | A posed shot of hardware/an object against a set or seamless background | Last resort, alongside `key_art` |
| `portrait` | A posed photograph of a person | Last resort; a candid at an event is `event_photo`, not `portrait` |
| `diagram` | An explanatory drawing carrying information the prose cannot | Satisfies the Long Read's information-figure requirement; may have `capture_year: null` if synthetic |
| `map` | A geographic figure | Satisfies the Long Read requirement |
| `chart` | A data figure | Satisfies the Long Read requirement; may have `capture_year: null` if synthetic |
| `artefact` | The physical object itself (museum/archive) | Satisfies the Long Read requirement |
| `document` | A page, screen, listing or record (e.g. a store listing) | Counts as a distinct shape; the primary-document rung of the hierarchy |

Cross-issue budgets that read this field (SPEC §3.8, WP-4): **≥3 distinct** `data-shows` values per
issue; the Long Read carries **≥1** of {`diagram`, `map`, `chart`, `artefact`}; `min_distinct_shapes: 3`
replaces the retired `wikimedia_max_pct` / `wikimedia_max_count` thresholds (SPEC §3.14, WP-6).

---

## Chapter plan

Documented in full in `references/chapter-plan-schema.md` (WP-1 owns it; WP-5's
`validate-chapter-plan.py` enforces it). WP-1 added, per SPEC §3.1:

| Field | Where | Required |
|---|---|---|
| `issue_meta.research_cut_at` | issue meta | weekly |
| `issue_meta.window` `{from, to}` | issue meta | weekly |
| `issue_meta.cover_leads_on` — `"news"` \| `"long_read"` | issue meta | weekly |
| `issue_meta.lead_rationale` — ≥120 chars | issue meta | weekly |
| `issue_meta.lead_override_reason` — ≥80 chars | issue meta | only when the rut rule (SPEC §3.6) trips |
| `vintage` — `"news"` \| `"evergreen"` | the `long_read` chapter | weekly |
| `material_span` — `YYYY–YYYY`, en-dash | the `long_read` chapter | when `vintage == "evergreen"` |
| `latest_development` — `YYYY-MM` | the `long_read` chapter | when `vintage == "evergreen"` |
| `rows[].key` + `rows[].source_band` | the `week_in_numbers` chapter | weekly |

`research_cut_at` is **copied from state** (below) — the planner does not invent it, and
`window.to` must equal it while `window.from` is the previous issue's cut.

> **WP-1 clarification (reported, not improvised).** SPEC §3.1 gives `source_band: "touchline"` — a
> band id — but The Week in Numbers is defined in `chapter-plan-schema.md` (v8.36) as the *personal*
> stat strip rendering from state, so a band-only vocabulary cannot express its personal rows. The
> value set is therefore: **the `chapter_id` of a chapter present in this plan, or the literal
> `"state"`**. WP-5 must accept `"state"`.

---

## State — `state/signal-state.json`

**WP-1 owns the file. WP-9 wires the reads and writes into `SKILL.md`'s phases.** Validators read it
but never write it. Every key below is additive — no pre-existing key changed.

### `research_cut_at`

```jsonc
"research_cut_at": "2026-07-26T02:10:00Z"
```

ISO8601 UTC instant. **Written at publish** (WP-9, end of pipeline) as the moment research for the
issue just shipped stopped; **read at Phase 0/3a** of the *next* issue as the opening bound of its
coverage window. The whole point: the coverage window is bounded by instants, not by calendar days,
so "Sunday's final was inside the week" stops being an excuse for treating an unknowable result as
covered. Copied into the plan as `issue_meta.window.from` (previous value) and
`issue_meta.research_cut_at` / `window.to` (this run's value).

### `open_loops[]`

```jsonc
"open_loops": [{
  "id": "loop_2026-07-19_wc-final",           // convention: loop_<expected_resolution_date>_<slug>
  "claim": "World Cup final, Spain v Argentina, MetLife",
  "expected_resolution_date": "2026-07-19",   // YYYY-MM-DD
  "band": "touchline",                        // chapter_id of the band that owes the resolution
  "issue_opened": 17,                         // weekly issue number
  "status": "open",                           // "open" | "resolved" | "dropped"
  "resolution": null                          // null while open; free text + source_url when resolved
}]
```

- **Written** at publish (WP-9) for every `status: "upcoming"` fact whose event concludes after the
  research cut, and updated to `resolved`/`dropped` the following week.
- **Read** by `validate-research-bundle.py` (WP-5) via `--state`, and by `validate-issue.py` (WP-4),
  both applying the maturity rule of SPEC §3.7. A loop is **matured** when `status == "open"` and
  `expected_resolution_date <= run_date`.
- `id` is the join key with `facts[].resolves_loop` and with `data-resolves-loop` in the HTML. Keep it
  stable once written — it is a foreign key, not a label.
- `dropped` is an honest terminal state for a loop that was never reported. It exists so the ledger
  records the miss instead of quietly deleting it; a dropped loop no longer matures.

### `cover_lead_ledger[]`

```jsonc
"cover_lead_ledger": [{                       // last 12 entries, NEWEST FIRST
  "issue": 18, "date": "2026-07-26",
  "topic_family": "uk_politics",              // closed enumeration — see below
  "one_line": "Burnham's first ordinary week",
  "led_on": "news"                            // "news" | "long_read" — from issue_meta.cover_leads_on
}]
```

- **Written** at publish (WP-9): prepend one entry per **standard weekly** (specials do not lead a
  weekly cover and are not numbered), then truncate to 12.
- **Read** by `validate-chapter-plan.py` (WP-5) for the rut rule (SPEC §3.6): fail when the same
  `topic_family` appears as `led_on: "news"` in **≥3 of the last 4** entries **and** the plan sets
  `cover_leads_on: "news"` on that same family **and** `lead_override_reason` is absent or <80 chars.
  Also read by the planner in Phase 4 — seeing nine weeks of lead history is the fix for defect C,
  where `last_cover_lead` (one week) was all the planner could see.
- `topic_family` **vocabulary comes from `references/chapter-plan-schema.md` § Topic Family
  Enumeration** — the same closed list that governs `pieces[*].topic_family`. There is one
  topic-family vocabulary in the system; do not create a parallel set for state.
- `cover_lead_ledger` supersedes nothing: `last_cover_lead` (prose) and `ongoing_stories[].lead_history`
  stay as they are. Note that `lead_history` is a *story-thread* record and is **not** interchangeable
  with this ledger — see § Seed provenance.

### `sports_calendar[]`

```jsonc
"sports_calendar": [{
  "event": "The Open Championship", "sport": "golf",
  "start": "2026-07-16", "end": "2026-07-19",
  "importance": 1,                             // 1 = must appear, 2 = should, 3 = if room
  "reader_relevant": true,                     // per interest_depth, below
  "needs_verification": true                   // Phase 0 confirms dates against a source before use
}]
```

- **Read** at Phase 0 (WP-9) so the planner knows an event is coming *before* the research bundle
  happens to mention it; and by the Touchline planning that WP-2/WP-3 restructure. Defect D was in
  part that no sporting calendar existed at all, so a Sunday-concluding major simply was not on
  anyone's list.
- `sport` values used in the seed: `football`, `golf`, `multi_sport`. Keep them aligned with the
  `data-sport` values the results ledger renders (SPEC §3.4/§3.11) and with `interest_depth` keys.
- **`needs_verification: true` on every seeded entry, without exception.** The seed is a prompt to
  check, never a fact of record: Phase 0 must confirm dates against a source before the planner
  relies on an entry. Nothing here asserts a venue, a fixture or a result, by design (SPEC §3.12).
- Maintenance: entries whose `end` has passed may be pruned at publish; do not rewrite an entry's
  dates from memory — re-verify or delete it.

### `used_image_urls`

```jsonc
"used_image_urls": { "<sha256(url)[:12]>": { "issues": [17, 18], "led": [17, 18] } }
```

- Keyed by the **first 12 hex chars of sha256 of the source URL** — the same hash
  `mirror-images.py` already uses for cached filenames, so the key joins state ↔
  `assets/cached/manifest.json` ↔ the mirrored file.
- `issues` = every issue number the asset appeared in; `led` = the issues where it was a band's **lead**
  figure (`.plate-img.lead`).
- **Populated by WP-8** (`mirror-images.py`, which now also writes the manifest with url + licence per
  hash — SPEC §3.10). **Read by WP-4** for the cross-issue budget: a `src` that `led` the previous
  issue may not lead this one (SPEC §3.8). Seeded **empty (`{}`)** — nothing can be back-filled
  honestly, because `mirror-images.py` discarded the URLs of everything already published
  (verified: ~400 Commons candidates reverse-hashed, no match), so the first populated entries arrive
  with issue #19.

### `interest_depth`

```jsonc
"interest_depth": { "motorsport": "results_only", "football": "full", "golf": "majors_only" }
```

Value set (SPEC §3.5): `full` · `majors_only` · `results_only` · `off`.

| Value | Means |
|---|---|
| `full` | Ongoing narrative coverage: fixtures, form, standings, transfer/organisational news |
| `majors_only` | Only the sport's set-piece events (a major championship, a final, a cup); routine tour weeks are out |
| `results_only` | Concluded results of the big events, in the results ledger; session-by-session and paddock process are out |
| `off` | Not covered |

- **Read** by the researcher/planner (WP-9 wiring) and by `functions/daily/profile.js` feed weighting
  (WP-7: motorsport weighted **low**, consistent with `results_only`; existing football/golf weights
  unchanged).
- Keys are **sports**, matching `sports_calendar[].sport` and the rendered `data-sport` values.
- **A key that is absent is not a policy.** Only the three sports the owner has weighted are seeded.
  A sport with no key should be treated as unset — cover it on news value, and add a key when the
  owner states a depth. Do not silently read an absent key as `off`; that would re-create the
  invisible-sport problem (defect D) in a new place.

---

## Seed provenance — what the seeded values are grounded in

Recorded because a seed that looks like a fact of record but was guessed is worse than an empty field.

- **`research_cut_at: "2026-07-26T02:10:00Z"`** — the literal from SPEC §3.5. It is consistent with,
  but not derivable from, the repo: `state/quality-log.jsonl`'s issue-#18 entry is timestamped
  `2026-07-26T02:51:16Z` (gate 3, i.e. after writing), which bounds the research cut from above.
  WP-9 overwrites this at the next publish with a measured value.
- **`cover_lead_ledger`** — seeded with the **10 most recent standard weeklies, #18 → #9**, newest
  first. Issue numbers and dates are from `archive-manifest.json`; each `topic_family` and `one_line`
  is read off that issue's rendered cover in `issues/`. `led_on` is `long_read` only for #17 and #16,
  where the cover's lead transmission *is* the issue's Long Read (the single-Long-Read spine only
  exists from #16 / v8.37; before that a weekly had rotating anchors, so `news` is the accurate value).
  Two consequences worth knowing:
  - `ongoing_stories[]`'s Burnham `lead_history` (`2026-05-24`, `2026-05-31`, `2026-06-21`,
    `2026-07-12`, `2026-07-19`) is **not** a cover-lead record and does not reconcile with the covers:
    `2026-05-31` matches no weekly (the nearest, #11 / `2026-06-01`, led on the DR Congo Ebola PHEIC),
    and `2026-07-12` maps to #16 / `2026-07-13`, whose cover led on the Telstar 1 Long Read. The
    ledger follows the **rendered covers**, which is what the rut rule is about.
  - Issue #8 (`2026-05-10`) is deliberately **not** in the ledger: its cover led on the
    Instructure/Canvas breach, and the closed topic-family enumeration has no family for a
    cybersecurity/data-breach story. Rather than mis-file it, the ledger starts at #9. The gap is a
    real finding about the enumeration, not an omission.
- **`open_loops`** — the two losses the SPEC's diagnosis names, both from issue #17 (`2026-07-19`),
  both `status: "dropped"`. Grounding: #17 carries the World Cup final as an explicit upcoming fact
  ("Spain v Argentina at MetLife Stadium, 15:00 ET today"), and issue #18 contains no report of the
  result; The Open's final round is absent from #17 *and* #18 entirely — #17 has no golf coverage at
  all. `resolution` records that honestly, including the fact that the 2026-07-20 Season Review
  special covered the tournament outside the weekly of record. #18 is frozen (SPEC §1.3), so these
  are recorded, not repaired.
- **`sports_calendar`** — four entries, all `needs_verification: true`, no venues, no fixtures, no
  results. The Open Championship (16–19 July 2026) and the Glasgow 2026 Commonwealth Games
  (23 July – 2 August 2026) are the two events the SPEC's diagnosis rests on; the Premier League
  (21 Aug) and Serie A (23 Aug) 2026-27 openings are grounded in state's own
  `recent_next_week_themes`. Known gaps Phase 0 should add **once dates are confirmed from a source**:
  the UEFA Champions League 2026-27 league phase (September), the remaining F1 rounds after the
  August break, and any autumn athletics/cricket set-pieces WP-7's new feeds surface. Deliberately
  absent: the Ryder Cup (biennial — 2027, not 2026) and the men's golf majors (all four concluded
  before the research cut, The Open last), so golf legitimately yields until 2027.
- **`interest_depth`** — the three sports the owner weighted (motorsport `results_only`, football
  `full`, golf `majors_only`). Football and golf are the only sports in the reader profile's interest
  list (`references/spec/global.md` § The Reader: "Juventus and Serie A, Premier League and Champions
  League, golf (majors/Ryder Cup)"); motorsport is not in that list, which is exactly why its depth
  needs stating rather than inferring. No other sport is seeded — see the absent-key rule above.
