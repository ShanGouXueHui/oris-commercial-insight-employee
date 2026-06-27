import unittest

from app.ota_instruction_manifest import (
    CONTROL_ORDER,
    build_manifest_baseline,
    get_manifest_control,
    summarize_manifest,
    validate_instruction_manifest,
)


class Module70OtaInstructionManifestTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_manifest_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['controls'], [])

    def test_enabled_returns_controls_in_order(self):
        result = build_manifest_baseline(env={'ORIS_OTA_INSTRUCTION_MANIFEST_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'ota_instruction_manifest_baseline_defined')
        self.assertEqual(result['control_count'], 7)
        self.assertEqual(result['control_names'], list(CONTROL_ORDER))
        self.assertEqual(result['expected_unit_test_count'], 360)

    def test_manifest_source_and_entrypoint_are_defined(self):
        source = get_manifest_control('github_manifest_source')
        entry = get_manifest_control('single_entrypoint_target')
        writer = get_manifest_control('allowlisted_writer')
        self.assertEqual(source['implementation'], 'ops/ota/next_instruction.json')
        self.assertEqual(entry['implementation'], 'unified-OTA-entry.sh')
        self.assertEqual(writer['implementation'], 'scripts/w70.py')

    def test_manifest_validation_accepts_safe_instruction(self):
        manifest = {'active_module': 70, 'entrypoint': 'unified-OTA-entry.sh', 'writer': 'scripts/w70.py', 'expected_unit_test_count': 360, 'allowed_paths': ['reports/testing/latest_test_result.json'], 'stop_condition': 'commercial_ready_true'}
        result = validate_instruction_manifest(manifest)
        self.assertTrue(result['valid'])
        self.assertTrue(result['entrypoint_allowed'])
        self.assertTrue(result['writer_allowlisted'])

    def test_manifest_validation_rejects_missing_or_unlisted_instruction(self):
        result = validate_instruction_manifest({'entrypoint': 'other.sh', 'writer': 'tmp/run.py'})
        self.assertFalse(result['valid'])
        self.assertFalse(result['entrypoint_allowed'])
        self.assertFalse(result['writer_allowlisted'])
        self.assertIn('active_module', result['missing_fields'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_manifest(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['control_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
