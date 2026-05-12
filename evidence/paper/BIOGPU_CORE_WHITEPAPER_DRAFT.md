# BioGPU-Core Whitepaper Draft

## Abstract

BioGPU-Core is a software and benchmark framework for designing a biological computing accelerator based on living neuronal substrates interfaced through MEA/HD-MEA systems. Current versions use public real MEA datasets as replay substrates, demonstrating pulse-aligned biological response separability and a hardware-neutral runtime contract. The long-term goal is a live closed-loop BioGPU prototype with measured task and energy comparisons against silicon baselines.

## Current evidence

BioGPU-Core has processed public MEA data into 11,547 pulse windows, built spike-response feature matrices, and shown target-vs-nontarget separability above shuffled controls in culture-aware splits.

## Architecture

```text
BioGPUJob -> living/replay substrate -> BioGPUTrace -> readout -> BioGPUResult
```

## First material

2D lab-grown neuronal culture on MEA/HD-MEA.

## Limitations

Current data do not prove live hardware operation or GPU superiority. Those require a physical MEA/HD-MEA system and energy measurement.
