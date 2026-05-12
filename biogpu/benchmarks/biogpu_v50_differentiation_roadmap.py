"""Generate BioGPU-Core v5.0 differentiation and first-mover roadmap artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from dataclasses import asdict

from biogpu.os.differentiation_v50 import (
    PROJECT_POSITIONING,
    differentiators,
    os_capabilities,
    proof_targets,
    project_summary,
)

DEFAULT_OUT = Path("outputs/realdata_zenodo_14363732_v50_differentiation_roadmap")


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _md_table(rows: list[dict], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        vals = []
        for field in fields:
            val = row.get(field, "")
            if isinstance(val, list):
                val = "; ".join(str(v) for v in val)
            vals.append(str(val).replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_report(out_dir: Path = DEFAULT_OUT) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    diff_rows = [asdict(x) for x in differentiators()]
    cap_rows = [asdict(x) for x in os_capabilities()]
    proof_rows = [asdict(x) for x in proof_targets()]
    summary = project_summary()

    (out_dir / "v50_project_positioning.json").write_text(json.dumps(PROJECT_POSITIONING, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "v50_differentiation_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_csv(out_dir / "v50_differentiators.csv", diff_rows)
    _write_csv(out_dir / "v50_os_capabilities.csv", cap_rows)
    _write_csv(out_dir / "v50_proof_targets.csv", proof_rows)

    report = f"""# BioGPU-Core v5.0 Differentiation and First-Mover Roadmap

## Project target

**{PROJECT_POSITIONING['technical_kernel']}** remains the technical kernel. The external product path is:

```text
BioSDK / Living Compute SDK
→ BioCompute Runtime
→ NSI-1.0 / Neural Substrate Interface
→ BioCompute Control Plane
→ BiC OS
```

## Primary claim

{PROJECT_POSITIONING['primary_claim']}

## What we must not overclaim

- We are not claiming to be the first biological computer.
- We are not claiming to replace GPUs for LLM inference.
- We are not claiming live BioGPU proof before laboratory validation.
- We are not replacing NWB; NSI should interoperate with NWB/HDF5/API/vendor exports.

## Differentiators to build toward

{_md_table(diff_rows, ['id', 'title', 'status', 'first_mover_claim'])}

## BiC OS capabilities

{_md_table(cap_rows, ['id', 'title', 'target_layer', 'beta_form', 'mature_form'])}

## Proof targets

{_md_table(proof_rows, ['id', 'claim', 'can_prove_before_lab', 'release_gate'])}

## Strategic conclusion

The project should not try to win by claiming "first wetware computer" or "GPU replacement". The highest-value path is to become the **vendor-neutral interface, runtime, evidence, and AI-agent operating layer** for living neural compute. That is the part we can prove incrementally before lab access, and it is the foundation of a credible future BiC OS.
"""
    (out_dir / "BIOGPU_V50_DIFFERENTIATION_REPORT.md").write_text(report, encoding="utf-8")
    return {
        "out_dir": str(out_dir),
        "differentiator_count": len(diff_rows),
        "os_capability_count": len(cap_rows),
        "proof_target_count": len(proof_rows),
        "ready": True,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    result = build_report(Path(args.out_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
