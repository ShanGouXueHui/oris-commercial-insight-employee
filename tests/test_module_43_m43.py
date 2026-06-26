import unittest

from app.m38 import build_m43_gate, summarize_m43


class Module43Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m43_gate({'summary_status': 'complete'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_complete_summary_opens_gate(self):
        result = build_m43_gate({'summary_status': 'complete'}, env={'ORIS_INSIGHT_M43_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['gate_status'], 'open')
        self.assertFalse(result['file_written'])

    def test_incomplete_summary_closes_gate(self):
        result = build_m43_gate({'summary_status': 'incomplete'}, env={'ORIS_INSIGHT_M43_ENABLED': 'true'})
        self.assertEqual(result['gate_status'], 'closed')
        self.assertEqual(result['source_summary_status'], 'incomplete')

    def test_summary_safe_defaults(self):
        summary = summarize_m43(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
