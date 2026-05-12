# BioGPU v4.7 — First 72 Hours on Power PC

## Hour 0–2: unpack and install

```bash
unzip biogpu-core-v4_7_final_pc_runner_patch.zip -d biogpu-core-v4_7
cd biogpu-core-v4_7
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## Hour 2–4: smoke validation

```bash
bash scripts/run_biogpu_v47_powerpc_smoke.sh
```

Expected: current tests pass and `outputs/v47_smoke/v47_final_pc_patch_summary.json` says `ready_for_power_pc_handoff: true`.

## Hour 4–8: add full preprocessed dataset

```bash
mkdir -p data/external
cp /path/to/Pre_processed_MEA_data.zip data/external/Pre_processed_MEA_data.zip
bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip
```

Expected SHA256:

```text
502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6
```

## Hour 8–18: reproduce compact results

```bash
bash scripts/run_biogpu_v47_powerpc_stage1_v33_compact.sh
bash scripts/run_biogpu_v47_powerpc_stage2_v36_lineage_compact.sh
```

Expected: results in the same family as the evidence pack. Exact shuffled values can vary by seed.

## Hour 18–48: run full lineage statistics

```bash
bash scripts/run_biogpu_v47_powerpc_full_shuffle_1000.sh
```

Do not start extended methods until the full run completes and result tables are inspected.

## Hour 48–72: package and inspect

```bash
bash scripts/run_biogpu_v47_latency_energy_measurement.sh
bash scripts/package_biogpu_v47_powerpc_results.sh
```

Then inspect `outputs/biogpu_v47_powerpc_final_result_bundle.zip`.
