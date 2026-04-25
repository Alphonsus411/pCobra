from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from cobra.core import Lexer, Parser
from core.interpreter import InterpretadorCobra


def _ejecutar_codigo_y_capturar_stdout(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    inter = InterpretadorCobra()

    with patch("sys.stdout", new_callable=StringIO) as out:
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            for nodo in ast:
                inter.ejecutar_nodo(nodo)

    return out.getvalue()


def _lineas_sin_trazas(salida: str) -> list[str]:
    lineas_limpias: list[str] = []
    for linea in salida.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("["):
            continue
        if linea.startswith("cobra> "):
            linea = linea[len("cobra> ") :].strip()
        if linea.startswith("... "):
            linea = linea[len("... ") :].strip()
        if linea:
            lineas_limpias.append(linea)
    return lineas_limpias


def _ejecutar_via_interactive(codigo: str) -> str:
    inter = InterpretadorCobra()
    ast = Parser(Lexer(codigo).tokenizar()).parsear()

    with patch("sys.stdout", new_callable=StringIO) as out:
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            for nodo in ast:
                inter.ejecutar_nodo(nodo)
    return out.getvalue()


def test_mientras_reutiliza_variable_externa_sin_crear_scope() -> None:
    codigo = """
var i = 10

mientras i < 12:
    i = i + 1
fin

imprimir(i)
"""

    salida = _ejecutar_codigo_y_capturar_stdout(codigo)
    lineas = _lineas_sin_trazas(salida)

    assert lineas[-1] == "12"
    assert "Variable no declarada: i" not in salida
    assert "NameError" not in salida


def test_ejecutar_e_interactive_observan_mismo_scope() -> None:
    codigo_archivo = """
var contador = 0
mientras contador < 2:
    contador = contador + 1
fin

var base = 10
func subir_base():
    base = base + 5
fin
subir_base()

imprimir("contador")
imprimir(contador)
imprimir("base")
imprimir(base)
"""
    salida_ejecutar = _lineas_sin_trazas(_ejecutar_codigo_y_capturar_stdout(codigo_archivo))
    salida_interactive = _lineas_sin_trazas(_ejecutar_via_interactive(codigo_archivo))

    esperadas = ["contador", "2", "base", "15"]
    assert salida_ejecutar[-len(esperadas) :] == esperadas
    assert salida_interactive[-len(esperadas) :] == esperadas


def test_mutacion_en_mientras_persiste_fuera_del_bucle() -> None:
    codigo = """
var total = 1
mientras total < 4:
    total = total + 1
fin
imprimir(total)
"""
    salida = _lineas_sin_trazas(_ejecutar_codigo_y_capturar_stdout(codigo))
    assert salida[-1] == "4"


def test_variable_externa_se_actualiza_en_scope_correcto_durante_mientras() -> None:
    codigo = """
var acumulado = 0
func sumar_hasta_dos():
    mientras acumulado < 2:
        acumulado = acumulado + 1
    fin
fin
sumar_hasta_dos()
imprimir(acumulado)
"""
    salida = _lineas_sin_trazas(_ejecutar_codigo_y_capturar_stdout(codigo))
    assert salida[-1] == "2"
