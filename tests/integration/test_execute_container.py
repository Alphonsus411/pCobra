import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
import pcobra
from cobra.cli.cli import main
from io import StringIO
from unittest.mock import patch


def test_execute_en_contenedor(tmp_path, monkeypatch):
    script = tmp_path / "prog.co"
    script.write_text("imprimir('hola')")

    import cobra.transpilers.module_map as module_map
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)

    with patch("cli.commands.execute_cmd.ejecutar_en_contenedor", return_value="hola") as mock_run, \
         patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["ejecutar", str(script), "--contenedor=python"])

    assert ret == 0
    mock_run.assert_called_once_with("imprimir('hola')", "python")
    assert "hola" in out.getvalue()
