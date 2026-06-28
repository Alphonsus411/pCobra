import os
import shlex
import sys
from pathlib import Path

import pytest
from pcobra._stubs import pexpect

ROOT = Path(__file__).resolve().parents[2]
PATCH_DIR = Path(__file__).parent


def _spawn(args="repl", extra_env=None):
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
        [sys.executable, "-m", "cli.cli", *shlex.split(args)], env=env, encoding="utf-8"
    )


@pytest.mark.integration
@pytest.mark.skipif(sys.platform == "win32", reason="pexpect no es compatible con Windows")
def test_interactive_persistence():
    child = _spawn()
    child.expect(">>> ")
    child.sendline("var x = 42")
    child.expect(">>> ")
    child.sendline("imprimir(x)")
    child.expect("42")
    child.expect(">>> ")
    child.sendline("salir")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0
