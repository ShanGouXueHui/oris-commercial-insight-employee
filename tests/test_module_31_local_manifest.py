import unittest

from app.tenant_operational_audit_retention import build_local_audit_manifest, summarize_local_audit_manifest


class Module31LocalManifestTests(unittest.TestCase):
    def test_manifest_disabled_by_default(self):
        result = build_local_audit_manifest(event_count=3, tenant_id="tenant-a", env={})
        self.assertFalse(result["allowed"])
        self.assertFalse(result["file_written"])

    def test_manifest_enabled_explicitly(self):
        result = build_local_audit_manifest(
            event_count=3,
            tenant_id="tenant-a",
            env={"ORIS_INSIGHT_LOCAL_AUDIT_MANIFEST_ENABLED": "true"},
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(result["event_count"], 3)
        self.assertEqual(result["tenant_id"], "tenant-a")

    def test_manifest_event_count_is_bounded(self):
        result = build_local_audit_manifest(
            event_count=99999,
            tenant_id="tenant-a",
            env={"ORIS_INSIGHT_LOCAL_AUDIT_MANIFEST_ENABLED": "true"},
        )
        self.assertEqual(result["event_count"], 1000)

    def test_manifest_summary_safe_defaults(self):
        summary = summarize_local_audit_manifest(env={})
        self.assertFalse(summary["enabled"])
        self.assertTrue(summary["manifest_only"])
        self.assertFalse(summary["file_written"])
        self.assertFalse(summary["external_storage_enabled"])


if __name__ == "__main__":
    unittest.main()
