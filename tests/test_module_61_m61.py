import unittest

from app.m61 import build_m61_summary, summarize_m61


class Module61Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m61_summary({'capsule_state': 'ready_capsule'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_capsule_returns_ready_summary(self):
        result = build_m61_summary(
            {'capsule_state': 'ready_capsule'},
            env={'ORIS_INSIGHT_M61_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_state'], 'ready_summary')
        self.assertTrue(result['summary_visible'])
        self.assertFalse(result['file_written'])

    def test_review_capsule_returns_review_summary(self):
        result = build_m61_summary(
            {'capsule_state': 'review_capsule'},
            env={'ORIS_INSIGHT_M61_ENABLED': 'true'},
        )
        self.assertEqual(result['summary_state'], 'review_summary')
        self.assertEqual(result['capsule_state'], 'review_capsule')

    def test_summary_safe_defaults(self):
        summary = summarize_m61(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
