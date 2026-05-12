"""Evidence ledger and result-bundle validation for v5.3."""
from __future__ import annotations

import hmac
import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


LOCAL_LEDGER_SIGNING_KEY_V53 = "BIOGPU_CORE_LOCAL_LEDGER_INTEGRITY_V53"


@dataclass(frozen=True)
class EvidenceBundleIssue:
    level: str
    path: str
    message: str


@dataclass(frozen=True)
class EvidenceBundleArtifact:
    path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class EvidenceBundleValidationReport:
    bundle_path: str
    valid: bool
    validation_level: str
    bundle_sha256: str | None
    bundle_size_bytes: int | None
    manifest_kind: str | None
    manifest_name: str | None
    zip_entry_count: int
    artifact_count: int
    issues: list[EvidenceBundleIssue] = field(default_factory=list)
    artifacts: list[EvidenceBundleArtifact] = field(default_factory=list)
    checks: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceLedgerEntry:
    entry_id: str
    created_utc: str
    bundle_path: str
    bundle_sha256: str
    bundle_size_bytes: int
    validation_status: str
    validation_level: str
    manifest_kind: str | None
    artifact_count: int
    issue_count: int
    previous_entry_hash: str | None
    entry_hash: str
    local_signature: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceLedger:
    ledger_id: str
    version: str
    created_utc: str
    entry_count: int
    chain_root: str
    entries: list[EvidenceLedgerEntry]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["entries"] = [entry.to_dict() for entry in self.entries]
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(data: Any) -> str:
    return sha256_bytes(canonical_json(data).encode("utf-8"))


def _issue(level: str, path: str, message: str) -> EvidenceBundleIssue:
    return EvidenceBundleIssue(level=level, path=path, message=message)


def _safe_zip_name(name: str) -> bool:
    if "\\" in name:
        return False
    pure = PurePosixPath(name)
    return not pure.is_absolute() and ".." not in pure.parts and bool(str(pure))


def _zip_member_bytes(bundle: zipfile.ZipFile, name: str) -> bytes:
    with bundle.open(name) as stream:
        return stream.read()


def _zip_json(bundle: zipfile.ZipFile, name: str) -> dict[str, Any]:
    data = _zip_member_bytes(bundle, name).decode("utf-8-sig")
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must be a JSON object")
    return payload


def validate_evidence_bundle(bundle_path: str | Path) -> EvidenceBundleValidationReport:
    path = Path(bundle_path)
    issues: list[EvidenceBundleIssue] = []
    artifacts: list[EvidenceBundleArtifact] = []
    checks: dict[str, Any] = {}

    if not path.exists():
        return EvidenceBundleValidationReport(
            bundle_path=str(path),
            valid=False,
            validation_level="missing_bundle",
            bundle_sha256=None,
            bundle_size_bytes=None,
            manifest_kind=None,
            manifest_name=None,
            zip_entry_count=0,
            artifact_count=0,
            issues=[_issue("error", str(path), "bundle file is missing")],
        )
    if not zipfile.is_zipfile(path):
        return EvidenceBundleValidationReport(
            bundle_path=str(path),
            valid=False,
            validation_level="not_zip",
            bundle_sha256=sha256_file(path),
            bundle_size_bytes=path.stat().st_size,
            manifest_kind=None,
            manifest_name=None,
            zip_entry_count=0,
            artifact_count=0,
            issues=[_issue("error", str(path), "bundle is not a valid zip file")],
        )

    manifest_kind: str | None = None
    manifest_name: str | None = None
    with zipfile.ZipFile(path) as bundle:
        infos = [info for info in bundle.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            issues.append(_issue("error", "$zip", "duplicate zip entries: " + ", ".join(duplicates)))
        for info in infos:
            if not _safe_zip_name(info.filename):
                issues.append(_issue("error", info.filename, "unsafe zip member path"))
                continue
            data = _zip_member_bytes(bundle, info.filename)
            artifacts.append(EvidenceBundleArtifact(info.filename, info.file_size, sha256_bytes(data)))

        names_set = set(names)
        if "V50_PC_VALIDATION_BUNDLE_MANIFEST.json" in names_set:
            manifest_kind = "v50_pc_validation_bundle"
            manifest_name = "V50_PC_VALIDATION_BUNDLE_MANIFEST.json"
            _validate_v50_manifest(bundle, manifest_name, names_set, issues, checks)
        elif "run_manifest.json" in names_set:
            manifest_kind = "v24_result_bundle"
            manifest_name = "run_manifest.json"
            _validate_v24_bundle(bundle, names_set, issues, checks)
        else:
            issues.append(_issue("error", "$manifest", "no recognized evidence manifest found"))

    valid = not any(issue.level == "error" for issue in issues)
    if valid and manifest_kind:
        validation_level = "manifest_and_checksums_validated"
    elif valid:
        validation_level = "zip_validated"
    else:
        validation_level = "failed"
    return EvidenceBundleValidationReport(
        bundle_path=str(path),
        valid=valid,
        validation_level=validation_level,
        bundle_sha256=sha256_file(path),
        bundle_size_bytes=path.stat().st_size,
        manifest_kind=manifest_kind,
        manifest_name=manifest_name,
        zip_entry_count=len(artifacts),
        artifact_count=len(artifacts),
        issues=issues,
        artifacts=artifacts,
        checks=checks,
    )


def _validate_v50_manifest(
    bundle: zipfile.ZipFile,
    manifest_name: str,
    names_set: set[str],
    issues: list[EvidenceBundleIssue],
    checks: dict[str, Any],
) -> None:
    try:
        manifest = _zip_json(bundle, manifest_name)
    except Exception as exc:
        issues.append(_issue("error", manifest_name, f"manifest JSON failed to parse: {exc}"))
        return
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        issues.append(_issue("error", f"{manifest_name}.artifacts", "v50 manifest must contain non-empty artifacts list"))
        return
    expected_count = manifest.get("artifact_count")
    if expected_count != len(artifacts):
        issues.append(_issue("error", f"{manifest_name}.artifact_count", "artifact_count does not match artifacts list length"))
    checked = 0
    for item in artifacts:
        if not isinstance(item, dict):
            issues.append(_issue("error", f"{manifest_name}.artifacts", "artifact record must be an object"))
            continue
        rel = item.get("path")
        member = f"artifacts/{rel}" if rel else ""
        if not rel or member not in names_set:
            issues.append(_issue("error", member or f"{manifest_name}.artifacts", "declared artifact is missing from bundle"))
            continue
        data = _zip_member_bytes(bundle, member)
        actual_hash = sha256_bytes(data)
        actual_size = len(data)
        if item.get("sha256") != actual_hash:
            issues.append(_issue("error", member, "declared sha256 does not match bundled artifact"))
        if item.get("size_bytes") != actual_size:
            issues.append(_issue("error", member, "declared size_bytes does not match bundled artifact"))
        checked += 1
    checks["declared_artifacts"] = len(artifacts)
    checks["checked_artifacts"] = checked


def _validate_v24_bundle(
    bundle: zipfile.ZipFile,
    names_set: set[str],
    issues: list[EvidenceBundleIssue],
    checks: dict[str, Any],
) -> None:
    required = ["run_manifest.json", "audit_log.jsonl", "session_summary.json"]
    for name in required:
        if name not in names_set:
            issues.append(_issue("error", name, "required v24 bundle artifact is missing"))
    if "audit_log.jsonl" in names_set and not _zip_member_bytes(bundle, "audit_log.jsonl").strip():
        issues.append(_issue("error", "audit_log.jsonl", "audit log must not be empty"))
    if "session_summary.json" in names_set:
        try:
            summary = _zip_json(bundle, "session_summary.json")
            if not summary.get("session_id"):
                issues.append(_issue("error", "session_summary.json.session_id", "session_id is required"))
            if not summary.get("result_bundle"):
                issues.append(_issue("warning", "session_summary.json.result_bundle", "result_bundle field is empty"))
            checks["session_status"] = summary.get("status")
        except Exception as exc:
            issues.append(_issue("error", "session_summary.json", f"session summary failed to parse: {exc}"))
    checks["required_artifacts"] = required


def local_signature(entry_hash: str, signing_key: str = LOCAL_LEDGER_SIGNING_KEY_V53) -> str:
    return hmac.new(signing_key.encode("utf-8"), entry_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def _entry_payload(entry: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in entry.items() if k not in {"entry_hash", "local_signature"}}


def create_ledger_entry(
    report: EvidenceBundleValidationReport,
    previous_entry_hash: str | None = None,
    signing_key: str = LOCAL_LEDGER_SIGNING_KEY_V53,
) -> EvidenceLedgerEntry:
    if report.bundle_sha256 is None or report.bundle_size_bytes is None:
        raise ValueError("cannot ledger a missing bundle")
    payload = {
        "entry_id": f"ledger-{report.bundle_sha256[:12]}",
        "created_utc": utc_now(),
        "bundle_path": report.bundle_path,
        "bundle_sha256": report.bundle_sha256,
        "bundle_size_bytes": report.bundle_size_bytes,
        "validation_status": "valid" if report.valid else "invalid",
        "validation_level": report.validation_level,
        "manifest_kind": report.manifest_kind,
        "artifact_count": report.artifact_count,
        "issue_count": len(report.issues),
        "previous_entry_hash": previous_entry_hash,
    }
    entry_hash = stable_hash(payload)
    return EvidenceLedgerEntry(**payload, entry_hash=entry_hash, local_signature=local_signature(entry_hash, signing_key))


def build_evidence_ledger(
    reports: list[EvidenceBundleValidationReport],
    ledger_id: str = "BIOGPU_CORE_V53_EVIDENCE_LEDGER",
    signing_key: str = LOCAL_LEDGER_SIGNING_KEY_V53,
) -> EvidenceLedger:
    entries: list[EvidenceLedgerEntry] = []
    previous_hash: str | None = None
    for report in sorted(reports, key=lambda item: item.bundle_path):
        if report.bundle_sha256 is None:
            continue
        entry = create_ledger_entry(report, previous_hash, signing_key)
        entries.append(entry)
        previous_hash = entry.entry_hash
    chain_root = stable_hash([entry.entry_hash for entry in entries]) if entries else stable_hash([])
    return EvidenceLedger(
        ledger_id=ledger_id,
        version="v5.3",
        created_utc=utc_now(),
        entry_count=len(entries),
        chain_root=chain_root,
        entries=entries,
    )


def validate_ledger_chain(
    ledger: EvidenceLedger | dict[str, Any],
    signing_key: str = LOCAL_LEDGER_SIGNING_KEY_V53,
) -> dict[str, Any]:
    data = ledger.to_dict() if isinstance(ledger, EvidenceLedger) else ledger
    issues: list[dict[str, str]] = []
    previous_hash: str | None = None
    entry_hashes: list[str] = []
    for index, entry in enumerate(data.get("entries", [])):
        if entry.get("previous_entry_hash") != previous_hash:
            issues.append({"path": f"entries[{index}].previous_entry_hash", "message": "previous hash chain mismatch"})
        recomputed_hash = stable_hash(_entry_payload(entry))
        if entry.get("entry_hash") != recomputed_hash:
            issues.append({"path": f"entries[{index}].entry_hash", "message": "entry hash mismatch"})
        expected_signature = local_signature(entry.get("entry_hash", ""), signing_key)
        if entry.get("local_signature") != expected_signature:
            issues.append({"path": f"entries[{index}].local_signature", "message": "local signature mismatch"})
        previous_hash = entry.get("entry_hash")
        entry_hashes.append(entry.get("entry_hash", ""))
    expected_root = stable_hash(entry_hashes)
    if data.get("chain_root") != expected_root:
        issues.append({"path": "chain_root", "message": "chain root mismatch"})
    return {"valid": not issues, "issue_count": len(issues), "issues": issues, "entry_count": len(entry_hashes)}
