import unittest

from app.local_manifest_receipt import build_local_manifest_receipt, summarize_local_manifest_receipt
from app.tenant_operational_audit_retention import build_local_manifest_checksum


class Module34LocalManifestReceiptTests(unittest.TestCase):
    def test_receipt_disabled_by_default(self):
        result = build_local_manifest_receipt({'manifest_id': 'm1'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['receipt_visible'])
        self.assertFalse(result['file_written'])

    def test_receipt_enabled_explicitly(self):
        result = build_local_manifest_receipt(
            {'manifest_id': 'm1', 'event_count': 3},
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_RECEIPT_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertTrue(result['receipt_visible'])
        self.assertEqual(len(result['checksum']), 64)

    def test_receipt_can_include_verification_result(self):
        manifest = {'manifest_id': 'm1', 'event_count': 3}
        checksum = build_local_manifest_checksum(
            manifest,
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED': 'true'},
        )['checksum']
        result = build_local_manifest_receipt(
            manifest,
            expected_checksum=checksum,
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_RECEIPT_ENABLED': 'true'},
        )
        self.assertTrue(result['verified'])

    def test_receipt_summary_safe_defaults(self):
        summary = summarize_local_manifest_receipt(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['receipt_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
