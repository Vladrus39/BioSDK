"""BioGPU-Core v4.3 hosted beta job model.

This module defines the server-side contracts for a hosted BioGPU beta:
users/workspaces, roles, quotas, job manifests, job lifecycle, and result
bundle references.  It intentionally models software/replay/read-only work;
live actuation jobs are not accepted by this scaffold.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


class UserRole(str, Enum):
    VIEWER = "viewer"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    OPERATOR = "operator"
    ADMIN = "admin"


class AccessTier(str, Enum):
    DEVELOPER_EVALUATION = "developer_evaluation"
    RESEARCH_PILOT = "research_pilot"
    ENTERPRISE_READ_ONLY = "enterprise_read_only"
    ENTERPRISE_LIVE_SHADOW = "enterprise_live_shadow"
    LAB_APPROVED_CLOSED_LOOP = "lab_approved_closed_loop"


class JobType(str, Enum):
    DATASET_IMPORT = "dataset_import"
    BENCHMARK_RUN = "benchmark_run"
    BIOLLM_TOOL_RUN = "biollm_tool_run"
    API_READONLY_VALIDATION = "api_readonly_validation"
    RESULT_BUNDLE_EXPORT = "result_bundle_export"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


SAFE_JOB_TYPES_BY_TIER: Dict[AccessTier, List[JobType]] = {
    AccessTier.DEVELOPER_EVALUATION: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    AccessTier.RESEARCH_PILOT: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    AccessTier.ENTERPRISE_READ_ONLY: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    AccessTier.ENTERPRISE_LIVE_SHADOW: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    # v4.3 still does not enable live actuation; the tier exists for planning
    # and must remain disabled until a lab/vendor allowlist is implemented.
    AccessTier.LAB_APPROVED_CLOSED_LOOP: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
}

UNSAFE_JOB_FIELDS = {
    "voltage",
    "amplitude",
    "current",
    "pulse_width",
    "frequency",
    "charge_density",
    "electrode_command",
    "stimulate",
    "stimulation",
    "pinout",
    "wiring",
    "media_recipe",
    "environment_control",
    "incubator_control",
    "closed_loop_actuation",
    "live_actuation",
}

ROLE_CREATE_PERMISSIONS: Dict[UserRole, List[JobType]] = {
    UserRole.VIEWER: [],
    UserRole.DEVELOPER: [JobType.DATASET_IMPORT, JobType.BENCHMARK_RUN, JobType.BIOLLM_TOOL_RUN],
    UserRole.RESEARCHER: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    UserRole.OPERATOR: [
        JobType.DATASET_IMPORT,
        JobType.BENCHMARK_RUN,
        JobType.BIOLLM_TOOL_RUN,
        JobType.API_READONLY_VALIDATION,
        JobType.RESULT_BUNDLE_EXPORT,
    ],
    UserRole.ADMIN: list(JobType),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find_unsafe_fields(payload: Any, prefix: str = "") -> List[str]:
    """Find unsafe key names recursively in a job payload."""
    hits: List[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_s = str(key)
            path = f"{prefix}.{key_s}" if prefix else key_s
            if key_s.lower() in UNSAFE_JOB_FIELDS:
                hits.append(path)
            hits.extend(find_unsafe_fields(value, path))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            hits.extend(find_unsafe_fields(value, f"{prefix}[{idx}]"))
    return hits


@dataclass(frozen=True)
class QuotaPolicyV43:
    tier: AccessTier
    max_active_jobs: int
    max_jobs_per_day: int
    max_upload_mb: int
    max_shuffle_controls: int
    max_runtime_minutes: int
    allow_external_readonly_api: bool
    allow_live_shadow: bool
    allow_live_actuation: bool = False


DEFAULT_QUOTAS: Dict[AccessTier, QuotaPolicyV43] = {
    AccessTier.DEVELOPER_EVALUATION: QuotaPolicyV43(AccessTier.DEVELOPER_EVALUATION, 2, 20, 250, 50, 20, False, False),
    AccessTier.RESEARCH_PILOT: QuotaPolicyV43(AccessTier.RESEARCH_PILOT, 4, 100, 2000, 250, 90, True, False),
    AccessTier.ENTERPRISE_READ_ONLY: QuotaPolicyV43(AccessTier.ENTERPRISE_READ_ONLY, 8, 500, 20000, 1000, 240, True, False),
    AccessTier.ENTERPRISE_LIVE_SHADOW: QuotaPolicyV43(AccessTier.ENTERPRISE_LIVE_SHADOW, 12, 1000, 50000, 2000, 480, True, True),
    AccessTier.LAB_APPROVED_CLOSED_LOOP: QuotaPolicyV43(AccessTier.LAB_APPROVED_CLOSED_LOOP, 12, 1000, 50000, 2000, 480, True, True, False),
}


@dataclass
class UserContextV43:
    user_id: str
    workspace_id: str
    role: UserRole
    tier: AccessTier


@dataclass
class BioGPUJobSpecV43:
    job_type: JobType
    manifest: Dict[str, Any]
    dataset_id: Optional[str] = None
    requested_result_bundle: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_for_context(self, ctx: UserContextV43) -> List[str]:
        errors: List[str] = []
        if self.job_type not in SAFE_JOB_TYPES_BY_TIER[ctx.tier]:
            errors.append(f"job_type_not_allowed_for_tier:{self.job_type.value}:{ctx.tier.value}")
        if self.job_type not in ROLE_CREATE_PERMISSIONS[ctx.role]:
            errors.append(f"job_type_not_allowed_for_role:{self.job_type.value}:{ctx.role.value}")
        unsafe = find_unsafe_fields(self.manifest)
        if unsafe:
            errors.append("unsafe_manifest_fields:" + ",".join(unsafe))
        if self.job_type == JobType.API_READONLY_VALIDATION:
            quota = DEFAULT_QUOTAS[ctx.tier]
            if not quota.allow_external_readonly_api:
                errors.append(f"external_readonly_api_not_allowed_for_tier:{ctx.tier.value}")
        # Explicitly gate all live actuation until a later lab-approved module.
        if bool(self.manifest.get("live_actuation")) or bool(self.manifest.get("closed_loop_actuation")):
            errors.append("live_actuation_disabled_in_v43")
        shuffle_controls = int(self.manifest.get("shuffle_controls", 0) or 0)
        max_shuffle = DEFAULT_QUOTAS[ctx.tier].max_shuffle_controls
        if shuffle_controls > max_shuffle:
            errors.append(f"shuffle_controls_exceed_quota:{shuffle_controls}>{max_shuffle}")
        return errors


@dataclass
class ResultBundleRefV43:
    bundle_id: str
    job_id: str
    uri: str
    created_at: str
    content_type: str = "application/zip"
    checksum: Optional[str] = None


@dataclass
class BioGPUJobRecordV43:
    job_id: str
    workspace_id: str
    created_by: str
    spec: BioGPUJobSpecV43
    status: JobStatus = JobStatus.QUEUED
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    validation_errors: List[str] = field(default_factory=list)
    result_bundle: Optional[ResultBundleRefV43] = None
    audit_events: List[Dict[str, Any]] = field(default_factory=list)

    def add_event(self, event: str, **details: Any) -> None:
        self.audit_events.append({"time": utc_now_iso(), "event": event, "details": details})
        self.updated_at = utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "job_type": self.spec.job_type.value,
            "dataset_id": self.spec.dataset_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "validation_errors": list(self.validation_errors),
            "result_bundle": None if self.result_bundle is None else self.result_bundle.__dict__,
            "audit_event_count": len(self.audit_events),
        }


class InMemoryJobStoreV43:
    """Small in-memory store for tests and hosted-server scaffolding.

    Production deployment should replace this with Postgres/Redis/object storage.
    """

    def __init__(self) -> None:
        self.jobs: Dict[str, BioGPUJobRecordV43] = {}

    def active_count(self, workspace_id: str) -> int:
        return sum(1 for j in self.jobs.values() if j.workspace_id == workspace_id and j.status in {JobStatus.QUEUED, JobStatus.RUNNING})

    def create_job(self, ctx: UserContextV43, spec: BioGPUJobSpecV43) -> BioGPUJobRecordV43:
        errors = spec.validate_for_context(ctx)
        quota = DEFAULT_QUOTAS[ctx.tier]
        if self.active_count(ctx.workspace_id) >= quota.max_active_jobs:
            errors.append(f"active_job_quota_exceeded:{quota.max_active_jobs}")
        job = BioGPUJobRecordV43(
            job_id="job_" + uuid4().hex[:16],
            workspace_id=ctx.workspace_id,
            created_by=ctx.user_id,
            spec=spec,
            validation_errors=errors,
        )
        if errors:
            job.status = JobStatus.FAILED
            job.add_event("validation_failed", errors=errors)
        else:
            job.add_event("queued")
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> BioGPUJobRecordV43:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        return self.jobs[job_id]

    def list_jobs(self, workspace_id: Optional[str] = None) -> List[BioGPUJobRecordV43]:
        jobs = list(self.jobs.values())
        if workspace_id:
            jobs = [j for j in jobs if j.workspace_id == workspace_id]
        return sorted(jobs, key=lambda j: j.created_at)

    def transition(self, job_id: str, status: JobStatus, **details: Any) -> BioGPUJobRecordV43:
        job = self.get_job(job_id)
        job.status = status
        job.add_event("status_transition", status=status.value, **details)
        return job

    def attach_result_bundle(self, job_id: str, uri: str) -> ResultBundleRefV43:
        job = self.get_job(job_id)
        bundle = ResultBundleRefV43(bundle_id="bundle_" + uuid4().hex[:16], job_id=job_id, uri=uri, created_at=utc_now_iso())
        job.result_bundle = bundle
        job.add_event("result_bundle_attached", uri=uri)
        return bundle


def default_server_capabilities() -> Dict[str, Any]:
    return {
        "version": "v4.3",
        "product": "BioGPU-Core Hosted Beta Server Scaffold",
        "safe_access_model": "maximum software access, no unapproved live actuation",
        "job_types": [j.value for j in JobType],
        "roles": [r.value for r in UserRole],
        "tiers": [t.value for t in AccessTier],
        "live_actuation_enabled": False,
        "result_bundle_contract": True,
        "audit_logging_required": True,
    }
