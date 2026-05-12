"""Run full v5.24 external export validation workflow."""
from biogpu.sdk.external_export_validation_v524 import run_external_export_validation_workflow_v524
import json

result = run_external_export_validation_workflow_v524()
summary = {
    "overall_status": result["overall_status"],
    "candidate_export_count": result["candidate_export_count"],
    "validated_export_count": result["validated_export_count"],
    "real_external_ready": result["real_external_ready"],
    "validated_paths": result["validated_export_paths"],
    "platforms_validated": result.get("platforms_validated", []),
}
print("=== V5.24 GATE ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))
print(f"\n=== DOWNSTREAM STATUS ===")
for key, value in result.get("downstream_status", {}).items():
    print(f"  {key}: {value}")
print(f"\n=== DIRECT ANSWER ===")
for key, value in result.get("direct_answer", {}).items():
    print(f"  {key}: {value}")
print(f"\nFiles written to outputs/v524_external_export_validation/")
