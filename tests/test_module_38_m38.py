import unittest

from app.m38 import build_m38_rollup, summarize_m38


class Module38Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m38_rollup([{'id': '1'}], env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_enabled_counts_items(self):
        result = build_m38_rollup([{'id': '1'}, {'id': '2'}], env={'ORIS_INSIGHT_M38_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['item_count'], 2)
        self.assertFalse(result['file_written'])

    def test_rollup_size_is_bounded(self):
        result = build_m38_rollup([{'id': str(index)} for index in range(105)], env={'ORIS_INSIGHT_M38_ENABLED': 'true'})
        self.assertEqual(result['item_count'], 100)

    def test_summary_safe_defaults(self):
        summary = summarize_m38(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
