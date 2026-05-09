from __future__ import annotations

from ast import literal_eval
from types import ModuleType

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP, USAR_COBRA_FACING_MODULE_FLAGS
from pcobra.core import usar_loader as core_usar_loader

from tests.integration.test_repl_usar_entrypoints_contract import (
    _assert_contrato_simbolos_saneados,
    _modulo_holobit_publico_stub,
    _modulo_numero_stub,
    _modulo_texto_stub,
)


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
def test_usar_numero_solo_simbolos_espanoles(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod_numero)

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
def test_usar_texto_solo_simbolos_espanoles(factory, executor, get_interp, monkeypatch):
    mod_texto = _modulo_texto_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod_texto)

    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "texto"')

    simbolos = set(interp.contextos[-1].values.keys())
    assert "a_snake" in simbolos
    assert "snake_case" not in simbolos


def _modulo_datos_publico_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["filtrar", "mapear", "reducir"]
    mod.filtrar = lambda valores, predicado=None: valores
    mod.mapear = lambda valores, fn=None: valores
    mod.reducir = lambda valores, fn=None, inicial=None: inicial if inicial is not None else valores[0]
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
    return mod


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_usar_datos_incluye_filtrar_mapear_reducir(factory, executor, get_interp, monkeypatch):
    mod_datos = _modulo_datos_publico_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod_datos)

    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "datos"')

    for simbolo in ("filtrar", "mapear", "reducir"):
        assert simbolo in interp.contextos[-1].values


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_rechaza_usar_numpy(factory, executor, get_interp, monkeypatch):
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    cmd = factory()
    interp = get_interp(cmd)
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto") as excinfo:
        executor(cmd, 'usar "numpy"')

    assert str(excinfo.value) == "usar_error[modulo_no_permitido]: módulo externo no permitido en REPL estricto (solo alias oficiales Cobra)"
    assert interp.contextos[-1].values == estado_pre


def test_holobit_sdk_internals_no_son_importables(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda nombre, **_kwargs: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.interpretador.configurar_restriccion_usar_repl(alias_map)
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "holobit_sdk"')


def test_usar_holobit_expone_solo_api_cobra_facing(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())

    simbolos = set(mod_holobit.__all__)
    assert simbolos == {"crear_holobit", "validar_holobit", "serializar_holobit", "deserializar_holobit", "proyectar", "transformar", "graficar", "combinar", "medir"}
    assert "holobit_sdk" not in interp.contextos[-1].values
    assert "_to_sdk_holobit" not in interp.contextos[-1].values


def test_simbolos_exportados_sin_doble_guion_bajo_y_sin_prohibidos():
    mod_holobit = _modulo_holobit_publico_stub()
    simbolos = set(mod_holobit.__all__)

    _assert_contrato_simbolos_saneados(simbolos)



def test_politica_publica_backends_exacta_python_javascript_rust():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_conflicto_no_overwrite_silencioso_reporta_error_estructurado(monkeypatch):
    mod_datos = _modulo_datos_publico_stub()

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod_datos)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)
    interp.contextos[-1].define("filtrar", lambda *_args, **_kwargs: "ocupado")

    class _NodoUsar:
        modulo = "datos"

    with pytest.raises(NameError, match=r"No se puede usar el módulo 'datos': (usar_error\[conflicto_simbolo\] )?colisión estructurada=") as excinfo:
        interp.ejecutar_usar(_NodoUsar())

    mensaje = str(excinfo.value)
    assert "colisión estructurada" in mensaje
    detalle = _extraer_error_estructurado_desde_colision(mensaje)
    assert detalle["code"] == "symbol_collision"
    assert detalle["message"] == "símbolo ya existe en contexto actual"
    assert detalle["symbol"] == "filtrar"
    assert detalle["module"] == "datos"
    assert detalle["phase"] == "preflight"


def test_conflictos_emiten_warning_estructurado_por_simbolo(monkeypatch, caplog):
    mod_datos = _modulo_datos_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod_datos)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)
    interp.contextos[-1].define("filtrar", lambda *_args, **_kwargs: "ocupado")
    interp.contextos[-1].define("mapear", lambda *_args, **_kwargs: "ocupado")

    class _NodoUsar:
        modulo = "datos"

    caplog.set_level("WARNING")
    with pytest.raises(NameError):
        interp.ejecutar_usar(_NodoUsar())

    mensajes = [registro.getMessage() for registro in caplog.records if "USAR collision symbol event" in registro.getMessage()]
    assert len(mensajes) >= 2
    assert any("'symbol': 'filtrar'" in mensaje for mensaje in mensajes)
    assert any("'symbol': 'mapear'" in mensaje for mensaje in mensajes)
    assert interp.contextos[-1].get("filtrar")() == "ocupado"
    assert interp.contextos[-1].get("mapear")() == "ocupado"


def test_usar_no_inyecta_simbolos_prohibidos_ni_objetos_backend(monkeypatch):
    mod = ModuleType("externo")
    mod.__all__ = ["ok", "self", "append", "map", "filter", "unwrap", "expect", "__danger__"]
    mod.ok = lambda: "ok"
    mod.self = mod.append = mod.map = mod.filter = mod.unwrap = mod.expect = lambda *_args, **_kwargs: None
    mod.__danger__ = lambda: "boom"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/mod_ext.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod)

    interp = InterpretadorCobra()
    monkeypatch.setitem(USAR_COBRA_FACING_MODULE_FLAGS, "mod_ext", True)
    interp.configurar_restriccion_usar_repl({"mod_ext": "mod_ext"})
    estado_pre = dict(interp.contextos[-1].values)

    class _NodoUsar:
        modulo = "mod_ext"

    interp.ejecutar_usar(_NodoUsar())

    simbolos = set(interp.contextos[-1].values.keys())
    assert "ok" in simbolos
    for prohibido in ("self", "append", "map", "filter", "unwrap", "expect", "__danger__"):
        assert prohibido not in simbolos
    assert "__danger__" not in interp.contextos[-1].values
    assert estado_pre.items() <= interp.contextos[-1].values.items()


def test_usar_holobit_inyecta_solo_all_y_nombres_en_espanol(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({**REPL_COBRA_MODULE_MAP, "holobit": "holobit"})

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())
    simbolos = set(interp.contextos[-1].values.keys())

    assert set(mod_holobit.__all__).issubset(simbolos)
    assert "Holobit" not in simbolos
    assert "holobit_sdk" not in simbolos
    assert "_to_sdk_holobit" not in simbolos
    assert all("_" in nombre or nombre.islower() for nombre in mod_holobit.__all__)


def test_holobit_corelib_deserializacion_invalida_regresion():
    import importlib.util
    from pathlib import Path

    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_regression", ruta)
    holobit = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(holobit)

    with pytest.raises((TypeError, ValueError, KeyError)):
        holobit.deserializar_holobit('{"tipo":"holobit","valores":[1],"extra":true}')


def test_holobit_corelib_superficie_publica_canonica_blackbox():
    import importlib.util
    from pathlib import Path

    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_blackbox_api", ruta)
    holobit = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(holobit)

    assert tuple(holobit.__all__) == (
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


def test_holobit_corelib_error_runtime_solo_terminos_cobra(monkeypatch):
    import importlib.util
    from pathlib import Path

    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_blackbox_runtime", ruta)
    holobit = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(holobit)

    monkeypatch.setattr(
        holobit._AdaptadorInternoHolobit,
        "graficar",
        lambda _hb: (_ for _ in ()).throw(ModuleNotFoundError("holobit_sdk.core.holobit")),
    )

    hb = holobit.crear_holobit([1, 2, 3])
    with pytest.raises(holobit.ErrorHolobit) as excinfo:
        holobit.graficar(hb)

    mensaje = str(excinfo.value)
    assert "Cobra" in mensaje
    assert "holobit_sdk" not in mensaje
    assert "SDKHolobit" not in mensaje


def test_binding_usar_sin_dependencia_lexer_parser_para_datos(monkeypatch):
    mod_datos = _modulo_datos_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda _nombre, **_kwargs: mod_datos)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(REPL_COBRA_MODULE_MAP)

    class _NodoUsar:
        modulo = "datos"

    interp.ejecutar_usar(_NodoUsar())

    simbolos = set(interp.contextos[-1].values.keys())
    assert {"filtrar", "mapear", "reducir"}.issubset(simbolos)


def test_binding_usar_holobit_no_expone_internals_directos(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl({**REPL_COBRA_MODULE_MAP, "holobit": "holobit"})

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())

    simbolos = set(interp.contextos[-1].values.keys())
    assert "holobit_sdk" not in simbolos
    assert "_to_sdk_holobit" not in simbolos
    assert all("__" not in nombre for nombre in simbolos)


def test_sanitizar_exports_publicos_rechaza_objeto_sdk_accidental_en_holobit():
    mod_holobit = _modulo_holobit_publico_stub()

    class _SDKObjetoAccidental:
        __module__ = "holobit_sdk.core.holobit"

    mod_holobit.__all__ = [*mod_holobit.__all__, "SDKHolobitAccidental"]
    mod_holobit.SDKHolobitAccidental = _SDKObjetoAccidental

    mapa, conflictos = core_usar_loader.sanitizar_exports_publicos(mod_holobit, "holobit")

    assert "SDKHolobitAccidental" not in mapa
    assert any(c["symbol"] == "SDKHolobitAccidental" for c in conflictos)
    assert any(c["code"] == "backend_module_object" for c in conflictos if c["symbol"] == "SDKHolobitAccidental")


def test_usar_holobit_no_filtra_nombres_sdk_accidentales_en_contexto(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    class _SDKObjetoAccidental:
        __module__ = "holobit_sdk.core.holobit"

    mod_holobit.__all__ = [*mod_holobit.__all__, "SDKHolobitAccidental"]
    mod_holobit.SDKHolobitAccidental = _SDKObjetoAccidental

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_holobit if nombre == "holobit" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())
    assert "SDKHolobitAccidental" not in interp.contextos[-1].values
