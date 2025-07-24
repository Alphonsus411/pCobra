import importlib
import json
import os
from core import qualia_bridge


def test_qualia_state_persistence(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    assert state.exists()
    qb2 = importlib.reload(qualia_bridge)
    assert "var x = 1" in qb2.QUALIA.history


def test_qualia_generates_suggestions(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("var x = 1")
    sugs = qb.get_suggestions()
    assert any("imprimir" in s for s in sugs)


def test_knowledge_persistence(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    monkeypatch.setenv("QUALIA_STATE_PATH", str(state))
    qb = importlib.reload(qualia_bridge)
    qb.register_execution("imprimir(1)")
    data = json.loads(state.read_text())
    assert "knowledge" in data
    assert data["knowledge"]["node_counts"].get("NodoImprimir")

