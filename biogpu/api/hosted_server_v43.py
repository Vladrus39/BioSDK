"""FastAPI scaffold for BioGPU-Core v4.3 hosted beta server.

This is a lightweight server contract, not a production SaaS backend.  It is
intended to make the beta path concrete: roles, job creation, validation,
quotas, result bundle endpoints, and safety-gated read-only operation.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

try:  # FastAPI is optional for environments that only import the models.
    from fastapi import FastAPI, Header, HTTPException
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore
    Header = None  # type: ignore
    HTTPException = Exception  # type: ignore
    class BaseModel:  # type: ignore
        pass
    def Field(default=None, **kwargs):  # type: ignore
        return default

from biogpu.beta.job_model_v43 import (
    AccessTier,
    BioGPUJobSpecV43,
    DEFAULT_QUOTAS,
    InMemoryJobStoreV43,
    JobStatus,
    JobType,
    UserContextV43,
    UserRole,
    default_server_capabilities,
)


class CreateJobRequestV43(BaseModel):
    job_type: str
    manifest: Dict[str, Any] = Field(default_factory=dict)
    dataset_id: Optional[str] = None
    requested_result_bundle: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateJobResponseV43(BaseModel):
    job_id: str
    status: str
    validation_errors: List[str]


def context_from_headers(
    x_biogpu_user: str = "anonymous",
    x_biogpu_workspace: str = "default",
    x_biogpu_role: str = "developer",
    x_biogpu_tier: str = "developer_evaluation",
) -> UserContextV43:
    try:
        role = UserRole(x_biogpu_role)
    except ValueError:
        role = UserRole.DEVELOPER
    try:
        tier = AccessTier(x_biogpu_tier)
    except ValueError:
        tier = AccessTier.DEVELOPER_EVALUATION
    return UserContextV43(
        user_id=x_biogpu_user,
        workspace_id=x_biogpu_workspace,
        role=role,
        tier=tier,
    )


def build_spec(req: CreateJobRequestV43) -> BioGPUJobSpecV43:
    try:
        job_type = JobType(req.job_type)
    except ValueError as exc:
        raise ValueError(f"unknown_job_type:{req.job_type}") from exc
    return BioGPUJobSpecV43(
        job_type=job_type,
        manifest=dict(req.manifest),
        dataset_id=req.dataset_id,
        requested_result_bundle=req.requested_result_bundle,
        metadata=dict(req.metadata),
    )


def make_app(store: Optional[InMemoryJobStoreV43] = None):
    if FastAPI is None:  # pragma: no cover
        raise RuntimeError("FastAPI is not installed")
    store = store or InMemoryJobStoreV43()
    app = FastAPI(title="BioGPU-Core Hosted Beta Server", version="4.3.0")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "version": "v4.3", "live_actuation_enabled": False}

    @app.get("/v1/server/capabilities")
    def capabilities() -> Dict[str, Any]:
        return default_server_capabilities()

    @app.get("/v1/server/quotas")
    def quotas() -> Dict[str, Any]:
        return {tier.value: q.__dict__ for tier, q in DEFAULT_QUOTAS.items()}

    @app.post("/v1/jobs", response_model=CreateJobResponseV43)
    def create_job(
        req: CreateJobRequestV43,
        x_biogpu_user: str = Header(default="anonymous"),
        x_biogpu_workspace: str = Header(default="default"),
        x_biogpu_role: str = Header(default="developer"),
        x_biogpu_tier: str = Header(default="developer_evaluation"),
    ) -> CreateJobResponseV43:
        ctx = context_from_headers(x_biogpu_user, x_biogpu_workspace, x_biogpu_role, x_biogpu_tier)
        try:
            spec = build_spec(req)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        job = store.create_job(ctx, spec)
        return CreateJobResponseV43(job_id=job.job_id, status=job.status.value, validation_errors=job.validation_errors)

    @app.get("/v1/jobs")
    def list_jobs(
        x_biogpu_workspace: str = Header(default="default"),
    ) -> Dict[str, Any]:
        return {"jobs": [j.to_dict() for j in store.list_jobs(x_biogpu_workspace)]}

    @app.get("/v1/jobs/{job_id}")
    def get_job(job_id: str) -> Dict[str, Any]:
        try:
            return store.get_job(job_id).to_dict()
        except KeyError:
            raise HTTPException(status_code=404, detail="job_not_found")

    @app.post("/v1/jobs/{job_id}/cancel")
    def cancel_job(job_id: str) -> Dict[str, Any]:
        try:
            job = store.transition(job_id, JobStatus.CANCELLED)
            return job.to_dict()
        except KeyError:
            raise HTTPException(status_code=404, detail="job_not_found")

    @app.get("/v1/jobs/{job_id}/result-bundle")
    def result_bundle(job_id: str) -> Dict[str, Any]:
        try:
            job = store.get_job(job_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="job_not_found")
        if job.result_bundle is None:
            # Scaffold endpoint: attach a deterministic mock URI so the contract is testable.
            bundle = store.attach_result_bundle(job_id, f"object://biogpu-beta-bundles/{job_id}.zip")
        else:
            bundle = job.result_bundle
        return bundle.__dict__

    @app.post("/v1/datasets/import")
    def import_dataset(
        req: CreateJobRequestV43,
        x_biogpu_user: str = Header(default="anonymous"),
        x_biogpu_workspace: str = Header(default="default"),
        x_biogpu_role: str = Header(default="developer"),
        x_biogpu_tier: str = Header(default="developer_evaluation"),
    ) -> CreateJobResponseV43:
        req.job_type = JobType.DATASET_IMPORT.value
        return create_job(req, x_biogpu_user, x_biogpu_workspace, x_biogpu_role, x_biogpu_tier)

    return app


app = make_app()
