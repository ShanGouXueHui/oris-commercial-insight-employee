import unittest

from app.m46 import build_m46_digest, summarize_m46


class Module46Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m46_digest({'snapshot_state': 'clear'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_clear_open_snapshot_returns_green(self):
        result = build_m46_digest(
            {'snapshot_state': 'clear', 'gate_status': 'open'},
            env={'ORIS_INSIGHT_M46_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['digest_state'], 'green')
        self.assertTrue(result['digest_visible'])
        self.assertFalse(result['file_written'])

    def test_hold_snapshot_returns_amber(self):
        result = build_m46_digest(
            {'snapshot_state': 'hold', 'gate_status': 'closed'},
            env={'ORIS_INSIGHT_M46_ENABLED': 'true'},
        )
        self.assertEqual(result['digest_state'], 'amber')
        self.assertEqual(result['gate_status'], 'closed')

    def test_summary_safe_defaults(self):
        summary = summarize_m46(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
