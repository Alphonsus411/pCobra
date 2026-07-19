import importlib
import subprocess
import sys
from pathlib import Path

import pytest

LEGACY_TRANSPILER_MODULES = (
    "pcobra.cobra.transpilers.transpiler.to_go",
    "pcobra.cobra.transpilers.transpiler.to_cpp",
    "pcobra.cobra.transpilers.transpiler.to_java",
    "pcobra.cobra.transpilers.transpiler.to_wasm",
    "pcobra.cobra.transpilers.transpiler.to_asm",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


def _purge_modules(prefixes: tuple[str, ...], monkeypatch: pytest.MonkeyPatch) -> None:
    modules = dict(sys.modules)
    for name, module in modules.items():
        if not name.startswith(prefixes) or "." not in name:
            continue
        parent_name, child_name = name.rsplit(".", 1)
        parent = modules.get(parent_name)
        if parent is not None and hasattr(parent, child_name):
            monkeypatch.setattr(parent, child_name, getattr(parent, child_name))

    for name in list(sys.modules):
        if name.startswith(prefixes):
            monkeypatch.delitem(sys.modules, name, raising=False)


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


def test_import_pcobra_no_precarga_transpiladores_legacy(monkeypatch):
    _purge_modules(("pcobra", "cobra", "core"), monkeypatch)

    importlib.import_module("pcobra")

    for module_name in LEGACY_TRANSPILER_MODULES:
        assert module_name not in sys.modules


def test_import_backend_pipeline_no_precarga_legacy(monkeypatch):
    _purge_modules(("pcobra",), monkeypatch)

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
        "import pcobra.cobra.cli.commands_v2.test_cmd; " + _legacy_assertion_snippet()
    )

    assert result.returncode == 0, result.stderr


def _run_cli_parse_isolated(subcommand: str) -> subprocess.CompletedProcess[str]:
    argv = [subcommand]
    if subcommand in {"run", "test"}:
        argv.append("dummy.co")
    code = (
        "from pcobra.cobra.cli.cli import CliApplication; "
        "app = CliApplication(); "
        "app.initialize(); "
        "app._ensure_command_structure(); "
        f"argv = {argv!r}; "
        "app.parser.parse_args(argv); " + _legacy_assertion_snippet()
    )
    return _run_python_isolated(code)


def test_cobra_repl_no_precarga_transpiladores_legacy():
    result = _run_cli_parse_isolated("repl")
    assert result.returncode == 0, result.stderr


def test_cobra_run_no_precarga_transpiladores_legacy():
    result = _run_cli_parse_isolated("run")
    assert result.returncode == 0, result.stderr


def test_cobra_test_no_precarga_transpiladores_legacy():
    result = _run_cli_parse_isolated("test")
    assert result.returncode == 0, result.stderr


def test_public_backends_permancen_exactamente_tres():
    policy = importlib.import_module("pcobra.cobra.architecture.backend_policy")
    contracts = importlib.import_module("pcobra.cobra.architecture.contracts")
    assert policy.PUBLIC_BACKENDS == ("python", "javascript", "rust")
    assert contracts.PUBLIC_BACKENDS == ("python", "javascript", "rust")
