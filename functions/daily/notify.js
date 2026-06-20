// The Signal — daily: significance-gated push (§D).
//
// "Push only when something big lands." After each poll, if a genuinely
// significant story is fresh on the brief — a named-entity-floor catch, or a
// high-confidence top catch first seen in the last few hours — fan out a SINGLE
// push to every subscription. Throttled so a quiet day stays silent and a busy
// one can't spam: at most one push per `min_interval_hours`, never the same item
// twice. Reuses the weekly's VAPID push path; degrades silently if push isn't
// configured.

import { sendPush } from "../_lib/webpush.js";

const LAST_PUSH_KEY = "push:last_significant";

// Pick the single best item worth interrupting the reader for, or null.
function pickSignificant(state, cfg, now) {
  const freshMs = (cfg.fresh_hours || 12) * 3.6e6;
  const minConf = cfg.min_confidence ?? 0.85;
  // Only the strip is in scope — these are the most significant fresh catches.
  const pool = (state.top_catches || []).filter((it) => {
    const seen = it.first_seen || 0;
    const fresh = seen > 0 && now - seen <= freshMs;
    return fresh && (it.entity_floor || (it.confidence || 0) >= minConf);
  });
  if (!pool.length) return null;
  // Best = entity-floor first, then highest confidence.
  pool.sort((a, b) =>
    (b.entity_floor ? 1 : 0) - (a.entity_floor ? 1 : 0) || (b.confidence || 0) - (a.confidence || 0)
  );
  return pool[0];
}

// Returns { pushed: bool, reason }. Never throws into the cron.
export async function maybePushSignificant(env, state, now) {
  const cfg = ((await safeConfigPush(env)) || {});
  if (!cfg.enabled) return { pushed: false, reason: "disabled" };
  if (!env.SUBSCRIPTIONS || !env.VAPID_PRIVATE_KEY || !env.VAPID_PUBLIC_KEY) {
    return { pushed: false, reason: "push not configured" };
  }

  const pick = pickSignificant(state, cfg, now);
  if (!pick) return { pushed: false, reason: "nothing significant" };

  // Throttle: skip if we pushed within the interval, or already sent this item.
  let last = null;
  try { last = JSON.parse((await env.DAILY_STATE.get(LAST_PUSH_KEY)) || "null"); } catch (_) {}
  const intervalMs = (cfg.min_interval_hours || 8) * 3.6e6;
  if (last) {
    if (last.id === pick.id) return { pushed: false, reason: "already pushed" };
    if (now - (last.ts || 0) < intervalMs) return { pushed: false, reason: "throttled" };
  }

  const body = (pick.hook || pick.summary || "").slice(0, 180);
  const pushBody = JSON.stringify({
    title: pick.title,
    body,
    url: "/",
    slug: null,
    image: null,
  });

  const list = await env.SUBSCRIPTIONS.list({ prefix: "sub:" });
  let sent = 0;
  for (const k of list.keys) {
    const raw = await env.SUBSCRIPTIONS.get(k.name);
    if (!raw) continue;
    let sub;
    try { sub = JSON.parse(raw); } catch { continue; }
    try {
      const resp = await sendPush(
        sub, pushBody, env.VAPID_PRIVATE_KEY, env.VAPID_PUBLIC_KEY,
        env.VAPID_SUBJECT || "mailto:noreply@the-signal.local"
      );
      if (resp.status === 404 || resp.status === 410) await env.SUBSCRIPTIONS.delete(k.name);
      else if (resp.ok || resp.status === 201) sent++;
    } catch (_) { /* skip a single dead endpoint */ }
  }

  await env.DAILY_STATE.put(LAST_PUSH_KEY, JSON.stringify({ id: pick.id, ts: now, title: pick.title }));
  return { pushed: true, reason: "ok", sent, item: pick.title };
}

// Read just the push.significant block without importing the whole config module
// graph cost into this hot path's typing — loadConfig already merges defaults.
async function safeConfigPush(env) {
  try {
    const { loadConfig } = await import("./config.js");
    const c = await loadConfig(env);
    return (c.push || {}).significant || {};
  } catch (_) {
    return {};
  }
}
