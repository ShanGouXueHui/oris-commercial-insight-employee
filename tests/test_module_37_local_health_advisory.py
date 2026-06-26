import unittest

from app.local_health_advisory import build_local_health_advisory, summarize_local_health_advisory


class Module37LocalHealthAdvisoryTests(unittest.TestCase):
    def test_advisory_disabled_by_default(self):
        result = build_local_health_advisory({'health_status': 'healthy'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['advisory_visible'])
        self.assertFalse(result['file_written'])

    def test_healthy_status_returns_info_advisory(self):
        result = build_local_health_advisory(
            {'health_status': 'healthy'},
            env={'ORIS_INSIGHT_LOCAL_HEALTH_ADVISORY_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['advisory_severity'], 'info')
        self.assertEqual(result['advisory_code'], 'no_action_needed')

    def test_attention_required_returns_warning_advisory(self):
        result = build_local_health_advisory(
            {'health_status': 'attention_required'},
            env={'ORIS_INSIGHT_LOCAL_HEALTH_ADVISORY_ENABLED': 'true'},
        )
        self.assertEqual(result['advisory_severity'], 'warning')
        self.assertEqual(result['advisory_code'], 'review_failed_or_missing_receipts')

    def test_advisory_summary_safe_defaults(self):
        summary = summarize_local_health_advisory(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['advisory_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
