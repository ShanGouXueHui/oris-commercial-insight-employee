def m59_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M59_ENABLED', '')).lower() == 'true'


def build_m59_rollup(summary, env=None):
    if not m59_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-59', 'file_written': False}
    state = str(summary.get('summary_state', 'review_summary'))
    rollup = 'ready_rollup' if state == 'ready_summary' else 'review_rollup'
    return {
        'allowed': True,
        'version': '2026-06-26-module-59',
        'rollup_state': rollup,
        'summary_state': state,
        'rollup_visible': True,
        'file_written': False,
    }


def summarize_m59(env=None):
    enabled = m59_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
