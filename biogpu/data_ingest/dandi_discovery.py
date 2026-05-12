from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import json
from pathlib import Path


@dataclass(frozen=True)
class DandiCandidate:
    dandiset_id: str
    name: str
    modality: str
    has_units: bool
    has_stimulus_or_behavior: bool
    why_relevant: str
    download_hint: str
    trust_level: str = "candidate"


def curated_candidates() -> list[DandiCandidate]:
    """Small curated starter list for task-aligned public-data work.

    This is intentionally conservative. Full DANDI discovery should use the
    dandi CLI/API online, but the repo can ship a stable starter manifest.
    """
    return [
        DandiCandidate(
            dandiset_id="000469",
            name="Human single-neuron activity during a Sternberg working memory task",
            modality="extracellular single-unit/ecephys NWB",
            has_units=True,
            has_stimulus_or_behavior=True,
            why_relevant="Contains spike times, stimuli, behavior, and working-memory task structure; useful for task-aligned window mapping, not MEA reservoir claims.",
            download_hint="dandi download https://dandiarchive.org/dandiset/000469",
            trust_level="strong public NWB task dataset",
        ),
        DandiCandidate(
            dandiset_id="000673",
            name="Human hippocampal working-memory intracranial dataset referenced by ripple-working-memory resources",
            modality="intracranial ecephys/LFP/single-unit NWB candidate",
            has_units=True,
            has_stimulus_or_behavior=True,
            why_relevant="Potential temporal-memory benchmark source if NWB interval/task metadata can be mapped.",
            download_hint="dandi download https://dandiarchive.org/dandiset/000673",
            trust_level="candidate pending local inspection",
        ),
    ]


def candidates_as_dict() -> list[dict[str, Any]]:
    return [asdict(c) for c in curated_candidates()]


def write_candidate_manifest(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"candidates": candidates_as_dict()}, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def keyword_score(metadata: dict[str, Any], keywords: list[str] | None = None) -> int:
    keys = keywords or ["ecephys", "units", "spike", "stimulus", "behavior", "NWB", "extracellular", "task"]
    blob = json.dumps(metadata, ensure_ascii=False).lower()
    return sum(1 for k in keys if k.lower() in blob)
