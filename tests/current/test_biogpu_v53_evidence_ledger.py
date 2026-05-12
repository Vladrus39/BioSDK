from __future__ import annotations

import json
import zipfile
from pathlib import Path

from biogpu.benchmarks.biogpu_v53_evidence_ledger import run
from biogpu.evidence.ledger_v53 import (
    build_evidence_ledger,
    local_signature,
    sha256_bytes,
    validate_evidence_bundle,
    validate_ledger_chain,
)


def _write_v50_like_bundle(root: Path, bad_hash: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    readme = b"# example\n"
    summary = b'{"status":"ok"}\n'
    artifacts = [
        {"path": "README.md", "category": "project_entry", "required": True, "size_bytes": len(readme), "sha256": sha256_bytes(readme)},
        {"path": "outputs/example.json", "category": "validation_output", "required": True, "size_bytes": len(summary), "sha256": sha256_bytes(summary)},
    ]
    if bad_hash:
        artifacts[1]["sha256"] = "0" * 64
    manifest = {
        "bundle_id": "BIOGPU_CORE_V50_PC_VALIDATION_BUNDLE",
        "version": "v5.0",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    bundle_path = root / "bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("V50_PC_VALIDATION_BUNDLE_MANIFEST.json", json.dumps(manifest))
        bundle.writestr("artifacts/README.md", readme)
        bundle.writestr("artifacts/outputs/example.json", summary)
    return bundle_path


def test_v53_validates_v50_like_bundle(tmp_path):
    report = validate_evidence_bundle(_write_v50_like_bundle(tmp_path))
    assert report.valid is True
    assert report.manifest_kind == "v50_pc_validation_bundle"
    assert report.checks["checked_artifacts"] == 2


def test_v53_detects_manifest_checksum_mismatch(tmp_path):
    report = validate_evidence_bundle(_write_v50_like_bundle(tmp_path, bad_hash=True))
    assert report.valid is False
    assert any("sha256" in issue.message for issue in report.issues)


def test_v53_detects_unsafe_zip_member_path(tmp_path):
    bundle_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("../escape.json", "{}")
    report = validate_evidence_bundle(bundle_path)
    assert report.valid is False
    assert any(issue.path == "../escape.json" for issue in report.issues)


def test_v53_builds_and_validates_ledger_chain(tmp_path):
    first = validate_evidence_bundle(_write_v50_like_bundle(tmp_path / "a"))
    second = validate_evidence_bundle(_write_v50_like_bundle(tmp_path / "b"))
    ledger = build_evidence_ledger([first, second])
    assert ledger.entry_count == 2
    assert ledger.entries[1].previous_entry_hash == ledger.entries[0].entry_hash
    assert validate_ledger_chain(ledger)["valid"] is True


def test_v53_local_signature_is_hmac_sha256():
    signature = local_signature("abc")
    assert len(signature) == 64
    assert signature == local_signature("abc")
    assert signature != local_signature("def")


def test_v53_runner_writes_summary_and_reference_bundle(tmp_path):
    summary = run(project_root=tmp_path, out_dir=tmp_path / "out")
    assert summary["milestone"] == "v5.3"
    assert summary["gate"]["reference_bundle_validated"] is True
    assert summary["gate"]["ledger_chain_validated"] is True
    assert (tmp_path / "out" / "V53_EVIDENCE_LEDGER.json").exists()
    assert (tmp_path / "out" / "reference_v24_session" / "biogpu_v24_result_bundle.zip").exists()
