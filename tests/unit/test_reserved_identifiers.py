import pytest

from cobra.core import Lexer
from cobra.core import Parser, ParserError


def test_variable_nombre_reservado():
    codigo = "var si = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


def test_funcion_nombre_reservado():
    codigo = """
    func mientras():
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


def test_parametro_nombre_reservado():
    codigo = """
    func foo(para):
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


@pytest.mark.parametrize("identificador", ["y", "o", "no", "elseif"])
def test_nombres_reservados_alias_logicos(identificador):
    codigo = f"var {identificador} = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


@pytest.mark.parametrize(
    "identificador",
    ["clase", "estructura", "registro"],
)
def test_nombres_reservados_alias_clase(identificador):
    codigo = f"var {identificador} = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()


@pytest.mark.parametrize("identificador", ["enum", "enumeracion"])
def test_nombres_reservados_alias_enum(identificador):
    codigo = f"var {identificador} = 1"
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    with pytest.raises(ParserError, match="palabra reservada"):
        parser.parsear()
