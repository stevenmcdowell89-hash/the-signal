#!/usr/bin/env python3
"""stitch_weekly.py — deterministic, skeleton-driven assembly for the standard
weekly (Transmission identity).

The weekly is assembled from THREE inputs:
  1. references/format-skeletons/weekly.json  — the fixed structure (movements,
     bands, order, cardinality). SINGLE SOURCE OF TRUTH for structure.
  2. chapter-plan.json                         — which optional/rotating bands are
     present this issue, per-band coverlines, and the cover copy.
  3. /tmp/signal-build/chapters/<band_id>.html — writer-produced INNER content for
     each present band (the component markup only — no band-head, no movement
     divider; the stitcher owns all chrome).

Because ALL chrome (cover, the four movement dividers, every band-head, the
colophon, the sign-off) is GENERATED HERE from the skeleton, the structural
failure class that shipped on 2026-07-12 (movement bands missing, The Desk
exploded into standalone sections, Release Radar as its own section) is
unrepresentable — the writer cannot affect structure, only fill content.

Output: a complete Transmission weekly matching docs/mockups/
reference-issue-transmission.html, with the weekly-only CSS bundle
(assets/css/weekly/*.css) and the minimal weekly JS (assets/script-weekly.js)
injected. Renders complete with JS off.

Usage:
  python3 stitch_weekly.py --plan PLAN.json --out OUT.html \
      [--build-dir /tmp/signal-build] [--issue-number N] [--skill-dir DIR] \
      [--asset-manifest assets/cached/manifest.json] [--strict-figure-provenance]

Exit codes: 0 success; 1 assembly/input error (missing content, sp-* leak, etc.)

── Coverage rebuild, 2026-07-26 (docs/editorial-coverage-rebuild-SPEC-2026-07-26.md)
The stitcher additionally owns three machine records in the rendered markup
(SPEC §3.4), because they are PLAN decisions the writer must not be able to
contradict:

  * data-vintage on the long-read <section>, plus the .lr-vintage mono line and
    the date-free .byline that an evergreen anchor requires (defect A). The
    .lr-title block itself is writer-authored in this pipeline, so the stitcher
    NORMALISES it rather than generating it — see apply_long_read_vintage().
  * data-cover-leads-on on the cover, and a station list that leads with the
    Long Read when issue_meta.cover_leads_on == "long_read" (defect C).
  * data-shows / data-capture-year / data-licence / data-allows-derivatives on
    every .plate-img, joined from assets/cached/manifest.json (SPEC §3.10) on
    the cached asset's hash (defects B/E). The stitcher can only FILL what the
    manifest knows and REPORT what neither the manifest nor the writer supplied;
    validate-issue.py (WP-4) is the gate. See stamp_figure_provenance().
"""

import argparse
import html as htmlmod
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ── waveform SVG paths (static; the paper-object divider) ─────────────────────
WAVE_PATHS = [
    "M0 13 H60 l6 -10 6 20 6 -20 6 20 6 -20 6 10 H160 l5 -8 5 16 5 -16 5 16 5 -8 H280 l7 -12 7 24 7 -24 7 24 7 -12 H420 l4 -6 4 12 4 -12 4 12 4 -6 H540 l6 -11 6 22 6 -22 6 22 6 -11 H680 l5 -7 5 14 5 -14 5 14 5 -7 H800",
    "M0 13 H40 l5 -9 5 18 5 -18 5 18 5 -9 H120 l7 -13 7 26 7 -26 7 26 7 -13 H260 l4 -6 4 12 4 -12 4 12 4 -6 H360 l6 -11 6 22 6 -22 6 22 6 -11 H500 l5 -8 5 16 5 -16 5 16 5 -8 H620 l7 -13 7 26 7 -26 7 26 7 -13 H800",
    "M0 13 H70 l6 -11 6 22 6 -22 6 22 6 -11 H180 l5 -9 5 18 5 -18 5 18 5 -9 H300 l8 -14 8 28 8 -28 8 28 8 -14 H460 l4 -7 4 14 4 -14 4 14 4 -7 H580 l6 -11 6 22 6 -22 6 22 6 -11 H720 l5 -8 5 16 5 -16 5 16 5 -8 H800",
    "M0 13 H50 l6 -11 6 22 6 -22 6 22 6 -11 H160 l5 -9 5 18 5 -18 5 18 5 -9 H280 l7 -12 7 24 7 -24 7 24 7 -12 H420 l4 -7 4 14 4 -14 4 14 4 -7 H540 l6 -11 6 22 6 -22 6 22 6 -11 H680 l5 -8 5 16 5 -16 5 16 5 -8 H800",
]


def wave(kind, path_idx=0, stroke=2.0, style=""):
    """A full-width waveform rule. kind in {ink, blue, signal-ink}."""
    cls = "wave"
    if kind == "blue":
        cls += " wave--blue"
    elif kind == "ink":
        cls += " wave--ink"
    stylea = f' style="{style}"' if style else ""
    p = WAVE_PATHS[path_idx % len(WAVE_PATHS)]
    return (
        f'  <div class="{cls}" aria-hidden="true"{stylea}>\n'
        f'    <svg viewBox="0 0 800 26" preserveAspectRatio="none">\n'
        f'      <path d="{p}" fill="none" stroke="currentColor" stroke-width="{stroke}"/>\n'
        f'    </svg>\n'
        f'  </div>\n'
    )


def esc(s):
    return htmlmod.escape(s or "", quote=True)


# ── SPEC §3.4 markup contracts (coverage rebuild) ─────────────────────────────

MONTH_ABBR = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

VINTAGE_VALUES = ("news", "evergreen")
COVER_LEADS_ON_VALUES = ("news", "long_read")

# the issue-date stamp inside a .byline — "19 JUL 2026", "5 July 2026"
BYLINE_DATE_RE = re.compile(r"\b(\d{1,2})\s+([A-Za-z]{3,9})\.?\s+(\d{4})\b")

# the .lr-vintage line the stitcher owns (idempotent re-stamping)
LR_VINTAGE_RE = re.compile(r'[ \t]*<div class="mono lr-vintage">.*?</div>\n?',
                           re.DOTALL)

BYLINE_RE = re.compile(r'<p class="mono byline">(.*?)</p>', re.DOTALL)

# a .plate-img opening tag — attributes may precede OR follow class=
PLATE_OPEN_RE = re.compile(r'<div\b[^>]*\bclass="[^"]*\bplate-img\b[^"]*"[^>]*>')

# mirror-images.py names cached files sha256(url)[:12] + extension
CACHED_HASH_RE = re.compile(r"^([0-9a-fA-F]{12})\.[A-Za-z0-9]+$")

FIGURE_PROVENANCE_KEYS = ("data-shows", "data-capture-year",
                          "data-licence", "data-allows-derivatives")

# SPEC §3.3 — the closed `shows` enum. Canonical home is
# references/image-source-types.json → "shows" (WP-6); load_shows_enum() reads it
# and falls back to this literal so the stitcher never depends on that file.
SHOWS_ENUM_FALLBACK = frozenset({
    "event_photo", "gameplay", "in_engine", "key_art", "product_shot", "portrait",
    "diagram", "map", "chart", "artefact", "document",
})


def load_shows_enum(skill_dir):
    try:
        d = json.loads((skill_dir / "references/image-source-types.json").read_text())
        shows = d.get("shows")
        vals = None
        if isinstance(shows, dict):
            vals = shows.get("values") or shows.get("enum") or [
                k for k in shows if not k.startswith("_")]
        elif isinstance(shows, list):
            vals = shows
        vals = {str(v) for v in (vals or []) if isinstance(v, str)}
        if vals:
            return frozenset(vals)
    except (OSError, ValueError, AttributeError):
        pass
    return SHOWS_ENUM_FALLBACK


def _clean_capture_year(v):
    """The rendering of data-capture-year, or None when there is no record.

    Legal: an integer year (1500-2100) → "YYYY"; explicit JSON null → "" (SPEC
    §3.2 allows a null capture year ONLY for a synthetic diagram/chart, and ""
    is how §3.9 sees "no year to compare"). Anything else — notably the literal
    "UNKNOWN" that mirror-images.py back-fills for assets cached before the
    manifest existed — is NOT a record and must render as an ABSENT attribute,
    so validate-issue.py fails the figure instead of reading a placeholder as
    provenance.
    """
    if v is None:
        return ""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return str(v) if 1500 <= v <= 2100 else None
    if isinstance(v, str) and re.fullmatch(r"\d{4}", v.strip()):
        return str(v.strip()) if 1500 <= int(v.strip()) <= 2100 else None
    return None


def month_year(ym):
    """'2021-03' → 'MAR 2021' (the .lr-vintage tail, SPEC §3.4)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})", (ym or "").strip())
    if not m:
        return None
    mo = int(m.group(2))
    if not 1 <= mo <= 12:
        return None
    return f"{MONTH_ABBR[mo - 1]} {m.group(1)}"


def _same_date(token, filed):
    """Is a byline date token the issue's own FILED stamp? Tolerant of
    zero-padding and month-name length ('5 July 2026' == '05 JUL 2026')."""
    a = BYLINE_DATE_RE.search(token or "")
    b = BYLINE_DATE_RE.search(filed or "")
    if not a or not b:
        return False
    return (int(a.group(1)) == int(b.group(1))
            and a.group(2)[:3].upper() == b.group(2)[:3].upper()
            and a.group(3) == b.group(3))


def apply_long_read_vintage(content, vintage, chapter, filed):
    """Stamp the Long Read's vintage chrome into the .lr-title block (SPEC §3.4).

    Defect A: with no vintage field the pipeline stamped the issue date on every
    anchor, so an evergreen feature read as "they've just discovered this".

    In THIS pipeline the writer authors the .lr-title block itself (see
    references/golden/*/chapters/long_read.html) — the stitcher owns the
    <section> wrapper, the band-head and the movement divider around it. The
    vintage line and the byline date are plan decisions, not writing decisions,
    so the stitcher normalises them here:

      evergreen → insert `<div class="mono lr-vintage">NOT THIS WEEK · A STANDING
                  STORY · <material_span> · LATEST DEVELOPMENT <MON YYYY></div>`
                  immediately before the <h2>, and strip the issue date out of
                  the .byline (replacing it with "· A STANDING STORY").
      news      → no .lr-vintage; the .byline carries today's date.

    Idempotent: any pre-existing .lr-vintage is removed before re-stamping.
    """
    content = LR_VINTAGE_RE.sub("", content)

    if vintage == "evergreen":
        span = str(chapter.get("material_span") or "").strip()
        latest = str(chapter.get("latest_development") or "").strip()
        my = month_year(latest)
        if not span or not my:
            die("The long_read chapter declares vintage='evergreen' but the plan "
                "is missing a usable material_span / latest_development "
                f"(material_span={span!r}, latest_development={latest!r}). "
                "SPEC §3.1 requires both when evergreen; latest_development is "
                "YYYY-MM. The .lr-vintage line (SPEC §3.4) cannot be built "
                "without them.")
        anchor = re.search(r"([ \t]*)<h2\b", content)
        if anchor is None:
            die("The long_read content has no <h2> — the stitcher cannot place "
                "the .lr-vintage line (SPEC §3.4 puts it between the mono kicker "
                "and the headline inside .lr-title).")
        indent = anchor.group(1)
        line = (f'{indent}<div class="mono lr-vintage">NOT THIS WEEK · '
                f'A STANDING STORY · {esc(span)} · LATEST DEVELOPMENT {my}</div>\n')
        content = content[:anchor.start()] + line + content[anchor.start():]

    def _byline(m):
        inner = m.group(1)
        if vintage == "evergreen":
            # SPEC §3.4: the byline MUST NOT contain the issue date.
            inner = BYLINE_DATE_RE.sub("", inner)
            inner = re.sub(r"(\s*·\s*)+", " · ", inner).strip().strip("·").strip()
            if "A STANDING STORY" not in inner.upper():
                inner = f"{inner} · A STANDING STORY"
        else:
            # SPEC §3.4: a news anchor keeps `· DD MON YYYY` as today.
            tok = BYLINE_DATE_RE.search(inner)
            if tok is None:
                inner = f"{inner.strip().strip('·').strip()} · {filed}"
            elif not _same_date(tok.group(0), filed):
                inner = BYLINE_DATE_RE.sub(filed, inner, count=1)
        return f'<p class="mono byline">{inner}</p>'

    content, n = BYLINE_RE.subn(_byline, content)
    if n == 0:
        print("  ! long_read has no <p class=\"mono byline\"> — the vintage "
              "byline contract (SPEC §3.4) could not be applied.")
    return content


def load_asset_manifest(path):
    """assets/cached/manifest.json (SPEC §3.10, written by WP-8's
    mirror-images.py): {"<sha256[:12]>": {shows, capture_year, licence{…}, …}}.
    Absent or unreadable → {} (the stitcher warns; it never invents provenance).
    """
    if not path or not Path(path).exists():
        return {}, f"absent ({path})"
    try:
        data = json.loads(Path(path).read_text())
    except (ValueError, OSError) as e:
        return {}, f"unreadable ({e})"
    if not isinstance(data, dict):
        return {}, "not an object"
    return data, f"{len(data)} asset[s]"


def stamp_figure_provenance(body, manifest, shows_enum=SHOWS_ENUM_FALLBACK):
    """Fill the §3.4 figure-provenance record on every .plate-img.

    Defects B/E. The four attributes are a machine record of the *asset*, not of
    the prose, so their home is assets/cached/manifest.json (SPEC §3.10) keyed by
    the sha256(url)[:12] that mirror-images.py already uses as the cached
    filename. The writer's <img src="/assets/cached/<hash>.jpg"> therefore joins
    straight onto it, and the stitcher stamps the attributes rather than asking
    the writer to hand-copy licence codes into markup.

    Precedence: a writer-authored attribute ALWAYS wins (it is an explicit
    authorial claim). The stitcher only fills what is absent, only from the
    manifest, and never invents a value.

    Returns (body, stamped_count, plate_count, gaps) where gaps is a list of
    (src, [missing keys]) for every figure still short of the full record —
    validate-issue.py (WP-4) is the gate that fails on those.
    """
    out, pos = [], 0
    stamped = plates = 0
    gaps = []
    for m in PLATE_OPEN_RE.finditer(body):
        plates += 1
        tag = m.group(0)
        im = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', body[m.end():m.end() + 4000])
        src = im.group(1) if im else ""
        entry = {}
        if src:
            hm = CACHED_HASH_RE.match(src.split("/")[-1].split("?")[0])
            if hm:
                entry = manifest.get(hm.group(1).lower(), {}) or {}
        if not isinstance(entry, dict):
            entry = {}

        # A PLACEHOLDER IS NOT A RECORD. mirror-images.py honestly back-fills
        # "UNKNOWN" / null for the ~438 assets cached before the manifest existed
        # (their source URLs are unrecoverable — sha256 is one-way). Stamping
        # those would turn "we do not know" into a rendered provenance claim, and
        # would hand WP-4 a data-capture-year it cannot compare and a
        # data-allows-derivatives="false" nobody established. So each field is
        # stamped ONLY when the manifest holds a real value; otherwise the
        # attribute stays absent and the figure is reported as a gap, which is
        # what makes validate-issue.py fail it.
        fill = {}
        shows = entry.get("shows")
        if isinstance(shows, str) and shows in shows_enum:
            fill["data-shows"] = shows
        if "capture_year" in entry:
            cy = _clean_capture_year(entry["capture_year"])
            if cy is not None:
                fill["data-capture-year"] = cy
        lic = entry.get("licence") if isinstance(entry.get("licence"), dict) else {}
        code = lic.get("code")
        if isinstance(code, str) and code.strip() and code.strip().upper() != "UNKNOWN":
            fill["data-licence"] = code.strip()
        if isinstance(lic.get("allows_derivatives"), bool):
            fill["data-allows-derivatives"] = "true" if lic["allows_derivatives"] else "false"

        add = [f'{k}="{esc(v)}"' for k, v in
               ((k, fill[k]) for k in FIGURE_PROVENANCE_KEYS if k in fill)
               if not re.search(r"\s" + re.escape(k) + r"\s*=", tag)]
        if add:
            tag = tag[:-1].rstrip() + " " + " ".join(add) + ">"
            stamped += 1

        missing = [k for k in FIGURE_PROVENANCE_KEYS
                   if not re.search(r"\s" + re.escape(k) + r"\s*=", tag)]
        if missing:
            gaps.append((src or "(no <img> found)", missing))

        out.append(body[pos:m.start()])
        out.append(tag)
        pos = m.end()
    out.append(body[pos:])
    return "".join(out), stamped, plates, gaps


def compute_dates(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return ("[DATE RANGE]", "[Date]", "")
    pretty = d.strftime("%-d %B %Y")
    start = d - timedelta(days=6)
    if start.month == d.month:
        rng = f"{start.day}–{d.day} {d.strftime('%b %Y')}".upper()
    else:
        rng = f"{start.strftime('%-d %b')}–{d.strftime('%-d %b %Y')}".upper()
    return (rng, pretty, d.strftime("%d %b %Y").upper())


# ── chrome generators ─────────────────────────────────────────────────────────

def render_head(title, body_attrs=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<!-- INJECT:CSS -->
</head>
<body{body_attrs}>
<div class="issue">
"""


def render_cover(cover, meta, issue_no, stations, dates, leads_on="news"):
    rng, pretty, _ = dates
    # SPEC §3.4/§3.1 (defect C): the cover declares what it leads on. The copy
    # stays the planner's — the stitcher only supplies the eyebrow DEFAULT and
    # the declaration, never editorial wording.
    default_eyebrow = ("BAND 01 — THE LEAD TRANSMISSION · THE LONG READ"
                       if leads_on == "long_read" else
                       "BAND 01 — THE LEAD TRANSMISSION")
    eyebrow = cover.get("eyebrow", default_eyebrow)
    lead_head = cover.get("lead_head_html") or esc(cover.get("lead_head", ""))
    standfirst = esc(cover.get("standfirst", ""))
    tagline = esc(cover.get("tagline", "tuning in to the week you lived"))
    location = esc(meta.get("location", "NORTHERN IRELAND")).upper()
    reading = esc(meta.get("reading_time", "ONE SITTING")).upper()
    no3 = str(issue_no).zfill(3) if issue_no else ""

    # tuner station list — one row per nav band present, in nav order
    st_rows = []
    for s in stations:
        oncls = " on" if s.get("on") else ""
        freq = esc(s.get("freq", ""))
        name = s.get("name_html") or esc(s.get("name", ""))
        # NOTE: the attribute is data-NAV-band, not data-station-band. Any
        # data-station* name would be double-counted by validate-issue.py's
        # navigator tally (re.findall(r"\bdata-station\b") — "-" is a word
        # boundary, so data-station-band matches it too and every station
        # counted twice, tripping the <=13 ceiling on a 7-station issue).
        band_attr = f' data-nav-band="{esc(s.get("band", ""))}"' if s.get("band") else ""
        st_rows.append(
            f'        <div class="station{oncls}" data-station{band_attr}>\n'
            f'          <span class="freq">{freq}</span>\n'
            f'          <span class="name">{name}</span>\n'
            f'        </div>'
        )
    stations_html = "\n".join(st_rows)

    return f"""
  <!-- ================= COVER ================= -->
  <header class="cover" data-cover-leads-on="{esc(leads_on)}">
    <div class="cover__top">
      <span class="mono">A Personal Weekly · Received &amp; Tuned</span>
      <span class="mono price">Sunday Edition</span>
    </div>
{wave("ink", 0, 2.0)}
    <h1 class="masthead">The <em>Signal</em></h1>
    <div class="masthead__sub">
      <span class="tag">{tagline}</span>
      <span class="mono">EST. 2026</span>
    </div>

    <div class="cover__body">
      <div class="lead">
        <div class="mono lead__eyebrow">{esc(eyebrow)}</div>
        <h2 class="lead__head">{lead_head}</h2>
        <p class="lead__stand">{standfirst}</p>
      </div>

      <nav class="tuner" aria-label="In this transmission">
        <div class="tuner__label">
          <span class="mono">STATION LIST</span>
          <span class="mono">№{no3}</span>
        </div>
{stations_html}
      </nav>
    </div>

    <div class="dataline">
      <span class="mono">TRANSMISSION №{no3}</span>
      <span class="dot" aria-hidden="true">·</span>
      <span class="mono">{rng}</span>
      <span class="dot" aria-hidden="true">·</span>
      <span class="mono">{location}</span>
      <span class="dot" aria-hidden="true">·</span>
      <span class="mono">FOLIO {no3}</span>
      <span class="dot" aria-hidden="true">·</span>
      <span class="mono">{reading}</span>
    </div>

    <div class="folio" aria-hidden="true">{no3}</div>
  </header>

{wave("blue", 1, 1.5, style="padding:0 40px;")}"""


def render_movement(mv):
    return f"""
  <!-- MOVEMENT {esc(mv['numeral'])} · {esc(mv['name'].upper())} -->
  <div class="movement" data-movement="{esc(mv['id'])}">
    <div class="movement__rule">
      <span class="movement__no">{esc(mv['numeral'])}</span>
      <span class="movement__name">{esc(mv['name'])}</span>
      <span class="mono movement__meta">{esc(mv['meta'])}</span>
    </div>
  </div>
"""


def render_bandhead(band_no, band_id, name, runtime):
    return f"""
  <div class="band" data-band="{esc(band_id)}">
    <div class="bandhead">
      <span class="mono code">BAND {band_no:02d} — <b>{esc(name.upper())}</b></span>
      <span class="mono runtime">{esc(runtime.upper())}</span>
    </div>
  </div>
"""


def die(msg):
    print(f"═══ WEEKLY STITCH FAILED ═══\n{msg}", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--build-dir", default="/tmp/signal-build")
    ap.add_argument("--issue-number", default="")
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--asset-manifest", default="",
                    help="assets/cached/manifest.json (SPEC §3.10) — the source of "
                         "the §3.4 figure-provenance attributes. Defaults to "
                         "<repo>/assets/cached/manifest.json when it exists.")
    ap.add_argument("--strict-figure-provenance", action="store_true",
                    help="fail the stitch when any .plate-img is short of the full "
                         "§3.4 provenance record (default: report and continue — "
                         "validate-issue.py is the ship gate).")
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir)
    plan = json.loads(Path(args.plan).read_text())
    skeleton = json.loads((skill_dir / "references/format-skeletons/weekly.json").read_text())
    chapters_dir = Path(args.build_dir) / "chapters"
    css_dir = skill_dir / "assets/css/weekly"
    js_file = skill_dir / "assets/script-weekly.js"

    meta = plan.get("issue_meta", {})
    if meta.get("format") != "weekly":
        die("stitch_weekly.py invoked on a non-weekly plan.")
    issue_no = args.issue_number or str(meta.get("issue_number", "") or "")
    dates = compute_dates(meta.get("date", ""))
    title = f"The Signal — Transmission №{str(issue_no).zfill(3)}" if issue_no else "The Signal — Weekly"

    # WP-8 · furniture layer (opt-in). A weekly plan may set
    #   "issue_meta": { … "design_system": "mx" }
    # to load the core-furniture add-on so the issue reaches its Law-2 density
    # budget (fixtures ledger, ticket, standings card, quote-objects, chart
    # card). The IDENTITY IS UNTOUCHED (Law 11): same masthead, same 800px
    # chassis, same three faces — the furniture arrives dressed through the
    # transmission alias. Absent the flag the weekly is byte-identical to the
    # pre-WP-8 generator (the legacy golden path). data-motion="tier1" is the
    # calm weekly tier (rise/settle/ticks/dial-sweep via mx-motion.js).
    mx = str(meta.get("design_system", "")).lower() == "mx"
    # data-mx-chrome="pill" arms the CSS scroll-timeline that fades the fixed
    # back-pill out past the masthead (Law 10: fixed chrome never overlaps
    # content at depth). See weekly-mx/10-mx-weekly.css §00a.
    body_attrs = (' data-skin="transmission" data-mx data-motion="tier1"'
                  ' data-format="weekly" data-mx-chrome="pill"') if mx else ""

    # present bands: from the plan's chapters[] (each chapter_id is a band_id)
    present = {c["chapter_id"]: c for c in plan.get("chapters", [])}
    bands_def = skeleton["bands"]

    # ── SPEC §3.1/§3.4 · cover lead (defect C) ───────────────────────────────
    # issue_meta.cover_leads_on ∈ {news, long_read}. When long_read, the cover's
    # station list LEADS with the Long Read (hoisted to the top of the tuner and
    # tuned ON) and the eyebrow default names it. Absent → "news", which is the
    # historical behaviour; validate-chapter-plan.py (WP-5) is the gate that
    # requires the field on a real weekly plan.
    leads_on = str(meta.get("cover_leads_on") or "news").strip().lower()
    if leads_on not in COVER_LEADS_ON_VALUES:
        die(f"issue_meta.cover_leads_on={meta.get('cover_leads_on')!r} is not one of "
            f"{list(COVER_LEADS_ON_VALUES)} (SPEC §3.1).")
    if "cover_leads_on" not in meta:
        print("  ! issue_meta.cover_leads_on absent — defaulting to \"news\" "
              "(SPEC §3.1 requires it on a weekly plan; WP-5's plan validator "
              "is the gate).")

    # ── SPEC §3.1/§3.4 · Long Read vintage (defect A) ────────────────────────
    lr_chapter = present.get("long_read", {})
    vintage = str(lr_chapter.get("vintage") or "").strip().lower()
    if not vintage:
        vintage = "news"
        print("  ! long_read.vintage absent — defaulting to \"news\" (the "
              "status-quo rendering: dated byline, no .lr-vintage). SPEC §3.1 "
              "requires it; validate-chapter-plan.py (WP-5) is the gate.")
    elif vintage not in VINTAGE_VALUES:
        die(f"long_read.vintage={lr_chapter.get('vintage')!r} is not one of "
            f"{list(VINTAGE_VALUES)} (SPEC §3.1).")

    # --- assemble body ---
    parts = [render_head(title, body_attrs)]

    # cover — stations built from nav bands present, in skeleton order
    stations = []
    band_order = []  # (movement, band_id) in skeleton order for present bands
    for mv in skeleton["movements"]:
        for band_id in mv["bands"]:
            if band_id not in bands_def:
                continue
            bdef = bands_def[band_id]
            is_present = bdef.get("required") or band_id in present
            if not is_present:
                continue
            band_order.append((mv, band_id))
            if bdef.get("nav") and band_id in present:
                pc = present[band_id]
                if pc.get("nav_coverline") or pc.get("nav_coverline_html"):
                    stations.append({
                        "band": band_id,
                        "freq": pc.get("nav_freq", ""),
                        "name_html": pc.get("nav_coverline_html") or esc(pc.get("nav_coverline", "")),
                        "on": bool(pc.get("nav_on")),
                    })

    # SPEC §3.1 · cover_leads_on="long_read": the station list leads with the
    # Long Read rather than following skeleton order (defect C — a demoted news
    # lead must not still occupy the top of the tuner).
    if leads_on == "long_read":
        lr_idx = next((i for i, s in enumerate(stations) if s.get("band") == "long_read"), None)
        if lr_idx is None:
            die("issue_meta.cover_leads_on=\"long_read\" but the plan gives the "
                "long_read chapter no nav_coverline — the cover cannot lead on a "
                "station that does not exist. Add nav_coverline/nav_freq to the "
                "long_read chapter.")
        lr_station = stations.pop(lr_idx)
        lr_station["on"] = True
        stations.insert(0, lr_station)

    parts.append(render_cover(plan.get("cover", {}), meta, issue_no, stations, dates,
                              leads_on=leads_on))

    # movements + bands, numbered sequentially (cover is BAND 01 conceptually)
    band_no = 1  # BAND 01 = the lead transmission on the cover
    wave_idx = 2
    current_movement = None
    for mv, band_id in band_order:
        if current_movement != mv["id"]:
            # close previous movement with a wave rule (except before the very first)
            if current_movement is not None:
                parts.append(wave("ink", wave_idx, 2.0, style="margin-top:26px;color:var(--signal);"))
                wave_idx += 1
            parts.append(render_movement(mv))
            current_movement = mv["id"]

        bdef = bands_def[band_id]
        band_no += 1
        parts.append(render_bandhead(band_no, band_id, bdef["name"], bdef.get("runtime", "")))

        # writer content for this band
        content = ""
        cf = chapters_dir / f"{band_id}.html"
        if cf.exists():
            content = cf.read_text()
        elif bdef.get("required"):
            die(f"Required band '{band_id}' has no content file at {cf}. "
                f"A required weekly band cannot be empty.")
        else:
            continue

        # structural hooks: wrap content so the gate finds stable data-role anchors
        role = {"long_read": "long-read", "the_desk": "desk"}.get(band_id)
        section_attrs = f' data-role="{role}"' if role else ""
        if band_id == "long_read":
            # SPEC §3.4: data-vintage is ALWAYS present on the long-read section.
            section_attrs += f' data-vintage="{esc(vintage)}"'
            content = apply_long_read_vintage(content, vintage, lr_chapter, dates[2])
        if band_id == "the_letter" and vintage == "evergreen" \
                and 'data-lr-framing="feature"' not in content:
            # SPEC §3.4: the Letter paragraph that introduces an evergreen anchor
            # carries data-lr-framing="feature". It is a PROSE paragraph the
            # writer authors — the stitcher cannot know which one, so it reports
            # and validate-issue.py (WP-4) is the gate.
            print("  ! the_letter carries no data-lr-framing=\"feature\" while the "
                  "Long Read is evergreen (SPEC §3.4). The framing paragraph is "
                  "writer-authored; validate-issue.py is the gate.")
        # section class from the band's content kind (mirrors the reference)
        sec_cls = {
            "letter": "letter", "figures": "", "digest": "caughtup",
            "longread": "longread", "round": "round", "desk": "round",
            "threads": "", "rabbit": "", "radar": "", "closepin": "", "colophon": "",
        }.get(bdef.get("content"), "")
        cls_attr = f' class="{sec_cls}"' if sec_cls else ""
        parts.append(f'  <section{cls_attr}{section_attrs}>\n{content.rstrip()}\n  </section>\n')

    # close final movement + colophon footer + signoff
    parts.append(wave("ink", wave_idx, 2.0, style="margin-top:30px;color:var(--signal);"))
    parts.append(render_colophon_footer(meta, issue_no, dates))
    parts.append("\n</div>\n<!-- INJECT:JS -->\n</body>\n</html>\n")

    body = "".join(parts)

    # --- SPEC §3.4/§3.10 · figure provenance on every .plate-img ---
    manifest_path = args.asset_manifest
    if not manifest_path:
        # <repo>/assets/cached/manifest.json — skill_dir is <repo>/.claude/skills/the-signal
        guess = skill_dir.parents[2] / "assets/cached/manifest.json" \
            if len(skill_dir.resolve().parents) >= 3 else None
        manifest_path = str(guess) if guess else ""
    manifest, manifest_note = load_asset_manifest(manifest_path)
    body, fig_stamped, fig_plates, fig_gaps = stamp_figure_provenance(
        body, manifest, load_shows_enum(skill_dir))

    # --- inject the "Return to The Signal" back-link pill (self-styled) ---
    back_path = skill_dir / "assets/template-parts/back-link.html"
    if back_path.exists() and "<!-- the-signal:back -->" not in body:
        back = back_path.read_text().rstrip() + "\n"
        # body tag may carry mx attributes (WP-8) — match the tag, keep attrs
        body = re.sub(r"(<body\b[^>]*>\n)", lambda m: m.group(1) + back, body, count=1)

    # --- weekly-format gate: ban special .sp-* vocabulary ---
    _weekly_sp_gate(body)

    # --- inject CSS + JS ---
    css_files = sorted(css_dir.glob("*.css"))
    if not css_files:
        die(f"No weekly CSS found in {css_dir}")
    # WP-8: on the furniture layer, append the transmission alias (maps --mx-*
    # onto the weekly tokens) then the curated furniture add-on. Order matters
    # — the alias must precede the components so tokens resolve. Legacy weeklies
    # bundle ONLY weekly/*.css (identical to before).
    if mx:
        alias = skill_dir / "assets/css/skins/skin-transmission.css"
        if alias.exists():
            css_files = css_files + [alias]
        css_files = css_files + sorted((skill_dir / "assets/css/weekly-mx").glob("*.css"))
    css_content = "\n".join(f.read_text() for f in css_files)

    js_content = js_file.read_text() if js_file.exists() else ""
    if mx:
        # add the motion controller ALONGSIDE the existing image-error fallback
        # (never replacing it — the weekly's JS-off paper contract is intact).
        motion_js = skill_dir / "assets/mx-motion.js"
        if motion_js.exists():
            js_content = js_content + "\n" + motion_js.read_text()

    body = body.replace("<!-- INJECT:CSS -->", f"<style>\n{css_content}\n</style>", 1)
    body = body.replace("<!-- INJECT:JS -->", f"<script>\n{js_content}\n</script>", 1)

    # --- placeholder substitution (idempotent; templates ship clean but belt-and-braces) ---
    rng, pretty, _ = dates
    body = body.replace("[DATE RANGE]", rng).replace("[Date]", pretty)
    body = body.replace("[YEAR]", pretty.split()[-1] if pretty and pretty != "[Date]" else "")
    if issue_no:
        body = body.replace("[N]", str(issue_no))

    # --- write + verify ---
    out = Path(args.out)
    out.write_text(body, encoding="utf-8")
    if "<!-- INJECT:CSS -->" in body or "<!-- INJECT:JS -->" in body:
        die("CSS/JS injection markers survived — injection failed.")
    if "<style>" not in body or "<div class=\"issue\">" not in body:
        die("Missing <style> or .issue wrapper in output.")

    # --- SPEC §3.4 figure-provenance report (WP-4's gate is the ship gate) ---
    if fig_gaps:
        msg = (f"{len(fig_gaps)} of {fig_plates} .plate-img figure[s] are short of the "
               f"SPEC §3.4 provenance record (data-shows / data-capture-year / "
               f"data-licence / data-allows-derivatives). The stitcher fills these "
               f"from the asset manifest ({manifest_note}); a figure whose src is "
               f"not a mirrored /assets/cached/<hash> asset, or whose hash has no "
               f"manifest entry, must carry them in the writer's own markup:\n"
               + "\n".join(f"  • {src} — missing {', '.join(ks)}" for src, ks in fig_gaps))
        if args.strict_figure_provenance:
            die(msg)
        print("  ! " + msg)

    kb = len(body.encode("utf-8")) / 1024
    print(f"=== weekly stitch OK ===")
    print(f"  Bands rendered: {len(band_order)} (+cover)")
    print(f"  Movements:      {', '.join(mv['id'] for mv in skeleton['movements'])}")
    print(f"  Furniture:      {'mx (design_system=mx)' if mx else 'legacy (none)'}")
    print(f"  Cover leads on: {leads_on}")
    print(f"  Long Read:      vintage={vintage}"
          + (f" · {lr_chapter.get('material_span')} · latest {lr_chapter.get('latest_development')}"
             if vintage == "evergreen" else ""))
    print(f"  Fig provenance: {fig_plates - len(fig_gaps)}/{fig_plates} complete "
          f"({fig_stamped} stamped from the manifest: {manifest_note})")
    print(f"  CSS:            {len(css_content.encode('utf-8'))/1024:.1f} KB ({len(css_files)} file[s])")
    print(f"  JS:             {len(js_content.encode('utf-8'))/1024:.1f} KB")
    print(f"  Output:         {out} ({kb:.1f} KB)")


def render_colophon_footer(meta, issue_no, dates):
    rng, pretty, filed = dates
    no = str(issue_no) if issue_no else ""
    nxt = str(int(issue_no) + 1).zfill(3) if str(issue_no).isdigit() else ""
    return f"""
  <div class="colophon">
    <span class="serif">The <em>Signal</em></span>
    <span class="mono">END OF TRANSMISSION №{str(issue_no).zfill(3)} · UNTIL NEXT SUNDAY</span>
  </div>

  <div class="signoff-line">
{wave("blue", 3, 1.5, style="max-width:200px;margin:0 auto;")}
    <p class="big">Until next Sunday — the week will <em>keep</em>.</p>
    <p class="mono stamp">SET IN INSTRUMENT SERIF, NEWSREADER &amp; JETBRAINS MONO · FILED {filed} · FOR ONE READER</p>
  </div>
"""


def _weekly_sp_gate(body):
    ALLOWED = {"sp-chapter-beads", "sp-wipe-layer", "sp-word", "sp-fade"}
    found = {}
    for m in re.finditer(r'class="[^"]*?\b(sp-[a-z][a-z0-9-]*)\b', body, re.IGNORECASE):
        tok = m.group(1)
        if tok in ALLOWED:
            continue
        found[tok] = found.get(tok, 0) + 1
    if found:
        die("Weekly uses special .sp-* vocabulary (scoped to body.is-special; "
            "renders unstyled on a weekly):\n" +
            "\n".join(f"  • {t} ×{n}" for t, n in sorted(found.items())))


if __name__ == "__main__":
    main()
