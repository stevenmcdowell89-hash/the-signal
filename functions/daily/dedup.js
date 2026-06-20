// The Signal — daily: dedup / cluster (§3.2, §5).
//
// A cluster collapses to one item that RETAINS ALL SOURCE LINKS (source link +
// best discussion thread), capped to avoid clutter. Clustering is by canonical
// URL first, then by title similarity (token Jaccard) so the same story across
// two sources merges even when the URLs differ.

const STOP = new Set([
  "the", "a", "an", "of", "to", "in", "on", "for", "and", "is", "are", "as",
  "at", "by", "with", "from", "this", "that", "it", "its", "be", "has", "have",
  "new", "will", "after", "over", "into", "out", "up", "how", "why", "what",
]);

export function canonicalUrl(raw) {
  try {
    const u = new URL(raw);
    u.hash = "";
    // strip tracking params
    const drop = [];
    for (const [k] of u.searchParams) {
      if (/^(utm_|fbclid|gclid|ref|ref_src|mc_cid|mc_eid|cmp|igshid)/i.test(k)) drop.push(k);
    }
    drop.forEach((k) => u.searchParams.delete(k));
    let s = u.toString();
    s = s.replace(/\/$/, "");
    return s.toLowerCase();
  } catch {
    return (raw || "").toLowerCase();
  }
}

function tokens(title) {
  return new Set(
    (title || "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2 && !STOP.has(w))
  );
}

function jaccard(a, b) {
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const t of a) if (b.has(t)) inter++;
  return inter / (a.size + b.size - inter);
}

// Stable cluster id (hash of the canonical url; falls back to title tokens).
export async function clusterId(canon) {
  const data = new TextEncoder().encode(canon);
  const buf = await crypto.subtle.digest("SHA-1", data);
  return [...new Uint8Array(buf)].slice(0, 8).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function mergeLinks(into, from) {
  const seen = new Set(into.map((l) => l.url));
  for (const l of from) {
    if (!seen.has(l.url)) {
      into.push(l);
      seen.add(l.url);
    }
  }
  // Cap clutter (§5): keep at most source(article) + best discussion + post.
  const byType = { article: [], discussion: [], post: [], feed: [] };
  for (const l of into) (byType[l.type] || byType.feed).push(l);
  const capped = [
    ...byType.article.slice(0, 1),
    ...byType.discussion.slice(0, 1),
    ...byType.post.slice(0, 1),
  ];
  return capped.length ? capped : into.slice(0, 2);
}

// Cluster a flat list of normalised entries. Returns clustered items keyed by id,
// each carrying merged links and the strongest rawScore / freshest published.
export async function clusterEntries(entries) {
  const byCanon = new Map();
  for (const e of entries) {
    const canon = canonicalUrl(e.url);
    e._canon = canon;
    e._tokens = tokens(e.title);
    if (!byCanon.has(canon)) byCanon.set(canon, []);
    byCanon.get(canon).push(e);
  }

  // First pass: collapse exact canonical-URL matches.
  const protoClusters = [];
  for (const [canon, group] of byCanon) {
    protoClusters.push({ canon, tokens: group[0]._tokens, members: group });
  }

  // Second pass: merge title-similar proto-clusters (greedy, threshold 0.6).
  const merged = [];
  for (const pc of protoClusters) {
    let hit = null;
    for (const m of merged) {
      if (m.domain === pc.members[0].domain && jaccard(m.tokens, pc.tokens) >= 0.6) {
        hit = m;
        break;
      }
    }
    if (hit) {
      hit.members.push(...pc.members);
    } else {
      merged.push({ canon: pc.canon, tokens: pc.tokens, domain: pc.members[0].domain, members: [...pc.members] });
    }
  }

  const items = [];
  for (const m of merged) {
    const id = await clusterId(m.canon);
    // Pick the representative member: highest rawScore, then freshest.
    const rep = m.members.slice().sort(
      (a, b) => b.rawScore - a.rawScore || b.published - a.published
    )[0];
    let links = [];
    for (const mem of m.members) links = mergeLinks(links, mem.links);
    const rawScore = Math.max(...m.members.map((x) => x.rawScore));
    const published = Math.min(...m.members.map((x) => x.published));
    items.push({
      id,
      canonical_url: m.canon,
      title: rep.title,
      summary: rep.summary || "",
      domain: rep.domain,
      source: rep.sourceId,
      source_type: rep.sourceType,
      weight: rep.weight,
      links,
      rawScore,
      published,
      memberSources: [...new Set(m.members.map((x) => x.sourceId))],
    });
  }
  return items;
}
