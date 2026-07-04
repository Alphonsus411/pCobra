from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    REPL_COBRA_MODULE_INTERNAL_PATH_MAP,
    USAR_COBRA_PUBLIC_MODULES,
    validar_contrato_modulos_canonicos_usar,
)
from pcobra.core.ast_nodes import NodoUsar
from pcobra.core.interpreter import InterpretadorCobra

RAIZ_REPO = Path(__file__).resolve().parents[2]

ALIASES_NUEVAS_CORELIBS = (
    "ruta",
    "serializacion",
    "proceso",
    "registro",
    "argumentos",
    "pruebas",
    "temporal",
    "cripto",
    "regex",
    "compresion",
    "configuracion",
)


def _nombre_import_desde_ruta_interna(ruta_relativa: str) -> str:
    """Convierte una ruta canónica interna en su nombre importable Python."""

    if ruta_relativa.startswith("src/pcobra/corelibs/"):
        return f"pcobra.corelibs.{Path(ruta_relativa).stem}"
    if ruta_relativa.startswith("src/pcobra/standard_library/"):
        return f"pcobra.standard_library.{Path(ruta_relativa).stem}"
    raise AssertionError(f"Ruta interna no soportada por el contrato: {ruta_relativa}")


@pytest.mark.parametrize("alias", ALIASES_NUEVAS_CORELIBS)
def test_alias_nueva_corelib_cumple_contrato_publico_y_modulo_importable(
    alias: str,
) -> None:
    validar_contrato_modulos_canonicos_usar()

    assert alias in USAR_COBRA_PUBLIC_MODULES
    assert alias in REPL_COBRA_MODULE_INTERNAL_PATH_MAP

    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
    ruta_interna = RAIZ_REPO / ruta_relativa
    assert (
        ruta_interna.exists()
    ), f"No existe la ruta interna para usar {alias}: {ruta_relativa}"

    modulo = importlib.import_module(_nombre_import_desde_ruta_interna(ruta_relativa))
    exportes = getattr(modulo, "__all__", None)
    assert exportes, f"El módulo {alias} debe definir __all__ no vacío"


@pytest.mark.parametrize("alias", ALIASES_NUEVAS_CORELIBS)
def test_contrato_superficie_nueva_corelib_coincide_exactamente_con_all(
    alias: str,
) -> None:
    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
    modulo = importlib.import_module(_nombre_import_desde_ruta_interna(ruta_relativa))

    assert tuple(CANONICAL_MODULE_SURFACE_CONTRACTS[alias].required_functions) == tuple(
        modulo.__all__
    )


@pytest.mark.parametrize("alias", ALIASES_NUEVAS_CORELIBS)
def test_repl_resuelve_nueva_corelib_con_nodo_usar_sin_parser_lexer(alias: str) -> None:
    interprete = InterpretadorCobra()
    interprete.configurar_restriccion_usar_repl({alias: alias})

    interprete.ejecutar_nodo(NodoUsar(alias))

    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
    modulo = importlib.import_module(_nombre_import_desde_ruta_interna(ruta_relativa))
    exportes = tuple(getattr(modulo, "__all__", ()))
    assert exportes
    assert any(nombre in interprete.variables for nombre in exportes)
