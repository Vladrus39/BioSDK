# BioGPU Encoder Design v2.6

## Encoder classes

- `SpatialEncoderV26`: maps vectors/grids to abstract electrode group weights.
- `TemporalEncoderV26`: maps sequences to abstract time bins.
- `RateEncoderV26`: maps class score dictionaries to normalized group weights.
- `HybridEncoderV26`: combines spatial and temporal intent.

## Input contract

`EncoderInput`:

- `task_id`
- `payload`
- `metadata`

## Output contract

`AbstractBioPattern`:

- `pattern_id`
- `kind`
- `target_groups`
- `time_bins`
- `weights`
- `readout_hint`
- `safety_level`
- `metadata`

## Safety model

Weights are normalized to `[-1, 1]` and remain abstract.
Time bins are software offsets and not a vendor pulse protocol.
Target groups are logical group labels, not physical pinouts.
