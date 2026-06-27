from __future__ import annotations

VERSION = '2026-06-27-module-71-commercialization-gates'
FLAG_NAME = 'ORIS_COMMERCIALIZATION_GATES_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

GATE_ORDER = (
    'product_readiness',
    'tenant_isolation',
    'api_contracts',
    'storage_migration',
    'security_rbac',
    'observability',
    'ota_loop_control',
    'commercial_stop_rule',
)

_GATE_STATUS = {
    'product_readiness': ('baseline_ready', 'modules 62-67 define core commercial baselines'),
    'tenant_isolation': ('baseline_ready', 'tenant scoped architecture and security are defined'),
    'api_contracts': ('baseline_ready', 'public v1 contract baseline exists'),
    'storage_migration': ('baseline_ready', 'storage ownership and migration readiness exist'),
    'security_rbac': ('baseline_ready', 'role and permission baseline exists'),
    'observability': ('baseline_ready', 'health, metrics, traces, logs, diagnostics exist'),
    'ota_loop_control': ('baseline_ready', 'GitHub instruction manifest and server polling exist'),
    'commercial_stop_rule': ('pending', 'requires all gates accepted plus operator approval'),
}


def gates_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_commercial_gate(name):
    if name not in _GATE_STATUS:
        raise KeyError(f'unknown commercial gate: {name}')
    status, rationale = _GATE_STATUS[name]
    return {'name': name, 'status': status, 'rationale': rationale, 'blocking': status != 'baseline_ready', 'file_written': False}


def build_commercialization_gates(env=None):
    enabled = gates_enabled(env)
    baseline = {'allowed': enabled, 'enabled': enabled, 'enabled_by_default': False, 'flag': FLAG_NAME, 'version': VERSION, 'file_written': False, 'external_calls': False, 'release_published': False, 'default_behavior_changed': False}
    if not enabled:
        baseline.update({'status': 'disabled', 'gate_count': 0, 'gate_names': [], 'gates': [], 'commercial_ready': False})
        return baseline
    gates = [get_commercial_gate(name) for name in GATE_ORDER]
    blockers = [gate['name'] for gate in gates if gate['blocking']]
    baseline.update({'status': 'commercialization_gates_defined', 'gate_scope': 'local_read_only_commercialization_target_gates', 'gate_count': len(gates), 'gate_names': list(GATE_ORDER), 'gates': gates, 'blocking_gate_count': len(blockers), 'blocking_gates': blockers, 'commercial_ready': False, 'operator_approval_required': True, 'commercial_next_step': 'convert pending stop rule into explicit release readiness review'})
    return baseline


def summarize_commercialization_gates(env=None):
    baseline = build_commercialization_gates(env=env)
    return {'enabled': baseline['enabled'], 'enabled_by_default': baseline['enabled_by_default'], 'status': baseline['status'], 'gate_count': baseline['gate_count'], 'blocking_gate_count': baseline.get('blocking_gate_count', 0), 'commercial_ready': baseline['commercial_ready'], 'file_written': baseline['file_written'], 'external_calls': baseline['external_calls'], 'release_published': baseline['release_published'], 'default_behavior_changed': baseline['default_behavior_changed']}
