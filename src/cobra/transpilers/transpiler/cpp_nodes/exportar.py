from core.ast_nodes import NodoExport


def visit_export(self, nodo: NodoExport):
    """Marca un símbolo para ser exportado."""
    self.agregar_linea(f"// export {nodo.nombre}")
