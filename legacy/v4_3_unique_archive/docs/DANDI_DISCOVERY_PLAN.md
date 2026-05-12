# DANDI Discovery Plan

## Goal

Find public NWB datasets that contain both spike/unit data and real stimulus/behavior metadata.

## Starter candidates

### DANDI 000469

Human single-neuron Sternberg working-memory dataset. Public notes indicate NWB files include spike times, waveforms, stimuli, behavior, electrode locations and subject demographics.

Use:

```bash
dandi download https://dandiarchive.org/dandiset/000469
```

Role:

- task-aligned working-memory spike benchmark;
- not MEA reservoir, but good for real spike/stimulus mapping.

### DANDI 000673

Working-memory intracranial candidate referenced in public code resources. Needs local NWB inspection.

## Discovery scoring

A DANDI dataset is high value for BioGPU if metadata/assets contain:

```text
ecephys
units
spike_times
stimulus
behavior
trials/intervals
task labels
```

## v0.8 status

biogpu-core includes a curated candidate manifest and a keyword scoring helper. Full online DANDI API crawling is deferred to v0.9.
