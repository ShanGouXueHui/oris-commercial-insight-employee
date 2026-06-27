import unittest

from app.release_review import ITEM_ORDER, build_release_review, get_review_item, summarize_release_review


class Module72ReleaseReviewTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_release_review(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertFalse(result['release_ready'])

    def test_enabled_returns_items_in_order(self):
        result = build_release_review(env={'ORIS_RELEASE_REVIEW_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'release_review_defined')
        self.assertEqual(result['item_count'], 5)
        self.assertEqual(result['item_names'], list(ITEM_ORDER))

    def test_ready_and_pending_items_are_separated(self):
        self.assertFalse(get_review_item('scope_locked')['blocking'])
        self.assertFalse(get_review_item('tests_passed')['blocking'])
        self.assertTrue(get_review_item('rollback_plan')['blocking'])
        self.assertTrue(get_review_item('operator_approval')['blocking'])

    def test_release_ready_remains_false_without_approval(self):
        result = build_release_review(env={'ORIS_RELEASE_REVIEW_ENABLED': '1'})
        self.assertEqual(result['blocking_item_count'], 2)
        self.assertFalse(result['release_ready'])
        self.assertTrue(result['operator_approval_required'])

    def test_summary_is_compact_and_safe(self):
        summary = summarize_release_review(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['item_count'], 0)
        self.assertFalse(summary['release_ready'])
        self.assertFalse(summary['external_calls'])


if __name__ == '__main__':
    unittest.main()
