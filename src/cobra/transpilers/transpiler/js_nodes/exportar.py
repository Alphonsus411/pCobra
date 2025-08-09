from cobra.core.ast_nodes import NodoExport


def visit_export(self, nodo: NodoExport):
    """Genera una sentencia de exportación."""
    self.agregar_linea(f"export {{ {nodo.nombre} }};")
