import unittest
from operations import signal_triage, intake_coverage, portfolio_health, capability_map, adoption_benchmarks
from system import CSWorkspaceCycle


def make_cycle(complete=True):
    c = CSWorkspaceCycle(
        ['account-demo'],
        [dict(gid='task-demo', account_id='account-demo', name='Demo account review',
              period='2030-Q1', custom_fields={'health': None})],
        [dict(account_id='account-demo', question='Approve?', owner='Demo CSM')])
    c.start_day([], [], [], '2030-01-01T00:00:00Z', '2030-01-02T00:00:00Z', intake_complete=complete)
    return c


class SystemTests(unittest.TestCase):
    def test_sod_required(self):
        with self.assertRaises(ValueError):
            CSWorkspaceCycle([], []).end_day()

    def test_prep_and_summary_do_not_complete_checkin(self):
        c = make_cycle()
        c.prepare_review('account-demo')
        c.after_engagement('account-demo', [])
        self.assertEqual(c.end_day()['check_ins_not_verified'], ['account-demo'])

    def test_explicit_checkin_needs_evidence(self):
        c = make_cycle()
        with self.assertRaises(ValueError):
            c.record_check_in('account-demo', '')
        c.record_check_in('account-demo', 'demo-note')
        self.assertEqual(c.end_day()['check_ins_not_verified'], [])

    def test_incomplete_reads_survive_eod(self):
        c = make_cycle(False)
        self.assertEqual(c.end_day()['status'], 'coverage incomplete')
        self.assertFalse(c.prepare_review('account-demo')['coverage_complete'])

    def test_unresolved_survives_handoff(self):
        self.assertEqual(make_cycle().end_day()['unresolved_decisions'][0]['question'], 'Approve?')

    def test_reconciliation_integrated_but_not_live(self):
        c = make_cycle()
        p = c.reconciliation.propose([dict(id='evidence-demo', account_id='account-demo',
                                           field='health', period='2030-Q1', value='green')],
                                     field='health')[0][0]
        c.reconciliation.approve(p)
        c.reconciliation.apply(p)
        self.assertEqual(len(c.end_day()['mock_teammate_audit']), 1)
        self.assertEqual(c.end_day()['external_writes'], 0)
        self.assertEqual(c.end_day()['posted_to_asana'], 0)

    def test_outside_book_rejected(self):
        with self.assertRaises(ValueError):
            make_cycle().prepare_review('other')

    def test_draft_kind_enforced(self):
        c = make_cycle()
        with self.assertRaises(ValueError):
            c.set_drafts([dict(id='d1', account_id='account-demo', kind='email', text='No')])

    def test_updated_drafts_recounted_at_eod(self):
        c = make_cycle()
        c.set_drafts([dict(id='d1', account_id='account-demo', kind='comment', text='Draft')])
        c.set_drafts([])
        self.assertEqual(c.end_day()['handoff_manifest']['count'], 0)

    def test_whole_demo_cycle(self):
        from demo_system import run
        out = run()
        self.assertEqual(out['end_of_day']['external_writes'], 0)
        self.assertEqual(out['end_of_day']['status'], 'mock coverage complete')
        self.assertEqual(out['end_of_day']['handoff_manifest']['count'], 1)
        self.assertEqual(len(out['teammate_proposals']), 1)
        self.assertEqual(out['end_of_day']['mock_teammate_audit'], [])

    def test_complete_cycle_handles_partial_reads(self):
        c = make_cycle(False)
        c.after_engagement('account-demo', [dict(account_id='account-demo', kind='commitment',
                                                 owner='Demo CSM', evidence_id='demo-note',
                                                 text='Review', due_on='2030-01-03')])
        out = c.end_day()
        self.assertEqual(out['status'], 'coverage incomplete')


class SignalTriageTests(unittest.TestCase):
    def test_low_utilization_flags_not_changes(self):
        out = signal_triage([dict(account_id='a1', period='2030-Q1', utilization=0.5,
                                  retention_score='green', qualitative=[], support_tickets=0)])
        self.assertEqual(out['flags'][0]['status'], 'flagged for human review')
        self.assertIn('utilization', out['flags'][0]['reasons'][0])

    def test_missing_signal_escalates_not_flags(self):
        out = signal_triage([dict(account_id='a1', period='2030-Q1', utilization=None,
                                  retention_score='green', qualitative=[], support_tickets=0)])
        self.assertFalse(out['flags'])
        self.assertIn('utilization', out['escalations'][0]['reason'])

    def test_contradictory_versions_escalate(self):
        row = dict(account_id='a1', period='2030-Q1', utilization=0.9,
                   retention_score='green', qualitative=[], support_tickets=0)
        out = signal_triage([row, dict(row, utilization=0.1)])
        self.assertEqual(out['escalations'][0]['reason'],
                         'contradictory signal versions; human reconciles')

    def test_qualitative_signals_flag(self):
        out = signal_triage([dict(account_id='a1', period='2030-Q1', utilization=0.9,
                                  retention_score='green', qualitative=['champion departed'],
                                  support_tickets=0)])
        self.assertIn('qualitative: champion departed', out['flags'][0]['reasons'])

    def test_healthy_account_no_flag(self):
        out = signal_triage([dict(account_id='a1', period='2030-Q1', utilization=0.95,
                                  retention_score='green', qualitative=[], support_tickets=2)])
        self.assertEqual((out['flags'], out['escalations']), ([], []))


class PortfolioTests(unittest.TestCase):
    def test_blank_health_is_unknown_not_healthy(self):
        out = portfolio_health([dict(gid='t1', account_id='a1', custom_fields={'health': None},
                                     last_reviewed_at=None)], now='2030-01-31T00:00:00Z')
        self.assertEqual(out['health_counts']['unknown'], 1)
        self.assertEqual(out['unknown_health'], ['a1'])

    def test_stale_review_surfaced(self):
        out = portfolio_health([dict(gid='t1', account_id='a1', custom_fields={'health': 'green'},
                                     last_reviewed_at='2029-12-01T00:00:00Z')],
                               now='2030-01-31T00:00:00Z', reviewed_within_days=30)
        self.assertEqual(out['unreviewed'][0]['account_id'], 'a1')

    def test_duplicate_gid_rejected(self):
        row = dict(gid='t1', account_id='a1', custom_fields={}, last_reviewed_at=None)
        with self.assertRaises(ValueError):
            portfolio_health([row, row], now='2030-01-31T00:00:00Z')


class CapabilityMapTests(unittest.TestCase):
    def test_high_volume_repeatable_maps_to_ai_studio(self):
        out = capability_map([dict(id='w1', name='Intake', volume='high',
                                   structure='repeatable', systems=[])])
        self.assertEqual(out['proposals'][0]['candidate'], 'ai_studio_rule')
        self.assertEqual(out['built'], 0)

    def test_judgment_maps_to_teammate(self):
        out = capability_map([dict(id='w1', name='Risk review', volume='low',
                                   structure='judgment', systems=[])])
        self.assertEqual(out['proposals'][0]['candidate'], 'ai_teammate')

    def test_external_systems_map_to_mcp(self):
        out = capability_map([dict(id='w1', name='Warehouse pull', volume='low',
                                   structure='repeatable', systems=['warehouse'])])
        self.assertEqual(out['proposals'][0]['candidate'], 'mcp_integration')

    def test_incomplete_description_goes_manual(self):
        out = capability_map([dict(id='w1', name='Mystery', volume='medium',
                                   structure='repeatable', systems=[])])
        self.assertEqual(out['proposals'][0]['candidate'], 'manual')


class AdoptionTests(unittest.TestCase):
    def test_on_track_and_behind(self):
        out = adoption_benchmarks([
            dict(account_id='a1', day=30, active_workflows=2, ai_requests=100),
            dict(account_id='a2', day=30, active_workflows=0, ai_requests=0)], {'30': 1, '60': 3, '90': 5})
        self.assertEqual([r['status'] for r in out['results']], ['on track', 'behind benchmark'])

    def test_missing_data_escalates_not_behind(self):
        out = adoption_benchmarks([dict(account_id='a1', day=30, active_workflows=None)],
                                  {'30': 1, '60': 3, '90': 5})
        self.assertFalse(out['results'])
        self.assertIn('not marked behind', out['escalations'][0]['reason'])

    def test_undefined_checkpoint_escalates(self):
        out = adoption_benchmarks([dict(account_id='a1', day=45, active_workflows=1)],
                                  {'30': 1, '60': 3, '90': 5})
        self.assertEqual(out['escalations'][0]['reason'], 'no benchmark defined for this checkpoint')

    def test_bad_plan_rejected(self):
        with self.assertRaises(ValueError):
            adoption_benchmarks([], {'45': 1})


class IntakeTests(unittest.TestCase):
    def test_contradictory_submission_versions_rejected(self):
        row = dict(gid='s1', account_id='a1', created_at='2030-01-01T12:00:00Z')
        with self.assertRaises(ValueError):
            intake_coverage([row, dict(row, text='changed')], ['a1'],
                            '2030-01-01T00:00:00Z', '2030-01-02T00:00:00Z')

    def test_duplicate_gid_collapses(self):
        row = dict(gid='s1', account_id='a1', created_at='2030-01-01T12:00:00Z')
        out = intake_coverage([row, row], ['a1'], '2030-01-01T00:00:00Z', '2030-01-02T00:00:00Z')
        self.assertEqual(len(out['submissions']), 1)


if __name__ == '__main__':
    unittest.main()

