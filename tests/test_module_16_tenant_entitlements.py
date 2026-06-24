import unittest

from app.tenant_entitlements import (
    DEFAULT_PLANS,
    TenantRecord,
    UsageRecord,
    build_default_entitlement,
    evaluate_entitlement,
    render_tenant_schema_manifest,
    summarize_tenant_entitlement_boundary,
)


class Module16TenantEntitlementTests(unittest.TestCase):
    def test_default_plans_include_free_team_enterprise(self):
        plan_ids = [plan.plan_id for plan in DEFAULT_PLANS]
        self.assertEqual(plan_ids, ["free", "team", "enterprise"])

    def test_build_default_entitlement_copies_plan_limits(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        plan = DEFAULT_PLANS[1]
        entitlement = build_default_entitlement(tenant, plan, effective_from="2026-06-24T00:00:00+00:00")
        self.assertEqual(entitlement.tenant_id, "tenant-a")
        self.assertEqual(entitlement.plan_id, "team")
        self.assertEqual(entitlement.monthly_request_quota, plan.monthly_request_quota)
        self.assertEqual(entitlement.per_minute_request_limit, plan.per_minute_request_limit)

    def test_evaluate_entitlement_allows_when_usage_below_quota(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0])
        decision = evaluate_entitlement(
            "tenant-a",
            [entitlement],
            UsageRecord(tenant_id="tenant-a", period="2026-06", request_count=10),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "entitlement_allowed")
        self.assertEqual(decision.remaining_monthly_requests, 90)

    def test_evaluate_entitlement_blocks_when_missing(self):
        decision = evaluate_entitlement("missing", [], None)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "tenant_entitlement_missing")

    def test_evaluate_entitlement_blocks_when_quota_exceeded(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0])
        decision = evaluate_entitlement(
            "tenant-a",
            [entitlement],
            UsageRecord(tenant_id="tenant-a", period="2026-06", request_count=100),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "monthly_quota_exceeded")
        self.assertEqual(decision.remaining_monthly_requests, 0)

    def test_schema_manifest_is_boundary_only(self):
        manifest = render_tenant_schema_manifest()
        self.assertEqual(manifest["tables"], ["tenants", "plans", "tenant_entitlements", "tenant_usage"])
        self.assertFalse(manifest["billing_provider_integrated"])
        self.assertFalse(manifest["payment_processing_enabled"])
        self.assertFalse(manifest["invoice_generation_enabled"])
        self.assertIn("real_payment_processing", manifest["non_scope"])

    def test_summary_reports_no_payment_or_invoice_processing(self):
        summary = summarize_tenant_entitlement_boundary()
        self.assertEqual(summary["table_count"], 4)
        self.assertTrue(summary["tenant_isolation_boundary"])
        self.assertTrue(summary["quota_enforcement_boundary"])
        self.assertFalse(summary["payment_processing_enabled"])
        self.assertFalse(summary["invoice_generation_enabled"])


if __name__ == "__main__":
    unittest.main()
