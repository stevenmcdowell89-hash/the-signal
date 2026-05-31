#!/usr/bin/env python3
"""check-theme-clustering.py — Gate against single-theme over-domination (v8.26).

The fixed/rotating section split keeps the section *count* right (3-4 rotating),
but nothing stopped one TOPIC THEME owning several sections at once. Issue #11
(31 May 2026) ran The Session + The Workshop + The Toolkit + the Pixel & Byte
lead all on wearables/recovery (Garmin x19, HRV x12, recovery x14) — it read as
a wearables special, not a varied weekly.

This gate scans each weekly section's heading + opening prose, scores it against
a set of theme clusters by keyword density, and fails if any single cluster owns
>= MAX_SECTIONS distinct sections (default 3). It is weekly-only.

Usage:
  python3 check-theme-clustering.py <stitched-weekly-html> [--max N] [--warn-only]
"""
import sys, re
from collections import defaultdict

# Theme clusters → trigger keywords (lowercased, word-ish). A section "belongs"
# to a cluster if >=2 distinct keywords from it appear in the section's
# heading+opening text. Sections can belong to more than one cluster.
CLUSTERS = {
    "wearables/recovery": [
        "garmin", "whoop", "oura", "fitbit", "wearable", "hrv",
        "heart-rate variability", "heart rate variability", "resting heart",
        "readiness", "recovery score", "body battery", "training readiness",
        "smart band", "cirqa", "strain", "sleep score", "vo2",
    ],
    "fitness/training": [
        "hypertrophy", "kettlebell", "deadlift", "squat", "running", "10k",
        "race pace", "training block", "mobility", "ibex", "lyss", "reps",
        "sets", "progressive overload", "zone 2", "marathon", "lifting",
    ],
    "football": [
        "premier league", "serie a", "juventus", "arsenal", "champions league",
        "psg", "scudetto", "inter milan", "matchday", "relegation", "fixture",
        "goalscorer", "transfer", "uefa",
    ],
    "star wars": [
        "star wars", "mandalorian", "grogu", "jedi", "sith", "skywalker",
        "andor", "ahsoka", "din djarin", "lucasfilm",
    ],
    "nintendo/switch": [
        "nintendo", "switch 2", "mario", "zelda", "joy-con", "amiibo",
    ],
    "uk politics": [
        "starmer", "westminster", "labour", "reform uk", "by-election",
        "downing street", "cabinet", "tory", "conservative", "snp",
    ],
    "ai": [
        "chatgpt", "gemini", "llm", "openai", "anthropic", "claude",
        "generative ai", "copilot", "model release",
    ],
    "personal finance": [
        "isa", "pension", "monzo", "revolut", "starling", "savings rate",
        "interest rate", "mortgage", "investing", "fintech",
    ],
}

# Section markers (weekly): label text → canonical section name.
# v8.27 roster: fixed (World, Pixel & Byte, The Toolkit, Touchline, Screen & Sound,
# Session) + rotating (Shelf, This Week in History, Listening, Money, Places) +
# trigger-driven (The Saga). Legacy labels kept so the gate still parses archived
# issues generated under the old roster.
SECTION_LABELS = [
    "The World This Week", "Pixel & Byte", "Pixel &amp; Byte", "The Toolkit",
    "The Touchline", "Screen & Sound", "Screen &amp; Sound", "The Session",
    "The Long Shelf", "On the Radar", "The Shelf", "This Week in History",
    "Listening", "Money", "Places", "The Saga", "Down the Rabbit Hole",
    # legacy labels (pre-v8.27 archived issues)
    "The Listen", "The Workshop", "The Ledger", "The Long Game", "The Wallet",
    "The Itinerary", "The Local", "The Brickyard", "The Lab", "The Channel",
]


def canon(name):
    return re.sub(r'\s+', ' ', name.replace('&amp;', '&')).strip()


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not paths:
        print("usage: check-theme-clustering.py <html> [--max N] [--warn-only]")
        sys.exit(2)
    html = open(paths[0], encoding='utf-8').read()
    mx = 3
    for i, a in enumerate(sys.argv):
        if a == '--max' and i + 1 < len(sys.argv):
            try: mx = int(sys.argv[i + 1])
            except Exception: pass
        elif a.startswith('--max='):
            try: mx = int(a.split('=', 1)[1])
            except Exception: pass
    warn_only = '--warn-only' in sys.argv

    body = re.sub(r'<style.*?</style>|<script.*?</script>', ' ', html, flags=re.S | re.I)

    # Skip the NAVIGATOR — it lists every section's teaser, so keywords from the
    # World lead bleed into every "section" and produce false clusters. The nav
    # is the run of .nav-card elements near the top; real section bodies start
    # after the last nav-card.
    nav_hits = [m.end() for m in re.finditer(r'nav-card', body)]
    scan_from = (max(nav_hits) if nav_hits else 0)
    body_main = body[scan_from:]

    # Each section's real body = from its label to the next section label.
    marks = []
    for lbl in SECTION_LABELS:
        m = re.search(re.escape(lbl), body_main)
        if m:
            marks.append((m.start(), canon(lbl)))
    marks.sort()
    sections = []
    for i, (pos, name) in enumerate(marks):
        # Scan ONLY up to the next section boundary (never past it — that bleed
        # was producing false clusters), and never more than 2600 chars.
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(body_main)
        end = min(nxt, pos + 2600)
        # Down the Rabbit Hole is a sidebar, not a full section — skip it.
        if name == "Down the Rabbit Hole":
            continue
        text = re.sub(r'<[^>]+>', ' ', body_main[pos:end]).lower()
        text = re.sub(r'\s+', ' ', text)
        sections.append((name, text))

    # Score each section against clusters.
    cluster_sections = defaultdict(set)
    for name, text in sections:
        for cl, kws in CLUSTERS.items():
            hits = sum(1 for kw in kws if kw in text)
            if hits >= 2:
                cluster_sections[cl].add(name)

    # Rotating/discretionary sections — the ones the planner CHOOSES. A theme
    # spanning the fixed news flow (World lead + On the Radar naming the same
    # ongoing story) is not the failure; the failure is discretionary sections
    # piling onto one theme. A cluster fails only if it owns >= mx sections AND
    # at least 2 of them are discretionary.
    ROTATING = {
        "The Shelf", "The Listen", "This Week in History", "The Workshop",
        "The Toolkit", "The Ledger", "The Long Game", "The Wallet",
        "The Itinerary", "The Local", "The Brickyard", "The Saga", "The Lab",
        "The Channel",
    }

    print("=== check-theme-clustering.py ===")
    print(f"Sections scanned: {len(sections)}   threshold: a theme in >= {mx} sections (>=2 rotating) fails")
    any_cluster = False
    for cl, secs in sorted(cluster_sections.items(), key=lambda kv: -len(kv[1])):
        if len(secs) >= 2:
            any_cluster = True
            rot = len(secs & ROTATING)
            print(f"  {cl}: {len(secs)} sections ({rot} rotating) — {', '.join(sorted(secs))}")
    if not any_cluster:
        print("  (no theme spans 2+ sections)")

    violations = {cl: secs for cl, secs in cluster_sections.items()
                  if len(secs) >= mx and len(secs & ROTATING) >= 2}
    if not violations:
        print("PASS — no single theme dominates the issue.")
        sys.exit(0)

    print("\nTHEME-CLUSTERING VIOLATIONS:")
    for cl, secs in sorted(violations.items(), key=lambda kv: -len(kv[1])):
        print(f"  '{cl}' owns {len(secs)} sections: {', '.join(sorted(secs))}")
    print("\nRe-angle or swap a rotating section so no theme owns 3+ sections.")
    print("The reader wants a varied Sunday read, not a single-topic special.")
    sys.exit(0 if warn_only else 1)


if __name__ == "__main__":
    main()
