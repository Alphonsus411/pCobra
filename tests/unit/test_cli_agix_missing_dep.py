from io import StringIO
from unittest.mock import patch
import sys

import pytest


def test_cli_agix_sin_agix(tmp_path):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    for mod in ["cli.cli", "cli.commands.agix_cmd", "ia.analizador_agix"]:
        sys.modules.pop(mod, None)
    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "agix.reasoning.basic":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=fake_import):
        from cli.cli import main
        with patch("sys.stdout", new_callable=StringIO) as out:
            with pytest.raises(SystemExit):
                main(["agix", str(archivo)])
        assert "Instala el paquete agix" in out.getvalue()
