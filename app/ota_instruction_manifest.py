from __future__ import annotations

VERSION = '2026-06-27-module-70-ota-instruction-manifest'
FLAG_NAME = 'ORIS_OTA_INSTRUCTION_MANIFEST_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

CONTROL_ORDER = (
    'github_manifest_source',
    'single_entrypoint_target',
    'allowlisted_writer',
    'expected_test_count',
    'timestamped_evidence',
    'advance_on_pass',
    'commercial_stop_condition',
)

_CONTROLS = {
    'github_manifest_source': ('ops/ota/next_instruction.json', 'GitHub-hosted OTA instruction source'),
    'single_entrypoint_target': ('unified-OTA-entry.sh', 'server executes one stable entrypoint'),
    'allowlisted_writer': ('scripts/w70.py', 'current module evidence writer'),
    'expected_test_count': ('360', 'full suite count expected by current instruction'),
    'timestamped_evidence': ('reports/ota', 'each server loop writes a timestamped OTA log'),
    'advance_on_pass': ('update manifest and entrypoint', 'next instruction is published through GitHub'),
    'commercial_stop_condition': ('commercial_ready_true', 'stop loop advancement only when accepted commercial target is met'),
}

REQUIRED_MANIFEST_FIELDS = (
    'active_module',
    'entrypoint',
    'writer',
    'expected_unit_test_count',
    'allowed_paths',
    'stop_condition',
)


def manifest_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_manifest_control(name):
    if name not in _CONTROLS:
        raise KeyError(f'unknown ota manifest control: {name}')
    implementation, purpose = _CONTROLS[name]
    return {
        'name': name,
        'implementation': implementation,
        'purpose': purpose,
        'safe_default': True,
        'file_written': False,
    }


def validate_instruction_manifest(manifest):
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
    allowed_paths = tuple(manifest.get('allowed_paths', ()))
    return {
        'valid': not missing and manifest.get('entrypoint') == 'unified-OTA-entry.sh' and manifest.get('writer', '').startswith('scripts/w'),
        'missing_fields': missing,
        'entrypoint_allowed': manifest.get('entrypoint') == 'unified-OTA-entry.sh',
        'writer_allowlisted': manifest.get('writer', '').startswith('scripts/w'),
        'allowed_paths': allowed_paths,
        'file_written': False,
    }


def build_manifest_baseline(env=None):
    enabled = manifest_enabled(env)
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
    controls = [get_manifest_control(name) for name in CONTROL_ORDER]
    baseline.update({
        'status': 'ota_instruction_manifest_baseline_defined',
        'manifest_scope': 'github_hosted_safe_ota_instruction_source',
        'control_count': len(controls),
        'control_names': list(CONTROL_ORDER),
        'controls': controls,
        'manifest_path': 'ops/ota/next_instruction.json',
        'active_module': 70,
        'expected_unit_test_count': 360,
        'server_polling_supported': True,
        'commercial_next_step': 'advance the manifest and unified entrypoint after each accepted evidence result',
    })
    return baseline


def summarize_manifest(env=None):
    baseline = build_manifest_baseline(env=env)
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
