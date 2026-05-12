from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from biogpu.substrates.vendors import (
    AxionMaestroAdapter,
    BioGPUVendorCommand,
    FinalSparkRemoteWetwareAdapter,
    MCSMEA2100Adapter,
    ThreeBrainHDMEAAdapter,
)


def build_v25_vendor_adapters(mode: str = "dry_run") -> list[Any]:
    return [
        MCSMEA2100Adapter(mode=mode),
        AxionMaestroAdapter(mode=mode),
        ThreeBrainHDMEAAdapter(mode=mode),
        FinalSparkRemoteWetwareAdapter(mode=mode),
    ]


def build_safe_probe_command() -> BioGPUVendorCommand:
    return BioGPUVendorCommand(
        command_id="v25_safe_probe_abstract",
        benchmark_id="B0_target_vs_random_electrode",
        pattern_id="abstract_target_group_probe",
        electrode_group_aliases=["target_group_A", "context_group_B"],
        timing_class="abstract_task_window",
        payload={
            "encoding_family": "spatial_alias_only",
            "readout_expected": "post_window_spike_features",
            "live_values": "not_included",
        },
    )


def build_v25_capability_matrix() -> list[dict[str, Any]]:
    rows = []
    for adapter in build_v25_vendor_adapters():
        cap = adapter.capability
        rows.append(cap.to_dict())
    return rows


def run_v25_dry_run(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    adapters = build_v25_vendor_adapters(mode="dry_run")
    command = build_safe_probe_command()

    dry_runs: list[dict[str, Any]] = []
    for adapter in adapters:
        connect_result = adapter.connect()
        validation_errors = adapter.validate_session({"run_mode": "dry_run"})
        ack = adapter.send_stimulation_pattern(command)
        spikes = adapter.read_spike_stream(duration_s=0.0)
        raw = adapter.read_raw_trace(duration_s=0.0)
        metadata = adapter.export_metadata()
        adapter.close()
        dry_runs.append(
            {
                "adapter_id": adapter.adapter_id,
                "connect_result": connect_result,
                "validation_errors": validation_errors,
                "command_ack": ack,
                "spike_stream": spikes,
                "raw_trace": raw,
                "metadata": metadata,
            }
        )

    capabilities = build_v25_capability_matrix()
    summary = {
        "version": "v2.5",
        "scope": "vendor adapter stubs and safe dry-run contract",
        "adapter_count": len(adapters),
        "adapters": [a.adapter_id for a in adapters],
        "live_output_performed": False,
        "safe_probe_command": command.to_dict(),
        "dry_run_status": "ok",
        "boundary": [
            "no live vendor backend implemented",
            "no vendor pinout included",
            "no live stimulation settings included",
            "no wet-lab protocol included",
        ],
    }

    (out / "v25_vendor_capability_matrix.json").write_text(json.dumps(capabilities, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "v25_vendor_dry_run_results.json").write_text(json.dumps(dry_runs, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "v25_safe_probe_command.json").write_text(json.dumps(command.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "v25_vendor_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    with (out / "v25_vendor_capability_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        fieldnames = [
            "vendor_id",
            "display_name",
            "platform_class",
            "role_in_biogpu_a1",
            "recording_supported",
            "stimulation_supported",
            "raw_trace_supported",
            "spike_stream_supported",
            "ttl_sync_supported",
            "environmental_sensors",
            "api_access_class",
            "channel_count_class",
            "live_backend_status",
            "boundary_notice",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in capabilities:
            row = dict(row)
            row["environmental_sensors"] = ";".join(row.get("environmental_sensors", []))
            writer.writerow(row)

    (out / "BIOGPU_V25_VENDOR_ADAPTERS_REPORT.md").write_text(render_v25_vendor_report(summary, capabilities), encoding="utf-8")
    return summary


def render_v25_vendor_report(summary: dict[str, Any], capabilities: list[dict[str, Any]]) -> str:
    lines = [
        "# BioGPU v2.5 — Vendor Adapter Stubs",
        "",
        "## Scope",
        "",
        "v2.5 adds a hardware-neutral adapter contract for future MEA/HD-MEA backends.",
        "The implementation is dry-run only: no live vendor command, live stimulation setting, pinout, or wet-lab recipe is included.",
        "",
        "## Adapters",
        "",
    ]
    for cap in capabilities:
        lines.extend([
            f"### {cap['display_name']}",
            "",
            f"- Vendor ID: `{cap['vendor_id']}`",
            f"- Platform class: {cap['platform_class']}",
            f"- Role: {cap['role_in_biogpu_a1']}",
            f"- Channel class: {cap['channel_count_class']}",
            f"- Recording: `{cap['recording_supported']}`",
            f"- Stimulation: `{cap['stimulation_supported']}`",
            f"- Raw trace: `{cap['raw_trace_supported']}`",
            f"- Spike stream: `{cap['spike_stream_supported']}`",
            f"- TTL sync: `{cap['ttl_sync_supported']}`",
            f"- API access: {cap['api_access_class']}",
            f"- Live backend status: `{cap['live_backend_status']}`",
            f"- Boundary: {cap['boundary_notice']}",
            "",
        ])
    lines.extend([
        "## Adapter API contract",
        "",
        "Each adapter exposes the same future-facing calls:",
        "",
        "```text",
        "connect()",
        "validate_session(manifest)",
        "send_stimulation_pattern(command)",
        "read_spike_stream(duration_s)",
        "read_raw_trace(duration_s)",
        "export_metadata()",
        "close()",
        "```",
        "",
        "## Safety boundary",
        "",
    ])
    lines.extend(f"- {item}" for item in summary["boundary"])
    lines.extend([
        "",
        "Real live-lab usage must be implemented as a separate vendor backend after selecting the platform, reading vendor SDK/manuals, validating hardware safety gates, and operating under approved lab SOPs.",
    ])
    return "\n".join(lines) + "\n"
