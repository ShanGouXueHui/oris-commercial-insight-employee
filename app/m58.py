def m58_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M58_ENABLED', '')).lower() == 'true'


def build_m58_summary(marker, env=None):
    if not m58_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-58', 'file_written': False}
    state = str(marker.get('marker_state', 'review_marker'))
    summary = 'ready_summary' if state == 'ready_marker' else 'review_summary'
    return {
        'allowed': True,
        'version': '2026-06-26-module-58',
        'summary_state': summary,
        'marker_state': state,
        'summary_visible': True,
        'file_written': False,
    }


def summarize_m58(env=None):
    enabled = m58_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
