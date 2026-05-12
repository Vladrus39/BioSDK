from __future__ import annotations

import csv
import json
from pathlib import Path

from biogpu.llm.tool_interface_v38 import (
    BioLLMModeV38,
    BioLLMTaskV38,
    BioLLMToolInterfaceV38,
    default_biollm_commercial_tiers_v38,
    run_biollm_tool_demo_v38,
)
from biogpu.apis.registry_v37 import list_external_api_platforms_v37


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def run_v38(output_dir: str = "outputs/realdata_zenodo_14363732_v38_biollm_tool_interface") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    interface = BioLLMToolInterfaceV38()

    demo_task = BioLLMTaskV38(
        task_id="v38_demo_task",
        user_goal="LLM asks BioGPU-Core to inspect read-only biological/replay activity and return a structured signal result.",
        mode=BioLLMModeV38.API_READ_ONLY.value,
        platform="mcs_mea2100",
        decoder_id="centroid_v27",
        duration_s=1.0,
        input_payload={"llm_agent": "demo", "requested_output": "structured_signal_result"},
    )
    manifest = interface.build_manifest(demo_task)
    result = interface.run(demo_task)

    write_json(out / "v38_biollm_manifest.json", manifest.to_dict())
    write_json(out / "v38_biollm_tool_result.json", result.to_dict())
    write_json(out / "v38_biollm_demo_direct.json", run_biollm_tool_demo_v38())

    tiers = [t.to_dict() for t in default_biollm_commercial_tiers_v38()]
    write_json(out / "v38_commercial_tiers.json", tiers)
    with (out / "v38_commercial_tiers.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tier", "allowed_modes", "customer_value", "restrictions", "monetization"])
        writer.writeheader()
        for t in tiers:
            writer.writerow({
                "tier": t["tier"],
                "allowed_modes": ";".join(t["allowed_modes"]),
                "customer_value": t["customer_value"],
                "restrictions": ";".join(t["restrictions"]),
                "monetization": t["monetization"],
            })

    report = f"""# BioGPU-Core v3.8 — BioLLM Tool Interface

## Purpose

v3.8 exposes BioGPU-Core as an LLM-callable tool / enterprise BioSDK interface.
An LLM or agent can pass a structured task to BioGPU, receive a validated manifest,
read a replay/API/mock trace, run a readout, and obtain a structured result with
safety and claim boundaries.

## Demo result

- Status: `{result.status}`
- Tool: `{result.llm_tool_name}`
- Mode: `{manifest.mode}`
- Platform: `{manifest.selected_platform}`
- Decoder: `{manifest.selected_decoder}`
- Signal: `{result.structured_result.get('biogpu_signal')}`
- Confidence: `{result.structured_result.get('confidence')}`
- Claim level: `{result.claim_level}`
- Live output performed: `{result.safety.get('live_output_performed')}`

## Commercial meaning

v3.8 is not a toy-only interface. It is the first enterprise-facing SDK layer:

1. Developer Evaluation: replay/mock/metadata demos.
2. Enterprise Read-Only BioSDK: paid connectors, audit logs, BioGPUTrace export.
3. Enterprise Live Shadow BioSDK: live read stream without actuation.
4. Lab-Approved Closed-Loop Add-on: future separate premium module after vendor/lab SOP approval.

## Safety boundary

v3.8 does not perform live stimulation or wet-lab control. It blocks writes and
carries claim_level with every result.
"""
    write_text(out / "BIOGPU_V38_BIOLLM_TOOL_INTERFACE_REPORT.md", report)

    summary = {
        "version": "v3.8",
        "component": "BioLLM Tool Interface",
        "status": "ok",
        "platforms_available": list_external_api_platforms_v37(),
        "demo_signal": result.structured_result.get("biogpu_signal"),
        "demo_confidence": result.structured_result.get("confidence"),
        "live_output_performed": result.safety.get("live_output_performed"),
        "commercial_tiers": [t["tier"] for t in tiers],
        "outputs": sorted(p.name for p in out.iterdir()),
    }
    write_json(out / "v38_summary.json", summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(run_v38(), indent=2, ensure_ascii=False))
