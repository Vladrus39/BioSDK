"""BioGPU Core v2.0 — Master pipeline runner.

One function to rule them all:
  run_pipeline(dataset_path, mode="replay") -> EvidenceBundle

Modes:
  - "replay": standard batch classification
  - "baseline": compare BioGPU vs logreg/RF/SVM
  - "ablation": drop feature groups, measure impact
  - "cross_vendor": MEA from different vendors
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.core.ingest.loader_v2 import load_dataset, detect_format
from biogpu.core.features.extractor_v2 import (
    extract_features, FEATURE_GROUPS, FEATURE_NAMES,
)
from biogpu.core.readout.classifier_v2 import run_baselines, run_ablation, ReadoutResult
from biogpu.core.evidence.bundle_v2 import EvidenceBundle, create_bundle, save_bundle


def run_pipeline(
    dataset_path: str | Path,
    mode: str = "replay",
    output_dir: str | Path = "outputs/v2_baselines",
    window_seconds: float = 1.0,
    n_folds: int = 5,
) -> dict[str, Any]:
    """Master pipeline: ingest -> features -> readout -> evidence.

    Args:
        dataset_path: path to data file
        mode: "replay", "baseline", "ablation"
        output_dir: where to save evidence bundles
        window_seconds: sliding window size
        n_folds: cross-validation folds

    Returns:
        dict with summary and evidence bundle path
    """
    print(f"\n{'='*60}")
    print(f"BioGPU Core v2.0 | {mode} | {Path(dataset_path).name}")
    print(f"{'='*60}")

    # 1. Ingest
    print("[ingest] Loading...")
    ingested = load_dataset(dataset_path)
    if ingested.errors:
        print(f"  Warnings: {ingested.errors}")
    if ingested.data is None:
        print("  ERROR: No data loaded")
        return {"status": "error", "errors": ingested.errors}
    print(f"  Format: {ingested.format}, channels={ingested.channel_count}, samples={ingested.sample_count}, rate={ingested.sample_rate_hz:.0f} Hz")

    # 2. Features
    print("[features] Extracting...")
    feats = extract_features(
        ingested.data,
        sample_rate_hz=max(ingested.sample_rate_hz, 100.0),
        window_size_seconds=window_seconds,
        window_overlap=0.5,
    )
    print(f"  Windows: {feats.n_windows}, features: {feats.features.shape[1]}")

    # 3. Labels — generate or use existing
    if ingested.labels is not None and len(ingested.labels) >= feats.n_windows:
        labels = ingested.labels[:feats.n_windows]
    else:
        # Synthetic labels for unsupervised data
        n_classes = min(4, max(2, feats.n_windows // 10))
        labels = np.array([i % n_classes for i in range(feats.n_windows)])
        print(f"  Using synthetic {n_classes}-class labels (unsupervised data)")

    # 4. Readout
    print(f"[readout] Running {n_folds}-fold CV...")
    readout_results = run_baselines(feats.features, labels, n_folds)

    print("  Results:")
    for name, res in readout_results.items():
        above = "ABOVE" if res.above_chance else "below"
        print(f"    {name:20s}: {res.accuracy:.4f} +/- {res.accuracy_std:.4f}  [{above} chance={res.chance_level:.3f}]")

    # 5. Ablation (if mode supports it)
    ablation_results = {}
    if mode in ("ablation",):
        print("[ablation] Dropping feature groups...")
        # Build feature group indices
        group_indices = {}
        idx = 0
        for gname, gfeats in FEATURE_GROUPS.items():
            group_indices[gname] = list(range(idx, idx + len(gfeats)))
            idx += len(gfeats)
        ablation_results = run_ablation(feats.features, labels, group_indices, n_folds)

        print("  Ablation impact (MLP accuracy drop):")
        full_acc = readout_results["mlp"].accuracy
        for gname in FEATURE_GROUPS:
            if f"drop_{gname}" in ablation_results and "mlp" in ablation_results[f"drop_{gname}"]:
                drop_acc = ablation_results[f"drop_{gname}"]["mlp"].accuracy
                delta = full_acc - drop_acc
                print(f"    drop_{gname:20s}: {drop_acc:.4f} (delta={delta:+.4f})")

    # 6. Evidence bundle
    print("[evidence] Creating bundle...")
    readout_dict = {}
    for name, res in readout_results.items():
        readout_dict[name] = {
            "accuracy": res.accuracy,
            "accuracy_std": res.accuracy_std,
            "above_chance": res.above_chance,
            "chance_level": res.chance_level,
            "n_samples": res.n_samples,
            "n_classes": res.n_classes,
        }

    ablation_dict = {}
    for k, v in ablation_results.items():
        ablation_dict[k] = {}
        for dec, res in v.items():
            ablation_dict[k][dec] = {"accuracy": res.accuracy, "above_chance": res.above_chance}

    bundle = create_bundle(
        dataset_path=str(dataset_path),
        dataset_sha256=ingested.sha256,
        mode=mode,
        feature_count=feats.features.shape[1],
        window_count=feats.n_windows,
        readout_results=readout_dict,
        ablation_results=ablation_dict,
        metadata={
            "format": ingested.format,
            "channels": ingested.channel_count,
            "samples": ingested.sample_count,
            "sample_rate": ingested.sample_rate_hz,
            "duration_seconds": ingested.duration_seconds,
            "load_time_ms": ingested.load_time_ms,
            "feature_groups": FEATURE_GROUPS,
        },
    )

    bundle_path = save_bundle(bundle, output_dir)
    print(f"  Bundle: {bundle_path}")
    print(f"  SHA256: {bundle.sha256[:16]}...")

    return {
        "status": "ok",
        "mode": mode,
        "dataset": Path(dataset_path).name,
        "format": ingested.format,
        "windows": feats.n_windows,
        "features": feats.features.shape[1],
        "best_accuracy": bundle.best_accuracy,
        "best_decoder": bundle.best_decoder,
        "chance_level": bundle.chance_level,
        "baseline_comparison": bundle.baseline_comparison,
        "bundle_sha256": bundle.sha256,
        "bundle_path": str(bundle_path),
    }
