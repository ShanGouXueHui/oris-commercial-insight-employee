import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_details_reports_runtime_rebuild(self):
        payload = self.client.get("/healthz/details").json()
        self.assertEqual(payload["version"], "0.2.0")
        self.assertTrue(payload["runtime_v2_backed_rebuild"])

    def test_rebuild_acceptance_endpoint_ready(self):
        payload = self.client.get("/insights/rebuild/acceptance").json()
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["runtime_v2_backed"])

    def test_rebuild_brief_endpoint_generates_brief(self):
        payload = self.client.post("/insights/rebuild/brief", json={"company_name": "TestCo", "vertical": "technology"}).json()
        self.assertEqual(payload["company_name"], "TestCo")
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["recommended_action"], "publish")

    def test_legacy_endpoint_still_works(self):
        response = self.client.post("/insights/executive-brief", json={"company_name": "LegacyCo", "industry": "Retail"})
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
