from __future__ import annotations
from pathlib import Path
from typing import Any
import json
from biogpu.data_ingest.zenodo_manifest import zenodo_manifest_dict
from biogpu.data_ingest.dandi_discovery import candidates_as_dict

def build_public_data_status_report(extra: dict[str, Any] | None = None) -> str:
    m = zenodo_manifest_dict()
    cands = candidates_as_dict()
    lines = [
        "# BioGPU v0.9 Public Data Status Report",
        "",
        "## Strategy",
        "",
        "SimulatedMEA is now an engineering scaffold. Real progress should come from public spike/NWB data and task-aligned stimulus windows.",
        "",
        "## Zenodo 14363732",
        "",
        f"Record: {m['record_url']}",
        f"Hardware: {m['hardware']}",
        "",
        "Recommended first download:",
    ]
    for f in m["files"]:
        if f.get("download_by_default"):
            lines.append(f"- `{f['filename']}` — {f['size_mb']} MB — {f['role']}")
    lines += [
        "",
        "Do not download raw HDF5 first unless you have enough storage; the raw zip is ~35.9 GB.",
        "",
        "## DANDI candidates",
        "",
    ]
    for c in cands:
        lines.append(f"- DANDI `{c['dandiset_id']}` — {c['name']} — relevance: {c['why_relevant']}")
    lines += [
        "",
        "## Honesty rule",
        "",
        "Real spike profiling can run on spike times alone. Classification/benchmark claims require real `start_s,end_s,label` stimulus windows from the dataset metadata.",
    ]
    if extra:
        lines += ["", "## Local status", "", "```json", json.dumps(extra, indent=2, ensure_ascii=False), "```"]
    return "\n".join(lines) + "\n"

def write_public_data_status_report(path: str | Path, extra: dict[str, Any] | None = None) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(build_public_data_status_report(extra), encoding="utf-8")
    return p
