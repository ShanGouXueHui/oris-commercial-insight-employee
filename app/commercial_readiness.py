from __future__ import annotations

VERSION = '2026-06-26-module-62-commercial-readiness'
FLAG_NAME = 'ORIS_COMMERCIAL_READINESS_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

DIMENSION_ORDER = (
    'tests',
    'docs',
    'safety',
    'configuration',
    'storage',
    'api',
    'security',
    'observability',
)

_DIMENSION_CATALOG = {
    'tests': {
        'title': 'Full-suite and module evidence readiness',
        'layer': 'validation',
        'tenant_relevance': 'tenant-safe release gates need repeatable evidence before acceptance',
        'baseline_requirement': 'record full-suite status, module evidence, exit code, and expected test count',
        'next_action': 'promote evidence checks into the commercial release gate',
    },
    'docs': {
        'title': 'Commercial operator documentation readiness',
        'layer': 'operator_experience',
        'tenant_relevance': 'tenant onboarding and support need stable runbooks and status docs',
        'baseline_requirement': 'keep rebuild notes, handoff, accepted status, and operator-facing guidance aligned',
        'next_action': 'add tenant onboarding, API, security, and operations runbooks',
    },
    'safety': {
        'title': 'Safe-by-default execution readiness',
        'layer': 'runtime_safety',
        'tenant_relevance': 'commercial tenants must not be affected by disabled experimental helpers',
        'baseline_requirement': 'disabled by default, no publish, no external call, no default behavior change',
        'next_action': 'turn safety invariants into release-blocking checks',
    },
    'configuration': {
        'title': 'Configuration separation readiness',
        'layer': 'configuration',
        'tenant_relevance': 'tenant and edition behavior must be controlled explicitly by configuration',
        'baseline_requirement': 'isolate module activation behind an opt-in environment flag',
        'next_action': 'define commercial, tenant, workspace, and operator configuration namespaces',
    },
    'storage': {
        'title': 'Storage and persistence readiness',
        'layer': 'data',
        'tenant_relevance': 'tenant artifacts need durable ownership, retention, and migration paths',
        'baseline_requirement': 'identify local-only paths before database-backed persistence is introduced',
        'next_action': 'design tenant/workspace/project/evidence storage boundaries and migrations',
    },
    'api': {
        'title': 'Versioned API boundary readiness',
        'layer': 'interface',
        'tenant_relevance': 'commercial integrations need stable versioned contracts',
        'baseline_requirement': 'separate internal helper outputs from future public API schemas',
        'next_action': 'draft v1 tenant, insight, execution, evidence, and audit API contracts',
    },
    'security': {
        'title': 'Tenant security readiness',
        'layer': 'security',
        'tenant_relevance': 'tenant isolation, RBAC, secrets, and auditability are commercial blockers',
        'baseline_requirement': 'treat tenant isolation, RBAC, secret handling, logging, and retention as gates',
        'next_action': 'define RBAC roles, audit events, secret policy, and retention policy',
    },
    'observability': {
        'title': 'Operational observability readiness',
        'layer': 'operations',
        'tenant_relevance': 'operators need traceable runs, diagnostics, and health signals per tenant',
        'baseline_requirement': 'capture run identifiers, health, metrics, failure diagnostics, and evidence pointers',
        'next_action': 'define health checks, metrics, run IDs, trace IDs, and failure taxonomy',
    },
}


def commercial_readiness_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_readiness_dimension(name):
    if name not in _DIMENSION_CATALOG:
        raise KeyError(f'unknown commercial readiness dimension: {name}')
    item = dict(_DIMENSION_CATALOG[name])
    item['name'] = name
    item['commercial_readiness_gate'] = True
    return item


def build_commercial_readiness_baseline(env=None):
    enabled = commercial_readiness_enabled(env)
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
            'dimension_count': 0,
            'dimension_names': [],
            'dimensions': [],
        })
        return baseline

    dimensions = [get_readiness_dimension(name) for name in DIMENSION_ORDER]
    baseline.update({
        'status': 'baseline_defined',
        'readiness_scope': 'local_read_only_commercial_baseline',
        'dimension_count': len(dimensions),
        'dimension_names': list(DIMENSION_ORDER),
        'dimensions': dimensions,
        'commercial_next_step': 'convert readiness dimensions into tenant, API, storage, security, and operations work items',
    })
    return baseline


def summarize_commercial_readiness(env=None):
    baseline = build_commercial_readiness_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'dimension_count': baseline['dimension_count'],
        'dimension_names': baseline['dimension_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
