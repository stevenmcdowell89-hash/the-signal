#!/usr/bin/env python3
"""Fixture generator for the editorial-coverage-rebuild verification harness (WP-10).

    python3 build-fixtures.py --out <dir> [--issue <html>] [--state <json>]

Why a generator and not 32 committed HTML files
-----------------------------------------------
Every rendered-issue fixture is `issues/signal_weekly_2026-07-26.html` (frozen
Issue #18, 141 KB) with **exactly one thing changed**. Committing the outputs
would put ~4.5 MB of near-identical HTML in the repo, and the one line that
matters in each file would be invisible. Committing the *mutations* instead makes
the whole fixture matrix readable in one screen per criterion, and it fails loudly
rather than silently if an anchor ever moves: `one()` asserts the anchor exists.

Inputs (read-only, never written):
  issues/signal_weekly_2026-07-26.html   frozen Issue #18 (SPEC §1.3)
  state/signal-state.json                the real state seed (WP-1's file)

Outputs, under --out:
  weekly/*.html    rendered-issue fixtures for validate-issue.py  (criteria 2,3,6,7,8)
  states/*.json    state fixtures                                 (criteria 4,5,6,7)
  plans/*.json     weekly chapter plans for validate-chapter-plan.py (criteria 1,4)
  bundles/*.json   research bundles for validate-research-bundle.py  (criterion 5)

`pass.html` is Issue #18 **plus the SPEC 2026-07-26 contract markup it predates** —
the "corrected fixture" of acceptance criteria #3 and #8. Every other weekly
fixture is `pass.html` with one defect introduced.

Provenance of the fixture matrix: the weekly HTML mutations and the three weekly
state fixtures are WP-4's (`build_fixtures.py`, scratchpad); the plans, bundles and
rut/loop states are WP-5's (`make-fixtures.py` + `make-plans.py`, scratchpad). Both
WPs flagged that WP-10 should own permanent copies. Merged here, unchanged in
substance; dead code removed and `--out` added.

NOTHING in this file invents a fact of record. Every fabricated calendar row or
loop claim is prefixed `FIXTURE DATA — not a real event` so it can never be
mistaken for one.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
# HERE = …/.claude/skills/the-signal/references/fixtures/coverage-rebuild
#         parents: [0] fixtures [1] references [2] the-signal [3] skills [4] .claude [5] <repo>
REPO = HERE.parents[5]
DEFAULT_ISSUE = REPO / "issues" / "signal_weekly_2026-07-26.html"
DEFAULT_STATE = REPO / "state" / "signal-state.json"


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────
def one(html: str, old: str, new: str, n: int = 1) -> str:
    """Replace the FIRST occurrence of `old`, asserting it exists.

    The assert is the point: Issue #18 is frozen, so a missing anchor means this
    generator is being run against the wrong file — which must be loud, not a
    silently-unmutated fixture that then passes every check.
    """
    if old not in html:
        raise SystemExit(f"FIXTURE ANCHOR NOT FOUND: {old[:90]!r}\n"
                         f"  (fixtures are derived from frozen Issue #18; is --issue correct?)")
    return html.replace(old, new, n)


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: pathlib.Path, obj) -> None:
    write(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# ═════════════════════════════════════════════════════════════════════════════
# 1. Rendered-issue fixtures, derived from frozen Issue #18
# ═════════════════════════════════════════════════════════════════════════════

# The four SPEC §3.4 provenance attributes to stamp on each .plate-img, keyed by
# the cached-asset hash in its <img src>. Values are chosen to SATISFY §3.8:
# ≥3 distinct shapes, an information figure in the Long Read, at most one key_art
# in Pixel & Byte and none of them leading.
PROVENANCE = {
    # hash            shows           capture_year  licence                 allows_derivatives
    "af9fc905ced8": ("event_photo",  "2026", "CC-BY-4.0",           "true"),  # COVER, the_letter/lead
    "bf64e308503b": ("artefact",     "2019", "CC-BY-SA-4.0",        "true"),  # FIG 01, long_read/lead
    "5a78b1b6198a": ("artefact",     "2019", "CC-BY-SA-4.0",        "true"),  # FIG 02, long_read
    "fb560e553feb": ("artefact",     "2007", "CC-BY-2.5",           "true"),  # FIG 03, long_read  <- §3.9
    "2601e4c02103": ("event_photo",  "2026", "PRESS-KIT-EDITORIAL", "true"),  # touchline/lead
    "8ff67aa0126f": ("gameplay",     "2026", "PRESS-KIT-EDITORIAL", "true"),  # pixel_byte/lead
    "1a2d67f3ca02": ("key_art",      "2026", "PRESS-KIT-EDITORIAL", "true"),  # pixel_byte
    "c0e890a4c08e": ("document",     "2026", "PRESS-KIT-EDITORIAL", "true"),  # pixel_byte
    "b43955d3d330": ("product_shot", "2026", "PRESS-KIT-EDITORIAL", "true"),  # pixel_byte
    "85eacdc20d4a": ("chart",        "",     "CC0",                 "true"),  # the_desk (synthetic)
    "b47a4ae1b7e0": ("event_photo",  "2026", "CC-BY-4.0",           "true"),  # the_threads
}

FIG_OPEN_RE = re.compile(r'<div\b[^>]*class="[^"]*\bplate-img\b[^"]*"[^>]*>')

# §3.9 worked example. #18's shipped FIG 03 caption puts the capture year only in
# the .credit span, so the visible sentence claims a "modern reconstruction" of a
# 2021 finding using a 2007 photo. FIXED is the SPEC's own suggested rewrite.
FIG03_SHIPPED = ('<span class="txt">A working modern reconstruction of the front dial — the '
                 'pointers that tracked the Sun, Moon and planets, turned by a single crank.')
FIG03_FIXED = ('<span class="txt">A 2007 working reconstruction of the front dial, built on the '
               'pre-2021 understanding — the pointers that tracked the Sun, Moon and planets, '
               'turned by a single crank.')

LR_TITLE_H2 = '      <h2>The Greeks who built a <em>cosmos</em> in bronze</h2>'
LR_VINTAGE = ('      <div class="mono lr-vintage">NOT THIS WEEK · A STANDING STORY · 1901–2021 · '
              'LATEST DEVELOPMENT MAR 2021</div>\n')
BYLINE_DATED = '<p class="mono byline">BY THE EDITOR · THE LONG READ · 26 JUL 2026</p>'
BYLINE_FREE = '<p class="mono byline">BY THE EDITOR · THE LONG READ · A STANDING STORY</p>'
LETTER_P = '<p>The rest of the week was the one everyone else lived.'
LETTER_P_FRAMED = '<p data-lr-framing="feature">The rest of the week was the one everyone else lived.'

TL_CAP_SHIPPED = '<span class="txt">Lando Norris on his way to pole at the Hungaroring'
TL_CAP_RESULT = '<span class="txt">Lando Norris won the Hungarian Grand Prix by 4 seconds'
TL_FIG_ANCHOR = '      <div data-mx-event="figure" class="plate-img lead"'
THREADS_BAND = '<div class="band" data-band="the_threads">'


def stamp_provenance(html: str) -> str:
    """Add the four §3.4 attributes to every .plate-img, keyed by asset hash."""
    out, pos = [], 0
    for m in FIG_OPEN_RE.finditer(html):
        tail = html[m.end():m.end() + 400]
        sm = re.search(r'<img[^>]*src="[^"]*/([0-9a-f]{12})\.', tail)
        if not sm or sm.group(1) not in PROVENANCE:
            raise SystemExit(f"unmapped .plate-img asset near offset {m.start()}; "
                             f"add it to PROVENANCE")
        shows, year, lic, ad = PROVENANCE[sm.group(1)]
        out.append(html[pos:m.start()])
        out.append(m.group(0)[:-1] +
                   f' data-shows="{shows}" data-capture-year="{year}"'
                   f' data-licence="{lic}" data-allows-derivatives="{ad}">')
        pos = m.end()
    out.append(html[pos:])
    return "".join(out)


def ledger_html(rows) -> str:
    """A §3.4 results ledger. rows = [(sport, date, match, result), …]."""
    body = "".join(
        f'        <div class="mx-ledger__row" data-sport="{s}">'
        f'<span class="mx-ledger__date">{d}</span>'
        f'<span class="mx-ledger__match">{m}</span>'
        f'<span class="mx-ledger__result">{r}</span></div>\n'
        for s, d, m, r in rows)
    return ('      <div class="mx-ledger" data-mx-event="ledger" data-role="results-ledger">\n'
            '        <div class="mx-ledger__caption">Results of Record · Since the Cut</div>\n'
            + body + '      </div>\n')


ONE_SPORT_ROWS = [
    ("motorsport", "26 JUL", "<b>Hungarian Grand Prix</b> — Hungaroring", "RACE"),
    ("motorsport", "25 JUL", "<b>Hungaroring qualifying</b> — Norris on pole", "POLE"),
]
TWO_SPORT_ROWS = ONE_SPORT_ROWS[:1] + [
    ("golf", "19 JUL", "<b>The Open Championship</b> — final round", "R4"),
]


def build_weekly(issue_html: str) -> dict[str, str]:
    """Return {fixture_name: html}. `pass` is the corrected baseline."""
    p = stamp_provenance(issue_html)
    p = one(p, '<header class="cover">', '<header class="cover" data-cover-leads-on="news">')
    p = one(p, '<section class="longread" data-role="long-read">',
               '<section class="longread" data-role="long-read" data-vintage="news">')
    # §3.4 polymorphic table: legal kinds on #18's two .mx-scorecard cards.
    p = one(p, '<div class="mx-scorecard" data-mx-event="ledger">',
               '<div class="mx-scorecard" data-mx-event="ledger" data-table-kind="championship">')
    p = one(p, '<div class="mx-scorecard deskcol__card" data-mx-event="ledger">',
               '<div class="mx-scorecard deskcol__card" data-mx-event="ledger" data-table-kind="league">')
    # §3.9: FIG 01/02 (2019) and FIG 03 (2007) sit in a band claiming 2021, so
    # each visible sentence must carry its own year.
    p = one(p, FIG03_SHIPPED, FIG03_FIXED)
    p = one(p, '<span class="txt">Fragment A, the largest surviving piece',
               '<span class="txt">Fragment A, photographed in 2019 — the largest surviving piece')
    p = one(p, '<span class="txt">The reverse of Fragment A —',
               '<span class="txt">The reverse of Fragment A, in a 2019 museum photograph —')

    fx: dict[str, str] = {"pass": p}

    # ── criterion #2 · Long Read vintage (§3.4) ──────────────────────────────
    fx["vintage-missing"] = one(p, ' data-vintage="news">', '>')
    fx["vintage-bad-enum"] = one(p, 'data-vintage="news"', 'data-vintage="ancient"')
    fx["vintage-news-with-lrvintage"] = one(p, LR_TITLE_H2, LR_VINTAGE + LR_TITLE_H2)

    ev = one(p, 'data-vintage="news"', 'data-vintage="evergreen"')
    ev_lrv = one(ev, LR_TITLE_H2, LR_VINTAGE + LR_TITLE_H2)
    fx["vintage-evergreen-ok"] = one(one(ev_lrv, BYLINE_DATED, BYLINE_FREE),
                                     LETTER_P, LETTER_P_FRAMED)                     # PASSING
    fx["vintage-evergreen-dated-byline"] = one(ev_lrv, LETTER_P, LETTER_P_FRAMED)
    fx["vintage-evergreen-no-lrvintage"] = one(one(ev, BYLINE_DATED, BYLINE_FREE),
                                               LETTER_P, LETTER_P_FRAMED)
    fx["vintage-evergreen-no-framing"] = one(ev_lrv, BYLINE_DATED, BYLINE_FREE)

    # ── criterion #3 · caption vintage (§3.9) ────────────────────────────────
    # The firing case is #18's OWN shipped caption wording, with only the capture
    # year added. That is the exact defect the owner spotted.
    fire = one(p, FIG03_FIXED, FIG03_SHIPPED)
    fx["capvintage-fire"] = fire
    fx["capvintage-null-year"] = one(
        fire, 'data-shows="artefact" data-capture-year="2007" data-licence="CC-BY-2.5"',
              'data-shows="artefact" data-capture-year="" data-licence="CC-BY-2.5"')  # §3.4a n3
    fx["capvintage-bad-year"] = one(p, 'data-capture-year="2007"', 'data-capture-year="c. 2007"')

    # ── §3.4a note 6 · provenance presence ──────────────────────────────────
    fx["provenance-missing"] = one(
        p, ' data-shows="artefact" data-capture-year="2007" data-licence="CC-BY-2.5"'
           ' data-allows-derivatives="true"', '')

    # ── criterion #8 · image shape budgets (§3.8) ───────────────────────────
    fx["shapes-keyart-leads-pb"] = one(p, 'data-shows="gameplay" data-capture-year="2026"',
                                          'data-shows="key_art" data-capture-year="2026"')
    fx["shapes-two-keyart-pb"] = one(p, 'data-shows="document" data-capture-year="2026"',
                                        'data-shows="key_art" data-capture-year="2026"')
    # all three Long Read artefacts become portraits -> no information figure
    fx["shapes-lr-no-information-figure"] = p.replace('data-shows="artefact"',
                                                      'data-shows="portrait"')
    # everything that is not event_photo becomes portrait -> 2 distinct shapes
    fx["shapes-two-distinct-shapes"] = re.sub(r'data-shows="(?!event_photo)[a-z_]+"',
                                              'data-shows="portrait"', p)
    # §3.8 "Never-lead, resolved 2026-07-26": key_art + portrait, issue-wide.
    fx["shapes-portrait-lead"] = one(
        p, 'data-shows="event_photo" data-capture-year="2026" data-licence="PRESS-KIT-EDITORIAL"',
           'data-shows="portrait" data-capture-year="2026" data-licence="PRESS-KIT-EDITORIAL"')
    fx["shapes-keyart-lead-nonpb"] = one(
        p, 'data-shows="event_photo" data-capture-year="2026" data-licence="CC-BY-4.0"',
           'data-shows="key_art" data-capture-year="2026" data-licence="CC-BY-4.0"')
    fx["shapes-productshot-lead"] = one(p, 'data-shows="gameplay" data-capture-year="2026"',
                                           'data-shows="product_shot" data-capture-year="2026"')
    # cross-issue: c0fbc060b733 is recorded in the REAL assets/cached/manifest.json
    # as led:[17], and this fixture's masthead FOLIO says 18.
    fx["shapes-repeat-lead"] = one(p, 'src="/assets/cached/af9fc905ced8.jpg"',
                                      'src="/assets/cached/c0fbc060b733.jpg"')
    fx["shapes-touchline-result-keyart"] = one(
        one(p, TL_CAP_SHIPPED, TL_CAP_RESULT),
        'data-shows="event_photo" data-capture-year="2026" data-licence="PRESS-KIT-EDITORIAL"',
        'data-shows="key_art" data-capture-year="2026" data-licence="PRESS-KIT-EDITORIAL"')
    fx["shapes-touchline-result-ok"] = one(p, TL_CAP_SHIPPED, TL_CAP_RESULT)          # PASSING

    # ── §3.4 · polymorphic table kind ───────────────────────────────────────
    fx["table-kind-bad"] = one(p, 'data-table-kind="championship"', 'data-table-kind="table"')
    fx["table-kind-finance"] = one(p, 'data-table-kind="league"', 'data-table-kind="finance"')

    # ── criterion #7 · sport tokens + results-ledger breadth (§3.11) ────────
    fx["ledger-one-sport"] = one(p, TL_FIG_ANCHOR, ledger_html(ONE_SPORT_ROWS) + TL_FIG_ANCHOR)
    fx["ledger-two-sports"] = one(p, TL_FIG_ANCHOR, ledger_html(TWO_SPORT_ROWS) + TL_FIG_ANCHOR)
    fx["ledger-multi-sport-token"] = one(p, TL_FIG_ANCHOR, ledger_html(
        ONE_SPORT_ROWS[:1] + [("multi_sport", "26 JUL",
                               "<b>Commonwealth Games</b> — day 4", "DAY 4")]) + TL_FIG_ANCHOR)
    fx["ledger-unknown-token"] = one(p, TL_FIG_ANCHOR, ledger_html(
        ONE_SPORT_ROWS[:1] + [("lawn_bowls", "26 JUL",
                               "<b>Commonwealth Games</b> — pairs final", "GOLD")]) + TL_FIG_ANCHOR)

    # ── criterion #6 · a matured loop REPORTED in the HTML (the passing case) ─
    fx["loop-resolved"] = one(p, THREADS_BAND, THREADS_BAND + '\n'
        '    <div class="mx-ledger" data-mx-event="ledger" data-role="results-ledger">\n'
        '      <div class="mx-ledger__row" data-sport="football"'
        ' data-resolves-loop="loop_2026-07-19_fixture-final">'
        '<span class="mx-ledger__date">19 JUL</span><span class="mx-ledger__match">'
        '<b>FIXTURE DATA — not a real event: Fixture Cup final</b> — carried forward from last week'
        '</span><span class="mx-ledger__result">DONE</span></div>\n'
        '      <div class="mx-ledger__row" data-sport="golf">'
        '<span class="mx-ledger__date">19 JUL</span><span class="mx-ledger__match">'
        '<b>FIXTURE DATA — not a real event: Fixture Open</b> — final round</span>'
        '<span class="mx-ledger__result">R4</span></div>\n'
        '    </div>')
    return fx


# ═════════════════════════════════════════════════════════════════════════════
# 2. State fixtures
# ═════════════════════════════════════════════════════════════════════════════
# Two families, deliberately different in shape:
#
#  * weekly-*.json are FULL copies of the real state with one key replaced.
#    validate-issue.py reads several state keys at once (open_loops,
#    sports_calendar, interest_depth, research_cut_at, used_image_urls), so a
#    partial state would exercise its tolerance paths rather than the rule.
#  * rutted-*.json / open-loop-matured.json are MINIMAL standalone objects.
#    The two upstream validators read exactly one key each, and a minimal fixture
#    makes the ledger under test readable in ten lines.

FIXTURE_TAG = "FIXTURE DATA — not a real event"


def build_states(real_state: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}

    # (a) criterion #6 — a MATURED open loop. The two loops seeded in the real
    #     state are `dropped` (honest history: neither the World Cup final nor The
    #     Open was ever reported, and #18 is frozen), and a DROPPED LOOP DOES NOT
    #     MATURE — so the seeds cannot make the §3.7 gates fire. SPEC §4 requires
    #     this fixture; WP-1 handoff 6 flagged it three times.
    s = copy.deepcopy(real_state)
    s["open_loops"] = [
        {"id": "loop_2026-07-19_fixture-final",
         "claim": f"{FIXTURE_TAG}: Fixture Cup final, concluding Sunday 19 July 2026",
         "expected_resolution_date": "2026-07-19", "band": "touchline",
         "issue_opened": 17, "status": "open", "resolution": None},
        {"id": "loop_2026-08-30_fixture-later",
         "claim": f"{FIXTURE_TAG}: a loop that has not matured yet",
         "expected_resolution_date": "2026-08-30", "band": "touchline",
         "issue_opened": 18, "status": "open", "resolution": None},
    ]
    out["weekly-matured-loop"] = s

    # (b) criterion #7 — a window in which TWO tracked sports concluded. The Open
    #     (golf, ends 2026-07-19) is real seeded data; the football row is invented
    #     fixture data, because the seeded calendar has no football event ending
    #     inside any July window.
    s = copy.deepcopy(real_state)
    s["research_cut_at"] = "2026-07-12T02:00:00Z"
    s["open_loops"] = []
    s["sports_calendar"] = [{
        "event": f"{FIXTURE_TAG}: Fixture Cup final", "sport": "football",
        "start": "2026-07-18", "end": "2026-07-18", "importance": 1,
        "reader_relevant": True, "needs_verification": True,
    }] + s["sports_calendar"]
    out["weekly-two-sports"] = s

    # (c) same window, golf switched off -> one tracked sport concluded -> the
    #     invariant is correctly NOT APPLICABLE. This is the case that proves the
    #     check is conditional and not a blanket "ledgers must be multi-sport".
    s = copy.deepcopy(out["weekly-two-sports"])
    s["interest_depth"]["golf"] = "off"
    s["sports_calendar"] = [e for e in s["sports_calendar"] if e["sport"] != "multi_sport"]
    out["weekly-golf-off"] = s

    # (d) criterion #7 — an ABSENT interest_depth key is UNSET, never `off`
    #     (WP-1 correction). cricket and athletics have no key at all and must
    #     still count as tracked, or defect D's invisible-sport problem reappears.
    s = copy.deepcopy(real_state)
    s["research_cut_at"] = "2026-07-12T02:00:00Z"
    s["open_loops"] = []
    s["interest_depth"] = {"motorsport": "results_only", "football": "full", "golf": "off"}
    s["sports_calendar"] = [
        {"event": f"{FIXTURE_TAG}: Fixture Test match, day 5", "sport": "cricket",
         "start": "2026-07-15", "end": "2026-07-19", "importance": 1,
         "reader_relevant": True, "needs_verification": True},
        {"event": f"{FIXTURE_TAG}: Fixture Diamond League meet", "sport": "athletics",
         "start": "2026-07-18", "end": "2026-07-18", "importance": 2,
         "reader_relevant": True, "needs_verification": True},
    ]
    out["weekly-unset-sports"] = s

    # (e) criterion #5 — minimal state for validate-research-bundle.py. Three
    #     loops: one MATURED, one open-but-not-due, one `dropped` with a PAST due
    #     date (which must not mature — that is the whole point of WP-1's note).
    out["open-loop-matured"] = {
        "open_loops": [
            {"id": "loop_2026-07-19_wc-final-open",
             "claim": "World Cup final, Spain v Argentina, MetLife",
             "expected_resolution_date": "2026-07-19", "band": "touchline",
             "issue_opened": 17, "status": "open", "resolution": None},
            {"id": "loop_2026-08-02_games-close",
             "claim": "Commonwealth Games closing ceremony",
             "expected_resolution_date": "2026-08-02", "band": "touchline",
             "issue_opened": 18, "status": "open", "resolution": None},
            {"id": "loop_2026-07-19_open-final-round-dropped",
             "claim": "The Open Championship final round",
             "expected_resolution_date": "2026-07-19", "band": "touchline",
             "issue_opened": 17, "status": "dropped",
             "resolution": "Never reported in the weekly of record."},
        ],
    }

    # (f) criterion #4 — a cover_lead_ledger RUTTED on uk_politics: 3 of the last
    #     4 entries led on news with the same family. The REAL ledger is not
    #     rutted (uk_politics appears once as news in its last 4), which is why
    #     this fixture has to exist — and is also the precondition for the rule
    #     being a real test rather than an artefact.
    out["rutted-uk-politics"] = {
        "open_loops": [],
        "cover_lead_ledger": [
            {"issue": 18, "date": "2026-07-26", "topic_family": "uk_politics",
             "one_line": "Burnham's first ordinary week", "led_on": "news"},
            {"issue": 17, "date": "2026-07-19", "topic_family": "uk_politics",
             "one_line": "A reshuffle nobody asked for", "led_on": "news"},
            {"issue": 16, "date": "2026-07-13", "topic_family": "space_exploration",
             "one_line": "Telstar 1", "led_on": "long_read"},
            {"issue": 15, "date": "2026-07-05", "topic_family": "uk_politics",
             "one_line": "The Budget that wasn't", "led_on": "news"},
            {"issue": 14, "date": "2026-06-28", "topic_family": "iran_war",
             "one_line": "Ceasefires into paperwork", "led_on": "news"},
        ],
    }

    # (g) criterion #4 — rutted on a family this plan does NOT lead on. The rule
    #     must not fire. This is the fixture that proves it is a forced conscious
    #     choice and not a suppression gate.
    out["rutted-other-family"] = {
        "open_loops": [],
        "cover_lead_ledger": [
            {"issue": 18, "date": "2026-07-26", "topic_family": "us_politics",
             "one_line": "x", "led_on": "news"},
            {"issue": 17, "date": "2026-07-19", "topic_family": "us_politics",
             "one_line": "y", "led_on": "news"},
            {"issue": 16, "date": "2026-07-13", "topic_family": "us_politics",
             "one_line": "z", "led_on": "news"},
            {"issue": 15, "date": "2026-07-05", "topic_family": "iran_war",
             "one_line": "w", "led_on": "news"},
        ],
    }
    return out


# ═════════════════════════════════════════════════════════════════════════════
# 3. Weekly chapter plans (criteria #1 and #4)
# ═════════════════════════════════════════════════════════════════════════════
# Generated rather than hand-written because a valid weekly plan needs all ten
# required bands and a >=6,000-word allocation, so the four fixtures differ from
# each other by one field in ~8 KB of boilerplate. The deltas are the fixture.

RATIONALE = (
    "The Commonwealth Games close on 2 Aug and the BoE held on 30 Jul; the Games' medal ledger is "
    "the week's biggest reader-relevant result, so the rate call runs in The Ledger and the Games "
    "take the cover."
)
OVERRIDE = (
    "Burnham lost a confidence vote this week, which is a change of government rather than another "
    "week of the same holding pattern, so it earns the cover a fourth time."
)
BANDS = [("the_letter", 450), ("week_in_numbers", 150), ("caught_up", 500),
         ("long_read", 1800), ("touchline", 650), ("pixel_byte", 550),
         ("screen_sound", 550), ("bookmark", 400), ("the_desk", 900),
         ("the_threads", 400), ("on_the_radar", 300), ("do_this_week", 150),
         ("colophon", 100)]


def _chapter(cid: str, num: int, words: int) -> dict:
    ch = {
        "chapter_id": cid, "chapter_num": num, "chapter_type": "opener",
        "chapter_title": cid.replace("_", " ").title(), "chapter_arc": "arc",
        "ground": "paper", "is_hype": False, "data_venue": None,
        "target_word_count": words, "images_needed": [], "key_facts": [],
        "forbidden_topics": [], "cross_refs": [],
        "nav_coverline": cid.replace("_", " ").upper(),
    }
    if cid == "long_read":
        ch["images_needed"] = [{"role": "front-dial gearing diagram",
                                "source_constraint": "open-access journal figure (CC BY)",
                                "alt_required": True}]
        ch["vintage"] = "evergreen"
        ch["material_span"] = "1901–2021"
        ch["latest_development"] = "2021-03"
    if cid == "week_in_numbers":
        ch["rows"] = [{"key": "Pole Margin", "source_band": "touchline", "value": "0.012s"},
                      {"key": "Sessions Logged", "source_band": "state", "value": "4"}]
    if cid == "touchline":
        ch["pieces"] = [{"role": "lead", "topic_family": "uk_politics",
                         "word_count_target": {"min": 300, "max": 500},
                         "headline_hint": "Burnham's first ordinary week",
                         "link_targets": ["https://example.com/a"]}]
        ch["results_ledger"] = [
            {"date": "2026-07-25", "event": "Serie A opener", "result": "Juve 2-1 Inter",
             "sport": "football"},
            {"date": "2026-07-24", "event": "Games 10,000m final", "result": "Gold, GBR",
             "sport": "athletics"}]
    return ch


def _base_plan() -> dict:
    return {
        "issue_meta": {
            "format": "weekly", "date": "2026-08-02", "topic": "weekly",
            "special_id": None, "execution_mode": "parallel", "issue_number": 19,
            "research_cut_at": "2026-08-02T02:10:00Z",
            "window": {"from": "2026-07-26T02:10:00Z", "to": "2026-08-02T02:10:00Z"},
            "cover_leads_on": "news",
            "cover_lead_topic_family": "uk_politics",
            "lead_rationale": RATIONALE,
        },
        "cover": {"lead_head": "Burnham's first ordinary week",
                  "standfirst": "A government settles into the job."},
        "chapters": [_chapter(cid, i, w) for i, (cid, w) in enumerate(BANDS, start=1)],
        "assets": {"css_inject_marker": "<!-- INJECT:CSS -->",
                   "js_inject_marker": "<!-- INJECT:JS -->", "scaffold_parts_used": []},
        "compliance": {"stat_budget_max": 12, "image_source_diversity_min": 0.5,
                       "accent_lockdown": True},
    }


def build_plans() -> dict[str, dict]:
    out: dict[str, dict] = {}

    # the valid baseline (passes clean) — the passing case of #1 and the
    # firing-case *input* of #4
    out["weekly-valid"] = _base_plan()

    # criterion #1 firing case — a single-field delta: the long_read omits vintage
    p = _base_plan()
    for ch in p["chapters"]:
        if ch["chapter_id"] == "long_read":
            for k in ("vintage", "material_span", "latest_development"):
                ch.pop(k, None)
    out["weekly-no-vintage"] = p

    # criterion #1, the other direction — a NEWS anchor carrying evergreen metadata
    p = _base_plan()
    for ch in p["chapters"]:
        if ch["chapter_id"] == "long_read":
            ch["vintage"] = "news"
    out["weekly-news-vintage-with-span"] = p

    # criterion #4 passing case — the same plan plus a written override reason
    p = _base_plan()
    p["issue_meta"]["lead_override_reason"] = OVERRIDE
    out["weekly-rut-overridden"] = p

    # criterion #4, the typo that would silently disable the rule: an out-of-enum
    # cover_lead_topic_family can never intersect the ledger, so the rut rule would
    # pass while checking nothing. WP-5 round 2 made this a HARD fail.
    p = _base_plan()
    p["issue_meta"]["cover_lead_topic_family"] = "uk_polotics"
    out["weekly-clf-out-of-enum"] = p

    # criterion #4 compatibility path — a PRE-AMENDMENT plan with no
    # cover_lead_topic_family at all. The rut verdict must still be reached by
    # falling back to pieces[role=lead].
    p = _base_plan()
    p["issue_meta"].pop("cover_lead_topic_family")
    out["weekly-no-clf"] = p

    # …and one with neither the field nor any lead piece: warn-and-skip, never a
    # rut failure on a family the plan never declared.
    p = _base_plan()
    p["issue_meta"].pop("cover_lead_topic_family")
    for ch in p["chapters"]:
        ch.pop("pieces", None)
    out["weekly-no-family-at-all"] = p

    # §3.11 — a results-ledger row tagged multi_sport (hard fail) plus one
    # off-list token (warn only, because a check that blocks a genuinely new sport
    # blocks the breadth it exists to force)
    p = _base_plan()
    for ch in p["chapters"]:
        if ch["chapter_id"] == "touchline":
            ch["results_ledger"][0]["sport"] = "multi_sport"
            ch["results_ledger"][1]["sport"] = "lawn_bowls"
    out["weekly-multi-sport"] = p
    return out


# ═════════════════════════════════════════════════════════════════════════════
# 4. Research bundles (criterion #5)
# ═════════════════════════════════════════════════════════════════════════════
_VERIFIED = {"head_status": 200, "content_type": "image/jpeg",
             "verified_at": "2026-07-26T01:44:00Z", "verified_by": "orchestrator"}
_LIC = {"holder": "Test Holder", "code": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/", "allows_derivatives": True}
# 4 source types, no domain over 50%, 16 unique URLs, 4 distinct shapes — so the
# ONLY variable between the firing and passing bundle is the resolving fact.
_DOMAINS = ["upload.wikimedia.org", "media.springernature.com",
            "images.nasa.gov", "blog.playstation.com"]
_SHAPES = ["event_photo", "diagram", "artefact", "gameplay"]


def _candidate(i: int) -> dict:
    return {"url_or_keyword": f"https://{_DOMAINS[i % 4]}/coverage-rebuild-fixture-{i}.jpg",
            "verified": dict(_VERIFIED), "context": f"fixture candidate {i}",
            "shows": _SHAPES[i % 4], "capture_year": 2024, "licence": dict(_LIC)}


def build_bundles() -> dict[str, dict]:
    fact = {"claim": "Spain beat Argentina 2-1 in the World Cup final at MetLife Stadium",
            "status": "happened", "date": "2026-07-19",
            "source_url": "https://www.bbc.co.uk/sport/football/fixture-report",
            "resolves_loop": "loop_2026-07-19_wc-final-open"}
    return {
        # criterion #5 passing case
        "loop-resolved": {"image_candidates": [_candidate(i) for i in range(16)],
                          "facts": [fact]},
        # criterion #5 firing case — the result is in the bundle but claims no loop
        "loop-unresolved": {"image_candidates": [_candidate(i) for i in range(16)],
                            "facts": [{k: v for k, v in fact.items() if k != "resolves_loop"}]},
        # the regression that would have caught this build's own breakage: WP-6
        # retired the Wikimedia thresholds and validate-research-bundle.py read
        # them unguarded, so Phase 3b crashed with KeyError in-tree.
        "repro-retired-threshold-keyerror": {
            "image_candidates": [_candidate(0), _candidate(4)],   # both Wikimedia
            "facts": []},
    }


# ═════════════════════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output directory (created if absent)")
    ap.add_argument("--issue", default=str(DEFAULT_ISSUE),
                    help="frozen Issue #18 HTML (read-only)")
    ap.add_argument("--state", default=str(DEFAULT_STATE),
                    help="real state/signal-state.json (read-only)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    issue = pathlib.Path(a.issue)
    state = pathlib.Path(a.state)
    for p in (issue, state):
        if not p.is_file():
            print(f"FATAL: fixture input not found: {p}", file=sys.stderr)
            return 2
    out = pathlib.Path(a.out)

    weekly = build_weekly(issue.read_text(encoding="utf-8"))
    for name, html in weekly.items():
        write(out / "weekly" / f"{name}.html", html)

    states = build_states(json.loads(state.read_text(encoding="utf-8")))
    for name, obj in states.items():
        write_json(out / "states" / f"{name}.json", obj)

    for name, obj in build_plans().items():
        write_json(out / "plans" / f"{name}.json", obj)
    for name, obj in build_bundles().items():
        write_json(out / "bundles" / f"{name}.json", obj)

    # an empty state, for the "no open_loops is legal, not a pass mark" tolerance
    write(out / "states" / "empty.json", "{}\n")

    if not a.quiet:
        print(f"fixtures -> {out}")
        print(f"  weekly/  {len(weekly)} html  (from {issue.name}, frozen)")
        print(f"  states/  {len(states) + 1} json (from {state.name})")
        print(f"  plans/   {len(build_plans())} json")
        print(f"  bundles/ {len(build_bundles())} json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
