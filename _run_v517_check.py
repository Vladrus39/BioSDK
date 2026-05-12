"""Check v5.17 external readonly API gate status."""
from biogpu.sdk.external_readonly_v517 import build_external_readonly_api_gate_v517
import json

gate = build_external_readonly_api_gate_v517()
summary = {
    "version": gate["version"],
    "overall_status": gate["overall_status"],
    "platform_count": gate["platform_count"],
    "mock_contract_passed_count": gate["mock_contract_passed_count"],
    "all_mock_contracts_passed": gate["all_mock_contracts_passed"],
    "configured_token_envs": gate["configured_token_envs"],
    "real_export_file_count": gate["real_export_file_count"],
    "real_external_ready": gate["real_external_ready"],
    "real_export_validation_status": gate["real_export_validation_status"],
    "validated_real_export_count": gate["validated_real_export_count"],
}
print(json.dumps(summary, indent=2, ensure_ascii=False))

print("\n--- Platform Reports ---")
for report in gate["platform_reports"]:
    print(f"  {report['platform']}: {report['contract_status']} | spikes={report['spike_event_count']} | trace={report['trace_sample_count']} | write_denied={report['write_denial_passed']}")
    if report.get("errors"):
        print(f"    ERRORS: {'; '.join(report['errors'])}")

print(f"\nRequired next steps:")
for step in gate["required_real_external_next_steps"]:
    print(f"  - {step}")
