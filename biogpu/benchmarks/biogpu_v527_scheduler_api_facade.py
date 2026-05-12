"""BioGPU-Core v5.27 scheduler API facade runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.runtime.scheduler_api_v527 import DEFAULT_OUT, run_scheduler_api_facade_workflow_v527, write_scheduler_api_facade_outputs_v527


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_scheduler_api_facade_workflow_v527(root=root, out_dir=out_dir)
    output_path = Path(root).resolve() / out_dir if not Path(out_dir).is_absolute() else Path(out_dir)
    paths = write_scheduler_api_facade_outputs_v527(audit, output_path)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v527_scheduler_api_facade status={summary['overall_status']}")
    print(f"scheduler_api_facade_ready={summary['scheduler_api_facade_ready']}")
    print(f"api_routes={summary['api_route_count']}")
    print(f"cancel_semantics={summary['cancel_semantics_passed']}")
    print(f"timeout_semantics={summary['timeout_semantics_passed']}")
    print(f"retry_semantics={summary['retry_semantics_passed']}")
    print(f"production_api_ready={summary['production_api_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.27 scheduler API facade")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()