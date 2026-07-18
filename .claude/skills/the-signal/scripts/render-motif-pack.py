#!/usr/bin/env python3
"""
render-motif-pack.py — turn a validated motif pack into the inline <style> token
block an issue carries (design-system-unification §4.2/§4.3, Phase 4).

The pack runtime emits ONLY a --mx-* token block (palette per act + type roles +
art slots). It never emits component CSS — the furniture core owns that. So
swapping the pack on a fixture re-themes it with ZERO CSS diffs in the repo:
this script is the entire per-issue theming surface.

Usage:
  python3 scripts/render-motif-pack.py <pack.json>            # prints <style>...
  python3 scripts/render-motif-pack.py <pack.json> --selector body
"""
import json, sys
from pathlib import Path

def _act_vars(act):
    m = {"--mx-paper": act.get("paper"), "--mx-paper-2": act.get("paper_2", act.get("paper")),
         "--mx-ink": act.get("ink"), "--mx-ink-deep": act.get("ink_deep", act.get("ink")),
         "--mx-accent": act.get("accent"), "--mx-accent-2": act.get("accent_2")}
    return "; ".join(f"{k}: {v}" for k, v in m.items() if v)

TYPE_FALLBACK = {
    "chunk": "Impact, sans-serif", "tall": "Impact, sans-serif", "script": "cursive",
    "hand": "cursive", "serif": "Georgia, serif", "sans": "system-ui, sans-serif",
    "mono": "ui-monospace, monospace",
}

def render(pack, selector="body"):
    acts = pack.get("acts", [])
    lines = [f"/* motif-pack: {pack.get('id','?')} (kit={pack.get('kit','?')}, "
             f"motion={pack.get('motion','tier0')}) — token block only, no component CSS */"]
    sel = f"{selector}[data-mx]"
    # act 1 (default) + type roles + art slots on the host
    host = []
    if acts: host.append(_act_vars(acts[0]))
    for role, fam in (pack.get("type") or {}).items():
        lead = fam.split(",")[0].strip()
        host.append(f"--mx-t-{role}: {fam if ',' in fam else lead + ', ' + TYPE_FALLBACK.get(role, 'sans-serif')}")
    for slot in ("pattern", "glyph", "band"):
        ref = pack.get(slot)
        if ref: host.append(f"--mx-{slot}: url('/assets/motif-art/{ref}')")
    lines.append(f"{sel} {{ {'; '.join(host)} }}")
    # act 2+ re-declare palette subset
    for i, act in enumerate(acts[1:], start=2):
        lines.append(f"{sel} [data-act=\"{i}\"] {{ {_act_vars(act)} }}")
    return "<style id=\"mx-motif\">\n" + "\n".join(lines) + "\n</style>"

def main():
    if len(sys.argv) < 2:
        print("usage: render-motif-pack.py <pack.json> [--selector <sel>]"); sys.exit(2)
    pack = json.loads(Path(sys.argv[1]).read_text())
    selector = "body"
    if "--selector" in sys.argv:
        selector = sys.argv[sys.argv.index("--selector") + 1]
    print(render(pack, selector))

if __name__ == "__main__":
    main()
