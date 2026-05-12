# biogpu-core v0.8 — Real Data Development Notes

## Purpose

v0.8 pivots BioGPU from simulated-only development into real public-data development.

The key correction is methodological:

- generic public spike data can validate ingestion, feature extraction and state profiling;
- task-aligned spike data with real stimulus/behavior windows is required for classification claims;
- SimulatedMEA remains an engineering scaffold, not evidence of BioGPU performance.

## New modules

```text
biogpu/data_ingest/stimulus_windows.py
biogpu/data_ingest/dandi_discovery.py
biogpu/data_ingest/brc_import.py
biogpu/benchmarks/task_aligned_real.py
scripts/create_public_data_templates.py
configs/task_aligned_real.yaml
configs/public_data_sources.yaml
```

## New CLI commands

```bash
python -m biogpu.cli public-data dandi-candidates
python -m biogpu.cli public-data dandi-candidates --output data/templates/dandi_candidates.json
python -m biogpu.cli public-data task-aligned spikes.txt windows.csv --source-type txt
```

## Real data honesty rule

Do not map synthetic labels onto unrelated spike times. A task-aligned benchmark is only valid if `stimulus_windows.csv` was derived from real experimental stimulus/behavior metadata.

Required columns:

```csv
start_s,end_s,label
```

Optional columns:

```csv
stimulus_id,split
```

## Public sources tracked

- Zenodo record 14363732 — MEA2100 raw HDF5 + preprocessed spike times; good for real spike ingestion/profiling.
- DANDI 000469 — human single-neuron Sternberg working-memory task; strong candidate for task-aligned NWB analysis.
- DANDI 000673 — candidate working-memory intracranial dataset pending inspection.
- arXiv 2602.05737 — closest external biological reservoir computing target; needs data/code access or author contact for reproduction.

## Next step

v0.9 should run the pipeline on downloaded public files and generate the first real-data report.
