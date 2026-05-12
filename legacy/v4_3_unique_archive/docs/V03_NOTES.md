# v0.3 Notes

v0.3 turns the project from a simple simulated reservoir demo into a more serious benchmark scaffold.

## Added

- Improved `SimulatedMEA` dynamics with recurrent strength, trace memory and reset.
- `Delayed Match` benchmark for cue memory across delay frames.
- `Reservoir Ablation` benchmark.
- Static HTML report/dashboard generator.
- Plot utilities for bars, noise curves, activity maps and spike rasters.
- API endpoints for all current benchmarks.
- Additional tests.

## Not proven

- No claim of outperforming GPU/CPU.
- No claim of biological energy advantage.
- No wetware result yet.
- Current reservoir still needs better dynamics and more stable task contribution.

## Next v0.4 targets

- Add recurrent memory metrics.
- Add richer temporal tasks.
- Add configurable readout windows.
- Add spike raster figures from actual benchmark runs.
- Add containerized run path.
- Add real MEA adapter skeleton with vendor-neutral data contracts.
