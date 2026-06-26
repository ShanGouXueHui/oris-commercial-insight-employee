def m47_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M47_ENABLED', '')).lower() == 'true'


def build_m47_badge(digest, env=None):
    if not m47_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-47', 'file_written': False}
    state = str(digest.get('digest_state', 'amber'))
    label = 'ready' if state == 'green' else 'review'
    return {
        'allowed': True,
        'version': '2026-06-26-module-47',
        'badge_label': label,
        'digest_state': state,
        'badge_visible': True,
        'file_written': False,
    }


def summarize_m47(env=None):
    enabled = m47_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
