#!/usr/bin/env python3
"""check-prose-rhythm.py — Phase 7 gate against paragraph walls (v8.24.8).

A literary special must break up its prose with VISUAL variety. Long runs of
paragraphs with no figure, pull-quote, gutter marginalia, stat row, image-quote,
ornament, table or list between them read as a wall of text and waste the
medium. (The WW1 Deep Dive shipped chapters with 15+ such paragraphs.) A text
sub-heading helps structure but is NOT a visual break, so it does not reset the
count here — the point is visual flair, not just sub-sections.

It walks block-level elements in document order, counts paragraphs since the
last visual break (resetting at visual breaks and chapter boundaries; ignoring
text sub-heads), and fails if any run exceeds the threshold.

Usage:
  python3 check-prose-rhythm.py <stitched-html> [--max N] [--warn-only]

Default --max is 9 (fail if >9 paragraphs with no visual break). Editorial
target is a visual break every 2-4 paragraphs; the gate only catches walls.
"""
import sys, re

# Genuine VISUAL breaks — these reset the run.
VISUAL_BREAK = re.compile(
    r'<figure\b|<blockquote\b|<table\b|<svg\b|<ul\b|<ol\b|<dl\b|<article\b'
    r'|<aside\b[^>]*\bmarginalia\b'
    r'|<div\b[^>]*\b(?:bignum-row|sp-ornament|is-wide|keep-digging)\b',
    re.I)
# Text sub-heads — ignored (neither count nor reset).
SUBHEAD = re.compile(r'<h[2-4]\b|<p\b[^>]*\bsp-kicker\b', re.I)
# A body paragraph (not an sp-kicker).
PARA = re.compile(r'<p\b(?![^>]*\bsp-kicker\b)', re.I)
BOUNDARY = re.compile(r'<(?:section|header|footer)\b', re.I)

TOKEN = re.compile(
    r'<(?:section|header|footer)\b'
    r'|<h[2-4]\b'
    r'|<p\b[^>]*\bsp-kicker\b'
    r'|<p\b'
    r'|<figure\b|<blockquote\b|<table\b|<svg\b|<ul\b|<ol\b|<dl\b|<aside\b|<article\b'
    r'|<div\b[^>]*\b(?:bignum-row|sp-ornament|is-wide|keep-digging)\b',
    re.I)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print("usage: check-prose-rhythm.py <html> [--max N] [--warn-only]")
        sys.exit(2)
    path = args[0]
    mx = 9
    for i, a in enumerate(sys.argv):
        if a == '--max' and i + 1 < len(sys.argv):
            try: mx = int(sys.argv[i + 1])
            except Exception: pass
        elif a.startswith('--max='):
            try: mx = int(a.split('=', 1)[1])
            except Exception: pass
    warn_only = '--warn-only' in sys.argv

    html = open(path, encoding='utf-8').read()
    m = re.search(r'</head\s*>', html, re.I)
    body = html[m.end():] if m else html
    body = re.sub(r'<style\b.*?</style>', ' ', body, flags=re.S | re.I)
    body = re.sub(r'<script\b.*?</script>', ' ', body, flags=re.S | re.I)

    run = 0
    worst = {}
    cur = "cover"
    for tok in TOKEN.finditer(body):
        s = tok.group(0)
        if BOUNDARY.match(s):
            run = 0
            t = re.search(r'id="([^"]+)"', body[tok.start():tok.start() + 200])
            cur = t.group(1) if t else cur
            continue
        if SUBHEAD.match(s):
            continue                      # ignore — not a visual break
        if PARA.match(s):
            run += 1
            if run > worst.get(cur, 0):
                worst[cur] = run
        elif VISUAL_BREAK.match(s):
            run = 0

    walls = {k: v for k, v in worst.items() if v > mx}
    print("=== check-prose-rhythm.py ===")
    print(f"File: {path}   threshold: >{mx} paragraphs with no visual break")
    longest = max(worst.values()) if worst else 0
    if not walls:
        print(f"PASS — longest unbroken run: {longest} paragraphs.")
        sys.exit(0)
    print("Paragraph walls (chapter id : longest run with no visual break):")
    for k, v in sorted(walls.items(), key=lambda kv: -kv[1]):
        print(f"  {v:3d}  {k}")
    print("\nBreak these up with a figure, pull-quote, gutter marginalia, stat row,")
    print("image-quote, ornament, table or list — a visual break every 2-4 paragraphs.")
    sys.exit(0 if warn_only else 1)


if __name__ == "__main__":
    main()
