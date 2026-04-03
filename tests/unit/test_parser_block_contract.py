from __future__ import annotations

import pytest

from cobra.core import Lexer, Parser, ParserError


def _error_de_parseo(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    parser = Parser(tokens)
    with pytest.raises(ParserError) as excinfo:
        parser.parsear()
    return str(excinfo.value)


def test_parser_falla_si_falta_dos_puntos_en_bloque() -> None:
    mensaje = _error_de_parseo(
        """
si 1 == 1
    pasar
fin
"""
    )
    assert mensaje == "Se esperaba ':' después de la condición del 'si'"


def test_parser_falla_si_falta_fin_en_bloque() -> None:
    mensaje = _error_de_parseo(
        """
si 1 == 1:
    pasar
"""
    )
    assert mensaje == "Se esperaba 'fin' para cerrar el bloque condicional"


def test_parser_falla_con_fin_inesperado() -> None:
    mensaje = _error_de_parseo("fin")
    assert mensaje == "Se encontró 'fin' inesperado"


@pytest.mark.parametrize(
    ("codigo", "prefijo_esperado"),
    [
        (
            """
si 1 == 1
    pasar
fin
""",
            "Se esperaba ':'",
        ),
        (
            """
mientras 1 == 1
    pasar
fin
""",
            "Se esperaba ':'",
        ),
        (
            """
si 1 == 1:
    pasar
""",
            "Se esperaba 'fin'",
        ),
    ],
)
def test_mensajes_de_error_son_consistentes(codigo: str, prefijo_esperado: str) -> None:
    mensaje = _error_de_parseo(codigo)
    assert mensaje.startswith(prefijo_esperado)


@pytest.mark.parametrize(
    ("codigo", "mensaje_esperado"),
    [
        (
            """
si 1 == 1
    pasar
fin
""",
            "Se esperaba ':' después de la condición del 'si'",
        ),
        (
            """
si 1 == 1:
    pasar
sino
    pasar
fin
""",
            "Se esperaba ':' después de 'sino'",
        ),
        (
            """
si 1 == 1:
    pasar
sino
si 2 == 2
    pasar
fin
""",
            "Se esperaba ':' después de la condición del 'sino si'",
        ),
        (
            """
mientras 1 == 1
    pasar
fin
""",
            "Se esperaba ':' después de la condición del bucle 'mientras'",
        ),
        (
            """
para i in rango(3)
    pasar
fin
""",
            "Se esperaba ':' después del iterable en 'para'",
        ),
        (
            """
try
    pasar
fin
""",
            "Se esperaba ':' después de 'try'",
        ),
    ],
)
def test_regresion_mensajes_con_espacios_y_saltos_de_linea(
    codigo: str, mensaje_esperado: str
) -> None:
    assert _error_de_parseo(codigo) == mensaje_esperado
