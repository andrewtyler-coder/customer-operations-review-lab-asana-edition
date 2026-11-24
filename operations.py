"""Synthetic read-only planning helpers for an Asana-shaped CS workspace.

No external I/O, no Asana reads or writes. Every helper consumes supplied
dictionaries and returns review material for a human.
"""
from datetime import datetime

# Renewal-risk signal families, after the model Asana's own CS leadership has
# described publicly: usage, a data-science retention score, qualitative
# account changes, and support engagement.
RENEWAL_SIGNALS = ('utilization', 'retention_score', 'qualitative', 'support_engagement')

# Asana capability kinds a workflow candidate can map to. This package only
# proposes the mapping; a human validates fit, cost and governance before build.
CAPABILITY_KINDS = ('ai_studio_rule', 'ai_teammate', 'mcp_integration', 'manual')


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone-aware timestamp required')
    return parsed


def intake_coverage(submissions, roster, start, cutoff, seen_ids=(), reads_complete=True):
    """Form submissions become intake tasks; coverage is exact-window, deduped by GID.

    Roster is current account ownership resolved by the caller; failed reads
    block advancement rather than looking complete.
    """
    lower, upper = timestamp(start), timestamp(cutoff)
    if lower > upper:
        raise ValueError('Invalid coverage window')
    roster, seen, unique = set(roster), set(seen_ids), {}
    for row in submissions:
        if row['gid'] in unique and unique[row['gid']] != row:
            raise ValueError('Contradictory submission versions')
        unique[row['gid']] = row
    matches = [r.copy() for r in unique.values()
               if r['account_id'] in roster
               and lower < timestamp(r['created_at']) <= upper and r['gid'] not in seen]
    matches.sort(key=lambda r: (timestamp(r['created_at']), r['gid']))
    return {'submissions': matches, 'complete': reads_complete,
            'completed_through': cutoff if reads_complete else None,
            'warning': None if reads_complete else 'Incomplete reads; coverage cannot advance'}


def signal_triage(signals, utilization_floor=0.70, support_ceiling=10):
    """Conservative renewal-risk triage. Missing data escalates; nothing is inferred.

    signals: rows with account_id, period, utilization (0..1 or None),
    retention_score ('red'/'yellow'/'green' or None), qualitative (list of
    human-recorded account changes), support_tickets (int or None).
    A flag is a reason to review the renewal, never an automated account change.
    """
    flags, escalations = [], []
    seen = {}
    for row in signals:
        key = (row['account_id'], row['period'])
        if key in seen and seen[key] != row:
            escalations.append({'account_id': row['account_id'], 'period': row['period'],
                                'reason': 'contradictory signal versions; human reconciles'})
            continue
        seen[key] = row
        reasons = []
        missing = [name for name in ('utilization', 'retention_score', 'support_tickets')
                   if row.get(name) is None]
        if missing:
            escalations.append({'account_id': row['account_id'], 'period': row['period'],
                                'reason': 'signal data missing: ' + ', '.join(missing)})
            continue
        if row['utilization'] < utilization_floor:
            reasons.append('utilization below %.0f%% floor' % (utilization_floor * 100))
        if row['retention_score'] == 'red':
            reasons.append('retention score red')
        if row.get('qualitative'):
            reasons.append('qualitative: ' + '; '.join(row['qualitative']))
        if row['support_tickets'] > support_ceiling:
            reasons.append('support engagement above ceiling')
        if reasons:
            flags.append({'account_id': row['account_id'], 'period': row['period'],
                          'reasons': reasons, 'status': 'flagged for human review'})
    return {'flags': flags, 'escalations': escalations, 'evaluated': len(seen),
            'note': 'low utilization is a symptom; review finds the cause'}


def task_attention(current, baseline, now, previous_check, reads_complete=True):
    """Missing tasks require verification; never infer completed from disappearance."""
    now, before = timestamp(now), timestamp(previous_check)
    if before > now:
        raise ValueError('Invalid task window')
    def index(rows):
        result = {}
        for r in rows:
            if r['gid'] in result:
                raise ValueError('Duplicate task GID')
            result[r['gid']] = r
        return result
    current, baseline = index(current), index(baseline)
    alerts = []
    fields = ('account_id', 'assignee', 'completed', 'due_on', 'name', 'section')
    for gid, row in current.items():
        old = baseline.get(gid)
        reasons = []
        if row['completed']:
            continue
        if old is None:
            reasons.append('newly relevant')
        elif any(old.get(f) != row.get(f) for f in fields):
            reasons.append('material change')
        if row.get('due_on') and before < timestamp(row['due_on']) <= now:
            reasons.append('newly due')
        if reasons:
            alerts.append({'task': row.copy(), 'reasons': reasons})
    return {'alerts': alerts, 'missing_requires_verification': sorted(set(baseline) - set(current)),
            'complete': reads_complete, 'baseline_can_advance': reads_complete,
            'baseline_policy': 'merge current; retain unverified missing tasks',
            'retained_baseline': list({**baseline, **current}.values()) if reads_complete else list(baseline.values())}


def account_review_prep(account_id, stories, tasks, unresolved=()):
    """Source-linked facts only; no generated sentiment or inferred commitments."""
    return {'account_id': account_id,
            'recent_stories': sorted([r.copy() for r in stories if r['account_id'] == account_id],
                                     key=lambda r: timestamp(r['created_at']), reverse=True)[:5],
            'open_tasks': [r.copy() for r in tasks if r['account_id'] == account_id and not r['completed']],
            'unresolved_decisions': [r.copy() for r in unresolved if r['account_id'] == account_id],
            'check_in_status': 'not verified by preparing this summary'}


def engagement_proposals(account_id, statements):
    """Consume human-labeled synthetic statements, not an AI transcript extractor."""
    proposals, review = [], []
    for s in statements:
        if s.get('account_id') == account_id and s['kind'] == 'commitment' and s.get('owner') and s.get('evidence_id'):
            proposals.append({'account_id': account_id, 'name': s['text'],
                              'assignee': s['owner'], 'due_on': s.get('due_on'),
                              'evidence_id': s['evidence_id'], 'status': 'proposal only'})
        else:
            review.append({'text': s['text'], 'reason': 'not a complete explicit commitment for this account'})
    return {'proposals': proposals, 'manual_review': review, 'writes_performed': 0}


def portfolio_health(account_tasks, now, reviewed_within_days=30):
    """Roll up a book of accounts for a portfolio-level view.

    Unknown health stays unknown. An account with no verified review inside the
    window is surfaced as unreviewed, not assumed healthy.
    account_tasks: rows with gid, account_id, custom_fields (may hold 'health'),
    last_reviewed_at (timezone-aware ISO string or None).
    """
    now = timestamp(now)
    counts, unreviewed, unknown = {}, [], []
    seen = set()
    for task in account_tasks:
        if task['gid'] in seen:
            raise ValueError('Duplicate task GID')
        seen.add(task['gid'])
        health = task.get('custom_fields', {}).get('health')
        if not health:
            unknown.append(task['account_id'])
            counts['unknown'] = counts.get('unknown', 0) + 1
        else:
            counts[health] = counts.get(health, 0) + 1
        last = task.get('last_reviewed_at')
        if last is None or (now - timestamp(last)).days > reviewed_within_days:
            unreviewed.append({'account_id': task['account_id'],
                               'last_reviewed_at': last,
                               'reason': 'no verified review inside %d days' % reviewed_within_days})
    return {'accounts': len(seen), 'health_counts': counts,
            'unknown_health': sorted(unknown), 'unreviewed': unreviewed,
            'note': 'counts describe supplied records only; blank health is unknown, not healthy'}


def capability_map(workflows):
    """Map described manual workflows to candidate Asana AI capabilities.

    workflows: rows with id, name, volume ('high'/'low'), structure
    ('repeatable'/'judgment'), systems (list of external tools involved).
    The mapping is a proposal for a human to validate; nothing is built or
    enabled by this helper.
    """
    proposals = []
    seen = set()
    for w in workflows:
        if w['id'] in seen:
            raise ValueError('Duplicate workflow ID')
        seen.add(w['id'])
        if w.get('structure') not in ('repeatable', 'judgment') or w.get('volume') not in ('high', 'low'):
            proposals.append({'workflow_id': w['id'], 'candidate': 'manual',
                              'rationale': 'incomplete description; a human scopes this workflow first',
                              'status': 'candidate only; human validates fit, cost and governance'})
            continue
        if w.get('systems'):
            candidate, rationale = ('mcp_integration',
                                    'work spanning external tools fits an integration over Asana MCP server')
        elif w['structure'] == 'judgment':
            candidate, rationale = ('ai_teammate',
                                    'context-and-judgment work fits an AI Teammate with checkpoints and approvals')
        elif w['structure'] == 'repeatable' and w['volume'] == 'high':
            candidate, rationale = ('ai_studio_rule',
                                    'high-volume repeatable work fits a no-code AI Studio rule')
        else:
            candidate, rationale = ('ai_studio_rule', 'repeatable work fits an AI Studio rule')
        proposals.append({'workflow_id': w['id'], 'candidate': candidate, 'rationale': rationale,
                          'status': 'candidate only; human validates fit, cost and governance'})
    return {'proposals': proposals, 'built': 0}


def adoption_benchmarks(usage_rows, plan):
    """Track AI adoption against 30/60/90-day benchmarks per account.

    usage_rows: rows with account_id, day (30/60/90), active_workflows (int or
    None), ai_requests (int or None). plan: {'30': min_workflows, '60': ..., '90': ...}.
    Missing usage data escalates; an account is never marked behind on absent data.
    Benchmarks measure adoption, not business outcomes.
    """
    parsed = {}
    for day, target in plan.items():
        if int(day) not in (30, 60, 90) or int(target) < 0:
            raise ValueError('Plan keys must be 30/60/90 with non-negative targets')
        parsed[int(day)] = int(target)
    results, escalations = [], []
    seen = set()
    for row in usage_rows:
        key = (row['account_id'], row['day'])
        if key in seen:
            raise ValueError('Duplicate usage row for account/day')
        seen.add(key)
        if row['day'] not in parsed:
            escalations.append({'account_id': row['account_id'], 'day': row['day'],
                                'reason': 'no benchmark defined for this checkpoint'})
            continue
        if row.get('active_workflows') is None:
            escalations.append({'account_id': row['account_id'], 'day': row['day'],
                                'reason': 'usage data missing; not marked behind on absent data'})
            continue
        target = parsed[row['day']]
        actual = row['active_workflows']
        results.append({'account_id': row['account_id'], 'day': row['day'],
                        'target': target, 'actual': actual,
                        'status': 'on track' if actual >= target else 'behind benchmark',
                        'ai_requests': row.get('ai_requests')})
    return {'results': results, 'escalations': escalations}


def handoff_manifest(drafts):
    """Recompute review manifest from exact current comment/status-update drafts.

    Does not post, approve, or validate a recipient. A teammate's EOD narrative
    is a draft a human reviews, never an auto-published status update.
    """
    from workflow import digest
    ids = [d['id'] for d in drafts]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate draft ID')
    return {'count': len(drafts), 'drafts': [d.copy() for d in drafts],
            'manifest_hash': digest(sorted(drafts, key=lambda d: d['id'])),
            'status': 'requires human review; nothing posted'}

