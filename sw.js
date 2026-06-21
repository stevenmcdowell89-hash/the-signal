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

const CACHE_VERSION = "v24";
const SHELL_CACHE = `signal-shell-${CACHE_VERSION}`;
const ISSUE_CACHE = `signal-issues-${CACHE_VERSION}`;
const IMAGE_CACHE = `signal-images-${CACHE_VERSION}`;
const EXTERNAL_CACHE = `signal-external-${CACHE_VERSION}`;
// The daily brief's rendered state — network-first with a cache fallback so the
// brief works offline, and silently kept warm overnight via periodic sync (§10).
const DAILY_CACHE = `signal-daily-${CACHE_VERSION}`;
const DAILY_URL = "/api/daily";

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
  if (event.data.type === "CACHE_DAILY") {
    // Page-driven warm of the brief's state into the offline cache.
    event.waitUntil(warmDaily().catch(() => {}));
  }
});

// Refresh the cached daily state from the network. Silent — no badge, no nag;
// the page owns the ambient app badge from its read-watermark (§10).
async function warmDaily() {
  const resp = await fetch(DAILY_URL, { cache: "no-store" });
  if (resp && resp.ok) {
    const cache = await caches.open(DAILY_CACHE);
    await cache.put(DAILY_URL, resp.clone());
  }
  return resp;
}

// Ambient overnight precache: keep the brief warm so it opens instantly offline.
// Support is patchy (Chromium-only, permission-gated) — registration is
// best-effort from the page; this just does the work when it does fire.
self.addEventListener("periodicsync", (event) => {
  if (event.tag === "signal-daily") {
    event.waitUntil(warmDaily().catch(() => {}));
  }
});

// --- Activate: clean up old caches -----------------------------------------
self.addEventListener("activate", (event) => {
  const KEEP = new Set([SHELL_CACHE, ISSUE_CACHE, IMAGE_CACHE, EXTERNAL_CACHE, DAILY_CACHE]);
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
  // Defensive: clear any cached redirected-from-follow Responses left over
  // from the v118 SW; they read as ok=true but the browser refuses to
  // serve them to navigation requests.
  if (existing && (existing.redirected || existing.type === "opaqueredirect" || !existing.ok)) {
    try { await cache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await cache.delete(req, MATCH_OPTS); } catch (_) {}
    existing = null;
  }
  if (existing) return;
  try {
    // Fetch canonical URL so the response is not flagged redirected.
    // See staleWhileRevalidate comment for the full rationale.
    const resp = await fetch(canonical, { credentials: "same-origin" });
    if (resp.ok && !resp.redirected) await putInCache(cache, req, resp);
  } catch (err) {
    // Best effort — individual misses don't fail the batch.
    console.warn(`[sw] precache miss: ${url}`, err);
  }
}

// --- Push: new-issue notification + deep pre-cache --------------------------
// On push, the SW wakes, shows the notification IMMEDIATELY, and then runs
// deepPrecacheIssue in the same waitUntil so the SW stays alive long enough
// to populate ISSUE_CACHE + IMAGE_CACHE with the new issue and its inline
// images. By the time the user taps the notification (or just leaves the
// device idle), the entire issue is offline-ready.
//
// Order matters: notification first, then precache. The 24 May 2026 weekly
// publish revealed a race where the push arrives at the device before
// Cloudflare has finished deploying the new HTML — so the first fetch in
// deepPrecacheIssue 404'd, the function returned silently, and the issue
// never landed in cache. Fix: deepPrecacheIssue now retries with backoff
// (see below) AND we fire the notification first so the user sees it
// without waiting for precache to complete.
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

    // Fire notification first — don't make it wait on precache.
    const notifyPromise = self.registration.showNotification(title, {
      body,
      icon: "/assets/icons/icon-192.png",
      badge: "/assets/icons/icon-192.png",
      image,
      tag: slug ? `signal-${slug}` : "signal-issue",
      renotify: true,
      data: { url },
    });

    // Then run precache in the same waitUntil so the SW stays alive long
    // enough to complete it. Both promises must settle before the SW can
    // be terminated.
    let precachePromise = Promise.resolve();
    if (url && url !== "/") {
      precachePromise = deepPrecacheIssue(url).catch((err) => {
        console.warn("[sw] deep pre-cache threw:", err);
      });
    }

    await Promise.all([notifyPromise, precachePromise]);
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

// Write a diagnostic entry to the signal-debug cache so /sw-status can
// surface what happened. Best-effort; never throws.
async function logDeepPrecache(entry) {
  try {
    const debugCache = await caches.open("signal-debug");
    const key = `/_debug/deep-precache/${Date.now()}_${encodeURIComponent(entry.issueUrl || "unknown")}`;
    await debugCache.put(
      key,
      new Response(JSON.stringify({ ts: new Date().toISOString(), ...entry }), {
        headers: { "Content-Type": "application/json" },
      }),
    );
  } catch (_) { /* swallow */ }
}

// Fetch issue HTML + cover + every inline /assets/cached/ image referenced
// by the HTML. Idempotent: skips anything already cached.
//
// CF-deployment race (24 May 2026 weekly bug): the push to subscribed
// devices fans out within seconds of the GitHub Action firing, which is
// often FASTER than Cloudflare's edge propagation of the newly-pushed
// HTML. The first fetch attempt 404'd and the function returned silently,
// leaving the new issue uncached. Result: user gets the notification,
// opens the PWA offline shortly after, the issue won't load.
//
// Fix: retry the HTML fetch with exponential backoff for up to ~30s
// (covers the typical CF propagation window). Log every attempt + final
// outcome to signal-debug cache so /sw-status surfaces failures.
async function deepPrecacheIssue(issueUrl) {
  const startedAt = Date.now();
  const issueCache = await caches.open(ISSUE_CACHE);
  const imageCache = await caches.open(IMAGE_CACHE);

  let html;
  const req = new Request(issueUrl);
  const canonical = canonicalUrl(req);
  let cached = await issueCache.match(canonical, MATCH_OPTS);
  if (!cached) cached = await issueCache.match(req, MATCH_OPTS);
  // Drop poisoned entries (redirected/opaqueredirect/non-ok) so the push
  // flow doesn't reuse them and short-circuit the refetch.
  if (cached && (cached.redirected || cached.type === "opaqueredirect" || !cached.ok)) {
    try { await issueCache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await issueCache.delete(req, MATCH_OPTS); } catch (_) {}
    cached = null;
  }
  if (cached) {
    html = await cached.clone().text();
    await logDeepPrecache({ issueUrl, canonical, outcome: "served-from-existing-cache" });
  } else {
    // Retry-on-non-2xx with exponential backoff. Total budget ~31s
    // (1+2+4+8+16). CF edge propagation usually completes well within
    // 5-10s but the budget gives margin for slow days.
    const backoffsMs = [0, 1000, 2000, 4000, 8000, 16000];
    let resp = null;
    const attempts = [];
    for (let i = 0; i < backoffsMs.length; i++) {
      if (backoffsMs[i] > 0) await new Promise((r) => setTimeout(r, backoffsMs[i]));
      try {
        resp = await fetch(canonical, { credentials: "same-origin", cache: "no-store" });
        attempts.push({ i, status: resp.status, redirected: resp.redirected, ok: resp.ok });
        if (resp.ok && !resp.redirected) break;
        resp = null;
      } catch (err) {
        attempts.push({ i, error: String((err && err.message) || err) });
        resp = null;
      }
    }
    if (!resp) {
      await logDeepPrecache({
        issueUrl, canonical, outcome: "html-fetch-failed-after-retries",
        attempts, elapsedMs: Date.now() - startedAt,
      });
      return;
    }
    html = await resp.clone().text();
    await putInCache(issueCache, req, resp);
    await logDeepPrecache({
      issueUrl, canonical, outcome: "cached-html",
      attempts, elapsedMs: Date.now() - startedAt,
    });
  }

  const imgRe = /src="(\/assets\/(?:cached|covers)\/[^"]+)"/g;
  const imageUrls = [...new Set([...html.matchAll(imgRe)].map((m) => m[1]))];
  const imageResults = await Promise.allSettled(
    imageUrls.map((u) => maybeFetchAndPut(imageCache, u)),
  );
  const imageFailures = imageResults.filter((r) => r.status === "rejected").length;
  await logDeepPrecache({
    issueUrl, canonical, outcome: "complete",
    imagesTotal: imageUrls.length,
    imagesFailed: imageFailures,
    elapsedMs: Date.now() - startedAt,
  });
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

  // API routes: the daily state is network-first with an offline cache
  // fallback; everything else under /api/ (config reads, token-gated writes,
  // manual run) must NEVER be cached — let the browser fetch it normally.
  if (sameOrigin && url.pathname.startsWith("/api/")) {
    if (url.pathname === DAILY_URL) {
      event.respondWith(networkFirstDaily(req));
    }
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

// Network-first for the daily brief: fresh when online, last-good when offline.
async function networkFirstDaily(req) {
  const cache = await caches.open(DAILY_CACHE);
  try {
    const resp = await fetch(req, { cache: "no-store" });
    if (resp && resp.ok) await cache.put(DAILY_URL, resp.clone());
    return resp;
  } catch (err) {
    const cached = await cache.match(DAILY_URL);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ generated_at: 0, status: { caught_up: false }, top_catches: [], sections: [], also: [], below_fold: [], today_tonight: [], footer: { kept: 0, scanned: 0, sources: 0, below_fold_count: 0 } }),
      { headers: { "content-type": "application/json" } }
    );
  }
}

async function cacheFirst(req, cacheName, opts = {}) {
  const cache = await caches.open(cacheName);
  const canonical = canonicalUrl(req);
  // Look up under both the canonical (no .html) and the request URL forms.
  let cached = await cache.match(canonical, MATCH_OPTS);
  if (!cached) cached = await cache.match(req, MATCH_OPTS);
  // Defensive: discard structurally unsafe cached entries (see SWR comment
  // for the full story). Opaque responses (cross-origin no-cors) stay —
  // they have type "opaque" and ok=false but are intentional.
  if (cached && cached.type !== "opaque" && (!cached.ok || cached.redirected || cached.type === "opaqueredirect")) {
    try { await cache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await cache.delete(req, MATCH_OPTS); } catch (_) {}
    cached = null;
  }
  if (cached) return cached;

  try {
    // For same-origin fetches, hit the CANONICAL url so the response
    // doesn't have .redirected=true (which the SW spec forbids serving
    // to navigation requests). For cross-origin opaque fetches, keep the
    // original Request — those can't be canonicalised and don't have
    // the .html-redirect problem.
    const fetchOpts = opts.allowOpaque
      ? { mode: "no-cors", credentials: "omit" }
      : { method: "GET", credentials: "same-origin" };
    const resp = opts.allowOpaque
      ? await fetch(req, fetchOpts)
      : await fetch(canonical, fetchOpts);
    if (resp && (resp.ok || resp.type === "opaque") && !resp.redirected) {
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

  // Defensive: throw out any cached entry that is structurally unsafe to
  // serve to a navigation request. Three kinds get evicted:
  //   - !ok (non-2xx) — would render as an error
  //   - opaqueredirect — would loop the browser through redirects forever
  //   - redirected (followed-from-redirect) — the SW spec forbids serving
  //     these to navigation requests via respondWith. PR #118's first cut
  //     of this fix tried fetch(req.url, {redirect:"follow"}) which made
  //     Responses with redirected=true; the browser then threw a
  //     NetworkError on every reopen of an issue. This delete clears any
  //     poisoned entries from devices that ran the v118 SW.
  if (cached && (!cached.ok || cached.type === "opaqueredirect" || cached.redirected)) {
    try { await cache.delete(canonical, MATCH_OPTS); } catch (_) {}
    try { await cache.delete(req, MATCH_OPTS); } catch (_) {}
    cached = null;
  }

  // Fetch the CANONICAL url (no .html), not the original request URL.
  //
  // CF's html_handling redirects /foo.html → /foo. The canonical URL
  // (no .html) doesn't redirect — it serves the file directly with a 200.
  //
  // If we fetched req.url with redirect:"follow", the resulting Response
  // would have .redirected = true — and the SW spec forbids serving
  // such Responses to navigation requests via respondWith. The browser
  // throws a NetworkError even though the response itself is a perfectly
  // valid 200 with the right HTML body. That was the bug that v118
  // didn't fully fix; it merely changed one symptom (loops) for another
  // (NetworkError on every reopen).
  //
  // Fetching the canonical URL directly: no redirect involved, response
  // has .redirected = false, safe to respondWith for navigations, and
  // safe to cache.put.
  const fetchPromise = fetch(canonical, {
    method: "GET",
    credentials: "same-origin",
  })
    .then((resp) => {
      // Belt-and-braces: only cache + serve responses that are safe.
      if (resp && resp.ok && !resp.redirected) {
        putInCache(cache, req, resp);
      }
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

  // Surface any debug-cache entries — historical putInCache failures AND
  // recent deepPrecacheIssue outcomes (attempts, status, elapsed). Most-
  // recent first by timestamp embedded in the entry payload.
  const debugLog = [];
  try {
    const debugCache = await caches.open("signal-debug");
    const debugKeys = await debugCache.keys();
    for (const k of debugKeys.slice(-40).reverse()) {
      const r = await debugCache.match(k);
      if (r) {
        try { debugLog.push(await r.json()); }
        catch (_) { debugLog.push({ key: k.url, parseError: true }); }
      }
    }
  } catch (_) {}

  const body = JSON.stringify(
    {
      sw_version: CACHE_VERSION,
      ts: new Date().toISOString(),
      caches: buckets,
      debug_log: debugLog,
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
