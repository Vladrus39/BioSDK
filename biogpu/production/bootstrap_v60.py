"""Production environment bootstrap v6.0."""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from biogpu.production.config_v60 import ProductionConfig


@dataclass
class BootstrapResult:
    success: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    created_paths: list[str] = field(default_factory=list)


class ProductionBootstrap:
    """Bootstraps production environment for BiC OS / BioCompute Runtime."""

    def __init__(self, config: ProductionConfig, project_root: str | Path = "."):
        self.config = config
        self.root = Path(project_root)

    def run(self) -> BootstrapResult:
        result = BootstrapResult(success=True)
        self._check_python(result)
        self._create_directories(result)
        self._init_tenant_db(result)
        self._init_incident_db(result)
        self._init_beta_db(result)
        self._init_storage(result)
        self._create_default_config(result)
        self._check_dependencies(result)
        result.success = len(result.errors) == 0
        return result

    def _check_python(self, result: BootstrapResult) -> None:
        import sys
        py_ok = sys.version_info >= (3, 11)
        result.checks.append({
            "check": "python_version",
            "passed": py_ok,
            "detail": f"Python {sys.version}",
        })
        if not py_ok:
            result.errors.append("Python >= 3.11 required")

    def _create_directories(self, result: BootstrapResult) -> None:
        dirs = [
            "data/production", "data/production/logs",
            "data/production/storage", "data/production/keys",
            "data/production/registry/packages", "configs",
        ]
        for d in dirs:
            p = self.root / d
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                result.created_paths.append(str(p))
        result.checks.append({
            "check": "directories", "passed": True,
            "detail": f"Created {len(result.created_paths)} new directories",
        })

    def _init_tenant_db(self, result: BootstrapResult) -> None:
        db_path = self.root / self.config.tenant_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE IF NOT EXISTS tenants (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, quota_jobs INTEGER DEFAULT 100, quota_storage_mb INTEGER DEFAULT 1024, api_key_hash TEXT, created_at TEXT DEFAULT (datetime('now')), active INTEGER DEFAULT 1)")
            conn.execute("CREATE TABLE IF NOT EXISTS tenant_memberships (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL, user_email TEXT NOT NULL, role TEXT DEFAULT 'viewer', created_at TEXT DEFAULT (datetime('now')), FOREIGN KEY (tenant_id) REFERENCES tenants(id))")
            conn.commit()
            conn.close()
            result.checks.append({"check": "tenant_db", "passed": True, "detail": str(db_path)})
        except Exception as exc:
            result.errors.append(f"tenant_db: {exc}")
            result.checks.append({"check": "tenant_db", "passed": False, "detail": str(exc)})

    def _init_incident_db(self, result: BootstrapResult) -> None:
        db_path = self.root / self.config.incident_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, severity TEXT DEFAULT 'low', status TEXT DEFAULT 'open', title TEXT NOT NULL, description TEXT, tenant_id TEXT, operator_id TEXT, created_at TEXT DEFAULT (datetime('now')), resolved_at TEXT, ledger_hash TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS incident_ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, incident_id TEXT NOT NULL, entry_type TEXT NOT NULL, entry_data TEXT, previous_hash TEXT, entry_hash TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')), FOREIGN KEY (incident_id) REFERENCES incidents(id))")
            conn.commit()
            conn.close()
            result.checks.append({"check": "incident_db", "passed": True, "detail": str(db_path)})
        except Exception as exc:
            result.errors.append(f"incident_db: {exc}")
            result.checks.append({"check": "incident_db", "passed": False, "detail": str(exc)})

    def _init_beta_db(self, result: BootstrapResult) -> None:
        db_path = self.root / self.config.beta_participant_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE IF NOT EXISTS beta_participants (id TEXT PRIMARY KEY, email TEXT NOT NULL, organization TEXT, approved INTEGER DEFAULT 0, onboarding_date TEXT, access_token_hash TEXT, active INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')))")
            conn.execute("CREATE TABLE IF NOT EXISTS beta_acceptance_records (id INTEGER PRIMARY KEY AUTOINCREMENT, participant_id TEXT NOT NULL, domain TEXT NOT NULL, accepted INTEGER DEFAULT 0, evidence_hash TEXT, signed_at TEXT, FOREIGN KEY (participant_id) REFERENCES beta_participants(id))")
            conn.commit()
            conn.close()
            result.checks.append({"check": "beta_db", "passed": True, "detail": str(db_path)})
        except Exception as exc:
            result.errors.append(f"beta_db: {exc}")
            result.checks.append({"check": "beta_db", "passed": False, "detail": str(exc)})

    def _init_storage(self, result: BootstrapResult) -> None:
        storage_root = self.root / self.config.storage_local_root
        storage_root.mkdir(parents=True, exist_ok=True)
        (storage_root / "objects").mkdir(exist_ok=True)
        (storage_root / "manifests").mkdir(exist_ok=True)
        result.checks.append({"check": "storage", "passed": True, "detail": str(storage_root)})

    def _create_default_config(self, result: BootstrapResult) -> None:
        config_path = self.root / "configs" / "production_config_v60.json"
        if not config_path.exists():
            self.config.to_json(config_path)
        result.checks.append({"check": "default_config", "passed": True, "detail": str(config_path)})

    def _check_dependencies(self, result: BootstrapResult) -> None:
        deps = ["numpy", "scipy", "sklearn", "pydantic", "yaml", "h5py", "fastapi", "uvicorn"]
        for dep in deps:
            try:
                __import__(dep)
                result.checks.append({"check": f"dep_{dep}", "passed": True, "detail": "imported"})
            except ImportError:
                result.errors.append(f"Missing dependency: {dep}")
                result.checks.append({"check": f"dep_{dep}", "passed": False, "detail": "not found"})


def bootstrap_production(
    config: ProductionConfig | None = None,
    project_root: str | Path = ".",
) -> BootstrapResult:
    if config is None:
        config = ProductionConfig()
    bootstrap = ProductionBootstrap(config, project_root)
    return bootstrap.run()
