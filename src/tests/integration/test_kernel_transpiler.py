import subprocess
import sys
import sys
import types

import core.sandbox as sandbox


def fake_sandbox(code, timeout=5, memoria_mb=None):
    return "hola\n"


def test_kernel_transpiler_mode(monkeypatch):
    monkeypatch.setenv("COBRA_JUPYTER_PYTHON", "1")
    outputs = []

    core_mod = types.ModuleType("cobra.core")
    class DummyLexer:
        def __init__(self, code):
            pass
        def tokenizar(self):
            return []
    class DummyParser:
        def __init__(self, tokens):
            pass
        def parsear(self):
            return []
    core_mod.Lexer = DummyLexer
    core_mod.Parser = DummyParser
    core_mod.utils = types.SimpleNamespace(PALABRAS_RESERVADAS=[])
    cobra_pkg = types.ModuleType("cobra")
    cobra_pkg.core = core_mod
    sys.modules["cobra"] = cobra_pkg
    sys.modules["cobra.core"] = core_mod
    sys.modules["cobra.core.utils"] = core_mod.utils

    interp_mod = types.ModuleType("core.interpreter")
    class FakeInterpreter:
        def __init__(self):
            self.variables = {}
        def ejecutar_ast(self, ast):
            return None
    interp_mod.InterpretadorCobra = FakeInterpreter
    qualia_mod = types.ModuleType("core.qualia_bridge")
    qualia_mod.get_suggestions = lambda: []
    core_pkg = types.ModuleType("core")
    core_pkg.interpreter = interp_mod
    core_pkg.qualia_bridge = qualia_mod
    sys.modules["core"] = core_pkg
    sys.modules["core.interpreter"] = interp_mod
    sys.modules["core.qualia_bridge"] = qualia_mod

    from jupyter_kernel import CobraKernel

    class DummyKernel(CobraKernel):
        def __init__(self):
            super().__init__()
            self.iopub_socket = None
            self.session = None

        def send_response(self, stream, msg_or_type, content, **kwargs):
            outputs.append((msg_or_type, content))

    monkeypatch.setattr(sandbox, "ejecutar_en_sandbox", fake_sandbox)
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
    assert ("stream", {"name": "stdout", "text": "hola\n"}) in outputs
    assert any(
        msg_type == "stream"
        and content.get("name") == "stderr"
        and "Advertencia" in content.get("text", "")
        for msg_type, content in outputs
    )
