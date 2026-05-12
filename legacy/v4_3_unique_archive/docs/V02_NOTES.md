# v0.2 Notes

v0.2 converts `biogpu-core` from a single benchmark prototype into a small benchmark suite.

## New technical blocks

- `V1Core`: orientation-like filter bank, sparse maps, lateral inhibition abstraction.
- `V1LikeEncoder`: maps orientation responses into stimulation channel banks.
- `Noise Robustness`: accuracy across noise levels.
- `Sequence Memory`: tests whether reservoir state carries order information.
- `energy.py`: transparent proxy metrics for event/spike/readout load.

## Scientific honesty

This still does not demonstrate that wetware beats GPU. It demonstrates that the project now has:

1. executable benchmarks,
2. baseline comparisons,
3. reservoir contribution tests,
4. energy proxy accounting,
5. adapter-ready architecture.
