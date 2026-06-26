import unittest

from app.m51 import build_m51_summary, summarize_m51


class Module51Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m51_summary({'card_state': 'ready_card'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_card_returns_ready_final_state(self):
        result = build_m51_summary(
            {'card_state': 'ready_card'},
            env={'ORIS_INSIGHT_M51_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['final_state'], 'ready')
        self.assertTrue(result['summary_visible'])
        self.assertFalse(result['file_written'])

    def test_review_card_returns_review_final_state(self):
        result = build_m51_summary(
            {'card_state': 'review_card'},
            env={'ORIS_INSIGHT_M51_ENABLED': 'true'},
        )
        self.assertEqual(result['final_state'], 'review')
        self.assertEqual(result['card_state'], 'review_card')

    def test_summary_safe_defaults(self):
        summary = summarize_m51(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
