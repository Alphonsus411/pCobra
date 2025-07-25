from io import StringIO
from unittest.mock import patch

from core.interpreter import InterpretadorCobra
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


def test_interpreter_atributo_lectura_escritura():
    codigo = """\natributo p nombre = '\"Ana\"'\nimprimir(atributo p nombre)\n"""
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    inter = InterpretadorCobra()
    inter.variables['p'] = {'__atributos__': {}}
    with patch('sys.stdout', new_callable=StringIO) as out:
        for nodo in ast:
            inter.ejecutar_nodo(nodo)
    assert out.getvalue().strip() == 'Ana'
