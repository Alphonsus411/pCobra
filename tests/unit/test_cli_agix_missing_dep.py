from io import StringIO
from unittest.mock import patch
import sys

import pytest


def test_cli_agix_sin_agix(tmp_path):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    from cli.cli import main
    with patch("ia.analizador_agix.Reasoner", None):
        with patch("sys.stdout", new_callable=StringIO) as out:
            try:
                main(["agix", str(archivo)])
            except SystemExit:
                pass
        assert "Instala el paquete agix" in out.getvalue()
