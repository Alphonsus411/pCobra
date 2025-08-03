import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser, ParserError
from core.ast_nodes import NodoFuncion, NodoAsignacion


def test_recursion_mixed_types_ast():
    codigo = '''
    func rec(n):
        si n <= 1:
            retorno 1
        sino:
            retorno n * rec(n - 1)
        fin
    fin
    var numero = 5
    var texto = "hola"
    '''
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    assert len(ast) == 3
    assert isinstance(ast[0], NodoFuncion)
    assert ast[0].nombre == "rec"
    assert isinstance(ast[1], NodoAsignacion)
    assert isinstance(ast[2], NodoAsignacion)


def test_error_lista_no_soportada():
    codigo = '''
    func dummy():
        fin
    x = [1, 2, 3]
    '''
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)

    with pytest.raises(ParserError, match="LBRACKET"):
        parser.parsear()
