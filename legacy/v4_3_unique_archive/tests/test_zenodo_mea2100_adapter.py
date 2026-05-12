from pathlib import Path
from biogpu.data_ingest.zenodo_mea2100 import parse_spike_txt, ZenodoMEA2100Config, ZenodoMEA2100SpikeTxtAdapter

def test_parse_spike_txt_two_columns(tmp_path: Path):
    p=tmp_path/"spikes.txt"; p.write_text("unit time\n1 0.1\n2 0.2\n2 0.3\n", encoding="utf-8")
    spikes=parse_spike_txt(p)
    assert spikes.unit_ids == [1,2,2]
    assert spikes.spike_times == [0.1,0.2,0.3]

def test_zenodo_adapter_reads_window(tmp_path: Path):
    p=tmp_path/"a_spikes.txt"; p.write_text("1 0.05\n2 0.20\n3 1.50\n", encoding="utf-8")
    adapter=ZenodoMEA2100SpikeTxtAdapter(ZenodoMEA2100Config(root_path=str(tmp_path), spike_glob="*.txt")); adapter.connect()
    spikes=adapter.read_spikes(300)
    assert spikes.unit_ids == [1,2]
