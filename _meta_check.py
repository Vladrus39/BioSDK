import importlib.metadata, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
m = importlib.metadata.metadata('biosdk')
print("=== METADATA ===")
for k, v in m.items():
    if k != 'Description':
        print(f"{k}: {v}")
print("\n=== CLASSIFIERS ===")
for c in m.get_all('Classifier', []):
    print(f"  {c}")
