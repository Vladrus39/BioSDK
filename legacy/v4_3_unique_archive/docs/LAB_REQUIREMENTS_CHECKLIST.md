# Real MEA stage — laboratory requirements checklist v0.6

## Goal

Move from SimulatedMEA to real MEA/HD-MEA data without pretending that software simulation proves wetware advantage.

## Minimum data needed for offline analysis

- electrode map;
- sampling rate;
- raw or spike-sorted activity;
- stimulation timestamps if present;
- stimulation channel/electrode IDs if present;
- culture/sample metadata at non-sensitive level;
- recording duration;
- any labels/tasks/stimulus metadata;
- quality flags if available.

## Minimum online/closed-loop requirements

- vendor SDK/API access;
- safe stimulation API controlled by lab team;
- real-time or near-real-time recording access;
- explicit stimulation limits from lab protocol;
- emergency stop / interlock process;
- logging of every stimulus and response;
- ethical/lab approval handled by the laboratory.

## What BioGPU-Core can provide

- data ingestion adapter;
- HDF5/NWB-like export;
- feature extraction;
- baseline-controlled decoder;
- repeated-run summaries;
- HTML reports;
- dashboard;
- analysis scripts;
- vendor-neutral adapter contract.

## What BioGPU-Core must not provide

- cell culture protocol;
- biological preparation instructions;
- unauthorized stimulation parameters;
- claims about consciousness/intelligence;
- medical or animal/human experimentation guidance.
