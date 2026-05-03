from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    bootstrap = (
        "import os, sys; "
        "assert 'PYTHONPATH' not in os.environ; "
        f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", bootstrap + code],
        capture_output=True,
        text=True,
    )


def test_bootstrap_runtime_manager_no_carga_modulos_legacy() -> None:
    result = _run_python_isolated(
        "from pcobra.cobra.bindings.runtime_manager import RuntimeManager; "
        "RuntimeManager(); "
        "import sys; "
        "legacy_prefixes = ('core', 'bindings', 'scripts', 'cobra.core', 'core.'); "
        "assert not any(name == 'core' or name == 'bindings' or name.startswith(legacy_prefixes) for name in sys.modules), "
        "'RuntimeManager cargó imports legacy durante bootstrap';"
    )

    assert result.returncode == 0, result.stderr


def test_bootstrap_backend_pipeline_no_carga_backends_legado() -> None:
    result = _run_python_isolated(
        "import pcobra.cobra.build.backend_pipeline as bp; "
        "bp.resolve_backend_runtime('app.co', {'preferred_backend': 'python'}); "
        "import sys; "
        "legacy_modules = ('pcobra.cobra.transpilers.transpiler.to_go', 'pcobra.cobra.transpilers.transpiler.to_cpp', 'pcobra.cobra.transpilers.transpiler.to_java', 'pcobra.cobra.transpilers.transpiler.to_wasm', 'pcobra.cobra.transpilers.transpiler.to_asm'); "
        "assert not any(name in sys.modules for name in legacy_modules), "
        "'BackendPipeline cargó transpiladores legacy en flujo estándar';"
    )

    assert result.returncode == 0, result.stderr


def test_politica_publica_exacta_en_todos_los_contratos() -> None:
    from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
    from pcobra.cobra.bindings.contract import OFFICIAL_PUBLIC_LANGUAGES
    from pcobra.cobra.bindings.contract import OFFICIAL_PUBLIC_ROUTE_MATRIX

    expected = ("python", "javascript", "rust")
    assert PUBLIC_BACKENDS == expected
    assert OFFICIAL_PUBLIC_LANGUAGES == expected
    assert tuple(OFFICIAL_PUBLIC_ROUTE_MATRIX.keys()) == expected
