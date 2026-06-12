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


def test_transpila_funcion_vacia_e_imprimir_sin_exitstack_ni_recursion():
    codigo_fuente = '''func vacia(n):
fin
imprimir("ok")
'''

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError("La transpilación no debe lanzar RecursionError") from exc

    assert "def vacia(n):" in codigo_python
    assert "pass" in codigo_python
    assert "print('ok')" in codigo_python
    assert "contextlib.ExitStack" not in codigo_python


def test_transpila_funcion_identidad_e_imprimir_sin_exitstack_ni_recursion():
    codigo_fuente = """func identidad(n):
    retorno n
fin
imprimir(identidad(3))
"""

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError(
            "La transpilación no debe producir maximum recursion depth exceeded"
        ) from exc
    except Exception as exc:
        assert "maximum recursion depth exceeded" not in str(exc)
        raise

    assert "def identidad(n):" in codigo_python
    assert "return n" in codigo_python
    assert "print(identidad(3))" in codigo_python
    assert "contextlib.ExitStack" not in codigo_python
    assert "maximum recursion depth exceeded" not in codigo_python


def test_transpila_script_gui_reducido_sin_exitstack_ni_recursion():
    codigo_fuente = '''func doble(n):
    retorno n * 2
fin

func resumen_numero(n):
    si n > 0: imprimir("positivo") sino: imprimir("no positivo") fin
    imprimir(doble(n))
fin

var x = 7
resumen_numero(x)
'''

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError("La transpilación no debe lanzar RecursionError") from exc

    assert "def doble(n):" in codigo_python
    assert "return n * 2" in codigo_python
    assert "def resumen_numero(n):" in codigo_python
    assert "if n > 0:" in codigo_python
    assert "else:" in codigo_python
    assert "print(doble(n))" in codigo_python
    assert "x = 7" in codigo_python
    assert "resumen_numero(x)" in codigo_python
    assert "contextlib.ExitStack" not in codigo_python


def test_regresion_transpila_gui_reducida_con_funciones_if_inline_sin_exitstack():
    codigo_fuente = '''func doble(n):
    retorno n * 2
fin

func resumen_numero(n):
    si n > 0: imprimir("positivo") sino: imprimir("no positivo") fin
    imprimir(doble(n))
fin

var x = 7
resumen_numero(x)
'''

    try:
        tokens = Lexer(codigo_fuente).analizar_token()
        ast = Parser(tokens).parsear()
        codigo_python = TranspiladorPython().generate_code(ast)
    except RecursionError as exc:  # pragma: no cover - el fallo debe ser explícito
        raise AssertionError("La transpilación no debe lanzar RecursionError") from exc

    fragmentos_esperados = (
        "def doble(n):",
        "return n * 2",
        "def resumen_numero(n):",
        "if n > 0:",
        "else:",
        "print(doble(n))",
        "x = 7",
        "resumen_numero(x)",
    )

    for fragmento in fragmentos_esperados:
        assert fragmento in codigo_python
    assert "contextlib.ExitStack" not in codigo_python
