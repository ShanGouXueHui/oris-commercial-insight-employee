import unittest

from app.remote_runtime_queue import (
    BoundaryRemoteRuntimeQueueAdapter,
    DisabledRemoteRuntimeQueueAdapter,
    build_remote_runtime_job_id,
    build_remote_runtime_queue_adapter,
    summarize_remote_runtime_queue,
)
from app.runtime_orchestration import RuntimeV2RunRequest


class Module15RemoteRuntimeQueueTests(unittest.TestCase):
    def test_default_queue_adapter_is_disabled_and_local_safe(self):
        adapter = build_remote_runtime_queue_adapter({})
        readiness = adapter.readiness()
        self.assertIsInstance(adapter, DisabledRemoteRuntimeQueueAdapter)
        self.assertTrue(readiness.ready)
        self.assertFalse(readiness.remote_dispatch_attempted)
        self.assertFalse(readiness.credential_exposed)

    def test_disabled_adapter_enqueue_does_not_dispatch(self):
        adapter = build_remote_runtime_queue_adapter({})
        job = adapter.enqueue(RuntimeV2RunRequest(company_name="Acme"))
        self.assertEqual(job.status, "local_only_not_dispatched")
        self.assertFalse(job.remote_dispatched)
        self.assertEqual(adapter.status(job.job_id)["job_id"], job.job_id)

    def test_remote_boundary_requires_endpoint(self):
        adapter = build_remote_runtime_queue_adapter({"ORIS_REMOTE_RUNTIME_QUEUE_MODE": "remote_boundary"})
        readiness = adapter.readiness()
        self.assertIsInstance(adapter, BoundaryRemoteRuntimeQueueAdapter)
        self.assertFalse(readiness.ready)
        self.assertEqual(readiness.reason, "remote_runtime_endpoint_missing")

    def test_remote_boundary_requires_credential(self):
        adapter = build_remote_runtime_queue_adapter(
            {
                "ORIS_REMOTE_RUNTIME_QUEUE_MODE": "remote_boundary",
                "ORIS_RUNTIME_QUEUE_ENDPOINT": "https://runtime.example.invalid/queue",
            }
        )
        readiness = adapter.readiness()
        self.assertFalse(readiness.ready)
        self.assertEqual(readiness.reason, "remote_runtime_credential_missing")
        self.assertFalse(readiness.remote_dispatch_attempted)

    def test_remote_boundary_configured_but_dispatch_disabled(self):
        adapter = build_remote_runtime_queue_adapter(
            {
                "ORIS_REMOTE_RUNTIME_QUEUE_MODE": "remote_boundary",
                "ORIS_RUNTIME_QUEUE_ENDPOINT": "https://runtime.example.invalid/queue",
                "ORIS_RUNTIME_QUEUE_TOKEN": "secret-token",
            }
        )
        readiness = adapter.readiness()
        self.assertTrue(readiness.ready)
        self.assertTrue(readiness.endpoint_configured)
        self.assertTrue(readiness.credential_configured)
        self.assertFalse(readiness.credential_exposed)
        self.assertFalse(readiness.remote_dispatch_attempted)
        job = adapter.enqueue(RuntimeV2RunRequest(company_name="Acme"))
        self.assertEqual(job.status, "boundary_ready_not_dispatched")
        self.assertFalse(job.remote_dispatched)

    def test_dispatch_enabled_is_blocked_until_implemented(self):
        adapter = build_remote_runtime_queue_adapter(
            {
                "ORIS_REMOTE_RUNTIME_QUEUE_MODE": "remote_boundary",
                "ORIS_RUNTIME_QUEUE_ENDPOINT": "https://runtime.example.invalid/queue",
                "ORIS_RUNTIME_QUEUE_TOKEN": "secret-token",
                "ORIS_REMOTE_RUNTIME_DISPATCH_ENABLED": "true",
            }
        )
        readiness = adapter.readiness()
        self.assertFalse(readiness.ready)
        self.assertTrue(readiness.dispatch_enabled)
        self.assertFalse(readiness.remote_dispatch_attempted)
        self.assertEqual(readiness.reason, "remote_dispatch_not_implemented_in_module_15")

    def test_summary_does_not_expose_credentials(self):
        summary = summarize_remote_runtime_queue(
            {
                "ORIS_REMOTE_RUNTIME_QUEUE_MODE": "remote_boundary",
                "ORIS_RUNTIME_QUEUE_ENDPOINT": "https://runtime.example.invalid/queue",
                "ORIS_RUNTIME_QUEUE_TOKEN": "secret-token",
            }
        )
        self.assertFalse(summary["credential_exposed"])
        self.assertFalse(summary["remote_dispatch_attempted"])
        self.assertEqual(summary["readiness"]["reason"], "remote_runtime_configured_but_dispatch_disabled")

    def test_job_id_is_deterministic(self):
        request = RuntimeV2RunRequest(company_name="Acme")
        first = build_remote_runtime_job_id(request, "queue-a")
        second = build_remote_runtime_job_id(request, "queue-a")
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("rrq-"))


if __name__ == "__main__":
    unittest.main()
