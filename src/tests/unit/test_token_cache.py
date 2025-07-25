import importlib
import sys
import hashlib
import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


def test_obtener_tokens_reutiliza(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))

    if 'src.core.ast_cache' in sys.modules:
        importlib.reload(sys.modules['src.core.ast_cache'])
    from core.ast_cache import obtener_tokens

    llamadas = {"count": 0}

    def fake_tokenizar(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)

    codigo = "var z = 3"
    obtener_tokens(codigo)
    obtener_tokens(codigo)

    assert llamadas["count"] == 1
    archivos = list(cache_dir.glob("*.tok"))
    assert len(archivos) == 1


def test_obtener_ast_reutiliza_tokens(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))

    if 'src.core.ast_cache' in sys.modules:
        importlib.reload(sys.modules['src.core.ast_cache'])
    from core.ast_cache import obtener_ast

    token_calls = {"count": 0}
    parse_calls = {"count": 0}

    def fake_tokenizar(self):
        token_calls["count"] += 1
        return []

    def fake_parsear(self):
        parse_calls["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)
    monkeypatch.setattr(Parser, "parsear", fake_parsear)

    codigo = "var a = 5"
    obtener_ast(codigo)

    # eliminar archivo AST para forzar nueva construcción manteniendo tokens
    checksum = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    ast_path = cache_dir / f"{checksum}.ast"
    if ast_path.exists():
        ast_path.unlink()

    obtener_ast(codigo)

    assert token_calls["count"] == 1
    assert parse_calls["count"] == 2
    assert (cache_dir / f"{checksum}.tok").exists()


def test_cache_fragmentos(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))

    from core.ast_cache import obtener_tokens_fragmento

    llamadas = {"count": 0}

    def fake_tokenizar(self, *a, **k):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "_tokenizar_base", fake_tokenizar)

    codigo = "imprimir(1)\n"
    obtener_tokens_fragmento(codigo)
    obtener_tokens_fragmento(codigo)
    assert llamadas["count"] == 1
