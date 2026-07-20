#!/usr/bin/env python3
"""check-rendered-metrics.py — parse tools/measure-issue.mjs output and
hard-fail on Law violations (WP-6 publish-gate wiring of the WP-0 rendered
gates). Runs inside publish-gate.sh for data-mx issues only.

Checks, per viewport (1440x900 and 390x844):
  - Law 2 density floor  : events.perScreen >= the format's floor
  - Law 2 words/screen   : words.perScreen <= the format's cap
  - Law 2 distribution   : no run of 3+ consecutive zero-event screens
  - Law 3 word floor     : words.bodyCopy >= the format's floor (F-18 backstop;
                           measured body copy excludes chrome + captions)
  - Law 10 craft flags   : chrome-overlap pairs == 0 · no reader-experienced
                           document H-scroll · no table-truncation flags
  - Law 5 motion census  : tier1/tier2 pages must show >= 1 element actually
                           animating during the scroll pass; reduced-motion
                           pass must show 0 animating elements at EVERY tier.

The numbers come from metrics.json — measured, never asserted (Part 6 §2).
Usage:
  check-rendered-metrics.py METRICS.json --format FMT --html ISSUE.html
Exit 0 = all green · 1 = violation(s) · 2 = usage/input error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Law 2 density floors (spec Part 1, Law 2 table; format slugs hyphenated).
DENSITY_FLOORS = {
    "weekly": 0.8,
    "deep-dive": 0.7,
    "rewind": 0.9,
    "season-review": 0.9,
    "versus": 0.8,
    "guide": 0.8,
    "shortlist": 0.8,
    "starter-kit": 0.8,
    "next": 0.8,
    "countdown": 1.0,
    "field-guide": 1.0,
}

# Law 2 words-per-screen caps.
WORDS_PER_SCREEN_CAPS = {"deep-dive": 220}
WORDS_PER_SCREEN_DEFAULT_CAP = 210

# Law 3 body-copy floors (mirrors validate-issue.py LAW3_WORD_FLOORS; the
# measured bodyCopy count is chrome/caption-free, so this is the strict form).
LAW3_FLOORS = {
    "weekly": 6000, "deep-dive": 8000, "season-review": 6500, "rewind": 7000,
    "versus": 4500, "guide": 3500, "shortlist": 3500, "starter-kit": 3500,
    "next": 3000, "countdown": 4500, "field-guide": 6000,
}


def motion_tier_of(html_path):
    """Read data-motion off the real <body> tag (after </head>)."""
    try:
        html = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    head_end = re.search(r"</head\s*>", html, re.I)
    if not head_end:
        return None
    m = re.search(r"<body\b[^>]*>", html[head_end.end():], re.I)
    if not m:
        return None
    t = re.search(r'data-motion="(tier[012])"', m.group(0))
    return t.group(1) if t else None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("metrics")
    ap.add_argument("--format", required=True)
    ap.add_argument("--html", default="", help="stitched issue (to read data-motion tier)")
    args = ap.parse_args(argv)

    fmt = args.format.lower().replace("_", "-")
    try:
        metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read metrics: {e}")
        return 2

    floor = DENSITY_FLOORS.get(fmt)
    wps_cap = WORDS_PER_SCREEN_CAPS.get(fmt, WORDS_PER_SCREEN_DEFAULT_CAP)
    law3 = LAW3_FLOORS.get(fmt)
    tier = motion_tier_of(args.html) if args.html else None

    fails, oks = [], []
    viewports = metrics.get("viewports", {})
    reduced = metrics.get("reducedMotion", {})
    if not viewports:
        print("ERROR: metrics.json has no viewports block")
        return 2

    for key, m in viewports.items():
        evps = m.get("events", {}).get("perScreen", 0)
        wps = m.get("words", {}).get("perScreen", 0)
        words = m.get("words", {}).get("bodyCopy", 0)
        dist = m.get("distribution", {})
        run = dist.get("longestZeroEventRun", 0)
        overlap = m.get("chromeOverlap", {}).get("uniquePairs", 0)
        hscroll = m.get("horizontalScroll", {}).get("flag", False)
        trunc = m.get("tableTruncation", {}).get("flags", [])
        anim = m.get("motion", {}).get("animatedElements", 0)
        r_anim = reduced.get(key, {}).get("animatedElements", 0)

        # Law 2 density floor
        if floor is not None:
            if evps < floor:
                fails.append(f"[{key}] LAW-2 DENSITY: {evps} ev/screen < {fmt} floor {floor}")
            else:
                oks.append(f"[{key}] density {evps} ev/screen >= floor {floor}")
        # Law 2 words/screen cap
        if wps > wps_cap:
            fails.append(f"[{key}] LAW-2 WORDS/SCREEN: {wps} > {fmt} cap {wps_cap}")
        else:
            oks.append(f"[{key}] words/screen {wps} <= cap {wps_cap}")
        # Law 2 distribution
        if dist.get("law2DistributionFail") or run >= 3:
            fails.append(f"[{key}] LAW-2 DISTRIBUTION: longest zero-event run {run} screens (>= 3)")
        else:
            oks.append(f"[{key}] longest zero-event run {run} screens")
        # Law 3 measured body copy (F-18 backstop)
        if law3 is not None:
            if words < law3:
                fails.append(f"[{key}] LAW-3 WORDS: {words:,} measured body-copy words < "
                             f"{fmt} floor {law3:,} (F-18: the 542-word stub)")
            else:
                oks.append(f"[{key}] body copy {words:,} words >= floor {law3:,}")
        # Law 10 craft flags
        if overlap:
            fails.append(f"[{key}] LAW-10 CHROME OVERLAP: {overlap} fixed-chrome/content "
                         f"pair(s) across scroll depths (attempt-#2's pill failure)")
        else:
            oks.append(f"[{key}] chrome overlap pairs 0")
        if hscroll:
            fails.append(f"[{key}] LAW-10 H-SCROLL: reader-experienced document horizontal scroll")
        else:
            oks.append(f"[{key}] no document h-scroll")
        if trunc:
            kinds = ", ".join(sorted({str(t.get('kind', t)) for t in trunc})[:4]) \
                if isinstance(trunc, list) else str(trunc)
            fails.append(f"[{key}] LAW-10 TABLE TRUNCATION: {len(trunc)} flag(s) ({kinds})")
        else:
            oks.append(f"[{key}] no table-truncation flags")
        # Law 5 motion census
        if tier in ("tier1", "tier2"):
            if anim < 1:
                fails.append(f"[{key}] LAW-5 MOTION: {tier} page but 0 elements animated "
                             f"during the scroll pass (attempt-#2 shipped zero motion)")
            else:
                oks.append(f"[{key}] motion census {anim} animated element(s) ({tier})")
        elif tier == "tier0":
            oks.append(f"[{key}] tier0 print-still — motion census {anim} (no minimum)")
        else:
            fails.append(f"[{key}] LAW-5 MOTION: could not read data-motion tier off the "
                         f"issue <body> — a data-mx issue must declare its tier")
        # reduced-motion must be silent at every tier
        if r_anim:
            fails.append(f"[{key}] LAW-5 REDUCED-MOTION: {r_anim} element(s) still animate "
                         f"under prefers-reduced-motion (must be 0)")
        else:
            oks.append(f"[{key}] reduced-motion census 0")

    print(f"=== rendered-metrics gate: format={fmt} tier={tier or '?'} "
          f"(floors: density {floor}, words/screen cap {wps_cap}, Law-3 {law3}) ===")
    for line in oks:
        print(f"  ok   {line}")
    for line in fails:
        print(f"  FAIL {line}")
    if fails:
        print(f"\nRENDERED GATES RED — {len(fails)} violation(s). Measured, not asserted "
              f"(metrics: {args.metrics}).")
        return 1
    print(f"\nRENDERED GATES GREEN — all checks passed at both viewports.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
