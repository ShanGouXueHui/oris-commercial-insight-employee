import unittest

from fastapi.testclient import TestClient

from app.config import load_product_settings
from app.main import app
from app.observability import build_runtime_observability_snapshot


class Module9ObservabilityTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_observability_snapshot_reports_smoke_ready(self):
        snapshot = build_runtime_observability_snapshot(load_product_settings())
        payload = snapshot.to_dict()
        self.assertEqual(payload["status"], "healthy")
        self.assertTrue(payload["runtime_v2_backed"])
        self.assertTrue(payload["module_9_deployment_smoke_ready"])
        self.assertIn("evidence_schema", payload)

    def test_healthz_observability_endpoint(self):
        payload = self.client.get("/healthz/observability").json()
        self.assertEqual(payload["status"], "healthy")
        self.assertTrue(payload["module_9_deployment_smoke_ready"])

    def test_health_details_includes_observability(self):
        payload = self.client.get("/healthz/details").json()
        self.assertTrue(payload["module_9_observability"])
        self.assertEqual(payload["observability"]["status"], "healthy")

    def test_rebuild_acceptance_reports_module_9_smoke_ready(self):
        payload = self.client.get("/insights/rebuild/acceptance").json()
        self.assertTrue(payload["module_9_deployment_smoke_ready"])
        self.assertTrue(payload["observability_boundary"])
        self.assertEqual(payload["observability"]["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
