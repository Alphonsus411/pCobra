from core.ast_nodes import NodoExport


def visit_export(self, nodo: NodoExport):
    """Reexporta un símbolo mediante ``pub use``."""
    self.agregar_linea(f"pub use {nodo.nombre};")
