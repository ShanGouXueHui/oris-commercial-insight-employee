from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol

from app.runtime_orchestration import RuntimeV2RunRequest

MODULE_15_REMOTE_QUEUE_VERSION = "2026-06-24-module-15"
DISABLED_QUEUE_MODES = {"disabled", "off", "local_only"}
REMOTE_BOUNDARY_MODES = {"remote_boundary", "runtime_v2_boundary", "worker_queue_boundary"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RemoteRuntimeQueueSettings:
    mode: str = "disabled"
    endpoint_configured: bool = False
    credential_configured: bool = False
    dispatch_enabled: bool = False
    queue_name: str = "insight-runtime-v2"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RemoteRuntimeJob:
    job_id: str
    request: RuntimeV2RunRequest
    status: str
    created_at: str
    queue_name: str
    remote_dispatched: bool = False
    reason: str = "queued_locally_boundary_only"

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "request": self.request.to_dict(),
            "status": self.status,
            "created_at": self.created_at,
            "queue_name": self.queue_name,
            "remote_dispatched": self.remote_dispatched,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RemoteRuntimeQueueReadiness:
    ready: bool
    queue_version: str
    mode: str
    queue_name: str
    endpoint_configured: bool
    credential_configured: bool
    credential_exposed: bool
    dispatch_enabled: bool
    remote_dispatch_attempted: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class RemoteRuntimeQueueAdapter(Protocol):
    def readiness(self) -> RemoteRuntimeQueueReadiness:
        ...

    def enqueue(self, request: RuntimeV2RunRequest) -> RemoteRuntimeJob:
        ...

    def status(self, job_id: str) -> dict[str, object]:
        ...


class DisabledRemoteRuntimeQueueAdapter:
    def __init__(self, settings: RemoteRuntimeQueueSettings) -> None:
        self.settings = settings
        self.jobs: dict[str, RemoteRuntimeJob] = {}

    def readiness(self) -> RemoteRuntimeQueueReadiness:
        return RemoteRuntimeQueueReadiness(
            ready=True,
            queue_version=MODULE_15_REMOTE_QUEUE_VERSION,
            mode=self.settings.mode,
            queue_name=self.settings.queue_name,
            endpoint_configured=self.settings.endpoint_configured,
            credential_configured=self.settings.credential_configured,
            credential_exposed=False,
            dispatch_enabled=False,
            remote_dispatch_attempted=False,
            reason="remote_runtime_queue_disabled_local_runtime_active",
        )

    def enqueue(self, request: RuntimeV2RunRequest) -> RemoteRuntimeJob:
        job = RemoteRuntimeJob(
            job_id=build_remote_runtime_job_id(request, self.settings.queue_name),
            request=request,
            status="local_only_not_dispatched",
            created_at=_utc_now(),
            queue_name=self.settings.queue_name,
            remote_dispatched=False,
            reason="remote_queue_disabled",
        )
        self.jobs[job.job_id] = job
        return job

    def status(self, job_id: str) -> dict[str, object]:
        job = self.jobs.get(job_id)
        if job is None:
            return {"job_id": job_id, "status": "unknown", "remote_dispatched": False}
        return job.to_dict()


class BoundaryRemoteRuntimeQueueAdapter:
    def __init__(self, settings: RemoteRuntimeQueueSettings) -> None:
        self.settings = settings
        self.jobs: dict[str, RemoteRuntimeJob] = {}

    def readiness(self) -> RemoteRuntimeQueueReadiness:
        if not self.settings.endpoint_configured:
            ready = False
            reason = "remote_runtime_endpoint_missing"
        elif not self.settings.credential_configured:
            ready = False
            reason = "remote_runtime_credential_missing"
        elif self.settings.dispatch_enabled:
            ready = False
            reason = "remote_dispatch_not_implemented_in_module_15"
        else:
            ready = True
            reason = "remote_runtime_configured_but_dispatch_disabled"
        return RemoteRuntimeQueueReadiness(
            ready=ready,
            queue_version=MODULE_15_REMOTE_QUEUE_VERSION,
            mode=self.settings.mode,
            queue_name=self.settings.queue_name,
            endpoint_configured=self.settings.endpoint_configured,
            credential_configured=self.settings.credential_configured,
            credential_exposed=False,
            dispatch_enabled=self.settings.dispatch_enabled,
            remote_dispatch_attempted=False,
            reason=reason,
        )

    def enqueue(self, request: RuntimeV2RunRequest) -> RemoteRuntimeJob:
        readiness = self.readiness()
        status = "boundary_ready_not_dispatched" if readiness.ready else "blocked_by_boundary"
        job = RemoteRuntimeJob(
            job_id=build_remote_runtime_job_id(request, self.settings.queue_name),
            request=request,
            status=status,
            created_at=_utc_now(),
            queue_name=self.settings.queue_name,
            remote_dispatched=False,
            reason=readiness.reason,
        )
        self.jobs[job.job_id] = job
        return job

    def status(self, job_id: str) -> dict[str, object]:
        job = self.jobs.get(job_id)
        if job is None:
            return {"job_id": job_id, "status": "unknown", "remote_dispatched": False}
        return job.to_dict()


def _bool_from_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _credential_configured(env: Mapping[str, str]) -> bool:
    return bool(env.get("ORIS_RUNTIME_QUEUE_TOKEN") or env.get("ORIS_REMOTE_RUNTIME_TOKEN"))


def _endpoint_configured(env: Mapping[str, str]) -> bool:
    return bool(env.get("ORIS_RUNTIME_QUEUE_ENDPOINT") or env.get("ORIS_REMOTE_RUNTIME_ENDPOINT"))


def load_remote_runtime_queue_settings(env: Mapping[str, str] | None = None) -> RemoteRuntimeQueueSettings:
    values = os.environ if env is None else env
    return RemoteRuntimeQueueSettings(
        mode=values.get("ORIS_REMOTE_RUNTIME_QUEUE_MODE", "disabled"),
        endpoint_configured=_endpoint_configured(values),
        credential_configured=_credential_configured(values),
        dispatch_enabled=_bool_from_env(values.get("ORIS_REMOTE_RUNTIME_DISPATCH_ENABLED"), False),
        queue_name=values.get("ORIS_REMOTE_RUNTIME_QUEUE_NAME", "insight-runtime-v2"),
    )


def build_remote_runtime_queue_adapter(env: Mapping[str, str] | None = None) -> RemoteRuntimeQueueAdapter:
    settings = load_remote_runtime_queue_settings(env)
    mode = settings.mode.strip().lower()
    if mode in REMOTE_BOUNDARY_MODES:
        return BoundaryRemoteRuntimeQueueAdapter(settings)
    return DisabledRemoteRuntimeQueueAdapter(settings)


def build_remote_runtime_job_id(request: RuntimeV2RunRequest, queue_name: str) -> str:
    raw = "|".join([queue_name, request.company_name.strip().lower(), str(request.vertical), request.geography, request.time_horizon])
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"rrq-{digest}"


def summarize_remote_runtime_queue(env: Mapping[str, str] | None = None) -> dict[str, object]:
    adapter = build_remote_runtime_queue_adapter(env)
    readiness = adapter.readiness()
    return {
        "queue_version": MODULE_15_REMOTE_QUEUE_VERSION,
        "readiness": readiness.to_dict(),
        "default_behavior": "local_runtime_active_until_remote_dispatch_enabled",
        "credential_exposed": False,
        "remote_dispatch_attempted": False,
        "supported_modes": ["disabled", "remote_boundary"],
    }
