"""Check pypirc for real PyPI config."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
pypirc = os.path.expanduser('~/.pypirc')
try:
    with open(pypirc, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if 'token' in line.lower() or 'password' in line.lower():
                key, _, _ = line.partition(':')
                print(f'{key.strip()}: ***')
            else:
                print(line)
except FileNotFoundError:
    print(f'File not found: {pypirc}')
