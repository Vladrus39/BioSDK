"""BioSDK — Vendor-Neutral Standard for Biological Neural Computation.

A clean 4-function API facade over the BioSDK runtime:
    open() → features() → readout() → evidence.bundle()

Usage:
    import biosdk
    ds = biosdk.open("data/external/api_exports/mcs_mea2100/file.h5")
    X = biosdk.features(ds, window_s=0.5)
    print(X.shape)

This package re-exports from the internal biogpu modules without exposing
their full complexity. For advanced usage, import from biogpu.* directly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

# ── Ensure the parent biogpu package is importable ──
_BIOSDK_ROOT = Path(__file__).resolve().parent.parent
if str(_BIOSDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_BIOSDK_ROOT))

import numpy as np

# ═══════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════

# Single source of truth: pyproject.toml. If running from an uninstalled
# checkout (no dist-info on sys.path), fall back to a sentinel so the
# attribute is always defined.
from importlib.metadata import PackageNotFoundError as _PkgNotFound
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("biosdk")
except _PkgNotFound:
    __version__ = "0.0.0+local"

__all__ = [
    "open", "features", "readout", "evidence_bundle",
    "list_adapters", "certified_adapters", "__version__",
]


def open(path: str | Path, vendor: str = "auto") -> Any:
    """Open a neural recording and return an NSIDataset handle.

    Args:
        path: Path to the data file (HDF5, NWB, EDF, CSV).
        vendor: Vendor hint. 'auto' tries all registered adapters.
            Specific: 'mcs', 'giroldini', 'dandi', 'allen', 'physionet', 'gcp2'.

    Returns:
        NSIDataset with .metadata, .data (np.ndarray), .feature_names.

    Example:
        >>> ds = biosdk.open("data/external/api_exports/mcs_mea2100/file.h5")
        >>> print(ds.metadata.vendor, ds.metadata.channel_count)
        mcs 17
    """
    from biogpu.nsi.adapters import get_adapter, list_adapters

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    if vendor == "auto":
        # Try all registered adapters
        for adapter_id in list_adapters():
            adapter_cls = get_adapter(adapter_id)
            if adapter_cls is None:
                continue
            try:
                instance = adapter_cls()
                # Quick metadata probe — fails fast if wrong vendor
                meta = instance.metadata(p)
                if meta.vendor == adapter_cls.vendor:
                    return instance.open(p)
            except Exception:
                continue
        raise ValueError(
            f"No adapter could open {p.name}. "
            f"Available adapters: {list_adapters()}. "
            f"Try vendor='mcs' or vendor='giroldini'."
        )
    else:
        adapter_id_map = {
            "mcs": "mcs_mea2100",
            "giroldini": "giroldini_mea",
            "dandi": "dandi_nwb",
            "allen": "dandi_nwb",
            "edf": "physionet_edf",
            "sleep": "physionet_edf",
            "gcp2": "gcp2_csv",
            "csv": "gcp2_csv",
            "tressoldi": "tressoldi_h3",
            "finalspark": "finalspark_neuroplatform",
        }
        aid = adapter_id_map.get(vendor, vendor)
        adapter_cls = get_adapter(aid)
        if adapter_cls is None:
            raise ValueError(
                f"Adapter '{aid}' not registered. Available: {list_adapters()}"
            )
        return adapter_cls().open(p)


def features(
    dataset: Any,
    window_s: float = 0.5,
    overlap: float = 0.0,
    max_windows: int | None = None,
) -> np.ndarray:
    """Extract feature vectors from an NSIDataset.

    Slides non-overlapping windows over the data and extracts 6 features
    per channel: RMS, MAV, zero-crossings, variance, peak, skewness.

    Args:
        dataset: NSIDataset returned by biosdk.open().
        window_s: Window size in seconds.
        overlap: Overlap fraction (0.0 = non-overlapping, 0.5 = 50%).
        max_windows: Cap on number of windows (None = all).

    Returns:
        np.ndarray of shape (n_windows, n_channels * 6), dtype float32.

    Example:
        >>> ds = biosdk.open("file.h5")
        >>> X = biosdk.features(ds, window_s=0.5)
        >>> print(X.shape)
        (39, 102)
    """
    if dataset.data is None:
        raise ValueError("Dataset has no loaded data. Call biosdk.open() first.")

    data = dataset.data
    sample_rate = dataset.metadata.sample_rate_hz
    if sample_rate <= 0:
        raise ValueError(f"Invalid sample rate: {sample_rate}")

    window_samples = int(window_s * sample_rate)
    stride = max(1, int(window_samples * (1.0 - overlap)))

    from biogpu.nsi import _default_feature_vector

    feature_list = []
    start = 0
    while start + window_samples <= data.shape[1]:
        if max_windows and len(feature_list) >= max_windows:
            break
        window = data[:, start:start + window_samples]
        fv = _default_feature_vector(window)
        feature_list.append(fv)
        start += stride

    if not feature_list:
        return np.array([], dtype=np.float32)

    return np.array(feature_list, dtype=np.float32)


def readout(
    X: np.ndarray,
    y: np.ndarray | None = None,
    classifier: str = "rf",
    cv_folds: int = 5,
) -> dict:
    """Run classification readout on extracted features.

    Args:
        X: Feature matrix (n_windows, n_features).
        y: Labels (n_windows,). If None, returns placeholder.
        classifier: 'rf' (RandomForest), 'lr' (LogisticRegression), 'svm' (SVM).
        cv_folds: Number of cross-validation folds.

    Returns:
        Dict with 'balanced_accuracy', 'cv_std', 'per_class', 'confusion_matrix'.

    Example:
        >>> X = biosdk.features(ds, window_s=0.5)
        >>> result = biosdk.readout(X, y)
        >>> print(result['balanced_accuracy'])
    """
    if y is None:
        return {
            "balanced_accuracy": None,
            "error": "No labels provided. Readout requires ground truth labels y.",
            "hint": "Use biosdk.readout(X, y) with label array.",
        }

    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.metrics import balanced_accuracy_score, confusion_matrix

    classifiers = {
        "rf": RandomForestClassifier(n_estimators=100, random_state=42),
        "lr": LogisticRegression(max_iter=2000, random_state=42),
        "svm": SVC(kernel="rbf", random_state=42),
    }

    clf = classifiers.get(classifier)
    if clf is None:
        raise ValueError(f"Unknown classifier: {classifier}. Use 'rf', 'lr', or 'svm'.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="balanced_accuracy")

    clf.fit(X_scaled, y)
    y_pred = clf.predict(X_scaled)
    cm = confusion_matrix(y, y_pred)

    classes = sorted(set(y))
    per_class = {}
    for i, cls in enumerate(classes):
        tp = cm[i, i]
        total = cm[i].sum()
        pred_total = cm[:, i].sum()
        per_class[int(cls)] = {
            "recall": round(float(tp / total if total > 0 else 0), 4),
            "precision": round(float(tp / pred_total if pred_total > 0 else 0), 4),
            "n": int(total),
        }

    return {
        "classifier": classifier,
        "balanced_accuracy": round(float(scores.mean()), 4),
        "cv_std": round(float(scores.std()), 4),
        "cv_folds": cv_folds,
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "n_samples": len(y),
        "n_features": X.shape[1],
    }


def evidence_bundle(
    results: dict,
    output_dir: str | Path = "evidence_bundle",
    metadata: dict | None = None,
) -> Path:
    """Create a signed evidence bundle from results.

    Args:
        results: Dict with benchmark results (from readout or custom).
        output_dir: Directory to write the bundle.
        metadata: Optional extra metadata to include.

    Returns:
        Path to the bundle directory.

    Example:
        >>> result = biosdk.readout(X, y)
        >>> bundle_path = biosdk.evidence_bundle(result, "my_bundle")
        >>> print(bundle_path)
    """
    import json, hashlib, hmac
    from datetime import datetime, timezone

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    bundle = {
        "biosdk_version": __version__,
        "generated_at": now,
        "results": results,
        "metadata": metadata or {},
    }

    # Write manifest
    manifest_path = out / "manifest.json"
    manifest_path.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    # Sign with SHA256
    content = manifest_path.read_bytes()
    bundle_hash = hashlib.sha256(content).hexdigest()
    import os as _hmac_os
    _signing_key = _hmac_os.environ.get(
        "BIOSDK_SIGNING_KEY",
        "biosdk-evidence-v0.1"
    ).encode()
    signature = hmac.new(
        key=_signing_key,
        msg=content,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Write signature
    sig_data = {
        "bundle_sha256": bundle_hash,
        "signature_hmac_sha256": signature,
        "verified_at": now,
    }
    (out / "signature.json").write_text(
        json.dumps(sig_data, indent=2),
        encoding="utf-8",
    )

    return out.resolve()


def list_adapters() -> list[str]:
    """List all registered NSI-1.0 adapter IDs.

    Example:
        >>> biosdk.list_adapters()
        ['giroldini_mea', 'mcs_mea2100']
    """
    from biogpu.nsi.adapters import list_adapters as _list
    return _list()


def certified_adapters() -> list[str]:
    """List certified NSI-1.0 adapters from the plugin registry.

    Example:
        >>> biosdk.certified_adapters()
        ['mcs_mea2100']
    """
    from biogpu.plugins.manager_v72 import PluginRegistry
    registry = PluginRegistry()
    return [p.name for p in registry.list_certified()]


# ═══════════════════════════════════════════════════════════════════════
# Friendly console output
# ═══════════════════════════════════════════════════════════════════════

def __repr__() -> str:
    adapters = list_adapters()
    certified = certified_adapters()
    return (
        f"BioSDK v{__version__} — Vendor-Neutral Standard for Biological Neural Computation\n"
        f"  Adapters: {len(adapters)} registered ({', '.join(adapters)})\n"
        f"  Certified: {len(certified)} ({', '.join(certified) if certified else 'none'})\n"
        f"  API: open() → features() → readout() → evidence.bundle()"
    )
