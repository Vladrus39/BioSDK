from __future__ import annotations

from fastapi import FastAPI

from biogpu.benchmarks.ablation import main as run_ablation
from biogpu.benchmarks.delayed_match import main as run_delayed_match
from biogpu.benchmarks.noise import main as run_noise
from biogpu.benchmarks.orientation import main as run_orientation
from biogpu.benchmarks.sequence import main as run_sequence
from biogpu.benchmarks.streaming import main as run_streaming
from biogpu.substrates import RealMEAVendorNeutralAdapter, RealMEAConfig, MaxOneLikeDryRunAdapter

app = FastAPI(title="BioGPU Core API", version="0.9.0")


@app.get("/health")
def health():
    return {"status": "ok", "project": "biogpu-core", "version": "0.9"}


@app.get("/substrates")
def substrates():
    return {
        "available": ["SimulatedMEA", "RealMEAVendorNeutralAdapter(dry-run)"],
        "future": ["HD-MEA", "OrganoidMEA", "NeuromorphicChip", "MemristorArray"],
    }


@app.get("/substrates/real-mea-contract")
def real_mea_contract():
    adapter = RealMEAVendorNeutralAdapter(RealMEAConfig(electrode_count=0))
    return adapter.health_check()


@app.get("/substrates/maxone-like-contract")
def maxone_like_contract():
    adapter = MaxOneLikeDryRunAdapter()
    return adapter.health_check()


@app.post("/benchmarks/orientation")
def benchmark_orientation(config: str = "configs/orientation.yaml"):
    return run_orientation(config)


@app.post("/benchmarks/noise")
def benchmark_noise(config: str = "configs/noise.yaml"):
    return run_noise(config)


@app.post("/benchmarks/sequence")
def benchmark_sequence(config: str = "configs/sequence.yaml"):
    return run_sequence(config)


@app.post("/benchmarks/delayed-match")
def benchmark_delayed_match(config: str = "configs/delayed_match.yaml"):
    return run_delayed_match(config)


@app.post("/benchmarks/ablation")
def benchmark_ablation(config: str = "configs/ablation.yaml"):
    return run_ablation(config)


@app.post("/benchmarks/streaming")
def benchmark_streaming(config: str = "configs/streaming.yaml"):
    return run_streaming(config)


@app.get("/public-data/sources")
def public_data_sources():
    return {"zenodo_14363732": {"adapter": "ZenodoMEA2100SpikeTxtAdapter", "status": "offline TXT spike ingestion"}, "dandi_nwb": {"adapter": "DandiNWBSpikeAdapter", "status": "local NWB units/spike_times ingestion"}}

@app.get("/public-data/dandi-candidates")
def public_data_dandi_candidates():
    from biogpu.data_ingest.dandi_discovery import candidates_as_dict
    return {"candidates": candidates_as_dict()}


@app.get("/public-data/task-aligned-contract")
def public_data_task_aligned_contract():
    return {
        "required": ["spike_source", "stimulus_windows"],
        "stimulus_window_columns": ["start_s", "end_s", "label"],
        "optional_columns": ["stimulus_id", "split"],
        "honesty_rule": "classification claims require real stimulus/behavior windows, not synthetic labels",
    }


@app.get("/public-data/zenodo-14363732-manifest")
def public_data_zenodo_manifest():
    from biogpu.data_ingest.zenodo_manifest import zenodo_manifest_dict
    return zenodo_manifest_dict()

@app.get("/public-data/brc2602-contract")
def public_data_brc2602_contract():
    from biogpu.data_ingest.brc2602_import import minimal_brc2602_contract
    return minimal_brc2602_contract()

@app.get("/public-data/nwb-discovery-contract")
def public_data_nwb_discovery_contract():
    return {"purpose":"Inspect local NWB files for /units, /intervals, /stimulus and build real stimulus_windows.csv.","commands":["python -m biogpu.cli public-data nwb-discover path/to/file.nwb --output outputs/reports/nwb_discovery.json","python -m biogpu.cli public-data task-aligned path/to/file.nwb path/to/stimulus_windows.csv --source-type nwb"],"honesty_rule":"Labels must come from real stimulus/behavior metadata, not synthetic post-hoc labeling."}
