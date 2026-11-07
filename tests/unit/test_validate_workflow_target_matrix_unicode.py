"""Regresión CP1252 para la política de workflows en Windows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "validate_workflow_target_matrix.py"
WINDOWS_CP1252_BOOTSTRAP = """
import runpy
import sys

sys.stdout.reconfigure(encoding="cp1252")
sys.platform = "win32"
runpy.run_path(sys.argv[1], run_name="__main__")
"""


def test_validate_workflow_target_matrix_preserva_salida_cp1252_en_windows_simulado() -> None:
    result = subprocess.run(
        [sys.executable, "-c", WINDOWS_CP1252_BOOTSTRAP, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert (
        "✅ Validación de política de targets en workflows: OK"
        in result.stdout.decode("utf-8")
    )
