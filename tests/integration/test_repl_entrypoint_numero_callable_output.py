from __future__ import annotations

from types import ModuleType

from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_nan"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_nan = lambda valor: valor != valor
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def test_entrypoint_repl_real_usar_numero_callable_es_finito_y_es_nan(monkeypatch, capsys):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()

    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("imprimir(es_finito(10))")
    cmd._ejecutar_en_modo_normal("imprimir(es_nan(10))")

    salida = capsys.readouterr().out
    assert "verdadero" in salida
    assert "falso" in salida
