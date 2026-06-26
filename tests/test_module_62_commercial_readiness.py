import unittest

from app.commercial_readiness import (
    DIMENSION_ORDER,
    build_commercial_readiness_baseline,
    get_readiness_dimension,
    summarize_commercial_readiness,
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


if __name__ == '__main__':
    unittest.main()
