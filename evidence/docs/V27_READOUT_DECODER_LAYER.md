# BioGPU v2.7 — Readout / Decoder Layer

The v2.7 layer decodes `BioGPUTrace` / feature vectors into predictions and confidence estimates.

It includes centroid, logistic-contract, linear-SVM-contract and online-centroid decoders. Minimal environments use deterministic dependency-free fallbacks; stronger power-PC runs may replace the contract implementations with sklearn-backed versions.

Safety boundary: this layer decodes features only and does not include live stimulation settings, wet-lab instructions, physical wiring, vendor pinouts, or cell-culture recipes.
