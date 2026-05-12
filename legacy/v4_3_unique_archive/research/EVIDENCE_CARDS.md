# Evidence Cards v0.1

## Card 01 — HD-MEA / MaxOne-like systems

FACT: High-density MEA systems provide dense electrode arrays, recording and stimulation workflows.

INFERENCE: HD-MEA is a strong target for future `RealMEAAdapter`.

HYPOTHESIS: HD-MEA can serve as the first serious laboratory bridge from simulated pipeline to living reservoir computing.

DECISION: Build substrate-independent adapter layer now.

## Card 02 — Classic MEA / MEA2100-like systems

FACT: Mature MEA systems are used for in vitro electrophysiology with cultures, slices and stimulation.

INFERENCE: Classic MEA may validate the software stack before moving to HD-MEA.

DECISION: Do not hard-code high-density assumptions.

## Card 03 — Biological Reservoir Computing

FACT: Cultured neuronal networks can be used as reservoirs with MEA stimulation and readout.

INFERENCE: This is the closest existing line to MEA-BioGPU-Core.

DECISION: Make reservoir computing the first living BioGPU model.

## Card 04 — MICrONS visual cortex

FACT: Visual cortex has extremely dense synaptic structure and functional maps.

INFERENCE: V1 is an architectural source, not a neuron-by-neuron copy target.

DECISION: Implement simplified V1-inspired core.

## Card 05 — Drosophila / FlyWire

FACT: Adult Drosophila connectome is mapped at large scale.

INFERENCE: Fly circuits can inspire compact modules.

DECISION: Use Drosophila as architecture source, not first physical substrate.

## Card 06 — NWB

FACT: NWB is a neurophysiology data standard.

DECISION: Add NWB-compatible export path after v0.1.

## Card 07 — Loihi / SpiNNaker / Memristors

FACT: Neuromorphic and compute-in-memory hardware exists as non-biological bridges.

INFERENCE: They can test event-driven/V1-like computation before wetware.

DECISION: Keep adapters for future hardware targets.
