from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol

from app.config import ModelProviderSettings

MODULE_12_PROVIDER_ADAPTER_VERSION = "2026-06-24-module-12"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProviderRequest:
    prompt: str
    task_type: str = "commercial_insight"
    max_tokens: int = 512

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderResponse:
    accepted: bool
    provider_mode: str
    adapter_version: str
    generated_text: str
    external_provider_used: bool
    error_code: str | None = None
    generated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "provider_mode": self.provider_mode,
            "adapter_version": self.adapter_version,
            "generated_text": self.generated_text,
            "external_provider_used": self.external_provider_used,
            "error_code": self.error_code,
            "generated_at": self.generated_at or _utc_now(),
        }


class ProviderAdapter(Protocol):
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        ...


class DeterministicTemplateProviderAdapter:
    provider_mode = "deterministic_template"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        prompt = request.prompt.strip() or "empty prompt"
        return ProviderResponse(
            accepted=True,
            provider_mode=self.provider_mode,
            adapter_version=MODULE_12_PROVIDER_ADAPTER_VERSION,
            generated_text=f"Deterministic provider response for {request.task_type}: {prompt[:160]}",
            external_provider_used=False,
            generated_at=_utc_now(),
        )


class ExternalProviderBoundaryAdapter:
    def __init__(self, provider_mode: str, api_key_configured: bool, allow_external_provider: bool) -> None:
        self.provider_mode = provider_mode
        self.api_key_configured = api_key_configured
        self.allow_external_provider = allow_external_provider

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        if not self.allow_external_provider:
            return ProviderResponse(
                accepted=False,
                provider_mode=self.provider_mode,
                adapter_version=MODULE_12_PROVIDER_ADAPTER_VERSION,
                generated_text="",
                external_provider_used=False,
                error_code="external_provider_disabled",
                generated_at=_utc_now(),
            )
        if not self.api_key_configured:
            return ProviderResponse(
                accepted=False,
                provider_mode=self.provider_mode,
                adapter_version=MODULE_12_PROVIDER_ADAPTER_VERSION,
                generated_text="",
                external_provider_used=False,
                error_code="provider_credential_missing",
                generated_at=_utc_now(),
            )
        return ProviderResponse(
            accepted=False,
            provider_mode=self.provider_mode,
            adapter_version=MODULE_12_PROVIDER_ADAPTER_VERSION,
            generated_text="",
            external_provider_used=False,
            error_code="live_provider_call_not_implemented",
            generated_at=_utc_now(),
        )


def _provider_key_configured(env: Mapping[str, str]) -> bool:
    return bool(env.get("ORIS_INSIGHT_PROVIDER_API_KEY") or env.get("ORIS_INSIGHT_MODEL_API_KEY"))


def build_provider_adapter(settings: ModelProviderSettings, env: Mapping[str, str] | None = None) -> ProviderAdapter:
    values = os.environ if env is None else env
    mode = settings.provider_mode.strip().lower()
    if mode in {"deterministic_template", "template", "none"}:
        return DeterministicTemplateProviderAdapter()
    return ExternalProviderBoundaryAdapter(
        provider_mode=settings.provider_mode,
        api_key_configured=_provider_key_configured(values),
        allow_external_provider=settings.allow_external_provider,
    )


def summarize_provider_adapter(settings: ModelProviderSettings, env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    mode = settings.provider_mode.strip().lower()
    external_mode_requested = mode not in {"deterministic_template", "template", "none"}
    return {
        "adapter_version": MODULE_12_PROVIDER_ADAPTER_VERSION,
        "provider_mode": settings.provider_mode,
        "default_model": settings.default_model,
        "allow_external_provider": settings.allow_external_provider,
        "external_mode_requested": external_mode_requested,
        "credential_configured": _provider_key_configured(values),
        "credential_exposed": False,
        "live_call_implemented": False,
        "default_behavior": "deterministic_local" if not external_mode_requested else "boundary_only_no_live_call",
        "supported_modes": ["deterministic_template", "external_boundary"],
    }
