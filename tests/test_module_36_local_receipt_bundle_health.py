import unittest

from app.local_receipt_bundle_health import build_local_receipt_bundle_health, summarize_local_receipt_bundle_health


class Module36LocalReceiptBundleHealthTests(unittest.TestCase):
    def test_health_disabled_by_default(self):
        result = build_local_receipt_bundle_health({'receipt_count': 1}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['health_visible'])
        self.assertFalse(result['file_written'])

    def test_health_reports_healthy_bundle(self):
        result = build_local_receipt_bundle_health(
            {'receipt_count': 2, 'verified_true_count': 2, 'verified_false_count': 0, 'checksum_count': 2},
            env={'ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_HEALTH_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['health_status'], 'healthy')

    def test_health_reports_attention_required(self):
        result = build_local_receipt_bundle_health(
            {'receipt_count': 2, 'verified_true_count': 1, 'verified_false_count': 1, 'checksum_count': 2},
            env={'ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_HEALTH_ENABLED': 'true'},
        )
        self.assertEqual(result['health_status'], 'attention_required')

    def test_health_summary_safe_defaults(self):
        summary = summarize_local_receipt_bundle_health(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['health_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
