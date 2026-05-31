#!/usr/bin/env python3
"""check-topic-lock.py — Gate 1 topic-lock enforcement (v8.25).

Two checks against a stitched weekly (or a special's Meanwhile):

  (a) Frequency cap: a tracked topic with recent_leads >= 3 (within 26 weeks)
      may not anchor the Lead unless weeks_since_last_lead >= recent_leads*2.
  (b) Development test: if a topic led the IMMEDIATELY PRECEDING issue and this
      issue's Lead is a holding pattern (no datable development), it must not
      lead. We detect a holding pattern by the presence of holding-pattern
      language in the Lead H2 + first paragraph WITHOUT a last_development
      recorded in state for that topic dated within the last 7 days.

The script reads the state file for ongoing_stories (lead_history,
last_development) and the stitched HTML for the actual Lead text. It is
advisory-but-loud: exit 1 on any violation so the orchestrator re-plans.

Usage:
  python3 check-topic-lock.py <stitched-weekly-html> --state <signal-state.json> \
      --issue-date YYYY-MM-DD [--warn-only]
"""
import sys, re, json, datetime

HOLDING = re.compile(
    r'\b(still|continues? to|clings? on|cling to|waiting|wait(?:s|ed)? on|await\w*|'
    r'waiting phase|holding pattern|for now|ahead of|turns? on (?:one|a|the)|'
    r'no breakthrough|no resolution|not into resolution|no challenge|no (?:confidence )?vote|'
    r'remains? (?:in|under|locked|deadlocked|unresolved)|blown itself out|'
    r'standoff|stand-off|deadlock|speculation|pressure (?:mounts|grows|continues)|'
    r'on the brink|in limbo|yet to|hangs? (?:in|on)|grind(?:s)? on)\b', re.I)


def parse_date(s):
    try:
        return datetime.date.fromisoformat(s)
    except Exception:
        return None


def get_arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def extract_world_lead(html):
    """Return (h2_text, first_para_text) of the World This Week Lead, best-effort."""
    # Strip the inlined stylesheet/script FIRST — they contain the literal text
    # "WORLD THIS WEEK" in comments and would mis-anchor the search.
    body = re.sub(r'<style.*?</style>|<script.*?</script>', ' ', html, flags=re.S | re.I)
    # Use the LAST "World This Week" hit (the section itself; an earlier hit may
    # be the navigator label). Then take the first heading (h2 or h3) + its para.
    hits = [m.start() for m in re.finditer(r'World This Week', body, re.I)]
    start = hits[-1] if hits else 0
    seg = body[start:start + 6000]
    h = re.search(r'<h[23][^>]*>(.*?)</h[23]>', seg, re.S)
    ht = re.sub(r'<[^>]+>', ' ', h.group(1)).strip() if h else ''
    after = seg[h.end():] if h else seg
    p = re.search(r'<p[^>]*>(.*?)</p>', after, re.S)
    pt = re.sub(r'<[^>]+>', ' ', p.group(1)).strip() if p else ''
    return re.sub(r'\s+', ' ', ht), re.sub(r'\s+', ' ', pt)


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not paths:
        print("usage: check-topic-lock.py <html> --state <state.json> --issue-date YYYY-MM-DD")
        sys.exit(2)
    html_path = paths[0]
    state_path = get_arg('--state')
    issue_date = parse_date(get_arg('--issue-date', datetime.date.today().isoformat()))
    warn_only = '--warn-only' in sys.argv

    html = open(html_path, encoding='utf-8').read()
    state = json.load(open(state_path)) if state_path else {}
    stories = state.get('ongoing_stories', [])

    h2, para = extract_world_lead(html)
    lead_blob = (h2 + ' ' + para).lower()

    print("=== check-topic-lock.py ===")
    print(f"Issue date: {issue_date}")
    print(f"World Lead H2: {h2[:90]}")

    failures = []
    for o in stories:
        topic = o.get('topic', '')
        # entity tokens: words >3 chars from the topic, plus any explicit aliases
        toks = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", topic)]
        toks += [a.lower() for a in o.get('aliases', [])]
        if not toks:
            continue
        hits = sum(1 for t in set(toks) if t in lead_blob)
        leads_this_issue = hits >= 2 or any(t in h2.lower() for t in toks)
        if not leads_this_issue:
            continue

        lh = [d for d in (parse_date(x) for x in o.get('lead_history', [])) if d]
        recent = [d for d in lh if (issue_date - d).days <= 26 * 7 and d < issue_date]
        recent_leads = len(recent)
        weeks_since = min(((issue_date - d).days // 7) for d in lh) if lh else 99

        # (a) frequency cap
        if recent_leads >= 3 and weeks_since < recent_leads * 2:
            failures.append(
                f"[FREQ] '{topic}': recent_leads={recent_leads}, weeks_since_last_lead={weeks_since} "
                f"< required {recent_leads*2}. Must rest from the Lead.")

        # (b) development test — did it lead the immediately preceding issue?
        led_prev = any((issue_date - d).days <= 9 for d in lh)  # within ~1 week prior
        if led_prev:
            ld = o.get('last_development') or {}
            ld_date = parse_date(ld.get('date', '')) if isinstance(ld, dict) else None
            has_fresh_dev = ld_date is not None and 0 <= (issue_date - ld_date).days <= 7
            if HOLDING.search(lead_blob) and not has_fresh_dev:
                failures.append(
                    f"[DEV] '{topic}': led the previous issue and this Lead reads as a holding "
                    f"pattern (holding-language present, no datable development in last_development "
                    f"within 7 days). Being most-discussed is not a development — yield the Lead.")

    if not failures:
        print("PASS — no topic-lock violation in the Lead.")
        sys.exit(0)
    print("\nTOPIC-LOCK VIOLATIONS:")
    for f in failures:
        print("  " + f)
    print("\nRe-plan the Lead: demote this topic to the tracker box / Companion / Also,")
    print("and lead with a story that has an actual development this week.")
    sys.exit(0 if warn_only else 1)


if __name__ == "__main__":
    main()
