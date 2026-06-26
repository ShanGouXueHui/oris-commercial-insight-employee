def m48_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M48_ENABLED', '')).lower() == 'true'


def build_m48_strip(badge, env=None):
    if not m48_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-48', 'file_written': False}
    label = str(badge.get('badge_label', 'review'))
    state = 'visible_ready' if label == 'ready' else 'visible_review'
    return {
        'allowed': True,
        'version': '2026-06-26-module-48',
        'strip_state': state,
        'badge_label': label,
        'strip_visible': True,
        'file_written': False,
    }


def summarize_m48(env=None):
    enabled = m48_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
