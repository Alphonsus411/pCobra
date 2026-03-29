from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    """Ejecuta Python aislado (-I) y sólo añade `src/` al sys.path dentro del proceso."""

    bootstrap = (
        "import sys; "
        f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", bootstrap + code],
        capture_output=True,
        text=True,
    )


def test_import_pcobra_cli_no_depende_de_scripts_runtime() -> None:
    """`scripts/` es tooling de desarrollo y no debe ser dependencia de runtime."""

    result = _run_python_isolated(
        "import pcobra.cli; print('ok')"
    )

    assert result.returncode == 0, (
        f"Fallo importando pcobra.cli en entorno aislado. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr
    assert "scripts" not in result.stderr.lower()


def test_import_canonical_cli_application_no_module_not_found_scripts() -> None:
    result = _run_python_isolated(
        "from pcobra.cobra.cli.cli import CliApplication; "
        "print(CliApplication.__name__)"
    )

    assert result.returncode == 0, (
        "El import de CliApplication no debe fallar por dependencias de desarrollo. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr
    assert "scripts" not in result.stderr.lower()


def test_cli_application_prepare_parser_carga_comandos_sin_imports_rotos() -> None:
    result = _run_python_isolated(
        "from pcobra.cobra.cli.cli import CliApplication; "
        "app = CliApplication(); "
        "app.initialize(); "
        "app._ensure_command_structure(); "
        "print(len(app.command_registry.commands))"
    )

    assert result.returncode == 0, (
        "Preparar el parser y registrar comandos debe funcionar sin imports rotos. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr
    assert "scripts" not in result.stderr.lower()

    num_commands = int(result.stdout.strip().splitlines()[-1])
    assert num_commands > 0
