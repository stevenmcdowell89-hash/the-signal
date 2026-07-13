#!/usr/bin/env python3
"""render-quality-page.py — bake state/quality-log.jsonl into quality.html.

The quality log lives under state/ which is excluded from the deployed site
(.assetsignore), so the page can't fetch it at runtime. Instead we render a
static quality.html at the repo root — served like index.html — and
regenerate it whenever a new score is logged (log-quality.sh calls this).

Paths default to the repo root computed from this script's location
(.claude/skills/the-signal/scripts/ -> 4 levels up). Override with the
SIGNAL_QUALITY_LOG and SIGNAL_QUALITY_PAGE environment variables.

Usage:
    python3 scripts/render-quality-page.py
"""
import os, sys, json, html, datetime, statistics
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
LOG_FILE = os.environ.get("SIGNAL_QUALITY_LOG",
                          os.path.join(REPO_ROOT, "state", "quality-log.jsonl"))
OUT_FILE = os.environ.get("SIGNAL_QUALITY_PAGE",
                          os.path.join(REPO_ROOT, "quality.html"))

# Full dimension list (v8.43). Older log rows lack the newer keys (novelty
# v8.27, length/visual v8.43) — cell(None) renders those as "—", so
# already-logged entries keep rendering unchanged.
DIMS = [("voice", "Voice"), ("density", "Density"), ("length", "Length"),
        ("structure", "Structure"), ("opening", "Opening"),
        ("throughline", "Throughline"), ("novelty", "Novelty"),
        ("visual", "Visual")]
DIM_KEYS = [k for k, _ in DIMS]


def load_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    # newest first
    rows.sort(key=lambda r: r.get("date", "") or r.get("ts", ""), reverse=True)
    return rows


def score_class(v):
    if v is None:
        return "s-na"
    if v >= 4.5:
        return "s5"
    if v >= 3.5:
        return "s4"
    if v >= 2.5:
        return "s3"
    if v >= 1.5:
        return "s2"
    return "s1"


def cell(v):
    disp = "—" if v is None else (f"{v:g}")
    return f'<td class="score {score_class(v)}">{disp}</td>'


def esc(s):
    return html.escape(str(s)) if s is not None else ""


FORMAT_LABELS = {
    "weekly": "Weekly", "deep_dive": "Deep Dive", "versus": "Versus",
    "rewind": "Rewind", "season_review": "Season Review",
    "starter_kit": "Starter Kit", "shortlist": "Shortlist",
    "next": "Next", "lookahead": "Lookahead", "countdown": "Countdown",
    "field_guide": "Field Guide",
}


def fmt_label(f):
    return FORMAT_LABELS.get(f, (f or "").replace("_", " ").title() or "—")


def build_summary(rows):
    overalls = [r["overall"] for r in rows if isinstance(r.get("overall"), (int, float))]
    by_writer = defaultdict(list)
    for r in rows:
        o = r.get("overall")
        if isinstance(o, (int, float)):
            by_writer[r.get("writer_model", "?")].append(o)
    weakest = Counter(r.get("weakest") for r in rows if r.get("weakest"))

    cards = []
    cards.append(("Issues scored", str(len(rows))))
    if overalls:
        cards.append(("Average overall", f"{statistics.mean(overalls):.2f}"))
    # The headline comparison this whole system exists to enable:
    if len(by_writer) >= 1:
        parts = [f"{esc(m)} {statistics.mean(v):.2f} <span class='muted'>(n={len(v)})</span>"
                 for m, v in sorted(by_writer.items())]
        cards.append(("Average by writer model", " &nbsp;·&nbsp; ".join(parts)))
    if weakest:
        top = ", ".join(f"{esc(k)} ×{n}" for k, n in weakest.most_common())
        cards.append(("Weakest dimension (freq)", top))

    return "".join(
        f'<div class="stat"><div class="stat-label">{esc(lbl)}</div>'
        f'<div class="stat-val">{val}</div></div>'
        for lbl, val in cards
    )


def build_table(rows):
    if not rows:
        return ('<div class="empty">No issues scored yet. The first score '
                'lands at Phase 8.5 of the next pipeline run — this table '
                'fills in from there.</div>')
    head = ("<tr><th>Date</th><th>Format</th><th class='left'>Issue</th>"
            "<th>Writer</th>"
            + "".join(f"<th>{lbl}</th>" for _, lbl in DIMS)
            + "<th>Overall</th><th class='left'>Weakest / note</th></tr>")
    body = []
    for r in rows:
        scores = r.get("scores", {})
        link = r.get("issue_file")
        title = esc(r.get("title") or r.get("issue_id") or "—")
        title_cell = (f'<a href="issues/{esc(link)}">{title}</a>'
                      if link else title)
        bf = ' <span class="tag">backfill</span>' if r.get("backfill") else ""
        weakest = esc(r.get("weakest") or "—")
        note = esc(r.get("note") or "")
        cells = "".join(cell(scores.get(k)) for k in DIM_KEYS)
        body.append(
            f"<tr><td class='nowrap'>{esc(r.get('date') or '—')}</td>"
            f"<td>{esc(fmt_label(r.get('format')))}</td>"
            f"<td class='left'>{title_cell}{bf}</td>"
            f"<td class='nowrap'>{esc(r.get('writer_model') or '—')}</td>"
            f"{cells}"
            f"{cell(r.get('overall'))}"
            f"<td class='left'><strong>{weakest}</strong> — "
            f"<span class='muted'>{note}</span></td></tr>"
        )
    return f"<table><thead>{head}</thead><tbody>{''.join(body)}</tbody></table>"


def render(rows):
    generated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scorers = sorted({r.get("scorer_model") for r in rows if r.get("scorer_model")})
    scorer_note = (" · scored by " + ", ".join(esc(s) for s in scorers)) if scorers else ""
    summary = build_summary(rows)
    table = build_table(rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>The Signal — Editorial Quality</title>
  <meta name="robots" content="noindex">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:#1A1A2E; --bg-2:#16213E; --bg-3:#20253E; --ink:#E8E8E8;
      --ink-2:#B6BAC6; --ink-dim:#888; --coral:#E94560; --orange:#FF6B35;
      --gold:#C9A66B; --line:rgba(255,255,255,0.08); --line-strong:rgba(255,255,255,0.16);
      --s5:#3FA66A; --s4:#6FA84B; --s3:#C9A66B; --s2:#D2814A; --s1:#E94560;
    }}
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:var(--bg);color:var(--ink);font-family:'Source Sans 3',sans-serif;
      min-height:100vh;padding:1.5rem 1.25rem 5rem;line-height:1.55;-webkit-font-smoothing:antialiased;}}
    .container{{max-width:1180px;margin:0 auto;}}
    .back{{display:inline-block;color:var(--ink-dim);text-decoration:none;font-size:0.8rem;
      letter-spacing:0.06em;margin-bottom:1.5rem;}}
    .back:hover{{color:var(--coral);}}
    header{{text-align:center;padding:0.5rem 0 1.5rem;}}
    .masthead{{font-family:'Playfair Display',serif;font-weight:900;
      font-size:clamp(2rem,5vw,3rem);letter-spacing:0.05em;text-transform:uppercase;
      background:linear-gradient(135deg,var(--coral),var(--orange));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}}
    .tagline{{font-size:0.72rem;color:var(--ink-dim);letter-spacing:0.28em;
      text-transform:uppercase;font-weight:600;margin-top:0.4rem;}}
    .intro{{max-width:760px;margin:1.5rem auto 0;color:var(--ink-2);font-size:0.95rem;}}
    .intro strong{{color:var(--ink);}}
    .stats{{display:flex;flex-wrap:wrap;gap:0.75rem;margin:2rem 0 1.5rem;}}
    .stat{{background:var(--bg-2);border:1px solid var(--line);border-radius:10px;
      padding:0.85rem 1.1rem;flex:1 1 220px;}}
    .stat-label{{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.16em;
      color:var(--ink-dim);font-weight:600;margin-bottom:0.35rem;}}
    .stat-val{{font-size:1.05rem;color:var(--ink);font-weight:600;}}
    .muted{{color:var(--ink-dim);font-weight:400;}}
    .table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--bg-2);}}
    table{{border-collapse:collapse;width:100%;font-size:0.88rem;}}
    th,td{{padding:0.6rem 0.7rem;text-align:center;border-bottom:1px solid var(--line);white-space:nowrap;}}
    th{{font-size:0.66rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-dim);
      font-weight:700;background:var(--bg-3);position:sticky;top:0;}}
    th.left,td.left{{text-align:left;white-space:normal;}}
    tbody tr:hover{{background:rgba(255,255,255,0.03);}}
    td a{{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line-strong);}}
    td a:hover{{color:var(--coral);}}
    td.left .muted{{font-size:0.82rem;}}
    .score{{font-weight:700;font-variant-numeric:tabular-nums;}}
    .s5{{color:var(--s5);}} .s4{{color:var(--s4);}} .s3{{color:var(--s3);}}
    .s2{{color:var(--s2);}} .s1{{color:var(--s1);}} .s-na{{color:var(--ink-dim);font-weight:400;}}
    .tag{{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--gold);
      border:1px solid var(--line-strong);border-radius:4px;padding:0.05rem 0.35rem;vertical-align:middle;}}
    .empty{{padding:3rem 1rem;text-align:center;color:var(--ink-dim);}}
    .legend{{margin-top:1rem;font-size:0.78rem;color:var(--ink-dim);}}
    .legend b{{color:var(--ink-2);}}
    footer{{margin-top:2.5rem;font-size:0.76rem;color:var(--ink-dim);text-align:center;line-height:1.7;}}
  </style>
</head>
<body>
  <div class="container">
    <a class="back" href="index.html">← The Signal archive</a>
    <header>
      <div class="masthead">Editorial Quality</div>
      <div class="tagline">Quality signal · not compliance</div>
    </header>

    <p class="intro">Every automated gate in the pipeline checks whether an issue
    broke a <strong>rule</strong>. This page is the one place that asks whether an issue
    was <strong>good</strong> — scored at Phase 8.5 against a fixed rubric by a dedicated
    scorer model, separate from the writer and the orchestrator. The number isn't the
    point; the trend is. Each row stamps the <strong>writer model</strong> next to the
    score, so over time this table answers the question a single read can't: did the
    stronger model actually write a better magazine?</p>

    <div class="stats">{summary}</div>

    <div class="table-wrap">{table}</div>

    <p class="legend"><b>Scores 1–5</b> per dimension
    (<span class="score s5">5</span> best …
    <span class="score s1">1</span> = the failure the spec warns about).
    <b>Throughline</b> is scored only for sequential formats (Deep Dive, Versus,
    Rewind, Season Review, Next); parallel formats show —.
    <b>Length</b> (in-band word count), <b>Novelty</b> and <b>Visual</b>
    (illustration richness) were added after the earliest rows — older issues
    show — for dimensions that didn't exist when they were scored.
    <b>Overall</b> is the mean of scored dimensions.</p>

    <footer>
      Generated {generated}{scorer_note}.<br>
      Backfilled rows were scored from sampled prose after the fact, by the
      orchestrator rather than an independent scorer — treat them as indicative,
      not as live-pipeline scores. Rubric: <code>references/quality-rubric.md</code>.
    </footer>
  </div>
</body>
</html>
"""


def main():
    rows = load_rows(LOG_FILE)
    page = render(rows)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(page)
    sys.stderr.write(f"rendered {OUT_FILE} from {len(rows)} row(s)\n")


if __name__ == "__main__":
    main()
