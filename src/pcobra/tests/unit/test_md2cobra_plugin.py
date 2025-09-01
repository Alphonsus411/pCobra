import importlib.metadata
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import sys

from cobra.cli.cli import main

# Añadimos la carpeta de plugins de ejemplo al path para importar el plugin
ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DIR = ROOT / "examples" / "plugins"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PLUGIN_DIR))


def test_md2cobra_plugin_generates_file(tmp_path):
    md = tmp_path / "ejemplo.md"
    md.write_text(
        """
Texto normal
```cobra
var x = 1
```
Mas texto
````cobra
var y = 2
````
""",
        encoding="utf-8",
    )
    salida = tmp_path / "salida.co"
    ep = importlib.metadata.EntryPoint(
        name="md2cobra",
        value="md2cobra_plugin:MarkdownToCobraCommand",
        group="cobra.plugins",
    )
    with patch("cli.plugin.entry_points", return_value=importlib.metadata.EntryPoints((ep,))):
        main(["md2cobra", "--input", str(md), "--output", str(salida)])

    assert salida.exists()
    contenido = salida.read_text(encoding="utf-8").strip()
    assert "var x = 1" in contenido
    assert "var y = 2" in contenido
