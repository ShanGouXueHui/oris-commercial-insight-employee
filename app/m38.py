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


def m41_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M41_ENABLED', '')).lower() == 'true'


def build_m41_checklist(readiness, env=None):
    if not m41_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-41', 'file_written': False}
    status = str(readiness.get('readiness_status', 'blocked'))
    checks = [
        {'name': 'readiness_visible', 'passed': True},
        {'name': 'ready_status', 'passed': status == 'ready'},
        {'name': 'local_only', 'passed': True},
    ]
    passed_count = sum(1 for item in checks if item['passed'])
    return {
        'allowed': True,
        'version': '2026-06-26-module-41',
        'check_count': len(checks),
        'passed_count': passed_count,
        'blocked_count': len(checks) - passed_count,
        'checks': checks,
        'file_written': False,
    }


def summarize_m41(env=None):
    enabled = m41_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}


def m42_enabled(env=None):
    values = {} if env is None else env
    return str(values.get('ORIS_INSIGHT_M42_ENABLED', '')).lower() == 'true'


def build_m42_summary(checklist, env=None):
    if not m42_enabled(env):
        return {'allowed': False, 'version': '2026-06-26-module-42', 'file_written': False}
    total = int(checklist.get('check_count', 0) or 0)
    passed = int(checklist.get('passed_count', 0) or 0)
    blocked = int(checklist.get('blocked_count', max(total - passed, 0)) or 0)
    status = 'complete' if total > 0 and blocked == 0 else 'incomplete'
    return {
        'allowed': True,
        'version': '2026-06-26-module-42',
        'summary_status': status,
        'check_count': total,
        'passed_count': passed,
        'blocked_count': blocked,
        'file_written': False,
    }


def summarize_m42(env=None):
    enabled = m42_enabled(env)
    return {'enabled': enabled, 'enabled_by_default': False, 'file_written': False}
