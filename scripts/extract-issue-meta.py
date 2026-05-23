#!/usr/bin/env python3
"""Extract a notification payload from an issue HTML file. JSON to stdout.

Used by .github/workflows/notify-on-publish.yml — produces the body for the
POST /api/notify call.
"""
import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract-issue-meta.py <path/to/issue.html>", file=sys.stderr)
        return 2

    issue_path = Path(sys.argv[1])
    if not issue_path.exists():
        print(f"not found: {issue_path}", file=sys.stderr)
        return 1

    slug = issue_path.stem
    html = issue_path.read_text(encoding="utf-8", errors="ignore")

    title_match = re.search(r"<title>([^<]+)</title>", html)
    raw_title = title_match.group(1) if title_match else f"The Signal — {slug}"
    # Strip "The Signal — " masthead prefix if present; we add our own.
    title = re.sub(r"^The Signal\s*[—–-]\s*", "", raw_title).strip()

    desc_match = re.search(
        r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE
    )
    body = (desc_match.group(1) if desc_match else "A new issue is live.").strip()
    if len(body) > 200:
        body = body[:197] + "..."

    payload = {
        "title": f"The Signal — {title}",
        "body": body,
        "url": "/" + issue_path.as_posix(),
        "image": f"/assets/covers/{slug}.jpg",
        "slug": slug,
    }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
