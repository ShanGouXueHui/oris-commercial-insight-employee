import unittest

from app.m60 import build_m60_capsule, summarize_m60


class Module60Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m60_capsule({'rollup_state': 'ready_rollup'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_rollup_returns_ready_capsule(self):
        result = build_m60_capsule(
            {'rollup_state': 'ready_rollup'},
            env={'ORIS_INSIGHT_M60_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['capsule_state'], 'ready_capsule')
        self.assertTrue(result['capsule_visible'])
        self.assertFalse(result['file_written'])

    def test_review_rollup_returns_review_capsule(self):
        result = build_m60_capsule(
            {'rollup_state': 'review_rollup'},
            env={'ORIS_INSIGHT_M60_ENABLED': 'true'},
        )
        self.assertEqual(result['capsule_state'], 'review_capsule')
        self.assertEqual(result['rollup_state'], 'review_rollup')

    def test_summary_safe_defaults(self):
        summary = summarize_m60(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
