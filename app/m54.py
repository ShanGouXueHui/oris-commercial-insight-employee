def m54_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M54_ENABLED', '')).lower() == 'true'


def build_m54_badge(rollup, env=None):
    if not m54_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-54', 'file_written': False}
    state = str(rollup.get('rollup_state', 'review_rollup'))
    badge = 'ready_badge' if state == 'ready_rollup' else 'review_badge'
    return {
        'allowed': True,
        'version': '2026-06-26-module-54',
        'badge_state': badge,
        'rollup_state': state,
        'badge_visible': True,
        'file_written': False,
    }


def summarize_m54(env=None):
    enabled = m54_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
