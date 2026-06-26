import unittest

from app.m38 import build_m45_snapshot, summarize_m45


class Module45Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m45_snapshot({'summary_state': 'clear'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_enabled_snapshot_visible(self):
        result = build_m45_snapshot(
            {'summary_state': 'clear', 'gate_status': 'open'},
            env={'ORIS_INSIGHT_M45_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertTrue(result['snapshot_visible'])
        self.assertEqual(result['snapshot_state'], 'clear')
        self.assertFalse(result['file_written'])

    def test_snapshot_preserves_hold_state(self):
        result = build_m45_snapshot(
            {'summary_state': 'hold', 'gate_status': 'closed'},
            env={'ORIS_INSIGHT_M45_ENABLED': 'true'},
        )
        self.assertEqual(result['snapshot_state'], 'hold')
        self.assertEqual(result['gate_status'], 'closed')

    def test_summary_safe_defaults(self):
        summary = summarize_m45(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
