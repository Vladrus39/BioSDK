"""Fix baselines_v85.py: move from __future__ import before bare string literal."""
import re

path = r'biogpu\validation\baselines_v85.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: split on the second docstring (the CAVEAT one)
# Find the position of the CAVEAT docstring
caveat_start = content.find('\n"""\n\u26a0\ufe0f CAVEAT')
if caveat_start < 0:
    caveat_start = content.find('\n"""\nCAVEAT')
if caveat_start < 0:
    for i, ch in enumerate(content):
        if ch == '\u26a0':
            caveat_start = content.rfind('\n"""\n', 0, i)
            break

print(f"CAVEAT start position: {caveat_start}")

# Remove the from __future__ line wherever it is
future_pattern = re.compile(r'\nfrom __future__ import annotations\n')
content = future_pattern.sub('\n', content, count=1)

# Now find the CAVEAT docstring again
caveat_start = content.find('\n"""\n\u26a0\ufe0f')
if caveat_start < 0:
    caveat_start = content.find('\n"""\nCAVEAT')

print(f"CAVEAT start (after removal): {caveat_start}")

# Insert from __future__ right before the CAVEAT docstring
insert_pos = caveat_start
content = content[:insert_pos] + '\nfrom __future__ import annotations' + content[insert_pos:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
future_pos = None
caveat_pos = None
for i, line in enumerate(lines):
    if 'from __future__' in line:
        future_pos = i + 1
    if 'CAVEAT' in line and caveat_pos is None and i > 0 and lines[i-1].strip() == '"""':
        caveat_pos = i + 1

print(f"from __future__ at line: {future_pos}")
print(f"CAVEAT docstring at line: {caveat_pos}")
print(f"Fix result: {'OK' if future_pos and caveat_pos and future_pos < caveat_pos else 'FAILED'}")

if future_pos:
    for j in range(max(0, future_pos-2), min(len(lines), future_pos+3)):
        print(f"  {j+1}: {lines[j].rstrip()}")
