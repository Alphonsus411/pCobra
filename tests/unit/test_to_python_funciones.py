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


def test_transpila_script_complejo_con_usar_funciones_retorno_y_llamadas():
    codigo_fuente = '''usar "numero"
usar "texto"
usar "datos"

func doble(n):
    retorno n * 2
fin

func cuadrado(n):
    retorno n * n
fin

func resumen_numero(n):
    si n > 10:
        retorno a_texto(n)
    sino:
        retorno "pequeno"
    fin
fin

y = doble(5)
z = cuadrado(y)
resumen = resumen_numero(z)
imprimir(y)
imprimir(resumen)
'''

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError("La transpilación no debe lanzar RecursionError") from exc
    except Exception as exc:
        if "maximum recursion depth exceeded" in str(exc):
            raise AssertionError(
                "La transpilación no debe superar la profundidad máxima de recursión"
            ) from exc
        raise

    assert "def doble(n):" in codigo_python
    assert "def cuadrado(n):" in codigo_python
    assert "def resumen_numero(n):" in codigo_python
    assert "y = doble(5)" in codigo_python
    assert "print(y)" in codigo_python


def test_transpila_funcion_doble_asignacion_e_imprimir_sin_exitstack_ni_recursion():
    codigo_fuente = """func doble(n):
    retorno n * 2
fin
var x = doble(5)
imprimir(x)
"""

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError("La transpilación no debe lanzar RecursionError") from exc

    assert "def doble(n):" in codigo_python
    assert "return n * 2" in codigo_python
    assert "x = doble(5)" in codigo_python
    assert "print(x)" in codigo_python
    assert "contextlib.ExitStack" not in codigo_python
