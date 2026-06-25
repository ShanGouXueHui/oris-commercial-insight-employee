import tempfile
import unittest
from pathlib import Path

from app.bootstrap_migration import (
    build_bootstrap_migration_plan,
    inspect_bootstrap_script,
    inspect_bootstrap_scripts,
    summarize_bootstrap_migration,
)


class Module21BootstrapMigrationTests(unittest.TestCase):
    def test_inspect_script_detects_evidence_harness_usage(self):
        status = inspect_bootstrap_script("scripts/bootstrap_insight_rebuild_module_19.sh")
        self.assertTrue(status.exists)
        self.assertTrue(status.uses_evidence_harness)
        self.assertEqual(status.module_number, 19)
        self.assertFalse(status.migration_required)

    def test_inspect_script_marks_missing_as_not_required(self):
        status = inspect_bootstrap_script("scripts/bootstrap_insight_rebuild_module_999.sh")
        self.assertFalse(status.exists)
        self.assertFalse(status.uses_evidence_harness)
        self.assertIsNone(status.module_number)
        self.assertFalse(status.migration_required)

    def test_inspect_scripts_handles_multiple_paths(self):
        statuses = inspect_bootstrap_scripts(
            ["scripts/bootstrap_insight_rebuild_module_19.sh", "scripts/bootstrap_insight_rebuild_module_20.sh"]
        )
        self.assertEqual(len(statuses), 2)
        self.assertTrue(all(status.exists for status in statuses))
        self.assertTrue(all(status.uses_evidence_harness for status in statuses))

    def test_migration_plan_selects_module_19(self):
        plan = build_bootstrap_migration_plan(
            ["scripts/bootstrap_insight_rebuild_module_19.sh", "scripts/bootstrap_insight_rebuild_module_20.sh"]
        )
        self.assertEqual(plan.scanned_count, 2)
        self.assertEqual(plan.migrated_count, 2)
        self.assertEqual(plan.pending_count, 0)
        self.assertIn("scripts/bootstrap_insight_rebuild_module_19.sh", plan.selected_for_module_21)
        self.assertFalse(plan.package_installation_enabled)
        self.assertFalse(plan.remote_code_fetch_enabled)
        self.assertFalse(plan.production_execution_changed)

    def test_pending_script_is_detected_in_temp_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bootstrap_insight_rebuild_module_42.sh"
            path.write_text("#!/usr/bin/env bash\necho legacy\n", encoding="utf-8")
            plan = build_bootstrap_migration_plan([str(path)])
            self.assertEqual(plan.scanned_count, 1)
            self.assertEqual(plan.migrated_count, 0)
            self.assertEqual(plan.pending_count, 1)
            self.assertEqual(plan.pending_paths, (str(path),))

    def test_summary_reports_no_live_actions(self):
        summary = summarize_bootstrap_migration(
            ["scripts/bootstrap_insight_rebuild_module_19.sh", "scripts/bootstrap_insight_rebuild_module_20.sh"]
        )
        self.assertEqual(summary["scanned_count"], 2)
        self.assertEqual(summary["migrated_count"], 2)
        self.assertEqual(summary["pending_count"], 0)
        self.assertFalse(summary["package_installation_enabled"])
        self.assertFalse(summary["remote_code_fetch_enabled"])
        self.assertFalse(summary["production_execution_changed"])


if __name__ == "__main__":
    unittest.main()
