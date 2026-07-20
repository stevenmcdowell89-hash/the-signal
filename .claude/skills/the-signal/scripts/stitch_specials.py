#!/usr/bin/env python3
"""stitch_specials.py — deterministic, skeleton-driven assembly for NEW-SYSTEM
(data-mx) special editions (WP-6). Sibling of stitch_weekly.py: same
architecture, applied to the unified design system.

A special is assembled from THREE inputs:
  1. references/format-skeletons/<format>.json — the fixed structure (slots,
     acts policy, killer features, motion tier, skin). SINGLE SOURCE OF TRUTH.
  2. chapter-plan.json (validated by validate-chapter-plan.py, which enforces
     the skeleton) — which slots run, act declarations, cover copy, kit.
  3. <build-dir>/chapters/<chapter_id>.html — writer-produced INTERIOR content
     only: body copy, quote contents, ledger rows, kit objects. NO chrome.

Because ALL chrome (masthead, cover, act openers, transit seams, chapter
plates, back pill, footer/colophon) is GENERATED HERE from the skeleton, the
attempt-#2 failure class (hand-rolled chrome, fixed-pill overlap, cover meta
leaking strategy vocabulary) is unrepresentable: a writer file containing
masthead/cover/act markup is REJECTED, not absorbed.

Bundling follows the stitch-issue.sh data-mx path (WP-3): per-skin CSS
manifest (core + one skin, byte-budgeted, one-masthead gate), the mx-motion.js
controller (WP-5), self-hosted fonts only. Motif packs (WP-4) inject at the
<!-- INJECT:MX-PACK --> marker in this stitcher's head template, and a pack's
cover_plate <template> is CONSUMED into the cover's .mx-cover__plate slot
(closing WP-4 gap #2).

Usage:
  python3 stitch_specials.py --plan PLAN.json --out OUT.html
      [--build-dir /tmp/signal-build] [--skill-dir DIR] [--pack PACK.json]

Exit codes: 0 success; 1 assembly/input/gate error.
"""

import argparse
import html as htmlmod
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Law-2 census vocabulary (core-components.md §4)
MX_EVENT_TYPES = {
    "figure", "ephemera", "ledger", "statband", "quote",
    "plate", "chart", "marquee", "cheatsheet",
}

# ── writer-file gates ────────────────────────────────────────────────────────
# Chrome vocabulary a writer interior may NEVER contain — the stitcher owns it.
CHROME_BANNED = [
    ("document scaffold", re.compile(r"<!DOCTYPE|<html\b|</html>|<head\b|</head>|<body\b|</body>", re.I)),
    ("style/script blocks", re.compile(r"<style\b|<script\b", re.I)),
    ("masthead (.mx-mast)", re.compile(r'class="[^"]*\bmx-mast\b')),
    ("cover (.mx-cover*)", re.compile(r'class="[^"]*\bmx-cover\b')),
    ("act opener (.mx-actopen)", re.compile(r'class="[^"]*\bmx-actopen\b')),
    ("transit seam (.mx-transit)", re.compile(r'class="[^"]*\bmx-transit\b')),
    ("chapter plate (.mx-plate)", re.compile(r'class="[^"]*\bmx-plate\b')),
    ("kicker strip (.mx-kickerstrip)", re.compile(r'class="[^"]*\bmx-kickerstrip\b')),
    ("footer/colophon", re.compile(r'class="[^"]*\b(?:mx-footer|mx-colophon)\b')),
    ("act declaration (data-act)", re.compile(r"\bdata-act\s*=")),
    ("back pill", re.compile(r"signal-back-to-archive|<!--\s*the-signal:")),
    ("injection markers", re.compile(r"<!--\s*INJECT:")),
]

# Legacy vocabularies undefined in an mx bundle (they'd render unstyled).
LEGACY_CLASS_RE = re.compile(r'class="[^"]*?\b((?:sp|hol)-[a-z][a-z0-9-]*)\b', re.I)

# ── per-skin vocabulary gate ─────────────────────────────────────────────────
# The event/editorial split, derived from core-components.md + skin-event.css:
# marquees, countdown grids, the --loud chunk-voice variants, and the event
# halves/horizon rhythm are EVENT-SKIN furniture (the "loud" register, Law 11:
# editorial keeps bookish gravitas — motif surface capped). An editorial
# issue's writer files must not reach for them.
EVENT_ONLY_CLASS_RE = re.compile(
    r'class="[^"]*?\b('
    r"mx-marquee(?:__[a-z-]+)?|"
    r"mx-countdown(?:__[a-z-]+)?|"
    r"mx-numbers--loud|"
    r"mx-plate--loud|"
    r"mx-half|"
    r"mx-ground-horizon"
    r')\b'
)

INJECT_CSS = "<!-- INJECT:CSS -->"
INJECT_JS = "<!-- INJECT:JS -->"
INJECT_PACK = "<!-- INJECT:MX-PACK -->"
COVER_PLATE_MARK = "<!-- MXS:COVER-PLATE -->"

FORMAT_LABELS = {
    "season_review": "Season Review", "deep_dive": "Deep Dive",
    "versus": "Versus", "rewind": "Rewind", "guide": "The Guide",
    "next": "The Next", "countdown": "The Countdown", "field_guide": "Field Guide",
}

ROMAN = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]

SKELETON_FILES = {
    "season_review": "season-review.json",
    "deep_dive": "deep-dive.json",
    "versus": "versus.json",
    "rewind": "rewind.json",
}


def esc(s):
    return htmlmod.escape(str(s or ""), quote=True)


def die(msg):
    print(f"═══ SPECIALS STITCH FAILED ═══\n{msg}", file=sys.stderr)
    sys.exit(1)


def pretty_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%-d %B %Y")
    except (ValueError, TypeError):
        return "[Date]"


# ── chrome generators (stitcher-owned; writers can never produce these) ──────

def render_head(title, description):
    """Head template. Order matters: bundle CSS first, per-issue act tokens,
    then the INJECT:MX-PACK marker LAST so pack tokens win the cascade
    (render-motif-pack.py injects at this marker). PWA block matches
    scripts/inject-pwa.py's snippet so the post-publish injector is a no-op."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{INJECT_CSS}
<!-- INJECT:MX-ACT-TOKENS -->
{INJECT_PACK}
<!-- the-signal:pwa -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#E94560">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png">
<script>
  if ('serviceWorker' in navigator) {{
    window.addEventListener('load', function () {{
      navigator.serviceWorker.register('/sw.js').catch(function (err) {{
        console.warn('SW registration failed:', err);
      }});
    }});
  }}
</script>
<!-- /the-signal:pwa -->
</head>
"""


def render_mast(fmt_label, topic, pdate):
    return f"""
<header class="mx-mast">
  <span class="mx-mast__title">The Signal<span class="mx-mast__stop">.</span></span>
  <span class="mx-mast__badge">{esc(fmt_label)}</span>
  <span class="mx-mast__meta">{esc(topic)} · {esc(pdate)}</span>
</header>
"""


def render_cover(cover, skeleton, acts, fmt_label, first_act):
    """Format-owned cover gesture (Law 7). Poster class comes from the
    skeleton; the ghost is the format's owned mark (season code / year band /
    numeral). ≥3 voices by construction: script overline + display title +
    mono sig."""
    cover_cls = skeleton.get("cover", {}).get("class", "mx-cover")
    grounds = " ".join(first_act.get("grounds", []))
    title_html = cover.get("title_html") or esc(cover.get("title", ""))
    ghost = esc(cover.get("ghost", ""))
    script_ghost = esc(cover.get("script_ghost", ""))
    overline = esc(cover.get("overline", ""))
    dek = esc(cover.get("dek", ""))
    pills = "".join(
        f"<span>Act {ROMAN[i + 1]} · {esc(a.get('title', a.get('name', '')))}</span>"
        for i, a in enumerate(acts)
    )
    ghost_html = f'\n  <div class="mx-cover__ghost" aria-hidden="true">{ghost}</div>' if ghost else ""
    sghost_html = (f'\n  <div class="mx-cover__script-ghost" aria-hidden="true">{script_ghost}</div>'
                   if script_ghost else "")
    return f"""
<section class="{cover_cls} {grounds}" data-act="{esc(first_act['name'])}">{ghost_html}{sghost_html}
  <div class="mx-cover__inner">
    <div class="mx-cover__sig">
      <span>The Signal<span class="mx-mast__stop">.</span></span>
      <span>{esc(fmt_label)}</span>
      <span>{esc(cover.get('sig_right', ''))}</span>
    </div>
    <span class="mx-cover__overline">{overline}</span>
    <h1 class="mx-cover__title">{title_html}</h1>
    {COVER_PLATE_MARK}
    <p class="mx-cover__dek">{dek}</p>
    <div class="mx-cover__pills">{pills}</div>
  </div>
</section>
"""


def render_actopen(idx, act):
    hand = esc(act.get("hand", ""))
    hand_html = f'\n  <span class="mx-actopen__hand">{hand}</span>' if hand else ""
    return f"""
<header class="mx-actopen" data-mx-event="plate">
  <span class="mx-actopen__no">Act {ROMAN[idx]}</span>
  <h2 class="mx-actopen__title">{esc(act.get('title', act.get('name', '')))}</h2>{hand_html}
</header>
"""


def render_transit(prev_act, next_act):
    card = esc(next_act.get("transit_card", "Change Here"))
    return f"""
<div class="mx-transit" data-mx-event="marquee">
  <div class="mx-transit__side mx-transit__side--left">
    <div class="mx-transit__mega" aria-hidden="true">{esc(prev_act.get('name', '')).upper()}</div>
    <div class="mx-transit__label">
      <span class="mx-transit__hand">leaving</span>
      <span class="mx-transit__name">{esc(prev_act.get('title', prev_act.get('name', '')))}</span>
    </div>
  </div>
  <div class="mx-transit__center"><div class="mx-transit__card">{card}</div></div>
  <div class="mx-transit__side mx-transit__side--right">
    <div class="mx-transit__mega" aria-hidden="true">{esc(next_act.get('name', '')).upper()}</div>
    <div class="mx-transit__label">
      <span class="mx-transit__hand">entering</span>
      <span class="mx-transit__name">{esc(next_act.get('title', next_act.get('name', '')))}</span>
    </div>
  </div>
</div>
"""


def render_plate(no, ch, loud):
    loud_cls = " mx-plate--loud" if loud else ""
    return f"""
<header class="mx-plate{loud_cls}" data-mx-event="plate">
  <div class="mx-plate__ghost" aria-hidden="true">{ROMAN[min(no, len(ROMAN) - 1)]}</div>
  <span class="mx-plate__no">FILE {no:02d}</span>
  <h2 class="mx-plate__title">{esc(ch.get('chapter_title', ''))}</h2>
  <p class="mx-plate__dek">{esc(ch.get('chapter_arc', ''))}</p>
</header>
"""


def render_footer(fmt_label, topic, pdate):
    return f"""
<footer class="mx-footer">
  <b>The Signal</b>
  <span>End of the {esc(fmt_label)} · {esc(topic)} · filed {esc(pdate)} · set in six voices · for one reader</span>
</footer>
"""


# ── writer-file gates ────────────────────────────────────────────────────────

def gate_writer_file(cid, content, skin):
    """Reject chrome, legacy vocabulary, and (on editorial skins) event-only
    loud furniture in a writer interior. Returns a list of violations."""
    problems = []
    for label, pat in CHROME_BANNED:
        hits = pat.findall(content)
        if hits:
            problems.append(f"{cid}.html: contains stitcher-owned chrome — {label} "
                            f"({len(hits)} hit(s)). Writers fill interiors ONLY; "
                            f"masthead/cover/act/plate chrome is generated from the skeleton.")
    legacy = sorted({m for m in LEGACY_CLASS_RE.findall(content)})
    if legacy:
        problems.append(f"{cid}.html: legacy special/holiday classes (undefined in an mx "
                        f"bundle): {', '.join(legacy[:6])}")
    if skin == "editorial":
        loud = sorted({m for m in EVENT_ONLY_CLASS_RE.findall(content)})
        if loud:
            problems.append(f"{cid}.html: event-skin-only loud furniture on an editorial "
                            f"issue (Law 11 — editorial keeps bookish restraint): "
                            f"{', '.join(loud[:6])}")
    return problems


def gate_census(cid, content, planned):
    """The interior must deliver at least the events the plan committed to."""
    found = re.findall(r'data-mx-event="([a-z-]+)"', content)
    bad_types = sorted({t for t in found if t not in MX_EVENT_TYPES})
    problems = []
    if bad_types:
        problems.append(f"{cid}.html: data-mx-event type(s) outside the Law-2 vocabulary: "
                        f"{', '.join(bad_types)}")
    planned_total = sum(v for v in (planned or {}).values() if isinstance(v, int) and v > 0)
    if len(found) < planned_total:
        problems.append(f"{cid}.html: delivers {len(found)} data-mx-event marker(s) but the "
                        f"plan committed to {planned_total} — the writer under-delivered "
                        f"the chapter's Law-2 quota.")
    return problems


# ── main assembly ────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--build-dir", default="/tmp/signal-build")
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--pack", default="")
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir)
    repo_root = skill_dir.parent.parent.parent
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    meta = plan.get("issue_meta", {})
    fmt = meta.get("format", "")

    if meta.get("design_system") != "mx":
        die("stitch_specials.py only assembles NEW-SYSTEM plans "
            "(issue_meta.design_system:'mx'). Legacy specials go through "
            "stitch-issue.sh; weeklies through stitch_weekly.py.")
    if fmt not in SKELETON_FILES:
        die(f"format '{fmt}' has no WP-6 skeleton "
            f"(have: {sorted(SKELETON_FILES)}). Add references/format-skeletons/ "
            f"coverage before stitching this format.")

    skeleton = json.loads((skill_dir / "references" / "format-skeletons"
                           / SKELETON_FILES[fmt]).read_text(encoding="utf-8"))
    skin = skeleton["skin"]
    motion = meta.get("motion") or skeleton["motion"]
    fmt_label = FORMAT_LABELS.get(fmt, "Special Edition")
    fmt_slug = fmt.replace("_", "-")
    topic = meta.get("topic", "")
    pdate = pretty_date(meta.get("date", ""))

    # ── CSS bundle: per-skin manifest, budget, one-masthead gate (WP-3) ──
    manifest_path = skill_dir / "references" / "css-manifests" / f"{skin}.txt"
    if not manifest_path.is_file():
        die(f"css manifest not found: {manifest_path}")
    css_dir = skill_dir / "assets" / "css"
    rel_files = [ln.strip() for ln in manifest_path.read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
    css_files = [css_dir / rel for rel in rel_files]
    missing = [str(p) for p in css_files if not p.is_file()]
    if missing:
        die("css manifest lists missing file(s):\n  " + "\n  ".join(missing))
    css_content = "\n".join(p.read_text(encoding="utf-8") for p in css_files)
    css_total = len(css_content.encode("utf-8"))
    budget = (120 if skin == "editorial" else 160) * 1024
    if css_total > budget:
        die(f"MX bundle budget exceeded: {css_total:,} bytes > {budget:,} ({skin} skin). "
            f"Trim the skin/manifest — legacy layers must never be re-added (F-5).")
    if ".mx-mast" not in css_content:
        die("mx bundle does not define .mx-mast (core/13-chrome.css missing from manifest?)")
    legacy_mast = sorted(set(re.findall(r"\.(?:hol-masthead|mast)(?![\w-])", css_content)))
    if legacy_mast:
        die("MX bundle masthead gate (F-3): legacy masthead vocabulary in bundle: "
            + ", ".join(legacy_mast))

    # ── JS: the WP-5 motion controller only ──
    js_file = skill_dir / "assets" / "mx-motion.js"
    if not js_file.is_file():
        die(f"mx motion controller not found: {js_file}")
    js_content = js_file.read_text(encoding="utf-8")

    # ── acts ──
    acts = meta.get("acts") or []
    if not acts:
        die("issue_meta.acts is empty — the plan validator should have caught this.")
    pack_path = args.pack or ""
    have_tokens = all(isinstance(a.get("tokens"), dict) and a["tokens"] for a in acts)
    if not pack_path and not have_tokens:
        die("Acts declare no palettes: provide a motif pack (--pack) or per-act "
            "'tokens' maps in issue_meta.acts — otherwise every act renders the "
            "neutral defaults and the scroll does not travel (Law 4).")

    # ── chapters: gates, then grouping by act ──
    chapters = sorted((c for c in plan.get("chapters", []) if isinstance(c, dict)),
                      key=lambda c: c.get("chapter_num", 0))
    chapters_dir = Path(args.build_dir) / "chapters"
    slots_def = {s["slot_id"]: s for s in skeleton.get("slots", [])}
    sig = skeleton.get("signature_moment", {}) or {}
    sig_slot, sig_class = sig.get("slot"), sig.get("class")

    problems = []
    interiors = {}
    for ch in chapters:
        cid = ch.get("chapter_id")
        cf = chapters_dir / f"{cid}.html"
        if not cf.is_file():
            problems.append(f"missing interior: {cf} — every planned chapter needs a "
                            f"writer file before stitching.")
            continue
        content = cf.read_text(encoding="utf-8")
        problems += gate_writer_file(cid, content, skin)
        problems += gate_census(cid, content, ch.get("visual_events"))
        interiors[cid] = content
    if problems:
        die("writer-file gates failed:\n  • " + "\n  • ".join(problems))

    # ── assemble ──
    title = f"The Signal — {topic} · {fmt_label}"
    description = plan.get("cover", {}).get("dek") or f"{fmt_label}: {topic}"
    parts = [render_head(title, description)]
    parts.append(f'<body data-mx data-skin="{skin}" data-motion="{motion}" '
                 f'data-mx-chrome="pill" data-format="{fmt_slug}">\n')

    # back pill (self-styled template part; core reserves its zone via
    # data-mx-chrome="pill")
    back_path = skill_dir / "assets" / "template-parts" / "back-link.html"
    if not back_path.is_file():
        die(f"back-link template missing: {back_path}")
    parts.append(back_path.read_text(encoding="utf-8").rstrip() + "\n")

    parts.append(render_mast(fmt_label, topic, pdate))
    parts.append(render_cover(plan.get("cover", {}), skeleton, acts, fmt_label, acts[0]))

    plate_no = 0
    for ai, act in enumerate(acts, start=1):
        if ai > 1:
            parts.append(render_transit(acts[ai - 2], act))
        grounds = " ".join(act.get("grounds", []))
        parts.append(f'\n<section data-act="{esc(act["name"])}" class="{grounds}">\n'
                     f'<div class="mx-wrap">\n')
        parts.append(render_actopen(ai, act))
        for ch in chapters:
            if ch.get("act") != ai:
                continue
            cid = ch.get("chapter_id")
            plate_no += 1
            slot = ch.get("skeleton_slot")
            sig_cls = f" {sig_class}" if (sig_slot and slot == sig_slot and sig_class) else ""
            parts.append(f'<article id="{esc(cid)}" class="mx-chapter{sig_cls}" '
                         f'data-mx-chapter="{esc(cid)}" data-mx-slot="{esc(slot)}">')
            parts.append(render_plate(plate_no, ch, loud=(skin == "event")))
            parts.append(interiors[cid].rstrip() + "\n")
            parts.append("</article>\n")
        parts.append("</div>\n</section>\n")

    parts.append(render_footer(fmt_label, topic, pdate))
    parts.append(f"\n{INJECT_JS}\n</body>\n</html>\n")
    html = "".join(parts)

    # every planned chapter must have landed exactly once
    for ch in chapters:
        n = html.count(f'data-mx-chapter="{ch.get("chapter_id")}"')
        if n != 1:
            die(f"chapter '{ch.get('chapter_id')}' rendered {n} times — act assignment "
                f"({ch.get('act')!r}) does not match a declared act.")

    # ── inject CSS + per-issue act tokens + JS ──
    html = html.replace(INJECT_CSS, f"<style>\n{css_content}\n</style>", 1)
    act_token_css = ""
    for a in acts:
        toks = a.get("tokens")
        if isinstance(toks, dict) and toks:
            body = "\n".join(f"  {k}: {v};" for k, v in toks.items())
            act_token_css += f'[data-mx] [data-act="{a["name"]}"] {{\n{body}\n}}\n'
    if act_token_css:
        html = html.replace("<!-- INJECT:MX-ACT-TOKENS -->",
                            f"<style data-mx-issue-acts>\n{act_token_css}</style>", 1)
    else:
        html = html.replace("<!-- INJECT:MX-ACT-TOKENS -->\n", "", 1)
    html = html.replace(INJECT_JS, f"<script>\n{js_content}\n</script>", 1)

    out = Path(args.out)
    out.write_text(html, encoding="utf-8")

    # ── motif pack: validate → inject → consume cover plate (WP-4 gap #2) ──
    pack_notes = []
    if pack_path:
        pack_file = Path(pack_path)
        if not pack_file.is_file():
            die(f"motif pack not found: {pack_file}")
        motif_dir = repo_root / "tools" / "motif"
        r = subprocess.run([sys.executable, str(motif_dir / "validate-motif-pack.py"),
                            str(pack_file)], capture_output=True, text=True)
        if r.returncode != 0:
            die(f"motif pack REJECTED by validator — refusing to stitch with it:\n"
                f"{r.stdout}{r.stderr}")
        r = subprocess.run([sys.executable, str(motif_dir / "render-motif-pack.py"),
                            str(pack_file), "--inject", str(out), "--out", str(out)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            die(f"motif pack injection failed:\n{r.stdout}{r.stderr}")
        pack_notes = [ln for ln in r.stdout.splitlines() if ln.strip()]
        html = out.read_text(encoding="utf-8")

    # cover-plate consumption: a pack's <template data-mx-pack-cover-plate>
    # becomes the live .mx-cover__plate art slot (WP-4 handed this gap to WP-6).
    tpl = re.search(r'<template data-mx-pack-cover-plate="[^"]*">(.*?)</template>',
                    html, re.S)
    if tpl and COVER_PLATE_MARK in html:
        plate_div = f'<div class="mx-cover__plate" aria-hidden="true">{tpl.group(1).strip()}</div>'
        html = html.replace(COVER_PLATE_MARK, plate_div, 1)
        html = html.replace(tpl.group(0), "", 1)
        pack_notes.append("cover plate: pack cover_plate consumed into .mx-cover__plate")
    else:
        html = html.replace(COVER_PLATE_MARK + "\n", "", 1).replace(COVER_PLATE_MARK, "", 1)
    out.write_text(html, encoding="utf-8")

    # ── post-write verification ──
    checks = []
    if INJECT_CSS in html or INJECT_JS in html:
        checks.append("injection markers survived — injection failed")
    if not pack_path and INJECT_PACK in html:
        # no pack: drop the inert marker so the shipped head is clean
        html = html.replace(INJECT_PACK + "\n", "", 1).replace(INJECT_PACK, "", 1)
        out.write_text(html, encoding="utf-8")
    body_html = html[html.find("</head>"):]
    if len(re.findall(r'class="[^"]*\bmx-mast\b', body_html)) != 1:
        checks.append("expected exactly ONE .mx-mast in the document (F-3)")
    if not re.search(r'<section\b[^>]*\bdata-act=', body_html):
        checks.append("no section[data-act] — acts missing (Law 1/4)")
    if "data-mx-event=" not in body_html:
        checks.append("no data-mx-event markers — the Law-2 census has nothing to count")
    if "signal-back-to-archive" not in html or "<!-- the-signal:back -->" not in html:
        checks.append("back pill missing from output")
    if checks:
        die("post-write verification failed:\n  • " + "\n  • ".join(checks))

    n_events = len(re.findall(r'data-mx-event="', body_html))
    print("=== specials stitch OK ===")
    print(f"  Format:    {fmt} ({skin} skin, {motion}) — skeleton {SKELETON_FILES[fmt]}")
    print(f"  Chapters:  {len(chapters)} across {len(acts)} act(s)")
    print(f"  CSS:       {css_total / 1024:.1f} KB from {len(css_files)} manifest files "
          f"(budget {budget // 1024} KB)")
    print(f"  JS:        {len(js_content.encode()) / 1024:.1f} KB (mx-motion.js)")
    print(f"  Events:    {n_events} data-mx-event markers in document")
    if pack_notes:
        print("  Motif pack:")
        for n in pack_notes:
            print(f"    {n}")
    print(f"  Output:    {out} ({len(html.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
