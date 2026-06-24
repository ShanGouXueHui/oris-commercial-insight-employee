import unittest

from app.config import load_product_settings
from app.provider_adapters import (
    DeterministicTemplateProviderAdapter,
    ExternalProviderBoundaryAdapter,
    ProviderRequest,
    build_provider_adapter,
    summarize_provider_adapter,
)


class Module12ProviderAdapterTests(unittest.TestCase):
    def test_deterministic_provider_generates_local_response(self):
        adapter = DeterministicTemplateProviderAdapter()
        response = adapter.generate(ProviderRequest(prompt="Analyze Acme", task_type="brief"))
        self.assertTrue(response.accepted)
        self.assertFalse(response.external_provider_used)
        self.assertEqual(response.provider_mode, "deterministic_template")
        self.assertIn("Analyze Acme", response.generated_text)

    def test_build_provider_adapter_uses_deterministic_default(self):
        settings = load_product_settings({}).model
        adapter = build_provider_adapter(settings, {})
        self.assertIsInstance(adapter, DeterministicTemplateProviderAdapter)

    def test_external_boundary_rejects_when_disabled(self):
        adapter = ExternalProviderBoundaryAdapter(
            provider_mode="external_boundary",
            api_key_configured=True,
            allow_external_provider=False,
        )
        response = adapter.generate(ProviderRequest(prompt="hello"))
        self.assertFalse(response.accepted)
        self.assertFalse(response.external_provider_used)
        self.assertEqual(response.error_code, "external_provider_disabled")

    def test_external_boundary_requires_credential_when_enabled(self):
        adapter = ExternalProviderBoundaryAdapter(
            provider_mode="external_boundary",
            api_key_configured=False,
            allow_external_provider=True,
        )
        response = adapter.generate(ProviderRequest(prompt="hello"))
        self.assertFalse(response.accepted)
        self.assertEqual(response.error_code, "provider_credential_missing")

    def test_provider_summary_does_not_expose_credential(self):
        settings = load_product_settings(
            {
                "ORIS_INSIGHT_MODEL_PROVIDER": "external_boundary",
                "ORIS_INSIGHT_ALLOW_EXTERNAL_MODEL_PROVIDER": "true",
                "ORIS_INSIGHT_DEFAULT_MODEL": "boundary-model",
            }
        ).model
        summary = summarize_provider_adapter(settings, {"ORIS_INSIGHT_PROVIDER_API_KEY": "secret-value"})
        self.assertTrue(summary["credential_configured"])
        self.assertFalse(summary["credential_exposed"])
        self.assertFalse(summary["live_call_implemented"])
        self.assertEqual(summary["default_behavior"], "boundary_only_no_live_call")


if __name__ == "__main__":
    unittest.main()
