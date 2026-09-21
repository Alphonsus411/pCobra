"""Contrato focal del Parser para llamadas postfix de método."""

import pytest

from pcobra.cobra.core.lexer import Lexer, TipoToken
from pcobra.cobra.core.parser import ClassicParser, ParserError
from pcobra.core.ast_nodes import (
    NodoAtributo,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoOperacionBinaria,
    NodoValor,
)


def _parsear(codigo: str):
    tokens = Lexer(codigo).tokenizar()
    parser = ClassicParser(tokens)
    return tokens, parser, parser.parsear()


def test_llamada_metodo_sin_argumentos() -> None:
    _, _, ast = _parsear("persona.saludar()")

    llamada = ast[0]
    assert type(llamada) is NodoLlamadaMetodo
    assert isinstance(llamada.objeto, NodoIdentificador)
    assert llamada.objeto.nombre == "persona"
    assert llamada.nombre_metodo == "saludar"
    assert llamada.argumentos == []


def test_llamada_metodo_con_un_argumento() -> None:
    _, _, ast = _parsear('persona.cambiar_nombre("Ana")')

    llamada = ast[0]
    assert isinstance(llamada, NodoLlamadaMetodo)
    assert llamada.nombre_metodo == "cambiar_nombre"
    assert len(llamada.argumentos) == 1
    assert isinstance(llamada.argumentos[0], NodoValor)
    assert llamada.argumentos[0].valor == "Ana"


def test_llamada_metodo_conserva_varios_argumentos_en_orden() -> None:
    _, _, ast = _parsear("persona.procesar(1, 2, 3)")

    llamada = ast[0]
    assert isinstance(llamada, NodoLlamadaMetodo)
    assert llamada.nombre_metodo == "procesar"
    assert [argumento.valor for argumento in llamada.argumentos] == [1, 2, 3]


def test_llamada_metodo_acepta_expresiones_como_argumentos() -> None:
    _, _, ast = _parsear("persona.procesar(a + b, otra())")

    llamada = ast[0]
    assert isinstance(llamada, NodoLlamadaMetodo)
    assert len(llamada.argumentos) == 2
    assert isinstance(llamada.argumentos[0], NodoOperacionBinaria)
    assert isinstance(llamada.argumentos[1], NodoLlamadaFuncion)
    assert llamada.argumentos[1].nombre == "otra"


def test_llamada_funcion_simple_permanece_intacta() -> None:
    _, _, ast = _parsear("saludar()")

    llamada = ast[0]
    assert type(llamada) is NodoLlamadaFuncion
    assert llamada.nombre == "saludar"
    assert llamada.argumentos == []


def test_acceso_atributo_permanece_intacto() -> None:
    _, _, ast = _parsear("persona.nombre")

    atributo = ast[0]
    assert type(atributo) is NodoAtributo
    assert isinstance(atributo.objeto, NodoIdentificador)
    assert atributo.objeto.nombre == "persona"
    assert atributo.nombre == "nombre"


def test_llamada_metodo_consume_sus_tokens_completamente() -> None:
    tokens, parser, _ = _parsear("persona.procesar(1, 2, 3)")

    assert parser.token_actual().tipo == TipoToken.EOF
    assert tokens[parser.posicion :][0].tipo == TipoToken.EOF
    assert not {
        TipoToken.LPAREN,
        TipoToken.RPAREN,
        TipoToken.COMA,
    }.intersection(token.tipo for token in tokens[parser.posicion :])


def test_llamada_metodo_rechaza_keyword_como_nombre() -> None:
    tokens = Lexer("persona.metodo()").tokenizar()

    assert tokens[2].tipo == TipoToken.METODO
    with pytest.raises(ParserError, match="Se esperaba el nombre del atributo"):
        ClassicParser(tokens).parsear()


def test_dos_llamadas_metodo_consecutivas() -> None:
    _, _, ast = _parsear("persona.saludar()\npersona.despedir()")

    assert [type(nodo) for nodo in ast] == [NodoLlamadaMetodo, NodoLlamadaMetodo]
    assert [nodo.nombre_metodo for nodo in ast] == ["saludar", "despedir"]


def test_llamada_metodo_seguida_de_otra_declaracion() -> None:
    _, _, ast = _parsear('persona.saludar()\nimprimir "fin"')

    assert isinstance(ast[0], NodoLlamadaMetodo)
    assert isinstance(ast[1], NodoImprimir)


def test_llamada_metodo_despues_de_declaracion_de_clase() -> None:
    codigo = """\
clase Persona:
    metodo saludar(este):
        imprimir "Hola"
fin

persona.saludar()
"""

    _, _, ast = _parsear(codigo)

    assert isinstance(ast[-1], NodoLlamadaMetodo)
    assert ast[-1].nombre_metodo == "saludar"
