# BioGPU-A1 Ideal Reference Design v2.1

This file is the current **ideal working sample** for the first real BioGPU prototype.

It is intentionally split into two parts:

1. **Engineering details we can define now** — geometry, connection chain, software contracts, formulas and measurement fields.
2. **Wet-lab details that must be replaced by qualified SOP/vendor protocol** — exact cell handling, concentrations, sterile steps, incubation routines and live stimulation limits.

## 1. Physical object

**Name:** BioGPU-A1

**Physical concept:** replaceable living-neural MEA/HD-MEA cartridge connected to reusable stimulation/acquisition electronics and BioGPU runtime.

**Target envelope:**

```text
External dry module target: 90 mm x 90 mm x 25 mm
Replaceable wet cartridge target: <= 60 mm x 60 mm x 15 mm
Active neural/electrode field target: 4 mm x 4 mm = 16 mm^2
Bridge electrode count: 59-60 channels
Target HD-MEA electrode count: >=1024 addressable channels
Stretch HD-MEA electrode count: 4096+ channels
Nominal HD-MEA pitch class: 50 um
Planning pitch range: 20-200 um
Nominal extracellular sampling class: 20 kHz
Initial response windows: 0.5 s pre + exact event + 0.5 s post
```

All geometry values are engineering targets. Vendor dimensions override them after hardware selection.

## 2. Wetware stack — ideal current view

```text
Living material:
  human iPSC-derived mixed cortical-like neurons

Support:
  astrocyte / glial support or supplier-validated support protocol

Surface class:
  PDL or PEI base adhesion class
  + laminin/fibronectin ECM cue class

Medium class:
  BrainPhys route for electrophysiology/activity-preserving experiments
  OR Neurobasal Plus + B-27 Plus route for robust survival/maturation

Interface:
  HD-MEA preferred
  60-channel MEA acceptable bridge prototype
```

This is not a final culturing recipe. The final recipe depends on chosen cell supplier, surface chemistry, MEA vendor, lab SOP and biosafety review.

## 3. Connection chain

```text
BioGPU runtime
→ vendor SDK
→ stimulator/amplifier headstage
→ MEA/HD-MEA holder
→ electrode array
→ living neural layer
→ recorded electrical response
→ acquisition stream
→ BioGPUTrace
→ feature extraction
→ readout
→ BioGPUResult
→ benchmark/closed-loop controller
```

## 4. Required session metadata

Every live BioGPU session must record at least:

```text
substrate_id
cell_material_id
cell_supplier_or_lab_batch
MEA_vendor
MEA_layout_id
electrode_count
electrode_pitch
electrode_effective_area
recording_sampling_rate
stimulation_protocol_id
environment_telemetry
session_start_time
session_duration
readout_model_id
benchmark_task_id
energy_metering_status
```

## 5. Why this may change

The design changes if:

- vendor MEA geometry is different;
- cell supplier requires different surface/medium;
- network activity is too weak, unstable or over-synchronized;
- closed-loop latency is too high;
- energy measurement shows environment overhead dominates;
- HD-MEA is unavailable and bridge 60-channel MEA must be used first.

## 6. Footer statement

This is the **current ideal BioGPU-A1 working reference design**. It contains concrete engineering dimensions, connection architecture and formulas. Biological execution details must be replaced by a qualified laboratory SOP and vendor manuals before live implementation.
