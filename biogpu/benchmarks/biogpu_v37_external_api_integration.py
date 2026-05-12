from __future__ import annotations
import csv, json, zipfile
from pathlib import Path
from typing import Any

from biogpu.apis.registry_v37 import list_external_api_platforms_v37, make_external_api_client_v37
from biogpu.apis.base_external_api_v37 import commercial_tiers_v37, PermissionDeniedV37

OUT_DIR = Path("outputs/realdata_zenodo_14363732_v37_external_api")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_report_v37(out_dir: Path = OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    platforms = list_external_api_platforms_v37()
    metadata_rows = []
    trace_summaries = []
    denied_write_checks = []

    for platform in platforms:
        client = make_external_api_client_v37(platform, access_mode="read_only")
        metadata = client.connect().to_dict()
        trace = client.export_biogpu_trace(duration_s=0.5).to_dict()
        write_json(out_dir / f"trace_{platform}_v37.json", trace)
        metadata_rows.append(metadata)
        trace_summaries.append({
            "platform": platform,
            "adapter_name": metadata["adapter_name"],
            "channel_count": metadata["channel_count"],
            "sample_rate_hz": metadata["sample_rate_hz"],
            "spike_event_count": len(trace["spike_events"]),
            "trace_sample_count": len(trace["trace_samples"]),
            "live_output_performed": trace["safety"]["live_output_performed"],
            "supports_live_stimulation": metadata["supports_live_stimulation"],
        })
        try:
            client.send_stimulation_pattern({"abstract_pattern_id": "demo_only"})
            denied = False
            error = "NO_ERROR"
        except PermissionDeniedV37 as exc:
            denied = True
            error = str(exc)
        denied_write_checks.append({"platform": platform, "write_denied": denied, "error": error[:160]})
        client.close()

    tiers = [t.to_dict() for t in commercial_tiers_v37()]
    write_csv(out_dir / "v37_external_api_metadata.csv", metadata_rows)
    write_csv(out_dir / "v37_external_api_trace_summary.csv", trace_summaries)
    write_csv(out_dir / "v37_write_denial_checks.csv", denied_write_checks)
    write_csv(out_dir / "v37_commercial_tiers.csv", tiers)

    summary = {
        "version": "v3.7",
        "title": "External API / BioSDK Integration Skeleton",
        "platform_count": len(platforms),
        "platforms": platforms,
        "access_scope": "metadata/read-only/replay/live-shadow skeleton only",
        "live_output_performed": False,
        "write_denial_passed": all(r["write_denied"] for r in denied_write_checks),
        "commercial_positioning": "evaluation/read-only SDK first; paid controlled/live modules later",
        "next_step": "v3.8 BioLLM Tool Interface or live-data shadow runner",
    }
    write_json(out_dir / "v37_external_api_summary.json", summary)

    md = [
        "# BioGPU-Core v3.7 — External API / BioSDK Integration Skeleton",
        "",
        "v3.7 converts BioGPU-Core from a replay-only package into an API-ready BioSDK skeleton.",
        "",
        "## What this allows",
        "",
        "- Enterprises/labs can validate integration using metadata, mock clients, exported spikes/traces and BioGPUTrace bundles.",
        "- The SDK can read or import data, run readout/benchmark layers and produce auditable result bundles.",
        "- It does not perform live stimulation, electrode control, environment control or wet-lab operations.",
        "",
        "## Commercial interpretation",
        "",
        "This is not the final restricted product. It is the enterprise onboarding tier: safe evaluation first, paid read-only SDK second, live shadow third, and lab-approved closed-loop modules only after validation.",
        "",
        "## Platforms represented",
        "",
    ]
    for row in trace_summaries:
        md.append(f"- {row['platform']}: {row['channel_count']} channels, {row['sample_rate_hz']} Hz, live stimulation supported by v3.7 = {row['supports_live_stimulation']}")
    md += [
        "",
        "## Commercial tiers",
        "",
    ]
    for t in tiers:
        md.append(f"### {t['tier']}")
        md.append(f"- Intended user: {t['intended_user']}")
        md.append(f"- Commercial note: {t['commercial_note']}")
        md.append("")
    (out_dir / "BIOGPU_V37_EXTERNAL_API_BIOSDK_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    bundle = out_dir / "biogpu_v37_external_api_biosdk_bundle.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(out_dir.glob("*")):
            if path.name != bundle.name and path.is_file():
                zf.write(path, path.name)
    summary["bundle"] = str(bundle)
    write_json(out_dir / "v37_external_api_summary.json", summary)
    return summary


def main() -> None:
    summary = generate_report_v37()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
