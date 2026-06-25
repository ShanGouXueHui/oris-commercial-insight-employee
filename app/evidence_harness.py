from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

MODULE_20_EVIDENCE_HARNESS_VERSION = "2026-06-25-module-20"
SENSITIVE_KEY_PARTS = ("secret", "token", "password", "api_key", "credential", "dsn", "database_url")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EvidenceHarnessConfig:
    module_name: str
    bootstrap_version: str
    expected_unit_test_count: int
    result_filename: str
    report_filename: str
    implemented_boundaries: tuple[str, ...]
    evidence_files: tuple[str, ...]
    next_module: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TestRunSnapshot:
    test_command: str
    test_exit_code: int
    product_base_sha: str
    log_file: str
    generated_at: str = ""

    @property
    def status(self) -> str:
        return "passed" if self.test_exit_code == 0 else "failed"

    def to_dict(self) -> dict[str, object]:
        return {
            "test_command": self.test_command,
            "test_exit_code": self.test_exit_code,
            "status": self.status,
            "product_base_sha": self.product_base_sha,
            "log_file": self.log_file,
            "generated_at": self.generated_at or _utc_now(),
        }


def _is_sensitive_key(key: object) -> bool:
    lowered = str(key).lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def redact_sensitive_values(value: object) -> object:
    if isinstance(value, Mapping):
        output: dict[str, object] = {}
        for key, item in value.items():
            if _is_sensitive_key(key):
                output[str(key)] = "<redacted>"
            else:
                output[str(key)] = redact_sensitive_values(item)
        return output
    if isinstance(value, list):
        return [redact_sensitive_values(item) for item in value]
    if isinstance(value, tuple):
        return [redact_sensitive_values(item) for item in value]
    return value


def build_latest_test_result_payload(
    config: EvidenceHarnessConfig,
    snapshot: TestRunSnapshot,
    flags: Mapping[str, object] | None = None,
    checks: Sequence[str] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "module": config.module_name,
        "bootstrap_version": config.bootstrap_version,
        "status": snapshot.status,
        "generated_at": snapshot.generated_at or _utc_now(),
        "test_command": snapshot.test_command,
        "test_exit_code": snapshot.test_exit_code,
        "product_base_sha": snapshot.product_base_sha,
        "evidence_harness_version": MODULE_20_EVIDENCE_HARNESS_VERSION,
        "expected_unit_test_count": config.expected_unit_test_count,
        "log_file": snapshot.log_file,
        "checks": list(checks or ()),
    }
    if flags:
        payload.update(redact_sensitive_values(dict(flags)))
    return payload


def render_execution_report(
    config: EvidenceHarnessConfig,
    snapshot: TestRunSnapshot,
    evidence_commit_sha: str | None = None,
) -> str:
    boundaries = "\n".join(f"- {item}" for item in config.implemented_boundaries)
    evidence_files = "\n".join(f"- {item}" for item in config.evidence_files)
    commit_value = evidence_commit_sha or "Pending until evidence commit completes."
    return f"""# {config.module_name} Execution Report

## Module

{config.module_name}

## Bootstrap Version

{config.bootstrap_version}

## Product Base Commit

{snapshot.product_base_sha}

## Test Command

{snapshot.test_command}

## Test Result

- test exit code: {snapshot.test_exit_code}
- status: {snapshot.status}
- expected unit test count: {config.expected_unit_test_count}

## Implemented Boundaries

{boundaries}

## Evidence Files

{evidence_files}

## Evidence Commit SHA

{commit_value}

## Next Module

{config.next_module}
"""


def write_harness_evidence(
    config: EvidenceHarnessConfig,
    snapshot: TestRunSnapshot,
    flags: Mapping[str, object] | None = None,
    checks: Sequence[str] | None = None,
    testing_dir: str = "reports/testing",
    execution_dir: str = "reports/execution",
) -> dict[str, object]:
    payload = build_latest_test_result_payload(config, snapshot, flags=flags, checks=checks)
    testing_path = Path(testing_dir)
    execution_path = Path(execution_dir)
    testing_path.mkdir(parents=True, exist_ok=True)
    execution_path.mkdir(parents=True, exist_ok=True)
    (testing_path / config.result_filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (testing_path / "latest_test_result.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (execution_path / config.report_filename).write_text(render_execution_report(config, snapshot), encoding="utf-8")
    return payload


def record_evidence_commit_sha(report_path: str, evidence_commit_sha: str) -> None:
    path = Path(report_path)
    text = path.read_text(encoding="utf-8").replace("Pending until evidence commit completes.", evidence_commit_sha)
    path.write_text(text, encoding="utf-8")


def summarize_evidence_harness_upgrade() -> dict[str, object]:
    return {
        "evidence_harness_version": MODULE_20_EVIDENCE_HARNESS_VERSION,
        "latest_result_writer": True,
        "execution_report_renderer": True,
        "sensitive_value_redaction": True,
        "evidence_commit_recorder": True,
        "reusable_bootstrap_helper": True,
        "live_external_action_enabled": False,
    }
