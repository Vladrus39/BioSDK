"""Self-diagnostic script for BioSDK codebase — v2."""
import os
import sys
import traceback

print("=== SYNTAX CHECK ===")
errors = []
count = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.venv', '.git', 'legacy', 'build', 'dist', '.pytest_cache')]
    for f in files:
        if f.endswith('.py'):
            count += 1
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='replace') as fh:
                    src = fh.read()
                compile(src, fp, 'exec')
            except SyntaxError as e:
                errors.append(f"{fp}: line {e.lineno} — {e.msg}")
            except Exception as e:
                errors.append(f"{fp}: {type(e).__name__}: {e}")

print(f"  Files scanned: {count}")
if errors:
    print(f"  SYNTAX ERRORS: {len(errors)}")
    for e in errors[:20]:
        print(f"    {e}")
else:
    print(f"  Result: ALL {count} files have valid syntax")

print("\n=== IMPORT CHECK ===")
sys.path.insert(0, '.')

for pkg in ['biogpu', 'biosdk']:
    try:
        __import__(pkg)
        print(f"  {pkg}: OK")
    except Exception as e:
        print(f"  {pkg}: FAILED - {type(e).__name__}: {e}")

subs = ['nsi', 'runtime', 'dashboard', 'safety', 'validation', 'simulators', 'production', 'telemetry', 'plugins', 'schemas']
for s in subs:
    try:
        __import__(f'biogpu.{s}')
        print(f"  biogpu.{s}: OK")
    except Exception as e:
        print(f"  biogpu.{s}: FAILED - {type(e).__name__}: {e}")

print("\n=== KEY CLASS IMPORT CHECK ===")
keys = [
    ('biogpu.nsi', 'NSIDataset'),
    ('biogpu.nsi', 'NSIAdapter'),
    ('biogpu.nsi', 'NSIMetadata'),
]
for mod, cls in keys:
    try:
        m = __import__(mod, fromlist=[cls])
        getattr(m, cls)
        print(f"  {mod}.{cls}: OK")
    except Exception as e:
        print(f"  {mod}.{cls}: MISSING - {type(e).__name__}")

print("\n=== TEST FILE COUNT ===")
test_dir = 'tests/current'
if os.path.isdir(test_dir):
    tests = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    print(f"  Test files in {test_dir}: {len(tests)}")
else:
    print(f"  Test dir '{test_dir}' not found")

print("\n=== MODULE STRUCTURE ===")
try:
    top_dirs = [d for d in os.listdir('biogpu') if os.path.isdir(os.path.join('biogpu', d)) and not d.startswith('_')]
    print(f"  biogpu submodule dirs: {len(top_dirs)}")
    missing_init = []
    for d in sorted(top_dirs):
        has_init = os.path.isfile(os.path.join('biogpu', d, '__init__.py'))
        py_count = len([f for f in os.listdir(os.path.join('biogpu', d)) if f.endswith('.py') and f != '__init__.py'])
        if not has_init:
            missing_init.append(d)
        print(f"    {d}/ {'[INIT]' if has_init else '[NO INIT]'} ({py_count} .py files)")
    if missing_init:
        print(f"\n  WARNING: {len(missing_init)} dirs missing __init__.py: {', '.join(missing_init)}")
except Exception as e:
    print(f"  ERROR listing biogpu: {e}")

print("\n=== CROSS-FILE REFERENCE CHECK ===")
# Check that root-level scripts can import from biogpu
root_scripts = [
    '_bic_os_cross_modal.py',
    '_bic_os_cross_dataset.py',
    '_bic_os_crossval.py',
    'run_biosdk.py',
]
for s in root_scripts:
    if os.path.isfile(s):
        try:
            with open(s, 'r') as fh:
                src = fh.read()
            compile(src, s, 'exec')
            print(f"  {s}: syntax OK")
        except SyntaxError as e:
            print(f"  {s}: SYNTAX ERROR line {e.lineno}")
    else:
        print(f"  {s}: FILE NOT FOUND")

print("\n=== DIAGNOSTIC COMPLETE ===")
