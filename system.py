"""One-cycle synthetic CS workspace orchestration, with explicit lifecycle gates.

Composes the offline helpers the way an Asana CS team runs its day: intake
coverage, account review preparation, attested check-ins, post-engagement
proposals, draft handoff narratives and end-of-day review. Local state only.
"""
from operations import (intake_coverage, task_attention, account_review_prep,
                        engagement_proposals, handoff_manifest, timestamp)
from workflow import TeammateReviewQueue


class CSWorkspaceCycle:
    """Local state only. No live Asana adapters, durable storage, authentication or posts."""
    def __init__(self, account_ids, account_tasks, unresolved=()):
        self.account_ids = set(account_ids)
        if any(t['account_id'] not in self.account_ids for t in account_tasks):
            raise ValueError('Task outside configured book of business')
        self.reconciliation = TeammateReviewQueue(account_tasks)
        self.unresolved = [r.copy() for r in unresolved]
        if any(r.get('account_id') not in self.account_ids for r in self.unresolved):
            raise ValueError('Decision outside configured book of business')
        self.submissions = []
        self.tasks = []
        self.check_ins = {}
        self.sod_report = None
        self.engagements = []
        self.drafts = []

    def start_day(self, submissions, tasks, baseline, start, cutoff, seen_ids=(),
                  intake_complete=True, tasks_complete=True):
        # Invalidate the previous check before ingesting: a failed refresh cannot look current.
        self.sod_report = None
        self.submissions = list({r['gid']: r.copy() for r in submissions
                                 if r['account_id'] in self.account_ids
                                 and timestamp(r['created_at']) <= timestamp(cutoff)}.values())
        self.tasks = [r.copy() for r in tasks if r['account_id'] in self.account_ids]
        self.sod_report = {
            'intake': intake_coverage(submissions, self.account_ids, start, cutoff, seen_ids, intake_complete),
            'tasks': task_attention(self.tasks, [t for t in baseline if t['account_id'] in self.account_ids],
                                    cutoff, start, tasks_complete)}
        return self.sod_report

    def prepare_review(self, account_id):
        self._check_account(account_id)
        if self.sod_report is None:
            raise ValueError('Start day first to establish coverage')
        result = account_review_prep(account_id, self.submissions, self.tasks, self.unresolved)
        result['coverage_complete'] = self.sod_report['intake']['complete'] and self.sod_report['tasks']['complete']
        return result

    def record_check_in(self, account_id, evidence_id):
        """Caller attests synthetic completion; not inferred from prep or summary."""
        self._check_account(account_id)
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError('Completion evidence required')
        self.check_ins[account_id] = {'evidence_id': evidence_id, 'status': 'caller-attested mock completion'}

    def after_engagement(self, account_id, statements):
        self._check_account(account_id)
        report = engagement_proposals(account_id, statements)
        self.engagements.append(report)
        return report

    def set_drafts(self, drafts):
        if any(d.get('account_id') not in self.account_ids for d in drafts):
            raise ValueError('Draft outside configured book of business')
        if d_invalid := [d for d in drafts if d.get('kind') not in ('comment', 'status_update')]:
            raise ValueError('Draft kind must be comment or status_update: %r' % d_invalid[0].get('id'))
        result = handoff_manifest(drafts)
        self.drafts = [d.copy() for d in drafts]
        return result

    def end_day(self):
        if self.sod_report is None:
            raise ValueError('Start day first; cannot report an unchecked day')
        complete = self.sod_report['intake']['complete'] and self.sod_report['tasks']['complete']
        return {'status': 'mock coverage complete' if complete else 'coverage incomplete',
                'coverage': self.sod_report,
                'check_ins': dict(self.check_ins),
                'check_ins_not_verified': sorted(self.account_ids - set(self.check_ins)),
                'unresolved_decisions': [r.copy() for r in self.unresolved],
                'engagement_proposals': list(self.engagements),
                'handoff_manifest': handoff_manifest(self.drafts),
                'mock_teammate_audit': list(self.reconciliation.audit),
                'external_writes': 0,
                'posted_to_asana': 0}

    def _check_account(self, account_id):
        if account_id not in self.account_ids:
            raise ValueError('Account outside configured book of business')

