#!/usr/bin/env python3
"""
validate-chapter-plan.py — Mandatory gate between Phase 4 (Planner) and Phase 5 (Writers).

Usage:
    python scripts/validate-chapter-plan.py [path-to-plan.json]
    python scripts/validate-chapter-plan.py [path-to-plan.json] --state [path-to-state.json]
    python scripts/validate-chapter-plan.py --test

Default plan path: /tmp/signal-build/chapter-plan.json

Exits 0 on PASS. Exits 1 on any failure (prints all errors before exiting).

v8.36 — RETIRES the cadence-floor (old rule 7) and deficit-promotion (old rule 8)
rotating-section validators. Domain cadence is now a simple editorial checklist line
("each domain surfaces at least monthly"), not a planner-enforced gate — The Threads
now owns continuity, so a quiet domain no longer needs a forced-include gate. The
rotating-roster cadence map, the state-resolution helper, and their tests are gone.

v8.37 (W-3) — RELAXES `check_section_shape`: the mandatory considered-piece backbone
is retired. The single Long Read carries the deep work; the rounds carry the week's
news at whatever depth the material earns. A round may be a Lead, a plain Catch-Up
roundup, picks, or a silent yield — there is no longer a "Lead-or-yield_reason"
hard-fail. Piece well-formedness (topic_family / word floors / companion-needs-lead /
distinct families) and the Catch-Up no-namedrops rule are still enforced. The
long-shelf, release-radar, sub-format, key-facts, and discovery-quota rules are
unchanged.
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_PLAN_PATH = "/tmp/signal-build/chapter-plan.json"

VALID_FORMATS = {
    "weekly",
    "deep_dive",
    "countdown",
    "season_review",
    "versus",
    "rewind",
    "starter_kit",
    "blueprint",
    "shortlist",
    "field_guide",
}

# Format → execution_mode mapping (hard rule)
FORMAT_EXECUTION_MODE = {
    "weekly":        "parallel",
    "countdown":     "parallel",
    "field_guide":   "parallel",
    "shortlist":     "parallel",
    "starter_kit":   "parallel",
    "blueprint":     "parallel",
    "deep_dive":     "sequential",
    "versus":        "sequential",
    "rewind":        "sequential",
    "season_review": "sequential",
}

# Formats where is_hype=True is permitted
HYPE_ALLOWED_FORMATS = {"countdown", "field_guide"}

# Formats where is_hype=True is BANNED (literary — full default chrome)
HYPE_BANNED_FORMATS = {"deep_dive", "versus", "rewind", "season_review"}

VALID_EXECUTION_MODES = {"parallel", "sequential"}

VALID_GROUNDS = {"paper", "ink", "gallery"}

VALID_CHAPTER_TYPES = {
    "opener",
    "hype",
    "literary",
    "practical",
    "gallery",
    "interlude",
    "signature",
    "closer",
}

# Round chapter IDs whose piece/catch_up well-formedness is validated (weekly format only).
# v8.37 (W-3): the mandatory considered-piece backbone is RETIRED — the single Long Read carries
# the deep work and these rounds carry the week's news at whatever depth the material earns. A round
# may run a Lead, a plain Catch-Up roundup, picks, or a silent yield; there is NO Lead-or-yield
# hard-fail. check_section_shape() now validates only piece well-formedness + the Catch-Up
# no-namedrops rule (nothing structural is required to be present). See check_section_shape().
# Accept both the underscored convention (spec) and existing single-word / kebab variants
# observed in real issue markup (id="world", id="tech", id="football", id="screen").
# v8.27 adds The Toolkit (now a fixed-but-yields section, was rotating).
FIXED_SECTION_CHAPTER_IDS = {
    "world", "world-this-week",
    "pixel_byte", "pixel-byte", "tech",
    "toolkit", "the_toolkit", "the-toolkit",
    "touchline", "football",
    "screen_sound", "screen-sound", "screen",
    "session",
}

# v8.15 — chapter ID that requires the `items` array with wildcard discipline.
# NOTE (v8.18.1): "shelf" was previously in this set, but it collides with the
# rotating "The Shelf" section (books + music). The Long Shelf is a different
# section (curated 6-8 link list opener). Require the canonical kebab/underscore
# form only.
LONG_SHELF_CHAPTER_IDS = {"long_shelf", "long-shelf"}

# v8.30 — Release Radar (upcoming media releases) is a required weekly chapter.
RELEASE_RADAR_CHAPTER_IDS = {"release_radar", "release-radar"}
RELEASE_RADAR_CATEGORIES = {"film", "tv", "game", "lego", "tech", "book", "music"}

# v8.17 — sub-format mapping: chapter_id -> allowed sub_format values
SCREEN_SOUND_CHAPTER_IDS = {"screen_sound", "screen-sound", "screen"}
HISTORY_CHAPTER_IDS = {"history", "this_week_in_history", "this-week-in-history"}
SUB_FORMAT_BY_CHAPTER = {
    "screen_sound": "directors_cut",
    "history": "closer_look",
}
# v8.17 — sub-format word-count floors (Lead piece for directors_cut; featured_item for closer_look)
SUB_FORMAT_LEAD_FLOOR = {
    "directors_cut": 550,
    "closer_look": 600,
}

# v8.15 / v8.28 — per-role minimum word-count floor (spec § Article Structure).
# v8.28: floors relaxed to small SANITY minimums (was lead 300 / companion 200). "Length
# follows material" — a tight, fully-substantive 150-word lead must pass; the old floor
# forced padding. These are sanity bounds only, not targets. (Sub-format floors like
# directors_cut=550 are separate and still apply.)
PIECE_MIN_FLOOR = {"lead": 150, "companion": 120}

# v8.15 — closed topic-family enumeration. See references/chapter-plan-schema.md.
TOPIC_FAMILIES = {
    # news_geopolitics
    "iran_war", "ukraine", "russia", "china_geopolitics", "us_politics",
    "uk_politics", "eu_politics", "africa", "middle_east_non_iran",
    "asia_pacific", "climate_environment", "space_exploration",
    "pandemics_health", "ni_politics",
    # tech_gaming
    "switch_2", "playstation", "xbox", "nintendo_other", "pc_gaming",
    "steam_deck", "geforce_now", "consumer_ai", "generative_ai_consumer",
    "ai_search", "tablets_phones", "wearables_consumer", "e_readers",
    "lego", "streaming_tech", "smart_home",
    # sport
    "serie_a", "premier_league", "champions_league", "europa_league",
    "wc_qualifiers", "wc_finals", "euros", "golf_majors", "golf_ryder_cup",
    "golf_tours", "f1", "tennis_slams", "tennis_other", "rugby_six_nations",
    "rugby_world_cup", "olympics", "cricket", "snooker", "sport_governance",
    # screen_culture
    "star_wars", "mcu", "dc", "disney_other", "apple_tv", "netflix",
    "prime_video", "nowtv_hbo", "cinema_releases", "film_classics",
    "music_synthwave", "music_general", "audio_dramas", "podcasts_critical",
    "podcasts_history",
    # fitness
    "running_science", "concurrent_training", "hypertrophy", "kettlebells",
    "gymnastics_rings", "recovery_mobility", "wearable_data",
    "nutrition_recomp", "landmine_training", "home_gym_programming",
    "race_prep",
    # other
    "ni_local", "travel_european", "theme_parks", "books_fantasy_scifi",
    "books_history", "books_other", "ukpf_fintech", "ukpf_investing",
    "etsy_side_hustle", "productivity_workflows",
}

KEBAB_RE = re.compile(r'^[a-z0-9]+([-_][a-z0-9]+)*$')  # v8.15: underscores allowed alongside hyphens (e.g. pixel_byte, screen_sound, long_shelf)
DATE_RE  = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# v8.36 — the canonical rotating-section cadence map and its chapter_id lookup were
# removed alongside the cadence-floor / deficit-promotion validators (old rules 7 & 8).
# Domain cadence is now an editorial checklist ("each domain surfaces at least monthly"),
# not a planner-enforced gate. See references/spec/weekly.md § Rotation Mechanics and
# the §5 gate ledger in docs/signal-final-recommendations-2026-07.md.

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class ValidationError(Exception):
    pass

errors = []

def err(msg):
    errors.append(msg)

def require_key(obj, key, path):
    if key not in obj:
        err(f"[MISSING] {path}: required key '{key}' not found")
        return False
    return True

# ─────────────────────────────────────────────────────────────────────────────
# Check functions
# ─────────────────────────────────────────────────────────────────────────────

def check_issue_meta(meta):
    """Check 1 + 2 + 3 + 4: top-level keys, format vocab, execution_mode match."""
    path = "issue_meta"

    required = ["format", "date", "topic", "special_id", "execution_mode"]
    for key in required:
        require_key(meta, key, path)

    if "format" not in meta:
        return  # can't continue without format

    fmt = meta.get("format")
    mode = meta.get("execution_mode")
    date = meta.get("date")

    # 3. format in closed vocab
    if fmt not in VALID_FORMATS:
        err(f"[FORMAT] issue_meta.format='{fmt}' is not in the closed vocabulary: {sorted(VALID_FORMATS)}")

    # date format
    if date and not DATE_RE.match(str(date)):
        err(f"[DATE] issue_meta.date='{date}' must be YYYY-MM-DD")

    # 4. execution_mode matches format
    if fmt and mode:
        if mode not in VALID_EXECUTION_MODES:
            err(f"[EXEC_MODE] issue_meta.execution_mode='{mode}' must be 'parallel' or 'sequential'")
        elif fmt in FORMAT_EXECUTION_MODE:
            expected = FORMAT_EXECUTION_MODE[fmt]
            if mode != expected:
                err(
                    f"[EXEC_MODE] issue_meta.execution_mode='{mode}' does not match format '{fmt}'. "
                    f"Expected: '{expected}'. "
                    f"(parallel formats: countdown, field_guide, shortlist, starter_kit, blueprint, weekly; "
                    f"sequential: deep_dive, versus, rewind, season_review)"
                )


def check_section_shape(ch, cpath):
    """v8.37 (W-3): the ROUNDS validate piece well-formedness only — no mandatory backbone.

    History: v8.15 mandated a two-anchor Lead + Companion; v8.27-v8.28 made the Catch-Up the
    spine; v8.34 inverted it to require a considered-piece Lead-or-yield. **v8.37 (W-3) retires the
    mandatory-considered-piece requirement entirely:** the single Long Read (`08-anchor-piece`)
    carries the deep work, and the rounds carry the week's news at whatever depth the material
    earns. A round may run a considered Lead, a plain Catch-Up roundup, picks, or nothing (a silent
    yield). There is NO "must have a Lead or a yield_reason" hard-fail any more.

    What is still validated (structural well-formedness only, if the fields are present):
      - `pieces` array: 0-2 entries. At most one role='lead'; at most one role='companion'; a
        Companion still requires a Lead (a companion with no lead is malformed).
      - Sanity word floors only (lead 150, companion 120) — length follows material, no padding.
      - Each piece: topic_family in enum, valid word_count_target, headline_hint, link_targets.
      - If a Companion is present, Lead.topic_family != Companion.topic_family.
      - Catch-Up "no bare namedrops" rule: every `catch_up` item carries headline_hint,
        why_it_matters, and a non-empty link_targets.
    """
    # v8.28 — the Lead is OPTIONAL: a section may be pure Catch-Up (facts) with no pieces at
    # all. `pieces` may therefore be absent or empty; if present it holds 0-2 entries
    # (an optional Lead + an optional Companion).
    pieces = ch.get("pieces")
    if pieces is None:
        pieces = []
    if not isinstance(pieces, list):
        err(f"[PIECES] {cpath}.pieces must be an array.")
        return
    if len(pieces) > 2:
        err(f"[PIECES] {cpath}.pieces may contain at most 2 entries (an optional Lead + an optional Companion). Found {len(pieces)}.")
        return

    roles_seen = []
    tf_by_role = {}
    for j, p in enumerate(pieces):
        ppath = f"{cpath}.pieces[{j}]"
        if not isinstance(p, dict):
            err(f"[PIECES] {ppath} must be an object.")
            continue
        role = p.get("role")
        if role not in ("lead", "companion"):
            err(f"[PIECES] {ppath}.role='{role}' must be 'lead' or 'companion'.")
        else:
            roles_seen.append(role)

        tf = p.get("topic_family")
        if tf is None:
            err(f"[PIECES] {ppath}: missing required field 'topic_family'.")
        elif tf not in TOPIC_FAMILIES:
            err(f"[PIECES] {ppath}.topic_family='{tf}' is not in the closed enumeration (see references/chapter-plan-schema.md § Topic Family Enumeration).")
        elif role in ("lead", "companion"):
            tf_by_role[role] = tf

        wct = p.get("word_count_target")
        if wct is None:
            err(f"[PIECES] {ppath}: missing required field 'word_count_target'.")
        elif not isinstance(wct, dict):
            err(f"[PIECES] {ppath}.word_count_target must be an object with min and max.")
        else:
            wmin = wct.get("min")
            wmax = wct.get("max")
            if not isinstance(wmin, int):
                err(f"[PIECES] {ppath}.word_count_target.min must be an integer.")
            elif role in PIECE_MIN_FLOOR and wmin < PIECE_MIN_FLOOR[role]:
                err(f"[PIECES] {ppath}.word_count_target.min={wmin} below spec floor of {PIECE_MIN_FLOOR[role]} for role '{role}'.")
            if not isinstance(wmax, int):
                err(f"[PIECES] {ppath}.word_count_target.max must be an integer.")
            elif isinstance(wmin, int) and wmax < wmin:
                err(f"[PIECES] {ppath}.word_count_target.max={wmax} must be >= min={wmin}.")

        for key in ("headline_hint", "link_targets"):
            if key not in p:
                err(f"[PIECES] {ppath}: missing required field '{key}'.")

    # Role coverage (v8.28): 0 or 1 lead; at most one companion; a Companion requires a Lead.
    lead_count = roles_seen.count("lead")
    companion_count = roles_seen.count("companion")
    if lead_count > 1:
        err(f"[PIECES] {cpath}.pieces may contain at most one 'lead'. Found roles: {roles_seen}.")
    if companion_count > 1:
        err(f"[PIECES] {cpath}.pieces may contain at most one 'companion'. Found roles: {roles_seen}.")
    if companion_count >= 1 and lead_count == 0:
        err(f"[PIECES] {cpath}: a Companion requires a Lead. A fixed section needs a considered piece (a Lead) or a yield_reason — drop the companion, add a lead, or yield.")

    # Distinct topic families when a companion is present.
    if "lead" in tf_by_role and "companion" in tf_by_role and tf_by_role["lead"] == tf_by_role["companion"]:
        err(f"[PIECES] {cpath}: Lead.topic_family and Companion.topic_family are both '{tf_by_role['lead']}'. When a Companion runs it MUST be on a different topic family (topic-family discipline).")

    # v8.37 (W-3) — the mandatory considered-piece backbone is RETIRED. The single Long Read
    # (the `08-anchor-piece` slot) now carries the deep work; the ROUNDS (world/pixel_byte/
    # toolkit/touchline/screen_sound/session) carry the week's news at whatever depth the material
    # earns. A round may run a considered Lead, a plain Catch-Up roundup, picks, or nothing — the
    # Lead/Catch-Up shape stays AVAILABLE but is no longer mandatory-deep. So there is no
    # "must have a Lead or a yield_reason" hard-fail any more: a catch-up-only round is fine, and
    # an empty/thin round is a silent yield. What IS still validated below: piece well-formedness
    # (topic_family / word floors / companion-needs-lead / distinct families — handled above) and
    # the Catch-Up "no bare namedrops" rule.
    catch_up = ch.get("catch_up")

    # v8.27 — Catch-Up "no bare namedrops": every roundup item carries what + why + link.
    if catch_up is not None:
        if not isinstance(catch_up, list):
            err(f"[CATCH_UP] {cpath}.catch_up must be an array of roundup items.")
        else:
            for k, item in enumerate(catch_up):
                ipath = f"{cpath}.catch_up[{k}]"
                if not isinstance(item, dict):
                    err(f"[CATCH_UP] {ipath} must be an object.")
                    continue
                for key in ("headline_hint", "why_it_matters"):
                    if not item.get(key):
                        err(f"[CATCH_UP] {ipath}: missing or empty '{key}' — Catch-Up items must say what it is and why it matters (no bare namedrops, v8.27).")
                links = item.get("link_targets")
                if not (isinstance(links, list) and len(links) > 0):
                    err(f"[CATCH_UP] {ipath}: 'link_targets' must be a non-empty array — every Catch-Up item needs a link (v8.27).")


def check_key_facts(ch, cpath):
    """v8.29: validate structured `key_facts` records carried from the bundle.

    Each entry is either a bare string (back-compat) or a structured fact record
    {claim, status, date, source_url, [type, speaker, quote]}. The structured
    form carries the researcher's happened/upcoming decision down to the writer
    (see references/spec/global.md § fact-provenance). We mirror the bundle gate
    (validate-research-bundle.py) so a malformed record can't slip through the
    planner even though the bundle gate already ran upstream.

    Note: the run-date temporal check (status=happened in the future) lives in the
    bundle gate, which has --run-date; the plan validator is run without a date
    anchor, so here we validate shape + status/date well-formedness + opinion
    provenance only.
    """
    facts = ch.get("key_facts")
    if not isinstance(facts, list):
        return  # presence/type already covered by required_fields
    for k, f in enumerate(facts):
        ipath = f"{cpath}.key_facts[{k}]"
        if isinstance(f, str):
            continue  # bare string is accepted for back-compat
        if not isinstance(f, dict):
            err(f"[KEY_FACTS] {ipath}: must be a string or a structured fact object.")
            continue
        for key in ("claim", "status", "date", "source_url"):
            if not f.get(key):
                err(f"[KEY_FACTS] {ipath}: structured fact missing/empty '{key}'.")
        status = f.get("status")
        if status is not None and status not in ("happened", "upcoming"):
            err(f"[KEY_FACTS] {ipath}: status='{status}' must be 'happened' or 'upcoming'.")
        date = f.get("date")
        if date and not DATE_RE.match(str(date)):
            err(f"[KEY_FACTS] {ipath}: date='{date}' must be YYYY-MM-DD.")
        src = f.get("source_url")
        if src and not str(src).startswith(("http://", "https://")):
            err(f"[KEY_FACTS] {ipath}: source_url='{src}' must be an http(s) URL.")
        ftype = f.get("type", "fact")
        if ftype not in ("fact", "opinion"):
            err(f"[KEY_FACTS] {ipath}: type='{ftype}' must be 'fact' or 'opinion'.")
        if ftype == "opinion":
            if not f.get("speaker"):
                err(f"[KEY_FACTS] {ipath}: type=opinion requires a non-empty 'speaker'.")
            if not f.get("quote"):
                err(f"[KEY_FACTS] {ipath}: type=opinion requires a non-empty 'quote' (the real words).")


def check_long_shelf_items(ch, cpath):
    """v8.15: long_shelf chapter requires an `items` array of 6-8 entries with >=2 wildcards."""
    items = ch.get("items")
    if items is None:
        err(f"[ITEMS] {cpath}: long_shelf chapter is missing required 'items' array (v8.15).")
        return
    if not isinstance(items, list):
        err(f"[ITEMS] {cpath}.items must be an array.")
        return
    if not (6 <= len(items) <= 8):
        err(f"[ITEMS] {cpath}.items must contain 6-8 entries. Found {len(items)}.")

    wildcard_count = 0
    for j, it in enumerate(items):
        ipath = f"{cpath}.items[{j}]"
        if not isinstance(it, dict):
            err(f"[ITEMS] {ipath} must be an object.")
            continue
        for key in ("title", "source", "link", "hook", "wildcard"):
            if key not in it:
                err(f"[ITEMS] {ipath}: missing required field '{key}'.")
        if it.get("wildcard") is True:
            wildcard_count += 1

    if wildcard_count < 2:
        err(f"[ITEMS] {cpath}: long_shelf needs >=2 items with wildcard=true. Found {wildcard_count} (v8.15 wildcard discipline).")


def check_release_radar(ch, cpath):
    """v8.30: release_radar chapter requires a `radar_items` array of >=15 upcoming-weighted
    media releases across >=4 distinct categories. Mirrors check_long_shelf_items; this is the
    structural gate that stops Release Radar being silently dropped (the 1 June test gap)."""
    items = ch.get("radar_items")
    if items is None:
        err(f"[RADAR] {cpath}: release_radar chapter is missing required 'radar_items' array (v8.30).")
        return
    if not isinstance(items, list):
        err(f"[RADAR] {cpath}.radar_items must be an array.")
        return
    if len(items) < 15:
        err(f"[RADAR] {cpath}.radar_items must contain >=15 entries (15-20 target). Found {len(items)}.")

    cats = set()
    for j, it in enumerate(items):
        ipath = f"{cpath}.radar_items[{j}]"
        if not isinstance(it, dict):
            err(f"[RADAR] {ipath} must be an object.")
            continue
        for key in ("title", "category", "date", "status", "link"):
            if not it.get(key):
                err(f"[RADAR] {ipath}: missing required field '{key}'.")
        cat = it.get("category")
        if cat is not None and cat not in RELEASE_RADAR_CATEGORIES:
            err(f"[RADAR] {ipath}: category='{cat}' must be one of {sorted(RELEASE_RADAR_CATEGORIES)}.")
        elif cat:
            cats.add(cat)
        st = it.get("status")
        if st is not None and st not in ("happened", "upcoming"):
            err(f"[RADAR] {ipath}: status='{st}' must be 'happened' or 'upcoming'.")
        d = it.get("date")
        if d and not DATE_RE.match(str(d)):
            err(f"[RADAR] {ipath}: date='{d}' must be YYYY-MM-DD.")

    if len(cats) < 4:
        err(f"[RADAR] {cpath}: release_radar needs >=4 distinct categories. Found {len(cats)} ({sorted(cats)}).")


def check_sub_format(ch, cpath, ch_id):
    """v8.17: validate optional sub_format field.

    Rules:
      - sub_format must be one of {null, "directors_cut", "closer_look"} when present.
      - "directors_cut" is only legal on screen_sound chapters.
      - "closer_look" is only legal on history chapters.
      - When sub_format="directors_cut": Lead piece's word_count_target.min must be >= 550.
      - When sub_format="closer_look": chapter must have a featured_item (single deep-dive)
        with word_count_target.min >= 600, and MUST NOT have items/also_items arrays.
    """
    sub_format = ch.get("sub_format")
    if sub_format is None:
        # featured_item is forbidden when sub_format is null (only valid for closer_look)
        if ch.get("featured_item") is not None:
            err(f"[SUB_FORMAT] {cpath}: 'featured_item' is only allowed when sub_format='closer_look'.")
        return

    allowed_values = {None, "directors_cut", "closer_look"}
    if sub_format not in allowed_values:
        err(f"[SUB_FORMAT] {cpath}.sub_format='{sub_format}' must be one of {sorted(v for v in allowed_values if v is not None)} or null (v8.17).")
        return

    # Chapter-binding: directors_cut on screen_sound only, closer_look on history only
    if sub_format == "directors_cut" and ch_id not in SCREEN_SOUND_CHAPTER_IDS:
        err(f"[SUB_FORMAT] {cpath}: sub_format='directors_cut' is only legal on screen_sound chapter (v8.17). Chapter id='{ch_id}'.")
        return
    if sub_format == "closer_look" and ch_id not in HISTORY_CHAPTER_IDS:
        err(f"[SUB_FORMAT] {cpath}: sub_format='closer_look' is only legal on history chapter (v8.17). Chapter id='{ch_id}'.")
        return

    if sub_format == "directors_cut":
        # Lead word floor raised to 550
        pieces = ch.get("pieces") or []
        lead = next((p for p in pieces if isinstance(p, dict) and p.get("role") == "lead"), None)
        if lead is None:
            # check_pieces already errors on missing lead; don't duplicate
            return
        wct = lead.get("word_count_target") or {}
        wmin = wct.get("min")
        if isinstance(wmin, int) and wmin < SUB_FORMAT_LEAD_FLOOR["directors_cut"]:
            err(f"[SUB_FORMAT] {cpath}: sub_format='directors_cut' requires Lead.word_count_target.min >= {SUB_FORMAT_LEAD_FLOOR['directors_cut']}. Found {wmin} (v8.17).")

    if sub_format == "closer_look":
        # Single featured_item, no items/also_items array
        if ch.get("items") is not None:
            err(f"[SUB_FORMAT] {cpath}: sub_format='closer_look' forbids 'items' array — A Closer Look is a single narrative (v8.17).")
        if ch.get("also_items") is not None:
            err(f"[SUB_FORMAT] {cpath}: sub_format='closer_look' forbids 'also_items' — A Closer Look replaces the standard event-plus-timeline pattern with a single 600-800 word narrative (v8.17).")
        feat = ch.get("featured_item")
        if feat is None:
            err(f"[SUB_FORMAT] {cpath}: sub_format='closer_look' requires 'featured_item' object (v8.17).")
            return
        if not isinstance(feat, dict):
            err(f"[SUB_FORMAT] {cpath}.featured_item must be an object.")
            return
        for key in ("topic_family", "word_count_target", "headline_hint", "link_targets"):
            if key not in feat:
                err(f"[SUB_FORMAT] {cpath}.featured_item: missing required field '{key}'.")
        tf = feat.get("topic_family")
        if tf is not None and tf not in TOPIC_FAMILIES:
            err(f"[SUB_FORMAT] {cpath}.featured_item.topic_family='{tf}' is not in the closed enumeration.")
        wct = feat.get("word_count_target") or {}
        wmin = wct.get("min")
        if isinstance(wmin, int) and wmin < SUB_FORMAT_LEAD_FLOOR["closer_look"]:
            err(f"[SUB_FORMAT] {cpath}: sub_format='closer_look' requires featured_item.word_count_target.min >= {SUB_FORMAT_LEAD_FLOOR['closer_look']}. Found {wmin} (v8.17).")


def check_chapters(chapters, issue_meta):
    """Check 5–12: chapter field presence, uniqueness, ordering, cross-refs, grounds, types, is_hype."""
    if not isinstance(chapters, list) or len(chapters) == 0:
        err("[CHAPTERS] 'chapters' must be a non-empty array")
        return

    fmt = issue_meta.get("format", "")
    mode = issue_meta.get("execution_mode", "")

    chapter_ids = []
    chapter_nums = []
    chapter_id_set = set()

    required_fields = [
        "chapter_id", "chapter_num", "chapter_type", "chapter_title",
        "chapter_arc", "ground", "is_hype", "data_venue",
        "target_word_count", "images_needed", "key_facts",
        "forbidden_topics", "cross_refs",
    ]

    # First pass: collect IDs and nums, check required fields
    for i, ch in enumerate(chapters):
        cpath = f"chapters[{i}]"
        ch_id = ch.get("chapter_id", f"<missing-id-{i}>")

        # 5. All required fields present
        for key in required_fields:
            require_key(ch, key, cpath)

        ch_id = ch.get("chapter_id")
        ch_num = ch.get("chapter_num")

        if ch_id is not None:
            # 6. chapter_id is unique kebab-case
            if not KEBAB_RE.match(str(ch_id)):
                err(f"[CHAPTER_ID] {cpath}.chapter_id='{ch_id}' must be kebab-case (lowercase alphanumeric and hyphens only)")
            if ch_id in chapter_id_set:
                err(f"[CHAPTER_ID] {cpath}.chapter_id='{ch_id}' is duplicated")
            else:
                chapter_id_set.add(ch_id)
                chapter_ids.append(ch_id)

        if ch_num is not None:
            if not isinstance(ch_num, int) or ch_num < 1:
                err(f"[CHAPTER_NUM] {cpath}.chapter_num='{ch_num}' must be a positive integer")
            chapter_nums.append(ch_num)

        # 10. ground in closed vocab
        ground = ch.get("ground")
        if ground is not None and ground not in VALID_GROUNDS:
            err(f"[GROUND] {cpath}.ground='{ground}' must be one of {sorted(VALID_GROUNDS)}")

        # 11. chapter_type in closed vocab
        ch_type = ch.get("chapter_type")
        if ch_type is not None and ch_type not in VALID_CHAPTER_TYPES:
            err(f"[CHAPTER_TYPE] {cpath}.chapter_type='{ch_type}' must be one of {sorted(VALID_CHAPTER_TYPES)}")

        # 12. is_hype validation
        is_hype = ch.get("is_hype")
        if is_hype is True:
            if fmt in HYPE_BANNED_FORMATS:
                err(
                    f"[IS_HYPE] {cpath}: is_hype=true is banned on literary format '{fmt}'. "
                    f"Hype modifiers only allowed on: {sorted(HYPE_ALLOWED_FORMATS)}"
                )
            # (if fmt not in HYPE_ALLOWED_FORMATS but also not banned, allow with no error
            #  to be permissive for weekly/blueprint/shortlist/starter_kit if planner chooses)

        # 13. v8.27 — fixed-section Lead + Catch-Up shape (weekly format only)
        if fmt == "weekly" and ch_id in FIXED_SECTION_CHAPTER_IDS:
            check_section_shape(ch, cpath)

        # 14. v8.15 — long_shelf `items` array with wildcard discipline (weekly format only)
        if fmt == "weekly" and ch_id in LONG_SHELF_CHAPTER_IDS:
            check_long_shelf_items(ch, cpath)

        # 14b. v8.30 — release_radar `radar_items` array (weekly format only)
        if fmt == "weekly" and ch_id in RELEASE_RADAR_CHAPTER_IDS:
            check_release_radar(ch, cpath)

        # 15. v8.17 — optional sub_format field (Director's Cut on screen_sound, A Closer Look on history)
        if fmt == "weekly" and ("sub_format" in ch or "featured_item" in ch):
            check_sub_format(ch, cpath, ch_id)

        # 16. v8.29 — structured key_facts records (all formats)
        check_key_facts(ch, cpath)

    # 16b. v8.30 — Release Radar is a mandatory weekly chapter (presence check).
    if fmt == "weekly" and not (chapter_id_set & RELEASE_RADAR_CHAPTER_IDS):
        err("[RADAR] weekly plan is missing the required 'release_radar' chapter (v8.30 — Release Radar owns upcoming media releases and must always run; it was silently dropped before this gate).")

    # 7. chapter_num is 1..N, no gaps
    if chapter_nums:
        n = len(chapter_nums)
        sorted_nums = sorted(chapter_nums)
        if sorted_nums != list(range(1, n + 1)):
            err(
                f"[CHAPTER_NUM] chapter_num values {sorted_nums} must form a contiguous sequence 1..{n}. "
                f"Found gaps or duplicates."
            )

    # Second pass: check cross_refs (needs full chapter_id_set)
    for i, ch in enumerate(chapters):
        cpath = f"chapters[{i}]"
        cross_refs = ch.get("cross_refs")
        if cross_refs is None:
            continue

        if not isinstance(cross_refs, list):
            err(f"[CROSS_REFS] {cpath}.cross_refs must be an array")
            continue

        # 9. cross_refs empty for parallel formats
        if mode == "parallel" and len(cross_refs) > 0:
            err(
                f"[CROSS_REFS] {cpath}.cross_refs must be empty for parallel execution_mode '{mode}'. "
                f"Found: {cross_refs}. "
                f"Cross-refs are only allowed for sequential formats (deep_dive, versus, rewind, season_review)."
            )

        # 8. cross_refs reference existing chapter_ids
        for ref in cross_refs:
            if ref not in chapter_id_set:
                err(
                    f"[CROSS_REFS] {cpath}.cross_refs contains '{ref}' which does not match any chapter_id. "
                    f"Known ids: {sorted(chapter_id_set)}"
                )


def check_discovery_picks(plan, issue_meta):
    """v8.19: Lens-not-filter discovery quota.

    Standard weeklies must carry an issue-level discovery_picks array with
    >= 3 entries. Each entry must reference a chapter and have a non-empty
    headline_hint + discovery_rationale. Specials are exempt (they're
    single-topic by design).
    """
    fmt = (issue_meta or {}).get("format", "")
    if fmt != "weekly":
        return  # specials are exempt

    picks = plan.get("discovery_picks")
    if picks is None:
        err(
            "[DISCOVERY] plan.discovery_picks is missing — v8.19 lens-not-filter rule "
            "requires standard weeklies to carry >= 3 issue-level discovery picks. "
            "See editorial-spec.md § The Lens, Not the Filter."
        )
        return
    if not isinstance(picks, list):
        err("[DISCOVERY] plan.discovery_picks must be an array.")
        return
    if len(picks) < 3:
        err(
            f"[DISCOVERY] plan.discovery_picks has {len(picks)} entries; v8.19 requires >= 3 on "
            "standard weeklies. Every weekly must surface at least three 'you wouldn't have "
            "looked for this yourself' items across the issue. The Long Shelf's 2 wildcards "
            "count toward this; the remaining 1+ can come from any other section."
        )

    for j, p in enumerate(picks if isinstance(picks, list) else []):
        ppath = f"plan.discovery_picks[{j}]"
        if not isinstance(p, dict):
            err(f"[DISCOVERY] {ppath} must be an object.")
            continue
        for key in ("chapter_id", "headline_hint", "discovery_rationale"):
            if not p.get(key):
                err(f"[DISCOVERY] {ppath}: missing or empty required field '{key}'.")


def check_assets(assets):
    """Check assets block."""
    path = "assets"
    for key in ["css_inject_marker", "js_inject_marker", "scaffold_parts_used"]:
        require_key(assets, key, path)

    parts = assets.get("scaffold_parts_used")
    if parts is not None and not isinstance(parts, list):
        err(f"[ASSETS] assets.scaffold_parts_used must be an array of filename strings")


def check_compliance(compliance):
    """Check compliance block."""
    path = "compliance"
    for key in ["stat_budget_max", "image_source_diversity_min", "accent_lockdown"]:
        require_key(compliance, key, path)

    accent = compliance.get("accent_lockdown")
    if accent is not True:
        err(
            f"[COMPLIANCE] compliance.accent_lockdown must be true (v8.4 hard rule — coral reserved for "
            f"chapter gate numerals, Countdown D-day badge, and page progress bar only)"
        )

    budget = compliance.get("stat_budget_max")
    if budget is not None and (not isinstance(budget, int) or budget < 1):
        err(f"[COMPLIANCE] compliance.stat_budget_max must be a positive integer")

    diversity = compliance.get("image_source_diversity_min")
    if diversity is not None:
        if not isinstance(diversity, (int, float)) or not (0 <= diversity <= 1):
            err(f"[COMPLIANCE] compliance.image_source_diversity_min must be a number between 0 and 1")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def _parse_main_args(argv):
    """Parse plan path + optional --state <path>. Returns (plan_path, state_path)."""
    plan_path = None
    state_path = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--state":
            if i + 1 < len(argv):
                state_path = argv[i + 1]
                i += 2
                continue
            else:
                print("ERROR: --state requires a path argument")
                sys.exit(2)
        if plan_path is None and not a.startswith("--"):
            plan_path = a
        i += 1
    return (plan_path or DEFAULT_PLAN_PATH, state_path)


def main():
    plan_path_str, state_path = _parse_main_args(sys.argv)
    plan_path = Path(plan_path_str)

    # 1. Resolve path
    if not plan_path.exists():
        print(f"ERROR: No plan file found at '{plan_path}'")
        print(f"       Generate a plan with the Planner subagent first (Phase 4).")
        sys.exit(1)

    # 2. JSON parses
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failed: {e}")
        sys.exit(1)

    if not isinstance(plan, dict):
        print("ERROR: Plan must be a JSON object (dict), not array or scalar")
        sys.exit(1)

    # 3. Required top-level keys
    top_required = ["issue_meta", "chapters", "assets", "compliance"]
    for key in top_required:
        if key not in plan:
            err(f"[MISSING] Top-level key '{key}' not found")

    # Only continue sub-checks if the parent block exists
    issue_meta = plan.get("issue_meta", {})
    chapters   = plan.get("chapters", [])
    assets     = plan.get("assets", {})
    compliance = plan.get("compliance", {})

    if isinstance(issue_meta, dict):
        check_issue_meta(issue_meta)

    if isinstance(chapters, list):
        check_chapters(chapters, issue_meta if isinstance(issue_meta, dict) else {})

    if isinstance(assets, dict):
        check_assets(assets)

    if isinstance(compliance, dict):
        check_compliance(compliance)

    # v8.36 — rotating-section cadence enforcement (old rules 7 & 8) RETIRED.
    # Domain cadence is now an editorial checklist line, not a planner gate.

    # v8.19 — lens-not-filter discovery quota (weekly only)
    if isinstance(issue_meta, dict):
        check_discovery_picks(plan, issue_meta)

    # ── Report ──
    if errors:
        print(f"FAIL — {len(errors)} error(s) found in '{plan_path}':")
        print()
        for i, e in enumerate(errors, 1):
            print(f"  [{i}] {e}")
        print()
        print("Fix all errors and re-run this validator before spawning writer subagents.")
        sys.exit(1)
    else:
        chapter_count = len(chapters) if isinstance(chapters, list) else 0
        fmt = issue_meta.get("format", "?") if isinstance(issue_meta, dict) else "?"
        mode = issue_meta.get("execution_mode", "?") if isinstance(issue_meta, dict) else "?"
        print(f"PASS — '{plan_path}' is valid.")
        print(f"  Format: {fmt}  |  Execution: {mode}  |  Chapters: {chapter_count}")
        sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# Inline tests (run when called with --test)
# ─────────────────────────────────────────────────────────────────────────────

def run_inline_tests():
    """Run PASS + FAIL test cases inline and print results."""
    import tempfile, os

    test_results = []

    def make_plan(**overrides):
        """Build a minimal valid plan, apply overrides at top level or nested path."""
        plan = {
            "issue_meta": {
                "format": "countdown",
                "date": "2026-06-15",
                "topic": "Efteling",
                "special_id": "countdown-efteling-2026",
                "execution_mode": "parallel"
            },
            "chapters": [
                {
                    "chapter_id": "by-the-numbers",
                    "chapter_num": 1,
                    "chapter_type": "opener",
                    "chapter_title": "By the Numbers",
                    "chapter_arc": "The shape of the trip",
                    "ground": "ink",
                    "is_hype": True,
                    "data_venue": None,
                    "target_word_count": 400,
                    "images_needed": [{"role": "hero", "source_constraint": "Wikimedia", "alt_required": True}],
                    "key_facts": ["Efteling founded 1952"],
                    "forbidden_topics": [],
                    "cross_refs": []
                }
            ],
            "assets": {
                "css_inject_marker": "<!-- INJECT:CSS -->",
                "js_inject_marker": "<!-- INJECT:JS -->",
                "scaffold_parts_used": ["00-head-open.html", "19-closing.html"]
            },
            "compliance": {
                "stat_budget_max": 12,
                "image_source_diversity_min": 0.5,
                "accent_lockdown": True
            },
            # v8.19 — discovery_picks default for fixture (only consulted by weekly format)
            "discovery_picks": [
                {"chapter_id": "long_shelf", "headline_hint": "wildcard pick 1", "discovery_rationale": "outside usual coverage"},
                {"chapter_id": "long_shelf", "headline_hint": "wildcard pick 2", "discovery_rationale": "outside usual coverage"},
                {"chapter_id": "screen_sound", "headline_hint": "new-to-reader show", "discovery_rationale": "not in their viewing list"}
            ]
        }
        no_radar = overrides.pop("_no_radar", False)
        for k, v in overrides.items():
            plan[k] = v
        # v8.30 — weekly plans now require a release_radar chapter. Auto-inject a valid one
        # for any weekly fixture that doesn't already supply (or explicitly opt out of) one,
        # so the pre-existing weekly tests keep passing; release-radar-specific tests pass
        # their own radar chapter or set _no_radar=True.
        if (not no_radar and isinstance(plan.get("issue_meta"), dict)
                and plan["issue_meta"].get("format") == "weekly"
                and isinstance(plan.get("chapters"), list)
                and not any(isinstance(c, dict) and c.get("chapter_id") in RELEASE_RADAR_CHAPTER_IDS
                            for c in plan["chapters"])):
            nums = [c.get("chapter_num", 0) for c in plan["chapters"] if isinstance(c, dict)]
            plan["chapters"].append(valid_release_radar_chapter(max(nums or [0]) + 1))
        return plan

    def valid_release_radar_chapter(num):
        cats = ["film", "tv", "game", "lego", "tech", "book", "music"]
        items = [
            {"title": f"Release {i}", "category": cats[i % len(cats)], "date": "2026-06-20",
             "status": "upcoming", "link": "https://example.com", "note": "why"}
            for i in range(15)
        ]
        return {
            "chapter_id": "release_radar", "chapter_num": num, "chapter_type": "closer",
            "chapter_title": "Release Radar", "chapter_arc": "what's coming", "ground": "paper",
            "is_hype": False, "data_venue": None, "target_word_count": 300, "images_needed": [],
            "key_facts": [], "forbidden_topics": [], "cross_refs": [], "radar_items": items
        }

    def run_test(name, plan_dict, expect_pass):
        global errors
        errors = []

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(plan_dict, f)
            tmp = f.name

        try:
            issue_meta = plan_dict.get("issue_meta", {})
            chapters   = plan_dict.get("chapters", [])
            assets     = plan_dict.get("assets", {})
            compliance = plan_dict.get("compliance", {})

            if isinstance(issue_meta, dict): check_issue_meta(issue_meta)
            if isinstance(chapters, list):   check_chapters(chapters, issue_meta if isinstance(issue_meta, dict) else {})
            if isinstance(assets, dict):     check_assets(assets)
            if isinstance(compliance, dict): check_compliance(compliance)
            # v8.36 — rotating cadence enforcement retired (old rules 7 & 8)
            # v8.19
            if isinstance(issue_meta, dict):
                check_discovery_picks(plan_dict, issue_meta)

            passed = len(errors) == 0
            ok = (passed == expect_pass)
            status = "PASS" if ok else "FAIL"
            test_results.append((status, name, errors[:] if not ok else []))
            return ok
        finally:
            os.unlink(tmp)

    # ── VALID cases ──
    run_test("valid minimal countdown (parallel)", make_plan(), expect_pass=True)
    run_test("valid weekly (parallel)", make_plan(issue_meta={
        "format": "weekly", "date": "2026-06-15", "topic": "weekly", "special_id": None, "execution_mode": "parallel"
    }), expect_pass=True)
    run_test("valid deep_dive (sequential)", make_plan(
        issue_meta={"format": "deep_dive", "date": "2026-06-15", "topic": "deep dive topic", "special_id": "deep-dive-2026", "execution_mode": "sequential"},
        chapters=[{
            "chapter_id": "intro",
            "chapter_num": 1,
            "chapter_type": "literary",
            "chapter_title": "Intro",
            "chapter_arc": "Opening frame",
            "ground": "paper",
            "is_hype": False,
            "data_venue": None,
            "target_word_count": 1000,
            "images_needed": [],
            "key_facts": [],
            "forbidden_topics": [],
            "cross_refs": []
        }]
    ), expect_pass=True)

    # ── INVALID cases ──
    bad_format = make_plan(issue_meta={**make_plan()["issue_meta"], "format": "weekly_special"})
    run_test("invalid format vocab", bad_format, expect_pass=False)

    bad_mode = make_plan(issue_meta={**make_plan()["issue_meta"], "execution_mode": "sequential"})
    run_test("execution_mode mismatch (countdown should be parallel)", bad_mode, expect_pass=False)

    bad_gap = make_plan(chapters=[
        {**make_plan()["chapters"][0]},
        {**make_plan()["chapters"][0], "chapter_id": "ch-three", "chapter_num": 3}
    ])
    run_test("chapter_num gap (1,3 not 1,2)", bad_gap, expect_pass=False)

    dup_id = make_plan(chapters=[
        {**make_plan()["chapters"][0]},
        {**make_plan()["chapters"][0], "chapter_num": 2}
    ])
    run_test("duplicate chapter_id", dup_id, expect_pass=False)

    bad_cross_parallel = make_plan(chapters=[{**make_plan()["chapters"][0], "cross_refs": ["by-the-numbers"]}])
    run_test("cross_refs non-empty in parallel format", bad_cross_parallel, expect_pass=False)

    bad_ref = make_plan(
        issue_meta={"format": "deep_dive", "date": "2026-06-15", "topic": "x", "special_id": "x", "execution_mode": "sequential"},
        chapters=[{
            "chapter_id": "intro", "chapter_num": 1, "chapter_type": "literary",
            "chapter_title": "Intro", "chapter_arc": "arc", "ground": "paper",
            "is_hype": False, "data_venue": None, "target_word_count": 500,
            "images_needed": [], "key_facts": [], "forbidden_topics": [],
            "cross_refs": ["nonexistent-chapter"]
        }]
    )
    run_test("cross_ref to nonexistent chapter_id", bad_ref, expect_pass=False)

    bad_ground = make_plan(chapters=[{**make_plan()["chapters"][0], "ground": "ocean"}])
    run_test("invalid ground vocab", bad_ground, expect_pass=False)

    bad_hype_literary = make_plan(
        issue_meta={"format": "deep_dive", "date": "2026-06-15", "topic": "x", "special_id": "x", "execution_mode": "sequential"},
        chapters=[{**make_plan()["chapters"][0], "chapter_num": 1, "is_hype": True}]
    )
    run_test("is_hype=true on literary format (deep_dive)", bad_hype_literary, expect_pass=False)

    no_accent = make_plan(compliance={**make_plan()["compliance"], "accent_lockdown": False})
    run_test("accent_lockdown=false (banned)", no_accent, expect_pass=False)

    bad_date = make_plan(issue_meta={**make_plan()["issue_meta"], "date": "15-06-2026"})
    run_test("invalid date format", bad_date, expect_pass=False)

    # ── v8.15 Lead + Companion + Long Shelf cases ──

    def weekly_fixed_chapter(chapter_id, pieces=None, items=None, extra=None):
        ch = {
            "chapter_id": chapter_id,
            "chapter_num": 1,
            "chapter_type": "opener",
            "chapter_title": chapter_id,
            "chapter_arc": "arc",
            "ground": "paper",
            "is_hype": False,
            "data_venue": None,
            "target_word_count": 800,
            "images_needed": [],
            "key_facts": [],
            "forbidden_topics": [],
            "cross_refs": []
        }
        if pieces is not None: ch["pieces"] = pieces
        if items is not None: ch["items"] = items
        if extra: ch.update(extra)
        return ch

    weekly_meta = {"format": "weekly", "date": "2026-06-15", "topic": "weekly", "special_id": None, "execution_mode": "parallel"}

    valid_pieces = [
        {"role": "lead", "topic_family": "us_politics", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": ["https://example.com"]},
        {"role": "companion", "topic_family": "climate_environment", "word_count_target": {"min": 250, "max": 450}, "headline_hint": "y", "link_targets": ["https://example.com"]}
    ]

    valid_long_shelf_items = [
        {"title": f"Item {i}", "source": "Src", "link": "https://example.com", "hook": "Hook.", "wildcard": (i >= 7)}
        for i in range(1, 9)
    ]

    # PASS: valid weekly with world chapter and long_shelf
    run_test("valid weekly with Lead + Companion world + long_shelf wildcards", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("world", pieces=valid_pieces),
            weekly_fixed_chapter("long_shelf", items=valid_long_shelf_items, extra={"chapter_num": 2})
        ]
    ), expect_pass=True)

    # PASS (v8.37): a round with no pieces is now fine — the considered-piece backbone is retired;
    # the round silently yields / carries plain news. No Lead-or-yield_reason hard-fail any more.
    run_test("weekly round with no pieces (v8.37 — no backbone required)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world")]
    ), expect_pass=True)

    # FAIL: Lead and Companion share topic_family
    same_family_pieces = [
        {"role": "lead", "topic_family": "iran_war", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": []},
        {"role": "companion", "topic_family": "iran_war", "word_count_target": {"min": 250, "max": 450}, "headline_hint": "y", "link_targets": []}
    ]
    run_test("pieces share topic_family", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=same_family_pieces)]
    ), expect_pass=False)

    # FAIL: topic_family not in enumeration
    bad_family_pieces = [
        {"role": "lead", "topic_family": "made_up_family", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": []},
        {"role": "companion", "topic_family": "climate_environment", "word_count_target": {"min": 250, "max": 450}, "headline_hint": "y", "link_targets": []}
    ]
    run_test("topic_family not in enumeration", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=bad_family_pieces)]
    ), expect_pass=False)

    # FAIL: Companion word_count_target.min below 200
    low_companion_pieces = [
        {"role": "lead", "topic_family": "us_politics", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": []},
        {"role": "companion", "topic_family": "climate_environment", "word_count_target": {"min": 100, "max": 200}, "headline_hint": "y", "link_targets": []}
    ]
    run_test("companion word_count floor below 200", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=low_companion_pieces)]
    ), expect_pass=False)

    # FAIL: long_shelf with fewer than 2 wildcards
    no_wildcard_items = [
        {"title": f"Item {i}", "source": "Src", "link": "https://example.com", "hook": "Hook.", "wildcard": False}
        for i in range(1, 9)
    ]
    run_test("long_shelf with <2 wildcards", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("long_shelf", items=no_wildcard_items)]
    ), expect_pass=False)

    # FAIL: long_shelf with too few items
    short_items = [
        {"title": f"Item {i}", "source": "Src", "link": "https://example.com", "hook": "Hook.", "wildcard": (i >= 4)}
        for i in range(1, 6)
    ]
    run_test("long_shelf with only 5 items", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("long_shelf", items=short_items)]
    ), expect_pass=False)

    # PASS: non-weekly formats are not bound by the Lead+Companion rule
    run_test("countdown chapter without pieces (not bound by Lead+Companion)",
             make_plan(), expect_pass=True)

    # ── v8.27 / v8.34 considered-piece backbone shape cases ──

    lead_only = [
        {"role": "lead", "topic_family": "us_politics", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": ["https://example.com"]}
    ]
    good_catch_up = [
        {"headline_hint": "Transfer confirmed", "why_it_matters": "Reshapes the title race", "link_targets": ["https://example.com"]},
        {"headline_hint": "Squad announced", "why_it_matters": "First call-up for X", "link_targets": ["https://example.com"]}
    ]

    # PASS (v8.34): a bare considered piece (Lead) is the backbone — Catch-Up is optional
    run_test("bare lead (considered piece) passes (v8.34)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=lead_only)]
    ), expect_pass=True)

    # PASS: Lead + non-namedrop Catch-Up (companion optional, omitted)
    run_test("lead + substantive catch_up passes (no companion)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=lead_only, extra={"catch_up": good_catch_up})]
    ), expect_pass=True)

    # PASS: Lead + yield_reason (section runs short)
    run_test("lead + yield_reason passes (section yields)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("toolkit", pieces=lead_only, extra={"yield_reason": "thin tech week"})]
    ), expect_pass=True)

    # FAIL: Catch-Up item is a bare namedrop (missing why_it_matters)
    namedrop_catch_up = [
        {"headline_hint": "New game out", "why_it_matters": "", "link_targets": ["https://example.com"]}
    ]
    run_test("catch_up bare namedrop (no why) fails", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("pixel_byte", pieces=lead_only, extra={"catch_up": namedrop_catch_up})]
    ), expect_pass=False)

    # FAIL: Catch-Up item missing link
    nolink_catch_up = [
        {"headline_hint": "New game out", "why_it_matters": "Sequel to a cult hit", "link_targets": []}
    ]
    run_test("catch_up item without link fails", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("pixel_byte", pieces=lead_only, extra={"catch_up": nolink_catch_up})]
    ), expect_pass=False)

    # PASS: The Toolkit is now a fixed section running Lead + Catch-Up
    run_test("toolkit fixed section with lead + catch_up passes", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("toolkit", pieces=lead_only, extra={"catch_up": good_catch_up})]
    ), expect_pass=True)

    # v8.37 (W-3): a round with ONLY a Catch-Up (no Lead, no yield_reason) now PASSES — the
    # considered-piece backbone is retired; the single Long Read carries the deep work, so a round
    # that just carries plain news is fine. (Under v8.34 this was a hard fail.)
    pure_catchup_ch = weekly_fixed_chapter("pixel_byte", extra={"catch_up": good_catch_up})
    pure_catchup_ch.pop("pieces", None)
    run_test("pure catch_up round with no lead passes (v8.37 — no backbone required)", make_plan(
        issue_meta=weekly_meta,
        chapters=[pure_catchup_ch]
    ), expect_pass=True)

    # v8.34: a section with only Catch-Up but an explicit yield_reason passes (it is yielding)
    yielded_catchup_ch = weekly_fixed_chapter("pixel_byte", extra={"catch_up": good_catch_up, "yield_reason": "thin gaming week"})
    yielded_catchup_ch.pop("pieces", None)
    run_test("catch_up-only section with yield_reason passes (v8.34)", make_plan(
        issue_meta=weekly_meta,
        chapters=[yielded_catchup_ch]
    ), expect_pass=True)

    # v8.28: a Companion with no Lead fails
    companion_only = [
        {"role": "companion", "topic_family": "f1", "word_count_target": {"min": 200, "max": 400}, "headline_hint": "x", "link_targets": ["https://example.com"]}
    ]
    run_test("companion without a lead fails (v8.28)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("touchline", pieces=companion_only, extra={"catch_up": good_catch_up})]
    ), expect_pass=False)

    # v8.28: a tight 150-word lead passes (floor relaxed from 300)
    tight_lead = [
        {"role": "lead", "topic_family": "us_politics", "word_count_target": {"min": 150, "max": 250}, "headline_hint": "x", "link_targets": ["https://example.com"]}
    ]
    run_test("tight 150-word lead passes (v8.28 floor relaxed)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=tight_lead, extra={"catch_up": good_catch_up})]
    ), expect_pass=True)

    # ── v8.17 sub-format cases ──

    dc_lead = [
        {"role": "lead", "topic_family": "star_wars", "word_count_target": {"min": 600, "max": 750}, "headline_hint": "Maul retrospective", "link_targets": ["https://example.com"]},
        {"role": "companion", "topic_family": "audio_dramas", "word_count_target": {"min": 250, "max": 450}, "headline_hint": "BBC drama pick", "link_targets": ["https://example.com"]}
    ]

    # PASS: valid Director's Cut on screen_sound with Lead >= 550
    run_test("valid directors_cut on screen_sound", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("screen_sound", pieces=dc_lead, extra={"sub_format": "directors_cut"}),
        ]
    ), expect_pass=True)

    # FAIL: directors_cut with Lead word floor below 550
    dc_lead_low = [
        {"role": "lead", "topic_family": "star_wars", "word_count_target": {"min": 400, "max": 700}, "headline_hint": "x", "link_targets": ["https://example.com"]},
        {"role": "companion", "topic_family": "audio_dramas", "word_count_target": {"min": 250, "max": 450}, "headline_hint": "y", "link_targets": ["https://example.com"]}
    ]
    run_test("directors_cut Lead word floor below 550", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("screen_sound", pieces=dc_lead_low, extra={"sub_format": "directors_cut"}),
        ]
    ), expect_pass=False)

    # FAIL: directors_cut on a non-screen_sound chapter
    run_test("directors_cut on wrong chapter (world)", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("world", pieces=valid_pieces, extra={"sub_format": "directors_cut"}),
        ]
    ), expect_pass=False)

    # FAIL: invalid sub_format value
    run_test("invalid sub_format value", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("screen_sound", pieces=dc_lead, extra={"sub_format": "bogus_mode"}),
        ]
    ), expect_pass=False)

    # PASS: valid A Closer Look on history with featured_item >= 600
    closer_look_chapter = weekly_fixed_chapter("history", extra={
        "sub_format": "closer_look",
        "featured_item": {
            "topic_family": "books_history",
            "word_count_target": {"min": 600, "max": 800},
            "headline_hint": "The Anglo-Zanzibar War",
            "link_targets": ["https://en.wikipedia.org/wiki/Anglo-Zanzibar_War"]
        }
    })
    run_test("valid closer_look on history", make_plan(
        issue_meta=weekly_meta,
        chapters=[closer_look_chapter]
    ), expect_pass=True)

    # FAIL: closer_look featured_item below 600 floor
    closer_look_low = weekly_fixed_chapter("history", extra={
        "sub_format": "closer_look",
        "featured_item": {
            "topic_family": "books_history",
            "word_count_target": {"min": 400, "max": 600},
            "headline_hint": "x",
            "link_targets": ["https://en.wikipedia.org/wiki/Test"]
        }
    })
    run_test("closer_look featured_item below 600", make_plan(
        issue_meta=weekly_meta,
        chapters=[closer_look_low]
    ), expect_pass=False)

    # FAIL: closer_look with also_items present (forbidden)
    closer_look_with_items = weekly_fixed_chapter("history", extra={
        "sub_format": "closer_look",
        "featured_item": {
            "topic_family": "books_history",
            "word_count_target": {"min": 600, "max": 800},
            "headline_hint": "ok",
            "link_targets": ["https://en.wikipedia.org/wiki/Test"]
        },
        "also_items": [{"title": "x", "link": "https://example.com"}]
    })
    run_test("closer_look forbids also_items", make_plan(
        issue_meta=weekly_meta,
        chapters=[closer_look_with_items]
    ), expect_pass=False)

    # FAIL: closer_look on wrong chapter
    run_test("closer_look on wrong chapter (screen_sound)", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("screen_sound", pieces=dc_lead, extra={
                "sub_format": "closer_look",
                "featured_item": {
                    "topic_family": "books_history",
                    "word_count_target": {"min": 600, "max": 800},
                    "headline_hint": "x",
                    "link_targets": ["https://en.wikipedia.org/wiki/Test"]
                }
            }),
        ]
    ), expect_pass=False)

    # FAIL: featured_item present but sub_format is null
    orphan_featured = weekly_fixed_chapter("history", extra={
        "featured_item": {
            "topic_family": "books_history",
            "word_count_target": {"min": 600, "max": 800},
            "headline_hint": "x",
            "link_targets": ["https://en.wikipedia.org/wiki/Test"]
        }
    })
    run_test("featured_item without closer_look sub_format", make_plan(
        issue_meta=weekly_meta,
        chapters=[orphan_featured]
    ), expect_pass=False)

    # ── v8.19 discovery_picks cases ──

    # FAIL: weekly with discovery_picks missing
    run_test("weekly missing discovery_picks", make_plan(
        issue_meta=weekly_meta,
        chapters=[
            weekly_fixed_chapter("world", pieces=valid_pieces)
        ],
        discovery_picks=None
    ), expect_pass=False)

    # FAIL: weekly with only 2 discovery_picks (below floor of 3)
    run_test("weekly with 2 discovery_picks (below floor)", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=valid_pieces)],
        discovery_picks=[
            {"chapter_id": "long_shelf", "headline_hint": "x", "discovery_rationale": "y"},
            {"chapter_id": "long_shelf", "headline_hint": "x2", "discovery_rationale": "y2"}
        ]
    ), expect_pass=False)

    # PASS: discovery_picks rule does not fire on specials (countdown)
    run_test("discovery_picks rule skipped on countdown", make_plan(
        discovery_picks=None
    ), expect_pass=True)

    # FAIL: discovery_picks entry missing required fields
    run_test("discovery_picks entry missing rationale", make_plan(
        issue_meta=weekly_meta,
        chapters=[weekly_fixed_chapter("world", pieces=valid_pieces)],
        discovery_picks=[
            {"chapter_id": "long_shelf", "headline_hint": "x", "discovery_rationale": ""},
            {"chapter_id": "long_shelf", "headline_hint": "x2", "discovery_rationale": "ok"},
            {"chapter_id": "screen_sound", "headline_hint": "x3", "discovery_rationale": "ok"}
        ]
    ), expect_pass=False)

    # ── v8.29 structured key_facts ──
    def kf_chapter(key_facts):
        return {
            "chapter_id": "by-the-numbers", "chapter_num": 1, "chapter_type": "opener",
            "chapter_title": "By the Numbers", "chapter_arc": "The shape of the trip",
            "ground": "ink", "is_hype": True, "data_venue": None, "target_word_count": 400,
            "images_needed": [{"role": "hero", "source_constraint": "Wikimedia", "alt_required": True}],
            "key_facts": key_facts, "forbidden_topics": [], "cross_refs": []
        }

    run_test("structured key_fact (valid) passes", make_plan(chapters=[kf_chapter([
        {"claim": "State of Play airs", "status": "upcoming", "date": "2026-06-05", "source_url": "https://blog.playstation.com/x"}
    ])]), expect_pass=True)

    run_test("bare-string key_fact still passes (back-compat)", make_plan(chapters=[kf_chapter([
        "Efteling founded 1952"
    ])]), expect_pass=True)

    run_test("structured key_fact missing source_url fails", make_plan(chapters=[kf_chapter([
        {"claim": "Juve beat Inter 2-1", "status": "happened", "date": "2026-05-30"}
    ])]), expect_pass=False)

    run_test("structured key_fact bad status fails", make_plan(chapters=[kf_chapter([
        {"claim": "x", "status": "maybe", "date": "2026-05-30", "source_url": "https://x.com/y"}
    ])]), expect_pass=False)

    run_test("opinion key_fact without quote fails", make_plan(chapters=[kf_chapter([
        {"claim": "Norris took pole", "status": "happened", "date": "2026-05-24",
         "source_url": "https://formula1.com/x", "type": "opinion", "speaker": "Lando Norris"}
    ])]), expect_pass=False)

    # ── v8.30 release_radar enforcement ──
    rr_world = weekly_fixed_chapter("world", pieces=valid_pieces, extra={"catch_up": good_catch_up, "chapter_num": 1})

    def radar_chapter(items, num=2):
        return {"chapter_id": "release_radar", "chapter_num": num, "chapter_type": "closer",
                "chapter_title": "Release Radar", "chapter_arc": "coming", "ground": "paper",
                "is_hype": False, "data_venue": None, "target_word_count": 300, "images_needed": [],
                "key_facts": [], "forbidden_topics": [], "cross_refs": [], "radar_items": items}

    run_test("weekly missing release_radar fails", make_plan(
        _no_radar=True, issue_meta=weekly_meta, chapters=[dict(rr_world)]
    ), expect_pass=False)

    few_items = [{"title": f"R{i}", "category": ["film", "tv", "game", "book"][i % 4], "date": "2026-06-20",
                  "status": "upcoming", "link": "https://example.com"} for i in range(10)]
    run_test("release_radar <15 items fails", make_plan(
        _no_radar=True, issue_meta=weekly_meta, chapters=[dict(rr_world), radar_chapter(few_items)]
    ), expect_pass=False)

    onecat_items = [{"title": f"R{i}", "category": "film", "date": "2026-06-20",
                     "status": "upcoming", "link": "https://example.com"} for i in range(15)]
    run_test("release_radar <4 categories fails", make_plan(
        _no_radar=True, issue_meta=weekly_meta, chapters=[dict(rr_world), radar_chapter(onecat_items)]
    ), expect_pass=False)

    valid_items = [{"title": f"R{i}", "category": ["film", "tv", "game", "book", "music"][i % 5], "date": "2026-06-20",
                    "status": "upcoming", "link": "https://example.com"} for i in range(16)]
    run_test("valid release_radar passes", make_plan(
        _no_radar=True, issue_meta=weekly_meta, chapters=[dict(rr_world), radar_chapter(valid_items)]
    ), expect_pass=True)

    # ── Summary ──
    print("\n=== INLINE TEST RESULTS ===")
    total = len(test_results)
    passed_count = sum(1 for r in test_results if r[0] == "PASS")
    for status, name, errs in test_results:
        mark = "✓" if status == "PASS" else "✗"
        print(f"  {mark} [{status}] {name}")
        if errs:
            for e in errs:
                print(f"         | {e}")

    print(f"\n{passed_count}/{total} tests passed.")
    if passed_count < total:
        print("PIPELINE TEST: FAIL")
        return False
    else:
        print("PIPELINE TEST: PASS")
        return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_inline_tests()
        sys.exit(0 if success else 1)
    else:
        main()
