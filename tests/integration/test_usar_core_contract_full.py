from __future__ import annotations

from ast import literal_eval
from types import ModuleType

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP
from pcobra.core import usar_loader as core_usar_loader

from tests.integration.test_repl_usar_entrypoints_contract import (
    _assert_contrato_simbolos_saneados,
    _modulo_holobit_publico_stub,
    _modulo_numero_stub,
    _modulo_texto_stub,
)


def _modulo_datos_publico_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["filtrar", "mapear", "reducir"]
    mod.filtrar = lambda valores, predicado=None: valores
    mod.mapear = lambda valores, fn=None: valores
    mod.reducir = lambda valores, fn=None, inicial=None: inicial if inicial is not None else valores[0]
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
    return mod


def _extraer_error_estructurado_desde_colision(mensaje: str) -> dict[str, str]:
    prefijo = "colisión estructurada="
    assert prefijo in mensaje
    payload = mensaje.split(prefijo, 1)[1].strip()
    return literal_eval(payload)


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_01_numero_exporta_solo_espanol(factory, executor, get_interp, monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: _modulo_numero_stub())
    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "numero"')
    simbolos = set(interp.contextos[-1].values.keys())
    assert "es_finito" in simbolos
    assert "isfinite" not in simbolos


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_02_texto_exporta_solo_espanol(factory, executor, get_interp, monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: _modulo_texto_stub())
    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "texto"')
    simbolos = set(interp.contextos[-1].values.keys())
    assert "a_snake" in simbolos
    assert "snake_case" not in simbolos


def test_03_datos_contiene_filtrar_mapear_reducir(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: _modulo_datos_publico_stub())
    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.ejecutar_codigo('usar "datos"')
    simbolos = cmd.interpretador.contextos[-1].values
    for nombre in ("filtrar", "mapear", "reducir"):
        assert nombre in simbolos


def test_04_rechaza_numpy_y_no_inyecta(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)))
    cmd = InteractiveCommand(InterpretadorCobra())
    estado_pre = dict(cmd.interpretador.contextos[-1].values)
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "numpy"')
    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_05_rechaza_holobit_sdk(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))
    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.interpretador.configurar_restriccion_usar_repl({**REPL_COBRA_MODULE_MAP, "holobit": "holobit"})
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "holobit_sdk"')


def test_06_saneamiento_excluye_nombres_prohibidos_y_doble_guion_bajo():
    _assert_contrato_simbolos_saneados(set(_modulo_holobit_publico_stub().__all__))


def test_07_startup_no_carga_backends_legacy():
    import importlib
    import sys

    legacy = (
        "pcobra.cobra.transpilers.transpiler.to_go",
        "pcobra.cobra.transpilers.transpiler.to_cpp",
        "pcobra.cobra.transpilers.transpiler.to_java",
        "pcobra.cobra.transpilers.transpiler.to_wasm",
        "pcobra.cobra.transpilers.transpiler.to_asm",
    )
    importlib.import_module("pcobra")
    for nombre in legacy:
        assert nombre not in sys.modules


def test_08_politica_publica_backends_exacta():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_09_colision_reporta_error_estructurado(monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: _modulo_datos_publico_stub())
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)
    interp.contextos[-1].define("filtrar", lambda *_args, **_kwargs: "ocupado")

    class _NodoUsar:
        modulo = "datos"

    with pytest.raises(NameError, match=r"No se puede usar el módulo 'datos': colisión estructurada=") as excinfo:
        interp.ejecutar_usar(_NodoUsar())

    detalle = _extraer_error_estructurado_desde_colision(str(excinfo.value))
    assert detalle["code"] == "symbol_collision"
    assert detalle["message"] == "símbolo ya existe en contexto actual"
    assert detalle["symbol"] == "filtrar"
    assert detalle["module"] == "datos"
    assert detalle["phase"] == "preflight"


def test_10_no_inyecta___self_append_map_filter_unwrap_expect(monkeypatch):
    mod = ModuleType("externo")
    mod.__all__ = ["ok", "self", "append", "map", "filter", "unwrap", "expect", "__danger__"]
    mod.ok = lambda: "ok"
    mod.self = mod.append = mod.map = mod.filter = mod.unwrap = mod.expect = lambda *_args, **_kwargs: None
    mod.__danger__ = lambda: "boom"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/mod_ext.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)
    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({"mod_ext": "mod_ext"})

    class _NodoUsar:
        modulo = "mod_ext"

    with pytest.raises(ImportError, match=r"rechazos de saneamiento en usar") as excinfo:
        interp.ejecutar_usar(_NodoUsar())

    msg = str(excinfo.value)
    for token in ("self", "append", "map", "filter", "unwrap", "expect"):
        assert token in msg
    assert "__danger__" not in interp.contextos[-1].values
