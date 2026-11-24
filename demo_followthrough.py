"""Synthetic follow-through demonstration; no network, no sends, no writes."""
import json
from followthrough import (follow_up_cadence, daily_brief, ApprovalBoundAction,
                           resolve_evidence, carryover_queue, verify_closeout)


def main():
    now = '2030-01-05T00:00:00Z'
    cadence = follow_up_cadence(
        ['account-demo-1', 'account-demo-2', 'account-demo-3', 'account-demo-4'],
        touches=[
            dict(account_id='account-demo-2', sent_at='2030-01-02T09:00:00Z', evidence_id='touch-1'),
            dict(account_id='account-demo-2', sent_at='2030-01-04T09:00:00Z', evidence_id='touch-2'),
            dict(account_id='account-demo-3', sent_at='2030-01-02T09:00:00Z', evidence_id='touch-3'),
            dict(account_id='account-demo-4', sent_at='2030-01-02T09:00:00Z', evidence_id=None),
        ],
        responses=[
            dict(account_id='account-demo-1', received_at='2030-01-03T10:00:00Z', evidence_id='reply-1'),
        ])
    brief = daily_brief(['account-demo-1', 'account-demo-2', 'account-demo-3'],
                        {'account-demo-1': 'closed by verified response; no outreach owed'},
                        reads_complete=False, unchecked_sources=['activity feed page 2'])

    gate = ApprovalBoundAction()
    payload = dict(kind='status_update', account_id='account-demo-2',
                   text='Follow-up ladder exhausted; human review proposed.')
    gate.present(payload)
    gate.approve(payload)
    applied = gate.apply(payload)
    duplicate = gate.apply(payload)
    readback = gate.read_back(payload)

    evidence = resolve_evidence(
        dict(id='rec-demo-9', require_shareable=True),
        primary_rows=[dict(id='rec-demo-9', shareable=False, ref='internal-recording-9')],
        fallback_rows=[dict(id='rec-demo-9', shareable=True, ref='share-link-9')])

    loops = carryover_queue([
        dict(id='loop-1', account_id='account-demo-2', kind='pending_approval',
             owner='Demo CSM', due_on='2030-01-04'),
        dict(id='loop-2', account_id='account-demo-3', kind='missing_item',
             owner=None, due_on=None)], now=now)

    closeout = verify_closeout(dict(form='eod', account_id='account-demo-2', text='Day complete'),
                               saved_rows=[dict(payload_hash='no-match', id='saved-1')])

    print(json.dumps({'mode': 'synthetic review only; nothing sent, posted or written',
                      'follow_up_cadence': cadence, 'daily_brief': brief,
                      'approval_bound_action': {'applied': applied, 'duplicate_attempt': duplicate,
                                                'read_back': readback},
                      'evidence_resolution': evidence, 'carryover_queue': loops,
                      'closeout_verification': closeout}, indent=2))


if __name__ == '__main__':
    main()

