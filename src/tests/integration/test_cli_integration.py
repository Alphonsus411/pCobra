import os
import sys
import shutil
from pathlib import Path

import pexpect
import pytest

ROOT = Path(__file__).resolve().parents[2]
PATCH_DIR = Path(__file__).parent


def _spawn(args, extra_env=None):
    env = os.environ.copy()
    pythonpath = [str(ROOT), str(ROOT / "backend" / "src"), str(PATCH_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env["PCOBRA_TOML"] = str(PATCH_DIR / "empty.toml")
    env.pop("PYTEST_CURRENT_TEST", None)
    if extra_env:
        env.update(extra_env)
    return pexpect.spawn(
        f"{sys.executable} -m cli.cli {args}", env=env, encoding="utf-8"
    )


def test_ejecutar_modo_normal():
    child = _spawn("ejecutar src/tests/data/ejemplo.co")
    child.expect("hola")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


def test_jupyter_command():
    if not shutil.which("jupyter"):
        pytest.skip("jupyter no disponible")
    child = _spawn("jupyter", {"PEXPECT_TESTING": "1"})
    child.expect("FAKE_RUN")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


def test_docs_command():
    if not shutil.which("sphinx-build") or not shutil.which("sphinx-apidoc"):
        pytest.skip("Sphinx no disponible")
    child = _spawn("docs", {"PEXPECT_TESTING": "1"})
    child.expect("Documentaci")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0


def test_ejecutar_sandbox():
    child = _spawn("ejecutar src/tests/data/ejemplo.co --sandbox", {"PEXPECT_TESTING": "1"})
    child.expect("hola")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0
