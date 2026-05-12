"""BioSDK release-candidate evidence package, v5.25."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/v525_biosdk_release_candidate_evidence")
SDK_NAME = "BioSDK / Living Compute SDK"
RC_LABEL = "biosdk_rc_evidence_v5.25"


@dataclass(frozen=True)
class BioSDKReleaseCandidateItemV525:
    item_id: str
    title: str
    package_layer: str
    status: str
    proof_level: str
    required_for_rc_evidence: bool
    artifacts: tuple[str, ...]
    blockers: tuple[str, ...]
    allowed_statement: str
    forbidden_statement: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def _artifact(root: Path, relative_path: str) -> tuple[str, bool, dict[str, Any]]:
    path = root / relative_path
    return relative_path, path.exists(), _read_json(path) if path.suffix.lower() == ".json" else {}


def _present(paths: tuple[tuple[str, bool, dict[str, Any]], ...]) -> tuple[str, ...]:
    return tuple(path for path, exists, _ in paths if exists)


def _missing(paths: tuple[tuple[str, bool, dict[str, Any]], ...]) -> tuple[str, ...]:
    return tuple(path for path, exists, _ in paths if not exists)


def _ready_item(
    item_id: str,
    title: str,
    package_layer: str,
    proof_level_ready: str,
    required_for_rc_evidence: bool,
    artifacts: tuple[tuple[str, bool, dict[str, Any]], ...],
    condition: bool,
    missing_reason: str,
    allowed_statement: str,
    forbidden_statement: str,
) -> BioSDKReleaseCandidateItemV525:
    blockers = list(_missing(artifacts))
    if not condition:
        blockers.append(missing_reason)
    return BioSDKReleaseCandidateItemV525(
        item_id=item_id,
        title=title,
        package_layer=package_layer,
        status="ready" if not blockers else "blocked",
        proof_level=proof_level_ready if not blockers else "missing_or_incomplete",
        required_for_rc_evidence=required_for_rc_evidence,
        artifacts=_present(artifacts),
        blockers=tuple(blockers),
        allowed_statement=allowed_statement,
        forbidden_statement=forbidden_statement,
    )


def build_biosdk_release_candidate_items_v525(root: str | Path = ".") -> tuple[BioSDKReleaseCandidateItemV525, ...]:
    project_root = Path(root)
    v512 = _artifact(project_root, "outputs/v512_biosdk_evidence_pack/V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json")
    v513 = _artifact(project_root, "outputs/v513_biosdk_core_api/V513_BIOSDK_CORE_API_SUMMARY.json")
    v514 = _artifact(project_root, "outputs/v514_sample_acquisition_gate/V514_SAMPLE_ACQUISITION_SUMMARY.json")
    v521 = _artifact(project_root, "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json")
    v522 = _artifact(project_root, "outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json")
    v523 = _artifact(project_root, "outputs/v523_user_upload_fixture/V523_USER_UPLOAD_FIXTURE_SUMMARY.json")
    v524 = _artifact(project_root, "outputs/v524_external_export_validation/V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json")
    readme = _artifact(project_root, "README.md")
    master_plan = _artifact(project_root, "docs/MASTER_PROJECT_PLAN_V50.md")
    external_guide = _artifact(project_root, "docs/EXTERNAL_EXPORT_VALIDATION_GUIDE_V524.md")
    rc_guide = _artifact(project_root, "docs/BIOSDK_RELEASE_CANDIDATE_EVIDENCE_GUIDE_V525.md")
    module = _artifact(project_root, "biogpu/sdk/release_candidate_evidence_v525.py")
    runner = _artifact(project_root, "biogpu/benchmarks/biogpu_v525_biosdk_release_candidate_evidence.py")
    script = _artifact(project_root, "scripts/run_biogpu_v525_biosdk_release_candidate_evidence.ps1")
    tests = _artifact(project_root, "tests/current/test_biogpu_v525_biosdk_release_candidate_evidence.py")
    example = _artifact(project_root, "examples/biosdk_v525_release_candidate_evidence.py")

    v512_json = v512[2]
    v513_json = v513[2]
    v514_json = v514[2]
    v521_json = v521[2]
    v522_json = v522[2]
    v523_json = v523[2]
    v524_json = v524[2]

    evidence_kernel_ready = bool(v512_json.get("biosdk_evidence_kernel_ready")) and v512_json.get("full_biosdk_ready") is False
    core_api_ready = bool(v513[1]) and str(v513_json.get("overall_status", "")).startswith("biosdk_core_api")
    sample_proof_ready = bool(v514_json.get("full_sample_proof_ready")) and not v514_json.get("missing_required_sample_ids")
    cross_dataset_ready = (
        bool(v521_json.get("public_cross_dataset_evidence_ready"))
        and bool(v521_json.get("external_partner_evidence_ready"))
        and bool(v521_json.get("vendor_user_evidence_ready"))
        and v521_json.get("full_biosdk_ready") is False
    )
    examples_ready = bool(v522_json.get("public_examples_ready")) and int(v522_json.get("blocked_example_count", 1) or 0) == 0 and v522_json.get("full_biosdk_ready") is False
    user_upload_ready = bool(v523_json.get("user_upload_validated")) and bool(v523_json.get("safety_scan_passed"))
    external_export_ready = bool(v524_json.get("real_external_ready")) and int(v524_json.get("validated_export_count", 0) or 0) >= 1
    docs_ready = all(_exists(project_root, path) for path in ("README.md", "docs/MASTER_PROJECT_PLAN_V50.md", "docs/EXTERNAL_EXPORT_VALIDATION_GUIDE_V524.md", "docs/BIOSDK_RELEASE_CANDIDATE_EVIDENCE_GUIDE_V525.md"))
    v525_surface_ready = all(_exists(project_root, path) for path in (
        "biogpu/sdk/release_candidate_evidence_v525.py",
        "biogpu/benchmarks/biogpu_v525_biosdk_release_candidate_evidence.py",
        "scripts/run_biogpu_v525_biosdk_release_candidate_evidence.ps1",
        "tests/current/test_biogpu_v525_biosdk_release_candidate_evidence.py",
        "examples/biosdk_v525_release_candidate_evidence.py",
    ))

    return (
        _ready_item(
            "v512_evidence_kernel",
            "BioSDK evidence kernel",
            "evidence_foundation",
            "local_evidence_kernel_ready",
            True,
            (v512,),
            evidence_kernel_ready,
            "v5.12 evidence kernel summary is missing, incomplete or overclaims full SDK readiness",
            "BioSDK has a local evidence-kernel package with clear gaps.",
            "BioSDK is fully production-ready because v5.12 exists.",
        ),
        _ready_item(
            "v513_core_api",
            "BioSDK core API facade",
            "sdk_api",
            "safe_local_facade_ready",
            True,
            (v513,),
            core_api_ready,
            "v5.13 core API summary is missing or not active",
            "BioSDK has a safe local facade for replay, NSI validation and queue admission.",
            "The facade is a durable production runtime service.",
        ),
        _ready_item(
            "v514_sample_proof",
            "Sample acquisition proof matrix",
            "sample_evidence",
            "required_samples_present_or_validated",
            True,
            (v514,),
            sample_proof_ready,
            "v5.14 sample proof is not complete for the current RC evidence bar",
            "BioSDK has the current required sample proof matrix satisfied for RC evidence review.",
            "The sample matrix proves every future dataset/vendor integration.",
        ),
        _ready_item(
            "v521_cross_dataset_evidence",
            "Cross-dataset evidence matrix",
            "sample_evidence",
            "public_external_user_upload_matrix_ready",
            True,
            (v521,),
            cross_dataset_ready,
            "v5.21 does not yet show public, external and user-upload evidence ready together",
            "BioSDK has public dataset, validated read-only external export and safe user-upload evidence in one matrix.",
            "The matrix proves full private vendor portability or production BioSDK readiness.",
        ),
        _ready_item(
            "v522_public_examples",
            "Public examples and handoff runbook",
            "developer_experience",
            "examples_and_handoffs_ready",
            True,
            (v522,),
            examples_ready,
            "v5.22 examples are missing, blocked or overclaim full SDK readiness",
            "BioSDK has runnable public examples plus external/user-upload handoff examples.",
            "Examples prove live wetware/API control or BiC OS readiness.",
        ),
        _ready_item(
            "v523_user_upload_fixture",
            "Safe user-upload fixture proof",
            "sample_evidence",
            "safe_readonly_user_upload_validated",
            True,
            (v523,),
            user_upload_ready,
            "v5.23 safe user-upload fixture is missing or safety scan did not pass",
            "BioSDK has one safe read-only user-upload validation path.",
            "User-upload proof is equivalent to full private vendor export proof.",
        ),
        _ready_item(
            "v524_external_export",
            "Real read-only external export proof",
            "external_evidence",
            "validated_non_secret_readonly_export",
            True,
            (v524,),
            external_export_ready,
            "v5.24 real external export validation is missing or no export passed",
            "BioSDK has one validated non-secret read-only external export fixture.",
            "The export proves live API access, stimulation or closed-loop control.",
        ),
        _ready_item(
            "rc_docs_and_boundaries",
            "RC docs and claim boundaries",
            "documentation",
            "rc_docs_with_claim_boundaries",
            True,
            (readme, master_plan, external_guide, rc_guide),
            docs_ready,
            "README, master plan or RC evidence guide is missing",
            "BioSDK RC evidence is documented with explicit claim limits.",
            "Docs can loosen the evidence boundary or claim BiC OS readiness.",
        ),
        _ready_item(
            "v525_surface",
            "v5.25 package surface",
            "release_candidate_packaging",
            "runner_script_tests_example_present",
            True,
            (module, runner, script, tests, example),
            v525_surface_ready,
            "v5.25 SDK module, runner, script, tests or example is missing",
            "BioSDK RC evidence package can be regenerated and tested locally.",
            "The package surface is an installable production SDK release by itself.",
        ),
    )


def build_biosdk_release_candidate_evidence_v525(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    items = build_biosdk_release_candidate_items_v525(project_root)
    required_items = [item for item in items if item.required_for_rc_evidence]
    ready_required_items = [item for item in required_items if item.status == "ready"]
    evidence_ready = len(ready_required_items) == len(required_items)
    blocked_items = [item for item in required_items if item.status != "ready"]
    if evidence_ready:
        overall_status = "biosdk_release_candidate_evidence_ready_full_biosdk_not_claimed"
    else:
        overall_status = "biosdk_release_candidate_evidence_incomplete"
    manifest = _manifest(items)
    return {
        "version": "v5.25",
        "sdk_name": SDK_NAME,
        "release_candidate_label": RC_LABEL,
        "phase": "biosdk_release_candidate_evidence_package",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core_release_candidate_evidence",
        "bic_os_phase_locked": True,
        "biosdk_release_candidate_evidence_ready": evidence_ready,
        "required_item_count": len(required_items),
        "ready_required_item_count": len(ready_required_items),
        "blocked_required_item_count": len(blocked_items),
        "blocked_item_ids": [item.item_id for item in blocked_items],
        "full_biosdk_ready": False,
        "production_biocompute_runtime_ready": False,
        "live_external_api_ready": False,
        "items": [item.to_dict() for item in items],
        "manifest": manifest,
        "remaining_engineering_blockers": [
            "durable scheduler and persisted worker lifecycle",
            "installable SDK release artifacts and versioned API docs",
            "production auth, roles, storage and hosted/on-prem deployment",
            "external live API/token validation without write access",
            "multi-session/multi-vendor expansion beyond current representative samples",
        ],
        "direct_answer": {
            "can_package_biosdk_rc_evidence_now": "yes" if evidence_ready else "not_yet",
            "is_full_biosdk_proven": "no",
            "is_bic_os_ready": "no",
            "should_jump_to_bic_os_now": "no",
            "next_best_build_step": "freeze SDK RC docs and start durable scheduler/worker proof" if evidence_ready else "close the blocked RC evidence items first",
        },
        "claim_boundary": "v5.25 packages the current BioSDK release-candidate evidence layer. It does not claim full production BioSDK, BioCompute Runtime, live external API control, closed-loop wetware operation or BiC OS readiness.",
    }


def _manifest(items: tuple[BioSDKReleaseCandidateItemV525, ...]) -> dict[str, Any]:
    evidence_artifacts = sorted({artifact for item in items for artifact in item.artifacts})
    return {
        "manifest_id": RC_LABEL,
        "sdk_name": SDK_NAME,
        "package_kind": "evidence_manifest_not_installable_release",
        "evidence_artifacts": evidence_artifacts,
        "acceptance_commands": [
            "powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v524_external_export_validation.ps1",
            "powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v525_biosdk_release_candidate_evidence.ps1",
            "python -m pytest -q tests/current",
        ],
        "claim_boundary_required": True,
        "bic_os_phase_locked": True,
    }


def write_biosdk_release_candidate_evidence_outputs_v525(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_SUMMARY.json",
        "checklist_json": out / "V525_BIOSDK_RELEASE_CANDIDATE_CHECKLIST.json",
        "checklist_csv": out / "V525_BIOSDK_RELEASE_CANDIDATE_CHECKLIST.csv",
        "manifest_json": out / "V525_BIOSDK_RELEASE_CANDIDATE_MANIFEST.json",
        "markdown_report": out / "BIOGPU_V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"items", "manifest"}}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["checklist_json"].write_text(json.dumps({"items": audit["items"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["manifest_json"].write_text(json.dumps(audit["manifest"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_checklist_csv(paths["checklist_csv"], audit["items"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_checklist_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["item_id", "title", "package_layer", "status", "proof_level", "required_for_rc_evidence", "artifacts", "blockers"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = dict(row)
            payload["artifacts"] = " | ".join(str(item) for item in row.get("artifacts", []))
            payload["blockers"] = " | ".join(str(item) for item in row.get("blockers", []))
            writer.writerow({key: payload.get(key) for key in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.25 BioSDK Release-Candidate Evidence",
        "",
        "## Direct Answer",
        "",
        f"- Can package BioSDK RC evidence now: `{answer['can_package_biosdk_rc_evidence_now']}`",
        f"- Full BioSDK proven: `{answer['is_full_biosdk_proven']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Jump to BiC OS now: `{answer['should_jump_to_bic_os_now']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Checklist",
        "",
        "| Item | Status | Proof | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for item in audit["items"]:
        blockers = "; ".join(str(blocker) for blocker in item.get("blockers", []))
        lines.append(f"| `{item['item_id']}` | `{item['status']}` | `{item['proof_level']}` | {blockers} |")
    lines.extend([
        "",
        "## Remaining Engineering Blockers",
        "",
    ])
    for blocker in audit["remaining_engineering_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)