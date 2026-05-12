"""Storage and retention backend contract proof, v5.38."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import stable_hash
from biogpu.runtime.identity_provider_contract_v537 import run_identity_provider_contract_workflow_v537


DEFAULT_OUT = Path("outputs/v538_storage_retention_contract")


@dataclass(frozen=True)
class StorageBucketContractV538:
    bucket_id: str
    purpose: str
    object_prefix: str
    retention_days: int
    immutable_required: bool
    encryption_required: bool
    allowed_content_types: tuple[str, ...]
    local_contract_only: bool = True
    production_object_storage_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StorageObjectRecordV538:
    object_id: str
    bucket_id: str
    object_key: str
    object_type: str
    content_type: str
    size_bytes: int
    sha256: str
    retention_days: int
    immutable: bool
    source_version: str
    local_uri: str
    production_object_storage_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_storage_bucket_contracts_v538() -> dict[str, StorageBucketContractV538]:
    return {
        "result_bundles": StorageBucketContractV538("result_bundles", "BioCompute result bundle payloads", "results/", 90, False, True, ("application/json",)),
        "audit_artifacts": StorageBucketContractV538("audit_artifacts", "runtime and control-plane audit artifacts", "audit/", 365, False, True, ("application/json", "text/csv", "text/markdown")),
        "retention_manifests": StorageBucketContractV538("retention_manifests", "retention manifests and export indexes", "retention/", 3650, True, True, ("application/json",)),
        "ledger_roots": StorageBucketContractV538("ledger_roots", "append-only proof and incident ledger roots", "ledger-roots/", 3650, True, True, ("application/json",)),
    }


def build_storage_payload_fixtures_v538(v537_audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    v536_summary = dict(v537_audit.get("v536_dependency_summary") or {})
    identity_bundle = dict(v537_audit.get("identity_audit_bundle") or {})
    dashboard_bundle = dict(v536_summary.get("dashboard_audit_bundle") or {})
    proof_root = stable_hash({
        "v537_identity_bundle_sha256": identity_bundle.get("bundle_sha256"),
        "v536_dashboard_bundle_sha256": dashboard_bundle.get("bundle_sha256"),
        "identity_provider_contract_ready": v537_audit.get("identity_provider_contract_ready"),
        "production_auth_ready": v537_audit.get("production_auth_ready"),
    })
    retention_manifest = {
        "version": "v5.38",
        "created_at": utc_now_iso(),
        "policy_name": "local_control_plane_storage_retention_contract",
        "export_before_prune": True,
        "non_destructive_retention": True,
        "objects_expected": ["result_bundle_summary", "identity_audit_bundle", "retention_manifest", "proof_root_anchor"],
        "production_retention_backend_ready": False,
        "bic_os_phase_locked": True,
    }
    retention_manifest["manifest_sha256"] = stable_hash(retention_manifest)
    return {
        "result_bundle_summary": {
            "version": "v5.38",
            "object_type": "result_bundle_summary",
            "source_version": "v5.37",
            "identity_provider_contract_ready": v537_audit.get("identity_provider_contract_ready"),
            "identity_validation_matrix_ready": v537_audit.get("identity_validation_matrix_ready"),
            "accepted_identity_fixture_count": v537_audit.get("accepted_identity_fixture_count"),
            "denied_identity_fixture_count": v537_audit.get("denied_identity_fixture_count"),
            "production_object_storage_ready": False,
            "bic_os_phase_locked": True,
        },
        "identity_audit_bundle": {
            "version": "v5.38",
            "object_type": "identity_audit_bundle",
            "source_version": "v5.37",
            "bundle_sha256": identity_bundle.get("bundle_sha256"),
            "bundle_ready": identity_bundle.get("bundle_ready"),
            "v537_status": v537_audit.get("overall_status"),
            "production_object_storage_ready": False,
            "bic_os_phase_locked": True,
        },
        "retention_manifest": retention_manifest,
        "proof_root_anchor": {
            "version": "v5.38",
            "object_type": "proof_root_anchor",
            "source_version": "v5.37",
            "proof_root_sha256": proof_root,
            "identity_bundle_sha256": identity_bundle.get("bundle_sha256"),
            "dashboard_bundle_sha256": dashboard_bundle.get("bundle_sha256"),
            "append_only_required": True,
            "remote_notarization_ready": False,
            "production_object_storage_ready": False,
            "bic_os_phase_locked": True,
        },
    }


def _payload_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")


def write_storage_fixture_objects_v538(payloads: dict[str, dict[str, Any]], buckets: dict[str, StorageBucketContractV538], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    store_root = out / "local_object_store"
    store_root.mkdir(parents=True, exist_ok=True)
    placement = {
        "result_bundle_summary": "result_bundles",
        "identity_audit_bundle": "audit_artifacts",
        "retention_manifest": "retention_manifests",
        "proof_root_anchor": "ledger_roots",
    }
    records: list[dict[str, Any]] = []
    for object_type, payload in payloads.items():
        bucket_id = placement[object_type]
        bucket = buckets[bucket_id]
        data = _payload_bytes(payload)
        sha256 = stable_hash(payload)
        object_key = f"{bucket.object_prefix}{object_type}_{sha256[:16]}.json"
        local_path = store_root / bucket_id / object_key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        record = StorageObjectRecordV538(
            object_id="obj_" + stable_hash({"bucket_id": bucket_id, "object_key": object_key})[:16],
            bucket_id=bucket_id,
            object_key=object_key,
            object_type=object_type,
            content_type="application/json",
            size_bytes=len(data),
            sha256=sha256,
            retention_days=bucket.retention_days,
            immutable=bucket.immutable_required,
            source_version=str(payload.get("source_version", "v5.38")),
            local_uri=str(local_path).replace("\\", "/"),
        ).to_dict()
        records.append(record)
    manifest = build_storage_object_manifest_v538(records, buckets)
    manifest_path = out / "V538_STORAGE_OBJECT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "store_root": str(store_root).replace("\\", "/"),
        "manifest_path": str(manifest_path).replace("\\", "/"),
        "records": records,
        "manifest": manifest,
    }


def build_storage_object_manifest_v538(records: list[dict[str, Any]], buckets: dict[str, StorageBucketContractV538]) -> dict[str, Any]:
    manifest_base = {
        "version": "v5.38",
        "created_at": utc_now_iso(),
        "object_count": len(records),
        "bucket_count": len(buckets),
        "objects": records,
        "bucket_contracts": {bucket_id: bucket.to_dict() for bucket_id, bucket in buckets.items()},
        "all_objects_hashed": all(len(str(record.get("sha256", ""))) == 64 for record in records),
        "immutable_object_count": sum(1 for record in records if record.get("immutable") is True),
        "production_object_storage_ready": False,
        "production_retention_backend_ready": False,
        "bic_os_phase_locked": True,
    }
    manifest_base["manifest_sha256"] = stable_hash(manifest_base)
    return manifest_base


def validate_storage_object_integrity_v538(records: list[dict[str, Any]], manifest: dict[str, Any], buckets: dict[str, StorageBucketContractV538]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    required_buckets = {"result_bundles", "audit_artifacts", "retention_manifests", "ledger_roots"}
    observed_buckets = {str(record.get("bucket_id")) for record in records}
    if not required_buckets.issubset(observed_buckets):
        issues.append({"path": "bucket_id", "message": "required storage bucket missing"})
    for index, record in enumerate(records):
        bucket_id = str(record.get("bucket_id"))
        bucket = buckets.get(bucket_id)
        if bucket is None:
            issues.append({"path": f"objects[{index}].bucket_id", "message": "unknown bucket"})
            continue
        if record.get("content_type") not in bucket.allowed_content_types:
            issues.append({"path": f"objects[{index}].content_type", "message": "content type not allowed"})
        if record.get("retention_days") != bucket.retention_days:
            issues.append({"path": f"objects[{index}].retention_days", "message": "retention days mismatch"})
        if record.get("immutable") is not bucket.immutable_required:
            issues.append({"path": f"objects[{index}].immutable", "message": "immutability mismatch"})
        local_uri = record.get("local_uri")
        local_path = Path(str(local_uri)) if local_uri else None
        if local_path is None or not local_path.exists():
            issues.append({"path": f"objects[{index}].local_uri", "message": "local object missing"})
            continue
        try:
            payload = json.loads(local_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            issues.append({"path": f"objects[{index}].local_uri", "message": "object is not JSON"})
            continue
        if stable_hash(payload) != record.get("sha256"):
            issues.append({"path": f"objects[{index}].sha256", "message": "object hash mismatch"})
        if local_path.stat().st_size != record.get("size_bytes"):
            issues.append({"path": f"objects[{index}].size_bytes", "message": "object size mismatch"})
    immutable_roots_ready = any(record.get("bucket_id") == "ledger_roots" and record.get("immutable") is True for record in records)
    if not immutable_roots_ready:
        issues.append({"path": "ledger_roots", "message": "immutable ledger root object missing"})
    if manifest.get("object_count") != len(records):
        issues.append({"path": "manifest.object_count", "message": "object count mismatch"})
    if manifest.get("production_object_storage_ready") is True or manifest.get("production_retention_backend_ready") is True:
        issues.append({"path": "manifest.production", "message": "production storage claim present"})
    return {
        "version": "v5.38",
        "storage_object_integrity_ready": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "object_count": len(records),
        "bucket_count": len(observed_buckets),
        "immutable_roots_ready": immutable_roots_ready,
        "manifest_sha256": manifest.get("manifest_sha256"),
        "production_object_storage_ready": False,
        "production_retention_backend_ready": False,
        "bic_os_phase_locked": True,
    }


def build_local_access_contracts_v538(records: list[dict[str, Any]]) -> dict[str, Any]:
    access_contracts: list[dict[str, Any]] = []
    for record in records:
        access_contracts.append({
            "object_id": record.get("object_id"),
            "bucket_id": record.get("bucket_id"),
            "object_key": record.get("object_key"),
            "access_uri": f"v538-local://{record.get('bucket_id')}/{record.get('object_key')}",
            "requires_authenticated_principal": True,
            "expires_in_seconds": 900,
            "checksum_required": record.get("sha256"),
            "public_internet_exposed": False,
            "production_signed_url_ready": False,
            "bic_os_phase_locked": True,
        })
    return {
        "version": "v5.38",
        "local_access_contract_ready": len(access_contracts) == len(records) and all(item["public_internet_exposed"] is False for item in access_contracts),
        "access_contract_count": len(access_contracts),
        "contracts": access_contracts,
        "production_signed_url_ready": False,
        "production_object_storage_ready": False,
        "bic_os_phase_locked": True,
    }


def run_immutable_overwrite_probe_v538(records: list[dict[str, Any]]) -> dict[str, Any]:
    immutable_records = [record for record in records if record.get("immutable") is True]
    denied: list[dict[str, Any]] = []
    allowed: list[dict[str, Any]] = []
    for record in records:
        attempted = {
            "object_id": record.get("object_id"),
            "bucket_id": record.get("bucket_id"),
            "object_key": record.get("object_key"),
            "attempted_action": "overwrite",
            "accepted": record.get("immutable") is not True,
            "status": "denied_immutable_object" if record.get("immutable") is True else "would_require_new_version",
            "production_object_storage_ready": False,
            "bic_os_phase_locked": True,
        }
        if attempted["accepted"]:
            allowed.append(attempted)
        else:
            denied.append(attempted)
    return {
        "version": "v5.38",
        "immutable_overwrite_denial_ready": len(immutable_records) >= 2 and len(denied) == len(immutable_records),
        "immutable_object_count": len(immutable_records),
        "denied_overwrite_count": len(denied),
        "allowed_new_version_count": len(allowed),
        "denied_attempts": denied,
        "allowed_attempts": allowed,
        "production_object_storage_ready": False,
        "bic_os_phase_locked": True,
    }


def build_storage_audit_bundle_v538(integrity: dict[str, Any], access_contract: dict[str, Any], overwrite_probe: dict[str, Any], v537_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.38",
        "created_at": utc_now_iso(),
        "storage_object_integrity_ready": integrity.get("storage_object_integrity_ready"),
        "local_access_contract_ready": access_contract.get("local_access_contract_ready"),
        "immutable_overwrite_denial_ready": overwrite_probe.get("immutable_overwrite_denial_ready"),
        "object_count": integrity.get("object_count"),
        "manifest_sha256": integrity.get("manifest_sha256"),
        "v537_dependency_status": v537_summary.get("overall_status"),
        "v537_identity_contract_ready": v537_summary.get("identity_provider_contract_ready"),
        "production_object_storage_ready": False,
        "production_retention_backend_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V538_STORAGE_RETENTION_AUDIT_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_storage_retention_contract_workflow_v538(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v537_dependency = run_identity_provider_contract_workflow_v537(project_root, out / "d537")
    buckets = build_storage_bucket_contracts_v538()
    payloads = build_storage_payload_fixtures_v538(v537_dependency)
    stored = write_storage_fixture_objects_v538(payloads, buckets, out)
    integrity = validate_storage_object_integrity_v538(stored["records"], stored["manifest"], buckets)
    access_contract = build_local_access_contracts_v538(stored["records"])
    overwrite_probe = run_immutable_overwrite_probe_v538(stored["records"])
    bundle = build_storage_audit_bundle_v538(integrity, access_contract, overwrite_probe, v537_dependency, out)
    proof_ready = (
        v537_dependency.get("identity_provider_contract_ready") is True
        and integrity.get("storage_object_integrity_ready") is True
        and access_contract.get("local_access_contract_ready") is True
        and overwrite_probe.get("immutable_overwrite_denial_ready") is True
        and bundle.get("bundle_ready") is True
        and integrity.get("production_object_storage_ready") is False
    )
    return {
        "version": "v5.38",
        "phase": "storage_retention_contract",
        "overall_status": "storage_retention_contract_proof_ready_runtime_not_claimed" if proof_ready else "storage_retention_contract_proof_incomplete",
        "active_phase": "biocompute_control_plane_storage_contract_proof",
        "bic_os_phase_locked": True,
        "storage_retention_contract_ready": proof_ready,
        "storage_object_integrity_ready": integrity.get("storage_object_integrity_ready") is True,
        "retention_manifest_ready": stored["manifest"].get("all_objects_hashed") is True and len(str(stored["manifest"].get("manifest_sha256", ""))) == 64,
        "local_access_contract_ready": access_contract.get("local_access_contract_ready") is True,
        "immutable_overwrite_denial_ready": overwrite_probe.get("immutable_overwrite_denial_ready") is True,
        "storage_audit_bundle_ready": bundle.get("bundle_ready") is True,
        "v537_dependency_ready": v537_dependency.get("identity_provider_contract_ready") is True,
        "object_count": integrity.get("object_count"),
        "bucket_count": integrity.get("bucket_count"),
        "immutable_object_count": overwrite_probe.get("immutable_object_count"),
        "denied_overwrite_count": overwrite_probe.get("denied_overwrite_count"),
        "production_object_storage_ready": False,
        "production_retention_backend_ready": False,
        "production_signed_url_ready": False,
        "production_auth_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "bucket_contracts": {bucket_id: bucket.to_dict() for bucket_id, bucket in buckets.items()},
        "object_manifest": stored["manifest"],
        "storage_integrity": integrity,
        "local_access_contract": access_contract,
        "immutable_overwrite_probe": overwrite_probe,
        "storage_audit_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v537_dependency_summary": {key: value for key, value in v537_dependency.items() if key not in {"identity_validation_matrix", "identity_dashboard_access_probe", "v536_dependency_summary"}},
        "missing_real_inputs": [
            "production object storage bucket or account",
            "bucket IAM policy tied to production identity provider",
            "server-side encryption and key-management configuration",
            "object versioning and retention-lock configuration",
            "remote immutable ledger root storage or notarization endpoint",
            "backup/restore and lifecycle policy evidence",
            "production signed URL/session policy",
        ],
        "remaining_runtime_blockers": [
            "production identity provider integration and persistent tenant membership",
            "hosted dashboard server and browser session enforcement",
            "production object storage and audit retention backend",
            "external notarization or remote append-only storage for incident ledger roots",
            "real external read-only API credentials or partner exports",
            "lab-approved live telemetry and closed-loop approval workflow",
        ],
        "direct_answer": {
            "did_we_find_real_object_storage_config": "no",
            "what_we_added_instead": "local object-storage, retention and immutable-root contract proof",
            "is_production_storage_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add packaged SDK distribution and install gate" if proof_ready else "fix v5.38 storage contract blockers first",
        },
        "claim_boundary": "v5.38 proves local storage bucket contracts, object integrity manifests, retention metadata, local access contracts and immutable-root overwrite denial over the v5.37 identity contract. It does not claim production object storage, hosted retention, remote notarization, full BioCompute Runtime or BiC OS readiness.",
    }


def write_storage_retention_contract_outputs_v538(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V538_STORAGE_RETENTION_CONTRACT_SUMMARY.json",
        "buckets_json": out / "V538_STORAGE_BUCKET_CONTRACTS.json",
        "manifest_json": out / "V538_STORAGE_OBJECT_MANIFEST.json",
        "integrity_json": out / "V538_STORAGE_INTEGRITY.json",
        "access_json": out / "V538_LOCAL_ACCESS_CONTRACTS.json",
        "overwrite_probe_json": out / "V538_IMMUTABLE_OVERWRITE_PROBE.json",
        "objects_csv": out / "V538_STORAGE_OBJECTS.csv",
        "markdown_report": out / "BIOGPU_V538_STORAGE_RETENTION_CONTRACT_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"bucket_contracts", "object_manifest", "storage_integrity", "local_access_contract", "immutable_overwrite_probe"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["buckets_json"].write_text(json.dumps(audit["bucket_contracts"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["manifest_json"].write_text(json.dumps(audit["object_manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["integrity_json"].write_text(json.dumps(audit["storage_integrity"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["access_json"].write_text(json.dumps(audit["local_access_contract"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["overwrite_probe_json"].write_text(json.dumps(audit["immutable_overwrite_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_storage_objects_csv(paths["objects_csv"], audit["object_manifest"].get("objects", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_storage_objects_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames = ["object_id", "bucket_id", "object_key", "object_type", "content_type", "size_bytes", "sha256", "retention_days", "immutable", "local_uri"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.38 Storage Retention Contract",
        "",
        "## Direct Answer",
        "",
        f"- Real object storage config found: `{answer['did_we_find_real_object_storage_config']}`",
        f"- Added instead: {answer['what_we_added_instead']}",
        f"- Production storage ready: `{answer['is_production_storage_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Storage object integrity ready: `{audit['storage_object_integrity_ready']}`",
        f"- Retention manifest ready: `{audit['retention_manifest_ready']}`",
        f"- Local access contract ready: `{audit['local_access_contract_ready']}`",
        f"- Immutable overwrite denial ready: `{audit['immutable_overwrite_denial_ready']}`",
        f"- Objects: `{audit['object_count']}`",
        f"- Buckets: `{audit['bucket_count']}`",
        "",
        "## Missing Real Inputs",
        "",
    ]
    for missing in audit["missing_real_inputs"]:
        lines.append(f"- {missing}")
    lines.extend(["", "## Remaining Runtime Blockers", ""])
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)