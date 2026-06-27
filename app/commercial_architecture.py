from __future__ import annotations

VERSION = '2026-06-27-module-63-commercial-architecture'
FLAG_NAME = 'ORIS_COMMERCIAL_ARCHITECTURE_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

ENTITY_ORDER = (
    'tenant',
    'workspace',
    'project',
    'insight',
    'evidence',
    'execution',
    'audit',
    'billing_readiness',
)

BOUNDARY_ORDER = (
    'api_boundary',
    'storage_boundary',
    'security_boundary',
    'observability_boundary',
)

_ENTITY_CATALOG = {
    'tenant': {
        'owner_key': 'tenant_id',
        'purpose': 'top-level commercial customer isolation unit',
        'required_controls': ('isolation', 'rbac_scope', 'retention_policy'),
    },
    'workspace': {
        'owner_key': 'workspace_id',
        'purpose': 'tenant-scoped collaboration and configuration unit',
        'required_controls': ('tenant_parent', 'member_policy', 'configuration_scope'),
    },
    'project': {
        'owner_key': 'project_id',
        'purpose': 'workspace-scoped commercial insight work unit',
        'required_controls': ('workspace_parent', 'lifecycle_state', 'access_policy'),
    },
    'insight': {
        'owner_key': 'insight_id',
        'purpose': 'reviewable business insight artifact',
        'required_controls': ('project_parent', 'review_state', 'version_policy'),
    },
    'evidence': {
        'owner_key': 'evidence_id',
        'purpose': 'traceable source and validation record',
        'required_controls': ('insight_parent', 'provenance', 'immutability_hint'),
    },
    'execution': {
        'owner_key': 'run_id',
        'purpose': 'traceable generation or validation run',
        'required_controls': ('tenant_parent', 'status', 'diagnostics'),
    },
    'audit': {
        'owner_key': 'audit_event_id',
        'purpose': 'security and compliance event trail',
        'required_controls': ('actor', 'action', 'target', 'timestamp'),
    },
    'billing_readiness': {
        'owner_key': 'meter_event_id',
        'purpose': 'future commercial metering without activating billing behavior',
        'required_controls': ('tenant_parent', 'usage_unit', 'billing_disabled_by_default'),
    },
}

_BOUNDARY_CATALOG = {
    'api_boundary': {
        'scope': 'versioned_contracts',
        'requirement': 'separate public API schemas from internal helper dictionaries',
        'next_action': 'draft v1 tenant, workspace, project, insight, evidence, execution, and audit contracts',
    },
    'storage_boundary': {
        'scope': 'durable_persistence',
        'requirement': 'separate local evidence paths from future tenant-owned persistence',
        'next_action': 'map entity ownership to tables, migrations, retention, and backup policies',
    },
    'security_boundary': {
        'scope': 'tenant_protection',
        'requirement': 'require tenant isolation, RBAC, secret hygiene, safe logging, and audit trails',
        'next_action': 'define roles, permissions, audit events, secret policy, and data retention gates',
    },
    'observability_boundary': {
        'scope': 'operator_diagnostics',
        'requirement': 'require health, metrics, run IDs, trace IDs, and failure taxonomy',
        'next_action': 'standardize tenant-scoped run diagnostics and operator-facing health checks',
    },
}


def commercial_architecture_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_architecture_entity(name):
    if name not in _ENTITY_CATALOG:
        raise KeyError(f'unknown commercial architecture entity: {name}')
    item = dict(_ENTITY_CATALOG[name])
    item['name'] = name
    item['commercial_entity'] = True
    item['file_written'] = False
    return item


def get_architecture_boundary(name):
    if name not in _BOUNDARY_CATALOG:
        raise KeyError(f'unknown commercial architecture boundary: {name}')
    item = dict(_BOUNDARY_CATALOG[name])
    item['name'] = name
    item['commercial_boundary'] = True
    item['file_written'] = False
    return item


def build_commercial_architecture_baseline(env=None):
    enabled = commercial_architecture_enabled(env)
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
        baseline.update({
            'status': 'disabled',
            'entity_count': 0,
            'boundary_count': 0,
            'entity_names': [],
            'boundary_names': [],
            'entities': [],
            'boundaries': [],
        })
        return baseline

    entities = [get_architecture_entity(name) for name in ENTITY_ORDER]
    boundaries = [get_architecture_boundary(name) for name in BOUNDARY_ORDER]
    baseline.update({
        'status': 'architecture_baseline_defined',
        'architecture_scope': 'local_read_only_tenant_commercial_architecture_baseline',
        'entity_count': len(entities),
        'boundary_count': len(boundaries),
        'entity_names': list(ENTITY_ORDER),
        'boundary_names': list(BOUNDARY_ORDER),
        'entities': entities,
        'boundaries': boundaries,
        'commercial_next_step': 'convert architecture entities and boundaries into versioned schemas, migrations, RBAC, and operator diagnostics',
    })
    return baseline


def summarize_commercial_architecture(env=None):
    baseline = build_commercial_architecture_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'entity_count': baseline['entity_count'],
        'boundary_count': baseline['boundary_count'],
        'entity_names': baseline['entity_names'],
        'boundary_names': baseline['boundary_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
