"""Regresión del contrato de sugerencias automáticas para GUI/IA.

Cada recomendación documentada debe partir de código validado por ``Lexer`` y
``Parser`` y debe proponer solo construcciones ya aceptadas por el parser.
"""

from __future__ import annotations

import pytest

from pcobra.cobra.core import Lexer, Parser, ParserError


RECOMENDACIONES_GUI = [
    pytest.param(
        "retorno_en_funciones",
        """
func saludar(nombre):
    retorno nombre
fin
""",
        """
func saludar(nombre):
    retornar nombre
fin
""",
        "Libro §3.3 Sentencias y §3.4 Funciones: usar `retorno`, no `retornar`.",
        id="retorno-en-funciones",
    ),
    pytest.param(
        "usar_importacion_con_cadena",
        """
usar "numero"
imprimir(es_finito(10))
""",
        """
usar "numero" como numero
imprimir(numero.es_finito(10))
""",
        "Libro §3.6 Módulos: `usar` no acepta alias `como`; usar importación plana.",
        id="usar-sin-alias-como",
    ),
    pytest.param(
        "funciones_con_func",
        """
func calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
""",
        """
funcion calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
""",
        "Libro §3.4 Funciones: el parser implementa `func`/`definir`.",
        id="func-no-funcion",
    ),
]


def _parsear(codigo: str):
    tokens = Lexer(codigo).tokenizar()
    return Parser(tokens).parsear()


@pytest.mark.parametrize(
    ("nombre", "fragmento_sugerido", "fragmento_invalido", "regla_libro"),
    RECOMENDACIONES_GUI,
)
def test_recomendaciones_gui_solo_proponen_fragmentos_aceptados_por_parser(
    nombre: str,
    fragmento_sugerido: str,
    fragmento_invalido: str,
    regla_libro: str,
) -> None:
    assert nombre
    assert regla_libro.startswith("Libro §3")
    ast = _parsear(fragmento_sugerido)
    assert ast


@pytest.mark.parametrize(
    ("nombre", "fragmento_sugerido", "fragmento_invalido", "regla_libro"),
    RECOMENDACIONES_GUI,
)
def test_recomendaciones_gui_cubren_ejemplos_invalidos_sin_ampliar_parser(
    nombre: str,
    fragmento_sugerido: str,
    fragmento_invalido: str,
    regla_libro: str,
) -> None:
    assert nombre
    assert fragmento_sugerido != fragmento_invalido
    assert regla_libro
    with pytest.raises(ParserError):
        _parsear(fragmento_invalido)
