from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra.cli.commands_v2.repl_cmd import ReplCommandV2


def _modulo_numero_stub() -> ModuleType:
    mod = ModuleType("numero")
    mod.__all__ = ["es_finito", "es_nan", "signo", "desviacion_estandar", "_interno"]
    mod.es_finito = lambda valor: valor == valor and valor not in (float("inf"), float("-inf"))
    mod.es_nan = lambda valor: valor != valor
    mod.signo = lambda valor: -1 if valor < 0 else (1 if valor > 0 else 0)
    mod.desviacion_estandar = lambda _valores: 0.0
    mod._interno = lambda _valor: "oculto"
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/numero.py"
    return mod


def test_entrypoint_repl_real_numero_callable_y_stdout_canonico_sin_error_no_implementada(monkeypatch, capsys):
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
    assert "Función 'es_nan' no implementada" not in salida




def test_entrypoint_repl_numero_callable_output_regresion_binding_runtime(monkeypatch, capsys):
    # Contexto: regresión del bug de binding runtime (callable Python en contexto de `usar`).
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
    cmd._ejecutar_en_modo_normal("imprimir(signo(0-5))")

    salida = capsys.readouterr().out
    assert "verdadero" in salida
    assert "falso" in salida
    assert "-1" in salida
    assert "Función 'es_finito' no implementada" not in salida
    assert "Función 'es_nan' no implementada" not in salida
    assert "Función 'signo' no implementada" not in salida
def test_entrypoint_repl_real_numero_callable_directo_sin_no_implementada(monkeypatch, capsys):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')
    cmd._ejecutar_en_modo_normal("es_finito(10)")
    cmd._ejecutar_en_modo_normal("es_nan(10)")

    salida = capsys.readouterr().out
    assert "Función 'es_finito' no implementada" not in salida
    assert "Función 'es_nan' no implementada" not in salida


def test_entrypoint_repl_real_rechaza_simbolo_no_exportado_por_superficie_publica(monkeypatch):
    mod_numero = _modulo_numero_stub()

    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_numero if nombre == "numero" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )

    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "numero"')

    with pytest.raises(NameError, match=r"Variable no declarada: desviacion_estandar"):
        cmd._ejecutar_en_modo_normal("desviacion_estandar([1, 2, 3])")


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


def test_entrypoint_repl_real_imprimir_booleanos_canonicos_no_regresion(monkeypatch, capsys):
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
    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    assert lineas.count("verdadero") >= 1
    assert lineas.count("falso") >= 1


def test_entrypoint_repl_texto_flujo_integral_callable_output(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "texto"')
    cmd._ejecutar_en_modo_normal('imprimir(recortar("  Cobra  "))')
    cmd._ejecutar_en_modo_normal('imprimir(repetir("ja", 3))')
    cmd._ejecutar_en_modo_normal('imprimir(quitar_acentos("canción"))')

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "Cobra" in salida
    assert "jajaja" in salida
    assert "cancion" in salida


def test_entrypoint_repl_asignacion_lista_no_reporta_nodolista(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal("var xs = [1, 2, 3]")
    cmd._ejecutar_en_modo_normal("imprimir(xs)")

    salida = capsys.readouterr().out
    assert "[1, 2, 3]" in salida
    assert "Expresión no soportada: tipo=NodoLista" not in salida


def test_entrypoint_repl_usar_datos_longitud_argumento_inline(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal("imprimir(longitud([1, 2, 3]))")

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "3" in salida


def test_entrypoint_repl_lista_con_expresiones_y_longitud(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal("var a = 10")
    cmd._ejecutar_en_modo_normal("var xs = [a, a + 1]")
    cmd._ejecutar_en_modo_normal("imprimir(longitud(xs))")

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "2" in salida
