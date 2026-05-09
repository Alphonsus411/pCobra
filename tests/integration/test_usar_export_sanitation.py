from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.core import usar_loader as core_usar_loader


class _NodoUsar:
    def __init__(self, modulo: str) -> None:
        self.modulo = modulo


def _modulo_stub(nombre: str, exports: dict[str, object]) -> ModuleType:
    mod = ModuleType(nombre)
    mod.__all__ = list(exports)
    for k, v in exports.items():
        setattr(mod, k, v)
    mod.__file__ = f"/workspace/pCobra/src/pcobra/corelibs/{nombre}.py"
    return mod


def test_usar_numero_y_texto_solo_exponen_nombres_canonicos_espanol(monkeypatch):
    numero = _modulo_stub("numero", {"es_finito": lambda n: n == n, "isfinite": lambda n: n == n})
    texto = _modulo_stub("texto", {"a_snake": lambda s: s, "to_snake": lambda s: s})
    stubs = {"numero": numero, "texto": texto}
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: stubs[nombre])
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre: stubs[nombre])

    interp = InterpretadorCobra()
    interp.ejecutar_usar(_NodoUsar("numero"))
    interp.ejecutar_usar(_NodoUsar("texto"))

    simbolos = set(interp.contextos[-1].values)
    assert "es_finito" in simbolos
    assert "a_snake" in simbolos
    assert "isfinite" not in simbolos
    assert "to_snake" not in simbolos


def test_usar_datos_expone_filtrar_mapear_reducir_no_equivalentes_en_ingles(monkeypatch):
    datos = _modulo_stub(
        "datos",
        {
            "filtrar": lambda xs, fn: [x for x in xs if fn(x)],
            "mapear": lambda xs, fn: [fn(x) for x in xs],
            "reducir": lambda xs, fn, ini=None: ini,
            "filter": lambda xs, fn: [x for x in xs if fn(x)],
            "map": lambda xs, fn: [fn(x) for x in xs],
        },
    )
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: datos)
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre: datos)

    interp = InterpretadorCobra()
    interp.ejecutar_usar(_NodoUsar("datos"))
    simbolos = set(interp.contextos[-1].values)

    assert {"filtrar", "mapear", "reducir"}.issubset(simbolos)
    assert "filter" not in simbolos
    assert "map" not in simbolos


@pytest.mark.parametrize("modulo_externo", ["numpy", "node-fetch", "serde", "holobit_sdk"])
def test_rechaza_usar_modulos_externos_no_permitidos(modulo_externo):
    interp = InterpretadorCobra()

    with pytest.raises(PermissionError):
        interp.ejecutar_usar(_NodoUsar(modulo_externo))


def test_rechaza_simbolos_prohibidos_en_exports(monkeypatch):
    modulo = _modulo_stub(
        "datos",
        {
            "filtrar": lambda xs, fn: [x for x in xs if fn(x)],
            "__oculto__": lambda: None,
            "_interno": lambda: None,
            "self": object(),
            "append": object(),
            "map": object(),
            "filter": object(),
            "unwrap": object(),
            "expect": object(),
        },
    )
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: modulo)
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre: modulo)

    interp = InterpretadorCobra()
    interp.ejecutar_usar(_NodoUsar("datos"))
    simbolos = set(interp.contextos[-1].values)

    assert "filtrar" in simbolos
    for prohibido in ("__oculto__", "_interno", "self", "append", "map", "filter", "unwrap", "expect"):
        assert prohibido not in simbolos


def test_colision_en_usar_emite_advertencia_y_no_sobrescribe(monkeypatch):
    numero = _modulo_stub("numero", {"es_finito": lambda _n: "desde_usar"})
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: numero)
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre: numero)

    interp = InterpretadorCobra()
    interp.contextos[-1].define("es_finito", "valor_preexistente")

    interp.configurar_politica_colision_usar("warn_alias_required")

    with pytest.warns(RuntimeWarning, match="Conflicto de nombres en `usar`"):
        with pytest.raises(NameError, match="colisión"):
            interp.ejecutar_usar(_NodoUsar("numero"))

    assert interp.contextos[-1].values["es_finito"] == "valor_preexistente"
