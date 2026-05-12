"""Authenticated local service process and result-bundle contract, v5.28."""
from __future__ import annotations

import csv
import hashlib
import hmac
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:  # FastAPI is optional for pure workflow/tests that use the facade directly.
    from fastapi import FastAPI, Header, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore
    Header = None  # type: ignore
    HTTPException = Exception  # type: ignore

    class BaseModel:  # type: ignore
        pass

from biogpu.beta.job_model_v43 import JobStatus
from biogpu.runtime.durable_scheduler_v526 import enqueue_reference_jobs_v526
from biogpu.runtime.scheduler_api_v527 import CancelRequestV527, SchedulerAPIFacadeV527, scheduler_api_route_manifest_v527


DEFAULT_OUT = Path("outputs/v528_authenticated_local_service")
DEFAULT_DB_NAME = "V528_AUTHENTICATED_LOCAL_SERVICE.sqlite3"
import os as _os
V528_DEVELOPER_API_KEY = _os.environ.get("BIOSDK_DEV_KEY", "fixture-local-dev-key")
V528_WORKER_API_KEY = _os.environ.get("BIOSDK_WORKER_KEY", "fixture-local-worker-key")
V528_VIEWER_API_KEY = _os.environ.get("BIOSDK_VIEWER_KEY", "fixture-local-viewer-key")


@dataclass(frozen=True)
class LocalServicePrincipalV528:
    key_id: str
    user_id: str
    workspace_id: str
    role: str
    scopes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LocalServiceAuthResultV528:
    accepted: bool
    status: str
    principal: LocalServicePrincipalV528 | None = None
    errors: tuple[str, ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["principal"] = self.principal.to_dict() if self.principal else None
        return data


@dataclass(frozen=True)
class LocalServiceOperationV528:
    action: str
    accepted: bool
    status: str
    principal_id: str | None = None
    job_id: str | None = None
    errors: tuple[str, ...] = tuple()
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ResultBundleDownloadRequestV528(BaseModel):
    include_payload: bool = True


class AuthenticatedLocalServiceV528:
    """Local auth facade over v5.27 scheduler semantics and local JSON bundles."""

    def __init__(self, db_path: str | Path, result_dir: str | Path | None = None) -> None:
        self.scheduler = SchedulerAPIFacadeV527(db_path, result_dir)
        self._principals = _default_principal_registry()

    def health(self) -> dict[str, Any]:
        scheduler_health = self.scheduler.health()
        return {
            "status": "ok",
            "version": "v5.28",
            "local_service_ready": True,
            "auth_required_for_v1": True,
            "non_secret_fixture_keys": True,
            "scheduler": scheduler_health,
            "result_bundle_download_contract_ready": True,
            "production_api_ready": False,
            "production_scheduler_ready": False,
            "production_biocompute_runtime_ready": False,
            "live_actuation_enabled": False,
            "bic_os_phase_locked": True,
        }

    def authenticate(self, api_key: str | None) -> LocalServiceAuthResultV528:
        if not api_key:
            return LocalServiceAuthResultV528(False, "missing_api_key", errors=("missing_api_key",))
        for candidate_key, principal in self._principals.items():
            if hmac.compare_digest(api_key, candidate_key):
                return LocalServiceAuthResultV528(True, "authenticated", principal=principal)
        return LocalServiceAuthResultV528(False, "invalid_api_key", errors=("invalid_api_key",))

    def whoami(self, api_key: str | None) -> LocalServiceOperationV528:
        auth = self.authenticate(api_key)
        if not auth.accepted or auth.principal is None:
            return _auth_denied("whoami", auth)
        return LocalServiceOperationV528("whoami", True, "authenticated", auth.principal.key_id, payload=auth.principal.to_dict())

    def list_jobs(self, api_key: str | None, status: str | None = None) -> LocalServiceOperationV528:
        principal = self._require_scope("list_jobs", api_key, "jobs:read")
        if isinstance(principal, LocalServiceOperationV528):
            return principal
        return LocalServiceOperationV528("list_jobs", True, "ok", principal.key_id, payload={"jobs": self.scheduler.list_jobs(status)})

    def get_job(self, api_key: str | None, job_id: str) -> LocalServiceOperationV528:
        principal = self._require_scope("get_job", api_key, "jobs:read")
        if isinstance(principal, LocalServiceOperationV528):
            return principal
        try:
            job = self.scheduler.get_job(job_id)
        except KeyError:
            return LocalServiceOperationV528("get_job", False, "job_not_found", principal.key_id, job_id, errors=("job_not_found",))
        return LocalServiceOperationV528("get_job", True, "ok", principal.key_id, job_id, payload=job)

    def cancel_job(self, api_key: str | None, job_id: str, reason: str = "user_requested_cancel") -> LocalServiceOperationV528:
        principal = self._require_scope("cancel_job", api_key, "jobs:write")
        if isinstance(principal, LocalServiceOperationV528):
            return principal
        action = self.scheduler.cancel_job(job_id, reason=reason)
        return LocalServiceOperationV528("cancel_job", action.accepted, action.status, principal.key_id, job_id, errors=action.errors, payload=action.to_dict())

    def worker_step(self, api_key: str | None, worker_id: str = "local_service_worker_v528") -> LocalServiceOperationV528:
        principal = self._require_scope("worker_step", api_key, "workers:step")
        if isinstance(principal, LocalServiceOperationV528):
            return principal
        action = self.scheduler.worker_step(worker_id)
        return LocalServiceOperationV528("worker_step", action.get("status") == JobStatus.SUCCEEDED.value, action.get("status", "unknown"), principal.key_id, action.get("job_id"), errors=tuple(action.get("errors") or []), payload=action)

    def download_result_bundle(self, api_key: str | None, job_id: str, include_payload: bool = True) -> LocalServiceOperationV528:
        principal = self._require_scope("download_result_bundle", api_key, "bundles:read")
        if isinstance(principal, LocalServiceOperationV528):
            return principal
        try:
            job = self.scheduler.get_job(job_id)
        except KeyError:
            return LocalServiceOperationV528("download_result_bundle", False, "job_not_found", principal.key_id, job_id, errors=("job_not_found",))
        bundle = job.get("result_bundle")
        if job.get("status") != JobStatus.SUCCEEDED.value or not bundle:
            return LocalServiceOperationV528("download_result_bundle", False, "result_bundle_not_ready", principal.key_id, job_id, errors=("result_bundle_not_ready",))
        uri = str(bundle.get("uri", ""))
        bundle_path = Path(uri)
        if not bundle_path.exists():
            return LocalServiceOperationV528("download_result_bundle", False, "result_bundle_file_missing", principal.key_id, job_id, errors=("result_bundle_file_missing",))
        data = bundle_path.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        checksum = str(bundle.get("checksum", ""))
        checksum_matches = checksum == sha256
        payload: dict[str, Any] | None = None
        if include_payload:
            try:
                payload = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                payload = {"raw_text": data.decode("utf-8", errors="replace")}
        contract = {
            "job_id": job_id,
            "bundle_id": bundle.get("bundle_id"),
            "uri": uri,
            "content_type": "application/json",
            "size_bytes": len(data),
            "sha256": sha256,
            "declared_checksum": checksum,
            "checksum_matches": checksum_matches,
            "payload_included": include_payload,
            "payload": payload,
            "download_is_local_file_contract": True,
            "production_object_storage_ready": False,
        }
        status = "download_contract_ready" if checksum_matches else "checksum_mismatch"
        errors = tuple() if checksum_matches else ("checksum_mismatch",)
        return LocalServiceOperationV528("download_result_bundle", checksum_matches, status, principal.key_id, job_id, errors=errors, payload=contract)

    def _require_scope(self, action: str, api_key: str | None, scope: str) -> LocalServicePrincipalV528 | LocalServiceOperationV528:
        auth = self.authenticate(api_key)
        if not auth.accepted or auth.principal is None:
            return _auth_denied(action, auth)
        if scope not in auth.principal.scopes:
            return LocalServiceOperationV528(action, False, "missing_scope", auth.principal.key_id, errors=(f"missing_scope:{scope}",))
        return auth.principal


def _default_principal_registry() -> dict[str, LocalServicePrincipalV528]:
    return {
        V528_DEVELOPER_API_KEY: LocalServicePrincipalV528("local_developer", "developer_v528", "default", "developer", ("jobs:read", "jobs:write", "bundles:read")),
        V528_WORKER_API_KEY: LocalServicePrincipalV528("local_worker", "worker_v528", "default", "worker", ("jobs:read", "workers:step", "bundles:read")),
        V528_VIEWER_API_KEY: LocalServicePrincipalV528("local_viewer", "viewer_v528", "default", "viewer", ("jobs:read", "bundles:read")),
    }


def _auth_denied(action: str, auth: LocalServiceAuthResultV528) -> LocalServiceOperationV528:
    return LocalServiceOperationV528(action, False, auth.status, None, errors=auth.errors, payload=auth.to_dict())


def make_authenticated_local_service_app_v528(db_path: str | Path, result_dir: str | Path | None = None):
    if FastAPI is None:  # pragma: no cover
        raise RuntimeError("FastAPI is not installed")
    service = AuthenticatedLocalServiceV528(db_path, result_dir)
    app = FastAPI(title="BioGPU-Core Authenticated Local Service", version="5.28.0")

    def _ok_or_raise(operation: LocalServiceOperationV528) -> dict[str, Any]:
        if operation.accepted:
            return operation.to_dict()
        if operation.status in {"missing_api_key", "invalid_api_key"}:
            raise HTTPException(status_code=401, detail=operation.status)
        if operation.status == "missing_scope":
            raise HTTPException(status_code=403, detail=operation.errors[0] if operation.errors else "missing_scope")
        if operation.status == "job_not_found":
            raise HTTPException(status_code=404, detail="job_not_found")
        raise HTTPException(status_code=409, detail=operation.status)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return service.health()

    @app.get("/v1/service/whoami")
    def whoami(x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.whoami(x_biogpu_api_key))

    @app.get("/v1/scheduler/jobs")
    def list_jobs(status: str | None = None, x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.list_jobs(x_biogpu_api_key, status))

    @app.get("/v1/scheduler/jobs/{job_id}")
    def get_job(job_id: str, x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.get_job(x_biogpu_api_key, job_id))

    @app.post("/v1/scheduler/jobs/{job_id}/cancel")
    def cancel_job(job_id: str, req: CancelRequestV527 | None = None, x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.cancel_job(x_biogpu_api_key, job_id, reason=(req.reason if req else "user_requested_cancel")))

    @app.post("/v1/scheduler/workers/{worker_id}/step")
    def worker_step(worker_id: str, x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.worker_step(x_biogpu_api_key, worker_id))

    @app.get("/v1/result-bundles/{job_id}/download")
    def download_result_bundle(job_id: str, include_payload: bool = True, x_biogpu_api_key: str | None = Header(default=None)) -> dict[str, Any]:
        return _ok_or_raise(service.download_result_bundle(x_biogpu_api_key, job_id, include_payload=include_payload))

    return app


def authenticated_local_service_route_manifest_v528(app: Any) -> list[dict[str, Any]]:
    return scheduler_api_route_manifest_v527(app)


def run_authenticated_local_service_workflow_v528(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / DEFAULT_DB_NAME
    if db_path.exists():
        db_path.unlink()
    enqueue = enqueue_reference_jobs_v526(db_path)
    service = AuthenticatedLocalServiceV528(db_path, out / "service_worker_results")
    app = make_authenticated_local_service_app_v528(db_path, out / "service_worker_results")
    routes = authenticated_local_service_route_manifest_v528(app)

    health_before = service.health()
    missing_auth = service.list_jobs(None)
    invalid_auth = service.list_jobs("invalid-v528-key")
    whoami = service.whoami(V528_DEVELOPER_API_KEY)
    jobs_before = service.list_jobs(V528_DEVELOPER_API_KEY)
    scope_denial = service.worker_step(V528_DEVELOPER_API_KEY, "developer_cannot_step_workers")
    worker_action = service.worker_step(V528_WORKER_API_KEY, "local_service_worker_v528")
    worker_job_id = worker_action.job_id
    download = service.download_result_bundle(V528_DEVELOPER_API_KEY, worker_job_id or "", include_payload=True)
    queued_after_worker = service.scheduler.list_jobs(JobStatus.QUEUED.value)
    cancel_action = service.cancel_job(V528_DEVELOPER_API_KEY, queued_after_worker[0]["job_id"], reason="v528_authenticated_cancel_probe") if queued_after_worker else LocalServiceOperationV528("cancel_job", False, "no_queued_job", "local_developer", errors=("no_queued_job",))
    viewer_cancel_denial = service.cancel_job(V528_VIEWER_API_KEY, cancel_action.job_id or "missing", reason="viewer_scope_probe")
    health_after = service.health()
    jobs = service.scheduler.list_jobs()
    events = service.scheduler.store.list_events()
    blocked_submission_count = sum(1 for submission in enqueue["submissions"].values() if not submission["admission"]["accepted"])
    route_paths = {route["path"] for route in routes}
    proof_ready = (
        health_after["auth_required_for_v1"]
        and missing_auth.status == "missing_api_key"
        and invalid_auth.status == "invalid_api_key"
        and whoami.accepted
        and scope_denial.status == "missing_scope"
        and worker_action.accepted
        and download.accepted
        and bool(download.payload and download.payload.get("checksum_matches"))
        and cancel_action.accepted
        and viewer_cancel_denial.status == "missing_scope"
        and "/v1/result-bundles/{job_id}/download" in route_paths
        and blocked_submission_count >= 1
    )
    actions = {
        "missing_auth": missing_auth.to_dict(),
        "invalid_auth": invalid_auth.to_dict(),
        "whoami": whoami.to_dict(),
        "jobs_before": jobs_before.to_dict(),
        "developer_worker_scope_denial": scope_denial.to_dict(),
        "worker_step": worker_action.to_dict(),
        "result_bundle_download": download.to_dict(),
        "cancel": cancel_action.to_dict(),
        "viewer_cancel_scope_denial": viewer_cancel_denial.to_dict(),
    }
    return {
        "version": "v5.28",
        "phase": "authenticated_local_service_result_bundle_download",
        "overall_status": "authenticated_local_service_contract_ready_runtime_not_claimed" if proof_ready else "authenticated_local_service_contract_incomplete",
        "active_phase": "biocompute_runtime_local_service_proof",
        "bic_os_phase_locked": True,
        "authenticated_local_service_ready": proof_ready,
        "auth_required_for_v1": health_after["auth_required_for_v1"],
        "non_secret_fixture_keys_only": True,
        "api_route_count": len(routes),
        "persisted_job_count": len(enqueue["persisted_jobs"]),
        "blocked_submission_count": blocked_submission_count,
        "missing_auth_rejected": missing_auth.status == "missing_api_key",
        "invalid_auth_rejected": invalid_auth.status == "invalid_api_key",
        "scope_denial_passed": scope_denial.status == "missing_scope" and viewer_cancel_denial.status == "missing_scope",
        "worker_step_semantics_passed": worker_action.accepted,
        "result_bundle_download_contract_passed": download.accepted and bool(download.payload and download.payload.get("checksum_matches")),
        "checksum_validation_passed": bool(download.payload and download.payload.get("checksum_matches")),
        "cancel_semantics_passed": cancel_action.accepted,
        "production_api_ready": False,
        "production_scheduler_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "db_path": str(db_path.relative_to(project_root)).replace("\\", "/") if db_path.is_relative_to(project_root) else str(db_path),
        "health_before": health_before,
        "health_after": health_after,
        "route_manifest": routes,
        "actions": actions,
        "jobs": jobs,
        "events": events,
        "download_contract": download.payload or {},
        "remaining_runtime_blockers": [
            "real secret management and key rotation instead of local fixture keys",
            "long-running hosted service supervision and graceful shutdown",
            "multi-worker concurrency with cancellation propagation",
            "production object storage and signed bundle download URLs",
            "quota-backed retry and timeout policy",
            "deployment, TLS, audit retention and tenant isolation",
        ],
        "direct_answer": {
            "did_we_add_authenticated_local_service_contract": "yes" if proof_ready else "not_yet",
            "did_we_add_result_bundle_download_contract": "yes" if download.accepted else "not_yet",
            "is_production_api_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add supervised local runtime process with graceful shutdown and audit log export" if proof_ready else "fix v5.28 auth/download contract blockers first",
        },
        "claim_boundary": "v5.28 proves a local authenticated service contract with non-secret fixture API keys, scope checks, scheduler worker-step/cancel semantics and local result-bundle download checksum validation. It does not claim production secret management, hosted API readiness, live external API control, closed-loop wetware operation, full BioCompute Runtime or BiC OS readiness.",
    }


def write_authenticated_local_service_outputs_v528(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V528_AUTHENTICATED_LOCAL_SERVICE_SUMMARY.json",
        "routes_json": out / "V528_AUTHENTICATED_LOCAL_SERVICE_ROUTES.json",
        "actions_json": out / "V528_AUTHENTICATED_LOCAL_SERVICE_ACTIONS.json",
        "download_json": out / "V528_RESULT_BUNDLE_DOWNLOAD_CONTRACT.json",
        "jobs_json": out / "V528_AUTHENTICATED_LOCAL_SERVICE_JOBS.json",
        "events_json": out / "V528_AUTHENTICATED_LOCAL_SERVICE_EVENTS.json",
        "jobs_csv": out / "V528_AUTHENTICATED_LOCAL_SERVICE_JOBS.csv",
        "markdown_report": out / "BIOGPU_V528_AUTHENTICATED_LOCAL_SERVICE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"route_manifest", "actions", "jobs", "events", "download_contract"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["routes_json"].write_text(json.dumps({"routes": audit["route_manifest"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["actions_json"].write_text(json.dumps(audit["actions"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["download_json"].write_text(json.dumps(audit["download_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["jobs_json"].write_text(json.dumps({"jobs": audit["jobs"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["events_json"].write_text(json.dumps({"events": audit["events"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_jobs_csv(paths["jobs_csv"], audit["jobs"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_jobs_csv(path: Path, jobs: list[dict[str, Any]]) -> None:
    fieldnames = ["job_id", "job_type", "dataset_id", "status", "result_bundle_ready", "validation_errors"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow({
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "dataset_id": job.get("dataset_id"),
                "status": job.get("status"),
                "result_bundle_ready": bool(job.get("result_bundle")),
                "validation_errors": " | ".join(str(item) for item in job.get("validation_errors", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.28 Authenticated Local Service",
        "",
        "## Direct Answer",
        "",
        f"- Authenticated local service contract: `{answer['did_we_add_authenticated_local_service_contract']}`",
        f"- Result-bundle download contract: `{answer['did_we_add_result_bundle_download_contract']}`",
        f"- Production API ready: `{answer['is_production_api_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- API routes: `{audit['api_route_count']}`",
        f"- Missing auth rejected: `{audit['missing_auth_rejected']}`",
        f"- Invalid auth rejected: `{audit['invalid_auth_rejected']}`",
        f"- Scope denial passed: `{audit['scope_denial_passed']}`",
        f"- Worker step passed: `{audit['worker_step_semantics_passed']}`",
        f"- Result-bundle checksum validation passed: `{audit['checksum_validation_passed']}`",
        f"- Cancel semantics passed: `{audit['cancel_semantics_passed']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)