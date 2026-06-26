def m50_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M50_ENABLED', '')).lower() == 'true'


def build_m50_card(summary, env=None):
    if not m50_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-50', 'file_written': False}
    status = str(summary.get('summary_status', 'review_summary'))
    card_state = 'ready_card' if status == 'ready_summary' else 'review_card'
    return {
        'allowed': True,
        'version': '2026-06-26-module-50',
        'card_state': card_state,
        'summary_status': status,
        'card_visible': True,
        'file_written': False,
    }


def summarize_m50(env=None):
    enabled = m50_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
