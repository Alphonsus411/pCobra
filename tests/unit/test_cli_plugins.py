import importlib.metadata
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import sys

from cli.cli import main
from cli.plugin_registry import limpiar_registro

# Añadimos la carpeta de plugins de ejemplo al path para poder importar el plugin
ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = ROOT / "examples" / "plugins"
sys.path.insert(0, str(ROOT / "backend" / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PLUGIN_DIR))


def test_cli_saludo_plugin():
    ep = importlib.metadata.EntryPoint(
        name="saludo",
        value="saludo_plugin:SaludoCommand",
        group="cobra.plugins",
    )
    limpiar_registro()
    with patch("cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        with patch("sys.stdout", new_callable=StringIO) as out:
            main(["saludo"])
    assert "¡Hola desde el plugin de ejemplo!" in out.getvalue()
