from __future__ import annotations

from pcobra.standard_library import __all__ as standard_library_public_api
from pcobra.standard_library import decoradores

EXPECTED_PUBLIC_DECORATORS = {
    "memoizar",
    "dataclase",
    "temporizar",
    "depreciado",
    "sincronizar",
    "reintentar",
    "reintentar_async",
    "orden_total",
    "despachar_por_tipo",
}


def test_standard_library_reexporta_decoradores_publicos_criticos() -> None:
    missing = EXPECTED_PUBLIC_DECORATORS - set(standard_library_public_api)
    assert not missing, f"Decoradores públicos faltantes en standard_library.__all__: {sorted(missing)}"


def test_decoradores_modulo_mantiene_inventario_publico_critico() -> None:
    missing = EXPECTED_PUBLIC_DECORATORS - set(decoradores.__all__)
    assert not missing, f"Decoradores públicos faltantes en decoradores.__all__: {sorted(missing)}"


def test_decoradores_publicos_siguen_disponibles_como_callables() -> None:
    for symbol in sorted(EXPECTED_PUBLIC_DECORATORS):
        exported = getattr(decoradores, symbol, None)
        assert callable(exported), f"El decorador `{symbol}` ya no es callable"
