from io import StringIO
from unittest.mock import patch
import pytest

from cli.cli import main


@pytest.mark.timeout(5)
def test_error_msg_compile_missing(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo)])
    assert "El archivo" in out.getvalue()


@pytest.mark.timeout(5)
def test_error_msg_execute_missing(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(archivo)])
    assert "El archivo" in out.getvalue()
