import importlib
import json
import os
import pytest
from core import qualia_bridge


def test_qualia_state_persistence(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    assert state.exists()
    qb2 = importlib.reload(qualia_bridge)
    assert "var x = 1" in qb2.QUALIA.history


def test_qualia_generates_suggestions(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    sugs = qb.get_suggestions()
    assert any("imprimir" in s for s in sugs)


def test_knowledge_persistence(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("imprimir(1)")
    data = json.loads(state.read_text())
    assert "knowledge" in data
    assert data["knowledge"]["node_counts"].get("NodoImprimir")


def test_sugerir_funciones_por_asignaciones(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    for i in range(5):
        qb.register_execution(f"var v{i} = {i}")
    sugs = qb.get_suggestions()
    assert any("funciones" in s for s in sugs)
    assert any("nombres descriptivos" in s for s in sugs)


def test_sugerencia_pandas_matplotlib(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution('usar "pandas"')
    sugs = qb.get_suggestions()
    assert any("matplotlib" in s for s in sugs)


def test_qualia_rejects_outside_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", "/etc/passwd")
    with pytest.raises(ValueError):
        importlib.reload(qualia_bridge)


def test_qualia_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    evil = tmp_path / ".." / "mal.json"
    monkeypatch.setenv("QUALIA_STATE_PATH", str(evil))
    with pytest.raises(ValueError):
        importlib.reload(qualia_bridge)


def test_qualia_rejects_symlink(tmp_path, monkeypatch):
    """El path no debe ser un enlace simbólico que apunte fuera de ~/.cobra."""
    home = tmp_path
    cobra_dir = home / ".cobra"
    cobra_dir.mkdir()

    target = home / "outside.json"
    target.write_text("{}")

    link = cobra_dir / "state.json"
    link.symlink_to(target)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(link))

    with pytest.raises(ValueError):
        importlib.reload(qualia_bridge)


def test_state_file_permissions(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    if os.name == "posix":
        assert state.exists()
        mode = state.stat().st_mode & 0o777
        assert mode == 0o600


def test_state_dir_permissions(tmp_path, monkeypatch):
    state = tmp_path / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    dir_path = state.parent
    # Elimina el directorio para probar la creación con permisos
    for child in dir_path.glob("*"):
        if child.is_file() or child.is_symlink():
            child.unlink()
    dir_path.rmdir()
    qb.save_state(qb.QUALIA)
    if os.name == "posix":
        mode = dir_path.stat().st_mode & 0o777
        assert mode == 0o700


def test_symlink_created_after_resolve(tmp_path, monkeypatch):
    home = tmp_path
    state = home / ".cobra" / "state.json"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)

    state.parent.mkdir(parents=True, exist_ok=True)
    target = home / "outside.json"
    target.write_text("{}")
    state.symlink_to(target)

    with pytest.raises(OSError):
        qb.save_state(qb.QUALIA)

