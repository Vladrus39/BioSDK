"""Read tail of master plan - last 80 lines."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('docs/MASTER_PROJECT_PLAN_V50.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Total lines: {len(lines)}\n')
for line in lines[-80:]:
    print(line.rstrip())
