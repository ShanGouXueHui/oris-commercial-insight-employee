import unittest

from app.m55 import build_m55_summary, summarize_m55


class Module55Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m55_summary({'badge_state': 'ready_badge'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_badge_returns_ready_summary(self):
        result = build_m55_summary(
            {'badge_state': 'ready_badge'},
            env={'ORIS_INSIGHT_M55_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_state'], 'ready_summary')
        self.assertTrue(result['summary_visible'])
        self.assertFalse(result['file_written'])

    def test_review_badge_returns_review_summary(self):
        result = build_m55_summary(
            {'badge_state': 'review_badge'},
            env={'ORIS_INSIGHT_M55_ENABLED': 'true'},
        )
        self.assertEqual(result['summary_state'], 'review_summary')
        self.assertEqual(result['badge_state'], 'review_badge')

    def test_summary_safe_defaults(self):
        summary = summarize_m55(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
