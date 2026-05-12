from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.analysis.zenodo_pulse_readout import (
    CandidateFeatureTable,
    PulseFeatureMatrix,
    PulseFeatureMetadata,
    build_candidate_target_table,
    build_pulse_feature_matrix,
    leave_one_culture_candidate_readout,
)
from biogpu.data_ingest.zenodo_protocol_windows import discover_protocol_windows, summarize_protocol_windows


FEATURE_SETS: dict[str, list[str]] = {
    "all_features": [
        "candidate_response_delta_count",
        "candidate_response_count",
        "candidate_pre_response_count",
        "candidate_exact_delta_count",
        "candidate_response_delta_percentile_within_pulse",
        "candidate_response_delta_zscore_within_pulse",
        "pulse_mean_response_delta_count",
        "pulse_max_response_delta_count",
    ],
    "raw_candidate_counts_only": [
        "candidate_response_delta_count",
        "candidate_response_count",
        "candidate_pre_response_count",
        "candidate_exact_delta_count",
    ],
    "post_minus_pre_delta_only": ["candidate_response_delta_count"],
    "exact_window_delta_only": ["candidate_exact_delta_count"],
    "within_pulse_rank_zscore_only": [
        "candidate_response_delta_percentile_within_pulse",
        "candidate_response_delta_zscore_within_pulse",
    ],
    "pulse_context_only_negative_control": [
        "pulse_mean_response_delta_count",
        "pulse_max_response_delta_count",
    ],
    "all_without_rank_zscore": [
        "candidate_response_delta_count",
        "candidate_response_count",
        "candidate_pre_response_count",
        "candidate_exact_delta_count",
        "pulse_mean_response_delta_count",
        "pulse_max_response_delta_count",
    ],
}


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _one_sided_high_p_value(observed: float, null_values: list[float]) -> float | None:
    clean = [float(v) for v in null_values if np.isfinite(v)]
    if not clean or not np.isfinite(observed):
        return None
    return float((1 + sum(v >= observed for v in clean)) / (len(clean) + 1))


def select_candidate_features(table: CandidateFeatureTable, feature_names: list[str]) -> CandidateFeatureTable:
    """Return a CandidateFeatureTable with only selected feature columns."""
    name_to_idx = {name: idx for idx, name in enumerate(table.feature_names)}
    missing = [name for name in feature_names if name not in name_to_idx]
    if missing:
        raise KeyError(f"Missing feature(s): {missing}")
    idx = [name_to_idx[name] for name in feature_names]
    return CandidateFeatureTable(
        X=table.X[:, idx].astype(np.float32, copy=False),
        y=table.y,
        culture=table.culture,
        metadata=table.metadata,
        feature_names=[table.feature_names[i] for i in idx],
    )


def bootstrap_fold_metric_ci(
    fold_rows: list[dict[str, Any]],
    metric: str = "roc_auc",
    n_bootstraps: int = 1000,
    seed: int = 123,
    ci: tuple[float, float] = (0.025, 0.975),
) -> dict[str, Any]:
    """Equal-culture bootstrap CI from leave-one-culture fold metrics.

    This intentionally resamples folds/cultures rather than individual candidate rows so the
    uncertainty estimate is less dominated by cultures with many pulse windows.
    """
    values = np.asarray([float(r[metric]) for r in fold_rows if r.get(metric) is not None and np.isfinite(float(r[metric]))], dtype=float)
    if len(values) == 0:
        return {
            "metric": metric,
            "n_cultures_with_metric": 0,
            "mean": None,
            "median": None,
            "ci_low": None,
            "ci_high": None,
            "n_bootstraps": int(n_bootstraps),
        }
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(max(1, int(n_bootstraps))):
        sample = rng.choice(values, size=len(values), replace=True)
        boots.append(float(np.mean(sample)))
    q_low, q_high = np.quantile(np.asarray(boots, dtype=float), ci)
    return {
        "metric": metric,
        "n_cultures_with_metric": int(len(values)),
        "fold_mean": float(np.mean(values)),
        "fold_median": float(np.median(values)),
        "ci_low": float(q_low),
        "ci_high": float(q_high),
        "n_bootstraps": int(max(1, int(n_bootstraps))),
        "ci": [float(ci[0]), float(ci[1])],
        "note": "CI bootstraps held-out culture folds with equal culture weight; it is a robustness interval, not a substitute for larger independent datasets.",
    }


def attach_bootstrap_cis(result: dict[str, Any], n_bootstraps: int = 1000, seed: int = 123) -> dict[str, Any]:
    folds = result.get("folds", [])
    out = dict(result)
    out["culture_bootstrap_ci"] = {
        "roc_auc": bootstrap_fold_metric_ci(folds, "roc_auc", n_bootstraps=n_bootstraps, seed=seed),
        "balanced_accuracy": bootstrap_fold_metric_ci(folds, "balanced_accuracy", n_bootstraps=n_bootstraps, seed=seed + 1),
        "accuracy": bootstrap_fold_metric_ci(folds, "accuracy", n_bootstraps=n_bootstraps, seed=seed + 2),
    }
    return out


def summarize_readout_no_rows(result: dict[str, Any]) -> dict[str, Any]:
    """Keep heavy fold/shuffle rows out of the top-level summary."""
    return {k: v for k, v in result.items() if k not in ("folds", "shuffle_rows")}


def run_negative_sweep(
    matrix: PulseFeatureMatrix,
    negative_counts: list[int],
    label_shuffles: int = 20,
    bootstrap_repeats: int = 1000,
    seed: int = 101,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    for idx, neg in enumerate(negative_counts):
        table = build_candidate_target_table(matrix, negative_per_pulse=int(neg), seed=seed + idx * 17)
        result = leave_one_culture_candidate_readout(table, n_label_shuffles=int(label_shuffles), seed=seed + idx * 17 + 1)
        result = attach_bootstrap_cis(result, n_bootstraps=int(bootstrap_repeats), seed=seed + idx * 17 + 2)
        observed = result.get("observed", {})
        baseline = result.get("label_shuffle_baseline", {})
        ci_auc = result.get("culture_bootstrap_ci", {}).get("roc_auc", {})
        row = {
            "negative_per_pulse": int(neg),
            "sample_count": int(result.get("sample_count", 0)),
            "pulse_count_used": int(result.get("pulse_count_used", 0)),
            "positive_fraction": float(result.get("positive_fraction", float("nan"))),
            "observed_roc_auc": observed.get("roc_auc"),
            "observed_balanced_accuracy": observed.get("balanced_accuracy"),
            "shuffle_roc_auc_median": baseline.get("roc_auc_median"),
            "shuffle_balanced_accuracy_median": baseline.get("balanced_accuracy_median"),
            "p_value_roc_auc_gt_shuffle": baseline.get("p_value_roc_auc_gt_shuffle"),
            "culture_bootstrap_auc_ci_low": ci_auc.get("ci_low"),
            "culture_bootstrap_auc_ci_high": ci_auc.get("ci_high"),
        }
        rows.append(row)
        details[f"negative_per_pulse_{int(neg)}"] = result
    return {"rows": rows, "details": details}


def run_feature_ablation(
    matrix: PulseFeatureMatrix,
    negative_per_pulse: int = 3,
    label_shuffles: int = 20,
    bootstrap_repeats: int = 1000,
    seed: int = 503,
) -> dict[str, Any]:
    base_table = build_candidate_target_table(matrix, negative_per_pulse=int(negative_per_pulse), seed=seed)
    rows: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    for idx, (name, features) in enumerate(FEATURE_SETS.items()):
        sub_table = select_candidate_features(base_table, features)
        result = leave_one_culture_candidate_readout(sub_table, n_label_shuffles=int(label_shuffles), seed=seed + 10 + idx)
        result = attach_bootstrap_cis(result, n_bootstraps=int(bootstrap_repeats), seed=seed + 100 + idx)
        observed = result.get("observed", {})
        baseline = result.get("label_shuffle_baseline", {})
        ci_auc = result.get("culture_bootstrap_ci", {}).get("roc_auc", {})
        rows.append(
            {
                "feature_set": name,
                "features": ";".join(features),
                "feature_count": int(len(features)),
                "negative_per_pulse": int(negative_per_pulse),
                "observed_roc_auc": observed.get("roc_auc"),
                "observed_balanced_accuracy": observed.get("balanced_accuracy"),
                "shuffle_roc_auc_median": baseline.get("roc_auc_median"),
                "shuffle_balanced_accuracy_median": baseline.get("balanced_accuracy_median"),
                "p_value_roc_auc_gt_shuffle": baseline.get("p_value_roc_auc_gt_shuffle"),
                "culture_bootstrap_auc_ci_low": ci_auc.get("ci_low"),
                "culture_bootstrap_auc_ci_high": ci_auc.get("ci_high"),
            }
        )
        details[name] = result
    rows.sort(key=lambda r: (float("-inf") if r.get("observed_roc_auc") is None else float(r["observed_roc_auc"])), reverse=True)
    return {"rows": rows, "details": details, "negative_per_pulse": int(negative_per_pulse)}


def _write_dict_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_v16_report(summary: dict[str, Any]) -> str:
    neg_lines = "\n".join(
        f"- negative_per_pulse={r['negative_per_pulse']}: ROC AUC={r.get('observed_roc_auc'):.5f}, "
        f"shuffle median={r.get('shuffle_roc_auc_median'):.5f}, p={r.get('p_value_roc_auc_gt_shuffle')}"
        for r in summary.get("negative_sweep", {}).get("rows", [])
        if r.get("observed_roc_auc") is not None and r.get("shuffle_roc_auc_median") is not None
    )
    abl_lines = "\n".join(
        f"- {r['feature_set']}: ROC AUC={r.get('observed_roc_auc'):.5f}, "
        f"shuffle median={r.get('shuffle_roc_auc_median'):.5f}, p={r.get('p_value_roc_auc_gt_shuffle')}"
        for r in summary.get("feature_ablation", {}).get("rows", [])
        if r.get("observed_roc_auc") is not None and r.get("shuffle_roc_auc_median") is not None
    )
    return f"""# Zenodo 14363732 — Pulse-level readout robustness v1.6

## Purpose

v1.6 strengthens the v1.5 pulse-level readout with three checks:

1. Multiple random negative electrodes per pulse.
2. Equal-culture bootstrap confidence intervals from leave-one-culture folds.
3. Feature-block ablation to see which spike-response features carry the separability.

## Negative-per-pulse sweep

{neg_lines or '- No rows produced.'}

## Feature ablation

{abl_lines or '- No rows produced.'}

## Full summary

```json
{_safe_json(summary)}
```

## Honesty rules

- This is still a real-data separability benchmark, not a claim that BioGPU outperforms a silicon GPU.
- The confidence intervals are culture-bootstrap intervals over held-out culture folds. They are more honest than row bootstrap, but still limited by only 18 cultures.
- Feature ablation is essential because within-pulse percentile/z-score features can make target-vs-random separation easier; raw-count-only results must be reported alongside all-feature results.
- Heavy experiments are listed in `docs/COMPUTE_BACKLOG.md` and `PROJECT_COMPUTE_BACKLOG_V16.md` so they are not lost.
"""


def write_v16_outputs(
    root_path: str | Path,
    out_dir: str | Path,
    response_window_ms: float = 100.0,
    negative_counts: list[int] | None = None,
    ablation_negative_per_pulse: int = 3,
    label_shuffles: int = 20,
    bootstrap_repeats: int = 1000,
    seed: int = 101,
) -> dict[str, Any]:
    negative_counts = [1, 3, 5] if negative_counts is None else [int(v) for v in negative_counts]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    windows = discover_protocol_windows(root_path)
    protocol_summary = summarize_protocol_windows(windows)
    matrix = build_pulse_feature_matrix(root_path, response_window_ms=response_window_ms)

    negative_sweep = run_negative_sweep(
        matrix,
        negative_counts=negative_counts,
        label_shuffles=int(label_shuffles),
        bootstrap_repeats=int(bootstrap_repeats),
        seed=seed,
    )
    feature_ablation = run_feature_ablation(
        matrix,
        negative_per_pulse=int(ablation_negative_per_pulse),
        label_shuffles=int(label_shuffles),
        bootstrap_repeats=int(bootstrap_repeats),
        seed=seed + 1000,
    )

    summary = {
        "task": "pulse_level_readout_robustness_v1_6",
        "protocol_summary": protocol_summary,
        "feature_matrix": {
            "pulse_count": int(matrix.X.shape[0]),
            "feature_count": int(matrix.X.shape[1]),
            "electrode_count": int(len(matrix.electrodes)),
            "response_window_ms": float(response_window_ms),
            "cultures": int(len(set(str(m.culture) for m in matrix.metadata))) if matrix.metadata else 0,
        },
        "parameters": {
            "negative_counts": negative_counts,
            "ablation_negative_per_pulse": int(ablation_negative_per_pulse),
            "label_shuffles": int(label_shuffles),
            "bootstrap_repeats": int(bootstrap_repeats),
            "seed": int(seed),
        },
        "negative_sweep": {
            "rows": negative_sweep["rows"],
            "interpretation": "Robustness check: true target vs more random non-target electrodes from the same pulse. AUC should stay above shuffled baseline as negatives increase.",
        },
        "feature_ablation": {
            "rows": feature_ablation["rows"],
            "interpretation": "Ablation check: report raw-count-only and rank/zscore-derived features separately to avoid overclaiming.",
        },
        "honesty_note": "v1.6 adds robustness evidence, not a final BioGPU advantage proof. Heavy external-data and larger permutation work is tracked in compute backlog files.",
    }

    (out / "v16_readout_robustness_summary.json").write_text(_safe_json(summary), encoding="utf-8")
    (out / "negative_sweep_details.json").write_text(_safe_json(negative_sweep["details"]), encoding="utf-8")
    (out / "feature_ablation_details.json").write_text(_safe_json(feature_ablation["details"]), encoding="utf-8")
    _write_dict_csv(negative_sweep["rows"], out / "negative_per_pulse_sweep.csv")
    _write_dict_csv(feature_ablation["rows"], out / "feature_ablation.csv")
    (out / "PULSE_LEVEL_READOUT_ROBUSTNESS_REPORT.md").write_text(render_v16_report(summary), encoding="utf-8")
    return summary


def load_pulse_feature_matrix_from_v15_outputs(v15_out_dir: str | Path) -> PulseFeatureMatrix:
    """Load a v1.5 pulse_feature_matrix.npz + pulse_feature_metadata.csv without reparsing spike CSV files."""
    base = Path(v15_out_dir)
    npz_path = base / "pulse_feature_matrix.npz"
    meta_path = base / "pulse_feature_metadata.csv"
    if not npz_path.exists():
        raise FileNotFoundError(f"Missing {npz_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path}")
    data = np.load(npz_path, allow_pickle=True)
    X = np.asarray(data["X"], dtype=np.float32)
    electrodes = [int(v) for v in np.asarray(data["electrodes"]).tolist()]
    feature_names = [str(v) for v in np.asarray(data["feature_names"], dtype=object).tolist()]
    response_window_ms = float(np.asarray(data["response_window_ms"]).ravel()[0]) if "response_window_ms" in data else 100.0
    metadata: list[PulseFeatureMetadata] = []
    with meta_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_raw = row.get("target_id", "")
            target_id = None if target_raw in ("", "None", None) else int(float(str(target_raw)))
            metadata.append(
                PulseFeatureMetadata(
                    row_index=int(float(row.get("row_index", len(metadata)))),
                    recording_path=str(row.get("recording_path", "")),
                    culture=str(row.get("culture", "")),
                    date=str(row.get("date", "")),
                    condition=str(row.get("condition", "")),
                    target_type=str(row.get("target_type", "")),
                    target_id=target_id,
                    pulse_index=int(float(row.get("pulse_index", 0))),
                    start_s=float(row.get("start_s", 0.0)),
                    end_s=float(row.get("end_s", 0.0)),
                    duration_s=float(row.get("duration_s", 0.0)),
                )
            )
    if len(metadata) != X.shape[0]:
        raise ValueError(f"Metadata row count {len(metadata)} does not match X rows {X.shape[0]}")
    return PulseFeatureMatrix(
        X=X,
        metadata=metadata,
        electrodes=electrodes,
        feature_names=feature_names,
        response_window_ms=response_window_ms,
    )


def write_v16_outputs_from_v15_matrix(
    v15_out_dir: str | Path,
    out_dir: str | Path,
    negative_counts: list[int] | None = None,
    ablation_negative_per_pulse: int = 3,
    label_shuffles: int = 20,
    bootstrap_repeats: int = 1000,
    seed: int = 101,
) -> dict[str, Any]:
    """Run v1.6 from the saved v1.5 matrix, avoiding expensive raw spike CSV reparsing."""
    negative_counts = [1, 3, 5] if negative_counts is None else [int(v) for v in negative_counts]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    matrix = load_pulse_feature_matrix_from_v15_outputs(v15_out_dir)
    conditions = [m.condition for m in matrix.metadata]
    targets = [m.target_id for m in matrix.metadata if m.target_id is not None]

    negative_sweep = run_negative_sweep(
        matrix,
        negative_counts=negative_counts,
        label_shuffles=int(label_shuffles),
        bootstrap_repeats=int(bootstrap_repeats),
        seed=seed,
    )
    feature_ablation = run_feature_ablation(
        matrix,
        negative_per_pulse=int(ablation_negative_per_pulse),
        label_shuffles=int(label_shuffles),
        bootstrap_repeats=int(bootstrap_repeats),
        seed=seed + 1000,
    )

    summary = {
        "task": "pulse_level_readout_robustness_v1_6_from_v15_matrix",
        "input": {
            "v15_out_dir": str(v15_out_dir),
            "note": "Fast-path used saved v1.5 pulse feature matrix; no raw spike CSV reparse was needed.",
        },
        "feature_matrix": {
            "pulse_count": int(matrix.X.shape[0]),
            "feature_count": int(matrix.X.shape[1]),
            "electrode_count": int(len(matrix.electrodes)),
            "response_window_ms": float(matrix.response_window_ms),
            "cultures": int(len(set(str(m.culture) for m in matrix.metadata))) if matrix.metadata else 0,
            "conditions": {str(k): int(v) for k, v in zip(*np.unique(np.asarray(conditions, dtype=object), return_counts=True))},
            "target_class_count": int(len(set(int(v) for v in targets))),
        },
        "parameters": {
            "negative_counts": negative_counts,
            "ablation_negative_per_pulse": int(ablation_negative_per_pulse),
            "label_shuffles": int(label_shuffles),
            "bootstrap_repeats": int(bootstrap_repeats),
            "seed": int(seed),
        },
        "negative_sweep": {
            "rows": negative_sweep["rows"],
            "interpretation": "Robustness check: true target vs more random non-target electrodes from the same pulse. AUC should stay above shuffled baseline as negatives increase.",
        },
        "feature_ablation": {
            "rows": feature_ablation["rows"],
            "interpretation": "Ablation check: report raw-count-only and rank/zscore-derived features separately to avoid overclaiming.",
        },
        "honesty_note": "v1.6 used the saved v1.5 feature matrix for speed. Raw CSV reparsing and larger external-data runs are tracked in compute backlog files.",
    }
    (out / "v16_readout_robustness_summary.json").write_text(_safe_json(summary), encoding="utf-8")
    (out / "negative_sweep_details.json").write_text(_safe_json(negative_sweep["details"]), encoding="utf-8")
    (out / "feature_ablation_details.json").write_text(_safe_json(feature_ablation["details"]), encoding="utf-8")
    _write_dict_csv(negative_sweep["rows"], out / "negative_per_pulse_sweep.csv")
    _write_dict_csv(feature_ablation["rows"], out / "feature_ablation.csv")
    (out / "PULSE_LEVEL_READOUT_ROBUSTNESS_REPORT.md").write_text(render_v16_report(summary), encoding="utf-8")
    return summary
