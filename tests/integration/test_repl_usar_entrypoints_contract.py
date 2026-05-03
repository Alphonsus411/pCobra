from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.core.runtime import InterpretadorCobra
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def _modulo_texto_stub() -> ModuleType:
    mod = ModuleType("texto")
    mod.__all__ = ["a_snake"]
    mod.a_snake = lambda texto: "hola_mundo" if texto == "HolaMundo" else str(texto)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/texto.py"
    return mod


@pytest.mark.parametrize("factory", [lambda: InteractiveCommand(InterpretadorCobra()), ReplCommandV2])
def test_entrypoints_repl_configuran_restriccion_estricta(factory):
    cmd = factory()
    interp = cmd.interpretador if isinstance(cmd, InteractiveCommand) else cmd._delegate.interpretador
    assert interp._repl_usar_alias_map == REPL_COBRA_MODULE_MAP


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numero_sin_prefijo(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "numero"')
    executor(cmd, "es_finito(10)")

    assert interp.obtener_variable("es_finito")(10) is True


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_texto_sin_prefijo(factory, executor, get_interp, monkeypatch):
    mod_texto = _modulo_texto_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "texto":
            return mod_texto
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "texto"')
    executor(cmd, 'a_snake("HolaMundo")')

    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numpy_restringido_atomico(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    executor(cmd, 'usar "numero"')
    estado_pre_numpy = dict(interp.contextos[-1].values)
    simbolos_pre = set(interp.contextos[-1].values.keys())

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        executor(cmd, 'usar "numpy"')

    # Contrato de Cobra: `usar` es plano (sin `.`), no se expone namespace tipo `numero.*`.
    assert "numpy" not in interp.variables
    assert "numpy" not in interp.contextos[-1].values
    assert estado_pre_numpy == interp.contextos[-1].values
    assert simbolos_pre == set(interp.contextos[-1].values.keys())

    with pytest.raises(Exception, match=r"Token no reconocido: '\.'"):
        executor(cmd, "numero.es_finito(10)")





def _modulo_tiempo_stub() -> ModuleType:
    mod = ModuleType("tiempo")
    mod.__all__ = ["ahora"]
    mod.ahora = lambda: "2026-05-03T00:00:00"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/tiempo.py"
    return mod


def _modulo_datos_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["longitud"]
    mod.longitud = lambda valores: len(valores)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
    return mod

def _modulo_numero_multi_export_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_par"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_par = lambda valor: isinstance(valor, int) and valor % 2 == 0
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def _assert_contrato_simbolos_saneados(simbolos: set[str]) -> None:
    bloqueados_explicitos = {"self", "append", "map", "filter", "unwrap", "expect"}
    for simbolo in simbolos:
        assert "__" not in simbolo
        assert not simbolo.startswith("_")
        assert simbolo not in bloqueados_explicitos


def _modulo_holobit_publico_stub() -> ModuleType:
    mod = ModuleType("holobit")
    mod.__all__ = [
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    ]
    for nombre in mod.__all__:
        setattr(mod, nombre, lambda *args, _nombre=nombre, **kwargs: {"ok": _nombre, "args": args, "kwargs": kwargs})
    mod.Holobit = object
    mod._to_sdk_holobit = lambda *_args, **_kwargs: None
    mod.holobit_sdk = object()
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/holobit.py"
    return mod


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_colision_no_sobrescribe_usuario(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_multi_export_stub()
    mod_texto = _modulo_texto_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        if nombre == "texto":
            return mod_texto
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    interp.contextos[-1].define("es_finito", lambda _valor: "ocupado")

    with pytest.raises(NameError, match=r"No se puede usar el módulo 'numero': colisión estructurada="):
        executor(cmd, 'usar "numero"')

    assert interp.obtener_variable("es_finito")("x") == "ocupado"
    assert "es_par" not in interp.contextos[-1].values


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_rechazo_externo_no_inyecta_simbolos(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "numero":
            return mod_numero
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)
    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        executor(cmd, 'usar "requests"')

    assert estado_pre == interp.contextos[-1].values
    assert "requests" not in interp.contextos[-1].values


def test_usar_externo_whitelist_sin_all_falla_claro_y_atomico(monkeypatch):
    mod_externo = ModuleType("externo_sin_all")
    mod_externo.__file__ = "/tmp/externo_sin_all.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo", lambda *_args, **_kwargs: mod_externo)

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(None)

    class _NodoUsar:
        modulo = "externo_sin_all"

    estado_pre = dict(interp.contextos[-1].values)

    with pytest.raises(ImportError, match="módulo externo no exportable para usar: requiere __all__ con callables públicos"):
        interp.ejecutar_usar(_NodoUsar())

    assert estado_pre == interp.contextos[-1].values
    assert "externo_sin_all" not in interp.contextos[-1].values


@pytest.mark.parametrize(
    ("factory", "executor", "get_interp"),
    [
        (lambda: InteractiveCommand(InterpretadorCobra()), lambda cmd, code: cmd.ejecutar_codigo(code), lambda cmd: cmd.interpretador),
        (ReplCommandV2, lambda cmd, code: cmd._ejecutar_en_modo_normal(code), lambda cmd: cmd._delegate.interpretador),
    ],
)
def test_repl_contract_resuelve_usar_datos_y_tiempo(factory, executor, get_interp, monkeypatch):
    mod_datos = _modulo_datos_stub()
    mod_tiempo = _modulo_tiempo_stub()

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "datos":
            return mod_datos
        if nombre == "tiempo":
            return mod_tiempo
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    cmd = factory()
    interp = get_interp(cmd)

    executor(cmd, 'usar "datos"')
    executor(cmd, 'usar "tiempo"')

    assert interp.obtener_variable("longitud")([1, 2, 3]) == 3
    assert interp.obtener_variable("ahora")() == "2026-05-03T00:00:00"


def test_repl_contract_seguridad_usar_holobit_restringe_internals_y_saneamiento(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()

    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "holobit":
            return mod_holobit
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)
    interp._repl_usar_alias_map = alias_map

    class _NodoUsar:
        modulo = "holobit"

    interp.ejecutar_usar(_NodoUsar())
    simbolos_holobit = set(mod_holobit.__all__)

    for simbolo in simbolos_holobit:
        assert simbolo in interp.contextos[-1].values

    _assert_contrato_simbolos_saneados(simbolos_holobit)

    assert "Holobit" not in interp.contextos[-1].values
    assert "_to_sdk_holobit" not in interp.contextos[-1].values
    assert "holobit_sdk" not in interp.contextos[-1].values

    cmd = InteractiveCommand(InterpretadorCobra())
    cmd.interpretador.configurar_restriccion_usar_repl(alias_map)
    estado_pre = dict(cmd.interpretador.contextos[-1].values)
    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        cmd.ejecutar_codigo('usar "holobit_sdk"')

    assert estado_pre == cmd.interpretador.contextos[-1].values


def test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite(monkeypatch):
    mod_holobit = _modulo_holobit_publico_stub()
    mod_datos = _modulo_datos_stub()
    alias_map = {**REPL_COBRA_MODULE_MAP, "holobit": "holobit"}

    def _resolver_modulo(nombre: str, **_kwargs):
        if nombre == "holobit":
            return mod_holobit
        if nombre == "datos":
            return mod_datos
        raise ModuleNotFoundError(nombre)

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda nombre: _resolver_modulo(nombre))

    interp = InterpretadorCobra()
    interp.configurar_restriccion_usar_repl(alias_map)
    interp._repl_usar_alias_map = alias_map

    interp.contextos[-1].define("graficar", lambda _hb: "ocupado")
    estado_pre_holobit = dict(interp.contextos[-1].values)
    with pytest.raises(NameError, match=r"No se puede usar el módulo 'holobit':"):
        class _NodoUsarHolobit:
            modulo = "holobit"

        interp.ejecutar_usar(_NodoUsarHolobit())
    assert estado_pre_holobit == interp.contextos[-1].values

    assert interp.obtener_variable("graficar")({}) == "ocupado"

    interp.contextos[-1].define("longitud", lambda _v: -1)
    estado_pre_datos = dict(interp.contextos[-1].values)
    with pytest.raises(NameError, match=r"No se puede usar el módulo 'datos':"):
        class _NodoUsarDatos:
            modulo = "datos"

        interp.ejecutar_usar(_NodoUsarDatos())
    assert estado_pre_datos == interp.contextos[-1].values

    assert interp.obtener_variable("longitud")([]) == -1
