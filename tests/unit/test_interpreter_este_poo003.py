"""Binding de receptor desde fuente Cobra, sin construir AST manual."""

import pytest

from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.interpreter import InterpretadorCobra


def _ejecutar(inter, fuente):
    inter.ejecutar_ast(parsear_codigo_resuelto(fuente, usar_cache=False))


def _estado(inter):
    return tuple(inter.contextos), tuple(inter.mem_contextos), inter._call_depth


def _comprobar_ambitos(inter, anterior):
    contextos, memoria, profundidad = anterior
    assert len(inter.contextos) == len(contextos)
    assert all(a is b for a, b in zip(inter.contextos, contextos))
    assert len(inter.mem_contextos) == len(memoria)
    assert all(a is b for a, b in zip(inter.mem_contextos, memoria))
    assert inter._call_depth == profundidad


@pytest.mark.parametrize("receptor", ["este", "self"])
def test_retorno_conserva_identidad_y_no_filtra_receptor(receptor):
    inter = InterpretadorCobra()
    anterior = _estado(inter)
    _ejecutar(
        inter,
        "clase Persona:\n"
        f"    metodo identidad({receptor}):\n"
        f"        retorno {receptor}\n"
        "fin\n"
        "var persona = Persona()\n"
        "var resultado = persona.identidad()\n",
    )
    assert inter.obtener_variable("resultado") is inter.obtener_variable("persona")
    with pytest.raises(NameError):
        inter.obtener_variable(receptor)
    _comprobar_ambitos(inter, anterior)


def test_este_escribe_y_lee_atributos_de_la_instancia_correcta():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo guardar(este, valor):\n"
        "        atributo este nombre = valor\n"
        "    metodo consultar(este):\n"
        "        retorno atributo este nombre\n"
        "fin\n"
        "var primera = Persona()\n"
        "var segunda = Persona()\n"
        "primera.guardar(42)\n"
        "segunda.guardar(7)\n"
        "var valor_primero = primera.consultar()\n"
        "var valor_segundo = segunda.consultar()\n",
    )
    assert inter.obtener_variable("valor_primero") == 42
    assert inter.obtener_variable("valor_segundo") == 7
    assert inter.obtener_variable("primera") is not inter.obtener_variable("segunda")


def test_este_local_no_confunde_ni_modifica_el_global():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "var este = 42\n"
        "clase Persona:\n"
        "    metodo identidad(este):\n"
        "        retorno este\n"
        "fin\n"
        "var persona = Persona()\n"
        "var resultado = persona.identidad()\n",
    )
    assert inter.obtener_variable("resultado") is inter.obtener_variable("persona")
    assert inter.obtener_variable("este") == 42


def test_fallo_en_cuerpo_restaura_ambitos_y_permite_otra_llamada():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo fallo(este):\n"
        "        var capturado = este\n"
        "        retorno inexistente\n"
        "    metodo identidad(este):\n"
        "        retorno este\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    anterior = _estado(inter)
    with pytest.raises(NameError, match=r"^Variable no declarada: inexistente$"):
        _ejecutar(inter, "persona.fallo()\n")
    _comprobar_ambitos(inter, anterior)
    with pytest.raises(NameError):
        inter.obtener_variable("este")
    _ejecutar(inter, "var resultado = persona.identidad()\n")
    assert inter.obtener_variable("resultado") is inter.obtener_variable("persona")
    _comprobar_ambitos(inter, anterior)


def test_no_se_inventa_un_receptor_alternativo():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo identidad(otro):\n"
        "        retorno otro\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    with pytest.raises(
        TypeError,
        match=r"^Método 'identidad' requiere un receptor 'este' o 'self'$",
    ):
        _ejecutar(inter, "persona.identidad()\n")


def test_ruta_self_no_introduce_este_implicito():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo identidad(self):\n"
        "        retorno este\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    with pytest.raises(NameError, match=r"^Variable no declarada: este$"):
        _ejecutar(inter, "persona.identidad()\n")


@pytest.mark.parametrize(
    ("argumentos", "esperados"),
    [
        ("", 1),
        ("1, 2", 1),
    ],
)
def test_metodo_rechaza_aridad_incorrecta_sin_filtrar_ambitos(argumentos, esperados):
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo guardar(este, valor):\n"
        "        atributo este numero = valor\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    anterior = _estado(inter)
    with pytest.raises(
        TypeError,
        match=rf"^Método 'guardar': se esperaban {esperados} argumentos$",
    ):
        _ejecutar(inter, f"persona.guardar({argumentos})\n")
    _comprobar_ambitos(inter, anterior)
    assert inter.obtener_variable("persona")["__atributos__"] == {}


def test_argumento_de_metodo_se_evalua_una_vez_en_el_entorno_llamador():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "var numero = 42\n"
        "clase Persona:\n"
        "    metodo devolver(este, numero):\n"
        "        retorno numero\n"
        "fin\n"
        "var persona = Persona()\n"
        "var resultado = persona.devolver(numero)\n",
    )
    assert inter.obtener_variable("resultado") == 42
    assert inter.obtener_variable("numero") == 42


def test_metodo_sin_parametros_rechaza_la_ausencia_de_receptor():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo identidad():\n"
        "        retorno 42\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    with pytest.raises(
        TypeError,
        match=r"^Método 'identidad' requiere un receptor 'este' o 'self'$",
    ):
        _ejecutar(inter, "persona.identidad()\n")
