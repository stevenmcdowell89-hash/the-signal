#!/usr/bin/env node
/**
 * render.mjs — WP-0 screenshot harness for The Signal design-system
 * unification (spec: docs/design-system-unification-SPEC-2026-07-18.md).
 *
 * Usage: node tools/render.mjs <issue-path-or-url> --out <dir>
 *
 * Produces, for BOTH 1440x900 and 390x844 (served over HTTP, service worker
 * neutralized, cross-origin requests aborted, full stepwise smooth-scroll
 * pass first so reveal-on-scroll content has fired):
 *   <out>/1440/cover.png              viewport shot at scroll 0
 *   <out>/1440/depth-0.png..depth-7.png   8 evenly spaced depths (0..bottom)
 *   <out>/390/cover.png + depth-0..7.png
 *   <out>/dark-1440.png               one dark-mode (prefers-color-scheme:
 *                                     dark) cover render at 1440x900
 *   <out>/render-manifest.json        what was shot, page heights, depths
 *
 * Screenshots are harness-produced at fixed positions — never curated.
 */

import fs from 'node:fs';
import path from 'node:path';
import {
  loadPlaywright, launchBrowser, resolveTarget, prepareContext, openPage,
  smoothScrollPass, parseArgs,
} from './lib/mx-harness.mjs';

const USAGE = 'Usage: node tools/render.mjs <issue-path-or-url> --out <dir>';

const WIDTHS = [
  { key: '1440', width: 1440, height: 900 },
  { key: '390', width: 390, height: 844 },
];

async function shootWidth(browser, target, vp, outDir, manifest) {
  const dir = path.join(outDir, vp.key);
  fs.mkdirSync(dir, { recursive: true });
  const context = await prepareContext(browser, {
    width: vp.width, height: vp.height, origin: target.origin,
  });
  const page = await openPage(context, target.url);

  // cover first (pre-scroll state, as a reader lands on it)
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(dir, 'cover.png') });

  // full smooth-scroll pass so reveal-on-scroll content fires
  const pass = await smoothScrollPass(page, { collectMotion: false });
  const maxScroll = Math.max(0, pass.pageHeight - vp.height);

  const depths = [];
  for (let i = 0; i < 8; i++) {
    const y = Math.round((maxScroll * i) / 7);
    depths.push(y);
    await page.evaluate((top) => window.scrollTo({ top, behavior: 'auto' }), y);
    await page.waitForTimeout(450);
    await page.screenshot({ path: path.join(dir, `depth-${i}.png`) });
  }

  manifest.widths[vp.key] = {
    viewport: { width: vp.width, height: vp.height },
    pageHeight: pass.pageHeight,
    maxScroll,
    depths,
    files: ['cover.png', ...depths.map((_, i) => `depth-${i}.png`)],
  };
  await context.close();
}

async function shootDark(browser, target, outDir, manifest) {
  const context = await prepareContext(browser, {
    width: 1440, height: 900, origin: target.origin, colorScheme: 'dark',
  });
  const page = await openPage(context, target.url);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
  const file = path.join(outDir, 'dark-1440.png');
  await page.screenshot({ path: file });
  manifest.dark = { viewport: { width: 1440, height: 900 }, file: 'dark-1440.png' };
  await context.close();
}

async function main() {
  const args = parseArgs(process.argv.slice(2), USAGE);
  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  const pw = loadPlaywright();
  const target = await resolveTarget(args._[0]);
  const browser = await launchBrowser(pw);

  const manifest = {
    tool: 'tools/render.mjs',
    source: args._[0],
    url: target.url,
    generatedAt: new Date().toISOString(),
    widths: {},
    dark: null,
  };

  try {
    for (const vp of WIDTHS) {
      console.log(`[render] ${vp.key}px pass…`);
      await shootWidth(browser, target, vp, outDir, manifest);
    }
    console.log('[render] dark-mode render at 1440…');
    await shootDark(browser, target, outDir, manifest);
  } finally {
    await browser.close();
    await target.close();
  }

  fs.writeFileSync(path.join(outDir, 'render-manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`[render] wrote ${outDir} (${Object.keys(manifest.widths).map((k) => `${k}: ${manifest.widths[k].files.length} shots`).join(', ')} + dark-1440.png)`);
}

main().catch((e) => { console.error(e); process.exit(1); });
