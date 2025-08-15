import subprocess
import sys
import types
import pytest


def timeout_run(cmd, input=None, capture_output=True, text=True, timeout=None):
    raise subprocess.TimeoutExpired(cmd, timeout or 5)

@pytest.mark.timeout(5)
def test_kernel_reports_timeout(monkeypatch):
    monkeypatch.setenv("COBRA_JUPYTER_PYTHON", "1")
    outputs = []

    # Crea un módulo "cli" mínimo requerido por cobra.semantico
    cli_mod = types.ModuleType("cli")
    utils_mod = types.ModuleType("cli.utils")
    semver_mod = types.ModuleType("cli.utils.semver")
    semver_mod.es_version_valida = lambda v: True
    utils_mod.semver = semver_mod
    cli_mod.utils = utils_mod
    sys.modules.setdefault("cli", cli_mod)
    sys.modules.setdefault("cli.utils", utils_mod)
    sys.modules.setdefault("cli.utils.semver", semver_mod)

    ts_mod = types.ModuleType("tree_sitter_languages")
    ts_mod.get_parser = lambda lang: types.SimpleNamespace(
        parse=lambda b: types.SimpleNamespace(root_node=types.SimpleNamespace(children=[], is_named=False))
    )
    sys.modules.setdefault("tree_sitter_languages", ts_mod)

    transp_mod = types.ModuleType("cobra.transpilers.transpiler.to_python")
    class FakeTranspilador:
        def generate_code(self, ast):
            return "while True:\n    pass"
    transp_mod.TranspiladorPython = FakeTranspilador
    sys.modules.setdefault(
        "cobra.transpilers.transpiler.to_python", transp_mod
    )

    from jupyter_kernel import CobraKernel

    class DummyKernel(CobraKernel):
        def __init__(self):
            super().__init__()
            self.iopub_socket = None
            self.session = None

        def send_response(self, stream, msg_or_type, content, **kwargs):
            outputs.append((msg_or_type, content))

    monkeypatch.setattr(subprocess, "run", timeout_run)
    setup_mod = types.ModuleType("pybind11.setup_helpers")
    setup_mod.Pybind11Extension = object
    setup_mod.build_ext = object
    sys.modules["pybind11.setup_helpers"] = setup_mod
    mod = types.ModuleType("pybind11")
    mod.setup_helpers = setup_mod
    sys.modules["pybind11"] = mod
    sys.modules.setdefault("corelibs", types.ModuleType("corelibs"))

    kernel = DummyKernel()
    kernel.do_execute("imprimir('hola')", False)

    assert any(
        msg_type == "stream"
        and content.get("name") == "stderr"
        and "tiempo límite" in content.get("text", "")
        for msg_type, content in outputs
    )
