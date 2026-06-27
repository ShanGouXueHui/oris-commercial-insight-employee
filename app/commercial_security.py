from __future__ import annotations

VERSION = '2026-06-27-module-66-commercial-security'
FLAG_NAME = 'ORIS_COMMERCIAL_SECURITY_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

ROLE_ORDER = ('owner', 'admin', 'analyst', 'viewer', 'auditor')
PERMISSION_ORDER = (
    'tenant.manage',
    'workspace.manage',
    'project.manage',
    'insight.write',
    'insight.read',
    'evidence.read',
    'execution.read',
    'audit.read',
)

_ROLE_PERMISSIONS = {
    'owner': PERMISSION_ORDER,
    'admin': ('workspace.manage', 'project.manage', 'insight.write', 'insight.read', 'evidence.read', 'execution.read'),
    'analyst': ('project.manage', 'insight.write', 'insight.read', 'evidence.read', 'execution.read'),
    'viewer': ('insight.read', 'evidence.read', 'execution.read'),
    'auditor': ('audit.read', 'insight.read', 'evidence.read', 'execution.read'),
}


def security_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_role_policy(role):
    if role not in _ROLE_PERMISSIONS:
        raise KeyError(f'unknown commercial role: {role}')
    return {
        'role': role,
        'permissions': tuple(_ROLE_PERMISSIONS[role]),
        'tenant_scoped': True,
        'least_privilege': role != 'owner',
        'audit_required': True,
        'file_written': False,
    }


def build_security_baseline(env=None):
    enabled = security_enabled(env)
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
        baseline.update({'status': 'disabled', 'role_count': 0, 'permission_count': 0, 'roles': [], 'permissions': []})
        return baseline
    policies = [get_role_policy(role) for role in ROLE_ORDER]
    baseline.update({
        'status': 'security_rbac_baseline_defined',
        'security_scope': 'local_read_only_commercial_security_rbac_baseline',
        'role_count': len(policies),
        'permission_count': len(PERMISSION_ORDER),
        'roles': list(ROLE_ORDER),
        'permissions': list(PERMISSION_ORDER),
        'policies': policies,
        'tenant_isolation_required': True,
        'audit_required': True,
        'safe_logging_required': True,
        'secret_boundary_required': True,
        'commercial_next_step': 'convert role policies into middleware checks and audit events',
    })
    return baseline


def summarize_security(env=None):
    baseline = build_security_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'role_count': baseline['role_count'],
        'permission_count': baseline['permission_count'],
        'roles': baseline['roles'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
