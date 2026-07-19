"""motiflib.py — shared model for The Signal motif packs (L2, spec §2.1–§2.3).

A motif pack is ONE validated JSON file that re-themes a data-mx issue with
ZERO repo-CSS changes: per-act --mx-* token blocks, six type-role remaps from
the font whitelist, up to four art slots (pattern / glyph / band / cover
plate) and a grain + kit + motion declaration.

Used by:
  tools/motif/validate-motif-pack.py  (plan-time validation, exit 1 on reject)
  tools/motif/render-motif-pack.py    (pack -> deterministic head injection)

stdlib only. No network. Deterministic output (goldenized under
tools/motif/golden/).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

MOTIF_DIR = Path(__file__).resolve().parent
REPO_ROOT = MOTIF_DIR.parent.parent
DEFAULT_WHITELIST = MOTIF_DIR / "font-whitelist.json"
FONTS_DIR = REPO_ROOT / "assets" / "fonts"

# ---------------------------------------------------------------- contract

TYPE_ROLES = ("chunk", "tall", "script", "hand", "serif", "mono")

# §2.4 — one kit per issue
KITS = ("dossier", "broadcast", "scrapbook", "matchday", "scorecard",
        "paddock", "inventory", "cinema", "library", "logbook")

MOTION_TIERS = ("tier0", "tier1", "tier2")

# grain register -> --mx-grain opacity (an act token --mx-grain overrides)
GRAINS = {
    "none": "0",
    "soft": "0.04",
    "paper": "0.06",
    "halftone": "0.08",
    "heavy": "0.11",
}

# Act-token whitelist: the §2.2 contract's re-scopable palette + object
# surfaces + grain. Art/type/layout tokens are pack-level, never per-act.
ALLOWED_ACT_TOKENS = {
    "--mx-paper", "--mx-ink", "--mx-ink-soft",
    "--mx-accent", "--mx-accent-ink", "--mx-accent-2", "--mx-accent-2-ink",
    "--mx-support-1", "--mx-support-2", "--mx-hair",
    "--mx-card", "--mx-card-ink", "--mx-card-edge", "--mx-card-window",
    "--mx-tape", "--mx-ghost", "--mx-quote-bg", "--mx-shadow",
    "--mx-hand-ink", "--mx-stamp-ink",
    "--mx-grain",
}
REQUIRED_ACT_TOKENS = ("--mx-paper", "--mx-ink", "--mx-accent")

# Art byte caps (SVG SOURCE bytes, pre-encoding — documented in the spec's
# WP-4 block): pattern <=8KB, glyph <=4KB, band <=8KB, cover plate <=8KB.
ART_CAPS = {"pattern": 8192, "glyph": 4096, "band": 8192, "cover_plate": 8192}

REQUIRED_TOP_KEYS = ("id", "acts", "type", "pattern", "glyph", "band",
                     "cover_plate", "grain", "kit", "motion")
OPTIONAL_TOP_KEYS = ("notes",)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

# The head-injection marker (define once, here). stitch-issue.sh's mx path
# and render-motif-pack.py --inject replace this marker when present, else
# insert immediately before </head> (i.e. AFTER the bundle + per-issue
# styles, so pack tokens win the cascade).
INJECT_MARKER = "<!-- INJECT:MX-PACK -->"


class PackError(Exception):
    """A named validation failure. code is machine-stable."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


# ---------------------------------------------------------------- helpers

def load_json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PackError("SCHEMA", f"not valid JSON: {e}") from e


def load_whitelist(path: Path | None = None) -> dict:
    data = load_json(path or DEFAULT_WHITELIST)
    return data["families"]


def parse_hex(value: str):
    """#rgb/#rrggbb -> (r, g, b) 0..255, or None if not plain hex."""
    if not isinstance(value, str) or not HEX_RE.match(value.strip()):
        return None
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rel_luminance(rgb) -> float:
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    la, lb = rel_luminance(parse_hex(hex_a)), rel_luminance(parse_hex(hex_b))
    lo, hi = min(la, lb), max(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- art slots

def resolve_art(pack_path: Path, slot: str, value):
    """Return SVG source text for an art slot, or None.

    Accepted shapes (§2.3): null · "file.svg" (resolved relative to the pack
    file, then to a sibling art/ directory) · {"svg": "<svg .../>"} inline.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        svg = value.get("svg")
        if not isinstance(svg, str) or not svg.strip():
            raise PackError("SCHEMA", f"{slot}: inline art object needs a non-empty 'svg' string")
        return svg
    if isinstance(value, str):
        if slot == "cover_plate":
            # cover_plate is inline-or-null by contract (§2.3)
            if value.lstrip().startswith("<"):
                return value
            raise PackError("SCHEMA", "cover_plate must be inline SVG markup or null")
        if not value.endswith(".svg"):
            raise PackError("SCHEMA", f"{slot}: expected an .svg filename or {{'svg': ...}}, got {value!r}")
        base = Path(pack_path).resolve().parent
        for cand in (base / value, base / "art" / value):
            if cand.is_file():
                return cand.read_text(encoding="utf-8")
        raise PackError("SCHEMA", f"{slot}: art file not found next to pack (or in art/): {value}")
    raise PackError("SCHEMA", f"{slot}: must be null, an .svg filename, or {{'svg': ...}}")


_FILL_STROKE_ATTR_RE = re.compile(r"""\b(fill|stroke)\s*=\s*["']([^"']*)["']""", re.I)
_FILL_STROKE_STYLE_RE = re.compile(r"""(fill|stroke)\s*:\s*([^;"'}]+)""", re.I)


def check_currentcolor(slot: str, svg: str):
    """pattern/glyph SVGs must ride currentColor: every explicit fill/stroke
    is currentColor or none, and currentColor appears at least once (spec
    §2.2 — the one indirection that replaced layer 33's per-venue rules)."""
    if "currentColor" not in svg:
        raise PackError("CURRENTCOLOR",
                        f"{slot}: SVG never references currentColor")
    for m in _FILL_STROKE_ATTR_RE.finditer(svg):
        v = m.group(2).strip()
        if v not in ("currentColor", "none"):
            raise PackError("CURRENTCOLOR",
                            f"{slot}: hard-coded {m.group(1)}=\"{v}\" (only currentColor or none allowed)")
    for m in _FILL_STROKE_STYLE_RE.finditer(svg):
        v = m.group(2).strip()
        if v not in ("currentColor", "none"):
            raise PackError("CURRENTCOLOR",
                            f"{slot}: hard-coded style {m.group(1)}:{v} (only currentColor or none allowed)")
    for banned in ("<script", "<image", "href="):
        if banned in svg:
            raise PackError("CURRENTCOLOR",
                            f"{slot}: banned construct {banned!r} in SVG (self-contained vector art only)")


# ---------------------------------------------------------------- validation

def validate_pack(pack_path: Path, whitelist_path: Path | None = None):
    """Validate a pack. Returns (pack_dict, art_dict, report_lines).
    Raises PackError with a named code on the first failure of each class;
    collects everything via validate_pack_report() in the CLI."""
    errors: list[PackError] = []
    report: list[str] = []
    pack = load_json(pack_path)
    families = load_whitelist(whitelist_path)

    def err(code, msg):
        errors.append(PackError(code, msg))

    # -- schema shape --------------------------------------------------
    if not isinstance(pack, dict):
        raise PackError("SCHEMA", "pack root must be a JSON object")
    missing = [k for k in REQUIRED_TOP_KEYS if k not in pack]
    unknown = [k for k in pack if k not in REQUIRED_TOP_KEYS + OPTIONAL_TOP_KEYS]
    if missing:
        err("SCHEMA", f"missing required key(s): {', '.join(missing)}")
    if unknown:
        err("SCHEMA", f"unknown key(s): {', '.join(unknown)}")
    pack_id = pack.get("id")
    if not isinstance(pack_id, str) or not SLUG_RE.match(pack_id or ""):
        err("SCHEMA", f"id must be a lowercase slug, got {pack_id!r}")

    # -- act arithmetic (1-3 acts, ids sequential from 1) --------------
    acts = pack.get("acts")
    if not isinstance(acts, list) or not acts:
        err("ACT-ARITHMETIC", "acts must be a non-empty array")
        acts = []
    if len(acts) > 3:
        err("ACT-ARITHMETIC", f"{len(acts)} acts — a pack carries 1-3 acts (Law 4)")
    for i, act in enumerate(acts, start=1):
        if not isinstance(act, dict):
            err("ACT-ARITHMETIC", f"act #{i} is not an object")
            continue
        if act.get("id") != i:
            err("ACT-ARITHMETIC",
                f"act #{i} has id {act.get('id')!r} — ids must be sequential integers 1..{len(acts)}")
        name = act.get("name")
        if not isinstance(name, str) or not SLUG_RE.match(name or ""):
            err("SCHEMA", f"act #{i}: name must be a slug, got {name!r}")
        tokens = act.get("tokens")
        if not isinstance(tokens, dict) or not tokens:
            err("SCHEMA", f"act #{i}: tokens object required")
            continue
        bad = sorted(set(tokens) - ALLOWED_ACT_TOKENS)
        if bad:
            err("SCHEMA", f"act #{i}: token key(s) outside the §2.2 contract: {', '.join(bad)}")
        for req in REQUIRED_ACT_TOKENS:
            if req not in tokens:
                err("SCHEMA", f"act #{i}: required token {req} missing")

        # -- AA contrast per act pair (WCAG 2.x relative luminance) ----
        # Bars: --mx-ink vs --mx-paper >= 4.5 (body-copy bar — running text
        # renders in ink on the act's paper); --mx-accent vs --mx-paper
        # >= 3.0 (large-display bar — the accent renders only as display
        # type, kickers, chips and rules >= 18.66px bold / 24px, Law 8).
        paper, ink, accent = (tokens.get("--mx-paper"), tokens.get("--mx-ink"),
                              tokens.get("--mx-accent"))
        for label, v in (("--mx-paper", paper), ("--mx-ink", ink), ("--mx-accent", accent)):
            if v is not None and parse_hex(v) is None:
                err("CONTRAST-AA", f"act #{i}: {label} must be plain hex for contrast checking, got {v!r}")
        if all(parse_hex(v) for v in (paper, ink, accent) if v is not None) and paper and ink and accent:
            r_body = contrast_ratio(ink, paper)
            r_disp = contrast_ratio(accent, paper)
            report.append(f"  act {i} ({act.get('name')}): ink/paper {r_body:.2f}:1 (bar 4.5) · "
                          f"accent/paper {r_disp:.2f}:1 (bar 3.0)")
            if r_body < 4.5:
                err("CONTRAST-AA",
                    f"act #{i} ({act.get('name')}): --mx-ink {ink} on --mx-paper {paper} = "
                    f"{r_body:.2f}:1 — below the 4.5:1 body-copy bar")
            if r_disp < 3.0:
                err("CONTRAST-AA",
                    f"act #{i} ({act.get('name')}): --mx-accent {accent} on --mx-paper {paper} = "
                    f"{r_disp:.2f}:1 — below the 3.0:1 large-display bar")

    # -- type roles vs whitelist ---------------------------------------
    typ = pack.get("type")
    if not isinstance(typ, dict):
        err("SCHEMA", "type must be an object with the six roles")
    else:
        missing_roles = [r for r in TYPE_ROLES if r not in typ]
        unknown_roles = [r for r in typ if r not in TYPE_ROLES]
        if missing_roles:
            err("SCHEMA", f"type: missing role(s): {', '.join(missing_roles)}")
        if unknown_roles:
            err("SCHEMA", f"type: unknown role(s): {', '.join(unknown_roles)}")
        for role in TYPE_ROLES:
            fam = typ.get(role)
            if fam is None:
                continue
            if fam not in families:
                err("FONT-WHITELIST",
                    f"type.{role}: \"{fam}\" is not on the whitelist "
                    f"(tools/motif/font-whitelist.json) — packs cannot introduce fonts")
            elif families[fam].get("kind") == "self-hosted":
                for face in families[fam]["faces"]:
                    if not (FONTS_DIR / face["file"]).is_file():
                        err("FONT-WHITELIST",
                            f"type.{role}: \"{fam}\" declares missing file assets/fonts/{face['file']}")

    # -- art slots: bytes + currentColor -------------------------------
    art = {}
    for slot in ("pattern", "glyph", "band", "cover_plate"):
        try:
            svg = resolve_art(pack_path, slot, pack.get(slot))
        except PackError as e:
            errors.append(e)
            svg = None
        art[slot] = svg
        if svg is None:
            continue
        size = len(svg.encode("utf-8"))
        cap = ART_CAPS[slot]
        report.append(f"  art {slot}: {size:,} bytes (cap {cap:,})")
        if size > cap:
            err("ART-BYTE-CAP",
                f"{slot}: SVG source {size:,} bytes exceeds cap {cap:,} bytes")
        if slot in ("pattern", "glyph"):
            try:
                check_currentcolor(slot, svg)
            except PackError as e:
                errors.append(e)

    # -- kit / motion / grain ------------------------------------------
    if pack.get("kit") not in KITS:
        err("KIT", f"kit {pack.get('kit')!r} not in the §2.4 list: {', '.join(KITS)}")
    if pack.get("motion") not in MOTION_TIERS:
        err("MOTION", f"motion {pack.get('motion')!r} must be one of {', '.join(MOTION_TIERS)}")
    if pack.get("grain") not in GRAINS:
        err("GRAIN", f"grain {pack.get('grain')!r} must be one of {', '.join(sorted(GRAINS))}")

    return pack, art, report, errors
