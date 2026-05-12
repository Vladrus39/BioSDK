# DANDI quick start

```bash
pip install dandi pynwb
dandi download DANDI:<DANDISET_ID>/<asset_path>.nwb -o data/dandi
python -m biogpu.cli public-data dandi-profile data/dandi/example.nwb --window-ms 1000
```
