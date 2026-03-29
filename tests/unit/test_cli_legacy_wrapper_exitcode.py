from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_WRAPPER_PATH = REPO_ROOT / "cobra" / "cli" / "cli.py"


def _base_env() -> dict[str, str]:
    env = os.environ.copy()
    original_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT), str(REPO_ROOT / "src"), original_pythonpath])
    )
    return env


def _run_module(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        text=True,
        env=_base_env(),
        check=False,
        timeout=20,
    )


def _run_legacy_wrapper_file(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LEGACY_WRAPPER_PATH), *args],
        capture_output=True,
        text=True,
        env=_base_env(),
        check=False,
        timeout=20,
    )


@pytest.mark.timeout(20)
def test_wrapper_legacy_y_entrypoints_canonicos_comparten_exitcode_en_error_controlado() -> None:
    args = ("compilar", "archivo_que_no_existe.co")

    canonical = _run_module("pcobra.cli", *args)
    legacy_wrapper = _run_legacy_wrapper_file(*args)
    legacy_src_wrapper = _run_module("cli.cli", *args)

    assert canonical.returncode != 0
    assert legacy_wrapper.returncode == canonical.returncode
    assert legacy_src_wrapper.returncode == canonical.returncode


def test_main_del_wrapper_legacy_devuelve_int() -> None:
    spec = importlib.util.spec_from_file_location("legacy_cli_wrapper", LEGACY_WRAPPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    resultado = module.main(["compilar", "archivo_que_no_existe.co"])
    assert isinstance(resultado, int)
