import unittest

from app.m38 import build_m44_summary, summarize_m44


class Module44Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m44_summary({'gate_status': 'open'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_open_gate_returns_clear(self):
        result = build_m44_summary({'gate_status': 'open'}, env={'ORIS_INSIGHT_M44_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_state'], 'clear')
        self.assertFalse(result['file_written'])

    def test_closed_gate_returns_hold(self):
        result = build_m44_summary({'gate_status': 'closed'}, env={'ORIS_INSIGHT_M44_ENABLED': 'true'})
        self.assertEqual(result['summary_state'], 'hold')
        self.assertEqual(result['gate_status'], 'closed')

    def test_summary_safe_defaults(self):
        summary = summarize_m44(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
