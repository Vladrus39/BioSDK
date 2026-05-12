from pathlib import Path
import json
from biogpu.data_ingest.brc_import import write_brc_spec_template


def test_brc_template_writes_json(tmp_path: Path):
    p = write_brc_spec_template(tmp_path / "brc.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["label_column"] == "label"
    assert "2602.05737" in data["source_url"]
