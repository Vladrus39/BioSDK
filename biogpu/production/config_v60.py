"""Production configuration system v6.0.

Centralized configuration for all production services. Supports
environment variables, .env files, and programmatic overrides.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


@dataclass
class ProductionConfig:
    """Master production configuration for BioCompute Runtime / BiC OS."""

    # Identity
    identity_provider_enabled: bool = True
    identity_provider_host: str = "127.0.0.1"
    identity_provider_port: int = 8400
    identity_jwt_secret: str = ""
    identity_token_expiry_minutes: int = 60
    identity_admin_users: list[str] = field(default_factory=lambda: ["admin@biocompute.local"])

    # Tenant
    tenant_db_path: str = "data/production/tenants.db"
    tenant_default_quota_jobs: int = 100
    tenant_default_quota_storage_mb: int = 1024

    # Storage
    storage_backend: str = "local"
    storage_local_root: str = "data/production/storage"
    storage_s3_endpoint: str = ""
    storage_s3_bucket: str = "biocompute-production"
    storage_s3_access_key: str = ""
    storage_s3_secret_key: str = ""

    # Workers
    worker_pool_size: int = 4
    worker_max_retries: int = 3
    worker_timeout_seconds: int = 3600
    worker_heartbeat_interval_seconds: int = 30

    # Registry
    registry_enabled: bool = True
    registry_host: str = "127.0.0.1"
    registry_port: int = 8401
    registry_packages_dir: str = "data/production/registry/packages"

    # Signing
    signing_enabled: bool = True
    signing_key_path: str = "data/production/keys/release_signing.key"
    signing_algorithm: str = "HMAC-SHA256"

    # CI/CD
    ci_enabled: bool = True
    ci_precommit_hooks_path: str = "configs/precommit_hooks.yaml"
    ci_gate_matrix_path: str = "configs/ci_gate_matrix.json"

    # Security
    security_threat_model_path: str = "docs/SECURITY_THREAT_MODEL_V60.md"
    security_audit_enabled: bool = True

    # Incidents
    incident_db_path: str = "data/production/incidents.db"
    incident_retention_days: int = 365

    # Notifications
    notification_provider: str = "smtp"
    notification_smtp_host: str = "localhost"
    notification_smtp_port: int = 25
    notification_webhook_url: str = ""
    notification_from: str = "bic-os@biocompute.local"

    # Beta
    beta_enabled: bool = False
    beta_participant_db_path: str = "data/production/beta_participants.db"
    beta_max_participants: int = 10

    # OS supervision
    os_service_name: str = "BiCOS"
    os_service_display_name: str = "BiC OS Production Runtime"
    os_service_description: str = "BioCompute Runtime production daemon"
    os_service_log_path: str = "data/production/logs/bicos.log"

    # Meta
    config_version: str = "v6.0"
    environment: str = "development"
    production_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    def validate(self) -> list[str]:
        errors = []
        if self.environment == "production" and not self.identity_jwt_secret:
            errors.append("identity_jwt_secret must be set in production environment")
        if self.environment == "production" and self.notification_provider == "console":
            errors.append("notification_provider should not be 'console' in production")
        if self.worker_pool_size < 1:
            errors.append("worker_pool_size must be >= 1")
        return errors

    @classmethod
    def from_env(cls) -> "ProductionConfig":
        return cls(
            identity_provider_enabled=os.getenv("BICOS_IDENTITY_ENABLED", "true").lower() == "true",
            identity_provider_host=os.getenv("BICOS_IDENTITY_HOST", "127.0.0.1"),
            identity_provider_port=int(os.getenv("BICOS_IDENTITY_PORT", "8400")),
            identity_jwt_secret=os.getenv("BICOS_IDENTITY_JWT_SECRET", ""),
            identity_token_expiry_minutes=int(os.getenv("BICOS_IDENTITY_TOKEN_EXPIRY", "60")),
            worker_pool_size=int(os.getenv("BICOS_WORKER_POOL_SIZE", "4")),
            storage_backend=os.getenv("BICOS_STORAGE_BACKEND", "local"),
            environment=os.getenv("BICOS_ENVIRONMENT", "development"),
            production_mode=os.getenv("BICOS_PRODUCTION_MODE", "false").lower() == "true",
            config_version="v6.0",
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "ProductionConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def load_production_config(
    config_path: str | Path | None = None,
    use_env: bool = True,
) -> ProductionConfig:
    if config_path and Path(config_path).exists():
        config = ProductionConfig.from_file(config_path)
    elif use_env:
        config = ProductionConfig.from_env()
    else:
        config = ProductionConfig()
    if use_env:
        _apply_env_overrides(config)
    return config


def _apply_env_overrides(config: ProductionConfig) -> None:
    mapping = {
        "BICOS_IDENTITY_ENABLED": ("identity_provider_enabled", lambda v: v.lower() == "true"),
        "BICOS_IDENTITY_HOST": ("identity_provider_host", str),
        "BICOS_IDENTITY_PORT": ("identity_provider_port", int),
        "BICOS_IDENTITY_JWT_SECRET": ("identity_jwt_secret", str),
        "BICOS_WORKER_POOL_SIZE": ("worker_pool_size", int),
        "BICOS_STORAGE_BACKEND": ("storage_backend", str),
        "BICOS_ENVIRONMENT": ("environment", str),
        "BICOS_PRODUCTION_MODE": ("production_mode", lambda v: v.lower() == "true"),
    }
    for env_key, (attr, cast) in mapping.items():
        val = os.getenv(env_key)
        if val is not None:
            setattr(config, attr, cast(val))
