import unittest

from app.unified_ota import (
    CONTROL_ORDER,
    build_unified_ota_baseline,
    get_ota_control,
    summarize_unified_ota,
)


class Module68UnifiedOtaTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_unified_ota_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['controls'], [])

    def test_enabled_returns_controls_in_order(self):
        result = build_unified_ota_baseline(env={'ORIS_UNIFIED_OTA_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'unified_ota_baseline_defined')
        self.assertEqual(result['control_count'], 7)
        self.assertEqual(result['control_names'], list(CONTROL_ORDER))

    def test_entrypoint_and_fast_forward_controls_are_defined(self):
        entry = get_ota_control('single_entrypoint')
        pull = get_ota_control('repo_fast_forward_only')
        self.assertEqual(entry['implementation'], 'unified-OTA-entry.sh')
        self.assertIn('ff-only', pull['implementation'])
        self.assertTrue(entry['safe_default'])

    def test_lock_and_runner_controls_are_defined(self):
        lock = get_ota_control('lock_guard')
        runner = get_ota_control('allowlisted_runner')
        self.assertIn('lock', lock['implementation'])
        self.assertEqual(runner['implementation'], 'unified-OTA-entry.sh')

    def test_logs_and_evidence_controls_are_defined(self):
        logs = get_ota_control('timestamped_logs')
        evidence = get_ota_control('evidence_autocommit')
        no_release = get_ota_control('no_release_publish')
        self.assertEqual(logs['implementation'], 'reports/ota')
        self.assertIn('push', evidence['implementation'])
        self.assertIn('disabled', no_release['implementation'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_unified_ota(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['control_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
