"""BioGPU-Core v5.17 external read-only API/export gate runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.sdk.external_readonly_v517 import DEFAULT_OUT, write_external_readonly_outputs_v517


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    paths = write_external_readonly_outputs_v517(root=root, out_dir=out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v517_external_readonly_api status={summary['overall_status']}")
    print(f"mock_contracts={summary['mock_contract_passed_count']}/{summary['platform_count']}")
    print(f"real_external_ready={summary['real_external_ready']}")
    print(f"real_export_file_count={summary['real_export_file_count']}")
    print(f"bic_os_phase_locked={summary['bic_os_phase_locked']}")
    return {"summary": summary, "outputs": paths}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.17 external read-only API/export gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
