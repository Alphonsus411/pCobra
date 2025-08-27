import os
import sys
from pathlib import Path

import pexpect
import pytest

ROOT = Path(__file__).resolve().parents[2]
PATCH_DIR = Path(__file__).parent


def _spawn(args="interactive", extra_env=None):
    env = os.environ.copy()
    pythonpath = [str(ROOT), str(ROOT / "backend" / "src"), str(PATCH_DIR)]
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


@pytest.mark.integration
def test_interactive_persistence():
    child = _spawn()
    child.expect("cobra> ")
    child.sendline("x = 42")
    child.expect("cobra> ")
    child.sendline("imprimir(x)")
    child.expect("42")
    child.expect("cobra> ")
    child.sendline("salir")
    child.expect(pexpect.EOF)
    child.wait()
    assert child.exitstatus == 0
