import pytest

from core.interpreter import InterpretadorCobra
from core.ast_nodes import (
    NodoAsignacion,
    NodoBloque,
    NodoCondicional,
    NodoIdentificador,
    NodoOperacionBinaria,
    NodoValor,
)
from cobra.core import TipoToken, Token


def test_referencia_circular_variable():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoIdentificador("a")
    with pytest.raises(RuntimeError, match="Ciclo de variables detectado"):
        inter.evaluar_expresion(NodoIdentificador("a"))


def test_resolucion_encadenada_sin_ciclo():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(10)
    assert inter.evaluar_expresion(NodoIdentificador("a")) == 10
    assert inter.variables["a"] == 10
    assert inter.variables["b"] == 10


def test_name_error_variable_ausente_se_distingue_de_ciclo():
    inter = InterpretadorCobra()
    with pytest.raises(NameError, match=r"^Variable no declarada: z$"):
        inter.evaluar_expresion(NodoIdentificador("z"))


def test_variable_apuntando_a_asignacion_autorreferente():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoAsignacion("tmp", NodoIdentificador("a"))
    with pytest.raises(RuntimeError, match=r"^Ciclo de variables detectado en 'a'$"):
        inter.evaluar_expresion(NodoIdentificador("a"))


def test_ejecutar_asignacion_rechaza_autorreferencia_directa():
    inter = InterpretadorCobra()
    with pytest.raises(RuntimeError, match=r"^Ciclo de variables detectado en 'a'$"):
        inter.ejecutar_asignacion(NodoAsignacion("a", NodoIdentificador("a")))


def test_ejecutar_asignacion_rechaza_autorreferencia_indirecta():
    inter = InterpretadorCobra()
    inter.variables["b"] = NodoIdentificador("a")
    with pytest.raises(RuntimeError, match=r"^Ciclo de variables detectado en 'a'$"):
        inter.ejecutar_asignacion(NodoAsignacion("a", NodoIdentificador("b")))


def test_ciclo_alias_no_escala_a_recursion_error():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoIdentificador("a")

    try:
        inter.evaluar_expresion(NodoIdentificador("a"))
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")
    except RuntimeError as exc:
        assert str(exc) == "Ciclo de variables detectado en 'a'"


def test_condicional_rechaza_nodo_ast_sin_materializar_en_condicion():
    inter = InterpretadorCobra()
    condicional = NodoCondicional(
        condicion=NodoValor(NodoIdentificador("x")),
        bloque_si=NodoBloque([]),
        bloque_sino=NodoBloque([]),
    )

    with pytest.raises(
        RuntimeError,
        match=r"^Condición no materializada: se recibió nodo AST NodoIdentificador$",
    ):
        inter.ejecutar_condicional(condicional)


def test_evaluar_identificador_delega_unicamente_en_resolver(monkeypatch):
    inter = InterpretadorCobra()
    llamadas = []

    def _resolver_controlado(nombre, visitados=None):
        llamadas.append((nombre, visitados))
        return 123

    monkeypatch.setattr(inter, "_resolver_identificador", _resolver_controlado)

    resultado = inter.evaluar_expresion(NodoIdentificador("alias"))

    assert resultado == 123
    assert len(llamadas) == 1
    assert llamadas[0][0] == "alias"


def test_resolver_identificador_lanza_error_si_materializacion_devuelve_ast(monkeypatch):
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")

    monkeypatch.setattr(
        inter,
        "_materializar_valor",
        lambda valor, visitados, origen="general", **kwargs: NodoIdentificador("x"),
    )

    with pytest.raises(
        RuntimeError,
        match=r"^Resolución inválida de variable: 'a' quedó en nodo AST \(NodoIdentificador\)$",
    ):
        inter._resolver_identificador("a")


def test_materializacion_completa_en_cadena_identificador_y_valor():
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(NodoIdentificador("c"))
    inter.variables["c"] = NodoValor(42)

    resultado = inter.evaluar_expresion(NodoIdentificador("a"))

    assert resultado == 42
    assert inter.variables["a"] == 42
    assert inter.variables["b"] == 42
    assert inter.variables["c"] == 42


def test_binaria_materializa_operandos_encadenados_completamente():
    inter = InterpretadorCobra()
    inter.variables["izq"] = NodoValor(NodoIdentificador("a"))
    inter.variables["a"] = NodoValor(8)
    inter.variables["der"] = NodoValor(NodoIdentificador("b"))
    inter.variables["b"] = NodoValor(5)

    expresion = NodoOperacionBinaria(
        NodoIdentificador("izq"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("der"),
    )

    assert inter.evaluar_expresion(expresion) == 13
