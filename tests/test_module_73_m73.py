import unittest

from app.m73 import CHECKS, build_m73, summarize_m73


class Module73Tests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_m73(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])

    def test_enabled_returns_checks(self):
        result = build_m73(env={'ORIS_M73_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'm73_defined')
        self.assertEqual(result['check_count'], 5)
        self.assertEqual(result['checks'], list(CHECKS))

    def test_ready_requires_operator_note(self):
        result = build_m73(env={'ORIS_M73_ENABLED': '1'})
        self.assertFalse(result['ready'])
        self.assertTrue(result['operator_note_required'])

    def test_summary_is_compact(self):
        summary = summarize_m73(env={})
        self.assertFalse(summary['enabled'])
        self.assertEqual(summary['status'], 'disabled')
        self.assertEqual(summary['check_count'], 0)
        self.assertFalse(summary['ready'])

    def test_enabled_does_not_publish(self):
        result = build_m73(env={'ORIS_M73_ENABLED': 'yes'})
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertFalse(result['external_calls'])


if __name__ == '__main__':
    unittest.main()
