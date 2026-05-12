# BioGPU-Core v4.9 — Naming Correction + BiC OS Strategy

## Decision

Keep **BioGPU-Core** as the repository and technical kernel name.

Use the following product hierarchy:

```text
BioGPU-Core                  technical kernel / repository / history
BioSDK / Living Compute SDK  developer-facing SDK layer
BioCompute Runtime           near-term external product category
NSI-1.0                      Neural Substrate Interface standard draft
BioCompute Control Plane     hosted/on-prem server layer
BiC OS                       working codename for future OS-level product
```

## Why not SomaOS as the public OS name

SomaOS is a good neural metaphor, but it has public name-collision risk. It should not be used as the primary public brand without legal clearance.

## Why BiC OS

**BiC OS** is short and memorable. It can stand for:

```text
BioCompute OS
Biological Interface Compute OS
Biological Compute Control OS
```

It should remain a working codename until trademark, domain and package-index checks are completed.

## Claim policy

Do not claim:

```text
first biological computer
first wetware OS
GPU replacement for LLM
CUDA replacement
```

Allowed positioning:

```text
BioGPU-Core is the technical kernel of a vendor-neutral BioCompute Runtime and BioSDK for living neural compute, designed to evolve toward BiC OS — an OS-like control plane for neural substrates, LLM agents, experiments, safety and auditable result bundles.
```
