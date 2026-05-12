"""Check v5.24 export validation status."""
from biogpu.sdk.external_export_validation_v524 import build_external_export_validation_gate_v524
import json

audit = build_external_export_validation_gate_v524()
summary = {
    "overall_status": audit["overall_status"],
    "candidate_count": audit["candidate_export_count"],
    "validated_count": audit["validated_export_count"],
    "blocked_count": audit["blocked_export_count"],
    "real_external_ready": audit["real_external_ready"],
    "validated_paths": audit["validated_export_paths"],
    "blocked_paths": audit["blocked_export_paths"],
    "platforms": audit.get("platforms_validated", []),
}
print(json.dumps(summary, indent=2, ensure_ascii=False))

# Also show individual reports
for report in audit["reports"]:
    print(f"\n--- {report['relative_path']} ---")
    print(f"  gate_status: {report['gate_status']}")
    print(f"  file_format: {report['file_format']}")
    print(f"  sha256: {report['sha256'][:16]}...")
    print(f"  safety_scan: {report['safety_scan_passed']}")
    print(f"  readonly_evidence: {report['readonly_data_evidence']}")
    print(f"  recognized_format: {report['recognized_readonly_format']}")
    print(f"  trace_datasets: {report['trace_dataset_count']}")
    print(f"  event_datasets: {report['event_dataset_count']}")
    if report["forbidden_hits"]:
        print(f"  FORBIDDEN: {report['forbidden_hits']}")
    if report["errors"]:
        print(f"  ERRORS: {report['errors']}")
    if report["source_reference"]:
        print(f"  source: {report['source_reference'].get('source_name', 'unknown')}")
