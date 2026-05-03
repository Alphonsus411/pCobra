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

    with pytest.raises(PermissionError, match=r"módulos externos no soportados en REPL"):
        executor(cmd, 'usar "numpy"')

    # Contrato de Cobra: `usar` es plano (sin `.`), no se expone namespace tipo `numero.*`.
    assert "numpy" not in interp.variables
    assert "numpy" not in interp.contextos[-1].values
    assert estado_pre_numpy == interp.contextos[-1].values
    assert simbolos_pre == set(interp.contextos[-1].values.keys())

    with pytest.raises(Exception, match=r"Token no reconocido: '\.'"):
        executor(cmd, "numero.es_finito(10)")



def _modulo_numero_multi_export_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_par"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_par = lambda valor: isinstance(valor, int) and valor % 2 == 0
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
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

    with pytest.raises(NameError, match=r"No se puede usar el módulo 'numero': el símbolo 'es_finito' ya existe"):
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

    with pytest.raises(PermissionError, match=r"módulos externos no soportados en REPL"):
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
