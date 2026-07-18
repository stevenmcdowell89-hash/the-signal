// tools/measure-issue.mjs — The Signal · design-system unification · WP-0(a)
// ---------------------------------------------------------------------------
// The MEASUREMENT harness. Renders a served issue at 1440x900 and 390x844,
// warms up scroll-reveals, smooth-scrolls, and emits a metrics.json that is the
// SOLE source of truth for the numeric Laws. Per Part 6 §2 ("measured, never
// asserted") no subagent prose estimate may substitute for this file's output.
//
// Emits, per viewport:
//   - words / events / screens / events_per_screen / words_per_screen   (Law 2/3)
//   - longest_zero_event_run_screens + event centres per screen          (Law 2 distribution)
//   - event_breakdown (selector -> count), img_count, role_img_count     (audit trail)
//   - chrome_overlap: fixed/sticky chrome obscuring content centres       (Law 10)
//   - h_scroll: document-level horizontal overflow                        (Law 10)
//   - table_truncation: cells clipped mid-content w/o wrap affordance     (Law 10)
//   - motion: animations observed during a real scroll + reduced-motion   (Law 5)
//
// Usage:
//   node tools/measure-issue.mjs <repoRoot> <urlPath> <outJsonPath>
// e.g. node tools/measure-issue.mjs . /issues/signal_countdown_2026-06-14.html \
//        docs/design-system-unification-EVIDENCE/wp-1/countdown.metrics.json
//
// Environment: Chromium at /opt/pw-browsers/chromium, served over HTTP (root-
// absolute asset paths), service worker BLOCKED (it hijacks navigations).
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const TOOL_VERSION = 'measure-issue/1.0.0';
const EXE = '/opt/pw-browsers/chromium';

const [repoRoot, urlPath, outPath] = process.argv.slice(2);
if (!repoRoot || !urlPath || !outPath) {
  console.error('usage: node tools/measure-issue.mjs <repoRoot> <urlPath> <outJsonPath>');
  process.exit(2);
}
const ROOT = path.resolve(repoRoot);
fs.mkdirSync(path.dirname(path.resolve(outPath)), { recursive: true });

const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
};

// ── Law-2 EVENT VOCABULARY ────────────────────────────────────────────────
// A "designed visual event" is one of the closed list in Law 2. Selectors are
// the UNION of the legacy taxonomy (hol-/sp-/dd-, verified against the rendered
// countdown/field-guide/deep-dive) and the forthcoming mx- core. querySelectorAll
// only matches rendered DOM nodes, so the shared <style>/comment phantoms present
// in every issue file never count. Granularity is deliberate:
//   OBJECT-level  — each ephemera/plate/figure/quote/divider element = 1 event.
//   BLOCK-level   — a stat band / ledger / table / cheat-sheet counts ONCE
//                   (nesting-dedup skips its rows/cells so a 12-cell band != 12).
// NOT events (excluded by omission): drop caps, hairlines, subheads, bold runs,
// marginalia, plain paragraphs.
const EVENT_SELECTORS = [
  // ephemera objects (each = 1)
  '.hol-polaroid', '.hol-postcard', '.hol-stamp', '.hol-ticket', '.hol-coaster',
  '.hol-pull', '.hol-coin', '.hol-telegram', '.hol-index-card', '.hol-pennant',
  '.mx-ephemera', '.mx-postcard', '.mx-stamp', '.mx-ticket', '.mx-coaster',
  '.mx-card', '.mx-pin-card', '.mx-polaroid', '.mx-coin',
  // numbered plates / act openers / anchor blocks (each = 1)
  '.hol-wonder__card', '.hol-unmissable__card', '.hol-meal-slot__entry',
  '.hol-half__opener', '.hol-kicker-strip', '.hol-anchor',
  '.mx-plate', '.mx-act-open', '.mx-anchor',
  // captioned figures (each = 1); bare imgs/role=img dedup under these
  'figure', '.fig', '.mx-figure',
  // quote-objects with a named source (each = 1)
  '.pullquote', '.mx-quote', '.mx-postcard-quote',
  // marquee / act-divider / ornament (each = 1)
  '.hol-marquee', '.hol-transit', '.sp-ornament', '.hol-fleuron',
  '.mx-marquee', '.mx-transit', '.mx-act-divider',
  // stat bands (container = 1; cells dedup out)
  '.hol-trip-numbers', '.hol-countdown', '.bignum-row', '.bignum', '.mx-stat-band',
  // ledgers / tables / scorecards (container = 1; rows dedup out)
  '.hol-chalkboard', '.data-table', 'table', '.dd-tl',
  '.hol-scorecard', '.mx-ledger', '.mx-scorecard', '.mx-table',
  // cheat-sheet (container = 1 if present, else items count)
  '.keep-digging', '.dd-keep-digging', '.cheat-sheet', '.mx-cheat-sheet', '.kd-item',
  // real-image census (dedups under figures/ephemera; standalone captioned img = 1)
  'img', '[role="img"]',
];

const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.svg': 'image/svg+xml', '.avif': 'image/avif', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ico': 'image/x-icon', '.txt': 'text/plain' };

function serve(root) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      try {
        let p = decodeURIComponent(req.url.split('?')[0]);
        if (p.endsWith('/')) p += 'index.html';
        const fp = path.join(root, p);
        if (!fp.startsWith(root) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) {
          res.writeHead(404); res.end('not found'); return;
        }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
        fs.createReadStream(fp).pipe(res);
      } catch (e) { res.writeHead(500); res.end(String(e)); }
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

async function warmUp(page) {
  // Walk the full page so every one-way scroll-reveal IntersectionObserver fires;
  // reveals are one-way so content stays shown after we return to top.
  await page.evaluate(async () => {
    const h = document.documentElement.scrollHeight;
    const step = Math.round(window.innerHeight * 0.6);
    for (let y = 0; y <= h; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); }
    window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 150));
  });
}

async function smoothScrollTo(page, y) {
  await page.evaluate(async (targetY) => {
    await new Promise((res) => {
      const start = window.scrollY, dist = targetY - start, dur = 500, t0 = performance.now();
      function step(t) {
        const k = Math.min(1, (t - t0) / dur);
        window.scrollTo(0, start + dist * (0.5 - 0.5 * Math.cos(Math.PI * k)));
        if (k < 1) requestAnimationFrame(step); else res();
      }
      requestAnimationFrame(step);
    });
  }, y);
  await page.waitForTimeout(120);
}

// Static DOM census: events (nesting-deduped), words, distribution, imgs, tables.
async function census(page, selectors, vpHeight) {
  return page.evaluate(({ selectors, vpHeight }) => {
    const MINW = 36, MINH = 24;
    const scrollY = window.scrollY;
    // Collect candidate elements in document order, dedupe by nesting.
    const matched = [];
    const seen = new Set();
    for (const sel of selectors) {
      for (const el of document.querySelectorAll(sel)) matched.push({ el, sel });
    }
    // Order by DOM position so ancestors are considered before descendants.
    matched.sort((a, b) => {
      const p = a.el.compareDocumentPosition(b.el);
      if (p & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
      if (p & Node.DOCUMENT_POSITION_PRECEDING) return 1;
      return 0;
    });
    const events = [];
    const breakdown = {};
    for (const { el, sel } of matched) {
      if (seen.has(el)) continue;
      // nested inside an already-counted event?
      let anc = el.parentElement, nested = false;
      while (anc) { if (seen.has(anc)) { nested = true; break; } anc = anc.parentElement; }
      if (nested) continue;
      const r = el.getBoundingClientRect();
      if (r.width < MINW || r.height < MINH) continue;               // icons/hairlines
      const style = getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden' || +style.opacity === 0) continue;
      seen.add(el);
      const centreDocY = r.top + scrollY + r.height / 2;
      events.push({ sel, centreDocY });
      breakdown[sel] = (breakdown[sel] || 0) + 1;
    }
    const scrollHeight = document.documentElement.scrollHeight;
    const words = (document.body.innerText || '').trim().split(/\s+/).filter(Boolean).length;
    const imgCount = document.querySelectorAll('img').length;
    const roleImgCount = document.querySelectorAll('[role="img"]').length;

    // Distribution: bucket event centres into screen indices; longest zero run.
    const totalScreens = Math.max(1, Math.ceil(scrollHeight / vpHeight));
    const perScreen = new Array(totalScreens).fill(0);
    for (const e of events) {
      const idx = Math.min(totalScreens - 1, Math.floor(e.centreDocY / vpHeight));
      perScreen[idx]++;
    }
    let longestZero = 0, run = 0;
    for (const c of perScreen) { if (c === 0) { run++; longestZero = Math.max(longestZero, run); } else run = 0; }

    return {
      words, events: events.length, scrollHeight, totalScreens,
      events_per_screen: +(events.length / (scrollHeight / vpHeight)).toFixed(3),
      words_per_screen: +(words / (scrollHeight / vpHeight)).toFixed(1),
      longest_zero_event_run_screens: longestZero,
      events_per_screen_series: perScreen,
      event_breakdown: breakdown,
      img_count: imgCount, role_img_count: roleImgCount,
    };
  }, { selectors, vpHeight });
}

// Law 10: horizontal document scroll.
async function hScroll(page) {
  return page.evaluate(() => {
    const de = document.documentElement;
    const overflow = de.scrollWidth - de.clientWidth;
    return { has_hscroll: overflow > 1, overflow_px: overflow };
  });
}

// Law 10: table cells clipped without a wrap/scroll affordance.
async function tableTruncation(page) {
  return page.evaluate(() => {
    let hits = 0; const detail = [];
    const affordance = (el) => {
      let a = el;
      while (a && a !== document.body) {
        const s = getComputedStyle(a);
        if (s.overflowX === 'auto' || s.overflowX === 'scroll') return true;
        a = a.parentElement;
      }
      return false;
    };
    for (const cell of document.querySelectorAll('table td, table th')) {
      const clipped = cell.scrollWidth - cell.clientWidth > 1;
      const s = getComputedStyle(cell);
      const nowrapClip = s.whiteSpace === 'nowrap' && (s.textOverflow === 'clip' || s.overflow === 'hidden');
      if ((clipped || nowrapClip) && !affordance(cell)) {
        hits++; detail.push({ text: (cell.innerText || '').slice(0, 40), scrollWidth: cell.scrollWidth, clientWidth: cell.clientWidth });
      }
    }
    return { table_truncation_hits: hits, detail: detail.slice(0, 10) };
  });
}

// Law 10: fixed/sticky chrome obscuring content centres. At each depth, if a
// text-bearing content element's centre point resolves (elementFromPoint) to a
// fixed/sticky chrome root, that content is being covered -> overlap.
async function chromeOverlap(page, depths, vpHeight) {
  const hits = [];
  for (const y of depths) {
    await smoothScrollTo(page, y);
    const r = await page.evaluate(() => {
      const isChrome = (el) => {
        let a = el;
        while (a && a !== document.body && a !== document.documentElement) {
          const s = getComputedStyle(a);
          if (s.position === 'fixed' || s.position === 'sticky') return a;
          a = a.parentElement;
        }
        return null;
      };
      const TEXT = 'p,h1,h2,h3,h4,h5,h6,li,dd,dt,figcaption,blockquote,td,th,a';
      let obscured = 0; const samples = [];
      for (const c of document.querySelectorAll(TEXT)) {
        if (isChrome(c)) continue;                          // chrome's own text
        const rect = c.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 10) continue;
        const cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
        if (cy < 0 || cy > window.innerHeight || cx < 0 || cx > window.innerWidth) continue;
        if (!(c.innerText || '').trim()) continue;
        const top = document.elementFromPoint(cx, cy);
        if (top && isChrome(top)) {
          obscured++;
          if (samples.length < 4) samples.push({ chrome: (isChrome(top).className || isChrome(top).tagName || '').toString().slice(0, 40), covered: (c.innerText || '').trim().slice(0, 40) });
        }
      }
      return { obscured, samples };
    });
    if (r.obscured > 0) hits.push({ scrollY: y, obscured: r.obscured, samples: r.samples });
  }
  await smoothScrollTo(page, 0);
  return { chrome_overlap_depths_with_hits: hits.length, total_obscured_samples: hits.reduce((a, h) => a + h.obscured, 0), hits };
}

// Law 5: motion actually observed during a real scroll. Polls the Web-Animations
// API for running animations and samples furniture transform/opacity deltas.
async function motionCensus(page, vpHeight) {
  const sampleSel = EVENT_SELECTORS.join(',');
  return page.evaluate(async ({ sampleSel }) => {
    const snap = () => {
      const m = new Map();
      const els = [...document.querySelectorAll(sampleSel)].slice(0, 400);
      for (const el of els) { const s = getComputedStyle(el); m.set(el, s.transform + '|' + s.opacity); }
      return m;
    };
    window.scrollTo(0, 0);
    await new Promise(r => setTimeout(r, 120));
    const before = snap();
    let maxRunning = 0; const seenAnims = new Set();
    const h = document.documentElement.scrollHeight, step = Math.round(window.innerHeight * 0.5);
    for (let y = 0; y <= h; y += step) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 90));
      const running = document.getAnimations().filter(a => a.playState === 'running');
      maxRunning = Math.max(maxRunning, running.length);
      for (const a of running) seenAnims.add(a);
    }
    await new Promise(r => setTimeout(r, 150));
    const after = snap();
    let moved = 0;
    for (const [el, v] of after) { if (before.has(el) && before.get(el) !== v) moved++; }
    window.scrollTo(0, 0);
    return {
      animations_running_max: maxRunning,
      animations_total_distinct: seenAnims.size,
      furniture_moved_count: moved,
    };
  }, { sampleSel });
}

async function measureViewport(browser, port, vpName, vp, opts) {
  const ctx = await browser.newContext({
    viewport: vp, colorScheme: 'light',
    reducedMotion: opts.reducedMotion ? 'reduce' : 'no-preference',
    deviceScaleFactor: 1, serviceWorkers: 'block',
  });
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}${urlPath}`, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await page.waitForTimeout(400);
  await warmUp(page);

  const base = await census(page, EVENT_SELECTORS, vp.height);
  const scrollHeight = base.scrollHeight;
  const depths = [1, 2, 3, 4, 5, 6, 7, 8].map(i => Math.round((scrollHeight - vp.height) * (i / 9))).filter(y => y >= 0);

  const motion = await motionCensus(page, vp.height);
  const overlap = await chromeOverlap(page, depths, vp.height);
  const hs = await hScroll(page);
  const trunc = await tableTruncation(page);

  await ctx.close();
  return {
    viewport: vp, reduced_motion: !!opts.reducedMotion,
    ...base, h_scroll: hs, table_truncation: trunc, chrome_overlap: overlap, motion,
  };
}

(async () => {
  const srv = await serve(ROOT);
  const port = srv.address().port;
  const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
  const out = { tool: TOOL_VERSION, url: urlPath, generated_utc: null, viewports: {} };
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    out.viewports[vpName] = await measureViewport(browser, port, vpName, vp, {});
  }
  // Reduced-motion control at desktop only — Law 5 requires zero motion here.
  const rm = await measureViewport(browser, port, 'desktop', VIEWPORTS.desktop, { reducedMotion: true });
  out.reduced_motion_control = {
    animations_running_max: rm.motion.animations_running_max,
    animations_total_distinct: rm.motion.animations_total_distinct,
    furniture_moved_count: rm.motion.furniture_moved_count,
  };
  await browser.close();
  srv.close();
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  const d = out.viewports.desktop, m = out.viewports.mobile;
  console.log(`[measure] ${urlPath}`);
  console.log(`  desktop: ${d.events} events / ${d.totalScreens} screens = ${d.events_per_screen} ev/screen · ${d.words} words · longest-zero-run ${d.longest_zero_event_run_screens} · hscroll=${d.h_scroll.has_hscroll} · trunc=${d.table_truncation.table_truncation_hits} · chrome-overlap-depths=${d.chrome_overlap.chrome_overlap_depths_with_hits} · motion(anim=${d.motion.animations_total_distinct},moved=${d.motion.furniture_moved_count})`);
  console.log(`  mobile:  ${m.events} events / ${m.totalScreens} screens = ${m.events_per_screen} ev/screen · ${m.words} words · hscroll=${m.h_scroll.has_hscroll} · trunc=${m.table_truncation.table_truncation_hits} · chrome-overlap-depths=${m.chrome_overlap.chrome_overlap_depths_with_hits}`);
  console.log(`  reduced-motion control: anim=${out.reduced_motion_control.animations_total_distinct}, moved=${out.reduced_motion_control.furniture_moved_count}`);
  console.log(`  -> ${outPath}`);
})().catch((e) => { console.error(e); process.exit(1); });
