// The Signal — Cloudflare Worker entry point.
//
// We're on "Workers Static Assets" (not Pages Functions), so /functions/*.js
// is NOT auto-routed. This file is the single Worker script — it dispatches
// /api/* to the handlers in functions/ and falls through to env.ASSETS.fetch()
// for everything else (the static site).

import { onRequestGet as vapidPublicKey } from "./functions/api/vapid-public-key.js";
import { onRequestPost as subscribe } from "./functions/api/subscribe.js";
import { onRequestPost as notify } from "./functions/api/notify.js";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;

    if (url.pathname === "/api/vapid-public-key" && method === "GET") {
      return vapidPublicKey({ request, env });
    }
    if (url.pathname === "/api/subscribe" && method === "POST") {
      return subscribe({ request, env });
    }
    if (url.pathname === "/api/notify" && method === "POST") {
      return notify({ request, env });
    }

    // Everything else: static assets (index.html, /issues/*, /assets/*, /sw.js, etc.)
    return env.ASSETS.fetch(request);
  },
};
