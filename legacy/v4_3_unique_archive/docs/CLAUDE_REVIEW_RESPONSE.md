# Response to external review / Claude note — v0.6

## Position

We agree with the core critique.

The v0.5 project has become a useful research scaffold, but the simulated reservoir has not produced a stable scientific performance signal. Infrastructure improved strongly; reservoir accuracy did not.

## What the v0.5 numbers imply

The important warning signs are:

- Orientation and noise benchmarks regressed across versions.
- In at least one ablation, removing recurrent memory improves accuracy.
- Some reservoir outputs are below shuffled/random baselines.
- The best signal appears only in delayed/streaming memory-style tasks, and even there it is weak.

## Project decision

v0.6 is a pivot release.

We stop treating further SimulatedMEA tuning as the main research path. From now on, SimulatedMEA is used for:

1. interface validation;
2. reproducibility testing;
3. adapter contract testing;
4. benchmark protocol development;
5. data-format preparation.

It is not used as evidence that BioGPU outperforms digital hardware.

## New rule

No performance claim is accepted unless it passes:

1. repeated-seed evaluation;
2. shuffled/random reservoir comparison;
3. raw digital baseline comparison;
4. ablation analysis;
5. task-specific interpretation;
6. energy accounting when physical hardware exists.

## Strategic pivot

The next real signal must come from one of two external paths:

1. neuromorphic hardware path — Loihi 2 / Lava / SpiNNaker-like execution;
2. wetware path — MEA/HD-MEA lab, public dataset, or remote neural platform.

`biogpu-core` remains valuable because it provides the measurement scaffold for these paths.
