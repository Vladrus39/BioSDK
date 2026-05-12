from __future__ import annotations

import csv, json, math, re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

# sklearn intentionally not required in v1.2 real-data analysis.
# We use a small nearest-centroid classifier to keep the pipeline lightweight.

from biogpu.data_ingest.zenodo_mea2100_preprocessed import (
    discover_recording_dirs,
    parse_electrode_number,
    read_metadata,
)
from biogpu.data_ingest.zenodo_stimulus_reconstruction import (
    normalize_condition,
    extract_target,
)


ELECTRODES_60 = [
    12,13,14,16,17,21,22,23,24,25,26,27,28,
    31,32,33,34,35,36,37,38,
    41,42,43,44,45,46,47,48,
    51,52,53,54,55,56,57,58,
    61,62,63,64,65,66,67,68,
    71,72,73,74,75,76,77,78,
    82,83,84,86,87,
]


def electrode_xy(e: int) -> tuple[int, int]:
    return int(e) // 10, int(e) % 10


def electrode_distance(a: int, b: int, metric: str = "manhattan") -> float:
    ar, ac = electrode_xy(a); br, bc = electrode_xy(b)
    if metric == "euclidean":
        return float(math.sqrt((ar-br)**2 + (ac-bc)**2))
    return float(abs(ar-br) + abs(ac-bc))


@dataclass
class RecordingVector:
    path: str
    date: str
    culture: str
    plate_id: str
    div: int | None
    condition: str
    target_type: str
    target_id: int | None
    duration_s: float
    sampling_hz: float
    total_spikes: int
    active_electrodes: int
    array_rate_hz: float
    electrode_rates: dict[int, float]


def _parse_identity(rec: Path, root: Path, meta: dict[str, Any]) -> dict[str, Any]:
    culture = rec.parent.name
    m = re.search(r"(.+?)_(\d+)DIV", culture)
    plate = m.group(1) if m else culture.split("_")[0]
    div = int(m.group(2)) if m else None
    date = ""
    for part in rec.parts:
        if re.match(r"\d{2}-\d{2}-\d{4}", part):
            date = part; break
    condition = normalize_condition(rec.name, meta)
    target_type, target_id = extract_target(rec.name, condition)
    return dict(path=str(rec.relative_to(root)), date=date, culture=culture, plate_id=plate, div=div,
                condition=condition, target_type=target_type, target_id=target_id)


def load_recording_vectors(root_path: str | Path) -> list[RecordingVector]:
    root = Path(root_path)
    out: list[RecordingVector] = []
    for rec in discover_recording_dirs(root):
        meta = read_metadata(rec)
        hz = float(meta.get("sampling_fr_hz") or 20000.0)
        dur = float(meta.get("recording_duration_sec") or 0.0)
        rates: dict[int, float] = {}
        total = 0
        for f in sorted(rec.glob("electrode*.csv")):
            eid = parse_electrode_number(f)
            with open(f, 'rb') as fh:
                n = max(0, sum(1 for _ in fh) - 1)
            total += n
            rates[eid] = float(n / dur) if dur else 0.0
        ident = _parse_identity(rec, root, meta)
        out.append(RecordingVector(
            **ident,
            duration_s=dur,
            sampling_hz=hz,
            total_spikes=total,
            active_electrodes=sum(1 for v in rates.values() if v > 0),
            array_rate_hz=float(total / dur) if dur else 0.0,
            electrode_rates=rates,
        ))
    return out


def recording_feature_matrix(recordings: list[RecordingVector], include_electrodes: bool = True):
    rows = []
    names = ["duration_s", "total_spikes", "active_electrodes", "array_rate_hz"]
    if include_electrodes:
        names += [f"rate_e{e}" for e in ELECTRODES_60]
    for r in recordings:
        row = [r.duration_s, r.total_spikes, r.active_electrodes, r.array_rate_hz]
        if include_electrodes:
            row += [r.electrode_rates.get(e, 0.0) for e in ELECTRODES_60]
        rows.append(row)
    return np.asarray(rows, dtype=float), names



def _standardize_train_test(X_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = X_train.mean(axis=0)
    sigma = X_train.std(axis=0)
    sigma[sigma == 0] = 1.0
    return (X_train - mu) / sigma, (X_test - mu) / sigma


def _nearest_centroid_predict(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> np.ndarray:
    classes = sorted(set(y_train.tolist()))
    centroids = []
    for c in classes:
        centroids.append(X_train[y_train == c].mean(axis=0))
    C = np.vstack(centroids)
    d = ((X_test[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
    idx = np.argmin(d, axis=1)
    return np.asarray([classes[i] for i in idx])


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred)) if len(y_true) else 0.0


def _confusion(labels: list[str], truth: list[str], preds: list[str]) -> list[list[int]]:
    pos = {c:i for i,c in enumerate(labels)}
    mat = [[0 for _ in labels] for _ in labels]
    for t,p in zip(truth, preds):
        if t in pos and p in pos:
            mat[pos[t]][pos[p]] += 1
    return mat


def _group_cv_scores(X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> tuple[list[float], list[str], list[str]]:
    scores=[]; truth=[]; preds=[]
    for g in sorted(set(groups.tolist())):
        train = groups != g
        test = groups == g
        if len(set(y[train].tolist())) < 2:
            continue
        Xtr, Xte = _standardize_train_test(X[train], X[test])
        pred = _nearest_centroid_predict(Xtr, y[train], Xte)
        scores.append(_accuracy(y[test], pred))
        truth.extend(y[test].tolist()); preds.extend(pred.tolist())
    return scores, truth, preds


def _simple_stratified_scores(X: np.ndarray, y: np.ndarray, n_splits: int = 5, seed: int = 7) -> list[float]:
    rng = np.random.default_rng(seed)
    idx_by_class = {c: np.where(y == c)[0].tolist() for c in sorted(set(y.tolist()))}
    for ids in idx_by_class.values(): rng.shuffle(ids)
    scores=[]
    for fold in range(n_splits):
        test_ids=[]
        for ids in idx_by_class.values():
            test_ids.extend(ids[fold::n_splits])
        test=np.asarray(sorted(test_ids), dtype=int)
        train=np.asarray([i for i in range(len(y)) if i not in set(test_ids)], dtype=int)
        if len(test)==0 or len(set(y[train].tolist())) < 2: continue
        Xtr,Xte=_standardize_train_test(X[train],X[test])
        pred=_nearest_centroid_predict(Xtr,y[train],Xte)
        scores.append(_accuracy(y[test],pred))
    return scores

def condition_benchmark(recordings: list[RecordingVector]) -> dict[str, Any]:
    subset = [r for r in recordings if r.condition in {"baseline", "lightstim"}]
    X, names = recording_feature_matrix(subset, include_electrodes=True)
    y = np.asarray([r.condition for r in subset])
    groups = np.asarray([r.culture for r in subset])
    scores, truth, preds = _group_cv_scores(X, y, groups)
    scores2 = _simple_stratified_scores(X, y, 5)
    labels = ["baseline", "lightstim"]
    return {
        "task": "recording_level_condition_classification",
        "classifier": "nearest_centroid_standardized",
        "labels": labels,
        "n_recordings": len(subset),
        "n_cultures": len(set(groups)),
        "feature_count": len(names),
        "leave_one_group_accuracy_mean": float(np.mean(scores)) if scores else None,
        "leave_one_group_accuracy_std": float(np.std(scores)) if scores else None,
        "stratified_5fold_accuracy_mean": float(np.mean(scores2)) if scores2 else None,
        "stratified_5fold_accuracy_std": float(np.std(scores2)) if scores2 else None,
        "confusion_matrix_leave_group": _confusion(labels, truth, preds),
        "honesty_note": "Recording-level condition benchmark; not pulse-level stimulus-window benchmark.",
    }


def _baseline_by_culture(recordings: list[RecordingVector]) -> dict[str, RecordingVector]:
    base = {}
    for r in recordings:
        if r.condition == "baseline":
            base[r.culture] = r
    return base


def spot_response_profiles(recordings: list[RecordingVector]) -> list[dict[str, Any]]:
    baseline = _baseline_by_culture(recordings)
    rows = []
    for r in recordings:
        if r.condition != "lightstim" or r.target_id is None:
            continue
        b = baseline.get(r.culture)
        if b is None:
            continue
        deltas = {e: r.electrode_rates.get(e, 0.0) - b.electrode_rates.get(e, 0.0) for e in ELECTRODES_60}
        vals = np.asarray(list(deltas.values()), dtype=float)
        target = int(r.target_id)
        target_delta = float(deltas.get(target, np.nan))
        # percentile of target delta among all electrodes, if target exists in MEA electrode list
        if not np.isnan(target_delta):
            percentile = float((np.sum(vals <= target_delta) / len(vals)) * 100.0)
        else:
            percentile = float("nan")
        by_dist: dict[int, list[float]] = {}
        for e, d in deltas.items():
            dist = int(electrode_distance(target, e))
            by_dist.setdefault(dist, []).append(float(d))
        dist_summary = {str(k): float(np.mean(v)) for k, v in sorted(by_dist.items()) if k <= 4}
        rows.append({
            "path": r.path,
            "culture": r.culture,
            "spot": target,
            "duration_s": r.duration_s,
            "baseline_path": b.path,
            "target_electrode_present": target in ELECTRODES_60,
            "target_delta_rate_hz": target_delta if target in ELECTRODES_60 else None,
            "target_delta_percentile": percentile if target in ELECTRODES_60 else None,
            "global_mean_delta_rate_hz": float(np.mean(vals)),
            "global_median_delta_rate_hz": float(np.median(vals)),
            "max_delta_rate_hz": float(np.max(vals)),
            "min_delta_rate_hz": float(np.min(vals)),
            "mean_delta_by_manhattan_distance_0_to_4": dist_summary,
            "assumption": "spot ID is treated as MEA grid coordinate/electrode ID; verify against original protocol before anatomical claims.",
        })
    return rows


def spot_level_summary(spot_rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [r for r in spot_rows if r.get("target_electrode_present") and r.get("target_delta_rate_hz") is not None]
    percentiles = [r["target_delta_percentile"] for r in valid if r.get("target_delta_percentile") is not None]
    target_delta = [r["target_delta_rate_hz"] for r in valid if r.get("target_delta_rate_hz") is not None]
    return {
        "lightstim_recordings_with_baseline": len(spot_rows),
        "target_electrode_present_count": len(valid),
        "median_target_delta_rate_hz": float(np.median(target_delta)) if target_delta else None,
        "mean_target_delta_rate_hz": float(np.mean(target_delta)) if target_delta else None,
        "median_target_delta_percentile": float(np.median(percentiles)) if percentiles else None,
        "spots_analyzed": sorted(set(int(r["spot"]) for r in spot_rows)),
        "honesty_note": "Spot-level response profile is recording-level baseline-vs-lightstim delta, not pulse-triggered PSTH.",
    }


def spot_classification(recordings: list[RecordingVector]) -> dict[str, Any]:
    subset = [r for r in recordings if r.condition == "lightstim" and r.target_id is not None]
    counts: dict[int, int] = {}
    for r in subset:
        counts[int(r.target_id)] = counts.get(int(r.target_id), 0) + 1
    keep = {k for k, v in counts.items() if v >= 2}
    subset = [r for r in subset if int(r.target_id) in keep]
    if len(subset) < 6 or len(keep) < 2:
        return {"status": "not_enough_repeated_spots", "class_counts": counts, "honesty_note": "Too few repeated spots for robust spot-level classification."}
    X, _ = recording_feature_matrix(subset, include_electrodes=True)
    y = np.asarray([str(r.target_id) for r in subset])
    scores = _simple_stratified_scores(X, y, n_splits=2)
    return {
        "task": "exploratory_spot_classification_repeated_spots_only",
        "classifier": "nearest_centroid_standardized",
        "n_recordings": len(subset),
        "n_spot_classes": len(set(y)),
        "class_counts_kept": {str(k): counts[k] for k in sorted(keep)},
        "stratified_accuracy_mean": float(np.mean(scores)) if scores else None,
        "stratified_accuracy_std": float(np.std(scores)) if scores else None,
        "chance_level_approx": float(1.0 / len(set(y))),
        "honesty_note": "Exploratory only: few repeated classes and recording-level features; not pulse-window evidence.",
    }


def write_outputs(root_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    recs = load_recording_vectors(root_path)
    rows = []
    for r in recs:
        d = asdict(r); d.pop("electrode_rates")
        rows.append(d)
    # CSV recording summary
    with (out/"recording_vectors_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    cond = condition_benchmark(recs)
    spot_rows = spot_response_profiles(recs)
    spot_sum = spot_level_summary(spot_rows)
    spot_cls = spot_classification(recs)
    with (out/"spot_response_profiles.json").open("w", encoding="utf-8") as f:
        json.dump(spot_rows, f, indent=2, ensure_ascii=False)
    with (out/"condition_level_benchmark.json").open("w", encoding="utf-8") as f:
        json.dump(cond, f, indent=2, ensure_ascii=False)
    with (out/"spot_level_summary.json").open("w", encoding="utf-8") as f:
        json.dump(spot_sum, f, indent=2, ensure_ascii=False)
    with (out/"spot_classification_exploratory.json").open("w", encoding="utf-8") as f:
        json.dump(spot_cls, f, indent=2, ensure_ascii=False)
    report = render_markdown_report(cond, spot_sum, spot_cls)
    (out/"CONDITION_SPOT_ANALYSIS_REPORT.md").write_text(report, encoding="utf-8")
    return {"condition": cond, "spot_summary": spot_sum, "spot_classification": spot_cls}


def render_markdown_report(cond: dict[str, Any], spot_sum: dict[str, Any], spot_cls: dict[str, Any]) -> str:
    return f"""# Zenodo 14363732 — Condition / Spot-level real-data analysis v1.2

## Scope

This is a real-data analysis on the uploaded `Pre_processed_MEA_data.zip` archive.

It uses exact recording-level labels reconstructed from metadata/folder names. It does **not** claim pulse-level stimulus timing, because the preprocessed archive does not contain TTL/onset fields.

## Condition-level benchmark

- Task: baseline vs lightstim
- Validation: leave-one-culture/group and stratified folds
- Accuracy mean, leave-one-group: `{cond.get('leave_one_group_accuracy_mean')}`
- Accuracy std, leave-one-group: `{cond.get('leave_one_group_accuracy_std')}`
- Accuracy mean, stratified 5-fold: `{cond.get('stratified_5fold_accuracy_mean')}`
- Confusion matrix [baseline, lightstim]: `{cond.get('confusion_matrix_leave_group')}`

## Spot-level response profile

- LightStim recordings with matching baseline: `{spot_sum.get('lightstim_recordings_with_baseline')}`
- Target electrode present count: `{spot_sum.get('target_electrode_present_count')}`
- Mean target delta rate, Hz: `{spot_sum.get('mean_target_delta_rate_hz')}`
- Median target delta rate, Hz: `{spot_sum.get('median_target_delta_rate_hz')}`
- Median target delta percentile: `{spot_sum.get('median_target_delta_percentile')}`
- Spots analyzed: `{spot_sum.get('spots_analyzed')}`

## Exploratory repeated-spot classification

```json
{json.dumps(spot_cls, indent=2, ensure_ascii=False)}
```

## Honesty note

This is recording-level evidence. It supports real-data ingestion and condition/spot response profiling. It does not yet support PSTH or pulse-triggered BioGPU claims.

Next required step: inspect raw HDF5 trigger/TTL/protocol fields or original stimulation protocol to build pulse-level `stimulus_windows.csv`.
"""
