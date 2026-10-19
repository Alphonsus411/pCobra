from io import StringIO
from unittest.mock import patch

from cobra.cli.cli import main
from cobra.transpilers import module_map


def test_cli_sandbox_docker_invoca_docker(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    with (
        patch("builtins.input", side_effect=["print(2+2)", "salir()"]),
        patch(
            "pcobra.cobra.cli.commands.interactive_cmd.ejecutar_en_contenedor",
            return_value="4\n",
        ) as mock_ejecutar_en_contenedor,
    ):
        main(["repl", "--sandbox-docker", "python"])
        mock_ejecutar_en_contenedor.assert_called_once_with(
            "print(2+2)", "python"
        )


def test_cli_sandbox_docker_sin_docker(monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    with (
        patch("builtins.input", side_effect=["print(1)", "salir()"]),
        patch(
            "pcobra.cobra.cli.commands.interactive_cmd.ejecutar_en_contenedor",
            side_effect=RuntimeError(
                "Docker no está disponible: no se encontró el ejecutable en PATH"
            ),
        ),
        patch("sys.stdout", new_callable=StringIO) as out,
    ):
        main(["repl", "--sandbox-docker", "python"])
    assert (
        out.getvalue()
        == "Error: Docker no está disponible: no se encontró el ejecutable en PATH\n"
    )
