"""BioSDK public examples readiness gate, v5.22."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.sdk.cross_dataset_evidence_v521 import build_cross_dataset_evidence_pack_v521


DEFAULT_OUT = Path("outputs/v522_biosdk_public_examples")
SDK_NAME = "BioSDK / Living Compute SDK"

PUBLIC_REQUIRED_EXAMPLE_IDS = (
    "biosdk_minimal_replay_flow",
    "dandi_task_benchmark_example",
    "allen_orientation_benchmark_example",
    "cross_dataset_evidence_example",
    "public_examples_manifest_example",
)


@dataclass(frozen=True)
class BioSDKPublicExampleV522:
    example_id: str
    title: str
    example_path: str
    command: str
    source_ids: tuple[str, ...]
    status: str
    proof_level: str
    required_for_public_sdk: bool
    requires_external_material: bool
    evidence_artifacts: tuple[str, ...]
    blockers: tuple[str, ...]
    allowed_statement: str
    forbidden_statement: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _artifact_exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def _source_status(audit: dict[str, Any], source_id: str) -> str:
    for source in audit.get("sources", []):
        if isinstance(source, dict) and source.get("source_id") == source_id:
            return str(source.get("status", "missing_or_incomplete"))
    return "missing_or_incomplete"


def _source_artifacts(audit: dict[str, Any], source_id: str) -> tuple[str, ...]:
    for source in audit.get("sources", []):
        if isinstance(source, dict) and source.get("source_id") == source_id:
            return tuple(str(item) for item in source.get("evidence_artifacts", []))
    return tuple()


def _ready_if(root: Path, example_path: str, condition: bool, missing_reason: str) -> tuple[str, tuple[str, ...]]:
    blockers: list[str] = []
    if not _artifact_exists(root, example_path):
        blockers.append(f"missing example file: {example_path}")
    if not condition:
        blockers.append(missing_reason)
    return ("ready" if not blockers else "blocked_missing_example_or_artifacts", tuple(blockers))


def build_biosdk_public_examples_v522(root: str | Path = ".") -> tuple[BioSDKPublicExampleV522, ...]:
    project_root = Path(root)
    cross_dataset = build_cross_dataset_evidence_pack_v521(project_root)
    public_ready = bool(cross_dataset.get("public_cross_dataset_evidence_ready"))
    dandi_ready = _source_status(cross_dataset, "dandi_nwb_task") == "benchmark_available"
    allen_ready = _source_status(cross_dataset, "allen_visual_coding_orientation") == "benchmark_available"
    external_ready = _source_status(cross_dataset, "external_readonly_api_or_export") == "real_external_ready"
    vendor_ready = _source_status(cross_dataset, "vendor_user_upload_sample") == "validated_readonly_samples"
    v513_summary_ready = _artifact_exists(project_root, "outputs/v513_biosdk_core_api/V513_BIOSDK_CORE_API_SUMMARY.json") or _artifact_exists(project_root, "examples/biosdk_v513_minimal_flow.py")

    core_status, core_blockers = _ready_if(project_root, "examples/biosdk_v513_minimal_flow.py", v513_summary_ready, "v5.13 BioSDK core API summary or example is missing")
    dandi_status, dandi_blockers = _ready_if(project_root, "examples/biosdk_v516_dandi_task_benchmark.py", dandi_ready, "DANDI v5.16 benchmark is not available")
    allen_status, allen_blockers = _ready_if(project_root, "examples/biosdk_v520_allen_orientation_benchmark.py", allen_ready, "Allen v5.20 orientation benchmark is not available")
    cross_status, cross_blockers = _ready_if(project_root, "examples/biosdk_v521_cross_dataset_evidence.py", public_ready, "v5.21 public cross-dataset evidence is not ready")
    manifest_status, manifest_blockers = _ready_if(project_root, "examples/biosdk_v522_public_examples.py", public_ready, "v5.21 public cross-dataset evidence is not ready")

    external_blockers = tuple() if external_ready else (
        "real non-secret external read-only token/export is missing",
        "v5.17 currently proves mock contract/write-denial only",
    )
    vendor_blockers = tuple() if vendor_ready else (
        "safe read-only vendor/user sample is missing",
        "v5.19 currently proves intake scanner/routing only",
    )

    return (
        BioSDKPublicExampleV522(
            example_id="biosdk_minimal_replay_flow",
            title="Minimal BioSDK replay facade flow",
            example_path="examples/biosdk_v513_minimal_flow.py",
            command="python examples/biosdk_v513_minimal_flow.py",
            source_ids=("biosdk_core_api",),
            status=core_status,
            proof_level="safe_replay_nsi_queue_facade" if core_status == "ready" else "missing_or_incomplete",
            required_for_public_sdk=True,
            requires_external_material=False,
            evidence_artifacts=("outputs/v513_biosdk_core_api/V513_BIOSDK_CORE_API_SUMMARY.json",),
            blockers=core_blockers,
            allowed_statement="BioSDK exposes a local safe replay facade with NSI validation and queue admission.",
            forbidden_statement="The minimal flow proves production BioCompute Runtime or BiC OS readiness.",
        ),
        BioSDKPublicExampleV522(
            example_id="dandi_task_benchmark_example",
            title="DANDI NWB task benchmark example",
            example_path="examples/biosdk_v516_dandi_task_benchmark.py",
            command="python examples/biosdk_v516_dandi_task_benchmark.py",
            source_ids=("dandi_nwb_task",),
            status=dandi_status,
            proof_level="single_public_nwb_task_readout" if dandi_status == "ready" else "missing_or_incomplete",
            required_for_public_sdk=True,
            requires_external_material=False,
            evidence_artifacts=_source_artifacts(cross_dataset, "dandi_nwb_task"),
            blockers=dandi_blockers,
            allowed_statement="BioSDK can demonstrate one public DANDI/NWB task-window benchmark.",
            forbidden_statement="The DANDI example proves all NWB data or external wetware integration.",
        ),
        BioSDKPublicExampleV522(
            example_id="allen_orientation_benchmark_example",
            title="Allen visual-coding orientation benchmark example",
            example_path="examples/biosdk_v520_allen_orientation_benchmark.py",
            command="python examples/biosdk_v520_allen_orientation_benchmark.py",
            source_ids=("allen_visual_coding_orientation",),
            status=allen_status,
            proof_level="single_public_allen_session_orientation_readout" if allen_status == "ready" else "missing_or_incomplete",
            required_for_public_sdk=True,
            requires_external_material=False,
            evidence_artifacts=_source_artifacts(cross_dataset, "allen_visual_coding_orientation"),
            blockers=allen_blockers,
            allowed_statement="BioSDK can demonstrate one public Allen visual-coding orientation benchmark.",
            forbidden_statement="The Allen example proves full Allen cache coverage or BiC OS readiness.",
        ),
        BioSDKPublicExampleV522(
            example_id="cross_dataset_evidence_example",
            title="Cross-dataset public evidence summary example",
            example_path="examples/biosdk_v521_cross_dataset_evidence.py",
            command="python examples/biosdk_v521_cross_dataset_evidence.py",
            source_ids=("zenodo_raw_mea", "dandi_nwb_task", "allen_visual_coding_orientation"),
            status=cross_status,
            proof_level="three_public_source_evidence_summary" if cross_status == "ready" else "missing_or_incomplete",
            required_for_public_sdk=True,
            requires_external_material=False,
            evidence_artifacts=("outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_EVIDENCE_SUMMARY.json", "outputs/v521_cross_dataset_evidence_pack/V521_CROSS_DATASET_SOURCE_MATRIX.json"),
            blockers=cross_blockers,
            allowed_statement="BioSDK can summarize the current public evidence layer across Zenodo, DANDI and Allen.",
            forbidden_statement="The cross-dataset example proves full BioSDK, private vendor portability or BiC OS readiness.",
        ),
        BioSDKPublicExampleV522(
            example_id="public_examples_manifest_example",
            title="Public examples manifest example",
            example_path="examples/biosdk_v522_public_examples.py",
            command="python examples/biosdk_v522_public_examples.py",
            source_ids=("biosdk_public_examples",),
            status=manifest_status,
            proof_level="public_example_catalog_and_runbook" if manifest_status == "ready" else "missing_or_incomplete",
            required_for_public_sdk=True,
            requires_external_material=False,
            evidence_artifacts=("outputs/v522_biosdk_public_examples/V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json",),
            blockers=manifest_blockers,
            allowed_statement="BioSDK can expose a public examples catalog and runbook for the proven public layer.",
            forbidden_statement="The examples manifest closes real external or vendor sample proof by itself.",
        ),
        BioSDKPublicExampleV522(
            example_id="external_readonly_handoff_example",
            title="External read-only API/export handoff example",
            example_path="examples/biosdk_v517_external_readonly_gate.py",
            command="python examples/biosdk_v517_external_readonly_gate.py",
            source_ids=("external_readonly_api_or_export",),
            status="ready" if external_ready else "blocked_waiting_for_real_external_material",
            proof_level="real_external_readonly_export" if external_ready else "mock_contract_handoff_only",
            required_for_public_sdk=False,
            requires_external_material=True,
            evidence_artifacts=_source_artifacts(cross_dataset, "external_readonly_api_or_export"),
            blockers=external_blockers,
            allowed_statement="BioSDK documents the read-only external handoff and keeps writes blocked.",
            forbidden_statement="BioSDK has real external wetware/API proof before a real non-mock export or token passes.",
        ),
        BioSDKPublicExampleV522(
            example_id="vendor_user_upload_handoff_example",
            title="Vendor/user-upload read-only intake handoff example",
            example_path="examples/biosdk_v519_vendor_user_upload_gate.py",
            command="python examples/biosdk_v519_vendor_user_upload_gate.py",
            source_ids=("vendor_user_upload_sample",),
            status="ready" if vendor_ready else "blocked_waiting_for_safe_vendor_or_user_sample",
            proof_level="validated_safe_upload_sample" if vendor_ready else "intake_scanner_handoff_only",
            required_for_public_sdk=False,
            requires_external_material=True,
            evidence_artifacts=_source_artifacts(cross_dataset, "vendor_user_upload_sample"),
            blockers=vendor_blockers,
            allowed_statement="BioSDK documents the safe read-only vendor/user sample intake flow.",
            forbidden_statement="BioSDK has private/vendor portability without at least one safe real sample.",
        ),
    )


def build_biosdk_public_examples_gate_v522(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    cross_dataset = build_cross_dataset_evidence_pack_v521(project_root)
    examples = build_biosdk_public_examples_v522(project_root)
    required = [example for example in examples if example.required_for_public_sdk]
    ready_required = [example for example in required if example.status == "ready"]
    public_examples_ready = len(ready_required) == len(required) and bool(cross_dataset.get("public_cross_dataset_evidence_ready"))
    external_ready = bool(cross_dataset.get("external_partner_evidence_ready"))
    vendor_ready = bool(cross_dataset.get("vendor_user_evidence_ready"))
    if public_examples_ready and external_ready and vendor_ready:
        overall_status = "biosdk_public_examples_ready_full_sample_proof_available_full_biosdk_not_claimed"
    elif public_examples_ready and vendor_ready and not external_ready:
        overall_status = "biosdk_public_examples_and_user_upload_ready_external_blocked"
    elif public_examples_ready and external_ready and not vendor_ready:
        overall_status = "biosdk_public_examples_and_external_ready_vendor_blocked"
    elif public_examples_ready:
        overall_status = "biosdk_public_examples_ready_external_vendor_blocked"
    else:
        overall_status = "biosdk_public_examples_incomplete"
    if public_examples_ready and external_ready and vendor_ready:
        next_best_build_step = "package the validated public, user-upload and external export evidence into SDK release-candidate docs while keeping full BioSDK/runtime claims blocked"
        claim_boundary = "v5.22 packages the proven public BioSDK path, validated user-upload handoff and validated read-only external export handoff into runnable examples. It does not claim full BioSDK, live external API access, production runtime or BiC OS readiness."
    elif vendor_ready and not external_ready:
        next_best_build_step = "obtain one real external read-only export/token while keeping the validated user-upload path in the public SDK runbook"
        claim_boundary = "v5.22 packages the proven public BioSDK path and validated user-upload handoff into runnable examples. It does not close real external API/export proof without new non-secret external material."
    elif external_ready and not vendor_ready:
        next_best_build_step = "add one safe vendor/user-upload sample while keeping external read-only proof attached to the SDK-facing proof path"
        claim_boundary = "v5.22 packages the proven public BioSDK path and external handoff into runnable examples. It does not close vendor/user-upload proof without a safe sample."
    else:
        next_best_build_step = "add one safe vendor/user sample or one real external read-only export while keeping the public examples as the SDK-facing proof path"
        claim_boundary = "v5.22 packages the proven public BioSDK path into runnable examples and a runbook. It does not close real external API/export or vendor/user-upload proof without new non-secret external material."
    return {
        "version": "v5.22",
        "sdk_name": SDK_NAME,
        "phase": "biosdk_public_examples",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "public_examples_ready": public_examples_ready,
        "required_public_example_count": len(required),
        "ready_required_public_example_count": len(ready_required),
        "example_count": len(examples),
        "blocked_example_count": sum(1 for example in examples if example.status != "ready"),
        "public_cross_dataset_evidence_ready": bool(cross_dataset.get("public_cross_dataset_evidence_ready")),
        "external_partner_evidence_ready": external_ready,
        "vendor_user_evidence_ready": vendor_ready,
        "full_biosdk_ready": False,
        "examples": [example.to_dict() for example in examples],
        "runbook": _runbook(examples),
        "direct_answer": {
            "can_public_users_run_examples_now": "yes" if public_examples_ready else "not_yet",
            "is_full_biosdk_proven": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": next_best_build_step,
        },
        "claim_boundary": claim_boundary,
    }


def _runbook(examples: tuple[BioSDKPublicExampleV522, ...]) -> dict[str, Any]:
    public_commands = [
        {"example_id": example.example_id, "command": example.command, "status": example.status}
        for example in examples
        if example.required_for_public_sdk
    ]
    handoff_commands = [
        {"example_id": example.example_id, "command": example.command, "status": example.status, "requires_external_material": example.requires_external_material}
        for example in examples
        if not example.required_for_public_sdk
    ]
    return {
        "environment": {"PYTHONPATH": ".", "pytest_plugin_autoload": "disabled_for_tests"},
        "public_example_commands": public_commands,
        "external_handoff_commands": handoff_commands,
        "recommended_sequence": [item["example_id"] for item in public_commands],
    }


def write_biosdk_public_examples_outputs_v522(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json",
        "example_catalog_json": out / "V522_BIOSDK_PUBLIC_EXAMPLE_CATALOG.json",
        "example_catalog_csv": out / "V522_BIOSDK_PUBLIC_EXAMPLE_CATALOG.csv",
        "runbook_json": out / "V522_BIOSDK_PUBLIC_EXAMPLE_RUNBOOK.json",
        "markdown_report": out / "BIOGPU_V522_BIOSDK_PUBLIC_EXAMPLES_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key not in {"examples", "runbook"}}
    summary["blocked_example_ids"] = [example["example_id"] for example in audit["examples"] if example["status"] != "ready"]
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["example_catalog_json"].write_text(json.dumps(audit["examples"], indent=2, ensure_ascii=False), encoding="utf-8")
    paths["runbook_json"].write_text(json.dumps(audit["runbook"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_example_csv(paths["example_catalog_csv"], audit["examples"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_example_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["example_id", "title", "example_path", "command", "status", "proof_level", "required_for_public_sdk", "requires_external_material", "source_ids", "evidence_artifacts", "blockers"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = dict(row)
            payload["source_ids"] = " | ".join(str(item) for item in row.get("source_ids", []))
            payload["evidence_artifacts"] = " | ".join(str(item) for item in row.get("evidence_artifacts", []))
            payload["blockers"] = " | ".join(str(item) for item in row.get("blockers", []))
            writer.writerow({key: payload.get(key) for key in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.22 BioSDK Public Examples",
        "",
        "## Direct Answer",
        "",
        f"- Public users can run examples now: `{answer['can_public_users_run_examples_now']}`",
        f"- Full BioSDK proven: `{answer['is_full_biosdk_proven']}`",
        f"- BiC OS ready: `{answer['is_bic_os_ready']}`",
        f"- Next best build step: {answer['next_best_build_step']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Examples",
        "",
        "| Example | Status | Command |",
        "| --- | --- | --- |",
    ]
    for example in audit["examples"]:
        lines.append(f"| `{example['example_id']}` | `{example['status']}` | `{example['command']}` |")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)
