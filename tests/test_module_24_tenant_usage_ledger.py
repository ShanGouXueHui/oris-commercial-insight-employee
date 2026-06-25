import unittest
from datetime import datetime, timezone

from app.tenant_entitlements import DEFAULT_PLANS, TenantRecord, build_default_entitlement
from app.tenant_usage_ledger import (
    InMemoryTenantUsageLedger,
    evaluate_entitlement_against_usage_ledger,
    monthly_period,
    reset_default_tenant_usage_ledger,
    summarize_tenant_usage_ledger,
)


class Module24TenantUsageLedgerTests(unittest.TestCase):
    def setUp(self):
        reset_default_tenant_usage_ledger()

    def test_monthly_period_is_deterministic(self):
        now = datetime(2026, 6, 25, 12, 30, tzinfo=timezone.utc)
        self.assertEqual(monthly_period(now), "2026-06")

    def test_empty_ledger_returns_zero_usage(self):
        ledger = InMemoryTenantUsageLedger()
        usage = ledger.get_usage("tenant-a", period="2026-06")
        self.assertEqual(usage.tenant_id, "tenant-a")
        self.assertEqual(usage.period, "2026-06")
        self.assertEqual(usage.request_count, 0)

    def test_consume_increments_monthly_usage(self):
        ledger = InMemoryTenantUsageLedger()
        first = ledger.consume("tenant-a", period="2026-06")
        second = ledger.consume("tenant-a", period="2026-06")
        self.assertEqual(first.request_count, 1)
        self.assertEqual(second.request_count, 2)
        self.assertEqual(ledger.get_usage("tenant-a", period="2026-06").request_count, 2)

    def test_snapshot_reports_current_count(self):
        ledger = InMemoryTenantUsageLedger()
        ledger.consume("tenant-a", period="2026-06")
        snapshot = ledger.snapshot("tenant-a", period="2026-06")
        self.assertEqual(snapshot.tenant_id, "tenant-a")
        self.assertEqual(snapshot.period, "2026-06")
        self.assertEqual(snapshot.request_count, 1)
        self.assertEqual(snapshot.ledger_version, "2026-06-25-module-24")

    def test_entitlement_evaluation_uses_ledger_usage(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0], effective_from="2026-06-25T00:00:00+00:00")
        ledger = InMemoryTenantUsageLedger()
        for _ in range(10):
            ledger.consume("tenant-a", period="2026-06")
        decision = evaluate_entitlement_against_usage_ledger("tenant-a", (entitlement,), ledger=ledger, period="2026-06")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.remaining_monthly_requests, 90)

    def test_entitlement_evaluation_blocks_when_ledger_reaches_quota(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0], effective_from="2026-06-25T00:00:00+00:00")
        ledger = InMemoryTenantUsageLedger()
        for _ in range(100):
            ledger.consume("tenant-a", period="2026-06")
        decision = evaluate_entitlement_against_usage_ledger("tenant-a", (entitlement,), ledger=ledger, period="2026-06")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "monthly_quota_exceeded")

    def test_summary_reports_local_only_ledger(self):
        summary = summarize_tenant_usage_ledger(InMemoryTenantUsageLedger())
        self.assertEqual(summary["tenant_usage_ledger_version"], "2026-06-25-module-24")
        self.assertEqual(summary["ledger_type"], "in_memory")
        self.assertTrue(summary["monthly_period_supported"])
        self.assertTrue(summary["consume_supported"])
        self.assertTrue(summary["snapshot_supported"])
        self.assertFalse(summary["external_storage_enabled"])
        self.assertFalse(summary["live_external_action_enabled"])


if __name__ == "__main__":
    unittest.main()
