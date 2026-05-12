"""
BioSDK — Unified Deploy Script
================================
One command to:
  1. Build wheel
  2. Upload to TestPyPI
  3. Commit + push to GitHub
  4. Verify install

Usage:
  python _deploy.py                  # full deploy
  python _deploy.py --build-only     # just build wheel
  python _deploy.py --pypi-only      # build + upload
  python _deploy.py --version 0.1.4  # bump version first
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = os.environ.get("PYTHON_PATH", "python")
PROJECT = "biosdk"
REPO = "testpypi"


def run(cmd, **kw):
    """Run a command and print output."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(ROOT), **kw)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})")
        sys.exit(1)
    return result


def get_version():
    """Read version from pyproject.toml."""
    txt = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for line in txt.splitlines():
        if line.strip().startswith('version'):
            return line.split('"')[1]
    return None


def set_version(new_ver):
    """Bump version in pyproject.toml and README.md."""
    for fname in ["pyproject.toml", "README.md"]:
        path = ROOT / fname
        txt = path.read_text(encoding="utf-8")
        old_ver = get_version()
        txt = txt.replace(f'version = "{old_ver}"', f'version = "{new_ver}"')
        txt = txt.replace(f"v{old_ver}", f"v{new_ver}")
        path.write_text(txt, encoding="utf-8")
        print(f"  Updated {fname}: {old_ver} -> {new_ver}")


def build():
    """Build the wheel."""
    print("\n[1/4] Building wheel...")
    run(f'{PYTHON} -m build --wheel')


def upload():
    """Upload to TestPyPI."""
    print("\n[2/4] Uploading to TestPyPI...")
    whl = sorted(ROOT.glob(f"dist/{PROJECT}-*.whl"))[-1]
    run(f'{PYTHON} -m twine upload --repository {REPO} "{whl}"')


def git_push():
    """Commit and push to GitHub."""
    print("\n[3/4] Pushing to GitHub...")
    ver = get_version()

    # Stage changes
    run("git add -A")

    # Check if there's anything to commit
    result = subprocess.run(
        "git diff --cached --quiet",
        shell=True, cwd=str(ROOT),
        capture_output=True,
    )
    if result.returncode == 1:
        run(f'git commit -m "BioSDK v{ver} deploy"')
    else:
        print("  Nothing to commit")

    run("git push")


def verify():
    """Install from TestPyPI and verify."""
    print("\n[4/4] Verifying install...")
    ver = get_version()
    run(
        f'{PYTHON} -m pip install -i https://test.pypi.org/simple/ '
        f'{PROJECT}=={ver} --force-reinstall --no-deps'
    )
    run(f'{PYTHON} -c "import {PROJECT}; print(\'OK:\', {PROJECT}.__version__)"')


def main():
    args = sys.argv[1:]

    # --version X.Y.Z
    if "--version" in args:
        idx = args.index("--version")
        new_ver = args[idx + 1]
        print(f"Bumping version: {new_ver}")
        set_version(new_ver)

    ver = get_version()
    print(f"BioSDK v{ver} deploy")
    print(f"  Python: {PYTHON}")
    print(f"  Project root: {ROOT}")

    build_only = "--build-only" in args
    pypi_only = "--pypi-only" in args

    build()

    if build_only:
        whl = sorted(ROOT.glob(f"dist/{PROJECT}-*.whl"))[-1]
        print(f"\nWheel ready: {whl}")
        return

    upload()

    if pypi_only:
        print("\nUploaded to TestPyPI. Skipping git push and verify.")
        return

    git_push()
    verify()

    print(f"\n{'='*60}")
    print(f"Deploy complete: BioSDK v{ver}")
    print(f"  PyPI:    https://test.pypi.org/project/{PROJECT}/{ver}/")
    print(f"  GitHub:  https://github.com/Vladrus39/BioSDK")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
