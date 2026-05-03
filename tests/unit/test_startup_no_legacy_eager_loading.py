import importlib
import subprocess
import sys
from pathlib import Path

LEGACY_TRANSPILER_MODULES = (
    "pcobra.cobra.transpilers.transpiler.to_go",
    "pcobra.cobra.transpilers.transpiler.to_cpp",
    "pcobra.cobra.transpilers.transpiler.to_java",
    "pcobra.cobra.transpilers.transpiler.to_wasm",
    "pcobra.cobra.transpilers.transpiler.to_asm",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


def _purge_modules(prefixes: tuple[str, ...]) -> None:
    for name in list(sys.modules):
        if name.startswith(prefixes):
            sys.modules.pop(name, None)


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


def _legacy_assertion_snippet() -> str:
    return (
        "import sys; "
        "legacy_modules = ("
        "'pcobra.cobra.transpilers.transpiler.to_go',"
        "'pcobra.cobra.transpilers.transpiler.to_cpp',"
        "'pcobra.cobra.transpilers.transpiler.to_java',"
        "'pcobra.cobra.transpilers.transpiler.to_wasm',"
        "'pcobra.cobra.transpilers.transpiler.to_asm'"
        "); "
        "assert not any(name in sys.modules for name in legacy_modules), "
        "'startup cargó backends legacy eager';"
    )


def test_import_pcobra_no_precarga_transpiladores_legacy():
    _purge_modules(("pcobra", "cobra", "core"))

    importlib.import_module("pcobra")

    for module_name in LEGACY_TRANSPILER_MODULES:
        assert module_name not in sys.modules


def test_import_backend_pipeline_no_precarga_legacy():
    _purge_modules(("pcobra",))

    importlib.import_module("pcobra.cobra.build.backend_pipeline")

    for module_name in LEGACY_TRANSPILER_MODULES:
        assert module_name not in sys.modules


def test_import_cli_no_precarga_transpiladores_legacy():
    result = _run_python_isolated(
        "import pcobra.cobra.cli.cli; " + _legacy_assertion_snippet()
    )

    assert result.returncode == 0, result.stderr


def test_import_comandos_run_repl_test_no_precarga_transpiladores_legacy():
    result = _run_python_isolated(
        "import pcobra.cobra.cli.commands_v2.run_cmd; "
        "import pcobra.cobra.cli.commands_v2.repl_cmd; "
        "import pcobra.cobra.cli.commands_v2.test_cmd; "
        + _legacy_assertion_snippet()
    )

    assert result.returncode == 0, result.stderr


def test_public_backends_permancen_exactamente_tres():
    policy = importlib.import_module("pcobra.cobra.architecture.backend_policy")
    contracts = importlib.import_module("pcobra.cobra.architecture.contracts")
    assert policy.PUBLIC_BACKENDS == ("python", "javascript", "rust")
    assert contracts.PUBLIC_BACKENDS == ("python", "javascript", "rust")
