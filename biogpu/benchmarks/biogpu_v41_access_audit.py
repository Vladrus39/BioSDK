from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from biogpu.beta.access_policy_v41 import VERSION, write_v41_outputs


def build_v41_package(output: str | Path = "outputs/realdata_zenodo_14363732_v41_access_audit") -> dict:
    out = Path(output)
    written = write_v41_outputs(out)
    bundle_path = out / "biogpu_v41_access_audit_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in out.glob("*"):
            if p.is_file() and p != bundle_path:
                zf.write(p, arcname=p.name)
    summary = {
        "version": VERSION,
        "output_dir": str(out),
        "written_count": len(written),
        "bundle": str(bundle_path),
        "live_output_performed": False,
        "access_strategy": "maximum safe software access; live-control remains approval-gated",
    }
    (out / "session_summary_v41.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/realdata_zenodo_14363732_v41_access_audit")
    args = parser.parse_args()
    print(json.dumps(build_v41_package(args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
