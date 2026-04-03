from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import TipoToken, Token
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoOperacionBinaria,
    NodoValor,
)
from core.interpreter import InterpretadorCobra
from core.lexer import Lexer
from core.parser import Parser

_EJECUTAR_ASIGNACION_ORIGINAL = InterpretadorCobra.ejecutar_asignacion


def _ejecutar_asignacion_sin_retorno(
    inter: InterpretadorCobra, nodo: NodoAsignacion, visitados: set[str] | None = None
) -> None:
    _EJECUTAR_ASIGNACION_ORIGINAL(inter, nodo, visitados)
    return None


def _ejecutar_codigo_y_capturar_salida(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            with patch("core.qualia_bridge.register_execution", return_value=None), patch(
                "pcobra.core.qualia_bridge.register_execution", return_value=None
            ), patch.object(
                InterpretadorCobra,
                "ejecutar_asignacion",
                new=_ejecutar_asignacion_sin_retorno,
            ):
                inter.ejecutar_ast(ast)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    return out.getvalue().strip()


def test_comparacion_identificador_en_imprimir_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 10
imprimir x == 10
"""
    )
    assert salida == "True"


def test_comparacion_identificador_con_suma_en_imprimir_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 5
imprimir x + 5 == 10
"""
    )
    assert salida == "True"


def test_comparacion_identificador_en_condicional_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 10
si x == 10:
    imprimir "ok"
fin
"""
    )
    assert salida == "ok"


def test_comparacion_identificador_con_suma_en_condicional_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 5
si x + 5 == 10:
    imprimir "ok"
fin
"""
    )
    assert salida == "ok"


def test_identificador_indefinido_en_comparacion_controlado_sin_recursionerror() -> None:
    codigo = "imprimir y == 10\n"

    try:
        _ejecutar_codigo_y_capturar_salida(codigo)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")
    except NameError as exc:
        assert str(exc) == "Variable no declarada: y"
    else:
        pytest.fail("Se esperaba NameError para identificador no declarado")


def test_ast_directo_comparacion_identificador_sin_recursionerror() -> None:
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
            with patch("core.qualia_bridge.register_execution", return_value=None), patch(
                "pcobra.core.qualia_bridge.register_execution", return_value=None
            ), patch.object(
                InterpretadorCobra,
                "ejecutar_asignacion",
                new=_ejecutar_asignacion_sin_retorno,
            ):
                inter.ejecutar_ast(ast)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "True"


def test_ast_directo_comparacion_identificador_con_suma_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(5)),
        NodoImprimir(
            NodoOperacionBinaria(
                NodoOperacionBinaria(
                    NodoIdentificador("x"),
                    Token(TipoToken.SUMA, "+"),
                    NodoValor(5),
                ),
                Token(TipoToken.IGUAL, "=="),
                NodoValor(10),
            )
        ),
    ]

    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            with patch("core.qualia_bridge.register_execution", return_value=None), patch(
                "pcobra.core.qualia_bridge.register_execution", return_value=None
            ), patch.object(
                InterpretadorCobra,
                "ejecutar_asignacion",
                new=_ejecutar_asignacion_sin_retorno,
            ):
                inter.ejecutar_ast(ast)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "True"


def test_ast_directo_condicional_identificador_sin_recursionerror() -> None:
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
            with patch("core.qualia_bridge.register_execution", return_value=None), patch(
                "pcobra.core.qualia_bridge.register_execution", return_value=None
            ), patch.object(
                InterpretadorCobra,
                "ejecutar_asignacion",
                new=_ejecutar_asignacion_sin_retorno,
            ):
                inter.ejecutar_ast(ast)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert out.getvalue().strip() == "ok"


def test_ast_directo_alias_encadenado_en_comparacion_materializa_booleano() -> None:
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(10)

    expresion = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.IGUAL, "=="),
        NodoValor(10),
    )

    try:
        resultado = inter.evaluar_expresion(expresion)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert resultado is True


def test_comparacion_con_ciclo_alias_lanza_error_controlado_y_no_recursionerror() -> None:
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoIdentificador("a")

    expresion = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.IGUAL, "=="),
        NodoValor(10),
    )

    try:
        with pytest.raises(RuntimeError, match=r"^Ciclo de variables detectado en 'a'$"):
            inter.evaluar_expresion(expresion)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")


def test_operacion_suma_materializa_identificador_y_alias() -> None:
    inter = InterpretadorCobra()
    inter.variables["a"] = NodoIdentificador("b")
    inter.variables["b"] = NodoValor(7)

    expresion = NodoOperacionBinaria(
        NodoIdentificador("a"),
        Token(TipoToken.SUMA, "+"),
        NodoValor(3),
    )

    try:
        resultado = inter.evaluar_expresion(expresion)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert resultado == 10


def test_operacion_and_materializa_identificador_y_alias() -> None:
    inter = InterpretadorCobra()
    inter.variables["flag"] = NodoIdentificador("alias_flag")
    inter.variables["alias_flag"] = NodoValor(True)

    expresion = NodoOperacionBinaria(
        NodoIdentificador("flag"),
        Token(TipoToken.AND, "&&"),
        NodoValor(True),
    )

    try:
        resultado = inter.evaluar_expresion(expresion)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert resultado is True


def test_operacion_or_materializa_identificador_y_alias() -> None:
    inter = InterpretadorCobra()
    inter.variables["flag"] = NodoIdentificador("alias_flag")
    inter.variables["alias_flag"] = NodoValor(False)

    expresion = NodoOperacionBinaria(
        NodoIdentificador("flag"),
        Token(TipoToken.OR, "||"),
        NodoValor(True),
    )

    try:
        resultado = inter.evaluar_expresion(expresion)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")

    assert resultado is True
