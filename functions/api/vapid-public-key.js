// GET /api/vapid-public-key
// Returns the VAPID public key (base64url uncompressed P-256 point) for the
// client to subscribe with. Read from the VAPID_PUBLIC_KEY env var set on the
// Cloudflare Pages project.

export async function onRequestGet({ env }) {
  const key = (env.VAPID_PUBLIC_KEY || "").trim();
  if (!key) {
    return new Response("VAPID_PUBLIC_KEY not configured", { status: 503 });
  }
  return new Response(key, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
