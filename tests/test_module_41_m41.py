import unittest

from app.m38 import build_m41_checklist, summarize_m41


class Module41Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m41_checklist({'readiness_status': 'ready'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_status_passes_all_checks(self):
        result = build_m41_checklist({'readiness_status': 'ready'}, env={'ORIS_INSIGHT_M41_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['check_count'], 3)
        self.assertEqual(result['passed_count'], 3)
        self.assertFalse(result['file_written'])

    def test_blocked_status_has_blocked_check(self):
        result = build_m41_checklist({'readiness_status': 'blocked'}, env={'ORIS_INSIGHT_M41_ENABLED': 'true'})
        self.assertEqual(result['blocked_count'], 1)
        self.assertEqual(result['passed_count'], 2)

    def test_summary_safe_defaults(self):
        summary = summarize_m41(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
