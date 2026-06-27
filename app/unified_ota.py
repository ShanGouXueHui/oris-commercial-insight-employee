from __future__ import annotations

VERSION = '2026-06-27-module-68-unified-ota'
FLAG_NAME = 'ORIS_UNIFIED_OTA_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

CONTROL_ORDER = (
    'single_entrypoint',
    'repo_fast_forward_only',
    'lock_guard',
    'allowlisted_runner',
    'timestamped_logs',
    'evidence_autocommit',
    'no_release_publish',
)

_CONTROLS = {
    'single_entrypoint': ('unified-OTA-entry.sh', 'one stable server-side command entry'),
    'repo_fast_forward_only': ('git pull --ff-only origin main', 'avoid merge drift on the server'),
    'lock_guard': ('/tmp/oris-unified-ota.lock', 'avoid overlapping loop runs'),
    'allowlisted_runner': ('scripts/r68.py', 'execute only the module runner declared by the entrypoint'),
    'timestamped_logs': ('reports/ota', 'write numbered OTA execution logs'),
    'evidence_autocommit': ('git commit and push evidence paths', 'return execution result to GitHub'),
    'no_release_publish': ('release disabled', 'do not publish artifacts or external services'),
}


def unified_ota_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_ota_control(name):
    if name not in _CONTROLS:
        raise KeyError(f'unknown unified ota control: {name}')
    implementation, purpose = _CONTROLS[name]
    return {
        'name': name,
        'implementation': implementation,
        'purpose': purpose,
        'safe_default': True,
        'file_written': False,
    }


def build_unified_ota_baseline(env=None):
    enabled = unified_ota_enabled(env)
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
        baseline.update({'status': 'disabled', 'control_count': 0, 'control_names': [], 'controls': []})
        return baseline
    controls = [get_ota_control(name) for name in CONTROL_ORDER]
    baseline.update({
        'status': 'unified_ota_baseline_defined',
        'ota_scope': 'safe_server_side_unified_ota_entry_baseline',
        'control_count': len(controls),
        'control_names': list(CONTROL_ORDER),
        'controls': controls,
        'background_task_ready': True,
        'server_manual_install_required': True,
        'commercial_next_step': 'install a server scheduler to call the unified entrypoint periodically',
    })
    return baseline


def summarize_unified_ota(env=None):
    baseline = build_unified_ota_baseline(env=env)
    return {
        'enabled': baseline['enabled'],
        'enabled_by_default': baseline['enabled_by_default'],
        'status': baseline['status'],
        'control_count': baseline['control_count'],
        'control_names': baseline['control_names'],
        'file_written': baseline['file_written'],
        'external_calls': baseline['external_calls'],
        'release_published': baseline['release_published'],
        'default_behavior_changed': baseline['default_behavior_changed'],
    }
