"""BioGPU-Core v5.1 — Dataset & API expansion benchmark.

Probes all Dataset/API expansion phase sources and writes a machine-readable
status report under outputs/v51_dataset_expansion/.

Sources covered
---------------
1. Zenodo 14363732 raw HDF5 / TTL gate  (zenodo_raw_hdf5_gate)
2. DANDI curated-candidate manifest     (dandi_discovery)
3. DANDI/NWB inspection (offline gate)  (dandi_nwb.inspect_nwb_units)
4. AllenSDK orientation dataset probe   (datasets.orientation — pure synthetic)
5. Vendor adapter registry probe        (datasets.registry_v42)
6. User-upload import skeleton probe    (datasets.importers_v42)

All probes are safe offline and never make network calls.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Probe functions
# ---------------------------------------------------------------------------

def probe_zenodo_raw_hdf5(project_root: Path, outdir: Path) -> dict[str, Any]:
    from biogpu.data_ingest.zenodo_raw_hdf5_gate import probe_all_raw_hdf5_assets
    report = probe_all_raw_hdf5_assets(project_root=project_root)
    _write_json(outdir / "zenodo_raw_hdf5_gate.json", report.to_dict())
    return {
        "probe": "zenodo_raw_hdf5_gate",
        "overall_status": report.overall_status,
        "asset_count": len(report.assets),
        "summary": report.summary,
    }


def probe_dandi_candidates(outdir: Path) -> dict[str, Any]:
    from biogpu.data_ingest.dandi_discovery import curated_candidates, write_candidate_manifest
    candidates = curated_candidates()
    manifest_path = outdir / "dandi_curated_candidates.json"
    write_candidate_manifest(manifest_path)
    return {
        "probe": "dandi_discovery",
        "candidate_count": len(candidates),
        "dandiset_ids": [c.dandiset_id for c in candidates],
        "manifest_written": str(manifest_path),
    }


def probe_dandi_nwb_gate(outdir: Path) -> dict[str, Any]:
    """Report NWB file availability without requiring an actual download."""
    from biogpu.data_ingest.dandi_nwb import inspect_nwb_units
    # No NWB files present yet; this is an offline gate probe.
    result = inspect_nwb_units("data/external/nwb_placeholder_not_present.nwb")
    _write_json(outdir / "dandi_nwb_gate.json", result)
    return {
        "probe": "dandi_nwb_gate",
        "nwb_file_present": result.get("exists", False),
        "gate_status": "not_downloaded" if not result.get("exists", False) else "available",
        "download_hint": (
            "Download an NWB file from https://dandiarchive.org/dandiset/000469 "
            "and place it under data/external/nwb/ to enable NWB parsing."
        ),
    }


def probe_orientation_dataset(outdir: Path) -> dict[str, Any]:
    """Generate a small synthetic orientation dataset as benchmark signal."""
    from biogpu.datasets.orientation import generate_orientation_dataset, ORIENTATIONS
    patterns = generate_orientation_dataset(size=16, samples_per_class=20, seed=42)
    label_counts = {}
    for p in patterns:
        label_counts[int(p.label)] = label_counts.get(int(p.label), 0) + 1
    summary = {
        "probe": "orientation_dataset",
        "orientations": ORIENTATIONS,
        "total_patterns": len(patterns),
        "label_counts": label_counts,
        "pattern_shape": list(patterns[0].data.shape),
        "source": "synthetic_local_no_download_needed",
    }
    _write_json(outdir / "orientation_dataset_probe.json", summary)
    return summary


def probe_vendor_registry(outdir: Path) -> dict[str, Any]:
    from biogpu.datasets.registry_v42 import build_default_dataset_registry_v42
    registry = build_default_dataset_registry_v42()
    errors = registry.validate()
    entries_summary = [
        {
            "dataset_id": e.dataset_id,
            "status": e.status,
            "access_mode": e.access_mode.value,
            "priority": e.beta_release_priority,
        }
        for e in registry.entries.values()
    ]
    result = {
        "probe": "vendor_registry_v42",
        "entry_count": len(registry.entries),
        "validation_errors": errors,
        "entries": entries_summary,
    }
    _write_json(outdir / "vendor_registry_probe.json", result)
    return {
        "probe": "vendor_registry_v42",
        "entry_count": len(registry.entries),
        "validation_errors": len(errors),
        "p0_count": sum(1 for e in registry.entries.values() if e.beta_release_priority == "P0"),
    }


def probe_user_upload_importers(outdir: Path) -> dict[str, Any]:
    from biogpu.datasets.importers_v42 import build_importer_catalog_v42
    catalog = build_importer_catalog_v42()
    result = {
        "probe": "user_upload_importers_v42",
        "importer_count": len(catalog),
        "importer_ids": sorted(catalog.keys()),
        "extensions_covered": sorted({
            ext
            for imp in catalog.values()
            for ext in imp.supported_extensions
        }),
    }
    _write_json(outdir / "user_upload_importers_probe.json", result)
    return result


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main(
    project_root: str = ".",
    output_dir: str = "outputs/v51_dataset_expansion",
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    probes: list[dict[str, Any]] = []

    probes.append(probe_zenodo_raw_hdf5(root, outdir))
    probes.append(probe_dandi_candidates(outdir))
    probes.append(probe_dandi_nwb_gate(outdir))
    probes.append(probe_orientation_dataset(outdir))

    # Vendor registry and importers: tolerate missing implementations gracefully.
    try:
        probes.append(probe_vendor_registry(outdir))
    except Exception as exc:
        probes.append({"probe": "vendor_registry_v42", "error": str(exc)})

    try:
        probes.append(probe_user_upload_importers(outdir))
    except Exception as exc:
        probes.append({"probe": "user_upload_importers_v42", "error": str(exc)})

    # Aggregate gating decisions.
    raw_hdf5_available = any(
        p.get("overall_status") == "available"
        for p in probes
        if p.get("probe") == "zenodo_raw_hdf5_gate"
    )
    raw_hdf5_status = next(
        (p.get("overall_status", "unknown") for p in probes if p.get("probe") == "zenodo_raw_hdf5_gate"),
        "unknown",
    )
    nwb_available = any(
        p.get("nwb_file_present") is True
        for p in probes
        if p.get("probe") == "dandi_nwb_gate"
    )
    nwb_status = next(
        (p.get("gate_status", "unknown") for p in probes if p.get("probe") == "dandi_nwb_gate"),
        "unknown",
    )

    summary: dict[str, Any] = {
        "phase": "dataset_api_expansion",
        "milestone": "v5.1",
        "python": sys.version,
        "platform": platform.platform(),
        "project_root": str(root),
        "probes": probes,
        "gate": {
            "raw_hdf5_available": raw_hdf5_available,
            "nwb_available": nwb_available,
            "orientation_synthetic_available": True,
            "vendor_registry_loaded": any(
                "error" not in p
                for p in probes
                if p.get("probe") == "vendor_registry_v42"
            ),
        },
        "notes": [
            f"raw_hdf5_gate={raw_hdf5_status}; raw_hdf5_available={raw_hdf5_available}.",
            f"dandi_nwb_gate={nwb_status}; nwb_available={nwb_available}.",
            "orientation_dataset is fully synthetic and always available.",
        ],
    }

    _write_json(outdir / "V51_DATASET_EXPANSION_SUMMARY.json", summary)
    print(f"v51_dataset_expansion probe count={len(probes)}")
    print(f"raw_hdf5_available={raw_hdf5_available}")
    print(f"nwb_available={nwb_available}")
    return summary


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="BioGPU v5.1 Dataset/API expansion probe runner")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--out-dir", default="outputs/v51_dataset_expansion")
    args = ap.parse_args()
    main(project_root=args.project_root, output_dir=args.out_dir)
