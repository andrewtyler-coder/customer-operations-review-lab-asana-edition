"""End-to-end synthetic workspace planning demonstration; no network or writes."""
import json
from operations import (intake_coverage, signal_triage, task_attention,
                        account_review_prep, engagement_proposals, handoff_manifest,
                        portfolio_health, capability_map, adoption_benchmarks)


def main():
    start, cutoff = '2030-01-01T00:00:00Z', '2030-01-02T00:00:00Z'
    submission = dict(gid='submission-demo-1', account_id='account-demo-1', kind='form_submission',
                      created_at='2030-01-01T12:00:00Z', evidence_id='demo-source-1',
                      text='Please review our next step.\nThank you!')
    task = dict(gid='task-demo-1', account_id='account-demo-1', assignee='Demo CSM',
                completed=False, due_on='2030-01-01T18:00:00Z', name='Review proposed next step',
                section='In Progress')
    decisions = [dict(account_id='account-demo-1', question='Approve proposed next step?', owner='Demo CSM')]
    result = {
        'mode': 'synthetic planning only; no Asana connections, posts or updates',
        'intake_coverage': intake_coverage([submission, submission], ['account-demo-1'], start, cutoff),
        'signal_triage': signal_triage([
            dict(account_id='account-demo-1', period='2030-Q1', utilization=0.42,
                 retention_score='yellow', qualitative=['champion departed'], support_tickets=12),
            dict(account_id='account-demo-2', period='2030-Q1', utilization=None,
                 retention_score='green', qualitative=[], support_tickets=3)]),
        'task_attention': task_attention([task], [], cutoff, start),
        'account_review_prep': account_review_prep('account-demo-1',
                                                   [dict(submission, account_id='account-demo-1')],
                                                   [task], decisions),
        'post_engagement': engagement_proposals('account-demo-1', [
            dict(account_id='account-demo-1', kind='commitment', owner='Demo CSM',
                 evidence_id='demo-note-1', text='Review the proposed next step', due_on='2030-01-03'),
            dict(kind='suggestion', text='Consider a future follow-up')]),
        'portfolio_health': portfolio_health([
            dict(gid='task-demo-h1', account_id='account-demo-1',
                 custom_fields={'health': 'green'}, last_reviewed_at='2030-01-01T09:00:00Z'),
            dict(gid='task-demo-h2', account_id='account-demo-2',
                 custom_fields={'health': None}, last_reviewed_at=None)], now=cutoff),
        'capability_map': capability_map([
            dict(id='wf-demo-1', name='Intake triage', volume='high', structure='repeatable', systems=[]),
            dict(id='wf-demo-2', name='Renewal risk review', volume='low', structure='judgment', systems=[]),
            dict(id='wf-demo-3', name='Usage pull from warehouse', volume='low', structure='repeatable',
                 systems=['data-warehouse'])]),
        'adoption_benchmarks': adoption_benchmarks([
            dict(account_id='account-demo-1', day=30, active_workflows=2, ai_requests=140),
            dict(account_id='account-demo-2', day=30, active_workflows=None, ai_requests=None)],
            {'30': 1, '60': 3, '90': 5}),
        'handoff_manifest': handoff_manifest([
            dict(id='draft-demo-1', account_id='account-demo-1', kind='comment',
                 text='Draft only: thank you for the discussion.')])}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

