"""Command-line wrapper for validating NSI-1.0 JSON payloads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from biogpu.standards.nsi_v10 import (
    NSI_SCHEMA_BY_NAME,
    nsi_spec,
    reference_nsi_objects,
    validate_nsi_object,
    validate_result_bundle,
)


SCHEMA_CHOICES = tuple(sorted(NSI_SCHEMA_BY_NAME))


def _read_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("NSI input JSON must be an object")
    return data


def _write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_reference_objects(out_dir: str | Path) -> dict[str, Any]:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    objects = reference_nsi_objects()
    written: list[str] = []
    combined = target / "NSI_1_0_REFERENCE_OBJECTS.json"
    _write_json(combined, objects)
    written.append(str(combined))
    for schema_name, payload in objects.items():
        path = target / f"{schema_name}.reference.json"
        _write_json(path, payload)
        written.append(str(path))
    return {"written": written, "count": len(written)}


def add_validate_nsi_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--schema", choices=SCHEMA_CHOICES, help="NSI schema name to validate against")
    parser.add_argument("--input", help="JSON payload to validate")
    parser.add_argument("--output", help="Optional path to write the validation report JSON")
    parser.add_argument("--result-bundle", action="store_true", help="Apply stricter BioComputeResultBundle checks")
    parser.add_argument("--list-schemas", action="store_true", help="Print available NSI schema names")
    parser.add_argument("--write-reference", help="Write reference NSI objects to this directory")


def run_validate_nsi(args: argparse.Namespace) -> int:
    if args.list_schemas:
        print(json.dumps({"schemas": list(SCHEMA_CHOICES), "standard": nsi_spec()["standard"]}, indent=2))
        return 0

    if args.write_reference:
        result = write_reference_objects(args.write_reference)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if not args.schema:
        raise SystemExit("--schema is required unless --list-schemas or --write-reference is used")
    if not args.input:
        raise SystemExit("--input is required unless --list-schemas or --write-reference is used")

    payload = _read_json(args.input)
    if args.result_bundle or args.schema == "BioComputeResultBundle":
        report = validate_result_bundle(payload)
    else:
        report = validate_nsi_object(args.schema, payload)
    data = report.to_dict()
    data["input"] = str(args.input)
    if args.output:
        _write_json(args.output, data)
        data["output"] = str(args.output)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if report.valid else 1


def build_parser(prog: str = "biogpu-validate-nsi") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, description="Validate NSI-1.0 JSON payloads")
    add_validate_nsi_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_validate_nsi(args)


if __name__ == "__main__":
    raise SystemExit(main())