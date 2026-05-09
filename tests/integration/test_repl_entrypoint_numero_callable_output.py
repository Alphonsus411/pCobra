from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_nan", "entero_a_base", "_interno"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_nan = lambda valor: valor != valor
    mod.entero_a_base = lambda valor, _base=2: format(int(valor), "b")
    mod._interno = lambda _valor: "oculto"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def test_entrypoint_repl_real_numero_stdout_canonico_y_sin_error_no_implementada(monkeypatch, capsys):
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
    assert "Función 'es_finito' no implementada" not in salida


def test_entrypoint_repl_real_rechaza_simbolo_no_exportado_por_superficie_publica(monkeypatch):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')

    with pytest.raises(NameError, match=r"Variable no declarada: entero_a_base"):
        cmd._ejecutar_en_modo_normal("entero_a_base(10)")


def test_entrypoint_repl_real_rechaza_numpy_externo(monkeypatch):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    with pytest.raises(PermissionError, match=r"(módulo externo no permitido en REPL estricto|modulo_fuera_catalogo_publico)"):
        cmd._ejecutar_en_modo_normal('usar "numpy"')


def test_entrypoint_repl_real_funcion_usuario_sigue_operativa_tras_usar(monkeypatch, capsys):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal(
        "func doble(n):\n"
        "    retorno n * 2\n"
        "fin"
    )
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("imprimir(doble(5))")

    salida = capsys.readouterr().out
    assert "10" in salida
