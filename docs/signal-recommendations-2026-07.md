# The Signal — Improvement Recommendations (with reader impact)

_July 2026. A functionality- and UX-focused review of the three streams — the daily Brief, the weekly magazine, and special editions — with tiered recommendations. Each item lists both **what** changes and **what it means for you as the reader**. Weekly-as-anchor is the organising priority._

> Produced from a five-track investigation (daily engine, weekly editorial, specials, cross-cutting UX, and external research into comparable products). Investigation-only: no product code was changed to produce this.

---

## Executive read

The Signal is a sophisticated product. The daily Brief's mechanical triage engine is well-built; the weekly's prose floor is high and its fact density real; the Deep Dive, when it lands, is the best reader experience in the product. These recommendations are about the gap between "competent and handsome" and "the thing you look forward to."

Four findings cut across all three streams:

1. **It's really two streams, not three — and `manifest.json` already says so** ("The Brief, daily — and The Read, a Sunday-morning magazine"). Specials sit _under_ The Read. Framing it as **one living daily wrapped around a Sunday anchor, with specials as rare interruptions** clarifies the whole roadmap.
2. **The system optimises for compliance, not quality.** ~8 gate scripts, a 1,684-line spec patched v8.13→v8.34, ~20 subagent calls/issue with zero retries — which "proves compliance, not quality." The one quality instrument (the Phase 9.5 scorer) has named **`voice` as weakest for five straight issues** and nothing acts on it.
3. **The daily→weekly bridge is asserted everywhere but no bytes flow.** The weekly's "already-informed reader" identity rests on the daily's `story_log`, which nothing outside the daily pipeline can read. Closing this is the highest-leverage structural move.
4. **Real defects ship past the gates:** the daily's only push is dead code; cadence is triple-confused (10-min cron vs "3h" docs vs an advisory knob nothing reads); the 21 Jun weekly shipped "13 words · 13 sections · 13 links · 13 images."

**The through-line for you as a reader:** today the product is competent but a little dutiful and impersonal — you read it because it's thorough. These changes aim to make it personal, opinionated, and continuous: something with a voice that remembers your week, tells you what it _added up to_, and lands at the same time every Sunday as a thing you look forward to.

---

## The one big move

**Turn the weekly's Foreword into a genuine editor's letter with a point of view — and make it the magazine's "one big thing."**

The weekly's claim to being the anchor is that it can step back and _have a view_. Right now no section does that in a human voice: the Foreword is an authorless news summary, and the real synthesis is buried inside the World section behind an "Angle" box. A first-person, opinionated letter — using the existing "borrowed angles, our voice" rule so the stance is sourced, not invented — naming the one thing worth this reader's Sunday and why it mattered _to his world_.

**For you as the reader:** instead of opening to an anonymous news-desk summary, you open to "here's what I made of this week, and the one thing worth your time." It's the difference between reading a supplement and hearing from someone — and it's the reason to look forward to Sunday. Cheap to build (one chapter), the direct fix for the chronic weakest dimension (voice), and the one thing the daily can _structurally never_ provide.

---

## Holistic / cross-cutting

### Tier 1 — do first
- **H1. Build the daily→weekly data bridge.** A `GET /api/daily/digest?since=7d` endpoint reading `story_log`/`items` from D1 — what surfaced and _moved_ this week. _For you:_ invisible directly, but it's what makes every "your week" feature possible; the weekly stops re-telling you things you read on Tuesday and starts genuinely knowing what your week looked like.
- **H2. Wire the quality scorer to an action.** When the last N issues share a weakest dimension, the repair brief targets that tic. _For you:_ a critic already sits beside your magazine each week noting "the voice is flat again" and is ignored; wired up, that flatness gets fixed _before_ the issue reaches you.
- **H3. Promote the weekly to the front door.** A persistent "This Sunday · The Read" hero _above_ the tabs; daily + specials become feeds underneath. _For you:_ you open the app and the Sunday magazine is the first thing you see, not the disposable feed with your flagship hidden behind a tab.
- **H4. De-jolt the seam.** Honour `prefers-color-scheme` on the home so the shell is continuous with the warm-paper issues. _For you:_ moving into an issue stops being a jarring dark→bright flash every time; the product feels like one thing.

### Tier 2 — investment
- **H5. Save-for-later as the human bridge.** A star/save affordance on daily items (localStorage first). _For you:_ you can keep anything from the brief instead of losing it in the feed — and your saves become the raw material for Sunday, so the weekly reflects what _you_ found interesting.
- **H6. Reciprocal cross-stream links.** Brief → "This Sunday's Read" card; weekly → "Following up on the week's threads." _For you:_ the two streams stop feeling like separate bookmarks and become one story at two speeds.
- **H7. Split Settings into "Reader" and "Engine."** _For you:_ you get real reading controls (text size, theme, notification cadence) instead of an engineer's panel full of knobs like "undated-penalty" that mean nothing to you.
- **H8. Auto-generate the archive from a manifest.** _For you:_ past issues become browsable and searchable with correct counts, so you can actually re-find that deep dive from May.

### Tier 3 — polish
- **H9. "New since your last visit"** across all three streams. _For you:_ at a glance you see what changed, no re-reading.
- **H10. Reader typography controls** (size, width, sepia/dark) in issues. _For you:_ the long Sunday read is comfortable for your eyes and device.
- **H11. Estimated read time** per feature and issue. _For you:_ "I've got 20 minutes — which piece fits?" instead of committing blind.
- **H12. Protect the Sunday slot** (same time, same voice). _For you:_ the issue becomes a fixed, reliable part of Sunday morning — a ritual.

---

## Stream 1 — The Weekly (the anchor; highest priority)

**Diagnosis.** The v8.34 "synthesis for an already-informed reader" concept _is landing_ — but only in the World section. The other sections still do beautifully-written catch-up (the daily's job). Compounding it: a pervasive house **voice tic** the gates can't catch (aphoristic section-closers; the "Angle" box reprinted as a pull-quote); lost **personality** since the v8.27 generic-bucket rename (branded sections and the actionable service layer both gone); and **no person in the personal magazine** — no editor's voice, no continuity, no signature feature.

### Tier 1 — do first
- **W1. The editor's letter.** _(The one big move.)_ _For you:_ a voice and a point of view to open on — the reason to look forward to Sunday.
- **W2. Propagate synthesis beyond World — or let sections yield.** Enforce ≥3 sections carrying a cross-week "named layer"; make "yield rather than fill" bite. Target **8–9 sections, not 12–13** (~630KB now vs good-era ~160KB). _For you:_ every section you read earns its place by giving you the "so what," and the issue is shorter and denser — you finish feeling you gained something, not that you did homework.
- **W3. Kill the voice tic with a targeted gate.** Replace the random-3-paragraph spot check with a document-level scan for the two actual tics. _For you:_ the prose gets out of its own way — less "written," more _said_; you stop noticing the verbal habits.
- **W4. Stop leaking the machinery into prose.** Lines like "The daily brief carried the fireworks" violate the spec's own invisibility rule. _For you:_ synthesis is shown, not narrated; it feels effortless rather than explained.

### Tier 2 — investment
- **W5. Week-to-week continuity.** A "last week / this week" callback and a numbered running-story tracker for the dominant arc. _For you:_ the magazine remembers — you feel inside an ongoing narrative rather than reading 52 disconnected one-offs. The biggest driver of not-wanting-to-miss-an-issue.
- **W6. Restore the service layer and section character.** One actionable "one thing to do" beat per issue; reconsider the generic bucket names. _For you:_ useful, actionable things return, and the magazine feels hand-made _for you_ again, not assembled from a template.
- **W7. Consume the daily bridge (depends on H1/H5).** Surface saved/flagged items and tracked threads inside the weekly. _For you:_ the weekly becomes visibly _yours_ — "you flagged this; here's the one worth your Sunday."
- **W8. Fix the on-ramp.** Collapse the Navigator/Long Shelf overlap. _For you:_ you reach real content faster instead of wading through three contents-like blocks (two listing the same stories) before a single piece.

### Tier 3 — polish
- **W9. Real "Issue in Numbers" validation.** _For you:_ no more embarrassing glitches like "13/13/13/13" that undermine trust.
- **W10. A signature recurring feature** only The Signal has (e.g. a weekly "Connection" linking two unrelated stories). _For you:_ one distinctive thing you actively return for.
- **W11. Measure weekly coherence** (a `throughline` analogue for parallel formats). _For you:_ the magazine gets held to reading like one Sunday read, not 12 unrelated tabs.

---

## Stream 2 — The Brief (daily)

**Diagnosis.** The mechanical engine is the value and it's honestly good: profile-relevance + source-significance × recency × register, a _capped_ named-entity floor, content-led signal tiers ("done deal" beats "linked with"), demote-never-drop fairness caps, disciplined degradation, and the clean "N new since HH:MM" watermark. Weaknesses are around the edges: real bugs, cadence confusion, a missing read-state loop, and AI-layer accretion.

### Tier 1 — do first
- **B1. Fix the dead significance push** (`notify.js` reads a `top_catches` field no longer emitted; point it at `state.top20`). _For you:_ your phone actually pings for genuinely big breaking stories again — right now it's silent because the notification is broken.
- **B2. Reconcile cadence** (honour `cadence_hours` or delete it and fix the docs). _For you:_ honesty about freshness, and a "how often" control that actually does something.
- **B3. Add per-item read state.** Dim/collapse opened cards. _For you:_ the pile visibly shrinks as you read — a satisfying "clear the deck" loop instead of the whole feed re-presented every visit. The biggest daily UX lever.
- **B4. Make "Start here" tappable and "Today & Tonight" config-driven.** _For you:_ the prominent "start here" items become real links (they're dead text now), and dated events beyond football/film/gaming — a golf tee-time, a gig, a LEGO drop — can finally appear.

### Tier 2 — investment
- **B5. Save-for-later** (= H5). _For you:_ your keep-shelf in the daily.
- **B6. The digest endpoint** (= H1). _For you:_ invisible, but it stops the weekly repeating your week.
- **B7. Consolidate the AI editorial layer** (`picks`/`top20` are near-identical; `headlines`/`top20`/`start_here` overlap). _For you:_ one clear "here's what matters" instead of four competing curated lists.
- **B8. Strengthen default cross-source dedup** (enable `smartMerge` or extend entity-merge beyond football; consider semantic clustering). _For you:_ you stop seeing the same story twice from two outlets.

### Tier 3 — polish
- **B9. Client-side search.** _For you:_ find that thing you saw this morning instead of scrolling for it.
- **B10. Daily cost/quality history log.** _For you:_ invisible — observability for tuning.
- **B11. Optional "morning edition" snapshot.** _For you:_ a defined "here's your morning" moment for reading on waking.
- **B12. Retire the Reddit rotation workaround** once the Data API is approved. _For you:_ more reliable community content, fewer gaps.
- **B13. Fix/note the RSS velocity blind spot** (constant `rawScore` makes velocity always 0 for RSS; add a cross-feed "burst" signal). _For you:_ a story breaking across many feeds at once is recognised as important — better ordering.

---

## Stream 3 — Special editions

**Diagnosis.** The most ambitious and most over-built part. When it lands it lands hard (the Byzantine Deep Dive is the best reader experience in the product). But: **3 of 11 formats have never shipped** (Rewind, Season Review, Lookahead); the recommendation cluster (Shortlist / Starter Kit / Next / Lookahead) is **one format wearing four hats**; the trigger machinery is elaborate but partly vestigial; and the visual system is enormous (two parallel design systems, nine bespoke "signature moments").

**Format verdicts:** Deep Dive **keep (flagship)** · Field Guide **keep** (watch length) · Countdown **keep** · Versus **keep** · Next **keep** · Rewind **keep but prove it** · Season Review **keep, conditional** · Starter Kit **keep, tighten** · Shortlist **merge** · Lookahead **cut/fold** · Blueprint already retired (the precedent).

### Tier 1 — do first
- **S1. Resolve the three ghost formats** (fire once in a window, or demote to dormant). _For you:_ you actually get a Rewind / Season Review when the moment's right (the promised half-year Rewind keeps getting deferred), or they stop being phantom promises.
- **S2. Cut or fold Lookahead into the weekly** (overlaps the enforced Release Radar). _For you:_ no loss — that content lives in the weekly anyway; one fewer redundant issue type competing for a Sunday.
- **S3. Enforce Gate 1A + fact-provenance on the light formats.** _For you:_ specials stop occasionally talking _at_ you in a creepy second person ("you dropped off season four") or citing suspiciously clean stats — more trustworthy.

### Tier 2 — investment
- **S4. Merge the recommendation cluster to two** (keep **Next**; fold **Shortlist + Starter Kit** into one "Guide" with beginner and category modes). _For you:_ today those four read almost the same; collapsing to two clearly-different things means each special feels distinct and worth the long-form treatment.
- **S5. Simplify the trigger stack** (collapse `deep_dive_schedule` into P1/P2/P3, or drop the never-fired P3). _For you:_ specials fire reliably at the right moments instead of getting deferred out of existence.
- **S6. Wire hard length ceilings into `validate-issue.py`.** _For you:_ specials stay a "Sunday with coffee" read (Field Guide ~14.6k and the retired WWI DD ~24k are too long) — you actually finish them.

### Tier 3 — polish
- **S7. Audit the nine signature moments + removed-components graveyard.** _For you:_ distinctive flourishes stay only where they're genuinely beautiful; cleaner, more intentional design.
- **S8. Reconcile the holiday motion layer** with the "paper-and-ink, JS-off renders complete" contract. _For you:_ the holiday specials get calmer and more paper-like — less animation fighting the reading.

**Positioning.** Net effect: **fewer special types, each one clearly an event.** When a special interrupts your Sunday it feels like an occasion worth the swap — a genuine deep dive or trip guide — and the picks-style content becomes a nice recurring box in the weekly.

---

## If you only do five things

1. **W1 / the one big move** — the weekly editor's letter.
2. **H1 + H5 (→ W7)** — the daily→weekly bridge (digest + save-for-later) so the weekly is downstream of your real week.
3. **W2 + W3** — propagate synthesis to ≥3 sections, let the rest yield, kill the voice tic.
4. **H3** — make the weekly the home's front door.
5. **B1 + B2** — fix the dead daily push and the cadence confusion (fast, real bugs).

## A note on process

The deepest issue is cross-cutting: the machine now spends most of its energy proving it didn't break and almost none proving it's good. The eight gate scripts, the six-layer image chain, the ~20-call zero-retry pipeline are armour against regressions already solved. The next phase should rebalance toward the one signal that measures the product's reason to exist — following the anti-accretion rule the spec already believes in: **sharpen and connect the instruments you have (the scorer, the plain-English gate, the yield rule) rather than adding new ones.**
