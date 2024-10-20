# Parseamos los tokens para generar el AST
from src.core.lexer import Token, TipoToken
from src.core.parser import Parser

tokens = [
    Token(TipoToken.MIENTRAS, 'mientras'),
    Token(TipoToken.IDENTIFICADOR, 'x'),
    Token(TipoToken.MAYORQUE, '>'),
    Token(TipoToken.ENTERO, 0),
    Token(TipoToken.DOSPUNTOS, ':'),
    Token(TipoToken.IDENTIFICADOR, 'x'),
    Token(TipoToken.ASIGNAR, '='),
    Token(TipoToken.IDENTIFICADOR, 'x'),
    Token(TipoToken.RESTA, '-'),
    Token(TipoToken.ENTERO, 1),
    Token(TipoToken.EOF, None)
]

parser = Parser(tokens)
ast_raiz = parser.parsear()  # Aquí obtienes el AST
print("AST generado:", ast_raiz)  # Imprimir el AST generado para ver la estructura

