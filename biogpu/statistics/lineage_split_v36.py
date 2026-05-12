"""BioGPU v3.6 lineage-strict split utilities.

Why this matters:
the Zenodo v1.5 pulse-window matrix has culture labels such as
``40628_13DIV`` and ``40628_21DIV``. Those may represent the same base
culture/lineage recorded at different days in vitro. A normal culture-label
split can therefore leak lineage-specific structure between train and test.

v3.6 adds a stricter split level:
``base lineage`` holdout, where every DIV belonging to the same base id is
kept entirely in train or entirely in test.

Scope boundary: offline/public-data statistics only. This module never emits
live stimulation settings, wet-lab steps, vendor pinout, or wiring data.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import numpy as np

from biogpu.integration.realdata_replay_v32 import RealDataMatrixV32


CULTURE_RE = re.compile(r"^(?P<base>[A-Za-z0-9-]+?)(?:[_-](?P<div>\d+)\s*DIV)?$", re.IGNORECASE)


@dataclass(frozen=True)
class CultureLineageV36:
    culture: str
    base_lineage_id: str
    div: int | None
    parser_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineageSplitV36:
    split_id: str
    offset: int
    strategy: str
    train_idx: list[int]
    test_idx: list[int]
    test_lineages: list[str]
    test_cultures: list[str]
    overlapping_labels: list[int]
    leakage_check_passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_culture_lineage_v36(culture: str) -> CultureLineageV36:
    raw = str(culture).strip()
    m = CULTURE_RE.match(raw)
    if not m:
        return CultureLineageV36(raw, raw, None, "fallback_raw_culture")
    base = str(m.group("base")).strip()
    div_s = m.group("div")
    if div_s is None:
        return CultureLineageV36(raw, base or raw, None, "base_only")
    return CultureLineageV36(raw, base or raw, int(div_s), "base_plus_div")


def map_cultures_to_lineages_v36(cultures: Iterable[str]) -> dict[str, CultureLineageV36]:
    return {str(c): parse_culture_lineage_v36(str(c)) for c in sorted(set(map(str, cultures)))}


def _choose_holdout_lineages(lineages: list[str], offset: int, stride: int, heldout_count: int) -> list[str]:
    if not lineages:
        raise ValueError("No lineages available")
    stride = max(1, int(stride))
    heldout_count = max(1, int(heldout_count))
    out: list[str] = []
    # cycle with stride, preserving uniqueness
    for j in range(len(lineages) * stride + len(lineages)):
        cand = lineages[(int(offset) + j * stride) % len(lineages)]
        if cand not in out:
            out.append(cand)
        if len(out) >= min(heldout_count, len(lineages)):
            break
    return out


def build_lineage_strict_splits_v36(
    matrix: RealDataMatrixV32,
    split_offsets: tuple[int, ...] = (0, 1, 2, 3, 4, 5),
    lineage_stride: int = 2,
    heldout_lineage_count: int = 2,
) -> list[LineageSplitV36]:
    matrix.validate()
    culture_map = map_cultures_to_lineages_v36(matrix.cultures.astype(str))
    row_lineages = np.asarray([culture_map[str(c)].base_lineage_id for c in matrix.cultures.astype(str)], dtype=str)
    lineages = sorted(set(row_lineages.tolist()))
    if len(lineages) < 2:
        raise ValueError("Lineage-strict split requires at least two base lineages")
    out: list[LineageSplitV36] = []
    for off in split_offsets:
        test_lineages = _choose_holdout_lineages(lineages, int(off), lineage_stride, heldout_lineage_count)
        is_test = np.isin(row_lineages, np.asarray(test_lineages, dtype=str))
        train_mask, test_mask = ~is_test, is_test
        overlapping = sorted(set(map(int, matrix.y[train_mask])) & set(map(int, matrix.y[test_mask])))
        if not overlapping:
            continue
        label_mask = np.isin(matrix.y.astype(int), np.asarray(overlapping, dtype=int))
        train_idx = np.where(train_mask & label_mask)[0].astype(int).tolist()
        test_idx = np.where(test_mask & label_mask)[0].astype(int).tolist()
        if not train_idx or not test_idx:
            continue
        train_lineages = set(row_lineages[train_idx].tolist())
        test_lineages_set = set(row_lineages[test_idx].tolist())
        leak_free = train_lineages.isdisjoint(test_lineages_set)
        test_cultures = sorted(set(map(str, matrix.cultures[test_idx])))
        out.append(LineageSplitV36(
            split_id=f"lineage_holdout_offset_{int(off)}",
            offset=int(off),
            strategy="base_lineage_holdout_no_div_leakage",
            train_idx=train_idx,
            test_idx=test_idx,
            test_lineages=list(test_lineages),
            test_cultures=test_cultures,
            overlapping_labels=[int(x) for x in overlapping],
            leakage_check_passed=bool(leak_free),
        ))
    if not out:
        raise ValueError("No valid lineage-strict splits produced")
    return out


def lineage_audit_table_v36(matrix: RealDataMatrixV32) -> list[dict[str, Any]]:
    matrix.validate()
    culture_map = map_cultures_to_lineages_v36(matrix.cultures.astype(str))
    rows=[]
    for culture, parsed in culture_map.items():
        mask = matrix.cultures.astype(str) == culture
        rows.append({
            "culture": culture,
            "base_lineage_id": parsed.base_lineage_id,
            "div": parsed.div,
            "parser_status": parsed.parser_status,
            "row_count": int(mask.sum()),
            "target_classes": int(len(set(map(int, matrix.y[mask])))),
            "conditions": ";".join(sorted(set(map(str, matrix.conditions[mask])))),
        })
    return rows


def summarize_lineage_splits_v36(splits: list[LineageSplitV36]) -> list[dict[str, Any]]:
    return [{
        "split_id": s.split_id,
        "strategy": s.strategy,
        "offset": s.offset,
        "n_train": len(s.train_idx),
        "n_test": len(s.test_idx),
        "n_test_lineages": len(s.test_lineages),
        "test_lineages": ";".join(s.test_lineages),
        "n_test_cultures": len(s.test_cultures),
        "test_cultures": ";".join(s.test_cultures),
        "n_labels": len(s.overlapping_labels),
        "overlapping_labels": ";".join(map(str, s.overlapping_labels)),
        "leakage_check_passed": bool(s.leakage_check_passed),
    } for s in splits]
