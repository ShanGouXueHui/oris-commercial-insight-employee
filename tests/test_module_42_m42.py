import unittest

from app.m38 import build_m42_summary, summarize_m42


class Module42Tests(unittest.TestCase):
    def test_disabled_by_default(self):
        result = build_m42_summary({'check_count': 3, 'passed_count': 3}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['file_written'])

    def test_complete_summary_when_no_blocks(self):
        result = build_m42_summary(
            {'check_count': 3, 'passed_count': 3, 'blocked_count': 0},
            env={'ORIS_INSIGHT_M42_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['summary_status'], 'complete')
        self.assertFalse(result['file_written'])

    def test_incomplete_summary_when_blocked(self):
        result = build_m42_summary(
            {'check_count': 3, 'passed_count': 2, 'blocked_count': 1},
            env={'ORIS_INSIGHT_M42_ENABLED': 'true'},
        )
        self.assertEqual(result['summary_status'], 'incomplete')
        self.assertEqual(result['blocked_count'], 1)

    def test_summary_safe_defaults(self):
        summary = summarize_m42(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertFalse(summary['file_written'])


if __name__ == '__main__':
    unittest.main()
