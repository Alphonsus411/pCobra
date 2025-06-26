import os
import pytest
from src.cobra.parser.parser import Parser


def test_obtener_ast_reutiliza(monkeypatch, tmp_path):
    # Redirigir el directorio de cache a una carpeta temporal
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))

    import importlib, sys
    if 'src.core.ast_cache' in sys.modules:
        importlib.reload(sys.modules['src.core.ast_cache'])
    from src.core.ast_cache import obtener_ast

    llamadas = {"count": 0}

    def fake_parsear(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Parser, "parsear", fake_parsear)

    codigo = "var x = 1"
    obtener_ast(codigo)
    obtener_ast(codigo)

    assert llamadas["count"] == 1
    # Se creó un único archivo en la caché
    archivos = list(cache_dir.glob("*.ast"))
    assert len(archivos) == 1


@pytest.mark.timeout(5)
def test_limpiar_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    codigo = "var y = 2"

    import importlib, sys
    if 'src.core.ast_cache' in sys.modules:
        importlib.reload(sys.modules['src.core.ast_cache'])
    from src.core.ast_cache import obtener_ast, limpiar_cache

    obtener_ast(codigo)
    assert list(cache_dir.glob("*.ast"))

    limpiar_cache()
    assert list(cache_dir.glob("*.ast")) == []
