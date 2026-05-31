# The Signal — Editorial Quality Rubric

This rubric is the pipeline's **quality signal**. Every other gate in the
workflow measures *compliance* (did the issue break a rule?). This one
measures *quality* (is the issue good?) — the thing the magazine actually
exists to deliver, and the one dimension the compliance gates are
structurally blind to.

It is scored at **Phase 9.5**, after the repair loop (so it scores the
artifact that actually ships) and before publish, by a **dedicated scorer
agent** — never the orchestrator that ran the pipeline and never the writer
that produced the prose (a producer grading its own work drifts generous).
The scorer reads only this rubric and the finished issue, applies the six
dimensions below, and emits one JSON object. **Scoring is observational, not
a gate** — it never blocks or reverts a publish (Phase 10's cardinal rule
still holds: always publish). It exists to accumulate the signal, not to add
another failure mode. The orchestrator passes that object to `log-quality.sh`,
which appends it to `state/quality-log.jsonl` and regenerates the public
`quality.html` page.

The point is not the number. The point is that the number **accumulates
next to `writer_model` and `scorer_model`**, so over a dozen issues the log
answers questions no single read can: did the stronger writer model
actually score higher, or did we just spend more? Which dimension is
chronically weakest — i.e. where should the *spec* change, not the model?
Which formats underperform?

---

## How to score

- Each dimension is **1–5**. Use the whole scale. A 3 is "fine, shipped,
  unremarkable" — most issues should land around there. Reserve 5 for "I'd
  point at this as the example of how the magazine should read," and 1 for
  "this is the failure the spec warns about."
- **`throughline` is scored only for sequential formats** (Deep Dive,
  Versus, Rewind, Season Review, Next). For parallel formats (weekly,
  Countdown, Field Guide, Shortlist, Starter Kit, Lookahead) record it as
  `null` and exclude it from the average.
- **`overall`** = the mean of the non-null dimension scores, rounded to one
  decimal place. (`log-quality.sh` computes this — the scorer does not need
  to.)
- The scorer **must** name the single `weakest` dimension and write a
  one-sentence `note` saying *what specifically* dragged, every time —
  even on a strong issue. A grader forced to find the weakest link can't
  hide behind "looks good." This is the field that makes the log
  actionable rather than decorative.

The anchors below are drawn from real shipped issues in the archive. They
are the calibration — if a sampled passage reads like the cited failure,
it scores at the failure's level.

---

## Dimension 1 — Voice (plain English)

Is the prose communicating, or performing a register? This is the same
question the Phase 7 plain-English gate asks, graded on a scale instead of
pass/fail.

- **5** — Plain. Direct subject-verb-object sentences, every sentence
  adding information, no rhetorical pose. Reads like someone who knows the
  subject explaining it clearly.
- **3** — Mostly clear with occasional performance: a stray "And yet…", a
  withheld-word ending, a triplet reached for rhythm.
- **1** — Performs throughout. *Anchor: the WWI Deep Dive (2026-05-26)*
  describes its own structure in the body ("This Deep Dive covers… in
  three roughly equal sections", "The chapters that follow will support
  this frame, complicate it, and push against it") — magazine essayism
  getting between the reader and the information. *Anchor: the Yellow
  Turban Deep Dive* performed academic seriousness (lit-review walls,
  scholar name-checks, throat-clearing). Either costume = 1–2.

## Dimension 2 — Information density

Does the reader learn things, or is the word count filler? The Signal's
promise is a substantive Sunday read, not a vibe.

- **5** — Dense with concrete, specific, verifiable facts — named people,
  dates, numbers, mechanisms — every paragraph carrying its weight.
  *Anchor: the WWI Deep Dive's* per-power dimensional treatment
  (constitutional structure, economy, doctrine, naval policy, each with
  hard numbers).
- **3** — Solid, informative, but padded in places — paragraphs that
  restate rather than advance.
- **1** — Thin. Atmosphere and adjectives standing in for content; the
  reader finishes knowing little they didn't.

## Dimension 3 — Structural variety

Do the sections/chapters vary in shape, or does the issue fall into a
single repeated pattern? Compliance gates already forbid two *consecutive*
identical component patterns; this grades the issue as a whole.

- **5** — Each section earns its own shape; the read has rhythm and
  contrast.
- **3** — Competent but somewhat templated — *anchor: the WWI Deep Dive's*
  per-power chapters all march through the same dimension order, which
  reads systematic but flattens after the third repetition.
- **1** — One pattern, copy-pasted. *Anchor: the 24 May 2026 weekly* leaked
  special-edition `.sp-*` components into a weekly and routed front-matter
  around the gates — structural incoherence the reader can feel.

## Dimension 4 — Opening quality

Do chapters open with a real hook, or with the date-place-person vignette
formula the spec caps at two per issue?

- **5** — Openings that state the stakes or land a genuine hook. *Anchor:
  "Europe in 1914 was not sleepwalking. It had built the machinery of
  catastrophe over forty years and then, in thirty-eight days, switched it
  on."* / *"Two estates. Seven nights. One fork."*
- **3** — Functional openings, one or two leaning on the vignette template.
- **1** — Formula mannerism: most chapters open "On [date] in [place],
  [person] [did concrete thing]" as a structural recipe.

## Dimension 5 — Throughline *(sequential formats only)*

Does each chapter build on the last toward a single argument, or is it a
pile of independent sections under one cover?

- **5** — A clear spine; each chapter advances or tests a named thesis.
  *Anchor: the WWI Deep Dive* carries its "interlocking commitments +
  rigid mobilisation timetables" frame through every chapter and explicitly
  pressure-tests it.
- **3** — A loose connection; chapters relate to the topic but don't build.
- **1** — Disconnected; reordering the chapters would change nothing.
- **`null`** — parallel format; not applicable.

## Dimension 6 — Novelty *(v8.27)*

Did the issue tell the reader things he *didn't already know*, or did it
recap what he'd already seen? This is the dimension the v8.27 reset exists
to move — the magazine's core promise is "catch what he missed", and the
audit found ~35-45% of a typical issue was recap of the already-known. It
applies to every format; score it for the issue as a whole, weighted toward
the Leads and the Catch-Up roundups.

- **5** — Almost everything is missable: Leads that moved this week and add
  an angle beyond the headline; Catch-Up roundups full of developments the
  reader would otherwise have to trawl for; genuine discovery. Nothing reads
  as "I already knew that."
- **3** — A mix: some genuinely new, some recap of headlines the reader
  almost certainly saw. The odd holding-pattern Lead.
- **1** — Mostly recap. *Anchor: the Starmer ×3 run (17-31 May 2026)* — a
  leadership holding pattern led the World section three weeks running, each
  re-telling what the reader already knew; *Anchor:* a Pixel & Byte that led
  on a months-old rumour and namedropped three releases without saying what
  they were. The reader finishes knowing nothing he didn't on Saturday.

The scorer names `novelty` in `weakest`/`note` when it's the drag, the same
as any other dimension. This is observational — it never gates a publish.

---

## The JSON the scorer emits

```json
{
  "issue_id": "deep-dive-2026-05-26",
  "issue_file": "signal_deep-dive_2026-05-26.html",
  "title": "World War One",
  "format": "deep_dive",
  "date": "2026-05-26",
  "writer_model": "opus",
  "scorer_model": "claude-opus-4-8[1m]",
  "scores": { "voice": 3, "density": 5, "structure": 3, "opening": 4, "throughline": 4, "novelty": 3 },
  "weakest": "voice",
  "note": "Dimensional rigour is the strength; the Argument chapter performs the essay by narrating its own structure."
}
```

`log-quality.sh` injects `ts`, computes `overall` from `scores`, and
appends. The scorer never writes `ts` or `overall`.

## The honest caveats (read these)

1. **A separate scorer ≠ an unbiased scorer.** Using a sibling model
   removes the producer's stake, not all bias. Treat the log as a *trend*
   instrument, not a verdict on any single issue.
2. **The scorer model is part of the instrument.** A score shift can be the
   magazine changing or the grader changing — that's why `scorer_model` is
   stamped on every row. When you change scorer models, expect a
   recalibration discontinuity.
3. **Human anchor, monthly.** Roughly once a month the *reader* should score
   one issue blind on this rubric, logged with `scorer_model: "human"`. If
   the human and model scores for the same issue diverge sharply, the
   anchors here need retuning. This ~10-minute check is the only thing that
   keeps the measure honest long-term — without it the instrument can drift
   undetectably, which is the exact failure this rubric exists to prevent.
