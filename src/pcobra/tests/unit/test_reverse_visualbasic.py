from cobra.transpilers.reverse.from_visualbasic import ReverseFromVisualBasic
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoIdentificador


def test_reverse_from_visualbasic_basic():
    codigo = (
        "Function Foo(x)\n"
        "    y = x\n"
        "    Bar(y)\n"
        "End Function\n"
    )
    ast = ReverseFromVisualBasic().generate_ast(codigo)
    assert len(ast) == 1
    fn = ast[0]
    assert isinstance(fn, NodoFuncion)
    assert fn.nombre == "Foo"
    assert fn.parametros == ["x"]
    assert len(fn.cuerpo) == 2
    assert isinstance(fn.cuerpo[0], NodoAsignacion)
    llamada = fn.cuerpo[1]
    assert isinstance(llamada, NodoLlamadaFuncion)
    assert llamada.nombre == "Bar"
    assert llamada.argumentos == [NodoIdentificador("y")]
