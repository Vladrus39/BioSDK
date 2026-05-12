"""Fix baselines_v85.py: move from __future__ before bare string literal."""
path = 'biogpu/validation/baselines_v85.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the from __future__ import line and move it up
old = '"""\n\n"""\n⚠️ CAVEAT'
new = '"""\nfrom __future__ import annotations\n\n"""\n⚠️ CAVEAT'
content = content.replace(old, new)

# Remove the old from __future__ import line that's now below
content = content.replace('\nfrom __future__ import annotations\n', '\n', 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed baselines_v85.py")

# Verify
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines[:10], 1):
    print(f"  {i}: {line.rstrip()}")
