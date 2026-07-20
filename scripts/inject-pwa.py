#!/usr/bin/env python3
"""
Inject PWA hooks (manifest link, theme-color, icons, service-worker
registration) into HTML files. Idempotent — running twice on the same file
is a no-op.

Usage:
    python3 scripts/inject-pwa.py                    # all HTML in repo
    python3 scripts/inject-pwa.py path/to/file.html  # specific files
"""

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MARKER = "<!-- the-signal:pwa -->"

SNIPPET = f"""{MARKER}
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#E94560">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png">
<script>
  if ('serviceWorker' in navigator) {{
    window.addEventListener('load', function () {{
      navigator.serviceWorker.register('/sw.js').catch(function (err) {{
        console.warn('SW registration failed:', err);
      }});
    }});
  }}
</script>
<!-- /the-signal:pwa -->"""


def inject(html_path: Path) -> bool:
    """Add the snippet just before </head>. Returns True if modified."""
    content = html_path.read_text(encoding="utf-8")
    if MARKER in content:
        return False
    if "</head>" not in content:
        print(f"  ! {html_path.relative_to(REPO_ROOT)}: no </head> found, skipping")
        return False
    new_content = content.replace("</head>", SNIPPET + "\n</head>", 1)
    html_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="HTML files (default: index, issues, template)")
    args = ap.parse_args()

    if args.files:
        targets = [Path(f).resolve() for f in args.files]
    else:
        targets = [REPO_ROOT / "index.html"]
        targets += sorted((REPO_ROOT / "issues").glob("*.html"))
        template = REPO_ROOT / "assets" / "weekly-template.html"
        if template.exists():
            targets.append(template)
        # Also pick up the skill template if it exists
        for tpl in REPO_ROOT.glob(".claude/skills/the-signal/**/weekly-template.html"):
            targets.append(tpl)

    def rel(path: Path) -> str:
        # WP-6 mx-compat: targets may live outside the repo (fixture dry-runs);
        # relative_to raises there — fall back to the absolute path.
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return str(path)

    modified = 0
    for path in targets:
        if inject(path):
            modified += 1
            print(f"  + {rel(path)}")
        else:
            print(f"  = {rel(path)} (already has snippet)")

    print(f"\nDone. {modified}/{len(targets)} files modified.")


if __name__ == "__main__":
    main()
