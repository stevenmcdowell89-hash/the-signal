// GET /api/health — open read of feed + AI health (§E).
//
// So the reader can see, at a glance, that each feed is still pulling and that
// enrichment is running and what it's costing this month. Per-source 48h article
// counts come from D1; last-poll liveness + enrichment status from KV.

import { loadConfig, getMonthlySpendCents } from "../daily/config.js";
import { SOURCE_STATUS_KEY, ENRICH_STATUS_KEY } from "../daily/pipeline.js";
import { getSourceCounts } from "../daily/db.js";

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export async function onRequestGet({ env }) {
  const now = Date.now();
  const config = await loadConfig(env);

  // Per-source counts over the last 48h.
  let counts = new Map();
  if (env.DAILY_DB) {
    try { counts = await getSourceCounts(env.DAILY_DB, now - 48 * 3.6e6); } catch (_) {}
  }

  // Last-poll liveness blob.
  let status = { ts: 0, sources: {} };
  if (env.DAILY_STATE) {
    try { status = JSON.parse((await env.DAILY_STATE.get(SOURCE_STATUS_KEY)) || "null") || status; } catch (_) {}
  }
  const st = status.sources || {};

  // Every configured source (RSS/HN + bluesky), enabled or not.
  const defs = [
    ...(config.sources || []).map((s) => ({ id: s.id, name: s.name || s.id, domain: s.domain, weight: s.weight, enabled: s.enabled !== false, kind: s.type || "rss" })),
    ...(config.bluesky || []).map((b) => ({ id: b.id, name: "@" + (b.handle || b.id), domain: b.domain, weight: b.weight, enabled: b.enabled !== false, kind: "bluesky" })),
  ];

  const sources = defs.map((d) => {
    const c = counts.get(d.id);
    const s = st[d.id];
    const count_48h = c ? c.count : 0;
    // The dot shows the LAST KNOWN outcome and persists across Reddit's rolling
    // rotation — a throttled sub stays `dead` (red) until it actually succeeds, so a
    // chronic 429 isn't hidden between its turns. The per-row "tried Nm ago" label
    // (last_checked) is what proves it WAS attempted and when. `waiting` is reserved
    // for a reddit sub the rotation simply hasn't reached yet (no status at all).
    // `tried_this_poll` lets the UI flag a failure that's happening right now.
    const tried_this_poll = !!(s && status.ts && s.ts >= status.ts);
    let state;
    if (!d.enabled) state = "off";
    else if (s && s.ok) state = count_48h > 0 ? "ok" : "stale";
    else if (s && !s.ok) state = "dead";
    else if (d.kind === "reddit") state = "waiting"; // never reached by the rotation yet
    else state = count_48h > 0 ? "ok" : "unknown";
    return {
      id: d.id, name: d.name, domain: d.domain, weight: d.weight, enabled: d.enabled, kind: d.kind,
      count_48h, last_seen: c ? c.last_seen : null, state,
      last_checked: s ? s.ts : (status.ts || null),
      tried_this_poll, reason: s ? (s.reason || null) : null,
    };
  });

  // Enrichment / cost.
  let enr = null;
  if (env.DAILY_STATE) {
    try { enr = JSON.parse((await env.DAILY_STATE.get(ENRICH_STATUS_KEY)) || "null"); } catch (_) {}
  }
  const ec = config.enrichment || {};
  const spentCents = await getMonthlySpendCents(env);
  const enrichment = {
    configured_on: !!ec.enabled,
    has_key: !!env.ANTHROPIC_API_KEY,
    on: enr ? !!enr.on : false,
    reason: enr ? enr.reason : (ec.enabled ? (env.ANTHROPIC_API_KEY ? "no run yet" : "no ANTHROPIC_API_KEY") : "enrichment off"),
    model: (enr && enr.model) || ec.model || "claude-haiku-4-5",
    last_enriched: enr ? enr.enriched : 0,
    last_run: enr ? enr.ts : null,
    month_to_date_usd: Math.round(spentCents) / 100,
    cap_usd: Math.round(ec.monthly_spend_cap_cents || 500) / 100,
  };

  return json({ generated_at: now, last_poll: status.ts || null, sources, enrichment });
}
