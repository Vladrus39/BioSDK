"""Tamper-evident incident ledger proof, v5.34."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.beta.job_model_v43 import utc_now_iso
from biogpu.evidence.ledger_v53 import local_signature, stable_hash
from biogpu.runtime.incident_workflow_v533 import run_operator_incident_retention_workflow_v533


DEFAULT_OUT = Path("outputs/v534_tamper_evident_incident_ledger")
LOCAL_INCIDENT_LEDGER_SIGNING_KEY_V534 = "BIOGPU_CORE_LOCAL_INCIDENT_LEDGER_INTEGRITY_V534"


@dataclass(frozen=True)
class IncidentLedgerEntryV534:
    entry_index: int
    entry_id: str
    created_at: str
    record_type: str
    source_id: str
    source_version: str
    payload_sha256: str
    previous_entry_hash: str | None
    entry_hash: str
    local_signature: str
    production_incident_ledger_ready: bool = False
    bic_os_phase_locked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _entry_payload(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key not in {"entry_hash", "local_signature"}}


def _payload_hash(payload: Any) -> str:
    return stable_hash(payload)


def _source_record(record_type: str, source_id: str, payload: dict[str, Any], source_version: str = "v5.33") -> dict[str, Any]:
    return {"record_type": record_type, "source_id": source_id, "source_version": source_version, "payload": payload}


def build_incident_ledger_source_records_v534(v533_audit: dict[str, Any]) -> list[dict[str, Any]]:
    timeline = v533_audit.get("timeline", {})
    retention_manifest = v533_audit.get("retention_manifest", {})
    incident_audit_bundle = v533_audit.get("incident_audit_bundle", {})
    opened = timeline.get("opened_incident", {})
    acknowledgement = timeline.get("acknowledgement_action", {})
    resolution = timeline.get("resolution_action", {})
    active_incident_id = str(v533_audit.get("active_incident_id") or opened.get("incident_id") or "incident_unknown")
    return [
        _source_record("incident_opened", active_incident_id, opened),
        _source_record("operator_acknowledged", str(acknowledgement.get("action_id") or "acknowledgement_unknown"), acknowledgement),
        _source_record("incident_resolved", str(resolution.get("action_id") or "resolution_unknown"), resolution),
        _source_record("incident_retention_manifest", str(retention_manifest.get("manifest_sha256") or "retention_manifest_unknown"), retention_manifest),
        _source_record("incident_audit_bundle", str(incident_audit_bundle.get("bundle_sha256") or "incident_bundle_unknown"), incident_audit_bundle),
    ]


def create_incident_ledger_entry_v534(record: dict[str, Any], entry_index: int, previous_entry_hash: str | None = None, signing_key: str = LOCAL_INCIDENT_LEDGER_SIGNING_KEY_V534) -> IncidentLedgerEntryV534:
    payload_sha256 = _payload_hash(record.get("payload", {}))
    entry_base = {
        "entry_index": entry_index,
        "entry_id": f"incident-ledger-{entry_index:04d}-{payload_sha256[:12]}",
        "created_at": utc_now_iso(),
        "record_type": str(record.get("record_type")),
        "source_id": str(record.get("source_id")),
        "source_version": str(record.get("source_version", "v5.33")),
        "payload_sha256": payload_sha256,
        "previous_entry_hash": previous_entry_hash,
        "production_incident_ledger_ready": False,
        "bic_os_phase_locked": True,
    }
    entry_hash = stable_hash(entry_base)
    return IncidentLedgerEntryV534(**entry_base, entry_hash=entry_hash, local_signature=local_signature(entry_hash, signing_key))


def build_incident_ledger_v534(v533_audit: dict[str, Any], signing_key: str = LOCAL_INCIDENT_LEDGER_SIGNING_KEY_V534) -> dict[str, Any]:
    source_records = build_incident_ledger_source_records_v534(v533_audit)
    entries: list[dict[str, Any]] = []
    previous_hash: str | None = None
    for index, record in enumerate(source_records):
        entry = create_incident_ledger_entry_v534(record, index, previous_hash, signing_key).to_dict()
        entries.append(entry)
        previous_hash = entry["entry_hash"]
    chain_root = stable_hash([entry["entry_hash"] for entry in entries])
    retention_manifest = v533_audit.get("retention_manifest", {})
    incident_audit_bundle = v533_audit.get("incident_audit_bundle", {})
    return {
        "ledger_id": "BIOGPU_CORE_V534_INCIDENT_LEDGER",
        "version": "v5.34",
        "created_at": utc_now_iso(),
        "entry_count": len(entries),
        "chain_root": chain_root,
        "entries": entries,
        "source_records": source_records,
        "retention_manifest_sha256": retention_manifest.get("manifest_sha256"),
        "incident_audit_bundle_sha256": incident_audit_bundle.get("bundle_sha256"),
        "production_incident_ledger_ready": False,
        "bic_os_phase_locked": True,
    }


def validate_incident_ledger_chain_v534(ledger: dict[str, Any], signing_key: str = LOCAL_INCIDENT_LEDGER_SIGNING_KEY_V534) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    previous_hash: str | None = None
    entry_hashes: list[str] = []
    entries = list(ledger.get("entries", []))
    source_records = list(ledger.get("source_records", []))
    if len(entries) != len(source_records):
        issues.append({"path": "source_records", "message": "source record count does not match entry count"})
    for index, entry in enumerate(entries):
        if entry.get("entry_index") != index:
            issues.append({"path": f"entries[{index}].entry_index", "message": "entry index mismatch"})
        if entry.get("previous_entry_hash") != previous_hash:
            issues.append({"path": f"entries[{index}].previous_entry_hash", "message": "previous hash chain mismatch"})
        recomputed_hash = stable_hash(_entry_payload(entry))
        if entry.get("entry_hash") != recomputed_hash:
            issues.append({"path": f"entries[{index}].entry_hash", "message": "entry hash mismatch"})
        expected_signature = local_signature(str(entry.get("entry_hash", "")), signing_key)
        if entry.get("local_signature") != expected_signature:
            issues.append({"path": f"entries[{index}].local_signature", "message": "local signature mismatch"})
        if index < len(source_records):
            record = source_records[index]
            if record.get("record_type") != entry.get("record_type") or record.get("source_id") != entry.get("source_id"):
                issues.append({"path": f"source_records[{index}]", "message": "source record identity mismatch"})
            payload_hash = _payload_hash(record.get("payload", {}))
            if entry.get("payload_sha256") != payload_hash:
                issues.append({"path": f"source_records[{index}].payload", "message": "source payload hash mismatch"})
        previous_hash = str(entry.get("entry_hash"))
        entry_hashes.append(str(entry.get("entry_hash")))
    expected_root = stable_hash(entry_hashes)
    if ledger.get("chain_root") != expected_root:
        issues.append({"path": "chain_root", "message": "chain root mismatch"})
    retention_anchor_ready = any(entry.get("record_type") == "incident_retention_manifest" and entry.get("source_id") == ledger.get("retention_manifest_sha256") for entry in entries)
    if not retention_anchor_ready:
        issues.append({"path": "retention_manifest_sha256", "message": "retention manifest anchor missing"})
    return {
        "version": "v5.34",
        "valid": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "entry_count": len(entries),
        "chain_root": ledger.get("chain_root"),
        "retention_manifest_anchored": retention_anchor_ready,
        "local_signature_validation_ready": not any("local_signature" in issue["path"] for issue in issues),
        "production_incident_ledger_ready": False,
        "bic_os_phase_locked": True,
    }


def run_incident_ledger_tamper_probe_v534(ledger: dict[str, Any]) -> dict[str, Any]:
    tampered = json.loads(json.dumps(ledger, ensure_ascii=False))
    records = tampered.get("source_records", [])
    if len(records) > 1:
        payload = dict(records[1].get("payload") or {})
        payload["note"] = "tampered_after_ledger_commit"
        records[1]["payload"] = payload
    validation = validate_incident_ledger_chain_v534(tampered)
    return {
        "version": "v5.34",
        "tamper_probe_ready": validation["valid"] is False,
        "tampered_validation_valid": validation["valid"],
        "detected_issue_count": validation["issue_count"],
        "detected_issues": validation["issues"],
        "production_incident_ledger_ready": False,
        "bic_os_phase_locked": True,
    }


def build_incident_ledger_bundle_v534(ledger: dict[str, Any], validation: dict[str, Any], tamper_probe: dict[str, Any], v533_summary: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bundle = {
        "version": "v5.34",
        "created_at": utc_now_iso(),
        "ledger_id": ledger.get("ledger_id"),
        "entry_count": ledger.get("entry_count"),
        "chain_root": ledger.get("chain_root"),
        "retention_manifest_sha256": ledger.get("retention_manifest_sha256"),
        "incident_audit_bundle_sha256": ledger.get("incident_audit_bundle_sha256"),
        "validation": validation,
        "tamper_probe": tamper_probe,
        "v533_dependency_status": v533_summary.get("overall_status"),
        "production_incident_ledger_ready": False,
        "bic_os_phase_locked": True,
    }
    bundle_hash = stable_hash(bundle)
    bundle["bundle_sha256"] = bundle_hash
    path = out / "V534_INCIDENT_LEDGER_BUNDLE.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"bundle_path": str(path).replace("\\", "/"), "bundle_sha256": bundle_hash, "bundle_ready": path.exists() and len(bundle_hash) == 64, "bundle": bundle}


def run_tamper_evident_incident_ledger_workflow_v534(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    project_root = Path(root).resolve()
    out = project_root / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v533_dependency = run_operator_incident_retention_workflow_v533(project_root, out / "d533")
    ledger = build_incident_ledger_v534(v533_dependency)
    validation = validate_incident_ledger_chain_v534(ledger)
    tamper_probe = run_incident_ledger_tamper_probe_v534(ledger)
    bundle = build_incident_ledger_bundle_v534(ledger, validation, tamper_probe, v533_dependency, out)
    proof_ready = (
        v533_dependency.get("operator_incident_retention_ready") is True
        and validation.get("valid") is True
        and validation.get("retention_manifest_anchored") is True
        and tamper_probe.get("tamper_probe_ready") is True
        and bundle.get("bundle_ready") is True
        and v533_dependency.get("production_incident_retention_ready") is False
        and ledger.get("production_incident_ledger_ready") is False
    )
    return {
        "version": "v5.34",
        "phase": "tamper_evident_incident_ledger",
        "overall_status": "tamper_evident_incident_ledger_proof_ready_runtime_not_claimed" if proof_ready else "tamper_evident_incident_ledger_proof_incomplete",
        "active_phase": "biocompute_runtime_incident_ledger_proof",
        "bic_os_phase_locked": True,
        "tamper_evident_incident_ledger_ready": proof_ready,
        "incident_ledger_chain_valid": validation.get("valid") is True,
        "local_signature_validation_ready": validation.get("local_signature_validation_ready") is True,
        "retention_manifest_anchored": validation.get("retention_manifest_anchored") is True,
        "tamper_detection_passed": tamper_probe.get("tamper_probe_ready") is True,
        "incident_ledger_bundle_ready": bundle.get("bundle_ready") is True,
        "v533_dependency_ready": v533_dependency.get("operator_incident_retention_ready") is True,
        "entry_count": ledger.get("entry_count"),
        "chain_root": ledger.get("chain_root"),
        "retention_manifest_sha256": ledger.get("retention_manifest_sha256"),
        "incident_audit_bundle_sha256": ledger.get("incident_audit_bundle_sha256"),
        "production_incident_ledger_ready": False,
        "production_incident_retention_ready": False,
        "production_recovery_ready": False,
        "production_runtime_ready": False,
        "production_api_ready": False,
        "production_biocompute_runtime_ready": False,
        "full_biosdk_ready": False,
        "live_actuation_enabled": False,
        "ledger": ledger,
        "ledger_validation": validation,
        "tamper_probe": tamper_probe,
        "incident_ledger_bundle": {key: value for key, value in bundle.items() if key != "bundle"},
        "v533_dependency_summary": {key: value for key, value in v533_dependency.items() if key not in {"timeline", "v532_dependency_summary"}},
        "remaining_runtime_blockers": [
            "external notarization or remote append-only storage for incident ledger roots",
            "tenant-aware operator roles and incident permissions",
            "hosted incident dashboards and paging integrations",
            "production monitor loop and production alert routing",
            "production multi-worker retry orchestration with durable backoff timers",
            "process crash supervision instead of deterministic timeout fixtures",
        ],
        "direct_answer": {
            "did_we_add_tamper_evident_incident_ledger": "yes" if validation.get("valid") else "not_yet",
            "did_we_anchor_retention_manifest": "yes" if validation.get("retention_manifest_anchored") else "not_yet",
            "did_we_add_tamper_detection_probe": "yes" if tamper_probe.get("tamper_probe_ready") else "not_yet",
            "is_production_incident_ledger_ready": "no",
            "is_biocompute_runtime_ready": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "add tenant-aware operator roles and permissions proof" if proof_ready else "fix v5.34 incident ledger blockers first",
        },
        "claim_boundary": "v5.34 proves a local append-only incident ledger with chained hashes, local HMAC-style signatures, retention-manifest anchoring and tamper detection over the v5.33 incident workflow. It does not claim production notarization, hosted append-only storage, tenant permissions, full BioCompute Runtime or BiC OS readiness.",
    }


def write_tamper_evident_incident_ledger_outputs_v534(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V534_TAMPER_EVIDENT_INCIDENT_LEDGER_SUMMARY.json",
        "ledger_json": out / "V534_INCIDENT_LEDGER.json",
        "validation_json": out / "V534_INCIDENT_LEDGER_VALIDATION.json",
        "tamper_probe_json": out / "V534_INCIDENT_LEDGER_TAMPER_PROBE.json",
        "entries_csv": out / "V534_INCIDENT_LEDGER_ENTRIES.csv",
        "markdown_report": out / "BIOGPU_V534_TAMPER_EVIDENT_INCIDENT_LEDGER_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"ledger"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["ledger_json"].write_text(json.dumps(audit["ledger"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["validation_json"].write_text(json.dumps(audit["ledger_validation"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["tamper_probe_json"].write_text(json.dumps(audit["tamper_probe"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_entries_csv(paths["entries_csv"], audit["ledger"].get("entries", []))
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_entries_csv(path: Path, entries: list[dict[str, Any]]) -> None:
    fieldnames = ["entry_index", "entry_id", "record_type", "source_id", "payload_sha256", "previous_entry_hash", "entry_hash"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow({field: entry.get(field) for field in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.34 Tamper-Evident Incident Ledger",
        "",
        "## Direct Answer",
        "",
        f"- Tamper-evident incident ledger: `{answer['did_we_add_tamper_evident_incident_ledger']}`",
        f"- Retention manifest anchored: `{answer['did_we_anchor_retention_manifest']}`",
        f"- Tamper detection probe: `{answer['did_we_add_tamper_detection_probe']}`",
        f"- Production incident ledger ready: `{answer['is_production_incident_ledger_ready']}`",
        f"- BioCompute Runtime ready: `{answer['is_biocompute_runtime_ready']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Proof Summary",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Entry count: `{audit['entry_count']}`",
        f"- Chain valid: `{audit['incident_ledger_chain_valid']}`",
        f"- Signature validation ready: `{audit['local_signature_validation_ready']}`",
        f"- Retention manifest anchored: `{audit['retention_manifest_anchored']}`",
        f"- Tamper detection passed: `{audit['tamper_detection_passed']}`",
        f"- Chain root: `{audit['chain_root']}`",
        "",
        "## Remaining Runtime Blockers",
        "",
    ]
    for blocker in audit["remaining_runtime_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)