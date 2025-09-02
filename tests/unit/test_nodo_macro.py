from core.ast_nodes import NodoMacro


def test_nodo_macro_repr():
    nodo = NodoMacro('m', [1, 2])
    assert 'nombre=m' in repr(nodo)
    assert 'cuerpo=[1, 2]' in repr(nodo)
