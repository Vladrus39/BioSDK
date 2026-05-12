from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class BRCExperimentSpec:
    """Neutral spec for biological reservoir computing datasets.

    This does not assume a specific author file format. It captures the minimum
    contract BioGPU needs to reproduce BRC-style experiments: stimuli, response
    feature matrix or spike windows, labels, split, electrode maps and metadata.
    """

    source_name: str
    source_url: str | None = None
    stimulus_table: str | None = None
    spike_source: str | None = None
    response_feature_matrix: str | None = None
    label_column: str = "label"
    train_split_column: str | None = "split"
    stimulation_electrodes: list[int] = field(default_factory=list)
    recording_electrodes: list[int] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_brc_spec_template(path: str | Path) -> Path:
    spec = BRCExperimentSpec(
        source_name="BRC paper/data placeholder",
        source_url="https://arxiv.org/abs/2602.05737",
        stimulus_table="stimulus_windows.csv",
        spike_source="spikes.txt or session.nwb",
        response_feature_matrix="optional_precomputed_features.csv",
        notes="Fill this template once author data/code format is available.",
    )
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return p
