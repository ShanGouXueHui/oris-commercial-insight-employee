import unittest

from app.managed_database import (
    build_postgres_schema_manifest,
    managed_database_tables,
    render_postgres_create_table,
    summarize_managed_database_transition,
    table_names,
)


class Module13ManagedDatabaseTests(unittest.TestCase):
    def test_manifest_contains_evidence_and_guardrail_tables(self):
        names = table_names()
        self.assertIn("runtime_runs", names)
        self.assertIn("evidence_sources", names)
        self.assertIn("evidence_items", names)
        self.assertIn("guardrail_usage", names)
        self.assertEqual(len(names), 6)

    def test_postgres_manifest_is_boundary_only(self):
        manifest = build_postgres_schema_manifest()
        self.assertEqual(manifest["target"], "postgresql")
        self.assertFalse(manifest["live_connection_required"])
        self.assertEqual(manifest["default_runtime_store"], "sqlite_until_managed_db_enabled")
        self.assertIn("production_cutover", manifest["non_scope"])

    def test_render_postgres_create_table_includes_primary_key(self):
        table = managed_database_tables()[0]
        sql = render_postgres_create_table(table)
        self.assertTrue(sql.startswith("CREATE TABLE IF NOT EXISTS"))
        self.assertIn("PRIMARY KEY", sql)
        self.assertIn(table.name, sql)

    def test_manifest_create_statements_match_table_count(self):
        manifest = build_postgres_schema_manifest()
        self.assertEqual(len(manifest["table_names"]), len(manifest["create_table_statements"]))
        self.assertEqual(manifest["migration_order"], manifest["table_names"])

    def test_transition_summary_reports_not_cutover_ready(self):
        summary = summarize_managed_database_transition()
        self.assertEqual(summary["target"], "postgresql")
        self.assertEqual(summary["table_count"], 6)
        self.assertFalse(summary["live_connection_required"])
        self.assertFalse(summary["production_cutover_ready"])


if __name__ == "__main__":
    unittest.main()
