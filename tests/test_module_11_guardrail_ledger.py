import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.commercial_guardrails import SQLiteGuardrailLedger, build_guardrail_ledger, summarize_guardrail_ledger


class Module11GuardrailLedgerTests(unittest.TestCase):
    def test_sqlite_ledger_initializes_required_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "ledger.sqlite3")
            ledger = SQLiteGuardrailLedger(db_path)
            self.assertEqual(ledger.count_rows("guardrail_usage"), 0)
            self.assertGreaterEqual(ledger.count_rows("guardrail_metadata"), 2)

    def test_build_ledger_uses_sqlite_when_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "configured.sqlite3")
            ledger = build_guardrail_ledger(
                {
                    "ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_GUARDRAIL_LEDGER_PATH": db_path,
                }
            )
            self.assertIsInstance(ledger, SQLiteGuardrailLedger)
            self.assertTrue(Path(db_path).exists())

    def test_sqlite_ledger_persists_usage_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "persistent.sqlite3")
            now = datetime(2026, 6, 24, 12, 0, tzinfo=timezone.utc)
            first = SQLiteGuardrailLedger(db_path)
            self.assertEqual(first.consume("client-a", now=now), (1, 1))
            second = SQLiteGuardrailLedger(db_path)
            self.assertEqual(second.consume("client-a", now=now), (2, 2))
            self.assertEqual(second.count_rows("guardrail_usage"), 2)

    def test_ledger_summary_reports_sqlite_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "summary.sqlite3")
            summary = summarize_guardrail_ledger(
                {
                    "ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE": "sqlite",
                    "ORIS_INSIGHT_GUARDRAIL_LEDGER_PATH": db_path,
                }
            )
            self.assertEqual(summary["storage_mode"], "sqlite")
            self.assertTrue(summary["persistent_quota_ready"])
            self.assertEqual(summary["tables"], ["guardrail_metadata", "guardrail_usage"])


if __name__ == "__main__":
    unittest.main()
