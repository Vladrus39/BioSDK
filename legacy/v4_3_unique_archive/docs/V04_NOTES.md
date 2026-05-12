# biogpu-core v0.4 notes

v0.4 turns the v0.3 research scaffold into a more hardware-ready MVP.

## Added

- Vendor-neutral `RealMEAVendorNeutralAdapter` dry-run skeleton.
- `RealMEACapabilities` and `RealMEAConfig` contract classes.
- Configurable readout windows via `features.readout_bins` and `features.window_ms`.
- Reservoir memory/state metrics:
  - `temporal_trace_score`
  - `class_centroid_separability`
  - `reservoir_memory_report`
- Orientation benchmark HTML report now includes sample spike raster and activity map.
- API version updated to v0.4 with `/substrates/real-mea-contract`.
- Dockerfile and docker-compose path.
- `scripts/run_all_benchmarks.sh`.

## Safety note

The real MEA adapter is a contract only. It does not connect to hardware, does not
send electrical stimulation and does not define biological protocols. A real
implementation must be supplied by a qualified lab or equipment vendor SDK.

## Honest status

v0.4 still does not prove BioGPU advantage over silicon GPUs. It improves
engineering readiness, reproducibility, logging and future hardware integration.
