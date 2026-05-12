# BioGPU Dimensions and Connections v2.1

## High-level dimensions

The ideal first prototype should fit into a microscope-stage compatible MEA/HD-MEA cartridge/module.

Planning variables:

- external cartridge/module footprint;
- active electrode field width and height;
- electrode count;
- electrode pitch;
- chamber surface area;
- chamber medium volume;
- recording window length;
- sampling rate;
- loop latency.

## High-level connection chain

```text
BioGPU runtime
→ vendor SDK
→ stimulator/amplifier headstage
→ MEA/HD-MEA holder
→ MEA/HD-MEA electrodes
→ living neural layer
→ acquisition stream
→ BioGPUTrace
→ readout/benchmark
```

Vendor pinouts, physical wiring and live stimulation limits are not guessed in this repository.
