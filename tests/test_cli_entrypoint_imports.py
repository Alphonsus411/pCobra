from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    """Ejecuta Python aislado (-I) agregando solo `src/` al `sys.path`."""

    bootstrap = (
        "import sys; "
        f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", bootstrap + code],
        capture_output=True,
        text=True,
    )


def test_cli_main_carga_registro_sin_import_legacy_scripts_benchmarks() -> None:
    # Protege regresión por import legacy de scripts.benchmarks al cargar comandos.
    result = _run_python_isolated(
        "from pcobra.cli import main; "
        "raise SystemExit(main(['--ayuda']))"
    )

    assert result.returncode == 0, (
        "Invocar pcobra.cli:main con --ayuda debe cargar comandos sin fallar. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr
    assert "scripts.benchmarks" not in result.stderr
