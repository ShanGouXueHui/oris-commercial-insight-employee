import unittest

from app.loop_engineering import (
    LoopComponent,
    LoopDecision,
    LoopDefinition,
    assess_loop,
    build_loop_engineering_plan,
    default_loop_definitions,
    is_loop_bounded,
    summarize_loop_engineering_boundary,
)


class Module18LoopEngineeringTests(unittest.TestCase):
    def test_default_loops_include_oris_page_and_harness_upgrade(self):
        names = [loop.name for loop in default_loop_definitions()]
        self.assertIn("oris_page_improvement_loop", names)
        self.assertIn("harness_upgrade_loop", names)

    def test_bounded_loop_is_enabled(self):
        loop = LoopDefinition(
            name="safe-loop",
            goal="safe bounded loop",
            components=(LoopComponent.AUTOMATION, LoopComponent.EVIDENCE_GATE, LoopComponent.BUDGET_GATE),
            max_iterations=3,
            max_token_budget=10000,
        )
        assessment = assess_loop(loop)
        self.assertEqual(assessment.decision, LoopDecision.ENABLE_BOUNDARY)
        self.assertTrue(assessment.bounded)
        self.assertEqual(assessment.estimated_risk, "low")

    def test_unbounded_loop_is_rejected(self):
        loop = LoopDefinition(
            name="bad-loop",
            goal="too many iterations",
            components=(LoopComponent.AUTOMATION, LoopComponent.EVIDENCE_GATE, LoopComponent.BUDGET_GATE),
            max_iterations=100,
            max_token_budget=10000,
        )
        assessment = assess_loop(loop)
        self.assertEqual(assessment.decision, LoopDecision.REJECT)
        self.assertIn("loop_not_bounded", assessment.reasons)

    def test_loop_without_evidence_gate_is_rejected(self):
        loop = LoopDefinition(
            name="no-evidence-loop",
            goal="missing evidence",
            components=(LoopComponent.AUTOMATION, LoopComponent.BUDGET_GATE),
            max_iterations=2,
            max_token_budget=10000,
            evidence_required=False,
        )
        assessment = assess_loop(loop)
        self.assertEqual(assessment.decision, LoopDecision.REJECT)
        self.assertIn("evidence_gate_missing", assessment.reasons)

    def test_network_secret_loop_is_deferred(self):
        loop = LoopDefinition(
            name="live-loop",
            goal="live integration",
            components=(LoopComponent.AUTOMATION, LoopComponent.EVIDENCE_GATE, LoopComponent.BUDGET_GATE),
            max_iterations=2,
            max_token_budget=10000,
            requires_network=True,
            requires_secret=True,
        )
        assessment = assess_loop(loop)
        self.assertEqual(assessment.decision, LoopDecision.DEFER)
        self.assertIn("requires_network_boundary", assessment.reasons)
        self.assertIn("requires_secret_boundary", assessment.reasons)

    def test_loop_plan_requires_budget_and_evidence_gates(self):
        plan = build_loop_engineering_plan()
        self.assertTrue(plan["budget_gate_required"])
        self.assertTrue(plan["evidence_gate_required"])
        self.assertTrue(plan["human_acceptance_required"])
        self.assertFalse(plan["infinite_loop_allowed"])
        self.assertIn("oris_page_improvement_loop", plan["enabled_boundaries"])

    def test_summary_reports_loop_boundary(self):
        summary = summarize_loop_engineering_boundary()
        self.assertGreaterEqual(summary["loop_count"], 4)
        self.assertGreaterEqual(summary["enabled_boundary_count"], 3)
        self.assertTrue(summary["budget_gate_required"])
        self.assertTrue(summary["evidence_gate_required"])
        self.assertFalse(summary["infinite_loop_allowed"])

    def test_is_loop_bounded_enforces_limits(self):
        ok = LoopDefinition(
            name="ok",
            goal="ok",
            components=(LoopComponent.EVIDENCE_GATE, LoopComponent.BUDGET_GATE),
            max_iterations=10,
            max_token_budget=500000,
        )
        bad = LoopDefinition(
            name="bad",
            goal="bad",
            components=(LoopComponent.EVIDENCE_GATE, LoopComponent.BUDGET_GATE),
            max_iterations=11,
            max_token_budget=500001,
        )
        self.assertTrue(is_loop_bounded(ok))
        self.assertFalse(is_loop_bounded(bad))


if __name__ == "__main__":
    unittest.main()
