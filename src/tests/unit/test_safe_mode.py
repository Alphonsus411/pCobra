import backend  # garantiza rutas para submódulos
import pytest
from io import StringIO
from unittest.mock import patch

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoLlamadaFuncion, NodoValor
from core.semantic_validators import PrimitivaPeligrosaError


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens).parsear()


@pytest.mark.parametrize(
    "codigo",
    [
        "leer_archivo('x.txt')",
        "obtener_url('ejemplo')",
        "leer('x.txt')",
        "escribir('x.txt', 'hola')",
        "existe('x.txt')",
        "enviar_post('u', 'd')",
        "ejecutar('ls')",
        "listar_dir('.')",
    ],
)
def test_primitivas_rechazadas_en_modo_seguro(codigo):
    interp = InterpretadorCobra(safe_mode=True)
    ast = generar_ast(codigo)
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_codigo_seguro_se_ejecuta_en_modo_seguro():
    interp = InterpretadorCobra(safe_mode=True)
    nodo = NodoLlamadaFuncion("imprimir", [NodoValor("hola")])
    with patch('sys.stdout', new_callable=StringIO) as out:
        interp.ejecutar_llamada_funcion(nodo)
    assert out.getvalue().strip() == 'hola'
