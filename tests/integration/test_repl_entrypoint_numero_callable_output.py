from __future__ import annotations

from types import ModuleType

import pytest

from pcobra.core import usar_loader as core_usar_loader
from pcobra.core import interpreter as core_interpreter
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


def _modulo_datos_stub() -> ModuleType:
    mod = ModuleType("datos")
    mod.__all__ = ["longitud"]
    mod.longitud = lambda valor: len(valor)
    mod.__file__ = "/workspace/pCobra/src/pcobra/corelibs/datos.py"
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




def test_entrypoint_repl_usar_datos_longitud_variable_y_literal_exactos(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal("var xs = [1, 2, 3]")
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal("imprimir(longitud(xs))")
    cmd._ejecutar_en_modo_normal("imprimir(longitud([1, 2, 3]))")

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert salida.count("3") >= 2
def test_entrypoint_repl_lista_con_expresiones_y_longitud(capsys):
    cmd = ReplCommandV2()
    cmd._ejecutar_en_modo_normal('usar "datos"')
    cmd._ejecutar_en_modo_normal("var a = 10")
    cmd._ejecutar_en_modo_normal("var xs = [a, a + 1]")
    cmd._ejecutar_en_modo_normal("imprimir(longitud(xs))")

    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]
    assert "2" in salida


def test_entrypoint_repl_metadata_longitud_persistente_entre_sentencias(monkeypatch, capsys):
    """Regresión REPL: metadata de `usar` persiste entre sentencias incrementales."""
    mod_datos = _modulo_datos_stub()
    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo_cobra_oficial",
        lambda nombre: mod_datos if nombre == "datos" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )
    monkeypatch.setattr(
        core_usar_loader,
        "obtener_modulo",
        lambda nombre, **_kwargs: mod_datos if nombre == "datos" else (_ for _ in ()).throw(ModuleNotFoundError(nombre)),
    )
    monkeypatch.setattr(
        core_interpreter,
        "build_and_validate_usar_symbol_metadata",
        lambda *, module_name, symbol_name, callable_obj: {
            "origin_kind": "usar",
            "module": module_name,
            "symbol": symbol_name,
            "sanitized": True,
            "public_api": True,
            "backend_exposed": False,
            "callable": callable(callable_obj),
        },
    )

    cmd = ReplCommandV2()
    interp = cmd._delegate.interpretador

    # Sentencia 1
    cmd._ejecutar_en_modo_normal('usar "datos"')
    metadata_s1 = dict(getattr(interp, "_usar_symbol_metadata", {}))
    metadata_validador_s1 = dict(getattr(interp._validador, "_metadata_simbolos_usar", {}))
    ref_metadata_interp = getattr(interp, "_usar_symbol_metadata", None)
    ref_metadata_validador = getattr(interp._validador, "_metadata_simbolos_usar", None)

    assert "longitud" in metadata_s1
    assert isinstance(metadata_validador_s1, dict)

    # Sentencia 2
    cmd._ejecutar_en_modo_normal("var xs = [1,2,3]")
    metadata_s2 = dict(getattr(interp, "_usar_symbol_metadata", {}))
    metadata_validador_s2 = dict(getattr(interp._validador, "_metadata_simbolos_usar", {}))
    assert getattr(interp, "_usar_symbol_metadata", None) is ref_metadata_interp
    assert getattr(interp._validador, "_metadata_simbolos_usar", None) is ref_metadata_validador

    # Snapshot interno: para claves existentes, mismo contenido (se permiten adiciones).
    for clave, valor_s1 in metadata_s1.items():
        assert clave in metadata_s2
        assert metadata_s2[clave] == valor_s1
    for clave, valor_s1 in metadata_validador_s1.items():
        assert clave in metadata_validador_s2
        assert metadata_validador_s2[clave] == valor_s1

    # Sentencia 3
    cmd._ejecutar_en_modo_normal("imprimir(longitud(xs))")
    salida = [linea.strip() for linea in capsys.readouterr().out.splitlines() if linea.strip()]

    assert "3" in salida

    metadata_s3 = dict(getattr(interp, "_usar_symbol_metadata", {}))
    metadata_validador_s3 = dict(getattr(interp._validador, "_metadata_simbolos_usar", {}))
    assert getattr(interp, "_usar_symbol_metadata", None) is ref_metadata_interp
    assert getattr(interp._validador, "_metadata_simbolos_usar", None) is ref_metadata_validador

    # Invariante: no se pierde metadata previa ni se degrada a NoneType en llamadas posteriores.
    for clave, valor_s1 in metadata_s1.items():
        assert clave in metadata_s3
        assert metadata_s3[clave] == valor_s1
    for clave, valor_s1 in metadata_validador_s1.items():
        assert clave in metadata_validador_s3
        assert metadata_validador_s3[clave] == valor_s1
