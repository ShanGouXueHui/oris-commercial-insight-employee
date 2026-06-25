import unittest
from datetime import datetime, timezone

from app.commercial_guardrails import InMemoryGuardrailLedger
from app.config import load_product_settings
from app.tenant_entitlements import DEFAULT_PLANS, TenantRecord, UsageRecord, build_default_entitlement
from app.tenant_guardrails import (
    TenantGuardrailPolicy,
    evaluate_tenant_entitlement_guardrails,
    summarize_tenant_guardrail_bridge,
)


class Module22TenantGuardrailsTests(unittest.TestCase):
    def _settings(self, **overrides):
        env = {
            "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
            "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
            "ORIS_INSIGHT_RATE_LIMIT_PER_MINUTE": "100",
            "ORIS_INSIGHT_QUOTA_PER_DAY": "100",
        }
        env.update(overrides)
        return load_product_settings(env).commercial_guardrails

    def _tenant_entitlement(self, tenant_id="tenant-a", plan_index=0):
        tenant = TenantRecord(tenant_id=tenant_id, display_name="Tenant A")
        return build_default_entitlement(tenant, DEFAULT_PLANS[plan_index], effective_from="2026-06-25T00:00:00+00:00")

    def test_observe_entitlement_mode_does_not_block_missing_entitlement(self):
        decision = evaluate_tenant_entitlement_guardrails(
            "/insights/rebuild/brief",
            "POST",
            {"x-tenant-id": "tenant-a"},
            self._settings(),
            entitlements=(),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="observe", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "tenant_entitlement_observe_mode")
        self.assertEqual(decision.entitlement["reason"], "tenant_entitlement_missing")

    def test_blocking_mode_blocks_missing_entitlement(self):
        decision = evaluate_tenant_entitlement_guardrails(
            "/insights/rebuild/brief",
            "POST",
            {"x-tenant-id": "tenant-a"},
            self._settings(),
            entitlements=(),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status_code, 403)
        self.assertEqual(decision.reason, "tenant_entitlement_tenant_entitlement_missing")

    def test_blocking_mode_blocks_monthly_quota_exceeded(self):
        entitlement = self._tenant_entitlement("tenant-a", plan_index=0)
        decision = evaluate_tenant_entitlement_guardrails(
            "/insights/rebuild/brief",
            "POST",
            {"x-tenant-id": "tenant-a"},
            self._settings(),
            entitlements=(entitlement,),
            usage=UsageRecord(tenant_id="tenant-a", period="2026-06", request_count=100),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status_code, 429)
        self.assertEqual(decision.reason, "tenant_entitlement_monthly_quota_exceeded")

    def test_blocking_mode_allows_valid_entitlement_under_quota(self):
        entitlement = self._tenant_entitlement("tenant-a", plan_index=0)
        decision = evaluate_tenant_entitlement_guardrails(
            "/insights/rebuild/brief",
            "POST",
            {"x-tenant-id": "tenant-a"},
            self._settings(),
            entitlements=(entitlement,),
            usage=UsageRecord(tenant_id="tenant-a", period="2026-06", request_count=10),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "tenant_entitlement_allowed")
        self.assertEqual(decision.entitlement["remaining_monthly_requests"], 90)

    def test_commercial_guardrail_block_short_circuits_entitlement(self):
        settings = self._settings(
            ORIS_INSIGHT_REQUIRE_API_KEY="true",
            ORIS_INSIGHT_API_KEYS="module22-secret",
        )
        decision = evaluate_tenant_entitlement_guardrails(
            "/insights/rebuild/brief",
            "POST",
            {"x-tenant-id": "tenant-a"},
            settings,
            entitlements=(self._tenant_entitlement("tenant-a"),),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status_code, 401)
        self.assertEqual(decision.reason, "commercial_guardrail_api_key_missing")
        self.assertIsNone(decision.entitlement)

    def test_exempt_path_skips_entitlement(self):
        decision = evaluate_tenant_entitlement_guardrails(
            "/healthz",
            "GET",
            {},
            self._settings(ORIS_INSIGHT_REQUIRE_API_KEY="true", ORIS_INSIGHT_API_KEYS="module22-secret"),
            entitlements=(),
            policy=TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True),
            ledger=InMemoryGuardrailLedger(),
            now=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "exempt_path_entitlement_skipped")
        self.assertIsNone(decision.entitlement)

    def test_summary_is_local_and_provider_free(self):
        summary = summarize_tenant_guardrail_bridge(
            TenantGuardrailPolicy(entitlement_enforcement_mode="blocking", require_tenant_entitlement=True)
        )
        self.assertTrue(summary["commercial_guardrail_bridge"])
        self.assertTrue(summary["tenant_entitlement_bridge"])
        self.assertFalse(summary["billing_provider_integrated"])
        self.assertFalse(summary["payment_processing_enabled"])
        self.assertTrue(summary["local_deterministic_only"])


if __name__ == "__main__":
    unittest.main()
