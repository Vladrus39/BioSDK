from __future__ import annotations

import json
from pathlib import Path


def _fmt(x):
    if x is None:
        return ""
    try:
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def generate_dashboard(outputs_root: str = "outputs", out_file: str | None = None) -> str:
    root = Path(outputs_root)
    exp_dir = root / "experiments"
    report_dir = root / "reports"
    out = Path(out_file) if out_file else report_dir / "index.html"
    report_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for p in sorted(exp_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        bm = d.get("benchmark", p.stem)
        acc = d.get("metrics", {}).get("accuracy")
        ts = d.get("timestamp", d.get("created_utc", ""))
        proxy = d.get("energy_proxy", {}).get("proxy_score")
        baselines = d.get("baselines", {}) or {}
        best_baseline = max([v for v in baselines.values() if isinstance(v, (int, float))], default=None)
        html_name = p.stem + ".html"
        html_path = report_dir / html_name
        items.append((bm, ts, acc, best_baseline, proxy, p.name, html_name if html_path.exists() else None))
    rows = []
    for bm, ts, acc, best_baseline, proxy, name, html_name in items[:200]:
        report_link = f"<a href='{html_name}'>HTML</a>" if html_name else ""
        rows.append(
            f"<tr><td>{bm}</td><td>{ts}</td><td>{_fmt(acc)}</td><td>{_fmt(best_baseline)}</td>"
            f"<td>{_fmt(proxy)}</td><td><code>{name}</code></td><td>{report_link}</td></tr>"
        )
    html = """<!doctype html><html><head><meta charset='utf-8'>
<title>BioGPU Core Dashboard</title>
<style>
body{font-family:Arial,sans-serif;max-width:1200px;margin:30px auto;line-height:1.45;color:#222}
table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:7px;text-align:left}
th{background:#f2f2f2} code{background:#f5f5f5;padding:2px 4px}.note{background:#fff8db;padding:10px;border:1px solid #eadb8b}
</style>
</head><body><h1>BioGPU Core Dashboard</h1>
<p class='note'>Static dashboard generated from local benchmark JSON files. Accuracy alone is not proof of BioGPU advantage; compare baselines, energy proxy and memory metrics.</p>
<table><tr><th>Benchmark</th><th>Timestamp</th><th>Accuracy</th><th>Best baseline</th><th>Energy proxy</th><th>JSON</th><th>Report</th></tr>
""" + "\n".join(rows) + "\n</table></body></html>"
    out.write_text(html, encoding="utf-8")
    return str(out)


if __name__ == "__main__":
    print(generate_dashboard())
