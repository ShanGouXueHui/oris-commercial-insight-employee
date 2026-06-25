import json
import tempfile
import unittest
from pathlib import Path

from app.evidence_harness import (
    EvidenceHarnessConfig,
    TestRunSnapshot,
    build_latest_test_result_payload,
    record_evidence_commit_sha,
    redact_sensitive_values,
    render_execution_report,
    summarize_evidence_harness_upgrade,
    write_harness_evidence,
)


class Module20EvidenceHarnessTests(unittest.TestCase):
    def _config(self) -> EvidenceHarnessConfig:
        return EvidenceHarnessConfig(
            module_name="Insight Rebuild Module 20",
            bootstrap_version="test-version",
            expected_unit_test_count=84,
            result_filename="module_20.json",
            report_filename="module_20.md",
            implemented_boundaries=("boundary one", "boundary two"),
            evidence_files=("reports/testing/latest_test_result.json", "reports/execution/module_20.md"),
            next_module="Next module placeholder.",
        )

    def _snapshot(self, rc: int = 0) -> TestRunSnapshot:
        return TestRunSnapshot(
            test_command="python3 -m unittest discover -s tests -p test_*.py -q",
            test_exit_code=rc,
            product_base_sha="abc123",
            log_file="reports/execution/log.txt",
            generated_at="2026-06-25T00:00:00+00:00",
        )

    def test_snapshot_status_comes_from_exit_code(self):
        self.assertEqual(self._snapshot(0).status, "passed")
        self.assertEqual(self._snapshot(1).status, "failed")

    def test_latest_result_payload_contains_required_fields(self):
        payload = build_latest_test_result_payload(
            self._config(),
            self._snapshot(),
            flags={"module_20_evidence_harness": True},
            checks=["check_one"],
        )
        self.assertEqual(payload["module"], "Insight Rebuild Module 20")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["test_exit_code"], 0)
        self.assertEqual(payload["expected_unit_test_count"], 84)
        self.assertTrue(payload["module_20_evidence_harness"])
        self.assertEqual(payload["checks"], ["check_one"])

    def test_sensitive_values_are_redacted(self):
        payload = redact_sensitive_values(
            {
                "api_key": "secret",
                "nested": {"database_url": "postgresql://user:pass@example/db"},
                "safe": "value",
            }
        )
        self.assertEqual(payload["api_key"], "<redacted>")
        self.assertEqual(payload["nested"]["database_url"], "<redacted>")
        self.assertEqual(payload["safe"], "value")

    def test_execution_report_contains_boundaries_and_pending_sha(self):
        report = render_execution_report(self._config(), self._snapshot())
        self.assertIn("boundary one", report)
        self.assertIn("test exit code: 0", report)
        self.assertIn("Pending until evidence commit completes.", report)

    def test_write_harness_evidence_writes_latest_and_module_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            testing = Path(tmp) / "testing"
            execution = Path(tmp) / "execution"
            write_harness_evidence(
                self._config(),
                self._snapshot(),
                flags={"token": "secret", "safe_flag": True},
                checks=["check_one"],
                testing_dir=str(testing),
                execution_dir=str(execution),
            )
            latest = json.loads((testing / "latest_test_result.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["token"], "<redacted>")
            self.assertTrue(latest["safe_flag"])
            self.assertTrue((testing / "module_20.json").exists())
            self.assertTrue((execution / "module_20.md").exists())

    def test_record_evidence_commit_sha_replaces_pending_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text("Pending until evidence commit completes.", encoding="utf-8")
            record_evidence_commit_sha(str(path), "deadbeef")
            self.assertEqual(path.read_text(encoding="utf-8"), "deadbeef")

    def test_summary_reports_reusable_helper_flags(self):
        summary = summarize_evidence_harness_upgrade()
        self.assertTrue(summary["latest_result_writer"])
        self.assertTrue(summary["execution_report_renderer"])
        self.assertTrue(summary["sensitive_value_redaction"])
        self.assertTrue(summary["reusable_bootstrap_helper"])
        self.assertFalse(summary["live_external_action_enabled"])


if __name__ == "__main__":
    unittest.main()
