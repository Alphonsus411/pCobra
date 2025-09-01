from core.ast_nodes import (
    NodoListaTipo,
    NodoDiccionarioTipo,
    NodoValor,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.reverse.from_python import ReverseFromPython
from cobra.transpilers.import_helper import get_standard_imports


def test_transpilar_lista_tipo_python():
    nodo = NodoListaTipo("nums", "int", [NodoValor(1), NodoValor(2)])
    result = TranspiladorPython().generate_code([nodo])
    expected = get_standard_imports("python") + "nums: list[int] = [1, 2]\n"
    assert result == expected


def test_transpilar_diccionario_tipo_js():
    nodo = NodoDiccionarioTipo("datos", "str", "int", [(NodoValor("a"), NodoValor(1))])
    result = TranspiladorJavaScript().generate_code([nodo])
    imports = "".join(f"{line}\n" for line in get_standard_imports("js"))
    expected = imports + "let datos = {a: 1};"
    assert result.strip() == expected.strip()


def test_transpilar_lista_tipo_cpp():
    nodo = NodoListaTipo("valores", "int", [NodoValor(1), NodoValor(2)])
    result = TranspiladorCPP().generate_code([nodo])
    assert "std::vector<int> valores = {1, 2};" in result


def test_reverse_from_python_lista_diccionario():
    code = "lista = [1, 2]\ndic = {1: 2}"
    transpiler = ReverseFromPython()
    ast_nodes = transpiler.generate_ast(code)
    assert any(isinstance(n, NodoListaTipo) for n in ast_nodes)
    assert any(isinstance(n, NodoDiccionarioTipo) for n in ast_nodes)

