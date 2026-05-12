"""BioSDK external read-only API/export gate, v5.17."""
from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.apis.base_external_api_v37 import PermissionDeniedV37
from biogpu.apis.registry_v37 import list_external_api_platforms_v37, make_external_api_client_v37
from biogpu.sdk.external_export_validation_v524 import build_external_export_validation_gate_v524


DEFAULT_OUT = Path("outputs/v517_external_readonly_api_gate")
TOKEN_ENV_BY_PLATFORM = {
    "finalspark_remote_wetware": "FINALSPARK_TOKEN",
    "threebrain_hdmea": "THREEBRAIN_TOKEN",
    "axion_maestro": "AXION_TOKEN",
    "mcs_mea2100": "MCS_TOKEN",
    "dandi_archive": None,  # fully open — no token required
}


@dataclass(frozen=True)
class ExternalReadOnlyPlatformReportV517:
    platform: str
    adapter_name: str
    contract_status: str
    access_mode: str
    channel_count: int
    sample_rate_hz: float
    spike_event_count: int
    trace_sample_count: int
    supports_live_stimulation: bool
    live_output_performed: bool
    write_denial_passed: bool
    blocked_scope: tuple[str, ...]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _export_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in ("data/external/api_exports/**/*", "data/external/finalspark/**/*"):
        paths.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(paths))


def validate_mock_readonly_platform_v517(platform: str, duration_s: float = 0.25) -> dict[str, Any]:
    errors: list[str] = []
    client = make_external_api_client_v37(platform, access_mode="read_only")
    metadata = client.connect().to_dict()
    trace = client.export_biogpu_trace(duration_s=duration_s).to_dict()
    write_denial_passed = False
    write_denial_error = ""
    try:
        client.send_stimulation_pattern({"operation": "blocked_write_contract_probe"})
    except PermissionDeniedV37 as exc:
        write_denial_passed = True
        write_denial_error = str(exc)
    except Exception as exc:  # pragma: no cover - defensive contract report
        write_denial_error = str(exc)
        errors.append(f"unexpected_write_denial_exception:{type(exc).__name__}:{exc}")
    finally:
        client.close()
    safety = trace.get("safety", {})
    if metadata.get("supports_live_stimulation") is not False:
        errors.append("metadata_does_not_block_live_stimulation")
    if safety.get("live_output_performed") is not False:
        errors.append("trace_reports_live_output_performed")
    if safety.get("live_stimulation_enabled") is not False:
        errors.append("trace_reports_live_stimulation_enabled")
    if not write_denial_passed:
        errors.append("write_denial_failed")
    if int(len(trace.get("spike_events") or [])) <= 0:
        errors.append("no_spike_events_exported")
    if int(len(trace.get("trace_samples") or [])) <= 0:
        errors.append("no_trace_samples_exported")
    contract_status = "mock_readonly_contract_passed" if not errors else "mock_readonly_contract_failed"
    report = ExternalReadOnlyPlatformReportV517(
        platform=platform,
        adapter_name=str(metadata.get("adapter_name", "")),
        contract_status=contract_status,
        access_mode=str(metadata.get("access_mode", "")),
        channel_count=int(metadata.get("channel_count") or 0),
        sample_rate_hz=float(metadata.get("sample_rate_hz") or 0.0),
        spike_event_count=int(len(trace.get("spike_events") or [])),
        trace_sample_count=int(len(trace.get("trace_samples") or [])),
        supports_live_stimulation=bool(metadata.get("supports_live_stimulation")),
        live_output_performed=bool(safety.get("live_output_performed")),
        write_denial_passed=write_denial_passed,
        blocked_scope=tuple(str(item) for item in safety.get("blocked_scope", [])),
        errors=tuple(errors),
    )
    return {
        "report": report.to_dict(),
        "metadata": metadata,
        "trace_fixture": trace,
        "write_denial_error": write_denial_error,
    }


def build_external_readonly_api_gate_v517(root: str | Path = ".") -> dict[str, Any]:
    project_root = Path(root).resolve()
    platform_results = [validate_mock_readonly_platform_v517(platform) for platform in list_external_api_platforms_v37()]
    platform_reports = [item["report"] for item in platform_results]
    all_mock_contracts_passed = all(item["contract_status"] == "mock_readonly_contract_passed" for item in platform_reports)
    configured_tokens = [env_name for env_name in TOKEN_ENV_BY_PLATFORM.values() if env_name and os.environ.get(env_name)]
    export_paths = _export_paths(project_root)
    export_validation = build_external_export_validation_gate_v524(project_root)
    real_external_ready = bool(export_validation.get("real_external_ready"))
    real_external_material_present = bool(configured_tokens or export_paths)
    if all_mock_contracts_passed and real_external_ready:
        overall_status = "real_external_readonly_export_validated"
    elif all_mock_contracts_passed and real_external_material_present:
        overall_status = "mock_readonly_contract_passed_real_material_needs_validation"
    elif all_mock_contracts_passed:
        overall_status = "mock_readonly_contract_passed_real_external_required"
    else:
        overall_status = "external_readonly_contract_failed"
    return {
        "version": "v5.17",
        "phase": "external_readonly_api_export_gate",
        "overall_status": overall_status,
        "active_phase": "biosdk_public_core",
        "bic_os_phase_locked": True,
        "platform_count": len(platform_reports),
        "mock_contract_passed_count": sum(1 for item in platform_reports if item["contract_status"] == "mock_readonly_contract_passed"),
        "all_mock_contracts_passed": all_mock_contracts_passed,
        "configured_token_envs": configured_tokens,
        "real_export_file_count": len(export_paths),
        "real_export_paths_sample": [str(path.relative_to(project_root)).replace("\\", "/") for path in export_paths[:20]],
        "real_external_ready": real_external_ready,
        "real_export_validation_status": export_validation.get("overall_status"),
        "validated_real_export_count": int(export_validation.get("validated_export_count", 0)),
        "validated_real_export_paths": export_validation.get("validated_export_paths", []),
        "platform_reports": platform_reports,
        "required_real_external_next_steps": [] if real_external_ready else [
            "obtain one partner/vendor read-only token or export",
            "run metadata and read-only trace import without actuation",
            "store only non-secret validation artifacts",
            "keep live stimulation and closed-loop writes blocked",
        ],
        "claim_boundary": "v5.17 proves local read-only adapter contracts and write-denial behavior on mock clients. Real external proof is counted only when v5.24 validates a non-secret read-only export; this still does not prove live API access, stimulation or BiC OS readiness.",
    }


def write_external_readonly_outputs_v517(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    platform_results = [validate_mock_readonly_platform_v517(platform) for platform in list_external_api_platforms_v37()]
    gate = build_external_readonly_api_gate_v517(root)
    paths = {
        "summary_json": out / "V517_EXTERNAL_READONLY_API_SUMMARY.json",
        "platform_reports_json": out / "V517_EXTERNAL_READONLY_PLATFORM_REPORTS.json",
        "platform_reports_csv": out / "V517_EXTERNAL_READONLY_PLATFORM_REPORTS.csv",
        "trace_fixtures_json": out / "V517_EXTERNAL_READONLY_TRACE_FIXTURES.json",
        "markdown_report": out / "BIOGPU_V517_EXTERNAL_READONLY_API_REPORT.md",
    }
    paths["summary_json"].write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["platform_reports_json"].write_text(json.dumps({"platform_reports": gate["platform_reports"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["trace_fixtures_json"].write_text(json.dumps({"fixtures": platform_results}, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_platform_csv(paths["platform_reports_csv"], gate["platform_reports"])
    paths["markdown_report"].write_text(_markdown_report(gate), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_platform_csv(path: Path, reports: list[dict[str, Any]]) -> None:
    fields = [
        "platform",
        "adapter_name",
        "contract_status",
        "access_mode",
        "channel_count",
        "sample_rate_hz",
        "spike_event_count",
        "trace_sample_count",
        "write_denial_passed",
        "errors",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for report in reports:
            writer.writerow(
                {
                    "platform": report["platform"],
                    "adapter_name": report["adapter_name"],
                    "contract_status": report["contract_status"],
                    "access_mode": report["access_mode"],
                    "channel_count": report["channel_count"],
                    "sample_rate_hz": report["sample_rate_hz"],
                    "spike_event_count": report["spike_event_count"],
                    "trace_sample_count": report["trace_sample_count"],
                    "write_denial_passed": report["write_denial_passed"],
                    "errors": ";".join(report["errors"]),
                }
            )


def _markdown_report(gate: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.17 External Read-Only API Gate",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- Mock contracts passed: `{gate['mock_contract_passed_count']}/{gate['platform_count']}`",
        f"- Real external ready: `{gate['real_external_ready']}`",
        f"- Real export files: `{gate['real_export_file_count']}`",
        f"- BiC OS locked: `{gate['bic_os_phase_locked']}`",
        "",
        "## Platform Reports",
        "",
    ]
    for report in gate["platform_reports"]:
        lines.append(
            f"- `{report['platform']}`: `{report['contract_status']}`, spikes `{report['spike_event_count']}`, trace samples `{report['trace_sample_count']}`, write denied `{report['write_denial_passed']}`"
        )
    lines.extend(["", "## Required Real External Next Steps", ""])
    for step in gate["required_real_external_next_steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)
