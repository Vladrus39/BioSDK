from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from biogpu.data_ingest.zenodo_mea2100_preprocessed import discover_recording_dirs, read_metadata


@dataclass
class ReconstructedStimulusWindow:
    recording_path: str
    culture: str
    date: str
    condition: str
    target_type: str
    target_id: int | None
    start_s: float
    end_s: float
    label: str
    quality: str
    evidence: str


def normalize_condition(recording_name: str, metadata: dict[str, Any]) -> str:
    stim = str(metadata.get("stimulation", "") or "").strip().lower()
    name = recording_name.lower()
    if "lightstim" in name or stim == "lightstim":
        return "lightstim"
    if re.search(r"_stim\d+", name) or stim == "elecstim":
        return "elecstim"
    return "baseline"


def extract_target(recording_name: str, condition: str) -> tuple[str, int | None]:
    if condition == "lightstim":
        m = re.search(r"[Ss]pot\s*([0-9]+)|[Ss]pot([0-9]+)", recording_name)
        if m:
            return "light_spot", int(next(g for g in m.groups() if g))
        return "light_spot", None
    if condition == "elecstim":
        m = re.search(r"_Stim([0-9]+)", recording_name)
        if m:
            return "stimulation_electrode", int(m.group(1))
        return "stimulation_electrode", None
    return "none", None


def extract_date(recording_dir: Path) -> str:
    for part in recording_dir.parts:
        if re.match(r"\d{2}-\d{2}-\d{4}", part):
            return part
    return ""


def reconstruct_recording_level_windows(root_path: str | Path) -> list[ReconstructedStimulusWindow]:
    root = Path(root_path)
    windows: list[ReconstructedStimulusWindow] = []
    for rec in discover_recording_dirs(root):
        md = read_metadata(rec)
        condition = normalize_condition(rec.name, md)
        target_type, target_id = extract_target(rec.name, condition)
        duration = float(md.get("recording_duration_sec") or 0.0)
        rel = str(rec.relative_to(root))
        label = condition if target_id is None else f"{condition}:{target_type}:{target_id}"
        windows.append(
            ReconstructedStimulusWindow(
                recording_path=rel,
                culture=rec.parent.name,
                date=extract_date(rec),
                condition=condition,
                target_type=target_type,
                target_id=target_id,
                start_s=0.0,
                end_s=duration,
                label=label,
                quality="exact_recording_level",
                evidence="metadata recording_duration_sec + folder/meta stimulation label; pulse-level onsets are not present in Pre_processed_MEA_data.zip",
            )
        )
    return windows


def assess_pulse_window_availability(root_path: str | Path) -> dict[str, Any]:
    root = Path(root_path)
    meta_files = sorted(root.rglob("meta_data.csv"))
    protocol_files = sorted(root.rglob("stimulation_protocols/*_stimulation_protocol.csv"))
    headers: set[str] = set()
    for p in meta_files:
        with p.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            try:
                headers.update(next(reader))
            except StopIteration:
                pass
    protocol_headers: set[str] = set()
    for p in protocol_files[:10]:
        with p.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f)
            try:
                protocol_headers.update(next(reader))
            except StopIteration:
                pass
    known_timing_fields = {
        "stim_start_s", "stim_end_s", "stim_onset_s", "stim_offset_s",
        "stimulus_start", "stimulus_end", "trigger_time", "ttl_time",
        "pulse_times", "pulse_period_s", "pulse_duration_s",
    }
    found = sorted(headers.intersection(known_timing_fields))
    protocol_has_windows = {"start", "end", "target"}.issubset(protocol_headers)
    return {
        "meta_file_count": len(meta_files),
        "metadata_headers": sorted(headers),
        "pulse_timing_fields_found": found,
        "pulse_timing_fields_found_in_metadata": found,
        "pulse_level_reconstruction_possible_from_preprocessed_metadata": bool(found),
        "stimulation_protocol_file_count": len(protocol_files),
        "stimulation_protocol_headers_sample": sorted(protocol_headers),
        "pulse_level_reconstruction_possible_from_protocol_csv": bool(protocol_files and protocol_has_windows),
        "conclusion": "Pulse-level windows are available from stimulation_protocols CSV files" if protocol_files and protocol_has_windows else ("Pulse-level fields found in metadata; parser can be extended" if found else "No pulse-level protocol windows found"),
    }


def write_windows_csv(windows: list[ReconstructedStimulusWindow], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(windows[0]).keys()) if windows else [
        "recording_path", "culture", "date", "condition", "target_type", "target_id",
        "start_s", "end_s", "label", "quality", "evidence",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for w in windows:
            writer.writerow(asdict(w))


def summarize_reconstructed_windows(windows: list[ReconstructedStimulusWindow]) -> dict[str, Any]:
    by_condition: dict[str, int] = {}
    by_quality: dict[str, int] = {}
    targets: dict[str, list[int]] = {"light_spot": [], "stimulation_electrode": []}
    for w in windows:
        by_condition[w.condition] = by_condition.get(w.condition, 0) + 1
        by_quality[w.quality] = by_quality.get(w.quality, 0) + 1
        if w.target_id is not None and w.target_type in targets:
            targets[w.target_type].append(int(w.target_id))
    return {
        "window_count": len(windows),
        "by_condition": by_condition,
        "by_quality": by_quality,
        "light_spots": sorted(set(targets["light_spot"])),
        "stimulation_electrodes": sorted(set(targets["stimulation_electrode"])),
        "honesty_note": "These are exact recording-level windows. For pulse-level windows, use biogpu.data_ingest.zenodo_protocol_windows when stimulation_protocols CSV files are present.",
    }
