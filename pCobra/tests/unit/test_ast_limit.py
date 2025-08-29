import pytest
from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoImprimir, NodoValor
from core.cobra_config import cargar_configuracion


def test_limite_nodos(monkeypatch, tmp_path):
    cfg = tmp_path / "cfg.toml"
    cfg.write_text("[seguridad]\nlimite_nodos = 1\n")
    monkeypatch.setenv("COBRA_CONFIG", str(cfg))
    cargar_configuracion.cache_clear()
    interp = InterpretadorCobra()
    ast = [NodoImprimir(NodoValor(1)), NodoImprimir(NodoValor(2))]
    with pytest.raises(RuntimeError):
        interp.ejecutar_ast(ast)
