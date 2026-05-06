from __future__ import annotations

import subprocess
import sys
import tomllib
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


def test_pyproject_entrypoint_cobra_se_mantiene_canonico() -> None:
    """Contrato: el entrypoint público debe seguir apuntando a ``pcobra.cli:main``."""

    pyproject = REPO_ROOT / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)

    scripts = data.get("project", {}).get("scripts", {})
    assert scripts.get("cobra") == "pcobra.cli:main"


def test_cli_entrypoint_importa_modulos_instalables_unicamente() -> None:
    """El import del entrypoint no debe requerir paquetes ``scripts.*``."""

    result = _run_python_isolated(
        "from pcobra.cli import main; "
        "import sys; "
        "assert callable(main); "
        "assert not any(name == 'scripts' or name.startswith('scripts.') "
        "for name in sys.modules), "
        "'Se importó scripts.* durante bootstrap de pcobra.cli'; "
    )

    assert result.returncode == 0, (
        "El entrypoint pcobra.cli:main no debe depender de scripts.* "
        "en import-time. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
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


def test_cli_startup_preserva_utf8_en_literal_imprimir() -> None:
    """Contrato: startup de CLI debe preservar UTF-8 sin mojibake en salida."""

    result = _run_python_isolated(
        "import tempfile; "
        "from pathlib import Path; "
        "from pcobra.cli import main; "
        "tmp = Path(tempfile.gettempdir()) / 'pcobra_utf8_test.co'; "
        "tmp.write_text('imprimir(\"áéíóú ñ € 🚀\")\\n', encoding='utf-8'); "
        "raise SystemExit(main(['ejecutar', str(tmp)]))"
    )

    assert result.returncode == 0, (
        "La ejecución de `imprimir` con literal UTF-8 debe finalizar correctamente. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "áéíóú ñ € 🚀" in result.stdout, (
        "La salida UTF-8 del CLI debe preservarse sin mojibake. "
        f"stdout={result.stdout!r}"
    )
    assert "Ã¡" not in result.stdout and "â" not in result.stdout, (
        "Se detectó posible mojibake en salida de CLI. "
        f"stdout={result.stdout!r}"
    )


def test_cli_bootstrap_no_monkey_patchea_lexer() -> None:
    """Contrato: bootstrap de CLI no debe mutar métodos de ``Lexer``."""

    result = _run_python_isolated(
        "from pcobra.cobra.core.lexer import Lexer; "
        "before = Lexer._procesar_cadena; "
        "from pcobra.cli import main; "
        "rc = main(['--ayuda']); "
        "after = Lexer._procesar_cadena; "
        "assert rc == 0; "
        "assert before is after, "
        "'pcobra.cli bootstrap no debe monkey-patchear Lexer._procesar_cadena'; "
    )

    assert result.returncode == 0, (
        "El bootstrap CLI debe preservar el método original del lexer. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


@pytest.mark.parametrize("command,argv", [("repl", ["repl", "-h"]), ("run", ["run", "-h"]), ("test", ["test", "-h"])])
def test_cli_public_commands_do_not_import_legacy_transpilers_on_startup(command: str, argv: list[str]) -> None:
    """`repl`/`ejecutar`/`test` no deben cargar módulos legacy en import/startup."""

    result = _run_python_isolated(
        f"from pcobra.cli import main; rc = main({argv!r}); "
        "import sys; "
        "legacy_markers = ("
        "'pcobra.cobra.transpilers.transpiler.to_go',"
        "'pcobra.cobra.transpilers.transpiler.to_cpp',"
        "'pcobra.cobra.transpilers.transpiler.to_java',"
        "'pcobra.cobra.transpilers.transpiler.to_wasm',"
        "'pcobra.cobra.transpilers.transpiler.to_asm',"
        "'pcobra.cobra.internal_compat.legacy_contracts',"
        "); "
        "loaded = sorted(name for name in sys.modules if name in legacy_markers); "
        "assert rc == 0; "
        "assert not loaded, f'Startup cargó módulos legacy: {loaded}'; ",
    )

    assert result.returncode == 0, (
        "Las rutas públicas no deben cargar transpilers legacy en startup. "
        f"command={command!r} stdout={result.stdout!r} stderr={result.stderr!r}"
    )
