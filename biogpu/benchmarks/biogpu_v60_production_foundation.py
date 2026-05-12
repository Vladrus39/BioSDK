"""BioGPU-Core v6.0 Production Foundation benchmark runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.production.foundation_v60 import (
    DEFAULT_OUT,
    build_production_foundation,
    write_production_foundation_outputs,
)


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_production_foundation(root)
    paths = write_production_foundation_outputs(audit, out_dir)
    summary = json.loads(Path(paths["summary_json"]).read_text(encoding="utf-8"))
    print(f"v60_production_foundation bootstrap_success={audit['bootstrap_success']}")
    print(f"open_gap_count={audit['open_gap_count']}")
    print(f"production_ready_domain_count={audit['production_ready_domain_count']}")
    print(f"production_ready={audit['production_ready']}")
    print(f"bic_os_phase_locked={audit['bic_os_phase_locked']}")
    return {"summary": summary, "audit": audit, "outputs": paths}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="BioGPU-Core v6.0 Production Foundation")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(root=args.root, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
