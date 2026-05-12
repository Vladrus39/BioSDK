"""BioGPU-Core v5.24 external export validation runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.external_export_validation_v524 import DEFAULT_OUT, run_external_export_validation_workflow_v524, write_external_export_validation_outputs_v524


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = run_external_export_validation_workflow_v524(root)
    paths = write_external_export_validation_outputs_v524(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v524_external_export_validation status={summary['overall_status']}")
    print(f"candidate_exports={summary['candidate_export_count']}")
    print(f"validated_exports={summary['validated_export_count']}")
    print(f"real_external_ready={summary['real_external_ready']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.24 external export validation")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()