from pathlib import Path
from io import StringIO
from unittest.mock import patch, call

from cli.cli import main


def test_cli_contenedor_invoca_docker():
    with patch("subprocess.run") as mock_run:
        main(["contenedor"])
        raiz = Path(__file__).resolve().parents[3]
        mock_run.assert_called_once_with([
            "docker",
            "build",
            "-t",
            "cobra",
            str(raiz),
        ], check=True)


def test_cli_contenedor_sin_docker():
    with patch("subprocess.run", side_effect=FileNotFoundError), \
            patch("sys.stdout", new_callable=StringIO) as out:
        main(["contenedor"])
    assert "Docker no está instalado" in out.getvalue()
