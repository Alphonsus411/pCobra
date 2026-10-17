"""Identidad Cobra del constructor y adaptación exclusiva del backend Python."""

import pytest

from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.rust_adapter import RustAdapter
from pcobra.cobra.core import Lexer, Parser


def _parsear(fuente):
    return Parser(Lexer(fuente).tokenizar()).parsear()


@pytest.mark.parametrize("declaracion", ["metodo", "func"])
def test_constructor_conserva_identidad_y_python_ejecuta_su_cuerpo(declaracion):
    nodos = _parsear(
        "clase Persona:\n"
        f"    {declaracion} inicializar(este, nombre):\n"
        "        atributo este nombre = nombre\n"
        "fin\n"
    )
    metodo = nodos[0].metodos[0]
    assert metodo.nombre == "inicializar"
    assert metodo.nombre_original == "inicializar"
    assert metodo.parametros == ["este", "nombre"]

    python = PythonAdapter().compile(nodos)
    assert "def __init__(este, nombre):" in python
    assert "def inicializar(" not in python
    entorno = {}
    exec(compile(python, "<poo002>", "exec"), entorno)
    persona = entorno["Persona"]("Adolfo")
    assert persona.nombre == "Adolfo"
    assert metodo.nombre == "inicializar"
    assert metodo.parametros == ["este", "nombre"]


@pytest.mark.parametrize(
    "nombres", [("inicializar", "__init__"), ("__init__", "inicializar")]
)
def test_colision_historica_se_detecta_en_ambos_ordenes(nombres):
    fuente = (
        "clase Persona:\n"
        + "".join(
            f"    metodo {nombre}(este):\n        pasar\n" for nombre in nombres
        )
        + "fin\n"
    )
    parser = Parser(Lexer(fuente).tokenizar())
    clase = parser.parsear()[0]
    assert [metodo.nombre for metodo in clase.metodos] == list(nombres)
    assert len(parser.advertencias) == 1
    assert "inicializar" in parser.advertencias[0]
    assert "__init__" in parser.advertencias[0]


def test_funcion_global_inicializar_conserva_compatibilidad_existente():
    funcion = _parsear("func inicializar(valor):\n    retorno valor\nfin\n")[0]
    assert funcion.nombre == "__init__"
    assert funcion.nombre_original == "inicializar"


def test_constructor_historico_python_sigue_ejecutable():
    nodos = _parsear(
        "clase Persona:\n"
        "    metodo __init__(self, nombre):\n"
        "        atributo self nombre = nombre\n"
        "fin\n"
    )
    assert nodos[0].metodos[0].nombre == "__init__"
    entorno = {}
    exec(compile(PythonAdapter().compile(nodos), "<poo002-legacy>", "exec"), entorno)
    assert entorno["Persona"]("Adolfo").nombre == "Adolfo"


@pytest.mark.parametrize(
    ("adaptador", "cabecera"),
    [
        (JavaScriptAdapter, "inicializar(este, nombre) {"),
        (RustAdapter, "fn inicializar(este, nombre) {"),
    ],
)
def test_salida_provisional_aprobada_no_reintroduce_nombre_python(adaptador, cabecera):
    nodos = _parsear(
        "clase Persona:\n"
        "    metodo inicializar(este, nombre):\n"
        "        atributo este nombre = nombre\n"
        "fin\n"
    )
    salida = adaptador().compile(nodos)
    assert cabecera in salida
    assert "__init__" not in salida
    assert nodos[0].metodos[0].nombre == "inicializar"
    assert nodos[0].metodos[0].parametros == ["este", "nombre"]
