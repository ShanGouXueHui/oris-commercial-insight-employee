from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Mapping

PRODUCT_API_VERSION = "0.2.0"
RUNTIME_V2_FINAL_REFERENCE = "896bdc67942a27cea98b8a4eb8f49d946795a741"


def _bool_from_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ApiSettings:
    version: str = PRODUCT_API_VERSION
    service_name: str = "ORIS Commercial Insight Employee API"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeSettings:
    adapter_mode: str = "local_runtime_v2_contract"
    runtime_v2_reference: str = RUNTIME_V2_FINAL_REFERENCE
    evidence_mode: str = "github_report_aligned"
    approval_required_for_external_side_effects: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SourceSettings:
    connector_mode: str = "deterministic_local"
    allow_network_sources: bool = False
    deterministic_fixture_version: str = "2026-06-23-module-7"
    query_limit: int = 3

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ModelProviderSettings:
    provider_mode: str = "deterministic_template"
    allow_external_provider: bool = False
    default_model: str = "none"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class EvidencePersistenceSettings:
    storage_mode: str = "in_memory"
    local_path: str = "reports/evidence/runtime_runs"
    persist_full_claim_text: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ProductSettings:
    api: ApiSettings
    runtime: RuntimeSettings
    source: SourceSettings
    model: ModelProviderSettings
    evidence_persistence: EvidencePersistenceSettings

    def to_dict(self) -> dict[str, object]:
        return {
            "api": self.api.to_dict(),
            "runtime": self.runtime.to_dict(),
            "source": self.source.to_dict(),
            "model": self.model.to_dict(),
            "evidence_persistence": self.evidence_persistence.to_dict(),
        }


def load_product_settings(env: Mapping[str, str] | None = None) -> ProductSettings:
    values = os.environ if env is None else env
    return ProductSettings(
        api=ApiSettings(
            version=values.get("ORIS_INSIGHT_API_VERSION", PRODUCT_API_VERSION),
            service_name=values.get("ORIS_INSIGHT_SERVICE_NAME", "ORIS Commercial Insight Employee API"),
        ),
        runtime=RuntimeSettings(
            adapter_mode=values.get("ORIS_INSIGHT_RUNTIME_ADAPTER", "local_runtime_v2_contract"),
            runtime_v2_reference=values.get("ORIS_RUNTIME_V2_REFERENCE", RUNTIME_V2_FINAL_REFERENCE),
            evidence_mode=values.get("ORIS_INSIGHT_RUNTIME_EVIDENCE_MODE", "github_report_aligned"),
            approval_required_for_external_side_effects=_bool_from_env(
                values.get("ORIS_INSIGHT_APPROVAL_REQUIRED_FOR_EXTERNAL_SIDE_EFFECTS"), True
            ),
        ),
        source=SourceSettings(
            connector_mode=values.get("ORIS_INSIGHT_SOURCE_CONNECTOR", "deterministic_local"),
            allow_network_sources=_bool_from_env(values.get("ORIS_INSIGHT_ALLOW_NETWORK_SOURCES"), False),
            deterministic_fixture_version=values.get(
                "ORIS_INSIGHT_DETERMINISTIC_FIXTURE_VERSION", "2026-06-23-module-7"
            ),
            query_limit=int(values.get("ORIS_INSIGHT_SOURCE_QUERY_LIMIT", "3")),
        ),
        model=ModelProviderSettings(
            provider_mode=values.get("ORIS_INSIGHT_MODEL_PROVIDER", "deterministic_template"),
            allow_external_provider=_bool_from_env(values.get("ORIS_INSIGHT_ALLOW_EXTERNAL_MODEL_PROVIDER"), False),
            default_model=values.get("ORIS_INSIGHT_DEFAULT_MODEL", "none"),
        ),
        evidence_persistence=EvidencePersistenceSettings(
            storage_mode=values.get("ORIS_INSIGHT_EVIDENCE_STORAGE", "in_memory"),
            local_path=values.get("ORIS_INSIGHT_EVIDENCE_LOCAL_PATH", "reports/evidence/runtime_runs"),
            persist_full_claim_text=_bool_from_env(values.get("ORIS_INSIGHT_PERSIST_FULL_CLAIM_TEXT"), True),
        ),
    )
