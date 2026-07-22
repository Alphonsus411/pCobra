import os
import shutil
import sys
from pathlib import Path

import pytest

pexpect = pytest.importorskip("pexpect")

ROOT = Path(__file__).resolve().parents[2]
PATCH_DIR = Path(__file__).parent


def _spawn(args, extra_env=None):
    env = os.environ.copy()
    pythonpath = [str(ROOT), str(ROOT / "src"), str(PATCH_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env["COBRA_TOML"] = str(PATCH_DIR / "empty.toml")
    env.pop("PYTEST_CURRENT_TEST", None)
    if extra_env:
        env.update(extra_env)
    return pexpect.spawn(
        f"{sys.executable} -m cli.cli {args}", env=env, encoding="utf-8"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="pexpect no es compatible con Windows")
def test_ejecutar_modo_normal():
    child = _spawn("ejecutar tests/data/ejemplo.cobra")
    child.expect("hola")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


def test_jupyter_command(monkeypatch):
    import argparse
    import subprocess
    import types

    from pcobra.cobra.cli.commands.jupyter_cmd import JupyterCommand

    monkeypatch.setitem(sys.modules, "jupyter", types.ModuleType("jupyter"))

    llamadas = []

    def run_exitoso(args, **kwargs):
        llamadas.append((args, kwargs))
        return subprocess.CompletedProcess(args, returncode=0)

    python_resuelto = "/ruta/determinista/python"
    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.jupyter_cmd.subprocess.run", run_exitoso
    )
    monkeypatch.setattr(
        JupyterCommand,
        "_resolver_ejecutable",
        staticmethod(lambda _ejecutable: python_resuelto),
    )

    comando = JupyterCommand()
    argumentos = argparse.Namespace(notebook=None)

    assert comando.run(argumentos) == 0
    assert llamadas == [
        (
            [sys.executable, "-m", "pcobra.jupyter_kernel", "install"],
            {"check": True, "capture_output": True, "text": True},
        ),
        (
            [
                python_resuelto,
                "-m",
                "jupyter",
                "notebook",
                "--KernelManager.default_kernel_name=cobra",
            ],
            {"check": True},
        ),
    ]

    def run_con_error(args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args)

    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.jupyter_cmd.subprocess.run", run_con_error
    )

    assert comando.run(argumentos) == 1


@pytest.mark.skipif(sys.platform == "win32", reason="pexpect no es compatible con Windows")
def test_docs_command():
    if not shutil.which("sphinx-build") or not shutil.which("sphinx-apidoc"):
        pytest.skip("Sphinx no disponible")
    child = _spawn("docs", {"PEXPECT_TESTING": "1"})
    child.expect("Documentaci")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


@pytest.mark.skipif(sys.platform == "win32", reason="pexpect no es compatible con Windows")
def test_ejecutar_sandbox():
    child = _spawn("ejecutar tests/data/ejemplo.cobra --sandbox", {"PEXPECT_TESTING": "1"})
    child.expect("hola")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0
