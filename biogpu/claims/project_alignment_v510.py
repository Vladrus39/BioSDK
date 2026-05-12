"""Project alignment and claim audit, v5.10."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/v510_project_alignment_claim_audit")


@dataclass(frozen=True)
class ClaimAuditItemV510:
    claim_id: str
    title: str
    status: str
    confidence: str
    evidence: tuple[str, ...]
    gaps: tuple[str, ...]
    allowed_statement: str
    forbidden_statement: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def _status_supported(condition: bool, missing_status: str = "not_supported") -> str:
    return "supported" if condition else missing_status


def _artifact_map(root: Path) -> dict[str, Any]:
    paths = {
        "v50_bundle": "outputs/v50_pc_validation_bundle/V50_PC_VALIDATION_BUNDLE_SUMMARY.json",
        "v52_nsi": "outputs/v52_nsi_interface/V52_NSI_INTERFACE_SUMMARY.json",
        "v53_evidence_ledger": "outputs/v53_evidence_ledger/V53_EVIDENCE_LEDGER_SUMMARY.json",
        "v54_agent_bridge": "outputs/v54_llm_agent_bridge/V54_LLM_AGENT_BRIDGE_SUMMARY.json",
        "v55_control_plane": "outputs/v55_control_plane_queue/V55_CONTROL_PLANE_QUEUE_SUMMARY.json",
        "v56_raw_structure": "outputs/v56_raw_hdf5_structure/V56_RAW_HDF5_STRUCTURE_SUMMARY.json",
        "v57_alignment": "outputs/v57_raw_preprocessed_alignment/V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json",
        "v58_raw_native": "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_SUMMARY.json",
        "v59_stability": "outputs/v59_raw_native_stability_audit/V59_RAW_NATIVE_STABILITY_SUMMARY.json",
        "first_mover_strategy": "docs/BIC_OS_FIRST_MOVER_STRATEGY_V50.md",
        "master_plan": "docs/MASTER_PROJECT_PLAN_V50.md",
    }
    artifacts: dict[str, Any] = {}
    for key, relative_path in paths.items():
        path = root / relative_path
        artifacts[key] = {
            "path": relative_path,
            "exists": path.exists(),
            "json": _read_json(path) if path.suffix.lower() == ".json" else {},
        }
    return artifacts


def _evidence_for(artifacts: dict[str, Any], *keys: str) -> tuple[str, ...]:
    return tuple(str(artifacts[key]["path"]) for key in keys if artifacts.get(key, {}).get("exists"))


def _missing_for(artifacts: dict[str, Any], *keys: str) -> tuple[str, ...]:
    return tuple(str(artifacts[key]["path"]) for key in keys if not artifacts.get(key, {}).get("exists"))


def _v57_exact_matches(artifacts: dict[str, Any]) -> int | None:
    data = artifacts.get("v57_alignment", {}).get("json", {})
    value = data.get("exact_recording_match_count")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _v58_rows(artifacts: dict[str, Any]) -> int:
    data = artifacts.get("v58_raw_native", {}).get("json", {})
    try:
        return int(data.get("feature_row_count", 0))
    except (TypeError, ValueError):
        return 0


def _v59_repeatability_supported(artifacts: dict[str, Any]) -> bool:
    data = artifacts.get("v59_stability", {}).get("json", {})
    try:
        split_median = float(data.get("split_half_cosine_median", 0.0))
        margin = float(data.get("split_vs_cross_median_margin", 0.0))
    except (TypeError, ValueError):
        return False
    return split_median >= 0.95 and margin > 0.1


def _v59_target_supported(artifacts: dict[str, Any]) -> bool:
    data = artifacts.get("v59_stability", {}).get("json", {})
    return str(data.get("target_readout_signal_status")) == "exploratory_supported" or str(data.get("target_fingerprint_signal_status")) == "exploratory_supported"


def build_claim_register_v510(root: str | Path = ".") -> tuple[ClaimAuditItemV510, ...]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    core_keys = ("v52_nsi", "v53_evidence_ledger", "v54_agent_bridge", "v55_control_plane", "first_mover_strategy", "master_plan")
    raw_keys = ("v56_raw_structure", "v57_alignment", "v58_raw_native", "v59_stability")
    core_supported = all(artifacts[key]["exists"] for key in core_keys)
    raw_supported = all(artifacts[key]["exists"] for key in raw_keys)
    v57_exact = _v57_exact_matches(artifacts)
    v58_feature_rows = _v58_rows(artifacts)
    v59_repeatability = _v59_repeatability_supported(artifacts)
    v59_target_supported = _v59_target_supported(artifacts)

    items = [
        ClaimAuditItemV510(
            claim_id="project_meaning_alignment",
            title="Project remains aligned with BioCompute Runtime / BiC OS objective",
            status="supported" if core_supported and raw_supported else "partially_supported",
            confidence="high" if core_supported and raw_supported else "medium",
            evidence=_evidence_for(artifacts, *(core_keys + raw_keys)),
            gaps=_missing_for(artifacts, *(core_keys + raw_keys)),
            allowed_statement="The project remains on-mission: vendor-neutral runtime, NSI, evidence ledger, LLM/agent bridge, control plane and raw-data evidence layers are all being built around brain-first workflows.",
            forbidden_statement="The project has already become a complete biological OS or live biological computer.",
        ),
        ClaimAuditItemV510(
            claim_id="local_code_distinctness",
            title="Local codebase has a distinct integrated architecture",
            status="supported" if core_supported else "partially_supported",
            confidence="medium",
            evidence=_evidence_for(artifacts, "v52_nsi", "v53_evidence_ledger", "v54_agent_bridge", "v55_control_plane", "v58_raw_native", "v59_stability"),
            gaps=_missing_for(artifacts, "v52_nsi", "v53_evidence_ledger", "v54_agent_bridge", "v55_control_plane", "v58_raw_native", "v59_stability"),
            allowed_statement="The repository contains a distinct integrated implementation combining NSI schemas, evidence bundles, LLM-agent policy, control-plane admission and raw neural-data audits.",
            forbidden_statement="The code has proven global uniqueness against all existing public/private systems.",
        ),
        ClaimAuditItemV510(
            claim_id="global_uniqueness_proof",
            title="Global uniqueness of the code or concept",
            status="not_provable_locally",
            confidence="high",
            evidence=_evidence_for(artifacts, "first_mover_strategy", "master_plan"),
            gaps=("No exhaustive public/private prior-art search; local tests cannot prove nobody else has similar code.",),
            allowed_statement="Global uniqueness remains a hypothesis and positioning target, not a proven fact. We can claim local distinctness and evidence-backed design choices.",
            forbidden_statement="We have proven that nobody else has built similar code or architecture.",
        ),
        ClaimAuditItemV510(
            claim_id="vendor_neutral_standard_direction",
            title="Vendor-neutral BioCompute standard direction",
            status=_status_supported(artifacts["v52_nsi"]["exists"] and artifacts["v54_agent_bridge"]["exists"]),
            confidence="medium",
            evidence=_evidence_for(artifacts, "v52_nsi", "v54_agent_bridge", "v55_control_plane", "first_mover_strategy"),
            gaps=_missing_for(artifacts, "v52_nsi", "v54_agent_bridge", "v55_control_plane"),
            allowed_statement="A vendor-neutral interface and runtime direction exists as implemented NSI/agent/control-plane scaffolding.",
            forbidden_statement="NSI is an externally adopted universal standard today.",
        ),
        ClaimAuditItemV510(
            claim_id="raw_native_extraction_repeatability",
            title="Raw-native event-window extraction repeatability",
            status="supported" if v59_repeatability else "not_supported",
            confidence="high" if v59_repeatability else "medium",
            evidence=_evidence_for(artifacts, "v58_raw_native", "v59_stability"),
            gaps=tuple() if v59_repeatability else ("v5.9 repeatability threshold not met or summary missing.",),
            allowed_statement="Raw HDF5 event-window feature extraction is internally repeatable within recordings on the current raw subset.",
            forbidden_statement="Raw repeatability proves target-ID decoding, live compute or v15/v50 raw equivalence.",
        ),
        ClaimAuditItemV510(
            claim_id="raw_native_feature_matrix",
            title="Raw-derived feature matrix exists",
            status="supported" if v58_feature_rows > 0 else "not_supported",
            confidence="high" if v58_feature_rows > 0 else "medium",
            evidence=_evidence_for(artifacts, "v58_raw_native"),
            gaps=tuple() if v58_feature_rows > 0 else ("v5.8 raw-native feature matrix missing or empty.",),
            allowed_statement=f"A raw-derived event-window feature matrix exists with {v58_feature_rows} rows." if v58_feature_rows > 0 else "A raw-derived event-window feature matrix is planned but not available.",
            forbidden_statement="The raw-derived matrix proves raw equivalence for all earlier v15/v50 rows.",
        ),
        ClaimAuditItemV510(
            claim_id="raw_v15_v50_equivalence",
            title="Raw equivalence for v15/v50 PC validation rows",
            status="not_supported" if v57_exact == 0 else "unknown" if v57_exact is None else "partially_supported",
            confidence="high" if v57_exact == 0 else "medium",
            evidence=_evidence_for(artifacts, "v57_alignment", "v58_raw_native", "v59_stability"),
            gaps=("v5.7 found zero exact raw/preprocessed recording matches." if v57_exact == 0 else "Exact raw/preprocessed overlap has not been conclusively established.",),
            allowed_statement="Raw HDF5 evidence exists, but v15/v50 raw equivalence remains unproven until exact overlap and waveform-derived rebuild are validated.",
            forbidden_statement="v15/v50 PC validation has been fully rebuilt from exact raw waveforms.",
        ),
        ClaimAuditItemV510(
            claim_id="target_id_decoding",
            title="Target-ID decoding from current raw subset",
            status="supported" if v59_target_supported else "not_supported",
            confidence="high",
            evidence=_evidence_for(artifacts, "v59_stability"),
            gaps=tuple() if v59_target_supported else ("v5.9 target readout and fingerprint audits are not statistically supported on sparse repeated targets.",),
            allowed_statement="Target-ID decoding is not supported on the current sparse repeated-target raw subset." if not v59_target_supported else "A limited exploratory target signal is supported on repeated targets.",
            forbidden_statement="The current raw subset proves robust target-ID decoding.",
        ),
        ClaimAuditItemV510(
            claim_id="live_biogpu_proof",
            title="Live BioGPU proof",
            status="not_supported",
            confidence="high",
            evidence=tuple(),
            gaps=("No live wetware run, no approved closed-loop actuation, no live telemetry evidence bundle.",),
            allowed_statement="Current results are software replay, raw-data inspection and offline analysis.",
            forbidden_statement="A live BioGPU prototype has been proven.",
        ),
        ClaimAuditItemV510(
            claim_id="first_biological_computer",
            title="First biological computer claim",
            status="blocked",
            confidence="high",
            evidence=_evidence_for(artifacts, "first_mover_strategy"),
            gaps=("Existing biological computing and wetware API platforms are acknowledged by strategy docs.",),
            allowed_statement="The project aims for a vendor-neutral operating layer for living neural compute workflows.",
            forbidden_statement="BioGPU-Core is the first biological computer or first wetware API.",
        ),
        ClaimAuditItemV510(
            claim_id="gpu_replacement_or_energy_superiority",
            title="GPU replacement or energy superiority",
            status="blocked",
            confidence="high",
            evidence=_evidence_for(artifacts, "master_plan"),
            gaps=("No hardware energy measurement or GPU replacement benchmark exists.",),
            allowed_statement="The project can compare evidence bundles and benchmark methods, but hardware advantage remains unproven.",
            forbidden_statement="BioGPU-Core has proven GPU replacement or energy superiority.",
        ),
        ClaimAuditItemV510(
            claim_id="production_os",
            title="Production BiC OS",
            status="not_supported",
            confidence="high",
            evidence=_evidence_for(artifacts, "v55_control_plane", "master_plan"),
            gaps=("No production daemon, permission system, plugin manager, dashboard, live telemetry or production auth.",),
            allowed_statement="BiC OS is the long-term OS-like commercial target; current work is the runtime/control-plane kernel.",
            forbidden_statement="A production biological OS is finished.",
        ),
    ]
    return tuple(items)


def build_project_alignment_audit_v510(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root)
    artifacts = _artifact_map(project_root)
    claim_register = build_claim_register_v510(project_root)
    status_counts: dict[str, int] = {}
    for item in claim_register:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1
    forbidden_claims_supported = [item.claim_id for item in claim_register if item.claim_id in {"first_biological_computer", "gpu_replacement_or_energy_superiority"} and item.status == "supported"]
    project_alignment_item = next(item for item in claim_register if item.claim_id == "project_meaning_alignment")
    uniqueness_item = next(item for item in claim_register if item.claim_id == "global_uniqueness_proof")
    overall_status = "on_mission_with_claim_boundaries" if project_alignment_item.status in {"supported", "partially_supported"} and not forbidden_claims_supported else "claim_drift_detected"
    if uniqueness_item.status != "not_provable_locally":
        overall_status = "claim_drift_detected"

    return {
        "version": "v5.10",
        "overall_status": overall_status,
        "direct_answer": {
            "did_we_drift_from_project_meaning": "no" if overall_status == "on_mission_with_claim_boundaries" else "needs_review",
            "is_the_code_globally_unique_proven": "no_local_tests_cannot_prove_global_uniqueness",
            "what_is_proven": "integrated local runtime/evidence/agent/control-plane/raw-audit implementation plus raw event-window repeatability",
            "what_is_not_proven": "global uniqueness, first biological computer, live BioGPU, GPU replacement, energy superiority, raw v15/v50 equivalence and current raw target-ID decoding",
        },
        "status_counts": dict(sorted(status_counts.items())),
        "artifact_presence": {key: {"path": value["path"], "exists": bool(value["exists"])} for key, value in sorted(artifacts.items())},
        "claim_register": [item.to_dict() for item in claim_register],
        "claim_boundary": "This audit validates project alignment and claim discipline from local artifacts only. It does not perform an external prior-art search and cannot prove global uniqueness.",
    }


def write_project_alignment_outputs_v510(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V510_PROJECT_ALIGNMENT_SUMMARY.json",
        "claim_register_json": out / "V510_CLAIM_REGISTER.json",
        "claim_register_csv": out / "V510_CLAIM_REGISTER.csv",
        "markdown_report": out / "BIOGPU_V510_PROJECT_ALIGNMENT_CLAIM_AUDIT_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps({key: value for key, value in audit.items() if key != "claim_register"}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["claim_register_json"].write_text(json.dumps(audit["claim_register"], indent=2, ensure_ascii=False), encoding="utf-8")
    _write_claim_csv(paths["claim_register_csv"], audit["claim_register"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_claim_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["claim_id", "title", "status", "confidence", "allowed_statement", "forbidden_statement", "evidence", "gaps"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "claim_id": row["claim_id"],
                "title": row["title"],
                "status": row["status"],
                "confidence": row["confidence"],
                "allowed_statement": row["allowed_statement"],
                "forbidden_statement": row["forbidden_statement"],
                "evidence": " | ".join(str(value) for value in row.get("evidence", [])),
                "gaps": " | ".join(str(value) for value in row.get("gaps", [])),
            })


def _markdown_report(audit: dict[str, Any]) -> str:
    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v5.10 Project Alignment and Claim Audit",
        "",
        "## Direct Answer",
        "",
        f"- Did we drift from the project meaning: `{answer['did_we_drift_from_project_meaning']}`",
        f"- Is global uniqueness proven: `{answer['is_the_code_globally_unique_proven']}`",
        f"- What is proven: {answer['what_is_proven']}",
        f"- What is not proven: {answer['what_is_not_proven']}",
        "",
        "## Overall Status",
        "",
        f"`{audit['overall_status']}`",
        "",
        "## Claim Register",
        "",
        "| Claim | Status | Allowed | Forbidden |",
        "| --- | --- | --- | --- |",
    ]
    for row in audit["claim_register"]:
        lines.append(f"| `{row['claim_id']}` | `{row['status']}` | {row['allowed_statement']} | {row['forbidden_statement']} |")
    lines.extend([
        "",
        "## Boundary",
        "",
        audit["claim_boundary"],
        "",
    ])
    return "\n".join(lines)
