from __future__ import annotations

import argparse
import json
from pathlib import Path


def _run_benchmark(name: str, config: str) -> dict:
    if name == "orientation":
        from biogpu.benchmarks.orientation import main
    elif name == "noise":
        from biogpu.benchmarks.noise import main
    elif name == "sequence":
        from biogpu.benchmarks.sequence import main
    elif name in {"delayed", "delayed-match", "delayed_match"}:
        from biogpu.benchmarks.delayed_match import main
    elif name == "streaming":
        from biogpu.benchmarks.streaming import main
    elif name == "ablation":
        from biogpu.benchmarks.ablation import main
    else:
        raise SystemExit(f"Unknown benchmark: {name}")
    return main(config)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="biogpu-run", description="BioGPU Core research CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("benchmark", help="Run one benchmark")
    run.add_argument("name", choices=["orientation", "noise", "sequence", "delayed-match", "streaming", "ablation"])
    run.add_argument("--config", default=None)

    contract = sub.add_parser("contract", help="Print adapter contracts")
    contract.add_argument("name", choices=["real-mea", "maxone-like"])

    validate_nsi = sub.add_parser("validate-nsi", help="Validate NSI-1.0 JSON payloads")
    from biogpu.standards.nsi_cli_v52 import add_validate_nsi_arguments
    add_validate_nsi_arguments(validate_nsi)

    public = sub.add_parser("public-data", help="Inspect/profile public spike datasets")
    public_sub = public.add_subparsers(dest="public_command", required=True)
    zen = public_sub.add_parser("zenodo-profile")
    zen.add_argument("root_path")
    zen.add_argument("--window-ms", type=float, default=1000.0)
    zen.add_argument("--glob", default="**/*.txt")
    zen.add_argument("--time-unit", default="s")
    dn = public_sub.add_parser("dandi-profile")
    dn.add_argument("nwb_path")
    dn.add_argument("--window-ms", type=float, default=1000.0)
    dd = public_sub.add_parser("dandi-candidates")
    dd.add_argument("--output", default=None)
    zm = public_sub.add_parser("zenodo-manifest")
    zm.add_argument("--output", default=None)
    nd = public_sub.add_parser("nwb-discover")
    nd.add_argument("nwb_path")
    nd.add_argument("--output", default=None)
    brc = public_sub.add_parser("brc2602-contract")
    brc.add_argument("--output", default=None)
    pdr = public_sub.add_parser("status-report")
    pdr.add_argument("--output", default="outputs/reports/public_data_status_v09.md")
    ta = public_sub.add_parser("task-aligned")
    ta.add_argument("spike_source")
    ta.add_argument("windows_path")
    ta.add_argument("--source-type", default="txt", choices=["txt", "nwb", "zenodo_txt", "dandi_nwb"])
    ta.add_argument("--time-unit", default="s")
    ta.add_argument("--train-fraction", type=float, default=0.7)
    ta.add_argument("--seed", type=int, default=1)
    ta.add_argument("--readout-bins", type=int, default=4)

    args = parser.parse_args(argv)
    if args.command == "benchmark":
        config = args.config or f"configs/{args.name.replace('-', '_')}.yaml"
        if args.name == "delayed-match" and args.config is None:
            config = "configs/delayed_match.yaml"
        result = _run_benchmark(args.name, config)
        print(json.dumps({"benchmark": result.get("benchmark"), "metrics": result.get("metrics")}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "contract":
        if args.name == "real-mea":
            from biogpu.substrates.real_mea_base import RealMEAVendorNeutralAdapter
            adapter = RealMEAVendorNeutralAdapter()
        else:
            from biogpu.substrates.maxone_like import MaxOneLikeDryRunAdapter
            adapter = MaxOneLikeDryRunAdapter()
        print(json.dumps(adapter.health_check(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "validate-nsi":
        from biogpu.standards.nsi_cli_v52 import run_validate_nsi
        return run_validate_nsi(args)

    if args.command == "public-data":
        if args.public_command == "zenodo-profile":
            from biogpu.benchmarks.real_spike_profile import run_zenodo_profile
            result = run_zenodo_profile(args.root_path, args.window_ms, args.glob, args.time_unit)
            print(json.dumps({"benchmark": result.get("benchmark"), "metrics": result.get("metrics"), "health": result.get("health")}, ensure_ascii=False, indent=2))
        elif args.public_command == "dandi-profile":
            from biogpu.benchmarks.real_spike_profile import run_dandi_profile
            result = run_dandi_profile(args.nwb_path, args.window_ms)
            print(json.dumps({"benchmark": result.get("benchmark"), "metrics": result.get("metrics"), "health": result.get("health")}, ensure_ascii=False, indent=2))
        elif args.public_command == "dandi-candidates":
            from biogpu.data_ingest.dandi_discovery import candidates_as_dict, write_candidate_manifest
            if args.output:
                path = write_candidate_manifest(args.output)
                print(json.dumps({"written": str(path), "count": len(candidates_as_dict())}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"candidates": candidates_as_dict()}, ensure_ascii=False, indent=2))
        elif args.public_command == "zenodo-manifest":
            from biogpu.data_ingest.zenodo_manifest import zenodo_manifest_dict, write_zenodo_manifest
            if args.output:
                path = write_zenodo_manifest(args.output)
                print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(zenodo_manifest_dict(), ensure_ascii=False, indent=2))
        elif args.public_command == "nwb-discover":
            from biogpu.data_ingest.nwb_stimulus_discovery import inspect_nwb_structure, discover_stimulus_tables, write_nwb_discovery_report
            if args.output:
                path = write_nwb_discovery_report(args.nwb_path, args.output)
                print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"structure": inspect_nwb_structure(args.nwb_path), "stimulus_table_candidates": [c.__dict__ for c in discover_stimulus_tables(args.nwb_path)]}, ensure_ascii=False, indent=2))
        elif args.public_command == "brc2602-contract":
            from biogpu.data_ingest.brc2602_import import minimal_brc2602_contract, write_brc2602_contract
            if args.output:
                path = write_brc2602_contract(args.output)
                print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(minimal_brc2602_contract(), ensure_ascii=False, indent=2))
        elif args.public_command == "status-report":
            from biogpu.data_ingest.public_data_report import write_public_data_status_report
            path = write_public_data_status_report(args.output)
            print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
        elif args.public_command == "task-aligned":
            from biogpu.benchmarks.task_aligned_real import run_task_aligned_spike_benchmark
            result = run_task_aligned_spike_benchmark(
                args.spike_source,
                args.windows_path,
                source_type=args.source_type,
                time_unit=args.time_unit,
                train_fraction=args.train_fraction,
                seed=args.seed,
                readout_bins=args.readout_bins,
            )
            print(json.dumps({"benchmark": result.get("benchmark"), "metrics": result.get("metrics"), "window_summary": result.get("window_summary")}, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
