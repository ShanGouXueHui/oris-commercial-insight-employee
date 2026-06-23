import unittest

from app.domain_contracts import (
    AnalyticalLens,
    EvidenceItemContract,
    EvidenceSourceContract,
    EvidenceSourceType,
    InsightVertical,
    REQUIRED_BRIEF_LENSES,
    build_default_domain_contract,
    validate_evidence_against_contract,
)


class DomainContractTests(unittest.TestCase):
    def test_default_domain_contract_contains_all_required_lenses(self):
        contract = build_default_domain_contract("AITO", InsightVertical.AUTOMOTIVE)
        lenses = [section.lens for section in contract.required_sections]
        self.assertEqual(lenses, REQUIRED_BRIEF_LENSES)
        self.assertEqual(contract.subject.company_name, "AITO")

    def test_invalid_subject_rejected(self):
        with self.assertRaises(ValueError):
            build_default_domain_contract("")

    def test_source_credibility_gate(self):
        contract = build_default_domain_contract("TestCo")
        sources = [EvidenceSourceContract("s1", EvidenceSourceType.PUBLIC_WEB, "Low credibility", 0.2)]
        evidence = [EvidenceItemContract("e1", "s1", "claim", AnalyticalLens.COMPANY_PROFILE, 0.8)]
        errors = validate_evidence_against_contract(contract, sources, evidence)
        self.assertIn("source_credibility_below_gate:s1", errors)

    def test_missing_source_detected(self):
        contract = build_default_domain_contract("TestCo")
        errors = validate_evidence_against_contract(
            contract,
            [],
            [EvidenceItemContract("e1", "missing", "claim", AnalyticalLens.COMPANY_PROFILE, 0.9)],
        )
        self.assertIn("missing_source:e1", errors)

    def test_complete_evidence_set_passes_contract(self):
        contract = build_default_domain_contract("TestCo")
        sources = [EvidenceSourceContract("s1", EvidenceSourceType.PUBLIC_WEB, "Source", 0.9)]
        evidence = [
            EvidenceItemContract(f"e{idx}", "s1", f"claim {lens.value}", lens, 0.8)
            for idx, lens in enumerate(REQUIRED_BRIEF_LENSES)
        ]
        self.assertEqual(validate_evidence_against_contract(contract, sources, evidence), [])

    def test_to_dict_uses_stable_string_enums(self):
        contract = build_default_domain_contract("TestCo", InsightVertical.RETAIL)
        payload = contract.to_dict()
        self.assertEqual(payload["subject"]["vertical"], "retail")
        self.assertIn("public_web", payload["accepted_source_types"])


if __name__ == "__main__":
    unittest.main()
