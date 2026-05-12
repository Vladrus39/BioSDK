"""BioGPU-Core v5.14 sample acquisition gate runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.sample_acquisition_v514 import DEFAULT_OUT, build_sample_acquisition_gate_v514, write_sample_acquisition_outputs_v514


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    gate = build_sample_acquisition_gate_v514(root)
    paths = write_sample_acquisition_outputs_v514(gate, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v514_sample_acquisition status={summary['overall_status']}")
    print(f"active_phase={summary['active_phase']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    print(f"local_sources={summary['locally_available_independent_source_count']}/{summary['independent_source_target']}")
    print(f"dandi_nwb_validated={summary['dandi_nwb_validated']}")
    print(f"full_sample_proof_ready={summary['full_sample_proof_ready']}")
    return {"summary": summary, "gate": gate, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.14 sample acquisition gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
