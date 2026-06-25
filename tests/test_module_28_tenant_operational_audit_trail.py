import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.tenant_operational_audit import (
    DEFAULT_TENANT_OPERATIONAL_AUDIT_TRAIL,
    InMemoryTenantOperationalAuditTrail,
    SQLiteTenantOperationalAuditTrail,
    build_tenant_operational_audit_trail,
    reset_default_tenant_operational_audit_trail,
    summarize_tenant_operational_audit_trail,
    tenant_operational_audit_enabled,
)
from app.tenant_operational_audit_query import (
    TenantOperationalAuditQueryRequest,
    query_tenant_operational_audit,
    summarize_tenant_operational_audit_query,
    tenant_operational_audit_query_enabled,
)


class Module28TenantOperationalAuditTrailTests(unittest.TestCase):
    def setUp(self):
        reset_default_tenant_operational_audit_trail()
        self.client = TestClient(app)

    def test_default_operational_audit_disabled(self):
        summary = summarize_tenant_operational_audit_trail(env={})
        self.assertFalse(tenant_operational_audit_enabled(env={}))
        self.assertFalse(summary["enabled"])
        self.assertEqual(summary["storage_mode"], "in_memory")
        self.assertTrue(summary["request_path_unchanged_by_default"])

    def test_in_memory_audit_records_and_lists_events(self):
        trail = InMemoryTenantOperationalAuditTrail()
        event = trail.record_event(
            event_type="tenant_usage_visibility_read",
            actor_id="operator_verified",
            tenant_id="tenant-a",
            period="2026-06",
            operation="read_tenant_usage",
            result="allowed",
        )
        events = trail.list_events("tenant-a")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_id, event.event_id)
        self.assertEqual(events[0].actor_id, "operator_verified")

    def test_default_builder_returns_in_memory_audit_trail(self):
        trail = build_tenant_operational_audit_trail(env={})
        self.assertIs(trail, DEFAULT_TENANT_OPERATIONAL_AUDIT_TRAIL)

    def test_sqlite_audit_trail_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_audit.sqlite3")
            first = SQLiteTenantOperationalAuditTrail(db_path)
            first.record_event("tenant_usage_visibility_read", "operator_verified", "tenant-a", "2026-06", "read", "allowed")
            second = SQLiteTenantOperationalAuditTrail(db_path)
            events = second.list_events("tenant-a")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].tenant_id, "tenant-a")
        self.assertEqual(events[0].period, "2026-06")

    def test_sqlite_audit_trail_creates_metadata_and_event_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_audit.sqlite3")
            trail = SQLiteTenantOperationalAuditTrail(db_path)
            trail.record_event("tenant_usage_visibility_read", "operator_verified", "tenant-a", "2026-06", "read", "allowed")
            self.assertEqual(trail.count_rows("tenant_operational_audit_events"), 1)
            self.assertGreaterEqual(trail.count_rows("tenant_operational_audit_metadata"), 2)

    def test_builder_uses_sqlite_only_when_explicitly_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_audit.sqlite3")
            trail = build_tenant_operational_audit_trail(
                env={
                    "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_PATH": db_path,
                }
            )
            trail.record_event("tenant_usage_visibility_read", "operator_verified", "tenant-a", "2026-06", "read", "allowed")
            events = SQLiteTenantOperationalAuditTrail(db_path).list_events("tenant-a")
        self.assertEqual(len(events), 1)

    def test_summary_reports_enabled_sqlite_without_external_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "tenant_audit.sqlite3")
            summary = summarize_tenant_operational_audit_trail(
                env={
                    "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED": "true",
                    "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_STORAGE": "sqlite",
                    "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_PATH": db_path,
                }
            )
        self.assertTrue(summary["enabled"])
        self.assertEqual(summary["storage_mode"], "sqlite")
        self.assertTrue(summary["read_only_observability"])
        self.assertFalse(summary["external_storage_enabled"])
        self.assertFalse(summary["live_external_action_enabled"])

    def test_health_details_reports_module_28_audit_summary(self):
        with patch.dict(
            os.environ,
            {"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED": "true"},
            clear=False,
        ):
            response = self.client.get("/healthz/details")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["module_28_tenant_operational_audit_trail"])
        self.assertTrue(payload["tenant_operational_audit_trail"]["enabled"])
        self.assertFalse(payload["tenant_operational_audit_trail"]["external_storage_enabled"])
        self.assertFalse(payload["tenant_operational_audit_trail"]["live_external_action_enabled"])


class Module29TenantOperationalAuditQueryTests(unittest.TestCase):
    def test_query_disabled_by_default(self):
        trail = InMemoryTenantOperationalAuditTrail()
        trail.record_event("tenant_usage_visibility_read", "operator", "tenant-a", "2026-06", "read", "allowed")
        result = query_tenant_operational_audit(TenantOperationalAuditQueryRequest(tenant_id="tenant-a"), trail=trail, env={})
        self.assertFalse(tenant_operational_audit_query_enabled(env={}))
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "tenant_operational_audit_query_disabled")
        self.assertEqual(result.events, [])

    def test_enabled_query_returns_matching_tenant_events(self):
        trail = InMemoryTenantOperationalAuditTrail()
        trail.record_event("tenant_usage_visibility_read", "operator", "tenant-a", "2026-06", "read", "allowed")
        trail.record_event("tenant_usage_visibility_read", "operator", "tenant-b", "2026-06", "read", "allowed")
        result = query_tenant_operational_audit(
            TenantOperationalAuditQueryRequest(tenant_id="tenant-a"),
            trail=trail,
            env={"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED": "true"},
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, "tenant_operational_audit_query_allowed")
        self.assertEqual(result.to_dict()["event_count"], 1)
        self.assertEqual(result.events[0]["tenant_id"], "tenant-a")

    def test_enabled_query_supports_all_tenants(self):
        trail = InMemoryTenantOperationalAuditTrail()
        trail.record_event("tenant_usage_visibility_read", "operator", "tenant-a", "2026-06", "read", "allowed")
        trail.record_event("tenant_usage_visibility_read", "operator", "tenant-b", "2026-06", "read", "allowed")
        result = query_tenant_operational_audit(
            TenantOperationalAuditQueryRequest(tenant_id=None),
            trail=trail,
            env={"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED": "true"},
        )
        self.assertEqual(result.to_dict()["event_count"], 2)

    def test_query_limit_is_bounded(self):
        trail = InMemoryTenantOperationalAuditTrail()
        for index in range(3):
            trail.record_event("tenant_usage_visibility_read", "operator", "tenant-a", "2026-06", f"read-{index}", "allowed")
        result = query_tenant_operational_audit(
            TenantOperationalAuditQueryRequest(tenant_id="tenant-a", limit=2),
            trail=trail,
            env={"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED": "true"},
        )
        self.assertEqual(result.limit, 2)
        self.assertEqual(result.to_dict()["event_count"], 2)

    def test_query_reads_sqlite_trail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/audit.sqlite3"
            SQLiteTenantOperationalAuditTrail(db_path).record_event(
                "tenant_usage_visibility_read", "operator", "tenant-a", "2026-06", "read", "allowed"
            )
            result = query_tenant_operational_audit(
                TenantOperationalAuditQueryRequest(tenant_id="tenant-a"),
                trail=SQLiteTenantOperationalAuditTrail(db_path),
                env={"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED": "true"},
            )
        self.assertTrue(result.allowed)
        self.assertEqual(result.to_dict()["event_count"], 1)
        self.assertEqual(result.events[0]["tenant_id"], "tenant-a")

    def test_summary_reports_safe_defaults(self):
        disabled = summarize_tenant_operational_audit_query(env={})
        enabled = summarize_tenant_operational_audit_query(
            env={"ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED": "true"}
        )
        self.assertFalse(disabled["enabled"])
        self.assertTrue(enabled["enabled"])
        self.assertTrue(disabled["read_only"])
        self.assertFalse(disabled["external_storage_enabled"])
        self.assertFalse(disabled["live_external_action_enabled"])


if __name__ == "__main__":
    unittest.main()
