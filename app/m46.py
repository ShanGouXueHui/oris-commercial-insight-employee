def m46_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M46_ENABLED', '')).lower() == 'true'


def build_m46_digest(snapshot, env=None):
    if not m46_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-46', 'file_written': False}
    state = str(snapshot.get('snapshot_state', 'hold'))
    gate = str(snapshot.get('gate_status', 'closed'))
    digest_state = 'green' if state == 'clear' and gate == 'open' else 'amber'
    return {
        'allowed': True,
        'version': '2026-06-26-module-46',
        'digest_state': digest_state,
        'snapshot_state': state,
        'gate_status': gate,
        'digest_visible': True,
        'file_written': False,
    }


def summarize_m46(env=None):
    enabled = m46_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
