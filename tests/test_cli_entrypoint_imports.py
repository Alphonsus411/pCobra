from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
REGRESSION_IMPORT = "scripts.benchmarks"


pytestmark = [
    pytest.mark.timeout(5),
]


def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    """Ejecuta Python aislado (-I) agregando solo `src/` al `sys.path`."""

    bootstrap = (
        "import os, sys; "
        "assert 'PYTHONPATH' not in os.environ, 'PYTHONPATH debe venir limpio con -I'; "
        f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", bootstrap + code],
        capture_output=True,
        text=True,
    )


def test_cli_main_smoke_help_en_entorno_aislado() -> None:
    """Smoke test rápido: el arranque de CLI con ayuda no debe romper imports."""

    result = _run_python_isolated(
        "from pcobra.cli import main; "
        "raise SystemExit(main(['--ayuda']))"
    )

    assert result.returncode == 0, (
        "Invocar pcobra.cli.main(['--ayuda']) debe funcionar en entorno aislado. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr, (
        "No debe aparecer ModuleNotFoundError al arrancar CLI con --ayuda. "
        f"stderr={result.stderr!r}"
    )


def test_import_bench_cmd_no_depende_de_scripts_py_path() -> None:
    """Protege la regresión de import legacy `scripts.benchmarks`."""

    result = _run_python_isolated(
        "import pcobra.cobra.cli.commands.bench_cmd as bench_cmd; "
        "assert bench_cmd.BenchCommand.name == 'bench'"
    )

    assert result.returncode == 0, (
        "Importar pcobra.cobra.cli.commands.bench_cmd debe funcionar en entorno "
        "aislado sin scripts/ en PYTHONPATH. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr, (
        "Se detectó ModuleNotFoundError al importar bench_cmd. "
        f"stderr={result.stderr!r}"
    )
    assert REGRESSION_IMPORT not in result.stderr, (
        "Regresión detectada: el import de bench_cmd volvió a depender de "
        f"`{REGRESSION_IMPORT}`. Actualiza los imports al módulo canónico bajo "
        "`pcobra.cobra`. "
        f"stderr={result.stderr!r}"
    )
