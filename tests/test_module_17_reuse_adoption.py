import unittest

from app.reuse_adoption import (
    ReuseCandidate,
    ReuseCandidateType,
    ReuseDecision,
    assess_reuse_candidate,
    build_reuse_adoption_plan,
    calculate_reuse_score,
    default_reuse_candidates,
    summarize_reuse_adoption_boundary,
)


class Module17ReuseAdoptionTests(unittest.TestCase):
    def test_high_quality_candidate_is_adopted(self):
        candidate = ReuseCandidate(
            name="strong-skill",
            candidate_type=ReuseCandidateType.GITHUB_SKILL,
            source="github",
            stars=2000,
            downloads=20000,
            maintenance_score=20,
            security_score=20,
            license_approved=True,
            fits_product_boundary=True,
        )
        assessment = assess_reuse_candidate(candidate)
        self.assertEqual(assessment.decision, ReuseDecision.ADOPT)
        self.assertGreaterEqual(assessment.score, 75)

    def test_unapproved_license_is_rejected(self):
        candidate = ReuseCandidate(
            name="bad-license",
            candidate_type=ReuseCandidateType.OPENCLAW_SKILL,
            source="registry",
            stars=2000,
            downloads=20000,
            maintenance_score=20,
            security_score=20,
            license_approved=False,
            fits_product_boundary=True,
        )
        assessment = assess_reuse_candidate(candidate)
        self.assertEqual(assessment.decision, ReuseDecision.REJECT)
        self.assertIn("license_not_approved", assessment.reasons)

    def test_network_and_secret_candidate_is_not_direct_adopt(self):
        candidate = ReuseCandidate(
            name="live-skill",
            candidate_type=ReuseCandidateType.OPENCLAW_SKILL,
            source="registry",
            stars=2000,
            downloads=20000,
            maintenance_score=18,
            security_score=18,
            license_approved=True,
            fits_product_boundary=True,
            requires_network=True,
            requires_secret=True,
        )
        assessment = assess_reuse_candidate(candidate)
        self.assertNotEqual(assessment.decision, ReuseDecision.ADOPT)
        self.assertIn("requires_network_boundary", assessment.reasons)
        self.assertIn("requires_secret_boundary", assessment.reasons)

    def test_default_candidates_include_harness_and_agents_md(self):
        types = [candidate.candidate_type for candidate in default_reuse_candidates()]
        self.assertIn(ReuseCandidateType.HARNESS, types)
        self.assertIn(ReuseCandidateType.AGENTS_MD, types)

    def test_adoption_plan_turns_off_custom_code_default(self):
        plan = build_reuse_adoption_plan()
        self.assertFalse(plan["custom_code_default"])
        self.assertTrue(plan["harness_upgrade_recommended"])
        self.assertTrue(plan["agents_md_reuse_recommended"])
        self.assertGreaterEqual(plan["candidate_count"], 4)

    def test_summary_reports_reuse_boundary_counts(self):
        summary = summarize_reuse_adoption_boundary()
        self.assertGreaterEqual(summary["candidate_count"], 4)
        self.assertTrue(summary["harness_upgrade_recommended"])
        self.assertTrue(summary["agents_md_reuse_recommended"])
        self.assertFalse(summary["custom_code_default"])

    def test_score_penalizes_network_and_secret(self):
        safe = ReuseCandidate(
            name="safe",
            candidate_type=ReuseCandidateType.GITHUB_SKILL,
            source="github",
            stars=1000,
            downloads=10000,
            maintenance_score=10,
            security_score=10,
            license_approved=True,
            fits_product_boundary=True,
        )
        risky = ReuseCandidate(
            name="risky",
            candidate_type=ReuseCandidateType.GITHUB_SKILL,
            source="github",
            stars=1000,
            downloads=10000,
            maintenance_score=10,
            security_score=10,
            license_approved=True,
            fits_product_boundary=True,
            requires_network=True,
            requires_secret=True,
        )
        self.assertGreater(calculate_reuse_score(safe), calculate_reuse_score(risky))


if __name__ == "__main__":
    unittest.main()
