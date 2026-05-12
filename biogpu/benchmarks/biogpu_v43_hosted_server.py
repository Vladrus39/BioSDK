"""Generate v4.3 hosted beta server package outputs."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from biogpu.beta.job_model_v43 import (
    AccessTier,
    BioGPUJobSpecV43,
    DEFAULT_QUOTAS,
    InMemoryJobStoreV43,
    JobType,
    UserContextV43,
    UserRole,
    default_server_capabilities,
)

OUT_DIR = Path("outputs/realdata_zenodo_14363732_v43_hosted_server")


def create_demo_jobs() -> Dict[str, Any]:
    store = InMemoryJobStoreV43()
    research_ctx = UserContextV43("demo_researcher", "demo_workspace", UserRole.RESEARCHER, AccessTier.RESEARCH_PILOT)
    viewer_ctx = UserContextV43("demo_viewer", "demo_workspace", UserRole.VIEWER, AccessTier.DEVELOPER_EVALUATION)

    safe_job = store.create_job(
        research_ctx,
        BioGPUJobSpecV43(
            job_type=JobType.BENCHMARK_RUN,
            dataset_id="zenodo_14363732_preprocessed",
            manifest={
                "mode": "replay",
                "split": "lineage_strict",
                "decoder": "logistic_l2_v27",
                "shuffle_controls": 50,
                "result_bundle": True,
            },
        ),
    )
    unsafe_job = store.create_job(
        research_ctx,
        BioGPUJobSpecV43(
            job_type=JobType.BENCHMARK_RUN,
            dataset_id="external_live_platform",
            manifest={"mode": "live", "voltage": 1.0, "electrode_command": "stimulate"},
        ),
    )
    denied_job = store.create_job(
        viewer_ctx,
        BioGPUJobSpecV43(job_type=JobType.BENCHMARK_RUN, manifest={"mode": "replay"}),
    )
    store.attach_result_bundle(safe_job.job_id, f"object://biogpu-beta-bundles/{safe_job.job_id}.zip")
    return {
        "safe_job": safe_job.to_dict(),
        "unsafe_job": unsafe_job.to_dict(),
        "denied_job": denied_job.to_dict(),
        "job_count": len(store.list_jobs()),
    }


def endpoint_catalog() -> List[Dict[str, str]]:
    return [
        {"method": "GET", "path": "/health", "purpose": "Service health and safety flag."},
        {"method": "GET", "path": "/v1/server/capabilities", "purpose": "Hosted beta capabilities and disabled live actuation flag."},
        {"method": "GET", "path": "/v1/server/quotas", "purpose": "Tier quota policy for early users and enterprises."},
        {"method": "POST", "path": "/v1/jobs", "purpose": "Create a dataset/import/benchmark/BioLLM/read-only API job."},
        {"method": "GET", "path": "/v1/jobs", "purpose": "List workspace jobs."},
        {"method": "GET", "path": "/v1/jobs/{job_id}", "purpose": "Read job status, validation errors, audit count and bundle reference."},
        {"method": "POST", "path": "/v1/jobs/{job_id}/cancel", "purpose": "Cancel queued/running job in the scaffold contract."},
        {"method": "GET", "path": "/v1/jobs/{job_id}/result-bundle", "purpose": "Return result bundle reference or create mock object URI."},
        {"method": "POST", "path": "/v1/datasets/import", "purpose": "Convenience endpoint for dataset import jobs."},
    ]


def access_matrix() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for tier, quota in DEFAULT_QUOTAS.items():
        rows.append({
            "tier": tier.value,
            "max_active_jobs": quota.max_active_jobs,
            "max_jobs_per_day": quota.max_jobs_per_day,
            "max_upload_mb": quota.max_upload_mb,
            "max_shuffle_controls": quota.max_shuffle_controls,
            "allow_external_readonly_api": quota.allow_external_readonly_api,
            "allow_live_shadow": quota.allow_live_shadow,
            "allow_live_actuation": quota.allow_live_actuation,
        })
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_outputs(out_dir: Path = OUT_DIR) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    capabilities = default_server_capabilities()
    demos = create_demo_jobs()
    endpoints = endpoint_catalog()
    access = access_matrix()
    summary = {
        "version": "v4.3",
        "module": "Hosted Server Scaffold + Job Model",
        "live_actuation_enabled": False,
        "endpoint_count": len(endpoints),
        "access_tier_count": len(access),
        "demo_safe_job_status": demos["safe_job"]["status"],
        "demo_unsafe_job_status": demos["unsafe_job"]["status"],
        "demo_denied_job_status": demos["denied_job"]["status"],
        "safe_access_model": capabilities["safe_access_model"],
    }
    (out_dir / "v43_server_capabilities.json").write_text(json.dumps(capabilities, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "v43_demo_jobs.json").write_text(json.dumps(demos, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "v43_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(out_dir / "v43_endpoint_catalog.csv", endpoints)
    write_csv(out_dir / "v43_access_tier_matrix.csv", access)
    report = f"""# BioGPU-Core v4.3 Hosted Server Scaffold Report

## Purpose

v4.3 adds the hosted beta server contract: roles, tiers, quotas, safe job creation,
result bundle endpoints, and the minimum FastAPI surface for external testers.

## Safety boundary

- Maximum software-level access for early testers.
- Upload/replay/read-only/API-shadow style work is allowed by tier.
- Unapproved live actuation remains disabled.
- Unsafe manifest fields are rejected before jobs enter the queue.

## Demo validation

- Safe benchmark job: `{demos['safe_job']['status']}`
- Unsafe live-control job: `{demos['unsafe_job']['status']}`
- Viewer role denied job: `{demos['denied_job']['status']}`

## Generated outputs

- `v43_server_capabilities.json`
- `v43_endpoint_catalog.csv`
- `v43_access_tier_matrix.csv`
- `v43_demo_jobs.json`
- `v43_summary.json`
"""
    (out_dir / "BIOGPU_V43_HOSTED_SERVER_REPORT.md").write_text(report, encoding="utf-8")
    return summary


def main() -> None:
    print(json.dumps(generate_outputs(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
