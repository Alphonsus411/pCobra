"""Contrato focal de ejecución de constructores propios desde fuente Cobra."""

import pytest

from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.interpreter import InterpretadorCobra


def _ejecutar(inter, fuente):
    inter.ejecutar_ast(parsear_codigo_resuelto(fuente, usar_cache=False))


@pytest.mark.parametrize(
    ("nombre", "receptor"), [("inicializar", "este"), ("__init__", "self")]
)
def test_constructor_propio_inicializa_atributo(nombre, receptor):
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        f"    metodo {nombre}({receptor}, valor):\n"
        f"        atributo {receptor} numero = valor\n"
        "fin\n"
        "var persona = Persona(42)\n",
    )
    assert inter.obtener_variable("persona")["__atributos__"]["numero"] == 42


def test_constructor_y_argumento_se_ejecutan_una_vez():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "var argumentos = 0\n"
        "var construcciones = 0\n"
        "func producir():\n"
        "    global argumentos\n"
        "    argumentos = argumentos + 1\n"
        "    retorno 42\n"
        "fin\n"
        "clase Persona:\n"
        "    metodo inicializar(este, valor):\n"
        "        global construcciones\n"
        "        construcciones = construcciones + 1\n"
        "        atributo este numero = valor\n"
        "fin\n"
        "var persona = Persona(producir())\n",
    )
    assert inter.obtener_variable("argumentos") == 1
    assert inter.obtener_variable("construcciones") == 1
    assert inter.obtener_variable("persona")["__atributos__"]["numero"] == 42


def test_error_en_constructor_se_propaga_y_restaura_ambitos():
    inter = InterpretadorCobra()
    contextos = tuple(inter.contextos)
    memoria = tuple(inter.mem_contextos)
    profundidad = inter._call_depth
    with pytest.raises(NameError, match=r"^Variable no declarada: inexistente$"):
        _ejecutar(
            inter,
            "clase Persona:\n"
            "    metodo inicializar(este):\n"
            "        var local = 1\n"
            "        imprimir inexistente\n"
            "fin\n"
            "var persona = Persona()\n",
        )
    assert len(inter.contextos) == len(contextos)
    assert all(a is b for a, b in zip(inter.contextos, contextos))
    assert len(inter.mem_contextos) == len(memoria)
    assert all(a is b for a, b in zip(inter.mem_contextos, memoria))
    assert inter._call_depth == profundidad
    with pytest.raises(NameError):
        inter.obtener_variable("persona")


@pytest.mark.parametrize("argumentos", ["", "1, 2"])
def test_constructor_rechaza_numero_incorrecto_de_argumentos(argumentos):
    inter = InterpretadorCobra()
    with pytest.raises(TypeError):
        _ejecutar(
            inter,
            "clase Persona:\n"
            "    metodo inicializar(este, valor):\n"
            "        atributo este numero = valor\n"
            "fin\n"
            f"var persona = Persona({argumentos})\n",
        )


def test_retorno_del_constructor_no_reemplaza_la_instancia():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Persona:\n"
        "    metodo inicializar(este):\n"
        "        atributo este numero = 42\n"
        "        retorno 7\n"
        "fin\n"
        "var persona = Persona()\n",
    )
    persona = inter.obtener_variable("persona")
    assert persona["__clase__"]["nombre"] == "Persona"
    assert persona["__atributos__"]["numero"] == 42


def test_clase_sin_constructor_y_sin_argumentos_sigue_funcionando():
    inter = InterpretadorCobra()
    _ejecutar(inter, "clase Persona:\nfin\nvar persona = Persona()\n")
    assert inter.obtener_variable("persona")["__atributos__"] == {}


@pytest.mark.parametrize(
    "nombres",
    [
        ("inicializar", "__init__"),
        ("__init__", "inicializar"),
        ("inicializar", "inicializar"),
        ("__init__", "__init__"),
    ],
)
def test_constructor_duplicado_no_tiene_precedencia_implicita(nombres):
    fuente = (
        "clase Persona:\n"
        + "".join(
            f"    metodo {nombre}(este):\n        imprimir 1\n"
            for nombre in nombres
        )
        + "fin\nvar persona = Persona()\n"
    )
    with pytest.raises(TypeError, match="varios constructores propios"):
        _ejecutar(InterpretadorCobra(), fuente)


@pytest.mark.parametrize("parametros", ["", "otro"])
def test_receptor_de_constructor_no_soportado_se_rechaza(parametros):
    with pytest.raises(TypeError, match="receptor 'este' o 'self'"):
        _ejecutar(
            InterpretadorCobra(),
            "clase Persona:\n"
            f"    metodo inicializar({parametros}):\n"
            "        pasar\n"
            "fin\nvar persona = Persona()\n",
        )


def test_argumentos_sin_constructor_propio_se_rechazan():
    with pytest.raises(TypeError, match="sin constructor propio no acepta argumentos"):
        _ejecutar(
            InterpretadorCobra(),
            "clase Persona:\nfin\nvar persona = Persona(42)\n",
        )


def test_argumento_se_resuelve_en_el_entorno_llamador():
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "var numero = 42\n"
        "clase Persona:\n"
        "    metodo inicializar(este, numero):\n"
        "        atributo este numero = numero\n"
        "fin\nvar persona = Persona(numero)\n",
    )
    assert inter.obtener_variable("persona")["__atributos__"]["numero"] == 42
    assert inter.obtener_variable("numero") == 42


def test_constructor_heredado_no_se_invoca_implicitamente(capsys):
    inter = InterpretadorCobra()
    _ejecutar(
        inter,
        "clase Base:\n"
        "    metodo inicializar(este):\n"
        "        imprimir 42\n"
        "fin\n"
        "clase Hija(Base):\nfin\nvar hija = Hija()\n",
    )
    assert capsys.readouterr().out == ""
    assert inter.obtener_variable("hija")["__atributos__"] == {}
