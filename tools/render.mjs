// tools/render.mjs — The Signal · design-system unification · WP-0(d)
// ---------------------------------------------------------------------------
// The SCREENSHOT harness that feeds the Part 5 design-parity gate. Serves the
// repo over HTTP, renders a page in Chromium, and captures a NON-CURATED set:
// cover (true top, before any scroll), 8 smooth-scroll depths, one dark render,
// one reduced-motion render — at both 1440x900 and 390x844. Screenshots are the
// gate's evidence; the harness produces all depths so a builder cannot hand-pick.
//
// Usage:
//   node tools/render.mjs <repoRoot> <urlPath> <outDir/prefix>
// Writes <prefix>__<shot>__<vp>.png and prints the manifest.
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const EXE = '/opt/pw-browsers/chromium';
const [repoRoot, urlPath, outPrefix] = process.argv.slice(2);
if (!repoRoot || !urlPath || !outPrefix) {
  console.error('usage: node tools/render.mjs <repoRoot> <urlPath> <outDir/prefix>');
  process.exit(2);
}
const ROOT = path.resolve(repoRoot);
fs.mkdirSync(path.dirname(path.resolve(outPrefix)), { recursive: true });

const VIEWPORTS = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.avif': 'image/avif',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ico': 'image/x-icon', '.txt': 'text/plain' };

function serve(root) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      try {
        let p = decodeURIComponent(req.url.split('?')[0]);
        if (p.endsWith('/')) p += 'index.html';
        const fp = path.join(root, p);
        if (!fp.startsWith(root) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) { res.writeHead(404); res.end('not found'); return; }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
        fs.createReadStream(fp).pipe(res);
      } catch (e) { res.writeHead(500); res.end(String(e)); }
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

async function smoothScrollTo(page, y) {
  await page.evaluate(async (targetY) => {
    await new Promise((res) => {
      const start = window.scrollY, dist = targetY - start, dur = 550, t0 = performance.now();
      function step(t) { const k = Math.min(1, (t - t0) / dur); window.scrollTo(0, start + dist * (0.5 - 0.5 * Math.cos(Math.PI * k))); if (k < 1) requestAnimationFrame(step); else res(); }
      requestAnimationFrame(step);
    });
  }, y);
  await page.waitForTimeout(420);
}

async function pass(browser, port, opts, manifest) {
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    const ctx = await browser.newContext({ viewport: vp, colorScheme: opts.colorScheme || 'light',
      reducedMotion: opts.reducedMotion || 'no-preference', deviceScaleFactor: 1, serviceWorkers: 'block' });
    const page = await ctx.newPage();
    await page.goto(`http://127.0.0.1:${port}${urlPath}`, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(500);
    const shot = (n) => { const f = `${outPrefix}__${n}__${vpName}.png`; manifest.push(path.basename(f)); return f; };

    if (opts.colorScheme === 'dark') { await page.screenshot({ path: shot('dark') }); await ctx.close(); continue; }
    if (opts.reducedMotion === 'reduce') { if (vpName === 'desktop') await page.screenshot({ path: shot('reduced') }); await ctx.close(); continue; }

    // Cover FIRST at true top (some covers are scroll-reactive).
    await page.screenshot({ path: shot('cover') });
    // Warm-up walk so one-way reveals fire, then return to top.
    await page.evaluate(async () => { const h = document.documentElement.scrollHeight, s = Math.round(window.innerHeight * 0.6);
      for (let y = 0; y <= h; y += s) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 45)); } window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 200)); });
    const sh = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let i = 1; i <= 8; i++) { const y = Math.round((sh - vp.height) * (i / 9)); await smoothScrollTo(page, Math.max(0, y)); await page.screenshot({ path: shot('scroll' + i) }); }
    await ctx.close();
  }
}

(async () => {
  const srv = await serve(ROOT);
  const port = srv.address().port;
  const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
  const manifest = [];
  await pass(browser, port, { colorScheme: 'light' }, manifest);
  await pass(browser, port, { colorScheme: 'dark' }, manifest);
  await pass(browser, port, { reducedMotion: 'reduce' }, manifest);
  await browser.close();
  srv.close();
  fs.writeFileSync(`${outPrefix}__MANIFEST.json`, JSON.stringify({ url: urlPath, shots: manifest }, null, 2));
  console.log(`[render] ${urlPath} -> ${manifest.length} shots (${outPrefix}__*.png)`);
})().catch((e) => { console.error(e); process.exit(1); });
