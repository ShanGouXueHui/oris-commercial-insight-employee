import unittest

from app.m47 import build_m47_badge, summarize_m47


class Module47Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m47_badge({'digest_state': 'green'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_green_digest_returns_ready_badge(self):
        result = build_m47_badge(
            {'digest_state': 'green'},
            env={'ORIS_INSIGHT_M47_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['badge_label'], 'ready')
        self.assertTrue(result['badge_visible'])
        self.assertFalse(result['file_written'])

    def test_amber_digest_returns_review_badge(self):
        result = build_m47_badge(
            {'digest_state': 'amber'},
            env={'ORIS_INSIGHT_M47_ENABLED': 'true'},
        )
        self.assertEqual(result['badge_label'], 'review')
        self.assertEqual(result['digest_state'], 'amber')

    def test_summary_safe_defaults(self):
        summary = summarize_m47(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
