# BioGPU Hardware Architecture

First real BioGPU will be a lab module, not immediately a PCIe card.

## Layers

1. Living substrate cartridge — neurons on MEA/HD-MEA.
2. MEA/HD-MEA interface — stimulation and recording.
3. Environmental control — temperature, medium, viability.
4. Real-time controller — Python/vendor SDK/DAQ.
5. BioGPU software core — runtime, logs, readouts, benchmarks.

## Must measure

- channel count,
- sampling rate,
- stimulation timing precision,
- loop latency and jitter,
- firing stability,
- response repeatability,
- biological lifetime,
- total energy per task.
