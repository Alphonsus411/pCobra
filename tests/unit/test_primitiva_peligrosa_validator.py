import pytest

from pcobra.core.ast_nodes import NodoIdentificador, NodoLlamadaMetodo, NodoValor
from pcobra.core.semantic_validators import (
    PrimitivaPeligrosaError,
    ValidadorPrimitivaPeligrosa,
)


def test_existe_como_llamada_metodo_no_usa_escape_de_wrapper_publico():
    validador = ValidadorPrimitivaPeligrosa()
    validador.registrar_simbolo_publico_usar(
        "existe",
        "archivo",
        metadata={
            "module": "archivo",
            "exported_name": "existe",
            "is_sanitized_wrapper": True,
            "public_api": True,
        },
    )
    llamada = NodoLlamadaMetodo(
        NodoIdentificador("archivo"),
        "existe",
        [NodoValor("README.md")],
    )

    with pytest.raises(PrimitivaPeligrosaError):
        llamada.aceptar(validador)
