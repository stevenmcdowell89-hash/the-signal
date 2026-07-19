#!/usr/bin/env python3
"""validate-motif-pack.py — plan-time validator for The Signal motif packs
(design-system unification spec §2.2/§2.3, WP-4).

Usage:
  python3 tools/motif/validate-motif-pack.py PACK.json [PACK2.json ...]
        [--whitelist tools/motif/font-whitelist.json]

Checks (each rejection carries a named reason code):
  SCHEMA         §2.3 shape: id slug; acts[] objects; six type roles; art
                 slots null/.svg/{svg:...}; cover_plate inline-or-null;
                 act tokens restricted to the §2.2 contract keys
  ACT-ARITHMETIC 1-3 acts, ids sequential 1..N
  CONTRAST-AA    per act: --mx-ink vs --mx-paper >= 4.5:1 (body-copy bar) ·
                 --mx-accent vs --mx-paper >= 3.0:1 (large-display bar;
                 the accent only ever renders as display/kicker type)
  FONT-WHITELIST all six roles on tools/motif/font-whitelist.json (self-
                 hosted files must exist under assets/fonts/ — a pack can
                 never introduce a network font)
  ART-BYTE-CAP   SVG source: pattern <=8KB, glyph <=4KB, band <=8KB,
                 cover_plate <=8KB
  CURRENTCOLOR   pattern/glyph SVGs use currentColor; no hard-coded
                 fill/stroke except none; no <script>/<image>/href
  KIT            kit in the §2.4 list
  MOTION         motion in tier0|tier1|tier2
  GRAIN          grain register named (none/soft/paper/halftone/heavy)

Exit 0 = every pack green; exit 1 = any rejection (reasons printed).
stdlib only; no network.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motiflib import PackError, validate_pack  # noqa: E402


def main(argv):
    args = [a for a in argv[1:]]
    whitelist = None
    packs = []
    i = 0
    while i < len(args):
        if args[i] == "--whitelist":
            whitelist = Path(args[i + 1]); i += 2
        else:
            packs.append(Path(args[i])); i += 1
    if not packs:
        print(__doc__)
        return 2

    any_fail = False
    for pack_path in packs:
        print(f"=== {pack_path} ===")
        if not pack_path.is_file():
            print("  REJECT [SCHEMA] pack file not found")
            any_fail = True
            continue
        try:
            pack, art, report, errors = validate_pack(pack_path, whitelist)
        except PackError as e:
            print(f"  REJECT [{e.code}] {e}")
            any_fail = True
            continue
        for line in report:
            print(line)
        if errors:
            any_fail = True
            for e in errors:
                print(f"  REJECT [{e.code}] {e}")
            print(f"  VERDICT: REJECTED ({len(errors)} failure(s))")
        else:
            acts = pack.get("acts", [])
            print(f"  id={pack.get('id')} · {len(acts)} act(s) · kit={pack.get('kit')} · "
                  f"motion={pack.get('motion')} · grain={pack.get('grain')}")
            print("  VERDICT: GREEN")
        print()
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
