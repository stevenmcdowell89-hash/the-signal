# WP-4 — Rendered-issue checks

**Status: DONE.** Acceptance criteria **#2, #3, #6, #7, #8** implemented in
`.claude/skills/the-signal/scripts/validate-issue.py`, each shown firing on a known-bad input and
passing on a known-good one with real command output below. **Issue #18 now fails the gate** (exit 1,
5 failures) where it passed before — and two of the three predictions in the PROGRESS
expected-failure ledger needed **correcting, not confirming**: see § Issue #18 vs the predictions.

**One consequence to act on:** `verify-weekly-golden.sh` now **exits 1**. Both goldens fail the same
three image checks, because their writer-authored `chapters/*.html` predate the SPEC §3.4 provenance
contract. That is the check working, not a bug — but the golden fixture needs content changes I do not
own. See § Handoff notes 1.

---

## Files touched

| File | Owner | Change |
|---|---|---|
| `.claude/skills/the-signal/scripts/validate-issue.py` | **WP-4 (exclusive)** | +1,202 / −0 |

```
$ git diff --stat eb58747 -- .claude/skills/the-signal/scripts/validate-issue.py
 .../skills/the-signal/scripts/validate-issue.py | 1202 ++++++++++++++++++++++++
 1 file changed, 1202 insertions(+)

$ git status --short
 M .claude/skills/the-signal/scripts/validate-issue.py      <- mine
?? docs/editorial-coverage-rebuild-EVIDENCE/WP-4.md         <- this file
```

(An earlier run of the same command also listed `SKILL.md` and `WP-9.md` — WP-9's concurrent work,
never touched here; the orchestrator has since committed them.)

Nothing else. `issues/signal_weekly_2026-07-26.html` (#18) untouched, per SPEC §1.3. No file owned by
another WP was edited, and no new script was added — every check lands **inside** the two existing
mechanical gates (gate 1 = image checks, gate 2 = markup contracts), per SPEC §0.

**Baseline note.** I diffed against **`eb58747`**, not `fd32ba6` as the coordinator's mid-task message
asked, and not `git stash`. Reason, verifiable: `fd32ba6` is *downstream* of the WIP snapshot
`23672a7` ("WP-4 … in flight"), so it already contains 1,140 lines of my own half-finished work —
`git diff --stat eb58747 fd32ba6 -- <my file>` is `+1140`. Diffing against it would have understated
this WP by 95% and hidden any regression I introduced early. `eb58747` is the last commit before
WP-4 touched the file (`git log --oneline -- <my file>` confirms the only later commits are my own WIP
snapshots). This is the same trap WP-3 recorded for `git stash`, one commit further along.

---

## What the checks are

Seventeen new report lines (plus three sub-warnings: `figure-provenance/licence-unknown`,
`resolved-loops/unknown-id`, and the `coverage-rebuild` scope notice), all inside the existing two
gates. Scope rules are in `run_coverage_checks()`; every check name is new, so no pre-existing check
could change meaning.

| Check | SPEC | Gate | Verdict |
|---|---|---|---|
| `caption-vintage` | §3.9 | 1 | FAIL |
| `figure-provenance` / `figure-provenance/values` | §3.4, §3.4a n3+n6 | 1 | FAIL (+ WARN on `data-licence="UNKNOWN"`) |
| `image-shapes/distinct` | §3.8, §3.14 | 1 | FAIL |
| `image-shapes/pixel-byte-key-art` | §3.8 | 1 | FAIL |
| `image-shapes/never-lead` | §3.8 (resolved 2026-07-26) | 1 | FAIL |
| `image-shapes/never-lead-conditional` | §3.8 (`product_shot`) | 1 | WARN — see § What I could not check |
| `image-shapes/long-read-information` | §3.8 | 1 | FAIL |
| `image-shapes/touchline-result` | §3.8 | 1 | FAIL |
| `image-shapes/cross-issue-lead` | §3.8 | 1 | FAIL |
| `long-read-vintage` | §3.4 + §3.4a | 2 | FAIL |
| `lr-framing` | §3.4 | 2 | FAIL (evergreen only) |
| `cover-leads-on` | §3.4a n1 | 2 | FAIL |
| `table-kind` | §3.4 | 2 | FAIL on an illegal value; WARN on absence |
| `sport-tokens` | §3.11 | 2 | FAIL on `multi_sport` |
| `sport-tokens/vocabulary` | §3.11 | 2 | **WARN, and `--strict` cannot promote it** |
| `results-ledger-multi-sport` | §3.11 | 2 | FAIL |
| `resolved-loops` | §3.7 | 2 | FAIL (+ WARN on an unknown loop id) |

Two new flags, both auto-resolving so the gate keeps working for callers I cannot edit
(`stitch-issue.sh` / `publish-gate.sh` are WP-9's and pass neither):

- `--state PATH` — read-only; §3.4a note 7's requirement. Auto-discovered from the repo root, which is
  located **from the script's own path**, not the HTML's, so state is still found when the issue under
  test is a stitch in a temp directory (which is exactly how `verify-weekly-golden.sh` invokes the gate).
- `--run-date YYYY-MM-DD` — decides loop maturity (§3.7) and which calendar events concluded in-window
  (§3.11). Falls back to a date in the filename, then today (UTC). The resolved value **and its
  provenance** are printed, so a defaulted date is never silent:

```
  ── coverage-rebuild inputs (SPEC 2026-07-26) ──
     state:     /home/user/the-signal/state/signal-state.json OK
     manifest:  /home/user/the-signal/assets/cached/manifest.json OK (438 entries)
     run-date:  2026-07-26  (parsed from the filename (signal_weekly_2026-07-26.html))
     window:    (2026-07-26, 2026-07-26]  from state.research_cut_at
     issue no:  18  (masthead FOLIO)
     figures:   11 .plate-img
```

### Three implementation decisions worth recording

**1. Everything is scanned on `body_text_only()`, not the raw document.** Not cosmetic: the inlined
`<style>` bundle contains `.mx-scorecard[data-table-kind="…"]` and `.lr-title .lr-vintage{`. A
whole-document scan reads CSS selectors as rendered markup — `data-table-kind="…"` (a literal
ellipsis) would have been reported as an illegal sixth table kind on **every** issue, and the golden's
news-vintage Long Read would have "had" a `.lr-vintage` line. Verified: the four `lr-vintage`
occurrences in `weekly-mx/expected.html` are all CSS.

**2. Band prose excludes dateline furniture.** §3.9's `claim_max` is the largest year in the band's
**prose**. The Long Read's byline reads `· 26 JUL 2026`, so counting furniture as a claim sets
`claim_max` to the issue year in every band of every issue — turning "the band claims 2021" into "the
issue was published in 2026" and making the failure message undiagnostic. `.byline`, `.sigline`,
`.dataline`, `.stamp`, `.lr-vintage`, `.colophon` and `.runtime` are stripped before measuring.
Ledger **date cells** are deliberately *not* stripped: `1901 Recovered / 2005 Scanned / 2021 Modelled`
are claims of record, which is precisely what the rule reads. With this in place #18's Long Read
measures `claim_max = 2021`, matching the SPEC's worked example exactly.

**3. Nothing new is named `data-station*`.** Every attribute this WP matches is one WP-3 already emits
(`data-vintage`, `data-cover-leads-on`, `data-nav-band`, `data-shows`, `data-capture-year`,
`data-licence`, `data-allows-derivatives`, `data-lr-framing`, `data-sport`, `data-table-kind`,
`data-resolves-loop`). I introduced **zero** new attribute names, so the `\bdata-station\b` navigator
tally cannot be perturbed. Confirmed by the archive sweep below: `weekly-structure/nav-count` reports
the same value on every issue before and after.

### Scope: which issues the structure contracts apply to

`caption-vintage` and `sport-tokens` run on **every format** — both are self-gating (inert unless a
figure declares a capture year / something declares `data-sport`), and a dated figure lying about its
vintage is defect B wherever it is printed.

The weekly-structure contracts (§3.4, §3.7, §3.8, §3.11) run on a **weekly that is either new-system
(`data-mx`) or carries any post-rebuild attribute**. The first clause is the exemption the
Law-3/Law-9/F-16 checks already give the old-system archive. The second clause closes a hole I found
while scoping: **the mx layer is opt-in** (`stitch_weekly.py:541` writes `data-mx` only when
`mx=True`), and `verify-weekly-golden.sh` exercises the legacy non-mx path — so `new_system` alone
would have let a real, current, non-mx weekly stitch escape every contract silently. Keying on the
presence of *any* rebuild-era attribute is not circular: one attribute anywhere puts the issue in
scope for **all** of them, so an issue cannot dodge `cover-leads-on` by omitting
`data-cover-leads-on`. Verified both ways — the legacy golden stitch (no `data-mx`) is in scope and
is checked (it carries `data-nav-band`), and #16/#17 (`2026-07-13`, `2026-07-19`), which carry no
rebuild-era attribute, stay exempt and their verdicts are unchanged.

### Folding in the coordinator's two mid-task contract updates

**(1) The never-lead resolution is implemented as decided, and the part that cannot be decided
mechanically is reported, not approximated.**

- `key_art` and `portrait` leading **any** band, in any position: **hard FAIL**
  (`image-shapes/never-lead`). Evidence: `shapes-portrait-lead`, `shapes-keyart-lead-nonpb` (a
  key_art lead in *The Letter*, i.e. outside Pixel & Byte) both fail.
- `product_shot` leading: **WARN** (`image-shapes/never-lead-conditional`). The condition is "the
  band's subject IS the product", and **that fact is not in the rendered HTML.** A band carries no
  machine-readable subject type: `data-band="pixel_byte"` covers hardware, software, games and
  services alike, and inferring "this is a hardware review" from prose would be a guess. Per the
  SPEC's own reasoning — a check that guesses wrong on hardware coverage is worse than one that only
  enforces the unambiguous shapes — it is surfaced with the band and figure named, for the gate-3
  human read, and it does not block a ship. Evidence: `shapes-productshot-lead` → exit **0** with the
  warning printed.
- §3.8's original Pixel & Byte rule is kept **as well** (`at most one key_art in the band`), because
  the issue-wide never-lead rule does not subsume the *count*.

**(2) The shape lists are read from `image-source-types.json` at runtime, not hardcoded.**
`load_shows_vocab()` reads `shows.values` (the enum), `information_figure_shapes` and
`never_lead_shapes` from WP-6's file every run; the SPEC literals survive only as a fallback so there
is no hard dependency on another WP's file. The hard/conditional split is expressed as *the exception*
(`CONDITIONAL_LEAD_SHAPES = ("product_shot",)`) rather than as a copy of the ban list, so if WP-6 adds
a shape to `never_lead_shapes` it propagates as a hard fail — the plain reading of "never lead" —
instead of quietly needing a code change here. Proof the file is actually being read (note the list
printed in the output is `['key_art', 'portrait']` = `never_lead_shapes` minus the exception, and
`portrait` is the value WP-6's reconciliation *added*):

```
$ python3 .../validate-issue.py .../fx/pass.html --format weekly --skip-image-urls
[PASS] figure-provenance: all 11 .plate-img figure(s) carry the four-attribute provenance record
       (shows vocab from image-source-types.json: 11 values,
        information=['diagram', 'map', 'chart', 'artefact'],
        never_lead=['key_art', 'product_shot', 'portrait'])
[PASS] image-shapes/never-lead: none of the 4 declared lead figure(s) use a never-lead shape
       ['key_art', 'portrait']
```

The 22 sport tokens are read the same way, **parsed out of
`references/spec/data-contracts.md` § The closed sport-token list**, because WP-1's contract says
adding a token is "a one-line change to this list … and no consumer needs a code change" — which is
only true if the consumer reads the list. Output confirms: `(22 sport tokens from data-contracts.md)`.

---

## Verification

`python3 -m py_compile` and the fixture matrix. **Fixtures live in the scratchpad, not the repo**
(`references/fixtures/coverage-rebuild/**` is WP-10's). `build_fixtures.py` derives 28 HTML fixtures
and 4 state fixtures from frozen #18 by single-point mutation, so every fixture differs from a
*shipped* issue in exactly one respect. `pass.html` is #18 **plus the contract markup it predates** —
that is the "corrected fixture" of criteria #3 and #8, and it passes clean:

```
$ python3 .../validate-issue.py $S/fx/pass.html --format weekly --skip-image-urls --run-date 2026-07-26
[PASS] caption-vintage: 10 figure(s) with a dated capture year, all consistent with their band's claims:
       COVER [the_letter/lead, /assets/cached/af9fc905ced8.jpg] — capture 2026, band makes no dated claim;
       FIG. 01 [long_read/lead, …bf64e308503b.png] — capture 2019 < claim 2021, and the visible caption says so;
       FIG. 02 [long_read, …5a78b1b6198a.png] — capture 2019 < claim 2021, and the visible caption says so;
       FIG. 03 [long_read, …fb560e553feb.jpg] — capture 2007 < claim 2021, and the visible caption says so (+6 more)
[PASS] figure-provenance: all 11 .plate-img figure(s) carry the four-attribute provenance record
[PASS] image-shapes/distinct: 7 distinct data-shows value(s) (floor 3): ['artefact', 'chart', 'document',
       'event_photo', 'gameplay', 'key_art', 'product_shot']
[PASS] image-shapes/pixel-byte-key-art: Pixel & Byte: 1 key_art figure(s), none leading (4 figure(s) in the band)
[PASS] image-shapes/never-lead: none of the 4 declared lead figure(s) use a never-lead shape ['key_art', 'portrait']
[PASS] image-shapes/long-read-information: the Long Read carries 3 information figure(s): FIG. 01=artefact,
       FIG. 02=artefact, FIG. 03=artefact
[PASS] image-shapes/cross-issue-lead: none of the 4 lead figure(s) led issue #17 (1 asset(s) recorded as leading #17)
[PASS] table-kind: 2 data-table-kind value(s), all legal: ['championship', 'league']
[PASS] long-read-vintage: data-vintage="news" with a matching rendering (.lr-vintage absent, byline dated)
[PASS] cover-leads-on: cover declares data-cover-leads-on="news"
[PASS] results-ledger-multi-sport: not applicable — 0 tracked sport(s) concluded in the window
       (2026-07-26, 2026-07-26]: []; the invariant needs ≥2
[PASS] resolved-loops: no matured open loop as of 2026-07-26 (2 loop(s) in state; a 'dropped' or
       'resolved' loop does not mature) — 0 data-resolves-loop attribute(s) rendered
1 warning(s). PASS.                                    # the warning is image-urls: skipped
exit=0
```

### Criterion #2 — an evergreen anchor renders `.lr-vintage` + a date-free byline; a news anchor neither

Six firing cases and one passing case. Real output (each line is the run's only new failure):

```
### vintage-evergreen-ok                    (exit=0)
    [PASS] long-read-vintage: data-vintage="evergreen" with a matching rendering (.lr-vintage present,
           byline date-free)
    [PASS] lr-framing: data-lr-framing="feature" present in The Letter band (evergreen anchor)

### vintage-missing                         (exit=1)
    [FAIL] long-read-vintage: the Long Read section carries no data-vintage attribute. SPEC §3.4:
           data-vintage is ALWAYS present, 'news' or 'evergreen'. …
### vintage-bad-enum                        (exit=1)
    [FAIL] long-read-vintage: data-vintage="ancient" is not one of ['news', 'evergreen'] (SPEC §3.4)
### vintage-news-with-lrvintage             (exit=1)
    [FAIL] long-read-vintage: data-vintage="news" but the rendering disagrees: .lr-vintage line present
           on a NEWS anchor (SPEC §3.4: absent when news). Byline reads: 'BY THE EDITOR · THE LONG READ · 26 JUL 2026'
### vintage-evergreen-dated-byline          (exit=1)
    [FAIL] long-read-vintage: data-vintage="evergreen" but the rendering disagrees: the .byline carries
           an issue date ('26 JUL 2026') — an evergreen anchor's byline must NOT be dated, or the
           standing story is stamped as news. …
### vintage-evergreen-no-lrvintage          (exit=1)
    [FAIL] long-read-vintage: data-vintage="evergreen" but the rendering disagrees: no .lr-vintage line
           in .lr-title (SPEC §3.4: present when evergreen). Byline reads: 'BY THE EDITOR · THE LONG READ · A STANDING STORY'
### vintage-evergreen-no-framing            (exit=1)
    [FAIL] lr-framing: the Long Read is evergreen but no data-lr-framing="feature" paragraph is in
           The Letter band (SPEC §3.4). …
```

The byline-date matcher tolerates zero-padding and month-name length (`5 July 2026` == `05 JUL 2026`)
and also matches ISO dates, so it cannot be defeated by reformatting the date WP-3 normalises.

`cover-leads-on` (§3.4a note 1) fires on #18 (below) and passes on both goldens.

### Criterion #3 — caption vintage: #18's FIG 03 defect

Firing case is **#18's own shipped caption wording**, with only the capture year added:

```
### capvintage-fire                         (exit=1)
    [FAIL] caption-vintage: 1 of 10 dated figure(s) illustrate a later claim without saying so (SPEC §3.9):
    • FIG. 03 [long_read, /assets/cached/fb560e553feb.jpg]
        capture year 2007 is OLDER than the band's latest claim 2021, and "2007" does not appear in
        the caption's visible sentence.
        .plate-cap .txt (credit excluded) reads: 'A working modern reconstruction of the front dial —
        the pointers that tracked the Sun, Moon and planets, turned by a single crank.'
```

`claim_max = 2021`, the `.credit` span's "Reconstruction by Mogi Vicentini, 2007" is correctly **not**
counted (the credit is a *child* of `.txt` in the shipped markup, so excluding it means removing a
nested element, not skipping a sibling), and the SPEC's suggested rewrite passes — that is the FIG 03
line in `pass.html` above. Two boundary cases from §3.4a note 3:

```
### capvintage-null-year                    (exit=0)   # data-capture-year="" is the LEGAL null
### capvintage-bad-year                     (exit=1)
    [FAIL] figure-provenance/values: 1 invalid provenance value(s) …
    • FIG. 03 […] — data-capture-year="c. 2007" is neither empty nor a 4-digit year in 1500–2100
```

### Criterion #6 — a matured open loop absent from the rendered HTML

The two seeded loops are `dropped`, so per WP-1's note they never mature; the fixture state carries
one `open` loop due 2026-07-19 and one `open` loop due 2026-08-30 (not yet matured).

```
### pass.html + state-matured-loop, --run-date 2026-07-26            (exit=1)
    [FAIL] resolved-loops: 1 of 1 matured open loop(s) have no data-resolves-loop in the rendered HTML
           (run-date 2026-07-26, SPEC §3.7):
    • loop_2026-07-19_fixture-final — due 2026-07-19, band 'touchline', opened in issue 17:
      Fixture Cup final, concluding Sunday 19 July 2026
    A carried-forward result must be reported and marked with data-resolves-loop="<id>", or the loop
    silently vanishes (defect D).

### loop-resolved + state-matured-loop, --run-date 2026-07-26        (exit=0)   # the ledger row carries the id
### pass.html    + state-matured-loop, --run-date 2026-07-18         (exit=0)   # not yet matured — maturity is real, not decorative
```

The second `open` loop (due 2026-08-30) is correctly never counted at either run-date, and the
"1 of 1" wording proves only the matured one was considered.

### Criterion #7 — sport tokens and results-ledger breadth

```
### ledger-multi-sport-token                (exit=1)
    [FAIL] sport-tokens: data-sport="multi_sport" on 1 row(s) — FORBIDDEN in rendered HTML (SPEC §3.11;
           legal only in state.sports_calendar[].sport, where it classifies an EVENT). …
### ledger-unknown-token                    (exit=0)
    [WARN] sport-tokens/vocabulary: data-sport token(s) outside the closed list: ['lawn_bowls'].
           Not a failure — …a check that blocks a genuinely new sport would block the breadth it
           exists to force.
### ledger-unknown-token --strict           (exit=1, but NOT because of the token)
    [WARN] sport-tokens/vocabulary: … outside the closed list: ['lawn_bowls'].
    [FAIL] image-urls: skipped per --skip-image-urls          <- the only failure; pre-existing --strict behaviour
    1 failure(s)
```

The `--strict` run is the point: I added `Report.soft_warn()` for exactly this one finding, because
plain `warn()` is promoted to a failure by `--strict` and the SPEC says this must **never** fail. The
token warning stayed a warning while the pre-existing skip-warning was promoted, which shows both that
`--strict` still works and that this one finding is exempt.

`results_ledger_multi_sport` (needs `--state`, §3.4a note 7 — the window is
`(state.research_cut_at, run_date]`):

```
### ledger-one-sport  + state-two-sports  --run-date 2026-07-20     (exit=1)
     window:    (2026-07-12, 2026-07-20]  from state.research_cut_at
    [FAIL] results-ledger-multi-sport: ≥2 tracked sports concluded in the window (2026-07-12,
           2026-07-20]: ['football', 'golf'], but the results ledger carries 1 distinct data-sport
           value(s) (['motorsport']). SPEC §3.11 invariant results_ledger_multi_sport requires ≥2. …

### ledger-two-sports + state-two-sports  --run-date 2026-07-20     (exit=0)
    [PASS] results-ledger-multi-sport: 2 distinct sport token(s) in the results ledger
           (['golf', 'motorsport']) — ≥2 tracked sports concluded in the window …: ['football', 'golf']

### ledger-one-sport  + state-golf-off    --run-date 2026-07-20     (exit=0)
    [PASS] results-ledger-multi-sport: not applicable — 1 tracked sport(s) concluded in the window
           (2026-07-12, 2026-07-20]: ['football']; the invariant needs ≥2
```

Three further properties, each verified rather than assumed:

```
# An ABSENT interest_depth key is UNSET, never "off" (WP-1's correction). cricket and
# athletics have no key at all, and both still count as tracked:
### ledger-one-sport + state-unset-sports --run-date 2026-07-20     (exit=1)
    [FAIL] results-ledger-multi-sport: ≥2 tracked sports concluded in the window (2026-07-12,
           2026-07-20]: ['athletics', 'cricket'], but the results ledger carries 1 …

# A multi-sport games that concluded in-window counts as ">=2 sports concluded" — that is what a
# games IS, and its results are required to be tagged per sport. REAL seeded state, no fixture:
### ledger-one-sport + REAL state --run-date 2026-08-03             (exit=1)
    [FAIL] results-ledger-multi-sport: ≥2 tracked sports concluded in the window (2026-07-26,
           2026-08-03]: [] plus multi-sport event(s) ['Commonwealth Games (Glasgow 2026)'], but the
           results ledger carries 1 distinct data-sport value(s) (['motorsport']). …

# No results ledger AT ALL is worse, not exempt:
### pass.html (no ledger) + REAL state --run-date 2026-08-03        (exit=1)
    [FAIL] results-ledger-multi-sport: … but the issue (NO results ledger element) carries 0 distinct
           data-sport value(s) ([]). …
```

### Criterion #8 — image shape budgets

```
### shapes-two-distinct-shapes              (exit=1)
    [FAIL] image-shapes/distinct: 2 distinct data-shows value(s) across 11 figure(s) (['event_photo',
           'portrait']); the floor is 3 (SPEC §3.8 / §3.14 min_distinct_shapes). …
### shapes-keyart-leads-pb                  (exit=1)
    [FAIL] image-shapes/pixel-byte-key-art: 2 key_art figures (cap is 1): FIG. [pixel_byte/lead,
           …8ff67aa0126f.jpg]; FIG. [pixel_byte, …1a2d67f3ca02.jpg]; key_art is the band's LEAD figure
           (.plate-img.lead): FIG. [pixel_byte/lead, …8ff67aa0126f.jpg]. …
    [FAIL] image-shapes/never-lead: 1 band lead figure(s) use a never-lead shape ['key_art', 'portrait'] …
### shapes-two-keyart-pb                    (exit=1)   # two key_art, neither leading -> the COUNT rule alone
    [FAIL] image-shapes/pixel-byte-key-art: 2 key_art figures (cap is 1) …
### shapes-portrait-lead                    (exit=1)   # a portrait leading The Touchline
    [FAIL] image-shapes/never-lead: 1 band lead figure(s) use a never-lead shape ['key_art', 'portrait'] …
### shapes-keyart-lead-nonpb                (exit=1)   # key_art leading The LETTER — issue-wide, not just P&B
    [FAIL] image-shapes/never-lead: …
### shapes-productshot-lead                 (exit=0)   # conditional: reported, not failed
    [WARN] image-shapes/never-lead-conditional: 1 band lead figure(s) are ['product_shot'] …
### shapes-lr-no-information-figure         (exit=1)
    [FAIL] image-shapes/long-read-information: the Long Read's 3 figure(s) include none of ['diagram',
           'map', 'chart', 'artefact'] (SPEC §3.8). Declared: portrait. …
### shapes-touchline-result-keyart          (exit=1)
    [FAIL] image-shapes/touchline-result: 1 Touchline figure(s) report a concluded result but are not
           event_photo (SPEC §3.8):
    • FIG. [touchline/lead, …2601e4c02103.webp] — data-shows="key_art", caption reports a decided
      result ('won')
    A result that happened has a photograph of it happening.
### shapes-touchline-result-ok              (exit=0)   # same caption, data-shows="event_photo"
### shapes-repeat-lead                      (exit=1)
    [FAIL] image-shapes/cross-issue-lead: 1 figure(s) led issue #17 and lead issue #18 again (SPEC §3.8):
    • COVER [the_letter/lead, /assets/cached/c0fbc060b733.jpg]
```

The cross-issue case uses a **real** manifest fact, not a fixture: `c0fbc060b733` is recorded in
`assets/cached/manifest.json` as `led: [17]`, and the fixture is numbered 18 by its own masthead
`FOLIO`, so the check reads live data end-to-end. (Two of the mutations above also trip
`never-lead` as a side-effect, because replacing an `artefact` lead with `portrait` is itself a
never-lead violation — the extra failure is correct, not a false positive.)

### No pre-existing check changed verdict — full archive sweep

Every issue in `issues/` plus the mx golden, run under the `eb58747` script and mine, comparing the
`[PASS]/[WARN]/[FAIL]` verdict of every check by name. A `REGRESSION:` column would list any
pre-existing check whose verdict changed. Only rows that changed at all are printed:

```
$ for f in issues/*.html .../golden/weekly-mx/expected.html; do  <BASE vs NEW verdict diff>  done
FILE                                     BASE   NEW    new failures / regressions
signal_weekly_2026-07-26.html            0      1      figure-provenance image-shapes/distinct
                                                       image-shapes/long-read-information
                                                       long-read-vintage cover-leads-on
expected.html                            0      1      figure-provenance image-shapes/distinct
                                                       image-shapes/long-read-information
(only rows with a change are printed)
```

**34 files swept; 32 unchanged, 0 regressions.** The 13 pre-#16 weeklies and every special keep their
existing verdicts and exit codes (most already exit 1 for reasons that predate this WP). #16 and #17
still exit 0: they carry no rebuild-era attribute, so they take the archive exemption and report
`[WARN] coverage-rebuild: pre-rebuild weekly …`. **A check that failed every historical issue would
be suspicious; these two fail exactly the two artifacts that are in scope**, which is the intended
blast radius.

---

## Issue #18 vs the predicted failures

`$ python3 .../validate-issue.py issues/signal_weekly_2026-07-26.html --format weekly --skip-image-urls`
→ **exit 1, 5 failures, 3 warnings** (was exit 0).

| PROGRESS prediction | Fired? | Real result |
|---|---|---|
| caption-vintage FAILs at FIG 03 (`capture_year` 2007 vs band's 2021) | **No — prediction corrected** | `[WARN] caption-vintage: no .plate-img carries a non-empty 4-digit data-capture-year, so SPEC §3.9 has nothing to compare.` |
| shape budget FAILs (P&B leads on `key_art`; Long Read has no diagram/map/chart/artefact) | **Partly — 2 of 5 budgets fire; the key_art clause does not** | `[FAIL] image-shapes/distinct: 0 distinct data-shows value(s) across 11 figure(s)`; `[FAIL] image-shapes/long-read-information: the Long Read's 3 figure(s) include none of ['diagram','map','chart','artefact']. Declared: (no data-shows)` |
| long-read vintage FAILs (no `data-vintage`) | **Yes, exactly as predicted** | `[FAIL] long-read-vintage: the Long Read section carries no data-vintage attribute.` |

**Why two predictions were wrong, and why that is not a bug in my checks.** The ledger was written
against §3.9/§3.8 as if #18 declared its figure shapes. **It does not: #18 carries no
`data-shows`, `data-capture-year`, `data-licence` or `data-allows-derivatives` on any of its 11
figures** — it was stitched before WP-3 existed, and §3.4a note 6 explains that even today WP-3 would
stamp nothing, because all 438 manifest entries are `UNKNOWN` back-fills. So:

- **caption-vintage cannot fire on #18**, because the attribute the rule reads is absent, and §3.4a
  note 3 fixes the rule's domain as "a non-empty 4-digit value". Making it fire on an *absent*
  attribute would be a second, weaker provenance check wearing §3.9's name — and it would report
  "the caption doesn't state a year" when the truth is "nobody recorded the year". The defect is
  caught, in the right place and with the right message: `[FAIL] figure-provenance` names FIG 03
  (`…fb560e553feb.jpg`) among 11 of 11 figures short of the record, and the caption-vintage WARN says
  in terms that this is **not** a pass. The rule itself is proven on `capvintage-fire`, which is #18's
  FIG 03 markup and #18's own caption wording with only the capture year added — the exact defect the
  owner spotted, failing.
- **the key_art clause likewise cannot fire**, for the same reason: no figure says it is key art.
  The shape budget still **FAILs on #18** as criterion #8 requires, via the two clauses that are
  counted over *what the issue declares* — 0 distinct shapes against a floor of 3, and no information
  figure in the Long Read. I deliberately did **not** weaken those two to "skip when undeclared":
  the budget is a per-issue floor on what the reader is shown, and "we didn't say what the pictures
  are" is not a way to satisfy it.

**Two failures nobody predicted:**

- `[FAIL] cover-leads-on: <header class="cover"> carries no data-cover-leads-on attribute` — correct;
  §3.4a note 1's attribute post-dates #18.
- `[FAIL] figure-provenance` (11 of 11) — the §3.4a note 6 check that only WP-4 can make bite.

Plus `[WARN] table-kind: 2 .mx-scorecard element(s) carry no data-table-kind`. #18 is **not
repaired**; these are recorded, per SPEC §1.3.

**Suggested ledger correction (PROGRESS is not mine to edit):** rows 1 and 2 should read
*"caption-vintage: WARN — inert on #18, because #18 declares no `data-capture-year`; proven on the
FIG-03-derived fixture"* and *"shape budget: FAIL via distinct-shapes (0/3) and the Long Read's
missing information figure; the key_art clause is inert for the same reason"*, with a new row for
`figure-provenance` (11 of 11) and `cover-leads-on`.

---

## The goldens

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh > golden.txt 2>&1 ; echo "REAL EXIT=$?"
REAL EXIT=1
   30 × [PASS]
[FAIL] figure-provenance: 7 of 7 .plate-img figure(s) are short of the SPEC §3.4 provenance record …
[FAIL] image-shapes/distinct: 0 distinct data-shows value(s) across 7 figure(s) ([]); the floor is 3 …
[FAIL] image-shapes/long-read-information: the Long Read's 2 figure(s) include none of […] …
```

(Captured to a file and `$?` read directly — per WP-3's trap note, `| tail` would have reported 0.)

```
$ python3 .../validate-issue.py .../golden/weekly-mx/expected.html --format weekly --skip-image-urls
exit=1
[FAIL] figure-provenance: 14 of 14 .plate-img figure(s) are short of the SPEC §3.4 provenance record …
[FAIL] image-shapes/distinct: 0 distinct data-shows value(s) across 14 figure(s) ([]) …
[FAIL] image-shapes/long-read-information: the Long Read's 2 figure(s) include none of […] …
```

**The regenerated golden no longer passes, and I did not soften a check to make it.** Both golden
paths — legacy (7 figures) and mx (14) — fail the *same three* image checks and nothing else. Two
things are worth reading out of that:

1. **WP-3's vintage work is independently confirmed on both paths.** The golden **passes**
   `long-read-vintage` (`data-vintage="news"`, `.lr-vintage` absent, byline dated) and
   `cover-leads-on` — including on the legacy non-mx stitch, which is where I expected a gap. That is
   criterion #2's passing half, measured on real generator output rather than a fixture.
2. **The failures are in the fixture's writer content, not the generator.** The golden's
   `chapters/*.html` carry `.plate-img` markup with no provenance attributes, and its Long Read
   figures are photographs. `references/golden/**` is **WP-3's** and the harness is **WP-10's**, so I
   cannot fix either. See § Handoff notes 1 for the minimal change.

---

## What I could not check, and why

1. **`product_shot` may lead only when the band's subject IS the product.** Not decidable from the
   rendered HTML: no band declares a subject type, and `pixel_byte` mixes hardware, software, games
   and services. Implemented as a WARN naming the band and the figure, for gate 3. Making it a FAIL
   would break legitimate hardware coverage; guessing from prose would be worse than not checking.
2. **Whether a `data-shows` value is TRUE.** Every shape budget trusts the declared attribute. A
   writer who labels key art `gameplay` passes every check in this file. That is a Part-6/gate-3
   verification duty, and it is stated in the same terms `check_law9_voices` already uses.
3. **"Captioned as a concluded result" is a caption-text heuristic.** Decided-outcome verbs, a
   scoreline, or `by N shots/points/…`, plus any figure carrying `data-resolves-loop`. Calibrated
   narrow on #18's real Touchline caption ("on his way to pole … the race is still hours from its
   first corner"), which must **not** fire and does not; bare "championship"/"title" are excluded
   because they appear in event *names*. A cleverly-worded result caption can evade it.
4. **The cross-issue lead budget is only as good as `manifest.json`'s `led[]`.** WP-8's back-fill
   records exactly one `led` hash per issue (18 hashes for 18 issues) — i.e. the **cover** lead only —
   but the contract defines `led` as "the issues where it was a **band's** lead figure". #18 alone has
   4 `.plate-img.lead`. So today the check can only catch a repeated *cover* lead. See handoff 3.
5. **The window's opening bound for an already-published issue.** `state.research_cut_at` is #18's
   *own* cut, so validating #18 yields the empty window `(2026-07-26, 2026-07-26]` and
   `results-ledger-multi-sport` is correctly "not applicable". This is right for the real pipeline
   (at validate time, state still holds the *previous* cut) but it means the invariant cannot be
   retro-tested against a shipped issue. Demonstrated with fixture states instead, plus one real-state
   run at `--run-date 2026-08-03`.
6. **No browser render.** Everything here is markup-level.
7. **`--strict` still promotes the pre-existing `image-urls: skipped` warning to a failure.** Untouched
   pre-existing behaviour; it is why the `--strict` fixture run exits 1.

---

## Handoff notes

1. **→ WP-3 (owns `references/golden/**`) and WP-10 (harness): the goldens now fail three image
   checks, and the fix is in the fixture's writer content.** Minimal change, in
   `references/golden/weekly{,-mx}/chapters/*.html`: add the four §3.4 attributes to every
   `.plate-img`, and make ≥1 Long Read figure a `diagram|map|chart|artefact` — that is exactly what
   `scratchpad/fx/pass.html` does to #18, and it is the whole difference between exit 1 and exit 0.
   Alternatively give the golden's assets real records in `assets/cached/manifest.json` and let
   WP-3's stitcher stamp them, which is the direction §3.4a note 6 points. Until then
   `verify-weekly-golden.sh` exits 1 and WP-10's harness must treat that as the *expected* state or
   fix the fixture; **do not** fix it by weakening the check, or criterion #8 becomes unverifiable.
2. **→ orchestrator: the PROGRESS expected-failure ledger needs the correction above.** Two of its
   three predictions were written against a version of #18 that declares figure shapes. #18 declares
   none, so caption-vintage and the key_art clause are inert on it; the defects are caught by
   `figure-provenance` and the two counted shape budgets. Wording proposed at the end of § Issue #18.
3. **→ WP-8: `manifest.json`'s `led[]` currently records cover leads only.** The contract
   (data-contracts.md § `used_image_urls`) says `led` = "the issues where it was a band's **lead**
   figure (`.plate-img.lead`)". The back-fill has one hash per issue; #18 has four `.plate-img.lead`
   (`af9fc905ced8`, `bf64e308503b`, `2601e4c02103`, `8ff67aa0126f`) and only the first is in `led`.
   Recording all band leads going forward makes SPEC §3.8's cross-issue budget actually bite. Two
   further requests, seconding WP-3: keep `capture_year` an integer or absent (never the string
   `"UNKNOWN"`), and `licence.allows_derivatives` a real boolean or absent.
4. **→ WP-9 (owns `stitch-issue.sh` / `publish-gate.sh`): nothing is required, but two things are
   available.** `--state` and `--run-date` auto-resolve, and the resolved values and their provenance
   are printed every run, so the loop and breadth checks are live today. Passing `--run-date` explicitly
   from the pipeline (which knows the real publish date) would remove the filename/today fallback;
   passing `--state` would remove the repo-root discovery. Also: an issue's number is read from the
   masthead `FOLIO`, so the cross-issue lead budget silently degrades to a WARN on any issue that
   renders no folio.
5. **→ WP-6: the derived lists are now read at runtime, so your file is load-bearing for a ship
   gate.** `validate-issue.py` reads `shows.values`, `information_figure_shapes` and
   `never_lead_shapes` from `image-source-types.json` every run (SPEC literals are fallback only). The
   hard/conditional split lives here as *the exception* — `CONDITIONAL_LEAD_SHAPES = ("product_shot",)`
   — so **appending** a shape to `never_lead_shapes` will hard-fail it as a lead with no code change,
   which is the plain reading of the list's name. If you ever want a *second* conditional shape, that
   needs a line here.
6. **→ WP-1: `data-sport` tokens are parsed out of `data-contracts.md` § The closed sport-token list**
   (the ` · `-separated backticked paragraph, currently 22 tokens), so appending a token there needs no
   code change, as your contract promises. Keep that paragraph's shape; if it is ever restructured the
   parser falls back to a 22-token literal and prints
   `(22 sport tokens from the data-contracts.md literal (file unreadable))` — a visible, not silent,
   degradation.
7. **→ orchestrator: `fd32ba6` is not a clean baseline for `validate-issue.py`.** It is downstream of
   the `23672a7` WIP snapshot and already contains 1,140 lines of this WP's in-flight work. I used
   `eb58747`, the last commit before WP-4 touched the file, and said so above. This is WP-3's
   `git stash` problem in a new form: a mid-task snapshot makes *any* later commit unusable as a
   "before" for the file being snapshotted. A WP asked to prove "pre-existing vs mine" needs the ref
   that predates its own first WIP commit.
8. **→ WP-10: the fixtures are in the scratchpad and are yours if you want them.**
   `build_fixtures.py` (a single script; derives everything from frozen #18 by one-point mutation),
   28 HTML fixtures, 4 state fixtures, `run_matrix.sh` (the whole matrix in one command). The state
   fixtures' invented rows are prefixed `FIXTURE DATA — not a real event` so they can never be
   mistaken for facts of record. Deliberately **not** in the repo:
   `references/fixtures/coverage-rebuild/**` is yours.

---
---

# WP-4 round 2 — closing the §3.9 blind spot; `finance` and per-card table kinds

**Status: DONE.** Both fixes shipped in the same exclusive file, `scripts/validate-issue.py`
(+303/−33 against **`d10d34c`**, the named baseline). Everything below is re-run output, including the
39-case matrix, Issue #18, both goldens and the full archive sweep.

Headline: **on the real mx golden, with WP-3b's editorial caption fix reverted, `d10d34c` PASSES and
this version FAILS.** That is the blind spot, closed, demonstrated on the artifact it was found in.

```
$ python3 <d10d34c copy>  fx/golden-unfixed-caption.html --format weekly --skip-image-urls --run-date 2026-07-19
[PASS] caption-vintage: 10 figure(s) with a dated capture year, all consistent with their band's claims…
$ python3 scripts/validate-issue.py fx/golden-unfixed-caption.html --format weekly --skip-image-urls --run-date 2026-07-19
[FAIL] caption-vintage: 1 of 10 dated figure(s) illustrate a later claim without saying so (SPEC §3.9):
```

(The fixture is the committed golden with one edit: `Andy Burnham, pictured in 2024 —` → `Andy Burnham —`.
That figure is `data-capture-year="2024"`, and its band's only dated claim is "This morning" / "sixty-four
years ago this week". Under the old rule the band "made no dated claim" and a 2024 portrait sailed
through a paragraph about this week's handover.)

## 1 · `claim_max` now reads three kinds of dated claim, and quotes its evidence

WP-3b was right that this mattered more than a normal gap: caption vintage is *the* check for the
defect that prompted the rebuild, and a version that only works when the prose happens to use digits
gives false assurance exactly where a reader would be misled. Three sources are now read, and **every
verdict quotes the phrase that produced the year**, so the reasoning is auditable instead of magic:

| Source | Example | Resolved to |
|---|---|---|
| digits (as before) | "In March **2021** a team at UCL…" | 2021 |
| spelled year | "**nineteen sixty-five**", "**nineteen oh six**", "**nineteen hundred and one**", "**eighteen seventy-seven**", "**twenty twenty-one**", "**nineteen fourteen**", "**two thousand and four**", "**seventeen seventy-six**" | 1965 · 1906 · 1901 · 1877 · 2021 · 1914 · 2004 · 1776 |
| spelled decade | "the **nineteen-seventies**" | 1970 — the decade **start**, deliberately conservative: a decade names a range, and the low end is the reading that cannot manufacture a false failure |
| century | "the **twentieth century**", "the **twenty-first century**" | 1900 · 2000 (century start, same reasoning) |
| **this-week deixis** | "**this week**", "**today**", "**tonight**", "**yesterday**", "**this afternoon/morning/evening/weekend/month/year**", "**last night**", "**as this is read**", "on/last/this **Monday**…" | the issue's own year, from the resolved `--run-date` |

Deixis is the source that fixes WP-3b's actual case, and it is not a guess: in a weekly, "this week"
**is** a claim about the issue's year. Weekday hits are skipped when a 4-digit year follows within 30
characters, so "on Monday 15 July 1965" stays a historical date and does not become 2026. Verified
unit-by-unit:

```
$ python3 -c "…band_claim_years(phrase, issue_year=2026)…"
In March 2021 a team at UCL published…                 -> 2021 [digits '2021']
the machine was raised in nineteen hundred and one…    -> 1901 [spelled 'nineteen hundred and one' → 1901]
a nineteen sixty-five flyby…                           -> 1965 [spelled 'nineteen sixty-five' → 1965]
eighteen seventy-seven, the first Championships         -> 1877 [spelled 'eighteen seventy-seven' → 1877]
twenty twenty-one brought the first complete model      -> 2021 [spelled 'twenty twenty-one' → 2021]
the deal closed in two thousand and four                -> 2004 [spelled 'two thousand and four' → 2004]
the nineteen-seventies changed everything               -> 1970 [spelled decade (start of decade) → 1970]
the twentieth century had barely started                -> 1900 [century 'twentieth century' → 1900 (century start)]
the twenty-first century's first great remake            -> 2000 [century → 2000 (century start)]
sworn in as prime minister on Monday, the Westminster…  -> 2026 [this-week deixis 'on Monday' → the issue's year 2026]
the race is still to run this afternoon                 -> 2026 [this-week deixis 'this afternoon' → 2026]
on Monday 15 July 1965 the craft reached Mars            -> 1965 [digits '1965']   <- weekday guard works
```

**Three false-positive traps, closed and tested** (all three are phrases from real issues):

```
crushed and fused by two thousand years in seawater      -> NONE   # a duration, not the year 2000
fifteen hundred years of lost workshops                  -> NONE   # ditto (quantity-noun guard)
nineteen hundred people watched                          -> NONE   # ditto
```

`two thousand …` requires a numeric tail, and the `<century> hundred` form is refused when a quantity
noun follows (`years|months|people|miles|…`). Without those guards issue #18's own Long Read —
"two thousand years in seawater" — would have manufactured a claim of 2000.

### What remains unparseable, and how it is reported

Four forms are recognisably dates but cannot be resolved to a year here, because each needs an anchor
this check does not have. Rather than pass silently or fail falsely, they raise
**`caption-vintage/unparsed-dates`** — a WARNING that quotes exactly what it could not parse:

| Form | Example | Why not resolved |
|---|---|---|
| relative span | "**one hundred and forty-nine years after** the first Championships", "**sixty-four years ago**", "**twenty-five years after** Halo shipped" | needs the anchor event's year (1877, the issue's week, 2001) — not in the band |
| turn of the century | "at the **turn of the century**" | 1900 or 2000, genuinely ambiguous |
| bare decade | "the **sixties**" | 1960s or 1860s; a *prefixed* decade ("the nineteen-sixties") **is** resolved |
| vague span | "**half a century ago**", "**decades ago**" | no arithmetic available |

The warning is filtered so it is diagnostic and not ambient: it fires only for a figure that would
otherwise **pass**, whose caption does **not** already state its year, and whose capture year is
**before** the issue's year (every unresolved form above looks backwards, so a current-year capture
cannot be beaten by one). Real output, on the fixture built from #18's Letter with the deixis removed
and WP-3b's own phrase inserted:

```
### capvintage-unparsed-warn   (exit=0)
[PASS] caption-vintage: 10 figure(s) with a dated capture year, all consistent with their band's claims…
[WARN] caption-vintage/unparsed-dates: 1 dated figure(s) sit in a band whose prose carries a date
       expression that cannot be resolved to a year, so §3.9's claim_max may be UNDERSTATED and the
       verdict below may be a false pass:
    • COVER [the_letter/lead, /assets/cached/af9fc905ced8.jpg] — capture 2024; band 'the_letter'
      contains a date expression this check cannot resolve to a year:
      relative-span: 'one hundred and forty-nine years after'; relative-span: 'twenty-five years after'
    This is the documented blind spot, reported rather than hidden: … Digits, spelled-out years and
    this-week deixis ARE resolved. Check by eye that the caption is not older than what the band
    claims — or write the year into the caption, which makes both the reader and this check certain.
```

It took **four** separate edits to that fixture to strip every deixis marker out of one band
("this week", "the week", "this afternoon", "on Tuesday"), which is itself a result: the rule does not
hang on a single phrase.

**One further correctness fix, measured:** `.bandhead` joined the furniture stripped from band prose.
One of the weekly's bands is literally called *Do This Week*, and its band-head would otherwise date
every figure in it to the issue year on the strength of its own title. Stripping it changed no verdict
anywhere in the archive (those bands' prose says "this week" too), so the only effect is that the
evidence quoted in a failure is always a sentence, never furniture.

### Firing and passing cases (real output, with the `d10d34c` verdict alongside)

```
### capvintage-spelled-claim        d10d34c exit=0   NOW exit=1
    # #18's Long Read with its digit years spelled out (2021→"twenty twenty-one", 2005→"two thousand
    # and five", 1901→"nineteen oh one") and FIG 03 back to its shipped caption. That band carries NO
    # deixis, so this isolates the spelled-year parser.
    NOW  [FAIL] caption-vintage: 1 of 10 dated figure(s) illustrate a later claim without saying so:
         • FIG. 03 […fb560e553feb.jpg] capture year 2007 is OLDER than the band's latest claim 2021
           [spelled 'twenty twenty-one' → 2021], and "2007" does not appear in the caption's visible sentence.
    WAS  [PASS] caption-vintage: 10 figure(s) … all consistent with their band's claims
### capvintage-spelled-claim-ok     d10d34c exit=0   NOW exit=0     # same band, caption corrected
### capvintage-deixis-fire          d10d34c exit=0   NOW exit=1
    # The Letter's cover plate at data-capture-year="2024"; that band has no year in its prose at all.
    NOW  [FAIL] … capture year 2024 is OLDER than the band's latest claim 2026 [this-week deixis
           'this afternoon' → the issue's year 2026], and "2024" does not appear in the caption…
    WAS  [PASS] … COVER — capture 2024, band makes no dated claim          <- the blind spot, exactly
### capvintage-deixis-ok            d10d34c exit=0   NOW exit=0     # caption says "in 2024"
```

And on the committed golden, the same figure is now *checked* rather than waved through — the check
validates WP-3b's editorial fix instead of ignoring it:

```
NOW  [PASS] caption-vintage: … FIG. 01 [the_letter, /assets/cached/2a9d4f29c684.jpg] — capture 2024
     < claim 2026, and the visible caption says so; COVER […] — capture 2026 ≥ band's latest claim
     2026 (this-week deixis 'This morning' → the issue's year 2026); …
WAS  [PASS] caption-vintage: … FIG. 01 [the_letter, …] — capture 2024, band makes no dated claim; …
```

## 2 · `data-table-kind` is read from `weekly.json`, and reported per card

**Moved to runtime, as suggested.** `load_table_kinds()` parses the enum out of
`weekly.json § structural_hooks.table_kind` (the inline `data-table-kind ∈ a|b|c…` list), falling back
to `furniture_layer.components.standings_card` and then to a literal — which now includes `finance`.
The provenance is printed, so a fallback is visible rather than silent:

```
### table-kind-finance             d10d34c exit=1   NOW exit=0
    NOW  [PASS] table-kind: 2 data-table-kind value(s), all legal: ['championship', 'finance']
                (6 table kind(s) from weekly.json § structural_hooks.table_kind)
    WAS  [FAIL] table-kind: data-table-kind value(s) outside the five legal shapes: ['finance'].
                Legal: ['league', 'medal', 'gc', 'leaderboard', 'championship']
### table-kind-bad                 NOW exit=1      # 'table' is still rejected
    [FAIL] table-kind: data-table-kind value(s) outside the legal shapes: ['table']. Legal: ['league',
    'medal', 'gc', 'leaderboard', 'championship', 'finance'] (6 table kind(s) from weekly.json …).
    … If the shape is genuinely new, it is a weekly.json + CSS change (WP-3's files), not a value a
    writer can invent.
```

A seventh kind will now propagate the moment WP-3 adds it. The hardcoded enum was the whole reason
WP-3b could not stamp the Desk card without taking the golden to exit 1, and it should not be able to
happen again.

**Per-card reporting: yes, worth it.** WP-3b is right that the per-issue form was effectively silent —
one declared card suppressed the warning for every undeclared one. The card is now named by band and
title, which is what makes it actionable, and the message says explicitly that a per-issue check would
have said nothing. The noise is bounded (a weekly carries two cards):

```
# the mx golden — the case the old form hid completely
[WARN] table-kind/undeclared: 1 of 2 .mx-scorecard card(s) carry no data-table-kind and render as the
       unstyled base shape:
    • band 'the_desk' — "The Rate War · As of 19 Jul"
    Declare one of ['league', 'medal', 'gc', 'leaderboard', 'championship', 'finance'] (SPEC §3.4 /
    §3.11). Reported per card: 1 card(s) in this issue DO declare a kind, and a per-issue check would
    have said nothing about these.

# issue #18 — both cards, both named
[WARN] table-kind/undeclared: 2 of 2 .mx-scorecard card(s) …
    • band 'touchline' — "Drivers' Championship · Into Round 11"
    • band 'the_desk' — "The Rate War · As of 26 Jul"
```

The check is split so the two findings can never mask each other: `table-kind` (value validity, FAIL)
and `table-kind/undeclared` (absence, WARN).

## 3 · Re-runs — no regression anywhere

**39-case matrix** (the original 32 plus 7 new: 5 caption-vintage year-form cases, 2 table-kind).
Every one of the original 32 verdicts is unchanged; all 39 behave as documented.

```
$ bash run_matrix.sh          # 39 cases
### pass.html (the corrected fixture)              (exit=0)
### vintage-missing / -bad-enum / -news-with-lrvintage / -evergreen-dated-byline /
    -evergreen-no-lrvintage / -evergreen-no-framing (exit=1 each, one FAIL each)
### vintage-evergreen-ok                           (exit=0)
### capvintage-fire                                (exit=1)  caption-vintage
### capvintage-null-year                           (exit=0)  data-capture-year="" still legal
### capvintage-bad-year                            (exit=1)  figure-provenance/values
### capvintage-spelled-claim                       (exit=1)  NEW
### capvintage-spelled-claim-ok                    (exit=0)  NEW
### capvintage-deixis-fire                         (exit=1)  NEW
### capvintage-deixis-ok                           (exit=0)  NEW
### capvintage-unparsed-warn                       (exit=0)  NEW — WARN only, no false failure
### provenance-missing                             (exit=1)
### shapes-keyart-leads-pb / -two-keyart-pb / -lr-no-information-figure /
    -two-distinct-shapes / -repeat-lead / -touchline-result-keyart /
    -portrait-lead / -keyart-lead-nonpb              (exit=1 each)
### shapes-productshot-lead                        (exit=0)  WARN (conditional never-lead)
### shapes-touchline-result-ok                     (exit=0)
### table-kind-bad                                 (exit=1)
### table-kind-finance                             (exit=0)  NEW — was exit=1 at d10d34c
### table-kind-one-undeclared                      (exit=0)  NEW — per-card WARN
### ledger-multi-sport-token                       (exit=1)
### ledger-unknown-token                           (exit=0)  soft WARN
### ledger-one-sport + state-two-sports            (exit=1)
### ledger-two-sports + state-two-sports           (exit=0)
### ledger-one-sport + state-golf-off              (exit=0)  not applicable
### pass.html + state-matured-loop                 (exit=1)  resolved-loops
### loop-resolved + state-matured-loop             (exit=0)
### pass.html + state-matured-loop @ 2026-07-18    (exit=0)  not yet matured
### ledger-unknown-token --strict                  (exit=1 — image-urls only; token stayed a WARN)
```

**Archive sweep, 34 files, `d10d34c` vs now, comparing every check's verdict by name.** Only three
rows changed at all, all of them the intended rename of one warning:

```
FILE                                     d10d34c  NOW      verdict changes
signal_season-review_2026-07-20.html     exit=0   exit=0   < [WARN] table-kind > [WARN] table-kind/undeclared
signal_weekly_2026-07-26.html            exit=1   exit=1   < [WARN] table-kind > [WARN] table-kind/undeclared
expected.html                            exit=0   exit=0   > [WARN] table-kind/undeclared
(rows shown = changed; 31 files identical)
```

**No exit code changed anywhere.** No issue newly fails `caption-vintage` — the spelled-year and deixis
rules found nothing in the archive to fail, because the archive's captions either state their years
(WP-3b's corrections) or carry no capture year at all. The one *new* finding is the golden's
`table-kind/undeclared`, which the per-issue form had hidden.

**Issue #18: unchanged, still exit 1, still 5 failures** — `figure-provenance` (11/11),
`image-shapes/distinct`, `image-shapes/long-read-information`, `long-read-vintage`, `cover-leads-on`;
warnings `caption-vintage` (still inert: #18 declares no capture year, so §3.9 still has nothing to
compare — the round-2 work does not change that), `table-kind/undeclared` (now naming both cards) and
`image-urls`. **Not repaired**, per SPEC §1.3.

**Both goldens: `verify-weekly-golden.sh` REAL EXIT=0**, and the mx golden validates at exit 0
directly. WP-3's fixture repair (`fa8c80c`) plus WP-3b's provenance recovery mean the golden now
passes every check I own, with three warnings (`figure-provenance/licence-unknown` ×4,
`table-kind/undeclared` ×1, `image-urls`). The § handoff-1 item from round 1 is **closed** — by the
fixture being fixed, not by a check being weakened.

```
$ bash .claude/skills/the-signal/scripts/verify-weekly-golden.sh > golden2.txt 2>&1 ; echo "REAL EXIT=$?"
REAL EXIT=0
$ python3 -m py_compile .claude/skills/the-signal/scripts/validate-issue.py && echo OK
OK
$ git status --short
 M .claude/skills/the-signal/references/golden/weekly/chapter-plan.json   <- not mine (concurrent WP)
 M .claude/skills/the-signal/scripts/validate-issue.py                    <- mine
 M .claude/skills/the-signal/scripts/verify-weekly-golden.sh              <- not mine (concurrent WP)
 M docs/editorial-coverage-rebuild-EVIDENCE/WP-4.md                       <- this file
```

(The two files marked *not mine* appeared during this round — another WP working the golden harness
concurrently. Untouched here; `git diff --numstat d10d34c` shows my footprint is `303 33
.claude/skills/the-signal/scripts/validate-issue.py` and nothing else.)

*One artefact of the baseline method, so nobody misreads it:* the `d10d34c` copy runs from the
scratchpad, so its `SKILL_ROOT` cannot find `references/`, and it prints
`shows vocab from the SPEC §3.3/§3.8 literals (image-source-types.json unreadable)`. That is the
fallback doing its job, not a difference between the two versions — the literals and the file agree on
all three shape lists, and no verdict differs because of it. `TABLE_KINDS` at `d10d34c` was genuinely
hardcoded with no file read at all, so the `table-kind-finance` failure above is real, not a path
artefact.

## Round-2 handoff notes

1. **→ WP-3 / WP-3b: the Desk's finance card is now stampable and is being asked for by name.**
   `finance` is legal (read from your `weekly.json`), and `table-kind/undeclared` names
   `band 'the_desk' — "The Rate War · As of 19 Jul"` in the golden. Adding `data-table-kind="finance"`
   there clears the last warning I raise against the golden's furniture.
2. **→ WP-2 / WP-6: the remaining §3.9 exposure is editorial, not mechanical.** A relative span
   ("*one hundred and forty-nine years after the first Championships*") cannot be resolved by any
   check, so the durable fix is the writing rule: **if a figure is older than the week it illustrates,
   the year goes in the visible sentence.** That single sentence in the editorial spec makes the
   caption right for the reader *and* makes this check certain, which is why the warning says so.
3. **→ WP-10: seven new fixtures, same script.** `build_fixtures.py` now emits 35 HTML fixtures
   (including `golden-unfixed-caption.html`, built from the committed golden by reverting one caption —
   the cleanest possible regression test for the blind spot) and 3 state fixtures. `run_matrix.sh` runs
   all 39 cases in one command.
4. **→ coordinator: the deixis rule makes `--run-date` load-bearing for §3.9, not just §3.7.** It is
   still auto-resolved (filename, then today UTC) and its provenance is printed every run, but a
   pipeline that passes a wrong `--run-date` now moves `claim_max` for every band that says "this
   week". Passing it explicitly from the publish step (WP-9's `stitch-issue.sh`) would remove the
   fallback entirely.
