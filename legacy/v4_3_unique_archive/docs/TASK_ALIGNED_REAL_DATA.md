# Task-Aligned Real Data Layer

BioGPU can process real spike trains now, but benchmark claims need stimulus alignment.

## Data levels

### Level 1 — Spike profile

Input: spike times only.

Output: firing rate, active units, feature vectors.

Valid claims:

- ingestion works;
- features can be extracted;
- spike statistics can be compared.

Invalid claims:

- pattern recognition;
- reservoir task accuracy;
- BioGPU advantage.

### Level 2 — Stimulus-window aligned spikes

Input:

- spike times;
- real stimulus/behavior window table with labels.

Output:

- feature matrix per window;
- linear readout benchmark;
- honest task classification.

### Level 3 — BRC aligned data

Input:

- stimulation electrode maps;
- recording electrode maps;
- response windows;
- labels/splits;
- original paper/task metadata.

Output:

- direct reproduction of BRC-style biological reservoir computing.

## Window CSV schema

```csv
start_s,end_s,label,stimulus_id,split
0.000,0.500,A,stim_001,train
0.600,1.100,B,stim_002,train
```

## CLI

```bash
python -m biogpu.cli public-data task-aligned \
  data/session_spikes.txt \
  data/stimulus_windows.csv \
  --source-type txt \
  --readout-bins 4
```
