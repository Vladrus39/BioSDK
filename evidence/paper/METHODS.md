# Methods Draft v3.0

## Data layer

The project uses public MEA-derived data as the first evidence layer. Earlier versions constructed recording-level, spot-level and pulse-window analyses, then moved from analysis scripts toward a BioGPU runtime abstraction.

## Runtime contracts

```text
BioGPUJob -> BioGPU substrate -> BioGPUTrace -> feature/readout -> BioGPUResult
```

## Benchmark registry

The benchmark registry defines each task by input contract, encoder, substrate requirement, readout, metrics, controls, success gates and hardware readiness.

## Encoder/readout stack

The encoder layer maps digital task payloads into abstract biological patterns. The readout layer maps feature batches or traces into predictions and BioGPUResult objects. Both remain vendor-neutral and do not define live electrical parameters.

## Closed loop

```text
observation -> readout -> reward/error -> policy decision -> next abstract action
```

Current v3.0 closed-loop operation is dry-run/replay only.

## Energy/performance accounting

The energy model separates power components and latency components. It is a measurement scaffold, not a proof of advantage.
