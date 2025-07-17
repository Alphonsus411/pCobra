import subprocess
from io import StringIO
import sys
import types

from jupyter_kernel import CobraKernel


def fake_run(cmd, input=None, capture_output=True, text=True):
    return subprocess.CompletedProcess(cmd, 0, stdout="hola\n", stderr="")


def test_kernel_transpiler_mode(monkeypatch):
    monkeypatch.setenv("COBRA_JUPYTER_PYTHON", "1")
    outputs = []

    class DummyKernel(CobraKernel):
        def __init__(self):
            super().__init__()
            self.iopub_socket = None
            self.session = None

        def send_response(self, stream, msg_or_type, content, **kwargs):
            outputs.append((msg_or_type, content))

    monkeypatch.setattr(subprocess, "run", fake_run)
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
