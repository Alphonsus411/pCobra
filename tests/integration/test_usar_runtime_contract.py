from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import USAR_RUNTIME_EXPORT_OVERRIDES
from pcobra.core import usar_symbol_policy


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


def test_holobit_runtime_override_exporta_exclusivamente_api_publica():
    assert tuple(USAR_RUNTIME_EXPORT_OVERRIDES["holobit"]) == (
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    )


def test_sanear_exportables_clasifica_y_rechaza_wrappers_backend():
    modulo_sdk = ModuleType("holobit_sdk")

    class WrapperConWrapped:
        __wrapped__ = modulo_sdk

    class WrapperConSdk:
        _sdk = modulo_sdk

    simbolos = [
        ("crear_holobit", lambda valores: valores),
        ("holobit_sdk", modulo_sdk),
        ("wrapper", WrapperConWrapped()),
        ("wrapper_sdk", WrapperConSdk()),
    ]
    permitidos, clasificacion, _warnings = usar_symbol_policy.sanear_exportables_para_usar(simbolos)

    assert [nombre for nombre, _ in permitidos] == ["crear_holobit"]
    codigos = {rechazo.nombre: rechazo.codigo for rechazo in clasificacion.rechazos_duros}
    assert codigos["holobit_sdk"] == "cobra_public_equivalent"
    assert codigos["wrapper"] == "backend_module_object"
    assert codigos["wrapper_sdk"] == "backend_module_object"


def test_rechaza_numpy_en_repl_estricto_sin_inyeccion(monkeypatch):
    monkeypatch.setattr(
        "pcobra.core.usar_loader.obtener_modulo_cobra_oficial",
        lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"numero": "numero"})
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match="modulo_fuera_catalogo_publico|módulo externo no permitido en REPL estricto") as exc:
        interp.ejecutar_usar(_nodo("numpy"))

    assert "usar_error[modulo_fuera_catalogo_publico]" in str(exc.value)
    assert estado_pre == interp.contextos[-1].values


def test_texto_simbolo_existente_fuera_de_override_falla_como_no_declarado(monkeypatch):
    mod = ModuleType("texto")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["texto"], "normalizar_unicode"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["texto"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.normalizar_unicode = lambda texto, forma="NFC": texto
    mod.__file__ = "/workspace/pCobra/src/pcobra/standard_library/texto.py"

    monkeypatch.setattr("pcobra.core.usar_loader.obtener_modulo_cobra_oficial", lambda _nombre: mod)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"texto": "texto"})
    interp.ejecutar_usar(_nodo("texto"))

    assert "normalizar_unicode" not in interp.contextos[-1].values
    with pytest.raises(NameError, match=r"^Variable no declarada: normalizar_unicode$"):
        interp.contextos[-1].get("normalizar_unicode")


def test_regresion_texto_detecta_mapeo_interno_incompleto_y_filtra_fuera_de_api_publica():
    mod = ModuleType("texto")
    mod.__all__ = [*USAR_RUNTIME_EXPORT_OVERRIDES["texto"], "normalizar_unicode"]
    for name in USAR_RUNTIME_EXPORT_OVERRIDES["texto"]:
        setattr(mod, name, lambda *args, **kwargs: (args, kwargs))
    mod.normalizar_unicode = lambda texto, forma="NFC": texto

    from pcobra.core.usar_loader import sanitizar_exports_publicos

    mapa_limpio, conflictos = sanitizar_exports_publicos(mod, "texto")

    assert "normalizar_unicode" not in mapa_limpio
    assert any(
        conflicto.get("symbol") == "normalizar_unicode" and conflicto.get("code") == "outside_public_api"
        for conflicto in conflictos
    )
