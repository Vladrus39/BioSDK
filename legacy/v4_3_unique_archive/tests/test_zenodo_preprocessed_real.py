from pathlib import Path
from biogpu.data_ingest.zenodo_mea2100_preprocessed import read_sample_num_csv, recording_dir_to_spiketrain, profile_dataset
from biogpu.benchmarks.zenodo_real_dataset_profile import run_zenodo_real_dataset_profile

def test_read_sample_num_csv(tmp_path: Path):
    p=tmp_path/'electrode012.csv'; p.write_text('sample_num\n10\n20\n',encoding='utf-8')
    assert read_sample_num_csv(p)==[10,20]

def test_recording_profile_and_spiketrain(tmp_path: Path):
    rec=tmp_path/'EXP PTSD'/'11-11-2022'/'39566_21DIV'/'39566_21DIV_LightStim_Spot34_D-00144'
    (rec/'metadata').mkdir(parents=True)
    (rec/'metadata'/'meta_data.csv').write_text('recording_duration_sec\tsampling_fr_hz\tstimulation\n1.0\t1000\tLightStim\n',encoding='utf-8')
    (rec/'electrode012.csv').write_text('sample_num\n100\n200\n',encoding='utf-8')
    profiles=profile_dataset(tmp_path)
    assert len(profiles)==1 and profiles[0].condition=='lightstim' and profiles[0].spot==34
    st=recording_dir_to_spiketrain(rec)
    assert st.unit_ids==[12,12] and st.spike_times==[0.1,0.2]
    assert run_zenodo_real_dataset_profile(str(tmp_path))['summary']['recording_count']==1
