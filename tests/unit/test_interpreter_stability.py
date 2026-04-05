from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import Lexer, Parser, TipoToken, Token
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoValor,
)
from core.errors import CondicionNoBooleanaError
from core.interpreter import InterpretadorCobra
from core.semantic_validators.base import ValidadorBase


def _lineas_sin_trazas(salida: str) -> list[str]:
    return [
        linea.strip()
        for linea in salida.splitlines()
        if linea.strip() and not linea.lstrip().startswith("[")
    ]


def _ejecutar_codigo(codigo: str) -> InterpretadorCobra:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()
    for nodo in ast:
        inter.ejecutar_nodo(nodo)
    return inter


def test_condicional_valido_con_variable_definida() -> None:
    inter = _ejecutar_codigo(
        """
var x = 1
si x == 1:
    var z = 99
fin
"""
    )
    assert inter.variables["z"] == 99


def test_condicional_con_variable_no_definida_lanza_nameerror() -> None:
    with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
        _ejecutar_codigo(
            """
si y == 1:
    pasar
fin
"""
        )


def test_condicional_con_tipo_no_booleano_lanza_error_semantico() -> None:
    with pytest.raises(
        CondicionNoBooleanaError, match=r"^La condición debe ser booleana$"
    ):
        _ejecutar_codigo(
            """
si 1:
    pasar
fin
"""
        )


def test_si_verdadero_ejecuta_bloque_y_emite_salida() -> None:
    inter = InterpretadorCobra()
    ast = [NodoCondicional(NodoValor(True), [NodoImprimir(NodoValor("ok"))], [])]

    with patch("sys.stdout", new_callable=StringIO) as out:
        for nodo in ast:
            inter.ejecutar_nodo(nodo)

    lineas = _lineas_sin_trazas(out.getvalue())
    assert lineas == ["ok"]


def test_si_falso_no_ejecuta_bloque_y_no_imprime() -> None:
    inter = InterpretadorCobra()
    ast = [NodoCondicional(NodoValor(False), [NodoImprimir(NodoValor("no"))], [])]

    with patch("sys.stdout", new_callable=StringIO) as out:
        for nodo in ast:
            inter.ejecutar_nodo(nodo)

    lineas = _lineas_sin_trazas(out.getvalue())
    assert lineas == []


@pytest.mark.parametrize("condicion", ["5", '"hola"', "x"])
def test_condicional_con_condicion_no_booleana_lanza_error_semantico(
    condicion: str,
) -> None:
    with pytest.raises(
        CondicionNoBooleanaError, match=r"^La condición debe ser booleana$"
    ):
        _ejecutar_codigo(
            f"""
var x = 5
si {condicion}:
    pasar
fin
"""
        )


def test_condicional_con_comparacion_mantiene_comportamiento_correcto() -> None:
    inter = _ejecutar_codigo(
        """
var x = 5
si x == 5:
    var ok = 1
fin
"""
    )
    assert inter.variables["ok"] == 1


def test_condicional_false_no_ejecuta_bloque_si_y_ejecuta_sino() -> None:
    inter = _ejecutar_codigo(
        """
var salida = 0
si 1 == 2:
    var salida = 1
sino:
    var salida = 2
fin
"""
    )
    assert inter.variables["salida"] == 2


def test_condicionales_anidados_se_ejecutan_correctamente() -> None:
    inter = _ejecutar_codigo(
        """
var bandera = 1
si bandera == 1:
    si 2 > 1:
        var valor = 7
    sino:
        var valor = 0
    fin
fin
"""
    )
    assert inter.variables["valor"] == 7


def test_anidamiento_profundo_no_lanza_recursion_error() -> None:
    profundidad = 8
    codigo = ["var ok = 0"]
    codigo.extend("    " * i + "si 1 == 1:" for i in range(profundidad))
    codigo.append("    " * profundidad + "var ok = 1")
    codigo.extend("    " * i + "fin" for i in reversed(range(profundidad)))

    try:
        inter = _ejecutar_codigo("\n".join(codigo))
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert inter.variables["ok"] == 1


def test_identificador_y_en_declaracion_y_uso() -> None:
    inter = _ejecutar_codigo(
        """
var y = 3
var resultado = y + 4
"""
    )
    assert inter.variables["resultado"] == 7


def test_ast_imprimir_comparacion_booleana_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(10)),
        NodoImprimir(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(10),
            )
        ),
    ]

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    lineas = _lineas_sin_trazas(out.getvalue())
    assert lineas[-1] in {"verdadero", "falso"}


def test_ast_condicional_ejecuta_bloque_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(10)),
        NodoCondicional(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(10),
            ),
            [NodoImprimir(NodoValor("ok"))],
            [],
        ),
    ]

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    lineas = _lineas_sin_trazas(out.getvalue())
    assert lineas[-1] == "ok"


def test_expresiones_booleanas_validas_siguen_funcionando_en_condicional() -> None:
    inter = InterpretadorCobra()
    condicion_compuesta = NodoOperacionBinaria(
        NodoOperacionBinaria(
            NodoIdentificador("x"),
            Token(TipoToken.IGUAL, "=="),
            NodoValor(5),
        ),
        Token(TipoToken.AND, "y"),
        NodoOperacionUnaria(
            Token(TipoToken.NOT, "!"),
            NodoOperacionBinaria(
                NodoIdentificador("y"),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(1),
            ),
        ),
    )
    ast = [
        NodoAsignacion("x", NodoValor(5)),
        NodoAsignacion("y", NodoValor(0)),
        NodoCondicional(condicion_compuesta, [NodoAsignacion("ok", NodoValor(1))], []),
    ]

    for nodo in ast:
        inter.ejecutar_nodo(nodo)

    assert inter.variables["ok"] == 1


def test_ast_comparacion_identificador_indefinido_controla_nameerror_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    nodo = NodoImprimir(
        NodoOperacionBinaria(
            NodoIdentificador("y"),
            Token(TipoToken.IGUAL, "=="),
            NodoValor(10),
        )
    )

    try:
        with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
            inter.ejecutar_nodo(nodo)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")


class _ValidadorCiclicoControlado(ValidadorBase):
    def visit_llamada_funcion(self, nodo: NodoLlamadaFuncion) -> None:
        self.generic_visit(nodo)
        if nodo.nombre == "bloquear":
            raise ValueError("error controlado de validación")


def test_validador_base_en_ast_ciclico_no_lanza_recursion_error_y_propaga_error_controlado() -> None:
    raiz = NodoLlamadaFuncion("raiz", [])
    nodo_bloqueado = NodoLlamadaFuncion("bloquear", [])
    raiz.argumentos.append(nodo_bloqueado)
    nodo_bloqueado.argumentos.append(raiz)

    validador = _ValidadorCiclicoControlado()

    try:
        with pytest.raises(ValueError, match=r"^error controlado de validación$"):
            raiz.aceptar(validador)
    except RecursionError as exc:
        pytest.fail(f"No debía lanzar RecursionError: {exc}")
