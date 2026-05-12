"""Build v6.0 remaining files: benchmark, tests, scripts, docs, examples."""
import os, sys

BASE = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap"
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 4. Benchmark runner
# ============================================================
with open(os.path.join(BASE, "biogpu", "benchmarks", "biogpu_v60_production_foundation.py"), "w", encoding="utf-8") as f:
    f.write('''"""BioGPU-Core v6.0 Production Foundation benchmark runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.production.foundation_v60 import (
    DEFAULT_OUT,
    build_production_foundation,
    write_production_foundation_outputs,
)


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_production_foundation(root)
    paths = write_production_foundation_outputs(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v60_production_foundation bootstrap_success={audit['bootstrap_success']}")
    print(f"open_gap_count={audit['open_gap_count']}")
    print(f"production_ready_domain_count={audit['production_ready_domain_count']}")
    print(f"production_ready={audit['production_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="BioGPU-Core v6.0 Production Foundation")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
''')
print("benchmark runner OK")

# ============================================================
# 5. PowerShell runner
# ============================================================
with open(os.path.join(BASE, "scripts", "run_biogpu_v60_production_foundation.ps1"), "w", encoding="utf-8") as f:
    f.write('''param(
    [string]$Python = "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v60_production_foundation"
)

Write-Host "BioGPU-Core v6.0 Production Foundation"
Write-Host "========================================="

$runner = "biogpu/benchmarks/biogpu_v60_production_foundation.py"

if (-not (Test-Path $runner)) {
    Write-Error "Runner not found: $runner"
    exit 1
}

& $Python -m pytest tests/current/test_biogpu_v60_production_foundation.py -q --tb=short 2>&1
$testExit = $LASTEXITCODE

& $Python $runner --root $Root --out-dir $OutDir
$runExit = $LASTEXITCODE

Write-Host ""
Write-Host "Test exit: $testExit"
Write-Host "Run exit: $runExit"

if ($testExit -ne 0 -or $runExit -ne 0) {
    Write-Host "V60 GATE FAILED" -ForegroundColor Red
    exit 1
}
Write-Host "V60 GATE PASSED" -ForegroundColor Green
exit 0
''')
print("PowerShell runner OK")

# ============================================================
# 6. Tests
# ============================================================
with open(os.path.join(BASE, "tests", "current", "test_biogpu_v60_production_foundation.py"), "w", encoding="utf-8") as f:
    f.write('''"""Tests for v6.0 Production Foundation."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from biogpu.production.config_v60 import ProductionConfig, load_production_config
from biogpu.production.bootstrap_v60 import ProductionBootstrap, bootstrap_production
from biogpu.production.foundation_v60 import (
    build_production_foundation,
    write_production_foundation_outputs,
    DomainReadiness,
)


class TestProductionConfig:
    def test_default_config(self):
        config = ProductionConfig()
        assert config.config_version == "v6.0"
        assert config.environment == "development"
        assert config.worker_pool_size == 4
        assert len(config.identity_admin_users) >= 1

    def test_config_validation_errors(self):
        config = ProductionConfig(environment="production", identity_jwt_secret="")
        errors = config.validate()
        assert len(errors) >= 1
        assert any("jwt_secret" in e.lower() for e in errors)

    def test_config_validation_passes(self):
        config = ProductionConfig(environment="development")
        errors = config.validate()
        assert len(errors) == 0

    def test_from_env(self):
        import os
        os.environ["BICOS_WORKER_POOL_SIZE"] = "8"
        config = ProductionConfig.from_env()
        assert config.worker_pool_size == 8

    def test_to_dict_roundtrip(self):
        config = ProductionConfig()
        d = config.to_dict()
        assert d["config_version"] == "v6.0"
        assert d["environment"] == "development"


class TestProductionBootstrap:
    def test_bootstrap_success(self, tmp_path):
        config = ProductionConfig()
        result = bootstrap_production(config, tmp_path)
        assert result.success
        assert len(result.errors) == 0

    def test_bootstrap_creates_tenant_db(self, tmp_path):
        config = ProductionConfig()
        result = bootstrap_production(config, tmp_path)
        db_path = tmp_path / config.tenant_db_path
        assert db_path.exists()

    def test_bootstrap_creates_incident_db(self, tmp_path):
        config = ProductionConfig()
        result = bootstrap_production(config, tmp_path)
        db_path = tmp_path / config.incident_db_path
        assert db_path.exists()

    def test_bootstrap_creates_storage(self, tmp_path):
        config = ProductionConfig()
        result = bootstrap_production(config, tmp_path)
        storage = tmp_path / config.storage_local_root
        assert storage.exists()
        assert (storage / "objects").exists()


class TestProductionFoundation:
    def test_build_foundation(self, tmp_path):
        audit = build_production_foundation(tmp_path)
        assert audit["version"] == "v6.0"
        assert "bootstrap_success" in audit
        assert audit["domain_count"] == 12
        assert audit["bic_os_phase_locked"] == True
        assert audit["production_ready"] == False

    def test_foundation_outputs(self, tmp_path):
        audit = build_production_foundation(tmp_path)
        out_dir = tmp_path / "outputs" / "v60_test"
        paths = write_production_foundation_outputs(audit, out_dir)
        assert Path(paths["summary_json"]).exists()
        assert Path(paths["full_audit_json"]).exists()
        assert Path(paths["domain_matrix_csv"]).exists()
        assert Path(paths["markdown_report"]).exists()

    def test_domain_count(self, tmp_path):
        audit = build_production_foundation(tmp_path)
        assert audit["domain_count"] == 12

    def test_open_gaps_exist(self, tmp_path):
        audit = build_production_foundation(tmp_path)
        assert audit["open_gap_count"] > 0
        assert audit["production_ready"] == False

    def test_audit_sha256_present(self, tmp_path):
        audit = build_production_foundation(tmp_path)
        assert "audit_sha256" in audit
        assert len(audit["audit_sha256"]) == 64


class TestDomainReadiness:
    def test_domain_defaults(self):
        d = DomainReadiness(domain_id="test_domain")
        assert d.gap_open == True
        assert d.local_evidence_present == False
        assert d.production_service_configured == False
''')
print("tests OK")

# ============================================================
# 7. Docs
# ============================================================
with open(os.path.join(BASE, "docs", "PRODUCTION_FOUNDATION_GUIDE_V60.md"), "w", encoding="utf-8") as f:
    f.write('''# BioGPU-Core v6.0 Production Foundation Guide

v6.0 is the first production infrastructure release. It upgrades the project from 56 local contract proofs toward production-ready BioCompute Runtime and BiC OS.

## What v6.0 Provides

- **ProductionConfig**: centralized configuration for all 12 production domains
- **ProductionBootstrap**: environment initialization (databases, storage, directories)
- **ProductionFoundation**: domain readiness assessment and audit

## 12 Production Domains

| # | Domain | v6.0 Status |
|---|--------|------------|
| 1 | production_identity_provider | Configured |
| 2 | persistent_tenant_membership | Database created |
| 3 | production_object_storage | Storage initialized |
| 4 | hosted_runtime_workers | Pool configured |
| 5 | live_private_registry | Directory ready |
| 6 | trusted_release_signing | Deferred to v6.6 |
| 7 | production_ci_cd_gates | Deferred to v6.7 |
| 8 | security_review_and_threat_model | Deferred to v6.8 |
| 9 | support_incident_system | Database created |
| 10 | notification_provider | SMTP configured |
| 11 | external_beta_acceptance | Database created |
| 12 | os_service_supervision | Deferred to v6.12 |

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v60_production_foundation.ps1
```

## Outputs

- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_SUMMARY.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_AUDIT.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_DOMAIN_MATRIX.csv`
- `outputs/v60_production_foundation/V60_BOOTSTRAP_RESULT.json`
- `outputs/v60_production_foundation/V60_CONFIG_SNAPSHOT.json`
- `outputs/v60_production_foundation/V60_PRODUCTION_FOUNDATION_REPORT.md`

## Configuration

Environment variables (prefix `BICOS_`):
- `BICOS_ENVIRONMENT` — development | staging | production
- `BICOS_PRODUCTION_MODE` — true | false
- `BICOS_IDENTITY_JWT_SECRET` — JWT signing secret
- `BICOS_WORKER_POOL_SIZE` — number of worker processes
- `BICOS_STORAGE_BACKEND` — local | s3 | minio

Or create `configs/production_config_v60.json`.

## Boundary

v6.0 validates production environment bootstrap and domain readiness. It does not claim production deployment, external signoff, or BiC OS production readiness until all 12 domains are closed.
''')
print("docs OK")

# ============================================================
# 8. Example
# ============================================================
with open(os.path.join(BASE, "examples", "biosdk_v60_production_foundation.py"), "w", encoding="utf-8") as f:
    f.write('''"""Minimal SDK example for v6.0 Production Foundation."""
from biogpu.production.config_v60 import ProductionConfig
from biogpu.production.bootstrap_v60 import bootstrap_production
from biogpu.production.foundation_v60 import build_production_foundation


def main():
    print("BioGPU-Core v6.0 Production Foundation - SDK Example")
    print()

    # 1. Load config
    config = ProductionConfig()
    print(f"Config loaded: v{config.config_version}, env={config.environment}")

    # 2. Bootstrap
    result = bootstrap_production(config, ".")
    print(f"Bootstrap: success={result.success}, checks={len(result.checks)}, errors={len(result.errors)}")
    for c in result.checks:
        print(f"  [{c['check']}] passed={c['passed']}")

    # 3. Foundation audit
    audit = build_production_foundation(".")
    print(f"Foundation: open_gaps={audit['open_gap_count']}, ready={audit['production_ready']}")
    print(f"BiC OS locked: {audit['bic_os_phase_locked']}")


if __name__ == "__main__":
    main()
''')
print("example OK")

print("Done. All v6.0 files written.")
