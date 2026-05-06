from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import USAR_RUNTIME_EXPORT_OVERRIDES


def _nodo(modulo: str):
    class _NodoUsar:
        pass

    _NodoUsar.modulo = modulo
    return _NodoUsar()


def test_holobit_export_only_runtime_override(monkeypatch):
    mod = ModuleType("holobit")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["holobit"], "holobit_sdk", "_to_sdk_holobit"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.holobit_sdk = object()
    mod._to_sdk_holobit = lambda *_: None
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/holobit.py"

    monkeypatch.setattr("pcobra.core.usar_loader.obtener_modulo_cobra_oficial", lambda _nombre: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"holobit": "holobit"})
    interp.ejecutar_usar(_nodo("holobit"))

    simbolos = set(interp.contextos[-1].values)
    assert set(USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]).issubset(simbolos)
    assert "holobit_sdk" not in simbolos
    assert "_to_sdk_holobit" not in simbolos
    assert all("__" not in name for name in simbolos)


def test_rechaza_numpy_en_repl_estricto_sin_inyeccion(monkeypatch):
    monkeypatch.setattr(
        "pcobra.core.usar_loader.obtener_modulo_cobra_oficial",
        lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match="módulo externo no permitido en REPL estricto"):
        interp.ejecutar_usar(_nodo("numpy"))

    assert estado_pre == interp.contextos[-1].values
