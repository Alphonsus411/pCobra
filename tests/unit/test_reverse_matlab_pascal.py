from cobra.transpilers.reverse.from_matlab import ReverseFromMatlab
from cobra.transpilers.reverse.from_pascal import ReverseFromPascal
from core.ast_nodes import NodoAsignacion, NodoCondicional, NodoFuncion, NodoPara


def test_reverse_from_matlab_basic():
    codigo = (
        "function y = foo(x)\n"
        "y = x\n"
        "if y\n"
        " y = y\n"
        "end\n"
        "for i = 1:3\n"
        " y = y\n"
        "end\n"
        "end\n"
    )

    ast = ReverseFromMatlab().generate_ast(codigo)
    assert len(ast) == 1
    fn = ast[0]
    assert isinstance(fn, NodoFuncion)
    assert fn.nombre == "foo"
    assert len(fn.cuerpo) == 3
    assert isinstance(fn.cuerpo[0], NodoAsignacion)
    assert isinstance(fn.cuerpo[1], NodoCondicional)
    assert isinstance(fn.cuerpo[2], NodoPara)


def test_reverse_from_pascal_basic():
    codigo = (
        "function foo(x: integer): integer;\n"
        "begin\n"
        "  y := x;\n"
        "  if y then\n"
        "  begin\n"
        "    y := y;\n"
        "  end;\n"
        "  for i := 1 to 3 do\n"
        "  begin\n"
        "    y := y;\n"
        "  end;\n"
        "end;\n"
    )

    ast = ReverseFromPascal().generate_ast(codigo)
    assert len(ast) == 1
    fn = ast[0]
    assert isinstance(fn, NodoFuncion)
    assert fn.nombre == "foo"
    assert len(fn.cuerpo) == 3
    assert isinstance(fn.cuerpo[0], NodoAsignacion)
    assert isinstance(fn.cuerpo[1], NodoCondicional)
    assert isinstance(fn.cuerpo[2], NodoPara)

