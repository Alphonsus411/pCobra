from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

LEGACY_BACKEND_MODULES = (
    "pcobra.cobra.transpilers.transpiler.to_go",
    "pcobra.cobra.transpilers.transpiler.to_cpp",
    "pcobra.cobra.transpilers.transpiler.to_java",
    "pcobra.cobra.transpilers.transpiler.to_wasm",
    "pcobra.cobra.transpilers.transpiler.to_asm",
    "pcobra.cobra.internal_compat.legacy_contracts",
    "pcobra.cobra.cli.internal_compat.legacy_targets",
)


def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    bootstrap = "import sys; " + f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    return subprocess.run([sys.executable, "-I", "-c", bootstrap + code], capture_output=True, text=True)


def test_cli_import_contract_usa_solo_backends_publicos():
    assert len(PUBLIC_BACKENDS) == 3
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_politica_publica_targets_falla_si_hay_targets_extra():
    result = _run_python_isolated(
        "from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS; "
        "assert PUBLIC_BACKENDS == ('python','javascript','rust'); "
        "assert tuple(PUBLIC_BACKENDS + ('go',)) != ('python','javascript','rust')"
    )
    assert result.returncode == 0, result.stderr


def test_startup_import_y_comandos_publicos_no_cargan_legacy_backends():
    checks = [
        "import pcobra; import sys",
        "import pcobra.cli; import sys",
    ]
    for code in checks:
        prepared = "LEGACY=" + repr(LEGACY_BACKEND_MODULES) + "; " + code + "; assert not any(name in sys.modules for name in LEGACY)"
        result = _run_python_isolated(prepared)
        assert result.returncode == 0, result.stderr

    env = {**os.environ, "PYTHONPATH": str(SRC_ROOT)}
    for cmd in (("-m", "pcobra.cli", "repl", "--help"), ("-m", "pcobra.cli", "run", "--help"), ("-m", "pcobra.cli", "test", "--help")):
        result = subprocess.run([sys.executable, *cmd], capture_output=True, text=True, env=env)
        assert result.returncode == 0, result.stderr
        assert "legacy" not in result.stderr.lower()
