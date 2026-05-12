"""BioGPU v3.2 fixed-manifest real-data replay runner.

This module connects the v1.5 Zenodo pulse-window feature matrix to the
v3.x BioGPU integration flow. Unlike v3.1, this runner uses real public MEA
pulse-window response features rather than a toy deterministic observation.

Scope boundary:
- offline public-data replay only;
- no live stimulation parameters;
- no wet-lab protocol;
- no vendor pinout/wiring;
- no GPU advantage claim.
"""
from __future__ import annotations

import csv
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from biogpu.metrics.baseline_v29 import compare_baselines_v29
from biogpu.metrics.energy_model_v29 import EnergyRunInputV29, PowerComponentV29, estimate_energy_v29
from biogpu.metrics.latency_model_v29 import LatencyComponentsV29, estimate_latency_v29
from biogpu.runtime.session_manager_v24 import BioGPUAuditLog, BioGPUResultBundler, artifact_ref, build_v24_manifest, validate_manifest


@dataclass(frozen=True)
class RealDataReplayConfigV32:
    version: str = "v3.2"
    matrix_filename: str = "pulse_feature_matrix.npz"
    metadata_filename: str = "pulse_feature_metadata.csv"
    decoder_id: str = "centroid_v27_vectorized"
    benchmark_id: str = "B1_spot_localization:fixed_manifest_realdata_replay"
    split_strategy: str = "fixed_stride_culture_holdout"
    culture_stride: int = 3
    heldout_culture_count: int = 5
    shuffle_count: int = 20
    seed: int = 32
    task_count_for_energy: int = 1000
    run_duration_s_for_energy: float = 60.0
    operator_note: str = "v3.2 fixed-manifest real-data replay using Zenodo pulse-window features"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealDataMatrixV32:
    X: np.ndarray
    y: np.ndarray
    cultures: np.ndarray
    conditions: np.ndarray
    recording_path: np.ndarray
    pulse_index: np.ndarray
    feature_names: list[str]
    source_path: str

    def validate(self) -> None:
        if self.X.ndim != 2:
            raise ValueError("X must be a 2D matrix")
        n, p = self.X.shape
        if n <= 0 or p <= 0:
            raise ValueError("X must not be empty")
        if len(self.y) != n or len(self.cultures) != n:
            raise ValueError("labels/cultures length must match X rows")
        if len(self.feature_names) != p:
            raise ValueError("feature_names length must match X columns")
        if not np.isfinite(self.X).all():
            raise ValueError("X contains non-finite values")

    def profile(self) -> dict[str, Any]:
        self.validate()
        return {
            "rows": int(self.X.shape[0]),
            "features": int(self.X.shape[1]),
            "cultures": int(len(set(map(str, self.cultures)))),
            "target_classes": int(len(set(map(int, self.y)))),
            "conditions": sorted(set(map(str, self.conditions))),
            "source_path": self.source_path,
            "feature_name_sample": self.feature_names[:10],
        }


@dataclass(frozen=True)
class RealDataSplitV32:
    train_idx: list[int]
    test_idx: list[int]
    test_cultures: list[str]
    overlapping_labels: list[int]
    strategy: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealDataReplayResultV32:
    version: str
    n_train: int
    n_test: int
    n_features: int
    labels: list[int]
    test_cultures: list[str]
    accuracy: float
    chance_approx: float
    shuffled_mean_accuracy: float
    shuffled_std_accuracy: float
    shuffled_max_accuracy: float
    improvement_vs_shuffle_mean: float
    p_value_empirical_greater_equal: float
    prediction_sample: list[dict[str, Any]]
    confusion: dict[str, dict[str, int]]
    safety_boundary: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_v15_realdata_matrix_v32(v15_dir: str | Path, config: RealDataReplayConfigV32 | None = None) -> RealDataMatrixV32:
    config = config or RealDataReplayConfigV32()
    v15 = Path(v15_dir)
    matrix_path = v15 / config.matrix_filename
    if not matrix_path.exists():
        raise FileNotFoundError(f"Cannot find v1.5 feature matrix: {matrix_path}")
    z = np.load(matrix_path, allow_pickle=True)
    required = {"X", "target_id", "culture", "condition", "recording_path", "pulse_index", "feature_names"}
    missing = required - set(z.files)
    if missing:
        raise ValueError(f"Matrix missing required arrays: {sorted(missing)}")
    matrix = RealDataMatrixV32(
        X=np.asarray(z["X"], dtype=float),
        y=np.asarray(z["target_id"], dtype=int),
        cultures=np.asarray(z["culture"], dtype=str),
        conditions=np.asarray(z["condition"], dtype=str),
        recording_path=np.asarray(z["recording_path"], dtype=str),
        pulse_index=np.asarray(z["pulse_index"], dtype=int),
        feature_names=[str(x) for x in z["feature_names"].tolist()],
        source_path=str(matrix_path),
    )
    matrix.validate()
    return matrix


def build_fixed_culture_split_v32(matrix: RealDataMatrixV32, config: RealDataReplayConfigV32 | None = None) -> RealDataSplitV32:
    config = config or RealDataReplayConfigV32()
    matrix.validate()
    cultures = sorted(set(map(str, matrix.cultures)))
    if not cultures:
        raise ValueError("no cultures found")
    stride = max(1, int(config.culture_stride))
    test_cultures = [cultures[i] for i in range(0, len(cultures), stride)][: int(config.heldout_culture_count)]
    if not test_cultures:
        test_cultures = [cultures[-1]]
    is_test_culture = np.isin(matrix.cultures.astype(str), np.asarray(test_cultures, dtype=str))
    train_mask = ~is_test_culture
    test_mask = is_test_culture
    overlapping = sorted(set(map(int, matrix.y[train_mask])) & set(map(int, matrix.y[test_mask])))
    if not overlapping:
        raise ValueError("fixed split has no overlapping target labels between train and test")
    label_mask = np.isin(matrix.y, np.asarray(overlapping, dtype=int))
    train_idx = np.where(train_mask & label_mask)[0].astype(int).tolist()
    test_idx = np.where(test_mask & label_mask)[0].astype(int).tolist()
    if not train_idx or not test_idx:
        raise ValueError("fixed split produced empty train/test indices")
    return RealDataSplitV32(
        train_idx=train_idx,
        test_idx=test_idx,
        test_cultures=test_cultures,
        overlapping_labels=[int(x) for x in overlapping],
        strategy=config.split_strategy,
    )


def _centroids(X: np.ndarray, y: np.ndarray, labels: list[int]) -> np.ndarray:
    rows = []
    for lab in labels:
        mask = y == int(lab)
        if not np.any(mask):
            raise ValueError(f"label {lab} has no training rows")
        rows.append(np.mean(X[mask], axis=0))
    return np.vstack(rows)


def _predict_centroid(X_test: np.ndarray, labels: list[int], centroid_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Squared Euclidean distance matrix: n_test x n_labels
    d = ((X_test[:, None, :] - centroid_matrix[None, :, :]) ** 2).sum(axis=2)
    order = np.argsort(d, axis=1)
    pred = np.asarray(labels, dtype=int)[order[:, 0]]
    best = d[np.arange(d.shape[0]), order[:, 0]]
    second = d[np.arange(d.shape[0]), order[:, 1]] if d.shape[1] > 1 else best
    confidence = np.maximum(0.0, np.minimum(1.0, (second - best) / (np.abs(second) + 1e-12)))
    return pred, confidence, d


def _confusion_dict(y_true: np.ndarray, y_pred: np.ndarray, labels: list[int]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {str(l): {str(k): 0 for k in labels} for l in labels}
    for t, p in zip(y_true, y_pred):
        out[str(int(t))][str(int(p))] += 1
    return out


def evaluate_realdata_centroid_v32(matrix: RealDataMatrixV32, split: RealDataSplitV32, config: RealDataReplayConfigV32 | None = None) -> tuple[RealDataReplayResultV32, list[dict[str, Any]]]:
    config = config or RealDataReplayConfigV32()
    X = matrix.X
    y = matrix.y.astype(int)
    train_idx = np.asarray(split.train_idx, dtype=int)
    test_idx = np.asarray(split.test_idx, dtype=int)
    labels = [int(x) for x in split.overlapping_labels]
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    centroid_matrix = _centroids(X_train, y_train, labels)
    y_pred, conf, _ = _predict_centroid(X_test, labels, centroid_matrix)
    accuracy = float(np.mean(y_pred == y_test))
    chance = float(1.0 / len(labels)) if labels else 0.0

    rng = np.random.default_rng(int(config.seed))
    shuffle_rows: list[dict[str, Any]] = []
    shuffle_acc: list[float] = []
    for i in range(int(config.shuffle_count)):
        shuffled = y_train.copy()
        rng.shuffle(shuffled)
        c_shuf = _centroids(X_train, shuffled, labels)
        pred_shuf, _, _ = _predict_centroid(X_test, labels, c_shuf)
        acc = float(np.mean(pred_shuf == y_test))
        shuffle_acc.append(acc)
        shuffle_rows.append({"shuffle_index": i, "accuracy": acc})

    shuffle_mean = float(np.mean(shuffle_acc)) if shuffle_acc else 0.0
    shuffle_std = float(np.std(shuffle_acc)) if shuffle_acc else 0.0
    shuffle_max = float(np.max(shuffle_acc)) if shuffle_acc else 0.0
    p_emp = float((sum(1 for a in shuffle_acc if a >= accuracy) + 1) / (len(shuffle_acc) + 1)) if shuffle_acc else 1.0

    sample_n = min(50, len(y_test))
    prediction_sample = []
    for j in range(sample_n):
        idx = int(test_idx[j])
        prediction_sample.append({
            "row_index": idx,
            "true_target_id": int(y_test[j]),
            "predicted_target_id": int(y_pred[j]),
            "confidence": float(conf[j]),
            "culture": str(matrix.cultures[idx]),
            "condition": str(matrix.conditions[idx]),
            "recording_path": str(matrix.recording_path[idx]),
            "pulse_index": int(matrix.pulse_index[idx]),
        })

    result = RealDataReplayResultV32(
        version="v3.2",
        n_train=int(len(train_idx)),
        n_test=int(len(test_idx)),
        n_features=int(X.shape[1]),
        labels=labels,
        test_cultures=split.test_cultures,
        accuracy=accuracy,
        chance_approx=chance,
        shuffled_mean_accuracy=shuffle_mean,
        shuffled_std_accuracy=shuffle_std,
        shuffled_max_accuracy=shuffle_max,
        improvement_vs_shuffle_mean=float(accuracy - shuffle_mean),
        p_value_empirical_greater_equal=p_emp,
        prediction_sample=prediction_sample,
        confusion=_confusion_dict(y_test, y_pred, labels),
        safety_boundary=[
            "offline public-data replay only",
            "no live stimulation settings emitted",
            "no wet-lab protocol",
            "no vendor pinout or wiring procedure",
            "no GPU advantage claim",
        ],
    )
    return result, shuffle_rows


def _write_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    path = Path(path)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_confusion_csv(path: str | Path, confusion: dict[str, dict[str, int]], labels: list[int]) -> None:
    rows = []
    for true_label in labels:
        row = {"true_label": int(true_label)}
        for pred_label in labels:
            row[f"pred_{pred_label}"] = int(confusion[str(true_label)][str(pred_label)])
        rows.append(row)
    _write_csv(path, rows)


def build_energy_latency_report_v32(result: RealDataReplayResultV32, config: RealDataReplayConfigV32) -> dict[str, Any]:
    energy = estimate_energy_v29(EnergyRunInputV29(
        task_count=int(config.task_count_for_energy),
        run_duration_s=float(config.run_duration_s_for_energy),
        components=(
            PowerComponentV29("host_replay_pc", 65.0, "offline real-data replay runtime", "placeholder"),
            PowerComponentV29("storage_logging_share", 5.0, "audit/result bundle storage", "placeholder"),
        ),
        notes="v3.2 replay energy accounting only; live substrate energy is not included.",
    ))
    latency = estimate_latency_v29(LatencyComponentsV29(
        encode_ms=0.5,
        substrate_io_ms=0.0,
        biological_response_ms=0.0,
        acquisition_ms=0.0,
        feature_extraction_ms=1.0,
        readout_ms=2.0,
        controller_update_ms=0.0,
        notes="v3.2 offline matrix replay latency placeholder; not a live BioGPU latency measurement.",
    ))
    baseline = compare_baselines_v29(task_count=int(config.task_count_for_energy), run_duration_s=float(config.run_duration_s_for_energy))
    return {
        "version": "v3.2",
        "scientific_boundary": "Energy/latency numbers are accounting placeholders for replay mode; they do not prove live BioGPU advantage.",
        "realdata_accuracy": result.accuracy,
        "shuffle_mean_accuracy": result.shuffled_mean_accuracy,
        "energy": energy.to_dict(),
        "latency": latency.to_dict(),
        "baseline_catalog": baseline,
    }


def render_realdata_report_v32(profile: dict[str, Any], split: RealDataSplitV32, result: RealDataReplayResultV32) -> str:
    return f"""# BioGPU-Core v3.2 Real-data Replay E2E Report

## Status

`COMPLETED_SOFTWARE_ONLY_REPLAY`

## Dataset

- Rows / pulse windows: `{profile['rows']}`
- Features: `{profile['features']}`
- Cultures: `{profile['cultures']}`
- Target classes in full matrix: `{profile['target_classes']}`
- Conditions: `{', '.join(profile['conditions'])}`

## Fixed manifest split

- Strategy: `{split.strategy}`
- Held-out cultures: `{', '.join(split.test_cultures)}`
- Overlapping labels used: `{', '.join(map(str, split.overlapping_labels))}`
- Train windows: `{result.n_train}`
- Test windows: `{result.n_test}`

## Readout result

- Decoder: `centroid_v27_vectorized`
- Accuracy: `{result.accuracy:.6f}`
- Chance approx: `{result.chance_approx:.6f}`
- Shuffled-label mean accuracy: `{result.shuffled_mean_accuracy:.6f}`
- Shuffled-label std accuracy: `{result.shuffled_std_accuracy:.6f}`
- Shuffled-label max accuracy: `{result.shuffled_max_accuracy:.6f}`
- Improvement vs shuffle mean: `{result.improvement_vs_shuffle_mean:.6f}`
- Empirical p-value, shuffled >= real: `{result.p_value_empirical_greater_equal:.6f}`

## Interpretation

This is the first v3.x end-to-end real-data replay pass. It uses the real v1.5 Zenodo pulse-window feature matrix and a fixed culture-heldout split. It is not a live BioGPU result, and it does not prove GPU advantage. It proves that the v3.x integration layer can consume real biological response vectors and produce an auditable readout bundle.

## Safety boundary

{chr(10).join('- ' + x for x in result.safety_boundary)}
"""


def run_realdata_replay_v32(v15_dir: str | Path, out_dir: str | Path, config: RealDataReplayConfigV32 | None = None) -> dict[str, Any]:
    config = config or RealDataReplayConfigV32()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    audit = BioGPUAuditLog()
    started = time.perf_counter()

    manifest = build_v24_manifest(
        run_mode="replay",
        benchmark_ids=["B1_spot_localization", "B5_energy_latency_comparison"],
        hardware_profile="software_only_v32_realdata_replay",
        operator_note=config.operator_note,
    )
    object.__setattr__(manifest, "version", "v3.2")
    manifest.config["v32_realdata_replay"] = config.to_dict()
    validation_errors = validate_manifest(manifest)
    audit.add("manifest_created", "ok", validation_errors=validation_errors)

    matrix = load_v15_realdata_matrix_v32(v15_dir, config)
    profile = matrix.profile()
    audit.add("matrix_loaded", "ok", rows=profile["rows"], features=profile["features"])

    split = build_fixed_culture_split_v32(matrix, config)
    audit.add("fixed_split_created", "ok", n_train=len(split.train_idx), n_test=len(split.test_idx), test_cultures=split.test_cultures)

    result, shuffle_rows = evaluate_realdata_centroid_v32(matrix, split, config)
    elapsed_s = time.perf_counter() - started
    audit.add("realdata_readout_completed", "ok", accuracy=result.accuracy, shuffle_mean=result.shuffled_mean_accuracy, elapsed_s=elapsed_s)

    energy_latency = build_energy_latency_report_v32(result, config)
    audit.add("energy_latency_accounting_completed", "ok", replay_only=True)

    files: dict[str, Any] = {}
    files["run_manifest_v32.json"] = manifest.to_dict()
    files["dataset_profile_v32.json"] = profile
    files["split_summary_v32.json"] = split.to_dict()
    files["realdata_readout_summary_v32.json"] = result.to_dict()
    files["energy_latency_report_v32.json"] = energy_latency
    files["e2e_realdata_summary_v32.json"] = {
        "version": "v3.2",
        "status": "completed_software_only_replay",
        "validation_errors": validation_errors,
        "dataset_rows": profile["rows"],
        "dataset_features": profile["features"],
        "n_train": result.n_train,
        "n_test": result.n_test,
        "accuracy": result.accuracy,
        "chance_approx": result.chance_approx,
        "shuffled_mean_accuracy": result.shuffled_mean_accuracy,
        "improvement_vs_shuffle_mean": result.improvement_vs_shuffle_mean,
        "empirical_p_value_shuffled_ge_real": result.p_value_empirical_greater_equal,
        "elapsed_s": elapsed_s,
        "live_output_performed": False,
        "gpu_advantage_claimed": False,
    }

    for name, data in files.items():
        (out / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_csv(out / "realdata_readout_predictions_sample_v32.csv", result.prediction_sample)
    _write_csv(out / "shuffled_baseline_v32.csv", shuffle_rows)
    _write_confusion_csv(out / "realdata_readout_confusion_v32.csv", result.confusion, result.labels)
    (out / "BIOGPU_V32_REALDATA_REPLAY_REPORT.md").write_text(render_realdata_report_v32(profile, split, result), encoding="utf-8")
    audit.write_jsonl(out / "audit_log_v32.jsonl")

    bundler = BioGPUResultBundler(out)
    bundle = bundler.build_bundle("biogpu_v32_realdata_replay_result_bundle.zip")
    artifacts = [artifact_ref(p, out, "v32_output") for p in sorted(out.iterdir()) if p.is_file()]
    session_summary = {
        "version": "v3.2",
        "session_id": manifest.session_id,
        "status": "completed",
        "validation_errors": validation_errors,
        "artifact_count": len(artifacts),
        "artifacts": [a.to_dict() for a in artifacts],
        "result_bundle": bundle.name,
    }
    (out / "session_summary_v32.json").write_text(json.dumps(session_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    # Rebuild bundle so session_summary is included as well.
    bundle = bundler.build_bundle("biogpu_v32_realdata_replay_result_bundle.zip")
    files["session_summary_v32.json"] = session_summary
    return files["e2e_realdata_summary_v32.json"] | {"result_bundle": str(bundle)}
