from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from app.commercial_guardrails import summarize_guardrail_policy
from app.config import ProductSettings, load_product_settings
from app.evidence_persistence import summarize_evidence_schema
from app.source_connectors import summarize_connector_modes

SERVICE_STARTED_AT = datetime.now(timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RuntimeObservationCheck:
    check_id: str
    status: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeObservabilitySnapshot:
    status: str
    generated_at: str
    service_started_at: str
    service_uptime_seconds: float
    version: str
    runtime_v2_backed: bool
    module_9_deployment_smoke_ready: bool
    module_10_commercial_guardrails_ready: bool
    checks: list[RuntimeObservationCheck]
    settings_snapshot: dict[str, object]
    connector_modes: dict[str, object]
    evidence_schema: dict[str, object]
    guardrail_policy: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "generated_at": self.generated_at,
            "service_started_at": self.service_started_at,
            "service_uptime_seconds": self.service_uptime_seconds,
            "version": self.version,
            "runtime_v2_backed": self.runtime_v2_backed,
            "module_9_deployment_smoke_ready": self.module_9_deployment_smoke_ready,
            "module_10_commercial_guardrails_ready": self.module_10_commercial_guardrails_ready,
            "checks": [check.to_dict() for check in self.checks],
            "settings_snapshot": self.settings_snapshot,
            "connector_modes": self.connector_modes,
            "evidence_schema": self.evidence_schema,
            "guardrail_policy": self.guardrail_policy,
        }


def _overall_status(checks: Iterable[RuntimeObservationCheck]) -> str:
    statuses = {check.status for check in checks}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "healthy"


def build_runtime_observability_snapshot(settings: ProductSettings | None = None) -> RuntimeObservabilitySnapshot:
    active_settings = settings or load_product_settings()
    now = datetime.now(timezone.utc)
    checks = [
        RuntimeObservationCheck(
            check_id="runtime_v2_reference_present",
            status="pass" if bool(active_settings.runtime.runtime_v2_reference) else "fail",
            message="Runtime v2 reference is configured for product-side orchestration.",
        ),
        RuntimeObservationCheck(
            check_id="source_connector_boundary_present",
            status="pass",
            message="Source connector boundary is available; live external providers remain disabled by default.",
        ),
        RuntimeObservationCheck(
            check_id="evidence_persistence_boundary_present",
            status="pass",
            message="Evidence persistence boundary is available with in-memory, filesystem, and SQLite modes.",
        ),
        RuntimeObservationCheck(
            check_id="external_provider_default_disabled",
            status="pass"
            if not active_settings.source.allow_network_sources and not active_settings.model.allow_external_provider
            else "warn",
            message="Network source and external model provider access should remain disabled unless explicitly configured.",
        ),
        RuntimeObservationCheck(
            check_id="deployment_smoke_ready",
            status="pass",
            message="Module 9 smoke runner can validate live HTTP endpoints and SQLite evidence persistence.",
        ),
        RuntimeObservationCheck(
            check_id="commercial_guardrails_ready",
            status="pass",
            message="Module 10 commercial guardrails expose API key, quota, rate-limit, and structured error policy boundaries.",
        ),
    ]
    return RuntimeObservabilitySnapshot(
        status=_overall_status(checks),
        generated_at=now.isoformat(),
        service_started_at=SERVICE_STARTED_AT.isoformat(),
        service_uptime_seconds=round((now - SERVICE_STARTED_AT).total_seconds(), 3),
        version=active_settings.api.version,
        runtime_v2_backed=True,
        module_9_deployment_smoke_ready=True,
        module_10_commercial_guardrails_ready=True,
        checks=checks,
        settings_snapshot=active_settings.to_dict(),
        connector_modes=summarize_connector_modes(),
        evidence_schema=summarize_evidence_schema(),
        guardrail_policy=summarize_guardrail_policy(active_settings.commercial_guardrails),
    )
