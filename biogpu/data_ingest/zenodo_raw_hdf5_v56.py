"""Zenodo 14363732 raw HDF5 structure and event inspection, v5.6."""
from __future__ import annotations

import csv
import json
import re
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


RAW_HDF5_DEFAULT_ROOT = Path("data/external/raw_hdf5")


@dataclass(frozen=True)
class RawHDF5EventCandidateV56:
    file: str
    stream: str
    entity: str
    label: str
    detector_kind: str
    event_count: int
    first_timestamp_us: int | None
    last_timestamp_us: int | None
    first_timestamp_s: float | None
    last_timestamp_s: float | None
    median_interval_s: float | None
    info_type_values: tuple[int, ...]
    sample_timestamps_us: tuple[int, ...]
    candidate_kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawHDF5FileInspectionV56:
    file: str
    size_bytes: int
    exists: bool
    h5py_available: bool
    valid_hdf5: bool
    protocol_type: str | None = None
    protocol_version: str | None = None
    generating_application: str | None = None
    recording_date: str | None = None
    recording_duration_us: int | None = None
    stimulation_kind: str = "unknown"
    target_id: str | None = None
    channel_count: int | None = None
    sample_count: int | None = None
    sample_rate_hz: float | None = None
    analog_stream_path: str | None = None
    channel_info_path: str | None = None
    event_candidate_count: int = 0
    event_total_count: int = 0
    event_candidates: tuple[RawHDF5EventCandidateV56, ...] = field(default_factory=tuple)
    top_level_keys: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawHDF5InspectionReportV56:
    version: str
    root: str
    file_count: int
    inspected_file_count: int
    valid_file_count: int
    files_with_events: int
    event_candidate_count: int
    event_total_count: int
    hdf5_total_bytes: int
    ttl_csv_count: int
    stimulation_kind_counts: dict[str, int]
    overall_status: str
    inspections: tuple[RawHDF5FileInspectionV56, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _decode_attr(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "decode"):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            pass
    return str(value)


def _median_interval_s(timestamps_us: list[int]) -> float | None:
    if len(timestamps_us) < 2:
        return None
    deltas = [b - a for a, b in zip(timestamps_us, timestamps_us[1:]) if b >= a]
    if not deltas:
        return None
    return round(float(statistics.median(deltas)) / 1_000_000.0, 6)


def infer_stimulation_kind_v56(path: str | Path) -> str:
    name = Path(path).name.lower()
    if "lightstim" in name or "light_stim" in name:
        return "light_stimulation"
    if "elecstim" in name or "_stim" in name or "stim" in name:
        return "electrical_stimulation"
    return "baseline_or_spontaneous"


def infer_target_id_v56(path: str | Path) -> str | None:
    stem = Path(path).stem
    match = re.search(r"(?:LightStim_Spot|Spot|ElecStim|Stim|stim)(\d+)", stem, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _detector_kind(label: str) -> str:
    lower = label.lower()
    if "stimulator" in lower or "stg events" in lower:
        return "stimulator_event"
    if "digital event" in lower or "digitalport" in lower:
        return "digital_port_event"
    return "event"


def _candidate_kind(label: str, file_name: str) -> str:
    text = f"{label} {file_name}".lower()
    if "stimulator" in text or "elecstim" in text or "_stim" in text:
        return "electrical_stimulation_event"
    if "lightstim" in text or "digital event detector" in text or "spot" in text:
        return "light_or_digital_stimulation_event"
    return "unknown_event"


def discover_raw_hdf5_files(root: str | Path = RAW_HDF5_DEFAULT_ROOT) -> list[Path]:
    base = Path(root)
    if not base.exists():
        return []
    return sorted(base.rglob("*.h5"))


def inspect_raw_hdf5_file_v56(path: str | Path, root: str | Path | None = None) -> RawHDF5FileInspectionV56:
    file_path = Path(path)
    rel = str(file_path)
    if root is not None:
        try:
            rel = str(file_path.relative_to(Path(root)))
        except ValueError:
            rel = str(file_path)
    if not file_path.exists():
        return RawHDF5FileInspectionV56(
            file=rel,
            size_bytes=0,
            exists=False,
            h5py_available=False,
            valid_hdf5=False,
            errors=("file_not_found",),
        )
    try:
        import h5py  # type: ignore
    except ImportError:
        return RawHDF5FileInspectionV56(
            file=rel,
            size_bytes=file_path.stat().st_size,
            exists=True,
            h5py_available=False,
            valid_hdf5=False,
            errors=("h5py_not_installed",),
        )

    try:
        with h5py.File(file_path, "r") as hf:
            data_group = hf.get("Data")
            recording_group = hf.get("Data/Recording_0")
            analog = hf.get("Data/Recording_0/AnalogStream/Stream_0/ChannelData")
            channel_info = hf.get("Data/Recording_0/AnalogStream/Stream_0/InfoChannel")
            duration_us = None
            if recording_group is not None and "Duration" in recording_group.attrs:
                duration_us = int(recording_group.attrs.get("Duration", 0))
            channel_count = int(analog.shape[0]) if analog is not None and len(analog.shape) >= 1 else None
            sample_count = int(analog.shape[1]) if analog is not None and len(analog.shape) >= 2 else None
            sample_rate_hz = None
            if duration_us and sample_count:
                sample_rate_hz = round(sample_count / (duration_us / 1_000_000.0), 6)
            candidates = tuple(_event_candidates_for_file(hf, rel))
            event_total = sum(candidate.event_count for candidate in candidates)
            return RawHDF5FileInspectionV56(
                file=rel,
                size_bytes=file_path.stat().st_size,
                exists=True,
                h5py_available=True,
                valid_hdf5=True,
                protocol_type=_decode_attr(hf.attrs.get("McsHdf5ProtocolType")) if "McsHdf5ProtocolType" in hf.attrs else None,
                protocol_version=_decode_attr(hf.attrs.get("McsHdf5ProtocolVersion")) if "McsHdf5ProtocolVersion" in hf.attrs else None,
                generating_application=_decode_attr(hf.attrs.get("GeneratingApplicationName")) if "GeneratingApplicationName" in hf.attrs else None,
                recording_date=_decode_attr(data_group.attrs.get("Date")) if data_group is not None and "Date" in data_group.attrs else None,
                recording_duration_us=duration_us,
                stimulation_kind=infer_stimulation_kind_v56(file_path),
                target_id=infer_target_id_v56(file_path),
                channel_count=channel_count,
                sample_count=sample_count,
                sample_rate_hz=sample_rate_hz,
                analog_stream_path="Data/Recording_0/AnalogStream/Stream_0/ChannelData" if analog is not None else None,
                channel_info_path="Data/Recording_0/AnalogStream/Stream_0/InfoChannel" if channel_info is not None else None,
                event_candidate_count=len(candidates),
                event_total_count=event_total,
                event_candidates=candidates,
                top_level_keys=tuple(str(key) for key in hf.keys()),
            )
    except Exception as exc:  # pragma: no cover - depends on corrupt external files
        return RawHDF5FileInspectionV56(
            file=rel,
            size_bytes=file_path.stat().st_size,
            exists=True,
            h5py_available=True,
            valid_hdf5=False,
            errors=(f"hdf5_open_failed:{type(exc).__name__}:{exc}",),
        )


def _event_candidates_for_file(hf: Any, file_name: str) -> list[RawHDF5EventCandidateV56]:
    event_group = hf.get("Data/Recording_0/EventStream")
    if event_group is None:
        return []
    candidates: list[RawHDF5EventCandidateV56] = []
    for stream_name in sorted(event_group.keys()):
        stream = event_group[stream_name]
        label = _decode_attr(stream.attrs.get("Label", ""))
        for entity_name in sorted(stream.keys()):
            if not str(entity_name).startswith("EventEntity"):
                continue
            dataset = stream[entity_name]
            if not hasattr(dataset, "shape") or len(dataset.shape) != 2 or dataset.shape[0] < 1:
                continue
            if int(dataset.shape[1]) <= 0:
                continue
            values = dataset[()]
            timestamps = [int(value) for value in values[0].tolist() if int(value) >= 0]
            info_type_values: tuple[int, ...] = ()
            if values.shape[0] >= 3:
                info_type_values = tuple(sorted({int(value) for value in values[2].tolist() if int(value) >= 0}))
            first_us = min(timestamps) if timestamps else None
            last_us = max(timestamps) if timestamps else None
            candidates.append(
                RawHDF5EventCandidateV56(
                    file=file_name,
                    stream=str(stream_name),
                    entity=str(entity_name),
                    label=label,
                    detector_kind=_detector_kind(label),
                    event_count=len(timestamps),
                    first_timestamp_us=first_us,
                    last_timestamp_us=last_us,
                    first_timestamp_s=round(first_us / 1_000_000.0, 6) if first_us is not None else None,
                    last_timestamp_s=round(last_us / 1_000_000.0, 6) if last_us is not None else None,
                    median_interval_s=_median_interval_s(timestamps),
                    info_type_values=info_type_values,
                    sample_timestamps_us=tuple(timestamps[:5]),
                    candidate_kind=_candidate_kind(label, file_name),
                )
            )
    return candidates


def inspect_raw_hdf5_tree_v56(
    root: str | Path = RAW_HDF5_DEFAULT_ROOT,
    max_files: int | None = None,
) -> RawHDF5InspectionReportV56:
    base = Path(root)
    files = discover_raw_hdf5_files(base)
    selected = files if max_files is None else files[:max_files]
    inspections = tuple(inspect_raw_hdf5_file_v56(path, base) for path in selected)
    valid_count = sum(1 for item in inspections if item.valid_hdf5)
    files_with_events = sum(1 for item in inspections if item.event_candidate_count > 0)
    event_candidate_count = sum(item.event_candidate_count for item in inspections)
    event_total_count = sum(item.event_total_count for item in inspections)
    ttl_csv_count = len(sorted(base.rglob("*.csv"))) if base.exists() else 0
    kind_counts: dict[str, int] = {}
    for item in inspections:
        kind_counts[item.stimulation_kind] = kind_counts.get(item.stimulation_kind, 0) + 1
    if not files:
        status = "not_downloaded"
    elif valid_count == len(selected) and event_candidate_count > 0:
        status = "raw_hdf5_events_available"
    elif valid_count > 0:
        status = "raw_hdf5_no_events_found"
    else:
        status = "raw_hdf5_unreadable"
    return RawHDF5InspectionReportV56(
        version="v5.6",
        root=str(base),
        file_count=len(files),
        inspected_file_count=len(inspections),
        valid_file_count=valid_count,
        files_with_events=files_with_events,
        event_candidate_count=event_candidate_count,
        event_total_count=event_total_count,
        hdf5_total_bytes=sum(path.stat().st_size for path in files if path.is_file()),
        ttl_csv_count=ttl_csv_count,
        stimulation_kind_counts=kind_counts,
        overall_status=status,
        inspections=inspections,
    )


def write_raw_hdf5_outputs_v56(report: RawHDF5InspectionReportV56, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V56_RAW_HDF5_STRUCTURE_SUMMARY.json",
        "file_report_json": out / "V56_RAW_HDF5_FILE_REPORT.json",
        "event_candidates_csv": out / "V56_TTL_EVENT_CANDIDATES.csv",
        "stimulus_windows_preview_csv": out / "V56_RAW_STIMULUS_WINDOWS_PREVIEW.csv",
        "markdown_report": out / "BIOGPU_V56_RAW_HDF5_STRUCTURE_REPORT.md",
    }
    summary = {
        "version": report.version,
        "overall_status": report.overall_status,
        "file_count": report.file_count,
        "inspected_file_count": report.inspected_file_count,
        "valid_file_count": report.valid_file_count,
        "files_with_events": report.files_with_events,
        "event_candidate_count": report.event_candidate_count,
        "event_total_count": report.event_total_count,
        "hdf5_total_gb": round(report.hdf5_total_bytes / (1024 ** 3), 3),
        "ttl_csv_count": report.ttl_csv_count,
        "stimulation_kind_counts": report.stimulation_kind_counts,
        "claim_boundary": "raw event/structure inspection only; no live biology and no advantage claim",
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["file_report_json"].write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    _write_event_candidates_csv(paths["event_candidates_csv"], report)
    _write_stimulus_windows_preview_csv(paths["stimulus_windows_preview_csv"], report)
    paths["markdown_report"].write_text(_markdown_report(report, summary), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _candidate_rows(report: RawHDF5InspectionReportV56) -> list[RawHDF5EventCandidateV56]:
    rows: list[RawHDF5EventCandidateV56] = []
    for inspection in report.inspections:
        rows.extend(inspection.event_candidates)
    return rows


def _write_event_candidates_csv(path: Path, report: RawHDF5InspectionReportV56) -> None:
    rows = _candidate_rows(report)
    fieldnames = [
        "file",
        "stream",
        "entity",
        "label",
        "detector_kind",
        "event_count",
        "first_timestamp_s",
        "last_timestamp_s",
        "median_interval_s",
        "info_type_values",
        "sample_timestamps_us",
        "candidate_kind",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            item = row.to_dict()
            item["info_type_values"] = ";".join(str(value) for value in row.info_type_values)
            item["sample_timestamps_us"] = ";".join(str(value) for value in row.sample_timestamps_us)
            writer.writerow({key: item.get(key) for key in fieldnames})


def _write_stimulus_windows_preview_csv(path: Path, report: RawHDF5InspectionReportV56) -> None:
    fieldnames = ["file", "stream", "entity", "event_index_preview", "timestamp_s", "sample_timestamp_us", "candidate_kind"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for candidate in _candidate_rows(report):
            for index, timestamp_us in enumerate(candidate.sample_timestamps_us):
                writer.writerow({
                    "file": candidate.file,
                    "stream": candidate.stream,
                    "entity": candidate.entity,
                    "event_index_preview": index,
                    "timestamp_s": round(timestamp_us / 1_000_000.0, 6),
                    "sample_timestamp_us": timestamp_us,
                    "candidate_kind": candidate.candidate_kind,
                })


def _markdown_report(report: RawHDF5InspectionReportV56, summary: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.6 Raw HDF5 Structure Report",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- HDF5 files: `{summary['file_count']}`",
        f"- Valid inspected files: `{summary['valid_file_count']}` / `{summary['inspected_file_count']}`",
        f"- Files with event candidates: `{summary['files_with_events']}`",
        f"- Event candidate datasets: `{summary['event_candidate_count']}`",
        f"- Total event timestamps across candidates: `{summary['event_total_count']}`",
        f"- Extracted HDF5 size: `{summary['hdf5_total_gb']}` GB",
        f"- External TTL CSV files: `{summary['ttl_csv_count']}`",
        f"- Stimulation kind counts: `{summary['stimulation_kind_counts']}`",
        "",
        "## Interpretation",
        "",
        "External TTL CSV files are absent, but embedded HDF5 EventStream datasets are present in many stimulation recordings. These event entities are the first-pass raw stimulus/TTL candidates for downstream raw-vs-preprocessed validation.",
        "",
        "## Claim Boundary",
        "",
        "This report maps raw HDF5 structure and event candidates only. It does not claim live BioGPU operation, wet-lab control, GPU replacement or performance/energy advantage.",
        "",
        "## First Event Candidates",
        "",
    ]
    for candidate in _candidate_rows(report)[:20]:
        lines.append(
            f"- `{candidate.file}` `{candidate.stream}/{candidate.entity}`: "
            f"{candidate.event_count} events, first={candidate.first_timestamp_s}s, "
            f"median_interval={candidate.median_interval_s}s, kind={candidate.candidate_kind}"
        )
    lines.append("")
    return "\n".join(lines)
