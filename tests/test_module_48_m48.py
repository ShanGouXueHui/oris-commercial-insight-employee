import unittest

from app.m48 import build_m48_strip, summarize_m48


class Module48Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m48_strip({'badge_label': 'ready'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_badge_returns_ready_strip(self):
        result = build_m48_strip(
            {'badge_label': 'ready'},
            env={'ORIS_INSIGHT_M48_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['strip_state'], 'visible_ready')
        self.assertTrue(result['strip_visible'])
        self.assertFalse(result['file_written'])

    def test_review_badge_returns_review_strip(self):
        result = build_m48_strip(
            {'badge_label': 'review'},
            env={'ORIS_INSIGHT_M48_ENABLED': 'true'},
        )
        self.assertEqual(result['strip_state'], 'visible_review')
        self.assertEqual(result['badge_label'], 'review')

    def test_summary_safe_defaults(self):
        summary = summarize_m48(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
