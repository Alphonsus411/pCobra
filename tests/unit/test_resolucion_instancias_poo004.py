"""Pruebas focales de POO-004: instanciación alcanzable desde fuente."""

from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoValor,
)
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser


def _parsear(codigo: str):
    return Parser(Lexer(codigo).analizar_token()).parsear()


def _valor_asignado(nodo):
    assert type(nodo) is NodoAsignacion
    return nodo.expresion


def test_clase_sin_argumentos_produce_instancia():
    ast = _parsear("clase Vacia:\nfin\nvar x = Vacia()")

    assert type(ast[0]) is NodoClase
    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Vacia"
    assert instancia.argumentos == []


def test_clase_con_un_argumento_preserva_valor_y_tipo():
    ast = _parsear(
        'clase Persona:\n'
        '    metodo inicializar(este, nombre):\n'
        '        imprimir nombre\n'
        'fin\n'
        'var persona = Persona("Adolfo")'
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Persona"
    assert len(instancia.argumentos) == 1
    assert type(instancia.argumentos[0]) is NodoValor
    assert instancia.argumentos[0].valor == "Adolfo"


def test_clase_con_varios_argumentos_preserva_orden_y_tipos():
    ast = _parsear(
        "clase Punto:\n"
        "    metodo inicializar(este, x, y):\n"
        "        imprimir x\n"
        "fin\n"
        "var p = Punto(1, 2)"
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Punto"
    assert [type(arg) for arg in instancia.argumentos] == [NodoValor, NodoValor]
    assert [arg.valor for arg in instancia.argumentos] == [1, 2]


def test_funcion_normal_permanece_llamada_funcion():
    ast = _parsear(
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        "var resultado = procesar(1)"
    )

    llamada = _valor_asignado(ast[1])
    assert type(llamada) is NodoLlamadaFuncion
    assert llamada.nombre == "procesar"
    assert type(llamada.argumentos[0]) is NodoValor


def test_clase_y_funcion_resuelven_cada_nombre_a_su_nodo():
    ast = _parsear(
        "clase Persona:\nfin\n"
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        'var resultado = procesar("Adolfo")'
    )

    assert type(_valor_asignado(ast[2])) is NodoInstancia
    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_instancia_y_llamada_postfix_son_expresiones_distintas():
    ast = _parsear(
        "clase Persona:\n"
        "    metodo saludar(este):\n"
        '        imprimir "Hola"\n'
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        "persona.saludar()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia
    llamada = ast[2]
    assert type(llamada) is NodoLlamadaMetodo
    assert type(llamada.objeto) is NodoIdentificador
    assert llamada.objeto.nombre == "persona"
    assert llamada.nombre_metodo == "saludar"
    assert llamada.argumentos == []


def test_referencia_hacia_delante_no_se_resuelve_como_instancia():
    ast = _parsear("var x = Posterior()\nclase Posterior:\nfin")

    assert type(_valor_asignado(ast[0])) is NodoLlamadaFuncion


def test_colision_clase_funcion_no_inventa_precedencia():
    ast = _parsear(
        "clase Duplicado:\nfin\n"
        "func Duplicado():\n"
        "    retornar 1\n"
        "fin\n"
        "var x = Duplicado()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion
