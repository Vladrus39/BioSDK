# BioGPU v4.6 Data Asset Policy

## Rule

The SDK does not embed full experimental datasets. It embeds:

- data asset manifests
- checksums
- import/validation code
- small sample subset for smoke tests

Full data archives are placed under:

```text
data/external/
```

## Registered baseline full asset

```text
asset_id: zenodo_14363732_preprocessed_mea
file: Pre_processed_MEA_data.zip
size_bytes: 12103495
md5: 56e4be13c4573252f055b6a1f775f9da
sha256: 502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6
zip_entries: 3581
electrode_csv_count: 3481
metadata_csv_count: 59
recording_count: 59
culture_label_count: 18
base_lineage_count: 10
```

## Why full data is external

- Keeps SDK light.
- Avoids mixing software release and research data.
- Enables enterprise/private data workflows.
- Scales to raw HDF5 archives and future DANDI/Allen/vendor datasets.

## Included sample subset

```text
data/samples/zenodo_14363732_preprocessed_sample.zip
```

The sample is only for parser/import smoke tests. It is not sufficient for scientific claims.
