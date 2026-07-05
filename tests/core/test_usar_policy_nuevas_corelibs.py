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
from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial, usar_modulo
from pcobra.core.ast_nodes import NodoUsar
from pcobra.core.interpreter import InterpretadorCobra

RAIZ_REPO = Path(__file__).resolve().parents[2]
RUTAS_BASE_CORELIBS_USAR = (
    RAIZ_REPO / "src/pcobra/corelibs",
    RAIZ_REPO / "src/pcobra/standard_library",
)

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


def _assert_ruta_interna_es_modulo_soportado(alias: str, ruta_relativa: str) -> Path:
    """Valida que la ruta canónica apunte a un módulo Python permitido."""

    ruta_interna = RAIZ_REPO / ruta_relativa
    assert ruta_interna.exists(), (
        f"No existe la ruta interna para usar {alias}: {ruta_relativa}"
    )
    assert ruta_interna.is_file(), (
        f"La ruta interna para usar {alias} debe ser un archivo: {ruta_relativa}"
    )
    assert ruta_interna.suffix == ".py", (
        f"La ruta interna para usar {alias} debe ser un módulo Python: {ruta_relativa}"
    )
    assert any(ruta_interna.is_relative_to(base) for base in RUTAS_BASE_CORELIBS_USAR), (
        f"La ruta interna para usar {alias} debe estar bajo corelibs/ o "
        f"standard_library/: {ruta_relativa}"
    )
    return ruta_interna


@pytest.mark.parametrize("alias", ALIASES_NUEVAS_CORELIBS)
def test_alias_nueva_corelib_cumple_contrato_publico_y_modulo_importable(
    alias: str,
) -> None:
    validar_contrato_modulos_canonicos_usar()

    assert alias in USAR_COBRA_PUBLIC_MODULES
    assert alias in REPL_COBRA_MODULE_INTERNAL_PATH_MAP

    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
    _assert_ruta_interna_es_modulo_soportado(alias, ruta_relativa)

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


def test_usar_modulo_inexistente_falla_con_excepcion_controlada() -> None:
    assert "modulo_inexistente" not in USAR_COBRA_PUBLIC_MODULES

    with pytest.raises((PermissionError, ValueError, FileNotFoundError, ImportError)) as excinfo:
        usar_modulo("modulo_inexistente")

    mensaje = str(excinfo.value).lower()
    assert (
        "fuera del catálogo" in mensaje
        or "fuera del catalogo" in mensaje
        or "no permitido" in mensaje
        or "no encontrado" in mensaje
    )


def test_usar_datos_expone_filtrar_callable_sin_callback_cobra() -> None:
    exports = usar_modulo("datos")

    assert "filtrar" in exports
    assert callable(exports["filtrar"])


def test_usar_datos_apunta_a_standard_library_y_loader_importa_nombre_correcto() -> None:
    ruta_relativa = REPL_COBRA_MODULE_INTERNAL_PATH_MAP["datos"]

    assert ruta_relativa == "src/pcobra/standard_library/datos.py"
    assert (RAIZ_REPO / ruta_relativa).is_file()

    modulo = obtener_modulo_cobra_oficial("datos")

    assert modulo.__name__ == "pcobra.standard_library.datos"
    assert modulo.__name__ != "pcobra.cobra.corelibs.datos"
    assert getattr(modulo, "__file__", None) is not None
    assert Path(modulo.__file__).resolve() == (RAIZ_REPO / ruta_relativa).resolve()
