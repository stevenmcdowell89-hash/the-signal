// The Signal — daily: shared Anthropic client.
//
// One place that talks to the model, so every AI surface (Tier-2 enrichment and
// the editorial layer) shares the same request shape, structured-output parsing,
// prompt caching, and cost accounting. Extracted from enrich.js so editorial.js
// reuses it verbatim rather than re-implementing the call.

const ENDPOINT = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
const DEFAULT_MODEL = "claude-haiku-4-5";

// $1 / $5 per M tokens for claude-haiku-4-5; cache read/write per Anthropic.
const IN_PER_TOK = 1.0 / 1e6;
const OUT_PER_TOK = 5.0 / 1e6;
const CACHE_READ_PER_TOK = 0.1 / 1e6;
const CACHE_WRITE_PER_TOK = 1.25 / 1e6;

// Token usage → cents. (Haiku rates; a costlier model just under-counts spend
// slightly — the cap is a guardrail, not an invoice.)
export function usageToCents(usage) {
  const u = usage || {};
  return (
    100 *
    ((u.input_tokens || 0) * IN_PER_TOK +
      (u.output_tokens || 0) * OUT_PER_TOK +
      (u.cache_read_input_tokens || 0) * CACHE_READ_PER_TOK +
      (u.cache_creation_input_tokens || 0) * CACHE_WRITE_PER_TOK)
  );
}

// One /v1/messages call with a JSON-schema-constrained response. The system block
// is marked ephemeral so a repeated system prompt (the profile/guidance, reused
// across items and passes within a ~5-min window) reads from cache. Returns
// { parsed, cents } — parsed is null on a non-JSON / malformed reply (callers
// degrade gracefully). Throws only on a non-OK HTTP status.
export async function callModel(env, { system, user, schema, model, max_tokens = 400 }) {
  const body = {
    model: model || DEFAULT_MODEL,
    max_tokens,
    system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
    output_config: { format: { type: "json_schema", schema } },
    messages: [{ role: "user", content: user }],
  };
  const resp = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`anthropic ${resp.status}: ${t.slice(0, 200)}`);
  }
  const data = await resp.json();
  const cents = usageToCents(data.usage);
  let parsed = null;
  const block = (data.content || []).find((b) => b.type === "text");
  if (block) {
    try { parsed = JSON.parse(block.text); } catch { parsed = null; }
  }
  return { parsed, cents };
}
