# WP-8 — Asset provenance + licence safety

**Date:** 2026-07-26
**Branch:** `claude/signal-antikythera-article-lzzlup`
**Contract:** SPEC §3.10. Acceptance criteria #9 and #10.
**Status:** done. Both criteria demonstrated below with real command output.

---

## 1. What changed

### Problem 1 — provenance did not survive publish

`scripts/mirror-images.py` names cached files `sha256(url)[:12]` and rewrites the HTML to point at
`/assets/cached/<hash>.<ext>`. The hash is one-way, so once the rewrite happened the source URL was
gone. The credit string in the HTML was the only record and it is unverifiable.

`mirror-images.py` now writes and maintains **`assets/cached/manifest.json`**, keyed by the same
12-char hash. `url_hash()` is byte-for-byte unchanged — changing it would orphan all 438 cached files.

Shape as implemented (SPEC §3.10 plus two additive keys, marked):

```jsonc
{ "af9fc905ced8": {
    "url":          "https://…"        | "UNKNOWN",
    "fetched_at":   "2026-07-26T…Z"    | "UNKNOWN",
    "licence": { "holder": "…" | "UNKNOWN",
                 "code":   "CC-BY-2.5" | "UNKNOWN",   // SPDX-ish token, SPEC §3.2
                 "url":    "https://…" | "UNKNOWN",
                 "allows_derivatives": true | false | null },
    "shows":        "in_engine"        | "UNKNOWN",   // enum SPEC §3.3
    "capture_year": 2007 | null        | "UNKNOWN",
    "issues":       [18],            // weekly issue numbers, from archive-manifest.json
    "led":          [18],            // issues where this asset was the cover figure
    "issue_slugs":  ["signal_weekly_2026-07-26"],   // ADDITIVE
    "led_slugs":    ["signal_weekly_2026-07-26"],   // ADDITIVE
    "notes":        "…" } }                          // ADDITIVE
```

**Why the three additive keys.** `issues`/`led` are ints per SPEC §3.5, but 15 of the 33 published
issues are specials with `issue_number: null` in `archive-manifest.json`. Rather than mix ints and
strings in one list (which every consumer would then have to type-check), `issues`/`led` stay
int-only and `issue_slugs`/`led_slugs` carry the complete picture. `notes` is required by the WP-8
brief: pre-manifest entries must say so in the record.

**Explicit unknown markers, never omitted keys.** A missing key is silent; a marker is auditable.
Two markers, because one is not enough:

| marker | used for | why |
|---|---|---|
| `"UNKNOWN"` (string) | `url`, `fetched_at`, `shows`, `capture_year`, `licence.holder/code/url` | SPEC §3.2 already defines `"UNKNOWN"` for `licence.code`; this extends the same convention. `capture_year` must use it because `null` is a *legitimate* value there (SPEC §3.2: null when `shows` ∈ {diagram, chart} and synthetic) |
| `null` | `licence.allows_derivatives` | it is a boolean; there is no string form, and callers must distinguish "known permissive" from "not known" |

**Which fields a later phase fills, and who owns it.** Documented in the module docstring and
repeated here:

| field | filled by |
|---|---|
| `url`, `fetched_at` | `mirror-images.py`, at download time |
| `issues`, `led`, `issue_slugs`, `led_slugs` | `mirror-images.py`, by scanning `/issues/*.html` |
| `licence{holder,code,url,allows_derivatives}`, `shows`, `capture_year` | **not this script.** They originate in the research bundle's `image_candidates[]` (SPEC §3.2): contract owned by **WP-1**, presence enforced by **WP-5** (`validate-research-bundle.py`), and copied into this manifest by the publish phase that **WP-9** wires in `SKILL.md` |

`mirror-images.py` never invents them. Until WP-9's wiring lands they stay `"UNKNOWN"` for *new*
images too, which is the honest state and is exactly what makes the gap visible.

**Durability guarantees.** The brief says treat losing an entry as a bug, so:

- **Merge-on-write.** `merge_entry()` fills gaps only. A known value is never overwritten by an
  unknown one, a key the incoming record does not carry is never touched, and unrecognised keys added
  by a later phase are preserved verbatim. `issues`/`led`/`*_slugs` are unioned, not replaced —
  usage history is append-only (an image that appeared in issue 17 appeared in issue 17).
- **Never prunes.** Entries whose bytes are no longer in the cache are carried through untouched and
  counted separately as `carried`. A merge that would shrink the manifest aborts:
  `FATAL: manifest merge would drop entries — refusing to write.`
- **Atomic write.** Temp file + `os.replace()`, so an interrupted run cannot truncate the record.
- **A corrupt manifest aborts the run** rather than being silently replaced by a fresh one — that is
  the one failure mode that would destroy provenance rather than merely fail to add it.
- **Idempotent.** Two consecutive runs produce a byte-identical file (proved in §3.2).

**Backfill — what is honestly knowable, and nothing more.**

- All 438 existing cached files got an entry. 425 of them have `url: "UNKNOWN"` and a note saying
  they predate the manifest and that the URL is unrecoverable. **No URL was guessed, and no licence
  was parsed out of a credit string.** (Credit strings *are* present in the HTML — e.g. `No 10
  Downing Street · CC BY-NC-ND` — but regexing free-text credits into a machine licence record would
  fabricate licences for entries like `Formula 1` or `Notebookcheck`. Explicitly not done.)
- 13 URLs *were* honestly recovered, and this is worth recording because the original diagnosis said
  none were. The reverse-hash attempt failed because it guessed at candidate URLs. Instead: re-hash
  every image URL that ever appeared **in this repo's own git history** and keep the ones whose hash
  matches a file in `assets/cached/`. 45 distinct URLs ever appeared; 13 matched. Each pair is
  verified by `sha256(url)[:12] == filename`, so these are proofs, not inferences. The remaining 425
  really are unrecoverable: their pre-rewrite HTML was never committed.
- `issues`/`led` were backfilled mechanically from the published HTML: 374 assets are referenced by
  an issue and 29 led one. This is honest provenance the pipeline already had and was throwing away.

### Problem 2 — a live licence violation

`scripts/extract-covers.py` smart-crops and resizes an issue's cover source into `assets/covers/`.
That is a derivative work. Issue #18's cover source is credited **CC BY-NC-ND** — ND means
NoDerivatives — so the pipeline was generating a prohibited derivative of the one image whose terms
are unambiguous.

`extract-covers.py` now reads `licence.allows_derivatives` from the manifest before deriving
anything:

| `allows_derivatives` | behaviour |
|---|---|
| `true` | derive normally |
| `false` | **REFUSE.** Nothing is written, any existing cover is left alone, the message names the file, the cached asset and the licence, and the run exits **2** |
| `null`, or no manifest entry, or no manifest file | **UNKNOWN.** Warn loudly and proceed by default; refuse under `--strict-licence` |

Refusals do not abort the batch — every other issue is still processed and the non-zero exit is
raised once at the end, so one bad source cannot half-generate an archive.

Also added, both forward-looking:

- **`FROZEN_SLUGS`** — SPEC §1 rule 3 freezes Issue #18. `signal_weekly_2026-07-26` is now skipped
  even under `--force`, so its published cover cannot be re-cropped, regenerated or deleted by a
  future run. Nothing in this WP touched it (md5 verified unchanged in §3.4).
- **`--nd-fallback contain`** — the non-cropping path the brief asked about. `make_thumb_contain()`
  scales the whole frame proportionally and letterboxes it onto the 800×533 canvas the archive grid
  expects; nothing is cut off. **It is opt-in per run and the default stays a hard refusal**, and the
  docstring says why: a pure proportional resize is defensible as a technical format change, but
  compositing the work onto a canvas of a different aspect ratio is itself an edit and CC's
  NoDerivatives term is not settled on it. So it is offered as a deliberate, per-run human decision,
  never as an automatic escape hatch.

### The judgement call: unknown licence proceeds by default

The brief flagged this as a judgement call. **Decision: unknown ⇒ warn and proceed; `--strict-licence`
escalates to refusal.**

Why not refuse on unknown:

1. **It would refuse everything, today.** All 438 cached assets currently have
   `allows_derivatives: null`, and 425 of them can never be resolved. Strict-by-default means every
   cover regeneration fails and `--force` becomes unusable — the existing archive is bricked.
2. **It would also refuse every new issue,** because `licence` only starts arriving once WP-1's
   bundle contract, WP-5's enforcement and WP-9's wiring are all in place. A gate that fails on
   100% of inputs from day one gets switched off or `|| true`'d within a week, and then the *real*
   check — the `false` branch — dies with it.
3. **"Unknown" is not evidence of ND.** Refusing on it buys no actual safety signal; it just
   converts a documented gap into noise.
4. **The default still fails safe on the thing that matters.** A licence known to forbid derivatives
   is refused, unconditionally, with no flag needed. That is the live violation SPEC §3.10 names.

What makes this safe rather than lazy: the gap is *loud*, not silent. Every unknown prints a per-file
warning, the run summary counts them, and `mirror-images.py` reports
`N without a source URL, N without a licence` on every run. `--strict-licence` is the intended
setting once licences are populated — see the handoff note.

---

## 2. Files touched

| File | Change |
|---|---|
| `scripts/mirror-images.py` | manifest write/merge/backfill, usage scan, `--manifest`, `--manifest-only`. `url_hash()` unchanged. |
| `scripts/extract-covers.py` | licence gate, `FROZEN_SLUGS`, `--manifest`, `--strict-licence`, `--nd-fallback`, `make_thumb_contain()`. |
| `assets/cached/manifest.json` | **new, generated** — 438 entries. WP-8's deliverable per SPEC §3.10; needs committing. |
| `docs/editorial-coverage-rebuild-EVIDENCE/WP-8.md` | this file. |

No other file was edited. `docs/editorial-coverage-rebuild-PROGRESS.md` deliberately untouched
(SPEC §1 rule 5).

Fixtures live in the scratchpad, never in the repo:
`/tmp/claude-0/-home-user-the-signal/81541fa2-7765-5cd6-810f-5027bff091c8/scratchpad/repo/`.

---

## 3. Verification

### 3.1 Acceptance criterion #9 — `extract-covers.py` exits non-zero on `allows_derivatives: false`

Fixture: a throwaway repo root in the scratchpad (copied scripts, two real cached images, three
fixture issue HTMLs, a hand-written manifest). `md5sum` confirms the script under test is
byte-identical to the repo's.

```
$ md5sum scripts/extract-covers.py $SP/repo/scripts/extract-covers.py
de0ca581ffc0bcaa1c7609dff7782be5  /home/user/the-signal/scripts/extract-covers.py
de0ca581ffc0bcaa1c7609dff7782be5  .../scratchpad/repo/scripts/extract-covers.py
```

**ND source (`allows_derivatives: false`) — refused, exit 2:**

```
$ python3 $SP/repo/scripts/extract-covers.py $SP/repo/issues/fixture_nd_2026-08-02.html; echo "exit=$?"
  ✗ REFUSED: fixture_nd_2026-08-02.html — will not crop/resize af9fc905ced8.jpg (/assets/cached/af9fc905ced8.jpg). Its licence forbids derivative works: CC-BY-NC-ND-2.0 (holder: No 10 Downing Street) <https://creativecommons.org/licenses/by-nc-nd/2.0/>. A cover thumbnail is a derivative. Use an image whose licence allows derivatives, or re-run with --nd-fallback contain after reading its caveat.

Done. Made: 0, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 0, refused: 1.

1 cover(s) refused on licence grounds:
  - REFUSED: fixture_nd_2026-08-02.html — will not crop/resize af9fc905ced8.jpg (/assets/cached/af9fc905ced8.jpg). Its licence forbids derivative works: CC-BY-NC-ND-2.0 (holder: No 10 Downing Street) <https://creativecommons.org/licenses/by-nc-nd/2.0/>. A cover thumbnail is a derivative. Use an image whose licence allows derivatives, or re-run with --nd-fallback contain after reading its caveat.
exit=2
```

**Permissive source (`allows_derivatives: true`) — derived, exit 0:**

```
$ python3 $SP/repo/scripts/extract-covers.py $SP/repo/issues/fixture_permissive_2026-08-09.html; echo "exit=$?"
  ✓ fixture_permissive_2026-08-09.jpg ← 1a2d67f3ca02.jpg

Done. Made: 1, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 0, refused: 0.
exit=0

$ ls -l $SP/repo/assets/covers/
-rw-r--r-- 1 root root 49173 Jul 26 11:14 fixture_permissive_2026-08-09.jpg
```

**Unknown licence — warn + proceed by default, refuse under `--strict-licence`:**

```
$ python3 scripts/extract-covers.py issues/fixture_unknown_2026-08-16.html; echo "exit=$?"
  ⚠ fixture_unknown_2026-08-16.html — no licence on record for 1a2d67f3ca02.jpg (/assets/cached/1a2d67f3ca02.jpg); provenance unknown, cannot confirm that a derivative is permitted. Proceeding — pass --strict-licence to refuse.
  ✓ fixture_unknown_2026-08-16.jpg ← 1a2d67f3ca02.jpg

Done. Made: 1, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 1, refused: 0.
exit=0

$ python3 scripts/extract-covers.py --strict-licence issues/fixture_unknown_2026-08-16.html; echo "exit=$?"
  ✗ REFUSED (--strict-licence): fixture_unknown_2026-08-16.html — no licence on record for 1a2d67f3ca02.jpg (/assets/cached/1a2d67f3ca02.jpg); provenance unknown, cannot confirm that a derivative is permitted.

Done. Made: 0, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 1, refused: 1.

1 cover(s) refused on licence grounds:
  - REFUSED (--strict-licence): fixture_unknown_2026-08-16.html — no licence on record for 1a2d67f3ca02.jpg (/assets/cached/1a2d67f3ca02.jpg); provenance unknown, cannot confirm that a derivative is permitted.
exit=2
```

The `deadbeef0000` entry in that fixture manifest has no bytes in the cache — it exists to prove the
merge never prunes orphans (§3.2).

**`--nd-fallback contain` — no crop, whole frame preserved, 3:2 canvas:**

```
$ python3 scripts/extract-covers.py --nd-fallback contain issues/fixture_nd_2026-08-02.html; echo "exit=$?"
  ~ fixture_nd_2026-08-02.jpg — af9fc905ced8.jpg is NoDerivatives [CC-BY-NC-ND-2.0 (holder: No 10 Downing Street) <https://creativecommons.org/licenses/by-nc-nd/2.0/>]; using the non-cropping contain path because --nd-fallback contain was given.
  ✓ fixture_nd_2026-08-02.jpg ← af9fc905ced8.jpg (contain)

Done. Made: 1, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 0, refused: 0.
exit=0

assets/covers/fixture_nd_2026-08-02.jpg (800, 533)     # 3:2 canvas, source letterboxed
assets/cached/af9fc905ced8.jpg (1024, 683)             # source, 1.499:1 — nothing cropped
```

**No manifest at all (first run) — both scripts still work:**

```
$ python3 scripts/extract-covers.py issues/fixture_permissive_2026-08-09.html; echo "exit=$?"
  · no provenance manifest at .../assets/cached/manifest.json — every licence is unknown. Run scripts/mirror-images.py --manifest-only to create it.
  ⚠ fixture_permissive_2026-08-09.html — no licence on record for 1a2d67f3ca02.jpg (…); provenance unknown, cannot confirm that a derivative is permitted. Proceeding — pass --strict-licence to refuse.
  ✓ fixture_permissive_2026-08-09.jpg ← 1a2d67f3ca02.jpg

Done. Made: 1, skipped: 0, frozen: 0, no cover: 0, missing src: 0, unknown licence: 1, refused: 0.
exit=0

$ python3 scripts/extract-covers.py --strict-licence issues/fixture_permissive_2026-08-09.html; echo "exit=$?"
  ✗ REFUSED (--strict-licence): fixture_permissive_2026-08-09.html — no licence on record for 1a2d67f3ca02.jpg (…); provenance unknown, cannot confirm that a derivative is permitted.
…
exit=2
```

**Corrupt manifest is refused, not overwritten, by both scripts:**

```
$ printf '{ not json' > $SP/corrupt.json
$ python3 scripts/mirror-images.py --manifest-only --manifest $SP/corrupt.json; echo "exit=$?"
FATAL: .../corrupt.json exists but is not valid JSON (Expecting property name enclosed in double quotes: line 1 column 3 (char 2)).
Refusing to overwrite it — that would lose provenance. Fix or move the file, then re-run.
exit=1
$ cat $SP/corrupt.json
{ not json                       # untouched

$ python3 scripts/extract-covers.py --manifest $SP/corrupt.json issues/fixture_permissive_2026-08-09.html; echo "exit=$?"
FATAL: .../corrupt.json is not valid JSON (…). Cannot verify image licences, so refusing to derive any cover.
exit=1
```

### 3.2 Acceptance criterion #10 — `mirror-images.py` writes the manifest with url + licence per hash

**Creation (438 entries, all fields present, honest unknowns):**

```
$ python3 scripts/mirror-images.py --manifest-only; echo "exit=$?"
Manifest: /home/user/the-signal/assets/cached/manifest.json
  entries: 438  (new 438, updated 0, unchanged 0, carried 0)
  backfilled with unknown provenance this run: 438
  entries with no source URL: 438
  entries with unknown licence: 438
  licence / shows / capture_year come from the research bundle (SPEC §3.2) — WP-1 contract, WP-5 enforcement, WP-9 wiring.
exit=0
```

Issue #18's cover source, as written — every key present, `led`/`issues` recovered mechanically:

```json
"af9fc905ced8": {
  "capture_year": "UNKNOWN",
  "fetched_at": "UNKNOWN",
  "issue_slugs": ["signal_weekly_2026-07-26"],
  "issues": [18],
  "led": [18],
  "led_slugs": ["signal_weekly_2026-07-26"],
  "licence": { "allows_derivatives": null, "code": "UNKNOWN", "holder": "UNKNOWN", "url": "UNKNOWN" },
  "notes": "Cached before assets/cached/manifest.json existed (WP-8, 2026-07-26). Source URL is unrecoverable: sha256(url)[:12] is one-way and the pre-rewrite HTML was never committed. Not inferred from the credit line.",
  "shows": "UNKNOWN",
  "url": "UNKNOWN"
}
```

**Provenance recovery from git history — 13 URLs, each verified by re-hashing:**

```
$ python3 - <<'PY'   # full script in §1; verifies sha256(url)[:12] == filename for every pair
verified + seeded 13 recovered source URLs into assets/cached/manifest.json
PY
```

**Merge round-trip on the real 438-entry manifest — nothing lost, known values survive, idempotent:**

```
$ cp assets/cached/manifest.json $SP/real-before-merge.json
$ python3 scripts/mirror-images.py --manifest-only; echo "exit=$?"
Manifest: /home/user/the-signal/assets/cached/manifest.json
  entries: 438  (new 0, updated 0, unchanged 438, carried 0)
  backfilled with unknown provenance this run: 0
  entries with no source URL: 425
  entries with unknown licence: 438
  licence / shows / capture_year come from the research bundle (SPEC §3.2) — WP-1 contract, WP-5 enforcement, WP-9 wiring.
exit=0

$ python3 -c '<compare before/after>'
entries before/after: 438 438
no entry lost: True
entries with a known source URL before/after: 13 13
all known URLs identical after re-run: True
full manifest unchanged by the second pass: True

sample recovered entry:
{
  "0b70090b884a": {
    "capture_year": "UNKNOWN",
    "fetched_at": "UNKNOWN",
    "issue_slugs": ["signal_field-guide_2026-05-17"],
    "issues": [],
    "led": [],
    "led_slugs": [],
    "licence": { "allows_derivatives": null, "code": "UNKNOWN", "holder": "UNKNOWN", "url": "UNKNOWN" },
    "notes": "Source URL recovered from git history (an older committed revision of an issue still carried the external URL); verified by sha256(url)[:12] == filename. licence/shows/capture_year remain unknown.",
    "shows": "UNKNOWN",
    "url": "https://cdn.libemaweb.com/f/151320/2560x1707/b5737b08eb/interieur-restaurant-nommos.JPG"
  }
}
```

The `url: "UNKNOWN"` count dropping 438 → 425 while `entries` stays 438 and every seeded URL is
byte-identical after the re-run is the merge proof: the run had no URL of its own to offer for those
13 hashes and did **not** clobber them back to `"UNKNOWN"`.

**Merge round-trip in the sandbox, with known licences and an orphan entry present:**

```
$ python3 scripts/mirror-images.py --manifest-only   # fixture repo, 3 entries, 2 cached files
  entries: 3  (new 0, updated 2, unchanged 0, carried 1)

entries before/after: 3 3
every pre-existing key survived: True
  1a2d67f3ca02: known scalars preserved=True  licence preserved=True  licence.allows_derivatives=True   issue_slugs=['fixture_permissive_2026-08-09', 'fixture_unknown_2026-08-16'] led_slugs=[…]
  af9fc905ced8: known scalars preserved=True  licence preserved=True  licence.allows_derivatives=False  issue_slugs=['fixture_nd_2026-08-02'] led_slugs=['fixture_nd_2026-08-02']
  deadbeef0000: known scalars preserved=True  licence preserved=True  licence.allows_derivatives=None   issue_slugs=[] led_slugs=[]
```

`deadbeef0000` has no bytes in the cache and was still carried through untouched (`carried 1`) —
the manifest never prunes. Known `true` and known `false` licences both survived a merge, and the
usage lists were unioned rather than replaced.

**Idempotence (second consecutive run is byte-identical):**

```
$ python3 scripts/mirror-images.py --manifest-only
  entries: 3  (new 0, updated 0, unchanged 2, carried 1)
$ diff -q $SP/run1.json assets/cached/manifest.json && echo "BYTE-IDENTICAL across runs"
BYTE-IDENTICAL across runs
```

### 3.3 `py_compile`

```
$ rm -rf scripts/__pycache__
$ python3 -m py_compile scripts/mirror-images.py scripts/extract-covers.py && echo "OK (exit 0)"
OK (exit 0)
```

### 3.4 The archive is not bricked and Issue #18 is untouched

```
$ python3 scripts/extract-covers.py; echo "exit=$?"
  ? signal_next_2026-05-31.html — no cover image found
  ? starterkit-audio-dramas.html — no cover image found
  ? versus-tlm-ibex.html — no cover image found

Done. Made: 0, skipped: 30, frozen: 0, no cover: 3, missing src: 0, unknown licence: 0, refused: 0.
exit=0
```

All 30 existing covers skipped, exit 0. The three `no cover image found` lines are pre-existing
behaviour for those specials, unchanged by this WP.

`FROZEN_SLUGS` holds even under `--force`, and the published cover's md5 is identical before and
after:

```
$ md5sum assets/covers/signal_weekly_2026-07-26.jpg
b1e51fe76bfeecc41b73847d0082d653  assets/covers/signal_weekly_2026-07-26.jpg

$ python3 scripts/extract-covers.py --force issues/signal_weekly_2026-07-26.html; echo "exit=$?"
  = signal_weekly_2026-07-26.jpg — frozen issue (SPEC §1 rule 3), left as published

Done. Made: 0, skipped: 0, frozen: 1, no cover: 0, missing src: 0, unknown licence: 0, refused: 0.
exit=0

$ md5sum assets/covers/signal_weekly_2026-07-26.jpg
b1e51fe76bfeecc41b73847d0082d653  assets/covers/signal_weekly_2026-07-26.jpg
```

### 3.5 Repo state — only WP-8's files

```
$ git diff --stat
 functions/daily/feeds.js   |  38 ++++
 functions/daily/profile.js | 120 ++++++++++++-
 scripts/extract-covers.py  | 227 +++++++++++++++++++++++-
 scripts/mirror-images.py   | 423 ++++++++++++++++++++++++++++++++++++++++++++-
 4 files changed, 801 insertions(+), 7 deletions(-)

$ git status --short
 M functions/daily/feeds.js
 M functions/daily/profile.js
 M scripts/extract-covers.py
 M scripts/mirror-images.py
?? assets/cached/manifest.json
```

`functions/daily/feeds.js` and `functions/daily/profile.js` are **WP-7's** exclusive files
(SPEC §2), being edited concurrently in the same worktree. WP-8 did not touch them.

WP-8's footprint: the two owned scripts, plus the new generated `assets/cached/manifest.json`.
`assets/covers/` and `issues/` are clean — no fixture leaked into the repo and no cover was mutated.

---

## 4. What's left

1. **`licence`, `shows` and `capture_year` are `"UNKNOWN"` for all 438 entries.** By design — WP-8
   cannot know them. They arrive when WP-1's bundle contract (§3.2), WP-5's enforcement and WP-9's
   publish-phase wiring are all in place. Nothing here blocks that: the keys exist and merge-on-write
   fills them without disturbing anything else.
2. **425 source URLs are permanently unrecoverable.** Recorded as such. Not fixable.
3. **`--strict-licence` is not yet the default,** and should not be flipped until (1) lands. See
   handoff note H2.
4. **Not attempted:** pruning stale cache files, deduplicating thumbnail variants of the same
   source, and cross-checking the manifest against `state/signal-state.json`'s `used_image_urls`
   (§3.5) — that state key does not exist yet and `state/signal-state.json` is WP-1's file.

## 5. Handoff notes

- **H1 — commit `assets/cached/manifest.json`.** It is untracked. It is WP-8's deliverable per
  SPEC §3.10 and the whole point is that it is durable; if it is not committed, provenance dies again
  at the next checkout. 438 entries, ~265 KB.
- **H2 — WP-9 should wire `--strict-licence` on, in the same change that starts populating
  `licence` from the research bundle.** The flag exists precisely so that flip is one word. Until
  then it would refuse every issue (see the judgement call in §1).
- **H3 — `af9fc905ced8` (Issue #18's cover source) is credited CC BY-NC-ND in the HTML but records
  `allows_derivatives: null`,** because WP-8 will not machine-parse credit strings into licences.
  The consequence: the ND gate would *not* fire on #18 today. It does not need to — `FROZEN_SLUGS`
  means #18's cover is never re-derived — but whoever owns the licence backfill should set this entry
  by hand from the published credit (`holder: "No 10 Downing Street"`, `code: "CC-BY-NC-ND"`,
  `allows_derivatives: false`) so the archive's one known ND asset is machine-readable. Merge-on-write
  will preserve it.
- **H4 — cover-region detection is duplicated** between `mirror-images.py` (`COVER_REGION_RES`,
  `_dom_only`) and `extract-covers.py` (`COVER_PATTERNS`, `_dom_only`). The two must agree on which
  figure "led" an issue. They cannot share a helper because SPEC §2 gives WP-8 no third file. If a
  later WP adds a `scripts/` shared module, fold both into it; until then, a change to one needs the
  same change to the other.
- **H5 — WP-4's cross-issue check (§3.8: "a `src` that `led` the previous issue may not lead this
  one") can read `led`/`led_slugs` straight from this manifest.** Already backfilled across all 33
  published issues: 29 assets carry a non-empty `led_slugs`. Note `led` is int-only (weeklies);
  specials are in `led_slugs`.
- **H6 — `--nd-fallback contain` is deliberately not automatic.** If the archive later wants ND
  sources usable, that is a licensing decision for the owner, not a default. The code path is ready.
