import unittest

from app.tenant_operational_audit_retention import (
    build_local_manifest_checksum,
    summarize_local_manifest_verification,
    verify_local_manifest_checksum,
)


class Module33LocalManifestVerificationTests(unittest.TestCase):
    def test_verification_disabled_by_default(self):
        result = verify_local_manifest_checksum({'manifest_id': 'm1'}, 'abc', env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['verification_visible'])
        self.assertFalse(result['verified'])

    def test_verification_enabled_matches_expected_checksum(self):
        manifest = {'manifest_id': 'm1', 'event_count': 3}
        checksum = build_local_manifest_checksum(
            manifest,
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED': 'true'},
        )['checksum']
        result = verify_local_manifest_checksum(
            manifest,
            checksum,
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_VERIFICATION_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertTrue(result['verified'])
        self.assertEqual(result['actual_checksum'], checksum)

    def test_verification_reports_mismatch(self):
        result = verify_local_manifest_checksum(
            {'manifest_id': 'm1'},
            '0' * 64,
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_VERIFICATION_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertFalse(result['verified'])

    def test_verification_summary_safe_defaults(self):
        summary = summarize_local_manifest_verification(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['verification_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
