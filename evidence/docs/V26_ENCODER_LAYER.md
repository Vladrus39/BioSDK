# BioGPU v2.6 — Encoder Layer

## Purpose

v2.6 adds the first formal encoder layer for BioGPU-Core.

The encoder layer converts digital task payloads into **abstract biological pattern intents**:

- spatial pattern;
- temporal pattern;
- rate-like pattern;
- hybrid spatiotemporal pattern.

## Critical boundary

The encoder layer deliberately does **not** generate live stimulation parameters.

It does not contain:

- voltage;
- amplitude;
- pulse width;
- frequency;
- current;
- charge density;
- pinout;
- wiring;
- wet-lab recipes.

A future vendor backend must translate abstract patterns using approved vendor documentation and lab SOPs.

## Why this matters

BioGPU needs a clean separation:

```text
digital task
→ BioGPU encoder
→ abstract BioPattern
→ replay / dry-run / vendor adapter
→ trace
→ readout
```

This allows the same benchmark to run in replay mode now and in live-lab mode later without rewriting the task code.
