/**
 * mx-harness.mjs — shared harness for tools/measure-issue.mjs and tools/render.mjs
 * (WP-0, design-system unification).
 *
 * Responsibilities:
 *  - serve the repo root over HTTP (ephemeral port) so root-absolute asset
 *    paths (/assets/...) resolve; NEVER file://
 *  - load Playwright from the system module path; launch the pinned Chromium
 *  - neutralize the service worker (route-abort /sw.js + stub
 *    navigator.serviceWorker.register) so it cannot hijack navigations
 *  - abort all cross-origin requests (Google Fonts etc. are blocked in this
 *    environment; aborting keeps runs fast and deterministic)
 *  - deterministic stepwise "smooth scroll" pass that triggers
 *    reveal-on-scroll content, with an optional motion census sampler
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, '..', '..');

const PLAYWRIGHT_MODULE = '/opt/node22/lib/node_modules/playwright';
const CHROMIUM_EXECUTABLE = '/opt/pw-browsers/chromium';
const BROWSERS_PATH = '/opt/pw-browsers';

/** Chrome (page furniture that is not content). Used to exclude words,
 *  events, and motion attached to navigational chrome. */
export const CHROME_SELECTOR = [
  '.signal-back-to-archive',
  '[data-signal-back]',
  '.progress-bar', '#progressBar', '.progress',
  '.mast', '.hol-masthead', '.mx-mast', '.kit-mast',
  'nav', '[role="navigation"]',
  'footer', '.sp-footer', '.mx-footer',
  '.hol-subscribe',
  '.skip-link',
  '.back-to-top', '#backToTop',
  '.hol-folio-badge',
].join(', ');

export function loadPlaywright() {
  process.env.PLAYWRIGHT_BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || BROWSERS_PATH;
  const require = createRequire(import.meta.url);
  try {
    return require(PLAYWRIGHT_MODULE);
  } catch (e) {
    // fall back to a resolvable 'playwright' (e.g. local node_modules)
    return require('playwright');
  }
}

export async function launchBrowser(pw) {
  const opts = { headless: true };
  if (fs.existsSync(CHROMIUM_EXECUTABLE)) opts.executablePath = CHROMIUM_EXECUTABLE;
  return pw.chromium.launch(opts);
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
  '.webmanifest': 'application/manifest+json',
  '.txt': 'text/plain; charset=utf-8',
};

/** Static file server rooted at `root`. Returns { server, origin, port }. */
export function startServer(root) {
  const server = http.createServer((req, res) => {
    try {
      let pathname = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      let filePath = path.normalize(path.join(root, pathname));
      if (!filePath.startsWith(path.normalize(root))) {
        res.writeHead(403); res.end('forbidden'); return;
      }
      let stat = fs.existsSync(filePath) ? fs.statSync(filePath) : null;
      if (stat && stat.isDirectory()) {
        filePath = path.join(filePath, 'index.html');
        stat = fs.existsSync(filePath) ? fs.statSync(filePath) : null;
      }
      if (!stat || !stat.isFile()) {
        res.writeHead(404, { 'content-type': 'text/plain' }); res.end('not found'); return;
      }
      const type = MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
      res.writeHead(200, { 'content-type': type, 'cache-control': 'no-store' });
      fs.createReadStream(filePath).pipe(res);
    } catch (e) {
      res.writeHead(500); res.end('server error');
    }
  });
  return new Promise((resolve, reject) => {
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      resolve({ server, port, origin: `http://127.0.0.1:${port}` });
    });
  });
}

/**
 * Resolve the CLI target (path or URL) to { url, origin, close() }.
 * A local path is served over HTTP from the repo root so /assets/... works.
 */
export async function resolveTarget(input) {
  if (/^https?:\/\//i.test(input)) {
    const u = new URL(input);
    return { url: input, origin: u.origin, close: async () => {} };
  }
  const abs = path.resolve(input);
  if (!fs.existsSync(abs)) throw new Error(`target not found: ${abs}`);
  let root = REPO_ROOT;
  let rel = path.relative(root, abs);
  if (rel.startsWith('..')) {
    // file outside the repo — serve its own directory (root-absolute asset
    // paths will 404, which the harness tolerates)
    root = path.dirname(abs);
    rel = path.basename(abs);
    console.warn(`[mx-harness] WARNING: ${abs} is outside the repo root; serving ${root} instead — /assets paths may 404`);
  }
  const { server, origin } = await startServer(root);
  const url = `${origin}/${rel.split(path.sep).map(encodeURIComponent).join('/')}`;
  return { url, origin, close: async () => new Promise((r) => server.close(r)) };
}

/**
 * New context with SW neutralized and cross-origin requests aborted.
 * opts: { width, height, reducedMotion, colorScheme, origin }
 */
export async function prepareContext(browser, opts) {
  const context = await browser.newContext({
    viewport: { width: opts.width, height: opts.height },
    reducedMotion: opts.reducedMotion ? 'reduce' : 'no-preference',
    colorScheme: opts.colorScheme || 'light',
    serviceWorkers: 'block',
    // WP-5 (additive, flag-gated by callers): render with page JavaScript
    // disabled to prove the JS-off = 100%-content rule. page.evaluate still
    // works (CDP Runtime), only the page's own scripts are disabled.
    javaScriptEnabled: opts.jsDisabled ? false : true,
  });
  context.setDefaultTimeout(20000);
  context.setDefaultNavigationTimeout(45000);
  // Stub SW registration so page JS never installs/uses a service worker.
  await context.addInitScript(() => {
    try {
      if (navigator.serviceWorker) {
        const fakeReg = {
          scope: '/', installing: null, waiting: null, active: null,
          addEventListener() {}, removeEventListener() {},
          update() { return Promise.resolve(); },
          unregister() { return Promise.resolve(true); },
        };
        Object.defineProperty(navigator.serviceWorker, 'register', {
          value: () => Promise.resolve(fakeReg), configurable: true,
        });
      }
    } catch (e) { /* ignore */ }
  });
  // Abort /sw.js and every cross-origin request (external hosts are blocked
  // in this environment; aborting immediately keeps runs deterministic).
  await context.route('**/*', (route) => {
    const reqUrl = route.request().url();
    if (!/^https?:/i.test(reqUrl)) return route.continue();
    let u;
    try { u = new URL(reqUrl); } catch { return route.abort(); }
    if (opts.origin && u.origin !== opts.origin) return route.abort();
    if (u.pathname === '/sw.js') return route.abort();
    return route.continue();
  });
  return context;
}

/** Navigate and settle without ever waiting on networkidle. */
export async function openPage(context, url, settleMs = 800) {
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  // Fonts: race document.fonts.ready against a 3s cap (blocked externals
  // abort fast, but never let a hung font fetch hang the run).
  await page.evaluate(() => Promise.race([
    document.fonts ? document.fonts.ready : Promise.resolve(),
    new Promise((r) => setTimeout(r, 3000)),
  ])).catch(() => {});
  await page.waitForTimeout(settleMs);
  return page;
}

/** In-page motion sampler source (stringified into evaluate).
 *  Records elements with animations/transitions that are actually firing
 *  (duration > 0, running or finished), excluding chrome elements. */
const MOTION_SAMPLE_FN = `(chromeSelector) => {
  window.__mxMotionSeen = window.__mxMotionSeen || new Map();
  const seen = window.__mxMotionSeen;
  let anims = [];
  try { anims = document.getAnimations(); } catch (e) { return seen.size; }
  for (const a of anims) {
    let dur = 0;
    try {
      const t = a.effect && a.effect.getTiming ? a.effect.getTiming() : null;
      dur = t && typeof t.duration === 'number' ? t.duration : 0;
    } catch (e) { continue; }
    if (!(dur > 0)) continue;
    if (a.playState !== 'running' && a.playState !== 'finished') continue;
    const el = a.effect && a.effect.target;
    if (!el || !(el instanceof Element)) continue;
    if (chromeSelector && el.closest(chromeSelector)) continue;
    const kind = a.constructor.name + ':' +
      (a.animationName || a.transitionProperty || 'unknown');
    if (!seen.has(el)) seen.set(el, new Set());
    seen.get(el).add(kind);
  }
  return seen.size;
}`;

/** Short readable descriptor for an element (in-page helper source). */
export const DESCRIBE_FN = `(el) => {
  const part = (e) => {
    if (!e || !e.tagName) return '';
    let s = e.tagName.toLowerCase();
    if (e.id) s += '#' + e.id;
    const cls = (typeof e.className === 'string' ? e.className : '')
      .trim().split(/\\s+/).filter(Boolean).slice(0, 2);
    if (cls.length) s += '.' + cls.join('.');
    return s;
  };
  const chain = [];
  let cur = el;
  for (let i = 0; cur && i < 3 && cur !== document.body; i++) {
    chain.unshift(part(cur));
    cur = cur.parentElement;
  }
  return chain.join(' > ');
}`;

/**
 * Deterministic stepwise scroll pass over the full page. Steps are ~70% of
 * a viewport with fixed waits so IntersectionObserver reveals fire.
 * If collectMotion, samples the motion census after every step.
 * Returns { pageHeight, steps, motionElements (or null) }.
 */
export async function smoothScrollPass(page, { collectMotion = false, stepWaitMs = 140, chromeSelector = CHROME_SELECTOR } = {}) {
  const vh = await page.evaluate(() => window.innerHeight);
  const step = Math.max(200, Math.round(vh * 0.7));
  let steps = 0;
  const MAX_STEPS = 600;
  const sample = async () => {
    if (!collectMotion) return;
    await page.evaluate(`(${MOTION_SAMPLE_FN})(${JSON.stringify(chromeSelector)})`).catch(() => {});
  };
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(stepWaitMs);
  await sample();
  let y = 0;
  while (steps < MAX_STEPS) {
    const maxScroll = await page.evaluate(() =>
      Math.max(0, Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0) - window.innerHeight));
    if (y >= maxScroll) break;
    y = Math.min(y + step, maxScroll);
    await page.evaluate((top) => window.scrollTo({ top, behavior: 'auto' }), y);
    await page.waitForTimeout(stepWaitMs);
    await sample();
    steps++;
  }
  // settle at the bottom, then one final sample
  await page.waitForTimeout(400);
  await sample();
  const pageHeight = await page.evaluate(() =>
    Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0));
  let motionElements = null;
  if (collectMotion) {
    motionElements = await page.evaluate(`(() => {
      const seen = window.__mxMotionSeen || new Map();
      const describe = ${DESCRIBE_FN};
      const out = [];
      for (const [el, kinds] of seen.entries()) {
        if (out.length >= 200) break;
        out.push({ selector: describe(el), kinds: Array.from(kinds).sort() });
      }
      return { count: seen.size, sampled: out };
    })()`);
  }
  return { pageHeight, steps, motionElements };
}

/** Minimal argv parser: positional target + --out <dir> (+ --repo-root).
 *  WP-5 additive flags (render.mjs only): --no-js, --burst [depthIndex]. */
export function parseArgs(argv, usage) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') args.out = argv[++i];
    else if (a === '--repo-root') args.repoRoot = argv[++i];
    else if (a === '--no-js') args.noJs = true;
    else if (a === '--burst') {
      args.burst = true;
      if (argv[i + 1] !== undefined && /^\d+$/.test(argv[i + 1])) args.burstDepth = Number(argv[++i]);
    }
    else if (a === '--help' || a === '-h') { console.log(usage); process.exit(0); }
    else args._.push(a);
  }
  if (args._.length !== 1 || !args.out) {
    console.error(usage);
    process.exit(2);
  }
  return args;
}
