from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from biogpu.analysis.zenodo_pulse_readout import CandidateFeatureTable, PulseFeatureMatrix, build_candidate_target_table
from biogpu.analysis.zenodo_pulse_v16 import FEATURE_SETS, load_pulse_feature_matrix_from_v15_outputs, select_candidate_features

V17_DEFAULT_READOUTS = ["centroid", "logistic_l2", "linear_svm"]
V17_DEFAULT_FEATURE_SETS = ["all_features", "raw_candidate_counts_only", "all_without_rank_zscore", "pulse_context_only_negative_control"]


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _one_sided_high_p_value(observed: float | None, null_values: list[float]) -> float | None:
    if observed is None or not np.isfinite(float(observed)):
        return None
    clean = [float(v) for v in null_values if np.isfinite(float(v))]
    if not clean:
        return None
    return float((1 + sum(v >= float(observed) for v in clean)) / (len(clean) + 1))


def _summary_stats(values: Iterable[float]) -> dict[str, Any]:
    arr = np.asarray([float(v) for v in values if np.isfinite(float(v))], dtype=float)
    if arr.size == 0:
        return {"n": 0, "mean": None, "median": None, "q025": None, "q975": None}
    return {"n": int(arr.size), "mean": float(arr.mean()), "median": float(np.median(arr)), "q025": float(np.quantile(arr, 0.025)), "q975": float(np.quantile(arr, 0.975))}


def _standardize(X_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    return scaler.fit_transform(np.asarray(X_train, dtype=np.float32)), scaler.transform(np.asarray(X_test, dtype=np.float32))


def _centroid_predict_score(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Z_train, Z_test = _standardize(X_train, X_test)
    center0 = Z_train[y_train == 0].mean(axis=0) if np.any(y_train == 0) else np.zeros(Z_train.shape[1], dtype=float)
    center1 = Z_train[y_train == 1].mean(axis=0) if np.any(y_train == 1) else np.zeros(Z_train.shape[1], dtype=float)
    d0 = ((Z_test - center0) ** 2).sum(axis=1)
    d1 = ((Z_test - center1) ** 2).sum(axis=1)
    score = d0 - d1
    return (score >= 0).astype(int), score


def _linear_predict_score(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, readout: str, seed: int) -> tuple[np.ndarray, np.ndarray]:
    Z_train, Z_test = _standardize(X_train, X_test)
    if readout == "logistic_l2":
        model = LogisticRegression(solver="liblinear", class_weight="balanced", max_iter=1000, random_state=int(seed))
    elif readout == "linear_svm":
        model = LinearSVC(class_weight="balanced", max_iter=5000, random_state=int(seed), dual="auto")
    else:
        raise ValueError(f"Unknown readout: {readout}")
    model.fit(Z_train, y_train)
    return model.predict(Z_test).astype(int), np.asarray(model.decision_function(Z_test), dtype=float)


def _predict_score(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, readout: str, seed: int) -> tuple[np.ndarray, np.ndarray]:
    if readout == "centroid":
        return _centroid_predict_score(X_train, y_train, X_test)
    return _linear_predict_score(X_train, y_train, X_test, readout, seed)


def leave_one_culture_binary_readout(table: CandidateFeatureTable, readout: str = "logistic_l2", label_shuffles: int = 0, seed: int = 17) -> dict[str, Any]:
    X = np.asarray(table.X, dtype=np.float32)
    y = np.asarray(table.y, dtype=int)
    groups = np.asarray(table.culture, dtype=str)
    if X.size == 0 or len(set(groups.tolist())) < 2 or len(set(y.tolist())) < 2:
        return {"status": "not_enough_data", "sample_count": int(len(y)), "readout": readout}
    logo = LeaveOneGroupOut()
    splits = list(logo.split(X, y, groups))
    fold_rows: list[dict[str, Any]] = []
    pred_all: list[np.ndarray] = []
    true_all: list[np.ndarray] = []
    score_all: list[np.ndarray] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splits):
        if len(set(y[train_idx].tolist())) < 2 or len(set(y[test_idx].tolist())) < 2:
            continue
        pred, score = _predict_score(X[train_idx], y[train_idx], X[test_idx], readout, seed + fold_idx)
        pred_all.append(pred); true_all.append(y[test_idx]); score_all.append(score)
        fold_rows.append({"fold": int(fold_idx), "heldout_culture": str(groups[test_idx][0]), "n_test": int(len(test_idx)), "positive_fraction": float(np.mean(y[test_idx])), "accuracy": float(accuracy_score(y[test_idx], pred)), "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)), "roc_auc": float(roc_auc_score(y[test_idx], score))})
    if not pred_all:
        return {"status": "no_valid_folds", "sample_count": int(len(y)), "readout": readout}
    pred_all_arr = np.concatenate(pred_all); true_all_arr = np.concatenate(true_all); score_all_arr = np.concatenate(score_all)
    observed = {"accuracy": float(accuracy_score(true_all_arr, pred_all_arr)), "balanced_accuracy": float(balanced_accuracy_score(true_all_arr, pred_all_arr)), "roc_auc": float(roc_auc_score(true_all_arr, score_all_arr))}
    rng = np.random.default_rng(seed)
    shuffle_rows: list[dict[str, Any]] = []
    for shuffle_idx in range(max(0, int(label_shuffles))):
        p_all: list[np.ndarray] = []; t_all: list[np.ndarray] = []; s_all: list[np.ndarray] = []
        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            y_train = y[train_idx].copy(); rng.shuffle(y_train)
            if len(set(y_train.tolist())) < 2 or len(set(y[test_idx].tolist())) < 2:
                continue
            pred, score = _predict_score(X[train_idx], y_train, X[test_idx], readout, seed + 1000 + shuffle_idx * 101 + fold_idx)
            p_all.append(pred); t_all.append(y[test_idx]); s_all.append(score)
        if p_all:
            pp = np.concatenate(p_all); tt = np.concatenate(t_all); ss = np.concatenate(s_all)
            shuffle_rows.append({"shuffle": int(shuffle_idx), "accuracy": float(accuracy_score(tt, pp)), "balanced_accuracy": float(balanced_accuracy_score(tt, pp)), "roc_auc": float(roc_auc_score(tt, ss))})
    null_auc = [float(r["roc_auc"]) for r in shuffle_rows]
    null_bal = [float(r["balanced_accuracy"]) for r in shuffle_rows]
    return {"task": "target_vs_non_target_candidate_readout_leave_one_culture_out_v1_7", "sample_count": int(len(y)), "culture_count": int(len(set(groups.tolist()))), "positive_fraction": float(np.mean(y)), "feature_count": int(X.shape[1]), "readout": readout, "observed": observed, "fold_summary": {"roc_auc": _summary_stats([r["roc_auc"] for r in fold_rows]), "balanced_accuracy": _summary_stats([r["balanced_accuracy"] for r in fold_rows]), "accuracy": _summary_stats([r["accuracy"] for r in fold_rows])}, "label_shuffle_baseline": {"shuffles": int(len(shuffle_rows)), "roc_auc": _summary_stats(null_auc), "balanced_accuracy": _summary_stats(null_bal), "p_value_roc_auc_gt_shuffle": _one_sided_high_p_value(observed["roc_auc"], null_auc), "p_value_balanced_accuracy_gt_shuffle": _one_sided_high_p_value(observed["balanced_accuracy"], null_bal)}, "folds": fold_rows, "shuffle_rows": shuffle_rows, "honesty_note": "v1.7 uses culture-held-out folds. The quick run uses limited shuffles/seeds; paper-grade rerun commands are supplied separately."}


def run_v17_repeated_seed_readouts(matrix: PulseFeatureMatrix, negative_counts: list[int] | None = None, negative_seeds: list[int] | None = None, readouts: list[str] | None = None, feature_set_names: list[str] | None = None, label_shuffles: int = 5) -> dict[str, Any]:
    negative_counts = [1, 3, 5] if negative_counts is None else [int(v) for v in negative_counts]
    negative_seeds = [101, 202, 303] if negative_seeds is None else [int(v) for v in negative_seeds]
    readouts = V17_DEFAULT_READOUTS if readouts is None else [str(v) for v in readouts]
    feature_set_names = V17_DEFAULT_FEATURE_SETS if feature_set_names is None else [str(v) for v in feature_set_names]
    rows: list[dict[str, Any]] = []; details: dict[str, Any] = {}
    for neg in negative_counts:
        for neg_seed in negative_seeds:
            base_table = build_candidate_target_table(matrix, negative_per_pulse=int(neg), seed=int(neg_seed))
            for fs_name in feature_set_names:
                table = select_candidate_features(base_table, FEATURE_SETS[fs_name])
                for readout in readouts:
                    result = leave_one_culture_binary_readout(table, readout=readout, label_shuffles=int(label_shuffles), seed=int(neg_seed + 10000 * neg + 37 * len(rows)))
                    observed = result.get("observed", {}); shuffle = result.get("label_shuffle_baseline", {})
                    row = {"negative_per_pulse": int(neg), "negative_seed": int(neg_seed), "feature_set": fs_name, "readout": readout, "sample_count": int(result.get("sample_count", 0)), "feature_count": int(result.get("feature_count", 0)), "positive_fraction": float(result.get("positive_fraction", float("nan"))), "observed_roc_auc": observed.get("roc_auc"), "observed_balanced_accuracy": observed.get("balanced_accuracy"), "observed_accuracy": observed.get("accuracy"), "shuffle_roc_auc_median": (shuffle.get("roc_auc") or {}).get("median"), "shuffle_balanced_accuracy_median": (shuffle.get("balanced_accuracy") or {}).get("median"), "p_value_roc_auc_gt_shuffle": shuffle.get("p_value_roc_auc_gt_shuffle")}
                    rows.append(row); details[f"neg{neg}_seed{neg_seed}_{fs_name}_{readout}"] = result
    return {"rows": rows, "details": details}


def summarize_v17_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["negative_per_pulse"], row["feature_set"], row["readout"]), []).append(row)
    out: list[dict[str, Any]] = []
    for (neg, fs_name, readout), group in grouped.items():
        auc = [float(r["observed_roc_auc"]) for r in group if r.get("observed_roc_auc") is not None]
        bal = [float(r["observed_balanced_accuracy"]) for r in group if r.get("observed_balanced_accuracy") is not None]
        sh = [float(r["shuffle_roc_auc_median"]) for r in group if r.get("shuffle_roc_auc_median") is not None]
        out.append({"negative_per_pulse": int(neg), "feature_set": fs_name, "readout": readout, "negative_seed_runs": int(len(group)), "roc_auc_mean": _summary_stats(auc)["mean"], "roc_auc_median": _summary_stats(auc)["median"], "roc_auc_q025": _summary_stats(auc)["q025"], "roc_auc_q975": _summary_stats(auc)["q975"], "balanced_accuracy_mean": _summary_stats(bal)["mean"], "balanced_accuracy_median": _summary_stats(bal)["median"], "shuffle_roc_auc_median_across_runs": _summary_stats(sh)["median"]})
    out.sort(key=lambda r: (float("-inf") if r.get("roc_auc_mean") is None else float(r["roc_auc_mean"])), reverse=True)
    return out


def _write_dict_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    fields: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def render_v17_report(summary: dict[str, Any]) -> str:
    lines = []
    for r in summary.get("best_rows", [])[:8]:
        if r.get("roc_auc_mean") is not None:
            lines.append(f"- neg={r['negative_per_pulse']}, {r['feature_set']}, {r['readout']}: AUC mean={r['roc_auc_mean']:.5f}, balanced acc mean={r['balanced_accuracy_mean']:.5f}")
    best_lines = "\n".join(lines) if lines else "- No rows produced."
    return f"""# BioGPU-Core v1.7 — paper-grade readout rerun scaffold

## Purpose

v1.7 adds stronger linear readouts and a repeatable rerun plan:

1. Repeated negative-electrode seeds.
2. Multiple readouts: nearest centroid, L2 logistic regression, linear SVM.
3. Feature-set comparison, including raw-count-only and pulse-context negative control.
4. A separate heavy-compute plan for 100+ seeds and 1000+ label shuffles.

## Local quick-run result

This archive contains a real local quick run. It verifies the full code path, but it is not the final publication-grade run.

## Best rows from local quick run

{best_lines}

## Full summary

```json
{_safe_json(summary)}
```

## Honesty rules

- The local quick run is real, but limited by execution time.
- The final paper-grade result must rerun `paper_full` settings from `docs/V17_PAPER_GRADE_RERUN_PLAN.md`.
- Report raw-count-only features separately from all features.
- The pulse-context-only negative control must stay near chance; if it rises, investigate leakage.
- This remains a biological separability benchmark, not a silicon-GPU advantage proof.
"""


def write_v17_outputs_from_v15_matrix(v15_out_dir: str | Path, out_dir: str | Path, negative_counts: list[int] | None = None, negative_seeds: list[int] | None = None, readouts: list[str] | None = None, feature_set_names: list[str] | None = None, label_shuffles: int = 5) -> dict[str, Any]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    matrix = load_pulse_feature_matrix_from_v15_outputs(v15_out_dir)
    result = run_v17_repeated_seed_readouts(matrix, negative_counts=negative_counts, negative_seeds=negative_seeds, readouts=readouts, feature_set_names=feature_set_names, label_shuffles=int(label_shuffles))
    summary_rows = summarize_v17_rows(result["rows"])
    conditions = [m.condition for m in matrix.metadata]; targets = [m.target_id for m in matrix.metadata if m.target_id is not None]
    summary = {"task": "pulse_level_readout_paper_grade_scaffold_v1_7_from_v15_matrix", "input": {"v15_out_dir": str(v15_out_dir), "note": "Fast-path from saved v1.5 feature matrix; raw spike CSV files were not reparsed."}, "feature_matrix": {"pulse_count": int(matrix.X.shape[0]), "feature_count": int(matrix.X.shape[1]), "electrode_count": int(len(matrix.electrodes)), "response_window_ms": float(matrix.response_window_ms), "cultures": int(len(set(str(m.culture) for m in matrix.metadata))) if matrix.metadata else 0, "conditions": {str(k): int(v) for k, v in zip(*np.unique(np.asarray(conditions, dtype=object), return_counts=True))}, "target_class_count": int(len(set(int(v) for v in targets)))}, "parameters": {"negative_counts": [int(v) for v in (negative_counts or [1, 3, 5])], "negative_seeds": [int(v) for v in (negative_seeds or [101, 202, 303])], "readouts": readouts or V17_DEFAULT_READOUTS, "feature_set_names": feature_set_names or V17_DEFAULT_FEATURE_SETS, "label_shuffles": int(label_shuffles), "run_mode": "local_quick" if int(label_shuffles) <= 10 and len(negative_seeds or [101, 202, 303]) <= 5 else "large"}, "best_rows": summary_rows[:12], "grouped_summary_rows": summary_rows, "honesty_note": "v1.7 supplies both local quick results and a full rerun plan. Use the full rerun before publication or strong claims."}
    (out / "v17_readout_paper_grade_summary.json").write_text(_safe_json(summary), encoding="utf-8")
    (out / "v17_repeated_seed_rows.json").write_text(_safe_json(result["rows"]), encoding="utf-8")
    (out / "v17_repeated_seed_details.json").write_text(_safe_json(result["details"]), encoding="utf-8")
    _write_dict_csv(result["rows"], out / "v17_repeated_seed_rows.csv")
    _write_dict_csv(summary_rows, out / "v17_grouped_summary.csv")
    (out / "PULSE_LEVEL_READOUT_PAPER_GRADE_REPORT.md").write_text(render_v17_report(summary), encoding="utf-8")
    return summary
