def visit_enum(self, nodo):
    """Genera un objeto que representa un ``enum``."""
    miembros = ", ".join(f"{m}: {i}" for i, m in enumerate(nodo.miembros))
    self.agregar_linea(f"const {nodo.nombre} = {{{miembros}}};")
