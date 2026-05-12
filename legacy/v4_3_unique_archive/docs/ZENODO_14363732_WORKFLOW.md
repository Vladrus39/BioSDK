# Zenodo 14363732 Workflow

Recommended first file:

```bash
python scripts/download_zenodo_14363732.py --file Pre_processed_MEA_data.zip --out data/zenodo_14363732 --verify-md5
```

Then extract it and run:

```bash
python -m biogpu.cli public-data zenodo-profile data/zenodo_14363732 --glob "**/*.txt" --window-ms 1000
```

Do not download `Raw_data_MEA_data.zip` first unless you have more than 40 GB free storage and enough bandwidth.

This dataset is excellent for real spike ingestion/profile. It does not automatically provide BioGPU task labels unless the experiment metadata is mapped into `stimulus_windows.csv`.
