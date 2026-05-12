"""BioSDK vendor/user-upload read-only sample gate, v5.19."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.datasets.importers_v42 import DatasetImportRequestV42, build_importer_catalog_v42
from biogpu.safety.boundary_v35 import FORBIDDEN_LIVE_FIELDS_V35, find_forbidden_keys_v35


DEFAULT_OUT = Path("outputs/v519_vendor_user_upload_gate")
VENDOR_PATTERNS = ("data/external/vendor_exports/**/*",)
USER_UPLOAD_PATTERNS = ("data/external/user_upload_samples/**/*",)
SUPPORTED_EXTENSIONS = {"csv", "json", "nwb", "h5", "hdf5", "zip"}
TEXT_SCAN_EXTENSIONS = {"csv", "json", "txt", "tsv", "md", "yaml", "yml"}
MAX_TEXT_SCAN_BYTES = 64_000


@dataclass(frozen=True)
class VendorUploadSampleReportV519:
    path: str
    sample_family: str
    importer_id: str
    gate_status: str
    extension: str
    size_bytes: int
    sha256: str
    supported_extension: bool
    schema_hint: str
    safety_scan_passed: bool
    forbidden_terms: tuple[str, ...]
    import_status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(paths))


def find_vendor_upload_samples_v519(root: str | Path = ".") -> list[Path]:
    project_root = Path(root).resolve()
    return sorted(set(_files(project_root, VENDOR_PATTERNS) + _files(project_root, USER_UPLOAD_PATTERNS)))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extension(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def _sample_family(path: Path) -> str:
    normalized = str(path).replace("\\", "/").lower()
    if "/vendor_exports/" in normalized:
        return "vendor_export"
    if "/user_upload_samples/" in normalized:
        return "user_upload"
    return "unknown"


def _importer_id_for_family(sample_family: str) -> str:
    return "vendor_export_v42" if sample_family == "vendor_export" else "user_upload_v42"


def _schema_hint(path: Path, extension: str) -> str:
    if extension in {"h5", "hdf5", "nwb"}:
        try:
            with path.open("rb") as handle:
                magic = handle.read(8)
            return "hdf5_magic_present" if magic == b"\x89HDF\r\n\x1a\n" else "hdf5_extension_magic_missing"
        except OSError:
            return "binary_unreadable"
    if extension == "zip":
        try:
            with path.open("rb") as handle:
                magic = handle.read(4)
            return "zip_magic_present" if magic.startswith(b"PK") else "zip_extension_magic_missing"
        except OSError:
            return "binary_unreadable"
    if extension == "json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return "json_parse_failed"
        return "json_object" if isinstance(payload, dict) else "json_array" if isinstance(payload, list) else "json_scalar"
    if extension in {"csv", "tsv"}:
        try:
            first_line = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()[0]
        except Exception:
            return "csv_header_unreadable"
        delimiter = "tab" if "\t" in first_line else "comma" if "," in first_line else "unknown"
        return f"text_table_header_{delimiter}"
    return "unsupported_or_unknown"


def _forbidden_terms_in_text(text: str) -> list[str]:
    normalized = text.lower().replace("-", "_").replace(" ", "_")
    return sorted(term for term in FORBIDDEN_LIVE_FIELDS_V35 if term in normalized)


def _safety_scan(path: Path, extension: str) -> tuple[bool, tuple[str, ...]]:
    terms: set[str] = set()
    terms.update(find_forbidden_keys_v35(path.parts))
    if extension == "json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(payload, dict):
                terms.update(find_forbidden_keys_v35(payload.keys()))
                terms.update(_forbidden_terms_in_text(json.dumps(payload, sort_keys=True)))
            elif isinstance(payload, list):
                terms.update(_forbidden_terms_in_text(json.dumps(payload, sort_keys=True)))
        except Exception:
            pass
    elif extension in TEXT_SCAN_EXTENSIONS:
        try:
            text = path.read_bytes()[:MAX_TEXT_SCAN_BYTES].decode("utf-8", errors="ignore")
            terms.update(_forbidden_terms_in_text(text))
        except OSError:
            terms.add("unreadable_text_scan")
    return not terms, tuple(sorted(terms))


def validate_vendor_upload_sample_v519(path: str | Path, root: str | Path = ".") -> dict[str, Any]:
    sample_path = Path(path).resolve()
    project_root = Path(root).resolve()
    sample_family = _sample_family(sample_path)
    importer_id = _importer_id_for_family(sample_family)
    extension = _extension(sample_path)
    supported_extension = extension in SUPPORTED_EXTENSIONS
    blockers: list[str] = []
    warnings: list[str] = []
    if not sample_path.exists():
        blockers.append("sample file missing")
        size_bytes = 0
        digest = ""
        schema_hint = "missing"
        safety_scan_passed = False
        forbidden_terms: tuple[str, ...] = tuple()
        import_status = "not_run"
    else:
        size_bytes = sample_path.stat().st_size
        digest = _sha256(sample_path)
        schema_hint = _schema_hint(sample_path, extension)
        safety_scan_passed, forbidden_terms = _safety_scan(sample_path, extension)
        if sample_family == "unknown":
            blockers.append("sample is outside vendor_exports/user_upload_samples")
        if not supported_extension:
            blockers.append(f"unsupported extension: {extension or 'none'}")
        if not safety_scan_passed:
            blockers.append("safety scan found forbidden live-control fields")
        catalog = build_importer_catalog_v42()
        importer = catalog[importer_id]
        try:
            source_uri = str(sample_path.relative_to(project_root)).replace("\\", "/")
        except ValueError:
            source_uri = str(sample_path)
        request = DatasetImportRequestV42(
            dataset_id="vendor_or_user_upload_sample",
            importer_id=importer_id,
            source_uri=source_uri,
            mode="read_only_replay",
            options={"extension": extension, "schema_hint": schema_hint, "sha256": digest},
        )
        result = importer.import_readonly(request).to_dict()
        import_status = str(result.get("status", "unknown"))
        warnings.extend(str(item) for item in result.get("warnings", []))
        if import_status == "blocked":
            blockers.append("v4.2 importer blocked request")
    gate_status = "readonly_sample_validated" if sample_path.exists() and supported_extension and safety_scan_passed and import_status != "blocked" and not blockers else "sample_blocked_or_incomplete"
    report = VendorUploadSampleReportV519(
        path=str(sample_path),
        sample_family=sample_family,
        importer_id=importer_id,
        gate_status=gate_status,
        extension=extension,
        size_bytes=size_bytes,
        sha256=digest,
        supported_extension=supported_extension,
        schema_hint=schema_hint,
        safety_scan_passed=safety_scan_passed,
        forbidden_terms=forbidden_terms,
        import_status=import_status,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )
    return {"report": report.to_dict()}


def build_vendor_upload_gate_v519(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    samples = find_vendor_upload_samples_v519(project_root)
    detailed = [validate_vendor_upload_sample_v519(path, project_root) for path in samples]
    reports = [item["report"] for item in detailed]
    valid_reports = [report for report in reports if report["gate_status"] == "readonly_sample_validated"]
    blocked_reports = [report for report in reports if report["gate_status"] != "readonly_sample_validated"]
    vendor_valid = any(report["sample_family"] == "vendor_export" for report in valid_reports)
    user_valid = any(report["sample_family"] == "user_upload" for report in valid_reports)
    if valid_reports:
        overall_status = "vendor_user_upload_readonly_samples_validated"
    elif samples:
        overall_status = "vendor_user_upload_samples_blocked_or_unsupported"
    else:
        overall_status = "vendor_user_upload_sample_missing_required"
    required_next_steps = [
        "promote validated non-secret sample reports into BioSDK evidence bundles",
        "keep uploaded files read-only and free of live-control fields",
    ] if valid_reports else [
        "place one read-only vendor export under data/external/vendor_exports/ or one user fixture under data/external/user_upload_samples/",
        "keep uploaded files read-only and free of live stimulation, pinout, wiring or wet-lab recipe fields",
        "run the v5.19 gate to produce sha256, schema hint and importer routing reports",
        "promote only validated non-secret sample reports into BioSDK evidence bundles",
    ]
    return {
        "version": "v5.19",
        "phase": "vendor_user_upload_readonly_gate",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "sample_count": len(samples),
        "validated_sample_count": len(valid_reports),
        "blocked_sample_count": len(blocked_reports),
        "vendor_export_validated": vendor_valid,
        "user_upload_validated": user_valid,
        "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
        "sample_reports": reports,
        "required_next_steps": required_next_steps,
        "claim_boundary": "v5.19 validates read-only vendor/user-upload intake contracts and safety scanning only. It does not prove live vendor integration, closed-loop control, or full private-beta readiness without real safe sample exports.",
    }


def write_vendor_upload_outputs_v519(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    project_root = Path(root).resolve()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    gate = build_vendor_upload_gate_v519(project_root)
    paths = {
        "summary_json": out / "V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json",
        "sample_reports_json": out / "V519_VENDOR_USER_UPLOAD_SAMPLE_REPORTS.json",
        "sample_reports_csv": out / "V519_VENDOR_USER_UPLOAD_SAMPLE_REPORTS.csv",
        "intake_template_json": out / "V519_VENDOR_USER_UPLOAD_INTAKE_TEMPLATE.json",
        "markdown_report": out / "BIOGPU_V519_VENDOR_USER_UPLOAD_GATE_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["sample_reports_json"].write_text(json.dumps({"samples": gate["sample_reports"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["intake_template_json"].write_text(json.dumps(_intake_template(), indent=2, ensure_ascii=False), encoding="utf-8")
    _write_reports_csv(paths["sample_reports_csv"], gate["sample_reports"])
    paths["markdown_report"].write_text(_markdown_report(gate), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _intake_template() -> dict[str, Any]:
    return {
        "target_directories": ["data/external/vendor_exports/", "data/external/user_upload_samples/"],
        "accepted_extensions": sorted(SUPPORTED_EXTENSIONS),
        "mode": "read_only_replay",
        "forbidden_fields": sorted(FORBIDDEN_LIVE_FIELDS_V35),
        "note": "Do not include live stimulation/control settings, pinouts, wiring maps or wet-lab recipes in uploaded fixtures.",
    }


def _write_reports_csv(path: Path, reports: list[dict[str, Any]]) -> None:
    fields = ["path", "sample_family", "importer_id", "gate_status", "extension", "size_bytes", "sha256", "schema_hint", "safety_scan_passed", "forbidden_terms", "blockers"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for report in reports:
            writer.writerow({field: ";".join(report[field]) if field in {"forbidden_terms", "blockers"} else report.get(field, "") for field in fields})


def _markdown_report(gate: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.19 Vendor/User Upload Gate",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- Samples: `{gate['sample_count']}`",
        f"- Validated samples: `{gate['validated_sample_count']}`",
        f"- Blocked samples: `{gate['blocked_sample_count']}`",
        f"- Vendor export validated: `{gate['vendor_export_validated']}`",
        f"- User upload validated: `{gate['user_upload_validated']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        "",
        "## Required Next Steps",
        "",
    ]
    for step in gate["required_next_steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)
