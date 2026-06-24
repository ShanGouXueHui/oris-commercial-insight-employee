import tempfile
import unittest
from pathlib import Path

from app.config import load_product_settings
from app.domain_contracts import InsightVertical, build_default_domain_contract
from app.evidence_ingestion import build_complete_sample_document, ingest_documents
from app.evidence_persistence import SQLITE_EVIDENCE_TABLES, SQLiteEvidenceStore, build_evidence_store
from app.runtime_orchestration import LocalRuntimeV2OrchestrationAdapter, RuntimeV2RunRequest


class Module8DurablePersistenceTests(unittest.TestCase):
    def _ingestion(self, company_name="PersistCo"):
        contract = build_default_domain_contract(company_name, InsightVertical.TECHNOLOGY)
        return ingest_documents(contract, [build_complete_sample_document(company_name)])

    def test_sqlite_schema_initializes_required_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "evidence.sqlite3")
            store = SQLiteEvidenceStore(db_path)
            self.assertEqual(store.count_rows("runtime_runs"), 0)
            for table in SQLITE_EVIDENCE_TABLES:
                self.assertGreaterEqual(store.count_rows(table), 0)

    def test_sqlite_store_persists_sources_and_evidence_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "evidence.sqlite3")
            store = SQLiteEvidenceStore(db_path)
            ingestion = self._ingestion()
            record = store.persist("rtv2-module8-test", ingestion)
            loaded = store.load_record("rtv2-module8-test")
            self.assertIsNotNone(loaded)
            self.assertEqual(record.storage_mode, "sqlite")
            self.assertEqual(loaded.evidence_count, len(ingestion.evidence_items))
            self.assertEqual(store.count_rows("runtime_runs"), 1)
            self.assertEqual(store.count_rows("evidence_sources"), len(ingestion.sources))
            self.assertEqual(store.count_rows("evidence_items"), len(ingestion.evidence_items))

    def test_build_evidence_store_uses_sqlite_when_configured(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "configured.sqlite3")
            settings = load_product_settings(
                {
                    "ORIS_INSIGHT_EVIDENCE_STORAGE": "sqlite",
                    "ORIS_INSIGHT_EVIDENCE_LOCAL_PATH": db_path,
                }
            )
            store = build_evidence_store(settings.evidence_persistence)
            self.assertIsInstance(store, SQLiteEvidenceStore)

    def test_runtime_adapter_can_persist_run_to_sqlite(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "runtime.sqlite3")
            settings = load_product_settings(
                {
                    "ORIS_INSIGHT_EVIDENCE_STORAGE": "sqlite",
                    "ORIS_INSIGHT_EVIDENCE_LOCAL_PATH": db_path,
                }
            )
            store = build_evidence_store(settings.evidence_persistence)
            adapter = LocalRuntimeV2OrchestrationAdapter(settings=settings, evidence_store=store)
            run = adapter.execute(RuntimeV2RunRequest(company_name="SQLiteCo", vertical=InsightVertical.RETAIL))
            self.assertTrue(run.accepted)
            self.assertEqual(run.persistence_record.storage_mode, "sqlite")
            self.assertEqual(store.count_rows("runtime_runs"), 1)
            self.assertEqual(store.count_rows("evidence_items"), len(run.ingestion.evidence_items))


if __name__ == "__main__":
    unittest.main()
