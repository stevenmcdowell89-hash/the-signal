// GET  /api/config  — open read of the live config (§6: reads open).
// POST /api/config  — token-gated write (§6: writes only).
//
// Token gating: a held token stored as the Worker secret SETTINGS_TOKEN. The
// settings UI sends it on every save via the X-Signal-Token header (or
// Authorization: Bearer …); the Worker verifies before writing. The token is a
// shared secret, not device-bound — each device pastes it once, stores it
// locally, then sends it automatically.

import { loadConfig, saveConfig } from "../daily/config.js";

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export function tokenOk(request, env) {
  const expected = (env.SETTINGS_TOKEN || "").trim();
  if (!expected) return false;
  const header =
    request.headers.get("X-Signal-Token") ||
    (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  // Constant-time-ish compare.
  if (!header || header.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < expected.length; i++) diff |= header.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

export async function onRequestGet({ env }) {
  const config = await loadConfig(env);
  return json(config);
}

export async function onRequestPost({ request, env }) {
  if (!tokenOk(request, env)) return json({ error: "unauthorized" }, 401);
  let incoming;
  try {
    incoming = await request.json();
  } catch {
    return json({ error: "invalid JSON" }, 400);
  }
  // Merge over the current live config so a partial save (e.g. just the fold
  // threshold) doesn't wipe everything else.
  const current = await loadConfig(env);
  const next = { ...current, ...incoming };
  if (incoming.enrichment) next.enrichment = { ...current.enrichment, ...incoming.enrichment };
  if (incoming.recency) next.recency = { ...current.recency, ...incoming.recency };
  if (incoming.push) {
    next.push = { ...current.push, ...incoming.push };
    if (incoming.push.significant)
      next.push.significant = { ...(current.push || {}).significant, ...incoming.push.significant };
  }
  if (incoming.profile) next.profile = { ...current.profile, ...incoming.profile };
  await saveConfig(env, next);
  return json({ ok: true, saved: true });
}
