from __future__ import annotations

VERSION = '2026-06-27-module-64-commercial-api-contracts'
FLAG_NAME = 'ORIS_COMMERCIAL_API_CONTRACTS_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

CONTRACT_ORDER = (
    'tenant_v1',
    'workspace_v1',
    'project_v1',
    'insight_v1',
    'evidence_v1',
    'execution_v1',
    'audit_v1',
)

_CONTRACTS = {
    'tenant_v1': ('tenant', ('tenant_id', 'name', 'status'), ('create', 'read', 'update')),
    'workspace_v1': ('workspace', ('tenant_id', 'workspace_id', 'name', 'status'), ('create', 'read', 'update')),
    'project_v1': ('project', ('tenant_id', 'workspace_id', 'project_id', 'status'), ('create', 'read', 'update')),
    'insight_v1': ('insight', ('tenant_id', 'project_id', 'insight_id', 'review_state'), ('create', 'read', 'update')),
    'evidence_v1': ('evidence', ('tenant_id', 'insight_id', 'evidence_id', 'source_ref'), ('create', 'read')),
    'execution_v1': ('execution', ('tenant_id', 'run_id', 'status', 'started_at'), ('create', 'read')),
    'audit_v1': ('audit', ('tenant_id', 'audit_event_id', 'actor', 'action'), ('read',)),
}


def api_contracts_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_api_contract(name):
    if name not in _CONTRACTS:
        raise KeyError(f'unknown commercial api contract: {name}')
    resource, required_fields, operations = _CONTRACTS[name]
    return {
        'name': name,
        'version': 'v1',
        'resource': resource,
        'required_fields': required_fields,
        'operations': operations,
        'tenant_scoped': True,
        'public_contract': True,
        'file_written': False,
    }


def build_api_contract_baseline(env=None):
    enabled = api_contracts_enabled(env)
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
        baseline.update({'status': 'disabled', 'contract_count': 0, 'contract_names': [], 'contracts': []})
        return baseline
    contracts = [get_api_contract(name) for name in CONTRACT_ORDER]
    baseline.update({
        'status': 'api_contract_baseline_defined',
        'api_scope': 'local_read_only_commercial_api_contract_baseline',
        'contract_count': len(contracts),
        'contract_names': list(CONTRACT_ORDER),
        'contracts': contracts,
        'commercial_next_step': 'convert contract dictionaries into request and response schemas',
    })
    return baseline


def summarize_api_contracts(env=None):
    baseline = build_api_contract_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'contract_count': baseline['contract_count'],
        'contract_names': baseline['contract_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
