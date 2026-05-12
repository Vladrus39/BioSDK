# BioGPU-Core run results

## v0.8 status

Test command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

Current v0.8 expected result:

```text
39 passed, warnings expected from sklearn/matplotlib depending on environment
```

## v0.8 interpretation

v0.8 is a public-data development release.

It adds the infrastructure needed to move from generic spike profiling to real task-aligned spike benchmarks:

- stimulus-window mapping;
- task-aligned spike classification;
- DANDI candidate manifest;
- BRC reproduction template.

## What is measured now

Valid:

- spike ingestion;
- real spike profiling;
- feature extraction;
- task-aligned classification if windows come from real metadata.

Invalid:

- BioGPU performance claim from unlabeled spike times;
- synthetic labels attached to unrelated public spikes;
- claims that SimulatedMEA predicts wetware advantage.

## Next report target

v0.9 should include a first real-data report from either:

1. Zenodo 14363732 spike profile; or
2. DANDI 000469 task-aligned NWB windows; or
3. BRC author data/code if available.


## v0.9 status

v0.9 is a real-public-data release. It adds Zenodo manifest/download workflow, NWB stimulus discovery, BRC 2602.05737 reproduction contract, and public-data report generation. No new performance advantage is claimed in v0.9.
