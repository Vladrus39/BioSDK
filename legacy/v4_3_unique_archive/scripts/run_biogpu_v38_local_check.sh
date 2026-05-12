#!/usr/bin/env bash
set -euo pipefail
python -m py_compile biogpu/llm/tool_interface_v38.py biogpu/benchmarks/biogpu_v38_biollm_tool_interface.py
python -m pytest -q tests/test_biogpu_v38_biollm_tool_interface.py
python -m biogpu.benchmarks.biogpu_v38_biollm_tool_interface
