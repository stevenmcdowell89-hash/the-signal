/*
 * The Signal — Service Worker
 *
 * Strategy:
 *   - App shell (index.html, shared CSS/JS, manifest, icons)
 *       precached on install. Cache-first thereafter.
 *   - Per-issue HTML (under /issues/) — cache-first with network fallback.
 *       Once an issue has been read online, it's available offline forever.
 *   - Cached images (under /assets/cached/) — cache-first.
 *   - The archive index — stale-while-revalidate.
 *   - External images (fonts, anything still on a third-party host) —
 *       runtime cached as opaque responses.
 *
 * Diagnostic endpoint:
 *   /sw-status  → JSON report of SW version + cache contents. Visit from
 *                 the phone to verify what's actually cached.
 */

const CACHE_VERSION = "v6";
const SHELL_CACHE = `signal-shell-${CACHE_VERSION}`;
const ISSUE_CACHE = `signal-issues-${CACHE_VERSION}`;
const IMAGE_CACHE = `signal-images-${CACHE_VERSION}`;
const EXTERNAL_CACHE = `signal-external-${CACHE_VERSION}`;

// Match options: needed for Cloudflare-served content.
//   ignoreVary  — Cloudflare sets `Vary: Accept-Encoding`, which makes
//                 default match() miss when the offline browser's
//                 encoding negotiation differs from the cached value.
//   ignoreSearch — query-string drift (?cb=…, ?v=…) doesn't break matches.
const MATCH_OPTS = { ignoreVary: true, ignoreSearch: true };

// URL normalization: with html_handling="none" in wrangler.jsonc, Cloudflare
// no longer redirects /foo.html → /foo. But to be robust against any
// historical inconsistency (and against re-introducing a redirect later),
// canonicalize URLs by stripping a trailing .html before using them as
// cache keys or match keys. /foo and /foo.html become the same cache entry.
function canonicalUrl(req) {
  const u = new URL(req.url);
  u.search = "";
  u.hash = "";
  if (u.pathname.endsWith(".html")) u.pathname = u.pathname.slice(0, -5);
  return u.toString();
}

const SHELL_ASSETS = [
  "/",
  "/index.html",
  "/assets/styles.css",
  "/assets/script.js",
  "/assets/icons/icon-192.png",
  "/assets/icons/icon-512.png",
  "/assets/icons/apple-touch-icon.png",
];

// --- Install: precache the app shell + every issue from the index ---------
self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL_CACHE);
    await Promise.all(
      SHELL_ASSETS.map((url) =>
        cache.add(url).catch((err) => {
          console.warn(`[sw] shell precache miss: ${url}`, err);
        }),
      ),
    );
    // Crawl the index for issue HTML + cover URLs and pre-fetch them.
    // Best-effort: never fail install over the precache.
    try { await precacheFromIndex(); }
    catch (err) { console.warn("[sw] precache-from-index failed:", err); }
  })());
  // Don't auto-skipWaiting here. The page checks for a previous controller
  // and posts SKIP_WAITING explicitly — either immediately (first install,
  // no controller) or after the user taps the update banner's Refresh.
});

// --- Message handler --------------------------------------------------------
self.addEventListener("message", (event) => {
  if (!event.data || !event.data.type) return;
  if (event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
  if (event.data.type === "PRECACHE_ALL") {
    // Page-driven top-up: catches new issues that have appeared since this
    // SW installed.
    event.waitUntil(precacheFromIndex().catch((err) => {
      console.warn("[sw] precache-from-index (top-up) failed:", err);
    }));
  }
});

// --- Activate: clean up old caches -----------------------------------------
self.addEventListener("activate", (event) => {
  const KEEP = new Set([SHELL_CACHE, ISSUE_CACHE, IMAGE_CACHE, EXTERNAL_CACHE]);
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => (KEEP.has(k) ? null : caches.delete(k))));
    // Evict the stale manifest from any previous version that cached it,
    // so a PWA reinstall fetches fresh from the network on the next try.
    try {
      const shell = await caches.open(SHELL_CACHE);
      await shell.delete("/manifest.json", { ignoreSearch: true });
    } catch (_) {}
  })());
  self.clients.claim();
});

// --- Precache discovery -----------------------------------------------------
// Fetches /index.html, extracts issue + cover URLs, and pre-fetches anything
// not already cached. HTML and covers only — in-issue images stay lazy (the
// existing cache-first route picks them up on first view) to keep the
// install footprint reasonable.
async function precacheFromIndex() {
  const indexResp = await fetch("/index.html", { cache: "no-cache" });
  if (!indexResp.ok) return;
  const html = await indexResp.text();

  const issueRe = /href="(issues\/[^"]+\.html)"/g;
  const slugRe = /data-cover-slug="([^"]+)"/g;
  const issueUrls = [...new Set([...html.matchAll(issueRe)].map((m) => "/" + m[1]))];
  const slugs = [...new Set([...html.matchAll(slugRe)].map((m) => m[1]))];
  const coverUrls = slugs.map((s) => `/assets/covers/${s}.jpg`);

  const issueCache = await caches.open(ISSUE_CACHE);
  const imageCache = await caches.open(IMAGE_CACHE);

  await Promise.all([
    ...issueUrls.map((url) => maybeFetchAndPut(issueCache, url)),
    ...coverUrls.map((url) => maybeFetchAndPut(imageCache, url)),
  ]);
}

async function maybeFetchAndPut(cache, url) {
  // putInCache stores under the canonical (no-.html) URL; check that first
  // so we don't re-fetch every visit just because the lookup key didn't match.
  const req = new Request(url);
  const canonical = canonicalUrl(req);
  let existing = await cache.match(canonical, MATCH_OPTS);
  if (!existing) existing = await cache.match(req, MATCH_OPTS);
  if (existing) return;
  try {
    const resp = await fetch(url);
    if (resp.ok) await putInCache(cache, req, resp);
  } catch (err) {
    // Best effort — individual misses don't fail the batch.
    console.warn(`[sw] precache miss: ${url}`, err);
  }
}

// --- Push: new-issue notification + deep pre-cache --------------------------
// On push, the SW wakes, fetches the new issue HTML + cover + every inline
// /assets/cached/ image, writes them to the appropriate caches, THEN shows
// the OS notification. By the time the user taps it (or just leaves the
// device idle), the entire issue is offline-ready.
self.addEventListener("push", (event) => {
  event.waitUntil((async () => {
    let data = {};
    try { data = event.data ? event.data.json() : {}; }
    catch (_) { /* non-JSON payload */ }

    const title = data.title || "The Signal";
    const body = data.body || "A new issue is live.";
    const url = data.url || "/";
    const image = data.image || undefined;
    const slug = data.slug || undefined;

    if (url && url !== "/") {
      try { await deepPrecacheIssue(url); }
      catch (err) { console.warn("[sw] deep pre-cache failed:", err); }
    }

    await self.registration.showNotification(title, {
      body,
      icon: "/assets/icons/icon-192.png",
      badge: "/assets/icons/icon-192.png",
      image,
      tag: slug ? `signal-${slug}` : "signal-issue",
      renotify: true,
      data: { url },
    });
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil((async () => {
    const target = new URL(targetUrl, self.location.origin);
    const clients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of clients) {
      const u = new URL(client.url);
      if (u.origin === target.origin && u.pathname === target.pathname) {
        return client.focus();
      }
    }
    return self.clients.openWindow(target.href);
  })());
});

// Fetch issue HTML + cover + every inline /assets/cached/ image referenced
// by the HTML. Idempotent: skips anything already cached.
async function deepPrecacheIssue(issueUrl) {
  const issueCache = await caches.open(ISSUE_CACHE);
  const imageCache = await caches.open(IMAGE_CACHE);

  let html;
  const req = new Request(issueUrl);
  const canonical = canonicalUrl(req);
  let cached = await issueCache.match(canonical, MATCH_OPTS);
  if (!cached) cached = await issueCache.match(req, MATCH_OPTS);
  if (cached) {
    html = await cached.clone().text();
  } else {
    const resp = await fetch(issueUrl);
    if (!resp.ok) return;
    html = await resp.clone().text();
    await putInCache(issueCache, req, resp);
  }

  const imgRe = /src="(\/assets\/(?:cached|covers)\/[^"]+)"/g;
  const imageUrls = [...new Set([...html.matchAll(imgRe)].map((m) => m[1]))];
  await Promise.all(imageUrls.map((u) => maybeFetchAndPut(imageCache, u)));
}

// --- Fetch routing ----------------------------------------------------------
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;

  // Diagnostic endpoint
  if (sameOrigin && url.pathname === "/sw-status") {
    event.respondWith(buildStatusResponse());
    return;
  }

  // Don't intercept the PWA manifest — let the browser fetch fresh on every
  // install attempt. Caching it makes orientation/scope/theme changes
  // require a SW update + activation before they propagate to a reinstall.
  if (sameOrigin && url.pathname === "/manifest.json") {
    return;
  }

  if (sameOrigin && url.pathname.startsWith("/issues/")) {
    // Stale-while-revalidate, NOT cache-first: serve the cached copy
    // immediately (so offline + fast paint both work) AND fetch in the
    // background so any post-publish fixes to the issue HTML reach the
    // reader the *next* time they open it. Pure cache-first means a
    // shipped bug stays shipped on every cached device forever.
    event.respondWith(staleWhileRevalidate(req, ISSUE_CACHE));
    return;
  }
  if (sameOrigin && url.pathname.startsWith("/assets/cached/")) {
    event.respondWith(cacheFirst(req, IMAGE_CACHE));
    return;
  }
  if (sameOrigin && (url.pathname === "/" || url.pathname === "/index.html")) {
    event.respondWith(staleWhileRevalidate(req, SHELL_CACHE));
    return;
  }
  if (sameOrigin) {
    event.respondWith(cacheFirst(req, SHELL_CACHE));
    return;
  }

  // Cross-origin: fonts, any external images that didn't get mirrored
  event.respondWith(cacheFirst(req, EXTERNAL_CACHE, { allowOpaque: true }));
});

// --- Strategies -------------------------------------------------------------

async function cacheFirst(req, cacheName, opts = {}) {
  const cache = await caches.open(cacheName);
  const canonical = canonicalUrl(req);
  // Look up under both the canonical (no .html) and the request URL forms.
  let cached = await cache.match(canonical, MATCH_OPTS);
  if (!cached) cached = await cache.match(req, MATCH_OPTS);
  // Defensive: discard cached redirects / non-ok responses (see SWR
  // comment). Opaque responses (cross-origin no-cors) stay — they have
  // type "opaque" and ok=false but are intentional.
  if (cached && !cached.ok && cached.type !== "opaque") {
    try { await cache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await cache.delete(req, MATCH_OPTS); } catch (_) {}
    cached = null;
  }
  if (cached) return cached;

  try {
    // redirect: "follow" mirrors the SWR fix — get the final 200 in one
    // hop instead of an opaqueredirect that has to round-trip.
    const fetchOpts = opts.allowOpaque
      ? { mode: "no-cors", credentials: "omit" }
      : { method: "GET", credentials: "same-origin", redirect: "follow" };
    const resp = opts.allowOpaque
      ? await fetch(req, fetchOpts)
      : await fetch(req.url, fetchOpts);
    if (resp && (resp.ok || resp.type === "opaque")) {
      await putInCache(cache, req, resp);
    }
    return resp;
  } catch (err) {
    // Network failed — last-resort attempts.
    const fallback =
      (await cache.match(canonical, MATCH_OPTS)) ||
      (await cache.match(req, MATCH_OPTS));
    if (fallback) return fallback;
    if (req.mode === "navigate") {
      const indexCache = await caches.open(SHELL_CACHE);
      const index =
        (await indexCache.match("/", MATCH_OPTS)) ||
        (await indexCache.match("/index.html", MATCH_OPTS));
      if (index) return index;
    }
    throw err;
  }
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  // Mirror cacheFirst: putInCache stores under the canonical (no-.html) key,
  // so the lookup has to try canonical first or .html requests always miss
  // and silently fall through to the network — which returns undefined
  // when offline. This is what broke offline issue access (PR #106).
  const canonical = canonicalUrl(req);
  let cached = await cache.match(canonical, MATCH_OPTS);
  if (!cached) cached = await cache.match(req, MATCH_OPTS);

  // Defensive: throw out any cached entry that isn't a proper 2xx response.
  // A previous buggy SW version may have stored an opaqueredirect under the
  // canonical key — without this check, every reopen of an issue served the
  // redirect back to the browser, which followed it, hit the SW again, hit
  // the same cached redirect, and looped. Today's putInCache won't write
  // these (.ok check is in place), but old caches on existing devices can.
  if (cached && (!cached.ok || cached.type === "opaqueredirect")) {
    try { await cache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await cache.delete(req, MATCH_OPTS); } catch (_) {}
    cached = null;
  }

  // Use redirect: "follow" on the network fetch. Navigation requests have
  // req.redirect === "manual", which means fetch(req) returns an
  // opaqueredirect Response when CF responds with a 307 (.html → no-.html).
  // That forces a round-trip through the browser's navigation flow and
  // re-enters the SW for the redirected URL — fragile, and the source of
  // the May 2026 "issues don't load" bug. Fetching the URL string with
  // explicit follow gives us the final 200 response in one hop, which is
  // what putInCache and the browser both want.
  const fetchPromise = fetch(req.url, {
    method: "GET",
    credentials: "same-origin",
    redirect: "follow",
  })
    .then((resp) => {
      if (resp && resp.ok) putInCache(cache, req, resp);
      return resp;
    })
    .catch(() => cached);
  return cached || fetchPromise;
}

// --- Cache write with robust fallback --------------------------------------
// cache.put() can fail for several reasons that don't surface clearly:
//   - response has forbidden headers (Set-Cookie, etc.)
//   - request is a "navigate" mode request and the implementation rejects it
//   - storage quota exceeded
// We try the original Request first, then fall back to a clean URL-string
// key, then record the failure into a debug cache so /sw-status can show it.
async function putInCache(cache, req, resp) {
  // Always key by the canonical URL so /foo.html and /foo (after a
  // Cloudflare redirect, or if it ever comes back) share one cache entry.
  const canonical = canonicalUrl(req);
  const respClone = resp.clone();

  try {
    const canonicalReq = new Request(canonical, { method: "GET", mode: "same-origin", credentials: "same-origin" });
    await cache.put(canonicalReq, respClone);
    return;
  } catch (err1) {
    // Synthetic Request rejected — fall back to the original.
    try {
      await cache.put(req, resp.clone());
      return;
    } catch (err2) {
      // Both failed — log to debug cache (visible via /sw-status).
      try {
        const debugCache = await caches.open("signal-debug");
        const entry = new Response(
          JSON.stringify({
            ts: new Date().toISOString(),
            url,
            err1: String(err1 && err1.message),
            err2: String(err2 && err2.message),
            reqMode: req.mode,
            respStatus: resp.status,
            respHeaders: [...resp.headers.entries()].slice(0, 20),
          }),
          { headers: { "Content-Type": "application/json" } },
        );
        await debugCache.put(`/_debug/${Date.now()}_${encodeURIComponent(url)}`, entry);
      } catch (_) {}
    }
  }
}

// --- /sw-status diagnostic endpoint ----------------------------------------
async function buildStatusResponse() {
  const cacheNames = await caches.keys();
  const buckets = {};
  for (const name of cacheNames) {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    buckets[name] = {
      count: keys.length,
      sample: keys.slice(0, 30).map((r) => r.url),
    };
  }

  // Surface any debug-cache entries (failed cache.put attempts)
  const failures = [];
  try {
    const debugCache = await caches.open("signal-debug");
    const debugKeys = await debugCache.keys();
    for (const k of debugKeys.slice(0, 20)) {
      const r = await debugCache.match(k);
      if (r) failures.push(await r.json());
    }
  } catch (_) {}

  const body = JSON.stringify(
    {
      sw_version: CACHE_VERSION,
      ts: new Date().toISOString(),
      caches: buckets,
      put_failures: failures,
    },
    null,
    2,
  );

  return new Response(body, {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
