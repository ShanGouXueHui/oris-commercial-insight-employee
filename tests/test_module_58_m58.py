import unittest

from app.m58 import build_m58_summary, summarize_m58


class Module58Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m58_summary({'marker_state': 'ready_marker'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_marker_returns_ready_summary(self):
        result = build_m58_summary(
            {'marker_state': 'ready_marker'},
            env={'ORIS_INSIGHT_M58_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_state'], 'ready_summary')
        self.assertTrue(result['summary_visible'])
        self.assertFalse(result['file_written'])

    def test_review_marker_returns_review_summary(self):
        result = build_m58_summary(
            {'marker_state': 'review_marker'},
            env={'ORIS_INSIGHT_M58_ENABLED': 'true'},
        )
        self.assertEqual(result['summary_state'], 'review_summary')
        self.assertEqual(result['marker_state'], 'review_marker')

    def test_summary_safe_defaults(self):
        summary = summarize_m58(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
