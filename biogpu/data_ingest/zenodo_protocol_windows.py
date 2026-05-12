from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.data_ingest.zenodo_mea2100_preprocessed import discover_recording_dirs, read_metadata
from biogpu.data_ingest.zenodo_stimulus_reconstruction import (
    extract_date,
    extract_target,
    normalize_condition,
)


@dataclass
class ProtocolStimulusWindow:
    recording_path: str
    culture: str
    date: str
    condition: str
    target_type: str
    target_id: int | None
    pulse_index: int
    start_s: float
    end_s: float
    duration_s: float
    label: str
    quality: str
    evidence: str
    protocol_file: str
    original_start: float
    original_end: float
    inferred_time_unit: str


def _infer_protocol_time_unit(rows: list[dict[str, str]], duration_s: float) -> str:
    """Infer whether protocol start/end values are seconds or milliseconds.

    The uploaded Zenodo MEA2100 preprocessed archive stores protocol starts like
    1869.65 for a 604.5 second recording. That is impossible in seconds and
    therefore means milliseconds. The function is conservative and only converts
    when values clearly exceed the recording duration.
    """
    vals: list[float] = []
    for row in rows:
        for key in ("start", "end"):
            try:
                vals.append(float(str(row.get(key, "")).strip()))
            except ValueError:
                pass
    if not vals:
        return "unknown"
    max_v = max(vals)
    if duration_s > 0 and max_v > duration_s * 1.5:
        return "ms"
    return "s"


def _read_protocol_rows(protocol_file: Path) -> list[dict[str, str]]:
    text = protocol_file.read_text(encoding="utf-8", errors="ignore")
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = "\t" if "\t" in sample.splitlines()[0] else ","
    return list(csv.DictReader(text.splitlines(), delimiter=delimiter))


def read_protocol_windows_for_recording(
    recording_dir: str | Path,
    root_path: str | Path | None = None,
) -> list[ProtocolStimulusWindow]:
    rec = Path(recording_dir)
    root = Path(root_path) if root_path is not None else rec.parent
    meta = read_metadata(rec)
    duration_s = float(meta.get("recording_duration_sec") or 0.0)
    condition = normalize_condition(rec.name, meta)
    target_type_from_name, target_id_from_name = extract_target(rec.name, condition)
    rel = str(rec.relative_to(root)) if root_path is not None else str(rec)
    date = extract_date(rec)
    culture = rec.parent.name

    out: list[ProtocolStimulusWindow] = []
    protocol_dir = rec / "stimulation_protocols"
    for protocol_file in sorted(protocol_dir.glob("*.csv")):
        rows = _read_protocol_rows(protocol_file)
        unit = _infer_protocol_time_unit(rows, duration_s)
        scale = 0.001 if unit == "ms" else 1.0
        for idx, row in enumerate(rows):
            try:
                original_start = float(str(row.get("start", "")).strip())
                original_end = float(str(row.get("end", "")).strip())
            except ValueError:
                continue
            target_raw = str(row.get("target", "")).strip()
            try:
                target_id = int(float(target_raw)) if target_raw else target_id_from_name
            except ValueError:
                target_id = target_id_from_name
            target_type = target_type_from_name
            if target_type == "none":
                target_type = "protocol_target" if target_id is not None else "none"
            start_s = original_start * scale
            end_s = original_end * scale
            if end_s < start_s:
                start_s, end_s = end_s, start_s
            label_target = "none" if target_id is None else str(target_id)
            label = f"{condition}:{target_type}:{label_target}:pulse"
            out.append(
                ProtocolStimulusWindow(
                    recording_path=rel,
                    culture=culture,
                    date=date,
                    condition=condition,
                    target_type=target_type,
                    target_id=target_id,
                    pulse_index=idx,
                    start_s=float(start_s),
                    end_s=float(end_s),
                    duration_s=float(max(0.0, end_s - start_s)),
                    label=label,
                    quality="exact_protocol_csv_pulse_window",
                    evidence="stimulation_protocols/*_stimulation_protocol.csv contains explicit start/end/target fields; times inferred as milliseconds when they exceed recording duration",
                    protocol_file=str(protocol_file.relative_to(rec)),
                    original_start=original_start,
                    original_end=original_end,
                    inferred_time_unit=unit,
                )
            )
    return out


def discover_protocol_windows(root_path: str | Path) -> list[ProtocolStimulusWindow]:
    root = Path(root_path)
    windows: list[ProtocolStimulusWindow] = []
    for rec in discover_recording_dirs(root):
        windows.extend(read_protocol_windows_for_recording(rec, root))
    return windows


def write_protocol_windows_csv(windows: list[ProtocolStimulusWindow], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(windows[0]).keys()) if windows else [
        "recording_path", "culture", "date", "condition", "target_type", "target_id",
        "pulse_index", "start_s", "end_s", "duration_s", "label", "quality", "evidence",
        "protocol_file", "original_start", "original_end", "inferred_time_unit",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for w in windows:
            writer.writerow(asdict(w))


def summarize_protocol_windows(windows: list[ProtocolStimulusWindow]) -> dict[str, Any]:
    by_condition: dict[str, int] = {}
    by_recording: dict[str, int] = {}
    by_unit: dict[str, int] = {}
    durations_ms: list[float] = []
    targets_by_condition: dict[str, set[int]] = {}
    for w in windows:
        by_condition[w.condition] = by_condition.get(w.condition, 0) + 1
        by_recording[w.recording_path] = by_recording.get(w.recording_path, 0) + 1
        by_unit[w.inferred_time_unit] = by_unit.get(w.inferred_time_unit, 0) + 1
        durations_ms.append(w.duration_s * 1000.0)
        if w.target_id is not None:
            targets_by_condition.setdefault(w.condition, set()).add(int(w.target_id))
    return {
        "pulse_window_count": len(windows),
        "recording_count_with_protocols": len(by_recording),
        "by_condition": by_condition,
        "inferred_time_units": by_unit,
        "mean_duration_ms": sum(durations_ms) / len(durations_ms) if durations_ms else None,
        "min_duration_ms": min(durations_ms) if durations_ms else None,
        "max_duration_ms": max(durations_ms) if durations_ms else None,
        "targets_by_condition": {k: sorted(v) for k, v in targets_by_condition.items()},
        "honesty_note": "These are exact pulse windows from preprocessed stimulation_protocols CSV files. Raw HDF5/TTL is still useful for independent verification, but is not required to build the first pulse-window benchmark from this archive.",
    }


def assess_protocol_window_availability(root_path: str | Path) -> dict[str, Any]:
    root = Path(root_path)
    protocol_files = sorted(root.rglob("stimulation_protocols/*_stimulation_protocol.csv"))
    windows = discover_protocol_windows(root)
    summary = summarize_protocol_windows(windows)
    return {
        "protocol_file_count": len(protocol_files),
        "pulse_level_protocol_windows_available": bool(protocol_files and windows),
        "summary": summary,
        "conclusion": "Pulse-level stimulus windows are available from stimulation_protocols CSV files" if protocol_files and windows else "No stimulation_protocols CSV files found",
    }
