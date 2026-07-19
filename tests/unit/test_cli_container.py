from pathlib import Path
from io import StringIO
from unittest.mock import patch, call

from pcobra.cobra.cli import cli as cli_module
from pcobra.cobra.cli.commands.container_cmd import ContainerCommand


def test_cli_contenedor_invoca_docker():
    with patch.object(cli_module, "resolve_command_profile", return_value="development"), \
         patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ContainerCommand]), \
         patch("subprocess.run") as mock_run:
        cli_module.main(["contenedor"])
        raiz = Path(__file__).resolve().parents[2]
        assert mock_run.call_args_list == [
            call(["docker", "--version"], check=True, capture_output=True),
            call(
                ["docker", "build", "-t", "cobra", str(raiz)],
                check=True,
                timeout=600,
            ),
        ]


def test_cli_contenedor_sin_docker():
    with patch.object(cli_module, "resolve_command_profile", return_value="development"), \
            patch.object(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [ContainerCommand]), \
            patch("subprocess.run", side_effect=FileNotFoundError), \
            patch("sys.stdout", new_callable=StringIO) as out:
        cli_module.main(["contenedor"])
    assert "Docker no está instalado" in out.getvalue()
