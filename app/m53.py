def m53_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M53_ENABLED', '')).lower() == 'true'


def build_m53_rollup(marker, env=None):
    if not m53_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-53', 'file_written': False}
    state = str(marker.get('marker_state', 'review_marker'))
    rollup = 'ready_rollup' if state == 'ready_marker' else 'review_rollup'
    return {
        'allowed': True,
        'version': '2026-06-26-module-53',
        'rollup_state': rollup,
        'marker_state': state,
        'rollup_visible': True,
        'file_written': False,
    }


def summarize_m53(env=None):
    enabled = m53_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
