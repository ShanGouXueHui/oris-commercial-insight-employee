import unittest

from app.m38 import build_m39_health, summarize_m39


class Module39Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m39_health({'item_count': 1}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_enabled_reports_ready(self):
        result = build_m39_health({'item_count': 2}, env={'ORIS_INSIGHT_M39_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['health_status'], 'ready')
        self.assertFalse(result['file_written'])

    def test_empty_and_bounded_status(self):
        empty = build_m39_health({'item_count': 0}, env={'ORIS_INSIGHT_M39_ENABLED': 'true'})
        bounded = build_m39_health({'item_count': 100}, env={'ORIS_INSIGHT_M39_ENABLED': 'true'})
        self.assertEqual(empty['health_status'], 'empty')
        self.assertEqual(bounded['health_status'], 'bounded')

    def test_summary_safe_defaults(self):
        summary = summarize_m39(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
