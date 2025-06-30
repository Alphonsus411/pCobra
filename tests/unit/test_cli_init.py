from io import StringIO
from unittest.mock import patch

from src.cli.cli import main


def test_cli_init_creates_project(tmp_path):
    ruta = tmp_path / "proy"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["init", str(ruta)])
    assert (ruta / "main.co").exists()
    assert "Proyecto Cobra inicializado" in out.getvalue()
