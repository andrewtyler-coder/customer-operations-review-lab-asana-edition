import unittest
from dataclasses import replace
from workflow import TeammateReviewQueue


def make_task(**over):
    task = dict(gid='task-demo', account_id='account-demo', name='Demo account review',
                period='2030-Q1', custom_fields={'health': None})
    task.update(over)
    return task


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.task = make_task()
        self.evidence = dict(id='evidence-demo', account_id='account-demo', field='health',
                             period='2030-Q1', value='green')
        self.q = TeammateReviewQueue([self.task])

    def proposal(self):
        return self.q.propose([self.evidence], field='health')[0][0]

    def test_duplicate_task_gid_rejected(self):
        with self.assertRaises(ValueError):
            TeammateReviewQueue([self.task, self.task])

    def test_blank_string_can_be_reviewed_and_applied(self):
        self.q.tasks['task-demo']['custom_fields']['health'] = ''
        p = self.proposal()
        self.q.approve(p)
        self.assertEqual(self.q.apply(p), 'mock applied')

    def test_duplicate_import_collapses(self):
        self.assertEqual(len(self.q.propose([self.evidence, self.evidence], field='health')[0]), 1)

    def test_missing_evidence_stays_blank(self):
        proposals, exceptions = self.q.propose([], field='health')
        self.assertFalse(proposals)
        self.assertEqual(exceptions[0]['reason'], 'no evidence')
        self.assertIsNone(self.q.tasks['task-demo']['custom_fields']['health'])

    def test_ambiguous_evidence_escalates(self):
        proposals, exceptions = self.q.propose(
            [self.evidence, dict(self.evidence, value='red')], field='health')
        self.assertFalse(proposals)
        self.assertEqual(exceptions[0]['reason'], 'ambiguous evidence')

    def test_wrong_account_not_matched(self):
        self.assertFalse(self.q.propose([dict(self.evidence, account_id='other')], field='health')[0])

    def test_wrong_period_not_matched(self):
        self.assertFalse(self.q.propose([dict(self.evidence, period='2030-Q2')], field='health')[0])

    def test_wrong_field_not_matched(self):
        self.assertFalse(self.q.propose([self.evidence], field='renewal_risk')[0])

    def test_existing_conflict_not_overwritten(self):
        self.q.tasks['task-demo']['custom_fields']['health'] = 'yellow'
        proposals, exceptions = self.q.propose([self.evidence], field='health')
        self.assertFalse(proposals)
        self.assertEqual(exceptions[0]['reason'], 'existing value conflicts; no overwrite')

    def test_missing_value_escalates(self):
        self.assertFalse(self.q.propose([dict(self.evidence, value='')], field='health')[0])

    def test_no_approval_blocks_apply(self):
        with self.assertRaises(PermissionError):
            self.q.apply(self.proposal())

    def test_changed_payload_invalidates_approval(self):
        p = self.proposal()
        self.q.approve(p)
        with self.assertRaises(PermissionError):
            self.q.apply(replace(p, proposed='red'))

    def test_stale_task_blocks_apply(self):
        p = self.proposal()
        self.q.approve(p)
        self.q.tasks['task-demo']['custom_fields']['health'] = 'Concurrent change'
        with self.assertRaises(ValueError):
            self.q.apply(p)

    def test_approved_apply_idempotent_and_audited(self):
        p = self.proposal()
        self.q.approve(p)
        self.assertEqual(self.q.apply(p), 'mock applied')
        self.assertEqual(self.q.apply(p), 'already applied')
        self.assertEqual(len(self.q.audit), 1)
        self.assertEqual(self.q.tasks['task-demo']['custom_fields']['health'], 'green')

    def test_matching_existing_value_no_change(self):
        self.q.tasks['task-demo']['custom_fields']['health'] = 'green'
        self.assertEqual(self.q.propose([self.evidence], field='health'), ([], []))


if __name__ == '__main__':
    unittest.main()

