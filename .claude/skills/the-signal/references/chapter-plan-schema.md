# Chapter Plan Schema (v8.27)

> **WP-6 (2026-07) — NEW-SYSTEM (data-mx) SPECIAL plans.** A special plan opts
> into the unified design system with `issue_meta.design_system: "mx"`. Its
> structure is then **skeleton-driven**: `references/format-skeletons/<format>.json`
> (season-review · deep-dive · versus · rewind) is the single source of truth,
> and `scripts/stitch_specials.py` assembles all chrome from it (writers fill
> interiors only). On top of everything below, an mx plan carries:
> `issue_meta.kit` (from the skeleton's allowed set), `issue_meta.acts`
> (1–3 acts: `{name, title, hand?, grounds[], tokens?, transit_card?}`),
> `issue_meta.event` (season_review/countdown) or `issue_meta.period` (rewind)
> for the Part-7 §2 timing sanity gate, plan-level `personalisation`
> (`{chapter_id, description, state_evidence[]}` — evidence strings must appear
> verbatim in `state/signal-state.json`), and per-chapter `skeleton_slot`,
> `act`, and `visual_events` (`{law2-event-type: count}` from the closed
> vocabulary figure/ephemera/ledger/statband/quote/plate/chart/marquee/cheatsheet).
> `validate-chapter-plan.py` enforces: Law-3 word floors per format, a
> planned-density reachability check (documented in each skeleton's
> `law2.planned_density_note`), planned distribution (no dead chapters/runs),
> killer features per Part 7 §3 (rule vocabulary in each skeleton's
> `killer_features`), the personalisation floor, and editorial-timing sanity.
> Legacy special plans (no `design_system` field) are governed by this document
> unchanged.
>
> **WP-8/8.1 (v8.43) — WEEKLY plans default to `design_system: "mx"`.** The core
> furniture layer is now ON BY DEFAULT for every weekly (not just specials). A
> weekly plan sets `issue_meta.design_system: "mx"` and allocates the furniture
> objects to bands per `references/format-skeletons/weekly.json` §
> `furniture_layer.band_slots`; writers fill their interiors with `data-mx-event`
> markers. The weekly keeps its Transmission identity (skin-transmission alias, no
> acts/kit/pack — those are special-only). Omit `design_system` only for a
> deliberate legacy back-compat weekly (the `references/golden/weekly/` fixture);
> new issues are `mx`.

The planner subagent writes `/tmp/signal-build/chapter-plan.json`. This file defines the contract between the planner and the writer subagents. Every field here is required unless marked optional.

The validator at `scripts/validate-chapter-plan.py` enforces this schema. A plan that fails validation cannot proceed to Phase 5 (writer subagents).

**2026-07-13 (quality handoff A5/A6) — the weekly word budget is allocated, and bundle images are routed.** A weekly plan's chapters (band selections) each carry a `target_word_count` that is the band's **allocated share** of the issue word budget, drawn from the band's `target_words` range in `references/format-skeletons/weekly.json`; the shares **MUST sum to >= 6,000** (aim 6,800–7,500 — mid-band, per B8) and `issue_meta.word_budget` declares the arithmetic. The planner also **routes** the research bundle's verified `image_candidates` into per-band `images_needed`: the `long_read` MUST carry >= 1 entry (`alt_required: true`), and every feature/round band allocated > 350 words should carry >= 1. `validate-chapter-plan.py` hard-fails a weekly plan whose allocations sum under 6,000 or whose long_read has empty `images_needed`, and warns on a > 350-word round band with none.

**v8.30 — Release Radar is a required, enforced weekly chapter.** Every `weekly` plan MUST include a `release_radar` chapter (rendered immediately after `screen_sound`) carrying a `radar_items` array of **15-20 upcoming-weighted media releases across ≥4 categories** (film/tv/game/lego/tech/book/music). The validator hard-fails a weekly plan that omits it or that ships a thin one. This closes the silent-drop gap that lost release coverage from the 1 June test issue — Release Radar was "tail content" with no schema field and no gate. (On the Radar stays events-only; Release Radar owns product/media releases.)

**v8.34 — considered piece is the backbone (INVERTS the v8.27-v8.28 spine).** A fixed-section chapter must carry a **considered piece** — a `role: "lead"` piece that is a synthesis, a roundup with a named layer, an angle, or a feature — **or** an explicit `yield_reason` string. The `catch_up` roundup is now **optional grounding context**, not a mandatory element: a section with only `catch_up` (no `lead`, no `yield_reason`) **FAILS** — it must yield, because exhaustive recap is the daily brief's job, not the weekly's. A bare Lead with no Catch-Up is fine (the considered piece stands alone). `pieces` holds **0-2 entries** (the considered piece as `lead`, plus an optional `companion`; a companion requires a lead). Word floors stay relaxed *sanity* minimums (lead 150, companion 120) — not targets; length follows the material. Facts in any piece/catch_up item must trace to a researched source (carried as `link_targets`). The clauses below from v8.28/v8.27 — "a section may be pure Catch-Up with no pieces" and "the mandatory second element is the substantive catch_up" — are **superseded by this block**.

**v8.28 (superseded by v8.34) — Lead optional + length follows material.** The Lead is no longer required: a fixed-section chapter may carry **0-2 pieces** (an optional `lead` + an optional `companion`; a companion requires a lead). A section may be pure Catch-Up (facts) with no `pieces` at all. Word floors are relaxed to small *sanity* minimums (lead 150, companion 120) — not targets; length follows the material. The section must still contain *something* substantive (a non-empty `catch_up`, a Lead, or a `yield_reason`), and a bare Lead with no second element still fails. Facts in any piece/catch_up item must trace to a researched source (carried as `link_targets`).

**v8.27 — Lead + Catch-Up (replaces the v8.15 mandatory two-anchor Lead + Companion).** Every fixed-section chapter (`world`, `pixel_byte`, `toolkit`, `touchline`, `screen_sound`, `session`) carries a `pieces` array (v8.28: 0-2 entries): an optional `role: "lead"` and an optional `role: "companion"` (if present, on a `topic_family` distinct from the Lead). The mandatory *second* element is the **substantive `catch_up` roundup** (or, where a section genuinely runs short, an explicit `yield_reason` string). Each `catch_up` item must carry `headline_hint`, `why_it_matters`, and a non-empty `link_targets` (the "no bare namedrops" rule — and the item must carry a real specific fact, not a beat-label). The `long_shelf` chapter still carries an `items` array of 6–8 entries with at least two `wildcard: true`. Topic families are a closed enumeration — see § Topic Family Enumeration at the bottom of this file.

> **Note (v8.27):** `toolkit` is now a fixed-but-yields section; when it does not appear in an issue it is simply omitted from `chapters`. The Saga is trigger-driven and is never a rotating cadence chapter.

> **Note (v8.36 — Weekly W-2, The Desk + The Threads + The Week in Numbers).**
> - **Rebranded rotating chapter_ids:** the money column is now `ledger` (was `money`/`the_money`) and the travel column is `itinerary` (was `places`/`the_places`). The change is reader-facing; the state-file continuity keys stay `the_money.last_appeared` / `the_places.last_appeared`.
> - **The Desk** is a service *department* grouping 1–2 running service columns — `session`, `ledger`, `itinerary`, `toolkit`. `session` and `toolkit` keep the fixed-section `pieces` shape above; `ledger` and `itinerary` remain plain rotating chapters. **Every Desk column that runs closes on a `.do-this-week` pin** — one concrete do-it-this-week action (rendered, not a plan field).
> - **New plain chapters** (no `pieces` shape, not shape-validated): `threads` (The Threads — the continuity engine off `ongoing_stories` + `training_phase` + `upcoming_trips`) and `week_in_numbers` (The Week in Numbers — the personal stat strip). Both render from state; neither is enforced by `validate-chapter-plan.py`.
> - **Retired (v8.36):** the hard-cadence-floor and deficit-promotion validators are gone — domain cadence is now an editorial checklist line, not a planner gate. There is no `deficit_override_reason` / `deficit_overrides` field any more.

**v8.17 additions:** optional `sub_format` field on the `screen_sound` and `history` chapters. Allowed values: `null` (default), `"directors_cut"` (screen_sound only), `"closer_look"` (history only). When `sub_format = "directors_cut"`, the Lead piece's word_count_target.min must be ≥ 550. When `sub_format = "closer_look"`, the history chapter must carry a single `featured_item` with word_count_target.min ≥ 600 and NO `items`/`also_items` array.

---

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "The Signal — Chapter Plan",
  "description": "Output of the Planner subagent. Consumed by writer subagents and stitch-issue.sh.",
  "type": "object",
  "required": ["issue_meta", "chapters", "assets", "compliance"],
  "properties": {

    "issue_meta": {
      "type": "object",
      "required": ["format", "date", "topic", "special_id", "execution_mode"],
      "properties": {
        "format": {
          "type": "string",
          "enum": [
            "weekly",
            "deep_dive",
            "countdown",
            "season_review",
            "versus",
            "rewind",
            "guide",
            "starter_kit",
            "shortlist",
            "next",
            "lookahead",
            "field_guide"
          ],
          "description": "Issue format — closed vocabulary. Use snake_case. 2026-07 WP-0 reconciliation: `guide` is the merged recommendation format (v8.39 S4; `shortlist`/`starter_kit` stay as archive back-compat slugs), `next` is live, `blueprint` is retired (v8.22) and no longer valid. `lookahead` is retired/folded (v8.39 S2) — its slug survives here for the two archived drafts only; do not plan new lookahead issues."
        },
        "date": {
          "type": "string",
          "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
          "description": "Issue date in YYYY-MM-DD format."
        },
        "topic": {
          "type": "string",
          "description": "Human-readable issue topic or headline. E.g. 'Efteling & Beekse Bergen' or 'Switch 2 Co-Op Games'."
        },
        "special_id": {
          "type": ["string", "null"],
          "description": "Unique slug for special editions, e.g. 'countdown-efteling-2026'. null for standard weekly."
        },
        "execution_mode": {
          "type": "string",
          "enum": ["parallel", "sequential"],
          "description": "How writer subagents are spawned. Derived from format — see mapping below. Must match the format."
        },
        "word_budget": {
          "type": "object",
          "description": "2026-07-13 handoff A5 — the issue-level word budget the planner is allocating against. For weeklies: target_total drawn from weekly.json word_budget (aim 6,800-7,500; hard floor 6,000; ceiling 9,000), and allocated_total = the sum of every chapter's target_word_count. Declaring it forces the planner to do the arithmetic that was previously skipped — the per-chapter shares are the decomposition of this number, never independent guesses.",
          "properties": {
            "target_total": { "type": "integer", "description": "The issue target the planner is aiming at (weekly: 6,800-7,500)." },
            "allocated_total": { "type": "integer", "description": "Sum of all chapters' target_word_count. Weekly: MUST be >= 6,000 (validator hard-fails below)." }
          }
        }
      }
    },

    "chapters": {
      "type": "array",
      "minItems": 1,
      "description": "Ordered list of chapters. chapter_num must be 1..N with no gaps.",
      "items": {
        "type": "object",
        "required": [
          "chapter_id",
          "chapter_num",
          "chapter_type",
          "chapter_title",
          "chapter_arc",
          "ground",
          "is_hype",
          "data_venue",
          "target_word_count",
          "images_needed",
          "key_facts",
          "forbidden_topics",
          "cross_refs"
        ],
        "properties": {

          "chapter_id": {
            "type": "string",
            "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
            "description": "Kebab-case slug, unique across all chapters. E.g. 'by-the-numbers', 'top-attractions', 'world-this-week'."
          },

          "chapter_num": {
            "type": "integer",
            "minimum": 1,
            "description": "1-indexed chapter number. Must form a contiguous sequence from 1 to N."
          },

          "chapter_type": {
            "type": "string",
            "enum": [
              "opener",
              "hype",
              "literary",
              "practical",
              "gallery",
              "interlude",
              "signature",
              "closer"
            ],
            "description": "Closed vocabulary. Informs CSS ground choices and writer behaviour. 'hype' chapters may use is-hype modifiers. 'literary' chapters must NOT."
          },

          "chapter_title": {
            "type": "string",
            "description": "Display title for the chapter gate and navigator. E.g. 'Five Moments Worth the Trip'."
          },

          "chapter_arc": {
            "type": "string",
            "description": "One-line dramatic arc — what the reader feels or understands by the end of this chapter. Shown in the chapter gate scg-deck. E.g. 'The rides worth your day'."
          },

          "ground": {
            "type": "string",
            "enum": ["paper", "ink", "gallery"],
            "description": "Chapter background. 'paper' = light cream. 'ink' = dark. 'gallery' = neutral slate (image-first chapters only). Alternate paper/ink across chapters — never two consecutive same ground."
          },

          "is_hype": {
            "type": "boolean",
            "description": "If true, writer may use .is-hype modifier on the chapter gate and section wrapper, and coral is permitted on sp-number, sp-kicker, etc. ONLY valid for Countdown and Field Guide formats — validator blocks is_hype:true on literary formats."
          },

          "data_venue": {
            "type": ["string", "null"],
            "description": "Venue slug for multi-venue Countdowns with 33-countdown-destinations.css active. E.g. 'efteling' or 'beekse-bergen'. null for single-venue or non-Countdown."
          },

          "target_word_count": {
            "type": "integer",
            "minimum": 100,
            "description": "The chapter's ALLOCATED SHARE of the issue word budget (2026-07-13 handoff A5) — not a soft suggestion. The planner MUST decompose the issue target into per-chapter shares; on a weekly, every planned content band's share is drawn from its `target_words` range in references/format-skeletons/weekly.json, and the shares MUST sum to >= 6,000 (aim 6,800-7,500, mid-band, so a light news week still clears 6,000). validate-chapter-plan.py hard-fails a weekly plan whose allocations sum below 6,000. The share is a commitment to attempt, not a hard cap: 'length follows the material' governs trimming a GIVEN share during writing — a writer landing far under its share flags the planner for more research; it does not ship short."
          },

          "dimensions_covered": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Deep Dive only (v8.22.14). For chapters that introduce a subject (a country, a person, an institution, a movement), the list of dimensions this chapter will cover. E.g. for a chapter on Germany in 1914: ['founding', 'constitutional', 'economic', 'military', 'naval', 'colonial', 'cultural_scientific', 'domestic_politics', 'foreign_policy']. The planner checks this list against the brief — if the brief asks for thorough coverage of a subject and the chapter declares fewer dimensions than a curious reader would expect, the planner adds them. Editorial discretion is allowed on depth-per-dimension (some get full paragraphs, some get a sentence) but no dimension may be silently omitted. Optional for non-introductory chapters (foreword, argument, keep-digging, conflict-walkthrough chapters that don't introduce new subjects)."
          },

          "images_needed": {
            "type": "array",
            "description": "Images the writer must place in this chapter (2026-07-13 handoff A6 — images are ROUTED by the planner, not left to writer initiative). REQUIRED NON-EMPTY, with at least one alt_required:true entry, for the weekly long_read and EVERY feature/round band (touchline, pixel_byte, screen_sound, bookmark, this_week_in_history, rotating slots); the planner draws each entry's role/source_constraint from the research bundle's image_candidates (verified URLs), so the writer renders a real <img> from the bundle rather than sourcing from scratch. validate-chapter-plan.py hard-fails a weekly whose long_read has an empty images_needed and warns on any round band allocated >350 words with none. May be empty only for structural/typographic bands (letter, figures, digest, threads, radar, closepin, colophon).",
            "items": {
              "type": "object",
              "required": ["role", "source_constraint", "alt_required"],
              "properties": {
                "role": {
                  "type": "string",
                  "description": "What the image shows / its editorial purpose. E.g. 'hero-establishing shot of Efteling entrance'."
                },
                "source_constraint": {
                  "type": "string",
                  "description": "Where to find it. E.g. 'Wikimedia Commons', 'official press kit', 'credited Flickr CC'. Never 'AI-generated'."
                },
                "alt_required": {
                  "type": "boolean",
                  "description": "If true, this image is essential — writer must source it or flag to planner. If false, writer may omit if nothing suitable found."
                }
              }
            }
          },

          "key_facts": {
            "type": "array",
            "items": {
              "oneOf": [
                { "type": "string" },
                {
                  "type": "object",
                  "required": ["claim", "status", "date", "source_url"],
                  "properties": {
                    "claim": { "type": "string" },
                    "status": { "type": "string", "enum": ["happened", "upcoming"] },
                    "date": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
                    "source_url": { "type": "string", "format": "uri" },
                    "type": { "type": "string", "enum": ["fact", "opinion"], "default": "fact" },
                    "speaker": { "type": "string", "description": "Required iff type=='opinion'." },
                    "quote": { "type": "string", "description": "Required iff type=='opinion' — the real words." }
                  }
                }
              ]
            },
            "description": "Specific facts from research-bundle.json the writer MUST include in this chapter. Verified facts only — the planner pulls these from the bundle's `facts` array. v8.29: each entry SHOULD be the structured fact record (copied from the bundle, carrying status/date/source_url so the writer renders the happened/upcoming tag rather than judging it mid-sentence; type=='opinion' carries speaker+quote). A bare string is still accepted for back-compat, but a fact whose timing or attribution is load-bearing must be the structured form. The validator hard-fails a structured record missing claim/status/date/source_url, a bad status/date, or an opinion missing speaker/quote."
          },

          "forbidden_topics": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Topics this chapter must NOT cover — anti-overlap with other chapters. E.g. 'do not cover accommodation — that is chapter 3'."
          },

          "cross_refs": {
            "type": "array",
            "items": { "type": "string" },
            "description": "chapter_ids this chapter may reference for narrative throughline. ONLY valid for sequential execution_mode (Deep Dive, Versus, Rewind, Season Review). Must be empty for parallel formats."
          },

          "pieces": {
            "type": "array",
            "description": "For round chapters with chapter_id in {world, pixel_byte, toolkit, touchline, screen_sound, session}. v8.37 (W-3): the mandatory considered-piece backbone is RETIRED — the single Long Read (`08-anchor-piece`) carries the deep work, and a round carries the week's news at whatever depth the material earns. 0-2 pieces — an OPTIONAL role=lead (a considered piece) plus an OPTIONAL role=companion (a companion still requires a lead). A round may run a Lead, a plain `catch_up` roundup with no lead, picks, or nothing (a silent yield) — none of these hard-fails. If a companion is present, Lead.topic_family MUST differ from Companion.topic_family. Validator hard-fails only on well-formedness: >1 lead, >1 companion, a companion without a lead, a companion sharing the lead's topic_family, a bad topic_family, or below-floor word counts. There is no longer a catch_up-only or empty-section hard-fail.",
            "minItems": 0,
            "maxItems": 2,
            "items": {
              "type": "object",
              "required": ["role", "topic_family", "word_count_target", "headline_hint", "link_targets"],
              "properties": {
                "role": {
                  "type": "string",
                  "enum": ["lead", "companion"],
                  "description": "'lead' is the section's centrepiece (required, exactly one). 'companion' is an OPTIONAL second deep piece (at most one) — run it only when the section genuinely has a second topic worth a full article."
                },
                "topic_family": {
                  "type": "string",
                  "description": "Must be drawn from the closed enumeration in § Topic Family Enumeration below. When a companion is present, Lead.topic_family != Companion.topic_family within the same chapter."
                },
                "word_count_target": {
                  "type": "object",
                  "required": ["min", "max"],
                  "properties": {
                    "min": { "type": "integer", "minimum": 120, "description": "2026-07-13 handoff A5: the min is the piece's share of the band's allocated target_words (weekly.json), no longer a bare sanity floor — a round band's pieces should cover its 350-600-word allocation (absolute floors remain lead 150, companion 120). Don't pad beyond the material: a piece landing far under its share flags the planner for more research instead of shipping short." },
                    "max": { "type": "integer", "minimum": 200, "description": "Ceiling. Lead typical 700, can run to 1000+. Companion typical 450, ceiling 600." }
                  },
                  "description": "Word-count band for this piece. Validator rejects Lead with min < 300 or Companion with min < 200."
                },
                "headline_hint": {
                  "type": "string",
                  "description": "Suggested headline angle / framing for the writer. Not the final headline — the writer composes that."
                },
                "link_targets": {
                  "type": "array",
                  "items": { "type": "string", "format": "uri" },
                  "description": "URLs the writer should consider linking. Pulled from research-bundle.json. Writer must include at least one outbound link per piece (Gate 1D)."
                }
              }
            }
          },

          "catch_up": {
            "type": "array",
            "description": "v8.27, OPTIONAL since v8.34 — the Catch-Up roundup for a fixed section: missable domain news + one-line safety-net headlines, used as grounding context for the considered piece (NOT exhaustive coverage — that's the daily's job). It is NOT a mandatory element: the mandatory element is the considered piece (a `lead`) or a `yield_reason`; a section with only catch_up and no lead/yield_reason hard-fails (it must yield). When present, each item carries what/why/link — NO bare namedrops. Validator hard-fails any item missing headline_hint, why_it_matters, or a non-empty link_targets.",
            "items": {
              "type": "object",
              "required": ["headline_hint", "why_it_matters", "link_targets"],
              "properties": {
                "headline_hint": { "type": "string", "description": "What it is — the one-line framing of the development." },
                "why_it_matters": { "type": "string", "description": "Why it matters to the reader. Non-empty — this is the anti-namedrop field." },
                "link_targets": { "type": "array", "items": { "type": "string", "format": "uri" }, "description": "At least one specific link. Every Catch-Up item must be followable." }
              }
            }
          },

          "yield_reason": {
            "type": ["string", "null"],
            "description": "v8.27 — Optional. When a fixed section genuinely runs short (thin week — especially The Toolkit, which is fixed-but-yields), set a one-line reason here instead of padding. Satisfies the 'second substantive element' requirement so a Lead-only section can pass. Don't use it to dodge a real Catch-Up when there is news."
          },

          "items": {
            "type": "array",
            "description": "REQUIRED for chapter_id 'long_shelf'. Array of 6-8 items with at least 2 carrying wildcard: true. Validator hard-fails if items.length < 6 or > 8, or if count(wildcard==true) < 2. For chapter_id 'history' with sub_format='closer_look', this array is FORBIDDEN — the chapter has a single featured item only.",
            "minItems": 6,
            "maxItems": 8,
            "items": {
              "type": "object",
              "required": ["title", "source", "link", "hook", "wildcard"],
              "properties": {
                "title": { "type": "string", "description": "Item title (linked in the final markup)." },
                "source": { "type": "string", "description": "Publisher / origin (e.g. 'The Atlantic', 'Stratechery', 'BBC Sounds')." },
                "link": { "type": "string", "format": "uri", "description": "Specific item URL — not a category page." },
                "hook": { "type": "string", "description": "One-sentence hook selling the content on its merit (no reader-profile leaks)." },
                "wildcard": { "type": "boolean", "description": "true if this item is outside the magazine's usual coverage areas (not gaming, sport, Star Wars, fantasy/sci-fi, fitness, UK consumer fintech, theme parks, history podcasts). At least 2 of the 6-8 items must be wildcards." }
              }
            }
          },

          "radar_items": {
            "type": "array",
            "description": "v8.30 — REQUIRED for chapter_id 'release_radar'. The weekly Release Radar: 15-20 upcoming-weighted media releases across ALL categories. Validator (check_release_radar) hard-fails if radar_items.length < 15 or if fewer than 4 distinct categories are represented. A weekly plan with NO release_radar chapter also hard-fails (the section is mandatory — it was silently dropped before v8.30). Distinct from `items` (the long_shelf field) by design — release items carry category/date/status, not source/hook/wildcard.",
            "minItems": 15,
            "maxItems": 24,
            "items": {
              "type": "object",
              "required": ["title", "category", "date", "status", "link"],
              "properties": {
                "title": { "type": "string", "description": "The release title (linked in the final markup)." },
                "category": { "type": "string", "enum": ["film", "tv", "game", "lego", "tech", "book", "music"], "description": "Closed media category — drives the .radar-cat colour dot. At least 4 distinct categories must appear across the section." },
                "date": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$", "description": "Release date (YYYY-MM-DD)." },
                "status": { "type": "string", "enum": ["happened", "upcoming"], "description": "Reuses the v8.29 fact-status tag. Release Radar is upcoming-weighted; a just-released item may be 'happened' (Now Showing / Out Now), everything else 'upcoming' (Coming Soon)." },
                "link": { "type": "string", "format": "uri", "description": "Specific source/store/trailer URL — not a category page." },
                "note": { "type": "string", "description": "Optional one-line why-it-matters / platform note." }
              }
            }
          },

          "sub_format": {
            "type": ["string", "null"],
            "enum": [null, "directors_cut", "closer_look"],
            "description": "v8.17 — Optional sub-format mode for specific chapters. Allowed values: null (default standard mode), 'directors_cut' (Screen & Sound only — Lead is a 550-750 word essay; Lead.word_count_target.min must be >= 550), 'closer_look' (History only — single 600-800 word narrative; chapter must have a featured_item with word_count_target.min >= 600 and NO items/also_items array). Validator rejects: sub_format='directors_cut' on any chapter other than screen_sound; sub_format='closer_look' on any chapter other than history; word floors not met; also_items present on closer_look."
          },

          "featured_item": {
            "type": "object",
            "description": "REQUIRED for chapter_id 'history' with sub_format='closer_look'. The single narrative deep-dive piece. Forbidden for other chapters.",
            "required": ["topic_family", "word_count_target", "headline_hint", "link_targets"],
            "properties": {
              "topic_family": { "type": "string", "description": "Drawn from the topic-family enum. Usually 'books_history' or an era-specific family." },
              "word_count_target": {
                "type": "object",
                "required": ["min", "max"],
                "properties": {
                  "min": { "type": "integer", "minimum": 600, "description": "A Closer Look floor: 600." },
                  "max": { "type": "integer", "minimum": 600, "description": "A Closer Look ceiling typical: 800." }
                }
              },
              "headline_hint": { "type": "string" },
              "link_targets": {
                "type": "array",
                "items": { "type": "string", "format": "uri" },
                "description": "Wikipedia link is mandatory; additional sources welcome."
              }
            }
          }

        }
      }
    },

    "discovery_picks": {
      "type": "array",
      "description": "v8.19 — Issue-level array of items the planner has flagged as 'discovery' (things the reader wouldn't have looked for themselves). Must contain >= 3 entries on standard weeklies. The Long Shelf's 2 wildcards count toward this; the remaining 1+ can come from any other section's content. Each entry references the chapter and item that's the discovery pick. Gate 2 verifies the array length and that each referenced item actually appears in the rendered HTML. Lens-not-filter enforcement.",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": ["chapter_id", "headline_hint", "discovery_rationale"],
        "properties": {
          "chapter_id": { "type": "string", "description": "The chapter containing this discovery pick." },
          "headline_hint": { "type": "string", "description": "Short identifier of the specific item / pick / topic that's the discovery moment." },
          "discovery_rationale": { "type": "string", "description": "One-sentence editorial reason this counts as a genuine discovery for this reader — not just 'new to the magazine'." }
        }
      }
    },

    "assets": {
      "type": "object",
      "required": ["css_inject_marker", "js_inject_marker", "scaffold_parts_used"],
      "properties": {
        "css_inject_marker": {
          "type": "string",
          "description": "The placeholder comment used in the HTML template for CSS injection. Canonical: '<!-- INJECT:CSS -->'."
        },
        "js_inject_marker": {
          "type": "string",
          "description": "The placeholder comment for JS injection. Canonical: '<!-- INJECT:JS -->'."
        },
        "scaffold_parts_used": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Template part filenames (from assets/template-parts/) used to build the scaffold. The stitcher reads these in order. E.g. ['00-head-open.html', '01-masthead.html', '02-wax-seal.html', '03-cover.html', '04-navigator.html', '05-foreword.html']."
        }
      }
    },

    "compliance": {
      "type": "object",
      "required": ["stat_budget_max", "image_source_diversity_min", "accent_lockdown"],
      "properties": {
        "stat_budget_max": {
          "type": "integer",
          "description": "Hard cap on total stat-heavy blocks across the issue. Per editorial-spec: max 12 combined (sp-stat-curtain: 1, sp-dash: 1, sp-number/sp-number-huge: 6, sp-datum: 4).",
          "default": 12
        },
        "image_source_diversity_min": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Minimum fraction of images that must NOT come from the dominant domain. 0.5 = no single domain may provide >50% of attributed images. Gate 3 enforces this.",
          "default": 0.5
        },
        "accent_lockdown": {
          "type": "boolean",
          "description": "Must always be true. Confirms the plan acknowledges v8.4 coral accent lockdown — coral reserved only for chapter gate numerals, Countdown D-day badge, and page progress bar.",
          "const": true
        }
      }
    }

  }
}
```

---

## Format → Execution Mode Mapping

The validator enforces this table. If `execution_mode` does not match the format, validation fails.

| Format | Execution Mode | Rationale |
|---|---|---|
| `weekly` | `parallel` | Sections are independent; no narrative throughline |
| `countdown` | `parallel` | Hype/list chapters independent by design |
| `field_guide` | `parallel` | Reference chapters are independent |
| `guide` | `parallel` | Merged recommendation format (v8.39 S4) — list-driven picks are independent |
| `shortlist` | `parallel` | Back-compat slug for guide (category mode) — list-driven picks are independent |
| `starter_kit` | `parallel` | Back-compat slug for guide (beginner mode) — listicle chapters are independent |
| `lookahead` | `parallel` | Calendar items are independent; The Crunch Weeks chapter aggregates after |
| `deep_dive` | `sequential` | Literary voice must coalesce across chapters |
| `versus` | `sequential` | Round verdicts reference prior rounds |
| `rewind` | `sequential` | Narrative arc and Throughline span all chapters |
| `next` | `sequential` | Every pick is judged against The Itch named in chapter 1; If You Only Try One depends on prior picks |
| `season_review` | `sequential` | Seasonal argument builds chapter to chapter |

---

## `chapter_type` Semantics

| Type | Description | Hype allowed? |
|---|---|---|
| `opener` | Cover, foreword, by-the-numbers — sets the stage | Countdown: yes; others: no |
| `hype` | Anticipation-forward: Top Attractions, Mood Board, Five Moments | Countdown + Field Guide only |
| `literary` | Long-form prose with spread layout: Deep Dive body, Rewind narrative | Never |
| `practical` | Reference-first: Before You Go, Field Guide sections, Starter Kit picks | Field Guide: yes for Opening + Unmissables; others: no |
| `gallery` | Mood Board, image-dominant | Yes |
| `interlude` | Breather chapter between dense chapters | No |
| `signature` | Format's signature moment chapter (sand-clock, memory-wall, etc.) | No |
| `closer` | Meanwhile, On the Radar, Footer | No |

---

## Minimal Valid Example

```json
{
  "issue_meta": {
    "format": "countdown",
    "date": "2026-06-15",
    "topic": "Efteling & Beekse Bergen",
    "special_id": "countdown-efteling-2026",
    "execution_mode": "parallel"
  },
  "chapters": [
    {
      "chapter_id": "by-the-numbers",
      "chapter_num": 1,
      "chapter_type": "opener",
      "chapter_title": "By the Numbers",
      "chapter_arc": "The shape of the trip at a glance",
      "ground": "ink",
      "is_hype": true,
      "data_venue": null,
      "target_word_count": 400,
      "images_needed": [
        {
          "role": "establishing hero — Efteling skyline or icon",
          "source_constraint": "official press kit or Wikimedia Commons CC",
          "alt_required": true
        }
      ],
      "key_facts": [
        "Efteling founded 1952",
        "Beekse Bergen safari park covers 90 hectares",
        "7 nights total: 2 Efteling, 5 Beekse Bergen"
      ],
      "forbidden_topics": [
        "do not describe individual rides — that is chapter-top-attractions",
        "do not cover accommodation — that is chapter-accommodation"
      ],
      "cross_refs": []
    }
  ],
  "assets": {
    "css_inject_marker": "<!-- INJECT:CSS -->",
    "js_inject_marker": "<!-- INJECT:JS -->",
    "scaffold_parts_used": [
      "00-head-open.html",
      "01-masthead.html",
      "02-wax-seal.html",
      "03-cover.html",
      "04-navigator.html",
      "05-foreword.html",
      "19-closing.html"
    ]
  },
  "compliance": {
    "stat_budget_max": 12,
    "image_source_diversity_min": 0.5,
    "accent_lockdown": true
  }
}
```

---

## Topic Family Enumeration (v8.15)

Every `pieces[*].topic_family` MUST be one of the values below. The enumeration is closed — adding a new family requires a spec amendment. Validator (`scripts/validate-chapter-plan.py`) hard-fails any plan with an unrecognised `topic_family`.

Families are grouped by cluster for readability; the cluster name is editorial shorthand only — the validator checks against the flat union of all values.

### news_geopolitics
`iran_war`, `ukraine`, `russia`, `china_geopolitics`, `us_politics`, `uk_politics`, `eu_politics`, `africa`, `middle_east_non_iran`, `asia_pacific`, `climate_environment`, `space_exploration`, `pandemics_health`, `ni_politics`

### tech_gaming
`switch_2`, `playstation`, `xbox`, `nintendo_other`, `pc_gaming`, `steam_deck`, `geforce_now`, `consumer_ai`, `generative_ai_consumer`, `ai_search`, `tablets_phones`, `wearables_consumer`, `e_readers`, `lego`, `streaming_tech`, `smart_home`

### sport
`serie_a`, `premier_league`, `champions_league`, `europa_league`, `wc_qualifiers`, `wc_finals`, `euros`, `golf_majors`, `golf_ryder_cup`, `golf_tours`, `f1`, `tennis_slams`, `tennis_other`, `rugby_six_nations`, `rugby_world_cup`, `olympics`, `cricket`, `snooker`, `sport_governance`

### screen_culture
`star_wars`, `mcu`, `dc`, `disney_other`, `apple_tv`, `netflix`, `prime_video`, `nowtv_hbo`, `cinema_releases`, `film_classics`, `music_synthwave`, `music_general`, `audio_dramas`, `podcasts_critical`, `podcasts_history`

### fitness
`running_science`, `concurrent_training`, `hypertrophy`, `kettlebells`, `gymnastics_rings`, `recovery_mobility`, `wearable_data`, `nutrition_recomp`, `landmine_training`, `home_gym_programming`, `race_prep`

### other
`ni_local`, `travel_european`, `theme_parks`, `books_fantasy_scifi`, `books_history`, `books_other`, `ukpf_fintech`, `ukpf_investing`, `etsy_side_hustle`, `productivity_workflows`

---

## Fixed-Section Considered-Piece Example (v8.27, inverted v8.34)

A considered piece (a Lead that passes the two-factor test) — the mandatory backbone — with an **optional** Catch-Up roundup grounding it (what/why/link, no namedrops). The Companion is omitted here — it's optional, as is the Catch-Up itself (a section may run the considered piece alone). The Catch-Up's last item shows the one-line safety-net pattern for a big known headline that didn't earn the Lead.

```json
{
  "chapter_id": "world",
  "chapter_num": 4,
  "chapter_type": "opener",
  "chapter_title": "The World This Week",
  "chapter_arc": "The story that moved, plus what else he missed",
  "ground": "paper",
  "is_hype": false,
  "data_venue": null,
  "target_word_count": 1000,
  "images_needed": [],
  "key_facts": [],
  "forbidden_topics": [],
  "cross_refs": [],
  "pieces": [
    {
      "role": "lead",
      "topic_family": "us_politics",
      "word_count_target": { "min": 400, "max": 700 },
      "headline_hint": "The Senate vote and what it means for the midterms (it moved this week + we add the analysis)",
      "link_targets": ["https://www.nytimes.com/...", "https://www.economist.com/..."]
    }
  ],
  "catch_up": [
    {
      "headline_hint": "COP intersessional concludes",
      "why_it_matters": "Widens the gap between pledges and plans before the autumn summit",
      "link_targets": ["https://unfccc.int/..."]
    },
    {
      "headline_hint": "Ukraine's biggest weekly territorial gain of the year",
      "why_it_matters": "Shifts the front line for the first time in months",
      "link_targets": ["https://www.bbc.co.uk/..."]
    },
    {
      "headline_hint": "Safety-net line: UK PM survives confidence vote",
      "why_it_matters": "A known headline kept as a line so it's never dropped — didn't earn the Lead (holding pattern, no new development)",
      "link_targets": ["https://www.bbc.co.uk/..."]
    }
  ]
}
```

A fixed section that genuinely runs short omits `catch_up` and sets a `yield_reason` instead — e.g. The Toolkit on a thin tech week:

```json
{
  "chapter_id": "toolkit",
  "chapter_num": 6,
  "chapter_type": "literary",
  "chapter_title": "The Toolkit",
  "chapter_arc": "One discovery worth finding",
  "ground": "paper",
  "is_hype": false,
  "data_venue": null,
  "target_word_count": 350,
  "images_needed": [],
  "key_facts": [],
  "forbidden_topics": [],
  "cross_refs": [],
  "pieces": [
    {
      "role": "lead",
      "topic_family": "productivity_workflows",
      "word_count_target": { "min": 300, "max": 500 },
      "headline_hint": "A split-screen gesture worth setting up on the tablet",
      "link_targets": ["https://www.xda-developers.com/..."]
    }
  ],
  "yield_reason": "Thin consumer-tech week; running a single discovery Lead rather than padding a roundup."
}
```

## Long Shelf Example (v8.15)

```json
{
  "chapter_id": "long_shelf",
  "chapter_num": 3,
  "chapter_type": "opener",
  "chapter_title": "The Long Shelf",
  "chapter_arc": "Eight things worth your time",
  "ground": "paper",
  "is_hype": false,
  "data_venue": null,
  "target_word_count": 500,
  "images_needed": [],
  "key_facts": [],
  "forbidden_topics": [],
  "cross_refs": [],
  "items": [
    { "title": "Item one", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "Item two", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "Item three", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "Item four", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "Item five", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "Item six", "source": "Source", "link": "https://...", "hook": "One sentence.", "wildcard": false },
    { "title": "A wildcard pick", "source": "Source", "link": "https://...", "hook": "Why it's outside the magazine's usual ground.", "wildcard": true },
    { "title": "Another wildcard pick", "source": "Source", "link": "https://...", "hook": "Why it's outside the magazine's usual ground.", "wildcard": true }
  ]
}
```
