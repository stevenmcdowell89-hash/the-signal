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

// High-churn domains where the strict same-title rule misses obvious variants of
// the SAME story ("Juventus complete X" vs "Juve sign X"). For these we also merge
// on a SHARED proper-noun entity at a lower title threshold — but still require
// real title overlap, so two DIFFERENT Juventus stories (different player) stay
// separate. (Distinct rumours are thinned later by keyword demotion + roll-ups.)
// `cricket` added (WP-11): the BBC files several variants of the SAME match report
// ("Phoenix beat Rockets in high-scoring thriller" / "Birmingham Phoenix beat Trent
// Rockets in record-breaking thriller") which land in the 0.35–0.5 Jaccard band the
// strict rule misses. Verified against the live feed before adding; `cycling`,
// `athletics` and `golf` were measured the same way and deliberately left OUT —
// there the same relaxation merged genuinely different stories (two Commonwealths
// team-news stories that contradicted each other; The Open's third- and final-round
// round-ups). See docs/editorial-coverage-rebuild-EVIDENCE/WP-11.md.
const RELAXED_DOMAINS = new Set(["football", "cricket"]);
const ENTITY_JACCARD = 0.35;

// Prominent proper nouns in a title (capitalised tokens in the ORIGINAL casing,
// minus stopwords) — the story's subject(s), used to gate the relaxed merge.
function dominantEntities(title) {
  const out = new Set();
  for (const m of String(title || "").matchAll(/\b([A-Z][A-Za-z]{2,})\b/g)) {
    const w = m[1].toLowerCase();
    if (!STOP.has(w)) out.add(w);
  }
  return out;
}
function sharesEntity(a, b) {
  if (!a || !b) return false;
  for (const x of a) if (b.has(x)) return true;
  return false;
}

// Stable cluster id (hash of the canonical url; falls back to title tokens).
export async function clusterId(canon) {
  const data = new TextEncoder().encode(canon);
  const buf = await crypto.subtle.digest("SHA-1", data);
  return [...new Uint8Array(buf)].slice(0, 8).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function mergeLinks(into, from) {
  const seen = new Set(into.map((l) => l.url));
  for (const l of from) {
    if (!seen.has(l.url)) {
      into.push(l);
      seen.add(l.url);
    }
  }
  // Cap clutter (§5): keep at most source(article) + best discussion + post.
  // The "best" discussion/post is the one with the most comments (richest thread)
  // so a clustered story shows its liveliest discussion.
  const byType = { article: [], discussion: [], post: [], feed: [] };
  for (const l of into) (byType[l.type] || byType.feed).push(l);
  byType.discussion.sort((a, b) => (b.count || 0) - (a.count || 0));
  byType.post.sort((a, b) => (b.count || 0) - (a.count || 0));
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
    protoClusters.push({ canon, tokens: group[0]._tokens, entities: dominantEntities(group[0].title), members: group });
  }

  // Second pass: merge title-similar proto-clusters (greedy). Same domain + title
  // Jaccard ≥0.5 as before; for high-churn domains, also merge a same-story variant
  // that shares a proper-noun entity at the lower ENTITY_JACCARD threshold.
  const merged = [];
  for (const pc of protoClusters) {
    const dom = pc.members[0].domain;
    const relaxed = RELAXED_DOMAINS.has(dom);
    let hit = null;
    for (const m of merged) {
      if (m.domain !== dom) continue;
      const j = jaccard(m.tokens, pc.tokens);
      if (j >= 0.5 || (relaxed && j >= ENTITY_JACCARD && sharesEntity(m.entities, pc.entities))) {
        hit = m;
        break;
      }
    }
    if (hit) {
      hit.members.push(...pc.members);
      for (const x of pc.entities) hit.entities.add(x);
    } else {
      merged.push({ canon: pc.canon, tokens: pc.tokens, entities: new Set(pc.entities), domain: dom, members: [...pc.members] });
    }
  }

  const items = [];
  for (const m of merged) {
    const id = await clusterId(m.canon);
    // Pick the representative member: highest rawScore, then freshest.
    const rep = m.members.slice().sort(
      (a, b) => b.rawScore - a.rawScore || (b.published || 0) - (a.published || 0)
    )[0];
    let links = [];
    for (const mem of m.members) links = mergeLinks(links, mem.links);
    const rawScore = Math.max(...m.members.map((x) => x.rawScore));
    // Earliest real publish date across the cluster; null if none was dated.
    const pubs = m.members.map((x) => x.published).filter((p) => p != null);
    const published = pubs.length ? Math.min(...pubs) : null;
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
