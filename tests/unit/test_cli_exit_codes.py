import sys
from io import StringIO
from unittest.mock import patch
import pytest

from cli.cli import main
from cli.commands import modules_cmd


def _run_sys_exit(args):
    with patch("sys.stdout", new_callable=StringIO):
        with pytest.raises(SystemExit) as exc:
            sys.exit(main(args))
    return exc.value.code


@pytest.mark.timeout(5)
def test_exit_code_compile_missing(tmp_path):
    archivo = tmp_path / "no.co"
    code = _run_sys_exit(["compilar", str(archivo)])
    assert code != 0


@pytest.mark.timeout(5)
def test_exit_code_execute_missing(tmp_path):
    archivo = tmp_path / "no.co"
    code = _run_sys_exit(["ejecutar", str(archivo)])
    assert code != 0


@pytest.mark.timeout(5)
def test_exit_code_module_remove_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(tmp_path))
    code = _run_sys_exit(["modulos", "remover", "algo.co"])
    assert code != 0
