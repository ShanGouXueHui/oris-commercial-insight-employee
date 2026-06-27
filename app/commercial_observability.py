from __future__ import annotations

VERSION = '2026-06-27-module-67-commercial-observability'
FLAG_NAME = 'ORIS_COMMERCIAL_OBSERVABILITY_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

SIGNAL_ORDER = ('health', 'metrics', 'traces', 'logs', 'run_diagnostics', 'failure_taxonomy')

_SIGNAL_CATALOG = {
    'health': ('readiness and liveness status', ('service_state', 'dependency_state')),
    'metrics': ('tenant-scoped operational counters', ('request_count', 'latency_ms', 'failure_count')),
    'traces': ('request and run correlation', ('trace_id', 'run_id', 'tenant_id')),
    'logs': ('safe operator diagnostics', ('event_type', 'severity', 'redaction_state')),
    'run_diagnostics': ('execution troubleshooting record', ('run_id', 'status', 'duration_ms')),
    'failure_taxonomy': ('standard failure classification', ('category', 'retryable', 'operator_action')),
}


def observability_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_observability_signal(name):
    if name not in _SIGNAL_CATALOG:
        raise KeyError(f'unknown observability signal: {name}')
    purpose, required_fields = _SIGNAL_CATALOG[name]
    return {
        'name': name,
        'purpose': purpose,
        'required_fields': required_fields,
        'tenant_scoped': name in {'metrics', 'traces', 'logs', 'run_diagnostics'},
        'safe_to_log': name != 'logs' or 'redaction_state' in required_fields,
        'file_written': False,
    }


def build_observability_baseline(env=None):
    enabled = observability_enabled(env)
    baseline = {
        'allowed': enabled,
        'enabled': enabled,
        'enabled_by_default': False,
        'flag': FLAG_NAME,
        'version': VERSION,
        'file_written': False,
        'external_calls': False,
        'release_published': False,
        'default_behavior_changed': False,
    }
    if not enabled:
        baseline.update({'status': 'disabled', 'signal_count': 0, 'signals': [], 'signal_names': []})
        return baseline
    signals = [get_observability_signal(name) for name in SIGNAL_ORDER]
    baseline.update({
        'status': 'observability_baseline_defined',
        'observability_scope': 'local_read_only_commercial_observability_baseline',
        'signal_count': len(signals),
        'signal_names': list(SIGNAL_ORDER),
        'signals': signals,
        'run_id_required': True,
        'trace_id_required': True,
        'safe_logging_required': True,
        'operator_diagnostics_required': True,
        'commercial_next_step': 'convert signals into health, metrics, trace, and diagnostics contracts',
    })
    return baseline


def summarize_observability(env=None):
    baseline = build_observability_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'signal_count': baseline['signal_count'],
        'signal_names': baseline['signal_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
