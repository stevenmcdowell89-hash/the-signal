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
      [--build-dir /tmp/signal-build] [--issue-number N] [--skill-dir DIR]

Exit codes: 0 success; 1 assembly/input error (missing content, sp-* leak, etc.)
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


def render_cover(cover, meta, issue_no, stations, dates):
    rng, pretty, _ = dates
    eyebrow = cover.get("eyebrow", "BAND 01 — THE LEAD TRANSMISSION")
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
        st_rows.append(
            f'        <div class="station{oncls}" data-station>\n'
            f'          <span class="freq">{freq}</span>\n'
            f'          <span class="name">{name}</span>\n'
            f'        </div>'
        )
    stations_html = "\n".join(st_rows)

    return f"""
  <!-- ================= COVER ================= -->
  <header class="cover">
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
                        "freq": pc.get("nav_freq", ""),
                        "name_html": pc.get("nav_coverline_html") or esc(pc.get("nav_coverline", "")),
                        "on": bool(pc.get("nav_on")),
                    })

    parts.append(render_cover(plan.get("cover", {}), meta, issue_no, stations, dates))

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

    kb = len(body.encode("utf-8")) / 1024
    print(f"=== weekly stitch OK ===")
    print(f"  Bands rendered: {len(band_order)} (+cover)")
    print(f"  Movements:      {', '.join(mv['id'] for mv in skeleton['movements'])}")
    print(f"  Furniture:      {'mx (design_system=mx)' if mx else 'legacy (none)'}")
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
