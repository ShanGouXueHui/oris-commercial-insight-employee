VERSION = 'm74'
FLAG_NAME = 'ORIS_M74_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}
CHECKS = ('owner_note', 'scope_note', 'evidence_note', 'test_note', 'go_note')


def m74_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def build_m74(env=None):
    enabled = m74_enabled(env)
    result = {'allowed': enabled, 'enabled': enabled, 'enabled_by_default': False, 'file_written': False, 'external_calls': False, 'release_published': False, 'default_behavior_changed': False}
    if not enabled:
        result.update({'status': 'disabled', 'check_count': 0, 'checks': [], 'ready': False})
        return result
    result.update({'status': 'm74_defined', 'check_count': len(CHECKS), 'checks': list(CHECKS), 'ready': False, 'go_note_required': True})
    return result


def summarize_m74(env=None):
    result = build_m74(env=env)
    return {'enabled': result['enabled'], 'status': result['status'], 'check_count': result['check_count'], 'ready': result['ready'], 'external_calls': result['external_calls']}
