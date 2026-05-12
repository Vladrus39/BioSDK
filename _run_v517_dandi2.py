"""Run v5.17 gate post-DANDI fix — v2."""
from biogpu.sdk.external_readonly_v517 import build_external_readonly_api_gate_v517
from biogpu.apis.registry_v37 import list_external_api_platforms_v37
import json

print("Platforms:", list_external_api_platforms_v37())
print()

gate = build_external_readonly_api_gate_v517()
print(f"Overall: {gate['overall_status']} | Platforms: {gate['platform_count']} | Passed: {gate['mock_contract_passed_count']}/{gate['platform_count']}")
print(f"Tokens: {gate['configured_token_envs']} | Export files: {gate['real_export_file_count']} | Real ready: {gate['real_external_ready']}")
print()

for report in gate["platform_reports"]:
    is_dandi = report["platform"] == "dandi_archive"
    tag = " [LIVE DANDI HTTP]" if is_dandi else " [mock]"
    print(f"{report['platform']}{tag}: {report['contract_status']} | spikes={report['spike_event_count']} trace={report['trace_sample_count']} write_denied={report['write_denial_passed']}")
    if is_dandi:
        print(f"  adapter={report['adapter_name']} channels={report['channel_count']} sr={report['sample_rate_hz']}")
    if report.get("errors"):
        print(f"  ERRORS: {'; '.join(report['errors'])}")
