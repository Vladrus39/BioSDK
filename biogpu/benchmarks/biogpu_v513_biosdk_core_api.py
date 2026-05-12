"""BioGPU-Core v5.13 BioSDK core API runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.core_v513 import DEFAULT_OUT, run_biosdk_reference_flow_v513, write_biosdk_core_outputs_v513


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    flow = run_biosdk_reference_flow_v513(root)
    paths = write_biosdk_core_outputs_v513(flow, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v513_biosdk_core_api status={summary['overall_status']}")
    print(f"active_phase={summary['active_phase']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    print(f"nsi_manifest_valid={summary['nsi_manifest_valid']}")
    print(f"queue_admission_accepted={summary['queue_admission_accepted']}")
    return {"summary": summary, "flow": flow, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.13 BioSDK core API")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
