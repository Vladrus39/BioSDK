from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any

class ExperimentLogger:
    def __init__(self, root: str = "outputs"):
        self.root = Path(root)
        self.exp_dir = self.root / "experiments"
        self.report_dir = self.root / "reports"
        self.figure_dir = self.root / "figures"
        for d in [self.exp_dir, self.report_dir, self.figure_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def save_json(self, name: str, payload: dict[str, Any]) -> Path:
        path = self.exp_dir / f"{name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def save_markdown_report(self, name: str, content: str) -> Path:
        path = self.report_dir / f"{name}.md"
        path.write_text(content, encoding="utf-8")
        return path
