def m38_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M38_ENABLED', '')).lower() == 'true'


def build_m38_rollup(items, env=None):
    if not m38_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-38', 'file_written': False}
    bounded = list(items)[:100]
    return {
        'allowed': True,
        'version': '2026-06-26-module-38',
        'item_count': len(bounded),
        'file_written': False,
    }


def summarize_m38(env=None):
    enabled = m38_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}


def m39_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M39_ENABLED', '')).lower() == 'true'


def build_m39_health(rollup, env=None):
    if not m39_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-39', 'file_written': False}
    count = int(rollup.get('item_count', 0) or 0)
    status = 'ready'
    if count == 0:
        status = 'empty'
    if count >= 100:
        status = 'bounded'
    return {
        'allowed': True,
        'version': '2026-06-26-module-39',
        'health_status': status,
        'item_count': count,
        'file_written': False,
    }


def summarize_m39(env=None):
    enabled = m39_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}


def m40_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M40_ENABLED', '')).lower() == 'true'


def build_m40_readiness(health, env=None):
    if not m40_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-40', 'file_written': False}
    status = str(health.get('health_status', 'unknown'))
    ready = status in {'ready', 'bounded'}
    reason = 'ready_for_review' if ready else 'not_ready_for_review'
    return {
        'allowed': True,
        'version': '2026-06-26-module-40',
        'readiness_status': 'ready' if ready else 'blocked',
        'reason': reason,
        'source_health_status': status,
        'file_written': False,
    }


def summarize_m40(env=None):
    enabled = m40_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
