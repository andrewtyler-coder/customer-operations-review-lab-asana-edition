"""Synthetic, offline AI-teammate review workflow over Asana-shaped CS records.

Models how a conservative AI Teammate drafts custom-field updates on account
tasks and routes everything uncertain to a human exception queue. No Asana
API, MCP server, or any other service connection.
"""
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Proposal:
    task_gid: str
    field: str
    expected: str | None
    proposed: str
    evidence_id: str


class TeammateReviewQueue:
    """In-memory demonstration of a human review boundary, not an approval system.

    Mirrors the gates Asana places on AI Teammates: the teammate may draft
    changes, a person approves each exact change, and anything ambiguous is
    escalated to a human-owned exception queue instead of resolved by guessing.
    """

    def __init__(self, account_tasks):
        self.tasks = {}
        for task in account_tasks:
            if task['gid'] in self.tasks:
                raise ValueError('Duplicate task GID; reconcile intake first')
            self.tasks[task['gid']] = dict(task, custom_fields=dict(task['custom_fields']))
        self.approvals = set()
        self.applied = set()
        self.audit = []

    def propose(self, evidence, field):
        """Draft custom-field updates from exact account/field/period matches."""
        proposals, exceptions = [], []
        for task in self.tasks.values():
            matches = [e for e in evidence if e['account_id'] == task['account_id']
                       and e['field'] == field and e['period'] == task['period']]
            # IDs can repeat in paginated imports; contradictory versions are not collapsed.
            unique = {digest(e): e for e in matches}
            matches = list(unique.values())
            if len(matches) != 1:
                exceptions.append({'task_gid': task['gid'], 'queue': 'Exceptions',
                                   'reason': 'no evidence' if not matches else 'ambiguous evidence'})
                continue
            e = matches[0]
            current = task['custom_fields'].get(field)
            if not e.get('value'):
                exceptions.append({'task_gid': task['gid'], 'queue': 'Exceptions',
                                   'reason': 'missing evidence value'})
            elif current == e['value']:
                continue
            elif current:
                exceptions.append({'task_gid': task['gid'], 'queue': 'Exceptions',
                                   'reason': 'existing value conflicts; no overwrite'})
            else:
                proposals.append(Proposal(task['gid'], field, current, e['value'], e['id']))
        return proposals, exceptions

    def approve(self, proposal):
        """Called only after a human reviews this exact proposal in the demo."""
        self.approvals.add(digest(asdict(proposal)))

    def apply(self, proposal):
        key = digest(asdict(proposal))
        if key in self.applied:
            return 'already applied'
        if key not in self.approvals:
            raise PermissionError('Exact proposal has not been approved')
        task = self.tasks[proposal.task_gid]
        if task['custom_fields'].get(proposal.field) != proposal.expected:
            raise ValueError('Task changed since review; review again')
        task['custom_fields'][proposal.field] = proposal.proposed
        self.applied.add(key)
        self.approvals.remove(key)
        self.audit.append({'proposal_hash': key, **asdict(proposal), 'status': 'mock applied'})
        return 'mock applied'


def main():
    data = json.loads((Path(__file__).parent / 'fixtures' / 'demo.json').read_text())
    queue = TeammateReviewQueue(data['account_tasks'])
    proposals, exceptions = queue.propose(data['evidence'], field='health')
    print(json.dumps({'mode': 'review only; no Asana writes',
                      'proposals': [asdict(p) for p in proposals],
                      'exception_queue': exceptions}, indent=2))


if __name__ == '__main__':
    main()

