# Chapter Plan Schema (v8.17)

The planner subagent writes `/tmp/signal-build/chapter-plan.json`. This file defines the contract between the planner and the writer subagents. Every field here is required unless marked optional.

The validator at `scripts/validate-chapter-plan.py` enforces this schema. A plan that fails validation cannot proceed to Phase 5 (writer subagents).

**v8.15 additions:** every fixed-section chapter (`world`, `pixel_byte`, `touchline`, `screen_sound`, `session`) carries a `pieces` array of exactly two entries (Lead + Companion) on distinct `topic_family` values. The `long_shelf` chapter carries an `items` array of 6–8 entries with at least two `wildcard: true`. Topic families are a closed enumeration — see § Topic Family Enumeration at the bottom of this file.

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
            "starter_kit",
            "blueprint",
            "shortlist",
            "field_guide"
          ],
          "description": "Issue format — closed vocabulary. Use snake_case."
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
            "description": "Target word count for this chapter's prose. Guides writer length but is not a hard cap — cut if content doesn't support it."
          },

          "images_needed": {
            "type": "array",
            "description": "Images the writer should source for this chapter. Role describes what the image should show.",
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
            "items": { "type": "string" },
            "description": "Specific facts from research-bundle.json the writer MUST include in this chapter. Verified facts only — planner pulls these from the research bundle."
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
            "description": "REQUIRED for fixed-section weekly chapters with chapter_id in {world, pixel_byte, touchline, screen_sound, session}. Exactly two pieces: one role=lead, one role=companion. Lead.topic_family MUST differ from Companion.topic_family. Validator hard-fails any plan where a fixed-section chapter omits this array or includes pieces with the same topic_family.",
            "minItems": 2,
            "maxItems": 2,
            "items": {
              "type": "object",
              "required": ["role", "topic_family", "word_count_target", "headline_hint", "link_targets"],
              "properties": {
                "role": {
                  "type": "string",
                  "enum": ["lead", "companion"],
                  "description": "'lead' is the section's centrepiece. 'companion' is the mandatory second substantive piece."
                },
                "topic_family": {
                  "type": "string",
                  "description": "Must be drawn from the closed enumeration in § Topic Family Enumeration below. Lead.topic_family != Companion.topic_family within the same chapter."
                },
                "word_count_target": {
                  "type": "object",
                  "required": ["min", "max"],
                  "properties": {
                    "min": { "type": "integer", "minimum": 200, "description": "Floor word count. Lead floor 300; Companion floor 200." },
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
          "description": "Template part filenames (from assets/template-parts/) used to build the scaffold. The stitcher reads these in order. E.g. ['00-head-open.html', '01-masthead.html', '02-wax-seal.html', '03-cover.html', '04-navigator-toc.html', '05-foreword.html']."
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
| `shortlist` | `parallel` | List-driven picks are independent |
| `starter_kit` | `parallel` | Listicle chapters are independent |
| `blueprint` | `parallel` | How-to phases are independent |
| `deep_dive` | `sequential` | Literary voice must coalesce across chapters |
| `versus` | `sequential` | Round verdicts reference prior rounds |
| `rewind` | `sequential` | Narrative arc spans all chapters |
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
      "04-navigator-toc.html",
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

## Fixed-Section Lead + Companion Example (v8.15)

```json
{
  "chapter_id": "world",
  "chapter_num": 4,
  "chapter_type": "opener",
  "chapter_title": "The World This Week",
  "chapter_arc": "Two stories that shaped the week",
  "ground": "paper",
  "is_hype": false,
  "data_venue": null,
  "target_word_count": 1100,
  "images_needed": [],
  "key_facts": [],
  "forbidden_topics": [],
  "cross_refs": [],
  "pieces": [
    {
      "role": "lead",
      "topic_family": "us_politics",
      "word_count_target": { "min": 400, "max": 700 },
      "headline_hint": "The Senate vote and what it means for the midterms",
      "link_targets": ["https://www.nytimes.com/...", "https://www.economist.com/..."]
    },
    {
      "role": "companion",
      "topic_family": "climate_environment",
      "word_count_target": { "min": 250, "max": 450 },
      "headline_hint": "COP intersessional concludes — the gap between pledges and plans",
      "link_targets": ["https://unfccc.int/..."]
    }
  ]
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
