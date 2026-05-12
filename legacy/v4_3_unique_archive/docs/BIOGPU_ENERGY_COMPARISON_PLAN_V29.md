# BioGPU Energy Comparison Plan v2.9

## Measurement levels

1. **Replay accounting** — software-only, no live substrate claim.
2. **Dry-run hardware accounting** — MEA backend absent, validates logging and bundle format.
3. **Live-lab telemetry** — measured host + electronics + environment + substrate I/O.
4. **GPU/CPU/neuromorphic comparison** — same benchmark registry, same task, same accuracy gate.

## Claim gate

BioGPU may only claim an advantage when it beats a baseline under the same measurement boundary.

Minimum fields:

- benchmark id;
- task count;
- run duration;
- accuracy / AUC / success gate;
- total wall power or integrated energy;
- latency distribution;
- environment overhead inclusion/exclusion;
- result bundle checksum.
