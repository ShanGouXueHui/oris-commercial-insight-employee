import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.commercial_guardrails import reset_default_guardrail_ledger
from app.config import load_product_settings
from app.main import app
from app.tenant_guardrails import build_local_tenant_entitlements, summarize_tenant_middleware_activation


class Module23TenantMiddlewareTests(unittest.TestCase):
    def setUp(self):
        reset_default_guardrail_ledger()
        self.client = TestClient(app)

    def test_default_tenant_guardrails_are_disabled(self):
        settings = load_product_settings({})
        self.assertFalse(settings.tenant_guardrails.enabled)

    def test_default_disabled_path_preserves_existing_headers(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "observe",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "false",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Guardrail-Reason"], "observe_mode_non_blocking")
        self.assertNotIn("X-ORIS-Tenant-Guardrail-Reason", response.headers)

    def test_enabled_observe_mode_adds_tenant_headers(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT": "observe",
                "ORIS_INSIGHT_REQUIRE_TENANT_ENTITLEMENT": "true",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance", headers={"x-tenant-id": "tenant-a"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Tenant-Guardrail-Reason"], "tenant_entitlement_observe_mode")
        self.assertEqual(response.headers["X-ORIS-Tenant-ID"], "tenant-a")

    def test_enabled_blocking_mode_blocks_missing_entitlement(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_TENANT_ENTITLEMENT": "true",
                "ORIS_INSIGHT_LOCAL_TENANT_ENTITLEMENTS_ENABLED": "false",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance", headers={"x-tenant-id": "tenant-a"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["tenant_guardrail"]["allowed"])
        self.assertEqual(response.headers["X-ORIS-Tenant-Guardrail-Reason"], "tenant_entitlement_tenant_entitlement_missing")

    def test_enabled_blocking_mode_allows_configured_local_entitlement(self):
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
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance", headers={"x-tenant-id": "tenant-a"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Tenant-Guardrail-Reason"], "tenant_entitlement_allowed")

    def test_health_details_reports_tenant_guardrail_settings(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT": "blocking",
            },
            clear=False,
        ):
            response = self.client.get("/healthz/details")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["module_23_tenant_guardrail_middleware"])
        self.assertTrue(payload["tenant_guardrails"]["enabled"])
        self.assertEqual(payload["tenant_guardrails"]["entitlement_enforcement_mode"], "blocking")

    def test_local_entitlement_builder_uses_configured_plan(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_LOCAL_TENANT_ENTITLEMENTS_ENABLED": "true",
                "ORIS_INSIGHT_LOCAL_TENANT_ID": "tenant-a",
                "ORIS_INSIGHT_LOCAL_TENANT_PLAN": "team",
            }
        )
        entitlements = build_local_tenant_entitlements(settings.tenant_guardrails)
        self.assertEqual(len(entitlements), 1)
        self.assertEqual(entitlements[0].tenant_id, "tenant-a")
        self.assertEqual(entitlements[0].plan_id, "team")

    def test_activation_summary_reports_default_behavior_change(self):
        settings = load_product_settings({"ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true"})
        summary = summarize_tenant_middleware_activation(settings.tenant_guardrails)
        self.assertTrue(summary["tenant_guardrails_enabled"])
        self.assertTrue(summary["default_behavior_changed"])


if __name__ == "__main__":
    unittest.main()
