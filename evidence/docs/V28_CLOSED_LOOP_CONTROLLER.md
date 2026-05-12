# BioGPU v2.8 — Closed-loop Controller

v2.8 adds the first hardware-neutral closed-loop controller:

`task → encoder → substrate/replay → trace/features → readout → reward/error → next abstract action`

## What it adds

- closed-loop config schema;
- observation / reward / decision / step-record contracts;
- confidence-seeking policy;
- accuracy+confidence reward;
- deterministic dry-run substrate;
- one-command local check;
- JSON/CSV/Markdown output bundle.

## Safety boundary

The controller updates only abstract payload fields such as `abstract_gain` and `abstract_exploration`. It does **not** emit live stimulation settings, voltage, current, pulse width, frequency, charge density, pinouts, wiring, wet-lab recipes, cell handling steps, or vendor SOP replacements.

## Why this matters

This is the first complete control-loop skeleton for a real BioGPU. When a qualified lab and vendor backend are available, the substrate call can be swapped while keeping the controller/readout/session contracts stable.
