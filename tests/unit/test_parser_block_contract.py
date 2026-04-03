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
