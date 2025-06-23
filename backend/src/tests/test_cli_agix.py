from io import StringIO
from unittest.mock import patch

from src.cli.cli import main


def test_cli_agix_generates_suggestion(tmp_path):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["agix", str(archivo)])
    salida = out.getvalue().strip()
    assert "Modelo seleccionado" in salida
