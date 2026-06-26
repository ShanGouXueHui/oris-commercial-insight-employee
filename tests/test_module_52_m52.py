import unittest

from app.m52 import build_m52_marker, summarize_m52


class Module52Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m52_marker({'final_state': 'ready'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_summary_returns_ready_marker(self):
        result = build_m52_marker(
            {'final_state': 'ready'},
            env={'ORIS_INSIGHT_M52_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['marker_state'], 'ready_marker')
        self.assertTrue(result['marker_visible'])
        self.assertFalse(result['file_written'])

    def test_review_summary_returns_review_marker(self):
        result = build_m52_marker(
            {'final_state': 'review'},
            env={'ORIS_INSIGHT_M52_ENABLED': 'true'},
        )
        self.assertEqual(result['marker_state'], 'review_marker')
        self.assertEqual(result['final_state'], 'review')

    def test_summary_safe_defaults(self):
        summary = summarize_m52(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
