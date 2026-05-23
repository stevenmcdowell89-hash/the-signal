// POST /api/subscribe
// Body: a PushSubscription JSON (output of subscription.toJSON()).
// Stores it in the SUBSCRIPTIONS KV namespace, keyed by SHA-256 of endpoint.

async function endpointKey(endpoint) {
  const hash = new Uint8Array(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(endpoint)),
  );
  let hex = "";
  for (let i = 0; i < hash.length; i++) hex += hash[i].toString(16).padStart(2, "0");
  return "sub:" + hex.slice(0, 24);
}

export async function onRequestPost({ request, env }) {
  if (!env.SUBSCRIPTIONS) {
    return new Response("SUBSCRIPTIONS KV binding missing", { status: 503 });
  }

  let sub;
  try {
    sub = await request.json();
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }

  if (!sub || typeof sub.endpoint !== "string" || !sub.keys || !sub.keys.p256dh || !sub.keys.auth) {
    return new Response("Invalid subscription", { status: 400 });
  }

  const key = await endpointKey(sub.endpoint);
  await env.SUBSCRIPTIONS.put(key, JSON.stringify({
    endpoint: sub.endpoint,
    keys: { p256dh: sub.keys.p256dh, auth: sub.keys.auth },
    subscribedAt: new Date().toISOString(),
  }));

  return new Response(JSON.stringify({ ok: true, key }), {
    headers: { "Content-Type": "application/json" },
  });
}
