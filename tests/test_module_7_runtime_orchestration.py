import unittest

from app.config import load_product_settings
from app.domain_contracts import REQUIRED_BRIEF_LENSES, InsightVertical
from app.runtime_orchestration import LocalRuntimeV2OrchestrationAdapter, RuntimeV2RunRequest
from app.source_connectors import DeterministicLocalSourceConnector, SourceQuery


class Module7RuntimeOrchestrationTests(unittest.TestCase):
    def test_config_separates_source_model_and_runtime_settings(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_SOURCE_CONNECTOR": "deterministic_local",
                "ORIS_INSIGHT_MODEL_PROVIDER": "deterministic_template",
                "ORIS_INSIGHT_RUNTIME_ADAPTER": "local_runtime_v2_contract",
            }
        )
        self.assertEqual(settings.source.connector_mode, "deterministic_local")
        self.assertEqual(settings.model.provider_mode, "deterministic_template")
        self.assertEqual(settings.runtime.adapter_mode, "local_runtime_v2_contract")
        self.assertFalse(settings.source.allow_network_sources)
        self.assertFalse(settings.model.allow_external_provider)

    def test_deterministic_local_source_connector_covers_required_lenses(self):
        settings = load_product_settings().source
        result = DeterministicLocalSourceConnector(settings).fetch(
            SourceQuery(company_name="Module7Co", vertical=InsightVertical.TECHNOLOGY)
        )
        lenses = {lens for doc in result.documents for lens in doc.claims_by_lens}
        self.assertEqual(lenses, set(REQUIRED_BRIEF_LENSES))
        self.assertFalse(result.metadata.network_access_used)
        self.assertFalse(result.metadata.external_provider_used)

    def test_runtime_adapter_generates_evidence_linked_accepted_run(self):
        adapter = LocalRuntimeV2OrchestrationAdapter(settings=load_product_settings())
        run = adapter.execute(RuntimeV2RunRequest(company_name="RuntimeCo", vertical=InsightVertical.RETAIL))
        self.assertTrue(run.accepted)
        self.assertEqual(run.quality.recommended_action, "publish")
        self.assertEqual(run.source_result.metadata.connector_id, "deterministic_local_source_connector")
        self.assertEqual(run.persistence_record.storage_mode, "in_memory")
        self.assertEqual(len(run.ingestion.coverage_by_lens), len(REQUIRED_BRIEF_LENSES))
        self.assertTrue(all(count >= 1 for count in run.ingestion.coverage_by_lens.values()))

    def test_runtime_adapter_keeps_empty_evidence_path_repairable(self):
        adapter = LocalRuntimeV2OrchestrationAdapter(settings=load_product_settings())
        run = adapter.execute(
            RuntimeV2RunRequest(company_name="RuntimeCo", vertical=InsightVertical.RETAIL, use_sample_evidence=False)
        )
        self.assertFalse(run.accepted)
        self.assertEqual(run.quality.recommended_action, "repair")
        self.assertTrue(run.ingestion.validation_errors)


if __name__ == "__main__":
    unittest.main()
