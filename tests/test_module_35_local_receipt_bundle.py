import unittest

from app.local_manifest_receipt_bundle import (
    MAX_RECEIPT_BUNDLE_SIZE,
    build_local_receipt_bundle_summary,
    summarize_local_receipt_bundle,
)


class Module35LocalReceiptBundleTests(unittest.TestCase):
    def test_bundle_disabled_by_default(self):
        result = build_local_receipt_bundle_summary([{'receipt_id': 'r1'}], env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['bundle_visible'])
        self.assertFalse(result['file_written'])

    def test_bundle_enabled_explicitly_counts_receipts(self):
        receipts = [
            {'receipt_id': 'r1', 'checksum': 'a', 'verified': True},
            {'receipt_id': 'r2', 'checksum': 'b', 'verified': False},
        ]
        result = build_local_receipt_bundle_summary(
            receipts,
            env={'ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['receipt_count'], 2)
        self.assertEqual(result['verified_true_count'], 1)
        self.assertEqual(result['verified_false_count'], 1)
        self.assertEqual(result['checksum_count'], 2)

    def test_bundle_size_is_bounded(self):
        receipts = [{'receipt_id': str(index)} for index in range(MAX_RECEIPT_BUNDLE_SIZE + 5)]
        result = build_local_receipt_bundle_summary(
            receipts,
            env={'ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_ENABLED': 'true'},
        )
        self.assertEqual(result['receipt_count'], MAX_RECEIPT_BUNDLE_SIZE)

    def test_bundle_summary_safe_defaults(self):
        summary = summarize_local_receipt_bundle(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['bundle_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
