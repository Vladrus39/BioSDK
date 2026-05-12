# BioGPU main goal

The main goal is **BioGPU**: to design and eventually implement a real working biological computing accelerator.

This repository must not drift into a generic MEA analysis toolkit. Public MEA/NWB/Allen data are used as the first proof layer and as a development substrate for the BioGPU software stack.

## Final target

```text
input/task
→ encoder
→ living neural substrate on MEA/HD-MEA
→ spike/raw response
→ feature extractor
→ readout/decoder
→ task output
→ benchmark against CPU/GPU/neuromorphic baselines
```

## What we have already proven with public data

1. Public Zenodo MEA data contain real spike responses.
2. Preprocessed data include `stimulation_protocol.csv` with `start/end/target` pulse windows.
3. 11,547 pulse windows were extracted.
4. Target electrode responses are above random electrode and random-time controls.
5. Candidate target-vs-non-target readouts generalize across cultures in quick local runs.
6. Raw spike-count-only features are already strong; pulse-context-only control stays near chance.

## What this proves

It proves a real public-data biological separability layer: neural response vectors contain extractable computational signal.

## What it does not prove yet

It does not yet prove that a live BioGPU is faster, cheaper, or more energy efficient than a silicon GPU. That requires a live hardware/lab phase.

## Project rule

Every new version must explicitly answer:

```text
How does this move us closer to a real working BioGPU?
```
