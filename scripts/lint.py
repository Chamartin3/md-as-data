#!/usr/bin/env python3
"""Unified linting script that runs ruff and pyright with fixing capabilities."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Run unified linting with optional fixing."""
    fix_mode = "--fix" in sys.argv
    project_root = Path(__file__).parent.parent

    print("🚀 Running unified lint check...")
    if fix_mode:
        print("🔧 Fix mode enabled - will attempt to auto-fix issues")

    success = True

    # Run ruff check (with optional fixing)
    ruff_cmd = ["uv", "run", "ruff", "check", str(project_root)]
    if fix_mode:
        ruff_cmd.append("--fix")

    if not run_command(ruff_cmd, "Ruff linting"):
        success = False

    # Run ruff format
    format_cmd = ["uv", "run", "ruff", "format", str(project_root)]
    if not run_command(format_cmd, "Ruff formatting"):
        success = False

    # Run pyright
    pyright_cmd = ["uv", "run", "pyright", str(project_root)]
    if not run_command(pyright_cmd, "Pyright type checking"):
        success = False

    if success:
        print("✅ All lint checks passed!")
        return 0
    else:
        print("❌ Some lint checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
