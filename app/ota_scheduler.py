from __future__ import annotations

VERSION = '2026-06-27-module-69-ota-scheduler'
FLAG_NAME = 'ORIS_OTA_SCHEDULER_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

SCHEDULER_ORDER = (
    'ten_minute_cadence',
    'server_local_schedule',
    'manual_install_only',
    'unified_entrypoint_target',
    'ota_log_append',
    'safe_reinstall',
    'least_privilege_mode',
)

_SCHEDULER = {
    'ten_minute_cadence': ('every_10_minutes', 'run the OTA loop every ten minutes'),
    'server_local_schedule': ('user_schedule', 'use server local scheduler'),
    'manual_install_only': ('scripts/install_unified_ota_loop.sh', 'requires explicit server-side install'),
    'unified_entrypoint_target': ('unified-OTA-entry.sh', 'call only the unified OTA entrypoint'),
    'ota_log_append': ('reports/ota/unified_ota_loop.log', 'append scheduler output to OTA logs'),
    'safe_reinstall': ('ORIS_UNIFIED_OTA_LOOP marker', 'replace only the managed schedule line'),
    'least_privilege_mode': ('user_scope', 'avoid privileged background installation'),
}


def scheduler_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_scheduler_control(name):
    if name not in _SCHEDULER:
        raise KeyError(f'unknown ota scheduler control: {name}')
    implementation, purpose = _SCHEDULER[name]
    return {
        'name': name,
        'implementation': implementation,
        'purpose': purpose,
        'safe_default': True,
        'file_written': False,
    }


def build_scheduler_baseline(env=None):
    enabled = scheduler_enabled(env)
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
    controls = [get_scheduler_control(name) for name in SCHEDULER_ORDER]
    baseline.update({
        'status': 'ota_scheduler_baseline_defined',
        'scheduler_scope': 'manual_server_schedule_for_unified_ota_entry',
        'control_count': len(controls),
        'control_names': list(SCHEDULER_ORDER),
        'controls': controls,
        'cadence_minutes': 10,
        'manual_install_required': True,
        'commercial_next_step': 'install the schedule entry once on the server and let GitHub evidence drive further OTA updates',
    })
    return baseline


def summarize_scheduler(env=None):
    baseline = build_scheduler_baseline(env=env)
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
