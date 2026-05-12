"""BioGPU-Core v5.2 NSI/interface phase runner."""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from biogpu.standards.nsi_conformance_v52 import (
    run_all_dataset_importer_conformance,
    run_all_vendor_adapter_conformance,
)
from biogpu.standards.nsi_v10 import (
    annotate_claim_level,
    nsi_spec,
    reference_nsi_objects,
    validate_nsi_object,
    validate_result_bundle,
)

DEFAULT_OUT = Path("outputs/v52_nsi_interface")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BioGPU-Core v5.2 NSI Interface Report",
            "",
            "## Scope",
            "",
            "v5.2 freezes the NSI-1.0 runtime-facing schema profile and validates adapter contracts without network or live biological actions.",
            "",
            "## Gate summary",
            "",
            f"- Schemas: {summary['schema_count']}",
            f"- Reference objects valid: {summary['reference_objects_valid']}",
            f"- Dataset importers passed: {summary['dataset_importer_conformance']['passed']}/{summary['dataset_importer_conformance']['total']}",
            f"- Vendor adapters passed: {summary['vendor_adapter_conformance']['passed']}/{summary['vendor_adapter_conformance']['total']}",
            f"- Reference result bundle valid: {summary['result_bundle_valid']}",
            f"- Allowed claim level: {summary['claim_annotation']['claim_level']}",
            "",
            "## Boundary",
            "",
            "No live stimulation, vendor write command, wet-lab protocol, or GPU replacement claim is introduced by this phase.",
            "",
        ]
    )


def run(out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    spec = nsi_spec()
    reference_objects = reference_nsi_objects()
    reference_validations = {
        name: validate_nsi_object(name, payload).to_dict()
        for name, payload in reference_objects.items()
    }
    dataset_reports = [report.to_dict() for report in run_all_dataset_importer_conformance()]
    vendor_reports = [report.to_dict() for report in run_all_vendor_adapter_conformance()]
    result_bundle_report = validate_result_bundle(reference_objects["BioComputeResultBundle"]).to_dict()
    claim_annotation = annotate_claim_level({"mode": "replay", "replay_data_validated": True})

    reference_objects_valid = all(report["valid"] for report in reference_validations.values())
    dataset_passed = sum(1 for report in dataset_reports if report["valid"])
    vendor_passed = sum(1 for report in vendor_reports if report["valid"])

    summary = {
        "phase": "nsi_interface",
        "milestone": "v5.2",
        "python": sys.version,
        "platform": platform.platform(),
        "schema_status": spec["schema_status"],
        "schema_count": len(spec["schemas"]),
        "reference_objects_valid": reference_objects_valid,
        "dataset_importer_conformance": {"passed": dataset_passed, "total": len(dataset_reports)},
        "vendor_adapter_conformance": {"passed": vendor_passed, "total": len(vendor_reports)},
        "result_bundle_valid": bool(result_bundle_report["valid"]),
        "claim_annotation": claim_annotation,
        "gate": {
            "nsi_schemas_frozen": spec["schema_status"] == "frozen_interface_profile",
            "adapter_conformance_passed": dataset_passed == len(dataset_reports) and vendor_passed == len(vendor_reports),
            "result_bundle_validator_passed": bool(result_bundle_report["valid"]),
            "claim_annotation_available": bool(claim_annotation["claim_level"]),
        },
    }

    _write_json(out / "NSI_1_0_FROZEN_SCHEMA.json", spec)
    _write_json(out / "NSI_1_0_REFERENCE_OBJECTS.json", reference_objects)
    _write_json(out / "NSI_1_0_REFERENCE_VALIDATION.json", reference_validations)
    _write_json(out / "NSI_1_0_DATASET_IMPORTER_CONFORMANCE.json", dataset_reports)
    _write_json(out / "NSI_1_0_VENDOR_ADAPTER_CONFORMANCE.json", vendor_reports)
    _write_json(out / "NSI_1_0_RESULT_BUNDLE_VALIDATION.json", result_bundle_report)
    _write_json(out / "V52_NSI_INTERFACE_SUMMARY.json", summary)
    (out / "BIOGPU_V52_NSI_INTERFACE_REPORT.md").write_text(_render_report(summary), encoding="utf-8")

    print(f"v52_nsi_interface schema_count={summary['schema_count']}")
    print(f"dataset_importer_conformance={dataset_passed}/{len(dataset_reports)}")
    print(f"vendor_adapter_conformance={vendor_passed}/{len(vendor_reports)}")
    print(f"result_bundle_valid={summary['result_bundle_valid']}")
    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.2 NSI/interface phase runner")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(args.out_dir)


if __name__ == "__main__":
    main()