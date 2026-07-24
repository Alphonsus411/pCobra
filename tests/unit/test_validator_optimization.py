import importlib
from unittest.mock import patch

from core.semantic_validators import construir_cadena, ValidadorPrimitivaPeligrosa


def test_construir_cadena_reutiliza_instancias():
    contador = 0

    original_init = ValidadorPrimitivaPeligrosa.__init__

    def cuenta_init(self):
        nonlocal contador
        contador += 1
        original_init(self)

    with patch.object(ValidadorPrimitivaPeligrosa, "__init__", cuenta_init):
        construir_cadena()  # Primera vez crea la cadena
        construir_cadena()  # Debe reutilizarla

    assert contador == 1


def test_construir_cadena_sin_reutilizar(monkeypatch):
    contador = 0
    original_init = ValidadorPrimitivaPeligrosa.__init__

    def cuenta_init(self):
        nonlocal contador
        contador += 1
        original_init(self)

    with patch.object(ValidadorPrimitivaPeligrosa, "__init__", cuenta_init):
        import core.semantic_validators as sv
        monkeypatch.setattr(sv, "_CADENA_DEFECTO", None)
        construir_cadena()
        monkeypatch.setattr(sv, "_CADENA_DEFECTO", None)
        construir_cadena()

    assert contador == 2


def test_valida_y_audita_cada_nodo_una_vez_por_fase():
    from core.interpreter import InterpretadorCobra
    from core.ast_nodes import NodoAsignacion, NodoValor

    interp = InterpretadorCobra()
    nodo = NodoAsignacion("x", NodoValor(1), declaracion=True)

    conteos = {
        "analysis": 0,
        "execution": 0,
    }

    class DummyValidator:
        def __init__(self):
            self.emitir_side_effects = False
            self.mode = "analysis"

        def visit(self, _):
            conteos[self.mode] += 1

    interp._validador = DummyValidator()
    interp.ejecutar_ast([nodo])

    assert conteos == {
        "analysis": 1,
        "execution": 1,
    }
