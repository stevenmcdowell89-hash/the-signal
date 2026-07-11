#!/usr/bin/env python3
"""Build the archive manifest (JSON) from the issues/ directory.

Sibling to extract-issue-meta.py. The filesystem is the source of truth for
*what issues exist*; this script derives each issue's structure (slug, format,
stream, date, cover, read-time, issue number) automatically, and lifts the
hand-authored card copy (title / summary) from index.html where present so no
curated blurb is lost. The output kills the stale hand-maintained tab counts
and unlocks archive search / grouping / read-state on the home.

Emits archive-manifest.json to the repo root (or --out). JSON to stdout with
--stdout.

  Usage:
    scripts/build-archive-manifest.py                 # writes archive-manifest.json
    scripts/build-archive-manifest.py --stdout        # prints, writes nothing
    scripts/build-archive-manifest.py --out path.json
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ISSUES_DIR = ROOT / "issues"
INDEX_HTML = ROOT / "index.html"

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}

# slug-prefix → (format slug, human label, stream). "weekly" issues are The
# Read (the anchor stream); everything else is a special edition.
FORMAT_RULES = [
    ("signal_weekly_", "weekly", "Standard Weekly", "weekly"),
    ("signal_deep-dive_", "deep-dive", "Deep Dive", "special"),
    ("signal_field-guide_", "field-guide", "Field Guide", "special"),
    ("signal_countdown_", "countdown", "The Countdown", "special"),
    ("signal_season-review_", "season-review", "Season Review", "special"),
    ("signal_rewind_", "rewind", "Rewind", "special"),
    ("signal_lookahead_", "lookahead", "Lookahead", "special"),
    ("signal_next_", "next", "The Next", "special"),
    ("signal_guide_", "guide", "The Guide", "special"),
    ("signal_versus_", "versus", "Versus", "special"),
    ("signal_shortlist_", "shortlist", "Shortlist", "special"),
    ("signal_starterkit_", "starter-kit", "Starter Kit", "special"),
    ("countdown-", "countdown", "The Countdown", "special"),
    ("versus-", "versus", "Versus", "special"),
    ("shortlist-", "shortlist", "Shortlist", "special"),
    ("starterkit-", "starter-kit", "Starter Kit", "special"),
]


def classify(slug):
    for prefix, fmt, label, stream in FORMAT_RULES:
        if slug.startswith(prefix):
            return fmt, label, stream
    # issue-1 / issue-2 and any bare weekly-style slug default to the weekly stream.
    if re.match(r"^issue-\d+$", slug):
        return "weekly", "Standard Weekly", "weekly"
    return "weekly", "Standard Weekly", "weekly"


def parse_iso_from_slug(slug):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", slug)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def parse_date_label(label):
    """Parse an authored card-date like '30 June 2026' or 'March 19-25, 2026'
    into a YYYY-MM-DD sort key. Best-effort; returns None if unparseable."""
    if not label:
        return None
    txt = re.sub(r"·.*$", "", label).strip()  # drop '· Special' suffix
    # '30 June 2026'
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", txt)
    if m and m.group(2).lower() in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    # 'March 19, 2026' / 'March 19-25, 2026'
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2})[^,]*,?\s+(\d{4})", txt)
    if m and m.group(1).lower() in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
    return None


def strip_tags(html):
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def read_time_minutes(html):
    words = len(strip_tags(html).split())
    return max(1, round(words / 200))


def authored_cards():
    """slug → {format_label, title, summary, date_label} lifted from index.html
    card / hero blocks, so curated copy survives into the manifest."""
    out = {}
    if not INDEX_HTML.exists():
        return out
    html = INDEX_HTML.read_text(encoding="utf-8", errors="ignore")
    # Match both .card and .hero-card anchors.
    anchor_re = re.compile(
        r'<a\s+class="(?:hero-)?card"[^>]*href="issues/([^"]+?)\.html"[^>]*>(.*?)</a>',
        re.S)
    field_re = {
        "format": re.compile(r'class="(?:card|hero)-format">(.*?)</div>', re.S),
        "title": re.compile(r'class="(?:card|hero)-title">(.*?)</div>', re.S),
        "summary": re.compile(r'class="(?:card|hero)-summary">(.*?)</div>', re.S),
        "date": re.compile(r'class="card-date">(.*?)</div>', re.S),
    }

    def clean(s):
        return re.sub(r"\s+", " ", strip_tags(s)).strip() if s else ""

    for m in anchor_re.finditer(html):
        slug, body = m.group(1), m.group(2)
        if slug in out:
            continue  # first occurrence (The Read block) wins
        rec = {}
        for k, rx in field_re.items():
            mm = rx.search(body)
            rec[k] = clean(mm.group(1)) if mm else ""
        out[slug] = rec
    return out


def build():
    cards = authored_cards()
    issues = []
    for path in sorted(ISSUES_DIR.glob("*.html")):
        slug = path.stem
        if slug.startswith("TEST-"):
            continue
        fmt, label, stream = classify(slug)
        card = cards.get(slug, {})
        html = path.read_text(encoding="utf-8", errors="ignore")

        # Title: authored card title > <title> (minus masthead prefix) > slug.
        title = card.get("title") or ""
        if not title:
            tm = re.search(r"<title>([^<]+)</title>", html)
            raw = tm.group(1) if tm else slug
            title = re.sub(r"^The Signal\s*[—–-]\s*", "", raw).strip()

        summary = card.get("summary") or ""
        if not summary:
            dm = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.I)
            summary = dm.group(1).strip() if dm else ""

        date = parse_iso_from_slug(slug) or parse_date_label(card.get("date")) or ""
        # A human date label: prefer the authored one, else format the ISO date.
        date_label = card.get("date") or ""
        if not date_label and date:
            try:
                d = datetime.strptime(date, "%Y-%m-%d")
                date_label = d.strftime("%-d %B %Y")
            except ValueError:
                date_label = date

        num = None
        mnum = re.search(r"Issue\s*#(\d+)", card.get("format", ""))
        if mnum:
            num = int(mnum.group(1))

        # Prefer the authored format label (carries "Issue #N · Standard Weekly"
        # or the special's descriptor) over the generic one.
        fmt_label = card.get("format") or label

        issues.append({
            "slug": slug,
            "url": f"issues/{slug}.html",
            "format": fmt,
            "format_label": fmt_label,
            "stream": stream,
            "title": title,
            "summary": summary,
            "date": date,
            "date_label": date_label,
            "issue_number": num,
            "cover": f"assets/covers/{slug}.jpg",
            "read_time": read_time_minutes(html),
        })

    # Newest first: sort by date desc, then issue_number desc as a tiebreak.
    issues.sort(key=lambda x: (x["date"] or "0000-00-00", x["issue_number"] or 0),
                reverse=True)

    weeklies = [i for i in issues if i["stream"] == "weekly"]
    specials = [i for i in issues if i["stream"] == "special"]
    latest_weekly = weeklies[0] if weeklies else None

    return {
        "generated_at": int(datetime.now(timezone.utc).timestamp() * 1000),
        "counts": {
            "weekly": len(weeklies),
            "special": len(specials),
            "total": len(issues),
        },
        "latest_weekly": latest_weekly,
        "issues": issues,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "archive-manifest.json"))
    ap.add_argument("--stdout", action="store_true", help="print JSON, write nothing")
    args = ap.parse_args()

    if not ISSUES_DIR.exists():
        print(f"no issues dir: {ISSUES_DIR}", file=sys.stderr)
        return 1

    manifest = build()
    text = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.stdout:
        print(text)
    else:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        c = manifest["counts"]
        print(f"wrote {args.out}: {c['total']} issues "
              f"({c['weekly']} weekly, {c['special']} special)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
