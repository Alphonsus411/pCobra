import sys
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
import pcobra
from io import StringIO
from unittest.mock import patch

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_execute_en_contenedor(tmp_path, monkeypatch):
    script = tmp_path / "prog.co"
    script.write_text("imprimir('hola')")

    import cobra.transpilers.module_map as module_map
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)

    monkeypatch.setattr(
        "pcobra.cobra.cli.services.run_service.sandbox_module.validar_dependencias",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "pcobra.cobra.cli.services.run_service.RUNTIME_MANAGER.validate_command_runtime",
        lambda *args, **kwargs: (None, SimpleNamespace(language="python"), None),
    )

    args = SimpleNamespace(
        archivo=str(script),
        debug=False,
        sandbox=False,
        contenedor="python",
        formatear=False,
        modo="mixto",
        seguro=True,
        verbose=0,
        depurar=False,
        extra_validators=None,
        allow_insecure_fallback=False,
    )
    with patch("pcobra.cobra.cli.services.run_service.ejecutar_en_contenedor_docker", return_value="hola") as mock_run, \
         patch("sys.stdout", new_callable=StringIO) as out:
        ret = ExecuteCommand().run(args)

    assert ret == 0
    mock_run.assert_called_once_with("imprimir('hola')", "python", timeout=30)
    assert "hola" in out.getvalue()
