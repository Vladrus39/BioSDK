"""BioGPU-Core v5.11 BiC OS boot readiness runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.os.boot_readiness_v511 import DEFAULT_OUT, build_bic_os_boot_readiness_v511, write_bic_os_boot_outputs_v511


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_bic_os_boot_readiness_v511(root)
    paths = write_bic_os_boot_outputs_v511(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v511_bic_os_boot_readiness status={summary['overall_status']}")
    print(f"product_name={summary['product_name']}")
    print(f"offline_runtime_kernel_bootable={summary['offline_runtime_kernel_bootable']}")
    print(f"production_os_ready={summary['production_os_ready']}")
    print(f"production_blocker_count={summary['production_blocker_count']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.11 BiC OS boot readiness")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
