# BioGPU Vendor Backend Implementation Plan

## Stage 1 — current v2.5

- Dry-run adapter contract.
- Capability matrix.
- Safe abstract command envelope.
- No live output.

## Stage 2 — selected platform backend

After choosing a concrete platform, create a private/live backend module that maps the standard BioGPU adapter contract to the vendor SDK.

Required before enabling live output:

- vendor SDK/manuals reviewed;
- hardware capability table confirmed;
- lab SOP approved;
- electrical safety gates defined by qualified personnel;
- live audit logging enabled;
- emergency stop / interlock behavior confirmed;
- mock run and replay run pass before live session.

## Stage 3 — live-lab integration

- `run_mode = live_lab` manifest;
- adapter mode switched from dry-run to live backend;
- stimulation commands translated only after passing safety gates;
- every command and trace exported into a result bundle.

## Stage 4 — BioGPU proof run

- execute B0/B1/B2 first;
- compare to replay results;
- measure latency and stability;
- only then attempt adaptive closed-loop benchmarks.
