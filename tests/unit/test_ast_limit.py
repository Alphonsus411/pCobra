import pytest
from src.core.interpreter import InterpretadorCobra
from src.core.ast_nodes import NodoImprimir, NodoValor
from src.core.cobra_config import _cache


def test_limite_nodos(monkeypatch, tmp_path):
    cfg = tmp_path / "cfg.toml"
    cfg.write_text("[seguridad]\nlimite_nodos = 1\n")
    monkeypatch.setenv("COBRA_CONFIG", str(cfg))
    _cache.clear()
    interp = InterpretadorCobra()
    ast = [NodoImprimir(NodoValor(1)), NodoImprimir(NodoValor(2))]
    with pytest.raises(RuntimeError):
        interp.ejecutar_ast(ast)
