import unittest

from app.brief_pipeline import GeneratedExecutiveBrief, build_sample_brief, generate_executive_brief_from_ingestion
from app.domain_contracts import AnalyticalLens, EvidenceSourceType, build_default_domain_contract
from app.evidence_ingestion import RawEvidenceDocument, ingest_documents
from app.quality_gates import GateStatus, assess_brief_quality, assess_sample_brief


class QualityGateTests(unittest.TestCase):
    def test_sample_brief_passes_quality_gates(self):
        assessment = assess_sample_brief("TestCo")
        self.assertTrue(assessment["accepted"])
        self.assertEqual(assessment["overall_status"], "pass")
        self.assertEqual(assessment["recommended_action"], "publish")

    def test_incomplete_brief_requires_repair(self):
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
        ingestion = ingest_documents(contract, [doc])
        brief = generate_executive_brief_from_ingestion(ingestion)
        assessment = assess_brief_quality(brief)
        self.assertFalse(assessment.accepted)
        self.assertEqual(assessment.recommended_action, "repair")
        self.assertTrue(assessment.limitations)

    def test_missing_risks_or_scenarios_fails_gate(self):
        sample = build_sample_brief("TestCo")
        brief = GeneratedExecutiveBrief(
            company_name="TestCo",
            sections=[],
            risks=[],
            scenarios=[],
            limitations=[],
            confidence_score=0.9,
            accepted=True,
        )
        assessment = assess_brief_quality(brief)
        self.assertEqual(assessment.overall_status, GateStatus.FAIL)
        self.assertFalse(assessment.accepted)
        self.assertIn("repair", assessment.recommended_action)
        self.assertEqual(sample["company_name"], "TestCo")

    def test_quality_result_serializes(self):
        assessment = assess_sample_brief("TestCo")
        self.assertIn("gate_results", assessment)
        self.assertTrue(all("gate_id" in item for item in assessment["gate_results"]))


if __name__ == "__main__":
    unittest.main()
