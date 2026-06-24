from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:8099"
MODULE = "Insight Rebuild Module 9"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _request_json(method: str, url: str, payload: dict[str, object] | None = None, timeout: float = 5.0) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def _wait_for_health(base_url: str, attempts: int = 30, delay_seconds: float = 0.5) -> tuple[bool, dict[str, Any]]:
    last_error: dict[str, Any] = {}
    for _ in range(attempts):
        try:
            status, payload = _request_json("GET", f"{base_url}/healthz")
            if status == 200 and payload.get("status") == "healthy":
                return True, payload
        except Exception as exc:  # pragma: no cover - useful smoke diagnostics
            last_error = {"error": type(exc).__name__, "message": str(exc)}
        time.sleep(delay_seconds)
    return False, last_error


def _sqlite_counts(db_path: str) -> dict[str, int]:
    path = Path(db_path)
    if not path.exists():
        return {"database_exists": 0, "runtime_runs": 0, "evidence_sources": 0, "evidence_items": 0}
    with sqlite3.connect(str(path)) as conn:
        return {
            "database_exists": 1,
            "runtime_runs": int(conn.execute("SELECT COUNT(*) FROM runtime_runs").fetchone()[0]),
            "evidence_sources": int(conn.execute("SELECT COUNT(*) FROM evidence_sources").fetchone()[0]),
            "evidence_items": int(conn.execute("SELECT COUNT(*) FROM evidence_items").fetchone()[0]),
        }


def run_smoke(base_url: str, db_path: str) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    ok, health_payload = _wait_for_health(base_url)
    checks.append({"check_id": "healthz", "passed": ok, "payload": health_payload})
    if not ok:
        return _result("failed", base_url, db_path, checks)

    try:
        status, details = _request_json("GET", f"{base_url}/healthz/details")
        checks.append({
            "check_id": "healthz_details",
            "passed": status == 200 and details.get("runtime_v2_backed_rebuild") is True and details.get("module_9_observability") is True,
            "payload": details,
        })
    except Exception as exc:
        checks.append({"check_id": "healthz_details", "passed": False, "error": type(exc).__name__, "message": str(exc)})

    try:
        status, observation = _request_json("GET", f"{base_url}/healthz/observability")
        checks.append({
            "check_id": "healthz_observability",
            "passed": status == 200 and observation.get("module_9_deployment_smoke_ready") is True,
            "payload": observation,
        })
    except Exception as exc:
        checks.append({"check_id": "healthz_observability", "passed": False, "error": type(exc).__name__, "message": str(exc)})

    try:
        status, acceptance = _request_json("GET", f"{base_url}/insights/rebuild/acceptance")
        checks.append({
            "check_id": "rebuild_acceptance",
            "passed": status == 200 and acceptance.get("module_9_deployment_smoke_ready") is True,
            "payload": acceptance,
        })
    except Exception as exc:
        checks.append({"check_id": "rebuild_acceptance", "passed": False, "error": type(exc).__name__, "message": str(exc)})

    try:
        status, brief = _request_json(
            "POST",
            f"{base_url}/insights/rebuild/brief",
            {"company_name": "Module9SmokeCo", "vertical": "technology", "use_sample_evidence": True},
        )
        checks.append({
            "check_id": "rebuild_brief_sqlite_persistence",
            "passed": status == 200
            and brief.get("accepted") is True
            and brief.get("evidence_persistence", {}).get("storage_mode") == "sqlite",
            "payload": brief,
        })
    except Exception as exc:
        checks.append({"check_id": "rebuild_brief_sqlite_persistence", "passed": False, "error": type(exc).__name__, "message": str(exc)})

    counts = _sqlite_counts(db_path)
    checks.append({
        "check_id": "sqlite_persistence_counts",
        "passed": counts["database_exists"] == 1 and counts["runtime_runs"] >= 1 and counts["evidence_items"] >= 1,
        "payload": counts,
    })
    return _result("passed" if all(bool(check.get("passed")) for check in checks) else "failed", base_url, db_path, checks)


def _result(status: str, base_url: str, db_path: str, checks: list[dict[str, object]]) -> dict[str, object]:
    return {
        "module": MODULE,
        "status": status,
        "generated_at": _utc_now(),
        "base_url": base_url,
        "sqlite_path": db_path,
        "checks": checks,
    }


def main() -> int:
    base_url = os.environ.get("ORIS_INSIGHT_SMOKE_BASE_URL", DEFAULT_BASE_URL)
    db_path = os.environ.get("ORIS_INSIGHT_EVIDENCE_LOCAL_PATH", "reports/evidence/runtime_runs/module9_smoke.sqlite3")
    result = run_smoke(base_url, db_path)
    Path("reports/testing").mkdir(parents=True, exist_ok=True)
    Path("reports/testing/insight_rebuild_module_9_smoke_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "base_url": base_url, "sqlite_path": db_path}, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
