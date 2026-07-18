#!/usr/bin/env python3
"""Phase 2 verification: re-dress a COPY of the Byzantium Deep Dive FROM THE CORE
(assets/css/core/*), not the Phase 1 shim. Proves the --mx-* contract + core
furniture layers render the same paper-and-ink kit. Adds data-mx to <body> so the
contract activates. Furniture content is the same issue-own facts as Phase 1."""
import json, re, html as htmllib
from pathlib import Path

ROOT  = Path("/home/user/the-signal")
SRC   = ROOT/"issues/signal_deep-dive_2026-06-30.html"
CORE  = ROOT/".claude/skills/the-signal/assets/css/core"
BRIDGE= ROOT/"docs/mockups/phase2/core-bridge.css"
DATA  = ROOT/"docs/mockups/phase1/dd-furniture.json"
OUT   = ROOT/"docs/mockups/phase2/signal_deep-dive_2026-06-30-core.html"

def esc(s): return htmllib.escape(s, quote=False)
def norm(s): return re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",s)).strip().replace("’","'")

doc  = SRC.read_text()
data = json.loads(DATA.read_text())
core_css = "\n".join((CORE/f).read_text() for f in
                     sorted(f.name for f in CORE.glob("*.css"))) + "\n" + BRIDGE.read_text()

def numbers_band(items):
    cells="".join(f'<div class="mx-numbers__cell"><span class="mx-numbers__fig">{esc(i["figure"])}</span>'
                  f'<span class="mx-numbers__lab">{esc(i["label"])}</span></div>' for i in items)
    return f'<div class="mx-block mx-numbers" role="group" aria-label="Byzantium in numbers">{cells}</div>'
def ledger(title,rows):
    body="".join(f'<dt>{esc(r["label"])}</dt><dd>{esc(r["value"])}</dd>' for r in rows)
    return f'<aside class="mx-block mx-ledger"><p class="mx-ledger__title">{esc(title)} · in brief</p><dl>{body}</dl></aside>'
def quote(q):
    return ('<blockquote class="mx-block mx-quote">'
            f'<p class="mx-quote__text">{esc(q["text"])}</p>'
            f'<cite class="mx-quote__source">{esc(q["source"])}</cite></blockquote>')
def stamp(label,big,sub):
    return f'<div class="mx-stamp" role="img" aria-label="{esc(label)} {esc(sub)}">{esc(label)}<b>{esc(big)}</b>{esc(sub)}</div>'
def cheat(rows):
    body="".join(f'<tr><td>{esc(r["period"])}</td><td class="mx-cheat__mono">{esc(r["dates"])}</td>'
                 f'<td>{esc(r["marker"])}</td><td>{esc(r["significance"])}</td></tr>' for r in rows)
    return ('<div class="mx-block mx-cheat"><div class="mx-cheat__head">The empire at a glance</div>'
            '<table><thead><tr><th>Period</th><th>Dates</th><th>Marker</th><th>Significance</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

head_end = re.search(r'</head\s*>', doc, re.I).end()
positions={}
for m in re.finditer(r'<h2 class="chapter-title">(.*?)</h2>', doc[head_end:], re.S):
    t=norm(m.group(1)); sec=doc.rfind('<section class="chapter"', head_end, head_end+m.start())
    if sec!=-1: positions[t]=sec

chapters=data["chapters"]
ins=[]
first=positions[norm(chapters[0]["title"])]
ins.append((first,'<div class="mx-block" style="display:flex;justify-content:flex-end;margin-bottom:-1rem">'
            + stamp("DEEP DIVE","№","BYZANTIUM")+'</div>'+numbers_band(data["numbers_band"])))
for i,ch in enumerate(chapters):
    nxt=chapters[i+1]["title"] if i+1<len(chapters) else "Keep Digging"
    ins.append((positions[norm(nxt)], ledger(ch["title"],ch["ledger"])+quote(ch["quote"])))
ins.append((positions[norm("Keep Digging")], cheat(data["cheat_sheet"])))

groups={}
for idx,h in ins: groups.setdefault(idx,[]).append(h)
out=doc
for idx in sorted(groups, reverse=True):
    out=out[:idx]+"\n"+"\n".join(groups[idx])+"\n"+out[idx:]

# add data-mx to the real <body>, inline the core before </head>
out=re.sub(r'(<body\b[^>]*?)>', r'\1 data-mx="page">', out, count=1)  # first body after replaced doc
# ensure we tagged the REAL body (after </head>): re-do precisely
he=re.search(r'</head\s*>',out,re.I)
tail=out[he.end():]
tail=re.sub(r'<body\b(?![^>]*data-mx)([^>]*)>', r'<body\1 data-mx="page">', tail, count=1)
out=out[:he.end()]+tail
style=f'\n<style id="mx-core">\n{core_css}\n</style>\n'
out=out[:he.start()]+style+out[he.start():]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out)
print(f"OK wrote {OUT}  ({len(out):,} chars); {sum(len(v) for v in groups.values())} furniture blocks; core={len(core_css):,} chars")
