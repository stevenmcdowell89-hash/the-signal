// GET /api/resolve-feed?url=…  — token-gated feed auto-discovery for the
// settings "Find a feed" box. Fetches the given page, and either confirms it is
// already a feed or follows its advertised <link rel="alternate"
// type="application/rss+xml|atom+xml"> to a real feed URL, validating that the
// result parses. Returns { ok, feed_url, title, items, already_feed? } or
// { ok:false, reason, suggest? }. The engine is unchanged — the caller stores
// feed_url as an ordinary rss source.
//
// This fetches an arbitrary URL server-side, so it is owner-only (same token as
// /api/config) and restricted to public http(s) hosts.

import { UA, parseFeed, discoverFeedUrl } from "../daily/ingest.js";
import { tokenOk } from "./config.js";

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

const msg = (e) => String((e && e.message) || e || "error").slice(0, 80);

// Block loopback / link-local / private ranges so the endpoint can't be used to
// probe internal services (basic SSRF guard for a single-user app).
function isInternalHost(host) {
  const h = (host || "").toLowerCase();
  if (h === "localhost" || h.endsWith(".local") || h.endsWith(".internal")) return true;
  if (h === "::1" || h === "0.0.0.0") return true;
  const m = h.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (m) {
    const [a, b] = [Number(m[1]), Number(m[2])];
    if (a === 127 || a === 10 || a === 0) return true;
    if (a === 169 && b === 254) return true;
    if (a === 192 && b === 168) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
  }
  return false;
}

// First <title> in the document — the channel/feed title in RSS and Atom (it
// precedes item/entry titles), with the common entities decoded for display.
function feedTitle(xml) {
  const t = (xml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || "";
  return t
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .trim();
}

const googleNews = (host) =>
  `https://news.google.com/rss/search?q=site:${encodeURIComponent(host)}%20when:7d`;

// Cap the bytes we ever run regex over. Real feeds are well under this; a page
// that's actually a multi-MB HTML document would otherwise risk blowing the
// Worker's CPU budget on the parse passes (which would kill the request and
// return an empty body to the client).
const MAX_DOC = 2_000_000;

async function fetchWithTimeout(url, accept, ms = 10000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const resp = await fetch(url, {
      headers: { "User-Agent": UA, Accept: accept },
      redirect: "follow",
      signal: ctrl.signal,
      cf: { cacheTtl: 60, cacheEverything: false },
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const text = await resp.text();
    return text.length > MAX_DOC ? text.slice(0, MAX_DOC) : text;
  } finally {
    clearTimeout(timer);
  }
}

const HTML_ACCEPT = "text/html,application/xhtml+xml,application/rss+xml;q=0.9,*/*;q=0.8";
const FEED_ACCEPT = "application/rss+xml, application/atom+xml, application/xml, text/xml";

export async function onRequestGet({ request, env }) {
  // Last-resort guard: this handler fetches arbitrary URLs and runs regex over
  // their (untrusted, possibly malformed) content. Any unexpected throw here
  // would otherwise surface to the browser as an empty 500 body, which the
  // client can only report as "Unexpected end of JSON input". Always answer JSON.
  try {
    if (!tokenOk(request, env)) return json({ ok: false, error: "unauthorized" }, 401);

    const raw = (new URL(request.url).searchParams.get("url") || "").trim();
    let target;
    try { target = new URL(raw); } catch { return json({ ok: false, reason: "Enter a valid URL." }); }
    if (target.protocol !== "http:" && target.protocol !== "https:")
      return json({ ok: false, reason: "Only http(s) URLs are supported." });
    if (isInternalHost(target.hostname))
      return json({ ok: false, reason: "That host isn't allowed." });

    let body;
    try { body = await fetchWithTimeout(target.href, HTML_ACCEPT); }
    catch (e) { return json({ ok: false, reason: `Couldn't fetch that page (${msg(e)}).` }); }

    // 1. The pasted URL is already a feed.
    const direct = parseFeed(body, { id: "probe", type: "rss" });
    if (direct.length)
      return json({ ok: true, feed_url: target.href, title: feedTitle(body) || target.hostname, items: direct.length, already_feed: true });

    // 2. Follow an advertised feed link.
    const feedUrl = discoverFeedUrl(body, target.href);
    if (!feedUrl)
      return json({ ok: false, reason: "No feed advertised on this page.", suggest: googleNews(target.hostname) });

    // 3. Validate the discovered feed actually parses.
    let feedBody;
    try { feedBody = await fetchWithTimeout(feedUrl, FEED_ACCEPT); }
    catch (e) { return json({ ok: false, reason: `Found a feed link but couldn't fetch it (${msg(e)}).`, feed_url: feedUrl }); }
    const items = parseFeed(feedBody, { id: "probe", type: "rss" });
    if (!items.length)
      return json({ ok: false, reason: "The advertised link wasn't a readable feed.", feed_url: feedUrl, suggest: googleNews(target.hostname) });

    return json({ ok: true, feed_url: feedUrl, title: feedTitle(feedBody) || target.hostname, items: items.length });
  } catch (e) {
    return json({ ok: false, reason: `Feed lookup failed (${msg(e)}).` }, 500);
  }
}
