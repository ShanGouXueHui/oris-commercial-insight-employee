import unittest

from app.m50 import build_m50_card, summarize_m50


class Module50Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m50_card({'summary_status': 'ready_summary'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_summary_returns_ready_card(self):
        result = build_m50_card(
            {'summary_status': 'ready_summary'},
            env={'ORIS_INSIGHT_M50_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['card_state'], 'ready_card')
        self.assertTrue(result['card_visible'])
        self.assertFalse(result['file_written'])

    def test_review_summary_returns_review_card(self):
        result = build_m50_card(
            {'summary_status': 'review_summary'},
            env={'ORIS_INSIGHT_M50_ENABLED': 'true'},
        )
        self.assertEqual(result['card_state'], 'review_card')
        self.assertEqual(result['summary_status'], 'review_summary')

    def test_summary_safe_defaults(self):
        summary = summarize_m50(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
