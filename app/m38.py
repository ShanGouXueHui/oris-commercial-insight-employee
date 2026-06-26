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
