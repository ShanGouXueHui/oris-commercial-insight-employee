import unittest

from app.m59 import build_m59_rollup, summarize_m59


class Module59Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m59_rollup({'summary_state': 'ready_summary'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_summary_returns_ready_rollup(self):
        result = build_m59_rollup(
            {'summary_state': 'ready_summary'},
            env={'ORIS_INSIGHT_M59_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['rollup_state'], 'ready_rollup')
        self.assertTrue(result['rollup_visible'])
        self.assertFalse(result['file_written'])

    def test_review_summary_returns_review_rollup(self):
        result = build_m59_rollup(
            {'summary_state': 'review_summary'},
            env={'ORIS_INSIGHT_M59_ENABLED': 'true'},
        )
        self.assertEqual(result['rollup_state'], 'review_rollup')
        self.assertEqual(result['summary_state'], 'review_summary')

    def test_summary_safe_defaults(self):
        summary = summarize_m59(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
