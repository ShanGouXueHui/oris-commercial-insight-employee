def m55_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M55_ENABLED', '')).lower() == 'true'


def build_m55_summary(badge, env=None):
    if not m55_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-55', 'file_written': False}
    state = str(badge.get('badge_state', 'review_badge'))
    summary = 'ready_summary' if state == 'ready_badge' else 'review_summary'
    return {
        'allowed': True,
        'version': '2026-06-26-module-55',
        'summary_state': summary,
        'badge_state': state,
        'summary_visible': True,
        'file_written': False,
    }


def summarize_m55(env=None):
    enabled = m55_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
