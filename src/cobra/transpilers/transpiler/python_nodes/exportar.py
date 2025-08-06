from core.ast_nodes import NodoExport


def visit_export(self, nodo: NodoExport):
    """Registra un símbolo para exportarlo mediante ``__all__``."""
    self.exportados.append(nodo.nombre)
