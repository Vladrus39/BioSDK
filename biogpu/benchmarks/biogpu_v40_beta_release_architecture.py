
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from biogpu.beta.architecture_v40 import VERSION, build_beta_release_architecture_v40, write_beta_release_outputs_v40


def build_v40_package(output: str | Path = "outputs/realdata_zenodo_14363732_v40_beta_release") -> dict:
    out = Path(output)
    written = write_beta_release_outputs_v40(out)
    bundle_path = out / "biogpu_v40_beta_release_bundle.zip"
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
        "external_beta_default": "mock/replay/read-only",
    }
    (out / "session_summary_v40.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/realdata_zenodo_14363732_v40_beta_release")
    args = parser.parse_args()
    print(json.dumps(build_v40_package(args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
