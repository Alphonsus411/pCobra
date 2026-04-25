from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_ci_lint_import_resolution_contract_guard_passes_on_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/ci/lint_import_resolution_contract.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
