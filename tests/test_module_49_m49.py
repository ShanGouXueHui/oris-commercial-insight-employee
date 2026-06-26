import unittest

from app.m49 import build_m49_summary, summarize_m49


class Module49Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m49_summary({'strip_state': 'visible_ready'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_strip_returns_ready_summary(self):
        result = build_m49_summary(
            {'strip_state': 'visible_ready'},
            env={'ORIS_INSIGHT_M49_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_status'], 'ready_summary')
        self.assertTrue(result['summary_visible'])
        self.assertFalse(result['file_written'])

    def test_review_strip_returns_review_summary(self):
        result = build_m49_summary(
            {'strip_state': 'visible_review'},
            env={'ORIS_INSIGHT_M49_ENABLED': 'true'},
        )
        self.assertEqual(result['summary_status'], 'review_summary')
        self.assertEqual(result['strip_state'], 'visible_review')

    def test_summary_safe_defaults(self):
        summary = summarize_m49(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
