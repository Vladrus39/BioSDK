"""
BioSDK -- Universal Deploy Script
================================
ONE command to ship a new release:
  1. Bump version across every project file (pyproject, README, CHANGELOG,
     SECURITY, .env header, PROJECT_STATUS_V85.json).
  2. Build wheel + sdist.
  3. Upload to TestPyPI (default) or PyPI (--prod) using PYPI_TOKEN from .env.
  4. Commit + annotated tag + push to GitHub using GITHUB_TOKEN from .env.
  5. Verify the published package round-trips (pip install + import check).

Quick usage
-----------
  python _deploy.py --bump patch --notes "Doc updates"
  python _deploy.py --version 0.2.0 --notes "Adapter X added"
  python _deploy.py --prod                    # publish to real PyPI
  python _deploy.py --dry-run                 # print plan, change nothing
  python _deploy.py --bump-only patch         # only update files, don't build/upload/push
  python _deploy.py --check                   # only run pre-flight checks

Notes on tokens
---------------
- `.env` (gitignored) holds GITHUB_TOKEN and PYPI_TOKEN.
- They are read once, exported into the subprocess env, and never echoed to stdout.
- If a token is missing, the script refuses the corresponding step (--skip-* makes that explicit).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"

# ──────────────────────────────────────────────────────────────────────
# Files that carry the project version. Each entry is (path, [substitutions]).
# Substitutions are regex pairs applied to the file text. They must be
# precise enough to NOT touch unrelated "vNN" session markers.
# ──────────────────────────────────────────────────────────────────────
VERSION_FILES: list[tuple[str, list[tuple[str, str]]]] = [
    ("pyproject.toml", [
        (r'^version\s*=\s*"\d+\.\d+\.\d+"', 'version = "{new}"'),
    ]),
    ("README.md", [
        # **v0.1.4 | 7 NSI-1.0 adapters | ...
        (r"\*\*v\d+\.\d+\.\d+\s*\|", "**v{new} |"),
        # *BioSDK v0.1.4. Open Core. ...
        (r"\*BioSDK\s+v\d+\.\d+\.\d+\.", "*BioSDK v{new}."),
    ]),
    (".env", [
        # # v0.1.3 | 2026-05-12
        (r"#\s*v\d+\.\d+\.\d+\s*\|\s*\d{4}-\d{2}-\d{2}", "# v{new} | {today}"),
    ]),
    ("PROJECT_STATUS_V85.json", [
        (r'"version"\s*:\s*"v?\d+\.\d+\.\d+"', '"version": "v{new}"'),
    ]),
    ("SECURITY.md", []),  # handled separately, see update_security()
    ("CHANGELOG.md", []),  # handled separately, see update_changelog()
]


# ──────────────────────────────────────────────────────────────────────
# .env loader (no extra dependencies)
# ──────────────────────────────────────────────────────────────────────
def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def redact(token: Optional[str]) -> str:
    if not token:
        return "<empty>"
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}…{token[-4:]}"


# ──────────────────────────────────────────────────────────────────────
# Subprocess helpers
# ──────────────────────────────────────────────────────────────────────
def run(cmd: str, *, env: Optional[dict] = None, check: bool = True,
        capture: bool = False, quiet: bool = False) -> subprocess.CompletedProcess:
    if not quiet:
        # Never echo tokens. Strip TWINE_* / *_TOKEN from any cmd that uses them.
        printable = re.sub(r"(pypi-[A-Za-z0-9_\-]{20,}|github_pat_[A-Za-z0-9_]{20,})", "***", cmd)
        print(f"  $ {printable}")
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd, shell=True, cwd=str(ROOT), env=full_env,
        capture_output=capture, text=True,
    )
    if check and proc.returncode != 0:
        if capture:
            print(proc.stdout)
            print(proc.stderr)
        print(f"  FAILED (exit {proc.returncode})")
        sys.exit(proc.returncode)
    return proc


# ──────────────────────────────────────────────────────────────────────
# Version helpers
# ──────────────────────────────────────────────────────────────────────
VERSION_RE = re.compile(r"^version\s*=\s*\"(\d+\.\d+\.\d+)\"\s*$", re.M)


def current_version() -> str:
    txt = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = VERSION_RE.search(txt)
    if not m:
        sys.exit("Could not find version = \"X.Y.Z\" in pyproject.toml")
    return m.group(1)


def bump_version(ver: str, kind: str) -> str:
    major, minor, patch = (int(x) for x in ver.split("."))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    sys.exit(f"Unknown bump kind: {kind!r}")


# ──────────────────────────────────────────────────────────────────────
# File rewriters
# ──────────────────────────────────────────────────────────────────────
def apply_substitutions(text: str, subs: list[tuple[str, str]],
                        new: str, today: str) -> tuple[str, int]:
    total = 0
    for pattern, repl in subs:
        repl_filled = repl.format(new=new, today=today)
        text, n = re.subn(pattern, repl_filled, text, flags=re.M)
        total += n
    return text, total


def update_simple_files(new: str, today: str, dry: bool) -> None:
    """Update pyproject.toml, README.md, .env, PROJECT_STATUS_V85.json."""
    for relpath, subs in VERSION_FILES:
        if not subs:
            continue
        path = ROOT / relpath
        if not path.exists():
            print(f"  - skip {relpath} (not found)")
            continue
        orig = path.read_text(encoding="utf-8")
        new_text, n = apply_substitutions(orig, subs, new=new, today=today)
        if n == 0:
            print(f"  - {relpath}: no version match (already at {new}?)")
            continue
        if dry:
            print(f"  - {relpath}: would update {n} occurrence(s)")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"  - {relpath}: updated {n} occurrence(s) -> v{new}")


def update_security(new: str, dry: bool) -> None:
    """Prepend new version to the supported-versions table in SECURITY.md."""
    path = ROOT / "SECURITY.md"
    if not path.exists():
        return
    txt = path.read_text(encoding="utf-8")
    # Already listed?
    if re.search(rf"^\|\s*{re.escape(new)}\s*\|", txt, re.M):
        print(f"  - SECURITY.md: {new} already in supported-versions table")
        return
    # Find the row after the header underline and insert.
    marker_re = re.compile(r"(\|---------\|-----------\|\n)")
    if not marker_re.search(txt):
        print("  - SECURITY.md: supported-versions table not found, skipped")
        return
    new_row = f"| {new}   | Yes       |\n"
    new_txt = marker_re.sub(lambda m: m.group(1) + new_row, txt, count=1)
    if dry:
        print(f"  - SECURITY.md: would add row '{new}'")
    else:
        path.write_text(new_txt, encoding="utf-8")
        print(f"  - SECURITY.md: added row '{new}'")


def update_changelog(new: str, today: str, notes: Optional[str], dry: bool) -> None:
    """Prepend a new [X.Y.Z] section to CHANGELOG.md."""
    path = ROOT / "CHANGELOG.md"
    if not path.exists():
        print("  - CHANGELOG.md: not found, skipped")
        return
    txt = path.read_text(encoding="utf-8")
    # Already has this version?
    if re.search(rf"^##\s+\[{re.escape(new)}\]", txt, re.M):
        print(f"  - CHANGELOG.md: section [{new}] already present, skipped")
        return
    body = notes.strip() if notes else "_TODO: describe changes._"
    # Each note line gets a "- " prefix; multi-line notes are kept verbatim.
    if notes and not notes.lstrip().startswith("-"):
        # Treat as a single bullet if no leading dash provided.
        body = "- " + body
    section = (
        f"## [{new}] -- {today}\n"
        f"\n"
        f"### Changed\n"
        f"{body}\n"
        f"\n"
    )
    # Insert after the leading header block, before the first existing section.
    parts = txt.split("\n## ", 1)
    if len(parts) == 2:
        head, rest = parts
        new_txt = head.rstrip() + "\n\n" + section + "## " + rest
    else:
        new_txt = txt.rstrip() + "\n\n" + section
    if dry:
        print(f"  - CHANGELOG.md: would prepend section [{new}]")
    else:
        path.write_text(new_txt, encoding="utf-8")
        print(f"  - CHANGELOG.md: prepended section [{new}]")


def set_everything(new: str, notes: Optional[str], dry: bool) -> None:
    today = date.today().isoformat()
    print(f"\n[bump] writing v{new} (today={today}) into project files:")
    update_simple_files(new, today, dry)
    update_security(new, dry)
    update_changelog(new, today, notes, dry)


# ──────────────────────────────────────────────────────────────────────
# Build / upload / git
# ──────────────────────────────────────────────────────────────────────
def python_cmd(env_map: dict[str, str]) -> str:
    return env_map.get("PYTHON_PATH") or os.environ.get("PYTHON_PATH") or sys.executable


def clean_dist() -> None:
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)


def build(py: str, dry: bool) -> None:
    print("\n[build] wheel + sdist")
    if dry:
        print("  (dry-run) skipped")
        return
    clean_dist()
    run(f'"{py}" -m build')


def upload(py: str, env_map: dict[str, str], prod: bool, dry: bool) -> None:
    repo = "pypi" if prod else "testpypi"
    print(f"\n[upload] -> {repo}")
    token = env_map.get("PYPI_TOKEN") or os.environ.get("PYPI_TOKEN")
    if not token:
        sys.exit(f"  PYPI_TOKEN missing in .env (needed for {repo})")
    if dry:
        print(f"  (dry-run) would twine upload to {repo} using token {redact(token)}")
        return
    files = sorted((ROOT / "dist").glob("*"))
    if not files:
        sys.exit("  no artifacts in dist/ -- build first")
    twine_env = {
        "TWINE_USERNAME": "__token__",
        "TWINE_PASSWORD": token,
        "TWINE_NON_INTERACTIVE": "1",
    }
    files_arg = " ".join(f'"{f}"' for f in files)
    run(f'"{py}" -m twine upload --repository {repo} {files_arg}', env=twine_env)


def git_authed_remote(env_map: dict[str, str]) -> Optional[str]:
    token = env_map.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    user = env_map.get("GITHUB_USER", "")
    repo = env_map.get("GITHUB_REPO", "")
    if not (token and user and repo):
        return None
    return f"https://x-access-token:{token}@github.com/{user}/{repo}.git"


def git_release(version: str, env_map: dict[str, str], dry: bool,
                allow_dirty: bool) -> None:
    print("\n[git] commit + tag + push")
    if dry:
        print("  (dry-run) would: git add -A; git commit; git tag; git push")
        return
    # Status check
    proc = run("git status --porcelain", capture=True, quiet=True)
    if not proc.stdout.strip() and not allow_dirty:
        print("  nothing staged -- repo is already clean (no commit will be made)")
    else:
        run("git add -A")
        # Was anything actually staged?
        staged = run("git diff --cached --quiet", check=False, quiet=True)
        if staged.returncode == 1:
            run(f'git commit -m "BioSDK v{version}"')
        else:
            print("  nothing to commit")

    # Tag (idempotent: skip if exists)
    tag = f"v{version}"
    proc = run(f"git tag -l {tag}", capture=True, quiet=True)
    if proc.stdout.strip():
        print(f"  tag {tag} already exists, leaving it")
    else:
        run(f'git tag -a {tag} -m "BioSDK {tag}"')

    # Push
    authed = git_authed_remote(env_map)
    if authed:
        # Push without exposing the URL in logs (run() redacts patterns).
        run(f"git push {authed} HEAD")
        run(f"git push {authed} {tag}")
    else:
        print("  GITHUB_TOKEN not set -- falling back to default remote (relies on git credentials)")
        run("git push")
        run(f"git push origin {tag}")


def verify(py: str, version: str, prod: bool, dry: bool) -> None:
    print("\n[verify] pip install + import")
    if dry:
        print("  (dry-run) skipped")
        return
    index = "https://pypi.org/simple/" if prod else "https://test.pypi.org/simple/"
    run(
        f'"{py}" -m pip install -i {index} biosdk=={version} '
        f'--force-reinstall --no-deps --quiet'
    )
    run(f'"{py}" -c "import biosdk; print(\'OK\', biosdk.__version__)"')


# ──────────────────────────────────────────────────────────────────────
# Pre-flight checks
# ──────────────────────────────────────────────────────────────────────
def preflight(env_map: dict[str, str], prod: bool, skip_pypi: bool, skip_git: bool) -> None:
    print("[preflight]")
    py = python_cmd(env_map)
    print(f"  python:    {py}")
    print(f"  root:      {ROOT}")
    print(f"  version:   {current_version()}")
    if not skip_pypi:
        token = env_map.get("PYPI_TOKEN") or ""
        print(f"  PYPI_TOKEN ({'pypi' if prod else 'testpypi'}): {redact(token)}")
        if not token:
            sys.exit("  PYPI_TOKEN is empty -- set in .env or pass --skip-pypi")
    if not skip_git:
        token = env_map.get("GITHUB_TOKEN") or ""
        print(f"  GITHUB_TOKEN: {redact(token)}")
        if not token:
            print("  warning: GITHUB_TOKEN empty -- will rely on local git credentials")
    # twine + build present?
    for mod in (["twine"] if not skip_pypi else []) + ["build"]:
        proc = run(f'"{py}" -m {mod} --version', check=False, capture=True, quiet=True)
        if proc.returncode != 0:
            sys.exit(f"  {mod} not installed in {py}. Run: \"{py}\" -m pip install {mod}")
        print(f"  {mod}:    {proc.stdout.strip().splitlines()[0]}")


# ──────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="_deploy.py",
        description="BioSDK universal deploy: bump -> build -> upload -> git -> verify.",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument("--version", help="Set explicit X.Y.Z (e.g. 0.1.5)")
    g.add_argument("--bump", choices=["patch", "minor", "major"],
                   help="Bump current version by this kind")
    g.add_argument("--bump-only", choices=["patch", "minor", "major"],
                   help="Only bump version files, skip build/upload/git/verify")

    p.add_argument("--notes", default=None,
                   help="Changelog notes for the new version (single bullet or multi-line)")
    p.add_argument("--prod", action="store_true",
                   help="Publish to real PyPI (default is TestPyPI)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print actions, do not change/build/upload/push")
    p.add_argument("--check", action="store_true",
                   help="Only run pre-flight checks")
    p.add_argument("--skip-build", action="store_true")
    p.add_argument("--skip-pypi", action="store_true")
    p.add_argument("--skip-git", action="store_true")
    p.add_argument("--skip-verify", action="store_true")
    p.add_argument("--allow-dirty", action="store_true",
                   help="Proceed even if git working tree has unrelated changes")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    env_map = load_env()

    if args.check:
        preflight(env_map, args.prod, args.skip_pypi, args.skip_git)
        print("\nOK")
        return

    # 1) Decide target version
    cur = current_version()
    if args.version:
        new = args.version
    elif args.bump:
        new = bump_version(cur, args.bump)
    elif args.bump_only:
        new = bump_version(cur, args.bump_only)
    else:
        new = cur  # re-deploy current version (no bump)

    print(f"BioSDK deploy: {cur} -> {new}")
    if args.dry_run:
        print("  (dry-run mode -- no writes, no network)")

    preflight(env_map, args.prod, args.skip_pypi, args.skip_git)

    # 2) Update files
    if new != cur:
        set_everything(new, args.notes, args.dry_run)

    if args.bump_only:
        print("\nbump-only mode: stopping here.")
        return

    py = python_cmd(env_map)

    # 3) Build
    if not args.skip_build:
        build(py, args.dry_run)

    # 4) Upload
    if not args.skip_pypi:
        upload(py, env_map, args.prod, args.dry_run)

    # 5) Git
    if not args.skip_git:
        git_release(new, env_map, args.dry_run, args.allow_dirty)

    # 6) Verify
    if not args.skip_pypi and not args.skip_verify:
        verify(py, new, args.prod, args.dry_run)

    print("\n" + "=" * 60)
    print(f"Done: BioSDK v{new}")
    repo = "https://pypi.org" if args.prod else "https://test.pypi.org"
    print(f"  PyPI:   {repo}/project/biosdk/{new}/")
    user = env_map.get("GITHUB_USER", "Vladrus39")
    repo_n = env_map.get("GITHUB_REPO", "BioSDK")
    print(f"  GitHub: https://github.com/{user}/{repo_n}/releases/tag/v{new}")
    print("=" * 60)


if __name__ == "__main__":
    main()
