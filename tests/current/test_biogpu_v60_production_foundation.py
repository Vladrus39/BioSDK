"""Tests for v6.0 Production Foundation."""
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
        assert audit["biosdk_phase_locked"] == True
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
