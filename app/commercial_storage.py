from __future__ import annotations

VERSION = '2026-06-27-module-65-commercial-storage'
FLAG_NAME = 'ORIS_COMMERCIAL_STORAGE_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

STORE_ORDER = (
    'tenant_store',
    'workspace_store',
    'project_store',
    'insight_store',
    'evidence_store',
    'execution_store',
    'audit_store',
    'meter_store',
)

_STORAGE = {
    'tenant_store': ('tenant', 'tenant_id', 'durable', ('retention_policy', 'isolation_key')),
    'workspace_store': ('workspace', 'workspace_id', 'durable', ('tenant_parent', 'config_scope')),
    'project_store': ('project', 'project_id', 'durable', ('workspace_parent', 'lifecycle_state')),
    'insight_store': ('insight', 'insight_id', 'durable', ('project_parent', 'version_state')),
    'evidence_store': ('evidence', 'evidence_id', 'durable', ('provenance', 'immutability_hint')),
    'execution_store': ('execution', 'run_id', 'diagnostic', ('status', 'failure_reason')),
    'audit_store': ('audit', 'audit_event_id', 'append_only', ('actor', 'action', 'timestamp')),
    'meter_store': ('metering', 'meter_event_id', 'append_only', ('tenant_parent', 'billing_disabled_by_default')),
}


def storage_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_storage_boundary(name):
    if name not in _STORAGE:
        raise KeyError(f'unknown commercial storage boundary: {name}')
    resource, key, mode, controls = _STORAGE[name]
    return {
        'name': name,
        'resource': resource,
        'primary_key': key,
        'persistence_mode': mode,
        'required_controls': controls,
        'tenant_owned': True,
        'migration_required': True,
        'file_written': False,
    }


def build_storage_boundary_baseline(env=None):
    enabled = storage_enabled(env)
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
        baseline.update({'status': 'disabled', 'store_count': 0, 'store_names': [], 'stores': []})
        return baseline
    stores = [get_storage_boundary(name) for name in STORE_ORDER]
    baseline.update({
        'status': 'storage_boundary_baseline_defined',
        'storage_scope': 'local_read_only_commercial_storage_boundary_baseline',
        'store_count': len(stores),
        'store_names': list(STORE_ORDER),
        'stores': stores,
        'local_evidence_separated': True,
        'commercial_next_step': 'convert storage boundaries into migrations, retention policy, and backup plan',
    })
    return baseline


def summarize_storage_boundaries(env=None):
    baseline = build_storage_boundary_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'store_count': baseline['store_count'],
        'store_names': baseline['store_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
