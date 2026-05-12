# BioGPU-Core v4.6 — Power-PC Transfer and Validation Runbook

## 0. Unpack

```bash
unzip biogpu-core-v4_6_clean_release_pc_ready.zip -d biogpu-core-v4_6
cd biogpu-core-v4_6
```

## 1. Create environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## 2. Run current smoke checks

```bash
bash scripts/run_biogpu_v46_powerpc_smoke.sh
```

This runs current-only tests and the v4.6 release validator with plugin autoload disabled.

## 3. Attach full baseline dataset

Put the full preprocessed archive here:

```bash
mkdir -p data/external
cp /PATH/TO/Pre_processed_MEA_data.zip data/external/Pre_processed_MEA_data.zip
```

Validate checksum and profile:

```bash
bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip
```

Expected full asset SHA256:

```text
502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6
```

## 4. Repeat reduced tests before heavy work

```bash
bash scripts/run_biogpu_v46_powerpc_stage1_compact.sh
```

## 5. Full shuffle validation

```bash
bash scripts/run_biogpu_v46_powerpc_full_shuffle_1000.sh
```

This stage is expected to be expensive. Do not start it until Stage 0/1 is clean.

## 6. Extended methods

```bash
bash scripts/run_biogpu_v46_powerpc_extended_methods_5000.sh
```

Run this after full_shuffle_1000 produces stable reports.

## 7. Raw HDF5/TTL work

```bash
bash scripts/download_zenodo_14363732_raw_hdf5_v46.sh
```

Then inspect HDF5 structure, TTL/stimulus channels and reconstruct raw-derived windows. This is one of the main open scientific tasks.

## 8. Dataset/API expansion

After raw HDF5, add:

- DANDI/NWB discovery + task aligned parser
- AllenSDK visual coding orientation benchmark
- FinalSpark read-only/export validation when credentials/data are available
- vendor exports for MCS/3Brain/Axion

## 9. Measurements

```bash
bash scripts/run_biogpu_v46_latency_energy_measurement.sh
```

This is a scaffold. For serious results, measure at wall-power/host boundary with fixed workload definitions.

## 10. Release decision

Private beta should not start until:

- full data asset validates
- compact replay repeats
- full_shuffle_1000 completed or explicitly deferred
- raw HDF5 plan is executed or documented as pending
- beta docs and security pack are current
