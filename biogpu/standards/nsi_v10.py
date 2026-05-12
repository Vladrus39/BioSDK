"""NSI-1.0 schemas for Neural Substrate Interface.

The schemas are minimal JSON-schema-like dictionaries so they remain lightweight
and do not require pydantic/jsonschema at import time.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal


NSI_VERSION = "NSI-1.0"
NSI_SCHEMA_STATUS = "frozen_interface_profile"

SAFETY_MODES = ["replay", "metadata_only", "read_only", "live_shadow", "approved_actuation"]
CLAIM_LEVELS = [
    "software_replay_only",
    "read_only_api_validation",
    "live_shadow_validation",
    "approved_live_biological_validation",
    "comparative_advantage_requires_telemetry",
]
BLOCKED_BY_DEFAULT = [
    "live_stimulation",
    "electrode_actuation",
    "wetware_environment_control",
    "free_form_vendor_write",
]


@dataclass(frozen=True)
class NSISchemaSpec:
    name: str
    purpose: str
    required_fields: List[str]
    optional_fields: List[str]
    maps_to_existing_standards: List[str]
    schema: Dict[str, Any]


@dataclass(frozen=True)
class NSIValidationIssue:
    level: Literal["error", "warning"]
    path: str
    message: str


@dataclass(frozen=True)
class NSIValidationReport:
    schema_name: str
    valid: bool
    checked_at_utc: str
    issues: List[NSIValidationIssue]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def errors(self) -> List[NSIValidationIssue]:
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> List[NSIValidationIssue]:
        return [issue for issue in self.issues if issue.level == "warning"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _object_schema(
    required_fields: List[str],
    optional_fields: List[str],
    field_types: Dict[str, str],
) -> Dict[str, Any]:
    properties: Dict[str, Dict[str, str]] = {}
    for field in required_fields + optional_fields:
        properties[field] = {"type": field_types.get(field, "string")}
    return {
        "type": "object",
        "required": required_fields,
        "properties": properties,
        "additionalProperties": True,
    }


def _schema(
    name: str,
    purpose: str,
    required_fields: List[str],
    optional_fields: List[str],
    maps_to_existing_standards: List[str],
    field_types: Dict[str, str],
) -> NSISchemaSpec:
    return NSISchemaSpec(
        name=name,
        purpose=purpose,
        required_fields=required_fields,
        optional_fields=optional_fields,
        maps_to_existing_standards=maps_to_existing_standards,
        schema=_object_schema(required_fields, optional_fields, field_types),
    )


NSI_SCHEMAS: List[NSISchemaSpec] = [
    _schema(
        name="BioComputeTrace",
        purpose="A common representation of spikes, traces, events, channels and metadata from replay/API/vendor sources.",
        required_fields=["trace_id", "source", "timebase", "channels", "events", "metadata", "checksum"],
        optional_fields=["raw_trace_uri", "nwb_uri", "vendor_export_uri", "stimulus_markers", "lineage_metadata"],
        maps_to_existing_standards=["NWB", "HDF5", "CSV exports", "vendor APIs"],
        field_types={"source": "object", "timebase": "object", "channels": "array", "events": "array", "metadata": "object", "stimulus_markers": "array", "lineage_metadata": "object"},
    ),
    _schema(
        name="BioComputeTaskManifest",
        purpose="Describes what task to run, which data to use, split policy, decoder, safety mode and output bundle.",
        required_fields=["manifest_id", "mode", "dataset", "task", "split_policy", "decoder", "safety_profile", "output_dir"],
        optional_fields=["shuffle_count", "bootstrap_iterations", "ablation", "api_platform", "license_tier"],
        maps_to_existing_standards=["BioGPU-Core manifests", "workflow job specs"],
        field_types={"dataset": "object", "task": "object", "split_policy": "object", "decoder": "object", "safety_profile": "object", "shuffle_count": "integer", "bootstrap_iterations": "integer", "ablation": "object"},
    ),
    _schema(
        name="BioComputeFeatureBatch",
        purpose="Feature matrix plus labels and biological metadata used for readout/benchmarking.",
        required_fields=["X", "feature_names", "labels", "sample_metadata", "feature_extractor", "checksum"],
        optional_fields=["culture_id", "lineage_id", "condition", "stimulus_window", "artifact_flags"],
        maps_to_existing_standards=["NumPy NPZ", "Parquet", "CSV metadata"],
        field_types={"X": "array", "feature_names": "array", "labels": "array", "sample_metadata": "array", "stimulus_window": "object", "artifact_flags": "array"},
    ),
    _schema(
        name="BioComputeReadoutResult",
        purpose="Prediction/metric output from readout models with baseline comparison and claim level.",
        required_fields=["result_id", "decoder", "metrics", "baseline", "claim_level", "created_at"],
        optional_fields=["confusion_matrix", "calibration", "confidence_intervals", "plots", "model_uri"],
        maps_to_existing_standards=["JSON metrics", "ML evaluation reports"],
        field_types={"decoder": "object", "metrics": "object", "baseline": "object", "confusion_matrix": "array", "calibration": "object", "confidence_intervals": "object", "plots": "array"},
    ),
    _schema(
        name="BioComputeResultBundle",
        purpose="Reproducibility bundle containing manifests, metrics, logs, checksums, plots and software versions.",
        required_fields=["bundle_id", "manifest", "metrics", "audit_log", "checksums", "software_versions", "claim_level"],
        optional_fields=["figures", "tables", "raw_links", "environment", "signature"],
        maps_to_existing_standards=["RO-Crate-style bundles", "ML experiment artifacts"],
        field_types={"manifest": "object", "metrics": "object", "audit_log": "array", "checksums": "object", "software_versions": "object", "figures": "array", "tables": "array", "raw_links": "array", "environment": "object", "signature": "object"},
    ),
    _schema(
        name="BioComputeSafetyProfile",
        purpose="Declares permissions and prohibited fields for replay/read-only/live-shadow/approved-actuation modes.",
        required_fields=["profile_id", "mode", "allowed_operations", "blocked_operations", "approval_required"],
        optional_fields=["operator", "protocol_id", "vendor_allowlist", "expires_at"],
        maps_to_existing_standards=["access control policies", "lab protocol approval records"],
        field_types={"allowed_operations": "array", "blocked_operations": "array", "approval_required": "boolean", "vendor_allowlist": "array"},
    ),
    _schema(
        name="BioComputeAdapterContract",
        purpose="Minimum conformance requirements for dataset/API/device adapters.",
        required_fields=["adapter_id", "platform", "capabilities", "read_methods", "safety_profile", "conformance_tests"],
        optional_fields=["write_methods", "latency_profile", "vendor_version", "credentials_ref"],
        maps_to_existing_standards=["SDK adapter interfaces", "device driver capability descriptors"],
        field_types={"capabilities": "object", "read_methods": "array", "safety_profile": "object", "conformance_tests": "array", "write_methods": "array", "latency_profile": "object"},
    ),
]

NSI_SCHEMA_BY_NAME = {schema.name: schema for schema in NSI_SCHEMAS}


def nsi_spec() -> Dict[str, object]:
    return {
        "standard": NSI_VERSION,
        "draft_lineage": "NSI-1.0-draft",
        "schema_status": NSI_SCHEMA_STATUS,
        "full_name": "Neural Substrate Interface 1.0",
        "project": "BioGPU-Core / BioCompute Runtime",
        "principle": "Do not replace NWB/HDF5/vendor formats; define a runtime interface profile above them.",
        "schemas": [asdict(x) for x in NSI_SCHEMAS],
        "safety_modes": SAFETY_MODES,
        "default_mode": "replay/read_only",
        "claim_levels": CLAIM_LEVELS,
        "blocked_by_default": BLOCKED_BY_DEFAULT,
    }


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    return True


def _issue(level: Literal["error", "warning"], path: str, message: str) -> NSIValidationIssue:
    return NSIValidationIssue(level=level, path=path, message=message)


def _report(schema_name: str, issues: List[NSIValidationIssue]) -> NSIValidationReport:
    return NSIValidationReport(
        schema_name=schema_name,
        valid=not any(issue.level == "error" for issue in issues),
        checked_at_utc=_utc_now(),
        issues=issues,
    )


def validate_nsi_object(schema_name: str, payload: Dict[str, Any]) -> NSIValidationReport:
    issues: List[NSIValidationIssue] = []
    schema = NSI_SCHEMA_BY_NAME.get(schema_name)
    if schema is None:
        return _report(schema_name, [_issue("error", "$", f"unknown NSI schema: {schema_name}")])
    if not isinstance(payload, dict):
        return _report(schema_name, [_issue("error", "$", "payload must be an object")])

    properties = schema.schema["properties"]
    for field in schema.required_fields:
        if field not in payload:
            issues.append(_issue("error", field, "required field is missing"))
            continue
        value = payload[field]
        if value is None or value == "":
            issues.append(_issue("error", field, "required field is empty"))
            continue
        expected = properties.get(field, {}).get("type", "string")
        if not _type_matches(value, expected):
            issues.append(_issue("error", field, f"expected {expected}, got {type(value).__name__}"))

    for field, value in payload.items():
        if field in properties and value is not None:
            expected = properties[field].get("type", "string")
            if not _type_matches(value, expected):
                issues.append(_issue("error", field, f"expected {expected}, got {type(value).__name__}"))

    if schema_name == "BioComputeSafetyProfile":
        _validate_safety_profile(payload, issues)
    elif schema_name in {"BioComputeReadoutResult", "BioComputeResultBundle"}:
        _validate_claim_level(payload, issues)
    elif schema_name == "BioComputeAdapterContract":
        _validate_adapter_contract(payload, issues)

    return _report(schema_name, issues)


def _validate_safety_profile(payload: Dict[str, Any], issues: List[NSIValidationIssue]) -> None:
    mode = payload.get("mode")
    if mode not in SAFETY_MODES:
        issues.append(_issue("error", "mode", f"mode must be one of {', '.join(SAFETY_MODES)}"))
    approval_required = payload.get("approval_required")
    if mode == "approved_actuation" and approval_required is not True:
        issues.append(_issue("error", "approval_required", "approved_actuation requires approval_required=true"))
    if mode != "approved_actuation":
        allowed = set(payload.get("allowed_operations", []))
        blocked = set(payload.get("blocked_operations", []))
        unsafe_allowed = allowed.intersection(BLOCKED_BY_DEFAULT)
        if unsafe_allowed:
            issues.append(_issue("error", "allowed_operations", "unsafe operations require approved_actuation: " + ", ".join(sorted(unsafe_allowed))))
        missing_blocked = set(BLOCKED_BY_DEFAULT).difference(blocked)
        if missing_blocked:
            issues.append(_issue("warning", "blocked_operations", "safe profiles should block: " + ", ".join(sorted(missing_blocked))))


def _validate_claim_level(payload: Dict[str, Any], issues: List[NSIValidationIssue]) -> None:
    claim_level = payload.get("claim_level")
    if claim_level not in CLAIM_LEVELS:
        issues.append(_issue("error", "claim_level", f"claim_level must be one of {', '.join(CLAIM_LEVELS)}"))
    if claim_level == "comparative_advantage_requires_telemetry":
        metrics = payload.get("metrics", {})
        telemetry = metrics.get("telemetry") if isinstance(metrics, dict) else None
        comparative_baseline = metrics.get("comparative_baseline") if isinstance(metrics, dict) else None
        if not telemetry or not comparative_baseline:
            issues.append(_issue("error", "metrics", "comparative advantage claims require telemetry and comparative_baseline metrics"))


def _validate_adapter_contract(payload: Dict[str, Any], issues: List[NSIValidationIssue]) -> None:
    safety_profile = payload.get("safety_profile", {})
    if isinstance(safety_profile, dict):
        safety_report = validate_nsi_object("BioComputeSafetyProfile", safety_profile)
        for issue in safety_report.issues:
            issues.append(_issue(issue.level, f"safety_profile.{issue.path}", issue.message))
    read_methods = payload.get("read_methods", [])
    conformance_tests = payload.get("conformance_tests", [])
    if isinstance(read_methods, list) and not read_methods:
        issues.append(_issue("error", "read_methods", "adapter contract must expose at least one read method"))
    if isinstance(conformance_tests, list) and not conformance_tests:
        issues.append(_issue("error", "conformance_tests", "adapter contract must declare conformance tests"))
    write_methods = payload.get("write_methods") or []
    mode = safety_profile.get("mode") if isinstance(safety_profile, dict) else None
    if write_methods and mode != "approved_actuation":
        issues.append(_issue("error", "write_methods", "write methods require approved_actuation safety profile"))


def validate_result_bundle(payload: Dict[str, Any]) -> NSIValidationReport:
    base = validate_nsi_object("BioComputeResultBundle", payload)
    issues = list(base.issues)
    for field in ["audit_log", "checksums", "software_versions"]:
        value = payload.get(field)
        if isinstance(value, (list, dict)) and not value:
            issues.append(_issue("error", field, "result bundles must not leave this field empty"))
    return _report("BioComputeResultBundle", issues)


def annotate_claim_level(evidence: Dict[str, Any]) -> Dict[str, Any]:
    mode = evidence.get("mode", evidence.get("safety_mode", "replay"))
    live_actuation = bool(evidence.get("live_actuation_performed", False))
    lab_approved = bool(evidence.get("lab_approval_recorded", False))
    telemetry = bool(evidence.get("telemetry_measured", False))
    comparative = bool(evidence.get("comparative_baseline_passed", False))

    if telemetry and comparative and evidence.get("request_comparative_claim", False):
        claim_level = "comparative_advantage_requires_telemetry"
    elif live_actuation and lab_approved and mode == "approved_actuation":
        claim_level = "approved_live_biological_validation"
    elif mode == "live_shadow" or evidence.get("live_shadow_validated", False):
        claim_level = "live_shadow_validation"
    elif mode == "read_only" or evidence.get("read_only_api_validated", False):
        claim_level = "read_only_api_validation"
    else:
        claim_level = "software_replay_only"

    blocked_claims = ["gpu_replacement", "first_biological_computer", "production_os"]
    if not live_actuation or not lab_approved:
        blocked_claims.append("live_biogpu_proof")
    if not telemetry or not comparative:
        blocked_claims.append("energy_or_performance_advantage")

    return {
        "claim_level": claim_level,
        "mode": mode,
        "blocked_claims": blocked_claims,
        "requires_next": _claim_requires_next(claim_level, telemetry, comparative, live_actuation, lab_approved),
    }


def _claim_requires_next(
    claim_level: str,
    telemetry: bool,
    comparative: bool,
    live_actuation: bool,
    lab_approved: bool,
) -> List[str]:
    required: List[str] = []
    if claim_level == "software_replay_only":
        required.extend(["read-only API or additional dataset validation", "adapter conformance report"])
    if not live_actuation or not lab_approved:
        required.append("approved lab/vendor live validation before live BioGPU claims")
    if not telemetry or not comparative:
        required.append("measured telemetry and matched comparative baseline before advantage claims")
    return required


def reference_nsi_objects() -> Dict[str, Dict[str, Any]]:
    safety_profile = {
        "profile_id": "nsi_reference_read_only",
        "mode": "read_only",
        "allowed_operations": ["metadata_read", "trace_read", "result_bundle_export"],
        "blocked_operations": BLOCKED_BY_DEFAULT,
        "approval_required": False,
    }
    task_manifest = {
        "manifest_id": "nsi_reference_manifest",
        "mode": "read_only",
        "dataset": {"dataset_id": "synthetic_reference", "source": "local"},
        "task": {"task_id": "orientation_decoding", "labels": [0, 45]},
        "split_policy": {"policy": "holdout", "seed": 42},
        "decoder": {"decoder_id": "centroid", "version": "reference"},
        "safety_profile": safety_profile,
        "output_dir": "outputs/v52_nsi_interface/reference",
    }
    readout_result = {
        "result_id": "nsi_reference_readout",
        "decoder": task_manifest["decoder"],
        "metrics": {"balanced_accuracy": 0.5, "n": 2},
        "baseline": {"kind": "chance", "balanced_accuracy": 0.5},
        "claim_level": "software_replay_only",
        "created_at": _utc_now(),
    }
    result_bundle = {
        "bundle_id": "BIOGPU_CORE_V52_NSI_REFERENCE_BUNDLE",
        "manifest": task_manifest,
        "metrics": readout_result["metrics"],
        "audit_log": [{"event": "reference_bundle_created", "status": "ok"}],
        "checksums": {"reference_payload": "sha256:reference-only"},
        "software_versions": {"biogpu_core": "5.2-nsi-interface"},
        "claim_level": "software_replay_only",
        "environment": {"execution": "offline_reference"},
    }
    adapter_contract = {
        "adapter_id": "nsi_reference_adapter",
        "platform": "reference_dataset_importer",
        "capabilities": {"metadata_read": True, "trace_read": True, "live_actuation": False},
        "read_methods": ["inspect", "import_readonly"],
        "safety_profile": safety_profile,
        "conformance_tests": ["required_fields", "read_only_safety", "no_live_actuation"],
    }
    return {
        "BioComputeTrace": {
            "trace_id": "nsi_reference_trace",
            "source": {"kind": "synthetic_reference", "uri": "memory://nsi-reference"},
            "timebase": {"unit": "s", "sample_rate_hz": 1000.0},
            "channels": [{"channel_id": "ch0"}],
            "events": [{"time": 0.0, "label": "reference_event"}],
            "metadata": {"purpose": "schema_reference"},
            "checksum": "sha256:reference-only",
        },
        "BioComputeTaskManifest": task_manifest,
        "BioComputeFeatureBatch": {
            "X": [[0.0, 1.0], [1.0, 0.0]],
            "feature_names": ["f0", "f1"],
            "labels": [0, 45],
            "sample_metadata": [{"sample_id": "s0"}, {"sample_id": "s1"}],
            "feature_extractor": "reference_feature_extractor",
            "checksum": "sha256:reference-only",
        },
        "BioComputeReadoutResult": readout_result,
        "BioComputeResultBundle": result_bundle,
        "BioComputeSafetyProfile": safety_profile,
        "BioComputeAdapterContract": adapter_contract,
    }


def assert_nsi_minimum_complete() -> None:
    data = nsi_spec()
    names = {schema["name"] for schema in data["schemas"]}
    required = {
        "BioComputeTrace",
        "BioComputeTaskManifest",
        "BioComputeFeatureBatch",
        "BioComputeReadoutResult",
        "BioComputeResultBundle",
        "BioComputeSafetyProfile",
        "BioComputeAdapterContract",
    }
    assert required.issubset(names)
    assert data["standard"] == NSI_VERSION
    assert data["schema_status"] == NSI_SCHEMA_STATUS
    assert data["default_mode"] == "replay/read_only"
    for schema in data["schemas"]:
        assert schema["schema"]["type"] == "object"
        assert schema["schema"]["required"] == schema["required_fields"]
