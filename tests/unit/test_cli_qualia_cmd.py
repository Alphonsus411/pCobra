import importlib
import json
from io import StringIO
from unittest.mock import patch


def _capture_json(output: str) -> dict:
    start = output.find("{")
    end = output.rfind("}") + 1
    return json.loads(output[start:end])


def test_cli_qualia_mostrar(tmp_path, monkeypatch, base_datos_temporal):
    _ = base_datos_temporal
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    state.parent.mkdir(parents=True, exist_ok=True)
    from core import qualia_bridge
    qb = importlib.reload(qualia_bridge)
    spirit = qb.QualiaSpirit()
    spirit.history.append("imprimir(1)")
    spirit.knowledge.node_counts["NodoImprimir"] = 1
    qb.save_state(spirit)
    qb.QUALIA = spirit
    from cobra.cli.cli import main
    with patch("sys.stdout", new_callable=StringIO) as out, patch(
        "cobra.cli.cli.setup_gettext", return_value=lambda s: s
    ):
        main(["qualia", "mostrar"])
    data = _capture_json(out.getvalue())
    assert data["node_counts"].get("NodoImprimir")


def test_cli_qualia_reiniciar(tmp_path, monkeypatch, base_datos_temporal):
    _ = base_datos_temporal
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    from core import qualia_bridge
    importlib.reload(qualia_bridge)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text("{}")
    from cobra.cli.cli import main
    with patch("sys.stdout", new_callable=StringIO) as out, patch(
        "cobra.cli.cli.setup_gettext", return_value=lambda s: s
    ):
        main(["qualia", "reiniciar"])
    assert not state.exists()
    assert "Estado de Qualia eliminado" in out.getvalue()
