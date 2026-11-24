import unittest
from followthrough import (follow_up_cadence, daily_brief, ApprovalBoundAction,
                           resolve_evidence, carryover_queue, verify_closeout, DEFAULT_LADDER)

NOW = '2030-01-05T00:00:00Z'


def touch(account, day, evidence='ev'):
    return dict(account_id=account, sent_at='2030-01-0%dT09:00:00Z' % day, evidence_id=evidence)


def reply(account, day, evidence='ev-r'):
    return dict(account_id=account, received_at='2030-01-0%dT10:00:00Z' % day, evidence_id=evidence)


class FollowUpCadenceTest(unittest.TestCase):
    def test_first_trigger_when_no_verified_touch(self):
        result = follow_up_cadence(['a1'], [], [])
        entry = result['accounts'][0]
        self.assertEqual(entry['outreach_owed'], DEFAULT_LADDER[0])
        self.assertEqual(entry['trigger'], 'first trigger')

    def test_repeat_entry_after_verified_touches(self):
        result = follow_up_cadence(['a1'], [touch('a1', 1, 't1'), touch('a1', 2, 't2')], [])
        entry = result['accounts'][0]
        self.assertEqual(entry['attempts'], 2)
        self.assertEqual(entry['outreach_owed'], DEFAULT_LADDER[2])
        self.assertEqual(entry['trigger'], 'repeat entry')

    def test_unverified_touch_not_counted(self):
        result = follow_up_cadence(['a1'], [touch('a1', 1, None)], [])
        self.assertEqual(result['accounts'][0]['attempts'], 0)

    def test_verified_response_closes_cycle(self):
        result = follow_up_cadence(['a1'], [touch('a1', 1, 't1')], [reply('a1', 2, 'r1')])
        entry = result['accounts'][0]
        self.assertEqual(entry['cycle'], 'closed by verified response')
        self.assertIsNone(entry['outreach_owed'])

    def test_unverified_response_does_not_close(self):
        result = follow_up_cadence(['a1'], [touch('a1', 1, 't1')], [reply('a1', 2, None)])
        self.assertEqual(result['accounts'][0]['cycle'], 'open')

    def test_touch_after_response_starts_new_cycle(self):
        result = follow_up_cadence(['a1'],
                                   [touch('a1', 1, 't1'), touch('a1', 4, 't2')],
                                   [reply('a1', 2, 'r1')])
        entry = result['accounts'][0]
        self.assertEqual(entry['attempts'], 1)
        self.assertEqual(entry['outreach_owed'], DEFAULT_LADDER[1])

    def test_ladder_exhausted_escalates_and_proposes_status_change(self):
        touches = [touch('a1', d, 't%d' % d) for d in (1, 2, 3)]
        result = follow_up_cadence(['a1'], touches, [])
        self.assertIn('escalate to human', result['accounts'][0]['outreach_owed'])
        proposal = result['status_change_proposals'][0]
        self.assertIn('requires human approval', proposal['status'])
        self.assertEqual(result['sends_performed'], 0)

    def test_empty_ladder_rejected(self):
        with self.assertRaises(ValueError):
            follow_up_cadence(['a1'], [], [], ladder=())


class DailyBriefTest(unittest.TestCase):
    def test_every_account_has_action_or_named_gap(self):
        brief = daily_brief(['a1', 'a2'], {'a1': 'review renewal'})
        self.assertEqual(brief['accounts_reviewed'], 1)
        self.assertEqual(brief['gaps'][0]['account_id'], 'a2')
        self.assertEqual(brief['total_accounts'], 2)

    def test_incomplete_reads_forbid_nothing_new(self):
        brief = daily_brief(['a1'], {}, reads_complete=False, unchecked_sources=['page 2'])
        self.assertIn('never report nothing new', brief['summary_rule'])
        self.assertFalse(brief['coverage_complete'])


class ApprovalBoundActionTest(unittest.TestCase):
    def setUp(self):
        self.gate = ApprovalBoundAction()
        self.payload = dict(kind='status_update', account_id='a1', text='exact text')

    def test_apply_requires_exact_approval(self):
        self.gate.present(self.payload)
        with self.assertRaises(PermissionError):
            self.gate.apply(self.payload)

    def test_approve_requires_present(self):
        with self.assertRaises(ValueError):
            self.gate.approve(self.payload)

    def test_apply_once_then_duplicate_refused(self):
        self.gate.present(self.payload)
        self.gate.approve(self.payload)
        record = self.gate.apply(self.payload)
        self.assertEqual(record['status'], 'mock applied')
        self.assertIn('duplicate refused', self.gate.apply(self.payload))

    def test_read_back_verifies_saved_record(self):
        self.gate.present(self.payload)
        self.gate.approve(self.payload)
        self.gate.apply(self.payload)
        self.assertTrue(self.gate.read_back(self.payload)['verified'])
        other = dict(self.payload, text='different text')
        self.assertFalse(self.gate.read_back(other)['verified'])

    def test_uncertain_outcome_blocks_retry_until_reconciled(self):
        self.gate.present(self.payload)
        self.gate.approve(self.payload)
        self.gate.report_uncertain(self.payload)
        with self.assertRaises(ValueError):
            self.gate.apply(self.payload)
        result = self.gate.reconcile(self.payload, 'human confirmed nothing saved')
        self.assertIn('fresh exact approval', result)
        with self.assertRaises(PermissionError):
            self.gate.apply(self.payload)

    def test_reconcile_requires_attestation(self):
        self.gate.present(self.payload)
        self.gate.report_uncertain(self.payload)
        with self.assertRaises(ValueError):
            self.gate.reconcile(self.payload, '')


class ResolveEvidenceTest(unittest.TestCase):
    def test_exact_id_match_primary(self):
        result = resolve_evidence(dict(id='r1'), [dict(id='r1', shareable=True)])
        self.assertEqual(result['status'], 'matched')
        self.assertFalse(result['fallback_used'])

    def test_internal_reference_held_when_shareable_required(self):
        result = resolve_evidence(dict(id='r1', require_shareable=True),
                                  [dict(id='r1', shareable=False)])
        self.assertEqual(result['status'], 'hold')
        self.assertIn('cannot substitute', result['reason'])

    def test_documented_fallback_labeled(self):
        result = resolve_evidence(dict(id='r1'), [], [dict(id='r1', shareable=True)])
        self.assertEqual(result['source'], 'documented fallback')
        self.assertTrue(result['fallback_used'])

    def test_incomplete_reads_forbid_latest_claim(self):
        result = resolve_evidence(dict(id='r1'), [], reads_complete=False)
        self.assertEqual(result['status'], 'unknown')
        self.assertTrue(result['may_not_claim_latest'])

    def test_duplicate_exact_ids_hold(self):
        rows = [dict(id='r1'), dict(id='r1')]
        self.assertEqual(resolve_evidence(dict(id='r1'), rows)['status'], 'hold')

    def test_missing_id_rejected(self):
        with self.assertRaises(ValueError):
            resolve_evidence(dict(), [])


class CarryoverQueueTest(unittest.TestCase):
    def loop(self, lid, owner='Demo CSM', due='2030-01-04', kind='pending_approval'):
        return dict(id=lid, account_id='a1', kind=kind, owner=owner, due_on=due)

    def test_overdue_flagged(self):
        result = carryover_queue([self.loop('l1')], NOW)
        self.assertTrue(result['open_loops'][0]['overdue'])

    def test_missing_owner_or_due_carried_and_flagged(self):
        result = carryover_queue([self.loop('l1', owner=None, due=None)], NOW)
        self.assertEqual(result['carried'], 1)
        self.assertIn('missing', result['incomplete_rows'][0]['incomplete'])

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            carryover_queue([self.loop('l1'), self.loop('l1')], NOW)

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            carryover_queue([self.loop('l1', kind='mystery')], NOW)


class VerifyCloseoutTest(unittest.TestCase):
    def setUp(self):
        self.payload = dict(form='eod', account_id='a1', text='done')
        from workflow import digest
        self.key = digest(self.payload)

    def test_verified_saved(self):
        result = verify_closeout(self.payload, [dict(payload_hash=self.key, id='s1')])
        self.assertEqual(result['status'], 'verified saved')

    def test_resubmit_after_verified_refused(self):
        result = verify_closeout(self.payload, [dict(payload_hash=self.key)], resubmit_requested=True)
        self.assertEqual(result['status'], 'refused')

    def test_no_match_holds_and_blocks_resubmission(self):
        result = verify_closeout(self.payload, [dict(payload_hash='other')])
        self.assertEqual(result['status'], 'hold')
        self.assertIn('blocked', result['resubmission'])

    def test_multiple_matches_hold(self):
        rows = [dict(payload_hash=self.key), dict(payload_hash=self.key)]
        self.assertEqual(verify_closeout(self.payload, rows)['status'], 'hold')


if __name__ == '__main__':
    unittest.main()

