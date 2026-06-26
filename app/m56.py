def m56_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M56_ENABLED', '')).lower() == 'true'


def build_m56_capsule(summary, env=None):
    if not m56_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-56', 'file_written': False}
    state = str(summary.get('summary_state', 'review_summary'))
    capsule = 'ready_capsule' if state == 'ready_summary' else 'review_capsule'
    return {
        'allowed': True,
        'version': '2026-06-26-module-56',
        'capsule_state': capsule,
        'summary_state': state,
        'capsule_visible': True,
        'file_written': False,
    }


def summarize_m56(env=None):
    enabled = m56_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
