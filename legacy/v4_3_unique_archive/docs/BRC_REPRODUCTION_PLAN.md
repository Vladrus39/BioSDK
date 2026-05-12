# Biological Reservoir Computing Reproduction Plan

## Target

The strongest external architecture target is the 2026 BRC paper:

`Neuro-Inspired Visual Pattern Recognition via Biological Reservoir Computing` — arXiv:2602.05737.

The paper describes:

- in vitro cultured cortical neuronal network;
- HD-MEA stimulation and readout;
- spatially distributed input stimulation;
- high-dimensional neural responses;
- linear readout for visual pattern classification.

## Why it matters

This is closest to the BioGPU architecture:

```text
input pattern → HD-MEA stimulation → living reservoir → spike response → linear readout
```

## v0.8 support

Added:

```text
biogpu/data_ingest/brc_import.py
BRCExperimentSpec
scripts/create_public_data_templates.py
```

## Required next inputs

To reproduce the paper directly, BioGPU needs at least one of:

- released response feature matrices;
- spike times + stimulation windows;
- electrode maps + labels + splits;
- code repository from authors.

## Honest status

Until the data/code are available, this remains a target architecture, not a reproduced result.
