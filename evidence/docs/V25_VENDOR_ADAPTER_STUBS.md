# BioGPU v2.5 — Vendor Adapter Stubs

v2.5 adds a vendor-adapter layer for future MEA/HD-MEA hardware integration.

## Purpose

The purpose is to make BioGPU-Core ready for real backends without rewriting the runtime later.
The same BioGPU runtime should be able to talk to:

- replay public-data substrate;
- dry-run vendor contract;
- future MCS MEA2100-class backend;
- future Axion Maestro-class backend;
- future 3Brain HD-MEA-class backend;
- future remote wetware API backend.

## Standard adapter contract

```text
connect()
validate_session(manifest)
send_stimulation_pattern(command)
read_spike_stream(duration_s)
read_raw_trace(duration_s)
export_metadata()
close()
```

## What is intentionally not included

- vendor pinout;
- physical wiring instruction;
- live electrical stimulation values;
- live tissue safety limits;
- wet-lab culturing recipe;
- device-specific SDK calls.

## Why

Those details must come from vendor documentation, approved SOPs and qualified lab validation.
The repository should provide the software architecture and audit contract, not unsafe live-lab instructions.
