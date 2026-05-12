"""Real external read-only export validation, v5.24."""
from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import h5py


DEFAULT_OUT = Path("outputs/v524_external_export_validation")
EXPORT_PATTERNS = ("data/external/api_exports/**/*", "data/external/finalspark/**/*")
SUPPORTED_EXTENSIONS = {".json", ".csv", ".h5", ".hdf5", ".nwb", ".zip"}
HDF5_EXTENSIONS = {".h5", ".hdf5", ".nwb"}
SIDEcar_SUFFIXES = (".source.json", ".metadata.json", ".manifest.json")
LIVE_CONTROL_TERMS = (
    "send_stimulation",
    "stimulation_pattern",
    "live_stimulation",
    "closed_loop_write",
    "write_endpoint",
    "write_command",
    "actuation",
    "pulse_width",
    "stimulus_amplitude",
    "stimulus_frequency",
    "current_injection",
    "pinout",
    "wiring",
    "wetlab_recipe",
)
KNOWN_SOURCE_BY_SHA256 = {
    "5d5bed4fbc745ab2bf9ed4d57b34ae6008fedee28b0f0c1855298182babb8852": {
        "source_name": "McsPyDataTools TestData 2014-07-09T10-17-35W8 Standard all 500 Hz.h5",
        "source_url": "https://github.com/multichannelsystems/McsPyDataTools/tree/master/McsPyDataTools/McsPy/tests/TestData",
        "direct_url": "https://raw.githubusercontent.com/multichannelsystems/McsPyDataTools/master/McsPyDataTools/McsPy/tests/TestData/2014-07-09T10-17-35W8%20Standard%20all%20500%20Hz.h5",
        "source_license_note": "McsPyDataTools package/repository test-data fixture; use as read-only validation material only.",
    }
}


@dataclass(frozen=True)
class ExternalExportValidationReportV524:
    relative_path: str
    platform_hint: str
    file_format: str
    file_size_bytes: int
    sha256: str
    gate_status: str
    safety_scan_passed: bool
    readonly_data_evidence: bool
    recognized_readonly_format: bool
    root_attrs: dict[str, str]
    dataset_count: int
    group_count: int
    trace_dataset_count: int
    event_dataset_count: int
    first_datasets: tuple[dict[str, Any], ...]
    source_reference: dict[str, Any]
    forbidden_hits: tuple[str, ...]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _platform_hint(path: Path) -> str:
    text = "/".join(part.lower() for part in path.parts)
    if "finalspark" in text:
        return "finalspark_remote_wetware"
    if "threebrain" in text or "3brain" in text:
        return "threebrain_hdmea"
    if "axion" in text or "maestro" in text:
        return "axion_maestro"
    if "mcs" in text or "mea2100" in text or "mcspydatatools" in text:
        return "mcs_mea2100"
    return "unknown_external_export"


def _is_sidecar(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in SIDEcar_SUFFIXES)


def find_external_export_candidates_v524(root: str | Path = ".") -> list[Path]:
    project_root = Path(root).resolve()
    found: list[Path] = []
    for pattern in EXPORT_PATTERNS:
        found.extend(path for path in project_root.glob(pattern) if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS and not _is_sidecar(path))
    return sorted(set(found))


def _hits(text: str, context: str) -> list[str]:
    lowered = text.lower()
    return [f"{context}:{term}" for term in LIVE_CONTROL_TERMS if term in lowered]


def _stringify(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)
    return repr(value)


def _json_scan(payload: Any, context: str = "json") -> tuple[list[str], bool]:
    forbidden: list[str] = []
    readonly_data_evidence = False
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            forbidden.extend(_hits(key_text, f"{context}.{key_text}"))
            if key_text.lower() in {"trace_samples", "spike_events", "spike_times_s", "records", "channel_data"}:
                readonly_data_evidence = True
            child_hits, child_evidence = _json_scan(value, f"{context}.{key_text}")
            forbidden.extend(child_hits)
            readonly_data_evidence = readonly_data_evidence or child_evidence
    elif isinstance(payload, list):
        readonly_data_evidence = bool(payload) and context.endswith(("records", "trace_samples", "spike_events", "spike_times_s"))
        for index, value in enumerate(payload[:100]):
            child_hits, child_evidence = _json_scan(value, f"{context}[{index}]")
            forbidden.extend(child_hits)
            readonly_data_evidence = readonly_data_evidence or child_evidence
    elif isinstance(payload, str):
        forbidden.extend(_hits(payload, context))
    return forbidden, readonly_data_evidence


def _validate_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    forbidden, readonly_data_evidence = _json_scan(payload)
    recognized = isinstance(payload, dict) and str(payload.get("mode") or payload.get("access_mode") or "").startswith("read_only")
    return {
        "file_format": "json_export",
        "safety_scan_passed": not forbidden,
        "readonly_data_evidence": readonly_data_evidence,
        "recognized_readonly_format": recognized,
        "root_attrs": {},
        "dataset_count": 0,
        "group_count": 0,
        "trace_dataset_count": 0,
        "event_dataset_count": 0,
        "first_datasets": tuple(),
        "forbidden_hits": forbidden,
    }


def _validate_csv(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader, [])
        rows = [row for _, row in zip(range(25), reader)]
    header_text = " ".join(headers)
    forbidden = _hits(header_text, "csv.header")
    readonly_data_evidence = any(name.lower() in {"time", "timestamp", "channel", "spike_time", "trace", "value"} for name in headers) and bool(rows)
    return {
        "file_format": "csv_export",
        "safety_scan_passed": not forbidden,
        "readonly_data_evidence": readonly_data_evidence,
        "recognized_readonly_format": readonly_data_evidence,
        "root_attrs": {},
        "dataset_count": 0,
        "group_count": 0,
        "trace_dataset_count": 0,
        "event_dataset_count": 0,
        "first_datasets": tuple(),
        "forbidden_hits": forbidden,
    }


def _validate_hdf5(path: Path) -> dict[str, Any]:
    forbidden: list[str] = []
    first_datasets: list[dict[str, Any]] = []
    trace_dataset_count = 0
    event_dataset_count = 0
    dataset_count = 0
    group_count = 0
    root_attrs: dict[str, str] = {}
    with h5py.File(path, "r") as handle:
        root_attrs = {str(key): _stringify(value) for key, value in handle.attrs.items()}
        for key, value in root_attrs.items():
            forbidden.extend(_hits(key, f"root_attr.{key}"))
            forbidden.extend(_hits(value, f"root_attr.{key}"))

        def visitor(name: str, obj: Any) -> None:
            nonlocal dataset_count, group_count, trace_dataset_count, event_dataset_count
            forbidden.extend(_hits(name, f"hdf5_path.{name}"))
            if isinstance(obj, h5py.Group):
                group_count += 1
                return
            if not isinstance(obj, h5py.Dataset):
                return
            dataset_count += 1
            lowered = name.lower()
            is_trace = any(marker in lowered for marker in ("channeldata", "framedata", "trace", "analogstream"))
            is_event = any(marker in lowered for marker in ("evententity", "timestamp", "segmentdata", "spike"))
            trace_dataset_count += int(is_trace)
            event_dataset_count += int(is_event)
            for key, value in obj.attrs.items():
                forbidden.extend(_hits(str(key), f"dataset_attr.{name}.{key}"))
                forbidden.extend(_hits(_stringify(value), f"dataset_attr.{name}.{key}"))
            if len(first_datasets) < 20:
                first_datasets.append({"path": name, "shape": tuple(int(size) for size in obj.shape), "dtype": str(obj.dtype)})

        handle.visititems(visitor)
    protocol_type = root_attrs.get("McsHdf5ProtocolType", "")
    readonly_data_evidence = trace_dataset_count > 0 or event_dataset_count > 0
    recognized = protocol_type == "RawData" or path.suffix.lower() == ".nwb"
    file_format = "mcs_hdf5_rawdata" if protocol_type == "RawData" else "nwb_hdf5" if path.suffix.lower() == ".nwb" else "hdf5_export"
    return {
        "file_format": file_format,
        "safety_scan_passed": not forbidden,
        "readonly_data_evidence": readonly_data_evidence,
        "recognized_readonly_format": recognized,
        "root_attrs": root_attrs,
        "dataset_count": dataset_count,
        "group_count": group_count,
        "trace_dataset_count": trace_dataset_count,
        "event_dataset_count": event_dataset_count,
        "first_datasets": tuple(first_datasets),
        "forbidden_hits": forbidden,
    }


def _validate_zip(path: Path) -> dict[str, Any]:
    forbidden: list[str] = []
    first_datasets: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    for name in names[:200]:
        forbidden.extend(_hits(name, f"zip_member.{name}"))
        first_datasets.append({"path": name, "shape": tuple(), "dtype": "zip_member"})
    readonly_data_evidence = any(Path(name).suffix.lower() in SUPPORTED_EXTENSIONS - {".zip"} for name in names)
    return {
        "file_format": "zip_export_archive",
        "safety_scan_passed": not forbidden,
        "readonly_data_evidence": readonly_data_evidence,
        "recognized_readonly_format": False,
        "root_attrs": {},
        "dataset_count": len(names),
        "group_count": 0,
        "trace_dataset_count": 0,
        "event_dataset_count": 0,
        "first_datasets": tuple(first_datasets[:20]),
        "forbidden_hits": forbidden,
    }


def validate_external_export_sample_v524(path: str | Path, root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    candidate = candidate.resolve()
    errors: list[str] = []
    sha256 = ""
    details: dict[str, Any] = {
        "file_format": "unsupported",
        "safety_scan_passed": False,
        "readonly_data_evidence": False,
        "recognized_readonly_format": False,
        "root_attrs": {},
        "dataset_count": 0,
        "group_count": 0,
        "trace_dataset_count": 0,
        "event_dataset_count": 0,
        "first_datasets": tuple(),
        "forbidden_hits": [],
    }
    try:
        sha256 = _sha256(candidate)
        suffix = candidate.suffix.lower()
        if suffix in HDF5_EXTENSIONS:
            details = _validate_hdf5(candidate)
        elif suffix == ".json":
            details = _validate_json(candidate)
        elif suffix == ".csv":
            details = _validate_csv(candidate)
        elif suffix == ".zip":
            details = _validate_zip(candidate)
        else:
            errors.append(f"unsupported_extension:{suffix}")
    except Exception as exc:
        errors.append(f"validation_error:{type(exc).__name__}:{exc}")
    safety_passed = bool(details.get("safety_scan_passed")) and not errors
    readonly_data_evidence = bool(details.get("readonly_data_evidence"))
    recognized = bool(details.get("recognized_readonly_format"))
    if safety_passed and readonly_data_evidence and recognized:
        gate_status = "readonly_external_export_validated"
    elif errors:
        gate_status = "external_export_validation_error"
    elif not safety_passed:
        gate_status = "blocked_live_control_terms_detected"
    elif not readonly_data_evidence:
        gate_status = "present_without_readonly_trace_or_event_data"
    else:
        gate_status = "present_needs_format_mapping"
    report = ExternalExportValidationReportV524(
        relative_path=_relative(candidate, project_root),
        platform_hint=_platform_hint(candidate),
        file_format=str(details.get("file_format", "unsupported")),
        file_size_bytes=candidate.stat().st_size if candidate.exists() else 0,
        sha256=sha256,
        gate_status=gate_status,
        safety_scan_passed=safety_passed,
        readonly_data_evidence=readonly_data_evidence,
        recognized_readonly_format=recognized,
        root_attrs=dict(details.get("root_attrs", {})),
        dataset_count=int(details.get("dataset_count", 0)),
        group_count=int(details.get("group_count", 0)),
        trace_dataset_count=int(details.get("trace_dataset_count", 0)),
        event_dataset_count=int(details.get("event_dataset_count", 0)),
        first_datasets=tuple(dict(item) for item in details.get("first_datasets", tuple())),
        source_reference=KNOWN_SOURCE_BY_SHA256.get(sha256, {}),
        forbidden_hits=tuple(str(item) for item in details.get("forbidden_hits", [])),
        errors=tuple(errors),
    )
    return {"report": report.to_dict()}


def build_external_export_validation_gate_v524(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    candidates = find_external_export_candidates_v524(project_root)
    reports = [validate_external_export_sample_v524(path, project_root)["report"] for path in candidates]
    validated = [report for report in reports if report["gate_status"] == "readonly_external_export_validated"]
    blocked = [report for report in reports if report["gate_status"] != "readonly_external_export_validated"]
    if validated:
        overall_status = "real_external_readonly_export_validated"
    elif candidates:
        overall_status = "external_export_material_present_needs_validation"
    else:
        overall_status = "external_export_material_missing"
    return {
        "version": "v5.24",
        "phase": "real_external_readonly_export_validation",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "candidate_export_count": len(candidates),
        "validated_export_count": len(validated),
        "blocked_export_count": len(blocked),
        "real_external_ready": bool(validated),
        "validated_export_paths": [report["relative_path"] for report in validated],
        "blocked_export_paths": [report["relative_path"] for report in blocked],
        "platforms_validated": sorted({report["platform_hint"] for report in validated}),
        "reports": reports,
        "required_next_steps": [] if validated else [
            "place one small read-only export under data/external/api_exports/<platform>/",
            "verify recorded trace/event data without live actuation fields",
            "rerun v5.24 and v5.17 gates",
        ],
        "claim_boundary": "v5.24 validates non-secret read-only export files only. It does not prove live external API access, stimulation, closed-loop control, production BioSDK or BiC OS readiness.",
    }


def write_external_export_validation_outputs_v524(audit: dict[str, Any], out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json",
        "reports_json": out / "V524_EXTERNAL_EXPORT_VALIDATION_REPORTS.json",
        "reports_csv": out / "V524_EXTERNAL_EXPORT_VALIDATION_REPORTS.csv",
        "markdown_report": out / "BIOGPU_V524_EXTERNAL_EXPORT_VALIDATION_REPORT.md",
    }
    summary = {key: value for key, value in audit.items() if key != "reports"}
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["reports_json"].write_text(json.dumps({"reports": audit["reports"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_reports_csv(paths["reports_csv"], audit["reports"])
    paths["markdown_report"].write_text(_markdown_report(audit), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_reports_csv(path: Path, reports: list[dict[str, Any]]) -> None:
    fieldnames = [
        "relative_path",
        "platform_hint",
        "file_format",
        "file_size_bytes",
        "sha256",
        "gate_status",
        "safety_scan_passed",
        "readonly_data_evidence",
        "recognized_readonly_format",
        "dataset_count",
        "trace_dataset_count",
        "event_dataset_count",
        "forbidden_hits",
        "errors",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            payload = dict(report)
            payload["forbidden_hits"] = " | ".join(str(item) for item in report.get("forbidden_hits", []))
            payload["errors"] = " | ".join(str(item) for item in report.get("errors", []))
            writer.writerow({key: payload.get(key) for key in fieldnames})


def _markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.24 External Export Validation",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Candidate exports: `{audit['candidate_export_count']}`",
        f"- Validated exports: `{audit['validated_export_count']}`",
        f"- Real external ready: `{audit['real_external_ready']}`",
        f"- BiC OS locked: `{audit['bic_os_phase_locked']}`",
        "",
        "## Reports",
        "",
    ]
    for report in audit["reports"]:
        lines.append(f"- `{report['relative_path']}`: `{report['gate_status']}`, format `{report['file_format']}`, sha256 `{report['sha256']}`")
    lines.extend(["", "## Boundary", "", audit["claim_boundary"], ""])
    return "\n".join(lines)


def run_external_export_validation_workflow_v524(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    audit = build_external_export_validation_gate_v524(project_root)
    v524_paths = write_external_export_validation_outputs_v524(audit, project_root / DEFAULT_OUT)

    from biogpu.sdk.external_readonly_v517 import DEFAULT_OUT as V517_OUT
    from biogpu.sdk.external_readonly_v517 import write_external_readonly_outputs_v517
    from biogpu.sdk.sample_acquisition_v514 import DEFAULT_OUT as V514_OUT
    from biogpu.sdk.sample_acquisition_v514 import build_sample_acquisition_gate_v514, write_sample_acquisition_outputs_v514
    from biogpu.sdk.cross_dataset_evidence_v521 import DEFAULT_OUT as V521_OUT
    from biogpu.sdk.cross_dataset_evidence_v521 import build_cross_dataset_evidence_pack_v521, write_cross_dataset_evidence_outputs_v521
    from biogpu.sdk.public_examples_v522 import DEFAULT_OUT as V522_OUT
    from biogpu.sdk.public_examples_v522 import build_biosdk_public_examples_gate_v522, write_biosdk_public_examples_outputs_v522

    v517_paths = write_external_readonly_outputs_v517(project_root, project_root / V517_OUT)
    v514_gate = build_sample_acquisition_gate_v514(project_root)
    v514_paths = write_sample_acquisition_outputs_v514(v514_gate, project_root / V514_OUT)
    v521_audit = build_cross_dataset_evidence_pack_v521(project_root)
    v521_paths = write_cross_dataset_evidence_outputs_v521(v521_audit, project_root / V521_OUT)
    v522_gate = build_biosdk_public_examples_gate_v522(project_root)
    v522_paths = write_biosdk_public_examples_outputs_v522(v522_gate, project_root / V522_OUT)

    return {
        **audit,
        "refreshed_outputs": {
            "v524": v524_paths,
            "v517": v517_paths,
            "v514": v514_paths,
            "v521": v521_paths,
            "v522": v522_paths,
        },
        "downstream_status": {
            "v514_overall_status": v514_gate.get("overall_status"),
            "v521_overall_status": v521_audit.get("overall_status"),
            "v522_overall_status": v522_gate.get("overall_status"),
            "full_sample_proof_ready": v514_gate.get("full_sample_proof_ready"),
            "external_partner_evidence_ready": v521_audit.get("external_partner_evidence_ready"),
        },
        "direct_answer": {
            "did_we_find_real_external_export": "yes" if audit["real_external_ready"] else "not_yet",
            "is_full_biosdk_proven": "no",
            "is_bic_os_ready": "no",
            "next_best_build_step": "review SDK release-candidate packaging with v5.24 evidence attached" if audit["real_external_ready"] else "obtain one small read-only export/token and rerun v5.24",
        },
    }