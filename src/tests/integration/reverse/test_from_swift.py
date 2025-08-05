import pytest

from cobra.transpilers.reverse.from_swift import ReverseFromSwift
from core.ast_nodes import NodoFuncion, NodoLlamadaFuncion, NodoValor


def test_reverse_from_swift_func_and_print():
    code = """
    func saludo() {
        print("Hola")
    }
    """
    transpiler = ReverseFromSwift()
    ast_nodes = transpiler.generate_ast(code)

    funcion = next(n for n in ast_nodes if isinstance(n, NodoFuncion))
    assert funcion.nombre == "saludo"

    llamada = next(n for n in funcion.cuerpo if isinstance(n, NodoLlamadaFuncion))
    assert llamada.nombre == "print"
    assert llamada.argumentos and isinstance(llamada.argumentos[0], NodoValor)
    assert llamada.argumentos[0].valor == "Hola"
