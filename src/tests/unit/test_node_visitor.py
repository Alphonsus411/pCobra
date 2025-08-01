import pytest

from core.visitor import NodeVisitor
from core.ast_nodes import NodoAST

class MiNodo(NodoAST):
    pass

class MiVisitor(NodeVisitor):
    pass

def test_generic_visit_se_ejecuta_para_nodo_desconocido():
    visitante = MiVisitor()
    with pytest.raises(NotImplementedError):
        visitante.visit(MiNodo())
