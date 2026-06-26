import unittest

from app.m38 import build_m40_readiness, summarize_m40


class Module40Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m40_readiness({'health_status': 'ready'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_health_returns_ready(self):
        result = build_m40_readiness({'health_status': 'ready'}, env={'ORIS_INSIGHT_M40_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['readiness_status'], 'ready')
        self.assertFalse(result['file_written'])

    def test_empty_health_returns_blocked(self):
        result = build_m40_readiness({'health_status': 'empty'}, env={'ORIS_INSIGHT_M40_ENABLED': 'true'})
        self.assertEqual(result['readiness_status'], 'blocked')
        self.assertEqual(result['reason'], 'not_ready_for_review')

    def test_summary_safe_defaults(self):
        summary = summarize_m40(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
