from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_ci_lint_no_legacy_bindings_imports_guard_passes_on_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/ci/lint_no_legacy_bindings_imports.py"],
        cwd=repo_root,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    assert result.returncode == 0, result.stdout + result.stderr
