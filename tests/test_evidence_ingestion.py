import unittest

from app.domain_contracts import AnalyticalLens, EvidenceSourceType, build_default_domain_contract
from app.evidence_ingestion import RawEvidenceDocument, build_complete_sample_document, build_ingestion_summary, ingest_documents


class EvidenceIngestionTests(unittest.TestCase):
    def test_complete_sample_passes(self):
        contract = build_default_domain_contract("TestCo")
        result = ingest_documents(contract, [build_complete_sample_document("TestCo")])
        self.assertTrue(result.accepted)
        self.assertEqual(result.validation_errors, [])

    def test_partial_document_reports_missing_coverage(self):
        contract = build_default_domain_contract("TestCo")
        doc = RawEvidenceDocument(
            document_id="d1",
            source_id="s1",
            source_type=EvidenceSourceType.PUBLIC_WEB,
            title="partial",
            content="partial",
            credibility_score=0.9,
            claims_by_lens={AnalyticalLens.COMPANY_PROFILE: "claim"},
        )
        result = ingest_documents(contract, [doc])
        self.assertFalse(result.accepted)
        self.assertTrue(any(item.startswith("missing_evidence_for_lens:") for item in result.validation_errors))

    def test_duplicate_source_ids_are_collapsed(self):
        contract = build_default_domain_contract("TestCo")
        doc1 = RawEvidenceDocument("d1", "s1", "public_web", "one", "one", 0.9, {AnalyticalLens.COMPANY_PROFILE: "claim"})
        doc2 = RawEvidenceDocument("d2", "s1", "public_web", "two", "two", 0.9, {AnalyticalLens.MARKET_STRUCTURE: "claim"})
        result = ingest_documents(contract, [doc1, doc2])
        self.assertEqual(len(result.sources), 1)

    def test_string_keys_are_supported(self):
        contract = build_default_domain_contract("TestCo")
        doc = RawEvidenceDocument("d1", "s1", "public_web", "source", "content", 0.9, {"company_profile": "claim"})
        result = ingest_documents(contract, [doc])
        self.assertEqual(result.sources[0].source_type.value, "public_web")
        self.assertEqual(result.evidence_items[0].lens.value, "company_profile")

    def test_summary_is_serializable(self):
        summary = build_ingestion_summary("TestCo")
        self.assertTrue(summary["accepted"])
        self.assertEqual(summary["subject_company"], "TestCo")
        self.assertIn("company_profile", summary["coverage_by_lens"])


if __name__ == "__main__":
    unittest.main()
