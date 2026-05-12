from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def stable_config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, default=str, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def make_run_metadata(benchmark: str, config: dict[str, Any], version: str = "0.5") -> dict[str, Any]:
    return {
        "project": "biogpu-core",
        "project_version": version,
        "benchmark": benchmark,
        "config_hash": stable_config_hash(config),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": "biogpu-result-v1",
    }
