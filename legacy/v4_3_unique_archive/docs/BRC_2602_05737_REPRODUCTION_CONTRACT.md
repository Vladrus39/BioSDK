# BRC 2602.05737 Reproduction Contract

This paper is currently the closest external architecture target for BioGPU.

Minimum artifacts needed for reproduction:

- HD-MEA spike or raw recording source.
- Stimulation pattern table.
- Electrode map.
- Labels/classes for input patterns.
- Train/test split or enough metadata to reproduce it.
- Readout feature extraction details.

Generate the contract:

```bash
python -m biogpu.cli public-data brc2602-contract --output data/templates/brc2602_contract.json
```
