import unittest

from app.harness_upgrade_loop import (
    HarnessUpgradeStepType,
    build_harness_upgrade_plan,
    build_harness_upgrade_plans,
    build_harness_upgrade_steps,
    default_harness_upgrade_candidates,
    summarize_harness_upgrade_loop,
)
from app.loop_engineering import LoopDecision
from app.reuse_adoption import ReuseDecision


class Module19HarnessUpgradeLoopTests(unittest.TestCase):
    def test_default_candidates_include_openclaw_and_agents_md(self):
        names = [candidate.name for candidate in default_harness_upgrade_candidates()]
        self.assertIn("openclaw-execution-harness-upgrade", names)
        self.assertIn("agents-md-operating-rules-upgrade", names)

    def test_harness_upgrade_steps_are_boundary_only(self):
        steps = build_harness_upgrade_steps()
        step_types = [step.step_type for step in steps]
        self.assertIn(HarnessUpgradeStepType.DISCOVER, step_types)
        self.assertIn(HarnessUpgradeStepType.REQUIRE_ACCEPTANCE, step_types)
        self.assertTrue(all(step.evidence_required for step in steps))
        self.assertFalse(any(step.live_action for step in steps))

    def test_plan_uses_loop_and_reuse_assessments(self):
        candidate = default_harness_upgrade_candidates()[0]
        plan = build_harness_upgrade_plan(candidate)
        self.assertEqual(plan.loop_name, "harness_upgrade_loop")
        self.assertEqual(plan.loop_decision, LoopDecision.ENABLE_BOUNDARY)
        self.assertIn(plan.reuse_assessment.decision, {ReuseDecision.ADOPT, ReuseDecision.FORK_AND_ADAPT})

    def test_plan_does_not_modify_live_harness(self):
        candidate = default_harness_upgrade_candidates()[0]
        plan = build_harness_upgrade_plan(candidate)
        self.assertFalse(plan.package_installation_enabled)
        self.assertFalse(plan.remote_code_fetch_enabled)
        self.assertFalse(plan.production_harness_modified)
        self.assertTrue(plan.human_acceptance_required)

    def test_build_plans_returns_all_default_candidates(self):
        plans = build_harness_upgrade_plans()
        self.assertEqual(len(plans), len(default_harness_upgrade_candidates()))
        self.assertTrue(all(plan.plan_version == "2026-06-25-module-19" for plan in plans))

    def test_summary_reports_no_live_actions(self):
        summary = summarize_harness_upgrade_loop()
        self.assertGreaterEqual(summary["plan_count"], 2)
        self.assertGreaterEqual(summary["adopt_or_adapt_count"], 1)
        self.assertFalse(summary["package_installation_enabled"])
        self.assertFalse(summary["remote_code_fetch_enabled"])
        self.assertFalse(summary["production_harness_modified"])
        self.assertTrue(summary["human_acceptance_required"])
        self.assertTrue(summary["evidence_required"])


if __name__ == "__main__":
    unittest.main()
