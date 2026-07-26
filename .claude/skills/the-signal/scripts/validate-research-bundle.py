#!/usr/bin/env python3
"""
validate-research-bundle.py — Phase 3b upstream PRODUCTION AID (not a ship gate).

**Where this sits (SPEC 2026-07-26 §1).** The gate ledger is exactly three ship
gates: (1) validate-issue.py image checks, (2) validate-issue.py markup
contracts, (3) the Phase 9.5 holistic read. This script is NOT a fourth one. A
hard fail here halts **production** — the planner does not spawn until the
researcher fixes the bundle — it does not fail a finished issue's ship. Every
report below prints that distinction; do not promote this to a ship gate.

Validates research-bundle.json BEFORE the planner spawns, catching the failure
modes that propagated through the 17 May test issue and the Issue #18 review:

  1. Fabricated URLs   — image_candidates entries with `url_or_keyword`
                         containing a keyword ("Wikimedia: Starmer") instead
                         of a verified URL. Forces writers to invent URLs.

  2. Mono-sourcing     — too many entries from one domain (typically Wikimedia
                         Special:FilePath because it verifies easily). Fails
                         RT-5 (single-domain >50%).

  3. Fact provenance   — every load-bearing claim carries status/date/source,
                         and a `status: "happened"` claim dated after the run
                         date is rejected (the "Norris on pole" temporal hole).

  4. Same-safe-shape   — (SPEC §3.2/§3.8/§3.14, 2026-07-26) every candidate
     bundles           declares WHAT IT SHOWS, its capture year and its licence,
                         and the bundle must offer at least
                         `thresholds.min_distinct_shapes` distinct `shows`
                         values. See § "Retired thresholds" below.

  5. Abandoned loops   — (SPEC §3.7, needs --state) a **matured** open loop
                         (`status: "open"` and `expected_resolution_date <=`
                         run date) with no `facts[].resolves_loop` naming it is
                         a hard fail: last week's promised result must come back.

**Retired thresholds, 2026-07-26 (SPEC §3.14, WP-6).** This script used to read
`thresholds["wikimedia_max_count"]` and `["wikimedia_max_pct"]`. WP-6 moved both
into `retired_thresholds` in references/image-source-types.json, which made those
two unguarded reads raise `KeyError` and broke the gate in-tree. They are now
replaced by the `min_distinct_shapes` FLOOR over `image_candidates[].shows` — a
ceiling on one domain reads as a target to fill up to, while nothing required an
informative shape. Do not reinstate the ceilings; the `shows` enum and the
threshold are read from the lookup file (never hardcoded here) exactly as
scripts/check-image-diversity.sh reads them, so the two cannot drift.

Reads the lookup table at references/image-source-types.json to classify
domains. Domains not in the lookup are flagged as "unknown" — counted toward
domain-ratio thresholds but not toward source-type diversity.

Usage:
  python3 scripts/validate-research-bundle.py /tmp/signal-build/research-bundle.json \
      --run-date 2026-07-26 --state state/signal-state.json

Exit codes:
  0 — PASS
  1 — FAIL (one or more rules violated; report printed). Production halt, NOT a
      ship failure: re-spawn the researcher and re-run. Nothing has been shipped.
  2 — usage / missing file / unreadable state
"""
import argparse
import concurrent.futures
import datetime
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def head_verify(url: str, timeout: float = 6.0) -> tuple[int | str, str]:
    """HEAD-check a URL; fall back to range-GET on 4xx that block HEAD.
    Returns (status_or_error_str, content_type)."""
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": BROWSER_UA,
        "Accept": "image/*,*/*;q=0.5",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status, (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower())
    except urllib.error.HTTPError as e:
        if e.code in (403, 405, 501):
            try:
                req_get = urllib.request.Request(url, method="GET", headers={
                    "User-Agent": BROWSER_UA,
                    "Accept": "image/*,*/*;q=0.5",
                    "Range": "bytes=0-0",
                })
                with urllib.request.urlopen(req_get, timeout=timeout) as resp:
                    return (resp.status, (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower())
            except Exception as e2:
                return (f"HEAD {e.code} / GET {e2.__class__.__name__}", "")
        deny = (e.headers.get("x-deny-reason") if e.headers else None) or ""
        if deny:
            return (f"blocked:{deny}", "")
        return (e.code, "")
    except urllib.error.URLError as e:
        if "host_not_allowed" in str(e.reason) or "Network is unreachable" in str(e.reason):
            return ("blocked:egress", "")
        return (f"URLError:{e.reason}", "")
    except Exception as e:
        return (f"{e.__class__.__name__}:{e}", "")


def load_lookup(skill_dir: Path) -> dict:
    p = skill_dir / "references" / "image-source-types.json"
    if not p.exists():
        print(f"ERROR: lookup table not found at {p}", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text())


def classify_domain(url: str, lookup: dict, explicit_type: str | None = None) -> str:
    """Return source_type for a URL. explicit_type wins; otherwise lookup by domain."""
    if explicit_type and explicit_type in lookup["types"]:
        return explicit_type
    netloc = urlparse(url).netloc.lower()
    # Strip leading www. — but only as a fallback; some keys include www.
    if netloc in lookup["domains"]:
        return lookup["domains"][netloc]
    stripped = netloc.removeprefix("www.")
    if stripped in lookup["domains"]:
        return lookup["domains"][stripped]
    # Flickr-style ambiguous host: needs explicit annotation
    if netloc in lookup.get("ambiguous_domains", {}):
        return "ambiguous"
    return "unknown"


VALID_FACT_STATUS = ("happened", "upcoming")
VALID_FACT_TYPES = ("fact", "opinion")

# SPEC §3.2 / data-contracts.md § Research bundle — the licence machine record.
LICENCE_REQUIRED_KEYS = ("holder", "code", "url", "allows_derivatives")
# `capture_year: null` is legal ONLY for a synthetic diagram/chart (SPEC §3.2).
CAPTURE_YEAR_NULLABLE_SHOWS = ("diagram", "chart")
# Earliest plausible capture year — photography/print, sanity bound only.
CAPTURE_YEAR_FLOOR = 1400


def parse_iso_date(s: str) -> datetime.date | None:
    """Parse a YYYY-MM-DD date. Returns None if unparseable."""
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None


def validate_facts(bundle: dict, run_date: datetime.date) -> tuple[list[str], list[str]]:
    """Phase 3b fact-provenance gate (mirror of the image verification chain).

    Each entry in the bundle's `facts` array is a structured record the
    researcher fills in *while the sources are open* — moving the
    "has this happened / who said it?" judgment upstream, out of the writer's
    prose. Required shape:

      {
        "claim":      "<one-line statement>",
        "status":     "happened" | "upcoming",
        "date":       "YYYY-MM-DD",          # the date of the event/claim
        "source_url": "https://…",
        "type":       "fact" | "opinion",    # optional, defaults to "fact"
        "speaker":    "<name>",              # REQUIRED iff type == "opinion"
        "quote":      "<the real words>"     # REQUIRED iff type == "opinion"
      }

    Rules enforced:
      F1  claim / status / date / source_url present and well-typed.
      F2  status in {happened, upcoming}; date parses as YYYY-MM-DD;
          source_url is an http(s) URL.
      F3  TEMPORAL CATCH — a fact tagged status=happened whose date is AFTER
          the run date cannot have occurred yet. This is the structural close
          of the State-of-Play / "Norris on pole" hole: the determination is
          made here, upstream, against when facts were knowable — not deferred
          to the writer rendering past tense against the issue's cover date.
      F5  CARRY-FORWARD JOIN KEY (SPEC §3.2) — the optional `resolves_loop` must
          be a non-empty string when present. It is a FOREIGN KEY into state's
          `open_loops[].id`; with --state, an id that matches no loop is a hard
          fail (a typo'd join key silently abandons the loop it claims to close).
      F4  BORROWED-ANGLE PROVENANCE — a fact with type=opinion must carry a
          non-empty `speaker` AND `quote`. You can only name a person (or hang
          an angle on them) when the real words are in the bundle; otherwise
          the angle is voiced unattributed in our own voice (see editorial-spec
          § "Borrowed angles, our voice").

    Returns (failures, warnings). An absent/empty `facts` array is a WARNING,
    not a failure — a thin-news section may legitimately carry none — but a
    malformed entry is always a hard fail.
    """
    failures: list[str] = []
    warnings: list[str] = []

    facts = bundle.get("facts", [])
    if not isinstance(facts, list):
        return ([f"  `facts` must be an array, got {type(facts).__name__}."], [])
    if not facts:
        warnings.append(
            "  bundle has no `facts` array — load-bearing claims cannot be "
            "provenance-checked upstream. Acceptable only for a genuinely fact-thin issue."
        )
        return (failures, warnings)

    for i, f in enumerate(facts):
        ctx = f.get("claim", f"facts[{i}]") if isinstance(f, dict) else f"facts[{i}]"
        ctx = (ctx[:60] + "…") if len(str(ctx)) > 61 else ctx
        if not isinstance(f, dict):
            failures.append(f"  facts[{i}]: must be an object, got {type(f).__name__}.")
            continue

        # F1 / F2 — required fields + types
        claim = f.get("claim")
        if not isinstance(claim, str) or not claim.strip():
            failures.append(f"  facts[{i}] ({ctx}): missing/empty `claim`.")

        status = f.get("status")
        if status not in VALID_FACT_STATUS:
            failures.append(
                f"  facts[{i}] ({ctx}): status={status!r}, must be one of {VALID_FACT_STATUS}.\n"
                f"    The researcher decides happened-vs-upcoming while the sources are open; the writer renders the tag."
            )

        date_raw = f.get("date")
        fdate = parse_iso_date(date_raw)
        if fdate is None:
            failures.append(f"  facts[{i}] ({ctx}): date={date_raw!r} is not a YYYY-MM-DD date.")

        src = f.get("source_url")
        if not (isinstance(src, str) and src.startswith(("http://", "https://"))):
            failures.append(
                f"  facts[{i}] ({ctx}): source_url={src!r} must be an http(s) URL — "
                f"every load-bearing fact traces to a source, same discipline as image candidates."
            )

        # F3 — temporal catch (only meaningful when status + date are valid)
        if status == "happened" and fdate is not None and fdate > run_date:
            failures.append(
                f"  facts[{i}] ({ctx}): status=happened but date {fdate} is AFTER the run date {run_date}.\n"
                f"    It cannot have happened yet. Tag it status=upcoming (writer renders it as forthcoming),\n"
                f"    or drop it. This is the State-of-Play / 'Norris on pole' temporal hole, caught upstream."
            )

        # F4 — borrowed-angle provenance
        ftype = f.get("type", "fact")
        if ftype not in VALID_FACT_TYPES:
            failures.append(f"  facts[{i}] ({ctx}): type={ftype!r}, must be one of {VALID_FACT_TYPES}.")
        if ftype == "opinion":
            speaker = f.get("speaker")
            quote = f.get("quote")
            if not (isinstance(speaker, str) and speaker.strip()):
                failures.append(
                    f"  facts[{i}] ({ctx}): type=opinion requires a non-empty `speaker`.\n"
                    f"    Name a person only when the real words back it; otherwise voice the angle unattributed."
                )
            if not (isinstance(quote, str) and quote.strip()):
                failures.append(
                    f"  facts[{i}] ({ctx}): type=opinion requires a non-empty `quote` (the real words).\n"
                    f"    Borrowed angle = real provenance: no quote in the bundle ⇒ the writer cannot attribute it."
                )

        # F5 — carry-forward join key shape (the id ↔ state cross-check is in
        # validate_open_loops, which needs --state).
        if "resolves_loop" in f:
            rl = f.get("resolves_loop")
            if not (isinstance(rl, str) and rl.strip()):
                failures.append(
                    f"  facts[{i}] ({ctx}): resolves_loop={rl!r} must be a non-empty string — it is the\n"
                    f"    foreign key into state.open_loops[].id (SPEC §3.2). Omit the field entirely if this\n"
                    f"    fact closes no loop; do not carry an empty or null placeholder."
                )

    return (failures, warnings)


def validate_open_loops(bundle: dict, state: dict, run_date: datetime.date) -> tuple[list[str], list[str], list[dict]]:
    """SPEC §3.7 — the open-loop resolution rule, bundle side.

    A loop is **matured** when `status == "open"` and
    `expected_resolution_date <= run_date`. A matured loop with no `facts[]`
    entry carrying a matching `resolves_loop` is a HARD FAIL: this is defect D's
    structural close. `status: "upcoming"` facts were gate-checked and then
    abandoned, so issue #17 carried "World Cup final, Spain v Argentina, 15:00 ET
    today" and issue #18 never reported the result — five verification layers
    refusing to guess a result, and no counterpart obligation to report it once it
    happened.

    Not matured, deliberately: `resolved` (already closed) and `dropped` (an
    honest terminal state for a loop that was never reported — it records the miss
    instead of deleting it). Both seeded loops in state are `dropped`, so the
    seeded state alone will NOT make this rule fire; a fixture with
    `status: "open"` and a past `expected_resolution_date` is required to
    demonstrate it (WP-1 handoff 6 / WP-9 handoff 5).

    An absent, empty or malformed-but-loopless `open_loops[]` is NOT a failure —
    no loops means no obligation (WP-9 handoff 3).

    Returns (failures, warnings, matured_loops).
    """
    failures: list[str] = []
    warnings: list[str] = []
    matured: list[dict] = []

    loops = state.get("open_loops")
    if loops is None:
        warnings.append(
            "  state carries no `open_loops[]` — SPEC §3.7 has nothing to mature this run. "
            "That is legal (a first run, or a week that opened no loops), not a pass mark."
        )
        return (failures, warnings, matured)
    if not isinstance(loops, list):
        failures.append(
            f"  state.open_loops must be an array, got {type(loops).__name__}. "
            f"The §3.7 maturity rule cannot run against it."
        )
        return (failures, warnings, matured)

    facts = bundle.get("facts")
    facts = facts if isinstance(facts, list) else []
    resolved_ids: dict[str, int] = {}
    for i, f in enumerate(facts):
        if isinstance(f, dict) and isinstance(f.get("resolves_loop"), str) and f["resolves_loop"].strip():
            resolved_ids.setdefault(f["resolves_loop"].strip(), i)

    loop_ids = {l.get("id") for l in loops if isinstance(l, dict)}

    # A resolves_loop naming no loop at all: the writer will render
    # data-resolves-loop="<id>" for a loop that does not exist, and the real loop
    # stays open with nobody watching it.
    for rid, fi in sorted(resolved_ids.items()):
        if rid not in loop_ids:
            failures.append(
                f"  facts[{fi}]: resolves_loop={rid!r} matches no id in state.open_loops[] "
                f"(known ids: {sorted(x for x in loop_ids if isinstance(x, str))}).\n"
                f"    `resolves_loop` is a foreign key, not a label (data-contracts.md § facts[]). Fix the id\n"
                f"    or drop the field — as written, the loop it claims to close is still open and unwatched."
            )

    for j, l in enumerate(loops):
        if not isinstance(l, dict):
            failures.append(f"  state.open_loops[{j}]: must be an object, got {type(l).__name__}.")
            continue
        if l.get("status") != "open":
            continue
        lid = l.get("id")
        erd = parse_iso_date(l.get("expected_resolution_date"))
        if erd is None:
            failures.append(
                f"  state.open_loops[{j}] ({lid!r}): status=open but "
                f"expected_resolution_date={l.get('expected_resolution_date')!r} is not a YYYY-MM-DD date.\n"
                f"    An open loop whose date cannot be parsed can never mature — it would sit in state "
                f"forever, unreported and unenforced."
            )
            continue
        if erd <= run_date:
            matured.append(l)

    for l in matured:
        lid = l.get("id")
        if not (isinstance(lid, str) and lid in resolved_ids):
            failures.append(
                f"  §3.7 MATURED LOOP UNRESOLVED: {lid!r} — expected resolution "
                f"{l.get('expected_resolution_date')}, on or before the run date {run_date}, "
                f"status=open.\n"
                f"    claim: {str(l.get('claim'))[:120]}\n"
                f"    owed by band: {l.get('band')!r} (opened in issue {l.get('issue_opened')!r}).\n"
                f"    No facts[] entry carries resolves_loop={lid!r}. The event this issue promised has\n"
                f"    happened; the bundle must carry the RESULT — a fact with the outcome, its date, its\n"
                f"    source_url and resolves_loop={lid!r} — or the loop must be closed in state as\n"
                f"    `dropped` with a reason (an honest recorded miss, not a silent one). This is defect D:\n"
                f"    the World Cup final was carried as upcoming and the result never reported."
            )

    return (failures, warnings, matured)


def validate_image_records(candidates: list, lookup: dict,
                          run_date: datetime.date) -> tuple[list[str], list[str], Counter]:
    """SPEC §3.2 + §3.14 — what each image SHOWS, when it was captured, its licence.

    Three required additions per `image_candidates[]` entry (WP-1 canonicalised in
    references/spec/data-contracts.md § Research bundle):

      `shows`        — REQUIRED, from the canonical enum in
                       references/image-source-types.json (`shows.values` keys).
                       The enum is READ from that file, never copied here: WP-6
                       owns it and a second copy is how the taxonomy drifted in
                       the first place. Orthogonal to `source_type` — a press kit
                       can supply `key_art` or `gameplay`, and the domain never
                       tells you which (defect E: Issue #18's Halo lead cleared
                       min_distinct_source_types comfortably while telling the
                       reader nothing the headline hadn't).
      `capture_year` — REQUIRED integer; `null` ONLY when
                       `shows ∈ {diagram, chart}` AND the asset is synthetic.
                       Defect B: a 2007 perspex reconstruction illustrated a 2021
                       breakthrough because nothing recorded the image's vintage.
                       WP-4's caption-vintage rule (§3.9) is a pure function of
                       this field, so it must be present and honest.
      `licence`      — REQUIRED object {holder, code, url, allows_derivatives}.
                       The credit line was prose, so extract-covers.py could not
                       know Issue #18's cover source was CC BY-**ND** before
                       smart-cropping it (§3.10, a live violation).

    Then the bundle-wide FLOOR that replaced the retired Wikimedia ceilings
    (§3.14): at least `thresholds.min_distinct_shapes` distinct `shows` values
    across the candidates, so the planner has something other than the same safe
    shape to route into every slot.

    Returns (failures, warnings, shows_counter).
    """
    failures: list[str] = []
    warnings: list[str] = []
    shapes: Counter = Counter()

    shows_block = lookup.get("shows") or {}
    shows_enum = list((shows_block.get("values") or {}).keys())
    info_shapes = shows_block.get("information_figure_shapes", [])
    last_resort = shows_block.get("last_resort_shapes", [])
    thresholds = lookup.get("thresholds", {})
    min_shapes = thresholds.get("min_distinct_shapes", 3)

    if not shows_enum:
        failures.append(
            "  references/image-source-types.json carries no `shows.values` block — the canonical\n"
            "  `shows` enum is missing, so SPEC §3.2/§3.14 cannot be enforced. The enum lives in that\n"
            "  file and nowhere else (WP-6 owns it); restore it rather than hardcoding a copy here."
        )
        return (failures, warnings, shapes)

    for i, c in enumerate(candidates):
        if not isinstance(c, dict):
            failures.append(f"  image_candidates[{i}]: must be an object, got {type(c).__name__}.")
            continue
        ctx = c.get("context", f"entry[{i}]")

        # ── shows ──
        shows = c.get("shows")
        if shows is None:
            failures.append(
                f"  entry[{i}] ({ctx}): missing required `shows` (SPEC §3.2). What does this picture\n"
                f"    DEPICT? Closed set: {sorted(shows_enum)}. `source_type` answers where it came from;\n"
                f"    it has never answered what is in the frame, which is how key art scored full marks."
            )
        elif not isinstance(shows, str) or shows not in shows_enum:
            failures.append(
                f"  entry[{i}] ({ctx}): shows={shows!r} is not in the canonical enum {sorted(shows_enum)}\n"
                f"    (the `shows` block of references/image-source-types.json). A typo'd shape is invisible\n"
                f"    to every downstream budget — WP-4's per-band §3.8 rules and the §3.9 caption-vintage\n"
                f"    rule both key off it — so this is a hard fail, not an advisory."
            )
        else:
            shapes[shows] += 1

        # ── capture_year ──
        if "capture_year" not in c:
            failures.append(
                f"  entry[{i}] ({ctx}): missing required `capture_year` (SPEC §3.2). Use the year the\n"
                f"    PHOTOGRAPH/RENDER was made, not the year of the thing depicted (a 2019 photo of a\n"
                f"    1901 artefact is 2019). Without it the caption-vintage rule (§3.9) cannot compare the\n"
                f"    image's vintage to the band's dated claims — defect B, exactly."
            )
        else:
            cy = c["capture_year"]
            if cy is None:
                if isinstance(shows, str) and shows in CAPTURE_YEAR_NULLABLE_SHOWS:
                    warnings.append(
                        f"  entry[{i}] ({ctx}): capture_year is null on a {shows!r} — legal ONLY for a\n"
                        f"    SYNTHETIC figure (one we or the source generated, with no capture event). The\n"
                        f"    bundle carries no machine field for synthetic-ness, so this is taken on the\n"
                        f"    researcher's word: if the figure was scanned or photographed, give the year."
                    )
                else:
                    failures.append(
                        f"  entry[{i}] ({ctx}): capture_year is null but shows={shows!r}. Null is legal ONLY\n"
                        f"    when shows ∈ {list(CAPTURE_YEAR_NULLABLE_SHOWS)} and the asset is synthetic "
                        f"(SPEC §3.2).\n"
                        f"    Every photograph, render, artefact shot and document scan has a year — find it."
                    )
            elif isinstance(cy, bool) or not isinstance(cy, int):
                failures.append(
                    f"  entry[{i}] ({ctx}): capture_year={cy!r} must be an integer year "
                    f"(or null for a synthetic diagram/chart)."
                )
            elif not (CAPTURE_YEAR_FLOOR <= cy <= run_date.year):
                failures.append(
                    f"  entry[{i}] ({ctx}): capture_year={cy} is outside "
                    f"{CAPTURE_YEAR_FLOOR}–{run_date.year}. An image cannot be captured after the run date."
                )

        # ── licence ──
        lic = c.get("licence")
        if lic is None:
            failures.append(
                f"  entry[{i}] ({ctx}): missing required `licence` object (SPEC §3.2):\n"
                f"      {{\"holder\": …, \"code\": \"CC-BY-2.5\", \"url\": …, \"allows_derivatives\": true}}\n"
                f"    The free-text credit is prose no check can read. `allows_derivatives` is what lets\n"
                f"    extract-covers.py refuse to crop an ND source — Issue #18's CC BY-ND cover was\n"
                f"    smart-cropped because this field did not exist."
            )
        elif not isinstance(lic, dict):
            failures.append(f"  entry[{i}] ({ctx}): licence must be an object, got {type(lic).__name__}.")
        else:
            for key in LICENCE_REQUIRED_KEYS:
                if key not in lic:
                    failures.append(f"  entry[{i}] ({ctx}): licence is missing required key {key!r}.")
            holder = lic.get("holder")
            if "holder" in lic and not (isinstance(holder, str) and holder.strip()):
                failures.append(
                    f"  entry[{i}] ({ctx}): licence.holder={holder!r} must be a non-empty string — the\n"
                    f"    person or institution to credit."
                )
            code = lic.get("code")
            if "code" in lic and not (isinstance(code, str) and code.strip()):
                failures.append(
                    f"  entry[{i}] ({ctx}): licence.code={code!r} must be a non-empty SPDX-ish token, or one\n"
                    f"    of PRESS-KIT-EDITORIAL | PUBLIC-DOMAIN | CC0 | UNKNOWN."
                )
            elif isinstance(code, str) and code.strip().upper() == "UNKNOWN":
                warnings.append(
                    f"  entry[{i}] ({ctx}): licence.code is UNKNOWN. Legal in the bundle and a signal to the\n"
                    f"    planner NOT to build on it — it is not a licence to crop or to lead on."
                )
            lurl = lic.get("url")
            if "url" in lic and not (isinstance(lurl, str) and lurl.startswith(("http://", "https://"))):
                failures.append(
                    f"  entry[{i}] ({ctx}): licence.url={lurl!r} must be an http(s) URL to the licence deed."
                )
            ad = lic.get("allows_derivatives")
            if "allows_derivatives" in lic and not isinstance(ad, bool):
                failures.append(
                    f"  entry[{i}] ({ctx}): licence.allows_derivatives={ad!r} must be a boolean "
                    f"(false for ANY ND licence)."
                )
            elif ad is False:
                warnings.append(
                    f"  entry[{i}] ({ctx}): licence.allows_derivatives is false (an ND licence). Usable as\n"
                    f"    an in-band figure, but extract-covers.py will REFUSE to crop or resize it (§3.10) —\n"
                    f"    do not route this candidate to the cover."
                )

    # ── bundle-wide shape floor (replaces the retired Wikimedia ceilings) ──
    if candidates and len(shapes) < min_shapes:
        failures.append(
            f"  Shape diversity: {len(shapes)} distinct `shows` value(s) ({sorted(shapes)}) "
            f"< minimum of {min_shapes} (thresholds.min_distinct_shapes).\n"
            f"    This FLOOR replaced the retired wikimedia_max_pct / wikimedia_max_count CEILINGS "
            f"(SPEC §3.14):\n"
            f"    a cap on one domain read as a target to fill up to, while nothing required an image that\n"
            f"    showed the mechanism working. A bundle offering one shape forces every band to run it.\n"
            f"    Reach up the hierarchy: information figures {info_shapes} and photographs of the actual\n"
            f"    thing happening. {last_resort} are the last resort and never a lead."
        )

    return (failures, warnings, shapes)


def main():
    ap = argparse.ArgumentParser(description="Phase 3b research-bundle validator.")
    ap.add_argument("bundle_path", help="Path to research-bundle.json")
    ap.add_argument("--verify-network", action="store_true",
                    help="HEAD-check every candidate URL ourselves and OVERWRITE the researcher's "
                         "verified block with the actual result. Use in CI or anywhere network egress works. "
                         "Closes the self-attestation hole at zero subagent cost.")
    ap.add_argument("--workers", type=int, default=8,
                    help="Parallel workers for --verify-network HEAD checks.")
    ap.add_argument("--write-back", action="store_true",
                    help="When used with --verify-network, write the rewritten bundle back to disk "
                         "so subsequent phases see the orchestrator-verified URLs.")
    ap.add_argument("--run-date", default=None,
                    help="The date the pipeline is RUNNING (YYYY-MM-DD), i.e. when facts are knowable. "
                         "Defaults to today (UTC). The facts gate uses this — not the issue's cover date — "
                         "as the 'has this happened?' anchor: a fact tagged status=happened but dated AFTER "
                         "the run date cannot have occurred yet and is rejected (the State-of-Play / "
                         "'Norris on pole' temporal hole).")
    ap.add_argument("--state", default=None,
                    help="Path to state/signal-state.json (SPEC §3.7, WP-9's Phase 3b invocation). "
                         "Enables the open-loop resolution rule: a MATURED loop (status='open' and "
                         "expected_resolution_date <= run date) with no facts[] entry carrying a matching "
                         "`resolves_loop` is a hard fail, and every `resolves_loop` must name a real loop id. "
                         "Tolerant of an absent or empty open_loops[] — no loops means no obligation. "
                         "Omit the flag to skip §3.7 entirely (an advisory is printed).")
    args = ap.parse_args()

    bundle_path = Path(args.bundle_path)
    if not bundle_path.exists():
        print(f"ERROR: {bundle_path} not found", file=sys.stderr)
        sys.exit(2)

    skill_dir = Path(__file__).resolve().parent.parent
    lookup = load_lookup(skill_dir)
    thresholds = lookup["thresholds"]

    bundle = json.loads(bundle_path.read_text())
    candidates = bundle.get("image_candidates", [])

    # Resolve the run-date anchor for the facts temporal gate (F3) and the §3.7
    # loop-maturity rule.
    if args.run_date:
        run_date = parse_iso_date(args.run_date)
        if run_date is None:
            print(f"ERROR: --run-date {args.run_date!r} is not YYYY-MM-DD", file=sys.stderr)
            sys.exit(2)
    else:
        run_date = datetime.datetime.utcnow().date()

    # ── state (SPEC §3.7) ─────────────────────────────────────────────────
    # Only read when --state is passed. An explicitly-passed path that does not
    # exist or does not parse is a CONFIGURATION error (exit 2), not a bundle
    # failure: silently continuing would mean the loop rule quietly did not run.
    state = None
    if args.state:
        state_path = Path(args.state)
        if not state_path.exists():
            print(f"ERROR: --state {state_path} not found", file=sys.stderr)
            sys.exit(2)
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError as e:
            print(f"ERROR: --state {state_path} is not valid JSON: {e}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(state, dict):
            print(f"ERROR: --state {state_path} must contain a JSON object", file=sys.stderr)
            sys.exit(2)

    # Facts gate runs regardless of whether image_candidates is populated — a
    # bundle can be fact-heavy and image-light. Collected now, reported below
    # alongside the image findings under one exit code.
    fact_failures, fact_warnings = validate_facts(bundle, run_date)

    # SPEC §3.7 — matured open loops must be resolved by a fact in this bundle.
    matured_loops: list[dict] = []
    if state is not None:
        loop_failures, loop_warnings, matured_loops = validate_open_loops(bundle, state, run_date)
        fact_failures.extend(loop_failures)
        fact_warnings.extend(loop_warnings)
    else:
        print("ADVISORY: no --state given — the SPEC §3.7 open-loop resolution rule did NOT run. "
              "Phase 3b passes --state; a manual run without it does not check carried-forward results.")

    # SPEC §3.2 / §3.14 — per-candidate shows/capture_year/licence + the
    # bundle-wide min_distinct_shapes floor. Independent of the URL/verified
    # checks below: a candidate can have a perfect URL and no provenance record.
    img_failures, img_warnings, shapes = validate_image_records(candidates, lookup, run_date)

    if not candidates:
        print("ADVISORY: research-bundle.json has no image_candidates — skipping image-source validation.")

    # ── v8.13.8 orchestrator-side HEAD verification ───────────────────────
    # When --verify-network is on (always in CI; in pipeline whenever egress
    # works), HEAD-check every URL ourselves and overwrite the researcher's
    # self-attested `verified` block with the actual result. This closes the
    # hole where a researcher could fabricate verification.
    # When egress is blocked (sandbox), every candidate gets verified:
    # {"head_status": "blocked:egress"} — the bundle gate downstream knows
    # to treat these as "verify in CI" rather than reject outright.
    if args.verify_network:
        print(f"=== --verify-network: HEAD-checking {len(candidates)} candidates (parallel) ===")
        urls = [c.get("url_or_keyword", "") for c in candidates]
        results: dict[int, tuple[int | str, str]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            future_to_i = {pool.submit(head_verify, u): i for i, u in enumerate(urls) if u}
            for fut in concurrent.futures.as_completed(future_to_i):
                results[future_to_i[fut]] = fut.result()
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        for i, c in enumerate(candidates):
            if i not in results:
                continue
            status, ctype = results[i]
            c["verified"] = {
                "head_status": status,
                "content_type": ctype,
                "verified_at": now,
                "verified_by": "orchestrator",
            }
        if args.write_back:
            bundle_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
            print(f"  wrote orchestrator-verified bundle back to {bundle_path}")
        # Quick stats
        ok = sum(1 for s, ct in results.values() if isinstance(s, int) and 200 <= s < 300 and ct.startswith("image/"))
        blocked = sum(1 for s, ct in results.values() if isinstance(s, str) and s.startswith("blocked"))
        bad = len(results) - ok - blocked
        print(f"  verified: {ok} OK / {blocked} egress-blocked / {bad} bad")
        print()

    failures = list(fact_failures) + list(img_failures)
    warnings = list(fact_warnings) + list(img_warnings)

    # Per-entry validation
    valid_entries = []
    for i, c in enumerate(candidates):
        url = c.get("url_or_keyword", "")
        explicit_type = c.get("source_type")
        ctx = c.get("context", f"entry[{i}]")

        if not url:
            warnings.append(f"  entry[{i}] ({ctx}): no url_or_keyword — will be skipped by writers")
            continue

        if not url.startswith(("http://", "https://")):
            failures.append(
                f"  entry[{i}] ({ctx}): url_or_keyword is not a URL: {url!r}\n"
                f"    Researcher must supply a direct, verified URL — keywords force writers to guess. See RT-16."
            )
            continue

        # v8.13.6 — reject URLs that are not direct image assets.
        # A "page URL" (e.g. https://www.efteling.com/en/park/restaurants/polles-keuken)
        # cannot be used as <img src> or background-image: a browser fetches HTML
        # and renders nothing. Writers have been observed copying these page URLs
        # verbatim from the bundle's notes. Block them upstream.
        # Accept .jpg/.jpeg/.png/.webp/.gif/.avif extensions OR an explicit
        # `direct_cdn: true` flag (escape hatch for CDN paths without extensions,
        # e.g. signed URLs / image proxies — rare but legitimate).
        IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif",
                    ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF", ".AVIF")
        # Strip querystring before checking extension (CDNs often append ?w=1280).
        path_only = urlparse(url).path
        is_image_ext = path_only.endswith(IMG_EXTS)
        explicit_direct = bool(c.get("direct_cdn", False))
        if not is_image_ext and not explicit_direct:
            failures.append(
                f"  entry[{i}] ({ctx}): url_or_keyword has no image extension and no direct_cdn flag: {url}\n"
                f"    Researcher must supply a direct image URL (.jpg/.png/.webp/.gif/.avif) — page URLs\n"
                f"    cannot be used as <img src>. If the CDN serves images without extensions (signed URLs,\n"
                f"    image proxies), set \"direct_cdn\": true on the candidate to bypass this check."
            )
            continue

        # v8.13.7 — UNBREAKABLE RULE: every image_candidate MUST carry a
        # `verified` block proving the researcher HEAD-checked the URL and
        # got a 2xx with Content-Type starting with image/. This closes the
        # last gap that lets fabricated, dead, or wrong-content URLs reach
        # writers. A URL the researcher could not verify must be DROPPED
        # from the bundle, not shipped with a "verify later" note.
        #
        # Required schema on each candidate:
        #   "verified": {
        #     "head_status": 200,
        #     "content_type": "image/jpeg",
        #     "verified_at": "2026-05-17T08:14:22Z"
        #   }
        #
        # Researcher contract: use the WebFetch tool (or equivalent) to HEAD/GET
        # every candidate URL during Phase 3. If the URL does not return a 2xx
        # with image/* Content-Type, find a replacement or drop the candidate.
        # Do NOT speculate URLs (e.g. /wikipedia/commons/thumb/{hash}/{hash}/
        # filename.jpg/1280px-filename.jpg) — Wikimedia thumbnail paths in
        # particular only exist for pre-generated sizes. Use the canonical
        # /wikipedia/commons/{hash}/{hash}/{filename}.{ext} path instead.
        verified = c.get("verified")
        if not isinstance(verified, dict):
            failures.append(
                f"  entry[{i}] ({ctx}): missing `verified` block. URL: {url}\n"
                f"    Researcher MUST HEAD-check every URL and record:\n"
                f"      \"verified\": {{ \"head_status\": 200, \"content_type\": \"image/jpeg\", \"verified_at\": \"<ISO timestamp>\" }}\n"
                f"    Unverified URLs cannot reach writers — fabricated, dead, and wrong-content URLs\n"
                f"    have shipped repeatedly when this check was absent."
            )
            continue
        v_status = verified.get("head_status")
        v_ctype = (verified.get("content_type") or "").lower()
        # v8.13.8 — a `blocked:*` status means the orchestrator's network was
        # restricted (sandbox), so verification deferred to CI. Treat as a
        # warning, not a fail: the bundle proceeds, the CI workflow does the
        # real verification, the auto-promote step holds main on red.
        if isinstance(v_status, str) and v_status.startswith("blocked"):
            warnings.append(
                f"  entry[{i}] ({ctx}): verified.head_status = {v_status!r} (egress restricted). "
                f"CI will re-verify with full network. URL: {url}"
            )
        elif not (isinstance(v_status, int) and 200 <= v_status < 300):
            failures.append(
                f"  entry[{i}] ({ctx}): verified.head_status is {v_status!r}, must be 2xx. URL: {url}\n"
                f"    Replace this candidate with a URL that returns 2xx, or drop it from the bundle."
            )
            continue
        elif not v_ctype.startswith("image/"):
            failures.append(
                f"  entry[{i}] ({ctx}): verified.content_type is {v_ctype!r}, must start with 'image/'. URL: {url}\n"
                f"    The URL returns non-image content (likely an HTML page). Replace it with a direct CDN image URL."
            )
            continue

        stype = classify_domain(url, lookup, explicit_type)
        if stype == "ambiguous":
            failures.append(
                f"  entry[{i}] ({ctx}): {urlparse(url).netloc} requires explicit source_type field.\n"
                f"    See ambiguous_domains in image-source-types.json. URL: {url}"
            )
            continue
        if stype == "unknown":
            warnings.append(
                f"  entry[{i}] ({ctx}): domain {urlparse(url).netloc} not in lookup — classified as 'unknown'.\n"
                f"    Add to references/image-source-types.json domains map if this is a real recurring source."
            )
        # F-17 (2026-07 WP-0): Getty/Shutterstock were mislabeled press_kit.
        # 'restricted' = licensed stock — preview/watermarked URLs are not
        # cleared for publication. Warn loudly; excluded from the source-type
        # diversity count below (like unknown/ambiguous).
        if stype == "restricted":
            warnings.append(
                f"  entry[{i}] ({ctx}): RESTRICTED source {urlparse(url).netloc} (licensed stock — "
                f"Getty/Shutterstock, F-17). Not a press kit; find a cleared replacement. "
                f"Excluded from source-type diversity counting. URL: {url}"
            )

        valid_entries.append((url, stype, ctx))

    # Aggregate validation
    if valid_entries:
        domains = Counter(urlparse(u).netloc for u, _, _ in valid_entries)
        types = Counter(t for _, t, _ in valid_entries
                        if t not in ("unknown", "ambiguous", "restricted"))  # F-17: restricted never counts
        total = len(valid_entries)

        # Rule 1: single-domain cap (RT-5 hard)
        for d, n in domains.items():
            pct = 100 * n / total
            if pct > thresholds["single_domain_max_pct"]:
                failures.append(
                    f"  RT-5 hard fail: {d} provides {n}/{total} images ({pct:.1f}%). "
                    f"Cap is {thresholds['single_domain_max_pct']}%."
                )

        # Rule 2: RETIRED 2026-07-26 (SPEC §3.14, WP-6). The Wikimedia ceilings
        # (`wikimedia_max_pct: 30` / `wikimedia_max_count: 4`) are gone from
        # `thresholds` and recorded in `retired_thresholds` in the lookup file.
        # Reading them here unguarded is what broke this gate with
        # `KeyError: 'wikimedia_max_count'`; DO NOT reinstate either read.
        #
        # Why they went: a ceiling with no matching floor reads as a target —
        # "four Wikimedia images allowed" — so Commons became the thing to fill up
        # to, while nothing at all required an image that showed the mechanism
        # working. The Antikythera Long Read used three Wikimedia images including a
        # 2007 perspex model to illustrate a 2021 result, and passed. Commons is
        # right when it holds the most INFORMATIVE image and wrong when it holds the
        # most CONVENIENT one, and a domain count cannot tell those apart.
        #
        # The replacement is a FLOOR on shapes, enforced over
        # `image_candidates[].shows` in validate_image_records() above
        # (thresholds.min_distinct_shapes), with the enum read from the lookup file
        # exactly as check-image-diversity.sh reads it. Wikimedia entries are still
        # bound by Rule 1 (the RT-5 single-domain cap) like every other domain.

        # Rule 3: minimum distinct source types
        if len(types) < thresholds["min_distinct_source_types"]:
            failures.append(
                f"  Source-type diversity: {len(types)} types represented ({sorted(types)}) "
                f"< minimum of {thresholds['min_distinct_source_types']}.\n"
                f"    The shippable menu: {sorted(t for t in lookup['types'] if t != 'restricted')} "
                f"('restricted' is quarantined stock and never counts, F-17)."
            )

        # Rule 4 (v8.13.7): unique-URL minimum. The researcher MUST surface
        # enough distinct candidates that writers can fill every chapter slot
        # without reuse. Issues have consistently shipped with the same image
        # repeated 2–3 times across the DOM because writers ran out of
        # bundle candidates. Enforce a minimum unique-URL count tied to the
        # bundle's stated need.
        unique_urls = {u for u, _, _ in valid_entries}
        min_unique = thresholds.get("min_unique_candidates", 16)
        if len(unique_urls) < min_unique:
            failures.append(
                f"  Unique-URL minimum: {len(unique_urls)} < required {min_unique}.\n"
                f"    Writers will be forced to reuse images. The researcher must surface MORE\n"
                f"    distinct candidates (target {min_unique}+) before the planner can spawn.\n"
                f"    Adjust thresholds.min_unique_candidates in image-source-types.json if a\n"
                f"    smaller issue legitimately needs fewer images."
            )

    # Report
    print("=== Phase 3b: validate-research-bundle.py "
          "(upstream production aid — NOT one of the three ship gates) ===")
    print(f"run-date (facts/loops anchor):  {run_date}")
    print(f"facts entries:                  {len(bundle.get('facts', []))}")
    print(f"image_candidates entries:       {len(candidates)}")
    print(f"valid URL entries:              {len(valid_entries)}")
    if valid_entries:
        types_repr = Counter(t for _, t, _ in valid_entries)
        print(f"by source type:                 {dict(types_repr)}")
    min_shapes = thresholds.get("min_distinct_shapes", 3)
    print(f"by shape (what they SHOW):      {dict(shapes)}")
    print(f"distinct shapes:                {len(shapes)} (floor {min_shapes})")
    if state is None:
        print("open loops (§3.7):              not checked (no --state)")
    else:
        loops_all = state.get("open_loops")
        n_loops = len(loops_all) if isinstance(loops_all, list) else 0
        print(f"open loops in state:            {n_loops} "
              f"({len(matured_loops)} matured on or before {run_date})")
        if matured_loops:
            print(f"matured loop ids:               "
                  f"{[l.get('id') for l in matured_loops if isinstance(l, dict)]}")
    print()

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(w)
        print()

    if failures:
        print("FAIL — rule violations:")
        for f in failures:
            print(f)
        print()
        print("PRODUCTION HALT, not a ship failure: nothing has been written or published. This is an")
        print("upstream production aid (SPEC §1) — the three ship gates are validate-issue.py's image")
        print("checks, its markup contracts, and the Phase 9.5 holistic read.")
        print("Re-spawn the researcher with this report so the bundle can be corrected before Phase 4 (planner).")
        sys.exit(1)

    print("PASS — research bundle complies with image-integrity, image-provenance (shows/capture_year/")
    print("licence), fact-provenance and open-loop-resolution rules.")
    sys.exit(0)


if __name__ == "__main__":
    main()
