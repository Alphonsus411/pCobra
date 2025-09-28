import importlib
from io import StringIO
from unittest.mock import patch


def test_reiniciar_limpiar_estado(base_datos_temporal, tmp_path, monkeypatch):
    _ = base_datos_temporal
    home = tmp_path / "home"
    home.mkdir()
    legacy_path = home / ".cobra" / "qualia_state.json"
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(legacy_path))

    from core import qualia_bridge as qb

    qb = importlib.reload(qb)

    spirit = qb.QualiaSpirit()
    spirit.history.append("imprimir(1)")
    qb.save_state(spirit)

    with qb.database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM qualia_state")
        assert cursor.fetchone()[0] == 1

    from cobra.cli.cli import main

    with patch("sys.stdout", new_callable=StringIO) as out, patch(
        "cobra.cli.cli.setup_gettext", return_value=lambda s: s
    ):
        exit_code = main(["qualia", "reiniciar"])

    assert exit_code == 0

    with qb.database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM qualia_state")
        assert cursor.fetchone()[0] == 0

    salida = out.getvalue()
    assert "Qualia" in salida
