from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpila_funcion_y_llamadas_a_corelibs_sin_contextlib():
    codigo_fuente = '''usar "numero"
usar "texto"

func doble(n):
    retorno n * 2
fin

imprimir(mayusculas("cobra"))
imprimir(doble(5))
'''

    tokens = Lexer(codigo_fuente).analizar_token()
    ast = Parser(tokens).parsear()
    codigo_python = TranspiladorPython().generate_code(ast)

    assert "mayusculas" in codigo_python
    assert "texto = obtener_modulo('texto')" in codigo_python
    assert "def doble(n):" in codigo_python
    assert "return n * 2" in codigo_python
    assert "print(mayusculas('cobra'))" in codigo_python
    assert "print(doble(5))" in codigo_python
    assert "contextlib" not in codigo_python
