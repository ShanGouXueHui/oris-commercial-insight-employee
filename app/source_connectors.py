from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Protocol

from app.config import SourceSettings
from app.domain_contracts import AnalyticalLens, EvidenceSourceType, InsightVertical, REQUIRED_BRIEF_LENSES
from app.evidence_ingestion import RawEvidenceDocument


def _vertical_value(value: InsightVertical | str) -> str:
    return value.value if isinstance(value, InsightVertical) else str(value)


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "subject"


@dataclass(frozen=True)
class SourceQuery:
    company_name: str
    vertical: InsightVertical | str = InsightVertical.GENERAL
    geography: str = "global"
    time_horizon: str = "12_months"
    required_lenses: tuple[AnalyticalLens, ...] = tuple(REQUIRED_BRIEF_LENSES)

    def to_dict(self) -> dict[str, object]:
        return {
            "company_name": self.company_name,
            "vertical": _vertical_value(self.vertical),
            "geography": self.geography,
            "time_horizon": self.time_horizon,
            "required_lenses": [lens.value for lens in self.required_lenses],
        }


@dataclass(frozen=True)
class SourceConnectorMetadata:
    connector_id: str
    connector_mode: str
    fixture_version: str
    network_access_used: bool
    external_provider_used: bool
    provider_boundary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SourceConnectorResult:
    query: SourceQuery
    documents: list[RawEvidenceDocument]
    metadata: SourceConnectorMetadata

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query.to_dict(),
            "document_count": len(self.documents),
            "document_ids": [document.document_id for document in self.documents],
            "metadata": self.metadata.to_dict(),
        }


class EvidenceSourceConnector(Protocol):
    def fetch(self, query: SourceQuery) -> SourceConnectorResult:
        """Return normalized raw evidence documents for a subject query."""


class ExternalEvidenceProviderNotConfigured(RuntimeError):
    pass


class DeterministicLocalSourceConnector:
    """Dependency-free source connector used for tests and offline runtime acceptance."""

    def __init__(self, settings: SourceSettings | None = None) -> None:
        self.settings = settings or SourceSettings()

    def fetch(self, query: SourceQuery) -> SourceConnectorResult:
        subject_slug = _slug(query.company_name)
        vertical = _vertical_value(query.vertical)
        documents = [
            RawEvidenceDocument(
                document_id=f"{subject_slug}_module7_company_packet",
                source_id="module7_local_company_disclosure",
                source_type=EvidenceSourceType.COMPANY_DISCLOSURE,
                title=f"Deterministic company packet for {query.company_name}",
                content=f"Offline fixture covering company-level signals for {query.company_name}.",
                credibility_score=0.92,
                claims_by_lens={
                    AnalyticalLens.COMPANY_PROFILE: f"{query.company_name} has a defined commercial profile in {vertical}.",
                    AnalyticalLens.PRODUCT_CAPABILITY: f"{query.company_name} product capability can be evaluated through roadmap, adoption, and delivery evidence.",
                    AnalyticalLens.STRATEGY_SIGNALS: f"{query.company_name} strategy signals are tracked through repeatable commercial evidence lenses.",
                },
            ),
            RawEvidenceDocument(
                document_id=f"{subject_slug}_module7_market_packet",
                source_id="module7_local_market_data",
                source_type=EvidenceSourceType.MARKET_DATA,
                title=f"Deterministic market packet for {vertical}",
                content=f"Offline fixture covering market and competitive signals for {vertical}.",
                credibility_score=0.88,
                claims_by_lens={
                    AnalyticalLens.MARKET_STRUCTURE: f"The {vertical} market can be analyzed through segment, channel, and demand structure.",
                    AnalyticalLens.COMPETITOR_LANDSCAPE: f"{query.company_name} competitors should be compared by capability, monetization, and go-to-market reach.",
                    AnalyticalLens.FINANCIAL_QUALITY: f"Financial quality should be assessed through growth, margin, cash conversion, and funding durability.",
                },
            ),
            RawEvidenceDocument(
                document_id=f"{subject_slug}_module7_risk_packet",
                source_id="module7_local_risk_model",
                source_type=EvidenceSourceType.PUBLIC_WEB,
                title=f"Deterministic risk and scenario packet for {query.company_name}",
                content=f"Offline fixture covering risks, scenarios, and limitations for {query.company_name}.",
                credibility_score=0.86,
                claims_by_lens={
                    AnalyticalLens.RISKS: "Commercial insight quality is exposed to source recency, source credibility, and missing real-world data risk.",
                    AnalyticalLens.SCENARIOS: "Base, upside, and downside cases must remain tied to explicit evidence coverage.",
                    AnalyticalLens.LIMITATIONS: "This Module 7 connector uses deterministic local evidence and does not perform live web, search, model, or database access.",
                },
            ),
        ]
        return SourceConnectorResult(
            query=query,
            documents=documents[: max(1, self.settings.query_limit)],
            metadata=SourceConnectorMetadata(
                connector_id="deterministic_local_source_connector",
                connector_mode=self.settings.connector_mode,
                fixture_version=self.settings.deterministic_fixture_version,
                network_access_used=False,
                external_provider_used=False,
                provider_boundary="future_web_search_model_provider_not_enabled",
            ),
        )


class FutureExternalSourceConnectorBoundary:
    """Boundary marker for future web/search/provider connectors; intentionally not executable in Module 7."""

    def __init__(self, settings: SourceSettings) -> None:
        self.settings = settings

    def fetch(self, query: SourceQuery) -> SourceConnectorResult:
        raise ExternalEvidenceProviderNotConfigured(
            "external_evidence_provider_not_configured; use deterministic_local until provider settings are explicitly enabled"
        )


def build_source_connector(settings: SourceSettings) -> EvidenceSourceConnector:
    if settings.connector_mode == "deterministic_local":
        return DeterministicLocalSourceConnector(settings)
    return FutureExternalSourceConnectorBoundary(settings)


def summarize_connector_modes(connectors: Iterable[str] | None = None) -> dict[str, object]:
    modes = list(connectors or ["deterministic_local", "future_external_web_search", "future_external_model_provider"])
    return {
        "active_mode": "deterministic_local",
        "available_modes": modes,
        "network_access_default": False,
        "external_provider_default": False,
    }
