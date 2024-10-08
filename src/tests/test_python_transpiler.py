import sys
import os

from src.core.lexer import Lexer

# Añadir el directorio 'core/transpiler' al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'transpiler')))

# Ahora puedes importar PythonTranspiler
from src.core.transpiler.python_transpiler import PythonTranspiler


def test_python_transpiler_basic_assignment():
    source_code = 'variable x = 10'
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = 'x = 10'
    assert transpiled_code == expected_code


def test_python_transpiler_function_with_if_else():
    source_code = '''
    variable x = 10
    funcion sumar() {
        si x mas 5 mientras 20
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''x = 10
def sumar():
    if x else 5 while 20'''
    assert transpiled_code == expected_code


def test_python_transpiler_function_with_return():
    source_code = '''
    funcion restar() {
        devolver x - y
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''def restar():
    return x - y'''
    assert transpiled_code == expected_code


def test_python_transpiler_nested_if():
    source_code = '''
    funcion verificar() {
        si x {
            si y mas z
        }
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''def verificar():
    if x:
        if y else z'''
    assert transpiled_code == expected_code


def test_python_transpiler_while_loop():
    source_code = '''
    funcion bucle() {
        mientras x menor que 10 {
            x = x + 1
        }
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''def bucle():
    while x < 10:
        x = x + 1'''
    assert transpiled_code == expected_code


def test_python_transpiler_complex_logic():
    source_code = '''
    variable a = 5
    variable b = 10
    si a mayor que b mas b
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''a = 5
b = 10
if a > b else b'''
    assert transpiled_code == expected_code


def test_python_transpiler_function_with_multiple_statements():
    source_code = '''
    funcion operaciones() {
        variable suma = x + y
        variable resta = x - y
        devolver suma, resta
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''def operaciones():
    suma = x + y
    resta = x - y
    return suma, resta'''
    assert transpiled_code == expected_code


def test_python_transpiler_with_for_loop():
    source_code = '''
    funcion iterar() {
        para i en rango(0, 10) {
            imprimir(i)
        }
    }
    '''
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = PythonTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = '''def iterar():
    for i in range(0, 10):
        print(i)'''
    assert transpiled_code == expected_code
