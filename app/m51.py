def m51_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M51_ENABLED', '')).lower() == 'true'


def build_m51_summary(card, env=None):
    if not m51_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-51', 'file_written': False}
    state = str(card.get('card_state', 'review_card'))
    final_state = 'ready' if state == 'ready_card' else 'review'
    return {
        'allowed': True,
        'version': '2026-06-26-module-51',
        'final_state': final_state,
        'card_state': state,
        'summary_visible': True,
        'file_written': False,
    }


def summarize_m51(env=None):
    enabled = m51_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
