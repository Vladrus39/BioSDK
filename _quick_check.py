"""Quick dependency and structure check."""
import os
import sys

print("=== DEPENDENCIES ===")
deps = ['numpy', 'scipy', 'sklearn', 'pydantic', 'yaml', 'h5py', 'matplotlib', 'fastapi', 'uvicorn', 'pytest']
for d in deps:
    try:
        __import__(d)
        print(f"  {d}: INSTALLED")
    except ImportError:
        print(f"  {d}: MISSING")

print("\n=== MISSING __init__.py ===")
for d in ['biogpu/analysis', 'biogpu/validation']:
    p = os.path.join(d, '__init__.py')
    exists = os.path.isfile(p)
    print(f"  {d}/__init__.py: {'EXISTS' if exists else 'MISSING'}")

print("\n=== DATA_INGEST INIT ===")
with open('biogpu/data_ingest/__init__.py', 'r') as f:
    lines = f.readlines()[:5]
    for l in lines:
        print(f"  {l.rstrip()}")

print("\n=== BIOSDK INIT ===")
with open('biosdk/__init__.py', 'r') as f:
    content = f.read()[:200]
    print(f"  {content}")
