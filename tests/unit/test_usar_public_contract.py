from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP
from pcobra.core import usar_loader as core_usar_loader

from tests.integration.test_repl_usar_entrypoints_contract import (
    _assert_contrato_simbolos_saneados,
    _modulo_holobit_publico_stub,
    _modulo_numero_stub,
    _modulo_texto_stub,
)
from tests.unit.test_backend_bootstrap_contract import _run_python_isolated


def _modulo_datos_publico_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["filtrar", "mapear", "reducir"]
    mod.filtrar = lambda valores, predicado=None: valores
    mod.mapear = lambda valores, fn=None: valores
    mod.reducir = lambda valores, fn=None, inicial=None: inicial if inicial is not None else valores[0]
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
    return mod


def test_usar_numero_y_texto_solo_espanol(monkeypatch):
    modulos = {"numero": _modulo_numero_stub(), "texto": _modulo_texto_stub()}
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: modulos[nombre])

    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.ejecutar_codigo('usar "numero"')
    cmd.ejecutar_codigo('usar "texto"')

    simbolos = set(cmd.interpretador.contextos[-1].values.keys())
    assert "es_finito" in simbolos
    assert "isfinite" not in simbolos
    assert "a_snake" in simbolos
    assert "snake_case" not in simbolos


def test_usar_datos_expone_filtrar_mapear_reducir(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre: _modulo_datos_publico_stub())

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)

    class _NodoUsar:
        modulo = "datos"

    interp.ejecutar_usar(_NodoUsar())

    simbolos = interp.contextos[-1].values
    assert {"filtrar", "mapear", "reducir"}.issubset(simbolos)


def test_rechazo_usar_numpy(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    cmd = InteractiveCommand(InterpretadorCobra())
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "numpy"')


def test_rechazo_internals_holobit_sdk(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _modulo_holobit_publico_stub() if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.interpretador.configurar_restriccion_usar_repl({**REPL_COBRA_MODULE_MAP, "holobit": "holobit"})
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "holobit_sdk"')


def test_usar_holobit_solo_api_cobra(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({**REPL_COBRA_MODULE_MAP, "holobit": "holobit"})

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())
    simbolos = set(interp.contextos[-1].values)
    assert "holobit_sdk" not in simbolos
    assert "_to_sdk_holobit" not in simbolos
    assert set(mod_holobit.__all__).issubset(simbolos)


def test_exportados_no_contienen_doble_guion_bajo():
    simbolos = set(_modulo_holobit_publico_stub().__all__)
    _assert_contrato_simbolos_saneados(simbolos)
    assert not any("__" in simbolo for simbolo in simbolos)


def test_no_aparecen_simbolos_prohibidos_en_exports():
    simbolos = set(_modulo_holobit_publico_stub().__all__)
    prohibidos = {"self", "append", "map", "filter", "unwrap", "expect"}
    assert simbolos.isdisjoint(prohibidos)


def test_runtime_startup_no_carga_legacy_backends():
    result = _run_python_isolated(
        "import pcobra; import sys; "
        "legacy = ("
        "'pcobra.cobra.transpilers.transpiler.to_go',"
        "'pcobra.cobra.transpilers.transpiler.to_cpp',"
        "'pcobra.cobra.transpilers.transpiler.to_java',"
        "'pcobra.cobra.transpilers.transpiler.to_wasm',"
        "'pcobra.cobra.transpilers.transpiler.to_asm',"
        "'pcobra.cobra.internal_compat.legacy_contracts',"
        "'pcobra.cobra.cli.internal_compat.legacy_targets',"
        "); "
        "assert not any(name in sys.modules for name in legacy), 'startup cargó módulos legacy';"
    )
    assert result.returncode == 0, result.stderr


def test_public_backends_contrato_exacto_en_backend_policy():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_public_backends_inmutable_tipo_tuple():
    assert isinstance(PUBLIC_BACKENDS, tuple)
    assert PUBLIC_BACKENDS == tuple(PUBLIC_BACKENDS)
