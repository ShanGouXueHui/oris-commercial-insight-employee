import unittest

from app.commercial_storage import (
    STORE_ORDER,
    build_storage_boundary_baseline,
    get_storage_boundary,
    summarize_storage_boundaries,
)


class Module65CommercialStorageTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_storage_boundary_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['stores'], [])

    def test_enabled_returns_storage_boundaries_in_order(self):
        result = build_storage_boundary_baseline(env={'ORIS_COMMERCIAL_STORAGE_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'storage_boundary_baseline_defined')
        self.assertEqual(result['store_count'], 8)
        self.assertEqual(result['store_names'], list(STORE_ORDER))
        self.assertTrue(result['local_evidence_separated'])

    def test_core_stores_are_tenant_owned_and_migration_ready(self):
        tenant = get_storage_boundary('tenant_store')
        workspace = get_storage_boundary('workspace_store')
        project = get_storage_boundary('project_store')
        self.assertTrue(tenant['tenant_owned'])
        self.assertTrue(workspace['migration_required'])
        self.assertIn('workspace_parent', project['required_controls'])

    def test_artifact_stores_preserve_traceability(self):
        insight = get_storage_boundary('insight_store')
        evidence = get_storage_boundary('evidence_store')
        execution = get_storage_boundary('execution_store')
        self.assertIn('version_state', insight['required_controls'])
        self.assertIn('provenance', evidence['required_controls'])
        self.assertIn('failure_reason', execution['required_controls'])

    def test_append_only_stores_are_defined(self):
        audit = get_storage_boundary('audit_store')
        meter = get_storage_boundary('meter_store')
        self.assertEqual(audit['persistence_mode'], 'append_only')
        self.assertEqual(meter['persistence_mode'], 'append_only')
        self.assertIn('billing_disabled_by_default', meter['required_controls'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_storage_boundaries(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['store_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
