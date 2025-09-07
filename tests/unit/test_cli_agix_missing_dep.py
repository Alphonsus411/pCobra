from io import StringIO
from unittest.mock import patch
import sys

import pytest
from cobra.cli.commands.agix_cmd import AgixCommand


def test_cli_agix_sin_agix(tmp_path):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    from cobra.cli.cli import main
    with patch("ia.analizador_agix.Reasoner", None):
        with patch("cobra.cli.cli.setup_gettext", return_value=lambda s: s):
            with patch(
                "cobra.cli.cli.AppConfig.BASE_COMMAND_CLASSES", new=[AgixCommand]
            ):
                with patch("sys.stdout", new_callable=StringIO) as out:
                    try:
                        main(["agix", str(archivo)])
                    except SystemExit:
                        pass
                assert "Instala el paquete agix" in out.getvalue()
