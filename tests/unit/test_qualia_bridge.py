import importlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest

MODULE_ALIASES = (
    "core.qualia_bridge",
    "pcobra.core.qualia_bridge",
)
DATABASE_ALIASES = (
    "core.database",
    "pcobra.core.database",
)


def _configure_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    db_path = tmp_path / "core.db"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("SQLITE_DB_KEY", str(db_path))
    monkeypatch.setenv("COBRA_DB_PATH", str(db_path))
    monkeypatch.delenv("QUALIA_STATE_PATH", raising=False)
    return home


def _clear_modules() -> None:
    for name in MODULE_ALIASES + DATABASE_ALIASES:
        sys.modules.pop(name, None)


def _reload_qualia(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    home = _configure_env(tmp_path, monkeypatch)
    _clear_modules()
    db_module = importlib.import_module("pcobra.core.database")
    _install_sqlite_stub(db_module, monkeypatch)
    sys.modules.setdefault("core.database", db_module)
    module = importlib.import_module("core.qualia_bridge")
    module = importlib.reload(module)
    _install_parser_stub(module, monkeypatch)
    return module, home


def _install_sqlite_stub(db_module, monkeypatch: pytest.MonkeyPatch) -> None:
    class StubSQLitePlus:
        def __init__(self, db_path: str, cipher_key: str | None = None) -> None:
            self._db_path = db_path

        def get_connection(self):
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            return conn

    monkeypatch.setattr(db_module, "_SQLITEPLUS_CLASS", None, raising=False)
    monkeypatch.setattr(db_module, "_SQLITEPLUS_INSTANCE", None, raising=False)
    monkeypatch.setattr(db_module, "_TABLES_READY", False, raising=False)
    monkeypatch.setattr(db_module, "_load_sqliteplus_class", lambda: StubSQLitePlus)


def _install_parser_stub(module, monkeypatch: pytest.MonkeyPatch) -> None:
    def _make_node(name: str, **attrs):
        cls = type(name, (), {})
        obj = cls()
        for key, value in attrs.items():
            setattr(obj, key, value)
        return obj

    class StubLexer:
        def __init__(self, source: str) -> None:
            self._source = source

        def analizar_token(self):
            return self._source

    class StubParser:
        def __init__(self, tokens: str) -> None:
            self._source = tokens

        def parsear(self):
            nodes = []
            text = self._source
            if "imprimir" in text:
                nodes.append(_make_node("NodoImprimir"))
            if "var " in text:
                try:
                    nombre = text.split("var ", 1)[1].split("=", 1)[0].strip()
                except IndexError:  # pragma: no cover - entradas malformadas
                    nombre = "x"
                nodes.append(_make_node("NodoAsignacion", nombre=nombre))
            if "usar" in text and "pandas" in text:
                nodes.append(_make_node("NodoUsar", modulo="pandas"))
            return nodes

    monkeypatch.setattr(module, "Lexer", StubLexer)
    monkeypatch.setattr(module, "Parser", StubParser)


def test_qualia_state_persistence(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    module.register_execution("var x = 1")

    with module.database.get_connection() as conn:
        row = conn.execute("SELECT payload FROM qualia_state WHERE id = 1").fetchone()
    assert row is not None
    payload = json.loads(row[0])
    assert "var x = 1" in payload["history"]

    module, _ = _reload_qualia(tmp_path, monkeypatch)
    assert "var x = 1" in module.QUALIA.history


def test_qualia_generates_suggestions(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    module.register_execution("var x = 1")
    sugs = module.get_suggestions()
    assert any("imprimir" in s for s in sugs)


def test_knowledge_persistence(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    module.register_execution("imprimir(1)")

    with module.database.get_connection() as conn:
        row = conn.execute("SELECT payload FROM qualia_state WHERE id = 1").fetchone()
    data = json.loads(row[0])
    assert data["knowledge"]["node_counts"].get("NodoImprimir")


def test_sugerir_funciones_por_asignaciones(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    for i in range(5):
        module.register_execution(f"var v{i} = {i}")
    sugs = module.get_suggestions()
    assert any("funciones" in s for s in sugs)
    assert any("nombres descriptivos" in s for s in sugs)


def test_sugerencia_pandas_matplotlib(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    module.register_execution('usar "pandas"')
    sugs = module.get_suggestions()
    assert any("matplotlib" in s for s in sugs)


def test_qualia_rejects_outside_home(tmp_path, monkeypatch):
    home = _configure_env(tmp_path, monkeypatch)
    monkeypatch.setenv("QUALIA_STATE_PATH", "/etc/passwd")
    _clear_modules()
    with pytest.raises(ValueError):
        importlib.import_module("core.qualia_bridge")
    monkeypatch.delenv("QUALIA_STATE_PATH", raising=False)
    assert not (home / "qualia_state.json").exists()


def test_qualia_rejects_traversal(tmp_path, monkeypatch):
    _configure_env(tmp_path, monkeypatch)
    evil = tmp_path / ".." / "mal.json"
    monkeypatch.setenv("QUALIA_STATE_PATH", str(evil))
    _clear_modules()
    with pytest.raises(ValueError):
        importlib.import_module("core.qualia_bridge")


def test_qualia_rejects_symlink(tmp_path, monkeypatch):
    home = _configure_env(tmp_path, monkeypatch)
    cobra_dir = home / ".cobra"
    cobra_dir.mkdir(exist_ok=True)

    target = home / "outside.json"
    target.write_text("{}")

    link = cobra_dir / "state.json"
    link.symlink_to(target)

    monkeypatch.setenv("QUALIA_STATE_PATH", str(link))
    _clear_modules()
    with pytest.raises(ValueError):
        importlib.import_module("core.qualia_bridge")


def test_migrates_legacy_state(tmp_path, monkeypatch, caplog):
    home = _configure_env(tmp_path, monkeypatch)
    legacy_file = home / ".cobra" / "qualia_state.json"
    legacy_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_payload = {
        "history": ["print('hola')"],
        "knowledge": {"node_counts": {"NodoImprimir": 1}},
    }
    legacy_file.write_text(json.dumps(legacy_payload, ensure_ascii=False), encoding="utf-8")

    caplog.set_level("INFO")
    module, _ = _reload_qualia(tmp_path, monkeypatch)

    assert not legacy_file.exists()
    assert "Migrado el estado de qualia" in caplog.text

    with module.database.get_connection() as conn:
        row = conn.execute("SELECT payload FROM qualia_state WHERE id = 1").fetchone()
    assert row is not None
    data = json.loads(row[0])
    assert data["history"] == legacy_payload["history"]

    module = importlib.reload(module)
    assert module.QUALIA.history == legacy_payload["history"]


def test_load_state_recovers_existing_data(tmp_path, monkeypatch):
    module, _ = _reload_qualia(tmp_path, monkeypatch)
    payload = {
        "history": ["persisted()"],
        "knowledge": {
            "node_counts": {"NodoAsignacion": 3},
            "patterns": ["lambda"],
            "variable_names": {"abc": 2},
            "modules_used": {"pandas": 1},
        },
    }
    with module.database.get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO qualia_state(id, payload) VALUES (1, ?)",
            (json.dumps(payload, ensure_ascii=False),),
        )
        conn.commit()

    module, _ = _reload_qualia(tmp_path, monkeypatch)
    assert module.QUALIA.history == ["persisted()"]
    assert module.QUALIA.knowledge.node_counts["NodoAsignacion"] == 3
    assert "lambda" in module.QUALIA.knowledge.patterns
