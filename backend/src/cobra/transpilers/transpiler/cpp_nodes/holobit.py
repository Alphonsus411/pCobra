def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores)
    if getattr(nodo, "nombre", None):
        self.agregar_linea(f"auto {nodo.nombre} = holobit({{ {valores} }});")
    else:
        self.agregar_linea(f"holobit({{ {valores} }});")
