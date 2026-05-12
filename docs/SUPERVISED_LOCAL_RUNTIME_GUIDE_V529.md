# BioGPU-Core v5.29 Supervised Local Runtime Guide

v5.29 adds a deterministic local supervisor over the v5.28 authenticated service.

It proves:

- runtime start creates a state file with process ID and runtime ID;
- heartbeat updates are written to a heartbeat file;
- supervised worker ticks process queued safe jobs and then report idle;
- graceful shutdown moves the runtime to `stopped` and blocks later worker ticks;
- JSONL audit events can be exported with a SHA-256 audit hash;
- production runtime, production daemon and BiC OS readiness remain blocked.

Run the gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v529_supervised_runtime.ps1
```

Outputs are written under `outputs/v529_supervised_local_runtime/`.

This is an in-process local supervisor proof, not an installed OS service, not a hosted runtime and not a live wetware control process.
