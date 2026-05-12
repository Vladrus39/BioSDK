"""FULL PROJECT AUDIT — BioSDK + Resonance, all checks in one pass."""
import os, sys, subprocess, json
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
RES = Path(r"C:\Users\vladi\Desktop\Braine\resonance_theory_research_pack_v0_5")

results = {
    "timestamp": None,
    "bio_path_exists": BIO.exists(),
    "res_path_exists": RES.exists(),
    "venv": {},
    "dashboard": {},
    "tests": {},
    "data": {},
    "modules": {},
    "issues": [],
}

# ── 1. VENV AUDIT ──
print("=" * 60)
print("1. VENV AUDIT")
print("=" * 60)
for label, venv_path, project in [
    ("resonance .venv", RES / ".venv", RES),
    ("bio .venv-1", BIO / ".venv-1", BIO),
    ("bio .venv", BIO / ".venv", BIO),
    ("bio Scripts/python", BIO / "Scripts" / "python.exe", BIO),
]:
    if label.endswith("python.exe"):
        exists = venv_path.exists()
        if exists:
            r = subprocess.run([str(venv_path), "-c", "import sys; print(sys.version)"], 
                             capture_output=True, text=True, timeout=10)
            print(f"  {label}: EXISTS, Python={r.stdout.strip()}")
            # Check key packages
            r2 = subprocess.run([str(venv_path), "-c", 
                "import sklearn,h5py,pydantic,fastapi,yaml; print('all ok')"],
                capture_output=True, text=True, timeout=10)
            if r2.returncode != 0:
                missing = r2.stderr.strip()
                print(f"    MISSING PACKAGES: {missing[:150]}")
                results["issues"].append(f"MISSING PACKAGES in {label}")
            else:
                print(f"    Key packages: OK")
        else:
            print(f"  {label}: MISSING")
        results["venv"][label] = {"exists": exists}
    else:
        exists = venv_path.exists()
        if exists:
            python_exe = venv_path / "Scripts" / "python.exe"
            if python_exe.exists():
                r = subprocess.run([str(python_exe), "-c", "import sys; print(sys.version)"], 
                                 capture_output=True, text=True, timeout=10)
                ver = r.stdout.strip() if r.returncode == 0 else "ERROR"
                print(f"  {label}: EXISTS, Python={ver[:80]}")
            else:
                print(f"  {label}: EXISTS but no python.exe in Scripts/")
        else:
            print(f"  {label}: MISSING")
        results["venv"][label] = {"exists": exists, "python": None}

# ── 2. DASHBOARD AUDIT ──
print("\n" + "=" * 60)
print("2. DASHBOARD AUDIT")
print("=" * 60)

# Check if daemon script exists
daemon_path = BIO / "biogpu" / "production" / "daemon_v570.py"
if daemon_path.exists():
    print(f"  daemon_v570.py: EXISTS ({daemon_path.stat().st_size} bytes)")
    # Can we import it?
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BIO)
    r = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, r'" + str(BIO) + "'); "
         "from biogpu.production.daemon_v570 import *; print('IMPORT OK')"],
        capture_output=True, text=True, timeout=15, env=env
    )
    if r.returncode != 0:
        err = r.stderr.strip()[-300:]
        print(f"    IMPORT FAILED: {err}")
        results["issues"].append(f"daemon_v570.py import fails")
    else:
        print(f"    IMPORT: OK")
else:
    print(f"  daemon_v570.py: MISSING")
    results["issues"].append("daemon_v570.py missing")

# Check server
server_path = list(BIO.glob("biogpu/dashboard/server_*.py"))
if server_path:
    print(f"  Server files: {[s.name for s in server_path]}")
else:
    print(f"  Server files: NONE")

# Try curl to dashboard
try:
    import urllib.request
    req = urllib.request.Request("http://127.0.0.1:8420/health")
    resp = urllib.request.urlopen(req, timeout=3)
    print(f"  Dashboard health: {resp.status} - {resp.read()[:200]}")
    results["dashboard"]["running"] = True
except Exception as e:
    print(f"  Dashboard health: NOT RESPONDING ({str(e)[:80]})")
    results["dashboard"]["running"] = False

# ── 3. TEST AUDIT ──
print("\n" + "=" * 60)
print("3. TEST AUDIT (BioSDK)")
print("=" * 60)

tests_dir = BIO / "tests" / "current"
test_files = sorted(tests_dir.glob("test_*.py")) if tests_dir.exists() else []
print(f"  Test files: {len(test_files)}")

# Run v60 with full output to see exact failure
v60 = tests_dir / "test_biogpu_v60_production_foundation.py"
if v60.exists():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BIO)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(v60), "-v", "--tb=line"],
        capture_output=True, text=True, timeout=120, env=env
    )
    lines = r.stdout.split("\n")
    passed = failed = 0
    for line in lines:
        if "PASSED" in line:
            passed += 1
        elif "FAILED" in line:
            failed += 1
            # Find the failure reason
            print(f"  FAIL: {line.strip()}")
    
    print(f"  v60: {passed} passed, {failed} failed")
    
    # Get failure details
    r2 = subprocess.run(
        [sys.executable, "-m", "pytest", str(v60), "-v", "--tb=short", "-k", "test_build_foundation"],
        capture_output=True, text=True, timeout=60, env=env
    )
    for line in r2.stdout.split("\n"):
        if "Error" in line or "error" in line or "FAILED" in line or "KeyError" in line:
            if "==" not in line:
                print(f"    {line.strip()[:150]}")
    results["tests"]["v60"] = {"passed": passed, "failed": failed}

# ── 4. MODULE STRUCTURE AUDIT ──
print("\n" + "=" * 60)
print("4. MODULE STRUCTURE")
print("=" * 60)

biogpu = BIO / "biogpu"
if biogpu.exists():
    for subdir in sorted(biogpu.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith("__"):
            py_files = list(subdir.glob("*.py"))
            py_count = len(py_files)
            kb = sum(f.stat().st_size for f in py_files) // 1024
            print(f"  biogpu/{subdir.name}/ — {py_count} .py files, {kb} KB")
    results["modules"]["biogpu_subdirs"] = [d.name for d in biogpu.iterdir() if d.is_dir() and not d.name.startswith("__")]

# ── 5. DATA AUDIT ──
print("\n" + "=" * 60)
print("5. DATA AVAILABILITY")
print("=" * 60)

data_external = BIO / "data" / "external"
if data_external.exists():
    for d in sorted(data_external.iterdir()):
        if d.is_dir():
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) // (1024*1024)
            file_count = len(list(d.rglob("*")))
            print(f"  {d.name}/ — ~{size} MB, {file_count} files")
    results["data"]["external_dirs"] = [d.name for d in data_external.iterdir() if d.is_dir()]

# Raw HDF5 check
raw_hdf5 = BIO / "data" / "external" / "raw_hdf5"
if raw_hdf5.exists():
    h5_files = list(raw_hdf5.rglob("*.h5"))
    print(f"\n  Raw HDF5 files: {len(h5_files)}")
    if h5_files:
        # Try reading first one
        import h5py
        try:
            with h5py.File(h5_files[0], "r") as f:
                keys = list(f.keys())[:10]
                print(f"  Sample HDF5 ({h5_files[0].name}): keys={keys}")
        except Exception as e:
            print(f"  Sample HDF5 READ ERROR: {e}")
    results["data"]["raw_hdf5_count"] = len(h5_files)

# ── 6. EVIDENCE BUNDLE CHECK ──
print("\n" + "=" * 60)
print("6. EVIDENCE BUNDLES")
print("=" * 60)

evidence = BIO / "evidence" / "outputs"
if evidence.exists():
    bundles = list(evidence.glob("*_readout"))
    print(f"  Evidence bundles (readout dirs): {len(bundles)}")
    for b in bundles[:5]:
        json_files = list(b.glob("*.json"))
        npz_files = list(b.glob("*.npz"))
        print(f"    {b.name}: {len(json_files)} json, {len(npz_files)} npz")
    results["evidence"]["bundle_count"] = len(bundles)

# ── 7. CROSS-MODAL CHECK ──
print("\n" + "=" * 60)
print("7. CROSS-MODAL / CROSS-VENDOR")
print("=" * 60)

cm = BIO / "outputs" / "v85_cross_modal"
if cm.exists():
    for f in sorted(cm.glob("*.json")):
        data = json.loads(f.read_text())
        if isinstance(data, dict):
            for k in ["common_keys", "gir_keys", "mcs_keys", "overlap", "structure"]:
                if k in data:
                    print(f"  {f.name}: {k}={data[k]}")

# ── 8. ISSUES SUMMARY ──
print("\n" + "=" * 60)
print("8. ISSUES FOUND")
print("=" * 60)
if results["issues"]:
    for i, issue in enumerate(results["issues"], 1):
        print(f"  {i}. {issue}")
else:
    print("  No critical issues found")

# Save full audit
import json
results["timestamp"] = __import__('datetime').datetime.now().isoformat()
out = RES / "analysis_output_v0_7" / "full_audit_2026_05_11.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2, default=str, ensure_ascii=False))
print(f"\nAudit saved to: {out}")
