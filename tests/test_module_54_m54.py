import unittest

from app.m54 import build_m54_badge, summarize_m54


class Module54Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m54_badge({'rollup_state': 'ready_rollup'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_rollup_returns_ready_badge(self):
        result = build_m54_badge(
            {'rollup_state': 'ready_rollup'},
            env={'ORIS_INSIGHT_M54_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['badge_state'], 'ready_badge')
        self.assertTrue(result['badge_visible'])
        self.assertFalse(result['file_written'])

    def test_review_rollup_returns_review_badge(self):
        result = build_m54_badge(
            {'rollup_state': 'review_rollup'},
            env={'ORIS_INSIGHT_M54_ENABLED': 'true'},
        )
        self.assertEqual(result['badge_state'], 'review_badge')
        self.assertEqual(result['rollup_state'], 'review_rollup')

    def test_summary_safe_defaults(self):
        summary = summarize_m54(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
