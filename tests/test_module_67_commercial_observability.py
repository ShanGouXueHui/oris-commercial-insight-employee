import unittest

from app.commercial_observability import (
    SIGNAL_ORDER,
    build_observability_baseline,
    get_observability_signal,
    summarize_observability,
)


class Module67CommercialObservabilityTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_observability_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['signals'], [])

    def test_enabled_returns_signals_in_order(self):
        result = build_observability_baseline(env={'ORIS_COMMERCIAL_OBSERVABILITY_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'observability_baseline_defined')
        self.assertEqual(result['signal_count'], 6)
        self.assertEqual(result['signal_names'], list(SIGNAL_ORDER))

    def test_health_metrics_and_traces_have_required_fields(self):
        health = get_observability_signal('health')
        metrics = get_observability_signal('metrics')
        traces = get_observability_signal('traces')
        self.assertIn('service_state', health['required_fields'])
        self.assertIn('latency_ms', metrics['required_fields'])
        self.assertIn('trace_id', traces['required_fields'])
        self.assertIn('run_id', traces['required_fields'])

    def test_logs_and_diagnostics_are_safe_and_actionable(self):
        logs = get_observability_signal('logs')
        diagnostics = get_observability_signal('run_diagnostics')
        taxonomy = get_observability_signal('failure_taxonomy')
        self.assertTrue(logs['safe_to_log'])
        self.assertIn('redaction_state', logs['required_fields'])
        self.assertIn('duration_ms', diagnostics['required_fields'])
        self.assertIn('operator_action', taxonomy['required_fields'])

    def test_enabled_baseline_requires_operator_controls(self):
        result = build_observability_baseline(env={'ORIS_COMMERCIAL_OBSERVABILITY_ENABLED': '1'})
        self.assertTrue(result['run_id_required'])
        self.assertTrue(result['trace_id_required'])
        self.assertTrue(result['safe_logging_required'])
        self.assertTrue(result['operator_diagnostics_required'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_observability(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['signal_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
