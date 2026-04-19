#!/bin/bash
# Injects CSS and JS into a generated Signal HTML file.
# Usage: ./inject-assets.sh <html-file>
#
# The agent generates HTML with exact placeholder comments:
#   <!-- INJECT:CSS -->  (in <head>)
#   <!-- INJECT:JS -->   (before </body>)
#
# This script replaces them with the full file contents,
# then verifies the injection succeeded.

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

# Inject using Python for reliable multi-line replacement
python3 << PYEOF
with open("$HTML_FILE", "r") as f:
    html = f.read()

with open("$ASSETS_DIR/styles.css", "r") as f:
    css = f.read()

with open("$ASSETS_DIR/script.js", "r") as f:
    js = f.read()

html = html.replace("<!-- INJECT:CSS -->", "<style>\n" + css + "\n</style>")
html = html.replace("<!-- INJECT:JS -->", "<script>\n" + js + "\n</script>")

with open("$HTML_FILE", "w") as f:
    f.write(html)

# Verify injection succeeded
assert "<style>" in html, "CSS injection failed — no <style> tag found"
assert "<script>" in html, "JS injection failed — no <script> tag found"
assert "<!-- INJECT:CSS -->" not in html, "CSS placeholder still present after injection"
assert "<!-- INJECT:JS -->" not in html, "JS placeholder still present after injection"

print(f"OK: Injected CSS ({len(css):,} chars) and JS ({len(js):,} chars)")
PYEOF
