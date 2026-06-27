import unittest

from app.commercialization_gates import (
    GATE_ORDER,
    build_commercialization_gates,
    get_commercial_gate,
    summarize_commercialization_gates,
)


class Module71CommercializationGatesTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_commercialization_gates(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertFalse(result['commercial_ready'])

    def test_enabled_returns_gates_in_order(self):
        result = build_commercialization_gates(env={'ORIS_COMMERCIALIZATION_GATES_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'commercialization_gates_defined')
        self.assertEqual(result['gate_count'], 8)
        self.assertEqual(result['gate_names'], list(GATE_ORDER))

    def test_core_gates_are_baseline_ready(self):
        for name in ('product_readiness', 'tenant_isolation', 'api_contracts', 'storage_migration', 'security_rbac', 'observability', 'ota_loop_control'):
            gate = get_commercial_gate(name)
            self.assertEqual(gate['status'], 'baseline_ready')
            self.assertFalse(gate['blocking'])

    def test_commercial_stop_rule_remains_blocking(self):
        gate = get_commercial_gate('commercial_stop_rule')
        self.assertEqual(gate['status'], 'pending')
        self.assertTrue(gate['blocking'])
        result = build_commercialization_gates(env={'ORIS_COMMERCIALIZATION_GATES_ENABLED': '1'})
        self.assertIn('commercial_stop_rule', result['blocking_gates'])
        self.assertFalse(result['commercial_ready'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_commercialization_gates(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['gate_count'], 0)
        self.assertFalse(summary['commercial_ready'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])


if __name__ == '__main__':
    unittest.main()
