/*
 * The Signal — Service Worker
 *
 * Strategy:
 *   - App shell (index.html, shared CSS/JS, manifest, icons)
 *       precached on install. Cache-first thereafter.
 *   - Per-issue HTML (under /issues/) — cache-first with network fallback.
 *       Once an issue has been read online, it's available offline forever.
 *   - Cached images (under /assets/cached/) — cache-first.
 *       These are same-origin after the image-mirroring backfill, so caching
 *       is efficient (no opaque-response quota cost).
 *   - The archive index — stale-while-revalidate, so new issues appear when
 *       online without blocking the offline read.
 *   - External images (Google Fonts, anything still on a third-party host)
 *       — runtime cached as opaque responses. Still works offline; counts
 *       toward quota but the volume is small after the backfill.
 *
 * Versioning: bump CACHE_VERSION when shared assets change in a breaking
 * way. Old caches are deleted on activate.
 */

const CACHE_VERSION = "v2";
const SHELL_CACHE = `signal-shell-${CACHE_VERSION}`;
const ISSUE_CACHE = `signal-issues-${CACHE_VERSION}`;
const IMAGE_CACHE = `signal-images-${CACHE_VERSION}`;
const EXTERNAL_CACHE = `signal-external-${CACHE_VERSION}`;

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
      // Use addAll with a tolerant fallback — if one shell asset is missing,
      // don't fail the whole install.
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
// Match options: ignoreVary because Cloudflare sets `Vary: Accept-Encoding`,
// which causes default match() to miss cached entries when the browser's
// negotiated encoding differs between online and offline contexts. Without
// this, navigation requests cached online don't satisfy offline navigations.
const MATCH_OPTS = { ignoreVary: true };

async function cacheFirst(req, cacheName, opts = {}) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req, MATCH_OPTS);
  if (cached) return cached;

  try {
    const fetchOpts = opts.allowOpaque ? { mode: "no-cors", credentials: "omit" } : {};
    const resp = await fetch(req, fetchOpts);
    if (resp && (resp.ok || resp.type === "opaque")) {
      // Store under the request URL stripped of any query string so cache hits
      // are insensitive to ?cb=... / ?v=... cache-bust suffixes.
      const cacheKey = new Request(req.url.split("?")[0], { method: "GET" });
      cache.put(cacheKey, resp.clone()).catch(() => {});
    }
    return resp;
  } catch (err) {
    // Network failed — try cache fallback on the normalised URL.
    const fallback = await cache.match(req.url.split("?")[0], MATCH_OPTS);
    if (fallback) return fallback;
    // For navigation requests, fall back to the cached index so the user
    // sees the archive instead of Chrome's offline error page.
    if (req.mode === "navigate") {
      const indexCache = await caches.open(SHELL_CACHE);
      const index = (await indexCache.match("/", MATCH_OPTS)) || (await indexCache.match("/index.html", MATCH_OPTS));
      if (index) return index;
    }
    throw err;
  }
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req, MATCH_OPTS);
  const cacheKey = new Request(req.url.split("?")[0], { method: "GET" });
  const fetchPromise = fetch(req)
    .then((resp) => {
      if (resp && resp.ok) cache.put(cacheKey, resp.clone()).catch(() => {});
      return resp;
    })
    .catch(() => cached);
  return cached || fetchPromise;
}
