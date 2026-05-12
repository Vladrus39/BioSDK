"""BioGPU-Core v5.4 LLM/Agent Bridge runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.llm.agent_bridge_v54 import (
    build_agent_response_v54,
    catalog_as_dict_v54,
    reference_agent_requests_v54,
)


DEFAULT_OUT = Path("outputs/v54_llm_agent_bridge")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_report(summary: dict[str, Any]) -> str:
    return "\n".join([
        "# BioGPU-Core v5.4 LLM/Agent Bridge Report",
        "",
        "## Summary",
        "",
        f"- Tool count: {summary['tool_count']}",
        f"- Approved reference requests: {summary['approved_count']}",
        f"- Blocked/approval-gated requests: {summary['not_approved_count']}",
        f"- Safe replay status: {summary['reference_statuses']['safe_replay']}",
        f"- Live-shadow status: {summary['reference_statuses']['live_shadow_with_approval']}",
        f"- Actuation attempt status: {summary['reference_statuses']['blocked_actuation']}",
        "",
        "## Boundary",
        "",
        "v5.4 allows LLM/agents to propose and validate BioCompute tasks. It does not let an LLM directly approve or execute live biological actuation.",
        "",
    ])


def run(out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    catalog = catalog_as_dict_v54()
    requests = reference_agent_requests_v54()
    responses = {name: build_agent_response_v54(req).to_dict() for name, req in requests.items()}
    statuses = {name: response["status"] for name, response in responses.items()}
    approved_count = sum(1 for response in responses.values() if response["policy_review"]["approved"])
    summary = {
        "phase": "llm_agent_bridge",
        "milestone": "v5.4",
        "tool_count": len(catalog),
        "reference_request_count": len(requests),
        "approved_count": approved_count,
        "not_approved_count": len(responses) - approved_count,
        "reference_statuses": statuses,
        "gate": {
            "safe_replay_agent_request_approved": responses["safe_replay"]["policy_review"]["approved"],
            "live_shadow_requires_or_has_approval": responses["live_shadow_with_approval"]["policy_review"]["requires_human_approval"],
            "direct_actuation_blocked": responses["blocked_actuation"]["status"] == "blocked",
            "nsi_manifest_emitted_for_safe_requests": all(
                response["nsi_task_manifest"] is not None
                for response in responses.values()
                if response["policy_review"]["approved"]
            ),
        },
    }
    _write_json(out / "V54_AGENT_TOOL_CATALOG.json", catalog)
    _write_json(out / "V54_REFERENCE_AGENT_REQUESTS.json", {name: req.to_dict() for name, req in requests.items()})
    _write_json(out / "V54_AGENT_RESPONSES.json", responses)
    _write_json(out / "V54_LLM_AGENT_BRIDGE_SUMMARY.json", summary)
    (out / "BIOGPU_V54_LLM_AGENT_BRIDGE_REPORT.md").write_text(_render_report(summary), encoding="utf-8")
    print(f"v54_llm_agent_bridge tool_count={summary['tool_count']}")
    print(f"approved_count={summary['approved_count']}")
    print(f"direct_actuation_blocked={summary['gate']['direct_actuation_blocked']}")
    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.4 LLM/Agent Bridge runner")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(args.out_dir)


if __name__ == "__main__":
    main()
