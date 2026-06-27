import unittest

from app.commercial_readiness import (
    DIMENSION_ORDER,
    build_commercial_readiness_baseline,
    get_readiness_dimension,
    summarize_commercial_readiness,
)
from app.commercial_architecture import (
    BOUNDARY_ORDER,
    ENTITY_ORDER,
    build_commercial_architecture_baseline,
    get_architecture_boundary,
    get_architecture_entity,
    summarize_commercial_architecture,
)


class Module62CommercialReadinessTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_commercial_readiness_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['dimensions'], [])

    def test_enabled_returns_all_dimensions_in_order(self):
        result = build_commercial_readiness_baseline(
            env={'ORIS_COMMERCIAL_READINESS_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'baseline_defined')
        self.assertEqual(result['dimension_count'], 8)
        self.assertEqual(result['dimension_names'], list(DIMENSION_ORDER))

    def test_tests_and_docs_dimensions_are_commercial_gates(self):
        tests = get_readiness_dimension('tests')
        docs = get_readiness_dimension('docs')
        self.assertEqual(tests['layer'], 'validation')
        self.assertIn('expected test count', tests['baseline_requirement'])
        self.assertEqual(docs['layer'], 'operator_experience')
        self.assertTrue(docs['commercial_readiness_gate'])

    def test_safety_and_configuration_dimensions_keep_default_behavior_stable(self):
        safety = get_readiness_dimension('safety')
        configuration = get_readiness_dimension('configuration')
        self.assertIn('disabled by default', safety['baseline_requirement'])
        self.assertIn('no external call', safety['baseline_requirement'])
        self.assertIn('environment flag', configuration['baseline_requirement'])
        self.assertEqual(configuration['layer'], 'configuration')

    def test_storage_and_api_dimensions_are_tenant_oriented(self):
        storage = get_readiness_dimension('storage')
        api = get_readiness_dimension('api')
        self.assertIn('tenant artifacts', storage['tenant_relevance'])
        self.assertIn('migrations', storage['next_action'])
        self.assertIn('versioned contracts', api['tenant_relevance'])
        self.assertEqual(api['layer'], 'interface')

    def test_security_and_observability_dimensions_cover_operations(self):
        security = get_readiness_dimension('security')
        observability = get_readiness_dimension('observability')
        self.assertIn('tenant isolation', security['baseline_requirement'])
        self.assertIn('RBAC', security['next_action'])
        self.assertIn('run identifiers', observability['baseline_requirement'])
        self.assertEqual(observability['layer'], 'operations')

    def test_dimension_lookup_returns_isolated_copies(self):
        first = get_readiness_dimension('api')
        first['layer'] = 'mutated'
        second = get_readiness_dimension('api')
        self.assertEqual(second['layer'], 'interface')

    def test_summary_is_compact_and_safe(self):
        summary = summarize_commercial_readiness(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['dimension_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


class Module63CommercialArchitectureTests(unittest.TestCase):
    def test_m63_disabled_by_default_is_safe(self):
        result = build_commercial_architecture_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['entities'], [])
        self.assertEqual(result['boundaries'], [])

    def test_m63_enabled_returns_ordered_baseline(self):
        result = build_commercial_architecture_baseline(
            env={'ORIS_COMMERCIAL_ARCHITECTURE_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'architecture_baseline_defined')
        self.assertEqual(result['entity_count'], 8)
        self.assertEqual(result['boundary_count'], 4)
        self.assertEqual(result['entity_names'], list(ENTITY_ORDER))
        self.assertEqual(result['boundary_names'], list(BOUNDARY_ORDER))

    def test_m63_customer_hierarchy_entities_are_explicit(self):
        tenant = get_architecture_entity('tenant')
        workspace = get_architecture_entity('workspace')
        project = get_architecture_entity('project')
        self.assertEqual(tenant['owner_key'], 'tenant_id')
        self.assertIn('tenant_parent', workspace['required_controls'])
        self.assertIn('workspace_parent', project['required_controls'])

    def test_m63_work_artifact_entities_are_traceable(self):
        insight = get_architecture_entity('insight')
        evidence = get_architecture_entity('evidence')
        execution = get_architecture_entity('execution')
        self.assertIn('review_state', insight['required_controls'])
        self.assertIn('provenance', evidence['required_controls'])
        self.assertEqual(execution['owner_key'], 'run_id')
        self.assertIn('diagnostics', execution['required_controls'])

    def test_m63_record_and_metering_entities_are_present(self):
        audit = get_architecture_entity('audit')
        billing = get_architecture_entity('billing_readiness')
        self.assertIn('action', audit['required_controls'])
        self.assertIn('timestamp', audit['required_controls'])
        self.assertIn('usage_unit', billing['required_controls'])
        self.assertTrue(billing['commercial_entity'])

    def test_m63_api_and_storage_boundaries_are_defined(self):
        api = get_architecture_boundary('api_boundary')
        storage = get_architecture_boundary('storage_boundary')
        self.assertEqual(api['scope'], 'versioned_contracts')
        self.assertIn('schemas', api['requirement'])
        self.assertEqual(storage['scope'], 'durable_persistence')
        self.assertIn('migrations', storage['next_action'])

    def test_m63_protection_and_operations_boundaries_are_defined(self):
        protection = get_architecture_boundary('security_boundary')
        operations = get_architecture_boundary('observability_boundary')
        self.assertIn('RBAC', protection['requirement'])
        self.assertIn('audit events', protection['next_action'])
        self.assertIn('run IDs', operations['requirement'])
        self.assertIn('health checks', operations['next_action'])

    def test_m63_summary_is_compact_and_safe(self):
        summary = summarize_commercial_architecture(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['entity_count'], 0)
        self.assertEqual(summary['boundary_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
