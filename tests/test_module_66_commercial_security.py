import unittest

from app.commercial_security import (
    PERMISSION_ORDER,
    ROLE_ORDER,
    build_security_baseline,
    get_role_policy,
    summarize_security,
)


class Module66CommercialSecurityTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_security_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['roles'], [])

    def test_enabled_returns_roles_and_permissions(self):
        result = build_security_baseline(env={'ORIS_COMMERCIAL_SECURITY_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'security_rbac_baseline_defined')
        self.assertEqual(result['role_count'], 5)
        self.assertEqual(result['permission_count'], len(PERMISSION_ORDER))
        self.assertEqual(result['roles'], list(ROLE_ORDER))

    def test_owner_and_admin_permissions_are_distinct(self):
        owner = get_role_policy('owner')
        admin = get_role_policy('admin')
        self.assertIn('tenant.manage', owner['permissions'])
        self.assertNotIn('tenant.manage', admin['permissions'])
        self.assertFalse(owner['least_privilege'])
        self.assertTrue(admin['least_privilege'])

    def test_viewer_and_auditor_are_read_oriented(self):
        viewer = get_role_policy('viewer')
        auditor = get_role_policy('auditor')
        self.assertIn('insight.read', viewer['permissions'])
        self.assertNotIn('insight.write', viewer['permissions'])
        self.assertIn('audit.read', auditor['permissions'])
        self.assertTrue(auditor['audit_required'])

    def test_enabled_baseline_requires_security_controls(self):
        result = build_security_baseline(env={'ORIS_COMMERCIAL_SECURITY_ENABLED': '1'})
        self.assertTrue(result['tenant_isolation_required'])
        self.assertTrue(result['audit_required'])
        self.assertTrue(result['safe_logging_required'])
        self.assertTrue(result['secret_boundary_required'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_security(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['role_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
