# BioGPU-Core v5.8 Raw-Native Benchmark Guide

## Purpose

v5.8 builds the first raw-native feature benchmark from the downloaded Zenodo 14363732 HDF5 archive.

It reads embedded HDF5 EventStream timestamps from v5.6, opens the corresponding raw HDF5 files, and extracts small analog `ChannelData` windows around each selected event. It never loads full waveform matrices into memory.

## What It Produces

The runner writes these artifacts under `outputs/v58_raw_native_benchmark/`:

- `V58_RAW_NATIVE_FEATURE_SUMMARY.json`
- `V58_RAW_NATIVE_FEATURE_MATRIX.npz`
- `V58_RAW_NATIVE_EVENT_METADATA.csv`
- `V58_RAW_NATIVE_EVENT_SOURCES.csv`
- `V58_RAW_NATIVE_CONDITION_READOUT.json`
- `BIOGPU_V58_RAW_NATIVE_BENCHMARK_REPORT.md`

The feature matrix contains raw-derived event-window features:

- response mean minus baseline mean per channel;
- response absolute mean minus baseline absolute mean per channel;
- response RMS minus baseline RMS per channel;
- response peak-to-peak per channel.

## Safety And Claim Boundary

This is an offline read-only raw-data benchmark. It does not perform live biology, hardware control, wet-lab stimulation or vendor writes.

It supports a raw-derived software benchmark over HDF5 event windows. It does not prove v15/v50 raw equivalence, GPU replacement, live BioGPU operation or energy superiority.

## Validation

Run the v5.8 gate on Windows:

```powershell
& .\scripts\run_biogpu_v58_raw_native_benchmark.ps1 -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
```

The default run samples up to 16 events per raw recording, extracts -20 ms / +80 ms windows, runs a held-out-recording condition readout, writes all artifacts, and runs focused synthetic HDF5 tests.
