import unittest

from app.tenant_operational_audit_retention import build_local_manifest_checksum, summarize_local_manifest_checksum


class Module32LocalManifestChecksumTests(unittest.TestCase):
    def test_checksum_disabled_by_default(self):
        result = build_local_manifest_checksum({'manifest_id': 'm1'}, env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['checksum_visible'])

    def test_checksum_enabled_explicitly(self):
        result = build_local_manifest_checksum(
            {'manifest_id': 'm1', 'event_count': 3},
            env={'ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED': 'true'},
        )
        self.assertTrue(result['allowed'])
        self.assertEqual(result['checksum_algorithm'], 'sha256')
        self.assertEqual(len(result['checksum']), 64)

    def test_checksum_is_deterministic_for_key_order(self):
        env = {'ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED': 'true'}
        first = build_local_manifest_checksum({'a': 1, 'b': 2}, env=env)
        second = build_local_manifest_checksum({'b': 2, 'a': 1}, env=env)
        self.assertEqual(first['checksum'], second['checksum'])

    def test_checksum_summary_safe_defaults(self):
        summary = summarize_local_manifest_checksum(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['checksum_visible'])
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_storage_enabled'])


if __name__ == '__main__':
    unittest.main()
