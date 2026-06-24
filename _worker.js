// The Signal — Cloudflare Worker entry point.
//
// We're on "Workers Static Assets" (not Pages Functions), so /functions/*.js
// is NOT auto-routed. This file is the single Worker script — it dispatches
// /api/* to the handlers in functions/ and falls through to env.ASSETS.fetch()
// for everything else (the static site).
//
// It also owns the Cron Trigger (`scheduled`) that drives the daily brief:
// every few hours the Worker polls sources, runs the triage pipeline, and
// writes the rendered state to KV/D1. See wrangler.jsonc → triggers.crons.

import { onRequestGet as vapidPublicKey } from "./functions/api/vapid-public-key.js";
import { onRequestPost as subscribe } from "./functions/api/subscribe.js";
import { onRequestPost as notify } from "./functions/api/notify.js";
import {
  onRequestGet as configGet,
  onRequestPost as configPost,
} from "./functions/api/config.js";
import {
  onRequestGet as dailyGet,
  onRequestPost as dailyRun,
  onRequestReset as dailyReset,
  onRequestRunStatus as dailyRunStatus,
} from "./functions/api/daily.js";
import { onRequestGet as healthGet } from "./functions/api/health.js";
import { onRequestGet as resolveFeed } from "./functions/api/resolve-feed.js";
import { run as runDaily, getState } from "./functions/daily/pipeline.js";
import { maybePushSignificant } from "./functions/daily/notify.js";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;
    const p = url.pathname;

    // --- Push (existing) ---
    if (p === "/api/vapid-public-key" && method === "GET") return vapidPublicKey({ request, env });
    if (p === "/api/subscribe" && method === "POST") return subscribe({ request, env });
    if (p === "/api/notify" && method === "POST") return notify({ request, env });

    // --- Daily ---
    if (p === "/api/daily" && method === "GET") return dailyGet({ request, env });
    if (p === "/api/daily/run" && method === "POST") return dailyRun({ request, env, ctx });
    if (p === "/api/daily/reset" && method === "POST") return dailyReset({ request, env });
    if (p === "/api/daily/run-status" && method === "GET") return dailyRunStatus({ request, env });
    if (p === "/api/health" && method === "GET") return healthGet({ request, env });

    // --- Config surface (reads open, writes token-gated) ---
    if (p === "/api/config" && method === "GET") return configGet({ request, env });
    if (p === "/api/config" && method === "POST") return configPost({ request, env });

    // --- Feed auto-discovery for the settings "Find a feed" box (token-gated) ---
    if (p === "/api/resolve-feed" && method === "GET") return resolveFeed({ request, env });

    // Everything else: static assets (index.html, /issues/*, /assets/*, /sw.js, etc.)
    return env.ASSETS.fetch(request);
  },

  // Cron Trigger — fires the daily pipeline. ctx.waitUntil keeps the run alive
  // past the handler return. A failure is logged (observability on) but never
  // throws the cron into a retry storm.
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      (async () => {
        try {
          const result = await runDaily(env, { trigger: "cron" });
          console.log("daily run:", JSON.stringify(result));
          // Significance-gated push: one nudge only if something big just landed.
          try {
            const state = await getState(env);
            if (state) {
              const pushed = await maybePushSignificant(env, state, Date.now());
              console.log("significant push:", JSON.stringify(pushed));
            }
          } catch (e) {
            console.error("significant push failed:", (e && e.stack) || e);
          }
        } catch (e) {
          console.error("daily run failed:", (e && e.stack) || e);
        }
      })()
    );
  },
};
