import unittest

from app.managed_database_adapter import (
    DisabledManagedDatabaseAdapter,
    PostgresBoundaryManagedDatabaseAdapter,
    build_managed_database_adapter,
    load_managed_database_adapter_settings,
    summarize_managed_database_adapter,
)


class Module14ManagedDatabaseAdapterTests(unittest.TestCase):
    def test_default_adapter_is_disabled_and_sqlite_runtime_safe(self):
        adapter = build_managed_database_adapter({})
        readiness = adapter.readiness()
        self.assertIsInstance(adapter, DisabledManagedDatabaseAdapter)
        self.assertTrue(readiness.ready)
        self.assertFalse(readiness.live_connection_attempted)
        self.assertFalse(readiness.credential_exposed)

    def test_postgres_boundary_reports_missing_credential(self):
        adapter = build_managed_database_adapter({"ORIS_INSIGHT_MANAGED_DB_MODE": "postgres_boundary"})
        readiness = adapter.readiness()
        self.assertIsInstance(adapter, PostgresBoundaryManagedDatabaseAdapter)
        self.assertFalse(readiness.ready)
        self.assertEqual(readiness.reason, "managed_database_credential_missing")
        self.assertFalse(readiness.live_connection_attempted)

    def test_postgres_boundary_with_credential_does_not_expose_secret(self):
        adapter = build_managed_database_adapter(
            {
                "ORIS_INSIGHT_MANAGED_DB_MODE": "postgres_boundary",
                "ORIS_INSIGHT_DATABASE_URL": "postgresql://user:secret@example/db",
            }
        )
        readiness = adapter.readiness()
        self.assertTrue(readiness.ready)
        self.assertTrue(readiness.credential_configured)
        self.assertFalse(readiness.credential_exposed)
        self.assertFalse(readiness.live_connection_attempted)

    def test_migration_preview_is_manifest_only(self):
        adapter = build_managed_database_adapter({})
        preview = adapter.migration_preview()
        self.assertTrue(preview["preview_only"])
        self.assertFalse(preview["live_connection_attempted"])
        self.assertEqual(len(preview["manifest"]["table_names"]), 6)

    def test_summary_reports_no_live_connection_attempt(self):
        summary = summarize_managed_database_adapter(
            {
                "ORIS_INSIGHT_MANAGED_DB_MODE": "postgres_boundary",
                "ORIS_INSIGHT_MANAGED_DB_DSN": "postgresql://user:secret@example/db",
            }
        )
        self.assertTrue(summary["preview_available"])
        self.assertFalse(summary["credential_exposed"])
        self.assertFalse(summary["live_connection_attempted"])
        self.assertEqual(summary["readiness"]["target"], "postgresql")

    def test_settings_loader_detects_live_connection_flag_without_connecting(self):
        settings = load_managed_database_adapter_settings(
            {
                "ORIS_INSIGHT_MANAGED_DB_MODE": "postgres_boundary",
                "ORIS_INSIGHT_MANAGED_DB_LIVE_CONNECTION_ENABLED": "true",
            }
        )
        self.assertTrue(settings.live_connection_enabled)
        adapter = build_managed_database_adapter(
            {
                "ORIS_INSIGHT_MANAGED_DB_MODE": "postgres_boundary",
                "ORIS_INSIGHT_MANAGED_DB_LIVE_CONNECTION_ENABLED": "true",
            }
        )
        self.assertFalse(adapter.readiness().live_connection_attempted)


if __name__ == "__main__":
    unittest.main()
