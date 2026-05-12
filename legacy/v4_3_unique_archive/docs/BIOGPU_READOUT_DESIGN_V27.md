# BioGPU Readout Design v2.7

Readout position in the BioGPU chain:

`task → encoder → substrate/replay/live → trace/features → readout → BioGPUResult`

The readout API is intentionally independent from the substrate. The same decoder can consume public replay features now and future live MEA/HD-MEA traces later.
