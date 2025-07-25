from src.cobra.transpilers.module_map import get_mapped_path

def visit_import(self, nodo):
    """Genera una importación ES module."""
    ruta = get_mapped_path(nodo.ruta, "js")
    self.agregar_linea(f"import '{ruta}';")
