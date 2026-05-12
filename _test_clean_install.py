"""Test clean-room pip install of biosdk v0.1.0 wheel."""
import shutil, subprocess, sys, json
from pathlib import Path

WHEEL = Path("dist/biosdk-0.1.0-py3-none-any.whl")
TEST_DIR = Path("D:/temp_biosdk_test")
VENV_PYTHON = TEST_DIR / ".venv" / "Scripts" / "python.exe"

# Copy wheel
TEST_DIR.mkdir(parents=True, exist_ok=True)
dest = TEST_DIR / WHEEL.name
shutil.copy(WHEEL, dest)
print(f"Wheel copied to {dest} ({dest.stat().st_size} bytes)")

# Install with dependencies
result = subprocess.run(
    [str(VENV_PYTHON), "-m", "pip", "install", "numpy", "scipy", "h5py", "scikit-learn", "--quiet"],
    capture_output=True, text=True, timeout=120
)
print("Dependencies installed" if result.returncode == 0 else f"Dep install: {result.stderr}")

# Install wheel
result = subprocess.run(
    [str(VENV_PYTHON), "-m", "pip", "install", str(dest), "--force-reinstall", "--no-deps"],
    capture_output=True, text=True, timeout=60
)
print(result.stdout.strip())

# Test import
code = """
import biosdk
print(f"BioSDK version: {biosdk.__version__}")
print(f"Adapters: {biosdk.list_adapters()}")
print(f"Certified: {biosdk.certified_adapters()}")
print("IMPORT OK")
"""
result = subprocess.run(
    [str(VENV_PYTHON), "-c", code],
    capture_output=True, text=True, timeout=30, cwd=str(TEST_DIR)
)
print(result.stdout)
if result.returncode != 0:
    print(f"STDERR: {result.stderr}")
    sys.exit(1)

# Test feature extraction on MCS data
MCS_FILE = r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\data\external\api_exports\mcs_mea2100\2014-07-09T10-17-35W8_Standard_all_500_Hz.h5"
code2 = f"""
import biosdk, numpy as np
ds = biosdk.open(r"{MCS_FILE}")
print(f"Vendor: {{ds.metadata.vendor}}, Channels: {{ds.metadata.channel_count}}")
X = biosdk.features(ds, window_s=0.5, max_windows=3)
print(f"Feature shape: {{X.shape}}")
print(f"Feature dtype: {{X.dtype}}")
assert X.shape == (3, 102), f"Expected (3, 102), got {{X.shape}}"
assert X.dtype == np.float32
assert np.all(np.isfinite(X)), "NaN in features!"
print("FEATURE EXTRACTION OK")
"""
result = subprocess.run(
    [str(VENV_PYTHON), "-c", code2],
    capture_output=True, text=True, timeout=60, cwd=str(TEST_DIR)
)
print(result.stdout)
if result.returncode != 0:
    print(f"STDERR: {result.stderr}")
    sys.exit(1)

print("\n=== CLEAN ROOM INSTALL: PASSED ===")
print(f"Python: {VENV_PYTHON}")
print(f"Wheel: {dest}")
