import unittest

from app.m56 import build_m56_capsule, summarize_m56


class Module56Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m56_capsule({'summary_state': 'ready_summary'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_summary_returns_ready_capsule(self):
        result = build_m56_capsule(
            {'summary_state': 'ready_summary'},
            env={'ORIS_INSIGHT_M56_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['capsule_state'], 'ready_capsule')
        self.assertTrue(result['capsule_visible'])
        self.assertFalse(result['file_written'])

    def test_review_summary_returns_review_capsule(self):
        result = build_m56_capsule(
            {'summary_state': 'review_summary'},
            env={'ORIS_INSIGHT_M56_ENABLED': 'true'},
        )
        self.assertEqual(result['capsule_state'], 'review_capsule')
        self.assertEqual(result['summary_state'], 'review_summary')

    def test_summary_safe_defaults(self):
        summary = summarize_m56(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
