"""NSI-1.0 adapter conformance helpers for v5.2."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from biogpu.standards.nsi_v10 import BLOCKED_BY_DEFAULT, validate_nsi_object


@dataclass(frozen=True)
class AdapterConformanceCheck:
    name: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdapterConformanceReport:
    adapter_id: str
    adapter_kind: str
    valid: bool
    contract: dict[str, Any]
    checks: list[AdapterConformanceCheck]
    validation_report: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _check(name: str, passed: bool, **details: Any) -> AdapterConformanceCheck:
    return AdapterConformanceCheck(name=name, status="pass" if passed else "fail", details=details)


def _callable_names(adapter: Any, method_names: list[str]) -> list[str]:
    return [name for name in method_names if callable(getattr(adapter, name, None))]


def _contract_validation_check(contract: dict[str, Any]) -> tuple[AdapterConformanceCheck, dict[str, Any]]:
    report = validate_nsi_object("BioComputeAdapterContract", contract).to_dict()
    return _check("nsi_contract_schema", bool(report["valid"]), issue_count=len(report["issues"])), report


def contract_for_dataset_importer(importer: Any) -> dict[str, Any]:
    supported_modes = sorted(getattr(importer, "supported_modes", []))
    supported_extensions = sorted(getattr(importer, "supported_extensions", []))
    read_methods = _callable_names(importer, ["inspect", "import_readonly"])
    return {
        "adapter_id": getattr(importer, "importer_id", importer.__class__.__name__),
        "platform": "dataset_importer",
        "capabilities": {
            "produces": getattr(importer, "produces", "BioComputeTrace"),
            "supported_modes": supported_modes,
            "supported_extensions": supported_extensions,
            "live_actuation": False,
        },
        "read_methods": read_methods,
        "safety_profile": {
            "profile_id": f"{getattr(importer, 'importer_id', 'dataset_importer')}_read_only_profile",
            "mode": "read_only" if "read_only_replay" in supported_modes else "metadata_only",
            "allowed_operations": ["metadata_read", "trace_read", "schema_inspect"],
            "blocked_operations": BLOCKED_BY_DEFAULT,
            "approval_required": False,
        },
        "conformance_tests": ["nsi_required_fields", "method_presence", "read_only_safety", "inspect_smoke"],
    }


def run_dataset_importer_conformance(importer: Any) -> AdapterConformanceReport:
    from biogpu.datasets.importers_v42 import DatasetImportRequestV42

    contract = contract_for_dataset_importer(importer)
    contract_check, validation_report = _contract_validation_check(contract)
    checks = [contract_check]
    checks.append(_check("read_methods_present", set(["inspect", "import_readonly"]).issubset(set(contract["read_methods"]))))
    checks.append(_check("no_live_actuation_capability", contract["capabilities"].get("live_actuation") is False))

    mode = "metadata_only" if "metadata_only" in getattr(importer, "supported_modes", set()) else "read_only_replay"
    request = DatasetImportRequestV42(
        dataset_id="nsi_conformance_reference",
        importer_id=contract["adapter_id"],
        source_uri="memory://nsi-conformance",
        mode=mode,
    )
    result = importer.inspect(request)
    checks.append(_check("inspect_smoke", result.status == "metadata_ready", status=result.status, warnings=result.warnings))
    checks.append(_check("no_live_control_performed", result.live_control_performed is False))

    valid = all(check.status == "pass" for check in checks)
    return AdapterConformanceReport(
        adapter_id=contract["adapter_id"],
        adapter_kind="dataset_importer",
        valid=valid,
        contract=contract,
        checks=checks,
        validation_report=validation_report,
    )


def run_all_dataset_importer_conformance() -> list[AdapterConformanceReport]:
    from biogpu.datasets.importers_v42 import build_importer_catalog_v42

    catalog = build_importer_catalog_v42()
    return [run_dataset_importer_conformance(catalog[key]) for key in sorted(catalog)]


def contract_for_vendor_adapter(adapter: Any) -> dict[str, Any]:
    capability = adapter.capability.to_dict()
    read_methods = _callable_names(adapter, ["read_spike_stream", "read_raw_trace", "export_metadata"])
    return {
        "adapter_id": getattr(adapter, "adapter_id", adapter.__class__.__name__),
        "platform": capability.get("platform_class", "vendor_adapter"),
        "capabilities": {
            **capability,
            "live_actuation": False,
        },
        "read_methods": read_methods,
        "safety_profile": {
            "profile_id": f"{getattr(adapter, 'adapter_id', 'vendor_adapter')}_metadata_profile",
            "mode": "read_only",
            "allowed_operations": ["metadata_read", "trace_read", "dry_run_probe"],
            "blocked_operations": BLOCKED_BY_DEFAULT,
            "approval_required": False,
        },
        "conformance_tests": ["nsi_required_fields", "method_presence", "dry_run_no_live_output", "metadata_export"],
    }


def run_vendor_adapter_conformance(adapter: Any) -> AdapterConformanceReport:
    contract = contract_for_vendor_adapter(adapter)
    contract_check, validation_report = _contract_validation_check(contract)
    checks = [contract_check]
    required_methods = ["connect", "validate_session", "read_spike_stream", "read_raw_trace", "export_metadata", "close"]
    present_methods = _callable_names(adapter, required_methods)
    checks.append(_check("required_methods_present", set(required_methods).issubset(set(present_methods)), present=present_methods))
    checks.append(_check("no_live_actuation_capability", contract["capabilities"].get("live_actuation") is False))

    connect_result = adapter.connect()
    validation_errors = adapter.validate_session({"run_mode": "dry_run"})
    metadata = adapter.export_metadata()
    adapter.close()
    checks.append(_check("dry_run_connect", connect_result.get("connected") is True and connect_result.get("live_hardware") is False, result=connect_result))
    checks.append(_check("dry_run_session_validation", validation_errors == [], errors=validation_errors))
    checks.append(_check("metadata_export", metadata.get("safety_boundary", {}).get("no_live_output_in_v25") is True))

    valid = all(check.status == "pass" for check in checks)
    return AdapterConformanceReport(
        adapter_id=contract["adapter_id"],
        adapter_kind="vendor_adapter_stub",
        valid=valid,
        contract=contract,
        checks=checks,
        validation_report=validation_report,
    )


def run_all_vendor_adapter_conformance() -> list[AdapterConformanceReport]:
    from biogpu.substrates.vendor_registry_v25 import build_v25_vendor_adapters

    return [run_vendor_adapter_conformance(adapter) for adapter in build_v25_vendor_adapters(mode="dry_run")]