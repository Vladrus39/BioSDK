"""Zenodo 14363732 raw HDF5 / TTL asset gate.

The Zenodo dataset 14363732 contains both:
  - Pre_processed_MEA_data.zip  (already validated in v5.0 PC validation phase)
  - Raw HDF5 files from MEA2100 system recordings (not bundled in the preprocessed ZIP)

This module knows the expected raw asset structure, checks local availability,
and returns clear gate status.  If raw files are present it delegates to the
h5py-based reader; if not, it returns explicit 'not_downloaded' metadata so
downstream code can skip or schedule a download.

Safe for offline / CI environments: no network calls are made here.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Known raw-HDF5 asset descriptors for Zenodo 14363732
# Source: Zenodo record metadata for https://zenodo.org/records/14363732
# ---------------------------------------------------------------------------

RAW_HDF5_ASSET_MANIFEST: list[dict[str, str]] = [
    {
        "asset_id": "zenodo_14363732_raw_hdf5",
        "description": "Raw MEA2100 HDF5 recordings for Zenodo 14363732",
        "expected_extension": ".h5",
        "download_hint": (
            "Download raw HDF5 files from https://zenodo.org/records/14363732 "
            "and place them under data/external/raw_hdf5/ in the project root."
        ),
        "local_subdir": "raw_hdf5",
    },
    {
        "asset_id": "zenodo_14363732_ttl_csv",
        "description": "TTL / event-marker CSV files paired with raw HDF5 recordings",
        "expected_extension": ".csv",
        "download_hint": (
            "TTL event CSVs accompany the raw HDF5 files at the same Zenodo record. "
            "Place them under data/external/raw_hdf5/ alongside the .h5 files."
        ),
        "local_subdir": "raw_hdf5",
    },
]

_GATE_STATUS_NOT_DOWNLOADED = "not_downloaded"
_GATE_STATUS_AVAILABLE = "available"
_GATE_STATUS_PARTIAL = "partial"
_GATE_STATUS_EMPTY_DIR = "empty_dir"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RawHDF5AssetProbe:
    asset_id: str
    description: str
    local_path: str
    dir_exists: bool
    file_count: int
    file_extension: str
    total_bytes: int
    sample_files: list[str]
    gate_status: str          # not_downloaded | available | partial | empty_dir
    download_hint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RawHDF5GateReport:
    project_root: str
    external_base: str
    assets: list[RawHDF5AssetProbe] = field(default_factory=list)
    overall_status: str = _GATE_STATUS_NOT_DOWNLOADED
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    def write_json(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return p


# ---------------------------------------------------------------------------
# Core probe logic
# ---------------------------------------------------------------------------

def probe_raw_hdf5_asset(
    descriptor: dict[str, str],
    external_base: Path,
) -> RawHDF5AssetProbe:
    """Check whether a single raw HDF5 asset is locally available."""
    subdir = external_base / descriptor["local_subdir"]
    ext = descriptor["expected_extension"]

    dir_exists = subdir.is_dir()
    files: list[Path] = []
    if dir_exists:
        files = sorted(subdir.rglob(f"*{ext}"))

    file_count = len(files)
    total_bytes = sum(f.stat().st_size for f in files if f.is_file())
    sample_files = [str(f.relative_to(external_base)) for f in files[:10]]

    if not dir_exists or file_count == 0:
        gate_status = _GATE_STATUS_NOT_DOWNLOADED if not dir_exists else _GATE_STATUS_EMPTY_DIR
    else:
        # Treat as partial if fewer than 2 files (heuristic; real threshold TBD once
        # the full Zenodo record structure is inspected locally)
        gate_status = _GATE_STATUS_AVAILABLE if file_count >= 2 else _GATE_STATUS_PARTIAL

    return RawHDF5AssetProbe(
        asset_id=descriptor["asset_id"],
        description=descriptor["description"],
        local_path=str(subdir),
        dir_exists=dir_exists,
        file_count=file_count,
        file_extension=ext,
        total_bytes=total_bytes,
        sample_files=sample_files,
        gate_status=gate_status,
        download_hint=descriptor["download_hint"],
    )


def probe_all_raw_hdf5_assets(
    project_root: str | Path | None = None,
) -> RawHDF5GateReport:
    """Probe all known raw HDF5 assets relative to *project_root*.

    If *project_root* is None, the working directory is used.
    """
    root = Path(project_root) if project_root else Path.cwd()
    external_base = root / "data" / "external"

    probes: list[RawHDF5AssetProbe] = [
        probe_raw_hdf5_asset(d, external_base) for d in RAW_HDF5_ASSET_MANIFEST
    ]

    available = sum(1 for p in probes if p.gate_status == _GATE_STATUS_AVAILABLE)
    partial = sum(1 for p in probes if p.gate_status == _GATE_STATUS_PARTIAL)

    if available == len(probes):
        overall = _GATE_STATUS_AVAILABLE
        summary = f"All {len(probes)} raw HDF5 asset groups available locally."
    elif available + partial > 0:
        overall = _GATE_STATUS_PARTIAL
        summary = f"{available} available, {partial} partial, {len(probes) - available - partial} not downloaded."
    else:
        overall = _GATE_STATUS_NOT_DOWNLOADED
        summary = (
            f"No raw HDF5 assets found under {external_base / 'raw_hdf5'}. "
            "Download from Zenodo record 14363732 to enable raw HDF5 reconstruction."
        )

    return RawHDF5GateReport(
        project_root=str(root),
        external_base=str(external_base),
        assets=probes,
        overall_status=overall,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Optional: h5py-based raw file inspection (only when h5py is available and
# the file actually exists)
# ---------------------------------------------------------------------------

def inspect_raw_hdf5_file(path: str | Path) -> dict[str, Any]:
    """Return a safe inspection dict for a single raw HDF5 file.

    Returns ``{"exists": False}`` when the file is absent.
    Returns ``{"exists": True, "h5py_available": False}`` when h5py is not installed.
    Returns top-level key list and dataset shapes when h5py is present.
    """
    p = Path(path)
    if not p.exists():
        return {"path": str(p), "exists": False, "gate_status": _GATE_STATUS_NOT_DOWNLOADED}

    try:
        import h5py  # type: ignore
    except ImportError:
        return {
            "path": str(p),
            "exists": True,
            "h5py_available": False,
            "gate_status": "h5py_not_installed",
            "install_hint": "pip install h5py",
        }

    info: dict[str, Any] = {
        "path": str(p),
        "exists": True,
        "h5py_available": True,
        "gate_status": _GATE_STATUS_AVAILABLE,
    }
    with h5py.File(p, "r") as hf:
        info["top_level_keys"] = list(hf.keys())[:20]
        shapes: dict[str, Any] = {}
        def _visitor(name: str, obj: Any) -> None:  # noqa: ANN001
            if hasattr(obj, "shape"):
                shapes[name] = {"shape": list(obj.shape), "dtype": str(obj.dtype)}
            if len(shapes) >= 30:
                return None
        hf.visititems(_visitor)
        info["dataset_shapes"] = shapes
        info["dataset_count"] = len(shapes)
    return info


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(output_dir: str = "outputs/v51_dataset_expansion") -> dict[str, Any]:
    report = probe_all_raw_hdf5_assets()
    out_path = report.write_json(
        Path(output_dir) / "ZENODO_RAW_HDF5_GATE_REPORT.json"
    )
    print(f"gate_status={report.overall_status}")
    print(f"summary={report.summary}")
    print(f"report_path={out_path}")
    return report.to_dict()


if __name__ == "__main__":
    main()
