import subprocess, sys

print("=== Проверка biosdk ===")

# 1. Проверить, установлен ли уже
try:
    import biosdk
    print(f"biosdk установлен: {biosdk.__file__}")
    if hasattr(biosdk, '__version__'):
        print(f"  Версия: {biosdk.__version__}")
except ImportError:
    print("biosdk НЕ установлен")

# 2. Проверить локальный wheel
from pathlib import Path
wheel = Path("dist/biosdk-0.1.0-py3-none-any.whl")
if wheel.exists():
    print(f"\nЛокальный wheel: {wheel} ({wheel.stat().st_size/1024:.0f} KB)")
else:
    print(f"\nЛокальный wheel НЕ найден")

# 3. Попробовать установить из локального wheel в --dry-run
print("\n=== Проверка установки из локального wheel ===")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "--dry-run", str(wheel)],
    capture_output=True, text=True
)
print(result.stdout[-500:] if result.stdout else "no stdout")
if result.stderr:
    print("STDERR:", result.stderr[-300:])

# 4. Проверить test.pypi.org
print("\n=== Проверка test.pypi.org ===")
result2 = subprocess.run(
    [sys.executable, "-m", "pip", "install", "--dry-run", "-i", "https://test.pypi.org/simple/", "biosdk"],
    capture_output=True, text=True
)
print(result2.stdout[-500:] if result2.stdout else "no stdout")
if result2.stderr:
    print("STDERR:", result2.stderr[-300:])

# 5. Проверить pypirc
pypirc = Path.home() / ".pypirc"
if pypirc.exists():
    print(f"\n.pypirc существует: {pypirc}")
    content = pypirc.read_text()
    # Показать только структуру, скрывая токены
    for line in content.split("\n"):
        if "password" in line.lower() or "token" in line.lower():
            print(f"  {line.split('=')[0].strip()}=***")
        else:
            print(f"  {line.strip()}")
else:
    print("\n.pypirc НЕ найден")

# 6. Проверить, что внутри biosdk пакета
print("\n=== Содержимое biosdk ===")
biosdk_dir = Path("biosdk")
if biosdk_dir.exists():
    for f in biosdk_dir.rglob("*.py"):
        print(f"  {f}")
else:
    print("  biosdk/ не найден")
