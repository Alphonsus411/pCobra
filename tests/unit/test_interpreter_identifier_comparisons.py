from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from cobra.core import TipoToken, Token
from core.ast_nodes import (
    NodoAST,
    NodoAsignacion,
    NodoCondicional,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
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

    salida = out.getvalue().strip()
    lineas = [linea for linea in salida.splitlines() if linea.strip()]
    return lineas[-1] if lineas else ""


def _ultima_linea_no_vacia(salida: str) -> str:
    lineas = [linea for linea in salida.strip().splitlines() if linea.strip()]
    return lineas[-1] if lineas else ""


def _ejecutar_codigo_y_capturar_stdout_completo(codigo: str) -> str:
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

    return out.getvalue()


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


def test_comparacion_identificador_con_suma_en_imprimir_desde_x_diez() -> None:
    salida = _ejecutar_codigo_y_capturar_salida(
        """
x = 10
imprimir x + 5 == 10
"""
    )
    assert salida == "False"




def test_regresion_imprimir_suma_y_comparacion_sin_recursionerror() -> None:
    salida = _ejecutar_codigo_y_capturar_stdout_completo(
        """
x = 5
imprimir x + 5
imprimir x == 10
"""
    )

    lineas = [
        linea.strip()
        for linea in salida.splitlines()
        if linea.strip() and not linea.lstrip().startswith("[")
    ]
    assert lineas[-2:] == ["10", "False"]

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


def test_identificador_derecho_indefinido_en_comparacion_controlado_sin_recursionerror() -> None:
    codigo = """
x = 10
imprimir x == y
"""

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

    assert _ultima_linea_no_vacia(out.getvalue()) == "True"


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

    assert _ultima_linea_no_vacia(out.getvalue()) == "True"


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

    assert _ultima_linea_no_vacia(out.getvalue()) == "ok"


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


def test_debug_traces_en_comparacion_identificador_simple() -> None:
    salida = _ejecutar_codigo_y_capturar_stdout_completo(
        """
x = 10
imprimir x == 10
"""
    )

    assert "[AST BEFORE OPT]" in salida
    assert "[AST AFTER OPT]" in salida
    assert "[EVAL]" in salida
    assert "[BIN-ENTER]" in salida
    assert "[BIN-LEFT]" in salida
    assert "[BIN-RIGHT]" in salida
    assert "[BIN-RESULT]" in salida
    assert _ultima_linea_no_vacia(salida) == "True"


def test_debug_traces_en_comparacion_identificador_con_suma() -> None:
    salida = _ejecutar_codigo_y_capturar_stdout_completo(
        """
x = 5
imprimir x + 5 == 10
"""
    )

    assert "[AST BEFORE OPT]" in salida
    assert "[AST AFTER OPT]" in salida
    assert "[EVAL]" in salida
    assert "[BIN-ENTER]" in salida
    assert "[BIN-LEFT]" in salida
    assert "[BIN-RIGHT]" in salida
    assert "[BIN-RESULT]" in salida
    assert _ultima_linea_no_vacia(salida) == "True"


def test_debug_traces_identificador_derecho_indefinido_nameerror_sin_recursionerror() -> None:
    codigo = """
x = 10
imprimir x == y
"""

    try:
        with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
            _ejecutar_codigo_y_capturar_stdout_completo(codigo)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")


def test_ast_ciclico_en_evaluacion_lanza_error_controlado_sin_recursionerror() -> None:
    inter = InterpretadorCobra()
    ciclo = NodoOperacionBinaria(
        NodoValor(1),
        Token(TipoToken.SUMA, "+"),
        NodoValor(2),
    )
    ciclo.derecha = ciclo

    try:
        with patch.object(
            NodoOperacionBinaria,
            "__repr__",
            lambda self: "<NodoOperacionBinariaCiclico>",
        ):
            with pytest.raises(Exception, match=r"Recursive evaluation detected"):
                inter.evaluar_expresion(ciclo)
    except RecursionError as exc:  # pragma: no cover - contrato explícito
        pytest.fail(f"No debía lanzar RecursionError: {exc}")


def test_ast_minimo_identificador_mas_valor_con_x_diez() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoAsignacion("x", NodoValor(10)),
        NodoImprimir(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.SUMA, "+"),
                NodoValor(5),
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

    lineas = [
        linea.strip()
        for linea in out.getvalue().splitlines()
        if linea.strip() and not linea.strip().startswith("[")
    ]
    assert "15" in lineas


def test_ast_minimo_identificador_igual_valor_con_x_diez() -> None:
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

    lineas = [
        linea.strip()
        for linea in out.getvalue().splitlines()
        if linea.strip() and not linea.strip().startswith("[")
    ]
    assert "True" in lineas


def test_ast_control_no_regresion_print_cinco_mas_cinco() -> None:
    inter = InterpretadorCobra()
    ast = [
        NodoImprimir(
            NodoOperacionBinaria(
                NodoValor(5),
                Token(TipoToken.SUMA, "+"),
                NodoValor(5),
            )
        )
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

    lineas = [
        linea.strip()
        for linea in out.getvalue().splitlines()
        if linea.strip() and not linea.strip().startswith("[")
    ]
    assert "10" in lineas


def test_binarias_con_identificadores_no_retorna_nodoast() -> None:
    inter = InterpretadorCobra()
    inter.variables["x"] = NodoValor(10)

    expresiones = [
        NodoOperacionBinaria(
            NodoIdentificador("x"),
            Token(TipoToken.IGUAL, "=="),
            NodoValor(10),
        ),
        NodoOperacionBinaria(
            NodoOperacionBinaria(
                NodoIdentificador("x"),
                Token(TipoToken.SUMA, "+"),
                NodoValor(5),
            ),
            Token(TipoToken.IGUAL, "=="),
            NodoValor(15),
        ),
    ]

    for expr in expresiones:
        resultado = inter.evaluar_expresion(expr)
        assert not isinstance(resultado, NodoAST)


def test_repr_ast_contrato_corto_en_operacion_binaria_anidada() -> None:
    class _NodoPeligroso:
        def __repr__(self) -> str:  # pragma: no cover - debe no invocarse
            raise AssertionError("No se debe invocar __repr__ de hijos")

        def __str__(self) -> str:  # pragma: no cover - debe no invocarse
            raise AssertionError("No se debe invocar __str__ de hijos")

    token_suma = Token(TipoToken.SUMA, "+")
    token_igual = Token(TipoToken.IGUAL, "==")
    expresion_anidada = NodoOperacionBinaria(
        NodoOperacionBinaria(_NodoPeligroso(), token_suma, NodoValor(1)),
        token_igual,
        NodoIdentificador("x"),
    )

    representacion = repr(expresion_anidada)
    assert representacion.startswith("<NodoOperacionBinaria id=")
    assert representacion.endswith(">")
    assert "_NodoPeligroso" not in representacion
    assert repr(expresion_anidada.izquierda).startswith("<NodoOperacionBinaria id=")


def test_str_delega_a_repr_en_nodos_objetivo() -> None:
    token_suma = Token(TipoToken.SUMA, "+")
    nodo_binario = NodoOperacionBinaria(NodoValor(1), token_suma, NodoValor(2))
    nodo_unario = NodoOperacionUnaria(token_suma, NodoValor(1))
    nodo_identificador = NodoIdentificador("x")
    nodo_imprimir = NodoImprimir(NodoValor(1))
    nodo_llamada = NodoLlamadaFuncion("f", [])

    for nodo in (
        nodo_binario,
        nodo_unario,
        nodo_identificador,
        nodo_imprimir,
        nodo_llamada,
    ):
        assert str(nodo) == repr(nodo)
