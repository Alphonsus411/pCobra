from io import StringIO
from unittest.mock import patch
import subprocess

from cli.cli import main
from cobra.transpilers import module_map


def test_cli_sandbox_docker_invoca_docker(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    with patch("builtins.input", side_effect=["print(2+2)", "salir()"]), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0, stdout="4\n", stderr="")
        main(["interactive", "--sandbox-docker", "python"])
        mock_run.assert_called_once_with(
            ["docker", "run", "--rm", "-i", "cobra-python-sandbox"],
            input="print(2+2)", text=True, capture_output=True, check=True,
        )


def test_cli_sandbox_docker_sin_docker(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    with patch("builtins.input", side_effect=["print(1)", "salir()"]), \
         patch("subprocess.run", side_effect=FileNotFoundError), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(["interactive", "--sandbox-docker", "python"])
    assert "Docker no está instalado" in out.getvalue()

