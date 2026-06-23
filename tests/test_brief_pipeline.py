import unittest

from app.brief_pipeline import build_sample_brief, generate_executive_brief_from_ingestion
from app.domain_contracts import AnalyticalLens, EvidenceSourceType, REQUIRED_BRIEF_LENSES, build_default_domain_contract
from app.evidence_ingestion import RawEvidenceDocument, build_complete_sample_document, ingest_documents


class BriefPipelineTests(unittest.TestCase):
    def test_sample_brief_contains_required_sections(self):
        brief = build_sample_brief("TestCo")
        lenses = [section["lens"] for section in brief["sections"]]
        self.assertEqual(lenses, [lens.value for lens in REQUIRED_BRIEF_LENSES])
        self.assertTrue(brief["accepted"])

    def test_sections_are_evidence_linked(self):
        brief = build_sample_brief("TestCo")
        section_by_lens = {section["lens"]: section for section in brief["sections"]}
        self.assertTrue(section_by_lens["company_profile"]["evidence_ids"])
        self.assertTrue(section_by_lens["risks"]["evidence_ids"])

    def test_incomplete_ingestion_lowers_confidence(self):
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
        self.assertFalse(brief.accepted)
        self.assertLessEqual(brief.confidence_score, 0.55)
        self.assertTrue(brief.limitations)

    def test_risks_and_scenarios_are_generated(self):
        brief = build_sample_brief("TestCo")
        self.assertEqual(len(brief["risks"]), 1)
        self.assertEqual(len(brief["scenarios"]), 3)

    def test_brief_output_is_serializable(self):
        brief = build_sample_brief("TestCo")
        self.assertEqual(brief["company_name"], "TestCo")
        self.assertIn("confidence_score", brief)
        self.assertIn("limitations", brief)


if __name__ == "__main__":
    unittest.main()
