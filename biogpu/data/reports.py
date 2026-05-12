from __future__ import annotations
from html import escape
from pathlib import Path


def _fmt(v):
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def benchmark_report_markdown(results: dict) -> str:
    title = results.get('benchmark', 'benchmark').replace('_', ' ').title()
    lines = [f"# {title} Report", ""]
    metrics = results.get('metrics', {})
    if 'accuracy' in metrics:
        lines.append(f"Accuracy: **{metrics['accuracy']:.3f}**")
        lines.append("")
    if results.get('baselines'):
        lines.append("## Baselines")
        for k, v in results.get('baselines', {}).items():
            lines.append(f"- {k}: {_fmt(v)}")
        lines.append("")
    if results.get('ablations'):
        lines.append("## Ablations")
        for k, v in results.get('ablations', {}).items():
            acc = v.get('accuracy') if isinstance(v, dict) else v
            lines.append(f"- {k}: {_fmt(acc)}")
        lines.append("")
    if results.get('noise_curve'):
        lines.append("## Noise curve")
        for level, acc in results['noise_curve'].items():
            lines.append(f"- noise {level}: {_fmt(acc)}")
        lines.append("")
    if results.get('energy_proxy'):
        lines.append("## Energy proxy")
        for k, v in results['energy_proxy'].items():
            lines.append(f"- {k}: {_fmt(v)}")
        lines.append("")
    if results.get('memory_report'):
        lines.append("## Reservoir memory/state metrics")
        for k, v in results['memory_report'].items():
            lines.append(f"- {k}: {_fmt(v)}")
        lines.append("")
    if results.get('figures'):
        lines.append("## Figures")
        for k, v in results['figures'].items():
            lines.append(f"- {k}: `{v}`")
        lines.append("")
    lines += ["## Interpretation", results.get("interpretation", "No interpretation generated.")]
    return "\n".join(lines)


def orientation_report_markdown(results: dict) -> str:
    return benchmark_report_markdown(results)


def benchmark_report_html(results: dict, figure_paths: list[str] | None = None) -> str:
    title = results.get('benchmark', 'benchmark').replace('_', ' ').title()
    figure_paths = figure_paths or []
    def table(d: dict) -> str:
        rows = []
        for k, v in d.items():
            if isinstance(v, dict):
                v = v.get('accuracy', v)
            rows.append(f"<tr><td>{escape(str(k))}</td><td>{escape(_fmt(v))}</td></tr>")
        return "<table>" + "".join(rows) + "</table>"
    html = ["<!doctype html><html><head><meta charset='utf-8'>",
            f"<title>{escape(title)}</title>",
            "<style>body{font-family:Arial,sans-serif;max-width:1100px;margin:30px auto;line-height:1.45} table{border-collapse:collapse;margin:10px 0} td,th{border:1px solid #ddd;padding:6px 10px} img{max-width:900px;border:1px solid #ddd;margin:12px 0} code{background:#f5f5f5;padding:2px 4px}</style>",
            "</head><body>", f"<h1>{escape(title)} Report</h1>"]
    metrics = results.get('metrics', {})
    if 'accuracy' in metrics:
        html.append(f"<p><b>Accuracy:</b> {metrics['accuracy']:.3f}</p>")
    if results.get('baselines'):
        html.append("<h2>Baselines</h2>" + table(results['baselines']))
    if results.get('ablations'):
        html.append("<h2>Ablations</h2>" + table(results['ablations']))
    if results.get('noise_curve'):
        html.append("<h2>Noise curve</h2>" + table(results['noise_curve']))
    if results.get('energy_proxy'):
        html.append("<h2>Energy proxy</h2>" + table(results['energy_proxy']))
    if results.get('memory_report'):
        html.append("<h2>Reservoir memory/state metrics</h2>" + table(results['memory_report']))
    if figure_paths:
        html.append("<h2>Figures</h2>")
        for p in figure_paths:
            html.append(f"<div><img src='{escape(str(p))}' alt='{escape(str(p))}'></div>")
    html.append("<h2>Interpretation</h2>")
    html.append(f"<p>{escape(results.get('interpretation', 'No interpretation generated.'))}</p>")
    html.append("</body></html>")
    return "\n".join(html)


def write_html_report(out_path: str | Path, results: dict, figure_paths: list[str] | None = None) -> str:
    out_path = Path(out_path)
    out_path.write_text(benchmark_report_html(results, figure_paths), encoding='utf-8')
    return str(out_path)
