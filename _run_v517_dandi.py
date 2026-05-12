"""Run v5.17 gate with new DANDI platform."""
from biogpu.sdk.external_readonly_v517 import build_external_readonly_api_gate_v517, validate_mock_readonly_platform_v517
from biogpu.apis.registry_v37 import list_external_api_platforms_v37
import json

print("Platforms:", list_external_api_platforms_v37())
print()

gate = build_external_readonly_api_gate_v517()
print(f"Overall status: {gate['overall_status']}")
print(f"Platform count: {gate['platform_count']}")
print(f"Mock passed: {gate['mock_contract_passed_count']}/{gate['platform_count']}")
print(f"Configured tokens: {gate['configured_token_envs']}")
print(f"Real export files: {gate['real_export_file_count']}")
print(f"Real external ready: {gate['real_external_ready']}")
print()

for report in gate["platform_reports"]:
    is_dandi = report["platform"] == "dandi_archive"
    tag = " [LIVE HTTP]" if is_dandi else ""
    print(f"--- {report['platform']}{tag} ---")
    print(f"  adapter: {report['adapter_name']}")
    print(f"  contract: {report['contract_status']}")
    print(f"  channels: {report['channel_count']}")
    print(f"  sample_rate: {report['sample_rate_hz']}")
    print(f"  spike_events: {report['spike_event_count']}")
    print(f"  trace_samples: {report['trace_sample_count']}")
    print(f"  write_denied: {report['write_denial_passed']}")
    if is_dandi:
        print(f"  NOTE: real HTTP data from api.dandiarchive.org")
    if report.get("errors"):
        print(f"  ERRORS: {'; '.join(report['errors'])}")
    print()
