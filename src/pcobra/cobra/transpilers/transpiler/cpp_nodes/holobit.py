def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores)
    self.usa_runtime_holobit = True
    if getattr(nodo, "nombre", None):
        self.agregar_linea(f"auto {nodo.nombre} = cobra_holobit({{ {valores} }});")
    else:
        self.agregar_linea(f"cobra_holobit({{ {valores} }});")
