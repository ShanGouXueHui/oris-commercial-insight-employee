import unittest

from app.ota_scheduler import (
    SCHEDULER_ORDER,
    build_scheduler_baseline,
    get_scheduler_control,
    summarize_scheduler,
)


class Module69OtaSchedulerTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_scheduler_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['controls'], [])

    def test_enabled_returns_controls_in_order(self):
        result = build_scheduler_baseline(env={'ORIS_OTA_SCHEDULER_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'ota_scheduler_baseline_defined')
        self.assertEqual(result['control_count'], 7)
        self.assertEqual(result['control_names'], list(SCHEDULER_ORDER))
        self.assertEqual(result['cadence_minutes'], 10)

    def test_install_and_target_controls_are_defined(self):
        install = get_scheduler_control('manual_install_only')
        target = get_scheduler_control('unified_entrypoint_target')
        self.assertEqual(install['implementation'], 'scripts/install_unified_ota_loop.sh')
        self.assertEqual(target['implementation'], 'unified-OTA-entry.sh')
        self.assertTrue(install['safe_default'])

    def test_log_and_reinstall_controls_are_defined(self):
        logs = get_scheduler_control('ota_log_append')
        reinstall = get_scheduler_control('safe_reinstall')
        privilege = get_scheduler_control('least_privilege_mode')
        self.assertIn('reports/ota', logs['implementation'])
        self.assertIn('ORIS_UNIFIED_OTA_LOOP', reinstall['implementation'])
        self.assertEqual(privilege['implementation'], 'user_scope')

    def test_summary_is_compact_and_safe(self):
        summary = summarize_scheduler(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['control_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
