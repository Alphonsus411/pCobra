"""POO-016: destinos atributo desde fuente y validación de símbolos."""

import pytest

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.core.ast_nodes import NodoAsignacion, NodoValor
from pcobra.cobra.semantico import AnalizadorSemantico


def _analizar(fuente):
    nodos = Parser(Lexer(fuente).tokenizar()).parsear()
    analizador = AnalizadorSemantico()
    analizador.analizar(nodos)
    return analizador


def test_escritura_y_lectura_canonicas_en_metodo():
    analizador = _analizar(
        "clase Persona:\n"
        "    metodo guardar(este, valor):\n"
        "        atributo este nombre = valor\n"
        "        imprimir atributo este nombre\n"
        "fin\n"
    )
    assert set(analizador.global_scope.simbolos) == {"Persona"}
    assert analizador.current_scope is analizador.global_scope


@pytest.mark.parametrize(
    ("parametros", "valor", "ausente"),
    [
        ("valor", "valor", "este"),
        ("este", "desconocido", "desconocido"),
    ],
)
def test_escritura_valida_receptor_y_rhs(parametros, valor, ausente):
    fuente = (
        "clase Persona:\n"
        f"    metodo guardar({parametros}):\n"
        f"        atributo este nombre = {valor}\n"
        "fin\n"
    )
    with pytest.raises(NameError, match=rf"^Variable no declarada: {ausente}$"):
        _analizar(fuente)


def test_nombre_del_campo_no_se_declara_como_variable_local():
    with pytest.raises(NameError, match=r"^Variable no declarada: nombre$"):
        _analizar(
            "clase Persona:\n"
            "    metodo guardar(este, valor):\n"
            "        atributo este nombre = valor\n"
            "        imprimir nombre\n"
            "fin\n"
        )


def test_asignacion_ordinaria_y_reasignacion_conservan_sus_simbolos():
    analizador = _analizar(
        'var nombre = "Adolfo"\nnombre = "Ana"\nimprimir nombre\n'
    )
    assert set(analizador.global_scope.simbolos) == {"nombre"}
    assert analizador.global_scope.resolver("nombre").tipo == "variable"


def test_asignacion_ordinaria_sigue_validando_rhs():
    with pytest.raises(NameError, match=r"^Variable no declarada: desconocido$"):
        _analizar("var nombre = desconocido\n")


def test_destino_ast_invalido_no_se_admite_como_nombre():
    with pytest.raises(TypeError, match="El nombre debe ser string"):
        AnalizadorSemantico().analizar(
            [NodoAsignacion(NodoValor(1), NodoValor(2))]
        )


def test_nombre_de_campo_ast_invalido_se_rechaza():
    nodos = Parser(
        Lexer(
            "clase Persona:\n"
            "    metodo guardar(este, valor):\n"
            "        atributo este nombre = valor\n"
            "fin\n"
        ).tokenizar()
    ).parsear()
    nodos[0].metodos[0].cuerpo[0].variable.nombre = 42
    with pytest.raises(TypeError, match="El nombre debe ser string"):
        AnalizadorSemantico().analizar(nodos)
