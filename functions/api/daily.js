// GET  /api/daily      — open read of the current rendered state (§4).
// POST /api/daily/run  — token-gated manual poll (the Cron Trigger calls
//                        run() directly; this lets a device force a refresh).

import { run, getState } from "../daily/pipeline.js";
import { tokenOk } from "./config.js";

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export async function onRequestGet({ env }) {
  const state = await getState(env);
  if (!state) {
    return json({ generated_at: 0, status: { caught_up: false }, top_catches: [], sections: [], also: [], below_fold: [], today_tonight: [], footer: { kept: 0, scanned: 0, sources: 0, below_fold_count: 0 } });
  }
  return json(state);
}

export async function onRequestPost({ request, env, ctx }) {
  if (!tokenOk(request, env)) return json({ error: "unauthorized" }, 401);
  try {
    const result = await run(env, { trigger: "manual" });
    return json(result);
  } catch (e) {
    return json({ error: String((e && e.message) || e) }, 500);
  }
}
