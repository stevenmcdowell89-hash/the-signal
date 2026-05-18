#!/usr/bin/env python3
"""
Inject a reading-progress tracker into each issue HTML.

The tracker writes the user's scroll position to localStorage every few
seconds so the archive's "Continue reading" card can surface where they
left off. Idempotent: re-running on the same file is a no-op.

localStorage shape:
    key:   signal-progress-<slug>
    value: { slug, title, pct (0-100), ts (epoch ms) }

Usage:
    python3 scripts/inject-progress.py                       # all /issues/*.html
    python3 scripts/inject-progress.py path/to/x.html        # specific files
"""

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ISSUES_DIR = REPO_ROOT / "issues"

MARKER = "<!-- the-signal:progress -->"

SNIPPET = f"""{MARKER}
<script>
(function () {{
  if (!('localStorage' in window)) return;
  try {{
    var path = window.location.pathname;
    var slug = (path.split('/').pop() || '').replace(/\\.html$/, '');
    if (!slug) return;
    var titleEl = document.querySelector('h1') || document.querySelector('title');
    var title = (titleEl ? titleEl.textContent : slug).trim().slice(0, 140);
    var key = 'signal-progress-' + slug;

    function pct() {{
      var doc = document.documentElement;
      var scrolled = window.scrollY || doc.scrollTop || 0;
      var max = Math.max(1, doc.scrollHeight - window.innerHeight);
      return Math.max(0, Math.min(100, (scrolled / max) * 100));
    }}
    function save() {{
      try {{
        localStorage.setItem(key, JSON.stringify({{
          slug: slug, title: title, pct: pct(), ts: Date.now()
        }}));
      }} catch (_) {{}}
    }}

    var t = null;
    function debounced() {{
      if (t) clearTimeout(t);
      t = setTimeout(save, 1500);
    }}
    window.addEventListener('scroll', debounced, {{ passive: true }});
    window.addEventListener('beforeunload', save);
    document.addEventListener('visibilitychange', function () {{
      if (document.visibilityState === 'hidden') save();
    }});
    // Save once after initial paint so even no-scroll opens register a visit.
    setTimeout(save, 3000);
  }} catch (_) {{}}
}})();
</script>
<!-- /the-signal:progress -->"""


def inject(html_path: Path) -> bool:
    content = html_path.read_text(encoding="utf-8")
    if MARKER in content:
        return False
    if "</body>" not in content:
        print(f"  ! {html_path.name}: no </body> found, skipping")
        return False
    new = content.replace("</body>", SNIPPET + "\n</body>", 1)
    html_path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="HTML files (default: all /issues/*.html)")
    args = ap.parse_args()

    targets = (
        [Path(f).resolve() for f in args.files]
        if args.files
        else sorted(ISSUES_DIR.glob("*.html"))
    )

    modified = 0
    for path in targets:
        if inject(path):
            modified += 1
            print(f"  + {path.relative_to(REPO_ROOT)}")
        else:
            print(f"  = {path.relative_to(REPO_ROOT)} (already has snippet or no </body>)")

    print(f"\nDone. {modified}/{len(targets)} files modified.")


if __name__ == "__main__":
    main()
