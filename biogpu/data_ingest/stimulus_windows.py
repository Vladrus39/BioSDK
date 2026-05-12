from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import csv
import json

from biogpu.schemas import SpikeTrain


@dataclass(frozen=True)
class StimulusWindow:
    """A stimulus-response window for task-aligned real spike data.

    This object is deliberately generic. Real datasets encode stimulus tables in
    different ways (NWB intervals, CSV event logs, MATLAB exports, lab metadata).
    BioGPU maps them into this neutral representation before extracting features.
    """

    start_s: float
    end_s: float
    label: str | int | float | None = None
    stimulus_id: str | None = None
    split: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_s(self) -> float:
        return max(0.0, float(self.end_s) - float(self.start_s))


def read_stimulus_windows_csv(path: str | Path) -> list[StimulusWindow]:
    """Read windows from CSV.

    Required columns: start_s,end_s. Optional: label,stimulus_id,split and any
    extra metadata columns.
    """
    p = Path(path)
    windows: list[StimulusWindow] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Empty stimulus window CSV: {p}")
        missing = {"start_s", "end_s"} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Stimulus window CSV missing required columns: {sorted(missing)}")
        for row in reader:
            metadata = {k: v for k, v in row.items() if k not in {"start_s", "end_s", "label", "stimulus_id", "split"}}
            label: str | int | float | None = row.get("label")
            # keep labels as strings unless they are clearly numeric
            if label is not None and label != "":
                try:
                    if "." in str(label):
                        label = float(label)
                    else:
                        label = int(label)
                except ValueError:
                    pass
            else:
                label = None
            windows.append(
                StimulusWindow(
                    start_s=float(row["start_s"]),
                    end_s=float(row["end_s"]),
                    label=label,
                    stimulus_id=row.get("stimulus_id") or None,
                    split=row.get("split") or None,
                    metadata=metadata,
                )
            )
    return windows


def write_stimulus_windows_csv(windows: Iterable[StimulusWindow], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    extra_keys: set[str] = set()
    for w in windows:
        extra_keys.update(w.metadata.keys())
        rows.append(w)
    fieldnames = ["start_s", "end_s", "label", "stimulus_id", "split"] + sorted(extra_keys)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for w in rows:
            row = {
                "start_s": w.start_s,
                "end_s": w.end_s,
                "label": w.label,
                "stimulus_id": w.stimulus_id,
                "split": w.split,
            }
            row.update(w.metadata)
            writer.writerow(row)
    return p


def read_stimulus_windows_json(path: str | Path) -> list[StimulusWindow]:
    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("windows", [])
    windows = []
    for item in payload:
        metadata = dict(item.get("metadata", {}))
        for k, v in item.items():
            if k not in {"start_s", "end_s", "label", "stimulus_id", "split", "metadata"}:
                metadata[k] = v
        windows.append(
            StimulusWindow(
                start_s=float(item["start_s"]),
                end_s=float(item["end_s"]),
                label=item.get("label"),
                stimulus_id=item.get("stimulus_id"),
                split=item.get("split"),
                metadata=metadata,
            )
        )
    return windows


def slice_spikes_to_window(spikes: SpikeTrain, window: StimulusWindow, relative_times: bool = True) -> SpikeTrain:
    units: list[int] = []
    times: list[float] = []
    for unit_id, t in zip(spikes.unit_ids, spikes.spike_times):
        tt = float(t)
        if float(window.start_s) <= tt < float(window.end_s):
            units.append(int(unit_id))
            times.append(tt - float(window.start_s) if relative_times else tt)
    return SpikeTrain(
        units,
        times,
        metadata={
            "source": "stimulus_window_slice",
            "window_start_s": window.start_s,
            "window_end_s": window.end_s,
            "label": window.label,
            "stimulus_id": window.stimulus_id,
            "relative_times": relative_times,
        },
    )


def build_windowed_spiketrains(
    spikes: SpikeTrain, windows: Iterable[StimulusWindow], relative_times: bool = True
) -> tuple[list[SpikeTrain], list[Any], list[StimulusWindow]]:
    st_list: list[SpikeTrain] = []
    labels: list[Any] = []
    used_windows: list[StimulusWindow] = []
    for w in windows:
        if w.label is None:
            continue
        st = slice_spikes_to_window(spikes, w, relative_times=relative_times)
        st_list.append(st)
        labels.append(w.label)
        used_windows.append(w)
    return st_list, labels, used_windows


def summarize_windows(windows: Iterable[StimulusWindow]) -> dict[str, Any]:
    ws = list(windows)
    labels = [w.label for w in ws if w.label is not None]
    label_counts: dict[str, int] = {}
    for lab in labels:
        label_counts[str(lab)] = label_counts.get(str(lab), 0) + 1
    durations = [w.duration_s for w in ws]
    return {
        "window_count": len(ws),
        "labeled_window_count": len(labels),
        "label_counts": label_counts,
        "min_duration_s": min(durations) if durations else None,
        "max_duration_s": max(durations) if durations else None,
        "mean_duration_s": sum(durations) / len(durations) if durations else None,
    }
