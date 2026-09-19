import pytest
from cobra.core import Lexer
from cobra.core import NodoTryCatch, Parser, ParserError


def parse(code: str):
    tokens = Lexer(code).analizar_token()
    return Parser(tokens)


def test_decorator_without_function():
    codigo = "@d var x = 1"
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_desde_without_import():
    codigo = "desde 'm' x"
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_unclosed_macro():
    codigo = "macro m { var x = 1 "
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_condicional_sino_sin_fin():
    codigo = """
    si x > 0:
        imprimir(x)
    sino:
        imprimir(x)
    """
    with pytest.raises(ParserError):
        parse(codigo).parsear()


def test_condicional_si_valido_con_dos_puntos_espaciado():
    codigo = """
si 1 == 1 :
    imprimir "ok"
fin
"""
    ast = parse(codigo).parsear()
    assert ast, "Se esperaba AST no vacío para condicional válido"


def test_condicional_si_sin_dos_puntos_lanza_parser_error():
    codigo = """
si 1 == 1
    imprimir "ok"
fin
"""
    with pytest.raises(ParserError) as exc_info:
        parse(codigo).parsear()

    assert str(exc_info.value) == "Se esperaba ':' después de la condición del 'si'"


def test_condicional_si_sin_fin_lanza_parser_error():
    codigo = """
si 1 == 1 :
    imprimir "ok"
"""
    with pytest.raises(ParserError) as exc_info:
        parse(codigo).parsear()

    assert str(exc_info.value) == "Se esperaba 'fin' para cerrar el bloque condicional"


def test_macro_llaves_desbalanceadas():
    codigo = "macro m { var x = 1 }}"
    with pytest.raises(ParserError):
        parse(codigo).parsear()


@pytest.mark.parametrize(
    "codigo",
    [
        """
intentar:
    imprimir("x")
fin
""",
        """
try:
    imprimir("x")
fin
""",
    ],
)
def test_try_sin_catch_lanza_parser_error(codigo):
    with pytest.raises(ParserError):
        parse(codigo).parsear()


@pytest.mark.parametrize(
    "codigo",
    [
        """
intentar:
    imprimir("x")
capturar:
    imprimir("error")
fin
""",
        """
try:
    imprimir("x")
catch:
    imprimir("error")
fin
""",
    ],
)
def test_catch_sin_identificador_lanza_parser_error(codigo):
    with pytest.raises(
        ParserError,
        match="Se esperaba un identificador después de 'catch' o 'capturar'",
    ):
        parse(codigo).parsear()


@pytest.mark.parametrize(
    "codigo",
    [
        """
intentar:
    lanzar "fallo"
capturar e:
    imprimir(e)
fin
""",
        """
try:
    throw "fallo"
catch e:
    imprimir(e)
fin
""",
        """
intentar:
    imprimir("x")
capturar e:
    imprimir(e)
finalmente:
    imprimir("fin")
fin
""",
    ],
)
def test_try_con_catch_valido_parsea(codigo):
    ast = parse(codigo).parsear()
    assert ast


@pytest.mark.parametrize("palabra_try", ["intentar", "try"])
def test_try_con_finalmente_sin_catch_preserva_bloques_ast(palabra_try):
    codigo = f"""
{palabra_try}:
    imprimir("x")
finalmente:
    imprimir("fin")
fin
"""

    ast = parse(codigo).parsear()

    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoTryCatch)
    assert len(nodo.bloque_try) == 1
    assert nodo.nombre_excepcion is None
    assert len(nodo.bloque_catch) == 0
    assert len(nodo.bloque_finally) == 1
