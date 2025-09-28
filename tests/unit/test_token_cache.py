import importlib
import sqlite3
import sys

from pcobra.cobra.core import Lexer, Parser


def _reload_ast_cache(monkeypatch):
    monkeypatch.delenv("COBRA_AST_CACHE", raising=False)
    sys.modules.pop("core.ast_cache", None)
    module = importlib.import_module("core.ast_cache")
    module = importlib.reload(module)
    module.limpiar_cache()
    return module


def _fetch_fragment_rows(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT fragment_name, content FROM ast_fragments ORDER BY fragment_name"
        ).fetchall()


def test_obtener_tokens_reutiliza(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    llamadas = {"count": 0}

    def fake_tokenizar(self):
        llamadas["count"] += 1
        return ["token"]

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)

    codigo = "var z = 3"
    ast_cache.obtener_tokens(codigo)
    ast_cache.obtener_tokens(codigo)

    assert llamadas["count"] == 1
    rows = _fetch_fragment_rows(base_datos_temporal)
    assert len(rows) == 1
    nombre, contenido = rows[0]
    assert nombre == "full_tokens"
    assert "token" in contenido


def test_tokens_persistidos(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    monkeypatch.setattr(Lexer, "tokenizar", lambda self: ["uno", "dos"])

    codigo = "var persistido = 1"
    tokens = ast_cache.obtener_tokens(codigo)

    with sqlite3.connect(base_datos_temporal) as conn:
        stored = conn.execute(
            "SELECT content FROM ast_fragments WHERE fragment_name = ?",
            ("full_tokens",),
        ).fetchone()

    assert stored is not None
    assert "uno" in stored[0]
    assert tokens == ast_cache.obtener_tokens(codigo)


def test_fragmentos_limpiar(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    monkeypatch.setattr(Lexer, "tokenizar", lambda self: ["a"])
    monkeypatch.setattr(Parser, "parsear", lambda self: ["ast"])

    ast_cache.obtener_ast("var limpia = 2")
    assert _fetch_fragment_rows(base_datos_temporal)

    ast_cache.limpiar_cache()
    assert _fetch_fragment_rows(base_datos_temporal) == []
