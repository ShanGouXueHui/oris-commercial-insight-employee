def m49_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M49_ENABLED', '')).lower() == 'true'


def build_m49_summary(strip, env=None):
    if not m49_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-49', 'file_written': False}
    state = str(strip.get('strip_state', 'visible_review'))
    status = 'ready_summary' if state == 'visible_ready' else 'review_summary'
    return {
        'allowed': True,
        'version': '2026-06-26-module-49',
        'summary_status': status,
        'strip_state': state,
        'summary_visible': True,
        'file_written': False,
    }


def summarize_m49(env=None):
    enabled = m49_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
