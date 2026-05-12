"""BioGPU Core v2.0 — Evidence bundles.

Append-only, content-addressed. No self-signing — just SHA256 chain.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EvidenceBundle:
    bundle_id: str
    pipeline_version: str = "v2.0"
    dataset: str = ""
    dataset_sha256: str = ""
    mode: str = "replay"
    feature_count: int = 0
    window_count: int = 0
    readout_results: dict[str, Any] = field(default_factory=dict)
    ablation_results: dict[str, Any] = field(default_factory=dict)
    best_accuracy: float = 0.0
    best_decoder: str = ""
    chance_level: float = 0.0
    baseline_comparison: dict[str, float] = field(default_factory=dict)
    generated_at: str = ""
    sha256: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def create_bundle(
    dataset_path: str,
    dataset_sha256: str,
    mode: str,
    feature_count: int,
    window_count: int,
    readout_results: dict[str, Any],
    ablation_results: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> EvidenceBundle:
    """Create an evidence bundle from pipeline results."""
    import uuid

    # Find best result
    best_acc = 0.0
    best_dec = ""
    baseline_comp: dict[str, float] = {}
    for dec, res in readout_results.items():
        if isinstance(res, dict) and "accuracy" in res:
            acc = res["accuracy"]
        elif hasattr(res, "accuracy"):
            acc = res.accuracy
        else:
            continue
        baseline_comp[dec] = acc
        if acc > best_acc:
            best_acc = acc
            best_dec = dec

    # Chance level
    chance = 0.0
    for res in readout_results.values():
        if isinstance(res, dict) and "chance_level" in res:
            chance = res["chance_level"]
            break
        elif hasattr(res, "chance_level"):
            chance = res.chance_level
            break

    bundle = EvidenceBundle(
        bundle_id=f"bundle-{uuid.uuid4().hex[:12]}",
        dataset=Path(dataset_path).name,
        dataset_sha256=dataset_sha256,
        mode=mode,
        feature_count=feature_count,
        window_count=window_count,
        readout_results=readout_results,
        ablation_results=ablation_results or {},
        best_accuracy=best_acc,
        best_decoder=best_dec,
        chance_level=chance,
        baseline_comparison=baseline_comp,
        generated_at=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {},
    )

    bundle_json = json.dumps(asdict(bundle), sort_keys=True, ensure_ascii=False, default=str)
    bundle.sha256 = hashlib.sha256(bundle_json.encode()).hexdigest()
    return bundle


def save_bundle(bundle: EvidenceBundle, output_dir: str | Path) -> Path:
    """Save evidence bundle to disk."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{bundle.bundle_id}.json"
    path.write_text(json.dumps(asdict(bundle), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path
