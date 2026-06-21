// The Signal — daily: ingest + parse (§3 Tier 1 step 1, §5 links).
//
// Workers has no DOMParser, so RSS/Atom is parsed with tolerant regex extraction
// — robust enough for the well-formed feeds in the starter set, and any feed
// that yields zero items on first ingest is dropped gracefully by the caller.
// HN comes from the Algolia JSON API (no parsing); Bluesky from the public XRPC
// JSON API.
//
// Every entry is normalised to:
//   { sourceId, sourceType, domain, weight, title, url, links[], rawScore,
//     published, commentsUrl? }
// where links[] is { type: "article"|"discussion"|"post"|"feed", url, label }.

const UA = "TheSignalDaily/1.0 (+https://the-signal; personal reading aggregator)";

async function fetchText(url, accept) {
  const resp = await fetch(url, {
    headers: { "User-Agent": UA, Accept: accept || "*/*" },
    cf: { cacheTtl: 60, cacheEverything: false },
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.text();
}

async function fetchJson(url) {
  const resp = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

// ---- tiny XML helpers (regex-based; tolerant) ----
//
// Robust HTML-entity decoding: numeric (decimal + hex) via code point, a named
// map for the common ones, run twice to catch double-encoding (&amp;#8217;),
// with tags stripped. This is what kept curly quotes / em-dashes / accents
// from showing up as raw "&#8217;" mojibake.
const NAMED = {
  nbsp: " ", amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", "#39": "'",
  ndash: "–", mdash: "—", hellip: "…", lsquo: "‘", rsquo: "’", sbquo: "‚",
  ldquo: "“", rdquo: "”", bdquo: "„", laquo: "«", raquo: "»", prime: "′", Prime: "″",
  eacute: "é", egrave: "è", ecirc: "ê", agrave: "à", acirc: "â", aacute: "á",
  uuml: "ü", ouml: "ö", auml: "ä", iuml: "ï", uacute: "ú", oacute: "ó",
  iacute: "í", ccedil: "ç", ntilde: "ñ", szlig: "ß", oslash: "ø", aring: "å",
  Eacute: "É", Agrave: "À", copy: "©", reg: "®", trade: "™", deg: "°",
  pound: "£", euro: "€", cent: "¢", yen: "¥", middot: "·", bull: "•",
  times: "×", divide: "÷", frac12: "½", frac14: "¼", frac34: "¾", amp_: "&",
};

function cp(n) {
  try {
    if (!n || (n >= 0xd800 && n <= 0xdfff)) return "";
    return String.fromCodePoint(n);
  } catch {
    return "";
  }
}

function decodeOnce(s) {
  return s
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => cp(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => cp(parseInt(d, 10)))
    .replace(/&([a-zA-Z][a-zA-Z0-9]*);/g, (m, n) =>
      NAMED[n] !== undefined ? NAMED[n] : NAMED[n.toLowerCase()] !== undefined ? NAMED[n.toLowerCase()] : m
    );
}

function decodeEntities(s) {
  if (!s) return "";
  s = s.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1"); // unwrap CDATA
  s = s.replace(/<[^>]+>/g, " "); // strip the original tags
  s = decodeOnce(s); // decode entities (may reveal tags that were entity-encoded)
  s = s.replace(/<[^>]+>/g, " "); // strip those revealed tags
  s = decodeOnce(s); // final pass for any remaining double-encoded entities
  return s.replace(/\s+/g, " ").trim();
}

// Clip a summary to ~n chars. Prefer a SENTENCE boundary (so it reads as a whole
// thought, not "…renowned for their"); fall back to a word boundary + ellipsis.
function clip(s, n) {
  s = (s || "").trim();
  if (s.length <= n) return s;
  const t = s.slice(0, n);
  // A sentence end (. ! ?) past the halfway mark → cut there, keep it clean.
  const sent = Math.max(t.lastIndexOf(". "), t.lastIndexOf("! "), t.lastIndexOf("? "));
  if (sent >= n * 0.5) return t.slice(0, sent + 1).trim();
  const sp = t.lastIndexOf(" ");
  return (sp > 60 ? t.slice(0, sp) : t).replace(/[\s.,;:–—-]+$/, "") + "…";
}

function firstTag(block, tag) {
  const m = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i"));
  return m ? decodeEntities(m[1]) : "";
}

// Atom <link href="..."/> (prefer rel="alternate")
function atomLink(block) {
  const links = [...block.matchAll(/<link\b[^>]*\/?>(?:<\/link>)?/gi)].map((m) => m[0]);
  let href = "";
  for (const l of links) {
    const rel = (l.match(/rel="([^"]*)"/i) || [])[1] || "alternate";
    const h = (l.match(/href="([^"]*)"/i) || [])[1];
    if (h && rel === "alternate") return h;
    if (h && !href) href = h;
  }
  return href;
}

// Returns the parsed epoch, or null when the feed gives no usable date. NULL is
// the clean "date unknown" signal — the engine then dates the item by when we
// first caught it (and penalises its age), instead of pretending it's brand new.
function parseDate(s) {
  if (!s) return null;
  const t = Date.parse(s);
  return Number.isNaN(t) ? null : t;
}

function parseFeed(xml, feed) {
  const out = [];
  // RSS <item> ... </item>
  const items = [...xml.matchAll(/<item\b[\s\S]*?<\/item>/gi)].map((m) => m[0]);
  if (items.length) {
    for (const block of items) {
      const title = firstTag(block, "title");
      const link = firstTag(block, "link") || (block.match(/<link[^>]*>([^<]+)/i) || [])[1] || "";
      const date = firstTag(block, "pubDate") || firstTag(block, "dc:date");
      const desc = firstTag(block, "description") || firstTag(block, "content:encoded") || firstTag(block, "summary");
      if (!title || !link) continue;
      out.push(makeEntry(feed, title, link.trim(), parseDate(date), clip(desc, 300)));
    }
    return out;
  }
  // Atom <entry> ... </entry>
  const entries = [...xml.matchAll(/<entry\b[\s\S]*?<\/entry>/gi)].map((m) => m[0]);
  for (const block of entries) {
    const title = firstTag(block, "title");
    const link = atomLink(block);
    const date = firstTag(block, "updated") || firstTag(block, "published");
    const desc = firstTag(block, "summary") || firstTag(block, "content");
    if (!title || !link) continue;
    out.push(makeEntry(feed, title, link.trim(), parseDate(date), clip(desc, 300)));
  }
  return out;
}

function makeEntry(feed, title, url, published, summary) {
  return {
    sourceId: feed.id,
    sourceType: feed.type,
    domain: feed.domain,
    weight: feed.weight,
    title,
    summary: summary || "",
    url,
    links: [{ type: "article", url, label: feed.name || feed.id }],
    rawScore: 1, // RSS has no popularity signal; baseline is recency/volume-driven
    published,
  };
}

// ---- per-source ingest ----
async function ingestRss(feed) {
  const xml = await fetchText(feed.url, "application/rss+xml, application/atom+xml, application/xml, text/xml");
  return parseFeed(xml, feed).slice(0, 60);
}

async function ingestHn(feed) {
  const data = await fetchJson(feed.url);
  const out = [];
  for (const hit of data.hits || []) {
    const title = hit.title || hit.story_title;
    if (!title) continue;
    const hnUrl = `https://news.ycombinator.com/item?id=${hit.objectID}`;
    const links = [{ type: "discussion", url: hnUrl, label: "HN", count: hit.num_comments || 0 }];
    if (hit.url) links.unshift({ type: "article", url: hit.url, label: "Article" });
    out.push({
      sourceId: feed.id,
      sourceType: "hn",
      domain: feed.domain,
      weight: feed.weight,
      title,
      summary: `${hit.points || 0} points · ${hit.num_comments || 0} comments on Hacker News`,
      url: hit.url || hnUrl,
      links,
      rawScore: (hit.points || 0) + (hit.num_comments || 0) * 0.5,
      published: (hit.created_at_i || Math.floor(Date.now() / 1000)) * 1000,
      commentsUrl: hnUrl,
    });
  }
  return out;
}

async function ingestBluesky(handle) {
  const url = `https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=${encodeURIComponent(
    handle.handle
  )}&limit=30&filter=posts_no_replies`;
  const data = await fetchJson(url);
  const out = [];
  for (const f of data.feed || []) {
    const post = f.post;
    if (!post || !post.record || !post.record.text) continue;
    const text = post.record.text.split("\n")[0].slice(0, 200);
    const rkey = post.uri.split("/").pop();
    const webUrl = `https://bsky.app/profile/${handle.handle}/post/${rkey}`;
    out.push({
      sourceId: handle.id,
      sourceType: "bluesky",
      domain: handle.domain,
      weight: handle.weight,
      title: text,
      summary: "",
      url: webUrl,
      links: [{ type: "post", url: webUrl, label: `@${handle.handle}` }],
      rawScore: (post.likeCount || 0) + (post.repostCount || 0) * 1.5,
      published: parseDate(post.indexedAt || post.record.createdAt),
    });
  }
  return out;
}

// ---- Reddit (public JSON now; OAuth Data API when secrets are set) ----
// Read-only top/day per subreddit. Works immediately via www.reddit.com/.json;
// if REDDIT_CLIENT_ID/SECRET are present it uses an app-only token against
// oauth.reddit.com (the approved Data API path) — same response shape. Links
// target the comments permalink (§5); the comment count rides on the discussion
// link so it survives clustering + persistence with no schema change.
let _redditToken = null; // { token, exp } — cached across the run

async function redditAppToken(env) {
  const id = env && env.REDDIT_CLIENT_ID;
  const secret = env && env.REDDIT_CLIENT_SECRET;
  if (!id || !secret) return null;
  if (_redditToken && _redditToken.exp > Date.now() + 60000) return _redditToken.token;
  try {
    const resp = await fetch("https://www.reddit.com/api/v1/access_token", {
      method: "POST",
      headers: {
        "User-Agent": UA,
        Authorization: "Basic " + btoa(`${id}:${secret}`),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    if (!data.access_token) return null;
    _redditToken = { token: data.access_token, exp: Date.now() + (data.expires_in || 3600) * 1000 };
    return _redditToken.token;
  } catch {
    return null;
  }
}

function subFromFeed(feed) {
  // Captures a single sub OR a multireddit ("a+b+c"); `+` is part of the path.
  const m = /reddit\.com\/r\/([A-Za-z0-9_+]+)/i.exec(feed.url || "");
  return (m && m[1]) || feed.subreddit || null;
}

async function ingestReddit(feed, env) {
  const sub = subFromFeed(feed);
  if (!sub) return [];
  const token = await redditAppToken(env);

  // No OAuth → public per-subreddit `.rss` (Atom). This is NOT the JSON Data API,
  // so it isn't approval-gated; it works today through the generic feed parser.
  // The link is the comments permalink (a discussion thread); comment counts
  // aren't in the RSS, so they arrive later once OAuth is configured.
  if (!token) {
    const xml = await fetchText(
      `https://www.reddit.com/r/${sub}/.rss?limit=25`,
      "application/atom+xml, application/rss+xml, application/xml, text/xml"
    );
    return parseFeed(xml, feed).map((e) => ({
      ...e,
      sourceType: "reddit",
      summary: `r/${sub}`,
      links: [{ type: "discussion", url: e.url, label: `r/${sub}` }],
      commentsUrl: e.url,
    }));
  }

  // OAuth Data API → top/day with scores + comment counts.
  const resp = await fetch(`https://oauth.reddit.com/r/${sub}/top?t=day&limit=25`, {
    headers: { "User-Agent": UA, Accept: "application/json", Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = await resp.json();
  const out = [];
  for (const child of (data.data && data.data.children) || []) {
    const p = child && child.data;
    if (!p || !p.title || p.stickied) continue;
    const permalink = `https://www.reddit.com${p.permalink}`;
    const comments = p.num_comments || 0;
    const isSelf = p.is_self || !p.url || /(^|\/\/)([a-z]+\.)?reddit\.com/i.test(p.url);
    const links = [];
    if (!isSelf && p.url) links.push({ type: "article", url: p.url, label: `r/${sub}` });
    links.push({ type: "discussion", url: permalink, label: `r/${sub}`, count: comments });
    out.push({
      sourceId: feed.id,
      sourceType: "reddit",
      domain: feed.domain,
      weight: feed.weight,
      title: decodeEntities(p.title),
      summary: `${p.score || 0} upvotes · ${comments} comments · r/${sub}`,
      url: isSelf ? permalink : p.url,
      links,
      rawScore: (p.score || 0) + comments * 0.5,
      published: (p.created_utc || Math.floor(Date.now() / 1000)) * 1000,
      commentsUrl: permalink,
    });
  }
  return out;
}

// Ingest every enabled source. Returns { entries[], live[], dead[] } where
// `dead` is the ids of sources that errored or returned nothing (the caller can
// surface these in-app for pruning; we drop them gracefully this run).
export async function ingestAll(config, env) {
  const entries = [];
  const live = [];
  const dead = [];
  const jobs = [];

  // Reddit gets fetched sequentially with a stagger (below), not concurrently —
  // hammering Reddit with every feed at once trips its per-IP rate limit and most
  // come back empty. Everything else runs concurrently.
  const redditFeeds = [];
  for (const feed of config.sources || []) {
    if (feed.enabled === false) continue;
    if (feed.type === "reddit") { redditFeeds.push(feed); continue; }
    jobs.push(
      (async () => {
        try {
          const got = feed.type === "hn" ? await ingestHn(feed) : await ingestRss(feed);
          if (got.length) {
            entries.push(...got);
            live.push(feed.id);
          } else {
            dead.push(feed.id);
          }
        } catch (e) {
          dead.push(feed.id);
        }
      })()
    );
  }
  for (const h of config.bluesky || []) {
    if (h.enabled === false || !h.handle) continue;
    jobs.push(
      (async () => {
        try {
          const got = await ingestBluesky(h);
          if (got.length) {
            entries.push(...got);
            live.push(h.id);
          } else dead.push(h.id);
        } catch {
          dead.push(h.id);
        }
      })()
    );
  }

  await Promise.allSettled(jobs);

  // Reddit: one feed at a time with a short gap, so we stay under the rate limit.
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let i = 0; i < redditFeeds.length; i++) {
    const feed = redditFeeds[i];
    try {
      const got = await ingestReddit(feed, env);
      if (got.length) { entries.push(...got); live.push(feed.id); }
      else dead.push(feed.id);
    } catch {
      dead.push(feed.id);
    }
    if (i < redditFeeds.length - 1) await sleep(600);
  }

  return { entries, live, dead };
}
