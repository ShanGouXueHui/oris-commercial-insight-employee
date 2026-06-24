import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.commercial_guardrails import InMemoryGuardrailLedger, evaluate_guardrails, reset_default_guardrail_ledger
from app.config import load_product_settings
from app.main import app


class Module10CommercialGuardrailsTests(unittest.TestCase):
    def setUp(self):
        reset_default_guardrail_ledger()
        self.client = TestClient(app)

    def test_default_observe_mode_is_non_blocking_and_reported(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "observe",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["module_10_commercial_guardrails"])
        self.assertTrue(payload["commercial_guardrails_boundary"])
        self.assertEqual(payload["guardrail_policy"]["enforcement_mode"], "observe")
        self.assertEqual(response.headers["X-ORIS-Guardrail-Reason"], "observe_mode_non_blocking")

    def test_blocking_mode_rejects_missing_api_key_for_commercial_endpoint(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "true",
                "ORIS_INSIGHT_API_KEYS": "module10-secret",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance")
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["error"]["error_code"], "api_key_missing")
        self.assertFalse(payload["guardrail"]["allowed"])

    def test_blocking_mode_allows_valid_api_key(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "true",
                "ORIS_INSIGHT_API_KEYS": "module10-secret",
                "ORIS_INSIGHT_RATE_LIMIT_PER_MINUTE": "10",
                "ORIS_INSIGHT_QUOTA_PER_DAY": "10",
            },
            clear=False,
        ):
            response = self.client.get("/insights/rebuild/acceptance", headers={"x-api-key": "module10-secret"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Guardrail-Reason"], "allowed")
        self.assertIn("X-ORIS-RateLimit-Remaining-Minute", response.headers)

    def test_rate_limit_blocks_after_configured_minute_limit(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "false",
                "ORIS_INSIGHT_RATE_LIMIT_PER_MINUTE": "1",
                "ORIS_INSIGHT_QUOTA_PER_DAY": "10",
            }
        ).commercial_guardrails
        ledger = InMemoryGuardrailLedger()
        now = datetime(2026, 6, 24, 12, 0, tzinfo=timezone.utc)
        first = evaluate_guardrails("/insights/rebuild/brief", "POST", {}, settings, ledger=ledger, now=now)
        second = evaluate_guardrails("/insights/rebuild/brief", "POST", {}, settings, ledger=ledger, now=now)
        self.assertTrue(first.allowed)
        self.assertFalse(second.allowed)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.error.error_code, "rate_limit_exceeded")

    def test_health_paths_remain_exempt_in_blocking_mode(self):
        with patch.dict(
            os.environ,
            {
                "ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT": "blocking",
                "ORIS_INSIGHT_REQUIRE_API_KEY": "true",
                "ORIS_INSIGHT_API_KEYS": "module10-secret",
            },
            clear=False,
        ):
            response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-ORIS-Guardrail-Reason"], "exempt_path")


if __name__ == "__main__":
    unittest.main()
