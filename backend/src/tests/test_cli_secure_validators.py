import sys
from io import StringIO
from unittest.mock import patch
import pytest

from src.cli.cli import main


def _run_sys_exit(args):
    with patch("sys.stdout", new_callable=StringIO):
        with pytest.raises(SystemExit) as exc:
            sys.exit(main(args))
    return exc.value.code


@pytest.mark.timeout(5)
def test_cli_seguro_archivos_prohibidos(tmp_path):
    archivo = tmp_path / "a.co"
    archivo.write_text("cargar_extension('x.so')")
    code = _run_sys_exit(["--seguro", "ejecutar", str(archivo)])
    assert code != 0


@pytest.mark.timeout(5)
def test_cli_seguro_reflexion_prohibida(tmp_path):
    archivo = tmp_path / "b.co"
    archivo.write_text("eval('1')")
    code = _run_sys_exit(["--seguro", "ejecutar", str(archivo)])
    assert code != 0
