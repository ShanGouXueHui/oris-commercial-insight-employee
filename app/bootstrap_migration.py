from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

MODULE_21_BOOTSTRAP_MIGRATION_VERSION = "2026-06-25-module-21"
EVIDENCE_HARNESS_IMPORT = "app.evidence_harness"


@dataclass(frozen=True)
class BootstrapScriptMigrationStatus:
    path: str
    exists: bool
    uses_evidence_harness: bool
    module_number: int | None
    migration_required: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BootstrapMigrationPlan:
    migration_version: str
    scanned_count: int
    migrated_count: int
    pending_count: int
    migrated_paths: tuple[str, ...]
    pending_paths: tuple[str, ...]
    selected_for_module_21: tuple[str, ...]
    package_installation_enabled: bool = False
    remote_code_fetch_enabled: bool = False
    production_execution_changed: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _module_number_from_path(path: str) -> int | None:
    marker = "bootstrap_insight_rebuild_module_"
    name = Path(path).name
    if marker not in name:
        return None
    suffix = name.split(marker, 1)[1].split(".", 1)[0]
    try:
        return int(suffix)
    except ValueError:
        return None


def inspect_bootstrap_script(path: str) -> BootstrapScriptMigrationStatus:
    script_path = Path(path)
    exists = script_path.exists()
    content = script_path.read_text(encoding="utf-8") if exists else ""
    uses_harness = EVIDENCE_HARNESS_IMPORT in content
    module_number = _module_number_from_path(path) if exists else None
    return BootstrapScriptMigrationStatus(
        path=path,
        exists=exists,
        uses_evidence_harness=uses_harness,
        module_number=module_number,
        migration_required=exists and not uses_harness,
    )


def inspect_bootstrap_scripts(paths: Iterable[str]) -> list[BootstrapScriptMigrationStatus]:
    return [inspect_bootstrap_script(path) for path in paths]


def default_bootstrap_script_paths() -> tuple[str, ...]:
    return tuple(str(path) for path in sorted(Path("scripts").glob("bootstrap_insight_rebuild_module_*.sh")))


def build_bootstrap_migration_plan(paths: Iterable[str] | None = None) -> BootstrapMigrationPlan:
    active_paths = tuple(paths or default_bootstrap_script_paths())
    statuses = inspect_bootstrap_scripts(active_paths)
    migrated = tuple(status.path for status in statuses if status.uses_evidence_harness)
    pending = tuple(status.path for status in statuses if status.migration_required)
    selected = tuple(path for path in migrated if path.endswith("bootstrap_insight_rebuild_module_19.sh"))
    return BootstrapMigrationPlan(
        migration_version=MODULE_21_BOOTSTRAP_MIGRATION_VERSION,
        scanned_count=len(statuses),
        migrated_count=len(migrated),
        pending_count=len(pending),
        migrated_paths=migrated,
        pending_paths=pending,
        selected_for_module_21=selected,
        package_installation_enabled=False,
        remote_code_fetch_enabled=False,
        production_execution_changed=False,
    )


def summarize_bootstrap_migration(paths: Iterable[str] | None = None) -> dict[str, object]:
    plan = build_bootstrap_migration_plan(paths)
    return {
        "bootstrap_migration_version": MODULE_21_BOOTSTRAP_MIGRATION_VERSION,
        "scanned_count": plan.scanned_count,
        "migrated_count": plan.migrated_count,
        "pending_count": plan.pending_count,
        "selected_for_module_21": list(plan.selected_for_module_21),
        "package_installation_enabled": plan.package_installation_enabled,
        "remote_code_fetch_enabled": plan.remote_code_fetch_enabled,
        "production_execution_changed": plan.production_execution_changed,
    }
