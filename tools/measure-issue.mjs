#!/usr/bin/env node
/**
 * measure-issue.mjs — WP-0 measurement tool for The Signal design-system
 * unification (spec: docs/design-system-unification-SPEC-2026-07-18.md).
 *
 * Usage: node tools/measure-issue.mjs <issue-path-or-url> --out <dir>
 *
 * Renders the issue at 1440x900 and 390x844 (served over HTTP, service
 * worker neutralized, cross-origin requests aborted), performs a stepwise
 * smooth-scroll pass so reveal-on-scroll content fires, then writes
 * <out>/metrics.json with, per viewport:
 *   - body-copy word count (visible text minus chrome/captions/credits)
 *   - designed-visual-event census (Law-2 closed list; [data-mx-event]
 *     markers preferred, DOM selector heuristics otherwise), with every
 *     counted event's selector, y-position and label for audit
 *   - events/screen, words/screen, distribution (longest zero-event run)
 *   - chrome-overlap detection at 10 scroll depths
 *   - document-level horizontal-scroll flag
 *   - table truncation without wrap/scroll affordance
 *   - motion census (animations/transitions that actually fired during the
 *     scroll pass) + a prefers-reduced-motion pass
 *
 * See tools/README-measure.md for the selector map rationale and limits.
 */

import fs from 'node:fs';
import path from 'node:path';
import {
  loadPlaywright, launchBrowser, resolveTarget, prepareContext, openPage,
  smoothScrollPass, parseArgs, CHROME_SELECTOR, DESCRIBE_FN,
} from './lib/mx-harness.mjs';

const USAGE = 'Usage: node tools/measure-issue.mjs <issue-path-or-url> --out <dir>';

const VIEWPORTS = [
  { key: '1440x900', width: 1440, height: 900 },
  { key: '390x844', width: 390, height: 844 },
];

/* ------------------------------------------------------------------ *
 * Law-2 closed-list event census — selector map (heuristic mode).
 * Calibrated against issues/signal_countdown_2026-06-14.html,
 * issues/signal_field-guide_2026-05-17.html and
 * docs/mockups/unification-furniture-kit-mockup.html.
 * Outermost candidate wins: a candidate nested inside another counted
 * candidate is skipped (a polaroid inside a counted composite is one
 * event, not two). Chrome subtree candidates are skipped.
 * ------------------------------------------------------------------ */
const EVENT_SELECTOR_MAP = [
  // composite captioned-figure objects (photo + caption/meta as one design)
  { type: 'figure', sel: '.hol-wonder, .hol-anchor, .hol-unmissable, .pick, figure' },
  // ephemera objects
  { type: 'ephemera', sel: '.hol-polaroid, .hol-postcard, .hol-ticket, .ticket, .mx-ticket, .hol-stamp, .kit-stamp, .mx-stamp, .hol-coaster, .kit-card, .mx-card' },
  // ledger / table blocks (ranked entries with facts rows count singly)
  { type: 'ledger', sel: '.hol-chalkboard, .hol-meal-slot__entry, .kit-ledger, .mx-ledger, .fixtures, .standings, .scorecard, .memory-test, .mtest, table' },
  // stat bands
  { type: 'statband', sel: '.hol-trip-numbers, .kit-stats, .mx-numbers, .stat-band, .hol-countdown, .hol-tminus, .vs-scoreboard' },
  // quote-objects (validated below: must carry a named source)
  { type: 'quote', sel: '.hol-pull, .hol-pull--big, .kit-quote, .mx-quote, blockquote, .sp-pullquote-huge' },
  // numbered plates / act & chapter openers
  { type: 'plate', sel: '.mx-plate, .kit-plate, .hol-half__opener, .hol-kicker-strip, .sp-chapter-gate, .chapter-head, .hol-opening' },
  // self-made charts / diagrams / maps (size-gated below to skip icons)
  { type: 'chart', sel: 'svg, canvas, .dial' },
  // marquees / act dividers / transit bands
  { type: 'marquee', sel: '.hol-marquee, .hol-transit, .mx-transit' },
  // cheat sheets and on-ramp style summary furniture
  { type: 'cheatsheet', sel: '.cheat-sheet, .mx-cheat, .kit-cheat, .hol-dont-miss, .keep-digging, .on-ramp, .week-plan' },
];

/** Selectors excluded from the body-copy word count (chrome handled via
 *  CHROME_SELECTOR; these are captions/credits per Law 3). */
const CAPTION_SELECTOR = 'figcaption, [class*="caption"], [class*="credit"], [class*="__cite"]';

/* ------------------------------------------------------------------ *
 * In-page measurement functions (evaluated as strings so they can share
 * the DESCRIBE_FN helper).
 * ------------------------------------------------------------------ */

const WORD_COUNT_FN = `(args) => {
  const { chromeSelector, captionSelector } = args;
  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'TITLE', 'HEAD', 'IFRAME', 'SVG']);
  const visCache = new Map();
  const isVisible = (el) => {
    if (visCache.has(el)) return visCache.get(el);
    let v;
    try {
      v = el.checkVisibility
        ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })
        : (el.getClientRects().length > 0);
    } catch (e) { v = el.getClientRects().length > 0; }
    visCache.set(el, v);
    return v;
  };
  let words = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const text = node.textContent;
    if (!text || !text.trim()) continue;
    const p = node.parentElement;
    if (!p) continue;
    if (SKIP_TAGS.has(p.tagName)) continue;
    if (p.closest('svg')) continue;
    if (chromeSelector && p.closest(chromeSelector)) continue;
    if (captionSelector && p.closest(captionSelector)) continue;
    if (p.closest('[aria-hidden="true"]')) continue;
    if (!isVisible(p)) continue;
    words += text.trim().split(/\\s+/).length;
  }
  return words;
}`;

const EVENT_CENSUS_FN = `(args) => {
  const { selectorMap, chromeSelector } = args;
  const describe = ${DESCRIBE_FN};
  const scrollY = window.scrollY;
  const isVisible = (el) => {
    try {
      if (el.checkVisibility && !el.checkVisibility({ checkOpacity: false, checkVisibilityCSS: true })) return false;
    } catch (e) { /* fall through */ }
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const labelOf = (el) => {
    const aria = el.getAttribute('aria-label') || el.getAttribute('alt');
    if (aria) return aria.slice(0, 70);
    const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
    if (t) return t.slice(0, 70);
    if (el.tagName === 'IMG') return (el.getAttribute('src') || 'img').slice(-70);
    return el.className && typeof el.className === 'string' ? el.className.slice(0, 70) : el.tagName.toLowerCase();
  };

  // MODE 1 — explicit markers from the future system
  const marked = Array.from(document.querySelectorAll('[data-mx-event]'));
  let candidates = [];
  let mode;
  if (marked.length > 0) {
    mode = 'data-mx-event';
    for (const el of marked) {
      if (chromeSelector && el.closest(chromeSelector) && !el.matches(chromeSelector)) continue;
      candidates.push({ el, type: el.getAttribute('data-mx-event') || 'marked', sel: '[data-mx-event]' });
    }
  } else {
    // MODE 2 — heuristic closed-list selectors
    mode = 'heuristic';
    const assigned = new Map(); // el -> {type, sel} (first matching map entry wins)
    for (const entry of selectorMap) {
      let els = [];
      try { els = Array.from(document.querySelectorAll(entry.sel)); } catch (e) { continue; }
      for (const el of els) {
        if (!assigned.has(el)) assigned.set(el, { type: entry.type, sel: entry.sel });
      }
    }
    // standalone content images count as figures
    for (const img of Array.from(document.querySelectorAll('img'))) {
      if (!assigned.has(img)) assigned.set(img, { type: 'figure', sel: 'img' });
    }
    candidates = Array.from(assigned.entries()).map(([el, a]) => ({ el, type: a.type, sel: a.sel }));
  }

  // document order so ancestors are processed before descendants
  candidates.sort((a, b) =>
    (a.el.compareDocumentPosition(b.el) & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1);

  const counted = new Set();
  const events = [];
  for (const c of candidates) {
    const el = c.el;
    if (chromeSelector && el.closest(chromeSelector)) continue;
    if (!isVisible(el)) continue;
    // outermost-wins dedupe
    let anc = el.parentElement, insideCounted = false;
    while (anc) { if (counted.has(anc)) { insideCounted = true; break; } anc = anc.parentElement; }
    if (insideCounted) continue;
    const r = el.getBoundingClientRect();
    if (mode === 'heuristic') {
      // size gates: skip icons/fasteners too small to be a designed event
      if (c.type === 'chart') { if (r.width < 200 || r.height < 120) continue; }
      else if (el.tagName === 'IMG') { if (r.width < 120 || r.height < 90) continue; }
      else if (r.width < 48 || r.height < 28) continue;
      // a quote-object only counts with a named source (Law 2 wording)
      if (c.type === 'quote') {
        const src = el.querySelector('cite, [class*="cite"], [class*="source"], [class*="attribution"]');
        if (!src || !(src.textContent || '').trim()) continue;
      }
      // plain layout tables with no rows of content are not events
      if (el.tagName === 'TABLE' && el.querySelectorAll('tr').length < 2) continue;
    }
    counted.add(el);
    events.push({
      type: c.type,
      selector: describe(el),
      matchedBy: c.sel,
      label: labelOf(el),
      y: Math.round(r.top + scrollY),
      h: Math.round(r.height),
    });
  }
  events.sort((a, b) => a.y - b.y);
  return { mode, events };
}`;

const HSCROLL_FN = `() => {
  const de = document.documentElement;
  const body = document.body;
  const se = document.scrollingElement || de;
  const scrollWidth = Math.max(de.scrollWidth, body ? body.scrollWidth : 0);
  const clientWidth = de.clientWidth;
  const geometricOverflow = scrollWidth > clientWidth + 1;
  // Law 10 cares about h-scroll a READER experiences. Tilted/bleeding
  // ephemera behind an overflow-x:hidden/clip root overflow geometrically
  // but the document cannot actually be scrolled sideways. Test it: attempt
  // a horizontal scroll and read back, and respect overflow-x on html/body.
  const rootOverflowX = getComputedStyle(de).overflowX;
  const bodyOverflowX = body ? getComputedStyle(body).overflowX : 'visible';
  const overflowXSuppressed = ['hidden', 'clip'].includes(rootOverflowX) ||
    ['hidden', 'clip'].includes(bodyOverflowX);
  const prev = se.scrollLeft;
  se.scrollLeft = 50;
  const scrollLeftAfterAttempt = se.scrollLeft;
  se.scrollLeft = prev;
  const flag = geometricOverflow && scrollLeftAfterAttempt > 0 && !overflowXSuppressed;
  // max visual right edge of laid-out elements (informational: transforms
  // and marquee tracks can exceed the viewport legitimately)
  let maxRight = 0;
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && r.right > maxRight) maxRight = r.right;
  }
  return {
    docScrollWidth: scrollWidth,
    clientWidth,
    geometricOverflow,
    scrollLeftAfterAttempt,
    overflowXSuppressed,
    flag,
    maxContentRightPx: Math.round(maxRight),
  };
}`;

const TRUNCATION_FN = `(args) => {
  const { chromeSelector } = args;
  const describe = ${DESCRIBE_FN};
  const flags = [];
  // Law 10: scroll-wrap only passes with a VISIBLE affordance. A container
  // with overflow-x:auto but no rendered horizontal scrollbar (overlay
  // scrollbars / scrollbar hidden) still cuts the table mid-word at rest.
  const rendersHScrollbar = (el) => {
    const s = getComputedStyle(el);
    const borders = (parseFloat(s.borderTopWidth) || 0) + (parseFloat(s.borderBottomWidth) || 0);
    return (el.offsetHeight - el.clientHeight - borders) >= 6;
  };
  const scrollWrapAncestor = (el) => {
    let a = el;
    while (a && a !== document.body) {
      const s = getComputedStyle(a);
      if ((s.overflowX === 'auto' || s.overflowX === 'scroll') && a.scrollWidth > a.clientWidth + 2) return a;
      a = a.parentElement;
    }
    return null;
  };
  const hasScrollAffordance = (el) => {
    const a = scrollWrapAncestor(el);
    return !!(a && rendersHScrollbar(a));
  };
  const clippingAncestor = (el) => {
    let a = el.parentElement;
    while (a && a !== document.documentElement) {
      const s = getComputedStyle(a);
      if (['hidden', 'clip', 'auto', 'scroll'].includes(s.overflowX)) return { el: a, mode: s.overflowX };
      a = a.parentElement;
    }
    const rs = getComputedStyle(document.documentElement);
    if (['hidden', 'clip'].includes(rs.overflowX)) return { el: document.documentElement, mode: rs.overflowX };
    return null;
  };
  const targets = document.querySelectorAll('table, th, td, .cheat-sheet');
  const flaggedTables = new Set();
  for (const el of targets) {
    if (chromeSelector && el.closest(chromeSelector)) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // avoid re-flagging every cell of an already-flagged table
    const owningTable = el.tagName === 'TH' || el.tagName === 'TD' ? el.closest('table') : null;
    if (owningTable && flaggedTables.has(owningTable)) continue;
    // case 1: content wider than the element's own box (clipped in place)
    if (el.scrollWidth > el.clientWidth + 2) {
      const s = getComputedStyle(el);
      if (s.overflowX !== 'auto' && s.overflowX !== 'scroll' && !hasScrollAffordance(el)) {
        flags.push({
          kind: 'clipped-in-place', selector: describe(el),
          scrollWidth: el.scrollWidth, clientWidth: el.clientWidth,
          cutPx: el.scrollWidth - el.clientWidth,
          text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 60),
        });
        if (el.tagName === 'TABLE') flaggedTables.add(el);
      }
    }
    // case 2 (tables only): the table lives in an overflow-x:auto/scroll
    // wrapper that is cut at rest but renders NO horizontal scrollbar —
    // visually identical to a hard clip (Law 10: affordance must be visible)
    if (el.tagName === 'TABLE' || el.classList.contains('cheat-sheet')) {
      const wrap = scrollWrapAncestor(el);
      if (wrap && !rendersHScrollbar(wrap)) {
        const nowrapCells = el.querySelectorAll ? Array.from(el.querySelectorAll('td, th'))
          .filter((c) => getComputedStyle(c).whiteSpace === 'nowrap').length : 0;
        flags.push({
          kind: 'scroll-wrap-no-visible-affordance', selector: describe(el),
          wrapper: describe(wrap),
          wrapperScrollWidth: wrap.scrollWidth, wrapperClientWidth: wrap.clientWidth,
          cutPx: wrap.scrollWidth - wrap.clientWidth,
          nowrapCells,
          text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 60),
        });
        if (el.tagName === 'TABLE') flaggedTables.add(el);
      }
    }
    // case 3 (tables only): the element itself sticks out past a clipping
    // ancestor (e.g. html { overflow-x: clip }) with no scroll affordance
    if (el.tagName === 'TABLE') {
      const clip = clippingAncestor(el);
      if (clip && (clip.mode === 'hidden' || clip.mode === 'clip') && !hasScrollAffordance(el)) {
        const cr = clip.el === document.documentElement
          ? { right: document.documentElement.clientWidth }
          : clip.el.getBoundingClientRect();
        if (r.right > cr.right + 2) {
          flags.push({
            kind: 'clipped-by-ancestor', selector: describe(el),
            ancestor: describe(clip.el === document.documentElement ? document.body : clip.el),
            elementRight: Math.round(r.right), clipRight: Math.round(cr.right),
            cutPx: Math.round(r.right - cr.right),
          });
          if (el.tagName === 'TABLE') flaggedTables.add(el);
        }
      }
    }
  }
  return { flags, fails: flags.length > 0 };
}`;

/** Full overlap sampling loop runs in-page (scrolls itself between samples). */
const OVERLAP_FN = `async (args) => {
  const { depths, waitMs, minOverlapPx } = args;
  const describe = ${DESCRIBE_FN};
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  // fixed/sticky discovery (position value does not change with scroll)
  const fixedEls = [];
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (s.position === 'fixed' || s.position === 'sticky') {
      fixedEls.push({ el, position: s.position });
    }
  }
  const contentSel = 'p, h1, h2, h3, h4, h5, h6, li, dt, dd, blockquote, td, th, img, figure';
  const vw = window.innerWidth, vh = window.innerHeight;
  const pairs = new Map();
  let totalIntersections = 0;
  // Decorative full-viewport texture layers (grain/scene grounds): fixed,
  // pointer-events none, covering ~the whole viewport. They are scenography,
  // not chrome — excluded from overlap pairs but recorded for audit.
  const fullViewportOverlays = [];
  const isDecorativeOverlay = (el, s, fr) => {
    if (s.pointerEvents !== 'none') return false;
    return fr.width >= vw * 0.85 && fr.height >= vh * 0.85;
  };
  for (const depth of depths) {
    window.scrollTo(0, depth);
    await sleep(waitMs);
    for (const f of fixedEls) {
      const s = getComputedStyle(f.el);
      if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.05) continue;
      const fr = f.el.getBoundingClientRect();
      if (fr.width < minOverlapPx || fr.height < minOverlapPx) continue;
      if (isDecorativeOverlay(f.el, s, fr)) {
        const d = describe(f.el);
        if (!fullViewportOverlays.includes(d)) fullViewportOverlays.push(d);
        continue;
      }
      if (fr.bottom < 0 || fr.top > vh || fr.right < 0 || fr.left > vw) continue;
      for (const c of document.querySelectorAll(contentSel)) {
        if (c === f.el || f.el.contains(c) || c.contains(f.el)) continue;
        // a fixed el overlapping another piece of chrome is not a content overlap
        const cr = c.getBoundingClientRect();
        if (cr.width === 0 || cr.height === 0) continue;
        if (cr.bottom < 0 || cr.top > vh) continue;
        if (!(c.textContent || '').trim() && c.tagName !== 'IMG' && c.tagName !== 'FIGURE') continue;
        const ow = Math.min(fr.right, cr.right) - Math.max(fr.left, cr.left);
        const oh = Math.min(fr.bottom, cr.bottom) - Math.max(fr.top, cr.top);
        if (ow >= minOverlapPx && oh >= minOverlapPx) {
          totalIntersections++;
          const key = describe(f.el) + ' :: ' + describe(c);
          if (!pairs.has(key)) {
            pairs.set(key, {
              fixed: describe(f.el), position: f.position, content: describe(c),
              firstDepth: depth, depthsSeen: 0,
              overlap: { w: Math.round(ow), h: Math.round(oh) },
              contentText: (c.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 60),
            });
          }
          pairs.get(key).depthsSeen++;
        }
      }
    }
  }
  const overlaps = Array.from(pairs.values()).slice(0, 100);
  return {
    fixedOrStickyElements: fixedEls.length,
    depthsSampled: depths.length,
    totalIntersections,
    uniquePairs: pairs.size,
    fails: pairs.size > 0,
    decorativeFullViewportOverlaysExcluded: fullViewportOverlays,
    overlaps,
  };
}`;

/* ------------------------------------------------------------------ */

function distribution(events, pageHeight, vh) {
  const screens = Math.max(1, Math.ceil(pageHeight / vh));
  const hasEvent = new Array(screens).fill(false);
  for (const ev of events) {
    const first = Math.max(0, Math.floor(ev.y / vh));
    const last = Math.min(screens - 1, Math.floor((ev.y + Math.max(1, ev.h) - 1) / vh));
    for (let i = first; i <= last && i < screens; i++) hasEvent[i] = true;
  }
  let longest = 0, run = 0;
  const emptyScreens = [];
  for (let i = 0; i < screens; i++) {
    if (!hasEvent[i]) { run++; emptyScreens.push(i); if (run > longest) longest = run; }
    else run = 0;
  }
  return {
    screensTotal: screens,
    emptyScreens,
    longestZeroEventRun: longest,
    law2DistributionFail: longest >= 3,
  };
}

async function measureViewport(browser, target, vp) {
  const context = await prepareContext(browser, {
    width: vp.width, height: vp.height, origin: target.origin,
  });
  const page = await openPage(context, target.url);
  const pass = await smoothScrollPass(page, { collectMotion: true });
  const pageHeight = pass.pageHeight;
  const screens = pageHeight / vp.height;

  const words = await page.evaluate(`(${WORD_COUNT_FN})(${JSON.stringify({
    chromeSelector: CHROME_SELECTOR, captionSelector: CAPTION_SELECTOR })})`);

  const census = await page.evaluate(`(${EVENT_CENSUS_FN})(${JSON.stringify({
    selectorMap: EVENT_SELECTOR_MAP, chromeSelector: CHROME_SELECTOR })})`);

  const hscroll = await page.evaluate(`(${HSCROLL_FN})()`);
  const truncation = await page.evaluate(`(${TRUNCATION_FN})(${JSON.stringify({
    chromeSelector: CHROME_SELECTOR })})`);

  // chrome overlap at 10 evenly spaced depths (>= 8 required by spec)
  const maxScroll = Math.max(0, pageHeight - vp.height);
  const depths = Array.from({ length: 10 }, (_, i) => Math.round((maxScroll * i) / 9));
  const overlap = await page.evaluate(`(${OVERLAP_FN})(${JSON.stringify({
    depths, waitMs: 250, minOverlapPx: 12 })})`);

  await context.close();

  const byType = {};
  for (const ev of census.events) byType[ev.type] = (byType[ev.type] || 0) + 1;

  return {
    viewport: { width: vp.width, height: vp.height },
    pageHeight,
    screens: round2(screens),
    words: {
      bodyCopy: words,
      perScreen: round2(words / screens),
    },
    events: {
      mode: census.mode,
      count: census.events.length,
      perScreen: round2(census.events.length / screens),
      byType,
      list: census.events,
    },
    distribution: distribution(census.events, pageHeight, vp.height),
    chromeOverlap: overlap,
    horizontalScroll: hscroll,
    tableTruncation: truncation,
    motion: {
      animatedElements: pass.motionElements ? pass.motionElements.count : 0,
      note: 'elements with animations/transitions (duration>0) observed firing during the scroll pass; chrome excluded',
      sampled: pass.motionElements ? pass.motionElements.sampled : [],
    },
  };
}

async function measureReducedMotion(browser, target, vp) {
  const context = await prepareContext(browser, {
    width: vp.width, height: vp.height, origin: target.origin, reducedMotion: true,
  });
  const page = await openPage(context, target.url);
  const pass = await smoothScrollPass(page, { collectMotion: true });
  await context.close();
  return {
    animatedElements: pass.motionElements ? pass.motionElements.count : 0,
    sampled: pass.motionElements ? pass.motionElements.sampled : [],
  };
}

function round2(n) { return Math.round(n * 100) / 100; }

async function main() {
  const args = parseArgs(process.argv.slice(2), USAGE);
  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  const pw = loadPlaywright();
  const target = await resolveTarget(args._[0]);
  const browser = await launchBrowser(pw);

  const metrics = {
    tool: 'tools/measure-issue.mjs',
    source: args._[0],
    url: target.url,
    generatedAt: new Date().toISOString(),
    viewports: {},
    reducedMotion: {},
  };

  try {
    for (const vp of VIEWPORTS) {
      console.log(`[measure] ${vp.key} main pass…`);
      metrics.viewports[vp.key] = await measureViewport(browser, target, vp);
      console.log(`[measure] ${vp.key} reduced-motion pass…`);
      metrics.reducedMotion[vp.key] = await measureReducedMotion(browser, target, vp);
    }
  } finally {
    await browser.close();
    await target.close();
  }

  const outFile = path.join(outDir, 'metrics.json');
  fs.writeFileSync(outFile, JSON.stringify(metrics, null, 2));
  console.log(`[measure] wrote ${outFile}`);

  for (const [key, m] of Object.entries(metrics.viewports)) {
    console.log(
      `  ${key}: ${m.words.bodyCopy} words · ${m.events.count} events (${m.events.mode}) · ` +
      `${m.events.perScreen} ev/screen over ${m.screens} screens · ` +
      `longest zero-run ${m.distribution.longestZeroEventRun} · ` +
      `overlap pairs ${m.chromeOverlap.uniquePairs} · ` +
      `hscroll ${m.horizontalScroll.flag} · truncation flags ${m.tableTruncation.flags.length} · ` +
      `motion ${m.motion.animatedElements} (reduced: ${metrics.reducedMotion[key].animatedElements})`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
