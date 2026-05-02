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
def test_repl_contract_usar_aliases_y_restriccion_numpy(factory, executor, get_interp, monkeypatch):
    mod_numero = _modulo_numero_stub()
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

    executor(cmd, 'usar "numero"')
    executor(cmd, "es_finito(10)")
    assert interp.obtener_variable("es_finito")(10) is True

    executor(cmd, 'usar "texto"')
    executor(cmd, 'a_snake("HolaMundo")')
    assert interp.obtener_variable("a_snake")("HolaMundo") == "hola_mundo"

    with pytest.raises(PermissionError, match="módulos externos no soportados en REPL"):
        executor(cmd, 'usar "numpy"')

    assert "numpy" not in interp.variables

    with pytest.raises(Exception, match=r"Token no reconocido: '\.'"):
        executor(cmd, "numero.es_finito(10)")
