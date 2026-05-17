#!/bin/bash
# Injects CSS and JS into a generated Signal HTML file.
# Usage: ./inject-assets.sh <html-file>
#
# The agent generates HTML with exact placeholder comments:
#   <!-- INJECT:CSS -->  (in <head>)
#   <!-- INJECT:JS -->   (before </body>)
#
# CSS is assembled from assets/css/*.css (alphabetical order).
# The numeric filename prefix (00-, 01-, ...) defines cascade order.
# If assets/css/ is absent, falls back to legacy assets/styles.css.

set -e

HTML_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"

if [ -z "$HTML_FILE" ]; then
    echo "Usage: $0 <html-file>"
    exit 1
fi

if [ ! -f "$HTML_FILE" ]; then
    echo "ERROR: $HTML_FILE not found"
    exit 1
fi

# Verify placeholders exist before attempting injection
if ! grep -q '<!-- INJECT:CSS -->' "$HTML_FILE"; then
    echo "ERROR: <!-- INJECT:CSS --> placeholder not found in $HTML_FILE"
    echo "The HTML must contain exactly: <!-- INJECT:CSS --> in the <head>"
    exit 1
fi

if ! grep -q '<!-- INJECT:JS -->' "$HTML_FILE"; then
    echo "ERROR: <!-- INJECT:JS --> placeholder not found in $HTML_FILE"
    echo "The HTML must contain exactly: <!-- INJECT:JS --> before </body>"
    exit 1
fi

# Assemble CSS
if [ -d "$ASSETS_DIR/css" ] && [ -n "$(ls -A "$ASSETS_DIR/css"/*.css 2>/dev/null)" ]; then
    CSS_MODE="split"
else
    CSS_MODE="legacy"
fi

# Inject using Python for reliable multi-line replacement
python3 << PYEOF
import glob
from pathlib import Path

html_path = Path("$HTML_FILE")
assets_dir = Path("$ASSETS_DIR")
css_mode = "$CSS_MODE"

html = html_path.read_text()

if css_mode == "split":
    css_files = sorted((assets_dir / "css").glob("*.css"))
    css_chunks = [f.read_text() for f in css_files]
    css = "\n".join(css_chunks)
    css_source = f"{len(css_files)} files from assets/css/"
else:
    css = (assets_dir / "styles.css").read_text()
    css_source = "assets/styles.css (legacy)"

js = (assets_dir / "script.js").read_text()

html = html.replace("<!-- INJECT:CSS -->", "<style>\n" + css + "\n</style>")
html = html.replace("<!-- INJECT:JS -->", "<script>\n" + js + "\n</script>")

html_path.write_text(html)

# Verify injection succeeded
assert "<style>" in html, "CSS injection failed — no <style> tag found"
assert "<script>" in html, "JS injection failed — no <script> tag found"
assert "<!-- INJECT:CSS -->" not in html, "CSS placeholder still present after injection"
assert "<!-- INJECT:JS -->" not in html, "JS placeholder still present after injection"

# === Sanity warnings (non-fatal) ===
import re
warnings = []

# 1. Duplicate masthead check
old_masthead_count = len(re.findall(r'<nav[^>]*class="[^"]*\bmasthead\b', html))
new_masthead_count = len(re.findall(r'<div[^>]*class="mast"', html))
if old_masthead_count > 0:
    warnings.append(f"Found {old_masthead_count} <nav class='masthead'> element(s) — these duplicate the persistent .mast div and will render unstyled. Remove them.")
if new_masthead_count > 1:
    warnings.append(f"Found {new_masthead_count} <div class='mast'> elements — there must be exactly one persistent masthead.")
if new_masthead_count == 0:
    warnings.append("No persistent masthead (<div class='mast'>) found — the issue will be missing the pinned chrome bar.")

# 2. Image URL sanity
# Flag thumb URLs which often 404
thumb_imgs = re.findall(r'src="https://upload\.wikimedia\.org/wikipedia/commons/thumb/[^"]+"', html)
if thumb_imgs:
    warnings.append(f"Found {len(thumb_imgs)} Wikimedia thumb URL(s) — these often 404. Use original-resolution paths or Special:FilePath redirects instead.")

# Flag literal placeholders
placeholder_imgs = re.findall(r'src="(\.\.\.|…)"', html)
if placeholder_imgs:
    warnings.append(f"Found {len(placeholder_imgs)} <img> tag(s) with placeholder src ('...' or '…') — these are unrendered. Replace with real URLs.")

if warnings:
    print("")
    print("!! Sanity warnings (review before publishing):")
    for w in warnings:
        print(f"   - {w}")
    print("")

print(f"OK: Injected CSS ({len(css):,} chars, {css_source}) and JS ({len(js):,} chars)")
PYEOF
