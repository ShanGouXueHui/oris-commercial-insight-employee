def m61_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M61_ENABLED', '')).lower() == 'true'


def build_m61_summary(capsule, env=None):
    if not m61_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-61', 'file_written': False}
    state = str(capsule.get('capsule_state', 'review_capsule'))
    summary = 'ready_summary' if state == 'ready_capsule' else 'review_summary'
    return {
        'allowed': True,
        'version': '2026-06-26-module-61',
        'summary_state': summary,
        'capsule_state': state,
        'summary_visible': True,
        'file_written': False,
    }


def summarize_m61(env=None):
    enabled = m61_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
