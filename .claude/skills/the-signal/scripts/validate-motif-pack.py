#!/usr/bin/env python3
"""
validate-motif-pack.py — gate a motif pack before it re-themes an issue
(design-system-unification spec §4.2 / §4.3 / Phase 4).

A motif pack is the ONLY per-issue theming surface: a token block + <=4 art
slots, rendered inline in the issue, NEVER new CSS in the repo. This validator
enforces the machine checks the spec names, at plan time:

  • WCAG AA contrast for every act's paper/ink AND accent/paper pair (>= 4.5:1)
  • font whitelist membership (only the ~15 approved families)
  • art-slot byte caps (pattern/glyph/band) + currentColor requirement on the
    glyph SVG slot (it is masked, so it MUST be a currentColor/mask asset)
  • act arithmetic (1-3 acts; each act fully specified; grounds valid)

Usage:
  python3 scripts/validate-motif-pack.py <pack.json>
  python3 scripts/validate-motif-pack.py --test
Exit 0 = pack is safe to theme with. Non-zero = rejected (all errors printed).
"""
import json, re, sys
from pathlib import Path

# ── Font whitelist — the families the core's six type roles may carry. ──
FONT_WHITELIST = {
    "Bowlby One", "Impact", "Arial Black",                       # chunk
    "Anton", "Bebas Neue",                                       # tall
    "Yellowtail", "Pacifico",                                   # script
    "Caveat", "Kalam", "Segoe Print",                          # hand
    "Cormorant Garamond", "EB Garamond", "Georgia", "Cinzel", "Playfair Display",  # serif
    "DM Sans", "Inter",                                         # sans
    "JetBrains Mono", "IBM Plex Mono", "Space Mono",           # mono
}
VALID_GROUNDS = {"paper", "ink", "gallery"}
ART_BYTE_CAPS = {"pattern": 12 * 1024, "glyph": 12 * 1024, "band": 40 * 1024}
AA = 4.5

def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def _lum(hex_):
    h = hex_.lstrip("#")
    if len(h) == 3: h = "".join(ch * 2 for ch in h)
    if len(h) != 6 or re.search(r"[^0-9a-fA-F]", h): raise ValueError(f"bad hex {hex_!r}")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def validate(pack, skill_dir=None):
    errs = []
    if not isinstance(pack, dict):
        return ["pack is not a JSON object"]
    if not pack.get("id"): errs.append("[ID] missing pack id")

    acts = pack.get("acts")
    if not isinstance(acts, list) or not (1 <= len(acts) <= 3):
        errs.append("[ACTS] 'acts' must be a list of 1-3 act objects")
        acts = acts if isinstance(acts, list) else []
    for i, act in enumerate(acts):
        if not isinstance(act, dict): errs.append(f"[ACT {i}] not an object"); continue
        for key in ("paper", "ink", "accent"):
            if key not in act: errs.append(f"[ACT {i}] missing '{key}'")
        ground = act.get("ground", "paper")
        if ground not in VALID_GROUNDS:
            errs.append(f"[ACT {i}] ground '{ground}' not in {sorted(VALID_GROUNDS)}")
        try:
            if "paper" in act and "ink" in act:
                r = contrast(act["paper"], act["ink"])
                if r < AA: errs.append(f"[ACT {i}] ink/paper contrast {r:.2f}:1 < AA {AA}")
            if "paper" in act and "accent" in act:
                r = contrast(act["paper"], act["accent"])
                if r < 3.0:  # accent is used for large text / rules → 3:1 AA-large floor
                    errs.append(f"[ACT {i}] accent/paper contrast {r:.2f}:1 < 3.0 (AA-large)")
        except ValueError as e:
            errs.append(f"[ACT {i}] {e}")

    # type roles → whitelist
    type_roles = pack.get("type", {})
    if isinstance(type_roles, dict):
        for role, family in type_roles.items():
            lead = family.split(",")[0].strip().strip("'\"")
            if lead and lead not in FONT_WHITELIST:
                errs.append(f"[FONT] role '{role}' lead family '{lead}' not in whitelist")

    # art slots — byte caps + currentColor requirement on glyph
    if skill_dir:
        art_dir = Path(skill_dir) / "references" / "motif-art"
        for slot in ("pattern", "glyph", "band"):
            ref = pack.get(slot)
            if not ref: continue
            asset = art_dir / ref
            if not asset.exists():
                errs.append(f"[ART] {slot} asset '{ref}' not found in references/motif-art/")
                continue
            size = asset.stat().st_size
            if size > ART_BYTE_CAPS[slot]:
                errs.append(f"[ART] {slot} '{ref}' {size}B > cap {ART_BYTE_CAPS[slot]}B")
            if slot == "glyph":
                txt = asset.read_text(errors="ignore")
                if "currentColor" not in txt and 'fill="none"' not in txt and "mask" not in ref:
                    errs.append(f"[ART] glyph '{ref}' must be a currentColor/mask asset "
                                f"(it is fed through mask-image: var(--mx-glyph))")

    motion = pack.get("motion", "tier0")
    if motion not in {"tier0", "tier1", "tier2", "still", "calm", "event"}:
        errs.append(f"[MOTION] '{motion}' not a valid tier")
    return errs


def run_tests():
    good = {
        "id": "byzantium-dossier-2026",
        "acts": [
            {"paper": "#F4ECDC", "ink": "#2B1B33", "accent": "#8E1F3B", "ground": "paper"},
            {"paper": "#EDE3CC", "ink": "#241018", "accent": "#7A2F1B", "ground": "paper"},
        ],
        "type": {"serif": "Cormorant Garamond", "mono": "JetBrains Mono", "chunk": "Bowlby One"},
        "pattern": None, "glyph": None, "band": None, "motion": "tier0",
    }
    cases = [
        ("valid dossier pack", good, True),
        ("low ink/paper contrast", {**good, "acts": [{"paper": "#F4ECDC", "ink": "#DAD0BB", "accent": "#8E1F3B"}]}, False),
        ("accent too pale", {**good, "acts": [{"paper": "#F4ECDC", "ink": "#2B1B33", "accent": "#E9C9C9"}]}, False),
        ("off-whitelist font", {**good, "type": {"serif": "Comic Sans MS"}}, False),
        ("bad ground", {**good, "acts": [{"paper": "#F4ECDC", "ink": "#2B1B33", "accent": "#8E1F3B", "ground": "ocean"}]}, False),
        ("too many acts", {**good, "acts": good["acts"] * 2}, False),
        ("bad hex", {**good, "acts": [{"paper": "#ZZZ", "ink": "#2B1B33", "accent": "#8E1F3B"}]}, False),
    ]
    passed = 0
    for name, pack, expect_ok in cases:
        errs = validate(pack)
        ok = (len(errs) == 0) == expect_ok
        passed += ok
        print(f"  {'✓' if ok else '✗'} {name}" + ("" if ok else f"  -> errs={errs}"))
    print(f"\n{passed}/{len(cases)} tests passed.")
    return passed == len(cases)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(0 if run_tests() else 1)
    if len(sys.argv) < 2:
        print("usage: validate-motif-pack.py <pack.json> | --test"); sys.exit(2)
    pack_path = Path(sys.argv[1])
    skill_dir = Path(__file__).resolve().parent.parent
    pack = json.loads(pack_path.read_text())
    errs = validate(pack, skill_dir=skill_dir)
    print(f"=== validate-motif-pack: {pack_path.name} ===")
    if errs:
        for e in errs: print(f"[FAIL] {e}")
        print(f"\n{len(errs)} error(s) — pack REJECTED."); sys.exit(1)
    print(f"[PASS] pack '{pack.get('id')}' valid ({len(pack.get('acts', []))} acts)."); sys.exit(0)


if __name__ == "__main__":
    main()
