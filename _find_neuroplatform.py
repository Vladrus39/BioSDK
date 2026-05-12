"""Check if neuroplatform is importable."""
try:
    import importlib.util
    spec = importlib.util.find_spec('neuroplatform')
    if spec:
        print(f"neuroplatform FOUND at: {spec.origin}")
    else:
        print("neuroplatform NOT found")
except Exception as e:
    print(f"Error: {e}")

# Also check pip
import subprocess, sys
result = subprocess.run([sys.executable, '-m', 'pip', 'index', 'versions', 'neuroplatform'], 
                       capture_output=True, text=True)
print(f"pip: {result.stdout.strip() or result.stderr.strip()}")
