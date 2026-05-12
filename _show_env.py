"""Read .env file."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    # Mask actual token values, show structure
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            print(line)
        elif '=' in line:
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if any(kw in key.upper() for kw in ('TOKEN', 'KEY', 'SECRET', 'PASSWORD', 'PASS')):
                mask = value[:8] + '...' + value[-4:] if len(value) > 15 else '***'
                print(f'{key}={mask}')
            else:
                print(f'{key}={value}')
except FileNotFoundError:
    print('.env file not found')
