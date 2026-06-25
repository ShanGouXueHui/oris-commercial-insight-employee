import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.commercial_guardrails import reset_default_guardrail_ledger
from app.config import load_product_settings
from app.main import app
from app.tenant_usage_ledger import (
    InMemoryTenantUsageLedger,
    SQLiteTenantUsageLedger,
    build_tenant_usage_ledger,
    reset_default_tenant_usage_ledger,
    summarize_tenant_usage_ledger,
)


FIXED_NOW = datetime(2026, 6, 25, 12, 30, tzinfo=timezone.utc)


class Module26DurableTenantUsageLedgerTests(unittest.TestCase):
    def setUp(self):
        reset_default_guardrail_ledger()
        reset_default_tenant_usage_ledger()
        self.client = TestClient(app)

    def test_default_tenant_usage_storage_is_in_memory(self):
        settings = load_product_settings({})
        self.assertEqual(settings.tenant_guardrails.tenant_usage_ledger_storage, "in_memory")
        self.assertIsInstance(build_tenant_usage_ledger(settings.tenant_guardrails, env={}), InMemoryTenantUsageLedger)

    def test_sqlite_tenant_usage_ledger_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            first = SQLiteTenantUsageLedger(db_path)
            first.consume("tenant-a", now=FIXED_NOW)
            first.consume("tenant-a", now=FIXED_NOW)
            second = SQLiteTenantUsageLedger(db_path)
            usage = second.get_usage("tenant-a", now=FIXED_NOW)
        self.assertEqual(usage.period, "2026-06")
        self.assertEqual(usage.request_count, 2)

    def test_sqlite_tenant_usage_ledger_creates_metadata_and_usage_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            ledger = SQLiteTenantUsageLedger(db_path)
            ledger.consume("tenant-a", period="2026-06")
            self.assertEqual(ledger.count_rows("tenant_usage"), 1)
            self.assertGreaterEqual(ledger.count_rows("tenant_usage_metadata"), 2)
            rows = ledger.load_usage_rows("tenant-a")
        self.assertEqual(rows[0]["tenant_id"], "tenant-a")
        self.assertEqual(rows[0]["period"], "2026-06")
        self.assertEqual(rows[0]["request_count"], 1)

    def test_builder_uses_sqlite_only_when_explicitly_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            ledger = build_tenant_usage_ledger(
                env={
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                }
            )
            self.assertIsInstance(ledger, SQLiteTenantUsageLedger)
            ledger.consume("tenant-a", period="2026-06")
            self.assertEqual(SQLiteTenantUsageLedger(db_path).get_usage("tenant-a", period="2026-06").request_count, 1)

    def test_summary_reports_sqlite_storage_without_external_store(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            summary = summarize_tenant_usage_ledger(
                env={
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                }
            )
        self.assertEqual(summary["tenant_usage_ledger_storage_version"], "2026-06-25-module-26")
        self.assertEqual(summary["storage_mode"], "sqlite")
        self.assertEqual(summary["durable_store"], "sqlite")
        self.assertTrue(summary["durable_storage_ready"])
        self.assertFalse(summary["external_storage_enabled"])
        self.assertFalse(summary["live_external_action_enabled"])

    def test_middleware_uses_configured_sqlite_tenant_usage_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
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
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                },
                clear=False,
            ):
                response = self.client.get("/insights/rebuild/acceptance", headers={"x-tenant-id": "tenant-a"})
            persisted = SQLiteTenantUsageLedger(db_path).get_usage("tenant-a")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Tenant-Usage-Consumed"], "true")
        self.assertEqual(response.headers["X-ORIS-Tenant-Usage-Request-Count"], "1")
        self.assertEqual(persisted.request_count, 1)

    def test_health_details_reports_durable_storage_when_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_usage.sqlite3")
            with patch.dict(
                os.environ,
                {
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH": db_path,
                },
                clear=False,
            ):
                response = self.client.get("/healthz/details")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["module_26_durable_tenant_usage_ledger"])
        self.assertEqual(payload["tenant_usage_ledger_storage"]["storage_mode"], "sqlite")
        self.assertTrue(payload["tenant_usage_ledger_storage"]["durable_storage_ready"])
        self.assertFalse(payload["tenant_usage_ledger_storage"]["external_storage_enabled"])


if __name__ == "__main__":
    unittest.main()
