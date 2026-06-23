import unittest

from app.runtime_v2_alignment import (
    RUNTIME_V2_REQUIRED_CAPABILITIES,
    build_architecture_summary,
    build_runtime_v2_alignment,
    validate_alignment,
)


class RuntimeV2AlignmentTests(unittest.TestCase):
    def test_runtime_v2_alignment_is_valid(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(validate_alignment(alignment), [])

    def test_required_capabilities_are_complete(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.required_capabilities, RUNTIME_V2_REQUIRED_CAPABILITIES)

    def test_product_mutation_is_allowed_only_after_runtime_acceptance(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.runtime_status, "accepted")
        self.assertTrue(alignment.product_repo_mutation_allowed)

    def test_rebuild_sequence_starts_with_architecture_alignment(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.rebuild_modules[0], "module_1_architecture_alignment")
        self.assertIn("module_6_api_surface_and_acceptance", alignment.rebuild_modules)

    def test_architecture_summary_identifies_next_module(self):
        summary = build_architecture_summary()
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["next_module"], "module_2_domain_contracts")


if __name__ == "__main__":
    unittest.main()
