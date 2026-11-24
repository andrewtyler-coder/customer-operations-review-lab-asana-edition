"""Run one complete synthetic CS workspace cycle; no live connections or writes."""
import json
from system import CSWorkspaceCycle


def run():
    cycle = CSWorkspaceCycle(
        ['account-demo'],
        [dict(gid='task-demo', account_id='account-demo', name='Demo account quarterly review',
              period='2030-Q1', custom_fields={'health': None})],
        [dict(account_id='account-demo', question='Approve next step?', owner='Demo CSM')])
    submission = dict(gid='submission-demo', account_id='account-demo', kind='form_submission',
                      created_at='2030-01-01T12:00:00Z', evidence_id='demo-message',
                      text='Please help with the next step.\nThank you!')
    task = dict(gid='task-demo-open', account_id='account-demo', name='Review next step',
                assignee='Demo CSM', completed=False, due_on='2030-01-01T18:00:00Z', section='In Progress')
    cycle.start_day([submission], [task], [], '2030-01-01T00:00:00Z', '2030-01-02T00:00:00Z')
    prep = cycle.prepare_review('account-demo')
    cycle.after_engagement('account-demo', [dict(account_id='account-demo', kind='commitment',
                                                 owner='Demo CSM', evidence_id='demo-note',
                                                 text='Review next step', due_on='2030-01-03')])
    cycle.record_check_in('account-demo', 'demo-note')
    cycle.set_drafts([dict(id='draft-demo', account_id='account-demo', kind='status_update',
                           text='Draft only: weekly account summary.')])
    proposals, exceptions = cycle.reconciliation.propose(
        [dict(id='evidence-demo', account_id='account-demo', field='health',
              period='2030-Q1', value='green')], field='health')
    # Deliberately leave proposals unapproved: the public demo never self-approves.
    return {'mode': 'synthetic CS workspace cycle; no external actions',
            'account_review_prep': prep,
            'teammate_proposals': [p.__dict__ for p in proposals],
            'exception_queue': exceptions,
            'end_of_day': cycle.end_day()}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

