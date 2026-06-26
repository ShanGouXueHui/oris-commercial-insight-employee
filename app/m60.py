def m60_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M60_ENABLED', '')).lower() == 'true'


def build_m60_capsule(rollup, env=None):
    if not m60_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-60', 'file_written': False}
    state = str(rollup.get('rollup_state', 'review_rollup'))
    capsule = 'ready_capsule' if state == 'ready_rollup' else 'review_capsule'
    return {
        'allowed': True,
        'version': '2026-06-26-module-60',
        'capsule_state': capsule,
        'rollup_state': state,
        'capsule_visible': True,
        'file_written': False,
    }


def summarize_m60(env=None):
    enabled = m60_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
