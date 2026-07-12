from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from pcobra.core.interpreter import InterpretadorCobra as CoreInterpretador
from pcobra.cobra.core.interpreter import InterpretadorCobra as CobraInterpretador
from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra import usar_loader


@pytest.mark.parametrize("interp_cls", [CoreInterpretador, CobraInterpretador])
def test_usar_export_policy_rechaza_simbolos_privados(interp_cls, monkeypatch):
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "_interno", "__oculto__"]
    mod.es_finito = lambda valor: valor == valor
    mod._interno = lambda: "no"
    mod.__oculto__ = lambda: "no"
    rel_path = usar_loader.REPL_COBRA_MODULE_INTERNAL_PATH_MAP["numero"]
    ruta_oficial = (
        Path(usar_loader.__file__).resolve().parents[3] / rel_path
    ).resolve()
    mod.__file__ = str(ruta_oficial)

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
