import unittest

from app.m53 import build_m53_rollup, summarize_m53


class Module53Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m53_rollup({'marker_state': 'ready_marker'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_marker_returns_ready_rollup(self):
        result = build_m53_rollup(
            {'marker_state': 'ready_marker'},
            env={'ORIS_INSIGHT_M53_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['rollup_state'], 'ready_rollup')
        self.assertTrue(result['rollup_visible'])
        self.assertFalse(result['file_written'])

    def test_review_marker_returns_review_rollup(self):
        result = build_m53_rollup(
            {'marker_state': 'review_marker'},
            env={'ORIS_INSIGHT_M53_ENABLED': 'true'},
        )
        self.assertEqual(result['rollup_state'], 'review_rollup')
        self.assertEqual(result['marker_state'], 'review_marker')

    def test_summary_safe_defaults(self):
        summary = summarize_m53(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
