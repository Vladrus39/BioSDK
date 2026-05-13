"""
BioSDK CLI — Command-line interface for BioSDK.

Usage:
    biosdk open <file>              Auto-detect format, show metadata
    biosdk features <file>          Extract NSI-1.0 feature vectors
    biosdk readout <file> <labels>  Classify with sklearn baselines
    biosdk evidence <dir>           Create signed evidence bundle
    biosdk os start|stop|status     BioCompute OS control
    biosdk benchmark <file>         Run BioReservoir benchmark

Entry point defined in pyproject.toml:
    [project.scripts]
    biosdk = "biosdk.cli:main"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# ── Ensure the parent package is importable ──
_BIOSDK_ROOT = Path(__file__).resolve().parent.parent
if str(_BIOSDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_BIOSDK_ROOT))

from biosdk import __version__


def cmd_open(args: argparse.Namespace) -> int:
    """Open a neural recording and display metadata."""
    from biosdk import open as biosdk_open

    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        return 1

    print(f"BioSDK v{__version__} — open {path.name}")
    try:
        ds = biosdk_open(str(path), vendor=args.vendor)
    except Exception as e:
        print(f"Error opening file: {e}")
        return 1

    meta = ds.metadata
    print(f"  Vendor:      {meta.vendor}")
    print(f"  Format:      {meta.format}")
    print(f"  Channels:    {meta.channel_count}")
    print(f"  Samples:     {meta.sample_count}")
    print(f"  Sample rate: {meta.sample_rate_hz} Hz")
    print(f"  Duration:    {meta.duration_s:.1f}s")
    if hasattr(meta, 'subject_id') and meta.subject_id:
        print(f"  Subject:     {meta.subject_id}")
    if hasattr(meta, 'recording_date') and meta.recording_date:
        print(f"  Recorded:    {meta.recording_date}")
    print(f"  Features:    {meta.feature_names}")
    if ds.data is not None:
        print(f"  Data shape:  {ds.data.shape}")

    return 0


def cmd_features(args: argparse.Namespace) -> int:
    """Extract NSI-1.0 feature vectors from a recording."""
    from biosdk import open as biosdk_open
    from biosdk import features as biosdk_features

    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        return 1

    print(f"BioSDK v{__version__} — features from {path.name}")
    try:
        ds = biosdk_open(str(path), vendor=args.vendor)
    except Exception as e:
        print(f"Error opening file: {e}")
        return 1

    t0 = time.perf_counter()
    X = biosdk_features(ds, window_s=args.window, overlap=args.overlap,
                        max_windows=args.max_windows)
    dt = time.perf_counter() - t0

    print(f"  Windows:     {X.shape[0]}")
    print(f"  Features:    {X.shape[1]} (={X.shape[1] // ds.metadata.channel_count} per channel × {ds.metadata.channel_count} ch)")
    print(f"  Shape:       {X.shape}")
    print(f"  Time:        {dt:.2f}s")
    print(f"  Mean:        {X.mean():.4f}")
    print(f"  Std:         {X.std():.4f}")

    if args.output:
        np.save(args.output, X)
        print(f"  Saved:       {args.output}")

    return 0


def cmd_readout(args: argparse.Namespace) -> int:
    """Run classification readout on extracted features."""
    import numpy as np
    from biosdk import open as biosdk_open
    from biosdk import features as biosdk_features
    from biosdk import readout as biosdk_readout

    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        return 1

    labels_path = Path(args.labels)
    if not labels_path.exists():
        print(f"Error: Labels file not found: {labels_path}")
        return 1

    print(f"BioSDK v{__version__} — readout on {path.name}")

    try:
        ds = biosdk_open(str(path), vendor=args.vendor)
    except Exception as e:
        print(f"Error opening file: {e}")
        return 1

    X = biosdk_features(ds, window_s=args.window, overlap=args.overlap,
                        max_windows=args.max_windows)

    # Load labels (one per window)
    y = np.loadtxt(labels_path, dtype=np.int32)
    if len(y.shape) == 0:
        y = np.array([y])
    if len(y) != X.shape[0]:
        print(f"Warning: labels ({len(y)}) != windows ({X.shape[0]}). Min-aligning.")
        n = min(len(y), X.shape[0])
        y = y[:n]
        X = X[:n]

    result = biosdk_readout(X, y, classifier=args.classifier, cv_folds=args.cv)
    print(f"  Classifier:  {result['classifier']}")
    print(f"  BA:          {result['balanced_accuracy']:.4f} ± {result['cv_std']:.4f}")
    print(f"  Samples:     {result['n_samples']}")
    print(f"  Features:    {result['n_features']}")
    print(f"  CV folds:    {result['cv_folds']}")
    if result.get('per_class'):
        print(f"  Per-class:")
        for cls, metrics in sorted(result['per_class'].items()):
            print(f"    class {cls}: recall={metrics['recall']:.3f}, "
                  f"precision={metrics['precision']:.3f}, n={metrics['n']}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"  Saved:       {args.output}")

    return 0


def cmd_evidence(args: argparse.Namespace) -> int:
    """Create a signed evidence bundle from benchmark results."""
    from biosdk import evidence_bundle

    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Error: Results file not found: {results_path}")
        return 1

    with open(results_path) as f:
        results = json.load(f)

    print(f"BioSDK v{__version__} — evidence bundle")
    try:
        bundle_path = evidence_bundle(
            results,
            output_dir=args.output,
            metadata=json.loads(args.meta) if args.meta else None,
        )
    except Exception as e:
        print(f"Error creating bundle: {e}")
        return 1

    print(f"  Bundle:      {bundle_path}")
    print(f"  Manifest:    {bundle_path / 'manifest.json'}")
    print(f"  Signature:   {bundle_path / 'signature.json'}")

    # Verify
    sig_path = bundle_path / "signature.json"
    if sig_path.exists():
        with open(sig_path) as f:
            sig = json.load(f)
        print(f"  SHA256:      {sig['bundle_sha256'][:16]}...")
        print(f"  HMAC:        {sig['signature_hmac_sha256'][:16]}...")

    return 0


def cmd_os(args: argparse.Namespace) -> int:
    """Control BioCompute OS daemon."""
    from biogpu.production.biocompute_os_v30 import (
        BioComputeOS, get_os, stop_os,
    )

    if args.os_command == "start":
        os = get_os(".")
        health = os.health_check()
        print(f"BioSDK v{__version__} — BioCompute OS v{health['version']}")
        print(f"  Status:      started")
        print(f"  Workers:     {health['scheduler']['max_workers']}")
        print(f"  Devices:     {health['device_manager']['n_devices']}")
        print(f"  Adapters:    {len(health['adapters'])}")
        print(f"  Safety:      {health['safety_gates']} gates")
        print(f"  Dashboard:   http://127.0.0.1:8420 (if running)")
        print(f"  State dir:   outputs/os_state/")

    elif args.os_command == "stop":
        stop_os()
        print(f"BioSDK v{__version__} — OS stopped")

    elif args.os_command == "status":
        try:
            from biogpu.production.biocompute_os_v30 import _os_instance
            os = _os_instance
            if os and os._daemon_running:
                health = os.health_check()
                print(f"BioSDK v{__version__} — OS status")
                print(f"  Version:     {health['version']}")
                print(f"  Uptime:      {health['uptime_seconds']:.0f}s")
                print(f"  Daemon:      {health['daemon']}")
                print(f"  Jobs:        {health['scheduler']['total_jobs']} total, "
                      f"{health['scheduler']['by_status'].get('completed', 0)} done")
                print(f"  Queue:       {health['scheduler']['queue_depth']} pending")
                print(f"  Devices:     {health['device_manager']['n_devices']} "
                      f"({health['device_manager']['online']} online)")
            else:
                print(f"BioSDK v{__version__} — OS not running")
        except Exception:
            print(f"BioSDK v{__version__} — OS not running")

    elif args.os_command == "jobs":
        try:
            from biogpu.production.biocompute_os_v30 import _os_instance
            os = _os_instance
            if os:
                jobs = os.list_jobs()
                print(f"BioSDK v{__version__} — OS jobs ({len(jobs)})")
                for j in jobs[:20]:
                    dur = ""
                    if j.get("started_at") and j.get("completed_at"):
                        dur = f", {j['completed_at'][:19]}"
                    print(f"  {j['job_id']}: {j['task']} [{j['status']}] "
                          f"created={j['created_at'][:19]}{dur}")
            else:
                print("OS not running")
        except Exception:
            print("OS not running")

    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Run BioReservoir benchmark on given data."""
    import numpy as np
    from pathlib import Path

    print(f"BioSDK v{__version__} — BioReservoir benchmark")
    print(f"  NOTE: Full benchmark requires biogpu runtime with mock FinalSpark API.")
    print(f"  Run: python _biogpu_v4_benchmark.py for the full pipeline.")

    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: File not found: {path}")
            return 1
        print(f"  Input: {path}")

    print(f"  Reservoir:   BioReservoirV40 (Izhikevich + STDP + small-world)")
    print(f"  Readout:     RidgeClassifier (5-fold CV)")
    print(f"  Baseline:    sklearn RandomForest, LogisticRegression")

    # Try running quick benchmark if data available
    try:
        from biogpu.substrates.bio_reservoir_v40 import BioReservoirV40
        r = BioReservoirV40(seed=42, reservoir_units=args.units)
        health = r.health_check()
        print(f"\n  Reservoir health check:")
        print(f"    Units:      {health['num_units']}")
        print(f"    Types:      {health['num_types']} ({health['type_distribution']})")
        print(f"    Synapses:   {health['synaptic_count']}")
        print(f"    Density:    {health['connectivity_density']:.3f}")
        print(f"    E/I ratio:  {health['excitatory_ratio']:.1%} excitatory")
        print(f"    STDP:       {'enabled' if health['stdp_enabled'] else 'disabled'}")
        print(f"    Numba:      {'active' if health.get('numba_enabled') else 'inactive'} "
              f"(v{health.get('numba_version', '?')})")
        r.close()
    except Exception as e:
        print(f"  Health check failed: {e}")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List available adapters, certified plugins."""
    from biosdk import list_adapters, certified_adapters

    print(f"BioSDK v{__version__} — Available adapters")
    adapters = list_adapters()
    certified = certified_adapters()
    print(f"  Registered:  {len(adapters)}")
    for a in adapters:
        cert = " [certified]" if a in certified else ""
        print(f"    - {a}{cert}")
    print(f"  Certified:   {len(certified)}")

    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Print BioSDK version and system info."""
    print(f"BioSDK v{__version__}")
    print(f"  Python:      {sys.version}")

    try:
        from biogpu.substrates.bio_reservoir_v40 import _HAS_NUMBA, _numba_version
        print(f"  Numba:       {'available' if _HAS_NUMBA else 'not installed'} "
              f"({_numba_version() if _HAS_NUMBA else ''})")
    except Exception:
        print(f"  Numba:       not checked")

    try:
        from biogpu.apis.mock_finalspark_api import SpikeEventCache
        c = SpikeEventCache()
        n = c.load_from_cache(max_files=1)
        print(f"  Data cache:  {n} MEAs available (mock FinalSpark API)")
    except Exception:
        print(f"  Data cache:  not checked")

    return 0


# ═══════════════════════════════════════════════════════════════════════
# Main CLI entry point
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="biosdk",
        description=f"BioSDK v{__version__} — Vendor-Neutral Standard for Biological Neural Computation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  biosdk open recording.h5                    # Show metadata
  biosdk features recording.h5 --window 0.5   # Extract features
  biosdk readout recording.h5 labels.txt       # Classify
  biosdk evidence results.json -o bundle/      # Evidence bundle
  biosdk os start                              # Start OS daemon
  biosdk list                                  # List adapters
  biosdk benchmark                             # Reservoir health
  biosdk version                               # Version info
        """,
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    sub = parser.add_subparsers(dest="command", help="Commands")

    # open
    p_open = sub.add_parser("open", help="Open a neural recording and show metadata")
    p_open.add_argument("path", help="Path to data file (HDF5, NWB, EDF, CSV)")
    p_open.add_argument("--vendor", "-v", default="auto",
                        help="Vendor hint: mcs, giroldini, dandi, edf, gcp2 (default: auto)")
    p_open.set_defaults(func=cmd_open)

    # features
    p_feat = sub.add_parser("features", help="Extract NSI-1.0 feature vectors")
    p_feat.add_argument("path", help="Path to data file")
    p_feat.add_argument("--vendor", "-v", default="auto", help="Vendor hint")
    p_feat.add_argument("--window", "-w", type=float, default=0.5,
                        help="Window size in seconds (default: 0.5)")
    p_feat.add_argument("--overlap", "-o", type=float, default=0.0,
                        help="Overlap fraction 0.0-1.0 (default: 0.0)")
    p_feat.add_argument("--max-windows", "-n", type=int, default=None,
                        help="Max windows to extract")
    p_feat.add_argument("--output", "-O", default=None,
                        help="Save features to .npy file")
    p_feat.set_defaults(func=cmd_features)

    # readout
    p_read = sub.add_parser("readout", help="Run classification readout")
    p_read.add_argument("path", help="Path to data file")
    p_read.add_argument("labels", help="Path to labels file (one per line)")
    p_read.add_argument("--vendor", "-v", default="auto", help="Vendor hint")
    p_read.add_argument("--window", "-w", type=float, default=0.5,
                        help="Window size in seconds")
    p_read.add_argument("--overlap", "-o", type=float, default=0.0,
                        help="Overlap fraction")
    p_read.add_argument("--max-windows", "-n", type=int, default=None)
    p_read.add_argument("--classifier", "-c", default="rf",
                        choices=["rf", "lr", "svm"],
                        help="Classifier: rf (RandomForest), lr (Logistic), svm (SVM)")
    p_read.add_argument("--cv", type=int, default=5,
                        help="CV folds (default: 5)")
    p_read.add_argument("--output", "-O", default=None,
                        help="Save results to JSON")
    p_read.set_defaults(func=cmd_readout)

    # evidence
    p_ev = sub.add_parser("evidence", help="Create signed evidence bundle")
    p_ev.add_argument("results", help="Path to benchmark results JSON")
    p_ev.add_argument("--output", "-o", default="evidence_bundle",
                      help="Output directory (default: evidence_bundle)")
    p_ev.add_argument("--meta", "-m", default=None,
                      help="Extra metadata as JSON string")
    p_ev.set_defaults(func=cmd_evidence)

    # os
    p_os = sub.add_parser("os", help="BioCompute OS control")
    p_os.add_argument("os_command", nargs="?", default="status",
                      choices=["start", "stop", "status", "jobs"],
                      help="OS command: start, stop, status, jobs")
    p_os.set_defaults(func=cmd_os)

    # benchmark
    p_bench = sub.add_parser("benchmark", help="BioReservoir benchmark")
    p_bench.add_argument("path", nargs="?", default=None,
                         help="Path to data file (optional)")
    p_bench.add_argument("--units", "-u", type=int, default=128,
                         help="Reservoir units (default: 128)")
    p_bench.add_argument("--task", "-t", default="temporal",
                         help="Task: temporal, cross_modal, closed_loop")
    p_bench.set_defaults(func=cmd_benchmark)

    # list
    p_list = sub.add_parser("list", help="List available adapters")
    p_list.set_defaults(func=cmd_list)

    # version (subcommand)
    p_ver = sub.add_parser("version", help="Show version and system info")
    p_ver.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if args.version or (args.command is None and not hasattr(args, 'func')):
        return cmd_version(args)
    elif hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
