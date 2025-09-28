import importlib
import sys

import pytest


@pytest.fixture
def database_module(tmp_path, monkeypatch):
    db_path = tmp_path / "core.db"
    monkeypatch.setenv("SQLITE_DB_KEY", str(db_path))
    monkeypatch.setenv("COBRA_DB_PATH", str(db_path))
    sys.modules.pop("pcobra.core.database", None)
    module = importlib.import_module("pcobra.core.database")
    return importlib.reload(module)


def test_tables_created_on_first_connection(database_module):
    with database_module.get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        names = {row[0] for row in cursor.fetchall()}
    assert {"ast_cache", "ast_fragments", "qualia_state"}.issubset(names)


def test_store_and_load_ast_roundtrip(database_module):
    database_module.clear_cache()
    database_module.store_ast(
        "hash-1",
        "print('hola')",
        {"nodos": 5, "valid": True},
        fragments=[("principal", "fragmento")],
    )
    data = database_module.load_ast("hash-1")
    assert data is not None
    assert data["source"] == "print('hola')"
    assert data["ast"]["nodos"] == 5
    assert data["fragments"] == {"principal": "fragmento"}


def test_save_qualia_state_smoke(database_module):
    database_module.save_qualia_state({"estado": "ok"})
    with database_module.get_connection() as conn:
        cursor = conn.execute("SELECT payload FROM qualia_state WHERE id=1")
        row = cursor.fetchone()
    assert row is not None
    assert "ok" in row[0]
