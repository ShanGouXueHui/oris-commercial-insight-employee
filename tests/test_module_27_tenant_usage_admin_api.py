import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.commercial_guardrails import reset_default_guardrail_ledger
from app.config import load_product_settings
from app.main import app
from app.tenant_usage_admin_api import evaluate_tenant_usage_admin_access, summarize_tenant_usage_admin_api, tenant_usage_admin_policy_from_settings
from app.tenant_usage_ledger import DEFAULT_TENANT_USAGE_LEDGER, SQLiteTenantUsageLedger, reset_default_tenant_usage_ledger


class Module27TenantUsageAdminApiTests(unittest.TestCase):
    def setUp(self):
        reset_default_guardrail_ledger()
        reset_default_tenant_usage_ledger()
        self.client = TestClient(app)

    def test_default_admin_api_disabled(self):
        settings = load_product_settings({})
        self.assertFalse(settings.tenant_guardrails.tenant_usage_admin_api_enabled)
        response = self.client.get("/insights/admin/tenant-usage?tenant_id=tenant-a")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["reason"], "tenant_usage_admin_api_disabled")

    def test_enabled_admin_api_requires_configured_admin_key(self):
        with patch.dict(os.environ, {"ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true"}, clear=False):
            response = self.client.get("/insights/admin/tenant-usage?tenant_id=tenant-a")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["reason"], "tenant_usage_admin_key_not_configured")

    def test_invalid_admin_key_is_rejected_without_secret_echo(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "correct-key",
            },
            clear=False,
        ):
            response = self.client.get(
                "/insights/admin/tenant-usage?tenant_id=tenant-a",
                headers={"x-oris-admin-key": "wrong-key"},
            )
        payload = response.json()["detail"]
        self.assertEqual(response.status_code, 403)
        self.assertEqual(payload["reason"], "tenant_usage_admin_key_invalid")
        self.assertNotIn("correct-key", str(payload))
        self.assertNotIn("wrong-key", str(payload))

    def test_admin_key_is_masked_in_settings_payload(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "secret-one,secret-two",
            }
        )
        payload = settings.tenant_guardrails.to_dict()
        self.assertEqual(payload["tenant_usage_admin_keys"], ["configured"])
        self.assertNotIn("secret-one", str(payload))
        self.assertNotIn("secret-two", str(payload))

    def test_admin_api_reads_in_memory_usage_when_enabled(self):
        DEFAULT_TENANT_USAGE_LEDGER.consume("tenant-a", period="2026-06")
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "admin-key",
            },
            clear=False,
        ):
            response = self.client.get(
                "/insights/admin/tenant-usage?tenant_id=tenant-a&period=2026-06",
                headers={"x-oris-admin-key": "admin-key"},
            )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["read_only"])
        self.assertEqual(payload["tenant_usage_admin_api_version"], "2026-06-25-module-27")
        self.assertEqual(payload["usage"]["request_count"], 1)
        self.assertEqual(payload["storage"]["storage_mode"], "in_memory")

    def test_admin_api_reads_sqlite_usage_when_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            SQLiteTenantUsageLedger(db_path).consume("tenant-a", period="2026-06")
            with patch.dict(
                os.environ,
                {
                    "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                    "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "admin-key",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                },
                clear=False,
            ):
                response = self.client.get(
                    "/insights/admin/tenant-usage?tenant_id=tenant-a&period=2026-06",
                    headers={"x-oris-admin-key": "admin-key"},
                )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["usage"]["request_count"], 1)
        self.assertEqual(payload["storage"]["storage_mode"], "sqlite")
        self.assertFalse(payload["external_storage_enabled"])
        self.assertFalse(payload["live_external_action_enabled"])

    def test_admin_api_read_does_not_consume_usage_when_tenant_middleware_consumption_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            SQLiteTenantUsageLedger(db_path).consume("tenant-a", period="2026-06")
            with patch.dict(
                os.environ,
                {
                    "ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED": "true",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED": "true",
                    "ORIS_INSIGHT_TENANT_USAGE_CONSUME_ON_ALLOWED_REQUEST": "true",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                    "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                    "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "admin-key",
                },
                clear=False,
            ):
                response = self.client.get(
                    "/insights/admin/tenant-usage?tenant_id=tenant-a&period=2026-06",
                    headers={"x-oris-admin-key": "admin-key"},
                )
            usage_after = SQLiteTenantUsageLedger(db_path).get_usage("tenant-a", period="2026-06")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["usage"]["request_count"], 1)
        self.assertEqual(usage_after.request_count, 1)

    def test_health_details_reports_module_27_admin_api_summary(self):
        response = self.client.get("/healthz/details")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["module_27_tenant_usage_admin_api"])
        self.assertFalse(payload["tenant_usage_admin_api"]["enabled"])
        self.assertTrue(payload["tenant_usage_admin_api"]["read_only"])
        self.assertTrue(payload["tenant_usage_admin_api"]["explicit_configuration_required"])

    def test_access_evaluator_allows_only_enabled_policy_with_matching_key(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED": "true",
                "ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS": "admin-key",
            }
        )
        policy = tenant_usage_admin_policy_from_settings(settings.tenant_guardrails)
        denied = evaluate_tenant_usage_admin_access({"x-oris-admin-key": "bad"}, policy)
        allowed = evaluate_tenant_usage_admin_access({"x-oris-admin-key": "admin-key"}, policy)
        summary = summarize_tenant_usage_admin_api(settings.tenant_guardrails)
        self.assertFalse(denied["allowed"])
        self.assertTrue(allowed["allowed"])
        self.assertTrue(summary["enabled"])
        self.assertFalse(summary["external_storage_enabled"])
        self.assertFalse(summary["live_external_action_enabled"])


if __name__ == "__main__":
    unittest.main()
