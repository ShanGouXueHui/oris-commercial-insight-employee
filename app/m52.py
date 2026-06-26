def m52_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M52_ENABLED', '')).lower() == 'true'


def build_m52_marker(summary, env=None):
    if not m52_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-52', 'file_written': False}
    state = str(summary.get('final_state', 'review'))
    marker = 'ready_marker' if state == 'ready' else 'review_marker'
    return {
        'allowed': True,
        'version': '2026-06-26-module-52',
        'marker_state': marker,
        'final_state': state,
        'marker_visible': True,
        'file_written': False,
    }


def summarize_m52(env=None):
    enabled = m52_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
