#!/usr/bin/env python3
"""Phase 1 injector: re-dress a COPY of the Byzantium Deep Dive with furniture
built only from the issue's own facts (dd-furniture.json), driven by the
mx-phase1-shim token/furniture stylesheet. Prototype only — never a live issue."""
import json, re, sys, html as htmllib
from pathlib import Path

SRC   = Path("/home/user/the-signal/issues/signal_deep-dive_2026-06-30.html")
SHIM  = Path("/home/user/the-signal/docs/mockups/phase1/mx-phase1-shim.css")
DATA  = Path("/home/user/the-signal/docs/mockups/phase1/dd-furniture.json")
OUT   = Path("/home/user/the-signal/docs/mockups/phase1/signal_deep-dive_2026-06-30-redressed.html")

def esc(s): return htmllib.escape(s, quote=False)

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip().replace("’", "'")

doc  = SRC.read_text()
shim = SHIM.read_text()
data = json.loads(DATA.read_text())

# ---- furniture HTML builders ----
def numbers_band(items):
    cells = "".join(
        f'<div class="mx-numbers__cell"><span class="mx-numbers__fig">{esc(i["figure"])}</span>'
        f'<span class="mx-numbers__lab">{esc(i["label"])}</span></div>' for i in items)
    return ('<div class="mx-block mx-numbers" role="group" aria-label="Byzantium in numbers">'
            f'{cells}</div>')

def ledger(title, rows):
    body = "".join(f'<dt>{esc(r["label"])}</dt><dd>{esc(r["value"])}</dd>' for r in rows)
    return (f'<aside class="mx-block mx-ledger"><p class="mx-ledger__title">{esc(title)} · in brief</p>'
            f'<dl>{body}</dl></aside>')

def quote(q):
    return ('<blockquote class="mx-block mx-quote">'
            f'<p class="mx-quote__text">{esc(q["text"])}</p>'
            f'<cite class="mx-quote__source">{esc(q["source"])}</cite></blockquote>')

def stamp(label, big, sub):
    return (f'<div class="mx-stamp" role="img" aria-label="{esc(label)} {esc(sub)}">'
            f'{esc(label)}<b>{esc(big)}</b>{esc(sub)}</div>')

def cheat(rows):
    body = "".join(
        f'<tr><td>{esc(r["period"])}</td><td class="mx-cheat__dates">{esc(r["dates"])}</td>'
        f'<td>{esc(r["marker"])}</td><td>{esc(r["significance"])}</td></tr>' for r in rows)
    return ('<div class="mx-block mx-cheat"><div class="mx-cheat__head">The empire at a glance</div>'
            '<table><thead><tr><th>Period</th><th>Dates</th><th>Marker</th><th>Significance</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

# ---- locate chapters in the REAL body (after </head>) ----
head_end = re.search(r'</head\s*>', doc, re.I).end()
titles_in_order = [c["title"] for c in data["chapters"]] + ["Keep Digging"]

# map normalized title -> section-start index of its <section class="chapter">
positions = {}
for m in re.finditer(r'<h2 class="chapter-title">(.*?)</h2>', doc[head_end:], re.S):
    t = norm(m.group(1))
    h2abs = head_end + m.start()
    sec = doc.rfind('<section class="chapter"', head_end, h2abs)
    if sec != -1:
        positions[t] = sec

want = {norm(t): t for t in titles_in_order}
missing = [orig for n, orig in want.items() if n not in positions]
if missing:
    print("ERROR: could not locate chapters:", missing); sys.exit(1)

# ---- build insertions: (index, html) ----
ins = []
chapters = data["chapters"]
# numbers band + a stamp before the first chapter
first_idx = positions[norm(chapters[0]["title"])]
ins.append((first_idx,
    '<div class="mx-block" style="display:flex;justify-content:flex-end;margin-bottom:-1rem">'
    + stamp("DEEP DIVE", "№", "BYZANTIUM") + '</div>' + numbers_band(data["numbers_band"])))

# each chapter's ledger+quote at the start of the NEXT chapter (= end of current)
for i, ch in enumerate(chapters):
    nxt = chapters[i+1]["title"] if i+1 < len(chapters) else "Keep Digging"
    idx = positions[norm(nxt)]
    block = ledger(ch["title"], ch["ledger"]) + quote(ch["quote"])
    ins.append((idx, block))

# cheat-sheet before Keep Digging (after the last chapter furniture)
ins.append((positions[norm("Keep Digging")], cheat(data["cheat_sheet"])))

# apply from the end so indices stay valid; same-index blocks keep insertion order
ins.sort(key=lambda x: x[0])
out = doc
groups = {}
for idx, htmlblock in ins:
    groups.setdefault(idx, []).append(htmlblock)
for idx in sorted(groups, reverse=True):
    payload = "\n" + "\n".join(groups[idx]) + "\n"
    out = out[:idx] + payload + out[idx:]

# inline the shim stylesheet before </head>
he = re.search(r'</head\s*>', out, re.I)
style = f'\n<style id="mx-phase1-shim">\n{shim}\n</style>\n'
out = out[:he.start()] + style + out[he.start():]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out)
added = sum(len(v) for v in groups.values())
print(f"OK wrote {OUT}")
print(f"inserted {added} furniture blocks across {len(groups)} anchor points")
print(f"size: {len(out):,} chars (was {len(doc):,})")

# Matched BASELINE copy: same freeze/token shim, NO furniture — so the before/
# after comparison is fair (both static; before = the real walls of text).
BASE = OUT.parent / "signal_deep-dive_2026-06-30-baseline.html"
he0 = re.search(r'</head\s*>', doc, re.I)
base = doc[:he0.start()] + style + doc[he0.start():]
BASE.write_text(base)
print(f"OK wrote {BASE} (baseline, no furniture)")
