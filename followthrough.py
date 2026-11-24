"""Synthetic follow-through controls for an Asana-shaped CS workflow.

Offline helpers modeling how a conservative AI Teammate handles follow-up
cadences, coverage-accounted daily briefs, approval-bound actions,
evidence-source hierarchies, open loops and closeout verification. No
external I/O, no Asana reads or writes, no messaging of any kind.
"""
from workflow import digest
from operations import timestamp

# A generic follow-up ladder: step labels a human configures, not a schedule.
# The teammate tracks which step is owed; it never sends anything.
DEFAULT_LADDER = ('first follow-up', 'repeat follow-up', 'final follow-up')

OPEN_LOOP_KINDS = ('pending_approval', 'promised_follow_up', 'missing_item')


def follow_up_cadence(account_ids, touches, responses, ladder=DEFAULT_LADDER):
    """Track verified outreach per account and show the exact step still owed.

    touches: verified outbound follow-ups, rows with account_id, sent_at,
    evidence_id. responses: verified inbound replies, rows with account_id,
    received_at, evidence_id. Rows without evidence are not counted: an
    unverified touch is not outreach, and an unverified reply does not reset
    a cycle. Distinguishes a first trigger from repeat follow-up, escalates
    at the top of the ladder, and stops outreach on a verified response.
    Proposes status changes for human approval; changes nothing itself.
    """
    if not ladder:
        raise ValueError('Ladder must define at least one step')
    results, proposals = [], []
    for account_id in account_ids:
        acct_touches = sorted((t for t in touches if t['account_id'] == account_id and t.get('evidence_id')),
                              key=lambda t: timestamp(t['sent_at']))
        acct_responses = sorted((r for r in responses if r['account_id'] == account_id and r.get('evidence_id')),
                                key=lambda r: timestamp(r['received_at']))
        last_response = acct_responses[-1] if acct_responses else None
        cycle_touches = [t for t in acct_touches
                         if last_response is None or timestamp(t['sent_at']) > timestamp(last_response['received_at'])]
        if last_response is not None and not cycle_touches:
            results.append({'account_id': account_id, 'cycle': 'closed by verified response',
                            'attempts': 0, 'outreach_owed': None, 'evidence_id': last_response['evidence_id']})
            continue
        attempts = len(cycle_touches)
        if attempts >= len(ladder):
            results.append({'account_id': account_id, 'cycle': 'open', 'attempts': attempts,
                            'outreach_owed': 'escalate to human; ladder exhausted'})
            proposals.append({'account_id': account_id, 'proposal': 'status change after exhausted follow-up ladder',
                              'attempts': attempts, 'status': 'requires human approval; never automatic'})
        else:
            results.append({'account_id': account_id, 'cycle': 'open', 'attempts': attempts,
                            'outreach_owed': ladder[attempts],
                            'trigger': 'first trigger' if attempts == 0 else 'repeat entry'})
    return {'accounts': results, 'status_change_proposals': proposals,
            'sends_performed': 0,
            'note': 'a prior outbound message does not reset the ladder; only a verified response does'}


def daily_brief(account_ids, actions, reads_complete=True, unchecked_sources=()):
    """Coverage-accounted brief: every account gets an action or a named gap.

    actions: mapping of account_id to a proposed action string. Any account
    without one is named as a gap with its reason. When reads are incomplete
    the brief says so and never reports 'nothing new'.
    """
    entries, gaps = [], []
    for account_id in account_ids:
        action = actions.get(account_id)
        if action:
            entries.append({'account_id': account_id, 'action': action})
        else:
            gaps.append({'account_id': account_id,
                         'reason': 'no verified review produced an action; named gap, not silence'})
    return {'accounts_reviewed': len(entries), 'gaps': gaps,
            'total_accounts': len(account_ids),
            'coverage_complete': reads_complete,
            'unchecked_sources': list(unchecked_sources),
            'summary_rule': ('coverage incomplete; never report nothing new'
                             if not reads_complete else 'every account has an action or a named gap')}


class ApprovalBoundAction:
    """One exact action, approved once, applied once, read back, never retried blind.

    In-memory demonstration of the boundary an Asana AI Teammate respects for
    consequential steps: the human approves the exact payload, the mock apply
    runs once, the saved result is read back, and an uncertain outcome blocks
    any retry until a human reconciles what actually happened.
    """

    def __init__(self):
        self.presented = {}
        self.approved = set()
        self.applied = set()
        self.uncertain = set()
        self.audit = []

    def present(self, payload):
        """Show the exact payload for review; returns its review token."""
        key = digest(payload)
        self.presented[key] = dict(payload)
        return key

    def approve(self, payload):
        """Called only after a human reviews this exact payload in the demo."""
        key = digest(payload)
        if key not in self.presented:
            raise ValueError('Payload was never presented for review')
        self.approved.add(key)

    def apply(self, payload):
        key = digest(payload)
        if key in self.uncertain:
            raise ValueError('Outcome uncertain; reconcile what happened before any retry')
        if key in self.applied:
            return 'already applied; duplicate refused'
        if key not in self.approved:
            raise PermissionError('Exact payload has not been approved')
        self.applied.add(key)
        self.approved.discard(key)
        record = {'action_hash': key, **dict(payload), 'status': 'mock applied'}
        self.audit.append(record)
        return record

    def read_back(self, payload):
        """Verify what actually saved for this exact payload."""
        key = digest(payload)
        for record in self.audit:
            if record['action_hash'] == key:
                return {'verified': True, 'record': dict(record)}
        return {'verified': False, 'reason': 'no saved record for this exact payload'}

    def report_uncertain(self, payload):
        """A timeout or missing response after a write attempt: block retries."""
        self.uncertain.add(digest(payload))
        return 'outcome uncertain; reconcile first, never auto-retry'

    def reconcile(self, payload, human_attestation):
        """Resolve uncertainty only on explicit human attestation of what happened."""
        key = digest(payload)
        if key not in self.uncertain:
            raise ValueError('Nothing uncertain about this payload')
        if not isinstance(human_attestation, str) or not human_attestation.strip():
            raise ValueError('Human attestation required to reconcile')
        self.uncertain.discard(key)
        self.approved.discard(key)  # stale approval dies with the uncertain attempt
        self.audit.append({'action_hash': key, 'status': 'reconciled by human',
                           'attestation': human_attestation})
        return 'reconciled; any new attempt needs a fresh exact approval'


def resolve_evidence(requirement, primary_rows, fallback_rows=(), reads_complete=True):
    """Match evidence by exact ID from a primary source, with a documented fallback.

    requirement: row with id and require_shareable (bool). An internal
    reference never substitutes where a shareable link is required. When
    reads are incomplete, nothing may be called the latest or only record.
    """
    if not requirement.get('id'):
        raise ValueError('Exact evidence ID required')
    rid = requirement['id']
    primary = [r for r in primary_rows if r.get('id') == rid]
    if len(primary) > 1:
        return {'status': 'hold', 'reason': 'duplicate records for exact ID; human reconciles'}
    if primary:
        row = primary[0]
        if requirement.get('require_shareable') and not row.get('shareable'):
            return {'status': 'hold', 'evidence': row.copy(),
                    'reason': 'internal reference cannot substitute for a shareable link'}
        return {'status': 'matched', 'source': 'primary', 'evidence': row.copy(),
                'fallback_used': False}
    fallback = [r for r in fallback_rows if r.get('id') == rid]
    if fallback:
        return {'status': 'matched', 'source': 'documented fallback', 'evidence': fallback[0].copy(),
                'fallback_used': True,
                'note': 'primary source did not hold this record; fallback labeled, not silent'}
    if not reads_complete:
        return {'status': 'unknown', 'reason': 'coverage incomplete; record may exist in unread sources',
                'may_not_claim_latest': True}
    return {'status': 'missing', 'reason': 'no record with this exact ID in any checked source'}


def carryover_queue(open_loops, now):
    """Open loops carry forward with owner, due date and evidence; none drop silently.

    open_loops: rows with id, account_id, kind (pending_approval,
    promised_follow_up, missing_item), owner, due_on (ISO date or None),
    evidence_id (optional). Rows missing an owner or due date are flagged as
    incomplete and still carried.
    """
    current = timestamp(now)
    queue, incomplete = [], []
    seen = set()
    for loop in open_loops:
        if loop['id'] in seen:
            raise ValueError('Duplicate open-loop ID')
        seen.add(loop['id'])
        if loop.get('kind') not in OPEN_LOOP_KINDS:
            raise ValueError('Unknown open-loop kind: %r' % loop.get('kind'))
        row = dict(loop)
        missing = [f for f in ('owner', 'due_on') if not loop.get(f)]
        if missing:
            row['incomplete'] = 'missing ' + ', '.join(missing)
            incomplete.append(row)
        else:
            due = loop['due_on'] if 'T' in loop['due_on'] else loop['due_on'] + 'T00:00:00Z'
            row['overdue'] = timestamp(due) < current
        queue.append(row)
    queue.sort(key=lambda r: (r.get('due_on') or '9999', r['id']))
    return {'open_loops': queue, 'incomplete_rows': incomplete, 'carried': len(queue),
            'rule': 'loops close only on verified completion; nothing drops off silently'}


def verify_closeout(submitted, saved_rows, resubmit_requested=False):
    """Submit-once closeout: verify the saved record; never resubmit on doubt.

    submitted: the exact payload that was sent for review. saved_rows: records
    read back afterwards. A match verifies the closeout; anything else holds.
    A resubmit request after verification is refused as a duplicate.
    """
    key = digest(submitted)
    matches = [r for r in saved_rows if r.get('payload_hash') == key]
    if len(matches) > 1:
        return {'status': 'hold', 'reason': 'multiple saved records match; human reconciles before any resubmission'}
    if matches:
        if resubmit_requested:
            return {'status': 'refused', 'reason': 'already verified saved; resubmission would be a duplicate'}
        return {'status': 'verified saved', 'record': matches[0].copy(), 'resubmission': 'not needed'}
    return {'status': 'hold', 'reason': 'no saved record verified; reconcile what happened first',
            'resubmission': 'blocked; rendering doubt is not proof of failure'}

