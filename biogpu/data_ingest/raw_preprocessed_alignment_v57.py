"""Raw HDF5 event to preprocessed pulse alignment audit, v5.7."""
from __future__ import annotations

import csv
import json
import re
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_RAW_EVENT_CANDIDATES = Path("outputs/v56_raw_hdf5_structure/V56_TTL_EVENT_CANDIDATES.csv")
DEFAULT_PULSE_METADATA = Path("evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv")


@dataclass(frozen=True)
class RawEventRecordingV57:
    source_file: str
    date: str
    culture: str
    condition: str
    target_id: str
    recording_stem: str
    event_entity_count: int
    representative_event_count: int
    total_event_timestamps: int
    first_event_s: float | None
    last_event_s: float | None
    median_interval_s: float | None
    candidate_kinds: tuple[str, ...]

    @property
    def exact_key(self) -> tuple[str, str, str, str, str]:
        return (self.date, self.culture, self.condition, self.target_id, _normalize_stem(self.recording_stem))

    @property
    def date_culture_target_key(self) -> tuple[str, str, str, str]:
        return (self.date, self.culture, self.condition, self.target_id)

    @property
    def condition_target_key(self) -> tuple[str, str]:
        return (self.condition, self.target_id)

    @property
    def date_culture_key(self) -> tuple[str, str]:
        return (self.date, self.culture)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PreprocessedPulseRecordingV57:
    recording_path: str
    date: str
    culture: str
    condition: str
    target_id: str
    recording_stem: str
    pulse_count: int
    first_start_s: float | None
    last_start_s: float | None
    median_interval_s: float | None
    median_duration_s: float | None

    @property
    def exact_key(self) -> tuple[str, str, str, str, str]:
        return (self.date, self.culture, self.condition, self.target_id, _normalize_stem(self.recording_stem))

    @property
    def date_culture_target_key(self) -> tuple[str, str, str, str]:
        return (self.date, self.culture, self.condition, self.target_id)

    @property
    def condition_target_key(self) -> tuple[str, str]:
        return (self.condition, self.target_id)

    @property
    def date_culture_key(self) -> tuple[str, str]:
        return (self.date, self.culture)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AlignmentAuditRowV57:
    raw_source_file: str
    raw_date: str
    raw_culture: str
    raw_condition: str
    raw_target_id: str
    raw_recording_stem: str
    raw_representative_event_count: int
    raw_median_interval_s: float | None
    match_level: str
    matched_preprocessed_recording_path: str | None
    matched_preprocessed_pulse_count: int | None
    matched_preprocessed_median_interval_s: float | None
    first_event_to_first_pulse_delta_s: float | None
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RawPreprocessedAlignmentReportV57:
    version: str
    raw_event_csv: str
    pulse_metadata_csv: str
    overall_status: str
    raw_event_recording_count: int
    preprocessed_pulse_recording_count: int
    exact_recording_match_count: int
    date_culture_target_match_count: int
    condition_target_match_count: int
    temporal_signature_match_count: int
    date_culture_overlap_count: int
    shared_targets_by_condition: dict[str, list[str]]
    raw_interval_signatures_by_condition: dict[str, list[float]]
    preprocessed_interval_signatures_by_condition: dict[str, list[float]]
    raw_recordings: tuple[RawEventRecordingV57, ...]
    preprocessed_recordings: tuple[PreprocessedPulseRecordingV57, ...]
    audit_rows: tuple[AlignmentAuditRowV57, ...]
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _path_parts(path: str) -> list[str]:
    return [part for part in re.split(r"[\\/]+", str(path)) if part]


def _normalize_stem(value: str) -> str:
    stem = Path(value).stem
    stem = re.sub(r"_D-00144$", "", stem, flags=re.IGNORECASE)
    stem = stem.replace("LightStim_spot", "LightStim_Spot")
    return stem.lower()


def _extract_date(path: str) -> str:
    for part in _path_parts(path):
        if re.match(r"\d{2}-\d{2}-\d{4}$", part):
            return part
    return ""


def _extract_culture(path: str) -> str:
    for part in _path_parts(path):
        match = re.match(r"(.+?_\d+DIV)", part, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_target_id(path: str) -> str:
    match = re.search(r"(?:LightStim[_-]*Spot|Spot|ElecStim|Stim|stim)(\d+)", path, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _condition_from_candidate(candidate_kind: str, source_file: str) -> str:
    lower = f"{candidate_kind} {source_file}".lower()
    if "light" in lower or "spot" in lower or "digital" in lower:
        return "lightstim"
    if "electrical" in lower or "elecstim" in lower or "stim" in lower:
        return "elecstim"
    return "unknown"


def _float_or_none(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _int_or_zero(value: Any) -> int:
    try:
        return int(float(str(value or "0").strip()))
    except ValueError:
        return 0


def _median(values: list[float]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(float(statistics.median(clean)), 6)


def _median_interval(values: list[float]) -> float | None:
    ordered = sorted(values)
    deltas = [later - earlier for earlier, later in zip(ordered, ordered[1:]) if later >= earlier]
    return _median(deltas)


def load_raw_event_recordings_v57(path: str | Path = DEFAULT_RAW_EVENT_CANDIDATES) -> tuple[RawEventRecordingV57, ...]:
    csv_path = Path(path)
    if not csv_path.exists():
        return tuple()
    groups: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_file = row.get("file", "")
            condition = _condition_from_candidate(row.get("candidate_kind", ""), source_file)
            target_id = _extract_target_id(source_file)
            recording_stem = _normalize_stem(_path_parts(source_file)[-1] if _path_parts(source_file) else source_file)
            key = (_extract_date(source_file), _extract_culture(source_file), condition, target_id, recording_stem)
            bucket = groups.setdefault(
                key,
                {
                    "source_file": source_file,
                    "event_counts": [],
                    "first_values": [],
                    "last_values": [],
                    "median_intervals": [],
                    "candidate_kinds": set(),
                },
            )
            event_count = _int_or_zero(row.get("event_count"))
            bucket["event_counts"].append(event_count)
            first_value = _float_or_none(row.get("first_timestamp_s"))
            last_value = _float_or_none(row.get("last_timestamp_s"))
            median_interval = _float_or_none(row.get("median_interval_s"))
            if first_value is not None:
                bucket["first_values"].append(first_value)
            if last_value is not None:
                bucket["last_values"].append(last_value)
            if median_interval is not None:
                bucket["median_intervals"].append(median_interval)
            bucket["candidate_kinds"].add(row.get("candidate_kind", ""))

    recordings: list[RawEventRecordingV57] = []
    for key, bucket in sorted(groups.items()):
        date, culture, condition, target_id, recording_stem = key
        event_counts = [int(value) for value in bucket["event_counts"]]
        recordings.append(
            RawEventRecordingV57(
                source_file=str(bucket["source_file"]),
                date=date,
                culture=culture,
                condition=condition,
                target_id=target_id,
                recording_stem=recording_stem,
                event_entity_count=len(event_counts),
                representative_event_count=max(event_counts) if event_counts else 0,
                total_event_timestamps=sum(event_counts),
                first_event_s=min(bucket["first_values"]) if bucket["first_values"] else None,
                last_event_s=max(bucket["last_values"]) if bucket["last_values"] else None,
                median_interval_s=_median(bucket["median_intervals"]),
                candidate_kinds=tuple(sorted(kind for kind in bucket["candidate_kinds"] if kind)),
            )
        )
    return tuple(recordings)


def load_preprocessed_pulse_recordings_v57(path: str | Path = DEFAULT_PULSE_METADATA) -> tuple[PreprocessedPulseRecordingV57, ...]:
    csv_path = Path(path)
    if not csv_path.exists():
        return tuple()
    groups: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            recording_path = row.get("recording_path", "")
            recording_stem = _normalize_stem(_path_parts(recording_path)[-1] if _path_parts(recording_path) else recording_path)
            date = row.get("date", "") or _extract_date(recording_path)
            culture = row.get("culture", "") or _extract_culture(recording_path)
            condition = (row.get("condition", "") or "unknown").lower()
            target_id = str(row.get("target_id", "") or "")
            key = (date, culture, condition, target_id, recording_stem)
            bucket = groups.setdefault(
                key,
                {
                    "recording_path": recording_path,
                    "starts": [],
                    "durations": [],
                },
            )
            start_s = _float_or_none(row.get("start_s"))
            duration_s = _float_or_none(row.get("duration_s"))
            if start_s is not None:
                bucket["starts"].append(start_s)
            if duration_s is not None:
                bucket["durations"].append(duration_s)

    recordings: list[PreprocessedPulseRecordingV57] = []
    for key, bucket in sorted(groups.items()):
        date, culture, condition, target_id, recording_stem = key
        starts = [float(value) for value in bucket["starts"]]
        recordings.append(
            PreprocessedPulseRecordingV57(
                recording_path=str(bucket["recording_path"]),
                date=date,
                culture=culture,
                condition=condition,
                target_id=target_id,
                recording_stem=recording_stem,
                pulse_count=len(starts),
                first_start_s=min(starts) if starts else None,
                last_start_s=max(starts) if starts else None,
                median_interval_s=_median_interval(starts),
                median_duration_s=_median(bucket["durations"]),
            )
        )
    return tuple(recordings)


def _intervals_by_condition(recordings: tuple[RawEventRecordingV57, ...] | tuple[PreprocessedPulseRecordingV57, ...]) -> dict[str, list[float]]:
    values: dict[str, set[float]] = {}
    for recording in recordings:
        interval = recording.median_interval_s
        if interval is None:
            continue
        values.setdefault(recording.condition, set()).add(round(float(interval), 6))
    return {condition: sorted(intervals) for condition, intervals in sorted(values.items())}


def _shared_targets(
    raw_recordings: tuple[RawEventRecordingV57, ...],
    preprocessed_recordings: tuple[PreprocessedPulseRecordingV57, ...],
) -> dict[str, list[str]]:
    raw_targets: dict[str, set[str]] = {}
    pre_targets: dict[str, set[str]] = {}
    for recording in raw_recordings:
        if recording.target_id:
            raw_targets.setdefault(recording.condition, set()).add(recording.target_id)
    for recording in preprocessed_recordings:
        if recording.target_id:
            pre_targets.setdefault(recording.condition, set()).add(recording.target_id)
    shared: dict[str, list[str]] = {}
    for condition in sorted(set(raw_targets) | set(pre_targets)):
        overlap = raw_targets.get(condition, set()) & pre_targets.get(condition, set())
        if overlap:
            shared[condition] = sorted(overlap, key=lambda value: int(value) if value.isdigit() else value)
    return shared


def _interval_matches(raw_interval: float | None, pre_interval: float | None, tolerance_s: float) -> bool:
    if raw_interval is None or pre_interval is None:
        return False
    return abs(float(raw_interval) - float(pre_interval)) <= float(tolerance_s)


def _build_audit_rows(
    raw_recordings: tuple[RawEventRecordingV57, ...],
    preprocessed_recordings: tuple[PreprocessedPulseRecordingV57, ...],
    tolerance_s: float,
) -> tuple[AlignmentAuditRowV57, ...]:
    exact_map = {recording.exact_key: recording for recording in preprocessed_recordings}
    date_culture_target_map: dict[tuple[str, str, str, str], PreprocessedPulseRecordingV57] = {}
    condition_target_map: dict[tuple[str, str], PreprocessedPulseRecordingV57] = {}
    date_culture_map: dict[tuple[str, str], PreprocessedPulseRecordingV57] = {}
    by_condition: dict[str, list[PreprocessedPulseRecordingV57]] = {}
    for recording in preprocessed_recordings:
        date_culture_target_map.setdefault(recording.date_culture_target_key, recording)
        condition_target_map.setdefault(recording.condition_target_key, recording)
        date_culture_map.setdefault(recording.date_culture_key, recording)
        by_condition.setdefault(recording.condition, []).append(recording)

    rows: list[AlignmentAuditRowV57] = []
    for raw_recording in raw_recordings:
        match_level = "no_alignment"
        matched: PreprocessedPulseRecordingV57 | None = None
        note = "No exact, target or temporal-signature match found in current preprocessed pulse metadata."
        if raw_recording.exact_key in exact_map:
            match_level = "exact_recording"
            matched = exact_map[raw_recording.exact_key]
            note = "Raw event recording and preprocessed pulse recording share date, culture, condition, target and recording stem."
        elif raw_recording.date_culture_target_key in date_culture_target_map:
            match_level = "date_culture_target"
            matched = date_culture_target_map[raw_recording.date_culture_target_key]
            note = "Raw and preprocessed records share date, culture, condition and target, but recording stems differ."
        elif raw_recording.condition_target_key in condition_target_map:
            match_level = "condition_target"
            matched = condition_target_map[raw_recording.condition_target_key]
            note = "Raw and preprocessed records share condition and target only; not an exact recording-level raw source."
        else:
            for candidate in by_condition.get(raw_recording.condition, []):
                if _interval_matches(raw_recording.median_interval_s, candidate.median_interval_s, tolerance_s):
                    match_level = "temporal_signature"
                    matched = candidate
                    note = "Raw EventStream cadence matches a preprocessed protocol cadence by condition only; this is not raw equivalence."
                    break
            if matched is None and raw_recording.date_culture_key in date_culture_map:
                match_level = "date_culture_only"
                matched = date_culture_map[raw_recording.date_culture_key]
                note = "Raw and preprocessed records share date/culture only; target or condition coverage differs."

        delta = None
        if raw_recording.first_event_s is not None and matched is not None and matched.first_start_s is not None:
            delta = round(float(raw_recording.first_event_s) - float(matched.first_start_s), 6)
        rows.append(
            AlignmentAuditRowV57(
                raw_source_file=raw_recording.source_file,
                raw_date=raw_recording.date,
                raw_culture=raw_recording.culture,
                raw_condition=raw_recording.condition,
                raw_target_id=raw_recording.target_id,
                raw_recording_stem=raw_recording.recording_stem,
                raw_representative_event_count=raw_recording.representative_event_count,
                raw_median_interval_s=raw_recording.median_interval_s,
                match_level=match_level,
                matched_preprocessed_recording_path=matched.recording_path if matched else None,
                matched_preprocessed_pulse_count=matched.pulse_count if matched else None,
                matched_preprocessed_median_interval_s=matched.median_interval_s if matched else None,
                first_event_to_first_pulse_delta_s=delta,
                note=note,
            )
        )
    return tuple(rows)


def _count_temporal_signature_matches(
    raw_recordings: tuple[RawEventRecordingV57, ...],
    preprocessed_recordings: tuple[PreprocessedPulseRecordingV57, ...],
    tolerance_s: float,
) -> int:
    by_condition: dict[str, list[PreprocessedPulseRecordingV57]] = {}
    for recording in preprocessed_recordings:
        by_condition.setdefault(recording.condition, []).append(recording)
    count = 0
    for raw_recording in raw_recordings:
        if any(
            _interval_matches(raw_recording.median_interval_s, candidate.median_interval_s, tolerance_s)
            for candidate in by_condition.get(raw_recording.condition, [])
        ):
            count += 1
    return count


def build_raw_preprocessed_alignment_report_v57(
    raw_event_csv: str | Path = DEFAULT_RAW_EVENT_CANDIDATES,
    pulse_metadata_csv: str | Path = DEFAULT_PULSE_METADATA,
    interval_tolerance_s: float = 0.02,
) -> RawPreprocessedAlignmentReportV57:
    raw_recordings = load_raw_event_recordings_v57(raw_event_csv)
    preprocessed_recordings = load_preprocessed_pulse_recordings_v57(pulse_metadata_csv)
    audit_rows = _build_audit_rows(raw_recordings, preprocessed_recordings, interval_tolerance_s)
    exact_count = sum(1 for row in audit_rows if row.match_level == "exact_recording")
    date_culture_target_count = sum(1 for row in audit_rows if row.match_level == "date_culture_target")
    condition_target_count = sum(1 for row in audit_rows if row.match_level == "condition_target")
    temporal_count = _count_temporal_signature_matches(raw_recordings, preprocessed_recordings, interval_tolerance_s)
    raw_date_cultures = {recording.date_culture_key for recording in raw_recordings}
    pre_date_cultures = {recording.date_culture_key for recording in preprocessed_recordings}
    date_culture_overlap_count = len(raw_date_cultures & pre_date_cultures)
    if not raw_recordings and not preprocessed_recordings:
        status = "missing_inputs"
    elif not raw_recordings or not preprocessed_recordings:
        status = "partial_inputs"
    elif exact_count > 0:
        status = "exact_recording_alignment_available"
    elif condition_target_count > 0 and temporal_count > 0:
        status = "target_and_temporal_signature_only"
    elif temporal_count > 0:
        status = "class_temporal_signature_only"
    else:
        status = "raw_and_preprocessed_present_no_exact_overlap"
    return RawPreprocessedAlignmentReportV57(
        version="v5.7",
        raw_event_csv=str(raw_event_csv),
        pulse_metadata_csv=str(pulse_metadata_csv),
        overall_status=status,
        raw_event_recording_count=len(raw_recordings),
        preprocessed_pulse_recording_count=len(preprocessed_recordings),
        exact_recording_match_count=exact_count,
        date_culture_target_match_count=date_culture_target_count,
        condition_target_match_count=condition_target_count,
        temporal_signature_match_count=temporal_count,
        date_culture_overlap_count=date_culture_overlap_count,
        shared_targets_by_condition=_shared_targets(raw_recordings, preprocessed_recordings),
        raw_interval_signatures_by_condition=_intervals_by_condition(raw_recordings),
        preprocessed_interval_signatures_by_condition=_intervals_by_condition(preprocessed_recordings),
        raw_recordings=raw_recordings,
        preprocessed_recordings=preprocessed_recordings,
        audit_rows=audit_rows,
        claim_boundary="coverage/alignment audit only; no raw equivalence claim unless exact recording matches are present and waveform-derived features are rebuilt",
    )


def write_raw_preprocessed_alignment_outputs_v57(
    report: RawPreprocessedAlignmentReportV57,
    out_dir: str | Path,
) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary_json": out / "V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json",
        "raw_recordings_csv": out / "V57_RAW_EVENT_RECORDINGS.csv",
        "preprocessed_recordings_csv": out / "V57_PREPROCESSED_PULSE_RECORDINGS.csv",
        "alignment_audit_csv": out / "V57_RAW_PREPROCESSED_ALIGNMENT_AUDIT.csv",
        "markdown_report": out / "BIOGPU_V57_RAW_PREPROCESSED_ALIGNMENT_REPORT.md",
    }
    summary = {
        "version": report.version,
        "overall_status": report.overall_status,
        "raw_event_recording_count": report.raw_event_recording_count,
        "preprocessed_pulse_recording_count": report.preprocessed_pulse_recording_count,
        "exact_recording_match_count": report.exact_recording_match_count,
        "date_culture_target_match_count": report.date_culture_target_match_count,
        "condition_target_match_count": report.condition_target_match_count,
        "temporal_signature_match_count": report.temporal_signature_match_count,
        "date_culture_overlap_count": report.date_culture_overlap_count,
        "shared_targets_by_condition": report.shared_targets_by_condition,
        "raw_interval_signatures_by_condition": report.raw_interval_signatures_by_condition,
        "preprocessed_interval_signatures_by_condition": report.preprocessed_interval_signatures_by_condition,
        "claim_boundary": report.claim_boundary,
    }
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_dataclass_csv(paths["raw_recordings_csv"], [recording.to_dict() for recording in report.raw_recordings])
    _write_dataclass_csv(paths["preprocessed_recordings_csv"], [recording.to_dict() for recording in report.preprocessed_recordings])
    _write_dataclass_csv(paths["alignment_audit_csv"], [row.to_dict() for row in report.audit_rows])
    paths["markdown_report"].write_text(_markdown_report(report, summary), encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _write_dataclass_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(value) for key, value in row.items()})


def _csv_value(value: Any) -> Any:
    if isinstance(value, (tuple, list)):
        return ";".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return value


def _markdown_report(report: RawPreprocessedAlignmentReportV57, summary: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.7 Raw vs Preprocessed Alignment Audit",
        "",
        "## Summary",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Raw event recordings: `{summary['raw_event_recording_count']}`",
        f"- Preprocessed pulse recordings: `{summary['preprocessed_pulse_recording_count']}`",
        f"- Exact recording matches: `{summary['exact_recording_match_count']}`",
        f"- Date/culture/target matches: `{summary['date_culture_target_match_count']}`",
        f"- Condition/target matches: `{summary['condition_target_match_count']}`",
        f"- Temporal signature matches: `{summary['temporal_signature_match_count']}`",
        f"- Shared targets by condition: `{summary['shared_targets_by_condition']}`",
        "",
        "## Interpretation",
        "",
        "This audit compares embedded raw HDF5 EventStream candidates from v5.6 with the preprocessed v15 pulse-window metadata used by the PC validation path. Exact recording matches are required before claiming raw-to-feature reconstruction for the benchmark rows.",
        "",
        "## Claim Boundary",
        "",
        report.claim_boundary,
        "",
        "## First Raw Alignment Rows",
        "",
    ]
    for row in report.audit_rows[:20]:
        lines.append(
            f"- `{row.raw_source_file}`: `{row.match_level}`, raw_interval={row.raw_median_interval_s}, "
            f"matched=`{row.matched_preprocessed_recording_path}`"
        )
    lines.append("")
    return "\n".join(lines)
