// Rendered-review harness for The Signal design-system unification (spec §9).
// Serves the repo root over HTTP, renders a page in Chromium, captures cover +
// scroll-depth + dark + reduced-motion screenshots at desktop and mobile, and
// computes the density metric (visual events / screen).
//
// Usage:
//   node render.mjs <repoRoot> <urlPath> <outPrefix> [selectorsJSON]

import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const EXE = '/opt/pw-browsers/chromium';
const [repoRoot, urlPath, outPrefix, selectorsArg] = process.argv.slice(2);
if (!repoRoot || !urlPath || !outPrefix) {
  console.error('usage: node render.mjs <repoRoot> <urlPath> <outPrefix> [selectorsJSON]');
  process.exit(2);
}
fs.mkdirSync(path.dirname(outPrefix), { recursive: true });

const DEFAULT_SELECTORS = [
  'figure', 'img',
  '.mx-ledger', '.mx-stat-band', '.mx-quote', '.mx-stamp', '.mx-numbers',
  '.mx-plate', '.mx-cheat-sheet', '.mx-ephemera', '.mx-marquee', '.mx-act-open',
];
const SELECTORS = selectorsArg ? JSON.parse(selectorsArg) : DEFAULT_SELECTORS;

const MIME = { '.html':'text/html', '.css':'text/css', '.js':'text/javascript',
  '.json':'application/json', '.png':'image/png', '.jpg':'image/jpeg',
  '.jpeg':'image/jpeg', '.gif':'image/gif', '.webp':'image/webp', '.svg':'image/svg+xml',
  '.avif':'image/avif', '.woff2':'font/woff2', '.woff':'font/woff', '.ico':'image/x-icon' };

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

const VIEWPORTS = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

async function smoothScrollTo(page, y) {
  await page.evaluate(async (targetY) => {
    await new Promise((res) => {
      const start = window.scrollY, dist = targetY - start, dur = 600, t0 = performance.now();
      function step(t) {
        const k = Math.min(1, (t - t0) / dur);
        window.scrollTo(0, start + dist * (0.5 - 0.5 * Math.cos(Math.PI * k)));
        if (k < 1) requestAnimationFrame(step); else res();
      }
      requestAnimationFrame(step);
    });
  }, y);
  await page.waitForTimeout(450);
}

async function pass(browser, port, opts) {
  const out = { density: null };
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    const ctx = await browser.newContext({ viewport: vp,
      colorScheme: opts.colorScheme || 'light',
      reducedMotion: opts.reducedMotion || 'no-preference',
      deviceScaleFactor: 1, serviceWorkers: 'block' });
    const page = await ctx.newPage();
    await page.goto(`http://127.0.0.1:${port}${urlPath}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(()=>{});
    await page.waitForTimeout(500);
    const tag = (n) => `${outPrefix}__${n}__${vpName}.png`;

    // Cover FIRST, at true top, before any scrolling — some covers are
    // scroll-reactive and must be shot before the warm-up walk.
    if (opts.colorScheme === 'dark') await page.screenshot({ path: tag('dark') });
    else if (opts.reducedMotion === 'reduce') { if (vpName === 'desktop') await page.screenshot({ path: tag('reduced') }); }
    else await page.screenshot({ path: tag('cover') });

    // Warm-up: walk the full page so every one-way scroll-reveal observer fires
    // (spec §9 — teleport-scroll under-triggers reveals; content must not read as
    // blank because JS hasn't run). Reveals are one-way, so content stays shown.
    await page.evaluate(async () => {
      const h = document.documentElement.scrollHeight, step = Math.round(window.innerHeight * 0.6);
      for (let y = 0; y <= h; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 200));
    });
    const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);

    if (opts.colorScheme === 'dark' || opts.reducedMotion === 'reduce') {
      // cover already shot above; nothing further for these passes
    } else {
      for (let i = 1; i <= 4; i++) {
        const y = Math.round((scrollHeight - vp.height) * (i / 5));
        await smoothScrollTo(page, y);
        await page.screenshot({ path: tag('scroll' + i) });
      }
      if (vpName === 'desktop') {
        const m = await page.evaluate((sels) => {
          const seen = new Set(); let events = 0;
          for (const sel of sels) for (const el of document.querySelectorAll(sel)) {
            const r = el.getBoundingClientRect();
            if (r.width < 40 || r.height < 24) continue;
            let anc = el.parentElement, nested = false;
            while (anc) { if (seen.has(anc)) { nested = true; break; } anc = anc.parentElement; }
            if (nested || seen.has(el)) continue;
            seen.add(el); events++;
          }
          const words = (document.body.innerText||'').trim().split(/\s+/).filter(Boolean).length;
          return { events, words, scrollHeight: document.documentElement.scrollHeight };
        }, SELECTORS);
        const screens = m.scrollHeight / 900;
        out.density = { events: m.events, words: m.words, scrollHeight: m.scrollHeight,
          screens: +screens.toFixed(2),
          events_per_screen: +(m.events/screens).toFixed(2),
          words_per_screen: +(m.words/screens).toFixed(1) };
      }
    }
    await ctx.close();
  }
  return out;
}

(async () => {
  const srv = await serve(repoRoot);
  const port = srv.address().port;
  const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
  const light = await pass(browser, port, { colorScheme: 'light' });
  await pass(browser, port, { colorScheme: 'dark' });
  await pass(browser, port, { reducedMotion: 'reduce' });
  await browser.close();
  srv.close();
  fs.writeFileSync(`${outPrefix}__density.json`, JSON.stringify(light.density || {}, null, 2));
  console.log('DENSITY ' + JSON.stringify(light.density || {}));
})().catch((e) => { console.error(e); process.exit(1); });
