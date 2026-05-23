// POST /api/notify
// Auth: Authorization: Bearer <NOTIFY_AUTH_TOKEN>
// Body: { title, body, url, image?, slug? }
//
// Fans the push out to every subscription in KV. Dead subscriptions
// (HTTP 404/410 from the push service) are pruned automatically.

import { sendPush } from "../_lib/webpush.js";

export async function onRequestPost({ request, env }) {
  const expected = (env.NOTIFY_AUTH_TOKEN || "").trim();
  const auth = request.headers.get("Authorization") || "";
  if (!expected || !auth.startsWith("Bearer ") || auth.slice(7) !== expected) {
    return new Response("Unauthorized", { status: 401 });
  }

  if (!env.SUBSCRIPTIONS) return new Response("SUBSCRIPTIONS KV binding missing", { status: 503 });
  if (!env.VAPID_PRIVATE_KEY || !env.VAPID_PUBLIC_KEY) {
    return new Response("VAPID keys not configured", { status: 503 });
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }
  if (!payload || !payload.title || !payload.url) {
    return new Response("Missing required fields: title, url", { status: 400 });
  }

  const pushBody = JSON.stringify({
    title: payload.title,
    body: payload.body || "",
    url: payload.url,
    image: payload.image || null,
    slug: payload.slug || null,
  });

  const list = await env.SUBSCRIPTIONS.list({ prefix: "sub:" });
  const results = [];

  for (const k of list.keys) {
    const raw = await env.SUBSCRIPTIONS.get(k.name);
    if (!raw) continue;
    let sub;
    try { sub = JSON.parse(raw); } catch { continue; }

    try {
      const resp = await sendPush(
        sub,
        pushBody,
        env.VAPID_PRIVATE_KEY,
        env.VAPID_PUBLIC_KEY,
        env.VAPID_SUBJECT || "mailto:noreply@the-signal.local",
      );
      results.push({ key: k.name, status: resp.status });
      if (resp.status === 404 || resp.status === 410) {
        await env.SUBSCRIPTIONS.delete(k.name);
      }
    } catch (err) {
      results.push({ key: k.name, error: String(err && err.message || err) });
    }
  }

  return new Response(JSON.stringify({ ok: true, sent: results.length, results }, null, 2), {
    headers: { "Content-Type": "application/json" },
  });
}
