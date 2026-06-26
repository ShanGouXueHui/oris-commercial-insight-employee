import unittest

from app.m57 import build_m57_marker, summarize_m57


class Module57Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m57_marker({'capsule_state': 'ready_capsule'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_ready_capsule_returns_ready_marker(self):
        result = build_m57_marker(
            {'capsule_state': 'ready_capsule'},
            env={'ORIS_INSIGHT_M57_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['marker_state'], 'ready_marker')
        self.assertTrue(result['marker_visible'])
        self.assertFalse(result['file_written'])

    def test_review_capsule_returns_review_marker(self):
        result = build_m57_marker(
            {'capsule_state': 'review_capsule'},
            env={'ORIS_INSIGHT_M57_ENABLED': 'true'},
        )
        self.assertEqual(result['marker_state'], 'review_marker')
        self.assertEqual(result['capsule_state'], 'review_capsule')

    def test_summary_safe_defaults(self):
        summary = summarize_m57(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
