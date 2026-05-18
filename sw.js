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

const CACHE_VERSION = "v4";
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
  "/manifest.json",
  "/assets/styles.css",
  "/assets/script.js",
  "/assets/icons/icon-192.png",
  "/assets/icons/icon-512.png",
  "/assets/icons/apple-touch-icon.png",
];

// --- Install: precache the app shell ---------------------------------------
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) =>
      Promise.all(
        SHELL_ASSETS.map((url) =>
          cache.add(url).catch((err) => {
            console.warn(`[sw] shell precache miss: ${url}`, err);
          }),
        ),
      ),
    ),
  );
  self.skipWaiting();
});

// --- Activate: clean up old caches -----------------------------------------
self.addEventListener("activate", (event) => {
  const KEEP = new Set([SHELL_CACHE, ISSUE_CACHE, IMAGE_CACHE, EXTERNAL_CACHE]);
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (KEEP.has(k) ? null : caches.delete(k)))),
    ),
  );
  self.clients.claim();
});

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

  if (sameOrigin && url.pathname.startsWith("/issues/")) {
    event.respondWith(cacheFirst(req, ISSUE_CACHE));
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
  if (cached) return cached;

  try {
    const fetchOpts = opts.allowOpaque ? { mode: "no-cors", credentials: "omit" } : {};
    const resp = await fetch(req, fetchOpts);
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
  const cached = await cache.match(req, MATCH_OPTS);
  const fetchPromise = fetch(req)
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
