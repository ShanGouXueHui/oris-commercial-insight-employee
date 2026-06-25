import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.commercial_guardrails import reset_default_guardrail_ledger
from app.config import load_product_settings
from app.main import app
from app.tenant_entitlements import DEFAULT_PLANS, TenantRecord, build_default_entitlement
from app.tenant_guardrails import (
    TenantGuardrailPolicy,
    evaluate_tenant_entitlement_guardrails,
    summarize_tenant_middleware_usage_ledger_bridge,
)
from app.tenant_usage_ledger import (
    DEFAULT_TENANT_USAGE_LEDGER,
    InMemoryTenantUsageLedger,
    reset_default_tenant_usage_ledger,
)


FIXED_NOW = datetime(2026, 6, 25, 12, 30, tzinfo=timezone.utc)


class Module25TenantMiddlewareUsageLedgerTests(unittest.TestCase):
    def setUp(self):
        reset_default_guardrail_ledger()
        reset_default_tenant_usage_ledger()
        self.client = TestClient(app)

    def test_default_usage_ledger_middleware_flags_are_disabled(self):
        settings = load_product_settings({})
        self.assertFalse(settings.tenant_guardrails.tenant_usage_ledger_enabled)
        self.assertFalse(settings.tenant_guardrails.tenant_usage_consume_on_allowed_request)

    def test_default_disabled_path_does_not_add_usage_headers(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "observe",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "false",
                "ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED": "false",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("X-ORIS-Tenant-Usage-Ledger-Version", response.headers)
        self.assertNotIn("X-ORIS-Tenant-Usage-Request-Count", response.headers)

    def test_explicit_configuration_enables_usage_ledger_bridge(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_CONSUME_ON_ALLOWED_REQUEST": "true",
            }
        )
        summary = summarize_tenant_middleware_usage_ledger_bridge(settings.tenant_guardrails)
        self.assertTrue(settings.tenant_guardrails.tenant_usage_ledger_enabled)
        self.assertTrue(settings.tenant_guardrails.tenant_usage_consume_on_allowed_request)
        self.assertEqual(summary["tenant_middleware_usage_ledger_version"], "2026-06-25-module-25")
        self.assertFalse(summary["request_path_unchanged_by_default"])

    def test_ledger_usage_blocks_when_tenant_reaches_monthly_quota(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0], effective_from="2026-06-25T00:00:00+00:00")
        usage_ledger = InMemoryTenantUsageLedger()
        for _ in range(100):
            usage_ledger.consume("tenant-a", now=FIXED_NOW)
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
            }
        )
        decision = evaluate_tenant_entitlement_guardrails(
            path="/insights/rebuild/acceptance",
            method="GET",
            headers={"x-tenant-id": "tenant-a"},
            settings=settings.commercial_guardrails,
            entitlements=(entitlement,),
            policy=TenantGuardrailPolicy(
                entitlement_enforcement_mode="blocking",
                require_tenant_entitlement=True,
                tenant_usage_ledger_enabled=True,
            ),
            tenant_usage_ledger=usage_ledger,
            now=FIXED_NOW,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status_code, 429)
        self.assertEqual(decision.reason, "tenant_entitlement_monthly_quota_exceeded")
        self.assertEqual(decision.tenant_usage_request_count, 100)
        self.assertFalse(decision.tenant_usage_consumed)

    def test_allowed_request_consumes_usage_when_explicitly_enabled(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0], effective_from="2026-06-25T00:00:00+00:00")
        usage_ledger = InMemoryTenantUsageLedger()
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
            }
        )
        decision = evaluate_tenant_entitlement_guardrails(
            path="/insights/rebuild/acceptance",
            method="GET",
            headers={"x-tenant-id": "tenant-a"},
            settings=settings.commercial_guardrails,
            entitlements=(entitlement,),
            policy=TenantGuardrailPolicy(
                entitlement_enforcement_mode="blocking",
                require_tenant_entitlement=True,
                tenant_usage_ledger_enabled=True,
                tenant_usage_consume_on_allowed_request=True,
            ),
            tenant_usage_ledger=usage_ledger,
            now=FIXED_NOW,
        )
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.tenant_usage_consumed)
        self.assertEqual(decision.tenant_usage_request_count, 1)
        self.assertEqual(usage_ledger.get_usage("tenant-a", now=FIXED_NOW).request_count, 1)

    def test_middleware_records_usage_headers_when_flags_are_enabled(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_TENANT_ENTITLEMENT": "true",
                "ORIS_INSIGHT_LOCAL_TENANT_ENTITLEMENTS_ENABLED": "true",
                "ORIS_INSIGHT_LOCAL_TENANT_ID": "tenant-a",
                "ORIS_INSIGHT_LOCAL_TENANT_PLAN": "free",
                "ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_CONSUME_ON_ALLOWED_REQUEST": "true",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance", headers={"x-tenant-id": "tenant-a"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Tenant-Guardrail-Reason"], "tenant_entitlement_allowed")
        self.assertEqual(response.headers["X-ORIS-Tenant-Usage-Ledger-Version"], "2026-06-25-module-24")
        self.assertEqual(response.headers["X-ORIS-Tenant-Usage-Consumed"], "true")
        self.assertEqual(response.headers["X-ORIS-Tenant-Usage-Request-Count"], "1")
        self.assertEqual(DEFAULT_TENANT_USAGE_LEDGER.get_usage("tenant-a").request_count, 1)

    def test_exempt_paths_do_not_consume_tenant_usage(self):
        tenant = TenantRecord(tenant_id="tenant-a", display_name="Tenant A")
        entitlement = build_default_entitlement(tenant, DEFAULT_PLANS[0], effective_from="2026-06-25T00:00:00+00:00")
        usage_ledger = InMemoryTenantUsageLedger()
        settings = load_product_settings({"ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking"})
        decision = evaluate_tenant_entitlement_guardrails(
            path="/healthz",
            method="GET",
            headers={"x-tenant-id": "tenant-a"},
            settings=settings.commercial_guardrails,
            entitlements=(entitlement,),
            policy=TenantGuardrailPolicy(
                entitlement_enforcement_mode="blocking",
                require_tenant_entitlement=True,
                tenant_usage_ledger_enabled=True,
                tenant_usage_consume_on_allowed_request=True,
            ),
            tenant_usage_ledger=usage_ledger,
            now=FIXED_NOW,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "exempt_path_entitlement_skipped")
        self.assertIsNone(decision.tenant_usage_request_count)
        self.assertFalse(decision.tenant_usage_consumed)
        self.assertEqual(usage_ledger.get_usage("tenant-a").request_count, 0)


if __name__ == "__main__":
    unittest.main()
