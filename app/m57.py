def m57_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M57_ENABLED', '')).lower() == 'true'


def build_m57_marker(capsule, env=None):
    if not m57_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-57', 'file_written': False}
    state = str(capsule.get('capsule_state', 'review_capsule'))
    marker = 'ready_marker' if state == 'ready_capsule' else 'review_marker'
    return {
        'allowed': True,
        'version': '2026-06-26-module-57',
        'marker_state': marker,
        'capsule_state': state,
        'marker_visible': True,
        'file_written': False,
    }


def summarize_m57(env=None):
    enabled = m57_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
