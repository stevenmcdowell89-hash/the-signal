#!/usr/bin/env python3
"""
stitch_specials.py — deterministic, skeleton-driven assembly for SPECIAL editions
on the furniture-core system (design-system-unification §7.3).

Mirrors stitch_weekly.py: the writer cannot affect structure, only fill content.
ALL chrome — cover, act openers, the single transit band, per-chapter heads, the
motif token block, the colophon — is GENERATED HERE from the skeleton + plan +
motif pack, so the F-14 class (placeholder chrome, malformed structure) is
unrepresentable. Writers produce ONLY each chapter's inner furniture markup at
<build>/chapters/<chapter_id>.html.

Inputs:
  --plan   chapter-plan.json  (issue_meta{format,skin,motif_pack,...}, cover, chapters[])
  --build-dir  <dir>/chapters/<chapter_id>.html  writer inner content per chapter
  skeleton   references/format-skeletons/<format>.json
  motif pack references/motif-packs/<motif_pack>.json  → inline --mx-* token block
  CSS        references/css-manifests/<format>.txt      → core + skin bundle

Output: a complete new-system issue: <body data-mx="page" data-skin data-special>,
the core furniture rendering under the motif's tokens.

A per-skin VOCABULARY GATE rejects any class in chapter content that is not an
allowed core/furniture class — so an out-of-skin (legacy .sp-* / .hol-*) class in
writer content fails the build instead of shipping.
"""
import argparse, json, re, sys
from pathlib import Path

import importlib.util as _ilu
_motif = None
_mp = Path(__file__).with_name("render-motif-pack.py")
if _mp.exists():
    _spec = _ilu.spec_from_file_location("render_motif_pack", _mp)
    _motif = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_motif)


def esc(s): return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
def die(msg): print(f"═══ SPECIAL STITCH FAILED ═══\n{msg}", file=sys.stderr); sys.exit(1)

# Allowed class prefixes/names in writer chapter content (the vocabulary gate).
ALLOWED_CLASS_RE = re.compile(r"^(mx-|is-|data-)")
ALLOWED_BARE = {"", "credit", "figure"}


def render_motif_block(skill_dir, pack_id, skin):
    if not pack_id:
        return f'<style id="mx-motif">/* no motif pack — core defaults + skin {skin} */</style>'
    p = skill_dir / "references/motif-packs" / f"{pack_id}.json"
    if not p.exists():
        die(f"motif_pack '{pack_id}' not found at {p}")
    pack = json.loads(p.read_text())
    if _motif:
        return _motif.render(pack, selector="body")
    # fallback minimal renderer
    a = pack.get("acts", [{}])[0]
    v = "; ".join(f"--mx-{k}: {a[k]}" for k in ("paper", "ink", "accent") if k in a)
    return f'<style id="mx-motif">body[data-mx] {{ {v} }}</style>'


def assemble_css(skill_dir, fmt):
    """Core + skin bundle from the per-format manifest (F-5)."""
    css_dir = skill_dir / "assets/css"
    manifest = skill_dir / "references/css-manifests" / f"{fmt}.txt"
    if not manifest.exists():
        die(f"no CSS manifest for format '{fmt}' at {manifest}")
    files = [ln.strip() for ln in manifest.read_text().splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    missing = [f for f in files if not (css_dir / f).exists()]
    if missing:
        die(f"manifest lists missing CSS: {missing[:3]}")
    return "\n".join((css_dir / f).read_text() for f in files)


def render_head(title, css, motif_block):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style id="mx-core">
{css}
</style>
{motif_block}
</head>
"""


def render_cover(cover, meta, skin):
    poster = " mx-cover--poster" if cover.get("poster") else ""
    eyebrow = esc(cover.get("eyebrow", meta.get("format", "").upper()))
    title = cover.get("title_html") or esc(cover.get("title", ""))
    stand = esc(cover.get("standfirst", ""))
    meta_items = cover.get("meta", [])
    meta_html = ""
    if meta_items:
        chips = "".join(f"<span>{esc(m)}</span>" for m in meta_items)
        meta_html = f'\n    <div class="mx-cover__meta">{chips}</div>'
    return f"""  <header class="mx-cover{poster}">
    <div class="mx-cover__eyebrow">{eyebrow}</div>
    <h1 class="mx-cover__title">{title}</h1>
    <p class="mx-cover__standfirst">{stand}</p>{meta_html}
  </header>
"""


def render_act_open(numeral, label):
    return (f'  <div class="mx-act-open" data-role="act-open">'
            f'<span class="mx-act-open__num">{esc(numeral)}</span>'
            f'<span class="mx-act-open__label">{esc(label)}</span></div>\n')


def render_transit(line):
    return (f'  <section class="mx-transit" data-role="transit">'
            f'<span class="mx-transit__mark">— intermission —</span>'
            f'<p class="mx-transit__line">{esc(line)}</p></section>\n')


def render_chapter_head(num, title):
    return (f'  <div class="mx-plate" data-role="chapter-head">'
            f'<span class="mx-plate__num">{esc(num)}</span>'
            f'<h2 class="mx-plate__title">{esc(title)}</h2></div>\n')


def vocab_gate(chapter_id, content):
    for m in re.finditer(r'class\s*=\s*"([^"]*)"', content):
        for cls in m.group(1).split():
            if cls in ALLOWED_BARE or ALLOWED_CLASS_RE.match(cls):
                continue
            die(f"vocabulary gate: chapter '{chapter_id}' uses out-of-skin class "
                f"'{cls}'. Special content may use only core .mx-* furniture classes.")


ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--build-dir", default="/tmp/signal-build")
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir)
    plan = json.loads(Path(args.plan).read_text())
    meta = plan.get("issue_meta", {})
    fmt = meta.get("format", "").lower().replace("_", "-")
    if fmt == "weekly":
        die("stitch_specials.py invoked on a weekly plan — use stitch_weekly.py.")
    skin = meta.get("skin") or ("event" if fmt in ("countdown", "field-guide", "season-review") else "editorial")
    motif_pack = meta.get("motif_pack")
    chapters_dir = Path(args.build_dir) / "chapters"

    skel_path = skill_dir / "references/format-skeletons" / f"{fmt}.json"
    skeleton = json.loads(skel_path.read_text()) if skel_path.exists() else {}

    css = assemble_css(skill_dir, fmt)
    motif_block = render_motif_block(skill_dir, motif_pack, skin)
    title = f"The Signal — {meta.get('topic', fmt.title())}"

    parts = [render_head(title, css, motif_block)]
    parts.append(f'<body class="is-special" data-special="{esc(fmt)}" data-mx="page" '
                 f'data-skin="{esc(skin)}" data-motion="{esc(meta.get("motion","calm"))}">\n')
    # deterministic archive back-link (the stitcher owns chrome — same as the weekly)
    back = skill_dir / "assets/template-parts/back-link.html"
    if back.exists():
        parts.append(back.read_text() + "\n")
    parts.append('<main class="mx-issue">\n')
    parts.append(render_cover(plan.get("cover", {}), meta, skin))

    current_act = None
    transit_done = False
    for ch in plan.get("chapters", []):
        cid = ch.get("chapter_id", "")
        act = ch.get("act", 1)
        # act opener when the act advances
        if act != current_act:
            parts.append(f'  <section data-act="{esc(act)}">\n')
            if current_act is not None:
                parts.append("  </section>\n")
            current_act = act
        # single transit band before act 2 (skeleton invariant: max 1)
        if ch.get("role") == "transit" and not transit_done:
            parts.append(render_transit(ch.get("transit_line", ch.get("chapter_title", ""))))
            transit_done = True
            continue
        num = ch.get("numeral") or ROMAN[ch.get("chapter_num", 0)] if ch.get("chapter_num", 0) < len(ROMAN) else str(ch.get("chapter_num", ""))
        parts.append(render_chapter_head(num, ch.get("chapter_title", cid)))
        cf = chapters_dir / f"{cid}.html"
        if cf.exists():
            content = cf.read_text()
            vocab_gate(cid, content)
            parts.append(f'  <section class="mx-chapter" data-chapter="{esc(cid)}">\n{content}\n  </section>\n')
        else:
            die(f"chapter '{cid}' has no content file at {cf}.")
    if current_act is not None:
        parts.append("  </section>\n")

    # colophon (deterministic)
    parts.append('  <footer class="mx-block" data-role="colophon">'
                 f'<p class="mx-eyebrow">The Signal · {esc(meta.get("date",""))} · '
                 f'{esc(fmt.replace("-"," ").title())}</p></footer>\n')
    parts.append("</main>\n</body>\n</html>\n")

    out = "".join(parts)
    Path(args.out).write_text(out)
    print(f"OK stitched {fmt} ({skin} skin, motif={motif_pack}) → {args.out} "
          f"({len(out):,} chars, {len(plan.get('chapters', []))} chapters)")


if __name__ == "__main__":
    main()
