#!/usr/bin/env python3
"""
validate-chapter-plan.py — Mandatory gate between Phase 4 (Planner) and Phase 5 (Writers).

Usage:
    python scripts/validate-chapter-plan.py [path-to-plan.json]

Default path: /tmp/signal-build/chapter-plan.json

Exits 0 on PASS. Exits 1 on any failure (prints all errors before exiting).

v8.11.0
"""

import json
import re
import sys
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

KEBAB_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
DATE_RE  = re.compile(r'^\d{4}-\d{2}-\d{2}$')

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

def main():
    plan_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PLAN_PATH
    plan_path = Path(plan_path)

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
            }
        }
        for k, v in overrides.items():
            plan[k] = v
        return plan

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
