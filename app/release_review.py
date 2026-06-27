from __future__ import annotations

VERSION = '2026-06-27-module-72-release-review'
FLAG_NAME = 'ORIS_RELEASE_REVIEW_ENABLED'
TRUE_VALUES = {'1', 'true', 'yes', 'on'}

ITEM_ORDER = ('scope_locked', 'tests_passed', 'evidence_present', 'rollback_plan', 'operator_approval')
_ITEM_STATUS = {
    'scope_locked': ('ready', 'commercial baseline scope is bounded'),
    'tests_passed': ('ready', 'full suite evidence is required'),
    'evidence_present': ('ready', 'latest result and execution report are required'),
    'rollback_plan': ('pending', 'operator must define rollback procedure'),
    'operator_approval': ('pending', 'human approval is required before release'),
}


def review_enabled(env=None):
    values = {} if env is None else env
    return str(values.get(FLAG_NAME, '')).strip().lower() in TRUE_VALUES


def get_review_item(name):
    if name not in _ITEM_STATUS:
        raise KeyError(f'unknown review item: {name}')
    status, rationale = _ITEM_STATUS[name]
    return {'name': name, 'status': status, 'rationale': rationale, 'blocking': status != 'ready', 'file_written': False}


def build_release_review(env=None):
    enabled = review_enabled(env)
    result = {'allowed': enabled, 'enabled': enabled, 'enabled_by_default': False, 'flag': FLAG_NAME, 'version': VERSION, 'file_written': False, 'external_calls': False, 'release_published': False, 'default_behavior_changed': False}
    if not enabled:
        result.update({'status': 'disabled', 'item_count': 0, 'items': [], 'release_ready': False})
        return result
    items = [get_review_item(name) for name in ITEM_ORDER]
    blockers = [item['name'] for item in items if item['blocking']]
    result.update({'status': 'release_review_defined', 'review_scope': 'local_read_only_release_readiness_review', 'item_count': len(items), 'item_names': list(ITEM_ORDER), 'items': items, 'blocking_item_count': len(blockers), 'blocking_items': blockers, 'release_ready': False, 'operator_approval_required': True})
    return result


def summarize_release_review(env=None):
    result = build_release_review(env=env)
    return {'enabled': result['enabled'], 'enabled_by_default': result['enabled_by_default'], 'status': result['status'], 'item_count': result['item_count'], 'release_ready': result['release_ready'], 'file_written': result['file_written'], 'external_calls': result['external_calls'], 'release_published': result['release_published'], 'default_behavior_changed': result['default_behavior_changed']}
