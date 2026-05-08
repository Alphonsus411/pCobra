from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.core.interpreter import InterpretadorCobra as CoreInterpretador
from pcobra.cobra.core.interpreter import InterpretadorCobra as CobraInterpretador
from pcobra.core import usar_loader as core_usar_loader


@pytest.mark.parametrize("interp_cls", [CoreInterpretador, CobraInterpretador])
def test_usar_export_policy_rechaza_simbolos_privados(interp_cls, monkeypatch):
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "_interno", "__oculto__"]
    mod.es_finito = lambda valor: valor == valor
    mod._interno = lambda: "no"
    mod.__oculto__ = lambda: "no"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"

    monkeypatch.setattr(core_usar_loader, "obtener_modulo_cobra_oficial", lambda _nombre: mod)

    from pcobra.core.lexer import Lexer
    from pcobra.core.parser import Parser

    interp = interp_cls()
    ast = Parser(Lexer('usar "numero"').tokenizar()).parsear()
    interp.ejecutar_ast(ast)

    assert callable(interp.obtener_variable("es_finito"))
    with pytest.raises(NameError):
        interp.obtener_variable("_interno")
    with pytest.raises(NameError):
        interp.obtener_variable("__oculto__")


def test_entrypoints_interpreter_comparten_clase_canonica():
    assert CoreInterpretador is CobraInterpretador
