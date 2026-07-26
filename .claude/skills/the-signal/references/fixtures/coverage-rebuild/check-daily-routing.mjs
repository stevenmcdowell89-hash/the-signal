// Acceptance criterion #11 — "The daily surfaces a cricket/cycling/athletics item
// (feed parses, domain routes)" — demonstrated OFFLINE.
//
// Lives under references/fixtures/coverage-rebuild/ because the SPEC §2 ownership
// map gives WP-10 exactly two paths: scripts/test-coverage-gates.sh and this
// fixtures tree. It is a harness helper, not a fixture.
//
//   node check-daily-routing.mjs --feeds <feeds.js> --profile <profile.js> \
//                               --score <score.js> --render <render.js> --rss <dir>
//
// Every path is a parameter so the harness can run the SAME assertions twice: once
// against the shipped files (the passing case) and once against the pre-WP-7 /
// pre-WP-11 versions materialised out of git (the firing case). Nothing is
// hardcoded to the working tree, and no network access is used.
//
// What is asserted, in the three layers the criterion names:
//   (1) FEEDS   — feeds.js declares a feed for each of cricket, cycling, athletics.
//   (2) PARSES  — the REAL parser (ingest.js parseFeed) turns the fixture RSS into
//                 entries carrying that domain.
//   (3) ROUTES  — the REAL scorer (score.js scoreProfile) gives each entry a score
//                 > 0 and leaves item.domain on the expected sport, AND render.js's
//                 NEWS_SPORT set contains that domain so the item is headline-eligible.
//
// What is NOT asserted, and why: whether the feed URLs are reachable. That needs
// egress the harness deliberately does not take, and it is a property of the BBC,
// not of this repo. WP-7 verified all 9 URLs return 200 with egress available
// (EVIDENCE/WP-7.md § 3.1); the harness reports that as not-demonstrated rather
// than claiming a pass.

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 ? process.argv[i + 1] : dflt;
};
const HERE = path.dirname(new URL(import.meta.url).pathname);
const FEEDS = arg("feeds");
const PROFILE = arg("profile");
const SCORE = arg("score");
const RENDER = arg("render");
const RSS = arg("rss", path.join(HERE, "rss"));
const LABEL = arg("label", "daily-routing");

const SPORTS = [
  { domain: "cricket", rss: "bbc-cricket-sample.xml" },
  { domain: "cycling", rss: "bbc-cycling-sample.xml" },
  { domain: "athletics", rss: "bbc-athletics-sample.xml" },
];

let fails = 0;
const ok = (cond, msg) => {
  console.log(`    ${cond ? "ok  " : "FAIL"}  ${msg}`);
  if (!cond) fails++;
};

const load = async (p) => import(pathToFileURL(path.resolve(p)).href);

// render.js's NEWS_SPORT is a function-local `const`, not an export, so it is read
// textually. Deliberate: the alternative is calling buildState() with a fabricated
// config and item set, which would test far more than this criterion asks about.
function newsSportSet(renderPath) {
  const src = readFileSync(renderPath, "utf8");
  const m = src.match(/const\s+NEWS_SPORT\s*=\s*new\s+Set\(\[([\s\S]*?)\]\)/);
  if (!m) return null;
  return new Set([...m[1].matchAll(/"([a-z_]+)"/g)].map((x) => x[1]));
}

console.log(`  [${LABEL}]`);
console.log(`    feeds=${FEEDS}`);
console.log(`    profile=${PROFILE}`);
console.log(`    render=${RENDER}`);

const { STARTER_FEEDS } = await load(FEEDS);
const { PROFILE: profile } = await load(PROFILE);
const { scoreProfile } = await load(SCORE);
// parseFeed comes from the shipped ingest.js in every run: it is not part of what
// WP-7/WP-11 changed, so swapping it would only add noise.
const { parseFeed } = await load(arg("ingest", path.join(path.dirname(FEEDS), "ingest.js")));

const news = newsSportSet(RENDER);
ok(news !== null, `render.js declares a NEWS_SPORT set (${news ? [...news].join(", ") : "NOT FOUND"})`);

for (const { domain, rss } of SPORTS) {
  // (1) a feed exists for the domain
  const feeds = (STARTER_FEEDS || []).filter((f) => f.domain === domain);
  ok(feeds.length > 0, `feeds.js declares ${feeds.length} feed(s) with domain="${domain}"`);
  const feed = feeds[0] || { id: `synthetic-${domain}`, type: "rss", domain, weight: 1, name: domain };

  // (2) the real parser reads the fixture RSS
  const xml = readFileSync(path.join(RSS, rss), "utf8");
  const items = parseFeed(xml, feed);
  ok(items.length === 2, `parseFeed(${rss}) -> ${items.length} entr(y|ies), all domain="${domain}"`
     + (items.length ? "" : "  <- feed did not parse"));

  // (3) the real scorer routes them above zero and leaves the domain alone
  let scored = 0;
  for (const it of items) {
    const pr = scoreProfile(it, profile, [], {});
    const good = pr.score > 0 && it.domain === domain && !pr.muted;
    if (good) scored++;
    console.log(`      ${good ? "·" : "×"} score=${pr.score.toFixed(2)} domain=${it.domain}`
                + `  ${it.title.slice(0, 72)}`);
  }
  ok(scored === items.length,
     `${scored}/${items.length} ${domain} item(s) score > 0 and stay in domain "${domain}"`);
  ok(news !== null && news.has(domain),
     `NEWS_SPORT contains "${domain}" (headline-eligible, render.js)`);
}

console.log(`  [${LABEL}] ${fails} assertion failure(s)`);
process.exit(fails === 0 ? 0 : 1);
